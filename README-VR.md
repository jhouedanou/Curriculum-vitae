# Galerie VR — Jean Luc Houédanou

`portfolio-vr.html` présente les projets du portfolio dans une galerie 3D circulaire. Elle s'ouvre dans un navigateur (ordinateur, téléphone) et dans un casque compatible WebXR.

## Fichiers

| Fichier | Rôle |
|---|---|
| `portfolio-vr.html` | Page, habillage 2D (en-tête, filtres, fiche projet) et scène A-Frame |
| `portfolio-vr.js` | Construction de la galerie : cartes, panneau d'accueil, console, fiche 3D |
| `projects-data.js` | Liste des projets, **source unique** partagée avec `index.html` |
| `assets/projets/` | Miniatures des projets (800 × 500) |

La galerie utilise A-Frame 1.6.0, chargé depuis `aframe.io`.

## Ajouter un projet

1. Ajouter un objet dans `projects-data.js`.
2. Ajouter sa miniature dans `assets/projets/` et renseigner `thumb`.

Le projet apparaît alors dans le portfolio et dans la galerie VR. Un projet sans miniature affiche son numéro à la place de l'image.

## Charte graphique

La galerie reprend les valeurs de `index.html` :

| Élément | Valeur |
|---|---|
| Fond | `#111522` |
| Surfaces | `#192236`, `#202b43` |
| Texte | `#f3eee5`, secondaire `#a8adbb` |
| Accent cuivre | `#c27a5b`, clair `#e0a083` |
| Accent lavande | `#8994e4`, clair `#b8beff` |
| Titres et textes | Figtree |
| Libellés | police à chasse fixe du système |

Chaque panneau est un canvas 2D plaqué sur un plan. Ce choix garde la police Figtree et les accents : les polices 3D intégrées à A-Frame ne les affichent pas.

## Contenu de la scène

- **Panneau d'accueil**, face à l'entrée : portrait, titre et texte de la page d'accueil.
- **Cartes des projets**, sur deux rangées, de part et d'autre de l'accueil.
- **Console**, devant l'accueil : filtres (Tous, Frontend, Full-stack, WordPress, Figma, Nuxt) et bouton de langue.
- **Sol quadrillé**, comme le fond du portfolio. L'anneau cuivre marque la limite de la zone de marche.

## Contrôles

| Appareil | Regarder | Se déplacer | Choisir |
|---|---|---|---|
| Ordinateur | Glisser avec la souris | Z Q S D, W A S D ou flèches | Clic |
| Téléphone | Glisser avec le doigt | — | Toucher |
| Casque | Tourner la tête | — | Rayon de la manette + gâchette |

Hors casque, un clic sur une carte ouvre une fiche à droite, avec le lien « Voir le projet ». Dans le casque, la fiche s'affiche dans la scène ; un clic dessus la ferme.

## Langue

Le bouton « VR / 3D » du portfolio transmet la langue en cours : `portfolio-vr.html?lang=fr` ou `?lang=en`. Le bouton de langue de la galerie bascule entre les deux.

## Limites connues

- La galerie n'a pas été testée sur un casque réel.
- Dans le casque, le lien vers le site d'un projet ne s'ouvre pas : l'adresse est affichée sur la fiche.
- Le suivi des mains sans manette (Apple Vision Pro) n'est pas géré.
