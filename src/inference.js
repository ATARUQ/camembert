import {
  env,
  pipeline,
} from "@huggingface/transformers";

env.allowLocalModels = true;
env.allowRemoteModels = false;
env.useBrowserCache = false;

env.localModelPath = import.meta.env.BASE_URL;

const MODEL_ID = "model";

let extractorPromise = null;

export function loadExtractor(progressCallback) {
  if (!extractorPromise) {
    extractorPromise = pipeline(
      "token-classification",
      MODEL_ID,
      {
        device: "wasm",
        dtype: "q8",
        progress_callback: progressCallback,
      }
    );
  }

  return extractorPromise;
}

function cleanPredictedText(value) {
  return String(value ?? "")
    .replaceAll("▁", " ")
    .replace(/\s+/g, " ")
    .trim();
}

function findPosition(text, extractedText, fromIndex) {
  const normalizedText =
    text.toLocaleLowerCase("fr");

  const normalizedExtractedText =
    extractedText.toLocaleLowerCase("fr");

  let start = normalizedText.indexOf(
    normalizedExtractedText,
    fromIndex
  );

  if (start === -1) {
    start = normalizedText.indexOf(
      normalizedExtractedText
    );
  }

  if (start === -1) {
    return {
      start: null,
      end: null,
    };
  }

  return {
    start,
    end: start + extractedText.length,
  };
}

export async function extractEntities(
  text,
  progressCallback
) {
  const extractor = await loadExtractor(
    progressCallback
  );

  const predictions = await extractor(text, {
    aggregation_strategy: "simple",
    ignore_labels: ["O"],
  });

  let searchCursor = 0;

  return predictions.map((prediction) => {
    const extractedText = cleanPredictedText(
      prediction.word
    );

    const hasValidOffsets =
      Number.isInteger(prediction.start) &&
      Number.isInteger(prediction.end) &&
      prediction.end > prediction.start;

    const reconstructedPosition =
      hasValidOffsets
        ? {
            start: prediction.start,
            end: prediction.end,
          }
        : findPosition(
            text,
            extractedText,
            searchCursor
          );

    if (reconstructedPosition.end !== null) {
      searchCursor = reconstructedPosition.end;
    }

    return {
      label:
        prediction.entity_group ??
        prediction.entity,
      text: extractedText,
      score: Number(prediction.score),
      start: reconstructedPosition.start,
      end: reconstructedPosition.end,
    };
  });
}