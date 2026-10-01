import json
import random
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "data/legacy/raw/pilot.jsonl"
OUTPUT_DIRECTORY = PROJECT_ROOT / "data/legacy/processed"

RANDOM_SEED = 42


def load_examples(path):
    with path.open(encoding="utf-8") as dataset_file:
        return [
            json.loads(line)
            for line in dataset_file
            if line.strip()
        ]


def write_jsonl(path, examples):
    with path.open("w", encoding="utf-8") as output_file:
        for example in examples:
            output_file.write(
                json.dumps(example, ensure_ascii=False) + "\n"
            )


def main():
    examples = load_examples(INPUT_PATH)

    examples_by_group = defaultdict(list)

    for example in examples:
        examples_by_group[example["group"]].append(example)

    groups = sorted(examples_by_group)
    random.Random(RANDOM_SEED).shuffle(groups)

    group_count = len(groups)
    train_end = round(group_count * 0.70)
    validation_end = train_end + round(group_count * 0.15)

    split_groups = {
        "train": groups[:train_end],
        "validation": groups[train_end:validation_end],
        "test": groups[validation_end:],
    }

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    all_assigned_groups = set()

    for split_name, selected_groups in split_groups.items():
        overlap = all_assigned_groups.intersection(selected_groups)

        if overlap:
            raise ValueError(
                f"Groupes présents dans plusieurs ensembles : {overlap}"
            )

        all_assigned_groups.update(selected_groups)

        split_examples = []

        for group in selected_groups:
            split_examples.extend(examples_by_group[group])

        output_path = OUTPUT_DIRECTORY / f"{split_name}.jsonl"
        write_jsonl(output_path, split_examples)

        print(
            f"{split_name}: "
            f"{len(split_examples)} exemples, "
            f"{len(selected_groups)} groupes"
        )

    if all_assigned_groups != set(groups):
        raise ValueError("Certains groupes n’ont pas été affectés")


if __name__ == "__main__":
    main()