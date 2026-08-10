# Northbound

Marketing site for an exclusive homeowner-insurance-lead business. Static HTML/CSS/JS —
no build step, no dependencies.

```
index.html     one-page site
privacy.html   CAN-SPAM / privacy draft
terms.html     commercial terms draft
styles.css     all styling
script.js      nav, reveal, territory grid, lead form
```

Preview locally:

```bash
cd ~/Desktop/northbound && python3 -m http.server 8752
# → http://localhost:8752
```

## Positioning

The page does **not** argue against other cold-email vendors — prospects have never heard of
them. It argues against the two things agencies already spend money on:

| | Cost per acquired policy |
|---|---|
| Direct mail | $250–$750 |
| Shared lead vendors | $180–$400 |
| **Northbound** | **$160–$200** |

At $40/lead and a 20–25% close rate, Northbound lands under both. That's the whole pitch,
and it's the first section after the hero.

## Pricing

| Tier | Price | Volume |
|---|---|---|
| Starter | **$40**/lead | up to 50/mo |
| Growth | **$35**/lead | 51–299/mo |
| Scale | **$30**/lead | 300+/mo |

To change: edit `.tier__price` in `index.html`, and the `$40` in the hero note, the CAC
card, and the README table above.

## ⚠️ Fill in before launch

Everything below is plausible placeholder copy, not verified fact. Ship it wrong and it's
a false-advertising problem.

**Company claims in the hero strip and body copy**
- `38 states served` — replace with your real number
- `~21 days to first lead` — replace with your real onboarding time
- `275M+ homeowner records` (How it works → Targeting)
- `$160–$200` CAC and the `20–25% close rate` it assumes
- `~75%` phone coverage and `~80%` DOB coverage in the lead record

**Sample content**
- The reply card in the "What a lead looks like" section is labeled **"Sample reply"** and
  uses an invented name. Swap in a real, permissioned screenshot before launch, or leave the
  label on. Do not present invented replies as real customer quotes.
- There is deliberately **no testimonials section and no team-bios section** — those need
  real people. Add them when you have real ones.

**Contact + legal**
- `hello@northbound.example` in the footer and `FALLBACK_EMAIL` in `script.js`
- Mailing address in the footer (CAN-SPAM requires a real physical address)
- All `[BRACKETED]` fields in `privacy.html` and `terms.html`, then a lawyer review

**Industry figures** — the $250–750 direct mail and $180–400 shared-lead ranges are commonly
cited but you should keep a source on file for each.

## Wiring up the form

`script.js` line 7:

```js
const FORM_ENDPOINT = 'https://northbound-api.<you>.workers.dev/lead';
```

With it empty, the form validates and then opens a prefilled email. With it set, it POSTs
JSON (`name, agency, email, zips, volume, source, ts`) — same shape as the Reframe Houses
Worker, so that one can be copied.

## Deploying

GitHub Pages: push and serve from the repo root. Or Cloudflare Pages with no build command
and `/` as the output directory.
