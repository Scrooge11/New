"""Generates the static pages for the JS Contracting & Electrical Services site.
Plain HTML output, no build step needed to edit the result. Run: python3 gen_site.py <repo>
"""
import sys, os, json

REPO = sys.argv[1]

# ---- Business facts. TODO placeholders are listed in README.md ----
NAME = "JS Contracting &amp; Electrical Services"
NAME_PLAIN = "JS Contracting & Electrical Services"
SHORT = "JS Contracting"
PHONE = "(000) 000-0000"          # TODO
PHONE_TEL = "+10000000000"        # TODO
EMAIL = "office@yourdomain.com"   # TODO
TOWN = "Your Town, ST"            # TODO
LICENSE = "Lic. #00000000"        # TODO
SITE_URL = "https://www.yourdomain.com"  # TODO
HOURS = [("Mon to Fri", "7:00 am to 5:00 pm"), ("Saturday", "By appointment"), ("Sunday", "Closed")]
TAGLINE = "Residential and commercial electrical, plus the contracting work around it."

ICON = {
 'check': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
 'phone': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
 'menu': '<svg class="icon-open" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg><svg class="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>',
 'panel': '<svg class="service-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 7h8M8 12h8M8 17h5"/></svg>',
 'plug': '<svg class="service-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 2v6M15 2v6M7 8h10v3a5 5 0 0 1-10 0V8zM12 16v6"/></svg>',
 'generator': '<svg class="service-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="8" width="18" height="10" rx="2"/><path d="M7 8V5h4v3M3 13h18M16 21v-3M8 21v-3"/></svg>',
 'bulb': '<svg class="service-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg>',
 'bolt': '<svg class="service-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"/></svg>',
 'house': '<svg class="service-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 11 12 3l9 8M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></svg>',
 'crew': '<svg class="why-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/></svg>',
 'badge': '<svg class="why-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5l-8-3z"/><path d="m9 12 2 2 4-4"/></svg>',
 'doc': '<svg class="why-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h6"/></svg>',
 'stamp': '<svg class="why-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m8.5 12.5 2.5 2.5 5-5"/></svg>',
}

def ld_json(extra=None):
    data = {
        "@context": "https://schema.org",
        "@type": "Electrician",
        "name": NAME_PLAIN,
        "url": SITE_URL + "/",
        "logo": SITE_URL + "/assets/logo/js-logo-primary.svg",
        "image": SITE_URL + "/assets/og-image.png",
        "telephone": PHONE_TEL,
        "email": EMAIL,
        "description": TAGLINE,
        "areaServed": TOWN,
        "address": {"@type": "PostalAddress", "addressLocality": TOWN},
        "priceRange": "$$",
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "07:00", "closes": "17:00"}
        ],
    }
    if extra: data.update(extra)
    return json.dumps(data, indent=2)

def head(title, desc, path, og_type="website"):
    full = f"{title} | {NAME_PLAIN}" if title else NAME_PLAIN
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE_URL}/{path}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{full}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE_URL}/{path}">
<meta property="og:image" content="{SITE_URL}/assets/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B1F3F">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira:wght@600;700;800&family=Barlow:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="css/styles.css">
<script type="application/ld+json">
{ld_json()}
</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
'''

def header(active):
    def li(href, label, key):
        cls = ' class="is-active" aria-current="page"' if key == active else ''
        return f'<li><a href="{href}"{cls}>{label}</a></li>'
    return f'''<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html" aria-label="{NAME_PLAIN} home">
      <img src="assets/logo/js-logo-horizontal.svg" alt="{NAME_PLAIN}" width="1280" height="380">
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">{ICON['menu']}</button>
    <nav class="site-nav" id="site-nav" aria-label="Main">
      <ul>
        {li('index.html', 'Home', 'home')}
        {li('services.html', 'Services', 'services')}
        {li('about.html', 'About', 'about')}
        {li('contact.html', 'Contact', 'contact')}
      </ul>
    </nav>
    <a class="btn btn-primary header-cta" href="tel:{PHONE_TEL}">{ICON['phone']}<span class="cta-long">Call {PHONE}</span><span class="cta-short">Call</span></a>
  </div>
