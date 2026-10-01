import "./style.css";

import {
  extractEntities,
  loadExtractor,
} from "./inference.js";

const LABELS = [
  "ACTION",
  "OBJET",
  "MOYEN",
  "BENEFICIAIRE",
  "FINALITE",
];

const LABEL_NAMES = {
  ACTION: "Action",
  OBJET: "Objet",
  MOYEN: "Moyen",
  BENEFICIAIRE: "Bénéficiaire",
  FINALITE: "Finalité",
};

document.querySelector("#app").innerHTML = `
  <main>
    <header class="page-header">
      <p class="eyebrow">CamemBERT spécialisé</p>
      <h1>Analyse d’une proposition</h1>
      <p class="introduction">
        Le modèle extrait localement cinq segments :
        l’action, l’objet, le moyen, le bénéficiaire et la finalité.
      </p>
    </header>

    <section class="model-panel">
      <div>
        <h2>Modèle local</h2>
        <p id="status" role="status" aria-live="polite">
          Le modèle n’est pas encore chargé.
        </p>
      </div>

      <button id="load-model" type="button">
        Charger le modèle
      </button>
    </section>

    <div class="progress-track" id="progress-track" hidden>
      <span id="progress-bar"></span>
    </div>

    <section class="analysis-panel">
      <label for="proposal">Proposition à analyser</label>

      <textarea
        id="proposal"
        rows="6"
        disabled
      >Installer des moustiquaires dans la salle de pause avec des cadres amovibles pour mieux récupérer.</textarea>

      <button id="analyze" type="button" disabled>
        Analyser la proposition
      </button>
    </section>

    <section id="result" hidden>
      <div class="result-header">
        <div>
          <p class="eyebrow">Extraction du modèle</p>
          <h2>Résultat de l’analyse</h2>
        </div>

        <span class="result-badge">
          Traitement local
        </span>
      </div>

      <div
        id="highlighted-text"
        class="highlighted-text"
      ></div>

      <dl class="entity-grid">
        ${LABELS.map(
  (label) => `
            <div class="entity-card entity-${label.toLowerCase()}">
              <dt>${LABEL_NAMES[label]}</dt>
              <dd id="value-${label.toLowerCase()}"></dd>
              <small id="score-${label.toLowerCase()}"></small>
            </div>
          `
).join("")}
      </dl>

      <details class="technical-details">
        <summary>Données techniques au format JSON</summary>
        <pre id="technical-json"></pre>
      </details>
    </section>
  </main>
`;

const loadButton =
  document.querySelector("#load-model");
const analyzeButton =
  document.querySelector("#analyze");
const proposalInput =
  document.querySelector("#proposal");
const statusOutput =
  document.querySelector("#status");
const progressTrack =
  document.querySelector("#progress-track");
const progressBar =
  document.querySelector("#progress-bar");
const resultSection =
  document.querySelector("#result");
const highlightedText =
  document.querySelector("#highlighted-text");
const technicalJson =
  document.querySelector("#technical-json");

function updateProgress(progress) {
  if (progress.status === "progress") {
    progressTrack.hidden = false;

    const percentage = Math.round(
      Number(progress.progress ?? 0)
    );

    progressBar.style.width = `${percentage}%`;
    statusOutput.textContent =
      `Chargement du modèle : ${percentage} %`;
    return;
  }

  if (progress.status === "ready") {
    statusOutput.textContent =
      "Préparation du modèle…";
  }
}

function groupEntities(entities) {
  const grouped = Object.fromEntries(
    LABELS.map((label) => [label, []])
  );

  for (const entity of entities) {
    if (grouped[entity.label]) {
      grouped[entity.label].push(entity);
    }
  }

  return grouped;
}

function renderEntityCards(groupedEntities) {
  for (const label of LABELS) {
    const entities = groupedEntities[label];
    const valueOutput = document.querySelector(
      `#value-${label.toLowerCase()}`
    );
    const scoreOutput = document.querySelector(
      `#score-${label.toLowerCase()}`
    );

    valueOutput.textContent = entities
      .map((entity) => entity.text)
      .join(" · ");

    if (entities.length === 0) {
      scoreOutput.textContent = "";
      continue;
    }

    const averageScore =
      entities.reduce(
        (total, entity) =>
          total + Number(entity.score),
        0
      ) / entities.length;

    scoreOutput.textContent =
      `Confiance : ${Math.round(averageScore * 100)} %`;
  }
}

function renderHighlightedText(text, entities) {
  highlightedText.replaceChildren();

  const sortedEntities = [...entities].sort(
    (first, second) =>
      first.start - second.start
  );

  let cursor = 0;

  for (const entity of sortedEntities) {
    if (
      !Number.isInteger(entity.start) ||
      !Number.isInteger(entity.end) ||
      entity.start < cursor ||
      entity.end <= entity.start
    ) {
      continue;
    }

    highlightedText.append(
      document.createTextNode(
        text.slice(cursor, entity.start)
      )
    );

    const mark = document.createElement("mark");
    mark.className =
      `highlight-${entity.label.toLowerCase()}`;
    mark.textContent = text.slice(
      entity.start,
      entity.end
    );
    mark.title =
      `${LABEL_NAMES[entity.label]} — ` +
      `${Math.round(Number(entity.score) * 100)} %`;

    highlightedText.append(mark);
    cursor = entity.end;
  }

  highlightedText.append(
    document.createTextNode(text.slice(cursor))
  );
}

loadButton.addEventListener("click", async () => {
  loadButton.disabled = true;
  statusOutput.textContent =
    "Chargement du modèle…";
  progressTrack.hidden = false;

  try {
    await loadExtractor(updateProgress);

    progressBar.style.width = "100%";
    statusOutput.textContent =
      "Le modèle est prêt.";
    proposalInput.disabled = false;
    analyzeButton.disabled = false;
    loadButton.textContent = "Modèle chargé";
  } catch (error) {
    console.error(error);
    statusOutput.textContent =
      `Erreur de chargement : ${error.message}`;
    loadButton.disabled = false;
  }
});

analyzeButton.addEventListener("click", async () => {
  const text = proposalInput.value.trim();

  if (!text) {
    statusOutput.textContent =
      "Saisissez une proposition à analyser.";
    proposalInput.focus();
    return;
  }

  analyzeButton.disabled = true;
  statusOutput.textContent =
    "Analyse en cours…";

  try {
    const entities = await extractEntities(text);
    const groupedEntities =
      groupEntities(entities);

    renderEntityCards(groupedEntities);
    renderHighlightedText(text, entities);

    technicalJson.textContent = JSON.stringify(
      {
        text,
        entities,
      },
      null,
      2
    );

    resultSection.hidden = false;
    statusOutput.textContent =
      "Analyse terminée.";

    resultSection.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  } catch (error) {
    console.error(error);
    statusOutput.textContent =
      `Erreur d’analyse : ${error.message}`;
  } finally {
    analyzeButton.disabled = false;
  }
});