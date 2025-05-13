import copy
import torch
import torch.nn as nn
from transformers import (
    T5PreTrainedModel,
    T5Config,
    T5ForConditionalGeneration, EncoderDecoderCache
)
from transformers.models.t5.modeling_t5 import T5Stack


class CustomT5WithStyle(T5PreTrainedModel):
    """
        style embeddings for SAQ/JSQ
        Has a small adapter in the decoder that fuses style embedding with decoder hidden states
    """
    def __init__(self, config: T5Config, style_emb_size=32):
        super().__init__(config)

        # Copy the config for encoder and decoder separately
        encoder_config = copy.deepcopy(config)
        encoder_config.is_decoder = False
        encoder_config.is_encoder_decoder = False
        encoder_config.use_cache = False

        decoder_config = copy.deepcopy(config)
        decoder_config.is_decoder = True
        decoder_config.is_encoder_decoder = False
        decoder_config.use_cache = True

        # Shared embeddings
        self.shared = nn.Embedding(config.vocab_size, config.d_model)

        # Encoder / Decoder
        self.encoder = T5Stack(encoder_config, self.shared)
        self.decoder = T5Stack(decoder_config, self.shared)

        # Style embeddings: 2 possible styles => SAQ=0, JSQ=1
        self.num_styles = 2
        self.style_emb_size = style_emb_size
        self.style_embeddings = nn.Embedding(self.num_styles, style_emb_size)

        # Adapter to fuse style embedding + decoder hidden states
        self.adapter = nn.Sequential(
            nn.Linear(config.d_model + style_emb_size, config.d_model),
            nn.ReLU(),
            nn.Linear(config.d_model, config.d_model),
            nn.ReLU()
        )

        # Final LM head => projects d_model to vocab_size
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)

        self.init_weights()

    #
    # NOTE: These two methods are required so that .resize_token_embeddings() works.
    #
    def get_input_embeddings(self):
        return self.shared

    def set_input_embeddings(self, new_embeddings):
        self.shared = new_embeddings
        self.encoder.set_input_embeddings(new_embeddings)
        self.decoder.set_input_embeddings(new_embeddings)

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        decoder_input_ids=None,
        decoder_attention_mask=None,
        labels=None,
        style_ids=None,

    ):

        """
        style_ids: (batch,) => 0=SAQ, 1=JSQ
        """
        # 1) Encode
        encoder_outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )
        enc_hidden = encoder_outputs.last_hidden_state  # (batch, src_len, d_model)

        if decoder_input_ids is None and labels is not None:
            # Get pad_token_id and a special decoder_start_token_id from config
            pad_token_id = self.config.pad_token_id
            decoder_start_token_id = self.config.decoder_start_token_id
            # If that doesn't exist, define your own, e.g. T5 uses 0 for start

            # shift tokens right
            decoder_input_ids = shift_tokens_right(labels, pad_token_id, decoder_start_token_id)



        # 2) Decode
        decoder_outputs = self.decoder(
            input_ids=decoder_input_ids,
            attention_mask=decoder_attention_mask,
            encoder_hidden_states=enc_hidden,
            encoder_attention_mask=attention_mask,
            return_dict=True
        )
        seq_output = decoder_outputs.last_hidden_state  # (batch, tgt_len, d_model)

        # 3) Style embedding
        style_vec = self.style_embeddings(style_ids)  # (batch, style_emb_size)

        # Expand style_vec across the time dimension
        batch_size, tgt_len, _ = seq_output.shape
        style_vec_expanded = style_vec.unsqueeze(1).expand(batch_size, tgt_len, self.style_emb_size)

        # 4) Fuse via adapter
        fused = torch.cat([seq_output, style_vec_expanded], dim=-1)  # (batch, tgt_len, d_model + style_emb_size)
        adapted = self.adapter(fused)                                # (batch, tgt_len, d_model)

        # 5) Project to vocab
        logits = self.lm_head(adapted)  # (batch, tgt_len, vocab_size)

        # Optional: compute loss if labels are provided
        loss = None
        if labels is not None:
            labels[labels == self.config.pad_token_id] = -100
            loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
            loss = loss_fct(
                logits.view(-1, logits.size(-1)),
                labels.view(-1)
            )

        return {
            "loss": loss,
            "logits": logits
        }

    def custom_generate(self,input_ids,attention_mask=None,style_ids=None,max_length=256,num_beams=1,
        pad_token_id=None,
        eos_token_id=None
    ):
        if pad_token_id is None:
            pad_token_id = self.config.pad_token_id
        if eos_token_id is None:
            eos_token_id = self.config.eos_token_id

        batch_size = input_ids.size(0)
        decoder_input_ids = torch.full(
            (batch_size, 1),
            pad_token_id,
            dtype=torch.long,
            device=input_ids.device
        )

        finished = [False] * batch_size
        for step in range(max_length):
            outputs = self.forward(
                input_ids=input_ids,
                attention_mask=attention_mask,
                decoder_input_ids=decoder_input_ids,
                style_ids=style_ids
            )
            logits = outputs["logits"]
            next_token_logits = logits[:, -1, :]
            next_tokens = torch.argmax(next_token_logits, dim=-1)  # greedy

            decoder_input_ids = torch.cat(
                [decoder_input_ids, next_tokens.unsqueeze(-1)],
                dim=-1
            )

            for i in range(batch_size):
                if not finished[i] and next_tokens[i].item() == eos_token_id:
                    finished[i] = True
            if all(finished):
                break

        return decoder_input_ids


def shift_tokens_right(input_ids, pad_token_id, decoder_start_token_id):
    """
    Shifts input_ids to the right, prepending the decoder_start_token_id.
    """
    shifted_input_ids = input_ids.new_zeros(input_ids.shape)
    shifted_input_ids[:, 1:] = input_ids[:, :-1].clone()
    shifted_input_ids[:, 0] = decoder_start_token_id

    # Replace any -100 (ignore_index) with pad_token_id
    shifted_input_ids = shifted_input_ids.masked_fill(
        shifted_input_ids == -100, pad_token_id
    )

    return shifted_input_ids

def load_pretrained_t5_small_into_custom(custom_model):
    """
    Load the official T5-small weights, ignoring the new style embeddings/adapter.
    """
    official_t5 = T5ForConditionalGeneration.from_pretrained("t5-small")
    state_dict = official_t5.state_dict()
    custom_model.load_state_dict(state_dict, strict=False)
    print("Loaded T5-small weights into CustomT5WithStyle (strict=False).")


def freeze_encoder_layers(model, num_layers_to_freeze=3):
    """
    Freeze the first `num_layers_to_freeze` blocks in the T5 encoder.
    """
    all_blocks = model.encoder.block
    for i in range(min(num_layers_to_freeze, len(all_blocks))):
        for param in all_blocks[i].parameters():
            param.requires_grad = False
    print(f"Froze the first {num_layers_to_freeze} encoder layers.")