</header>
<main id="main">
'''

def cta_strip(h, p):
    return f'''<section class="cta-strip" aria-label="Call now">
  <div class="wrap cta-inner">
    <div>
      <h2>{h}</h2>
      <p>{p}</p>
    </div>
    <div class="btn-row">
      <a class="btn btn-primary btn-lg" href="tel:{PHONE_TEL}">{ICON['phone']}Call {PHONE}</a>
      <a class="btn btn-outline-light btn-lg" href="contact.html">Request a quote</a>
    </div>
  </div>
</section>
'''

def footer():
    return f'''</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="assets/logo/js-logo-horizontal-white.svg" alt="{NAME_PLAIN}" width="1280" height="380">
        <p>{TAGLINE} Based in {TOWN}.</p>
      </div>
      <div class="footer-col">
        <h4>Contact</h4>
        <ul>
          <li><a href="tel:{PHONE_TEL}">{PHONE}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>{TOWN}</li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Pages</h4>
        <ul>
          <li><a href="services.html">Services</a></li>
          <li><a href="about.html">About</a></li>
          <li><a href="contact.html">Get a quote</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; <span data-year>2026</span> {NAME}. All rights reserved.</p>
      <p>{LICENSE} &middot; Licensed and insured</p>
    </div>
  </div>
</footer>
<script src="js/main.js"></script>
</body>
</html>
'''

# ---------------------------------------------------------------------------
SERVICES = [
    ('panel', '100A to 200A', 'Panel upgrades &amp; service changes',
     'Replace fuse boxes and undersized panels, add capacity for new loads, and clear up double-taps, missing grounds, and other code corrections. Utility coordination, permit, and inspection included.'),
    ('plug', 'Level 2 &middot; 40 to 60A', 'EV charger installation',
     'A dedicated circuit and a NEMA 14-50 outlet or hardwired charger in your garage or driveway. We run a load calculation first so the panel can handle it.'),
    ('generator', 'Portable inlet or standby', 'Generators &amp; transfer switches',
     'Interlock kits and inlets for portable generators, or automatic transfer switches for standby units, so the essentials stay on when the grid does not.'),
    ('bulb', 'Recessed &middot; exterior &middot; dimmers', 'Lighting &amp; ceiling fans',
     'Recessed and under-cabinet lighting, exterior and landscape fixtures, fan installs with proper bracing, and dimmers that actually match the bulbs.'),
    ('bolt', 'Same-week scheduling', 'Troubleshooting &amp; repairs',
     'Tripping breakers, dead outlets, flickering lights, buzzing at the panel. We find the cause, fix it, and tell you what we found.'),
    ('house', 'Kitchens &middot; baths &middot; basements', 'Remodels &amp; additions',
     'New circuits, relocated outlets, GFCI and AFCI protection, and the framing, drywall, and finish work around it. One contractor, one schedule.'),
]

def service_cards():
    out = []
    for icon, spec, h, p in SERVICES:
        out.append(f'''      <article class="service-card">
        {ICON[icon]}
        <span class="spec">{spec}</span>
        <h3>{h}</h3>
        <p>{p}</p>
      </article>''')
    return '\n'.join(out)

INDEX = head("", "Licensed electrician and general contractor. Panel upgrades, EV chargers, generators, lighting, troubleshooting, and remodels. Owner on every job, written quotes before work starts.", "") + header('home') + f'''
<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <p class="eyebrow">Licensed electrician + general contractor</p>
      <h1>Electrical work done right, by the person who answers the phone.</h1>
      <p class="lede">{NAME} handles residential and light-commercial electrical, and the remodel work that goes with it. The owner is on every job, and you get a written quote before anything starts.</p>
      <div class="btn-row">
        <a class="btn btn-primary btn-lg" href="contact.html">Get a free quote</a>
        <a class="btn btn-outline-light btn-lg" href="tel:{PHONE_TEL}">{ICON['phone']}Call {PHONE}</a>
      </div>
    </div>
    <div class="hero-art">
      <img src="assets/logo/js-mark-reverse.svg" alt="" width="800" height="520" fetchpriority="high">
    </div>
  </div>
