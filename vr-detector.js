/**
 * VR Device Detector - Meta Quest 3 & Apple Vision Pro
 * Détection automatique des casques VR pour redirection vers portfolio-vr.html
 */

class VRDetector {
    constructor() {
        this.vrDevices = {
            metaQuest3: false,
            appleVisionPro: false,
            otherVR: false
        };
        
        this.userAgentPatterns = {
            // Meta Quest 3 patterns
            quest3: [
                /OculusBrowser/i,
                /Quest/i,
                /Meta Quest/i,
                /VR\/1\.0/i,
                /Quest 3/i
            ],
            // Apple Vision Pro patterns
            visionPro: [
                /VisionOS/i,
                /Apple Vision/i,
                /Vision Pro/i,
                /visionOS/i
            ],
            // Generic VR patterns
            genericVR: [
                /VR/i,
                /Oculus/i,
                /SteamVR/i,
                /OpenXR/i,
                /WebXR/i
            ]
        };
    }

    /**
     * Détecte les capacités WebXR du navigateur
     */
    async detectWebXRCapabilities() {
        if (!navigator.xr) {
            return false;
        }

        try {
            // Vérifier le support VR immersif
            const vrSupported = await navigator.xr.isSessionSupported('immersive-vr');
            // Vérifier le support AR (Vision Pro)
            const arSupported = await navigator.xr.isSessionSupported('immersive-ar');
            
            return {
                vr: vrSupported,
                ar: arSupported,
                inline: await navigator.xr.isSessionSupported('inline')
            };
        } catch (error) {
            console.log('WebXR detection error:', error);
            return false;
        }
    }

    /**
     * Analyse l'User-Agent pour détecter les appareils VR spécifiques
     */
    analyzeUserAgent() {
        const userAgent = navigator.userAgent;
        
        console.log('User Agent détecté:', userAgent);

        // Détection Meta Quest 3
        for (const pattern of this.userAgentPatterns.quest3) {
            if (pattern.test(userAgent)) {
                this.vrDevices.metaQuest3 = true;
                console.log('Meta Quest 3 détecté via User-Agent');
                break;
            }
        }

        // Détection Apple Vision Pro
        for (const pattern of this.userAgentPatterns.visionPro) {
            if (pattern.test(userAgent)) {
                this.vrDevices.appleVisionPro = true;
                console.log('Apple Vision Pro détecté via User-Agent');
                break;
            }
        }

        // Détection VR générique
        if (!this.vrDevices.metaQuest3 && !this.vrDevices.appleVisionPro) {
            for (const pattern of this.userAgentPatterns.genericVR) {
                if (pattern.test(userAgent)) {
                    this.vrDevices.otherVR = true;
                    console.log('Appareil VR générique détecté');
                    break;
                }
            }
        }
    }

    /**
     * Détecte les caractéristiques de l'écran VR
     */
    detectVRDisplay() {
        const screen = window.screen;
        const viewport = {
            width: window.innerWidth,
            height: window.innerHeight,
            devicePixelRatio: window.devicePixelRatio || 1
        };

        // Résolutions typiques des casques VR
        const vrResolutions = {
            // Meta Quest 3: 2064 x 2208 par œil
            quest3: { width: 4128, height: 2208 },
            // Apple Vision Pro: 3660 x 3200 par œil  
            visionPro: { width: 7320, height: 3200 },
            // Autres résolutions VR communes
            generic: [
                { width: 2880, height: 1700 }, // Quest 2
                { width: 2560, height: 1440 }, // Various VR
            ]
        };

        console.log('Résolution détectée:', viewport);

        // Vérification des résolutions Quest 3
        if (viewport.width >= 2000 && viewport.height >= 2000) {
            if (Math.abs(viewport.width - vrResolutions.quest3.width) < 100 ||
                Math.abs(viewport.height - vrResolutions.quest3.height) < 100) {
                this.vrDevices.metaQuest3 = true;
                console.log('Meta Quest 3 détecté via résolution');
            }
        }

        // Vérification des résolutions Vision Pro
        if (viewport.width >= 3000 && viewport.height >= 1500) {
            if (Math.abs(viewport.width - vrResolutions.visionPro.width) < 200 ||
                Math.abs(viewport.height - vrResolutions.visionPro.height) < 200) {
                this.vrDevices.appleVisionPro = true;
                console.log('Apple Vision Pro détecté via résolution');
            }
        }
    }

