// Proposed "Next steps" body: a 3-week scoped pilot (15 Oct 2026).
// Builds only the body (the three week cards between the title and the "To confirm with you" strip), so it can be
// pasted into a duplicate of the live Next steps slide and keep that slide's hand-made breadcrumb, footer and counter.
//   node build_pilot_slide.js && python3 repack.py pilot_slide_raw.pptx pilot-slide-body.pptx
//   ->  pilot-slide-body.pptx (one slide, body only, speaker notes included)
const pptxgen = require('pptxgenjs');
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fi = require('react-icons/fi');

// design tokens: same as build_deck.js (metronome.com)
const C = {
  ink: '0D171A', bg: 'FAFBF8', card: 'FFFFFF', border: 'E5E7DD', muted: '565F5F', muted2: '6B726D',
  lime: 'C3EE8F', limeLight: 'DAF6AF', limePale: 'F1FFD0', deep: '125B49',
};
const FONT = 'Inter';

async function icon(name, color) {
  let svg = ReactDOMServer.renderToStaticMarkup(React.createElement(fi[name], { size: 128 }));
  svg = svg.replace(/currentColor/g, '#' + color);
  const buf = await sharp(Buffer.from(svg)).resize(128, 128).png().toBuffer();
  return 'image/png;base64,' + buf.toString('base64');
}

// fresh option objects every time (pptxgenjs mutates them)
const shadow = () => ({ type: 'outer', color: '0D171A', opacity: 0.08, blur: 6, offset: 1.5, angle: 90 });

function text(slide, t, o) {
  slide.addText(t, Object.assign({ fontFace: FONT, color: C.ink, margin: 0, isTextBox: true, valign: 'top' }, o));
}

const weeks = [
  {
    week: 'WEEK 1', title: 'Self-serve trial, live',
    what: 'Your compute events flow into a sandbox (live, or a replayed day), with your real trial terms and alerts wired to your app.',
    who: 'With your platform engineers',
    proof: 'Trial exhaustion reaches your app within ~5 min, not a day',
  },
  {
    week: 'WEEK 2', title: 'One enterprise deal, visible',
    what: 'Mirror one signed $100k / 3-year deal (ramp, discount, rollover) plus Pro and Enterprise Support, synced to Salesforce daily.',
    who: 'With RevOps and finance',
    proof: 'Customer and AE see the commit balance, no engineer needed',
  },
  {
    week: 'WEEK 3', title: 'A new GPU as config, then decide',
    what: 'Your team adds your next machine type to the rate card on its own. End of week 3: go/no-go review, then our proposal.',
    who: 'With your pricing owner and decision makers',
    proof: 'New GPU priced by your team in under 1 hour, no code change',
  },
];

