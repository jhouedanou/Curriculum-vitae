# Portfolio VR - Jean Luc Houédanou

## 🥽 Expérience VR Immersive

Ce portfolio propose une expérience VR immersive compatible avec les casques VR modernes (Meta Quest 3, Apple Vision Pro) et accessible depuis n'importe quel navigateur WebXR.

## 🚀 Fonctionnalités

### ✨ Expérience Immersive
- **Environnement 3D** : Portfolio navigable dans un espace 3D avec étoiles et particules
- **Projets interactifs** : 17 projets présentés sur des plateformes 3D avec détails complets
- **Navigation fluide** : Caméra libre avec contrôles souris/clavier et support VR
- **Material Design 3** : Palette de couleurs cohérente avec le portfolio classique

### 🎯 Détection Automatique
- **Meta Quest 3** : Détection automatique et redirection vers l'expérience VR
- **Autres casques VR** : Support Apple Vision Pro et casques WebXR
- **Fallback intelligent** : Accès manuel depuis n'importe quel appareil

### 🎮 Contrôles
- **VR** : Contrôleurs naturels pour Meta Quest, Vision Pro, etc.
- **Desktop** : Souris + clavier (WASD, clic droit + glisser pour rotation)
- **Mobile** : Interface tactile adaptée

## 📁 Architecture

```
portfolio-vr/
├── portfolio-vr.html          # Page principale VR
├── portfolio-data.js          # Données extraites du portfolio 
├── vr-portfolio-manager.js    # Composant A-Frame principal
├── vr-styles.css             # Styles spécifiques VR
├── vr-detector.js            # Détection automatique (modifié)
└── index.html                # Portfolio classique (modifié)
```

## 🛠 Technologies

- **A-Frame 1.4.0** : Framework WebXR/VR
- **WebXR** : Standard VR web natif
- **Material Design 3** : Cohérence visuelle
- **Vue.js 3** : Synchronisation avec portfolio classique
- **Progressive Enhancement** : Fonctionne sans VR

## 🔧 Configuration

### Activation de la détection automatique
Dans `index.html` :
```javascript
// Activer la détection automatique VR
window.VR_AUTO_DETECT_ENABLED = true;
```

### Paramètres URL supportés
- `?lang=fr|en` : Langue d'affichage
- `?section=about|experience|projects|contact` : Section de départ
- `?device=quest3|visionpro|manual` : Type d'appareil

### Exemples d'URLs
```
portfolio-vr.html?lang=en&section=projects
portfolio-vr.html?lang=fr&device=quest3
```

## 🎨 Personnalisation

### Couleurs (portfolio-data.js)
```javascript
colors: {
    primary: "#0593fc",    // Bleu principal
    secondary: "#27CDFE",  // Bleu clair
    accent: "#246CB7",     // Bleu foncé
    // ...
}
```

### Positions des projets
Les projets sont disposés en spirale 3D. Modifier dans `portfolio-data.js` :
```javascript
projects: [
    {
        id: 1,
        position: [-12, 1, -8], // [x, y, z]
        // ...
    }
]
```

### Environnement VR
Configuration dans `portfolio-vr.html` :
```html
<a-entity environment="preset: starry; groundColor: #0593fc; grid: 1x1">
```

## 🎯 Utilisation

### Accès depuis le portfolio classique
1. Cliquer sur le bouton **"Version VR"** 
2. Détection automatique de l'appareil
3. Transition animée vers l'expérience VR

### Navigation en VR
- **Projets** : Cliquer sur les plateformes pour voir les détails
- **Sections** : Plateformes principales (About, Experience, etc.)
- **Filtres** : Boutons de catégories en haut de l'espace
- **Aide** : Appuyer sur `H` ou cliquer sur `?`

### Contrôles clavier
- `ESC` : Fermer les modals
- `H` : Afficher/masquer l'aide
- `R` : Réinitialiser la position caméra
- `Clic droit + glisser` : Rotation manuelle

## 🔍 Développement

### Debug
Console développeur activée avec :
```javascript
console.log('🥽 Portfolio VR - Initialisation...');
// Logs détaillés de l'expérience VR
```

### Test local
```bash
# Serveur local requis pour WebXR
python -m http.server 8000
# ou
npx serve .
```

### Ajout de projets
1. Modifier `portfolio-data.js` avec les nouvelles données
2. Calculer position 3D appropriée
3. Ajouter catégorie si nécessaire

## 📱 Compatibilité

### Casques VR supportés
- ✅ **Meta Quest 3** (détection automatique)
- ✅ **Apple Vision Pro** (détection automatique)
- ✅ **Meta Quest 2** 
- ✅ **HTC Vive**
- ✅ **Valve Index**
- ✅ **Windows Mixed Reality**

### Navigateurs
- ✅ **Chrome/Edge** (WebXR natif)
- ✅ **Firefox** (WebXR activé)
- ✅ **Safari** (iOS 14.5+)
- ✅ **Oculus Browser** (Quest)

### Appareils
- ✅ **Desktop** (Windows, Mac, Linux)
- ✅ **Mobile** (iOS, Android)
- ✅ **Tablettes**

## 🐛 Dépannage

### VR non détectée
1. Vérifier que WebXR est activé dans le navigateur
2. Casque connecté et allumé
3. Permissions WebXR accordées

### Performance
- Réduire `particleCount` dans les systèmes de particules
- Désactiver les ombres sur appareils faibles
- Utiliser `renderer="antialias: false"` si nécessaire

### Problèmes de navigation
- Vérifier la position caméra initiale
- Réinitialiser avec la touche `R`
- Utiliser les contrôles alternatifs (souris/clavier)

## 🚀 Déploiement

### Prérequis
- Serveur HTTPS (requis pour WebXR)
- Headers CORS appropriés si domaines différents

### Optimisations production
1. Minifier les assets A-Frame
2. Optimiser les textures et modèles 3D
3. Implémenter le cache navigateur
4. Compression gzip/brotli

## 📊 Analytics VR

Tracking des interactions disponible :
```javascript
// Événements trackés automatiquement
- Entrée en VR
- Navigation sections
- Clics projets
- Temps d'engagement
- Type d'appareil
```

## 🔮 Améliorations futures

- [ ] **Hand tracking** pour Meta Quest 3
- [ ] **Eye tracking** pour Apple Vision Pro  
- [ ] **Spatial anchors** pour placement persistant
- [ ] **Multijoueur** avec partage d'expérience
- [ ] **Voice commands** navigation vocale
- [ ] **3D models** des projets
- [ ] **AI assistant** guide VR personnalisé

---

**Développé avec ❤️ par Jean Luc Houédanou**  
*Portfolio immersif nouvelle génération*