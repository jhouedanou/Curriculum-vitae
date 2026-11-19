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
cp .env.example .env               # puis mets ta clé API dans .env
```

Clé API : https://platform.claude.com → *API Keys*.

**PDF** : WeasyPrint a besoin de Pango.
- macOS : `brew install pango`
- Linux : `sudo apt install libpango-1.0-0 libpangoft2-1.0-0`
- Windows : si l'installation bloque, mets `pdf: false` dans `config.yaml`.
  Le bot crée alors le HTML : ouvre-le dans Chrome → Imprimer → Enregistrer en PDF.

## 2. Premier essai : une offre collée à la main

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

## 3. Tous les jours : la recherche automatique

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
python -m jobbot statut 12 envoye  # suivre tes candidatures (envoye / ignore / a_relire)
```

## 4. Les fichiers que tu modifies

| Fichier | Rôle |
|---|---|
| `cv.yaml` | **Ton CV, la seule source de vérité.** Le bot reformule et réordonne, il n'invente rien. |
| `cv_en.yaml` | Version anglaise, utilisée pour les offres en anglais. Garde les mêmes `id`. |
| `config.yaml` | Seuil, mots-clés, sources, modèles, limites. |
| `templates/` | Mise en page du CV et de la lettre (HTML + CSS). |

## 5. Les garde-fous contre l'invention

- Les postes, entreprises, dates et diplômes viennent de `cv.yaml`, jamais de l'IA.
- Une compétence absente de ton CV est **retirée** du CV adapté.
- Une expérience oubliée par l'IA est **remise** avec son texte d'origine.
- Un chiffre absent de ton CV est **signalé** dans `offre.md` → « À vérifier ».
- Une offre qui demande de l'argent est **signalée** (⚠️) : c'est le signe d'une arnaque.

## 6. Les sources

| Source | Méthode | Règle respectée |
|---|---|---|
| Novojob CI | Flux RSS officiel | Une lecture par lancement |
| Educarrière | Lecture de la page des offres | 1 requête toutes les 2 s, 2 pages max |
| Remotive | API publique (remote, en anglais) | 1 appel toutes les 6 h max (règle Remotive : 4/jour), lien vers l'offre gardé |

**Pas de LinkedIn ni d'Indeed** : leurs conditions interdisent la collecte automatique,
et ton compte peut être bloqué. Pour ces offres, utilise `coller`.

**Ajouter un site** : copie `jobbot/sources/novojob.py`, adapte-le, ajoute la classe
dans `jobbot/sources/__init__.py` et une entrée dans `config.yaml`.

## 7. Lancer chaque matin

macOS / Linux (`crontab -e`) — tous les jours à 7 h 30 :

```
30 7 * * * cd /chemin/vers/job-bot && .venv/bin/python -m jobbot go >> jobbot.log 2>&1
```

Windows : Planificateur de tâches → Créer une tâche de base → Programme :
`C:\chemin\job-bot\.venv\Scripts\python.exe`, arguments : `-m jobbot go`,
dossier de départ : `C:\chemin\job-bot`.

## 8. Tests (sans Internet ni clé API)

```bash
python -m pytest -q
```
