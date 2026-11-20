/**
 * Portfolio Info Panel - Composant pour afficher les informations des sections
 */

AFRAME.registerComponent('portfolio-info-panel', {
    schema: {
        section: { type: 'string' },
        language: { type: 'string', default: 'fr' }
    },

    init: function() {
        this.sections = {
            about: {
                fr: {
                    title: 'À Propos',
                    subtitle: 'Directeur Solutions Digitales',
                    content: 'Directeur Solutions Digitales expérimenté avec plus de 12 ans d\'expertise en développement web full-stack, design UI/UX et gestion de projets digitaux. Spécialiste front-end (VueJS, Nuxt) alliant expertise technique et vision stratégique pour créer des solutions web performantes et innovantes qui génèrent de la valeur mesurable.'
                },
                en: {
                    title: 'About Me',
                    subtitle: 'Digital Solutions Director',
                    content: 'Experienced Digital Solutions Director with over 12 years of expertise in full-stack web development, UI/UX design and digital project management. Frontend specialist (VueJS, Nuxt) combining technical expertise and strategic vision to create high-performance and innovative web solutions that generate measurable value.'
                }
            },
            experience: {
                fr: {
                    title: 'Expérience Professionnelle',
                    subtitle: '12+ ans d\'expertise',
                    content: 'Juin 2019 - Actuellement : Directeur solutions digitales chez Big Five Solutions\n\nJuin 2017 - Juin 2019 : Head Of Design chez WeDev Group\n\nFévrier 2017 - Juin 2017 : Responsable communication digitale chez Adonai Agri Batis\n\nJuillet 2016 - Janvier 2017 : Chargé de projet web chez CIFIDE\n\nAoût 2013 - Mars 2016 : Webmaster chez CERAP'
                },
                en: {
                    title: 'Professional Experience',
                    subtitle: '12+ years of expertise',
                    content: 'June 2019 - Currently: Digital Solutions Director at Big Five Solutions\n\nJune 2017 - June 2019: Head Of Design at WeDev Group\n\nFebruary 2017 - June 2017: Digital Communication Manager at Adonai Agri Batis\n\nJuly 2016 - January 2017: Web Project Manager at CIFIDE\n\nAugust 2013 - March 2016: Webmaster at CERAP'
                }
            },
            projects: {
                fr: {
                    title: 'Mes Réalisations',
                    subtitle: '17+ projets réalisés',
                    content: 'Portfolio de projets diversifiés :\n\n• Frontend : VueJS, React\n• Full-stack : Laravel, NuxtJS, Node.js\n• WordPress : Thèmes custom, Gutenberg\n• UI/UX : Figma, Adobe XD, Design System\n\nProjets phares : Vodacom, CASTEL Afrique, CIPREL, Dinor App, BigFive Solutions...'
                },
                en: {
                    title: 'My Projects',
                    subtitle: '17+ completed projects',
                    content: 'Diverse project portfolio:\n\n• Frontend: VueJS, React\n• Full-stack: Laravel, NuxtJS, Node.js\n• WordPress: Custom themes, Gutenberg\n• UI/UX: Figma, Adobe XD, Design System\n\nFeatured projects: Vodacom, CASTEL Africa, CIPREL, Dinor App, BigFive Solutions...'
                }
            },
            contact: {
                fr: {
                    title: 'Contactez-moi',
                    subtitle: 'Parlons de votre projet',
                    content: '📧 Email : jeanluc@houedanou.com\n\n📱 Téléphone : +225 07 48 34 82 21\n\n🌐 Portfolio : https://jhouedanou.github.io/Curriculum-vitae/\n\n💼 LinkedIn : Jean Luc Houédanou\n\n🐦 Twitter : @afrowebdesigner\n\nDisponible pour freelance et projets à temps plein.'
                },
                en: {
                    title: 'Contact Me',
                    subtitle: 'Let\'s talk about your project',
                    content: '📧 Email: jeanluc@houedanou.com\n\n📱 Phone: +225 07 48 34 82 21\n\n🌐 Portfolio: https://jhouedanou.github.io/Curriculum-vitae/\n\n💼 LinkedIn: Jean Luc Houédanou\n\n🐦 Twitter: @afrowebdesigner\n\nAvailable for freelance and full-time projects.'
                }
            }
        };

        this.setupEventListeners();
    },

    setupEventListeners: function() {
        // Écouter les événements de changement de section
        this.el.addEventListener('show-section', (event) => {
            this.showSection(event.detail.section);
        });
    },

    showSection: function(sectionName) {
        const section = this.sections[sectionName];
        if (!section) return;

        const lang = this.data.language;
        const content = section[lang] || section.fr;

        // Mettre à jour le titre
        const titleEl = this.el.querySelector('#sectionTitle');
        if (titleEl) {
            titleEl.setAttribute('text', 'value', content.title);
        }

        // Mettre à jour le sous-titre
        const subtitleEl = this.el.querySelector('#sectionSubtitle');
        if (subtitleEl) {
            subtitleEl.setAttribute('text', 'value', content.subtitle);
        }

        // Mettre à jour le contenu
        const contentEl = this.el.querySelector('#sectionContent');
        if (contentEl) {
            contentEl.setAttribute('text', 'value', content.content);
        }

        // Afficher le panel avec animation
        this.showPanel();
    },

    showPanel: function() {
        this.el.setAttribute('visible', true);
        this.el.setAttribute('animation__show', {
            property: 'scale',
            to: '1 1 1',
            dur: 400,
            easing: 'easeOutBack'
        });
    },

    hidePanel: function() {
        this.el.setAttribute('animation__hide', {
            property: 'scale',
            to: '0.001 0.001 0.001',
            dur: 300,
            easing: 'easeInBack'
        });

        setTimeout(() => {
            this.el.setAttribute('visible', false);
        }, 300);
    }
});

