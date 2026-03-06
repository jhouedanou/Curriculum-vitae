/**
 * Portfolio Data - Extraction des données du portfolio pour version VR
 * Basé sur les données du portfolio Vue.js existant
 */

window.PortfolioData = {
    // Projets extraits du portfolio existant avec positions 3D calculées
    projects: [
        {
            id: 1,
            title: "Landing Page Vodacom",
            position: [-12, 1, -8],
            color: "#0593fc",
            category: "frontend",
            url: "https://vodamedia.co.za/txtengage/",
            icon: "code",
            description: {
                fr: "Landing page pour Vodacom Afrique du Sud optimisant l'engagement utilisateur",
                en: "Landing page for Vodacom South Africa optimizing user engagement"
            },
            fullDescription: {
                fr: "Développement d'une landing page interactive pour Vodacom avec focus sur l'engagement utilisateur et les conversions.",
                en: "Development of an interactive landing page for Vodacom with focus on user engagement and conversions."
            },
            technologies: ["VueJS", "Responsive Design", "CSS3"],
            role: {
                fr: "Développeur Lead",
                en: "Lead Developer"
            },
            challenges: {
                fr: "Optimisation des performances et adaptation multi-device",
                en: "Performance optimization and multi-device adaptation"
            },
            results: {
                fr: "Amélioration de 40% de l'engagement utilisateur",
                en: "40% improvement in user engagement"
            }
        },
        {
            id: 2,
            title: "CASTEL AFRIQUE",
            position: [-8, 1, -12],
            color: "#27CDFE",
            category: "frontend",
            url: "https://castel-afrique.com",
            icon: "business",
            description: {
                fr: "Intégration complète de maquettes Adobe XD en site web performant",
                en: "Complete integration of Adobe XD mockups into high-performance website"
            },
            fullDescription: {
                fr: "Développement complet du site corporate de CASTEL Afrique avec intégration pixel-perfect des maquettes.",
                en: "Complete development of CASTEL Africa corporate website with pixel-perfect mockup integration."
            },
            technologies: ["HTML5", "CSS3", "JavaScript", "Adobe XD"],
            role: {
                fr: "Chef de projet & Développeur",
                en: "Project Manager & Developer"
            },
            challenges: {
                fr: "Intégration pixel-perfect et optimisation des performances",
                en: "Pixel-perfect integration and performance optimization"
            },
            results: {
                fr: "Site responsive haute performance livré dans les délais",
                en: "High-performance responsive website delivered on time"
            }
        },
        {
            id: 3,
            title: "Template WordPress pour les Awards du Digital et de la Presse Numérique",
            position: [-4, 1, -14],
            color: "#246CB7",
            category: "wordpress",
            url: "https://www.adpnafrica.com/",
            icon: "emoji_events",
            description: {
                fr: "Template WordPress professionnel pour site d'awards",
                en: "Professional WordPress template for awards website"
            },
            fullDescription: {
                fr: "Développement d'un template WordPress sur-mesure pour les Awards du Digital et de la Presse Numérique avec gestion des nominations, votes et présentation des lauréats.",
                en: "Development of custom WordPress template for Digital and Digital Press Awards with nomination management, voting system and winners presentation."
            },
            technologies: ["WordPress", "PHP", "Custom Post Types", "ACF"],
            role: {
                fr: "Développeur WordPress",
                en: "WordPress Developer"
            },
            challenges: {
                fr: "Système de gestion des awards et interface utilisateur intuitive",
                en: "Awards management system and intuitive user interface"
            },
            results: {
                fr: "Plateforme complète pour la gestion des awards digitaux",
                en: "Complete platform for digital awards management"
            }
        },
        {
            id: 4,
            title: "Dinor Calorie Counter",
            position: [0, 1, -16],
            color: "#0593fc",
            category: "fullstack",
            url: "https://dinor-calorie-counter-alt.vercel.app/",
            icon: "restaurant",
            description: {
                fr: "Application de suivi des calories avec interface moderne",
                en: "Calorie tracking application with modern interface"
            },
            fullDescription: {
                fr: "Application web complète pour le suivi des calories avec interface utilisateur intuitive et base de données nutritionnelle.",
                en: "Complete web application for calorie tracking with intuitive user interface and nutritional database."
            },
            technologies: ["React", "Next.js", "TypeScript", "Tailwind CSS"],
            role: {
                fr: "Développeur Full-stack",
                en: "Full-stack Developer"
            },
            challenges: {
                fr: "Interface utilisateur intuitive et gestion des données nutritionnelles",
                en: "Intuitive user interface and nutritional data management"
            },
            results: {
                fr: "Application moderne avec tracking précis des calories",
                en: "Modern application with accurate calorie tracking"
            }
        },
        {
            id: 5,
            title: "Dinor App",
            position: [4, 1, -14],
            color: "#27CDFE",
            category: "fullstack",
            url: "https://new.dinorapp.com/",
            icon: "restaurant_menu",
            description: {
                fr: "Plateforme complète de recettes et astuces culinaires multi-plateformes",
                en: "Complete multi-platform cooking recipes and tips platform"
            },
            fullDescription: {
                fr: "Développement d'une solution complète avec backend Filament, PWA en VueJS/NuxtJS et application mobile Flutter pour la présentation de recettes de cuisine et d'astuces culinaires.",
                en: "Development of complete solution with Filament backend, VueJS/NuxtJS PWA and Flutter mobile app for presenting cooking recipes and culinary tips."
            },
            technologies: ["Filament", "VueJS", "NuxtJS", "Flutter", "PWA"],
            role: {
                fr: "Architecte Full-stack",
                en: "Full-stack Architect"
            },
            challenges: {
                fr: "Architecture multi-plateforme et synchronisation des données",
                en: "Multi-platform architecture and data synchronization"
            },
            results: {
                fr: "Écosystème complet accessible sur web et mobile",
                en: "Complete ecosystem accessible on web and mobile"
            }
        },
        {
            id: 6,
            title: "CIPREL",
            position: [8, 1, -12],
            color: "#246CB7",
            category: "frontend",
            url: "https://ciprel.ci",
            icon: "electrical_services",
            description: {
                fr: "Site web responsive avec optimisation des performances",
                en: "Responsive website with performance optimization"
            },
            fullDescription: {
                fr: "Développement du site corporate de CIPREL avec focus sur l'expérience utilisateur et les performances.",
                en: "Development of CIPREL corporate website with focus on user experience and performance."
            },
            technologies: ["HTML5", "CSS3", "JavaScript", "Responsive"],
            role: {
                fr: "Développeur Front-end",
                en: "Front-end Developer"
            },
            challenges: {
                fr: "Intégration pixel-perfect et performances",
                en: "Pixel-perfect integration and performance"
            },
            results: {
                fr: "Amélioration de 60% des performances",
                en: "60% performance improvement"
            }
        },
        {
            id: 7,
            title: "Quizz CIPREL RH",
            position: [12, 1, -8],
            color: "#0593fc",
            category: "fullstack",
            url: "https://ciprelrh.netlify.app/questionnaire",
            icon: "quiz",
            description: {
                fr: "Application quiz interactive avec système de scoring avancé",
                en: "Interactive quiz application with advanced scoring system"
            },
            fullDescription: {
                fr: "Plateforme de quiz RH complète avec système de scoring, analytics et reporting pour le SIREXE.",
                en: "Complete HR quiz platform with scoring system, analytics and reporting for SIREXE."
            },
            technologies: ["NuxtJS", "VueJS", "JavaScript"],
            role: {
                fr: "Développeur Full-stack",
                en: "Full-stack Developer"
            },
            challenges: {
                fr: "Système de scoring complexe et analytics",
                en: "Complex scoring system and analytics"
            },
            results: {
                fr: "Interface intuitive avec reporting détaillé",
                en: "Intuitive interface with detailed reporting"
            }
        },
        {
            id: 8,
            title: "Soboa 95 ans",
            position: [14, 1, -4],
            color: "#27CDFE",
            category: "frontend",
            url: "https://soboa95ans.sn",
            icon: "cake",
            description: {
                fr: "Conception et développement complet avec design unique",
                en: "Complete design and development with unique design"
            },
            fullDescription: {
                fr: "Site commémoratif sur-mesure pour les 95 ans de Soboa avec design unique et animations personnalisées.",
                en: "Custom commemorative website for Soboa's 95th anniversary with unique design and custom animations."
            },
            technologies: ["HTML5", "CSS3", "JavaScript", "Design"],
            role: {
                fr: "Designer & Développeur",
                en: "Designer & Developer"
            },
            challenges: {
                fr: "Design unique et animations fluides",
                en: "Unique design and smooth animations"
            },
            results: {
                fr: "Site commémoratif remarqué par l'industrie",
                en: "Commemorative website recognized by industry"
            }
        },
        {
            id: 9,
            title: "BigFive360",
            position: [12, 1, 0],
            color: "#246CB7",
            category: "frontend",
            url: "https://bigfive360.com",
            icon: "360",
            description: {
                fr: "Site web présentant un service de visite virtuelle",
                en: "Website presenting virtual tour services"
            },
            fullDescription: {
                fr: "Développement d'un site web moderne pour présenter les services de visite virtuelle 360° avec galeries interactives et présentation des offres.",
                en: "Development of modern website to present 360° virtual tour services with interactive galleries and service presentation."
            },
            technologies: ["HTML5", "CSS3", "JavaScript", "Responsive"],
            role: {
                fr: "Développeur Front-end",
                en: "Front-end Developer"
            },
            challenges: {
                fr: "Intégration d'éléments interactifs et optimisation visuelle",
                en: "Interactive elements integration and visual optimization"
            },
            results: {
                fr: "Site moderne présentant efficacement les services de visite virtuelle",
                en: "Modern website effectively presenting virtual tour services"
            }
        },
        {
            id: 10,
            title: "BBlome",
            position: [8, 1, 4],
            color: "#0593fc",
            category: "wordpress",
            url: "https://bblome.com",
            icon: "local_bar",
            description: {
                fr: "Site web WordPress présentant la brasserie BBlome",
                en: "WordPress website presenting BBlome brewery"
            },
            fullDescription: {
                fr: "Développement d'un site web WordPress sur-mesure pour présenter la brasserie BBlome, ses produits et son histoire avec design attractif.",
                en: "Development of custom WordPress website to present BBlome brewery, its products and history with attractive design."
            },
            technologies: ["WordPress", "PHP", "CSS3", "JavaScript"],
            role: {
                fr: "Intégrateur WordPress",
                en: "WordPress Integrator"
            },
            challenges: {
                fr: "Design attractif et présentation optimale des produits",
                en: "Attractive design and optimal product presentation"
            },
            results: {
                fr: "Site web professionnel valorisant l'image de la brasserie",
                en: "Professional website enhancing brewery's image"
            }
        },
        {
            id: 11,
            title: "BigFive Solutions",
            position: [4, 1, 6],
            color: "#27CDFE",
            category: "frontend",
            url: "https://bigfive.solutions/",
            icon: "design_services",
            description: {
                fr: "Intégration fidèle des maquettes avec composants réutilisables",
                en: "Faithful mockup integration with reusable components"
            },
            fullDescription: {
                fr: "Site corporate avec système de design complet et composants réutilisables basés sur les maquettes Adobe XD.",
                en: "Corporate website with complete design system and reusable components based on Adobe XD mockups."
            },
            technologies: ["VueJS", "Design System", "Adobe XD"],
            role: {
                fr: "Développeur Front-end",
                en: "Front-end Developer"
            },
            challenges: {
                fr: "Design System et composants réutilisables",
                en: "Design System and reusable components"
            },
            results: {
                fr: "Système de design adopté par toute l'équipe",
                en: "Design system adopted by entire team"
            }
        },
        {
            id: 12,
            title: "Dashboard Timeo RH",
            position: [0, 1, 8],
            color: "#246CB7",
            category: "figma",
            url: "https://timeo-rh.vercel.app/",
            icon: "dashboard",
            description: {
                fr: "Conception sur Figma et conversion en frontend VueJS pour tableau de bord RH",
                en: "Figma design conception and VueJS frontend conversion for HR dashboard"
            },
            fullDescription: {
                fr: "Conception complète d'un dashboard RH sur Figma puis développement de l'interface utilisateur en VueJS avec fonctionnalités avancées de gestion des ressources humaines.",
                en: "Complete HR dashboard design on Figma then user interface development in VueJS with advanced human resources management features."
            },
            technologies: ["Figma", "VueJS", "UI/UX Design", "Dashboard"],
            role: {
                fr: "UI/UX Designer & Développeur Full-stack",
                en: "UI/UX Designer & Full-stack Developer"
            },
            challenges: {
                fr: "Conception UX/UI intuitive et développement d'interface complexe",
                en: "Intuitive UX/UI design and complex interface development"
            },
            results: {
                fr: "Dashboard moderne et fonctionnel pour la gestion RH",
                en: "Modern and functional dashboard for HR management"
            }
        },
        {
            id: 13,
            title: "App Mobile TimeoRH",
            position: [-4, 1, 6],
            color: "#0593fc",
            category: "figma",
            url: "https://www.figma.com/proto/2020d0oYwqBP5iDNsvSZCx/TimeoRH-v1?node-id=1-123&starting-point-node-id=1%3A73",
            icon: "phone_android",
            description: {
                fr: "Prototype mobile complet sur Figma pour application RH",
                en: "Complete mobile prototype on Figma for HR application"
            },
            fullDescription: {
                fr: "Conception d'une application mobile complète pour la gestion des ressources humaines avec interface intuitive et expérience utilisateur optimisée.",
                en: "Complete mobile application design for human resources management with intuitive interface and optimized user experience."
            },
            technologies: ["Figma", "Mobile Design", "UI/UX", "Prototyping"],
            role: {
                fr: "UI/UX Designer",
                en: "UI/UX Designer"
            },
            challenges: {
                fr: "Design mobile responsive et expérience utilisateur fluide",
                en: "Responsive mobile design and smooth user experience"
            },
            results: {
                fr: "Prototype mobile interactif prêt pour développement",
                en: "Interactive mobile prototype ready for development"
            }
        },
        {
            id: 14,
            title: "Kekeli Power",
            position: [-8, 1, 4],
            color: "#27CDFE",
            category: "figma",
            url: "https://www.figma.com/proto/oDDg1iznhgcetzRrxBLrh1/Kekeli?node-id=1430-2082&t=V7VYhGmearVdFi7x-0",
            icon: "electric_bolt",
            description: {
                fr: "Interface utilisateur moderne pour application énergétique",
                en: "Modern user interface for energy application"
            },
            fullDescription: {
                fr: "Conception d'interface pour application dans le domaine énergétique avec focus sur l'expérience utilisateur et l'accessibilité des données techniques.",
                en: "Interface design for energy sector application with focus on user experience and technical data accessibility."
            },
            technologies: ["Figma", "UI/UX Design", "Energy Tech"],
            role: {
                fr: "UI/UX Designer",
                en: "UI/UX Designer"
            },
            challenges: {
                fr: "Interface technique accessible et design moderne",
                en: "Accessible technical interface and modern design"
            },
            results: {
                fr: "Design system complet pour application énergétique",
                en: "Complete design system for energy application"
            }
        },
        {
            id: 15,
            title: "Fondation Hamadou Hampathé Ba",
            position: [-12, 1, 0],
            color: "#246CB7",
            category: "figma",
            url: "https://www.figma.com/proto/RkKr0fIma2HZ1JP9mi6jQu/Untitled?node-id=1-14",
            icon: "account_balance",
            description: {
                fr: "Site web institutionnel avec design culturel authentique",
                en: "Institutional website with authentic cultural design"
            },
            fullDescription: {
                fr: "Conception d'un site web pour la fondation culturelle avec respect des valeurs traditionnelles et interface moderne adaptée au contenu éducatif.",
                en: "Website design for cultural foundation respecting traditional values with modern interface adapted to educational content."
            },
            technologies: ["Figma", "Cultural Design", "UI/UX"],
            role: {
                fr: "UI/UX Designer",
                en: "UI/UX Designer"
            },
            challenges: {
                fr: "Design culturel respectueux et interface moderne",
                en: "Respectful cultural design and modern interface"
            },
            results: {
                fr: "Site institutionnel alliant tradition et modernité",
                en: "Institutional site combining tradition and modernity"
            }
        },
        {
            id: 16,
            title: "Jeu CIPREL Drag & Drop",
            position: [-14, 1, -4],
            color: "#0593fc",
            category: "fullstack",
            url: "https://jeuciprel.vercel.app/",
            icon: "games",
            description: {
                fr: "Jeu interactif avec fonctionnalités de glisser-déposer pour formation ludique",
                en: "Interactive game with drag and drop functionality for educational training"
            },
            fullDescription: {
                fr: "Développement d'un jeu éducatif interactif utilisant les API de glisser-déposer natif pour la formation et l'apprentissage ludique.",
                en: "Development of interactive educational game using native drag and drop APIs for training and gamified learning."
            },
            technologies: ["JavaScript", "Drag & Drop API", "HTML5", "CSS3"],
            role: {
                fr: "Développeur Full-stack",
                en: "Full-stack Developer"
            },
            challenges: {
                fr: "Implémentation des interactions de glisser-déposer fluides",
                en: "Implementation of smooth drag and drop interactions"
            },
            results: {
                fr: "Jeu éducatif interactif pour formation en entreprise",
                en: "Interactive educational game for corporate training"
            }
        },
        {
            id: 17,
            title: "Soeguibe",
            position: [-16, 1, -8],
            color: "#27CDFE",
            category: "wordpress",
            url: "https://soeguibe.com",
            icon: "web",
            description: {
                fr: "Template WordPress personnalisé avec éditeur avancé",
                en: "Custom WordPress template with advanced editor"
            },
            fullDescription: {
                fr: "Développement d'un thème WordPress sur-mesure avec éditeur Gutenberg personnalisé et fonctionnalités avancées.",
                en: "Development of custom WordPress theme with custom Gutenberg editor and advanced features."
            },
            technologies: ["WordPress", "Gutenberg", "PHP", "Custom Post Types"],
            role: {
                fr: "Intégrateur WordPress",
                en: "WordPress Integrator"
            },
            challenges: {
                fr: "Éditeur personnalisé et fonctionnalités avancées",
                en: "Custom editor and advanced features"
            },
            results: {
                fr: "Template WordPress flexible et performant",
                en: "Flexible and high-performance WordPress template"
            }
        },
        {
            id: 18,
            title: "SoboaFoot - Pronostics CAN 2025",
            position: [-16, 1, 0],
            color: "#0593fc",
            category: "fullstack",
            url: "https://soboafoot.com/",
            icon: "sports_soccer",
            description: {
                fr: "Plateforme de pronostics sportifs pour la CAN 2025 avec système de classement et points",
                en: "Sports prediction gaming platform for CAN 2025 with leaderboard and points system"
            },
            fullDescription: {
                fr: "Développement d'une plateforme de pronostics sportifs pour la Coupe d'Afrique des Nations 2025 avec système de classement, accumulation de points, calendrier des matchs, géolocalisation des partenaires et application mobile dédiée.",
                en: "Development of a sports prediction gaming platform for the 2025 Africa Cup of Nations with leaderboard system, points accumulation, match calendar, partner location mapping and dedicated mobile app."
            },
            technologies: ["Tailwind CSS", "Alpine.js", "Swiper.js", "Service Worker"],
            role: {
                fr: "Développeur Full-stack",
                en: "Full-stack Developer"
            },
            challenges: {
                fr: "Système de scoring en temps réel et gamification avec géolocalisation",
                en: "Real-time scoring system and gamification with geolocation"
            },
            results: {
                fr: "Plateforme engageante avec des milliers de participants actifs durant la CAN 2025",
                en: "Engaging platform with thousands of active participants during CAN 2025"
            }
        },
        {
            id: 19,
            title: "Eat Is Family",
            position: [-14, 1, 4],
            color: "#27CDFE",
            category: "fullstack",
            url: "https://www.eatisfamily.fr/",
            icon: "restaurant",
            description: {
                fr: "Intégration de template Figma sur NuxtJS avec API WordPress headless",
                en: "Figma template integration on NuxtJS with headless WordPress API"
            },
            fullDescription: {
                fr: "Intégration d'un template Figma en application NuxtJS avec CMS headless WordPress pour une entreprise de restauration événementielle spécialisée dans les stades, arènes et festivals en France.",
                en: "Figma template integration into NuxtJS application with headless WordPress CMS for an event catering company specializing in stadiums, arenas and festivals in France."
            },
            technologies: ["NuxtJS", "WordPress API", "Figma", "Vue.js"],
            role: {
                fr: "Développeur Front-end",
                en: "Front-end Developer"
            },
            challenges: {
                fr: "Architecture headless CMS et intégration fidèle du design Figma",
                en: "Headless CMS architecture and faithful Figma design integration"
            },
            results: {
                fr: "Site performant avec gestion de contenu flexible via WordPress",
                en: "High-performance site with flexible content management via WordPress"
            }
        }
    ],
    
    // Sections principales du portfolio
    sections: {
        about: {
            position: [0, 3, -5],
            title: { fr: "Qui je suis", en: "Who I Am" },
            icon: "👤",
            content: {
                fr: "Directeur Solutions Digitales expérimenté avec plus de 12 ans d'expertise en développement web full-stack, design UI/UX et gestion de projets digitaux.",
                en: "Experienced Digital Solutions Director with over 12 years of expertise in full-stack web development, UI/UX design and digital project management."
            }
        },
        experience: {
            position: [8, 3, -5], 
            title: { fr: "Expérience", en: "Experience" },
            icon: "💼",
            content: {
                fr: "Plus de 12 ans d'expérience dans le développement web, la gestion d'équipe et la direction de projets digitaux.",
                en: "Over 12 years of experience in web development, team management and digital project leadership."
            }
        },
        projects: {
            position: [0, 3, -12],
            title: { fr: "Réalisations", en: "Projects" },
            icon: "💻",
            content: {
                fr: "19+ projets réalisés dans divers domaines : frontend, fullstack, WordPress et design UI/UX.",
                en: "19+ projects completed in various fields: frontend, fullstack, WordPress and UI/UX design."
            }
        },
        contact: {
            position: [-8, 3, -5],
            title: { fr: "Contact", en: "Contact" },
            icon: "📧",
            content: {
                fr: "Contactez-moi pour discuter de vos projets digitaux et collaborations.",
                en: "Contact me to discuss your digital projects and collaborations."
            }
        }
    },
    
    // Palette de couleurs Material Design extraite du thème existant
    colors: {
        primary: "#0593fc",
        secondary: "#27CDFE", 
        accent: "#246CB7",
        dark: "#363636",
        grey: "#4a4a4a",
        white: "#ffffff",
        surface: "#ffffff"
    },
    
    // Catégories de projets avec couleurs spécifiques
    categories: {
        frontend: {
            color: "#0593fc",
            icon: "code",
            name: { fr: "Frontend", en: "Frontend" }
        },
        fullstack: {
            color: "#27CDFE", 
            icon: "layers",
            name: { fr: "Full-stack", en: "Full-stack" }
        },
        wordpress: {
            color: "#246CB7",
            icon: "web", 
            name: { fr: "WordPress", en: "WordPress" }
        },
        figma: {
            color: "#0593fc",
            icon: "design_services",
            name: { fr: "Design UI/UX", en: "UI/UX Design" }
        }
    },
    
    // Configuration VR
    vrConfig: {
        environment: {
            preset: "starry",
            groundColor: "#0593fc",
            grid: "1x1",
            fog: {
                type: "exponential",
                density: 0.005,
                color: "#0593fc"
            }
        },
        lighting: {
            ambient: {
                color: "#404040",
                intensity: 0.4
            },
            directional: {
                position: "1 4 1",
                color: "#0593fc", 
                intensity: 0.8
            },
            point: {
                position: "0 10 0",
                color: "#ffffff",
                intensity: 1
            }
        },
        camera: {
            startPosition: "0 1.6 8",
            acceleration: 65
        }
    },
    
    // Textes et traductions
    texts: {
        fr: {
            title: 'Portfolio VR',
            subtitle: 'Jean Luc Houédanou - Directeur Solutions Digitales',
            enterVR: 'Entrer en VR',
            exitVR: 'Retour au portfolio classique', 
            viewProject: 'Voir le projet',
            visitProject: 'Visiter le projet',
            close: 'Fermer',
            role: 'Rôle',
            technologies: 'Technologies',
            description: 'Description',
            challenges: 'Défis',
            results: 'Résultats',
            navigation: 'Utilisez les contrôleurs ou la souris pour naviguer'
        },
        en: {
            title: 'VR Portfolio',
            subtitle: 'Jean Luc Houédanou - Digital Solutions Director',
            enterVR: 'Enter VR',
            exitVR: 'Back to classic portfolio',
            viewProject: 'View Project', 
            visitProject: 'Visit Project',
            close: 'Close',
            role: 'Role',
            technologies: 'Technologies',
            description: 'Description',
            challenges: 'Challenges',
            results: 'Results',
            navigation: 'Use controllers or mouse to navigate'
        }
    }
};