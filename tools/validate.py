#!/usr/bin/env python3
"""Build gate for homefield-insurance (brief A.9 / G.1). Run from the repo root; exit 1 on any ERROR.
Checks: header+footer byte-identical across every marketing page (legal pages excluded); exactly one <h1>;
no <h5>; title ≤60 and description ≤155 on indexable pages (ERROR); canonical/og:url/og:image/twitter on
indexable pages and none of canonical on noindex pages; no relative asset/page links; JSON-LD parses and is
exactly one block on indexable pages; dateModified only where a visible "Last reviewed" line exists; duplicate
FAQ <summary> strings across indexable pages; Stripe/register blocklist with the two documented exemptions;
every internal href resolves to a file; sitemap lists exactly the indexable pages; robots/llms/404 present;
sample markers wherever a .reply/.record/.hm-mail/.hw-mail block appears."""
import re, sys, json, os, glob, io, html as htmlmod

LEGAL = {'privacy.html', 'terms.html', 'refunds.html'}
NOINDEX = LEGAL | {'pricing.html', '404.html'}
SITE = 'https://homefieldemail.com/'
BLOCKLIST = [r'\bcold[- ](email|outreach|call)', r'\bwarm(ed|ing|-?up)\b', r'pre-?warmed', r'inbox rotation',
             r'(?<!CAN-)\bspam\b', r'deliverability hack', r'\bbypass', r'email[- ]append', r'\bappend(ed|ing)?\b',
             r'matched to verified', r'verified emails?', r'(?<!to )data brokers?', r'\bbuy(ing)? lists?', r'purchase(d)? lists?',
             r'\bscraped?\b', r'skip-trac', r'get rich', r'\bguarantee', r'\bincome\b', r'4[–-]8\b', r'seven competitors', r'\[[A-Z ]{3,}\]']

def read(p): return io.open(p, encoding='utf-8').read()
def block(h, tag):
    m = re.search(r'<%s[\s>].*?</%s>' % (tag, tag), h, re.S); return m.group(0) if m else None
def visible(h):
    t = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', '', h, flags=re.S)
    return htmlmod.unescape(re.sub(r'<[^>]+>', ' ', t))

pages = sorted(glob.glob('*.html'))
marketing = [p for p in pages if p not in LEGAL]
indexable = [p for p in pages if p not in NOINDEX]
errors, warns = [], []
ref_nav, ref_foot = block(read('index.html'), 'header'), block(read('index.html'), 'footer')
summaries = {}
for p in marketing:
    h = read(p)
    if block(h, 'header') != ref_nav: errors.append(f'{p}: <header> differs from index.html')
    if block(h, 'footer') != ref_foot: errors.append(f'{p}: <footer> differs from index.html')
