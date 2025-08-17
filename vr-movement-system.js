/**
 * VR Movement System - Système de déplacement avancé pour A-Frame
 * Permet le déplacement libre dans l'environnement VR avec contrôles personnalisés
 */

AFRAME.registerComponent('enhanced-movement', {
    schema: {
        speed: { type: 'number', default: 5 },
        flyMode: { type: 'boolean', default: false },
        teleportEnabled: { type: 'boolean', default: true },
        collisionEnabled: { type: 'boolean', default: true },
        smoothMovement: { type: 'boolean', default: true },
        acceleration: { type: 'number', default: 65 },
        friction: { type: 'number', default: 0.1 }
    },

    init: function() {
        console.log('🚀 Enhanced Movement System - Initialisation...');
        
        this.keys = {};
        this.velocity = new THREE.Vector3();
        this.direction = new THREE.Vector3();
        this.prevTime = performance.now();
        this.isMoving = false;
        this.originalWASD = null;
        
        // Configuration des touches
        this.keyMap = {
            // Déplacement classique
            'KeyW': 'forward',
            'KeyS': 'backward', 
            'KeyA': 'left',
            'KeyD': 'right',
            'ArrowUp': 'forward',
            'ArrowDown': 'backward',
            'ArrowLeft': 'left',
            'ArrowRight': 'right',
            
            // Déplacement vertical (mode vol)
            'Space': 'up',
            'KeyQ': 'up',
            'KeyE': 'down',
            'ShiftLeft': 'down',
            'ShiftRight': 'down',
            
            // Contrôles spéciaux
            'KeyF': 'toggleFly',
            'KeyT': 'teleport',
            'KeyC': 'crouch',
            'KeyR': 'run'
        };
        
        this.speeds = {
            walk: this.data.speed,
            run: this.data.speed * 2,
            crouch: this.data.speed * 0.5,
            fly: this.data.speed * 1.5
        };
        
        this.currentSpeed = this.speeds.walk;
        this.setupEventListeners();
        this.disableDefaultWASD();
        this.createMovementIndicators();
        
        console.log('✅ Enhanced Movement System initialisé');
    },

    setupEventListeners: function() {
        // Événements clavier
        document.addEventListener('keydown', this.onKeyDown.bind(this));
        document.addEventListener('keyup', this.onKeyUp.bind(this));
        
        // Événements souris pour la téléportation
        if (this.data.teleportEnabled) {
            this.setupTeleportation();
        }
        
        // Prévenir le comportement par défaut pour certaines touches
        document.addEventListener('keydown', (event) => {
            if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.code)) {
                event.preventDefault();
            }
        });
    },

    disableDefaultWASD: function() {
        // Désactiver temporairement les contrôles WASD par défaut d'A-Frame
        const wasdControls = this.el.getAttribute('wasd-controls');
        if (wasdControls) {
            this.originalWASD = wasdControls;
            this.el.removeAttribute('wasd-controls');
        }
    },

    restoreDefaultWASD: function() {
        // Restaurer les contrôles WASD par défaut
        if (this.originalWASD) {
            this.el.setAttribute('wasd-controls', this.originalWASD);
        }
    },

    onKeyDown: function(event) {
        const action = this.keyMap[event.code];
        if (action) {
            this.keys[action] = true;
            this.handleSpecialActions(action, event);
            event.preventDefault();
        }
    },

    onKeyUp: function(event) {
        const action = this.keyMap[event.code];
        if (action) {
            this.keys[action] = false;
            event.preventDefault();
        }
    },

    handleSpecialActions: function(action, event) {
        switch(action) {
            case 'toggleFly':
                this.toggleFlyMode();
                break;
            case 'teleport':
                this.initiateTeleport();
                break;
            case 'run':
                this.currentSpeed = this.speeds.run;
                this.updateSpeedIndicator('Course');
                break;
            case 'crouch':
                this.currentSpeed = this.speeds.crouch;
                this.updateSpeedIndicator('Accroupi');
                break;
        }
    },

    toggleFlyMode: function() {
        this.data.flyMode = !this.data.flyMode;
        this.currentSpeed = this.data.flyMode ? this.speeds.fly : this.speeds.walk;
        
        const indicator = document.getElementById('movement-mode');
        if (indicator) {
            indicator.setAttribute('value', this.data.flyMode ? 'Mode Vol Activé' : 'Mode Marche');
            indicator.setAttribute('color', this.data.flyMode ? '#00ff00' : '#ffffff');
        }
        
        // Animation visuelle
        this.createModeChangeEffect();
        console.log('✈️ Mode vol:', this.data.flyMode ? 'ACTIVÉ' : 'DÉSACTIVÉ');
    },

    createModeChangeEffect: function() {
        const effect = document.createElement('a-ring');
        effect.setAttribute('position', this.el.getAttribute('position'));
        effect.setAttribute('radius-inner', '0.5');
        effect.setAttribute('radius-outer', '1');
        effect.setAttribute('color', this.data.flyMode ? '#00ff00' : '#0593fc');
        effect.setAttribute('opacity', '0.8');
        
        effect.setAttribute('animation__expand', {
            property: 'scale',
            to: '3 3 3',
            dur: 1000,
            easing: 'easeOutCubic'
        });
        
        effect.setAttribute('animation__fade', {
            property: 'opacity',
            to: '0',
            dur: 1000,
            easing: 'easeOutCubic'
        });
        
        this.el.sceneEl.appendChild(effect);
        
        setTimeout(() => {
            if (effect.parentNode) {
                effect.parentNode.removeChild(effect);
            }
        }, 1000);
    },

    tick: function(time, timeDelta) {
        if (!this.isActive()) return;
        
        const dt = timeDelta / 1000; // Convertir en secondes
        this.updateMovement(dt);
        this.updatePosition(dt);
        this.updateMovementIndicators();
    },

    isActive: function() {
        return Object.values(this.keys).some(pressed => pressed);
    },

    updateMovement: function(dt) {
        const camera = this.el.object3D;
        const direction = new THREE.Vector3();
        
        // Récupérer la direction de la caméra
        camera.getWorldDirection(direction);
        direction.y = 0; // Ignorer la composante Y pour le mouvement horizontal
        direction.normalize();
        
        // Calculer le vecteur droit
        const right = new THREE.Vector3();
        right.crossVectors(direction, camera.up).normalize();
        
        // Réinitialiser le mouvement
        this.direction.set(0, 0, 0);
        
        // Déplacement avant/arrière
        if (this.keys.forward) {
            this.direction.add(direction);
        }
        if (this.keys.backward) {
            this.direction.sub(direction);
        }
        
        // Déplacement gauche/droite
        if (this.keys.left) {
            this.direction.sub(right);
        }
        if (this.keys.right) {
            this.direction.add(right);
        }
        
        // Déplacement vertical (mode vol uniquement)
        if (this.data.flyMode) {
            if (this.keys.up) {
                this.direction.y += 1;
            }
            if (this.keys.down) {
                this.direction.y -= 1;
            }
        }
        
        // Normaliser pour éviter un mouvement plus rapide en diagonal
        if (this.direction.length() > 0) {
            this.direction.normalize();
            this.isMoving = true;
        } else {
            this.isMoving = false;
        }
    },

    updatePosition: function(dt) {
        if (!this.isMoving) {
            // Appliquer la friction
            this.velocity.multiplyScalar(1 - this.data.friction);
            if (this.velocity.length() < 0.01) {
                this.velocity.set(0, 0, 0);
            }
        } else {
            // Calcul de l'accélération
            const targetVelocity = this.direction.clone().multiplyScalar(this.currentSpeed);
            
            if (this.data.smoothMovement) {
                // Mouvement fluide avec accélération
                this.velocity.lerp(targetVelocity, this.data.acceleration * dt / 100);
            } else {
                // Mouvement instantané
                this.velocity.copy(targetVelocity);
            }
        }
        
        // Appliquer le mouvement
        if (this.velocity.length() > 0.01) {
            const movement = this.velocity.clone().multiplyScalar(dt);
            
            if (this.data.collisionEnabled) {
                this.applyMovementWithCollision(movement);
            } else {
                this.applyMovement(movement);
            }
        }
    },

    applyMovement: function(movement) {
        const currentPos = this.el.getAttribute('position');
        const newPos = {
            x: currentPos.x + movement.x,
            y: this.data.flyMode ? currentPos.y + movement.y : currentPos.y,
            z: currentPos.z + movement.z
        };
        
        this.el.setAttribute('position', newPos);
    },

    applyMovementWithCollision: function(movement) {
        // Version simplifiée de la détection de collision
        // Dans une version plus avancée, on utiliserait le raycasting
        const currentPos = this.el.getAttribute('position');
        
        // Limites de base (à adapter selon votre environnement)
        const bounds = {
            minX: -25, maxX: 25,
            minY: this.data.flyMode ? -5 : 1.6, maxY: this.data.flyMode ? 20 : 1.6,
            minZ: -25, maxZ: 25
        };
        
        const newPos = {
            x: Math.max(bounds.minX, Math.min(bounds.maxX, currentPos.x + movement.x)),
            y: Math.max(bounds.minY, Math.min(bounds.maxY, 
                this.data.flyMode ? currentPos.y + movement.y : currentPos.y)),
            z: Math.max(bounds.minZ, Math.min(bounds.maxZ, currentPos.z + movement.z))
        };
        
        this.el.setAttribute('position', newPos);
    },

    setupTeleportation: function() {
        this.teleportMarker = null;
        this.isAiming = false;
        
        // Écouter le double-clic pour la téléportation
        document.addEventListener('dblclick', (event) => {
            this.performTeleport(event);
        });
        
        // Écouter le mouvement de la souris pour l'aperçu de téléportation
        document.addEventListener('mousemove', (event) => {
            if (this.keys.teleport) {
                this.updateTeleportPreview(event);
            }
        });
    },

    initiateTeleport: function() {
        this.isAiming = true;
        this.createTeleportMarker();
        console.log('🎯 Mode téléportation activé - Double-cliquez pour vous téléporter');
    },

    createTeleportMarker: function() {
        if (this.teleportMarker) return;
        
        this.teleportMarker = document.createElement('a-ring');
        this.teleportMarker.setAttribute('radius-inner', '0.8');
        this.teleportMarker.setAttribute('radius-outer', '1.2');
        this.teleportMarker.setAttribute('color', '#00ff00');
        this.teleportMarker.setAttribute('opacity', '0.7');
        this.teleportMarker.setAttribute('rotation', '-90 0 0');
        this.teleportMarker.setAttribute('position', '0 0.1 -5');
        
        // Animation de pulsation
        this.teleportMarker.setAttribute('animation__pulse', {
            property: 'scale',
            to: '1.2 1.2 1.2',
            dur: 1000,
            loop: true,
            dir: 'alternate',
            easing: 'easeInOutSine'
        });
        
        this.el.sceneEl.appendChild(this.teleportMarker);
    },

    updateTeleportPreview: function(event) {
        if (!this.teleportMarker) return;
        
        // Utiliser le raycasting pour positionner le marqueur
        const camera = this.el.object3D;
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        raycaster.setFromCamera(mouse, camera);
        
        // Pour simplifier, on projette sur le plan Y=0
        const distance = -camera.position.y / raycaster.ray.direction.y;
        const point = raycaster.ray.origin.clone().add(
            raycaster.ray.direction.clone().multiplyScalar(distance)
        );
        
        this.teleportMarker.setAttribute('position', `${point.x} 0.1 ${point.z}`);
    },

    performTeleport: function(event) {
        if (!this.teleportMarker) return;
        
        const markerPos = this.teleportMarker.getAttribute('position');
        const newPos = {
            x: markerPos.x,
            y: this.data.flyMode ? markerPos.y + 2 : 1.6, // Hauteur standard
            z: markerPos.z
        };
        
        // Animation de téléportation
        this.el.setAttribute('animation__teleport', {
            property: 'position',
            to: `${newPos.x} ${newPos.y} ${newPos.z}`,
            dur: 300,
            easing: 'easeOutCubic'
        });
        
        // Effet visuel de téléportation
        this.createTeleportEffect(markerPos);
        
        // Nettoyer le marqueur
        this.removeTeleportMarker();
        this.keys.teleport = false;
        this.isAiming = false;
        
        console.log('⚡ Téléportation effectuée vers:', newPos);
    },

    createTeleportEffect: function(position) {
        const effect = document.createElement('a-entity');
        effect.setAttribute('position', position);
        effect.setAttribute('particle-system', {
            preset: 'dust',
            particleCount: 100,
            color: '#00ff00,#ffffff',
            size: 0.5,
            maxAge: 2
        });
        
        this.el.sceneEl.appendChild(effect);
        
        setTimeout(() => {
            if (effect.parentNode) {
                effect.parentNode.removeChild(effect);
            }
        }, 2000);
    },

    removeTeleportMarker: function() {
        if (this.teleportMarker && this.teleportMarker.parentNode) {
            this.teleportMarker.parentNode.removeChild(this.teleportMarker);
            this.teleportMarker = null;
        }
    },

    createMovementIndicators: function() {
        // Indicateur de vitesse
        const speedIndicator = document.createElement('div');
        speedIndicator.id = 'speed-indicator';
        speedIndicator.style.cssText = `
            position: fixed;
            bottom: 80px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-family: 'Outfit', sans-serif;
            font-size: 0.9rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            z-index: 1001;
            pointer-events: none;
        `;
        speedIndicator.textContent = 'Vitesse: Marche';
        document.body.appendChild(speedIndicator);
        
        // Indicateur de mode
        const modeIndicator = document.createElement('div');
        modeIndicator.id = 'movement-mode-indicator';
        modeIndicator.style.cssText = `
            position: fixed;
            bottom: 120px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-family: 'Outfit', sans-serif;
            font-size: 0.9rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            z-index: 1001;
            pointer-events: none;
        `;
        modeIndicator.textContent = 'Mode: Marche';
        document.body.appendChild(modeIndicator);
        
        // Aide contrôles
        this.createControlsHelp();
    },

    createControlsHelp: function() {
        const helpPanel = document.createElement('div');
        helpPanel.id = 'movement-controls-help';
        helpPanel.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: rgba(0, 0, 0, 0.85);
            color: white;
            padding: 16px;
            border-radius: 12px;
            font-family: 'Outfit', sans-serif;
            font-size: 0.8rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            z-index: 1001;
            pointer-events: none;
            max-width: 280px;
            line-height: 1.4;
        `;
        
        helpPanel.innerHTML = `
            <div style="font-weight: 600; margin-bottom: 12px; color: #0593fc;">🎮 Contrôles de Déplacement</div>
            <div><strong>WASD / Flèches:</strong> Se déplacer</div>
            <div><strong>Q / Espace:</strong> Monter (vol)</div>
            <div><strong>E / Shift:</strong> Descendre (vol)</div>
            <div><strong>F:</strong> Basculer mode vol</div>
            <div><strong>R:</strong> Courir (maintenir)</div>
            <div><strong>C:</strong> S'accroupir (maintenir)</div>
            <div><strong>T:</strong> Mode téléportation</div>
            <div><strong>Double-clic:</strong> Téléporter</div>
        `;
        
        document.body.appendChild(helpPanel);
        
        // Auto-masquer après 10 secondes
        setTimeout(() => {
            if (helpPanel.parentNode) {
                helpPanel.style.opacity = '0';
                helpPanel.style.transition = 'opacity 1s ease';
                setTimeout(() => {
                    if (helpPanel.parentNode) {
                        helpPanel.parentNode.removeChild(helpPanel);
                    }
                }, 1000);
            }
        }, 10000);
    },

    updateMovementIndicators: function() {
        // Mise à jour de la vitesse
        const speedIndicator = document.getElementById('speed-indicator');
        if (speedIndicator) {
            let speedText = 'Marche';
            if (this.keys.run) speedText = 'Course';
            else if (this.keys.crouch) speedText = 'Accroupi';
            else if (this.data.flyMode) speedText = 'Vol';
            
            speedIndicator.textContent = `Vitesse: ${speedText}`;
            speedIndicator.style.background = this.isMoving ? 
                'rgba(5, 147, 252, 0.8)' : 'rgba(0, 0, 0, 0.8)';
        }
        
        // Mise à jour du mode
        const modeIndicator = document.getElementById('movement-mode-indicator');
        if (modeIndicator) {
            modeIndicator.textContent = `Mode: ${this.data.flyMode ? 'Vol' : 'Marche'}`;
            modeIndicator.style.color = this.data.flyMode ? '#00ff00' : '#ffffff';
        }
    },

    updateSpeedIndicator: function(mode) {
        const speedIndicator = document.getElementById('speed-indicator');
        if (speedIndicator) {
            speedIndicator.textContent = `Vitesse: ${mode}`;
        }
    },

    remove: function() {
        // Nettoyer les événements et éléments
        this.restoreDefaultWASD();
        this.removeTeleportMarker();
        
        // Supprimer les indicateurs
        ['speed-indicator', 'movement-mode-indicator', 'movement-controls-help'].forEach(id => {
            const element = document.getElementById(id);
            if (element && element.parentNode) {
                element.parentNode.removeChild(element);
            }
        });
        
        console.log('🧹 Enhanced Movement System nettoyé');
    }
});

// Composant d'assistance pour les limites de zone
AFRAME.registerComponent('movement-bounds', {
    schema: {
        minX: { type: 'number', default: -50 },
        maxX: { type: 'number', default: 50 },
        minY: { type: 'number', default: 0 },
        maxY: { type: 'number', default: 20 },
        minZ: { type: 'number', default: -50 },
        maxZ: { type: 'number', default: 50 },
        showBounds: { type: 'boolean', default: false }
    },

    init: function() {
        if (this.data.showBounds) {
            this.createBoundaryVisualization();
        }
    },

    createBoundaryVisualization: function() {
        // Créer une boîte wireframe pour visualiser les limites
        const geometry = new THREE.BoxGeometry(
            this.data.maxX - this.data.minX,
            this.data.maxY - this.data.minY,
            this.data.maxZ - this.data.minZ
        );
        
        const material = new THREE.LineBasicMaterial({ 
            color: 0xff0000, 
            opacity: 0.3, 
            transparent: true 
        });
        
        const wireframe = new THREE.WireframeGeometry(geometry);
        const line = new THREE.LineSegments(wireframe, material);
        
        line.position.set(
            (this.data.maxX + this.data.minX) / 2,
            (this.data.maxY + this.data.minY) / 2,
            (this.data.maxZ + this.data.minZ) / 2
        );
        
        this.el.sceneEl.object3D.add(line);
    }
});

console.log('🚀 Enhanced Movement System chargé avec succès!');