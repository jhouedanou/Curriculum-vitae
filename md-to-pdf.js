const fs = require('fs');
const puppeteer = require('puppeteer');

(async () => {
  const markdown = fs.readFileSync('README.md', 'utf-8');
  const html = `
    <html>
      <head>
        <meta charset="utf-8">
        <title>README</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; }
          pre, code { background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
        </style>
      </head>
      <body>
        <pre id="md"></pre>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script>
          document.getElementById('md').outerHTML = marked.parse(`"""${markdown.replace(/`/g, '\`')}"""`);
        </script>
      </body>
    </html>
  `;

  const browser = await puppeteer.launch({args: ['--no-sandbox', '--disable-setuid-sandbox']});
  const page = await browser.newPage();
  await page.setContent(html, {waitUntil: 'networkidle0'});
  await page.pdf({path: 'README.pdf', format: 'A4', printBackground: true, margin: {top: 40, bottom: 40, left: 40, right: 40}});
  await browser.close();
})();