    /**
     * Détecte les APIs spécifiques VR - VERSION STRICTE
     */
    detectVRAPIs() {
        // Ne pas marquer comme VR juste parce que WebXR existe
        // WebXR est disponible sur tous les navigateurs modernes
        if (navigator.xr) {
            console.log('WebXR API disponible (mais pas forcément VR)');
            // Ne pas activer otherVR automatiquement
        }

        // WebVR deprecated - plus utilisé
        if (navigator.getVRDisplays) {
            console.log('WebVR API détectée (deprecated)');
            // Ne pas activer otherVR automatiquement non plus
        }

        // Détection des contrôleurs de jeu VR spécifiques uniquement
        if (navigator.getGamepads) {
            const gamepads = navigator.getGamepads();
            for (const gamepad of gamepads) {
                if (gamepad && (
                    gamepad.id.toLowerCase().includes('oculus') ||
                    gamepad.id.toLowerCase().includes('quest') ||
                    gamepad.id.toLowerCase().includes('vive') ||
                    gamepad.id.toLowerCase().includes('wmr') ||
                    gamepad.id.toLowerCase().includes('openvr')
                )) {
                    this.vrDevices.otherVR = true;
                    console.log('Contrôleur VR réel détecté:', gamepad.id);
                    break;
                }
            }
        }
    }

    /**
     * Fonction principale de détection
     */
    async detectVRDevice() {
        console.log('🥽 Début de la détection VR...');

        // 1. Analyser l'User-Agent
        this.analyzeUserAgent();

        // 2. Détecter les caractéristiques d'affichage
        this.detectVRDisplay();

        // 3. Vérifier les APIs VR
        this.detectVRAPIs();

        // 4. Vérifier WebXR
        const webXRCapabilities = await this.detectWebXRCapabilities();
        if (webXRCapabilities && (webXRCapabilities.vr || webXRCapabilities.ar)) {
            this.vrDevices.otherVR = true;
            console.log('WebXR capacités détectées:', webXRCapabilities);
        }

        return this.getDetectedDevice();
    }

    /**
     * Retourne l'appareil VR détecté
     */
    getDetectedDevice() {
        if (this.vrDevices.metaQuest3) {
            return {
                device: 'Meta Quest 3',
                type: 'quest3',
                shouldRedirect: true,
                capabilities: ['vr', 'hand-tracking', 'controllers']
            };
        }

        if (this.vrDevices.appleVisionPro) {
            return {
                device: 'Apple Vision Pro',
                type: 'visionpro',
                shouldRedirect: true,
                capabilities: ['vr', 'ar', 'hand-tracking', 'eye-tracking']
            };
        }

        if (this.vrDevices.otherVR) {
            return {
                device: 'VR Device',
                type: 'generic',
                shouldRedirect: true,
                capabilities: ['vr']
            };
        }

        return {
            device: 'No VR Device',
            type: 'none',
            shouldRedirect: false,
            capabilities: []
        };
    }

    /**
     * Redirige vers la version VR avec paramètres spécifiques
     */
    redirectToVR(deviceInfo, delay = 0) {
        const vrUrl = new URL('portfolio-vr-portal.html', window.location.href);
        
        // Ajouter des paramètres pour personnaliser l'expérience VR
        vrUrl.searchParams.set('device', deviceInfo.type);
        vrUrl.searchParams.set('capabilities', deviceInfo.capabilities.join(','));
        vrUrl.searchParams.set('auto-redirect', 'true');

        console.log(`🚀 Redirection vers VR dans ${delay}ms:`, vrUrl.toString());

        if (delay > 0) {
            // Afficher un message de redirection
            this.showRedirectMessage(deviceInfo, delay);
            
            setTimeout(() => {
                window.location.href = vrUrl.toString();
            }, delay);
        } else {
            window.location.href = vrUrl.toString();
        }
    }

