/* Homefield — site behavior
   ------------------------------------------------------------------
   CONFIG: point FORM_ENDPOINT at your Cloudflare Worker / CRM webhook.
   Leave it empty and the form falls back to opening a prefilled email. */

const FORM_ENDPOINT = '';                    // e.g. 'https://homefield-api.<you>.workers.dev/lead'
const FALLBACK_EMAIL = 'hello@homefield.example';
const CALENDLY_URL = 'https://calendly.com/zatulovebrian/call';

/* ── sticky nav: dark over the hero, light once past it ───────────── */
(() => {
  const nav = document.getElementById('nav');
  const hero = document.querySelector('.hero');
  if (!nav || !hero) return;

  const onScroll = () => {
    const past = window.scrollY > hero.offsetHeight - 80;
    nav.classList.toggle('is-solid', past);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
})();

/* ── mobile menu ──────────────────────────────────────────────────── */
(() => {
  const toggle = document.getElementById('navToggle');
  const menu = document.getElementById('mobileNav');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    menu.hidden = open;
  });

  menu.addEventListener('click', (e) => {
    if (e.target.tagName === 'A') {
      toggle.setAttribute('aria-expanded', 'false');
      menu.hidden = true;
    }
  });
})();

/* ── scroll reveal ────────────────────────────────────────────────── */
(() => {
  const targets = document.querySelectorAll('.reveal, .sechead, .cac__card, .step, .tier, .grid-2__text, .grid-2__visual, .faq__item');
  if (!('IntersectionObserver' in window)) {
    targets.forEach((el) => el.classList.add('in'));
    return;
  }

  targets.forEach((el) => el.classList.add('reveal'));

  // Anything already on screen at load shows instantly — the hero must never
  // fade in from blank. Only content the user scrolls to gets animated.
  const above = [];
  targets.forEach((el) => {
    if (el.getBoundingClientRect().top < window.innerHeight) {
      el.classList.add('in', 'no-anim');
      above.push(el);
    }
  });
  requestAnimationFrame(() => above.forEach((el) => el.classList.remove('no-anim')));

  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (!entry.isIntersecting) return;
      const delay = Math.min(i * 70, 280);
      setTimeout(() => entry.target.classList.add('in'), delay);
      io.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

  targets.forEach((el) => io.observe(el));

  // Failsafe: nothing stays hidden longer than a few seconds, whatever happens.
  setTimeout(() => targets.forEach((el) => el.classList.add('in')), 4000);
})();

/* ── territory map: decorative ZIP grid ───────────────────────────── */
(() => {
  const grid = document.querySelector('.map__grid');
  if (!grid) return;

  // Deterministic pattern so the "claimed" cluster looks intentional, not noisy.
  const claimed = new Set([9,10,11,16,17,18,19,23,24,25,26,27,31,32,33,34,38,39,40,41,46,47,48]);
  const dim = new Set([8,15,22,30,37,45,12,20,28,35,42,49]);

  for (let i = 0; i < 56; i++) {
    const cell = document.createElement('i');
    if (claimed.has(i)) cell.className = 'on';
    else if (dim.has(i)) cell.className = 'dim';
    grid.appendChild(cell);
  }
})();

/* ── lead form ────────────────────────────────────────────────────── */
(() => {
  const form = document.getElementById('leadForm');
  const status = document.getElementById('formStatus');
  if (!form || !status) return;

  const setStatus = (msg, kind) => {
    status.textContent = msg;
    status.className = 'form__status' + (kind ? ' ' + kind : '');
  };

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(form).entries());
    const required = ['name', 'agency', 'email'];
    const missing = required.filter((k) => !String(data[k] || '').trim());

    required.forEach((k) => {
      form.elements[k].setAttribute('aria-invalid', String(missing.includes(k)));
    });

    if (missing.length) {
      setStatus('Please fill in your name, business, and work email.', 'err');
      form.elements[missing[0]].focus();
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      form.elements.email.setAttribute('aria-invalid', 'true');
      setStatus('That email address does not look right.', 'err');
      return;
    }

    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    setStatus('Sending…');

    // No backend wired up yet — send them straight to the calendar, with
    // their answers pre-filled into Calendly's name/email/notes fields.
    if (!FORM_ENDPOINT) {
      const notes = [
        data.agency && `Agency: ${data.agency}`,
        data.zips && `ZIPs: ${data.zips}`,
        data.industry && `Industry: ${data.industry}`,
        data.volume && `Leads wanted / mo: ${data.volume}`,
      ].filter(Boolean).join('\n');
      const url = new URL(CALENDLY_URL);
      if (data.name) url.searchParams.set('name', data.name);
      if (data.email) url.searchParams.set('email', data.email);
      if (notes) url.searchParams.set('a1', notes);
      window.open(url.toString(), '_blank', 'noopener');
      setStatus('Opening the calendar — pick a time that works.', 'ok');
      btn.disabled = false;
      return;
    }

    try {
      const res = await fetch(FORM_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, source: 'homefield-site', ts: new Date().toISOString() }),
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      form.reset();
      setStatus("Got it. We'll come back within one business day with your ZIP availability.", 'ok');
    } catch (err) {
      setStatus(`Something went wrong. Email us directly at ${FALLBACK_EMAIL}.`, 'err');
    } finally {
      btn.disabled = false;
    }
  });
})();

/* ── footer year ──────────────────────────────────────────────────── */
document.getElementById('yr').textContent = new Date().getFullYear();


/* ── current page in nav ─────────────────────────────────────────── */
(() => {
  const here = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav__links a, .mobilenav a').forEach((a) => {
    if (a.getAttribute('href') === here) a.classList.add('is-current');
  });
})();
