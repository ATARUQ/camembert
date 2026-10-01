ENTITY_TYPES = [
    "ACTION",
    "OBJET",
    "MOYEN",
    "BENEFICIAIRE",
    "FINALITE",
]

LABELS = ["O"] + [
    f"{prefix}-{entity_type}"
    for entity_type in ENTITY_TYPES
    for prefix in ("B", "I")
]

LABEL_TO_ID = {
    label: index
    for index, label in enumerate(LABELS)
}

ID_TO_LABEL = {
    index: label
    for index, label in enumerate(LABELS)
}

MAX_LENGTH = 256


def find_entity_for_token(token_start, token_end, entities):
    for entity_index, entity in enumerate(entities):
        entity_start = entity["start"]
        entity_end = entity["end"]

        overlaps = (
            token_start < entity_end
            and token_end > entity_start
        )

        if overlaps:
            return entity_index, entity

    return None, None


def align_labels(example, tokenizer, keep_offsets=False):
    encoded = tokenizer(
        example["text"],
        truncation=True,
        max_length=MAX_LENGTH,
        return_offsets_mapping=True,
    )

    token_labels = []
    previous_entity_index = None

    for token_start, token_end in encoded["offset_mapping"]:
        if token_start == token_end:
            token_labels.append(-100)
            previous_entity_index = None
            continue

        entity_index, entity = find_entity_for_token(
            token_start,
            token_end,
            example["entities"],
        )

        if entity is None:
            token_labels.append(LABEL_TO_ID["O"])
            previous_entity_index = None
            continue

        prefix = (
            "B"
            if entity_index != previous_entity_index
            else "I"
        )

        label = f"{prefix}-{entity['label']}"
        token_labels.append(LABEL_TO_ID[label])
        previous_entity_index = entity_index

    if not keep_offsets:
        encoded.pop("offset_mapping")

    encoded["labels"] = token_labels
    return encoded


def decode_bio(label_ids, offset_mapping):
    """Reconstruit les segments (start, end, label) en offsets caractères."""
    entities = []
    current = None

    for label_id, (token_start, token_end) in zip(
        label_ids,
        offset_mapping,
    ):
        if label_id == -100:
            continue

        label = ID_TO_LABEL[int(label_id)]

        if label == "O":
            current = None
            continue

        prefix, entity_type = label.split("-", 1)

        if (
            prefix == "I"
            and current is not None
            and current["label"] == entity_type
        ):
            current["end"] = token_end
            continue

        current = {
            "start": token_start,
            "end": token_end,
            "label": entity_type,
        }
        entities.append(current)

    return entities