</section>

<div class="trust-bar">
  <div class="wrap">
    <ul class="trust-list">
      <li>{ICON['check']}Licensed &amp; insured</li>
      <li>{ICON['check']}Owner on every job</li>
      <li>{ICON['check']}Written quotes, no surprises</li>
      <li>{ICON['check']}Permits &amp; inspections handled</li>
    </ul>
  </div>
</div>

<section class="section" id="services">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">What we do</p>
      <h2>Electrical and contracting, under one roof.</h2>
      <p>From a single outlet to a full panel swap or a finished basement, one crew handles the whole job.</p>
    </div>
    <div class="services-grid">
{service_cards()}
    </div>
    <p class="section-foot"><a class="text-link" href="services.html">See all services</a></p>
  </div>
</section>

<section class="section section-alt" id="why">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Why JS</p>
      <h2>Small company. Straight answers.</h2>
    </div>
    <div class="why-grid">
      <div class="why-item">
        {ICON['crew']}
        <h3>One call, one crew</h3>
        <p>Electrical and general contracting from the same team means no waiting on a second trade, and no finger-pointing when something needs to change.</p>
      </div>
      <div class="why-item">
        {ICON['badge']}
        <h3>Owner on every job</h3>
        <p>You talk to the person doing the work, not a dispatcher. Same face at the estimate, the install, and the walkthrough.</p>
      </div>
      <div class="why-item">
        {ICON['doc']}
        <h3>Priced up front, in writing</h3>
        <p>You get a clear scope and a number before we start. If something changes, you hear about it before it costs you anything.</p>
      </div>
      <div class="why-item">
        {ICON['stamp']}
        <h3>Permitted, inspected, warrantied</h3>
        <p>Every job is permitted where required, inspected, and backed by our workmanship warranty.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section-dark" id="process">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">How a job goes</p>
      <h2>Four steps, no runaround.</h2>
    </div>
    <ol class="process">
      <li><h3>Call or send the form</h3><p>Tell us what is going on. For repairs, we can usually give you a ballpark on the phone.</p></li>
      <li><h3>Site visit and written quote</h3><p>We look at the panel, the run, and the finish work, then send a fixed quote with scope and timeline.</p></li>
      <li><h3>Work, permit, inspection</h3><p>We pull the permit, do the work, and meet the inspector. You do not have to be the go-between.</p></li>
      <li><h3>Walkthrough and cleanup</h3><p>We show you what was done, label the panel, and leave the space cleaner than we found it.</p></li>
    </ol>
  </div>
</section>

<section class="section" id="area">
  <div class="wrap area-inner">
    <div>
      <p class="eyebrow">Service area</p>
      <h2>Serving {TOWN} and the surrounding area.</h2>
      <p>Based in {TOWN}. We travel about 30 miles for most jobs, and farther for larger projects. Not sure if you are in range? Call and ask.</p>
      <p><a class="text-link" href="contact.html">Request a quote</a></p>
    </div>
    <div class="hours-card">
      <h3>Hours</h3>
      <dl>
        {''.join(f'<dt>{d}</dt><dd>{h}</dd>' for d, h in HOURS)}
      </dl>
      <p class="note">After-hours emergency? Call <a href="tel:{PHONE_TEL}">{PHONE}</a> and leave a message. We return emergency calls first.</p>
    </div>
  </div>
</section>

