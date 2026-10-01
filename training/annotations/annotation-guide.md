# Guide d’annotation

## Objectif

Identifier dans les propositions actionnables cinq types de segments :

- `ACTION`
- `OBJET`
- `MOYEN`
- `BENEFICIAIRE`
- `FINALITE`

Le jeu de référence est `data/grille_v2/` (source éditable : `propositions.py`).

Une information absente ne doit jamais être inventée.

## ACTION

Verbe ou groupe verbal décrivant ce qui doit être fait.

Exemples :

- `Installer`
- `Mettre en place`
- `Réorganiser`
- `Réduire`
- `Améliorer`

L’action doit être annotée sans le sujet ni les expressions introductives.

Exemple :

> On pourrait installer des moustiquaires.

Annotation :

- ACTION : `installer`
- OBJET : `des moustiquaires`

## OBJET

Élément sur lequel porte directement l’action.

Exemples :

- `des moustiquaires`
- `un planning prévisionnel des samedis`
- `la zone de stockage des palettes`
- `des réunions régulières de coordination`

Les compléments nécessaires pour identifier précisément l’objet peuvent être inclus.

## MOYEN

Ressource, outil, support ou méthode explicitement utilisé pour réaliser l’action.

Exemples :

- `avec des cadres amovibles`
- `à l’aide d’un tableau partagé`
- `en utilisant le matériel disponible`
- `grâce à un marquage au sol`

Les marqueurs `avec`, `à l’aide de`, `en utilisant` et `grâce à` ne font pas partie du segment annoté.

Un lieu, un bénéficiaire ou une fréquence ne constitue pas automatiquement un moyen.

## BENEFICIAIRE

Personne, groupe ou entité à qui la proposition profite, lorsqu’elle est nommée explicitement.

Exemples :

- `les infirmiers du service`
- `les aides-soignants`
- `les futurs patients`

Le marqueur `pour` qui introduit le bénéficiaire ne fait pas partie du segment annoté.

## FINALITE

Effet ou amélioration explicitement recherché (le « afin de… »).

Ce segment s’appelait `RESULTAT` dans l’ancien jeu. Il a été renommé pour ne pas être
confondu avec la dimension R (Résultat) de la grille 4×5, qui est portée par l’objet.

Exemples :

- `réduire le temps perdu`
- `éviter les erreurs de préparation`
- `permettre à l’équipe de mieux récupérer`
- `améliorer la qualité des livraisons`

Les marqueurs `pour`, `afin de`, `de façon à` et `pour que` ne font pas partie du segment annoté.

## Informations absentes

Un champ absent reste sans annotation.

Exemple :

> Installer des moustiquaires dans la salle de pause.

Annotations :

- ACTION : `Installer`
- OBJET : `des moustiquaires dans la salle de pause`
- MOYEN : absent
- BENEFICIAIRE : absent
- FINALITE : absent

## Plusieurs éléments coordonnés

Les éléments coordonnés appartenant à la même catégorie forment un seul segment lorsque cela reste naturel.

Exemple :

> Réduire le temps perdu et améliorer la qualité des livraisons.

FINALITE :

`Réduire le temps perdu et améliorer la qualité des livraisons`

## Expressions introductives

Les expressions suivantes restent hors annotation :

- `Je propose de`
- `On pourrait`
- `Il faudrait`
- `À mon avis`
- `Je pense que nous devrions`

## Conventions

- Conserver exactement le texte original.
- Ne pas corriger l’orthographe dans les annotations.
- Ne pas faire chevaucher deux entités.
- Ne pas attribuer le même texte à deux catégories.
- Ne pas déduire une information implicite.
- En cas d’ambiguïté, laisser le segment non annoté et signaler l’exemple pour révision.