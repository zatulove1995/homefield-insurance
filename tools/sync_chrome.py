#!/usr/bin/env python3
"""Copy the <header> and <footer> blocks from index.html into every marketing page so they are
byte-identical. Legal pages (slim header, no footer) are skipped. Run from the repo root."""
import io, re, glob
SKIP = {'privacy.html', 'terms.html', 'refunds.html'}
idx = io.open('index.html', encoding='utf-8').read()
nav = re.search(r'<header[\s>].*?</header>', idx, re.S).group(0)
foot = re.search(r'<footer[\s>].*?</footer>', idx, re.S).group(0)
for f in sorted(glob.glob('*.html')):
    if f in SKIP or f == 'index.html': continue
    h = io.open(f, encoding='utf-8').read()
    n = re.sub(r'<header[\s>].*?</header>', lambda m: nav, h, count=1, flags=re.S)
    n = re.sub(r'<footer[\s>].*?</footer>', lambda m: foot, n, count=1, flags=re.S)
    if '<footer' not in n: print(f'{f}: WARNING no footer'); 
    if n != h:
        io.open(f, 'w', encoding='utf-8').write(n); print(f'{f}: synced')
    else:
        print(f'{f}: already identical')
