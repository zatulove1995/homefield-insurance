#!/usr/bin/env python3
"""Rewrite the <head> of every indexable page to the canonical block (brief A.2), in order.
Reads tools/pages.json — {"file.html": {"title": ..., "description": ..., "og_type": "website|article"}}.
Keeps each page's JSON-LD <script type="application/ld+json"> and its page-scoped <style> untouched,
in that order, after the canonical block. Skips pricing.html, privacy.html, terms.html, refunds.html,
404.html (their heads are maintained by hand). Idempotent. Run from the repo root."""
import io, re, sys, json, html as htmlmod

SITE = 'https://homefieldemail.com/'
OG_IMAGE = SITE + 'assets/og.jpg'
OG_ALT = 'Homefield — exclusive homeowner leads for home services, insurance, and real estate'
FONTS = 'https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400&display=swap'
SKIP = {'pricing.html', 'privacy.html', 'terms.html', 'refunds.html', '404.html'}

import glob
pages = json.load(open('tools/pages.json', encoding='utf-8'))
def esc(s): return htmlmod.escape(htmlmod.unescape(s), quote=True)
def og_title(t): return re.sub(r'\s+[|—]\s+Homefield$', '', t)

# pages.json entries override; any other indexable page falls back to its own <title>/<meta description>
for f in sorted(glob.glob('*.html')):
    if f in SKIP: continue
    src = io.open(f, encoding='utf-8').read()
    m = re.search(r'<head>(.*?)</head>', src, re.S)
    if not m: print(f'{f}: no <head>', file=sys.stderr); continue
    head = m.group(1)
    meta = pages.get(f)
    if meta is None:
        t = re.search(r'<title>(.*?)</title>', head, re.S); d = re.search(r'<meta name="description" content="(.*?)">', head, re.S)
        if not (t and d): print(f'{f}: not in pages.json and no title/description to fall back on', file=sys.stderr); continue
        meta = {'title': htmlmod.unescape(re.sub(r'\s+', ' ', t.group(1)).strip()), 'description': htmlmod.unescape(d.group(1)),
                'og_type': 'article' if f in ('insurance-leads-cost.html', 'everquote-alternatives.html', 'everquote-vs-quotewizard.html') else 'website'}
    ld = re.findall(r'<script type="application/ld\+json">.*?</script>', head, re.S)
    styles = re.findall(r'<style>.*?</style>', head, re.S)
    if len(ld) > 1: print(f'{f}: WARNING {len(ld)} JSON-LD blocks (brief says one)', file=sys.stderr)
    if len(re.findall(r'<title>', head)) != 1: print(f'{f}: WARNING title count', file=sys.stderr)
    url = SITE if f == 'index.html' else SITE + f
    title, desc = meta['title'], meta['description']
    ogt = meta.get('og_type', 'website')
    if len(htmlmod.unescape(title)) > 60: print(f'{f}: title {len(title)} chars > 60', file=sys.stderr)
    if len(htmlmod.unescape(desc)) > 155: print(f'{f}: description {len(desc)} chars > 155', file=sys.stderr)
    block = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0A0D14">
<meta property="og:site_name" content="Homefield">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="{ogt}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(og_title(title))}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{OG_ALT}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(og_title(title))}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{OG_IMAGE}">
<meta name="twitter:image:alt" content="{OG_ALT}">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/favicon-48.png">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="{FONTS}">
<link href="{FONTS}" rel="stylesheet" media="print" onload="this.media='all'">
<noscript><link href="{FONTS}" rel="stylesheet"></noscript>
<link rel="stylesheet" href="/styles.css?v=nb5">
<script>document.documentElement.className += ' js';</script>
<script src="/script.js" defer></script>
'''
    tail = ''.join(x + '\n' for x in ld) + ''.join(x + '\n' for x in styles)
    new_head = '<head>\n' + block + tail + '</head>'
    out = src[:m.start()] + new_head + src[m.end():]
    if out != src:
        io.open(f, 'w', encoding='utf-8').write(out); print(f'{f}: head normalized')
    else:
        print(f'{f}: unchanged')