''' + cta_strip("Breaker keeps tripping? Burning smell at the panel?", "Those are the calls to make today, not next week.") + footer()

# ---------------------------------------------------------------------------
def checklist(items):
    return '<ul class="checklist">\n' + '\n'.join(f'  <li>{i}</li>' for i in items) + '\n</ul>'

SERVICES_PAGE = head("Services", "Residential and commercial electrical services plus remodels and additions: panel upgrades, EV chargers, generators, lighting, rewiring, troubleshooting, and finish work.", "services.html") + header('services') + f'''
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Services</p>
    <h1>What we do</h1>
    <p>Residential, light-commercial, and the contracting work that goes with it. If it is not on the list, ask. It probably is.</p>
  </div>
</section>

<section class="service-section" id="residential">
  <div class="wrap">
    <div class="section-head">
      <h2>Residential electrical</h2>
      <p>Most of our work is in homes: upgrades, repairs, and the new circuits that modern living keeps adding.</p>
    </div>
    {checklist([
      'Panel upgrades and service changes, 100A to 200A, meter and main combos',
      'Whole-house rewiring and knob-and-tube or aluminum wiring replacement',
      'New circuits for ranges, dryers, hot tubs, mini-splits, and workshops',
      'EV charger circuits, NEMA 14-50 outlets, and hardwired chargers',
      'Generator inlets, interlock kits, and automatic transfer switches',
      'Recessed, under-cabinet, and exterior lighting',
      'Ceiling fans and bathroom exhaust fans',
      'Outlets, switches, dimmers, and smart controls',
      'GFCI and AFCI protection and code corrections',
      'Hardwired, interconnected smoke and CO detectors',
      'Troubleshooting: tripping breakers, dead circuits, flickering lights',
      'Pre-sale and pre-purchase electrical inspections',
    ])}
  </div>
</section>

<section class="service-section" id="commercial">
  <div class="wrap">
    <div class="section-head">
      <h2>Commercial &amp; light industrial</h2>
      <p>Offices, shops, restaurants, and small warehouses. We schedule around your hours so you stay open.</p>
    </div>
    {checklist([
      'Tenant fit-outs and office build-outs',
      'Service upgrades and subpanels',
      'LED lighting retrofits and lighting controls',
      'Dedicated equipment circuits, single- and three-phase',
      'Exit and emergency lighting',
      'Parking lot and exterior lighting',
      'Panel maintenance and troubleshooting',
      'Data, low-voltage, and EV charging for fleets',
    ])}
  </div>
</section>

<section class="service-section" id="contracting">
  <div class="wrap">
    <div class="section-head">
      <h2>Contracting &amp; remodels</h2>
      <p>Electrical work usually means opening walls. We close them too, so you are not lining up a second contractor for the patching, trim, and paint-ready finish.</p>
    </div>
    {checklist([
      'Kitchen and bathroom remodels',
      'Basement finishing',
      'Additions and garage conversions',
      'Framing, drywall, and patching after electrical work',
      'Trim, doors, and finish carpentry',
      'Permitting and project management for combined jobs',
    ])}
  </div>
</section>

<section class="section section-alt" id="typical">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">At a glance</p>
      <h2>Common jobs and what they involve</h2>
      <p>Typical scope and time on site for a standard home. Your written quote will have the actual schedule for your job.</p>
    </div>
    <div class="table-wrap">
      <table class="spec-table">
        <thead><tr><th scope="col">Job</th><th scope="col">What is included</th><th scope="col">Typical time on site</th></tr></thead>
        <tbody>
          <tr><td>200-amp panel upgrade</td><td>New panel and breakers, grounding and bonding, utility coordination, permit and inspection</td><td>1 day</td></tr>
          <tr><td>Level 2 EV charger</td><td>Load calculation, dedicated 40 to 60A circuit, NEMA 14-50 outlet or hardwired unit</td><td>Half day</td></tr>
          <tr><td>Standby generator</td><td>Pad, transfer switch, wiring to the panel, gas contractor coordination, inspection</td><td>1 to 2 days</td></tr>
          <tr><td>Recessed lighting, 6 to 8 fixtures</td><td>Layout, wiring, dimmers, drywall patching, paint-ready finish</td><td>1 day</td></tr>
          <tr><td>Whole-house rewire</td><td>Room-by-room replacement of old wiring, new devices, patching included</td><td>3 to 7 days</td></tr>
          <tr><td>Basement finish</td><td>Framing, electrical, insulation, drywall, trim, lighting, egress review</td><td>3 to 6 weeks</td></tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">Times assume normal access and no surprises behind the walls. If we find something, you hear about it before we touch it.</p>
  </div>
