# CV Jean-Luc Houédanou - Guide de conversion en PDF

Ce dépôt contient le CV de Jean-Luc Houédanou en formats Markdown et PDF, en versions française et anglaise.

## 📋 Contenu du dépôt

- `CVHOUEDANOUJeanLuc.md` - CV en français (format Markdown)
- `ResumeHOUEDANOUJeanLuc.md` - CV en anglais (format Markdown)
- `CV_HOUEDANOU_JeanLuc.pdf` - PDF généré à partir du CV en français
- `CV_HOUEDANOU_JeanLuc-en.pdf` - PDF généré à partir du CV en anglais
- `github-markdown.css` - Feuille de style pour le rendu Markdown
- `md-to-pdf.js` - Script de conversion Markdown vers PDF
- `package.json` - Configuration du projet

## 🚀 Instructions pour la conversion Markdown → PDF

### Prérequis

Assurez-vous d'avoir Node.js installé sur votre système. Si ce n'est pas le cas, [téléchargez-le ici](https://nodejs.org/).

### Installation

1. Clonez ce dépôt :
   ```sh
   git clone https://github.com/jhouedanou/Curriculum-vitae.git
   cd Curriculum-vitae
   ```

2. Installez les dépendances :
   ```sh
   npm install
   ```

### Commandes de conversion

#### Utilisation avec npm (recommandé)

```sh
# Convertir tous les fichiers Markdown en PDF
npm run build-pdf

# Convertir uniquement le CV en français
npm run build-pdf-fr

# Convertir uniquement le CV en anglais
npm run build-pdf-en

# Convertir tous les fichiers avec des marges minimales (5mm)
npm run build-pdf-minimal

# Convertir le CV français avec des marges minimales
npm run build-pdf-fr-minimal

# Convertir le CV anglais avec des marges minimales
npm run build-pdf-en-minimal

# Optimisé pour tenir sur 2 pages maximum (marges 3mm, échelle 0.95)
npm run build-pdf-2pages

# CV français optimisé pour 2 pages
npm run build-pdf-fr-2pages

# CV anglais optimisé pour 2 pages
npm run build-pdf-en-2pages
```

#### Conversion avec des marges minimales

Pour générer un PDF avec des marges très petites (5mm) :

```sh
npx md-to-pdf CVHOUEDANOUJeanLuc.md --stylesheet github-markdown.css --body-class=markdown-body --pdf-options '{"margin": "5mm"}'
```

ou pour le CV en anglais :

```sh
npx md-to-pdf ResumeHOUEDANOUJeanLuc.md --stylesheet github-markdown.css --body-class=markdown-body --pdf-options '{"margin": "5mm"}'
```

#### Options personnalisées

Vous pouvez personnaliser davantage le rendu PDF avec différentes options :

```sh
# Format A4 avec des marges spécifiques
npx md-to-pdf CVHOUEDANOUJeanLuc.md --stylesheet github-markdown.css --body-class=markdown-body --pdf-options '{"format": "A4", "margin": "10mm"}'

# Orientation paysage
npx md-to-pdf CVHOUEDANOUJeanLuc.md --stylesheet github-markdown.css --body-class=markdown-body --pdf-options '{"format": "A4", "landscape": true, "margin": "7mm"}'
```

## 🔄 Mettre à jour le workflow GitHub Actions

Si vous souhaitez modifier la façon dont les PDF sont générés automatiquement via GitHub Actions, vous pouvez éditer le fichier `.github/workflows/pdf-readme.yml`.

### Configuration recommandée pour des marges minimales

Remplacez la section de génération PDF dans le workflow par :

```yaml
- name: Générer les PDF avec marges minimales
  run: |
    find . -name "*.md" | while read file; do
      npx md-to-pdf "$file" --stylesheet github-markdown.css --body-class=markdown-body --pdf-options '{"margin": "5mm"}'
    done
```

## ⚠️ Remarque importante

Ne pas utiliser l'option `--launch-options.args` qui provoque une erreur avec la version actuelle de md-to-pdf.

---

Pour plus d'informations, consultez la [documentation officielle de md-to-pdf](https://github.com/simonhaenisch/md-to-pdf).
