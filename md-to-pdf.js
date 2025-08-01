const fs = require('fs');
const puppeteer = require('puppeteer');

(async () => {
  const markdown = fs.readFileSync('cv_HOUEDANOU.md', 'utf-8');
  const html = `
    <html>
      <head>
        <meta charset="utf-8">
        <title>CV Jean Luc Houédanou</title>
        <style>
          /* Add your custom CSS here */
          body {
              font-family: 'Noto Color Emoji', 'Segoe UI Emoji', 'Apple Color Emoji', Barlow, sans-serif;
              line-height: 1.4;
              padding: 20px;
              margin: 0;
              font-size: 1em;
          }
          * {
              font-size: 12px;
          }
          pre {
              background: #2d2d2d;
              border-radius: 4px;
              margin: 0.5em 0;
          }
          code {
              font-family: 'Fira Code', Consolas, Monaco, monospace;
          }
          :not(pre) > code {
              background: #f0f0f0;
              padding: 2px 4px;
              border-radius: 3px;
              color: #e83e8c;
          }
          img { max-width: 100%; }
          table {
              border-collapse: collapse;
              width: 100%;
              margin: 1em 0;
          }
          th, td {
              border: 1px solid #ddd;
              padding: 8px;
              font-size: .8em;
          }
          th { background-color: #f4f4f4; }
          blockquote {
              border-left: 4px solid #ddd;
              padding-left: 1em;
              margin-left: 0;
              color: #666;
          }
          h1 {
              font-size: 1.6em;
              color: #000;
              font-weight: 700;
              border-bottom: 2px solid #eee;
              padding-bottom: 0.5rem;
              margin: 1.5rem 0;
          }
          h2 {
              color: #34495e;
              font-weight: 700;
              font-size: 1.4em;
              margin: 1.5rem 0;
          }
          h3 {
              color: #455a64;
              font-weight: 700;
              font-size: 1.2em;
          }
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
  await page.pdf({path: 'cv_HOUEDANOU.pdf', format: 'A4', printBackground: true, margin: {top: 40, bottom: 40, left: 40, right: 40}});
  await browser.close();
})();
