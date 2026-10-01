from pathlib import Path

from onnxruntime.quantization import (
    QuantType,
    quantize_dynamic,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_MODEL = (
    PROJECT_ROOT
    / "training/output/onnx/model.onnx"
)

OUTPUT_MODEL = (
    PROJECT_ROOT
    / "training/output/onnx/model_uint8.onnx"
)


def main():
    if not INPUT_MODEL.exists():
        raise FileNotFoundError(
            f"Modèle ONNX introuvable : {INPUT_MODEL}"
        )

    quantize_dynamic(
        model_input=str(INPUT_MODEL),
        model_output=str(OUTPUT_MODEL),
        weight_type=QuantType.QUInt8,
    )

    original_size = INPUT_MODEL.stat().st_size
    quantized_size = OUTPUT_MODEL.stat().st_size

    print(f"Modèle original : {original_size / 1_000_000:.1f} Mo")
    print(f"Modèle quantifié : {quantized_size / 1_000_000:.1f} Mo")
    print(f"Fichier créé : {OUTPUT_MODEL}")


if __name__ == "__main__":
    main()