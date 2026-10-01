"""
Valide propositions.py puis exporte le jeu au format JSONL pour CamemBERT.

Deux tâches sont servies par le même fichier :
  1. Extraction de segments (token classification) : champ "entities"
     -> liste {start, end, label} en offsets caractères ; à aligner sur les tokens
        CamemBERT via return_offsets_mapping=True (schéma BIO).
  2. Classification multi-label des index de la grille : champs "B", "E", "R", "A"
     et "labels" (vecteur multi-hot de 20 positions, ordre = INDEX_ORDER).

Usage : python build_dataset.py
Sorties : train.jsonl, dev.jsonl, dataset_full.jsonl
"""
import json
import random
from collections import Counter
from pathlib import Path

from propositions import PROPOSALS

HERE = Path(__file__).resolve().parent  # les JSONL sont écrits à côté de ce script

INDEX = {
    "B": ["Bp", "Bq", "Br", "Bs", "Bt"],
    "E": ["Eh", "Ek", "El", "Em", "En"],
    "R": ["Ra", "Re", "Ri", "Ro", "Ru"],
    "A": ["Ab", "Ac", "Ad", "Af", "Ag"],
}
INDEX_ORDER = [i for dim in "BERA" for i in INDEX[dim]]
SPAN_FIELDS = {
    "action": "ACTION", "objet": "OBJET", "moyen": "MOYEN",
    "beneficiaire": "BENEFICIAIRE", "finalite": "FINALITE",
}


def build(p):
    errors, ents = [], []
    for field, label in SPAN_FIELDS.items():
        span = p[field]
        if span is None:
            continue
        start = p["text"].find(span)
        if start < 0:
            errors.append(f"segment « {field} » introuvable : {span!r}")
            continue
        ents.append({"start": start, "end": start + len(span), "label": label, "text": span})
    ents.sort(key=lambda e: e["start"])
    for a, b in zip(ents, ents[1:]):
        if a["end"] > b["start"]:
            errors.append(f"chevauchement {a['label']} / {b['label']}")
    for dim, allowed in INDEX.items():
        if not p[dim]:
            errors.append(f"dimension {dim} vide")
        for code in p[dim]:
            if code not in allowed:
                errors.append(f"index inconnu {code} en {dim}")
    if p["action"] is None or p["objet"] is None:
        errors.append("action et objet sont obligatoires")
    rec = {
        "id": p["group"], "sector": p["sector"], "text": p["text"],
        "entities": ents,
        "B": p["B"], "E": p["E"], "R": p["R"], "A": p["A"],
        "labels": [int(i in p["B"] + p["E"] + p["R"] + p["A"]) for i in INDEX_ORDER],
    }
    return rec, errors


def main():
    records, n_err = [], 0
    ids = Counter(p["group"] for p in PROPOSALS)
    for dup in [k for k, v in ids.items() if v > 1]:
        print(f"[ERREUR] identifiant en double : {dup}")
        n_err += 1
    for p in PROPOSALS:
        rec, errs = build(p)
        for e in errs:
            print(f"[ERREUR] {p['group']}: {e}")
        n_err += len(errs)
        records.append(rec)
    if n_err:
        raise SystemExit(f"{n_err} erreur(s) — export annulé")

    # Découpage train/dev stratifié par secteur (≈ 20 % en dev)
    random.seed(42)
    by_sector = {}
    for r in records:
        by_sector.setdefault(r["sector"], []).append(r)
    train, dev = [], []
    for recs in by_sector.values():
        recs = recs[:]
        random.shuffle(recs)
        k = max(1, round(len(recs) * 0.2))
        dev += recs[:k]
        train += recs[k:]

    for name, rows in [("dataset_full.jsonl", records), ("train.jsonl", train), ("dev.jsonl", dev)]:
        with open(HERE / name, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Statistiques
    print(f"{len(records)} propositions, {len(by_sector)} secteurs — train {len(train)} / dev {len(dev)}")
    cnt = Counter(c for r in records for d in "BERA" for c in r[d])
    for dim in "BERA":
        print(dim, " ".join(f"{c}={cnt[c]}" for c in INDEX[dim]))
    spans = Counter(e["label"] for r in records for e in r["entities"])
    print("segments :", dict(spans))
    multi = sum(any(len(r[d]) > 1 for d in "BERA") for r in records)
    print(f"propositions multi-index : {multi}")


if __name__ == "__main__":
    main()
