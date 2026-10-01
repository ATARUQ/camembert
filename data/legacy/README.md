# Ancien jeu d'entraînement (archivé)

Remplacé par `data/grille_v2/`. Conservé pour mémoire ; ne fait plus partie du chemin d'entraînement.

- `scripts/generate_dataset.py` : liste `PROPOSALS` (champs `action`, `objet`, `moyen`, `resultat`) et
  reconstruction des phrases par gabarits (5 variantes par proposition).
- `scripts/prepare_dataset.py` : découpage train / validation / test par `group`.
- `raw/pilot.jsonl`, `processed/*.jsonl` : sorties de ces scripts (labels ACTION, OBJET, MOYEN, RESULTAT).

Dans le nouveau jeu, l'ancien `resultat` correspond au segment FINALITE (effet attendu),
à ne pas confondre avec la dimension R (Résultat) de la grille.
