import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
const fail = [];
const mustExist = ['index.html', 'app.js', 'style.css', 'diagnostics.js', 'assneo'];
for (const path of mustExist) if (!existsSync(path)) fail.push('Missing required path: ' + path);
if (existsSync('index.html')) {
  const html = readFileSync('index.html', 'utf8');
  for (const ref of ['./style.css', './diagnostics.js', './app.js']) {
    if (!html.includes(ref)) fail.push('index.html does not reference ' + ref);
  }
  if (!html.includes('id="board"')) fail.push('index.html is missing #board');
}
if (existsSync('app.js')) {
  const js = readFileSync('app.js', 'utf8');
  for (const id of ['board', 'flip', 'new', 'undo', 'resign', 'clock', 'moves']) {
    if (!js.includes("'" + id + "'") && !js.includes('"'+id+'"')) fail.push('app.js may be missing required UI binding: ' + id);
  }
  const assets = [...js.matchAll(/'([wb][kqrbnp]\.png)'/g)].map(m => m[1]);
  if (!assets.length) fail.push('No chess-piece PNG filenames detected in app.js');
  for (const asset of new Set(assets)) if (!existsSync(join('assneo', asset))) fail.push('Missing chess asset: assneo/' + asset);
}
if (existsSync('assneo')) {
  const pngs = readdirSync('assneo').filter(x => x.toLowerCase().endsWith('.png'));
  if (pngs.length < 12) fail.push('Expected at least 12 PNG piece assets in assneo/, found ' + pngs.length);
}
if (fail.length) {
  console.error('COVUA PRE-DEPLOY CHECK FAILED');
  fail.forEach((e, i) => console.error((i + 1) + '. ' + e));
  process.exit(1);
}
console.log('COVUA PRE-DEPLOY CHECK PASSED');
console.log('- Required app files present');
console.log('- HTML references verified');
console.log('- Chess UI bindings and assneo PNG assets checked');
