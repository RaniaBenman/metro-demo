// Replicate x Metronome: pre-demo deck (10 min) + demo divider + next steps + appendix.
// Built with pptxgenjs, then uploaded to Google Drive (converted to Google Slides).
const pptxgen = require('pptxgenjs');
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fi = require('react-icons/fi');
const fs = require('fs');

// ---------------------------------------------------------------- design tokens (metronome.com)
const C = {
  ink: '0D171A', bg: 'FAFBF8', surface: 'F1F2ED', card: 'FFFFFF', border: 'E5E7DD',
  muted: '565F5F', muted2: '6B726D', lime: 'C3EE8F', limeLight: 'DAF6AF', limePale: 'F1FFD0',
  green: '2EAC67', deep: '125B49', dark: '002F2C', dark2: '003834', white: 'FFFFFF',
  onDark: 'EEF3EF', onDarkMuted: 'A9BDB6',
};
const FONT = 'Inter';
const W = 10, H = 5.625;

const asset = (f) => 'image/png;base64,' + fs.readFileSync('assets/' + f).toString('base64');
const assetJpg = (f) => 'image/jpeg;base64,' + fs.readFileSync('assets/' + f).toString('base64');

async function icon(name, color) {
  let svg = ReactDOMServer.renderToStaticMarkup(React.createElement(fi[name], { size: 128 }));
  svg = svg.replace(/currentColor/g, '#' + color);
  const buf = await sharp(Buffer.from(svg)).resize(128, 128).png().toBuffer();
  return 'image/png;base64,' + buf.toString('base64');
}

// fresh option objects every time (pptxgenjs mutates them)
const shadow = () => ({ type: 'outer', color: '0D171A', opacity: 0.08, blur: 6, offset: 1.5, angle: 90 });

function card(slide, x, y, w, h, opts = {}) {
  slide.addShape('roundRect', {
    x, y, w, h, rectRadius: opts.radius ?? 0.08,
    fill: { color: opts.fill ?? C.card },
    line: { color: opts.line ?? C.border, width: opts.lineWidth ?? 0.75 },
    shadow: opts.shadow === false ? undefined : shadow(),
    objectName: opts.name,
  });
}

async function iconBubble(slide, name, x, y, d = 0.42, bubble = C.lime, color = C.ink) {
  slide.addShape('ellipse', { x, y, w: d, h: d, fill: { color: bubble }, line: { color: bubble } });
  const pad = d * 0.25;
  slide.addImage({ data: await icon(name, color), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad });
}

function text(slide, t, o) {
  slide.addText(t, Object.assign({ fontFace: FONT, color: C.ink, margin: 0, isTextBox: true, valign: 'top' }, o));
}

function eyebrow(slide, t, dark = false) {
  text(slide, t, { x: 0.5, y: 0.3, w: 9, h: 0.22, fontSize: 9, bold: true, charSpacing: 1.5,
    color: dark ? C.lime : C.muted2 });
}

function notes(slide, n) {
  slide.addNotes([
    `PURPOSE: ${n.purpose}`,
    `EMPHASIZE: ${n.emphasize}`,
    `TONE: ${n.tone}`,
    n.timing ? `TIMING: ${n.timing}` : null,
    n.talk ? `TALK TRACK: ${n.talk}` : null,
    n.ask ? `ASK THEM: ${n.ask}` : null,
    n.ifAsked ? `IF ASKED: ${n.ifAsked}` : null,
  ].filter(Boolean).join('\n\n'));
}

