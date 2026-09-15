#!/usr/bin/env python3
"""Generate the single JSON-LD @graph for every indexable page (brief A.4) and write it into <head>
(replacing any existing ld+json block). Entity names, @ids and the founder node are defined ONCE here so
every page agrees. Page config (breadcrumb trail, byline, article, service) is the PAGES table below.
FAQPage nodes are built from each page's visible <details> pairs (same logic as tools/faq_ld.py).
datePublished = first git commit of the file (or today for uncommitted files). Run from the repo root."""
import io, re, json, html, glob, subprocess, datetime, sys

SITE = 'https://homefieldemail.com/'
ORG, FOUNDER, WEBSITE = SITE + '#organization', SITE + '#founder', SITE + '#website'
TODAY = datetime.date.today().isoformat()
DESCRIPTOR = 'Homefield — exclusive homeowner leads for home services, insurance, and real estate.'
SKIP = {'pricing.html', 'privacy.html', 'terms.html', 'refunds.html', '404.html'}

# file: breadcrumb trail (list of (name, url)) after Home; byline (full Person + author); article; extra nodes builder
INS = ('Insurance leads', SITE + 'insurance-leads.html')
CMP = ('Compare', SITE + 'compare.html')
PAGES = {
  'index.html':                        dict(crumbs=[], byline=False),
  'industries.html':                   dict(crumbs=[('Industries', None)], byline=False),
  'how-it-works.html':                 dict(crumbs=[('How it works', None)], byline=True, service='parent'),
  'leads.html':                        dict(crumbs=[('The leads', None)], byline=False),
  'compare.html':                      dict(crumbs=[('Compare', None)], byline=True),
  'faq.html':                          dict(crumbs=[('FAQ', None)], byline=True, faq=True),
  'contact.html':                      dict(crumbs=[('Book a call', None)], byline=False, contact=True),
  'insurance-leads.html':              dict(crumbs=[('Insurance leads', None)], byline=True, service='insurance', faq=True),
  'home-insurance-leads.html':         dict(crumbs=[INS, ('Home insurance leads', None)], byline=True, faq=True),
  'home-and-auto-insurance-leads.html':dict(crumbs=[INS, ('Home and auto insurance leads', None)], byline=True, faq=True),
  'insurance-leads-cost.html':         dict(crumbs=[INS, ('What insurance leads cost', None)], byline=True, article=True, faq=True),
  'mortgage-protection-leads.html':    dict(crumbs=[INS, ('Mortgage protection leads', None)], byline=True, faq=True),
  'roofing-leads.html':                dict(crumbs=[('Roofing leads', None)], byline=True, faq=True),
  'hvac-leads.html':                   dict(crumbs=[('HVAC leads', None)], byline=True, faq=True),
  'everquote-alternatives.html':       dict(crumbs=[CMP, ('EverQuote alternatives', None)], byline=True, article=True, faq=True),
  'homefield-vs-everquote.html':       dict(crumbs=[CMP, ('Homefield vs EverQuote', None)], byline=True, article=True, faq=True),
  'homefield-vs-quotewizard.html':     dict(crumbs=[CMP, ('Homefield vs QuoteWizard', None)], byline=True, article=True, faq=True),
  'everquote-vs-quotewizard.html':     dict(crumbs=[CMP, ('EverQuote vs QuoteWizard', None)], byline=True, article=True, about=['EverQuote, Inc.', 'QuoteWizard.com LLC'], faq=True),
}

