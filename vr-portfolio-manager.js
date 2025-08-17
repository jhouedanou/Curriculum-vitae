/**
 * VR Portfolio Manager - Composant principal A-Frame
 * Gestion de l'expérience VR immersive du portfolio
 */

AFRAME.registerComponent('portfolio-manager', {
    schema: {
        language: { type: 'string', default: 'fr' },
        autoRotate: { type: 'boolean', default: false },
        showStats: { type: 'boolean', default: false },
        spaceName: { type: 'string', default: 'projects' }
    },

    init: function() {
        this.currentLang = this.getLanguageFromURL() || this.data.language;
        this.selectedProject = null;
        this.isInitialized = false;
        this.rotationSpeed = 0.002;
        
        // Seulement initialiser si on est dans l'espace projets
        if (this.data.spaceName === 'projects') {
            // Attendre que les données soient chargées
            this.waitForData().then(() => {
                this.initializeProjectsSpace();
            });
        }
    },

    waitForData: function() {
        return new Promise((resolve) => {
            const checkData = () => {
                if (window.PortfolioData) {
                    resolve();
                } else {
                    setTimeout(checkData, 100);
                }
            };
            checkData();
        });
    },

    initializeProjectsSpace: function() {
        console.log('🥽 Initialisation de l\'espace Projets...');
        
        this.createProjectPlatforms();
        this.createCategoryFilters();
        this.setupEventListeners();
        
        if (this.data.autoRotate) {
            this.startAutoRotation();
        }
        
        this.isInitialized = true;
        console.log('✅ Espace Projets initialisé');
    },

    getLanguageFromURL: function() {
        const params = new URLSearchParams(window.location.search);
        return params.get('lang') || 'fr';
    },

    createWelcomeSequence: function() {
        // Séquence d'accueil avec animation d'apparition
        const welcomeText = document.createElement('a-text');
        welcomeText.setAttribute('id', 'welcome-text');
        welcomeText.setAttribute('value', window.PortfolioData.texts[this.currentLang].subtitle);
        welcomeText.setAttribute('position', '0 8 -5');
        welcomeText.setAttribute('align', 'center');
        welcomeText.setAttribute('color', window.PortfolioData.colors.white);
        welcomeText.setAttribute('scale', '3 3 3');
        welcomeText.setAttribute('opacity', '0');
        
        // Animation d'apparition
        welcomeText.setAttribute('animation__fadein', {
            property: 'opacity',
            to: 1,
            dur: 2000,
            delay: 1000
        });
        
        welcomeText.setAttribute('animation__fadeout', {
            property: 'opacity', 
            to: 0,
            dur: 1000,
            delay: 5000
        });
        
        this.el.sceneEl.appendChild(welcomeText);
        
        // Supprimer après animation
        setTimeout(() => {
            if (welcomeText.parentNode) {
                welcomeText.parentNode.removeChild(welcomeText);
            }
        }, 7000);
    },

    createMainPlatforms: function() {
        const container = document.querySelector('#main-platforms') || this.createMainContainer();
        const sections = window.PortfolioData.sections;
        
        Object.keys(sections).forEach(key => {
            const section = sections[key];
            const platform = this.createSectionPlatform(key, section);
            container.appendChild(platform);
        });
    },

    createMainContainer: function() {
        const container = document.createElement('a-entity');
        container.setAttribute('id', 'main-platforms');
        container.setAttribute('position', '0 0 0');
        this.el.sceneEl.appendChild(container);
        return container;
    },

    createSectionPlatform: function(key, section) {
        const platform = document.createElement('a-entity');
        platform.setAttribute('id', `section-${key}`);
        platform.setAttribute('position', section.position.join(' '));
        platform.setAttribute('class', 'section-platform');
        
        // Base cylindrique avec Material Design
        const base = document.createElement('a-cylinder');
        base.setAttribute('radius', '2.5');
        base.setAttribute('height', '0.8');
        base.setAttribute('color', window.PortfolioData.colors.primary);
        base.setAttribute('metalness', '0.1');
        base.setAttribute('roughness', '0.3');
        base.setAttribute('class', 'interactive');
        base.setAttribute('shadow', 'cast: true; receive: true');
        
        // Animations interactives
        base.setAttribute('animation__hover', {
            property: 'scale',
            to: '1.1 1.1 1.1',
            startEvents: 'mouseenter',
            dur: 300,
            easing: 'easeOutCubic'
        });
        
        base.setAttribute('animation__leave', {
            property: 'scale', 
            to: '1 1 1',
            startEvents: 'mouseleave',
            dur: 300,
            easing: 'easeOutCubic'
        });
        
        // Pulse d'attraction
        base.setAttribute('animation__pulse', {
            property: 'material.emissiveIntensity',
            to: 0.3,
            dur: 2000,
            loop: true,
            dir: 'alternate',
            easing: 'easeInOutSine'
        });
        
        // Texte de la section
        const text = document.createElement('a-text');
        text.setAttribute('value', section.title[this.currentLang]);
        text.setAttribute('position', '0 1.2 0');
        text.setAttribute('align', 'center');
        text.setAttribute('color', window.PortfolioData.colors.white);
        text.setAttribute('scale', '2.5 2.5 2.5');
        text.setAttribute('font', 'dejavu');
        
        // Icône emoji
        const icon = document.createElement('a-text');
        icon.setAttribute('value', section.icon);
        icon.setAttribute('position', '0 0.5 0');
        icon.setAttribute('align', 'center');
        icon.setAttribute('scale', '4 4 4');
        
        // Description flottante
        const description = document.createElement('a-text');
        description.setAttribute('value', section.content[this.currentLang]);
        description.setAttribute('position', '0 -1.5 0');
        description.setAttribute('align', 'center');
        description.setAttribute('color', window.PortfolioData.colors.grey);
        description.setAttribute('scale', '1.2 1.2 1.2');
        description.setAttribute('wrap-count', '40');
        description.setAttribute('opacity', '0.8');
        
        platform.appendChild(base);
        platform.appendChild(text);
        platform.appendChild(icon);
        platform.appendChild(description);
        
        // Événement de navigation
        base.addEventListener('click', () => {
            this.navigateToSection(key);
        });
        
        return platform;
    },

    createProjectPlatforms: function() {
        const projects = window.PortfolioData.projects;
        const container = this.el; // Utiliser l'élément actuel (#projects-container)
        
        projects.forEach((project, index) => {
            const platform = this.createProjectPlatform(project, index);
            container.appendChild(platform);
        });
    },

    createProjectPlatform: function(project, index) {
        // Calculer position en grille pour l'espace projets
        const cols = 5; // 5 colonnes
        const spacing = 6; // Espacement entre projets
        const startX = -12; // Position de départ X
        const startZ = -5; // Position de départ Z
        
        const col = index % cols;
        const row = Math.floor(index / cols);
        const x = startX + (col * spacing);
        const z = startZ - (row * spacing);
        
        const platform = document.createElement('a-entity');
        platform.setAttribute('position', `${x} 1 ${z}`);
        platform.setAttribute('id', `project-${project.id}`);
        platform.setAttribute('class', `project-platform category-${project.category}`);
        
        // Base hexagonale pour distinction visuelle
        const base = document.createElement('a-box');
        base.setAttribute('width', '4');
        base.setAttribute('height', '0.5');
        base.setAttribute('depth', '4');
        base.setAttribute('color', project.color || window.PortfolioData.colors.primary);
        base.setAttribute('metalness', '0.2');
        base.setAttribute('roughness', '0.4');
        base.setAttribute('class', 'interactive project-base');
        base.setAttribute('shadow', 'cast: true; receive: true');
        
        // Animation de hover plus sophistiquée
        base.setAttribute('animation__hover', {
            property: 'position',
            to: '0 0.8 0',
            startEvents: 'mouseenter',
            dur: 400,
            easing: 'easeOutBack'
        });
        
        base.setAttribute('animation__leave', {
            property: 'position',
            to: '0 0 0', 
            startEvents: 'mouseleave',
            dur: 300,
            easing: 'easeInBack'
        });
        
        // Titre du projet
        const title = document.createElement('a-text');
        title.setAttribute('value', this.truncateText(project.title, 25));
        title.setAttribute('position', '0 1.5 0');
        title.setAttribute('align', 'center');
        title.setAttribute('color', window.PortfolioData.colors.white);
        title.setAttribute('scale', '1.8 1.8 1.8');
        title.setAttribute('wrap-count', '20');
        title.setAttribute('font', 'dejavu');
        
        // Badge de catégorie
        const categoryBadge = document.createElement('a-box');
        categoryBadge.setAttribute('width', '2');
        categoryBadge.setAttribute('height', '0.3');
        categoryBadge.setAttribute('depth', '0.1');
        categoryBadge.setAttribute('position', '0 2.2 0');
        categoryBadge.setAttribute('color', window.PortfolioData.categories[project.category].color);
        categoryBadge.setAttribute('opacity', '0.9');
        
        const categoryText = document.createElement('a-text');
        categoryText.setAttribute('value', project.category.toUpperCase());
        categoryText.setAttribute('position', '0 0 0.06');
        categoryText.setAttribute('align', 'center');
        categoryText.setAttribute('color', window.PortfolioData.colors.white);
        categoryText.setAttribute('scale', '1.2 1.2 1.2');
        
        categoryBadge.appendChild(categoryText);
        
        // Rôle
        const role = document.createElement('a-text');
        role.setAttribute('value', project.role[this.currentLang]);
        role.setAttribute('position', '0 0.8 0');
        role.setAttribute('align', 'center');
        role.setAttribute('color', window.PortfolioData.colors.accent);
        role.setAttribute('scale', '1.3 1.3 1.3');
        
        // Technologies (nuage de tags 3D)
        const techGroup = document.createElement('a-entity');
        techGroup.setAttribute('position', '0 -1 0');
        
        project.technologies.slice(0, 3).forEach((tech, techIndex) => {
            const tag = this.createTechTag(tech, techIndex);
            techGroup.appendChild(tag);
        });
        
        // Indicateur d'URL (si disponible)
        if (project.url) {
            const linkIndicator = document.createElement('a-sphere');
            linkIndicator.setAttribute('radius', '0.2');
            linkIndicator.setAttribute('position', '1.5 1.5 0');
            linkIndicator.setAttribute('color', '#00ff00');
            linkIndicator.setAttribute('material', 'emissive: #00ff00; emissiveIntensity: 0.3');
            linkIndicator.setAttribute('animation__glow', {
                property: 'material.emissiveIntensity',
                to: 0.8,
                dur: 1000,
                loop: true,
                dir: 'alternate'
            });
            platform.appendChild(linkIndicator);
        }
        
        platform.appendChild(base);
        platform.appendChild(title);
        platform.appendChild(categoryBadge);
        platform.appendChild(role);
        platform.appendChild(techGroup);
        
        // Événements d'interaction
        base.addEventListener('click', () => {
            this.openProjectDetail(project);
        });
        
        return platform;
    },

    createTechTag: function(tech, index) {
        // Positions circulaires pour les tags
        const angle = (index * 2 * Math.PI) / 3;
        const radius = 1.5;
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius;
        
        const tag = document.createElement('a-box');
        tag.setAttribute('width', '1.8');
        tag.setAttribute('height', '0.3');
        tag.setAttribute('depth', '0.3');
        tag.setAttribute('position', `${x} 0 ${z}`);
        tag.setAttribute('color', window.PortfolioData.colors.secondary);
        tag.setAttribute('opacity', '0.9');
        tag.setAttribute('metalness', '0.1');
        tag.setAttribute('roughness', '0.6');
        
        // Rotation vers la caméra
        tag.setAttribute('look-at', '[camera]');
        
        const tagText = document.createElement('a-text');
        tagText.setAttribute('value', tech);
        tagText.setAttribute('position', '0 0 0.16');
        tagText.setAttribute('align', 'center');
        tagText.setAttribute('color', window.PortfolioData.colors.dark);
        tagText.setAttribute('scale', '1 1 1');
        
        tag.appendChild(tagText);
        return tag;
    },

    createCategoryFilters: function() {
        const categories = window.PortfolioData.categories;
        const filterContainer = document.createElement('a-entity');
        filterContainer.setAttribute('id', 'category-filters');
        filterContainer.setAttribute('position', '0 6 5'); // Position au-dessus des projets
        
        Object.keys(categories).forEach((key, index) => {
            const category = categories[key];
            const filterButton = this.createCategoryFilter(key, category, index);
            filterContainer.appendChild(filterButton);
        });
        
        // Bouton "Tous"
        const allButton = this.createCategoryFilter('all', {
            color: window.PortfolioData.colors.white,
            name: { fr: 'Tous', en: 'All' }
        }, -1);
        filterContainer.appendChild(allButton);
        
        this.el.appendChild(filterContainer); // Ajouter au conteneur projets
    },

    createCategoryFilter: function(key, category, index) {
        const button = document.createElement('a-box');
        button.setAttribute('width', '2.5');
        button.setAttribute('height', '0.8'); 
        button.setAttribute('depth', '0.3');
        button.setAttribute('position', `${(index - 1.5) * 3} 0 0`);
        button.setAttribute('color', category.color);
        button.setAttribute('class', 'interactive category-filter');
        button.setAttribute('data-category', key);
        button.setAttribute('opacity', key === 'all' ? '1' : '0.7');
        
        const text = document.createElement('a-text');
        text.setAttribute('value', category.name[this.currentLang]);
        text.setAttribute('position', '0 0 0.16');
        text.setAttribute('align', 'center');
        text.setAttribute('color', window.PortfolioData.colors.white);
        text.setAttribute('scale', '1.5 1.5 1.5');
        
        button.appendChild(text);
        
        // Événement de filtrage
        button.addEventListener('click', () => {
            this.filterProjectsByCategory(key);
            this.updateFilterStates(key);
        });
        
        return button;
    },

    filterProjectsByCategory: function(category) {
        const projects = document.querySelectorAll('.project-platform');
        
        projects.forEach(project => {
            const shouldShow = category === 'all' || project.classList.contains(`category-${category}`);
            
            project.setAttribute('animation__filter', {
                property: 'scale',
                to: shouldShow ? '1 1 1' : '0.1 0.1 0.1',
                dur: 500,
                easing: 'easeInOutCubic'
            });
            
            project.setAttribute('animation__opacity', {
                property: 'opacity',
                to: shouldShow ? '1' : '0',
                dur: 500
            });
        });
    },

    updateFilterStates: function(activeCategory) {
        const filters = document.querySelectorAll('.category-filter');
        filters.forEach(filter => {
            const isActive = filter.getAttribute('data-category') === activeCategory;
            filter.setAttribute('opacity', isActive ? '1' : '0.7');
            filter.setAttribute('scale', isActive ? '1.1 1.1 1.1' : '1 1 1');
        });
    },

    openProjectDetail: function(project) {
        // Créer un modal VR immersif
        this.createProjectModal(project);
        
        // Son de notification (si disponible)
        this.playInteractionSound();
    },

    createProjectModal: function(project) {
        // Supprimer le modal existant
        const existingModal = document.querySelector('#project-modal');
        if (existingModal) {
            existingModal.parentNode.removeChild(existingModal);
        }
        
        const modal = document.createElement('a-entity');
        modal.setAttribute('id', 'project-modal');
        modal.setAttribute('position', '0 2 -6');
        modal.setAttribute('scale', '0.1 0.1 0.1');
        
        // Animation d'apparition
        modal.setAttribute('animation__appear', {
            property: 'scale',
            to: '1 1 1',
            dur: 800,
            easing: 'easeOutBack'
        });
        
        // Panneau principal
        const panel = document.createElement('a-plane');
        panel.setAttribute('width', '10');
        panel.setAttribute('height', '8');
        panel.setAttribute('color', window.PortfolioData.colors.white);
        panel.setAttribute('opacity', '0.95');
        panel.setAttribute('shadow', 'cast: true');
        panel.setAttribute('material', 'side: double');
        
        // Titre du projet
        const title = document.createElement('a-text');
        title.setAttribute('value', project.title);
        title.setAttribute('position', '0 3.2 0.01');
        title.setAttribute('align', 'center');
        title.setAttribute('color', window.PortfolioData.colors.dark);
        title.setAttribute('scale', '2.5 2.5 2.5');
        title.setAttribute('wrap-count', '30');
        
        // Description complète
        const description = document.createElement('a-text');
        description.setAttribute('value', project.fullDescription[this.currentLang]);
        description.setAttribute('position', '0 2 0.01');
        description.setAttribute('align', 'center');
        description.setAttribute('color', window.PortfolioData.colors.grey);
        description.setAttribute('scale', '1.3 1.3 1.3');
        description.setAttribute('wrap-count', '60');
        
        // Rôle
        const roleLabel = document.createElement('a-text');
        roleLabel.setAttribute('value', `${window.PortfolioData.texts[this.currentLang].role}: ${project.role[this.currentLang]}`);
        roleLabel.setAttribute('position', '0 0.8 0.01');
        roleLabel.setAttribute('align', 'center');
        roleLabel.setAttribute('color', window.PortfolioData.colors.primary);
        roleLabel.setAttribute('scale', '1.5 1.5 1.5');
        
        // Technologies
        const techLabel = document.createElement('a-text');
        techLabel.setAttribute('value', `${window.PortfolioData.texts[this.currentLang].technologies}: ${project.technologies.join(', ')}`);
        techLabel.setAttribute('position', '0 0.2 0.01');
        techLabel.setAttribute('align', 'center');
        techLabel.setAttribute('color', window.PortfolioData.colors.accent);
        techLabel.setAttribute('wrap-count', '70');
        techLabel.setAttribute('scale', '1.2 1.2 1.2');
        
        // Défis
        if (project.challenges) {
            const challengesLabel = document.createElement('a-text');
            challengesLabel.setAttribute('value', `${window.PortfolioData.texts[this.currentLang].challenges}: ${project.challenges[this.currentLang]}`);
            challengesLabel.setAttribute('position', '0 -0.4 0.01');
            challengesLabel.setAttribute('align', 'center');
            challengesLabel.setAttribute('color', window.PortfolioData.colors.grey);
            challengesLabel.setAttribute('wrap-count', '70');
            challengesLabel.setAttribute('scale', '1.1 1.1 1.1');
            modal.appendChild(challengesLabel);
        }
        
        // Résultats
        if (project.results) {
            const resultsLabel = document.createElement('a-text');
            resultsLabel.setAttribute('value', `${window.PortfolioData.texts[this.currentLang].results}: ${project.results[this.currentLang]}`);
            resultsLabel.setAttribute('position', '0 -1 0.01');
            resultsLabel.setAttribute('align', 'center');
            resultsLabel.setAttribute('color', window.PortfolioData.colors.accent);
            resultsLabel.setAttribute('wrap-count', '70');
            resultsLabel.setAttribute('scale', '1.1 1.1 1.1');
            modal.appendChild(resultsLabel);
        }
        
        // Boutons d'action
        const buttonGroup = document.createElement('a-entity');
        buttonGroup.setAttribute('position', '0 -2.5 0.01');
        
        // Bouton de visite
        if (project.url) {
            const visitBtn = this.createModalButton(
                window.PortfolioData.texts[this.currentLang].visitProject,
                '-2.5 0 0',
                window.PortfolioData.colors.primary,
                () => window.open(project.url, '_blank')
            );
            buttonGroup.appendChild(visitBtn);
        }
        
        // Bouton de fermeture
        const closeBtn = this.createModalButton(
            window.PortfolioData.texts[this.currentLang].close,
            '2.5 0 0',
            '#ff4444',
            () => this.closeProjectModal(modal)
        );
        buttonGroup.appendChild(closeBtn);
        
        // Assemblage du modal
        modal.appendChild(panel);
        modal.appendChild(title);
        modal.appendChild(description);
        modal.appendChild(roleLabel);
        modal.appendChild(techLabel);
        modal.appendChild(buttonGroup);
        
        // Ajout à la scène
        this.el.sceneEl.appendChild(modal);
        
        // Focus de la caméra sur le modal
        this.focusCameraOnModal(modal);
    },

    createModalButton: function(text, position, color, onClick) {
        const button = document.createElement('a-box');
        button.setAttribute('width', '3.5');
        button.setAttribute('height', '0.8');
        button.setAttribute('depth', '0.3');
        button.setAttribute('position', position);
        button.setAttribute('color', color);
        button.setAttribute('class', 'interactive modal-button');
        button.setAttribute('metalness', '0.1');
        button.setAttribute('roughness', '0.3');
        
        const buttonText = document.createElement('a-text');
        buttonText.setAttribute('value', text);
        buttonText.setAttribute('position', '0 0 0.16');
        buttonText.setAttribute('align', 'center');
        buttonText.setAttribute('color', window.PortfolioData.colors.white);
        buttonText.setAttribute('scale', '1.5 1.5 1.5');
        
        button.appendChild(buttonText);
        
        // Animation hover
        button.setAttribute('animation__hover', {
            property: 'scale',
            to: '1.1 1.1 1.1',
            startEvents: 'mouseenter',
            dur: 200
        });
        
        button.setAttribute('animation__leave', {
            property: 'scale',
            to: '1 1 1',
            startEvents: 'mouseleave',
            dur: 200
        });
        
        button.addEventListener('click', onClick);
        
        return button;
    },

    closeProjectModal: function(modal) {
        modal.setAttribute('animation__disappear', {
            property: 'scale',
            to: '0.1 0.1 0.1',
            dur: 500,
            easing: 'easeInBack'
        });
        
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 500);
    },

    focusCameraOnModal: function(modal) {
        const camera = document.querySelector('[camera]');
        if (camera) {
            camera.setAttribute('animation__focus', {
                property: 'position',
                to: '0 2 -2',
                dur: 1000,
                easing: 'easeInOutCubic'
            });
        }
    },

    navigateToSection: function(section) {
        console.log(`🚀 Navigation vers la section: ${section}`);
        
        const camera = document.querySelector('[camera]');
        const targetPos = window.PortfolioData.sections[section].position;
        
        // Animation fluide de la caméra
        camera.setAttribute('animation__move', {
            property: 'position',
            to: `${targetPos[0]} ${targetPos[1] + 3} ${targetPos[2] + 8}`,
            dur: 2500,
            easing: 'easeInOutCubic'
        });
        
        // Mise à jour de l'URL pour synchronisation
        const url = new URL(window.location);
        url.searchParams.set('section', section);
        window.history.pushState({}, '', url);
        
        // Effet de particules lors de la navigation
        this.createNavigationEffect(targetPos);
    },

    createNavigationEffect: function(targetPos) {
        const effect = document.createElement('a-entity');
        effect.setAttribute('position', targetPos.join(' '));
        effect.setAttribute('particle-system', {
            preset: 'dust',
            particleCount: 200,
            color: window.PortfolioData.colors.primary + ',' + window.PortfolioData.colors.secondary,
            size: 0.5,
            maxAge: 3
        });
        
        this.el.sceneEl.appendChild(effect);
        
        setTimeout(() => {
            if (effect.parentNode) {
                effect.parentNode.removeChild(effect);
            }
        }, 3000);
    },

    createParticleEffects: function() {
        // Système de particules ambiant
        const particles = document.createElement('a-entity');
        particles.setAttribute('id', 'ambient-particles');
        particles.setAttribute('position', '0 5 0');
        particles.setAttribute('particle-system', {
            preset: 'dust',
            particleCount: 150,
            color: window.PortfolioData.colors.primary + ',' + window.PortfolioData.colors.white,
            size: 0.3,
            maxAge: 8,
            accelerationSpread: '2 0 2'
        });
        
        this.el.sceneEl.appendChild(particles);
    },

    startAutoRotation: function() {
        this.tick = function() {
            if (this.isInitialized && this.data.autoRotate) {
                const platforms = document.querySelector('#main-platforms');
                if (platforms) {
                    const currentRotation = platforms.getAttribute('rotation');
                    platforms.setAttribute('rotation', {
                        x: currentRotation.x,
                        y: currentRotation.y + (this.rotationSpeed * 180 / Math.PI),
                        z: currentRotation.z
                    });
                }
            }
        };
    },

    setupEventListeners: function() {
        // Bouton de retour vers la version classique
        const exitBtn = document.querySelector('#exit-vr');
        if (exitBtn) {
            exitBtn.addEventListener('click', () => {
                this.exitToClassicPortfolio();
            });
        }
        
        // Gestion des touches clavier
        document.addEventListener('keydown', (event) => {
            switch(event.key) {
                case 'Escape':
                    this.closeAnyModal();
                    break;
                case 'h':
                case 'H':
                    this.toggleHelp();
                    break;
                case 'r':
                case 'R':
                    this.resetCameraPosition();
                    break;
            }
        });
        
        // Gestion de la souris pour rotation manuelle
        this.setupMouseControls();
    },

    setupMouseControls: function() {
        let isDragging = false;
        let lastMouseX = 0;
        
        document.addEventListener('mousedown', (event) => {
            if (event.button === 2) { // Right click
                isDragging = true;
                lastMouseX = event.clientX;
                event.preventDefault();
            }
        });
        
        document.addEventListener('mousemove', (event) => {
            if (isDragging) {
                const deltaX = event.clientX - lastMouseX;
                const platforms = document.querySelector('#main-platforms');
                if (platforms) {
                    const currentRotation = platforms.getAttribute('rotation');
                    platforms.setAttribute('rotation', {
                        x: currentRotation.x,
                        y: currentRotation.y + deltaX * 0.5,
                        z: currentRotation.z
                    });
                }
                lastMouseX = event.clientX;
            }
        });
        
        document.addEventListener('mouseup', () => {
            isDragging = false;
        });
        
        // Désactiver le menu contextuel
        document.addEventListener('contextmenu', (event) => {
            event.preventDefault();
        });
    },

    exitToClassicPortfolio: function() {
        // Animation de sortie
        const scene = document.querySelector('a-scene');
        scene.setAttribute('animation__exit', {
            property: 'scale',
            to: '0.1 0.1 0.1',
            dur: 1000,
            easing: 'easeInBack'
        });
        
        setTimeout(() => {
            const url = new URL(window.location);
            url.pathname = url.pathname.replace('portfolio-vr.html', 'index.html');
            // Conserver les paramètres de langue et section
            window.location.href = url.toString();
        }, 1000);
    },

    closeAnyModal: function() {
        const modal = document.querySelector('#project-modal');
        if (modal) {
            this.closeProjectModal(modal);
        }
    },

    toggleHelp: function() {
        let helpPanel = document.querySelector('#help-panel');
        
        if (helpPanel) {
            helpPanel.parentNode.removeChild(helpPanel);
        } else {
            helpPanel = this.createHelpPanel();
            this.el.sceneEl.appendChild(helpPanel);
        }
    },

    createHelpPanel: function() {
        const panel = document.createElement('a-plane');
        panel.setAttribute('id', 'help-panel');
        panel.setAttribute('position', '0 2 -3');
        panel.setAttribute('width', '8');
        panel.setAttribute('height', '6');
        panel.setAttribute('color', window.PortfolioData.colors.dark);
        panel.setAttribute('opacity', '0.9');
        
        const helpText = document.createElement('a-text');
        helpText.setAttribute('value', this.getHelpText());
        helpText.setAttribute('position', '0 0 0.01');
        helpText.setAttribute('align', 'center');
        helpText.setAttribute('color', window.PortfolioData.colors.white);
        helpText.setAttribute('wrap-count', '50');
        helpText.setAttribute('scale', '1.5 1.5 1.5');
        
        panel.appendChild(helpText);
        return panel;
    },

    getHelpText: function() {
        const texts = {
            fr: `AIDE - CONTRÔLES VR

• Clic gauche : Interagir avec les éléments
• Clic droit + glisser : Rotation manuelle
• ESC : Fermer les modals
• H : Afficher/masquer cette aide
• R : Réinitialiser la position de la caméra

NAVIGATION:
• Cliquez sur les plateformes pour naviguer
• Cliquez sur les projets pour voir les détails
• Utilisez les filtres de catégories en haut`,
            en: `HELP - VR CONTROLS

• Left click: Interact with elements
• Right click + drag: Manual rotation
• ESC: Close modals
• H: Show/hide this help
• R: Reset camera position

NAVIGATION:
• Click on platforms to navigate
• Click on projects to see details
• Use category filters at the top`
        };
        
        return texts[this.currentLang];
    },

    resetCameraPosition: function() {
        const camera = document.querySelector('[camera]');
        if (camera) {
            camera.setAttribute('animation__reset', {
                property: 'position',
                to: window.PortfolioData.vrConfig.camera.startPosition,
                dur: 1500,
                easing: 'easeInOutCubic'
            });
        }
    },

    truncateText: function(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    },

    playInteractionSound: function() {
        // Placeholder pour les effets sonores futurs
        console.log('🔊 Son d\'interaction');
    }
});

// Composant pour les statistiques de performance
AFRAME.registerComponent('vr-stats', {
    init: function() {
        if (window.PortfolioData && window.PortfolioData.vrConfig) {
            console.log('📊 VR Portfolio Stats initialized');
        }
    }
});

console.log('🥽 VR Portfolio Manager loaded successfully!');