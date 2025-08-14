# 🎨 Thème Material Design 3 - Portfolio

## Vue d'ensemble

Ce thème Material Design 3 a été créé en s'inspirant du design moderne de **Google Notebook LM**, avec une approche expressive et contemporaine qui respecte les principes de Material Design 3.

## ✨ Caractéristiques

### 🎨 Système de Couleurs
- **Couleurs primaires** : Palette bleue moderne (#0593FC - Dodger Blue)
- **Couleurs secondaires** : Bleu ciel vif (#27CDFE - Vivid Sky Blue)
- **Couleurs tertiaires** : Bleu azul (#246CB7 - Azul)
- **Surfaces** : Blanc pur (#FFFFFF) et bleu columbia (#D3E2F2)
- **États** : Couleurs d'erreur, succès, avertissement et info

### 📝 Typographie
- **Police principale** : Google Sans (inspirée de Google Notebook LM)
- **Police de secours** : Roboto
- **Système d'échelle** : 13 niveaux de taille (Display Large à Label Small)
- **Hiérarchie claire** : Espacement et poids optimisés pour la lisibilité

### 🧩 Composants
- **Boutons** : 3 variantes (principal, secondaire, tonal)
- **Cartes** : Avec ombres et états de survol
- **Navigation** : Items avec icônes et états actifs
- **Formulaires** : Inputs avec focus et validation
- **Tags** : Badges et étiquettes stylisées
- **Modales** : Overlays avec backdrop blur

### 🎭 Animations
- **Transitions** : Courbes d'accélération Material Design
- **Effets de survol** : Élévation et transformations subtiles
- **Ripple** : Effet d'onde au clic
- **Loading** : Spinners et états de chargement

### 📱 Responsive Design
- **Grid system** : Layouts adaptatifs
- **Breakpoints** : Mobile-first approach
- **Composants flexibles** : Adaptation automatique aux écrans

## 🚀 Utilisation

### 1. Inclusion du CSS
```html
<link rel="stylesheet" href="material-design-theme.css">
```

### 2. Classes disponibles
```html
<!-- Boutons -->
<button class="md-button">Principal</button>
<button class="md-button secondary">Secondaire</button>
<button class="md-button tonal">Tonal</button>

<!-- Cartes -->
<div class="md-card">Contenu</div>

<!-- Navigation -->
<div class="md-nav-item active">Accueil</div>

<!-- Tags -->
<div class="md-tag">VueJS</div>

<!-- Statistiques -->
<div class="md-stat">
    <div class="md-stat-number">25+</div>
    <div class="md-stat-label">Projets</div>
</div>
```

### 3. Variables CSS personnalisables
```css
:root {
    --md-primary: #0593FC;        /* Dodger Blue */
    --md-secondary: #27CDFE;      /* Vivid Sky Blue */
    --md-tertiary: #246CB7;       /* Azul */
    --md-surface: #FFFFFF;        /* White */
    --md-surface-container: #D3E2F2; /* Columbia Blue */
}
```

## 🎯 Intégration avec le Portfolio

### Fichiers modifiés
- `portfolio-fr.html` - Portfolio français avec nouveau thème
- `portfolio-en.html` - Portfolio anglais avec nouveau thème
- `index.html` - Page d'accueil avec nouveau thème

### Changements appliqués
1. **Remplacement des couleurs** : Ancien système Vue/Nuxt → Material Design 3
2. **Nouvelle typographie** : Google Sans + système d'échelle MD3
3. **Composants modernisés** : Boutons, cartes, navigation
4. **Espacement optimisé** : Système de spacing cohérent
5. **Ombres et élévations** : Hiérarchie visuelle améliorée

## 🔧 Personnalisation

### Modifier les couleurs
```css
:root {
    --md-primary: #VOTRE_COULEUR;
    --md-primary-container: #VOTRE_COULEUR_CONTAINER;
    --md-surface: #VOTRE_SURFACE;
}
```

### Ajouter de nouveaux composants
```css
.md-mon-composant {
    background: var(--md-surface-container);
    border-radius: 16px;
    border: 1px solid var(--md-outline-variant);
    padding: 16px;
}
```

### Créer des variantes
```css
.md-button.success {
    background: var(--md-success);
    color: var(--md-on-success);
}
```

## 📱 Compatibilité

- **Navigateurs modernes** : Chrome, Firefox, Safari, Edge
- **Mobile** : iOS Safari, Chrome Mobile
- **Support** : CSS Custom Properties, Grid, Flexbox
- **Fallbacks** : Roboto pour Google Sans

## 🎨 Inspiration et Références

- **Google Notebook LM** : Design moderne et épuré
- **Material Design 3** : Système de design officiel Google
- **Google Sans** : Typographie expressive et lisible
- **Principes MD3** : Élévation, couleur, typographie, motion

## 📚 Ressources

- [Material Design 3 Guidelines](https://m3.material.io/)
- [Google Fonts - Google Sans](https://fonts.google.com/specimen/Google+Sans)
- [Material Design Tokens](https://m3.material.io/foundations/design-tokens/overview)

## 🚀 Démonstration

Ouvrez `demo-material-design.html` pour voir tous les composants en action !

---

*Thème créé avec ❤️ pour moderniser le portfolio avec les meilleures pratiques de Material Design 3*
