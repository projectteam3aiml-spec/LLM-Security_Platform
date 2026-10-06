"""Trains the DistilBERT security classifier and writes best_model/ + tokenizer/ +
training_history.csv/training_loss.png/validation_accuracy.png/training_summary.txt
to outputs/security_classifier/.

Adapted from notebooks/05_train_security_classifier.ipynb: that notebook hardcoded
PROJECT_ROOT to a different machine's path (C:\\Users\\raich\\Desktop\\major\\...),
which doesn't exist here, so this script resolves paths relative to itself instead.
Training hyperparameters (4 epochs, batch 16, lr 2e-5, class-weighted loss) are kept
identical to the original notebook for fidelity.
"""
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from torch import nn
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
    set_seed,
)


def find_data_root(start: Path, marker: str = "Healthcare_Dataset_Preparation") -> Path:
    for candidate in (start, *start.parents):
        if candidate.name == marker:
            return candidate
        if (candidate / marker).is_dir():
            return candidate / marker
    raise FileNotFoundError(f"Could not locate '{marker}' starting from {start}")


BASE_DIR = find_data_root(Path(__file__).resolve())
PROCESSED = BASE_DIR / "data" / "processed"
OUTPUT = BASE_DIR / "outputs" / "security_classifier"
MODEL_OUTPUT = OUTPUT / "best_model"
TOKENIZER_OUTPUT = OUTPUT / "tokenizer"
OUTPUT.mkdir(parents=True, exist_ok=True)
MODEL_OUTPUT.mkdir(parents=True, exist_ok=True)
TOKENIZER_OUTPUT.mkdir(parents=True, exist_ok=True)

SEED = 42
# "distilbert-base-uncased" (hub id) works too, but huggingface_hub's default symlink-based
# cache silently produces an empty snapshots/ dir on this Windows setup (no symlink privilege),
# so we point at a plain local_dir download instead: see scripts/download_base_model.py.
MODEL_NAME = os.environ.get("BASE_MODEL_PATH", r"C:\dbu")
MAX_LENGTH = 256


