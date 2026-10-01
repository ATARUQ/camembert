import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "data/legacy/raw/pilot.jsonl"


PROPOSALS = [
    {
        "group": "vigne-001",
        "sector": "vigne",
        "action": "installer",
        "objet": "des repères visibles au début de chaque rang",
        "moyen": "des panneaux résistants aux intempéries",
        "resultat": "faciliter l’identification des parcelles",
    },
    {
        "group": "vigne-002",
        "sector": "vigne",
        "action": "organiser",
        "objet": "le rangement des outils de taille",
        "moyen": "un panneau avec des emplacements identifiés",
        "resultat": "réduire le temps passé à chercher le matériel",
    },
    {
        "group": "chai-001",
        "sector": "chai",
        "action": "marquer",
        "objet": "une zone réservée aux palettes dans le chai",
        "moyen": "du ruban de marquage au sol",
        "resultat": "éviter les déplacements inutiles",
    },
    {
        "group": "chai-002",
        "sector": "chai",
        "action": "mettre en place",
        "objet": "une fiche de contrôle près de chaque cuve",
        "moyen": "un support plastifié effaçable",
        "resultat": "limiter les oublis pendant les contrôles",
    },
    {
        "group": "conditionnement-001",
        "sector": "conditionnement",
        "action": "réorganiser",
        "objet": "le poste d’approvisionnement de la ligne",
        "moyen": "des bacs identifiés par couleur",
        "resultat": "réduire les arrêts de la mise en bouteilles",
    },
    {
        "group": "conditionnement-002",
        "sector": "conditionnement",
        "action": "afficher",
        "objet": "les changements de format prévus pour la journée",
        "moyen": "un tableau placé à l’entrée de la ligne",
        "resultat": "mieux préparer les changements de série",
    },
    {
        "group": "logistique-001",
        "sector": "logistique",
        "action": "identifier",
        "objet": "les zones de stockage des commandes",
        "moyen": "des étiquettes de couleur",
        "resultat": "retrouver plus rapidement les palettes",
    },
    {
        "group": "logistique-002",
        "sector": "logistique",
        "action": "créer",
        "objet": "un emplacement pour les commandes urgentes",
        "moyen": None,
        "resultat": "éviter qu’elles soient mélangées aux autres expéditions",
    },
    {
        "group": "maintenance-001",
        "sector": "maintenance",
        "action": "centraliser",
        "objet": "les demandes d’intervention",
        "moyen": "un formulaire partagé",
        "resultat": "prioriser plus facilement les réparations",
    },
    {
        "group": "maintenance-002",
        "sector": "maintenance",
        "action": "prévoir",
        "objet": "un contrôle hebdomadaire des équipements",
        "moyen": "une liste de vérification",
        "resultat": "détecter les anomalies avant une panne",
    },
    {
        "group": "qualite-001",
        "sector": "qualité",
        "action": "regrouper",
        "objet": "les procédures de contrôle qualité",
        "moyen": "un classeur accessible dans l’atelier",
        "resultat": "faciliter la consultation des consignes",
    },
    {
        "group": "qualite-002",
        "sector": "qualité",
        "action": "ajouter",
        "objet": "une vérification avant la fermeture des cartons",
        "moyen": None,
        "resultat": "réduire les erreurs de conditionnement",
    },
    {
        "group": "securite-001",
        "sector": "sécurité",
        "action": "sécuriser",
        "objet": "la circulation près des machines",
        "moyen": "un cheminement matérialisé au sol",
        "resultat": "diminuer le risque de collision",
    },
    {
        "group": "securite-002",
        "sector": "sécurité",
        "action": "remplacer",
        "objet": "les tapis usés devant les postes de lavage",
        "moyen": "des tapis antidérapants",
        "resultat": "éviter les glissades",
    },
    {
        "group": "accueil-001",
        "sector": "accueil",
        "action": "organiser",
        "objet": "des épreuves participatives sur le terrain du domaine",
        "moyen": "un jeu de piste et des mini-épreuves sportives",
        "resultat": "faire découvrir aux clients la culture et l’histoire du lieu",
    },
    {
        "group": "accueil-002",
        "sector": "accueil",
        "action": "mettre en place",
        "objet": "un planning prévisionnel des samedis",
        "moyen": "une rotation entre les salariés disponibles",
        "resultat": "mieux répartir la charge liée à l’accueil des visiteurs",
    },
    {
        "group": "conditions-001",
        "sector": "conditions de travail",
        "action": "planter",
        "objet": "des plantes répulsives autour de la zone de repos",
        "moyen": None,
        "resultat": "permettre à l’équipe de profiter de la pause sans piqûres",
    },
    {
        "group": "conditions-002",
        "sector": "conditions de travail",
        "action": "installer",
        "objet": "des moustiquaires dans la salle de pause",
        "moyen": "des cadres amovibles",
        "resultat": "améliorer la récupération pendant la pause",
    },
    {
        "group": "coordination-001",
        "sector": "coordination",
        "action": "mettre en place",
        "objet": "des réunions régulières entre les services",
        "moyen": "un ordre du jour partagé",
        "resultat": "réduire le temps perdu et améliorer les livraisons",
    },
    {
        "group": "administration-001",
        "sector": "administration",
        "action": "centraliser",
        "objet": "les informations utiles aux équipes",
        "moyen": "un tableau numérique commun",
        "resultat": "éviter les consignes contradictoires",
    },
]


