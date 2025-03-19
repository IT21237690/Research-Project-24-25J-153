
import json
import os
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from transformers import T5Tokenizer, T5Config
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import matplotlib.pyplot as plt

# If your model is in another file, import it:
from model import CustomT5WithStyle, load_pretrained_t5_small_into_custom, freeze_encoder_layers

# If you have the model code in the same file, you can remove the import above and paste it here.

class QGDataset(Dataset):

    def __init__(self, json_file, tokenizer, max_length=128):
        super().__init__()
        with open(json_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        input_text = item["input"]
        output_text = item["output"]
        style_id = item["style_id"]  # 0 => SAQ, 1 => JSQ

        # Tokenize the input and output
        source_enc = self.tokenizer(
            input_text,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        target_enc = self.tokenizer(
            output_text,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )

        input_ids = source_enc["input_ids"].squeeze(0)
        attention_mask = source_enc["attention_mask"].squeeze(0)
        labels = target_enc["input_ids"].squeeze(0)
        # Typically, T5 handles decoder masking internally.

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
            "style_id": style_id
        }


def train_one_epoch(model, dataloader, optimizer, device, max_grad_norm=None):
    """
    Performs one epoch of training using cross-entropy loss.
    Includes gradient clipping if max_grad_norm is provided.
    """
    model.train()
    total_loss = 0.0

    optimizer.zero_grad()


    for batch in tqdm(dataloader, desc="Training"):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        style_ids = batch["style_id"].to(device)

        # Forward pass. Let T5 handle "decoder_input_ids" internally by passing labels=.
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
            style_ids=style_ids
        )
        loss = outputs["loss"]

        optimizer.zero_grad()
        loss.backward()

        # Gradient Clipping
        if max_grad_norm is not None:
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)

        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / len(dataloader)
    return avg_loss


def evaluate(model, dataloader, device):
    """
    Evaluates the model on the validation or test set and returns the average loss.
    """
    model.eval()
    total_loss = 0.0

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            style_ids = batch["style_id"].to(device)

            # Forward pass
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
                style_ids=style_ids
            )
            loss = outputs["loss"]

            total_loss += loss.item()

    avg_loss = total_loss / len(dataloader)
    return avg_loss


def calculate_accuracy(model, dataloader, device):
    """
    Calculates accuracy of the model over the provided dataloader.
    """
    model.eval()
    total_correct = 0
    total_examples = 0

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Calculating Accuracy"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            style_ids = batch["style_id"].to(device)

            # Forward pass
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
                style_ids=style_ids
            )

            logits = outputs["logits"]
            predictions = torch.argmax(logits, dim=-1)

            # Compare predictions with labels
            labels_mask = labels != -100  # Ignore padding tokens
            total_correct += (predictions[labels_mask] == labels[labels_mask]).sum().item()
            total_examples += labels_mask.sum().item()

    accuracy = total_correct / total_examples
    return accuracy


def plot_metrics(train_losses, val_losses, train_accuracies, val_accuracies, save_path):
    """
    Plots Loss and Accuracy graphs for both training and validation.
    """
    epochs = range(1, len(train_losses) + 1)

    # Plot Loss
    plt.figure(figsize=(10, 5))
    plt.plot(epochs, train_losses, label="Train Loss")
    plt.plot(epochs, val_losses, label="Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Loss Over Epochs")
    plt.legend()
    plt.grid(True)

    if save_path:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(os.path.join(save_path, "loss_finetiuned.png"))
        print(f"Loss plot saved to: {os.path.join(save_path, 'loss.png')}")
    else:
        plt.show()

    plt.close()

    # Plot Accuracy
    plt.figure(figsize=(10, 5))
    plt.plot(epochs, train_accuracies, label="Train Accuracy")
    plt.plot(epochs, val_accuracies, label="Validation Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Accuracy Over Epochs")
    plt.legend()
    plt.grid(True)

    if save_path:
        plt.savefig(os.path.join(save_path, "accuracy_finetiuned.png"))
        print(f"Accuracy plot saved to: {os.path.join(save_path, 'accuracy.png')}")
    else:
        plt.show()

    plt.close()


