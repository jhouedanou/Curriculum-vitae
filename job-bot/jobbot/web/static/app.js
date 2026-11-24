// JobBot — interactions. Tout marche aussi sans JavaScript (formulaires classiques).
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const JSON_ACCEPT = { Accept: "application/json" };

  // ── Petit message temporaire ───────────────
  let toastMinuterie;
  function toast(texte) {
    const t = $("#toast");
    t.textContent = texte;
    t.hidden = false;
    clearTimeout(toastMinuterie);
    toastMinuterie = setTimeout(() => (t.hidden = true), 2600);
  }

  // ── Copier ─────────────────────────────────
  async function copier(texte) {
    try {
      await navigator.clipboard.writeText(texte);
      return true;
    } catch {
      // http:// sur le téléphone : l'API presse-papiers peut être bloquée
      const zone = document.createElement("textarea");
      zone.value = texte;
      zone.style.position = "fixed";
      zone.style.opacity = "0";
      document.body.append(zone);
      zone.select();
      const ok = document.execCommand("copy");
      zone.remove();
      return ok;
    }
  }
  document.addEventListener("click", async (e) => {
    const b = e.target.closest("[data-copier]");
    if (!b) return;
    const cible = $(b.dataset.copier);
    if (!cible) return;
    const ok = await copier(cible.innerText.trim());
    if (!ok) return toast("Copie impossible : sélectionne le texte à la main.");
    const avant = b.innerHTML;
    b.dataset.copie = "";
    b.innerHTML = b.classList.contains("btn-copier") ? "Copié" : '<svg class="ic"><use href="#i-check"/></svg>Copié';
    setTimeout(() => { b.innerHTML = avant; delete b.dataset.copie; }, 1800);
  });

  // ── Envoi automatique des listes déroulantes ──
  $$("[data-auto-submit]").forEach((s) =>
    s.addEventListener("change", async () => {
      const form = s.form;
      if (form.matches("[data-statut-form]")) {
        const r = await fetch(form.action, { method: "POST", body: new FormData(form), headers: JSON_ACCEPT });
        toast(r.ok ? `Suivi : ${s.selectedOptions[0].text}` : "Échec de l'enregistrement");
        if (r.ok && ["envoye", "entretien"].includes(s.value) && !$("#relance")) location.reload();
        return;
      }
      form.submit();
    })
  );

  // ── Aperçu CV / lettre ─────────────────────
  const apercu = $("#apercu");
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-apercu]");
    if (b && apercu) {
      $("iframe", apercu).src = b.dataset.apercu;
      $(".apercu-titre", apercu).textContent = b.dataset.titre;
      apercu.hidden = false;
      apercu.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    if (e.target.closest("[data-fermer-apercu]") && apercu) {
      apercu.hidden = true;
      $("iframe", apercu).removeAttribute("src");
    }
  });

  // ── Compteur de caractères (coller) ────────
  $$("[data-compteur]").forEach((c) => {
    const champ = $(c.dataset.compteur);
    const maj = () => (c.textContent = champ.value.trim().length.toLocaleString("fr-FR"));
    champ.addEventListener("input", maj);
    maj();
  });

  // ── Tâches de fond (collecte, notation, rédaction) ──
  const panneau = $("#tache");
  let suivie = null;

  function boutons(actifs) {
    $$("[data-tache-form] button").forEach((b) => (b.disabled = !actifs));
  }

  function afficher(t) {
    panneau.hidden = false;
    panneau.dataset.etat = t.etat;
    $(".tache-titre", panneau).textContent = t.titre;
    const m = Math.floor(t.duree / 60), s = t.duree % 60;
    $(".tache-duree", panneau).textContent = m ? `${m} min ${s}s` : `${s}s`;
    const j = $(".tache-journal", panneau);
    const enBas = j.scrollHeight - j.scrollTop - j.clientHeight < 30;
    j.textContent = t.lignes.join("\n");
    if (enBas) j.scrollTop = j.scrollHeight;
    const lien = $(".tache-lien", panneau);
    lien.hidden = t.etat === "en_cours" || !t.lien;
    lien.href = t.lien || "/";
    // Page /taches/<id> (sans JS au départ)
    const jp = $("#journal-page");
    if (jp) {
      jp.textContent = t.lignes.join("\n");
      $("#lien-page").hidden = t.etat === "en_cours";
      $("[data-tache-page]").textContent = { en_cours: "En cours…", ok: "Terminé.", erreur: "Échec." }[t.etat];
    }
  }

  async function suivre(id) {
    suivie = id;
    boutons(false);
    for (;;) {
      let t;
      try {
        const r = await fetch(`/api/taches/${id}`, { headers: JSON_ACCEPT });
        if (!r.ok) break;
        t = await r.json();
      } catch {
        await new Promise((ok) => setTimeout(ok, 3000));
        continue;
      }
      afficher(t);
      if (t.etat !== "en_cours") {
        boutons(true);
        if (t.etat === "ok") {
          const ici = location.pathname;
          const cible = new URL(t.lien || "/", location.href);
          // Résultat sur la page ouverte : on recharge pour l'afficher.
          if (cible.pathname === ici && !$("#journal-page")) {
            sessionStorage.setItem("jobbot-fini", t.titre);
            location.href = cible.href;
            if (cible.hash) location.reload();
          } else if ($("#journal-page") && cible.pathname.endsWith("/adapter")) {
            // Offre enregistrée sans IA : on ouvre tout de suite la page où l'on adapte le CV.
            location.href = cible.href;
          }
        }
        break;
      }
      await new Promise((ok) => setTimeout(ok, 1000));
    }
    suivie = null;
  }

  $(".tache-fermer", panneau)?.addEventListener("click", () => (panneau.hidden = true));

  $$("[data-tache-form]").forEach((form) =>
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (suivie) return toast("Une tâche tourne déjà.");
      const r = await fetch(form.action, { method: "POST", body: new FormData(form), headers: JSON_ACCEPT });
      const data = await r.json().catch(() => ({}));
      if (!r.ok) return toast(data.erreur || "Impossible de lancer la tâche.");
      if (form.action.endsWith("/coller")) {
        location.href = `/taches/${data.id}`;
        return;
      }
      suivre(data.id);
    })
  );

  const enCours = document.body.dataset.tache || $("[data-tache-page]")?.dataset.tachePage;
  if (enCours) suivre(enCours);
  const fini = sessionStorage.getItem("jobbot-fini");
  if (fini) {
    sessionStorage.removeItem("jobbot-fini");
    toast(`${fini} : terminé`);
  }

  // ── Suivi : glisser-déposer + liste déroulante ──
  async function changerStatut(id, statut) {
    const corps = new FormData();
    corps.set("statut", statut);
    const r = await fetch(`/offre/${id}/statut`, { method: "POST", body: corps, headers: JSON_ACCEPT });
    if (!r.ok) toast("Échec de l'enregistrement");
    return r.ok;
  }

  function compter() {
    $$(".colonne").forEach((c) => ($(".compte-col", c).textContent = $$(".carte", c).length));
  }

  let glissee = null;
  $$(".carte").forEach((c) => {
    c.addEventListener("dragstart", (e) => {
      glissee = c;
      c.classList.add("glisse");
      e.dataTransfer.effectAllowed = "move";
    });
    c.addEventListener("dragend", () => { c.classList.remove("glisse"); glissee = null; });
  });
  $$(".colonne").forEach((col) => {
    col.addEventListener("dragover", (e) => { if (glissee) { e.preventDefault(); col.classList.add("survol"); } });
    col.addEventListener("dragleave", (e) => { if (!col.contains(e.relatedTarget)) col.classList.remove("survol"); });
    col.addEventListener("drop", async (e) => {
      e.preventDefault();
      col.classList.remove("survol");
      if (!glissee) return;
      const carte = glissee, depart = carte.parentElement, statut = col.dataset.statut;
      if (depart === $(".cartes", col)) return;
      $(".cartes", col).prepend(carte);
      $(".carte-statut", carte).value = statut;
      compter();
      if (!(await changerStatut(carte.dataset.id, statut))) { depart.prepend(carte); compter(); }
      else toast(`Déplacée dans « ${$("h2", col).firstChild.textContent.trim()} »`);
    });
  });
  $$(".carte-statut").forEach((s) =>
    s.addEventListener("change", async () => {
      const carte = s.closest(".carte");
      if (!(await changerStatut(s.dataset.id, s.value))) return;
      if (s.value === "nouveau") carte.remove();
      else $(`.colonne[data-statut="${s.value}"] .cartes`)?.prepend(carte);
      compter();
      toast(`Suivi : ${s.selectedOptions[0].text}`);
    })
  );

  // Onglets de la page « Adapter » : CV, lettre, email
  $$("[data-onglet]").forEach((bouton) =>
    bouton.addEventListener("click", () => {
      $$("[data-onglet]").forEach((b) => b.setAttribute("aria-selected", String(b === bouton)));
      $$("[data-panneau]").forEach((p) => (p.hidden = p.dataset.panneau !== bouton.dataset.onglet));
    })
  );
})();
