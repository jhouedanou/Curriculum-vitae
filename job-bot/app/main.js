/**
 * JobBot — application de bureau.
 *
 * Elle lance le serveur du bot en arrière-plan (sur cet ordinateur seulement), affiche son interface
 * dans une fenêtre, et crée les PDF elle-même : aucune ligne de commande, aucun Python à installer.
 */
const { app, BrowserWindow, Menu, dialog, shell } = require('electron');
const { spawn } = require('child_process');
const crypto = require('crypto');
const fs = require('fs');
const http = require('http');
const net = require('net');
const os = require('os');
const path = require('path');

const ESSAI = process.env.JOBBOT_SMOKE === '1'; // essai automatique : démarre, vérifie, quitte
const FICHIERS_MODELE = ['cv.yaml', 'cv_en.yaml', 'config.yaml', 'photo.jpg', 'templates'];

let serveur = null;      // processus du bot
let fenetre = null;
let adresse = '';        // http://127.0.0.1:<port>
let journal = [];        // dernières lignes écrites par le bot, pour le message d'erreur
let crochetPdf = null;   // { url, jeton } : adresse où le bot demande un PDF

// ── Dossier de données ─────────────────────────────────────────────────────
const fichierReglages = () => path.join(app.getPath('userData'), 'reglages.json');
function lireReglages() {
  try { return JSON.parse(fs.readFileSync(fichierReglages(), 'utf-8')); } catch { return {}; }
}
function ecrireReglages(r) {
  fs.mkdirSync(path.dirname(fichierReglages()), { recursive: true });
  fs.writeFileSync(fichierReglages(), JSON.stringify(r, null, 2));
}
function dossierModele() {
  // Application installée : copie livrée avec elle. En développement : le dossier job-bot du dépôt.
  return app.isPackaged ? path.join(process.resourcesPath, 'modele') : path.join(__dirname, '..');
}
function dossierDonnees() {
  if (process.env.JOBBOT_HOME) return process.env.JOBBOT_HOME;
  const r = lireReglages();
  if (r.dossier && fs.existsSync(r.dossier)) return r.dossier;
  return app.isPackaged ? path.join(app.getPath('documents'), 'JobBot') : path.join(__dirname, '..');
}
/** Premier lancement : on dépose le CV, les réglages et les gabarits dans le dossier de données. */
function preparerDonnees(dossier) {
  fs.mkdirSync(dossier, { recursive: true });
  const modele = dossierModele();
  if (path.resolve(modele) === path.resolve(dossier)) return;
  for (const nom of FICHIERS_MODELE) {
    const source = path.join(modele, nom), cible = path.join(dossier, nom);
    if (fs.existsSync(source) && !fs.existsSync(cible)) fs.cpSync(source, cible, { recursive: true });
  }
}

// ── Outils réseau ──────────────────────────────────────────────────────────
function portLibre() {
  return new Promise((ok, ko) => {
    const s = net.createServer();
    s.unref();
    s.on('error', ko);
    s.listen(0, '127.0.0.1', () => { const { port } = s.address(); s.close(() => ok(port)); });
  });
}
function repond(url) {
  return new Promise(ok => {
    const r = http.get(url, rep => { rep.resume(); ok(rep.statusCode < 500); });
    r.on('error', () => ok(false));
    r.setTimeout(2000, () => { r.destroy(); ok(false); });
  });
}
async function attendre(url, secondes) {
  for (let i = 0; i < secondes * 4; i++) {
    if (await repond(url)) return true;
    if (serveur && serveur.exitCode !== null) return false;
    await new Promise(r => setTimeout(r, 250));
  }
  return false;
}

// ── PDF : le bot écrit le HTML, l'application l'imprime en PDF ─────────────
async function imprimerPdf(fichierHtml, fichierPdf) {
  const w = new BrowserWindow({ show: false, webPreferences: { javascript: false, sandbox: true } });
  try {
    await w.loadFile(fichierHtml);
    const pdf = await w.webContents.printToPDF({ preferCSSPageSize: true, printBackground: true });
    fs.writeFileSync(fichierPdf, pdf);
  } finally {
    w.destroy();
  }
}
function lancerServeurPdf(jeton, dossier) {
  return new Promise((ok, ko) => {
    const s = http.createServer((req, rep) => {
      let corps = '';
      req.on('data', d => { corps += d; if (corps.length > 10000) req.destroy(); });
      req.on('end', async () => {
        try {
          if (req.method !== 'POST' || req.headers['x-jeton'] !== jeton) { rep.writeHead(403).end(); return; }
          const { html, pdf } = JSON.parse(corps);
          // On n'imprime que des fichiers du dossier de données.
          const dedans = f => path.resolve(f).startsWith(path.resolve(dossier) + path.sep);
          if (!dedans(html) || !dedans(pdf) || !html.endsWith('.html') || !pdf.endsWith('.pdf')) { rep.writeHead(400).end(); return; }
          await imprimerPdf(html, pdf);
          rep.writeHead(200).end('ok');
        } catch (err) {
          rep.writeHead(500).end(String(err));
        }
      });
    });
    s.on('error', ko);
    s.listen(0, '127.0.0.1', () => ok(s));
  });
}

