const sharp = require('sharp');
const fs = require('fs');
const dl = process.argv[2];
(async () => {
  const nav = fs.readFileSync(`${dl}/metronome_nav_logo.svg`, 'utf8');
  const navWhite = nav.replace(/#0D171A/gi, '#FAFBF8').replace(/#565F5F/gi, '#B7C4BF');
  await sharp(Buffer.from(navWhite), { density: 1200 }).png().toFile('assets/metronome_logo_white.png');
  // Website-style hero panel: soft lime -> green gradient with faint grid lines
  const W = 1500, H = 1900;
  let lines = '';
  for (let x = 150; x < W; x += 150) lines += `<line x1="${x}" y1="0" x2="${x}" y2="${H}" stroke="#FFFFFF" stroke-opacity="0.16" stroke-width="2"/>`;
  for (let y = 150; y < H; y += 150) lines += `<line x1="0" y1="${y}" x2="${W}" y2="${y}" stroke="#FFFFFF" stroke-opacity="0.10" stroke-width="2"/>`;
  let hatch = '';
  for (let i = -H; i < W; i += 28) hatch += `<line x1="${i}" y1="${H}" x2="${i + 300}" y2="${H - 300}" stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="2"/>`;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
    <defs>
      <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#DAF6AF"/><stop offset="0.45" stop-color="#9BDD72"/><stop offset="1" stop-color="#3FB46A"/>
      </linearGradient>
      <radialGradient id="r" cx="0.3" cy="0.25" r="0.7">
        <stop offset="0" stop-color="#F1FFD0" stop-opacity="0.65"/><stop offset="1" stop-color="#F1FFD0" stop-opacity="0"/>
      </radialGradient>
      <clipPath id="c"><rect x="${W - 300}" y="${H - 300}" width="300" height="300"/></clipPath>
    </defs>
    <rect width="${W}" height="${H}" fill="url(#g)"/>
    <rect width="${W}" height="${H}" fill="url(#r)"/>
    ${lines}
    <g clip-path="url(#c)">${hatch}</g>
  </svg>`;
  await sharp(Buffer.from(svg)).png().toFile('assets/hero_gradient.png');
  for (const f of fs.readdirSync('assets')) { const m = await sharp('assets/' + f).metadata(); console.log(f, m.width + 'x' + m.height, fs.statSync('assets/' + f).size); }
})();