ORG_NODE = {
  "@type": "Organization", "@id": ORG, "name": "Homefield", "legalName": "Homefield Growth LLC", "url": SITE,
  "logo": {"@type": "ImageObject", "url": SITE + "assets/logo.png", "width": 512, "height": 512},
  "image": SITE + "assets/og.jpg",
  "description": "Homefield — exclusive homeowner leads for home services, insurance, and real estate. A pay-per-qualified-lead marketing service that emails homeowners in a client's territory, under the client's approved business identity, timed to the moment they are ready, and delivers the homeowners who reply asking for a quote, estimate, valuation or offer. One business per industry per ZIP.",
  "email": "brian@homefieldemail.com",
  "address": {"@type": "PostalAddress", "streetAddress": "14320 Ventura Blvd #1137", "addressLocality": "Los Angeles", "addressRegion": "CA", "postalCode": "91423", "addressCountry": "US"},
  "areaServed": {"@type": "Country", "name": "United States"},
  "founder": {"@id": FOUNDER},
  "knowsAbout": ["Homeowner marketing", "Home insurance renewal timing", "Home services marketing", "Real estate agent marketing", "Real estate investor marketing"],
  "contactPoint": {"@type": "ContactPoint", "contactType": "sales", "email": "brian@homefieldemail.com", "url": SITE + "contact.html", "availableLanguage": "en"},
}
PERSON_MIN = {"@type": "Person", "@id": FOUNDER, "name": "Brian Zatulove", "jobTitle": "Founder", "worksFor": {"@id": ORG}, "url": SITE + "how-it-works.html#byline"}
PERSON_FULL = dict(PERSON_MIN, email="brian@homefieldemail.com",
  description="Founder of Homefield. Previously co-founded Emotive, an SMS-marketing software company, and grew it from $0 to about $30M in revenue with about $70M in venture funding. Forbes 30 Under 30, 2021.",
  award="Forbes 30 Under 30 (2021)")
WEBSITE_NODE = {"@type": "WebSite", "@id": WEBSITE, "url": SITE, "name": "Homefield", "publisher": {"@id": ORG}, "inLanguage": "en-US"}

def strip(s): return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s))).strip()
def first_commit(f):
    try:
        out = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%aI', '--follow', '--', f], capture_output=True, text=True).stdout.strip().split('\n')
        d = [x for x in out if x][-1] if out and out[-1] else ''
        return d or (TODAY + 'T00:00:00-07:00')
    except Exception: return TODAY + 'T00:00:00-07:00'

def service_parent():
    return {"@type": "Service", "@id": SITE + "how-it-works.html#service", "name": "Homefield exclusive homeowner leads",
      "serviceType": "Pay-per-qualified-lead homeowner marketing service",
      "description": "Homefield emails homeowners in a client's locked territory, under the client's approved business identity from dedicated, reputation-managed sending domains, timed to a modeled moment (policy renewal window, roof or system age, just-listed/just-sold, ownership tenure and equity). Homeowners who reply expressing interest are delivered as qualified leads with a full record. One business per industry per ZIP; 100–500 ZIPs per business; about 21 days to first lead.",
      "provider": {"@id": ORG}, "areaServed": {"@type": "Country", "name": "United States"},
      "audience": {"@type": "BusinessAudience", "name": "Home services companies, home insurance agencies, real estate agents, real estate investors"},
      "termsOfService": SITE + "terms.html",
      "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Homefield campaigns by industry", "itemListElement": [
        {"@type": "Offer", "name": "Home services — aging roof and system outreach", "description": "Outreach timed to modeled roof and system age (roof past year 18, furnace or condenser past year 12) for roofing, HVAC, plumbing, solar and remodeling companies. Roofing: https://homefieldemail.com/roofing-leads.html · HVAC: https://homefieldemail.com/hvac-leads.html", "url": SITE + "industries.html#home-services"},
        {"@type": "Offer", "name": "Home insurance agencies — modeled renewal-window outreach", "description": "Email timed 30–45 days before the modeled home-policy renewal, plus a post-storm coverage-review wave within state rules.", "url": SITE + "home-insurance-leads.html", "itemOffered": {"@id": SITE + "insurance-leads.html#service"}},
        {"@type": "Offer", "name": "Real estate agents — just-listed and just-sold neighbor campaigns", "description": "Per-campaign flat rate, invoiced after the campaign runs.", "url": SITE + "industries.html#real-estate-agents"},
        {"@type": "Offer", "name": "Real estate investors — tenure and equity outreach", "description": "Outreach timed to ownership tenure and equity for real estate investors.", "url": SITE + "industries.html#real-estate-investors"},
      ]}}
