// Recolour customer logo SVGs to one grey and rasterise them to transparent PNGs (300 px tall).
// usage: node render_customer_logos.js <outdir> <name>=<file.svg> ...
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const GREY = '#565F5F'; // metronome.com logo-wall grey (= deck token C.muted)
const [outdir, ...pairs] = process.argv.slice(2);
fs.mkdirSync(outdir, { recursive: true });
(async () => {
  for (const pair of pairs) {
    const [name, file] = pair.split('=');
    let svg = fs.readFileSync(file, 'utf8');
    svg = svg.replace(/currentColor/g, GREY)
             .replace(/fill="#(000|000000|EE3D2C|ee3d2c)"/g, `fill="${GREY}"`)
             .replace(/stroke="#(000|000000)"/g, `stroke="${GREY}"`);
    const vb = svg.match(/viewBox="([\d.\s-]+)"/)[1].trim().split(/\s+/).map(Number);
    const density = Math.round(72 * 300 / vb[3]); // 300 px tall
    const out = path.join(outdir, `${name}.png`);
    const info = await sharp(Buffer.from(svg), { density }).png().toFile(out);
    console.log(name, `${info.width}x${info.height}`, 'aspect', (info.width / info.height).toFixed(3));
  }
})();
