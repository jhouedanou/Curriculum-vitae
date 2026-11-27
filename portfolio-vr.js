/**
 * Galerie VR du portfolio.
 * - Projets : window.PORTFOLIO_PROJECTS (projects-data.js), la même source que index.html.
 * - Charte : mêmes couleurs et polices que index.html. Chaque panneau est un canvas 2D
 *   plaqué sur un plan, ce qui garde Figtree et les accents (les polices 3D d'A-Frame ne les ont pas).
 */
(function () {
    'use strict';

    // ── Charte (valeurs de index.html) ─────────────────────────────────────
    const C = {
        bg: '#111522', surface: '#192236', paper: '#202b43', ink: '#f3eee5', muted: '#a8adbb',
        orange: '#c27a5b', orangeDark: '#e0a083', orangeSoft: 'rgba(194, 122, 91, .18)',
        sage: '#8994e4', sageDark: '#b8beff', sageSoft: 'rgba(137, 148, 228, .16)',
        line: 'rgba(243, 238, 229, .16)', grid: 'rgba(137, 148, 228, .22)'
    };
    const SANS = '"Figtree", system-ui, sans-serif';
    const MONO = 'ui-monospace, SFMono-Regular, Menlo, monospace';

    // ── Géométrie de la galerie ────────────────────────────────────────────
    const RADIUS = 5.6;          // distance des panneaux
    const CARD = 1.9;            // côté d'une carte, en mètres
    const ROW_Y = [1.3, 3.3];    // hauteur des deux rangées
    const FIRST_ANGLE = 31;      // les cartes commencent à ±30° de l'accueil
    const STEP_ANGLE = 298 / 14; // écart entre deux colonnes
    const WALK_RADIUS = 2.4;     // zone où l'on peut marcher

    const FILTERS = ['all', 'frontend', 'fullstack', 'wordpress', 'figma', 'nuxt'];
    const TXT = {
        fr: {
            filters: { all: 'Tous', frontend: 'Frontend', fullstack: 'Full-stack', wordpress: 'WordPress', figma: 'Figma', nuxt: 'Nuxt' },
            kicker: 'Directeur solutions digitales · Abidjan',
            title: 'Je transforme des idées en produits', accent: 'vivants.',
            intro: 'Je conçois, développe et mets en ligne des expériences web qui tiennent la route — du premier pixel au dernier serveur.',
            years: 'ans à construire', projects: 'projets', lookAround: 'Regardez autour de vous · choisissez un projet',
            hint: 'Glisser pour regarder · Z Q S D ou flèches pour avancer · cliquer sur un projet',
            back: '← Portfolio', langLabel: 'Passer en anglais', langBtn: 'EN',
            tech: 'Technologies', desc: 'Description', challenges: 'Défis', results: 'Résultats',
            visit: 'Voir le projet ↗', close: 'Fermer', clickClose: 'Cliquer pour fermer', noPreview: 'Aperçu non disponible',
            loaderKicker: 'Galerie VR', loaderTitle: 'Des projets', loaderAccent: 'à parcourir.', loading: 'Chargement de la galerie…',
            noWebgl: 'Ce navigateur ne peut pas afficher la galerie 3D. Les projets sont aussi sur le portfolio.',
            backLong: '← Retour au portfolio', docTitle: 'Jean Luc Houédanou — Galerie VR'
        },
        en: {
            filters: { all: 'All', frontend: 'Frontend', fullstack: 'Full-stack', wordpress: 'WordPress', figma: 'Figma', nuxt: 'Nuxt' },
            kicker: 'Digital solutions director · Abidjan',
            title: 'I turn ideas into', accent: 'living products.',
            intro: 'I design, build and ship web experiences that hold up — from the first pixel to the last server.',
            years: 'years building', projects: 'projects', lookAround: 'Look around · pick a project',
            hint: 'Drag to look · W A S D or arrows to move · click a project',
            back: '← Portfolio', langLabel: 'Passer en français', langBtn: 'FR',
            tech: 'Technologies', desc: 'Description', challenges: 'Challenges', results: 'Results',
            visit: 'View project ↗', close: 'Close', clickClose: 'Click to close', noPreview: 'No preview available',
            loaderKicker: 'VR gallery', loaderTitle: 'Projects', loaderAccent: 'to walk through.', loading: 'Loading the gallery…',
            noWebgl: 'This browser cannot display the 3D gallery. The projects are also on the portfolio.',
            backLong: '← Back to portfolio', docTitle: 'Jean Luc Houédanou — VR gallery'
        }
    };

    const projects = Array.isArray(window.PORTFOLIO_PROJECTS) ? window.PORTFOLIO_PROJECTS : [];
    const state = {
        lang: new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'fr',
        filter: 'all',
        selected: null
    };
    const t = () => TXT[state.lang];
    const loc = (p, key) => (state.lang === 'fr' ? p[key] : p[key + 'En']) || p[key] || '';
    const $ = id => document.getElementById(id);

    // Garde la caméra dans la zone de marche (hors casque : en VR, le casque décide).
    AFRAME.registerComponent('stay-inside', {
        schema: { radius: { default: WALK_RADIUS } },
        tick: function () {
            if (this.el.sceneEl.is('vr-mode')) return;
            const p = this.el.object3D.position;
            const d = Math.hypot(p.x, p.z);
            if (d > this.data.radius) { const k = this.data.radius / d; p.x *= k; p.z *= k; }
            p.y = 1.6;
        }
    });

    // ── Outils de dessin ───────────────────────────────────────────────────
    function makeCanvas(w, h) {
        const cv = document.createElement('canvas');
        cv.width = w; cv.height = h;
        return { cv: cv, ctx: cv.getContext('2d') };
    }
    function spacing(ctx, px) { if ('letterSpacing' in ctx) ctx.letterSpacing = px + 'px'; }
    function roundRect(ctx, x, y, w, h, r) {
        const rr = typeof r === 'number' ? [r, r, r, r] : r; // haut-gauche, haut-droit, bas-droit, bas-gauche
        ctx.beginPath();
        ctx.moveTo(x + rr[0], y);
        ctx.lineTo(x + w - rr[1], y); ctx.quadraticCurveTo(x + w, y, x + w, y + rr[1]);
        ctx.lineTo(x + w, y + h - rr[2]); ctx.quadraticCurveTo(x + w, y + h, x + w - rr[2], y + h);
        ctx.lineTo(x + rr[3], y + h); ctx.quadraticCurveTo(x, y + h, x, y + h - rr[3]);
        ctx.lineTo(x, y + rr[0]); ctx.quadraticCurveTo(x, y, x + rr[0], y);
        ctx.closePath();
    }
    function wrap(ctx, text, maxW, maxLines) {
        const words = String(text || '').split(/\s+/).filter(Boolean);
        const lines = [];
        let line = '';
        for (let i = 0; i < words.length; i++) {
            const test = line ? line + ' ' + words[i] : words[i];
            if (ctx.measureText(test).width <= maxW || !line) { line = test; continue; }
            lines.push(line); line = words[i];
            if (lines.length === maxLines) break;
        }
        if (lines.length < maxLines && line) lines.push(line);
        const used = lines.join(' ').split(/\s+/).length;
        if (used < words.length && lines.length) {
            let last = lines[lines.length - 1];
            while (last && ctx.measureText(last + '…').width > maxW) last = last.slice(0, -1);
            lines[lines.length - 1] = last.replace(/[\s,;:·—-]+$/, '') + '…';
        }
        return lines;
    }
    function paragraph(ctx, text, x, y, maxW, lineH, maxLines) {
        const lines = wrap(ctx, text, maxW, maxLines);
        lines.forEach((l, i) => ctx.fillText(l, x, y + i * lineH));
        return y + lines.length * lineH;
    }
    function cover(ctx, img, x, y, w, h) {
        const s = Math.max(w / img.naturalWidth, h / img.naturalHeight);
        const sw = w / s, sh = h / s;
        ctx.drawImage(img, (img.naturalWidth - sw) / 2, 0, sw, sh, x, y, w, h); // cadré en haut, comme sur le site
    }
    function panelBackground(ctx, w, h) {
        const g = ctx.createLinearGradient(0, 0, w, h);
        g.addColorStop(0, '#192236'); g.addColorStop(1, '#111522');
        ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
    }
    function border(ctx, w, h, color, lw) {
        ctx.strokeStyle = color || C.line; ctx.lineWidth = lw || 2;
        ctx.strokeRect(ctx.lineWidth / 2, ctx.lineWidth / 2, w - ctx.lineWidth, h - ctx.lineWidth);
    }
    function gridPattern(ctx, x, y, w, h, cell) {
        ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
        ctx.strokeStyle = 'rgba(137, 148, 228, .16)'; ctx.lineWidth = 1;
        for (let gx = x; gx <= x + w; gx += cell) { ctx.beginPath(); ctx.moveTo(gx, y); ctx.lineTo(gx, y + h); ctx.stroke(); }
        for (let gy = y; gy <= y + h; gy += cell) { ctx.beginPath(); ctx.moveTo(x, gy); ctx.lineTo(x + w, gy); ctx.stroke(); }
        ctx.restore();
    }
    function tags(ctx, list, x, y, maxW, size, maxRows) {
        const padX = Math.round(size * .7), boxH = Math.round(size * 2), gap = Math.round(size * .5);
        ctx.font = '600 ' + size + 'px ' + MONO; spacing(ctx, 0); ctx.textBaseline = 'middle';
        let cx = x, cy = y, row = 1;
        (list || []).forEach((label, i) => {
            const w = ctx.measureText(label).width + padX * 2;
            if (cx + w > x + maxW && cx > x) { row++; cx = x; cy += boxH + gap; }
            if (row > maxRows) return;
            const orange = i % 2 === 0;
            ctx.fillStyle = orange ? C.orangeSoft : C.sageSoft;
            roundRect(ctx, cx, cy, w, boxH, 4); ctx.fill();
            ctx.strokeStyle = orange ? 'rgba(194, 122, 91, .45)' : 'rgba(137, 148, 228, .45)'; ctx.lineWidth = 1; ctx.stroke();
            ctx.fillStyle = orange ? C.orangeDark : C.sageDark;
            ctx.fillText(label, cx + padX, cy + boxH / 2 + 1);
            cx += w + gap;
        });
        ctx.textBaseline = 'alphabetic';
        return cy + boxH;
    }
    const pad2 = n => (n < 10 ? '0' : '') + n;

    // ── Panneaux 3D ────────────────────────────────────────────────────────
    function addPanel(parent, cv, w, h, clickable) {
        const el = document.createElement('a-entity');
        if (clickable) el.classList.add('clickable');
        parent.appendChild(el);
        const tex = new THREE.CanvasTexture(cv);
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.anisotropy = 8;
        const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex }));
        el.setObject3D('mesh', mesh);
        return { el: el, tex: tex, mesh: mesh };
    }
    function addOutline(panel, w, h, color) {
        const m = new THREE.Mesh(new THREE.PlaneGeometry(w + .06, h + .06), new THREE.MeshBasicMaterial({ color: color }));
        m.position.z = -.01; m.visible = false;
        panel.el.object3D.add(m);
        return m;
    }
    function place(el, angleDeg, radius, y, tiltDeg) {
        const a = THREE.MathUtils.degToRad(angleDeg);
        el.object3D.position.set(radius * Math.sin(a), y, -radius * Math.cos(a));
        el.object3D.rotation.set(THREE.MathUtils.degToRad(tiltDeg || 0), -a, 0, 'YXZ');
    }
    function pointer(on) { const cv = $('scene').canvas; if (cv) cv.classList.toggle('is-pointing', on); }

    // ── Carte d'un projet (640 × 640) ──────────────────────────────────────
    function drawCard(card) {
        const ctx = card.ctx, p = card.project, W = 640, TH = 400;
        panelBackground(ctx, W, W);
        if (card.img) {
            cover(ctx, card.img, 0, 0, W, TH);
        } else {
            ctx.fillStyle = C.paper; ctx.fillRect(0, 0, W, TH);
            gridPattern(ctx, 0, 0, W, TH, 40);
            ctx.fillStyle = 'rgba(184, 190, 255, .28)'; ctx.font = '600 190px ' + SANS; spacing(ctx, -8); ctx.textAlign = 'center';
            ctx.fillText(pad2(card.index + 1), W / 2, 262);
            ctx.fillStyle = C.muted; ctx.font = '600 17px ' + MONO; spacing(ctx, 2);
            ctx.fillText(t().noPreview.toUpperCase(), W / 2, 346);
            ctx.textAlign = 'left';
        }
        ctx.fillStyle = C.line; ctx.fillRect(0, TH, W, 2);

        ctx.fillStyle = C.sageDark; ctx.font = '500 22px ' + MONO; spacing(ctx, 0);
        ctx.fillText(pad2(card.index + 1), 34, 442);
        ctx.fillStyle = C.muted; ctx.font = '600 16px ' + MONO; spacing(ctx, 2);
        ctx.fillText(wrap(ctx, loc(p, 'role').toUpperCase(), 500, 1)[0] || '', 80, 441);

        ctx.fillStyle = C.ink; ctx.font = '600 42px ' + SANS; spacing(ctx, -2);
        const end = paragraph(ctx, p.title, 34, 500, 572, 46, 2);
        tags(ctx, (p.technologies || []).slice(0, 3), 34, Math.min(end - 22, 586), 572, 15, 1);
        border(ctx, W, W);
        card.panel.tex.needsUpdate = true;
    }

    // ── Panneau d'accueil (1440 × 960) ─────────────────────────────────────
    function drawIntro(intro) {
        const ctx = intro.ctx, W = 1440, H = 960;
        const g = ctx.createLinearGradient(0, 0, W, H);
        g.addColorStop(0, '#202b43'); g.addColorStop(1, '#192236');
        ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
        gridPattern(ctx, 0, 0, W, H, 72);

        // Portrait, avec les coins asymétriques de la page « À propos »
        const px = 80, py = 120, pw = 420, ph = 560;
        ctx.save(); roundRect(ctx, px, py, pw, ph, [8, 96, 8, 96]); ctx.clip();
        if (intro.img) cover(ctx, intro.img, px, py, pw, ph); else { ctx.fillStyle = C.surface; ctx.fillRect(px, py, pw, ph); }
        ctx.restore();
        roundRect(ctx, px, py, pw, ph, [8, 96, 8, 96]); ctx.strokeStyle = C.line; ctx.lineWidth = 2; ctx.stroke();
        ctx.strokeStyle = 'rgba(137, 148, 228, .38)'; ctx.strokeRect(px + 26, py + 26, pw, ph);

        // Étiquette « N+ » : années calculées par experience-data.js
        ctx.fillStyle = '#192236'; roundRect(ctx, px - 30, py + ph - 70, 300, 130, 4); ctx.fill();
        ctx.strokeStyle = C.line; ctx.stroke();
        ctx.fillStyle = C.orangeDark; ctx.font = '500 64px ' + MONO; spacing(ctx, -2); ctx.fillText(window.ANNEES_EXPERIENCE + '+', px - 4, py + ph + 2);
        ctx.fillStyle = C.muted; ctx.font = '600 18px ' + MONO; spacing(ctx, 2); ctx.fillText(t().years.toUpperCase(), px - 4, py + ph + 36);

        const x = 590, maxW = 780;
        ctx.fillStyle = C.sageDark; ctx.font = '600 24px ' + MONO; spacing(ctx, 3);
        ctx.fillText(t().kicker.toUpperCase(), x, 176);

        // Titre : dernier mot en cuivre, comme sur le site
        ctx.font = '600 92px ' + SANS; spacing(ctx, -5);
        const lines = wrap(ctx, t().title, maxW, 3);
        let y = 286;
        ctx.fillStyle = C.ink;
        lines.forEach(l => { ctx.fillText(l, x, y); y += 96; });
        const lastW = ctx.measureText(lines[lines.length - 1] + ' ').width;
        ctx.fillStyle = C.orangeDark;
        if (lastW + ctx.measureText(t().accent).width <= maxW) ctx.fillText(t().accent, x + lastW, y - 96);
        else { ctx.fillText(t().accent, x, y); y += 96; }

        ctx.fillStyle = C.muted; ctx.font = '400 32px ' + SANS; spacing(ctx, 0);
        y = paragraph(ctx, t().intro, x, y + 4, maxW, 46, 4);

        ctx.fillStyle = C.line; ctx.fillRect(x, 792, maxW, 2);
        ctx.fillStyle = C.orangeDark; ctx.font = '600 22px ' + MONO; spacing(ctx, 2);
        ctx.fillText(t().lookAround.toUpperCase(), x, 846);
        ctx.fillStyle = C.muted;
        ctx.fillText(projects.length + ' ' + t().projects.toUpperCase(), x, 884);
        border(ctx, W, H);
        intro.panel.tex.needsUpdate = true;
    }

    // ── Bouton de la console (320 × 104) ───────────────────────────────────
    function drawButton(btn) {
        const ctx = btn.ctx, W = 320, H = 104;
        const active = btn.filter && btn.filter === state.filter;
        ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
        ctx.fillStyle = btn.primary ? C.orange : (active ? 'rgba(137, 148, 228, .30)' : C.surface);
        ctx.fillRect(0, 0, W, H);
        border(ctx, W, H, btn.primary ? C.orange : (active || btn.hover ? C.sage : C.line), active || btn.hover ? 5 : 2);
        ctx.fillStyle = btn.primary ? '#1b1420' : (active ? C.sageDark : (btn.hover ? C.ink : C.muted));
        ctx.font = '600 34px ' + SANS; spacing(ctx, 0); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(btn.label(), W / 2, H / 2 + 2);
        ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
        btn.panel.tex.needsUpdate = true;
    }

    // ── Fiche détaillée dans la scène, pour le casque (1280 × 880) ─────────
    function drawDetail(detail, card) {
        const ctx = detail.ctx, p = card.project, W = 1280, H = 880;
        const g = ctx.createLinearGradient(0, 0, W, H);
        g.addColorStop(0, '#202b43'); g.addColorStop(1, '#192236');
        ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

        const lx = 56, lw = 520;
        if (card.img) cover(ctx, card.img, lx, 60, lw, 325); else { ctx.fillStyle = C.surface; ctx.fillRect(lx, 60, lw, 325); gridPattern(ctx, lx, 60, lw, 325, 40); }
        ctx.strokeStyle = C.line; ctx.lineWidth = 2; ctx.strokeRect(lx, 60, lw, 325);
        ctx.fillStyle = C.sageDark; ctx.font = '600 20px ' + MONO; spacing(ctx, 2);
        ctx.fillText(t().tech.toUpperCase(), lx, 440);
        const tagsEnd = tags(ctx, p.technologies || [], lx, 462, lw, 19, 4);
        ctx.fillStyle = C.orangeDark; ctx.font = '500 21px ' + MONO; spacing(ctx, 0);
        ctx.fillText(wrap(ctx, String(p.url || '').replace(/^https?:\/\//, '').replace(/\/$/, ''), lw, 1)[0] || '', lx, Math.min(tagsEnd + 54, 760));

        const x = 640, mw = 584;
        ctx.fillStyle = C.sageDark; ctx.font = '600 20px ' + MONO; spacing(ctx, 2);
        ctx.fillText(wrap(ctx, loc(p, 'role').toUpperCase(), mw, 1)[0] || '', x, 86);
        ctx.fillStyle = C.ink; ctx.font = '600 54px ' + SANS; spacing(ctx, -3);
        let y = paragraph(ctx, p.title, x, 150, mw, 58, 2);
        [['desc', 'fullDescription', 7], ['challenges', 'challenges', 3], ['results', 'results', 3]].forEach(part => {
            y += 14;
            ctx.fillStyle = C.sageDark; ctx.font = '600 20px ' + MONO; spacing(ctx, 2);
            ctx.fillText(t()[part[0]].toUpperCase(), x, y);
            ctx.fillStyle = C.muted; ctx.font = '400 25px ' + SANS; spacing(ctx, 0);
            y = paragraph(ctx, loc(p, part[1]), x, y + 38, mw, 35, part[2]);
        });

        ctx.fillStyle = C.line; ctx.fillRect(56, H - 78, W - 112, 2);
        ctx.fillStyle = C.muted; ctx.font = '600 19px ' + MONO; spacing(ctx, 2);
        ctx.fillText(t().clickClose.toUpperCase(), 56, H - 36);
        border(ctx, W, H, C.sage, 3);
        detail.panel.tex.needsUpdate = true;
    }

    // ── Décor : sol quadrillé, anneaux, points lumineux ────────────────────
    function buildFloor(root) {
        const c = makeCanvas(128, 128), ctx = c.ctx;
        ctx.fillStyle = C.bg; ctx.fillRect(0, 0, 128, 128);
        ctx.fillStyle = C.grid; ctx.fillRect(0, 0, 128, 2); ctx.fillRect(0, 0, 2, 128);
        const tex = new THREE.CanvasTexture(c.cv);
        tex.colorSpace = THREE.SRGBColorSpace; tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.repeat.set(80, 80); tex.anisotropy = 8;
        const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.MeshBasicMaterial({ map: tex }));
        floor.rotation.x = -Math.PI / 2;
        root.object3D.add(floor);

        [[WALK_RADIUS + .35, C.orange, .55], [RADIUS + .9, C.sage, .45]].forEach(r => {
            const ring = new THREE.Mesh(new THREE.RingGeometry(r[0], r[0] + .035, 128), new THREE.MeshBasicMaterial({ color: r[1], transparent: true, opacity: r[2], side: THREE.DoubleSide }));
            ring.rotation.x = -Math.PI / 2; ring.position.y = .01;
            root.object3D.add(ring);
        });

        const pts = [];
        for (let i = 0; i < 260; i++) {
            const a = Math.random() * Math.PI * 2, e = .25 + Math.random() * 1.2, d = 22 + Math.random() * 8;
            pts.push(d * Math.cos(e) * Math.sin(a), d * Math.sin(e), d * Math.cos(e) * Math.cos(a));
        }
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
        root.object3D.add(new THREE.Points(geo, new THREE.PointsMaterial({ color: C.sageDark, size: .09, transparent: true, opacity: .55, fog: false })));
    }

    // ── Assemblage ─────────────────────────────────────────────────────────
    const cards = [];
    const buttons = [];
    let intro, detail;

    function matches(p) {
        if (state.filter === 'all') return true;
        if (state.filter === 'nuxt') return (p.technologies || []).some(x => x.toLowerCase().includes('nuxt'));
        return p.category === state.filter;
    }
    function refreshRaycasters() {
        document.querySelectorAll('[raycaster]').forEach(el => { const r = el.components.raycaster; if (r) r.refreshObjects(); });
    }
    function layout() {
        let n = 0;
        cards.forEach(card => {
            const show = matches(card.project);
            card.panel.el.object3D.visible = show;
            card.panel.el.classList.toggle('clickable', show);
            if (!show) return;
            // Colonnes de 2 cartes, posées en alternance à droite puis à gauche de l'accueil
            const col = Math.floor(n / 2), row = n % 2;
            const side = col % 2 === 0 ? 1 : -1, rank = Math.floor(col / 2);
            const angle = side * (FIRST_ANGLE + STEP_ANGLE * (rank + .5));
            place(card.panel.el, angle, RADIUS, ROW_Y[row], row === 1 ? 16 : 0);
            card.angle = angle;
            n++;
        });
        refreshRaycasters();
    }

    function inHeadset() { return $('scene').is('vr-mode'); }
    function showDetail(card) {
        if (!card || !inHeadset()) { detail.panel.el.object3D.visible = false; detail.panel.el.classList.remove('clickable'); return; }
        drawDetail(detail, card);
        place(detail.panel.el, card.angle, 3.3, 1.7, 0);
        detail.panel.el.object3D.visible = true;
        detail.panel.el.classList.add('clickable');
    }
    function fillSheet(card) {
        const sheet = $('sheet');
        if (!card) { sheet.hidden = true; return; }
        const p = card.project;
        $('sheet-role').textContent = loc(p, 'role');
        $('sheet-title').textContent = p.title;
        $('sheet-tags').replaceChildren.apply($('sheet-tags'), (p.technologies || []).map((x, i) => {
            const s = document.createElement('span'); s.className = 'vr-tag ' + (i % 2 ? 'vr-tag--sage' : 'vr-tag--orange'); s.textContent = x; return s;
        }));
        $('sheet-l1').textContent = t().desc; $('sheet-desc').textContent = loc(p, 'fullDescription');
        $('sheet-l2').textContent = t().challenges; $('sheet-challenges').textContent = loc(p, 'challenges');
        $('sheet-l3').textContent = t().results; $('sheet-results').textContent = loc(p, 'results');
        $('sheet-link').textContent = t().visit; $('sheet-link').href = p.url;
        $('sheet-close').setAttribute('aria-label', t().close);
        sheet.hidden = false;
    }
    function select(card) {
        if (state.selected) state.selected.outline.visible = false;
        state.selected = card && card !== state.selected ? card : null;
        if (state.selected) state.selected.outline.visible = true;
        fillSheet(state.selected);
        showDetail(state.selected);
        refreshRaycasters();
    }
    function setFilter(f) {
        state.filter = f;
        if (state.selected && !matches(state.selected.project)) select(null);
        buttons.forEach(drawButton);
        document.querySelectorAll('#filters button').forEach(b => b.classList.toggle('is-active', b.dataset.filter === f));
        layout();
    }
    function setLang(lang) {
        state.lang = lang;
        document.documentElement.lang = lang;
        document.title = t().docTitle;
        const url = new URL(location.href); url.searchParams.set('lang', lang); history.replaceState(null, '', url);
        $('lang').textContent = t().langBtn; $('lang').setAttribute('aria-label', t().langLabel);
        $('back').textContent = t().back; $('hint').textContent = t().hint;
        $('loader-back').textContent = t().backLong;
        document.querySelectorAll('#filters button').forEach(b => { b.textContent = t().filters[b.dataset.filter]; });
        cards.forEach(drawCard); buttons.forEach(drawButton); drawIntro(intro);
        fillSheet(state.selected); showDetail(state.selected);
    }

    function hoverable(target, onEnter, onLeave) {
        target.addEventListener('mouseenter', () => { pointer(true); onEnter(); });
        target.addEventListener('mouseleave', () => { pointer(false); onLeave(); });
    }

    function build() {
        const scene = $('scene');
        buildFloor($('floor'));

        // Accueil, face à l'entrée
        const ic = makeCanvas(1440, 960);
        intro = { ctx: ic.ctx, panel: addPanel($('intro'), ic.cv, 3.6, 2.4, false), img: null };
        place(intro.panel.el, 0, RADIUS, 2.2, 0);
        const portrait = new Image();
        portrait.onload = () => { intro.img = portrait; drawIntro(intro); };
        portrait.src = '1764523183346.jpg';

        // Console : filtres + langue, inclinée devant l'accueil
        const defs = FILTERS.map(f => ({ filter: f, label: () => t().filters[f], action: () => setFilter(f) }));
        defs.push({ primary: true, label: () => t().langBtn, action: () => setLang(state.lang === 'fr' ? 'en' : 'fr') });
        defs.forEach((d, i) => {
            const c = makeCanvas(320, 104);
            const btn = Object.assign({ ctx: c.ctx, hover: false, panel: addPanel($('controls'), c.cv, .56, .182, true) }, d);
            place(btn.panel.el, (i - (defs.length - 1) / 2) * 10.4, 3.4, .8, -30);
            hoverable(btn.panel.el, () => { btn.hover = true; drawButton(btn); }, () => { btn.hover = false; drawButton(btn); });
            btn.panel.el.addEventListener('click', btn.action);
            buttons.push(btn);
        });

        // Cartes des projets
        projects.forEach((p, i) => {
            const c = makeCanvas(640, 640);
            const panel = addPanel($('gallery'), c.cv, CARD, CARD, true);
            const card = { project: p, index: i, ctx: c.ctx, panel: panel, img: null, angle: 0, outline: addOutline(panel, CARD, CARD, C.orange) };
            hoverable(panel.el,
                () => { card.outline.visible = true; panel.mesh.scale.setScalar(1.04); },
                () => { card.outline.visible = state.selected === card; panel.mesh.scale.setScalar(1); });
            panel.el.addEventListener('click', () => select(card));
            if (p.thumb) {
                const img = new Image();
                img.onload = () => { card.img = img; drawCard(card); if (state.selected === card) showDetail(card); };
                img.src = p.thumb;
            }
            cards.push(card);
        });

        // Fiche 3D (casque uniquement)
        const dc = makeCanvas(1280, 880);
        detail = { ctx: dc.ctx, panel: addPanel($('detail'), dc.cv, 2.7, 1.86, false) };
        $('detail').setAttribute('visible', 'true');
        detail.panel.el.object3D.visible = false;
        detail.panel.el.addEventListener('click', () => select(null));
        scene.addEventListener('enter-vr', () => showDetail(state.selected));
        scene.addEventListener('exit-vr', () => showDetail(null));

        // Habillage 2D
        FILTERS.forEach(f => {
            const b = document.createElement('button');
            b.type = 'button'; b.dataset.filter = f;
            b.addEventListener('click', () => setFilter(f));
            $('filters').appendChild(b);
        });
        $('lang').addEventListener('click', () => setLang(state.lang === 'fr' ? 'en' : 'fr'));
        $('sheet-close').addEventListener('click', () => select(null));
        document.addEventListener('keydown', e => { if (e.key === 'Escape') select(null); });

        setLang(state.lang);
        setFilter('all');
        $('loader').classList.add('is-done');
        window.vrGallery = { state: state, cards: cards, select: select, setFilter: setFilter, setLang: setLang }; // pour les tests
    }

    function fail() {
        $('loader').classList.remove('is-done');
        $('loader-text').textContent = t().noWebgl;
        $('loader-back').hidden = false;
    }
    function hasWebGL() {
        try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; }
    }

    window.addEventListener('DOMContentLoaded', () => {
        document.documentElement.lang = state.lang;
        $('loader-kicker').textContent = t().loaderKicker;
        $('loader-title').firstChild.textContent = t().loaderTitle + ' ';
        $('loader-title').querySelector('span').textContent = t().loaderAccent;
        $('loader-text').textContent = t().loading;
        $('loader-back').textContent = t().backLong;
        if (!hasWebGL()) { fail(); return; }

        // Les polices doivent être prêtes avant de dessiner dans les canvas.
        const fonts = document.fonts
            ? Promise.all(['400 30px Figtree', '500 30px Figtree', '600 40px Figtree'].map(f => document.fonts.load(f))).catch(() => {})
            : Promise.resolve();
        const scene = $('scene');
        const ready = new Promise(res => (scene.hasLoaded ? res() : scene.addEventListener('loaded', res, { once: true })));
        Promise.all([Promise.race([fonts, new Promise(r => setTimeout(r, 3000))]), ready])
            .then(build)
            .catch(err => { console.error(err); fail(); });
    });
})();
