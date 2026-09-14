#!/usr/bin/env python3
"""Usage: python3 tools/faq_ld.py faq.html  → prints a FAQPage JSON node built from the page's own <details> pairs."""
import re, json, html, sys
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
canon = re.search(r'<link rel="canonical" href="([^"]+)"', src).group(1)
items = re.findall(r'<summary>(.*?)</summary>\s*<div class="faq__a">(.*?)</div>', src, re.S)
strip = lambda s: html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s))).strip()
node = {"@type": "FAQPage", "@id": canon + "#faq",
        "mainEntity": [{"@type": "Question", "name": strip(q),
                        "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in items]}
print(json.dumps(node, ensure_ascii=False, indent=2))