(async () => {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  pres.author = 'Rania Benman';
  pres.company = 'Metronome';
  pres.title = 'Next steps: 3-week scoped pilot (body only)';
  pres.theme = { headFontFace: FONT, bodyFontFace: FONT };

  const s = pres.addSlide();
  s.background = { color: C.bg };

  const checkIcon = await icon('FiCheck', C.ink);
  const usersIcon = await icon('FiUsers', C.deep);

  // column labels
  const label = { y: 1.32, h: 0.18, fontSize: 8, bold: true, charSpacing: 1, color: C.muted2 };
  text(s, 'WHAT WE DO TOGETHER, ON YOUR DATA', Object.assign({ x: 1.98, w: 4.25, objectName: 'Pilot label: what' }, label));
  text(s, 'SUCCESS CRITERION', Object.assign({ x: 6.35, w: 3.0, objectName: 'Pilot label: success' }, label));

  weeks.forEach((wk, i) => {
    const y = 1.56 + i * 0.94;
    const n = i + 1;
    s.addShape('roundRect', {
      x: 0.5, y, w: 9, h: 0.86, rectRadius: 0.08,
      fill: { color: C.card }, line: { color: C.border, width: 0.75 }, shadow: shadow(), objectName: `Pilot W${n} card`,
    });
    // week pill (same style as the live slide: lime, 14pt bold dark green)
    s.addShape('roundRect', {
      x: 0.68, y: y + 0.28, w: 1.1, h: 0.3, rectRadius: 0.15,
      fill: { color: C.lime }, line: { color: C.lime }, objectName: `Pilot W${n} pill`,
    });
    text(s, wk.week, { x: 0.68, y: y + 0.28, w: 1.1, h: 0.3, fontSize: 14, bold: true, color: C.deep,
      align: 'center', valign: 'middle', objectName: `Pilot W${n} pill text` });
    // what we do together
    text(s, wk.title, { x: 1.98, y: y + 0.09, w: 4.25, h: 0.22, fontSize: 12, bold: true, objectName: `Pilot W${n} title` });
    text(s, wk.what, { x: 1.98, y: y + 0.33, w: 4.25, h: 0.31, fontSize: 9, color: C.muted, objectName: `Pilot W${n} what` });
    s.addImage({ data: usersIcon, x: 1.98, y: y + 0.66, w: 0.12, h: 0.12, objectName: `Pilot W${n} who icon` });
    text(s, wk.who, { x: 2.15, y: y + 0.64, w: 4.08, h: 0.16, fontSize: 8, bold: true, color: C.deep,
      objectName: `Pilot W${n} who` });
    // success criterion
    s.addShape('roundRect', {
      x: 6.35, y: y + 0.1, w: 3.0, h: 0.66, rectRadius: 0.06,
      fill: { color: C.limePale }, line: { color: C.limeLight, width: 0.75 }, objectName: `Pilot W${n} success panel`,
    });
    s.addShape('ellipse', { x: 6.47, y: y + 0.29, w: 0.28, h: 0.28, fill: { color: C.lime }, line: { color: C.lime },
      objectName: `Pilot W${n} check bubble` });
    s.addImage({ data: checkIcon, x: 6.54, y: y + 0.36, w: 0.14, h: 0.14, objectName: `Pilot W${n} check` });
    text(s, wk.proof, { x: 6.85, y: y + 0.1, w: 2.42, h: 0.66, fontSize: 9.5, bold: true, color: C.deep,
      valign: 'middle', objectName: `Pilot W${n} success` });
  });

  s.addNotes([
    'PURPOSE: Close with a concrete, low-risk ask: a 3-week pilot on Replicate\'s own events that proves each blocker is solved and ends in a dated go/no-go. It answers "how do we get started?" and turns the demo into a decision.',
    'EMPHASIZE: Each week proves blockers on their own data, with a measurable criterion: trial exhaustion reaches their app within ~5 minutes (week 1); customer and AE see the commit balance without an engineer, with Pro and Enterprise Support on the invoice (week 2); their own team prices the next GPU in under an hour (week 3). Week 3 ends with the go/no-go review and our proposal.',
    'TONE: Confident and collaborative. This is an ask, not a pitch: slow down, ask the questions, then stop talking.',
    'TIMING: 2 minutes, after the demo.',
    'TALK TRACK: "You\'ve seen your four blockers handled on sample data. Our ask: three weeks to prove it on yours, in a sandbox, with nothing in production. Week 1 is your self-serve trial: your compute events, live or a replayed day, your real trial terms, and the alert wired to your app. Week 2, we re-create one signed enterprise deal with its ramp, discount and rollover, add your support tiers, and show the balance in your product and in Salesforce. Week 3, your team adds the next GPU on its own, and we meet for a go/no-go."',
    'ASK THEM: The four "To confirm with you" questions. Then: "Can we set the kickoff and go/no-go dates now? Who joins from platform engineering, RevOps, finance and pricing?"',
    'IF ASKED: Why ~5 minutes and not seconds? Thresholds are evaluated at least every 3 minutes and fire within 5 minutes of the usage being ingested; the hard stop stays in your app (docs: "Manage your customer lifecycle with Metronome notifications"). Our engineers are busy? Week 1 can start from a replayed day of events (34-day backfill window); live streaming can follow. Salesforce is not real time? The sync is daily and has to be switched on for the pilot account; live numbers come from the API, webhooks and the embedded dashboard. Ramps, discounts and rollover: docs "Launch an enterprise commit model" and "Manage contract lifecycle transitions". What does it cost? The proposal comes with the go/no-go review.',
  ].join('\n\n'));

  await pres.writeFile({ fileName: 'pilot_slide_raw.pptx' });
  console.log('written pilot_slide_raw.pptx');
})();
