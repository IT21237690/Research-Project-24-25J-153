import json
import os
import random
from typing import List, Dict

def convert_and_split_dataset(
    raw_file_path: str,
    output_dir: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    seed: int = 42
):

    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1."

    # 1. Load Raw Data
    with open(raw_file_path, "r", encoding="utf-8") as rf:
        raw_data = json.load(rf)

    # 2. Transform Data
    transformed_data = []
    for item in raw_data:
        task = item["task"].strip().upper()  # "SAQ" or "JSQ"
        original_input = item["input"]
        output_text = item["output"]

        if task == "SAQ":
            style_id = 0
            # Prepend [SAQ]
            new_input = "[SAQ] " + original_input.replace("Generate a SAQ:", "").strip()
        elif task == "JSQ":
            style_id = 1
            # Prepend [JSQ]
            new_input = "[JSQ] " + original_input.replace("Generate a JSQ:", "").strip()
        else:
            # Ignore or handle unexpected tasks
            print(f"Warning: Unknown task '{task}' encountered. Skipping.")
            continue

        transformed_data.append({
            "input": new_input,
            "output": output_text,
            "style_id": style_id
        })

    print(f"Total transformed samples: {len(transformed_data)}")

    # 3. Shuffle Data
    random.seed(seed)
    random.shuffle(transformed_data)

    # 4. Split Data
    total_samples = len(transformed_data)
    train_end = int(total_samples * train_ratio)
    val_end = train_end + int(total_samples * val_ratio)

    train_data = transformed_data[:train_end]
    val_data = transformed_data[train_end:val_end]
    test_data = transformed_data[val_end:]

    print(f"Train samples: {len(train_data)}")
    print(f"Validation samples: {len(val_data)}")
    print(f"Test samples: {len(test_data)}")

    # 5. Ensure Output Directory Exists
    os.makedirs(output_dir, exist_ok=True)

    # 6. Define Output File Paths
    train_output_path = os.path.join(output_dir, "train_dataset.json")
    val_output_path = os.path.join(output_dir, "val_dataset.json")
    test_output_path = os.path.join(output_dir, "test_dataset.json")

    # 7. Save Split Datasets
    with open(train_output_path, "w", encoding="utf-8") as wf:
        json.dump(train_data, wf, indent=2, ensure_ascii=False)
    print(f"Training dataset saved to: {train_output_path}")

    with open(val_output_path, "w", encoding="utf-8") as wf:
        json.dump(val_data, wf, indent=2, ensure_ascii=False)
    print(f"Validation dataset saved to: {val_output_path}")

    with open(test_output_path, "w", encoding="utf-8") as wf:
        json.dump(test_data, wf, indent=2, ensure_ascii=False)
    print(f"Test dataset saved to: {test_output_path}")

if __name__ == "__main__":
    # Customize these paths as needed
    RAW_FILE_PATH = "/home/minidu-tissera/PycharmProjects/Research-Project/v11/Datasets/formatted_data.json"
    OUTPUT_DIR = "/home/minidu-tissera/PycharmProjects/Research-Project/v11/Datasets/split_datasets/"

    convert_and_split_dataset(
        raw_file_path=RAW_FILE_PATH,
        output_dir=OUTPUT_DIR,
        train_ratio=0.7,
        val_ratio=0.2,
        test_ratio=0.1,
        seed=42  # Set a seed for reproducibility
    )
