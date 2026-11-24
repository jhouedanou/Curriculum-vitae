/**
 * Fabrique ce que l'application embarque :
 *   construit/jobbot-serveur/  le bot et Python, en un programme autonome (PyInstaller)
 *   construit/modele/          cv.yaml, réglages, gabarits et photo, copiés au premier lancement
 *
 * usage : node construire-serveur.js     (Python 3.10+ avec requirements.txt et pyinstaller installés)
 */
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ICI = __dirname;
const BOT = path.join(ICI, '..');
const SORTIE = path.join(ICI, 'construit');
const PYTHON = process.env.PYTHON || 'python3';
const SEP = process.platform === 'win32' ? ';' : ':';

fs.rmSync(SORTIE, { recursive: true, force: true });
fs.mkdirSync(SORTIE, { recursive: true });

const donnees = [
  [path.join(BOT, 'jobbot', 'web', 'templates'), 'jobbot/web/templates'],
  [path.join(BOT, 'jobbot', 'web', 'static'), 'jobbot/web/static'],
];
const args = [
  '-m', 'PyInstaller', path.join(ICI, 'serveur_entree.py'),
  '--name', 'jobbot-serveur', '--onedir', '--noconfirm', '--clean', '--log-level', 'WARN',
  '--paths', BOT,
  '--distpath', SORTIE, '--workpath', path.join(SORTIE, '_travail'), '--specpath', path.join(SORTIE, '_travail'),
  ...donnees.flatMap(([de, vers]) => ['--add-data', `${de}${SEP}${vers}`]),
  // Bibliothèques chargées à l'exécution, que PyInstaller ne devine pas seul.
  '--collect-submodules', 'jobbot',
  '--collect-submodules', 'uvicorn',
  '--collect-submodules', 'markdown',
  '--collect-data', 'trafilatura', '--collect-data', 'justext', '--collect-data', 'courlan',
  '--collect-data', 'htmldate', '--collect-data', 'dateparser',
  '--hidden-import', 'multipart', '--hidden-import', 'python_multipart',
  // L'application crée les PDF elle-même, et ne parle à aucune API.
  '--exclude-module', 'weasyprint', '--exclude-module', 'anthropic', '--exclude-module', 'pytest',
];
console.log('PyInstaller…');
execFileSync(PYTHON, args, { cwd: ICI, stdio: 'inherit' });
fs.rmSync(path.join(SORTIE, '_travail'), { recursive: true, force: true });

const modele = path.join(SORTIE, 'modele');
fs.mkdirSync(modele, { recursive: true });
for (const nom of ['cv.yaml', 'cv_en.yaml', 'config.yaml', 'photo.jpg', 'templates']) {
  fs.cpSync(path.join(BOT, nom), path.join(modele, nom), { recursive: true });
}
console.log('Prêt :', SORTIE);
