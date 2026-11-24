# JobBot

Le bot trouve les offres d'emploi qui collent à ton CV, puis prépare pour chacune :
- un **CV adapté** au poste (PDF + HTML),
- une **lettre de motivation**, seulement si l'offre en demande une,
- un **message court** prêt à envoyer (email ou LinkedIn).

**Il n'envoie rien.** Tu relis, puis tu envoies toi-même.

---

## 1. Installer

```bash
cd job-bot
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

**PDF** : WeasyPrint a besoin de Pango.
- macOS : `brew install pango`
- Linux : `sudo apt install libpango-1.0-0 libpangoft2-1.0-0`
- Windows : si l'installation bloque, mets `pdf: false` dans `config.yaml`.
  Le bot crée alors le HTML : ouvre-le dans Chrome → Imprimer → Enregistrer en PDF.

## 1 bis. Sans clé API : tout se rédige dans Claude Code

Aucune clé n'est nécessaire. Claude Code rédige ; le bot lit l'annonce, vérifie, met en page et suit.

1. Ouvre Claude Code à la racine du dépôt (le dossier qui contient `job-bot/`).
2. Tape `/candidature` suivi du lien de l'offre :

   ```
   /candidature https://exemple.com/offre/developpeur-front
   ```

3. Claude lit l'annonce, la compare à `cv.yaml`, rédige, puis lance le bot. Le dossier arrive dans
   `candidatures/<date>_<n°>_<entreprise>/`.

| Fichier | Usage |
|---|---|
| `CV_ATS_Jean_Luc_Houedanou.md` / `.pdf` | CV pour les logiciels de tri (ATS) : une colonne, sans photo ni tableau, titres standards. À déposer sur les sites de recrutement. |
| `CV_Jean_Luc_Houedanou.pdf` | CV mis en page, avec photo. Pour un envoi par email à une personne. |
| `Lettre_Jean_Luc_Houedanou.md` / `.pdf` | Lettre de motivation |
| `Email_Jean_Luc_Houedanou.md` | Destinataire, objet et texte de l'email |
| `offre.md` | Score, écarts, consignes, **points à vérifier** |

Les commandes que Claude Code utilise (tu peux aussi les lancer toi-même) :

```bash
python -m jobbot lien https://…                    # lire l'annonce et l'enregistrer, sans IA
python -m jobbot montrer 12                        # afficher le texte de l'offre n°12
python -m jobbot schema                            # format du fichier attendu
python -m jobbot importer d.json --offre 12        # garde-fous + mise en page du dossier rédigé
```

LinkedIn, Indeed et les pages qui demandent une connexion ne se lisent pas par lien :
colle le texte de l'annonce dans Claude Code, après `/candidature`.

La skill est dans `.claude/skills/candidature/SKILL.md`.

## 1 ter. Avec une clé API (facultatif)

Pour que le bot note et rédige seul, sans Claude Code : copie `.env.example` en `.env` et mets-y
`ANTHROPIC_API_KEY=sk-ant-…` (clé à créer sur https://platform.claude.com → *API Keys*).
Les commandes `go`, `noter`, `preparer`, `coller`, `relancer`, `entretien` et `lien … --rediger`
utilisent cette clé.

## 2. L'interface (ordinateur et téléphone)

```bash
python -m jobbot web
```

Le terminal affiche un lien et un QR code. Scanne-le avec le téléphone (même Wi-Fi) :
il reste connecté 6 mois. Le lien contient une clé secrète, ne le partage pas.
`python -m jobbot web --local` limite l'accès à cet ordinateur.

| Page | Ce que tu y fais |
|---|---|
| **Offres** | Les offres à traiter, de la meilleure à la moins bonne. Filtres « À traiter / Proches / Toutes », recherche, source. Les relances dues s'affichent en haut. |
| **Offre** | Verdict, exigences couvertes ou non, mots-clés absents, écarts classés par gravité. Message à copier (ou à ouvrir dans l'email / WhatsApp), aperçu et PDF du CV et de la lettre, « À vérifier avant d'envoyer », préparation d'entretien, relance. |
| **Suivi** | Tableau À relire → Envoyée → Entretien → Refus / Ignorée. Glisse les cartes (ou change le statut dans la liste sur téléphone). |
| **Nouvelle offre** | Donne le lien d'une annonce : le bot lit la page. Sans clé API, il l'enregistre et t'indique la commande `/candidature` à taper dans Claude Code. Pour LinkedIn, Indeed, email ou WhatsApp, colle le texte. |

Le bouton **Lancer la recherche** fait comme `go` ; le journal s'affiche en direct.
Une seule tâche tourne à la fois, et chaque bouton qui appelle Claude le dit.

## 3. Premier essai : une offre collée à la main

Copie une offre (LinkedIn, email, WhatsApp…) dans `offre.txt`, puis :

```bash
python -m jobbot coller offre.txt
```

Le dossier arrive dans `candidatures/2026-10-08_1_nom-entreprise/` :

| Fichier | Contenu |
|---|---|
| `CV_Jean_Luc_Houedanou.pdf` | CV adapté au poste |
| `Lettre_Jean_Luc_Houedanou.pdf` | Lettre (si demandée, ou avec `--lettre`) |
| `message.txt` | Destinataire, objet et message court |
| `offre.md` | Score, points forts, écarts, consignes, **points à vérifier** |

## 4. Tous les jours : la recherche automatique

```bash
python -m jobbot go
```

1. **Collecte** les nouvelles offres (Novojob, Educarrière, Remotive).
2. **Pré-filtre** gratuit par mots-clés (`config.yaml` → `filtre`).
3. **Note** chaque offre de 0 à 100 (Claude Haiku, rapide et peu cher).
4. **Prépare** les dossiers des offres ≥ 70 (Claude Sonnet), 5 maximum par lancement.

Autres commandes :

```bash
python -m jobbot top               # classement des offres notées
python -m jobbot top --min 50      # avec un seuil plus bas
python -m jobbot preparer 12       # dossier de l'offre n°12
python -m jobbot preparer 12 --lettre
python -m jobbot statut 12 envoye  # a_relire, envoye, entretien, refus, ignore (dossier ou pas)
python -m jobbot relances          # candidatures envoyées depuis 7 jours sans relance
python -m jobbot relancer 12       # message de relance
python -m jobbot entretien 12      # questions probables + réponses STAR tirées du CV, questions à poser, salaire
```

Le bot écarte aussi :
- les **offres expirées** (date limite passée) ;
- les **doublons** : la même offre publiée sur deux sites n'est notée qu'une fois ;
- les offres que tu as marquées **ignorées**.

## 5. Les fichiers que tu modifies

| Fichier | Rôle |
|---|---|
| `cv.yaml` | **Ton CV, la seule source de vérité.** Le bot reformule et réordonne, il n'invente rien. |
| `cv_en.yaml` | Version anglaise, utilisée pour les offres en anglais. Garde les mêmes `id`. |
| `config.yaml` | Seuil, mots-clés, sources, modèles, limites. |
| `templates/` | Mise en page du CV et de la lettre (HTML + CSS). |

## 6. Les garde-fous contre l'invention

- Les postes, entreprises, dates et diplômes viennent de `cv.yaml`, jamais de l'IA.
- Une compétence absente de ton CV est **retirée** du CV adapté.
- Une expérience oubliée par l'IA est **remise** avec son texte d'origine.
- Un chiffre absent de ton CV est **signalé** dans `offre.md` → « À vérifier ».
- Une offre qui demande de l'argent est **signalée** (⚠️) : c'est le signe d'une arnaque.
- Une réalisation sans résultat chiffré n'est pas complétée : le bot te pose la question
  (« Pour renforcer ton CV »). Ajoute le chiffre dans `cv.yaml` s'il est vrai.
- Les mots-clés de l'offre absents de ton CV sont listés, jamais ajoutés.

## 7. Les sources

| Source | Méthode | Règle respectée |
|---|---|---|
| Novojob CI et Bénin | Flux RSS officiels | Une lecture par lancement |
| Educarrière | Lecture de la page des offres | 1 requête toutes les 2 s, 2 pages max |
| Remotive | API publique (remote, en anglais) | 1 appel toutes les 6 h max (règle Remotive : 4/jour), lien vers l'offre gardé |

**Pas de LinkedIn, d'Indeed ni d'EmploiBénin** : leurs conditions (ou leur `robots.txt`)
interdisent la collecte automatique. Pour ces offres, colle le texte dans Claude Code (`/candidature`)
ou dans la page « Nouvelle offre ».

**Ajouter un site** : copie `jobbot/sources/novojob.py`, adapte-le, ajoute la classe
dans `jobbot/sources/__init__.py` et une entrée dans `config.yaml`.

## 8. Lancer chaque matin

macOS / Linux (`crontab -e`) — tous les jours à 7 h 30 :

```
30 7 * * * cd /chemin/vers/job-bot && .venv/bin/python -m jobbot go >> jobbot.log 2>&1
```

Windows : Planificateur de tâches → Créer une tâche de base → Programme :
`C:\chemin\job-bot\.venv\Scripts\python.exe`, arguments : `-m jobbot go`,
dossier de départ : `C:\chemin\job-bot`.

## 9. Tests (sans Internet ni clé API)

```bash
python -m pytest -q
```

## 10. Crédits

Les consignes d'analyse et de rédaction reprennent, adaptées en français, des skills
[resumeskills](https://github.com/paramchoudhary/resumeskills) (MIT). Voir `NOTICE.md`.