(async () => {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  pres.author = 'Rania Benman';
  pres.company = 'Metronome';
  pres.title = 'Replicate x Metronome: real-time billing for real-time inference';
  pres.theme = { headFontFace: FONT, bodyFontFace: FONT };

  // ------------------------------------------------------------ layouts
  pres.defineSlideMaster({
    title: 'CONTENT',
    background: { color: C.bg },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.52, w: 9, h: 0.6,
        fontFace: FONT, fontSize: 24, color: C.ink, valign: 'top', align: 'left', margin: 0 }, text: '' } },
      { image: { x: 0.5, y: 5.29, w: 1.3, h: 0.1077, data: asset('metronome_logo_ink_s.png') } },
      { text: { text: 'Replicate × Metronome  ·  October 2026', options: { x: 3, y: 5.24, w: 4, h: 0.2,
        fontFace: FONT, fontSize: 7.5, color: C.muted2, align: 'center', margin: 0 } } },
    ],
    slideNumber: { x: 9.1, y: 5.24, w: 0.4, h: 0.2, fontFace: FONT, fontSize: 7.5, color: C.muted2, align: 'right' },
  });
  pres.defineSlideMaster({
    title: 'DARK',
    background: { color: C.dark },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.55, y: 1.8, w: 4.9, h: 1.8,
        fontFace: FONT, fontSize: 32, color: C.white, valign: 'top', align: 'left', margin: 0 }, text: '' } },
    ],
  });
  // statement slide: stats on the left, the headline (title placeholder) on the right
  pres.defineSlideMaster({
    title: 'STATEMENT',
    background: { color: C.bg },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 4.9, y: 1.0, w: 4.6, h: 1.95,
        fontFace: FONT, fontSize: 28, color: C.ink, valign: 'top', align: 'left', margin: 0 }, text: '' } },
      { image: { x: 0.5, y: 5.29, w: 1.3, h: 0.1077, data: asset('metronome_logo_ink_s.png') } },
      { text: { text: 'Replicate × Metronome  ·  October 2026', options: { x: 3, y: 5.24, w: 4, h: 0.2,
        fontFace: FONT, fontSize: 7.5, color: C.muted2, align: 'center', margin: 0 } } },
    ],
    slideNumber: { x: 9.1, y: 5.24, w: 0.4, h: 0.2, fontFace: FONT, fontSize: 7.5, color: C.muted2, align: 'right' },
  });

  // ============================================================ 1. TITLE
  pres.addSection({ title: 'Opening' });
  let s = pres.addSlide({ masterName: 'DARK', sectionTitle: 'Opening' });
  s.addImage({ data: asset('metronome_logo_white_s.png'), x: 0.55, y: 0.5, w: 2.9, h: 0.24 });
  text(s, 'REPLICATE × METRONOME', { x: 0.55, y: 1.42, w: 4.9, h: 0.25, fontSize: 10, bold: true, charSpacing: 2, color: C.lime });
  s.addText('Your models run in real time. Your billing should too.', { placeholder: 'title' });
  text(s, 'Discovery recap, architecture, and a live demo of Replicate’s pricing in Metronome',
    { x: 0.55, y: 3.62, w: 4.6, h: 0.6, fontSize: 13, color: C.onDarkMuted });
  text(s, 'Rania Benman  ·  Strategist, Metronome  ·  October 2026',
    { x: 0.55, y: 4.8, w: 4.9, h: 0.25, fontSize: 10, color: C.onDark });
  s.addImage({ data: assetJpg('hero_gradient.jpg'), x: 5.85, y: 0.45, w: 3.7, h: 4.69 });
  card(s, 6.15, 1.2, 3.1, 3.2, { radius: 0.1, line: C.border });
  s.addImage({ data: asset('replicate_glyph_ink_s.png'), x: 6.38, y: 1.43, w: 0.22, h: 0.22 });
  text(s, 'Replicate · live billing', { x: 6.7, y: 1.42, w: 1.9, h: 0.25, fontSize: 10.5, bold: true });
  s.addShape('roundRect', { x: 8.53, y: 1.45, w: 0.5, h: 0.2, rectRadius: 0.1, fill: { color: C.lime }, line: { color: C.lime } });
  text(s, 'LIVE', { x: 8.53, y: 1.45, w: 0.5, h: 0.2, fontSize: 7, bold: true, align: 'center', valign: 'middle', charSpacing: 1 });
  const rows = [
    ['Compute · Nvidia A100 (80GB)', '$5.04 / hour, metered per second'],
    ['New GPU · Nvidia L40S', 'Priced with one rate'],
    ['Trial credit · $10 for 30 days', 'Alert within ~5 minutes'],
    ['Commit · $100k over 3 years', 'Balance in the customer’s own UI'],
  ];
  rows.forEach(([k, v], i) => {
    const y = 1.88 + i * 0.6;
    s.addShape('ellipse', { x: 6.4, y: y + 0.07, w: 0.09, h: 0.09, fill: { color: C.green }, line: { color: C.green } });
    text(s, k, { x: 6.6, y, w: 2.5, h: 0.22, fontSize: 8.5, color: C.muted2 });
    text(s, v, { x: 6.6, y: y + 0.22, w: 2.55, h: 0.26, fontSize: 10.5, bold: true });
  });
  notes(s, {
    purpose: 'Open with the one-line thesis and set the frame: Replicate sells real-time inference, so its billing has to keep up in real time too.',
    emphasize: '"Real time". Their product answers in milliseconds, but credit is checked once a day, a new GPU takes two teams and weeks, and commit balances need an engineer. The card on the right previews the four answers you will show.',
    tone: 'Warm, confident, unhurried. A partner who has done the homework, not a vendor reading a script.',
    timing: '30 seconds.',
    talk: 'Thank you for the time. Metronome is now a Stripe product, and Stripe is already in your stack. In the next ten minutes I will play back what we heard, show where Metronome sits in your stack, and then spend 30 minutes in the product with your own price list loaded. Interrupt me anytime.',
  });

  // ============================================================ 2. AGENDA
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Opening' });
  eyebrow(s, 'WHY WE’RE HERE');
  s.addText('Our 40 minutes, and what success looks like', { placeholder: 'title' });
  const agenda = [
    ['1', 'What we heard', '3 min  ·  your priorities and blockers, in your words'],
    ['2', 'How Metronome fits your stack', '5 min  ·  the model, the architecture, what changes'],
    ['3', 'Live demo: your pricing in Metronome', '30 min  ·  catalog, trial, support tiers, commits, quote-to-cash'],
    ['4', 'Next steps', '2 min  ·  a 4-week path to a decision'],
  ];
  s.addShape('line', { x: 0.72, y: 1.85, w: 0, h: 2.55, line: { color: C.border, width: 1.5 } });
  agenda.forEach(([n, t, d], i) => {
    const y = 1.42 + i * 0.85;
    s.addShape('ellipse', { x: 0.5, y, w: 0.44, h: 0.44, fill: { color: i === 2 ? C.lime : C.card }, line: { color: i === 2 ? C.lime : C.border, width: 1 } });
    text(s, n, { x: 0.5, y, w: 0.44, h: 0.44, fontSize: 13, bold: true, align: 'center', valign: 'middle' });
    text(s, t, { x: 1.15, y: y - 0.02, w: 3.9, h: 0.28, fontSize: 14, bold: true });
    text(s, d, { x: 1.15, y: y + 0.27, w: 3.9, h: 0.25, fontSize: 10, color: C.muted });
  });
  card(s, 5.45, 1.38, 4.05, 3.6);
  text(s, 'You should leave able to answer', { x: 5.75, y: 1.6, w: 3.6, h: 0.3, fontSize: 13, bold: true });
  const qs = [
    'Can we launch a new GPU without an engineering project?',
    'Can we keep a card-free trial without giving away GPU time?',
    'Can we sell support tiers and show commit customers where they stand?',
    'Does it plug into Stripe, NetSuite and Salesforce?',
  ];
  for (let i = 0; i < qs.length; i++) {
    const y = 2.1 + i * 0.68;
    await iconBubble(s, 'FiCheck', 5.75, y, 0.34);
    text(s, qs[i], { x: 6.25, y: y - 0.02, w: 3.05, h: 0.5, fontSize: 11.5 });
  }
  notes(s, {
    purpose: 'Set the stage and the clock (meeting flow and time management are judged), and agree on what "good" looks like before showing anything.',
    emphasize: 'Thirty of the forty minutes are in the product. The four questions on the right are the scorecard for today, and they map one-to-one to the blockers they shared.',
    tone: 'Crisp and organized, but inviting. Pause after the agenda and ask the room.',
    timing: '45 seconds.',
    ask: '"Anything you need to see today that is not on this list?" and "Who owns pricing changes on your side today, product, finance or engineering?" (discovery: decision process and stakeholders).',
  });

  // ============================================================ 3. TWO ENGINES
  pres.addSection({ title: 'Discovery' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Discovery' });
  eyebrow(s, 'WHERE REPLICATE IS GOING');
  s.addText('Two growth engines run through one billing system', { placeholder: 'title' });
  card(s, 0.5, 1.32, 4.4, 2.3);
  await iconBubble(s, 'FiUsers', 0.72, 1.52, 0.4);
  text(s, 'Self-serve, at developer scale', { x: 1.25, y: 1.58, w: 3.5, h: 0.3, fontSize: 13, bold: true });
  [['2M+', 'developers signed up¹'], ['30k', 'paying customers¹'], ['50k+', 'models in the catalog²']].forEach(([big, lab], i) => {
    const x = 0.72 + i * 1.38;
    text(s, big, { x, y: 2.1, w: 1.3, h: 0.5, fontSize: 26, bold: true, color: C.deep });
    text(s, lab, { x, y: 2.62, w: 1.3, h: 0.4, fontSize: 9.5, color: C.muted });
  });
  text(s, 'A card-free trial is the front door of the funnel', { x: 0.72, y: 3.15, w: 4.0, h: 0.3, fontSize: 11, color: C.ink, italic: true });
  card(s, 5.1, 1.32, 4.4, 2.3);
  await iconBubble(s, 'FiBriefcase', 5.32, 1.52, 0.4);
  text(s, 'Enterprise, at commit scale', { x: 5.85, y: 1.58, w: 3.5, h: 0.3, fontSize: 13, bold: true });
  text(s, [
    { text: 'Multi-year commits for a discount (e.g. $100k over 3 years)', options: { bullet: true, breakLine: true } },
    { text: 'Volume discounts, priority support and performance SLAs³', options: { bullet: true, breakLine: true } },
    { text: 'Multi-GPU capacity sold with committed-spend contracts³', options: { bullet: true } },
  ], { x: 5.35, y: 2.08, w: 3.95, h: 1.4, fontSize: 11, paraSpaceAfter: 6, color: C.ink });
  const tiles = [
    ['FiCpu', 'Hardware roadmap', '7 machine types today. Next: H100, H200, L40S and multi-GPU (12+ SKUs)'],
    ['FiCloud', 'Now part of Cloudflare²', 'Replicate’s catalog is coming to Workers AI: more developers, bigger deals'],
    ['FiShield', 'Rivals went prepaid-only⁴', 'Together AI has no free trial; Fireworks moved every self-serve account to prepaid (Jul 2026)'],
  ];
  for (let i = 0; i < tiles.length; i++) {
    const [ic, t, d] = tiles[i];
    const x = 0.5 + i * 3.04;
    card(s, x, 3.82, 2.88, 1.12, { fill: C.limePale, line: C.limeLight, shadow: false });
    await iconBubble(s, ic, x + 0.18, 3.98, 0.34, C.lime);
    text(s, t, { x: x + 0.62, y: 3.99, w: 2.15, h: 0.28, fontSize: 11, bold: true });
    text(s, d, { x: x + 0.18, y: 4.38, w: 2.58, h: 0.55, fontSize: 9, color: C.ink });
  }
  text(s, '¹ Replicate Series B announcement (Dec 2023)   ² Cloudflare blog, “Replicate joins Cloudflare” (Nov 2025)   ³ replicate.com/pricing   ⁴ Together AI docs; Fireworks blog (Jun 2026)',
    { x: 0.5, y: 5.0, w: 9, h: 0.18, fontSize: 7, color: C.muted2 });
  notes(s, {
    purpose: 'Show we understand Replicate’s business before talking about our product: two growth engines (self-serve at massive scale, and enterprise commits) that both depend on billing.',
    emphasize: 'The roadmap tile: today’s price list has 7 machine types, and you are adding H100, H200, L40S and multi-GPU. Every one of those goes through billing. The competitor tile: Together AI and Fireworks went prepaid-only, so Replicate’s card-free trial is a differentiator worth protecting, not a liability to shut down.',
    tone: 'Curious and respectful. It is their business, so invite correction rather than lecture.',
    timing: '1 minute 15 seconds.',
    ask: '"Is this how you think about it?", "Roughly what share of revenue is enterprise vs self-serve?", "How many new machine types do you plan this year?", "What does the Cloudflare integration change for billing, if anything?"',
    ifAsked: 'Numbers come from public sources only: Replicate’s Series B statement (2M developers, 30k paying, Dec 2023), Cloudflare’s acquisition post (50,000+ models), replicate.com/pricing (enterprise terms), Together AI docs and the Fireworks blog. They are directional and we would replace them with yours.',
  });

  // ============================================================ 4. WHY WE ARE HERE
  s = pres.addSlide({ masterName: 'STATEMENT', sectionTitle: 'Discovery' });
  eyebrow(s, 'WHY WE ARE HERE');
  const why = [
    ['50k+', 'open-source and fine-tuned models behind one API²'],
    ['30,000', 'paying customers  ·  2M+ developers signed up¹'],
    ['$40M', 'Series B led by a16z, with NVentures (NVIDIA), Sequoia and Y Combinator (Dec 2023)¹'],
  ];
  why.forEach(([big, lab], i) => {
    const y = 0.95 + i * 1.38;
    text(s, big, { x: 0.5, y, w: 3.8, h: 0.62, fontSize: 36, bold: true, color: C.deep });
    text(s, lab, { x: 0.5, y: y + 0.66, w: 3.8, h: 0.42, fontSize: 10, color: C.muted });
    if (i < why.length - 1) s.addShape('line', { x: 0.5, y: y + 1.2, w: 3.3, h: 0, line: { color: C.border, width: 1 } });
  });
  s.addText([
    { text: 'Every model run is a ' },
    { text: 'billing event', options: { color: C.green } },
    { text: ': rated, credited, invoiced.' },
  ], { placeholder: 'title' });
  text(s, 'You rebuilt model deployment as one API call. The monetization layer underneath it (SKUs, trials, commits, invoices) is still homegrown.',
    { x: 4.9, y: 3.2, w: 4.55, h: 0.75, fontSize: 13, color: C.ink });
  text(s, 'That gap is what we are here to close today.',
    { x: 4.9, y: 4.1, w: 4.55, h: 0.35, fontSize: 13, bold: true, color: C.deep });
  text(s, '¹ Replicate Series B announcement (Dec 2023)   ² Cloudflare blog, “Replicate joins Cloudflare” (Nov 2025)',
    { x: 0.5, y: 5.0, w: 9, h: 0.18, fontSize: 7, color: C.muted2 });
  notes(s, {
    purpose: 'Say in one line why we are in the room: Replicate turned model deployment into a single API call, but the layer that turns each run into revenue (SKUs, trials, commits, invoices) is still homegrown. It opens the "what we heard" part of the agenda and frames what follows: Replicate’s growth engines, then the four blockers.',
    emphasize: 'The headline. Every model run is a billing event: it has to be rated at the right price, drawn from the right credit or commit, and invoiced. At 30,000 paying customers and 50,000+ models, a homegrown layer becomes the bottleneck. Land the last line, "That gap is what we are here to close today", then pause.',
    tone: 'Confident and concise, a little provocative but respectful. Slow down on the headline; let the numbers speak.',
    timing: '30 to 45 seconds.',
    talk: 'You made deploying a model one API call. Underneath, every run is a billing event: rated, credited, invoiced. And that part is still built in-house. That gap is what we are here to close today.',
    ifAsked: 'Sources: Cloudflare blog "Replicate joins Cloudflare" (Nov 2025) for 50,000+ open-source and fine-tuned models; Replicate’s Series B statement via Orrick (Dec 2023) for 30,000 paying customers, 2 million developers signed up and the $40M Series B led by a16z with NVentures (NVIDIA’s venture arm), Heavybit, Sequoia and Y Combinator. These are the latest public figures; invite them to share current ones.',
  });

  // ============================================================ 5. BLOCKERS
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Discovery' });
  eyebrow(s, 'WHAT WE HEARD');
  s.addText('Four blockers, in your own words', { placeholder: 'title' });
  const pains = [
    ['FiCpu', '“To add a machine type, we have to involve two engineering teams. It can take weeks.”',
      'every new GPU waits on billing: revenue starts late and engineers leave the roadmap.'],
    ['FiClock', '“Our systems measure credit usage once a day.”',
      'up to a day of free GPU time per trial user. An 8x A40 (Large) runs $20.88/hour: about $500 a day.'],
    ['FiLifeBuoy', '“We can’t model fixed or percent-based fees, so we have no support tiers.”',
      'revenue left on the table from customers who are asking to pay for more.'],
    ['FiEye', '“We can’t tell customers where they are on their commit without an engineer.”',
      'manual pulls, uneasy customers, and renewals or expansions spotted too late.'],
  ];
  for (let i = 0; i < pains.length; i++) {
    const [ic, q, cost] = pains[i];
    const x = i % 2 === 0 ? 0.5 : 5.1, y = i < 2 ? 1.32 : 2.88;
    card(s, x, y, 4.4, 1.42);
    await iconBubble(s, ic, x + 0.2, y + 0.2, 0.42);
    text(s, q, { x: x + 0.8, y: y + 0.17, w: 3.42, h: 0.62, fontSize: 11.5, italic: true });
    text(s, [{ text: 'Cost: ', options: { bold: true, color: C.deep } }, { text: cost, options: { color: C.ink } }],
      { x: x + 0.8, y: y + 0.82, w: 3.42, h: 0.52, fontSize: 9.5 });
  }
  card(s, 0.5, 4.45, 9, 0.58, { fill: C.surface, line: C.border, shadow: false });
  text(s, 'And keep your quote-to-cash:', { x: 0.72, y: 4.45, w: 2.6, h: 0.58, fontSize: 11, bold: true, valign: 'middle' });
  [['Stripe', 'self-serve invoices'], ['NetSuite', 'enterprise invoicing'], ['Salesforce', 'CRM']].forEach(([n, d], i) => {
    const x = 3.3 + i * 2.05;
    s.addShape('roundRect', { x, y: 4.58, w: 1.9, h: 0.32, rectRadius: 0.16, fill: { color: C.card }, line: { color: C.border } });
    text(s, [{ text: n + '  ', options: { bold: true } }, { text: d, options: { color: C.muted } }],
      { x, y: 4.58, w: 1.9, h: 0.32, fontSize: 9.5, align: 'center', valign: 'middle' });
  });
  notes(s, {
    purpose: 'Play back their pains in their own words to earn the right to present, and attach a business cost to each one. This covers "what pain points the product will solve for us".',
    emphasize: 'The cost lines, especially the trial: with a once-a-day check, one trial user on an 8x A40 (Large) can burn up to about $500 of GPU time before anyone notices ($20.88/hour × 24; illustrative worst case). Also stress that Stripe, NetSuite and Salesforce stay.',
    tone: 'Empathetic and precise. Slow down and let them correct or add.',
    timing: '1 minute 30 seconds.',
    ask: '"Which of these hurts most this quarter?", "How long did the last machine type take end to end?", "How often do trial accounts run past their credit, and is that cost or abuse?", "How many customers are on commits today?"',
    ifAsked: 'The $500 is arithmetic on your public price ($20.88/hour for 8x A40 Large, times 24 hours), not data we have about your users.',
  });

  // ============================================================ 5. HOW IT WORKS
  pres.addSection({ title: 'Solution' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Solution' });
  eyebrow(s, 'HOW METRONOME WORKS');
  s.addText('Send usage once. Everything else is configuration', { placeholder: 'title' });
  const flow = [
    ['FiActivity', 'Usage event', 'What your platform already logs:', 'hardware: gpu-a100-large\nseconds: 150'],
    ['FiFilter', 'Billable metric', 'Sum of seconds, grouped by hardware, model and kind', ''],
    ['FiTag', 'Product + rate card', 'One compute product, one rate per machine type', 'A100 80GB: $5.04 / hour'],
    ['FiFileText', 'Contract', 'Each customer’s terms on top of the list price', 'trial credit · Pro Support · $100k commit at 15% off'],
    ['FiBarChart2', 'Invoices · balances · alerts', 'Updated as usage lands', 'to Stripe, NetSuite, Salesforce'],
  ];
  for (let i = 0; i < flow.length; i++) {
    const [ic, t, d, ex] = flow[i];
    const x = 0.45 + i * 1.875;
    card(s, x, 1.35, 1.6, 2.15, i === 4 ? { fill: C.limePale, line: C.limeLight } : {});
    await iconBubble(s, ic, x + 0.15, 1.5, 0.36);
    text(s, t, { x: x + 0.15, y: 1.95, w: 1.35, h: 0.45, fontSize: 11, bold: true });
    text(s, d, { x: x + 0.15, y: 2.42, w: 1.33, h: 0.55, fontSize: 8.5, color: C.muted });
    if (ex) text(s, ex, { x: x + 0.15, y: 2.98, w: 1.35, h: 0.45, fontSize: 8, color: C.deep, bold: true, fontFace: 'Roboto Mono' });
    if (i < flow.length - 1) {
      s.addShape('chevron', { x: x + 1.665, y: 2.3, w: 0.15, h: 0.25, fill: { color: C.green }, line: { color: C.green } });
    }
  }
  text(s, [
    { text: 'Engineering instruments once. ', options: { bold: true } },
    { text: 'Product and finance change prices, launch SKUs and sign custom contracts in the rate card and contracts, with no code change.', options: {} },
  ], { x: 0.5, y: 3.68, w: 9, h: 0.45, fontSize: 12 });
  const proofs = [
    ['A Stripe product', 'Stripe completed the acquisition in January 2026'],
    ['OpenAI · Anthropic · NVIDIA', 'already run on Metronome’s metering engine'],
    ['110,000 events / second', 'without pre-aggregation (Metronome docs)'],
  ];
  proofs.forEach(([b, d], i) => {
    const x = 0.5 + i * 3.04;
    card(s, x, 4.25, 2.88, 0.78, { fill: C.surface, line: C.border, shadow: false });
    text(s, b, { x: x + 0.18, y: 4.33, w: 2.6, h: 0.3, fontSize: 12.5, bold: true, color: C.deep });
    text(s, d, { x: x + 0.18, y: 4.64, w: 2.6, h: 0.3, fontSize: 8.5, color: C.muted });
  });
  notes(s, {
    purpose: 'Give a simple mental model (event, metric, price, contract, invoice) so the demo is easy to follow. This is the "explain complex things simply" moment.',
    emphasize: 'The separation. Your engineers send what they already log once (hardware + seconds); everything commercial becomes configuration that product or finance owns. Metronome’s docs put it as "your business team configures how to bill for it, all without additional code changes". Then the credibility strip: part of Stripe, trusted by OpenAI, Anthropic and NVIDIA, built for event volumes far above yours.',
    tone: 'Teacherly and simple. Draw the line with your hand from left to right.',
    timing: '1 minute 15 seconds.',
    ifAsked: 'Prices on the rate card are your public list, stored per hour ($/hour = $/second × 3,600, exactly), while usage is metered per second. That is the docs’ GPU-hour pattern. Sources: "How Metronome works", "Usage events at scale" (110,000 events/second, 5,000/second default, raised on request), Stripe newsroom (acquisition completed 14 Jan 2026).',
  });

  // ============================================================ 6. ARCHITECTURE
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Solution' });
  eyebrow(s, 'WHERE METRONOME FITS');
  s.addText('Between your platform and your quote-to-cash', { placeholder: 'title' });
  // left: Replicate
  s.addImage({ data: asset('replicate_glyph_ink_s.png'), x: 0.5, y: 1.36, w: 0.22, h: 0.22 });
  text(s, 'Replicate platform', { x: 0.82, y: 1.34, w: 1.9, h: 0.26, fontSize: 11, bold: true });
  const left = ['Predictions API (public models)', 'Deployments & trainings (private)', 'Sign-up & account pages', 'Entitlements: who can run'];
  left.forEach((t, i) => {
    const y = 1.75 + i * 0.73;
    card(s, 0.5, y, 2.25, 0.58, { shadow: false });
    text(s, t, { x: 0.62, y, w: 2.05, h: 0.58, fontSize: 9.5, valign: 'middle' });
  });
  // center: Metronome
  s.addShape('roundRect', { x: 3.2, y: 1.3, w: 3.6, h: 3.72, rectRadius: 0.1, fill: { color: C.dark }, line: { color: C.dark } });
  s.addImage({ data: asset('metronome_icon_lime_s.png'), x: 3.45, y: 1.47, w: 0.3, h: 0.255 });
  text(s, 'Metronome', { x: 3.85, y: 1.44, w: 2.0, h: 0.3, fontSize: 12, bold: true, color: C.white });
  const layers = [
    ['Ingest', 'events by API, idempotent, 34-day backfill'],
    ['Price', 'billable metrics, rate card, packages'],
    ['Contract', 'credits, commits, overrides, subscriptions'],
    ['Track', 'real-time balances and draft invoices'],
    ['Signal', 'webhooks, embeddable dashboards, APIs'],
  ];
  layers.forEach(([k, d], i) => {
    const y = 1.9 + i * 0.6;
    s.addShape('roundRect', { x: 3.4, y, w: 3.2, h: 0.48, rectRadius: 0.06, fill: { color: C.dark2 }, line: { color: C.dark2 } });
    text(s, k, { x: 3.55, y, w: 0.8, h: 0.48, fontSize: 9.5, bold: true, color: C.lime, valign: 'middle' });
    text(s, d, { x: 4.35, y, w: 2.2, h: 0.48, fontSize: 9, color: C.onDark, valign: 'middle' });
  });
  // right: systems
  text(s, 'Your quote-to-cash', { x: 7.25, y: 1.34, w: 2.25, h: 0.26, fontSize: 11, bold: true });
  const right = [
    ['Stripe', 'self-serve invoices, card collection'],
    ['NetSuite', 'enterprise invoices or revenue'],
    ['Salesforce', 'contracts, commits, balances (daily)'],
    ['Data warehouse', 'full data export'],
  ];
  right.forEach(([n, d], i) => {
    const y = 1.75 + i * 0.73;
    card(s, 7.25, y, 2.25, 0.58, { shadow: false });
    text(s, [{ text: n, options: { bold: true, breakLine: true } }, { text: d, options: { color: C.muted, fontSize: 8.5 } }],
      { x: 7.37, y, w: 2.05, h: 0.58, fontSize: 9.5, valign: 'middle' });
  });
  // arrows
  const arrow = (x1, y1, x2, color) => s.addShape('line', { x: x1, y: y1, w: x2 - x1, h: 0, line: { color, width: 1.75, endArrowType: 'triangle' } });
  arrow(2.8, 2.04, 3.15, C.green);
  arrow(2.8, 2.77, 3.15, C.green);
  s.addShape('line', { x: 2.8, y: 3.5, w: 0.35, h: 0, line: { color: C.deep, width: 1.75, beginArrowType: 'triangle' } });
  s.addShape('line', { x: 2.8, y: 4.23, w: 0.35, h: 0, line: { color: C.deep, width: 1.75, beginArrowType: 'triangle' } });
  [2.04, 2.77, 3.5, 4.23].forEach((y) => arrow(6.85, y, 7.2, C.green));
  text(s, 'usage events and sign-ups flow in; webhooks and dashboards flow back; invoices and syncs flow out',
    { x: 0.5, y: 5.06, w: 9, h: 0.16, fontSize: 7.5, color: C.muted2, align: 'center', italic: true });
  notes(s, {
    purpose: 'Answer "where does it fit in my stack?" (the marketecture the brief asks for) and show there is no rip-and-replace.',
    emphasize: 'Three flows. IN: your platform sends usage events (seconds, hardware, model), and sign-up creates a customer and a contract from a package alias, asynchronously, so sign-up stays card-free and Metronome is never in the critical path. BACK: webhooks tell your entitlement service when a trial runs out or a commit runs low, and dashboards embed in your account pages. OUT: Stripe keeps collecting self-serve payments, NetSuite gets enterprise invoices (or revenue data), Salesforce gets contracts, commits and balances daily.',
    tone: 'Technical but plain-spoken. Reassuring for the engineers in the room.',
    timing: '1 minute 30 seconds.',
    ask: '"Where do usage records live today, in a queue or a warehouse?" and "Is NetSuite your system for enterprise invoicing, or only for revenue recognition?"',
    ifAsked: 'Webhooks are signed, delivered at least once, and retried for up to 48 hours. Thresholds fire within about 5 minutes of the usage being ingested. The Salesforce sync is daily, and live numbers come from the API or dashboards. NetSuite is in Public Beta, with throughput up to 25,000 arrears invoices a month. Stripe invoices are created automatically when a Metronome invoice finalizes, and the billing provider can be set per contract (Stripe for paygo, NetSuite for enterprise).',
  });

  // ============================================================ 7. WHAT CHANGES
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Solution' });
  eyebrow(s, 'WHAT CHANGES');
  s.addText('Four blockers, four configurations you’ll see live', { placeholder: 'title' });
  const hdr = (t) => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.dark }, fontSize: 9.5 } });
  const tableRows = [
    [hdr('Today'), hdr('With Metronome'), hdr('In the demo')],
    ['Two teams and weeks per machine type',
      'Hardware is a pricing dimension: a new GPU is one rate, scheduled ahead or backdated to launch day. Discounts, commits and % fees follow automatically.',
      'Launch Nvidia L40S live'],
    ['Trial credit checked once a day: up to ~$500 of GPU time per user',
      '$10 trial credit, valid 30 days. Balances update as usage lands; alerts fire within ~5 min by webhook (~$2 on the same GPU). One rule covers every sign-up.',
      'Ada’s trial: used up and flagged'],
    ['No fixed or % fees, so no support tiers',
      'Subscription product: Pro Support at $500/month. Composite product: Enterprise Support at 10% of compute.',
      'Brightframe and Northwind invoices'],
    ['An engineer pulls commit data',
      'Prepaid or postpaid commits, negotiated discount, live balance and ledger, embeddable dashboard, commit alerts, Salesforce sync.',
      'Northwind (prepaid) or Kepler (postpaid)'],
  ].map((r, i) => i === 0 ? r : [
    { text: r[0], options: { bold: true } },
    { text: r[1] },
    { text: r[2], options: { bold: true, color: C.deep } },
  ]);
  s.addTable(tableRows, {
    x: 0.5, y: 1.32, w: 9, colW: [2.15, 4.75, 2.1], fontFace: FONT, fontSize: 9.5, color: C.ink,
    fill: { color: C.card }, border: { type: 'solid', pt: 0.75, color: C.border }, margin: [0.06, 0.1, 0.06, 0.1],
    valign: 'middle', rowH: [0.32, 0.8, 0.86, 0.68, 0.8],
  });
  notes(s, {
    purpose: 'Bridge from problems to the demo: each blocker becomes a configuration they are about to see working, not a promise.',
    emphasize: 'The "In the demo" column is a commitment. The trial row carries the number: from up to a day of exposure (~$500 on an 8x A40) to ~5 minutes (~$2), because thresholds are evaluated at least every three minutes and fire within five minutes of ingest (Metronome docs). The commit row: we will show both prepaid and postpaid, because we do not know yet which one you use.',
    tone: 'Energetic and confident. This is the turn from listening to showing.',
    timing: '1 minute.',
    talk: 'Enough slides. Let me show you your own price list running in Metronome.',
    ifAsked: 'Every capability here is documented: "Create and manage rate cards" (dimensional pricing, scheduled rate changes), "Free trials" and "Threshold notifications", "Create products" (subscription and composite), "Launch an enterprise commit model" and "Build API-powered customer dashboards".',
  });

  // ============================================================ 8. DEMO DIVIDER
  pres.addSection({ title: 'Demo' });
  s = pres.addSlide({ masterName: 'DARK', sectionTitle: 'Demo' });
  s.addImage({ data: asset('metronome_logo_white_s.png'), x: 0.55, y: 0.5, w: 2.9, h: 0.24 });
  text(s, 'LIVE DEMO  ·  30 MIN', { x: 0.55, y: 1.42, w: 4.6, h: 0.25, fontSize: 10, bold: true, charSpacing: 2, color: C.lime });
  s.addText('Replicate’s pricing, running in Metronome', { placeholder: 'title' });
  text(s, 'Four customers on one rate card', { x: 0.55, y: 3.5, w: 4.6, h: 0.3, fontSize: 11, bold: true, color: C.onDark });
  const personas = ['Ada Okafor · free trial', 'Brightframe AI · pay-as-you-go + Pro Support', 'Northwind Media · $100k prepaid commit', 'Kepler Games · $100k postpaid commit'];
  personas.forEach((p, i) => {
    const y = 3.88 + i * 0.32;
    s.addShape('ellipse', { x: 0.58, y: y + 0.06, w: 0.1, h: 0.1, fill: { color: C.lime }, line: { color: C.lime } });
    text(s, p, { x: 0.8, y, w: 4.3, h: 0.26, fontSize: 10, color: C.onDarkMuted });
  });
  const acts = [
    ['0', 'The model: one event, every price', '2 min'],
    ['1', 'A new GPU is a rate, not a project', '7 min'],
    ['2', 'A card-free trial that can’t leak', '6 min'],
    ['3', 'Support tiers you can sell', '5 min'],
    ['4', 'Where am I on my commit?', '7 min'],
    ['5', 'Fits your quote-to-cash', '3 min'],
  ];
  acts.forEach(([n, t, m], i) => {
    const y = 0.95 + i * 0.68;
    s.addShape('roundRect', { x: 5.55, y, w: 4.0, h: 0.56, rectRadius: 0.08, fill: { color: C.dark2 }, line: { color: C.dark2 } });
    text(s, n, { x: 5.7, y, w: 0.35, h: 0.56, fontSize: 16, bold: true, color: C.lime, valign: 'middle' });
    text(s, t, { x: 6.1, y, w: 2.75, h: 0.56, fontSize: 11.5, bold: true, color: C.white, valign: 'middle' });
    text(s, m, { x: 8.85, y, w: 0.6, h: 0.56, fontSize: 9.5, color: C.onDarkMuted, valign: 'middle', align: 'right' });
  });
  notes(s, {
    purpose: 'Anchor the demo flow and the timing so the audience knows where we are going, and so you can come back to this slide if questions run long.',
    emphasize: 'Each act answers one blocker. Four customers, one rate card, which is the "one rate card for every commercial model" story.',
    tone: 'Energetic. Then switch to the Metronome tab.',
    timing: '15 seconds, then the demo (see the demo runbook in "05 demo").',
    ask: 'Before act 4: "Do your enterprise customers prepay their commitment, or pay monthly against a minimum?" Show Northwind for prepaid and Kepler for postpaid.',
  });

  // ============================================================ 9. NEXT STEPS
  pres.addSection({ title: 'Next steps' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Next steps' });
  eyebrow(s, 'NEXT STEPS');
  s.addText('A 4-week path to a confident decision', { placeholder: 'title' });
  card(s, 0.5, 1.32, 3.7, 3.0);
  text(s, 'What you saw today', { x: 0.75, y: 1.5, w: 3.3, h: 0.3, fontSize: 13, bold: true });
  const saw = ['A new GPU priced with one rate', 'Trial overage flagged in minutes, not a day', 'Fixed and % support tiers on real invoices', 'Commit balances visible to customers and sales'];
  for (let i = 0; i < saw.length; i++) {
    const y = 1.98 + i * 0.56;
    await iconBubble(s, 'FiCheck', 0.75, y, 0.32);
    text(s, saw[i], { x: 1.2, y: y + 0.02, w: 2.85, h: 0.4, fontSize: 11 });
  }
  const steps = [
    ['Week 1', 'Technical deep-dive', 'Event schema (seconds, hardware, model), entitlement webhooks, Stripe, NetSuite and Salesforce mapping'],
    ['Weeks 2–3', 'Pilot on your data', 'Replay a day of real compute events in a sandbox, mirror one enterprise contract, launch one GPU'],
    ['Week 4', 'Success review', 'A GPU priced in under a day · trial overage caught in minutes · one commit dashboard live → proposal'],
  ];
  steps.forEach(([w, t, d], i) => {
    const y = 1.32 + i * 1.02;
    card(s, 4.45, y, 5.05, 0.9);
    s.addShape('roundRect', { x: 4.65, y: y + 0.2, w: 0.95, h: 0.28, rectRadius: 0.14, fill: { color: C.lime }, line: { color: C.lime } });
    text(s, w, { x: 4.65, y: y + 0.2, w: 0.95, h: 0.28, fontSize: 9, bold: true, align: 'center', valign: 'middle' });
    text(s, t, { x: 5.75, y: y + 0.12, w: 3.6, h: 0.28, fontSize: 12, bold: true });
    text(s, d, { x: 5.75, y: y + 0.42, w: 3.6, h: 0.42, fontSize: 9, color: C.muted });
  });
  card(s, 0.5, 4.45, 9, 0.58, { fill: C.limePale, line: C.limeLight, shadow: false });
  text(s, [
    { text: 'To confirm with you: ', options: { bold: true } },
    { text: 'prepaid or postpaid commits?  ·  trial credit amount and abuse rate?  ·  support tier pricing?  ·  NetSuite for billing, or revenue only?' },
  ], { x: 0.72, y: 4.45, w: 8.6, h: 0.58, fontSize: 10, valign: 'middle' });
  notes(s, {
    purpose: 'Close with a concrete, mutual plan and secure the next meeting: drive toward the decision that Metronome is right for Replicate.',
    emphasize: 'The success criteria in Week 4 are their own blockers, made measurable: a GPU priced in under a day, trial overage caught in minutes, one commit dashboard live. Then ask for the Week 1 deep-dive date and attendees.',
    tone: 'Decisive and collaborative. Summarize, then ask for the next step. Do not over-talk.',
    timing: '2 minutes, after the demo.',
    ask: '"Does this plan work for you? Who should join the technical deep-dive from platform, finance and RevOps? Can we put Week 1 on the calendar now?"',
    ifAsked: 'If they want cash up front or worry about fraud on high-cost models: see the appendix on prepaid credits with auto-recharge (the industry standard at Together AI, Fireworks and OpenAI).',
  });

  // ============================================================ A1. PREPAID OPTION
  pres.addSection({ title: 'Appendix' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Appendix' });
  eyebrow(s, 'APPENDIX  ·  IF ASKED');
  s.addText('Option: prepaid credits with auto-recharge', { placeholder: 'title' });
  card(s, 0.5, 1.32, 4.4, 2.75);
  text(s, 'The standard among your competitors', { x: 0.75, y: 1.5, w: 4.0, h: 0.3, fontSize: 13, bold: true });
  const comp = [
    ['Together AI', 'prepaid credits, $5 minimum, auto-recharge; no free trial'],
    ['Fireworks AI', 'every self-serve account prepaid since Jul 1, 2026; auto reload'],
    ['OpenAI API', 'prepaid billing with auto-reload'],
  ];
  comp.forEach(([n, d], i) => {
    const y = 2.0 + i * 0.72;
    text(s, n, { x: 0.75, y, w: 4.0, h: 0.26, fontSize: 11.5, bold: true, color: C.deep });
    text(s, d, { x: 0.75, y: y + 0.27, w: 4.0, h: 0.3, fontSize: 10, color: C.ink });
  });
  card(s, 5.1, 1.32, 4.4, 2.75, { fill: C.limePale, line: C.limeLight });
  text(s, 'How it runs in Metronome', { x: 5.35, y: 1.5, w: 4.0, h: 0.3, fontSize: 13, bold: true });
  text(s, [
    { text: 'Keep the card-free trial credit as the front door', options: { bullet: true, breakLine: true } },
    { text: 'Convert to a prepaid commit, released only when the Stripe payment succeeds (payment gate)', options: { bullet: true, breakLine: true } },
    { text: 'Auto-recharge: when the balance reaches a threshold, Metronome charges and tops it back up', options: { bullet: true, breakLine: true } },
    { text: 'A $0 balance alert tells your app to pause usage', options: { bullet: true } },
  ], { x: 5.3, y: 1.95, w: 4.0, h: 2.2, fontSize: 10.5, paraSpaceAfter: 6 });
  text(s, 'Sources: Together AI docs; Fireworks blog “Billing migration to prepaid” (Jun 2026); OpenAI Help Center; Metronome docs “Set prepaid balance thresholds”, “Payment-gated commits”, “Free trials”.',
    { x: 0.5, y: 4.25, w: 9, h: 0.4, fontSize: 8, color: C.muted2 });
  notes(s, {
    purpose: 'A suggestion, only if fraud, collections or cash flow come up. Prepaid credits with auto-recharge is now the norm among Replicate’s direct competitors.',
    emphasize: 'You do not have to choose between a card-free trial and getting paid up front. The trial stays your differentiator, and conversion can land on prepaid credits that refill automatically through Stripe.',
    tone: 'Advisory, not pushy: "here is what the market does and how you would do it here".',
    ifAsked: 'Metronome docs: auto-recharge needs a threshold of at least $5 and a recharge-to amount at least $10 above it. Payment-gated commits are released only after the Stripe payment succeeds; failed payments disable the threshold config until you re-enable it.',
  });

  // ============================================================ A2. OBJECTIONS
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Appendix' });
  eyebrow(s, 'APPENDIX  ·  QUESTIONS WE EXPECT');
  s.addText('Straight answers to the hard questions', { placeholder: 'title' });
  const qa = [
    ['Why not keep building in-house?', 'Today one machine type costs two teams and weeks. Here it is one rate, and your engineers send usage once and go back to the product.'],
    ['Why not Stripe Billing alone?', 'Keep Stripe for collection. Metronome, now a Stripe product, adds complex usage pricing and custom enterprise contracts on top.'],
    ['Is it really real time?', 'Balances and draft invoices update as usage lands. Thresholds are evaluated at least every 3 min and fire within 5 min. The hard stop stays in your app.'],
    ['Salesforce is only daily?', 'Yes, the sync is daily. Live numbers come from the API, webhooks and embedded dashboards.'],
    ['What about NetSuite?', 'Public Beta. NetSuite either bills enterprise contracts or receives Stripe-billed invoices for revenue, up to 25,000 arrears invoices/month.'],
    ['Can it take our volume?', 'Up to 110,000 events/s (5,000/s by default, raised on request), 100 events per call, 34-day dedupe and backfill window.'],
    ['We’re part of Cloudflare now', 'Replicate’s API and brand continue. Metronome supports several Stripe accounts (multi-entity) and custom pricing units, so it fits either path.'],
    ['Existing commits and balances?', 'Import existing contracts and invoices, and carry open balances with manual ledger entries.'],
  ];
  s.addTable(qa.map(([q, a]) => [{ text: q, options: { bold: true } }, { text: a }]), {
    x: 0.5, y: 1.3, w: 9, colW: [2.5, 6.5], fontFace: FONT, fontSize: 9, color: C.ink,
    fill: { color: C.card }, border: { type: 'solid', pt: 0.75, color: C.border }, margin: [0.04, 0.1, 0.04, 0.1],
    valign: 'middle', rowH: 0.45,
  });
  notes(s, {
    purpose: 'Backup for objection handling. Use it only if a question comes up and you want the exact wording; never present it top to bottom.',
    emphasize: 'Acknowledge the limit first (daily Salesforce sync, NetSuite in beta, hard stop in your app), then the answer. Owning limits builds trust.',
    tone: 'Calm, factual, non-defensive.',
    ifAsked: 'Sources, all from docs.metronome.com: "Manage your customer lifecycle with Metronome notifications" (evaluation timing), "Sync into Salesforce" (daily), "Integrate with NetSuite" (Public Beta, 25,000 invoices/month), "Usage events at scale" (throughput), "Invoice with Stripe" (multi-entity), "Set currencies and custom pricing units", "Import existing invoices", "Track the remaining balance of a credit or commit" (manual ledger entries).',
  });

  // ============================================================ A3. SOURCES
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Appendix' });
  eyebrow(s, 'APPENDIX  ·  SOURCES');
  s.addText('Every capability shown is documented', { placeholder: 'title' });
  const srcL = [
    ['New machine type', 'Create and manage rate cards · Create products (pricing group keys) · Launch new pricing'],
    ['GPU-hour pricing', 'Billing for provisioned throughput (seconds → hours conversion)'],
    ['Trial', 'Free trials · Implement a free trial · Threshold notifications'],
    ['Support tiers', 'Create products (subscription, composite) · Define subscription pricing'],
    ['Commits', 'Launch an enterprise commit model · Apply credits and commits · Offer discounts on commits'],
    ['Visibility', 'Build API-powered customer dashboards · Track the remaining balance of a credit or commit'],
    ['Quote-to-cash', 'Invoice with Stripe · Integrate with NetSuite · Sync into Salesforce'],
    ['Scale', 'Usage events at scale · Send usage events to /ingest'],
  ];
  s.addTable(srcL.map(([k, v]) => [{ text: k, options: { bold: true, color: C.deep } }, { text: v }]), {
    x: 0.5, y: 1.3, w: 9, colW: [1.8, 7.2], fontFace: FONT, fontSize: 9, color: C.ink,
    fill: { color: C.card }, border: { type: 'solid', pt: 0.75, color: C.border }, margin: [0.04, 0.1, 0.04, 0.1],
    valign: 'middle', rowH: 0.36,
  });
  text(s, 'All at docs.metronome.com. Business facts: Replicate Series B statement (Dec 2023), Cloudflare blog (Nov 2025), replicate.com/pricing, Stripe newsroom (Jan 2026), Together AI docs, Fireworks blog (Jun 2026), OpenAI Help Center.',
    { x: 0.5, y: 4.3, w: 9, h: 0.5, fontSize: 8.5, color: C.muted2 });
  notes(s, {
    purpose: 'Reference only: where each claim comes from, so any statement can be backed on the spot or in the follow-up email.',
    emphasize: 'Every technical choice in the demo comes from the official Metronome documentation.',
    tone: 'Not presented. Use it if someone asks "where is that documented?".',
  });

  await pres.writeFile({ fileName: 'Replicate_x_Metronome.pptx' });
  console.log('written Replicate_x_Metronome.pptx');
})();