</section>

''' + cta_strip("Not sure which one you need?", "Describe the problem and we will point you the right way. No charge for the conversation.") + footer()

# ---------------------------------------------------------------------------
ABOUT = head("About", "JS Contracting & Electrical Services is an owner-operated electrical and contracting company. Licensed, insured, and built on years in the trade.", "about.html") + header('about') + f'''
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">About</p>
    <h1>A small company built on years in the trade.</h1>
    <p>Owner-operated on purpose. Fewer jobs at a time, more attention on each one.</p>
  </div>
</section>

<section class="section">
  <div class="wrap about-grid">
    <div class="prose">
      <p>{NAME} is owner-operated. After years running crews and large projects, <strong>[Owner name]</strong> started JS to get back to what he likes best: doing the work himself, for people he will see again around town.</p>
      <p>That means a smaller crew, a direct line to the person responsible for your job, and the same face at the estimate, the install, and the walkthrough.</p>
      <p>We do residential and light-commercial electrical, and we handle the remodel work around it so you are not coordinating three contractors for one project. Every job is quoted in writing, permitted where required, and inspected.</p>
      <p><a class="text-link" href="contact.html">Get in touch</a></p>
    </div>
    <aside class="cred-card" aria-label="Credentials">
      <h3>Credentials</h3>
      <ul>
        <li>Master electrician, {LICENSE}</li>
        <li>General contractor registration #00000000</li>
        <li>General liability insured and bonded</li>
        <li>20+ years in the electrical trade</li>
        <li>Manufacturer-trained on EV chargers and standby generators</li>
      </ul>
    </aside>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">How we work</p>
      <h2>Three things you can hold us to.</h2>
    </div>
    <div class="values-grid">
      <div><h3>Safe first</h3><p>Lockout, testing, and proper grounding on every job. We do not rush live work, and we do not leave a panel we would not put in our own house.</p></div>
      <div><h3>Done once, done right</h3><p>Code-compliant and inspected, with the boxes labeled and the wall closed up. You should not need to call us back for the same thing.</p></div>
      <div><h3>Say it, then do it</h3><p>A written scope, a real schedule, and a phone call the moment anything changes. No surprise line items.</p></div>
    </div>
  </div>
</section>

''' + cta_strip("Have a project in mind?", "Tell us what you are planning and we will tell you what it takes.") + footer()

# ---------------------------------------------------------------------------
CONTACT = head("Get a quote", "Request a quote from JS Contracting & Electrical Services. Call, text, or send the form. We reply within one business day.", "contact.html") + header('contact') + f'''
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Contact</p>
    <h1>Get a quote</h1>
    <p>Tell us about the job. We reply within one business day, usually the same day.</p>
  </div>
</section>

