import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from sklearn.metrics import accuracy_score

# Initialize device and model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load model and tokenizer
model_name = 'Model/fine_tuned_model'
tokenizer_name = 'Model/tokenizer'

model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

# Load test dataset
test_file_path = 'Datasets/testData.json'

with open(test_file_path, 'r') as f:
    test_data = json.load(f)


# Dataset class
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, passages, questions, tokenizer, max_length=512):
        self.passages = passages
        self.questions = questions
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.passages)

    def __getitem__(self, idx):
        passage = self.passages[idx]
        question_data = self.questions[idx]
        question_text = question_data['question']

        # Tokenize passage + question
        combined_input = passage + " " + question_text
        encoding = self.tokenizer(
            combined_input,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        # Handle MCQ or short-answer
        if 'options' in question_data:
            options = question_data['options']
            encoded_options = [
                self.tokenizer(
                    option,
                    truncation=True,
                    padding='max_length',
                    max_length=self.max_length,
                    return_tensors='pt'
                ) for option in options
            ]
            return {
                'input_ids': encoding['input_ids'].squeeze(),
                'attention_mask': encoding['attention_mask'].squeeze(),
                'options': encoded_options,
                'answer': question_data['answer']
            }
        else:
            return {
                'input_ids': encoding['input_ids'].squeeze(),
                'attention_mask': encoding['attention_mask'].squeeze(),
                'answer': question_data['answer']
            }


# Prepare data
test_passages = []
test_questions = []
for entry in test_data:
    passage = entry['passage']
    for question in entry['questions']:
        test_passages.append(passage)
        test_questions.append(question)


def custom_collate_fn(batch):
    batch_dict = {
        'input_ids': [],
        'attention_mask': [],
        'answer': [],
        'options': []
    }

    for item in batch:
        batch_dict['input_ids'].append(item['input_ids'])
        batch_dict['attention_mask'].append(item['attention_mask'])
        batch_dict['answer'].append(item['answer'])
        if 'options' in item:
            batch_dict['options'].append(item['options'])
        else:
            batch_dict['options'].append(None)

    # Stack tensors for inputs and masks
    batch_dict['input_ids'] = torch.stack(batch_dict['input_ids'])
    batch_dict['attention_mask'] = torch.stack(batch_dict['attention_mask'])
    return batch_dict


# Create DataLoader
test_dataset = CustomDataset(test_passages, test_questions, tokenizer)
test_dataloader = DataLoader(test_dataset, batch_size=8, collate_fn=custom_collate_fn)


# Evaluation function
def evaluate_model(model, dataloader):
    model.eval()
    total_loss = 0
    all_preds = []
    all_answers = []

    for batch in dataloader:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        answers = batch['answer']

        with torch.no_grad():
            outputs = model(input_ids, attention_mask=attention_mask, labels=input_ids)
            loss = outputs.loss
            logits = outputs.logits

        total_loss += loss.item()

        # Get predicted text
        predicted_ids = torch.argmax(logits, dim=-1)
        predicted_texts = [tokenizer.decode(pred_id, skip_special_tokens=True) for pred_id in predicted_ids]

        for i, pred_text in enumerate(predicted_texts):
            true_answer = answers[i]
            all_preds.append(pred_text.strip().lower())
            all_answers.append(true_answer.strip().lower())

    # Calculate metrics
    avg_loss = total_loss / len(dataloader)
    print(f"Average Loss: {avg_loss:.4f}")

    accuracy = accuracy_score(all_answers, all_preds)
    print(f"Overall Accuracy: {accuracy:.4f}")

    # Optional: Separate metrics for MCQs and short-answer
    mcq_correct = 0
    short_correct = 0
    total_mcq = 0
    total_short = 0

    for i, pred in enumerate(all_preds):
        true_answer = all_answers[i]
        if 'options' in test_questions[i]:  # MCQ
            total_mcq += 1
            if pred == true_answer:
                mcq_correct += 1
        else:  # Short-answer
            total_short += 1
            if pred == true_answer:
                short_correct += 1

    mcq_accuracy = mcq_correct / total_mcq if total_mcq > 0 else 0
    short_accuracy = short_correct / total_short if total_short > 0 else 0

    print(f"MCQ Accuracy: {mcq_accuracy:.4f}")
    print(f"Short Answer Accuracy: {short_accuracy:.4f}")


# Evaluate model
evaluate_model(model, test_dataloader)
