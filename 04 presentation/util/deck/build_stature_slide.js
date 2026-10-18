// Appendix slide "Who already runs on Metronome" (15-16 Oct 2026): body only.
// Builds the customer logo row, the stats, the scale statement and the source line, to paste into a duplicate of a live
// appendix slide so the slide keeps the deck's eyebrow, footer and page number. The eyebrow is typed in Slides.
//   node build_stature_slide.js && python3 repack.py stature_slide_raw.pptx stature-slide-body.pptx
//   ->  stature-slide-body.pptx (one slide, body only, speaker notes included)
//   node build_stature_slide.js --logos-only && python3 repack.py stature_slide_raw.pptx stature-logo-row.pptx
//   ->  stature-logo-row.pptx (the logo row alone, as pasted on 16 Oct to replace the typed customer names)
// Logos: assets/customer-logos/*.png, rendered by render_customer_logos.js in metronome.com's logo grey (#565F5F) from
// metronome.com's own logo wall (OpenAI, Anthropic, NVIDIA, Confluent, Hugging Face) and databricks.com's header logo.
// Every figure is sourced (see the footnotes and the notes); the ~$1B price is press-reported, never disclosed by Stripe.
const pptxgen = require('pptxgenjs');
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fi = require('react-icons/fi');
const fs = require('fs');

// design tokens: same as build_deck.js (metronome.com)
const C = {
  ink: '0D171A', bg: 'FAFBF8', border: 'E5E7DD', muted: '565F5F', muted2: '6B726D',
  lime: 'C3EE8F', limeLight: 'DAF6AF', limePale: 'F1FFD0', deep: '125B49',
};
const FONT = 'Inter';

async function icon(name, color) {
  let svg = ReactDOMServer.renderToStaticMarkup(React.createElement(fi[name], { size: 128 }));
  svg = svg.replace(/currentColor/g, '#' + color);
  const buf = await sharp(Buffer.from(svg)).resize(128, 128).png().toBuffer();
  return 'image/png;base64,' + buf.toString('base64');
}

function text(slide, t, o) {
  slide.addText(t, Object.assign({ fontFace: FONT, color: C.ink, margin: 0, isTextBox: true, valign: 'top' }, o));
}

const stats = [
  ['< 1 hour', 'for OpenAI to change pricing in Metronome’s UI, with no engineering resources¹'],
  ['150M+', 'end users billed through Metronome, with billions in usage-based revenue processed²'],
  ['~$1B', 'Stripe’s acquisition of Metronome (reported), closed Jan 2026: the payments rail you already use for pay-as-you-go³'],
];

// customer logos, in the order of the original list; Hugging Face added on 16 Oct (on metronome.com's logo wall)
const logos = [
  ['openai', 'OpenAI'], ['anthropic', 'Anthropic'], ['nvidia', 'NVIDIA'],
  ['databricks', 'Databricks'], ['confluent', 'Confluent'], ['huggingface', 'Hugging Face'],
];
const logosOnly = process.argv.includes('--logos-only');

// one row across the title area: equal visual area per logo, justified between x 0.5 and 9.5, centred on y 0.85
async function logoRow(slide) {
  const AREA = 0.25; // square inches per logo
  const items = [];
  for (const [file, name] of logos) {
    const buf = fs.readFileSync(`assets/customer-logos/${file}.png`);
    const { width, height } = await sharp(buf).metadata();
    const ar = width / height;
    items.push({ name, data: 'image/png;base64,' + buf.toString('base64'), w: Math.sqrt(AREA * ar), h: Math.sqrt(AREA / ar) });
  }
  const gap = (9 - items.reduce((t, it) => t + it.w, 0)) / (items.length - 1);
  let x = 0.5;
  for (const it of items) {
    slide.addImage({ data: it.data, x, y: 0.85 - it.h / 2, w: it.w, h: it.h,
      altText: `${it.name} logo`, objectName: `Customer logo: ${it.name}` });
    x += it.w + gap;
  }
}

