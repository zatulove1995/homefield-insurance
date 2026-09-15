# Homefield — homefieldemail.com

Multi-page marketing site for Homefield: exclusive homeowner leads by email for **home services
businesses, home insurance agencies, real estate agents, and real estate investors**. One business per
industry per ZIP. Live at https://homefieldemail.com (GitHub Pages, custom domain via Cloudflare DNS).
Per-lead rates are quoted by industry on the call — no Homefield dollar figures on the site. The earlier
insurance-only version is tagged `insurance-only-final`.

## Pages
- Core: `index` · `industries` · `how-it-works` · `leads` · `compare` · `faq` · `contact`
- Leads by industry (SEO landing pages, Sept 2026): `insurance-leads` (hub) · `home-insurance-leads` ·
  `home-and-auto-insurance-leads` · `mortgage-protection-leads` · `roofing-leads` · `hvac-leads`
- Compare: `insurance-leads-cost` · `everquote-alternatives` · `homefield-vs-everquote` ·
  `homefield-vs-quotewizard` · `everquote-vs-quotewizard`
- Hidden / noindex: `pricing` (unlinked on purpose), `privacy`, `terms`, `refunds`, `404`

Shared: `styles.css` (cache key `?v=nb5`), `script.js` (nav, mobile menu, reveal, current-page highlight,
form → Calendly handoff). Page-scoped styles live in each page's own `<style>` with a per-page prefix
(`hm-` `in-` `hw-` `ld-` `cp-` `fq-` `pr-` `il-` `hi-` `ha-` `ic-` `mp-` `rf-` `hv-` `ea-` `ve-` `vq-` `vs-`).
All internal links are root-absolute (`/faq.html`). Every "Book a call" CTA → https://calendly.com/zatulovebrian/call.

## Build tools (`tools/`) — run from the repo root before every push
| Tool | What it owns |
|---|---|
| `sync_chrome.py` | Copies the `<header>` and `<footer>` from `index.html` into every marketing page (they must stay byte-identical; edit them in `index.html` only). |
| `normalize_head.py` | Rewrites each indexable page's `<head>` (canonical, OG/Twitter, favicons, non-blocking fonts, deferred script); titles/descriptions come from `tools/pages.json` or the page itself. |
| `jsonld.py` | Generates the single JSON-LD `@graph` per page (Organization, founder, WebSite, WebPage, BreadcrumbList, FAQPage from the visible `<details>`, Article/Service where configured). |
| `faq_ld.py` | Prints a FAQPage node from one page's visible FAQ (debugging aid). |
| `make_brand_assets.py` | Rasterizes the favicon set and `assets/logo.png`. |
| `validate.py` | The gate: chrome identity, one `<h1>`, title/description lengths, canonical/OG, JSON-LD validity, duplicate FAQ strings, register blocklist, broken links, sitemap coverage. Push only on `RESULT: PASS`. |

Copy rules (payment-processor and legal register): no spam-tooling vocabulary, no data-broker or list-buying
language, no guarantees, no Homefield per-lead prices, competitor facts attributed to their own pages with an
"as of" month, every sample reply/record marked `<!-- SAMPLE CONTENT — illustrative reply, not a real lead -->`.
See `terms.html` §4 (client is the CAN-SPAM sender) and §9 (phone numbers supplemental, no DNC representation).

SEO/AI-search files: `robots.txt` (everything allowed, sitemap declared), `sitemap.xml` (indexable pages only),
`llms.txt`, IndexNow key file at the root (`<key>.txt`). After each content push: bump `lastmod`, re-run
`tools/jsonld.py`, and POST the URL list to `https://api.indexnow.org/indexnow`.

Local preview: `python3 -m http.server 8811 --bind 127.0.0.1 --directory "$PWD"` → http://127.0.0.1:8811/
