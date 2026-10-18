# Deck source

The master copy of the pre-demo deck is the Google Slides file **"Replicate x Metronome - pre-demo deck"** in Google Drive › Metronome › Presentation ([open](https://docs.google.com/presentation/d/1HdrACtg-SPn5qvqFiTN043FZZF6ojzNDiABUA-67xo0/edit)). The logos and background panel it uses sit in the same Drive folder, with copies in `../brand/`.

This folder holds the source the deck was generated from:

| File | What it is |
|---|---|
| `build_deck.js` | pptxgenjs script that generates the deck: layouts, every slide, and speaker notes (purpose, emphasis, tone, timing, talk track). |
| `render_assets.js` | Renders the logos and the hero gradient panel used by the deck. |
| `repack.py` | Re-zips the generated .pptx with compression. pptxgenjs stores files uncompressed. |
| `Replicate x Metronome - pre-demo deck.pptx` | Latest generated version (13 slides). |
| `build_pilot_slide.js` | Generates only the body of the proposed "scoped pilot" Next steps slide (three week cards with success criteria), plus its speaker notes. |
| `pilot-slide-body.pptx` | Output of `build_pilot_slide.js`, the file imported into Google Slides. |
| `build_stature_slide.js` | Generates only the body of the appendix slide "Who already runs on Metronome" (customer logo row, three sourced stats, the scale statement, footnotes), plus its speaker notes. With `--logos-only` it outputs the logo row alone. |
| `stature-slide-body.pptx` | Output of `build_stature_slide.js`, the file first imported into Google Slides. |
| `stature-logo-row.pptx` | Output of `build_stature_slide.js --logos-only`, the logo row pasted onto the live slide. |
| `render_customer_logos.js` | Recolours the customer logo SVGs to metronome.com's logo grey (#565F5F) and renders them as transparent PNGs, kept in `../brand/customer-logos/`. |

## The generated file is not the master

The Google Slides deck was edited by hand after it was generated: Replicate logo on the title slide, a new Agenda slide, an edited "Two growth engines" slide, and hidden slides. `build_deck.js` does not contain those edits. Regenerating and re-uploading would replace them, so change the Google Slides file directly.

To add a generated slide to the live deck without touching hand edits:

1. Build the slide here.
2. Upload the .pptx to Drive.
3. In Google Slides, select the slide to insert after.
4. Use File › Import slides, pick only that slide, keep "Keep original theme" ticked.
5. Trash the uploaded .pptx.

That is how "Why we are here" was added on 15 Oct 2026. In `build_deck.js` it sits after "Two growth engines" (generated slide 3).

When a slide must keep the hand-made chrome (breadcrumb, eyebrow, footer, page counter), import only its body instead:

1. Duplicate a live slide of the same kind (Slide › Duplicate slide).
2. On the copy, marquee-select the old body and delete it, leaving the eyebrow, title, breadcrumb and footer.
3. Import the body .pptx with "Keep original theme" unticked, so no extra theme is added.
4. Marquee-select its objects, copy them, and paste them onto the copy, where they keep their position.
5. Copy the imported speaker notes onto the copy.
6. Retype the eyebrow and title on the copy.
7. Delete the imported slide and trash the uploaded .pptx.

Two slides were made this way on 15 Oct 2026:
- **Next steps, scoped pilot** (`build_pilot_slide.js`): a copy of the live Next steps slide, with the title retyped in bold capitals like the other restyled slides. It has since replaced the original Next steps slide in the live deck.
- **Appendix, "Who already runs on Metronome"** (`build_stature_slide.js`): a copy of the Sources slide, moved up one place so it opens the appendix. Every figure is footnoted. The ~$1B price is press-reported (Stripe never disclosed terms), so the slide says "reported".

On 16 Oct 2026 that slide's typed customer names were replaced by a logo row: OpenAI, Anthropic, NVIDIA, Databricks, Confluent, and Hugging Face, which was added then. The row was pasted the same way, from `stature-logo-row.pptx`, and the title box was deleted. Five logos come from metronome.com's own logo wall. Databricks, which is not on that wall, comes from the header of databricks.com. All six are recoloured to the wall's grey. The "$1B" stat became "~$1B" the same day. The slide's footnotes were also linked to their sources. There are five links, because footnote ³ cites both Upstarts Media and the Stripe newsroom. `build_stature_slide.js` writes the same links.

The Sources slide's Metronome doc references were also linked by hand on 16 Oct 2026, each to its official page. The URL list is in `../../research-brief.md`, section 3. The same day, the sources that are not about Metronome were removed from the line under its table: Replicate's Series B statement, the Cloudflare blog, replicate.com/pricing, Together AI docs, the Fireworks blog and the OpenAI Help Center. The slides that use those facts still cite them: the footnotes on "Why we are here" and the source line on the prepaid appendix slide. The line now reads "All at docs.metronome.com. Business facts: Stripe newsroom (Jan 2026)."

Two small fixes were later made by hand in Google Slides, so they are not in `build_deck.js` either. Both are on the "4 blockers" slide:
- The clock icon on the "once a day" card was replaced with a no-entry sign (`icon-no-entry.png`, in the Drive Presentation folder and in `../brand/`). It is `MdDoNotDisturbOn` from the open-source react-icons library (Google's Material Design icons).
- The NetSuite chip was widened to 2.3 in so its text no longer touches the edges. The Salesforce chip moved to X 7.8 in and narrowed to 1.5 in to make room.

## Rebuild

From a folder with `pptxgenjs`, `sharp`, `react`, `react-dom` and `react-icons` installed, and the brand images in `assets/` (see `render_assets.js`):

```bash
node build_deck.js
python3 repack.py Replicate_x_Metronome.pptx "Replicate x Metronome - pre-demo deck.pptx"
```

The two slide bodies build the same way. The customer slide also needs the logo PNGs from `../brand/customer-logos/`, copied to `assets/customer-logos/`:

```bash
node build_pilot_slide.js
python3 repack.py pilot_slide_raw.pptx pilot-slide-body.pptx
node build_stature_slide.js
python3 repack.py stature_slide_raw.pptx stature-slide-body.pptx
node build_stature_slide.js --logos-only
python3 repack.py stature_slide_raw.pptx stature-logo-row.pptx
```

To re-render the logos from their SVGs, run `node render_customer_logos.js assets/customer-logos openai=<file.svg> …` with one `name=file` pair per logo.
