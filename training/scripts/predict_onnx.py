import json
import sys
from pathlib import Path

from optimum.onnxruntime import (
    ORTModelForTokenClassification,
)
from transformers import AutoTokenizer, pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIRECTORY = PROJECT_ROOT / "training/output/onnx"


def main():
    if len(sys.argv) > 1:
        sentence = " ".join(sys.argv[1:])
    else:
        sentence = (
            "Installer des moustiquaires dans la salle de pause "
            "avec des cadres amovibles pour mieux récupérer."
        )

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_DIRECTORY
    )

    model = ORTModelForTokenClassification.from_pretrained(
        MODEL_DIRECTORY,
        file_name="model_uint8.onnx",
    )

    extractor = pipeline(
        "token-classification",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple",
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