def service_insurance():
    return {"@type": "Service", "@id": SITE + "insurance-leads.html#service", "name": "Homefield exclusive insurance leads for agents", "category": "Insurance",
      "serviceType": "Pay-per-qualified-lead homeowner marketing service for insurance agencies",
      "description": "Homefield emails homeowners in an insurance agency's locked ZIP codes, under the agency's approved identity, 30\u201345 days before the modeled home-policy renewal, and delivers the homeowners who reply asking for a quote as qualified leads with the full reply thread. One agency per ZIP; 100\u2013500 ZIPs per agency; about 21 days to first lead; billed weekly per qualified lead; no contract.",
      "provider": {"@id": ORG}, "areaServed": {"@type": "Country", "name": "United States"},
      "audience": {"@type": "BusinessAudience", "audienceType": "Independent, captive and multi-line property & casualty insurance agencies that write home insurance"},
      "termsOfService": SITE + "terms.html", "url": SITE + "insurance-leads.html",
      "offers": {"@type": "Offer", "name": "Pay per qualified lead", "description": "Rate set by industry and quoted in writing on a call; steps down above 50 and above 299 qualified leads per calendar month; one-time onboarding fee; no contract.", "url": SITE + "contact.html"}}

for f in sorted(glob.glob('*.html')):
    if f in SKIP: continue
    cfg = PAGES.get(f)
    if cfg is None: print(f'{f}: not in PAGES table — add it', file=sys.stderr); continue
    src = io.open(f, encoding='utf-8').read()
    url = SITE if f == 'index.html' else SITE + f
    title = strip(re.search(r'<title>(.*?)</title>', src, re.S).group(1))
    desc = html.unescape(re.search(r'<meta name="description" content="(.*?)">', src, re.S).group(1))
    has_reviewed = 'Last reviewed' in re.sub(r'<script.*?</script>|<!--.*?-->', '', src, flags=re.S)
    graph = [ORG_NODE, PERSON_FULL if cfg.get('byline') else PERSON_MIN, WEBSITE_NODE]
    page = {"@type": ["WebPage", "ContactPage"] if cfg.get('contact') else "WebPage", "@id": url + '#webpage', "url": url, "name": title, "description": desc,
            "isPartOf": {"@id": WEBSITE}, "about": {"@id": ORG}, "publisher": {"@id": ORG}}
    if cfg.get('byline'): page["author"] = {"@id": FOUNDER}
    page["datePublished"] = first_commit(f)
    if has_reviewed: page["dateModified"] = TODAY + 'T00:00:00-07:00'
    page.update({"inLanguage": "en-US", "primaryImageOfPage": {"@type": "ImageObject", "url": SITE + "assets/og.jpg", "width": 1200, "height": 630}})
    if cfg['crumbs']: page["breadcrumb"] = {"@id": url + '#breadcrumb'}
    graph.append(page)
    if cfg['crumbs']:
        items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE}]
        for i, (name, u) in enumerate(cfg['crumbs'], start=2):
            items.append({"@type": "ListItem", "position": i, "name": name, "item": u or url})
        graph.append({"@type": "BreadcrumbList", "@id": url + '#breadcrumb', "itemListElement": items})
    if cfg.get('article'):
        art = {"@type": "Article", "@id": url + '#article', "headline": re.sub(r'\s+[|—]\s+Homefield$', '', title), "mainEntityOfPage": {"@id": url + '#webpage'},
               "author": {"@id": FOUNDER}, "publisher": {"@id": ORG}, "datePublished": page["datePublished"], "inLanguage": "en-US",
               "image": SITE + "assets/og.jpg"}
        if has_reviewed: art["dateModified"] = page["dateModified"]
        if cfg.get('about'): art["about"] = [{"@type": "Organization", "name": n} for n in cfg['about']]
        graph.append(art)
    if cfg.get('service') == 'parent': graph.append(service_parent())
    if cfg.get('service') == 'insurance': graph.append(service_insurance())
    items = re.findall(r'<summary>(.*?)</summary>\s*<div class="faq__a">(.*?)</div>', src, re.S)
    if items and cfg.get('faq'):
        graph.append({"@type": "FAQPage", "@id": url + '#faq', "mainEntity": [
            {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in items]})
    blob = '<script type="application/ld+json">\n' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1) + '\n</script>'
    if re.search(r'<script type="application/ld\+json">.*?</script>', src, re.S):
        out = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: blob, src, count=1, flags=re.S)
    else:
        # after the deferred script.js tag, before the page <style>
        anchor = '<script src="/script.js" defer></script>\n'
        out = src.replace(anchor, anchor + blob + '\n', 1) if anchor in src else src.replace('</head>', blob + '\n</head>', 1)
    if out != src: io.open(f, 'w', encoding='utf-8').write(out); print(f'{f}: JSON-LD written ({len(graph)} nodes)')
    else: print(f'{f}: unchanged')
