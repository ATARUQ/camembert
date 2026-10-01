import json
import sys
from pathlib import Path

import pytest
from transformers import AutoTokenizer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "training/scripts"))

from bio import (  # noqa: E402
    ENTITY_TYPES,
    ID_TO_LABEL,
    LABEL_TO_ID,
    LABELS,
    align_labels,
    decode_bio,
)
from train import MODEL_ID  # noqa: E402

DATASET_PATH = PROJECT_ROOT / "data/grille_v2/dataset_full.jsonl"


def load_examples():
    with DATASET_PATH.open(encoding="utf-8") as dataset_file:
        return [
            json.loads(line)
            for line in dataset_file
            if line.strip()
        ]


EXAMPLES = load_examples()


@pytest.fixture(scope="module")
def tokenizer():
    return AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)


def test_label_set():
    assert len(LABELS) == 11
    assert LABELS[0] == "O"
    assert set(ENTITY_TYPES) == {
        "ACTION",
        "OBJET",
        "MOYEN",
        "BENEFICIAIRE",
        "FINALITE",
    }
    assert all(
        ID_TO_LABEL[LABEL_TO_ID[label]] == label
        for label in LABELS
    )


def test_dataset_is_complete():
    assert len(EXAMPLES) == 170


@pytest.mark.parametrize(
    "example",
    EXAMPLES,
    ids=[example["id"] for example in EXAMPLES],
)
def test_bio_round_trip(example, tokenizer):
    encoded = align_labels(example, tokenizer, keep_offsets=True)
    text = example["text"]

    special_tokens = set(
        tokenizer.all_special_ids
    )

    for token_id, label_id in zip(
        encoded["input_ids"],
        encoded["labels"],
    ):
        if token_id in special_tokens:
            assert label_id == -100

    decoded = [
        (entity["label"], text[entity["start"]:entity["end"]])
        for entity in decode_bio(
            encoded["labels"],
            encoded["offset_mapping"],
        )
    ]

    expected = [
        (entity["label"], entity["text"])
        for entity in sorted(
            example["entities"],
            key=lambda entity: entity["start"],
        )
    ]

    assert decoded == expected