<section class="section">
  <div class="wrap contact-grid">
    <form class="quote-form" name="quote" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field" data-fallback="Call or text {PHONE}, or email {EMAIL}, and we will take it from there." novalidate>
      <input type="hidden" name="form-name" value="quote">
      <p class="visually-hidden" aria-hidden="true"><label>Leave this field empty: <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
      <div class="field-row">
        <div class="field">
          <label for="q-name">Name</label>
          <input id="q-name" name="name" type="text" autocomplete="name" required>
        </div>
        <div class="field">
          <label for="q-phone">Phone</label>
          <input id="q-phone" name="phone" type="tel" autocomplete="tel" required>
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label for="q-email">Email <span class="optional">(optional)</span></label>
          <input id="q-email" name="email" type="email" autocomplete="email">
        </div>
        <div class="field">
          <label for="q-town">Address or town</label>
          <input id="q-town" name="town" type="text" autocomplete="street-address" placeholder="{TOWN}">
        </div>
      </div>
      <div class="field">
        <label for="q-type">Type of work</label>
        <select id="q-type" name="type">
          <option value="Repair or troubleshooting">Repair or troubleshooting</option>
          <option value="Panel upgrade">Panel upgrade or service change</option>
          <option value="EV charger">EV charger</option>
          <option value="Generator">Generator or transfer switch</option>
          <option value="Lighting or fans">Lighting or fans</option>
          <option value="Remodel or addition">Remodel or addition</option>
          <option value="Commercial">Commercial</option>
          <option value="Other">Something else</option>
        </select>
      </div>
      <div class="field">
        <label for="q-details">Describe the job</label>
        <textarea id="q-details" name="details" required placeholder="What is happening, where, and when you need it done. Photos of the panel help; you can text them to us after you submit."></textarea>
      </div>
      <fieldset class="field" style="border:0;padding:0;margin:0">
        <legend style="font-weight:600;color:var(--navy);padding:0;margin-bottom:.35rem">Best way to reach you</legend>
        <div class="radio-row">
          <label><input type="radio" name="contact-pref" value="Call" checked> Call</label>
          <label><input type="radio" name="contact-pref" value="Text"> Text</label>
          <label><input type="radio" name="contact-pref" value="Email"> Email</label>
        </div>
      </fieldset>
      <div class="form-status" role="status" aria-live="polite"></div>
      <div>
        <button class="btn btn-primary btn-lg" type="submit">Send request</button>
      </div>
      <p class="form-note">No mailing lists and no sales calls. We only use this to reply about your job.</p>
    </form>

    <aside class="contact-aside">
      <div class="contact-card">
        <div>
          <p class="label">Call or text</p>
          <a class="big" href="tel:{PHONE_TEL}">{PHONE}</a>
        </div>
        <div>
          <p class="label">Email</p>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
        </div>
        <div>
          <p class="label">Hours</p>
          <p>{'<br>'.join(f'{d}: {h}' for d, h in HOURS)}</p>
        </div>
        <div>
          <p class="label">Service area</p>
          <p>{TOWN} and about 30 miles around it.</p>
        </div>
        <div class="emergency">
          <p class="label">Emergency?</p>
          <p>Burning smell, sparks, or a hot panel: shut off the main if you can reach it safely, then call us. If there is smoke or fire, call 911 first.</p>
        </div>
      </div>
    </aside>
  </div>
</section>
''' + footer()

# ---------------------------------------------------------------------------
NOTFOUND = head("Page not found", "That page is not here.", "404.html") + header('') + f'''
<section class="notfound">
  <div class="wrap">
    <p class="code">404</p>
    <h1>This circuit is open.</h1>
    <p class="lede">The page you are looking for is not here. It may have moved, or the link may be old.</p>
    <div class="btn-row">
      <a class="btn btn-navy" href="index.html">Back to home</a>
      <a class="btn btn-primary" href="contact.html">Get a quote</a>
    </div>
  </div>
</section>
''' + footer()

pages = {'index.html': INDEX, 'services.html': SERVICES_PAGE, 'about.html': ABOUT, 'contact.html': CONTACT, '404.html': NOTFOUND}
for name, html in pages.items():
    with open(os.path.join(REPO, name), 'w') as f:
        f.write(html)
    print('wrote', name, len(html), 'bytes')
