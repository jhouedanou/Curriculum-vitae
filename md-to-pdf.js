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
          body { font-family: 'Noto Color Emoji', 'Segoe UI Emoji', 'Apple Color Emoji', Arial, sans-serif; margin: 40px; }
          pre, code { background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
        </style>
      </head>
      <body>
        <div id="md"></div>
        <script id="md-src" type="text/plain">${markdown.replace(/<\//g, '<\/')}</script>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script>
          const markdown = document.getElementById('md-src').textContent;
          document.getElementById('md').innerHTML = marked.parse(markdown);
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
