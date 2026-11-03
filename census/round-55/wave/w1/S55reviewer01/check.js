// Classifies each correction / pair-annotation line in each attack fixture tip as
// PROSE (visible text), CODE (inside a rendered code block), or COMMENT (raw HTML
// block), using commonmark.js 0.31.2 (CommonMark spec 0.31.2) as reference.
const commonmark = require('commonmark');
const fs = require('fs');
const path = require('path');

const WORK = process.argv[2];
const reader = new commonmark.Parser();
const writer = new commonmark.HtmlRenderer();
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function classify(html, t) {
  const e = esc(t);
  const rawIdx = html.indexOf(t);
  const escIdx = html.indexOf(e);
  let pos;
  if (rawIdx >= 0 && (escIdx < 0 || rawIdx < escIdx)) pos = rawIdx;
  else pos = escIdx;
  if (pos < 0) return 'ABSENT';
  const lastOpen = html.lastIndexOf('<!--', pos);
  const lastClose = html.lastIndexOf('-->', pos);
  if (lastOpen >= 0 && lastOpen > lastClose) return 'COMMENT';
  const pOpen = html.lastIndexOf('<pre><code', pos);
  const pClose = html.lastIndexOf('</code></pre>', pos);
  if (pOpen >= 0 && pOpen > pClose) return 'CODE';
  return 'PROSE';
}

for (const sid of fs.readdirSync(WORK).sort()) {
  const d = path.join(WORK, sid);
  if (!fs.statSync(d).isDirectory()) continue;
  for (const f of ['SCORECARD.md', 'LOG.md', 'census/round-51/preregistration.txt']) {
    const p = path.join(d, f);
    if (!fs.existsSync(p)) continue;
    const text = fs.readFileSync(p, 'utf8');
    const html = writer.render(reader.parse(text));
    text.split('\n').forEach((ln, i) => {
      if (!/CORRECTION|SOURCES\.md/.test(ln)) return;
      let t = ln.replace(/\r$/, '').replace(/^ +/, '');
      console.log([sid, f, i + 1, classify(html, t), JSON.stringify(t.slice(0, 70))].join('\t'));
    });
  }
}