(async () => {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  pres.author = 'Rania Benman';
  pres.company = 'Metronome';
  pres.title = 'Appendix: who already runs on Metronome (body only)';
  pres.theme = { headFontFace: FONT, bodyFontFace: FONT };

  const s = pres.addSlide();
  s.background = { color: C.bg };

  await logoRow(s);
  if (logosOnly) {
    await pres.writeFile({ fileName: 'stature_slide_raw.pptx' });
    console.log('written stature_slide_raw.pptx (logo row only)');
    return;
  }

  // divider under the customer logos
  s.addShape('line', { x: 0.5, y: 1.35, w: 9, h: 0, line: { color: C.border, width: 1 }, objectName: 'Stature divider' });

  stats.forEach(([big, lab], i) => {
    const x = 0.5 + i * 3.1;
    text(s, big, { x, y: 1.65, w: 2.8, h: 0.66, fontSize: 36, bold: true, color: C.deep, objectName: `Stature stat ${i + 1}` });
    text(s, lab, { x, y: 2.36, w: 2.8, h: 0.62, fontSize: 10, color: C.muted, objectName: `Stature stat ${i + 1} label` });
    if (i > 0) s.addShape('line', { x: x - 0.2, y: 1.72, w: 0, h: 1.2, line: { color: C.border, width: 1 },
      objectName: `Stature column rule ${i}` });
  });

  // scale statement
  s.addShape('roundRect', { x: 0.5, y: 3.45, w: 9, h: 0.78, rectRadius: 0.08,
    fill: { color: C.limePale }, line: { color: C.limeLight, width: 0.75 }, objectName: 'Stature scale card' });
  s.addShape('ellipse', { x: 0.75, y: 3.63, w: 0.42, h: 0.42, fill: { color: C.lime }, line: { color: C.lime },
    objectName: 'Stature scale bubble' });
  s.addImage({ data: await icon('FiActivity', C.ink), x: 0.855, y: 3.735, w: 0.21, h: 0.21, objectName: 'Stature scale icon' });
  text(s, [
    { text: 'Billions of usage events a day. ', options: { bold: true } },
    { text: 'Up to 110,000 events per second at ingest, with no pre-aggregation.⁴' },
  ], { x: 1.4, y: 3.45, w: 7.9, h: 0.78, fontSize: 13, valign: 'middle', objectName: 'Stature scale text' });

  // footnotes: each source is a link (added on the live slide on 16 Oct 2026)
  const link = (t, url) => ({ text: t, options: { hyperlink: { url } } });
  text(s, [
    { text: '¹ ' },
    link('Metronome customer story: OpenAI', 'https://metronome.com/customer-stories/open-ai'),
    { text: '   ² ' },
    link('Metronome Series C release (Feb 2025)', 'https://www.businesswire.com/news/home/20250225320307/en/Metronome-Secures-%2450-Million-in-Series-C-Funding-to-Drive-Adoption-of-Usage-Based-Pricing-in-Software-and-AI'),
    { text: '   ³ ' },
    link('Upstarts Media (Dec 2025)', 'https://www.upstartsmedia.com/p/scoop-stripe-pays-1-billion-for-metronome'),
    { text: '; ' },
    link('Stripe newsroom (Jan 2026)', 'https://stripe.com/newsroom/news/stripe-completes-metronome-acquisition'),
    { text: '   ⁴ ' },
    link('Metronome docs, “Usage events at scale”', 'https://docs.metronome.com/guides/events/high-volume-ingestion'),
  ], { x: 0.5, y: 4.85, w: 9, h: 0.18, fontSize: 7, color: C.muted2, objectName: 'Stature sources' });

  s.addNotes([
    'PURPOSE: Backup for credibility questions ("Who else runs on you?", "Will you be around?", "Can you take our volume?"). It shows that Metronome bills the AI leaders, is now part of Stripe, and runs at a scale far above one platform\'s needs.',
    'EMPHASIZE: The OpenAI proof point mirrors their first blocker: OpenAI changes pricing in under an hour with no engineers, where Replicate needs two teams and weeks per machine type. Stripe is the same rail they already use for pay-as-you-go.',
    'TONE: Factual and brief. Let the names speak; no overselling.',
    'TIMING: 30 seconds, only if asked.',
    'IF ASKED: Customer names: Metronome Series C release (25 Feb 2025) names OpenAI, Anthropic, Databricks, Confluent and NVIDIA, and 150M+ end users; Patrick Collison also named OpenAI, Anthropic and NVIDIA when Stripe announced the deal. "< 1 hour": quote from OpenAI\'s Senior Manager of Revenue Operations in the OpenAI customer story on metronome.com. Stripe completed the acquisition on 14 Jan 2026 (Stripe newsroom). The $1B price is press-reported (Upstarts Media, 3 Dec 2025, eight sources); Stripe disclosed no terms, so always say "reported". Scale: docs "Usage events at scale" (up to 110,000 events per second, 5,000 by default and raised on request, billions of events per day). Inference platforms on metronome.com\'s logo wall (Oct 2026) include Hugging Face, Together AI and Anyscale.',
  ].join('\n\n'));

  await pres.writeFile({ fileName: 'stature_slide_raw.pptx' });
  console.log('written stature_slide_raw.pptx');
})();
