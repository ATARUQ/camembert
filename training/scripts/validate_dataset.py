import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "data/grille_v2/dataset_full.jsonl"

ALLOWED_LABELS = {
    "ACTION",
    "OBJET",
    "MOYEN",
    "BENEFICIAIRE",
    "FINALITE",
}

INDEX = {
    "B": ["Bp", "Bq", "Br", "Bs", "Bt"],
    "E": ["Eh", "Ek", "El", "Em", "En"],
    "R": ["Ra", "Re", "Ri", "Ro", "Ru"],
    "A": ["Ab", "Ac", "Ad", "Af", "Ag"],
}

INDEX_ORDER = [
    code
    for dimension in "BERA"
    for code in INDEX[dimension]
]


def load_examples(path):
    examples = []

    with path.open(encoding="utf-8") as dataset_file:
        for line_number, line in enumerate(dataset_file, start=1):
            if not line.strip():
                continue

            try:
                example = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Ligne {line_number} : JSON invalide : {error}"
                ) from error

            examples.append(example)

    return examples


def validate_example(example, line_number):
    required_fields = {
        "id",
        "sector",
        "text",
        "entities",
        "B",
        "E",
        "R",
        "A",
        "labels",
    }

    missing_fields = required_fields - set(example)

    if missing_fields:
        raise ValueError(
            f"Ligne {line_number} : champs absents : "
            f"{sorted(missing_fields)}"
        )

    text = example["text"]

    if not isinstance(text, str) or not text.strip():
        raise ValueError(
            f"Ligne {line_number} : texte vide ou invalide"
        )

    entities = sorted(
        example["entities"],
        key=lambda entity: entity["start"],
    )

    previous_end = 0

    for entity in entities:
        label = entity.get("label")
        start = entity.get("start")
        end = entity.get("end")

        if label not in ALLOWED_LABELS:
            raise ValueError(
                f"Ligne {line_number} : label inconnu {label!r}"
            )

        if not isinstance(start, int) or not isinstance(end, int):
            raise ValueError(
                f"Ligne {line_number} : positions non entières"
            )

        if not 0 <= start < end <= len(text):
            raise ValueError(
                f"Ligne {line_number} : positions invalides "
                f"{start}:{end}"
            )

        if start < previous_end:
            raise ValueError(
                f"Ligne {line_number} : entités qui se chevauchent"
            )

        extracted_text = text[start:end]

        if not extracted_text.strip():
            raise ValueError(
                f"Ligne {line_number} : entité vide"
            )

        if extracted_text != extracted_text.strip():
            raise ValueError(
                f"Ligne {line_number} : espace inclus dans "
                f"l’entité {label}: {extracted_text!r}"
            )

        if entity.get("text", extracted_text) != extracted_text:
            raise ValueError(
                f"Ligne {line_number} : texte de l’entité {label} "
                f"différent du segment {start}:{end}"
            )

        previous_end = end

    active_codes = []

    for dimension, allowed_codes in INDEX.items():
        codes = example[dimension]

        if not codes:
            raise ValueError(
                f"Ligne {line_number} : dimension {dimension} vide"
            )

        unknown_codes = set(codes) - set(allowed_codes)

        if unknown_codes:
            raise ValueError(
                f"Ligne {line_number} : index inconnus "
                f"{sorted(unknown_codes)} en {dimension}"
            )

        active_codes.extend(codes)

    expected_labels = [
        int(code in active_codes)
        for code in INDEX_ORDER
    ]

    if example["labels"] != expected_labels:
        raise ValueError(
            f"Ligne {line_number} : vecteur labels incohérent "
            f"avec B/E/R/A"
        )


def main():
    examples = load_examples(DATASET_PATH)

    if not examples:
        raise ValueError("Le corpus est vide")

    identifiers = [example["id"] for example in examples]
    duplicate_ids = [
        identifier
        for identifier, count in Counter(identifiers).items()
        if count > 1
    ]

    if duplicate_ids:
        raise ValueError(
            f"Identifiants dupliqués : {duplicate_ids}"
        )

    texts = [example["text"] for example in examples]
    duplicate_texts = [
        text
        for text, count in Counter(texts).items()
        if count > 1
    ]

    if duplicate_texts:
        raise ValueError(
            f"{len(duplicate_texts)} texte(s) dupliqué(s)"
        )

    for line_number, example in enumerate(examples, start=1):
        validate_example(example, line_number)

    label_counts = Counter(
        entity["label"]
        for example in examples
        for entity in example["entities"]
    )

    sector_counts = Counter(
        example["sector"]
        for example in examples
    )

    print("Corpus valide")
    print(f"Exemples : {len(examples)}")
    print("Entités :")

    for label in sorted(ALLOWED_LABELS):
        print(f"  {label}: {label_counts[label]}")

    print("Secteurs :")

    for sector, count in sorted(sector_counts.items()):
        print(f"  {sector}: {count}")


if __name__ == "__main__":
    main()