def main():
    set_seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    train_df = pd.read_csv(PROCESSED / "security_train_processed.csv")
    validation_df = pd.read_csv(PROCESSED / "security_validation_processed.csv")
    test_df = pd.read_csv(PROCESSED / "security_test_processed.csv")
    print("Train:", train_df.shape, "Validation:", validation_df.shape, "Test:", test_df.shape)

    # Explicit mapping, not LabelEncoder -- must match how `label` was actually
    # encoded into the processed CSVs. Verified two ways before trusting it:
    # (1) it's the file the original preprocessing notebook produced for this purpose,
    # (2) independently confirmed against raw prompt text: label==2 rows are all
    # name/DOB/phone-style PHI, label==3 rows are all "pretend you're not an AI",
    # "developer mode", "obey my next command" jailbreak text. The current
    # best_model/config.json disagrees with this (claims 0=jailbreak/3=safe) but
    # that config.json belongs to an orphaned run with no weights and validation/test
    # row counts that don't match today's processed CSVs -- it's stale, not authoritative.
    label_mapping = pd.read_csv(BASE_DIR / "outputs" / "tokenized" / "label_mapping.csv")
    label2id = dict(zip(label_mapping["attack_type"], label_mapping["label"]))
    id2label = {int(v): k for k, v in label2id.items()}
    print("label2id:", label2id)

    assert sorted(train_df["label"].unique()) == sorted(id2label.keys()), "label_mapping.csv does not cover all labels present in the training data"

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    train_dataset = Dataset.from_pandas(train_df[["prompt", "label"]], preserve_index=False)
    validation_dataset = Dataset.from_pandas(validation_df[["prompt", "label"]], preserve_index=False)

    def tokenize_function(examples):
        return tokenizer(examples["prompt"], truncation=True, max_length=MAX_LENGTH)

    train_dataset = train_dataset.map(tokenize_function, batched=True, remove_columns=["prompt"])
    validation_dataset = validation_dataset.map(tokenize_function, batched=True, remove_columns=["prompt"])

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    class_counts = train_df["label"].value_counts().sort_index()
    num_classes = len(label2id)
    total_samples = len(train_df)
    class_weights = (total_samples / (num_classes * class_counts)).sort_index()
    class_weights_tensor = torch.tensor(class_weights.values, dtype=torch.float)
    print("Class weights:", dict(class_weights))

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=num_classes, id2label=id2label, label2id=label2id
    )

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        accuracy = accuracy_score(labels, predictions)
        precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
            labels, predictions, average="macro", zero_division=0
        )
        precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
            labels, predictions, average="weighted", zero_division=0
        )
        return {
            "accuracy": accuracy,
            "precision_macro": precision_macro,
            "recall_macro": recall_macro,
            "f1_macro": f1_macro,
            "precision_weighted": precision_weighted,
            "recall_weighted": recall_weighted,
            "f1_weighted": f1_weighted,
        }

    class WeightedTrainer(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
            labels = inputs.get("labels")
            outputs = model(**inputs)
            logits = outputs.get("logits")
            weights = class_weights_tensor.to(logits.device)
            loss_function = nn.CrossEntropyLoss(weight=weights)
            loss = loss_function(logits.view(-1, model.config.num_labels), labels.view(-1))
            return (loss, outputs) if return_outputs else loss

    training_args = TrainingArguments(
        output_dir=str(OUTPUT),
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        num_train_epochs=4,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        save_total_limit=2,
        report_to="none",
        fp16=torch.cuda.is_available(),
        seed=SEED,
    )

    trainer = WeightedTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    validation_results = trainer.evaluate(validation_dataset)
    print("Validation results:", validation_results)

    trainer.save_model(str(MODEL_OUTPUT))
    tokenizer.save_pretrained(str(TOKENIZER_OUTPUT))
    print("Best model saved to", MODEL_OUTPUT)

    history = pd.DataFrame(trainer.state.log_history)
    history.to_csv(OUTPUT / "training_history.csv", index=False)

    loss_history = history[history["loss"].notna()]
    plt.figure(figsize=(9, 5))
    plt.plot(loss_history["epoch"], loss_history["loss"], marker="o")
    plt.xlabel("Epoch")
    plt.ylabel("Training Loss")
    plt.title("Training Loss")
    plt.tight_layout()
    plt.savefig(OUTPUT / "training_loss.png", dpi=300)
    plt.close()

    eval_history = [log for log in trainer.state.log_history if "eval_accuracy" in log]
    plt.figure(figsize=(9, 5))
    plt.plot([log["epoch"] for log in eval_history], [log["eval_accuracy"] for log in eval_history], marker="o")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Validation Accuracy")
    plt.tight_layout()
    plt.savefig(OUTPUT / "validation_accuracy.png", dpi=300)
    plt.close()

    best_f1 = max(log["eval_f1_macro"] for log in eval_history)
    best_accuracy = max(log["eval_accuracy"] for log in eval_history)
    summary = f"""
========================================
SECURITY CLASSIFIER TRAINING SUMMARY
========================================

Model:
{MODEL_NAME}

Maximum Sequence Length:
{MAX_LENGTH}

Training Samples:
{len(train_df)}

Validation Samples:
{len(validation_df)}

Test Samples:
{len(test_df)}

Number of Classes:
{num_classes}

Epochs:
{training_args.num_train_epochs}

Learning Rate:
{training_args.learning_rate}

Batch Size:
{training_args.per_device_train_batch_size}

Best Validation Macro F1:
{best_f1:.4f}

Best Validation Accuracy:
{best_accuracy:.4f}

Classes:
{id2label}

========================================
"""
    print(summary)
    (OUTPUT / "training_summary.txt").write_text(summary, encoding="utf-8")
    print("Training completed.")


if __name__ == "__main__":
    main()
