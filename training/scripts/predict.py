import json
import sys
from pathlib import Path

from transformers import pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIRECTORY = (
    PROJECT_ROOT / "training/output/final-model"
)


def main():
    if len(sys.argv) > 1:
        sentence = " ".join(sys.argv[1:])
    else:
        sentence = (
            "Installer des moustiquaires dans la salle de pause "
            "avec des cadres amovibles pour mieux récupérer."
        )

    extractor = pipeline(
        task="token-classification",
        model=str(MODEL_DIRECTORY),
        tokenizer=str(MODEL_DIRECTORY),
        aggregation_strategy="simple",
        device="cpu",
    )

    predictions = extractor(sentence)

    result = {
        "text": sentence,
        "entities": [
            {
                "label": prediction["entity_group"],
                "text": sentence[
                    prediction["start"]:prediction["end"]
                ],
                "score": round(
                    float(prediction["score"]),
                    4,
                ),
                "start": prediction["start"],
                "end": prediction["end"],
            }
            for prediction in predictions
        ],
    }

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()