    /**
     * Affiche un message de redirection stylisé
     */
    showRedirectMessage(deviceInfo, delay) {
        // Créer overlay de redirection
        const overlay = document.createElement('div');
        overlay.id = 'vr-redirect-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #0593FC, #27CDFE);
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            font-family: 'Outfit', sans-serif;
            animation: fadeIn 0.5s ease;
        `;

        overlay.innerHTML = `
            <div style="text-align: center; animation: pulse 1s infinite;">
                <h1 style="font-size: 3rem; margin-bottom: 1rem; font-weight: 600;">🥽</h1>
                <h2 style="font-size: 2rem; margin-bottom: 1rem;">${deviceInfo.device} Détecté!</h2>
                <p style="font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9;">
                    Redirection vers l'expérience VR immersive...
                </p>
                <div style="width: 200px; height: 4px; background: rgba(255,255,255,0.3); border-radius: 2px; overflow: hidden;">
                    <div style="width: 0%; height: 100%; background: white; border-radius: 2px; animation: loading ${delay}ms linear;"></div>
                </div>
                <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.7;">
                    Capacités: ${deviceInfo.capabilities.join(', ')}
                </p>
            </div>
            <style>
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                }
                @keyframes loading {
                    from { width: 0%; }
                    to { width: 100%; }
                }
            </style>
        `;

        document.body.appendChild(overlay);

        // Permettre l'annulation en cliquant
        overlay.addEventListener('click', () => {
            overlay.remove();
            console.log('Redirection VR annulée par l\'utilisateur');
        });
    }
}

// Méthode pour redirection avec données du portfolio
VRDetector.prototype.redirectToVRWithData = function(portfolioData, lang = 'fr', section = null) {
    const vrUrl = new URL('portfolio-vr.html', window.location.href);
    vrUrl.searchParams.set('lang', lang);
    vrUrl.searchParams.set('device', this.lastDetection?.type || 'manual');
    
    if (section) {
        vrUrl.searchParams.set('section', section);
    }
    
    // Stocker les données dans sessionStorage pour la version VR
    sessionStorage.setItem('portfolioData', JSON.stringify(portfolioData));
    sessionStorage.setItem('portfolioLang', lang);
    sessionStorage.setItem('portfolioSection', section || '');
    
    console.log('🚀 Redirection VR avec données:', {
        url: vrUrl.toString(),
        lang,
        section,
        device: this.lastDetection?.type || 'manual'
    });
    
    // Animation de transition avant redirection
    this.showVRTransition(lang).then(() => {
        window.location.href = vrUrl.toString();
    });
};

// Méthode pour afficher la transition VR
VRDetector.prototype.showVRTransition = function(lang = 'fr') {
    return new Promise((resolve) => {
        const texts = {
            fr: {
                title: 'Passage en mode VR',
                subtitle: 'Préparation de votre expérience immersive...',
                loading: 'Chargement'
            },
            en: {
                title: 'Switching to VR mode',
                subtitle: 'Preparing your immersive experience...',
                loading: 'Loading'
            }
        };
        
        const text = texts[lang] || texts.fr;
        
        // Créer overlay de transition VR
        const overlay = document.createElement('div');
        overlay.id = 'vr-transition-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #0593FC, #27CDFE);
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 10001;
            font-family: 'Outfit', sans-serif;
            animation: fadeIn 0.5s ease;
        `;

        overlay.innerHTML = `
            <div style="text-align: center; animation: pulse 1s infinite;">
                <div style="font-size: 4rem; margin-bottom: 1rem; animation: rotate3d 2s linear infinite;">🥽</div>
                <h2 style="font-size: 2.5rem; margin-bottom: 1rem; font-weight: 600;">${text.title}</h2>
                <p style="font-size: 1.3rem; margin-bottom: 2rem; opacity: 0.9;">
                    ${text.subtitle}
                </p>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="width: 8px; height: 8px; background: white; border-radius: 50%; animation: bounce 1.4s ease-in-out infinite both;"></div>
                    <div style="width: 8px; height: 8px; background: white; border-radius: 50%; animation: bounce 1.4s ease-in-out 0.2s infinite both;"></div>
                    <div style="width: 8px; height: 8px; background: white; border-radius: 50%; animation: bounce 1.4s ease-in-out 0.4s infinite both;"></div>
                </div>
                <p style="margin-top: 1rem; font-size: 1rem; opacity: 0.8;">
                    ${text.loading}...
                </p>
            </div>
            <style>
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                }
                @keyframes rotate3d {
                    from { transform: rotateY(0deg); }
                    to { transform: rotateY(360deg); }
                }
                @keyframes bounce {
                    0%, 80%, 100% { transform: scale(0); }
                    40% { transform: scale(1); }
                }
            </style>
        `;

        document.body.appendChild(overlay);

        // Résoudre après 2 secondes
        setTimeout(() => {
            resolve();
        }, 2000);
    });
};

// Méthode pour redirection forcée (même sans VR détecté)
VRDetector.prototype.forceVRRedirect = function(lang = 'fr', section = null) {
    const portfolioData = {
        source: 'manual',
        timestamp: Date.now(),
        userAgent: navigator.userAgent
    };
    
    this.redirectToVRWithData(portfolioData, lang, section);
};

// Export pour utilisation
window.VRDetector = VRDetector;

// Auto-détection VR DÉSACTIVÉE
// Pour activer la détection automatique, définir window.VR_AUTO_DETECT_ENABLED = true dans la page
// DÉSACTIVÉ par défaut suite à la demande de l'utilisateur

console.log('🥽 VR Auto-Detection: DÉSACTIVÉE par défaut');

// Fonction manuelle pour tester la VR
window.testVRDetection = async function() {
    const detector = new VRDetector();
    const deviceInfo = await detector.detectVRDevice();
    console.log('🔍 Test VR:', deviceInfo);
    
    if (deviceInfo.shouldRedirect) {
        if (confirm(`Appareil VR détecté: ${deviceInfo.device}\nVoulez-vous accéder à la version VR?`)) {
            detector.redirectToVR(deviceInfo, 500);
        }
    } else {
        alert('Aucun appareil VR détecté');
    }
};