// ── Démarrage du bot ───────────────────────────────────────────────────────
function commandeServeur() {
  if (app.isPackaged) {
    const exe = process.platform === 'win32' ? 'jobbot-serveur.exe' : 'jobbot-serveur';
    return { cmd: path.join(process.resourcesPath, 'serveur', exe), args: [], cwd: process.resourcesPath };
  }
  const bot = path.join(__dirname, '..');
  const venv = path.join(bot, '.venv', 'bin', 'python');
  return { cmd: fs.existsSync(venv) ? venv : 'python3', args: ['-m', 'jobbot.app_serveur'], cwd: bot };
}
async function demarrer() {
  const dossier = dossierDonnees();
  preparerDonnees(dossier);
  const port = await portLibre();
  const jeton = crypto.randomBytes(18).toString('base64url');
  const jetonPdf = crypto.randomBytes(18).toString('base64url');
  const pdf = await lancerServeurPdf(jetonPdf, dossier);
  crochetPdf = { url: `http://127.0.0.1:${pdf.address().port}/`, jeton: jetonPdf };
  const { cmd, args, cwd } = commandeServeur();
  serveur = spawn(cmd, args, {
    cwd,
    env: { ...process.env, JOBBOT_HOME: dossier, JOBBOT_PORT: String(port), JOBBOT_JETON: jeton,
           JOBBOT_PDF_URL: crochetPdf.url, JOBBOT_PDF_JETON: jetonPdf, PYTHONUNBUFFERED: '1' },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  const noter = d => { journal = journal.concat(String(d).split('\n').filter(Boolean)).slice(-30); };
  serveur.stdout.on('data', noter);
  serveur.stderr.on('data', noter);
  serveur.on('error', err => noter(`Lancement impossible : ${err.message}`));
  adresse = `http://127.0.0.1:${port}`;
  if (!(await attendre(`${adresse}/static/app.css`, 60))) {
    throw new Error('Le bot ne répond pas.\n\n' + journal.slice(-12).join('\n'));
  }
  return `${adresse}/?t=${jeton}`;
}
function arreter() {
  if (serveur && serveur.exitCode === null) serveur.kill();
  serveur = null;
}

// ── Fenêtre et menu ────────────────────────────────────────────────────────
function creerFenetre() {
  fenetre = new BrowserWindow({
    width: 1360, height: 900, minWidth: 380, minHeight: 600, title: 'JobBot', show: !ESSAI,
    backgroundColor: '#f6f7f9',
    icon: path.join(__dirname, 'icone.png'),
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true },
  });
  fenetre.loadFile(path.join(__dirname, 'attente.html'));
  // Les liens vers l'extérieur (annonce, portfolio, email) s'ouvrent dans le navigateur ou le logiciel de courrier.
  const externe = url => !url.startsWith(adresse) && !url.startsWith('file:');
  fenetre.webContents.setWindowOpenHandler(({ url }) => {
    if (externe(url)) { shell.openExternal(url); return { action: 'deny' }; }
    return { action: 'allow' };
  });
  fenetre.webContents.on('will-navigate', (e, url) => {
    if (adresse && externe(url)) { e.preventDefault(); shell.openExternal(url); }
  });
  fenetre.on('closed', () => { fenetre = null; });
}
async function choisirDossier() {
  const r = await dialog.showOpenDialog(fenetre, {
    title: 'Dossier de données de JobBot',
    message: 'Choisis le dossier qui contient (ou contiendra) cv.yaml et tes candidatures.',
    properties: ['openDirectory', 'createDirectory'],
  });
  if (r.canceled || !r.filePaths[0]) return;
  ecrireReglages({ ...lireReglages(), dossier: r.filePaths[0] });
  app.relaunch();
  app.quit();
}
function creerMenu() {
  const dossier = dossierDonnees;
  const ouvrir = nom => () => shell.openPath(path.join(dossier(), nom));
  const menu = [
    ...(process.platform === 'darwin' ? [{ role: 'appMenu' }] : []),
    { label: 'Fichier', submenu: [
      { label: 'Ouvrir le dossier des candidatures', click: () => { fs.mkdirSync(path.join(dossier(), 'candidatures'), { recursive: true }); ouvrir('candidatures')(); } },
      { label: 'Ouvrir le dossier de données', click: () => shell.openPath(dossier()) },
      { type: 'separator' },
      { label: 'Modifier mon CV (cv.yaml)', click: ouvrir('cv.yaml') },
      { label: 'Modifier mon CV en anglais (cv_en.yaml)', click: ouvrir('cv_en.yaml') },
      { label: 'Modifier les réglages (config.yaml)', click: ouvrir('config.yaml') },
      { type: 'separator' },
      { label: 'Changer de dossier de données…', click: choisirDossier },
      ...(process.platform === 'darwin' ? [] : [{ type: 'separator' }, { role: 'quit', label: 'Quitter' }]),
    ] },
    { role: 'editMenu', label: 'Édition' },
    { label: 'Affichage', submenu: [
      { role: 'reload', label: 'Recharger' }, { type: 'separator' },
      { role: 'resetZoom', label: 'Taille réelle' }, { role: 'zoomIn', label: 'Agrandir' }, { role: 'zoomOut', label: 'Réduire' },
      { type: 'separator' }, { role: 'togglefullscreen', label: 'Plein écran' },
    ] },
    { role: 'windowMenu', label: 'Fenêtre' },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(menu));
}

// ── Essai automatique (utilisé par la fabrication de l'application) ────────
async function essai(url) {
  const fin = (code, message) => { console.log(message); arreter(); app.exit(code); };
  try {
    await fenetre.loadURL(url);
    const titre = await fenetre.webContents.executeJavaScript('document.title');
    if (!/JobBot/.test(titre)) return fin(1, `ESSAI ÉCHOUÉ : titre inattendu « ${titre} »`);
    // PDF : on imprime une page de test dans le dossier de données.
    const dossier = dossierDonnees();
    const html = path.join(dossier, 'essai.html'), pdf = path.join(dossier, 'essai.pdf');
    fs.writeFileSync(html, '<!doctype html><meta charset="utf-8"><h1>Essai JobBot</h1><p>éàç</p>');
    // Même chemin que le bot : une demande au crochet PDF, avec puis sans le bon jeton.
    const demander = jeton => fetch(crochetPdf.url, { method: 'POST', headers: { 'X-Jeton': jeton }, body: JSON.stringify({ html, pdf }) });
    if ((await demander('faux')).status !== 403) return fin(1, 'ESSAI ÉCHOUÉ : le crochet PDF accepte un mauvais jeton');
    const rep = await demander(crochetPdf.jeton);
    if (!rep.ok) return fin(1, `ESSAI ÉCHOUÉ : crochet PDF ${rep.status} ${await rep.text()}`);
    const taille = fs.statSync(pdf).size;
    fs.rmSync(html); fs.rmSync(pdf);
    if (taille < 1000) return fin(1, 'ESSAI ÉCHOUÉ : PDF vide');
    if (process.env.JOBBOT_SMOKE_CAPTURE) fs.writeFileSync(process.env.JOBBOT_SMOKE_CAPTURE, (await fenetre.webContents.capturePage()).toPNG());
    return fin(0, `ESSAI RÉUSSI : interface « ${titre} », PDF de ${taille} octets, données dans ${dossier}`);
  } catch (err) {
    return fin(1, `ESSAI ÉCHOUÉ : ${err.message}`);
  }
}

// ── Cycle de vie ───────────────────────────────────────────────────────────
// Linux : fenêtre Wayland native quand la session en propose une (Hyprland, Omarchy…), sinon X11.
if (process.platform === 'linux') app.commandLine.appendSwitch('ozone-platform-hint', 'auto');
if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on('second-instance', () => { if (fenetre) { if (fenetre.isMinimized()) fenetre.restore(); fenetre.focus(); } });
  app.whenReady().then(async () => {
    creerMenu();
    creerFenetre();
    try {
      const url = await demarrer();
      if (ESSAI) return essai(url);
      await fenetre.loadURL(url);
    } catch (err) {
      if (ESSAI) { console.log(`ESSAI ÉCHOUÉ : ${err.message}`); arreter(); app.exit(1); return; }
      dialog.showErrorBox('JobBot ne démarre pas', err.message);
      app.quit();
    }
  });
  app.on('window-all-closed', () => app.quit());
  app.on('before-quit', arreter);
  process.on('exit', arreter);
}
