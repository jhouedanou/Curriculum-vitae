/**
 * VR Portal Manager - Gestionnaire de portails pour navigation entre environnements
 * Utilise A-Frame pour créer des espaces séparés avec téléporation
 */

// Composant principal pour la gestion des portails
AFRAME.registerComponent('portal-manager', {
    schema: {
        currentSpace: { type: 'string', default: 'hub' },
        language: { type: 'string', default: 'fr' },
        enableTransitions: { type: 'boolean', default: true }
    },

    init: function() {
        this.spaces = {
            hub: 'hub-space',
            projects: 'projects-space', 
            experience: 'experience-space',
            about: 'about-space',
            contact: 'contact-space'
        };
        
        this.currentSpace = this.data.currentSpace;
        this.isTransitioning = false;
        
        this.setupInitialSpace();
        this.createPortalEffects();
        this.setupEventListeners();
        
        console.log('🌌 Portal Manager initialisé - Espace:', this.currentSpace);
    },

    setupInitialSpace: function() {
        // Afficher uniquement l'espace actuel au démarrage
        Object.keys(this.spaces).forEach(spaceKey => {
            const spaceElement = document.querySelector('#' + this.spaces[spaceKey]);
            if (spaceElement) {
                spaceElement.setAttribute('visible', spaceKey === this.currentSpace);
            }
        });
    },

    createPortalEffects: function() {
        // Créer les effets visuels des portails
        this.portalShader = {
            schema: {
                timeMsec: { type: 'time', is: 'uniform' },
                color: { type: 'color', default: '#0593fc', is: 'uniform' }
            },
            vertexShader: `
                varying vec2 vUv;
                void main() {
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform float timeMsec;
                uniform vec3 color;
                varying vec2 vUv;
                
                void main() {
                    float time = timeMsec / 1000.0;
                    vec2 center = vec2(0.5, 0.5);
                    float dist = distance(vUv, center);
                    
                    float ripple = sin(dist * 20.0 - time * 3.0) * 0.5 + 0.5;
                    float fade = 1.0 - smoothstep(0.0, 0.5, dist);
                    
                    vec3 finalColor = color * ripple * fade;
                    float alpha = fade * 0.8;
                    
                    gl_FragColor = vec4(finalColor, alpha);
                }
            `
        };
    },

    setupEventListeners: function() {
        // Écouter les événements de navigation
        this.el.addEventListener('navigate-to-space', (event) => {
            this.navigateToSpace(event.detail.space, event.detail.portalPosition);
        });
        
        // Gestion du retour au hub
        document.addEventListener('keydown', (event) => {
            if (event.key === 'h' || event.key === 'H') {
                this.navigateToSpace('hub');
            }
        });
    },

    navigateToSpace: function(targetSpace, portalPosition = null) {
        if (this.isTransitioning || targetSpace === this.currentSpace) {
            return;
        }

        console.log(`🚀 Navigation: ${this.currentSpace} → ${targetSpace}`);
        
        this.isTransitioning = true;
        
        if (this.data.enableTransitions) {
            this.createTransitionEffect(portalPosition).then(() => {
                this.switchSpace(targetSpace);
            });
        } else {
            this.switchSpace(targetSpace);
        }
    },

    createTransitionEffect: function(portalPosition) {
        return new Promise((resolve) => {
            // Effet de transition avec particules
            const camera = document.querySelector('[camera]');
            const transition = document.createElement('a-entity');
            
            transition.setAttribute('position', camera.getAttribute('position'));
            transition.setAttribute('particle-system', {
                preset: 'dust',
                particleCount: 500,
                color: '#0593fc,#27CDFE,#ffffff',
                size: 2,
                maxAge: 2,
                accelerationSpread: '10 10 10'
            });
            
            // Son de transition (si disponible)
            this.playTransitionSound();
            
            this.el.sceneEl.appendChild(transition);
            
            // Animation de fade
            this.createFadeTransition().then(() => {
                setTimeout(() => {
                    if (transition.parentNode) {
                        transition.parentNode.removeChild(transition);
                    }
                    resolve();
                }, 500);
            });
        });
    },

    createFadeTransition: function() {
        return new Promise((resolve) => {
            // Overlay de transition
            const overlay = document.createElement('div');
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: radial-gradient(circle, transparent 0%, #0593fc 100%);
                z-index: 5000;
                opacity: 0;
                transition: opacity 0.8s ease;
                pointer-events: none;
            `;
            
            document.body.appendChild(overlay);
            
            setTimeout(() => overlay.style.opacity = '1', 50);
            
            setTimeout(() => {
                overlay.style.opacity = '0';
                setTimeout(() => {
                    if (overlay.parentNode) {
                        overlay.parentNode.removeChild(overlay);
                    }
                    resolve();
                }, 800);
            }, 800);
        });
    },

    switchSpace: function(targetSpace) {
        const currentSpaceEl = document.querySelector('#' + this.spaces[this.currentSpace]);
        const targetSpaceEl = document.querySelector('#' + this.spaces[targetSpace]);
        
        if (!targetSpaceEl) {
            console.error('❌ Espace cible introuvable:', targetSpace);
            this.isTransitioning = false;
            return;
        }

        // Masquer l'espace actuel
        if (currentSpaceEl) {
            currentSpaceEl.setAttribute('visible', false);
        }
        
        // Afficher le nouvel espace
        targetSpaceEl.setAttribute('visible', true);
        
        // Repositionner la caméra
        this.setCameraPosition(targetSpace);
        
        // Mettre à jour l'état
        this.currentSpace = targetSpace;
        this.isTransitioning = false;
        
        // Événement de navigation terminée
        this.el.emit('space-changed', { 
            previousSpace: this.currentSpace,
            currentSpace: targetSpace 
        });
        
        // Mettre à jour l'URL
        this.updateURL(targetSpace);
        
        console.log('✅ Navigation terminée vers:', targetSpace);
    },

    setCameraPosition: function(space) {
        const camera = document.querySelector('[camera]');
        if (!camera) return;

        const positions = {
            hub: { x: 0, y: 1.6, z: 8 },
            projects: { x: 0, y: 1.6, z: 12 },
            experience: { x: 0, y: 1.6, z: 8 },
            about: { x: 0, y: 1.6, z: 6 },
            contact: { x: 0, y: 1.6, z: 8 }
        };

        const position = positions[space] || positions.hub;
        
        camera.setAttribute('animation__position', {
            property: 'position',
            to: `${position.x} ${position.y} ${position.z}`,
            dur: 1000,
            easing: 'easeInOutCubic'
        });
    },

    updateURL: function(space) {
        const url = new URL(window.location);
        if (space !== 'hub') {
            url.searchParams.set('space', space);
        } else {
            url.searchParams.delete('space');
        }
        window.history.pushState({}, '', url);
    },

    playTransitionSound: function() {
        // Placeholder pour effet sonore de transition
        console.log('🔊 Effet sonore de transition');
    },

    // Méthodes publiques
    getCurrentSpace: function() {
        return this.currentSpace;
    },

    getAllSpaces: function() {
        return Object.keys(this.spaces);
    }
});

// Composant pour les portails individuels
AFRAME.registerComponent('portal', {
    schema: {
        target: { type: 'string' },
        title: { type: 'string' },
        color: { type: 'color', default: '#0593fc' },
        size: { type: 'number', default: 3 },
        active: { type: 'boolean', default: true }
    },

    init: function() {
        this.createPortalStructure();
        this.setupInteractions();
        this.createPortalEffect();
    },

    createPortalStructure: function() {
        // Cadre du portail
        const frame = document.createElement('a-torus');
        frame.setAttribute('radius-outer', this.data.size);
        frame.setAttribute('radius-tubular', '0.1');
        frame.setAttribute('color', this.data.color);
        frame.setAttribute('metalness', '0.8');
        frame.setAttribute('roughness', '0.2');
        frame.setAttribute('class', 'interactive portal-frame');
        
        // Effet de lueur
        frame.setAttribute('animation__glow', {
            property: 'material.emissiveIntensity',
            to: 0.3,
            dur: 2000,
            loop: true,
            dir: 'alternate',
            easing: 'easeInOutSine'
        });

        // Surface du portail
        const surface = document.createElement('a-circle');
        surface.setAttribute('radius', this.data.size - 0.2);
        surface.setAttribute('material', 'shader: flat; transparent: true; opacity: 0.6');
        surface.setAttribute('color', this.data.color);
        surface.setAttribute('class', 'portal-surface');
        
        // Animation ondulation
        surface.setAttribute('animation__wave', {
            property: 'rotation',
            to: '0 0 360',
            dur: 10000,
            loop: true,
            easing: 'linear'
        });

        // Titre du portail
        const title = document.createElement('a-text');
        title.setAttribute('value', this.data.title);
        title.setAttribute('position', `0 ${this.data.size + 1} 0`);
        title.setAttribute('align', 'center');
        title.setAttribute('color', '#ffffff');
        title.setAttribute('scale', '2 2 2');
        title.setAttribute('font', 'dejavu');
        
        // Particules du portail
        const particles = document.createElement('a-entity');
        particles.setAttribute('particle-system', {
            preset: 'dust',
            particleCount: 50,
            color: this.data.color + ',#ffffff',
            size: 0.5,
            maxAge: 5,
            accelerationSpread: '1 1 1'
        });
        particles.setAttribute('position', '0 0 -0.1');

        this.el.appendChild(frame);
        this.el.appendChild(surface);
        this.el.appendChild(title);
        this.el.appendChild(particles);
        
        this.frame = frame;
        this.surface = surface;
    },

    setupInteractions: function() {
        this.frame.addEventListener('click', () => {
            if (this.data.active) {
                this.activatePortal();
            }
        });

        this.frame.addEventListener('mouseenter', () => {
            if (this.data.active) {
                this.highlightPortal();
            }
        });

        this.frame.addEventListener('mouseleave', () => {
            this.unhighlightPortal();
        });
    },

    createPortalEffect: function() {
        // Effet visuel avancé du portail
        const ripples = document.createElement('a-entity');
        ripples.setAttribute('position', '0 0 -0.05');
        
        for (let i = 0; i < 3; i++) {
            const ripple = document.createElement('a-ring');
            ripple.setAttribute('radius-inner', '0.1');
            ripple.setAttribute('radius-outer', '0.2');
            ripple.setAttribute('color', this.data.color);
            ripple.setAttribute('opacity', '0.3');
            ripple.setAttribute('position', '0 0 ' + (i * 0.01));
            
            ripple.setAttribute('animation__scale', {
                property: 'scale',
                to: `${this.data.size * 2} ${this.data.size * 2} 1`,
                dur: 3000 + (i * 500),
                loop: true,
                easing: 'easeOutCubic'
            });
            
            ripple.setAttribute('animation__fade', {
                property: 'opacity',
                to: 0,
                dur: 3000 + (i * 500),
                loop: true,
                easing: 'easeOutCubic'
            });
            
            ripples.appendChild(ripple);
        }
        
        this.el.appendChild(ripples);
    },

    activatePortal: function() {
        console.log('🌀 Activation du portail:', this.data.target);
        
        // Effet d'activation
        this.createActivationEffect();
        
        // Émettre l'événement de navigation
        const portalManager = document.querySelector('[portal-manager]');
        if (portalManager) {
            portalManager.emit('navigate-to-space', {
                space: this.data.target,
                portalPosition: this.el.getAttribute('position')
            });
        }
    },

    createActivationEffect: function() {
        // Flash lumineux
        this.frame.setAttribute('animation__flash', {
            property: 'material.emissiveIntensity',
            to: 1,
            dur: 300,
            dir: 'alternate',
            loop: 2
        });

        // Expansion temporaire
        this.el.setAttribute('animation__expand', {
            property: 'scale',
            to: '1.2 1.2 1.2',
            dur: 400,
            dir: 'alternate',
            easing: 'easeOutBack'
        });

        // Particules d'activation
        const burstParticles = document.createElement('a-entity');
        burstParticles.setAttribute('position', this.el.getAttribute('position'));
        burstParticles.setAttribute('particle-system', {
            preset: 'dust',
            particleCount: 200,
            color: this.data.color + ',#ffffff',
            size: 1,
            maxAge: 2,
            accelerationSpread: '5 5 5'
        });
        
        this.el.sceneEl.appendChild(burstParticles);
        
        setTimeout(() => {
            if (burstParticles.parentNode) {
                burstParticles.parentNode.removeChild(burstParticles);
            }
        }, 2000);
    },

    highlightPortal: function() {
        this.frame.setAttribute('animation__highlight', {
            property: 'scale',
            to: '1.1 1.1 1.1',
            dur: 200,
            easing: 'easeOutCubic'
        });
        
        this.surface.setAttribute('opacity', '0.8');
    },

    unhighlightPortal: function() {
        this.frame.setAttribute('animation__unhighlight', {
            property: 'scale',
            to: '1 1 1',
            dur: 200,
            easing: 'easeOutCubic'
        });
        
        this.surface.setAttribute('opacity', '0.6');
    }
});

// Composant pour les environnements d'espace
AFRAME.registerComponent('space-environment', {
    schema: {
        type: { type: 'string' },
        theme: { type: 'string', default: 'default' }
    },

    init: function() {
        this.setupEnvironment();
    },

    setupEnvironment: function() {
        const type = this.data.type;
        const theme = this.data.theme;
        
        // Configuration spécifique par type d'espace
        const configs = {
            hub: {
                environment: 'preset: starry; groundColor: #0593fc; grid: 1x1',
                lighting: 'ambient'
            },
            projects: {
                environment: 'preset: forest; groundColor: #246CB7; grid: none',
                lighting: 'creative'
            },
            experience: {
                environment: 'preset: egypt; groundColor: #27CDFE; grid: 2x2',
                lighting: 'professional'
            },
            about: {
                environment: 'preset: goaland; groundColor: #0593fc; grid: none',
                lighting: 'personal'
            },
            contact: {
                environment: 'preset: contact; groundColor: #246CB7; grid: 1x1',
                lighting: 'communication'
            }
        };
        
        const config = configs[type] || configs.hub;
        
        // Appliquer la configuration d'environnement
        if (config.environment) {
            this.el.setAttribute('environment', config.environment);
        }
        
        console.log(`🌍 Environnement ${type} configuré avec thème ${theme}`);
    }
});

console.log('🌌 VR Portal Manager chargé avec succès!');