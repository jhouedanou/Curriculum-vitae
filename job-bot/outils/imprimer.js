// Imprime des pages HTML en PDF avec Chromium (Playwright).
// usage : node imprimer.js <source.html> <sortie.pdf> [<source> <sortie> ...]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const a = process.argv.slice(2);
  const b = await chromium.launch();
  for (let i = 0; i < a.length; i += 2) {
    const p = await b.newPage();
    // setContent : un fichier .doc (HTML pour Word) serait téléchargé au lieu d'être affiché
    await p.setContent(fs.readFileSync(path.resolve(a[i]), 'utf8'), { waitUntil: 'load' });
    await p.pdf({ path: a[i + 1], format: 'A4', preferCSSPageSize: true, printBackground: true });
    await p.close();
  }
  await b.close();
})();