class SentenceBuilder:
    def __init__(self):
        self.parts = []
        self.entities = []

    @property
    def position(self):
        return sum(len(part) for part in self.parts)

    def add(self, text, label=None):
        start = self.position
        self.parts.append(text)

        if label:
            self.entities.append(
                {
                    "label": label,
                    "start": start,
                    "end": start + len(text),
                }
            )

        return self

    def build(self):
        return "".join(self.parts), self.entities


def add_action(builder, action, capitalize=False):
    displayed_action = (
        action[0].upper() + action[1:]
        if capitalize
        else action
    )
    builder.add(displayed_action, "ACTION")

def get_de_connector(action):
    first_letter = action[0].lower()

    if first_letter in "aeiouyh":
        return "d’"

    return "de "

def build_example(proposal, variant):
    builder = SentenceBuilder()

    action = proposal["action"]
    objet = proposal["objet"]
    moyen = proposal["moyen"]
    resultat = proposal["resultat"]

    if variant == 0:
        add_action(builder, action, capitalize=True)
        builder.add(" ")
        builder.add(objet, "OBJET")

        if moyen:
            builder.add(" avec ")
            builder.add(moyen, "MOYEN")

        if resultat:
            builder.add(" pour ")
            builder.add(resultat, "RESULTAT")

    elif variant == 1:
        builder.add("Je propose ")
        builder.add(get_de_connector(action))
        add_action(builder, action)
        builder.add(" ")
        builder.add(objet, "OBJET")

        if moyen:
            builder.add(" en utilisant ")
            builder.add(moyen, "MOYEN")

        if resultat:
            builder.add(" afin de ")
            builder.add(resultat, "RESULTAT")

    elif variant == 2:
        if resultat:
            builder.add("Pour ")
            builder.add(resultat, "RESULTAT")
            builder.add(", ")

        builder.add("on pourrait ")
        add_action(builder, action)
        builder.add(" ")
        builder.add(objet, "OBJET")

        if moyen:
            builder.add(" en s’appuyant sur ")
            builder.add(moyen, "MOYEN")

    elif variant == 3:
        builder.add("Il faudrait ")
        add_action(builder, action)
        builder.add(" ")
        builder.add(objet, "OBJET")

        if moyen:
            builder.add(" grâce à ")
            builder.add(moyen, "MOYEN")

        if resultat:
            builder.add(" de façon à ")
            builder.add(resultat, "RESULTAT")

    elif variant == 4:
        builder.add("À mon avis, il serait utile de ")
        add_action(builder, action)
        builder.add(" ")
        builder.add(objet, "OBJET")

        if moyen:
            builder.add(" avec ")
            builder.add(moyen, "MOYEN")

        if resultat:
            builder.add(" pour ")
            builder.add(resultat, "RESULTAT")

    builder.add(".")
    return builder.build()


def validate_example(example):
    text = example["text"]
    previous_end = -1

    for entity in sorted(
        example["entities"],
        key=lambda item: item["start"],
    ):
        start = entity["start"]
        end = entity["end"]

        assert 0 <= start < end <= len(text)
        assert start >= previous_end
        assert text[start:end].strip()
        previous_end = end


def main():
    examples = []

    for proposal in PROPOSALS:
        for variant in range(5):
            text, entities = build_example(proposal, variant)

            example = {
                "id": f"{proposal['group']}-v{variant + 1}",
                "group": proposal["group"],
                "sector": proposal["sector"],
                "text": text,
                "entities": entities,
                "source": "synthetic",
                "reviewed": False,
            }

            validate_example(example)
            examples.append(example)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
        for example in examples:
            output_file.write(
                json.dumps(example, ensure_ascii=False) + "\n"
            )

    print(f"{len(examples)} exemples écrits dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()