for p in pages:
    h = read(p)
    n_h1 = len(re.findall(r'<h1[\s>]', h))
    if n_h1 != 1: errors.append(f'{p}: {n_h1} <h1> tags')
    if '<h5' in h: errors.append(f'{p}: <h5> present (use p.foot__h / h3)')
    t = re.search(r'<title>(.*?)</title>', h, re.S); t = htmlmod.unescape(re.sub(r'\s+', ' ', t.group(1)).strip()) if t else ''
    d = re.search(r'<meta name="description" content="(.*?)"', h, re.S); d = htmlmod.unescape(d.group(1)) if d else ''
    if not t: errors.append(f'{p}: no <title>')
    if not d: errors.append(f'{p}: no meta description')
    if p in indexable:
        if len(t) > 60: errors.append(f'{p}: title {len(t)} chars > 60: {t}')
        if len(d) > 155: errors.append(f'{p}: description {len(d)} chars > 155')
        expect = SITE if p == 'index.html' else SITE + p
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', h)
        if not canon: errors.append(f'{p}: no canonical')
        elif canon.group(1) != expect: errors.append(f'{p}: canonical {canon.group(1)} != {expect}')
        ogu = re.search(r'<meta property="og:url" content="([^"]+)"', h)
        if not ogu or ogu.group(1) != expect: errors.append(f'{p}: og:url missing or wrong')
        for tag in ('og:image', 'twitter:card', 'og:title', 'og:description', 'theme-color'):
            if tag not in h: errors.append(f'{p}: no {tag}')
        if 'noindex' in h: errors.append(f'{p}: noindex on an indexable page')
        lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
        if len(lds) != 1: errors.append(f'{p}: {len(lds)} JSON-LD blocks (need exactly 1)')
        for blk in lds:
            try:
                j = json.loads(blk)
                if '@graph' not in j: errors.append(f'{p}: JSON-LD has no @graph')
                if '"dateModified"' in blk and 'Last reviewed' not in visible(h): errors.append(f'{p}: dateModified without a visible "Last reviewed" line')
                if 'FAQPage' in blk:
                    qs = [q['name'] for n in j['@graph'] if n.get('@type') == 'FAQPage' for q in n['mainEntity']]
                    vis = [htmlmod.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s))).strip() for s in re.findall(r'<summary>(.*?)</summary>', h, re.S)]
                    if qs != vis: errors.append(f'{p}: FAQPage questions differ from visible <summary> strings (rerun tools/faq_ld.py)')
            except Exception as e: errors.append(f'{p}: invalid JSON-LD: {e}')
        for s in re.findall(r'<summary>(.*?)</summary>', h, re.S):
            s = htmlmod.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s))).strip()
            summaries.setdefault(s, []).append(p)
        if '/styles.css?v=nb5' not in h: errors.append(f'{p}: stylesheet is not /styles.css?v=nb5')
    else:
        if 'noindex' not in h: errors.append(f'{p}: should be noindex')
        if 'rel="canonical"' in h: errors.append(f'{p}: canonical on a noindex page')
    if re.search(r'href="(styles\.css|[a-z-]+\.html)|src="script\.js"', h): errors.append(f'{p}: relative asset/page link left')
    text = visible(h)
    if p not in LEGAL:
        for pat in BLOCKLIST:
            for m in re.finditer(pat, text, re.I):
                before = text[max(0, m.start()-60):m.start()]
                word = m.group(0).lower()
                if word.startswith('income') and re.search(r"\b(no|not|none|nothing|never|don't|do not|know)\b", before, re.I): continue
                if word.startswith('guarantee') and re.search(r'[“"]', text[max(0, m.start()-40):m.start()]): continue
                ctx = text[max(0, m.start()-40):m.end()+40].replace('\n', ' ')
                errors.append(f'{p}: blocklist "{m.group(0)}" …{ctx}…')
        for cls in ('reply', 'record', 'hm-mail', 'hw-mail'):
            n_blocks = len(re.findall(r'class="%s[" ]' % cls, h))
            if n_blocks and 'SAMPLE CONTENT — illustrative' not in h: errors.append(f'{p}: .{cls} present without a SAMPLE CONTENT marker')
    for href in set(re.findall(r'href="([^"#?]+)(?:[#?][^"]*)?"', h)):
        if href.startswith(('http', 'mailto:', 'tel:', 'data:')) or href == '': continue
        target = 'index.html' if href == '/' else href.lstrip('/')
        if not os.path.exists(target): errors.append(f'{p}: broken link {href}')
for s, ps in summaries.items():
    if len(ps) > 1: errors.append(f'duplicate FAQ question on {ps}: "{s}"')
if os.path.exists('sitemap.xml'):
    locs = set(re.findall(r'<loc>(.*?)</loc>', read('sitemap.xml')))
    for p in pages:
        u = SITE if p == 'index.html' else SITE + p
        if p in NOINDEX and u in locs: errors.append(f'sitemap includes noindex page {p}')
        if p not in NOINDEX and u not in locs: errors.append(f'sitemap missing {p}')
    for u in locs:
        f = 'index.html' if u == SITE else u.replace(SITE, '')
        if not os.path.exists(f): errors.append(f'sitemap lists missing file {u}')
else: errors.append('no sitemap.xml')
for f in ('robots.txt', 'llms.txt', '404.html', 'favicon.ico', 'assets/og.jpg', 'assets/logo.png'):
    if not os.path.exists(f): errors.append(f'no {f}')
print(f'{len(pages)} pages checked ({len(indexable)} indexable)')
for w in warns: print('WARN ', w)
for e in errors: print('ERROR', e)
print('RESULT:', 'PASS' if not errors else f'FAIL ({len(errors)} errors)')
sys.exit(1 if errors else 0)
