import argparse
import json
from pathlib import Path

import numpy as np
import torch
from datasets import load_dataset
from seqeval.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    Trainer,
    TrainingArguments,
    set_seed,
)

from bio import (
    ENTITY_TYPES,
    ID_TO_LABEL,
    LABEL_TO_ID,
    LABELS,
    align_labels,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIRECTORY = PROJECT_ROOT / "data/grille_v2"
DEFAULT_OUTPUT_DIRECTORY = PROJECT_ROOT / "training/output"

MODEL_ID = "almanach/camembert-base"
RANDOM_SEED = 42
NUM_TRAIN_EPOCHS = 30

def compute_metrics(evaluation_prediction):
    logits, label_ids = evaluation_prediction
    prediction_ids = np.argmax(logits, axis=-1)

    true_predictions = []
    true_labels = []

    for predictions, labels in zip(
        prediction_ids,
        label_ids,
    ):
        sentence_predictions = []
        sentence_labels = []

        for prediction_id, label_id in zip(
            predictions,
            labels,
        ):
            if label_id == -100:
                continue

            sentence_predictions.append(
                ID_TO_LABEL[int(prediction_id)]
            )
            sentence_labels.append(
                ID_TO_LABEL[int(label_id)]
            )

        true_predictions.append(sentence_predictions)
        true_labels.append(sentence_labels)

    report = classification_report(
        true_labels,
        true_predictions,
        output_dict=True,
        zero_division=0,
    )

    per_entity_f1 = {
        f"f1_{entity_type.lower()}": report.get(
            entity_type,
            {},
        ).get("f1-score", 0.0)
        for entity_type in ENTITY_TYPES
    }

    return {
        "precision": precision_score(
            true_labels,
            true_predictions,
        ),
        "recall": recall_score(
            true_labels,
            true_predictions,
        ),
        "f1": f1_score(
            true_labels,
            true_predictions,
        ),
        "accuracy": accuracy_score(
            true_labels,
            true_predictions,
        ),
        **per_entity_f1,
    }


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--epochs",
        type=float,
        default=NUM_TRAIN_EPOCHS,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
    )
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    checkpoint_directory = arguments.output_dir / "checkpoints"
    final_model_directory = arguments.output_dir / "final-model"
    evaluation_directory = arguments.output_dir / "evaluation"

    set_seed(RANDOM_SEED)

    print(f"PyTorch : {torch.__version__}")
    print(f"MPS disponible : {torch.backends.mps.is_available()}")
    print(f"Modèle de base : {MODEL_ID}")

    data_files = {
        "train": str(DATA_DIRECTORY / "train.jsonl"),
        "validation": str(DATA_DIRECTORY / "dev.jsonl"),
    }

    dataset = load_dataset(
        "json",
        data_files=data_files,
    )

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        use_fast=True,
    )

    tokenized_dataset = dataset.map(
        lambda example: align_labels(
            example,
            tokenizer,
        ),
        remove_columns=dataset["train"].column_names,
        desc="Alignement des annotations",
    )

    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_ID,
        num_labels=len(LABELS),
        id2label=ID_TO_LABEL,
        label2id=LABEL_TO_ID,
    )

    data_collator = DataCollatorForTokenClassification(
        tokenizer=tokenizer
    )

    training_arguments = TrainingArguments(
        output_dir=str(checkpoint_directory),
        learning_rate=5e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=arguments.epochs,
        weight_decay=0.01,
        warmup_ratio=0.1,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=2,
        report_to="none",
        seed=RANDOM_SEED,
        data_seed=RANDOM_SEED,
    )

    trainer = Trainer(
        model=model,
        args=training_arguments,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
        data_collator=data_collator,
        processing_class=tokenizer,
        compute_metrics=compute_metrics,
    )

    trainer.train()

    final_model_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    trainer.save_model(final_model_directory)
    tokenizer.save_pretrained(final_model_directory)

    # Pas de jeu de test distinct : dev sert aussi à choisir le meilleur
    # checkpoint, ces chiffres sont donc légèrement optimistes.
    dev_metrics = trainer.evaluate(
        tokenized_dataset["validation"],
        metric_key_prefix="dev",
    )

    evaluation_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_path = (
        evaluation_directory / "dev-metrics.json"
    )

    with metrics_path.open(
        "w",
        encoding="utf-8",
    ) as metrics_file:
        json.dump(
            dev_metrics,
            metrics_file,
            ensure_ascii=False,
            indent=2,
        )

    print("Modèle enregistré dans :")
    print(final_model_directory)
    print("Résultats sur dev :")
    print(json.dumps(dev_metrics, indent=2))


if __name__ == "__main__":
    main()
