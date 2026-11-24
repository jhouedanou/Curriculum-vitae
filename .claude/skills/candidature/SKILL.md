---
name: candidature
description: Prépare un dossier de candidature (CV adapté, CV compatible ATS, lettre de motivation, email) pour une offre d'emploi donnée par son lien ou par son numéro dans le JobBot. À utiliser quand l'utilisateur colle l'adresse d'une offre, ou écrit /candidature.
---

# Candidature

Tu rédiges le dossier toi-même, ici, dans Claude Code. Le JobBot (`job-bot/`) fait le reste **sans clé API** : il lit l'annonce, applique les garde-fous, met en page et suit la candidature.

Entrée : `$ARGUMENTS` — l'adresse d'une offre (`https://…`), un numéro d'offre du JobBot, ou rien (demande alors le lien).

Toutes les commandes se lancent depuis `job-bot/`. Utilise `.venv/bin/python` s'il existe (Windows : `.venv\Scripts\python.exe`), sinon `python3`. Dans la suite, `PY` désigne cet interpréteur.

## 1. Obtenir l'offre

- **Un lien** : `PY -m jobbot lien "<adresse>"`. La commande lit la page et affiche le numéro de l'offre.
- **Un numéro** : passe à la suite.
- **Le lien est refusé** (LinkedIn, Indeed, page vide, connexion requise) : demande à l'utilisateur de coller le texte de l'annonce. Tu le mettras dans le bloc `offre` du fichier JSON (étape 4), sans `--offre`.

Puis lis le texte : `PY -m jobbot montrer <n°>`.

## 2. Lire les sources

1. Le CV, **seule source de vérité** : `job-bot/cv.yaml` (offre en français) ou `job-bot/cv_en.yaml` (offre en anglais).
2. Les règles de notation : la constante `SYSTEME` de `job-bot/jobbot/matcher.py`.
3. Les règles de rédaction : la constante `SYSTEME` de `job-bot/jobbot/writer.py`.
4. Le format du fichier à produire : `PY -m jobbot schema`.

Suis ces règles telles quelles. Les trois qui comptent le plus :

- **Zéro invention.** Tu reformules, tu choisis, tu réordonnes. Aucun chiffre, outil, diplôme, employeur, client ou projet absent du CV. Une compétence demandée par l'offre et absente du CV n'est jamais présentée comme acquise.
- **Mots-clés de l'offre.** Quand l'offre et le CV décrivent la même chose avec deux mots, emploie le mot exact de l'offre : les logiciels de tri (ATS) cherchent ces mots. Un mot-clé essentiel revient 2 à 4 fois, sans bourrage.
- **Identifiants copiés.** Les `id` d'expériences et de projets, et les noms de compétences, sont copiés depuis le CV.

## 3. Noter l'offre

Remplis l'objet `note` : score de 0 à 100, verdict, exigences couvertes ou non, manques classés par gravité, mots-clés absents du CV, langue (`fr` ou `en`), adresse d'envoi, date limite, consignes, alerte en cas de demande d'argent.

Si le score est sous 50, ou si un manque est critique, dis-le à l'utilisateur avant de rédiger et demande s'il veut continuer.

## 4. Rédiger et écrire le fichier

Écris `job-bot/candidatures/_brouillons/offre-<n°>.json` (ce dossier n'est pas versionné) :

```json
{
  "offre": null,
  "note": { "…": "voir le schéma" },
  "cv": {
    "titre": "Intitulé aligné sur le poste",
    "resume": "Profil de 3 à 4 phrases",
    "competences": ["8 à 12 compétences du CV, la plus utile d'abord"],
    "experiences": [{ "id": "bigfive", "puces": ["2 à 4 réalisations reformulées"] }],
    "projets": ["3 à 5 id de projets du CV"]
  },
  "lettre": { "objet": "…", "destinataire": "Service Recrutement — Entreprise", "paragraphes": ["…", "…", "…", "…"] },
  "message": { "objet_email": "…", "texte": "80 à 120 mots, signature incluse" },
  "a_completer": ["Question au candidat pour chiffrer une réalisation"]
}
```

- `experiences` : toutes les expériences du CV, dans l'ordre du CV.
- `lettre` : rédige-la toujours, sauf si l'utilisateur n'en veut pas (mets alors `null`). Quatre paragraphes, sans formule d'appel ni signature : le modèle les ajoute.
- `offre` : `null` si l'offre est en base ; sinon `{ "titre": "…", "texte": "annonce complète", "url": "…" }`.

## 5. Vérifier et mettre en page

```bash
PY -m jobbot importer candidatures/_brouillons/offre-<n°>.json --offre <n°>
```

Sans `--offre` si tu as rempli le bloc `offre`.

La commande affiche le dossier créé et des lignes « À vérifier ». Pour chacune :

- **Compétence retirée** : elle n'est pas dans le CV. Ne la remets pas.
- **Chiffre absent du CV** : si tu l'as inventé, corrige le fichier et relance la commande. S'il vient de l'offre (durée, date), laisse-le et signale-le.

Fichiers produits dans `job-bot/candidatures/<date>_<n°>_<entreprise>/` :

| Fichier | Usage |
|---|---|
| `CV_ATS_Jean_Luc_Houedanou.md` / `.pdf` | CV pour les sites de recrutement : une colonne, sans photo ni tableau |
| `CV_Jean_Luc_Houedanou.pdf` | CV mis en page, pour un envoi par email à une personne |
| `Lettre_Jean_Luc_Houedanou.md` / `.pdf` | Lettre de motivation |
| `Email_Jean_Luc_Houedanou.md` | Destinataire, objet et texte de l'email |
| `offre.md` | Score, écarts, consignes, points à vérifier |

Sans WeasyPrint, les PDF manquent : indique d'ouvrir le `.html` dans un navigateur, puis Imprimer → Enregistrer en PDF.

## 6. Rendre compte

Donne à l'utilisateur, en français simple :

1. Le score et le verdict, en une ligne.
2. Le chemin du dossier et la liste des fichiers.
3. Les points « À vérifier » qui restent.
4. Les questions de `a_completer`.
5. L'adresse ou le formulaire où envoyer, et la date limite.

**N'envoie rien.** L'utilisateur relit, puis envoie lui-même. Pour voir le dossier dans l'interface : `PY -m jobbot web`.