def main():

    ############## CONFIGURABLE PARAMETERS ##############
    #  - Adjust to your liking or pass them as arguments
    BATCH_SIZE = 16  # If GPU allows; otherwise keep 16
    NUM_EPOCHS = 30  # Train longer to better fit the dataset
    LEARNING_RATE = 3e-5  # Lower learning rate for more stable T5 fine-tuning
    WEIGHT_DECAY = 1e-3
    MAX_GRAD_NORM = 1.0
    accumulation_steps = 4
    PATIENCE = 5  # Early stopping after 5 epochs of no improvement
    FINE_TUNE_EXISTING = True

    # Paths
    TRAINED_MODEL_PATH = "/home/minidu-tissera/PycharmProjects/Research-Project/v11/QG/Models/custom_qg_model_v2.pt"
    SPLIT_DATA_DIR = "/home/minidu-tissera/PycharmProjects/Research-Project/v11/QG/Datasets/split_datasets/"
    TRAIN_FILE = os.path.join(SPLIT_DATA_DIR, "/home/minidu-tissera/PycharmProjects/Research-Project/v11/QG/Datasets/split_datasets/train_dataset.json")
    VAL_FILE = os.path.join(SPLIT_DATA_DIR, "/home/minidu-tissera/PycharmProjects/Research-Project/v11/QG/Datasets/split_datasets/val_dataset.json")
    # TEST_FILE = os.path.join(SPLIT_DATA_DIR, "/home/minidu-tissera/PycharmProjects/Research-Project/v11/Datasets/split_datasets/test_dataset.json")
    SAVE_PATH = "/home/minidu-tissera/PycharmProjects/Research-Project/v11/QG/Models/custom_qg_model_v3.pt"
    MODEL_NAME = "t5-small"
    GRAPH_SAVE_DIR = "/home/minidu-tissera/PycharmProjects/Research-Project/v11/QG/Models/Graphs/"
    BEST_MODEL_PATH = "/home/minidu-tissera/PycharmProjects/Research-Project/v11/QG/Models/custom_qg_model_best.pt"
    CHECKPOINT_BASE = "/home/minidu-tissera/PycharmProjects/Research-Project/v11/QG/Models/checkpoints"
    #####################################################

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 1. Load the tokenizer
    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)

    # Optional: Add special tokens for [SAQ], [JSQ]
    special_tokens_dict = {"additional_special_tokens": ["[SAQ]", "[JSQ]"]}
    tokenizer.add_special_tokens(special_tokens_dict)

    # 2. Build your custom model (do NOT resize yet)
    config = T5Config.from_pretrained(MODEL_NAME)
    model = CustomT5WithStyle(config, style_emb_size=32)

    if FINE_TUNE_EXISTING and os.path.exists(TRAINED_MODEL_PATH):
        # If a previously trained checkpoint exists, let's load it directly
        print(f"Loading existing trained model from: {TRAINED_MODEL_PATH}")

        model.resize_token_embeddings(len(tokenizer))

        state_dict = torch.load(TRAINED_MODEL_PATH, map_location="cpu")
        model.load_state_dict(state_dict)
        print("Loaded existing checkpoint for further fine-tuning.")
    else:
        # 3. No checkpoint found, so load the base T5-small weights FIRST
        print("No existing checkpoint found (or FINE_TUNE_EXISTING=False). Using base T5-small.")
        load_pretrained_t5_small_into_custom(model)

        # 4. Now resize token embeddings after loading weights
        model.resize_token_embeddings(len(tokenizer))

        # 5. (Optional) Freeze some encoder layers
        freeze_encoder_layers(model, num_layers_to_freeze=3)

    # 6. Load the split datasets
    train_dataset = QGDataset(TRAIN_FILE, tokenizer, max_length=128)
    val_dataset = QGDataset(VAL_FILE, tokenizer, max_length=128)
    # test_dataset = QGDataset(TEST_FILE, tokenizer, max_length=64)

    train_dataloader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    # test_dataloader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # 7. Training setup
    model.to(device)

    # Optimizer with Weight Decay
    optimizer = optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY  # Applies weight decay
    )

    # Learning Rate Scheduler
    # ReduceLROnPlateau reduces LR when a metric has stopped improving
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=0.01,  # Factor by which the learning rate will be reduced
        patience=5,  # Number of epochs with no improvement after which LR will be reduced
    )

    # Initialize lists to store losses and accuracies
    train_losses = []
    val_losses = []
    train_accuracies = []
    val_accuracies = []

    print("=== GRADIENTS BEFORE BACKWARD ===")
    for name, param in model.named_parameters():
        # Look for custom-layer names. Adjust as needed for your model.
        if "style_embeddings" in name or "adapter" in name:
            # Before backward pass, gradients should be None or zero.
            if param.grad is None:
                print(f"{name} grad is None (no backward yet).")
            else:
                grad_mean = param.grad.abs().mean().item()
                print(f"{name} grad mean before = {grad_mean:.6f}")

    # Initialize variables for early stopping
    best_val_loss = float('inf')
    trigger_times = 0

    # 8. Train/fine-tune for a few epochs
    for epoch in range(NUM_EPOCHS):
        print(f"\nEpoch {epoch + 1}/{NUM_EPOCHS}")
        print("-" * 20)

        # Training
        avg_train_loss = train_one_epoch(
            model,
            train_dataloader,
            optimizer,
            device,
            max_grad_norm=MAX_GRAD_NORM  # Apply gradient clipping
        )
        train_losses.append(avg_train_loss)

        # Training Accuracy
        train_accuracy = calculate_accuracy(model, train_dataloader, device)
        train_accuracies.append(train_accuracy)

        # Validation
        avg_val_loss = evaluate(model, val_dataloader, device)
        val_losses.append(avg_val_loss)

        # Validation Accuracy
        val_accuracy = calculate_accuracy(model, val_dataloader, device)
        val_accuracies.append(val_accuracy)

        print(f"Train Loss: {avg_train_loss:.4f}, Train Accuracy: {train_accuracy:.4f}")
        print(f"Validation Loss: {avg_val_loss:.4f}, Validation Animalccuracy: {val_accuracy:.4f}")

        # Scheduler step based on validation loss
        scheduler.step(avg_val_loss)

        # Retrieve and print the current learning rate
        current_lr = scheduler.get_last_lr()[0]
        print(f"Current Learning Rate: {current_lr}")

        # Save checkpoint every 10 epochs
        if (epoch + 1) % 10 == 0:
            checkpoint_path = f"{CHECKPOINT_BASE}{epoch + 1}.pt"
            torch.save(model.state_dict(), checkpoint_path)
            print(f"Checkpoint saved at epoch {epoch + 1} -> {checkpoint_path}")

        # # Early stopping condition
        # if avg_val_loss < best_val_loss:
        #     best_val_loss = avg_val_loss
        #     trigger_times = 0
        #     # Save the best model
        #     torch.save(model.state_dict(), BEST_MODEL_PATH)
        #     print(f"Best model updated and saved to {BEST_MODEL_PATH}")
        # else:
        #     trigger_times += 1
        #     print(f"No improvement in validation loss for {trigger_times} epoch(s).")
        #
        #     if trigger_times >= PATIENCE:
        #         print("Early stopping triggered.")
        #         break

    print("\n=== GRADIENTS AFTER BACKWARD ===")
    for name, param in model.named_parameters():
        if "style_embeddings" in name or "adapter" in name:
            if param.grad is None:
                print(f"{name} grad is None after backward (unexpected if layer is used).")
            else:
                grad_mean = param.grad.abs().mean().item()
                print(f"{name} grad mean after = {grad_mean:.6f}")


    # 9. Save the trained/fine-tuned model
    torch.save(model.state_dict(), SAVE_PATH)
    print(f"\nModel saved to {SAVE_PATH}")

    # 10. Plot metrics
    plot_metrics(
        train_losses=train_losses,
        val_losses=val_losses,
        train_accuracies=train_accuracies,
        val_accuracies=val_accuracies,
        save_path=GRAPH_SAVE_DIR
    )

    # # 11. Evaluate on Test Set (Optional)
    # print("\n=== Evaluating on Test Set ===")
    # test_loss = evaluate(model, test_dataloader, device)
    # test_accuracy = calculate_accuracy(model, test_dataloader, device)
    # print(f"Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.4f}")

    # Optionally, save test metrics or further analyze test results

if __name__ == "__main__":
    main()
