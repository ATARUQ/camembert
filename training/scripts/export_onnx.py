import shutil
import sys
from pathlib import Path

from optimum.exporters.onnx import main_export


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_MODEL_DIRECTORY = (
    PROJECT_ROOT / "training/output/final-model"
)

OUTPUT_DIRECTORY = PROJECT_ROOT / "training/output/onnx"

PUBLIC_MODEL_DIRECTORY = PROJECT_ROOT / "public/model"

# Transformers.js charge onnx/model_quantized.onnx pour dtype "q8" :
# on y publie le modèle produit par quantize_onnx.py.
PUBLIC_FILES = {
    "config.json": "config.json",
    "special_tokens_map.json": "special_tokens_map.json",
    "tokenizer.json": "tokenizer.json",
    "tokenizer_config.json": "tokenizer_config.json",
    "model_uint8.onnx": "onnx/model_quantized.onnx",
}


def export():
    if not INPUT_MODEL_DIRECTORY.exists():
        raise FileNotFoundError(
            f"Modèle entraîné introuvable : {INPUT_MODEL_DIRECTORY}"
        )

    main_export(
        model_name_or_path=str(INPUT_MODEL_DIRECTORY),
        output=OUTPUT_DIRECTORY,
        task="token-classification",
    )

    print(f"Modèle ONNX exporté dans : {OUTPUT_DIRECTORY}")


def publish():
    for source_name, target_name in PUBLIC_FILES.items():
        source = OUTPUT_DIRECTORY / source_name

        if not source.exists():
            raise FileNotFoundError(
                f"Fichier introuvable : {source} "
                f"(lancer quantize_onnx.py avant --publish)"
            )

        target = PUBLIC_MODEL_DIRECTORY / target_name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        print(f"{source.name} -> {target}")


if __name__ == "__main__":
    if "--publish" in sys.argv:
        publish()
    else:
        export()