/**
 * Composant pour les cartes de section
 */
AFRAME.registerComponent('portfolio-card', {
    schema: {
        section: { type: 'string' },
        color: { type: 'color', default: '#0593fc' },
        title: { type: 'string' }
    },

    init: function() {
        this.setupInteractions();
    },

    setupInteractions: function() {
        this.el.addEventListener('click', () => {
            this.selectCard();
        });

        this.el.addEventListener('mouseenter', () => {
            this.highlightCard();
        });

        this.el.addEventListener('mouseleave', () => {
            this.unhighlightCard();
        });
    },

    selectCard: function() {
        console.log('Carte sélectionnée:', this.data.section);

        // Émettre l'événement pour afficher le panel d'info
        const infoPanel = document.querySelector('#infoPanel');
        if (infoPanel) {
            infoPanel.emit('show-section', { section: this.data.section });
        }

        // Mettre à jour toutes les cartes
        this.updateAllCards();
    },

    updateAllCards: function() {
        const cards = document.querySelectorAll('[portfolio-card]');
        cards.forEach(card => {
            const cardComponent = card.components['portfolio-card'];
            if (cardComponent.data.section === this.data.section) {
                card.setAttribute('material', 'emissive', this.data.color);
                card.setAttribute('material', 'emissiveIntensity', '0.3');
            } else {
                card.setAttribute('material', 'emissive', '#000000');
                card.setAttribute('material', 'emissiveIntensity', '0');
            }
        });
    },

    highlightCard: function() {
        this.el.setAttribute('material', 'emissive', this.data.color);
        this.el.setAttribute('material', 'emissiveIntensity', '0.2');
    },

    unhighlightCard: function() {
        // Ne pas enlever le highlight si la carte est sélectionnée
        const isSelected = this.el.getAttribute('material').emissiveIntensity > 0.25;
        if (!isSelected) {
            this.el.setAttribute('material', 'emissive', '#000000');
            this.el.setAttribute('material', 'emissiveIntensity', '0');
        }
    }
});

console.log('Portfolio Info Panel composants chargés !');