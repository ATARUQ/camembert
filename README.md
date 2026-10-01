# CamemBERT — extraction de propositions viticoles

Ce projet entraîne un modèle CamemBERT spécialisé pour extraire quatre dimensions dans des propositions formulées par les salariés d’un domaine viticole :

- `ACTION` : ce qui doit être fait ;
- `OBJET` : ce sur quoi porte l’action ;
- `MOYEN` : la ressource ou la méthode utilisée ;
- `RESULTAT` : l’amélioration recherchée.

Le modèle entraîné est converti en ONNX, quantifié puis exécuté directement dans le navigateur avec Transformers.js.

## Structure du projet

```text
camembert/
├── src/                         Application web
├── public/model/                Modèle utilisé par le navigateur
│   ├── config.json
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   ├── special_tokens_map.json
│   └── onnx/
│       └── model_quantized.onnx
│
├── training/
│   ├── annotations/
│   │   └── annotation-guide.md
│   ├── data/
│   │   ├── raw/
│   │   ├── reviewed/
│   │   └── processed/
│   ├── scripts/
│   │   ├── generate_dataset.py
│   │   ├── validate_dataset.py
│   │   ├── prepare_dataset.py
│   │   ├── train.py
│   │   ├── predict.py
│   │   ├── predict_onnx.py
│   │   └── quantize_onnx.py
│   ├── output/                  Artefacts générés, non versionnés
│   │   ├── checkpoints/
│   │   ├── final-model/
│   │   ├── evaluation/
│   │   └── onnx/
│   └── requirements.txt
│
└── .github/workflows/deploy.yml
```

## Prérequis

- Node.js 24 ou une version compatible avec Vite ;
- Python 3.11 ;
- Git LFS ;
- npm.

## Installation de l’application web

```bash
npm install
npm run dev
```

## Environnement d’entraînement

Créer l’environnement Python :

```bash
python3.11 -m venv training/.venv
source training/.venv/bin/activate
```

Installer les dépendances :

```bash
python -m pip install --upgrade pip
python -m pip install -r training/requirements.txt
```

Quitter l’environnement :

```bash
deactivate
```

## Guide d’annotation

Les règles de délimitation des quatre entités sont décrites dans :

```text
training/annotations/annotation-guide.md
```

Une information absente ne doit jamais être inventée ou annotée.

## Génération du corpus pilote

```bash
python training/scripts/generate_dataset.py
```

Le corpus brut est généré dans :

```text
training/data/raw/pilot.jsonl
```

## Validation du corpus

```bash
python training/scripts/validate_dataset.py
```

Le validateur contrôle notamment :

- le format JSONL ;
- les identifiants dupliqués ;
- les positions des entités ;
- les chevauchements ;
- les labels autorisés ;
- les textes dupliqués.

## Préparation des ensembles

```bash
python training/scripts/prepare_dataset.py
```

Les fichiers sont générés dans :

```text
training/data/processed/train.jsonl
training/data/processed/validation.jsonl
training/data/processed/test.jsonl
```

La séparation est réalisée par groupe afin que les reformulations d’une même proposition ne soient pas réparties entre entraînement et test.

## Entraînement

```bash
python training/scripts/train.py
```

Le modèle PyTorch final est enregistré dans :

```text
training/output/final-model/
```

Les checkpoints intermédiaires sont enregistrés dans :

```text
training/output/checkpoints/
```

Les métriques du jeu de test sont enregistrées dans :

```text
training/output/evaluation/test-metrics.json
```

## Test du modèle PyTorch

```bash
python training/scripts/predict.py
```

Une phrase personnalisée peut être fournie :

```bash
python training/scripts/predict.py \
  "Installer des moustiquaires avec des cadres amovibles pour mieux récupérer."
```

## Export ONNX

```bash
optimum-cli export onnx \
  --model training/output/final-model \
  --task token-classification \
  training/output/onnx
```

Le modèle non quantifié est généré dans :

```text
training/output/onnx/model.onnx
```

## Quantification

```bash
python training/scripts/quantize_onnx.py
```

La version `QUInt8` est générée dans :

```text
training/output/onnx/model_uint8.onnx
```

Cette version a été retenue car elle préserve mieux les frontières des entités que la quantification dynamique `QInt8` lors de nos essais.

## Test du modèle ONNX

Dans `predict_onnx.py`, utiliser :

```python
file_name="model_uint8.onnx"
```

Puis lancer :

```bash
python training/scripts/predict_onnx.py
```

## Publication du modèle dans l’application

Copier les fichiers de configuration :

```bash
cp training/output/onnx/config.json public/model/
cp training/output/onnx/tokenizer.json public/model/
cp training/output/onnx/tokenizer_config.json public/model/
cp training/output/onnx/special_tokens_map.json public/model/
```

Copier le modèle quantifié sous le nom attendu par Transformers.js :

```bash
cp \
  training/output/onnx/model_uint8.onnx \
  public/model/onnx/model_quantized.onnx
```

Le navigateur charge alors :

```text
public/model/onnx/model_quantized.onnx
```

## Construction du site

```bash
npm run build
```

Les fichiers publiables sont générés dans :

```text
dist/
```

## Git LFS

Le modèle ONNX dépasse la limite habituelle de 100 Mio par fichier. Il est donc suivi avec Git LFS :

```bash
git lfs track "public/model/onnx/*.onnx"
```

Le workflow GitHub Actions utilise :

```yaml
with:
  lfs: true
```

afin de récupérer le véritable modèle avant de construire le site.

## Limites actuelles

Le corpus pilote est synthétique et de petite taille. Les résultats démontrent la faisabilité technique, mais ne constituent pas encore une validation en production.

Avant une utilisation réelle, il faudra :

- enrichir les secteurs et formulations ;
- ajouter des propositions réelles anonymisées ;
- faire réviser les annotations ;
- inclure davantage de phrases ambiguës ou incomplètes ;
- mesurer les performances par type d’entité ;
- tester le chargement et l’inférence sur plusieurs téléphones.
