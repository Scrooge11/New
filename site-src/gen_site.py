"""Generates the static pages for the JEMCO Contracting & Electrical Services site.
Plain HTML output, no build step needed to edit the result. Run: python3 site-src/gen_site.py .
All business facts live in the constants below. Items marked TODO are placeholders.
"""
import sys, os, json

REPO = sys.argv[1]

# ---- Business facts. TODO placeholders are listed in README.md ----
NAME = "JEMCO Contracting &amp; Electrical Services"
NAME_PLAIN = "JEMCO Contracting & Electrical Services"
PHONE = "(000) 000-0000"          # TODO
PHONE_TEL = "+10000000000"        # TODO
EMAIL = "office@jemcoelectric.com"   # TODO confirm once the domain is bought
TOWN = "Westford, MA"             # TODO confirm home base (assumed)
TOWN_SHORT = "Westford"
STATE = "MA"
LICENSE = "Lic. #00000000"        # TODO
HIC = "HIC #000000"               # TODO
SITE_URL = "https://www.jemcoelectric.com"  # TODO confirm once the domain is bought (jemcoelectric.com was available on Oct 18, 2026)
GBP_URL = "https://g.page/r/your-google-business-profile/review"  # TODO Google Business Profile review link
FACEBOOK_URL = ""                 # TODO optional
HOURS = [("Mon to Fri", "7:00 am to 5:00 pm"), ("Saturday", "By appointment"), ("Sunday", "Closed")]
TAGLINE = "Residential and commercial electrical, plus the contracting work around it."
WARRANTY = "2-year workmanship warranty"   # TODO confirm
# Assumed service area. Edit this list and the pages regenerate.
TOWNS = [("Westford", "Home base"), ("Chelmsford", ""), ("Littleton", ""), ("Acton", ""), ("Groton", ""),
         ("Tyngsborough", ""), ("Dunstable", ""), ("Carlisle", ""), ("Boxborough", ""), ("Ayer", ""),
         ("Harvard", ""), ("Lowell", ""), ("Concord", ""), ("Pepperell", ""), ("Billerica", ""), ("Bedford", "")]
TOWN_NAMES = [t for t, _ in TOWNS]
TOWNS_SHORT = ", ".join(TOWN_NAMES[:6]) + " and nearby towns"

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
 'star': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/></svg>',
}

# ---------------------------------------------------------------------------
# Structured data
# ---------------------------------------------------------------------------
def business_ld():
    data = {
        "@context": "https://schema.org",
        "@type": "Electrician",
        "@id": SITE_URL + "/#business",
        "name": NAME_PLAIN,
        "url": SITE_URL + "/",
        "logo": SITE_URL + "/assets/logo/jemco-logo-primary.svg",
        "image": SITE_URL + "/assets/og-image.png",
        "telephone": PHONE_TEL,
        "email": EMAIL,
        "description": TAGLINE,
        "address": {"@type": "PostalAddress", "addressLocality": TOWN_SHORT, "addressRegion": STATE, "addressCountry": "US"},
        "areaServed": [{"@type": "City", "name": f"{t}, {STATE}"} for t in TOWN_NAMES],
        "priceRange": "$$",
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "07:00", "closes": "17:00"}
        ],
        "sameAs": [u for u in [GBP_URL, FACEBOOK_URL] if u],
    }
    return data

def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faqs]}

def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + "/" + p} for i, (n, p) in enumerate(items)]}

def service_ld(sp):
    return {"@context": "https://schema.org", "@type": "Service", "serviceType": sp['service_type'],
            "name": sp['title'], "description": strip_tags(sp['desc']), "url": SITE_URL + "/" + sp['slug'] + ".html",
            "provider": {"@id": SITE_URL + "/#business"},
            "areaServed": [{"@type": "City", "name": f"{t}, {STATE}"} for t in TOWN_NAMES]}

def strip_tags(s):
    import re
    s = re.sub(r'<[^>]+>', '', s)
    return s.replace('&amp;', '&').replace('&middot;', '·').replace('&nbsp;', ' ')

# ---------------------------------------------------------------------------
# Page chrome
# ---------------------------------------------------------------------------
def head(title, desc, path, lds=None):
    full = f"{title} | {NAME_PLAIN}" if title else f"{NAME_PLAIN} | Electrician in {TOWN}"
    lds = [business_ld()] + (lds or [])
    ld = '\n'.join(f'<script type="application/ld+json">\n{json.dumps(d, indent=1)}\n</script>' for d in lds)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{SITE_URL}/{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME_PLAIN}">
<meta property="og:title" content="{full}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE_URL}/{path}">
<meta property="og:image" content="{SITE_URL}/assets/og-image.png">
<meta property="og:image:alt" content="{NAME_PLAIN} logo">
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
{ld}
<!-- Analytics: paste the Google tag (GA4) or Tag Manager snippet here once the property exists. -->
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
'''

NAV = [('index.html', 'Home', 'home'), ('services.html', 'Services', 'services'), ('service-area.html', 'Service area', 'area'),
       ('about.html', 'About', 'about'), ('contact.html', 'Contact', 'contact')]

def header(active):
    def li(h, l, k):
        attr = ' class="is-active" aria-current="page"' if k == active else ''
        return f'<li><a href="{h}"{attr}>{l}</a></li>'
    items = ''.join(li(h, l, k) for h, l, k in NAV)
    return f'''<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html" aria-label="{NAME_PLAIN} home">
      <img src="assets/logo/jemco-logo-horizontal-ondark.svg" alt="{NAME_PLAIN}" width="1826" height="380">
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">{ICON['menu']}</button>
    <nav class="site-nav" id="site-nav" aria-label="Main">
      <ul>{items}</ul>
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
    svc = ''.join(f'<li><a href="{s["slug"]}.html">{s["nav"]}</a></li>' for s in SERVICE_PAGES)
    return f'''</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid footer-grid-4">
      <div class="footer-brand">
        <img src="assets/logo/jemco-logo-horizontal-white.svg" alt="{NAME_PLAIN}" width="1826" height="380" loading="lazy">
        <p>{TAGLINE} Based in {TOWN}, serving {TOWNS_SHORT}.</p>
      </div>
      <div class="footer-col">
        <h4>Services</h4>
        <ul>{svc}</ul>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <ul>
          <li><a href="about.html">About</a></li>
          <li><a href="service-area.html">Service area</a></li>
          <li><a href="contact.html">Get a quote</a></li>
          <li><a href="{GBP_URL}" rel="noopener">Reviews on Google</a></li>
          <li><a href="privacy.html">Privacy</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Contact</h4>
        <ul>
          <li><a href="tel:{PHONE_TEL}">{PHONE}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>{TOWN}</li>
          <li>{HOURS[0][0]}: {HOURS[0][1]}</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; <span data-year>2026</span> {NAME}. All rights reserved.</p>
      <p>MA Master Electrician {LICENSE} &middot; {HIC} &middot; Licensed and insured</p>
    </div>
  </div>
</footer>
<script src="js/main.js"></script>
</body>
</html>
'''

def checklist(items):
    return '<ul class="checklist">\n' + '\n'.join(f'  <li>{i}</li>' for i in items) + '\n</ul>'

def faq_block(faqs, heading="Questions we get a lot"):
    items = '\n'.join(f'''      <details>
        <summary>{q}</summary>
        <div class="faq-body"><p>{a}</p></div>
      </details>''' for q, a in faqs)
    return f'''<section class="section section-alt" id="faq">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">FAQ</p>
      <h2>{heading}</h2>
    </div>
    <div class="faq">
{items}
    </div>
  </div>
</section>
'''

# ---------------------------------------------------------------------------
# Service pages (data)
# ---------------------------------------------------------------------------
SERVICE_PAGES = [
 dict(slug='panel-upgrades', nav='Panel upgrades', icon='panel', spec='100A to 200A', card='Panel upgrades &amp; service changes',
      card_p='Replace fuse boxes and undersized panels, add capacity for new loads, and clear up double-taps, missing grounds, and other code corrections. Utility coordination, permit, and inspection included.',
      service_type='Electrical panel upgrade', title='Electrical Panel Upgrades',
      h1=f'Electrical panel upgrades in {TOWN_SHORT} and nearby towns',
      desc=f'200-amp electrical panel upgrades, fuse box replacement and service changes in {TOWN_SHORT}, MA and nearby towns. Licensed master electrician. Permit and inspection included.',
      intro='A 100-amp panel was fine in 1985. Add an EV charger, a heat pump and an induction range and it is not. We replace fuse boxes and undersized panels with a new 200-amp service, bring grounding and bonding up to code, and handle the utility, the permit and the inspection.',
      includes=['New 200-amp panel with copper bus and arc-fault and ground-fault breakers where code requires them',
                'Meter socket, mast and service entrance cable replaced if undersized or damaged',
                'Grounding electrode system and bonding (water, gas, rebar) brought to current code',
                'Whole-house surge protection at the panel',
                'Every circuit traced, labeled and photographed for your records',
                'Utility disconnect and reconnect, permit and inspection',
                'Drywall patched where the old panel came out'],
      price=('$3,000 to $6,000', 'for most single-family homes. Higher if the mast, meter or grounding needs replacement or the panel moves. Fixed written quote after a site visit.'),
      signs_h='Signs it is time',
      signs=['Fuses instead of breakers, or a Federal Pacific, Zinsco or Sylvania panel',
             'Breakers that trip when the dryer and the microwave run together',
             'No empty slots for new circuits',
             'Adding an EV charger, heat pump, hot tub or standby generator',
             'Your insurer or a home inspector flagged the panel',
             'Scorch marks, buzzing or warmth at the panel (call today, not next week)'],
      faqs=[('How long does a panel upgrade take?', 'Most are one day on site. Power is off for four to eight hours while we swap the panel, and the inspection is scheduled within a few days.'),
            ('Do I need a permit for a panel upgrade in Massachusetts?', 'Yes. A service change requires an electrical permit and an inspection by the town wiring inspector. We pull the permit, schedule the inspection and meet the inspector.'),
            ('Will a new panel lower my insurance?', 'Many insurers decline or surcharge homes with fuse boxes or known-defective panels. A new panel often removes the surcharge; ask your agent before and after.'),
            ('Can you upgrade to 200 amps if the utility service is 100 amps?', 'Usually yes. We confirm the service drop with the utility and replace the meter socket and service cable as part of the job.')],
      related=['ev-charger-installation', 'generator-installation', 'electrical-repairs']),
 dict(slug='ev-charger-installation', nav='EV chargers', icon='plug', spec='Level 2 &middot; 40 to 60A', card='EV charger installation',
      card_p='A dedicated circuit and a NEMA 14-50 outlet or hardwired charger in your garage or driveway. We run a load calculation first so the panel can handle it.',
      service_type='EV charger installation', title='EV Charger Installation',
      h1=f'EV charger installation in {TOWN_SHORT} and nearby towns',
      desc=f'Level 2 home EV charger installation in {TOWN_SHORT}, MA and nearby towns. Dedicated 40 to 60 amp circuits, NEMA 14-50 outlets and hardwired chargers, permit included, rebate paperwork handled.',
      intro='A Level 2 charger adds 25 to 40 miles of range an hour instead of four. We run the dedicated circuit, install the outlet or hardwire the charger you chose, and make sure your panel can carry it before we quote.',
      includes=['Load calculation on your existing panel, the step most installers skip',
                'Dedicated 40, 50 or 60-amp circuit on a breaker sized to the charger',
                'NEMA 14-50 outlet or hardwired charger (Tesla Wall Connector, ChargePoint, Emporia, Wallbox, Grizzl-E and others)',
                'Outdoor-rated installation for driveways, with in-use covers and proper conduit',
                'Load-management chargers when the panel is close to full',
                'Permit and inspection',
                'Paperwork for utility rebates and the federal tax credit where they apply'],
      price=('$900 to $2,500', 'installed, depending on the distance from the panel and whether the run goes through finished space. Charger hardware is extra unless you ask us to supply it. Utility rebates may cover part of the wiring.'),
      signs_h='Good to know',
      signs=['Massachusetts utilities have offered rebates on home charger wiring; we confirm what applies to your address before we quote',
             'A full or 100-amp panel often still works with a load-managed charger; sometimes it needs an upgrade, and we tell you which before you commit',
             'Two EVs? One 60-amp circuit with two power-sharing chargers is cheaper than two circuits',
             'Hardwired is required for most 48-amp chargers; a 14-50 outlet lets you take a plug-in charger with you when you move'],
      faqs=[('Outlet or hardwired charger?', 'Hardwired is required for most 48-amp chargers and is better outdoors. A NEMA 14-50 outlet is the flexible option for a plug-in charger up to 40 amps. We size the circuit to the charger either way.'),
            ('How long does the installation take?', 'Half a day for most garages. Driveways with a long underground run take a day.'),
            ('Do I need a permit to install an EV charger in Massachusetts?', 'Yes. Any new circuit needs an electrical permit and an inspection. It is included in our price.'),
            ('Can my 100-amp panel handle an EV charger?', 'Often yes, with a load calculation and the right breaker. If not, a load-managed charger or a panel upgrade solves it, and we price both options.')],
      related=['panel-upgrades', 'generator-installation', 'lighting-installation']),
 dict(slug='generator-installation', nav='Generators', icon='generator', spec='Portable inlet or standby', card='Generators &amp; transfer switches',
      card_p='Interlock kits and inlets for portable generators, or automatic transfer switches for standby units, so the essentials stay on when the grid does not.',
      service_type='Generator installation', title='Standby Generators and Transfer Switches',
      h1=f'Standby generators and transfer switches in {TOWN_SHORT} and nearby towns',
      desc=f'Standby generator installation, automatic transfer switches, interlock kits and generator inlets in {TOWN_SHORT}, MA and nearby towns. Sized to your loads, permitted and inspected.',
      intro='When a nor\'easter takes the grid down, a standby generator starts itself in seconds. On a tighter budget, a transfer switch or interlock lets you run the essentials from a portable generator safely.',
      includes=['Load sizing for what you want covered: furnace or heat pump, well pump, sump, refrigerator, or the whole house',
                'Automatic standby generators (Generac, Kohler, Cummins) with an automatic transfer switch',
                'Manual transfer switches, interlock kits and inlet boxes for portable generators',
                'Pad, conduit and wiring to the panel',
                'Coordination with your gas or propane contractor',
                'Permit, inspection and first start-up',
                'Maintenance reminders so it starts when you need it'],
      price=('$10,000 to $16,000', 'installed for a 20 to 26 kW standby unit with transfer switch (gas or propane work by a licensed gas fitter is extra). Portable inlet with interlock: $900 to $1,800.'),
      signs_h='Choosing the right setup',
      signs=['Whole-house standby: no action needed during an outage, runs on natural gas or propane',
             'Essential-circuits standby: smaller unit, covers heat, water, refrigeration and a few outlets',
             'Portable with interlock: lowest cost, you start it and plug it in, good for a few days a year',
             'Well and septic pumps, sump pumps and heat pumps change the sizing; we count them'],
      faqs=[('What size generator do I need?', 'A 20 to 22 kW unit covers most single-family homes in the area, including a heat pump or central air. We size it from your actual loads, not a rule of thumb.'),
            ('Do I need a permit?', 'Yes, an electrical permit for the transfer switch and wiring, and a gas permit for the fuel line. We handle the electrical side and coordinate the gas fitter.'),
            ('How long does it take?', 'One to two days on site once the unit arrives. Lead times on standby units are usually one to three weeks.'),
            ('Can I run my furnace from a portable generator?', 'Yes, with an interlock kit or manual transfer switch and an inlet box. Never backfeed through a dryer outlet; it is dangerous for line workers and illegal.')],
      related=['panel-upgrades', 'ev-charger-installation', 'electrical-repairs']),
 dict(slug='lighting-installation', nav='Lighting &amp; fans', icon='bulb', spec='Recessed &middot; exterior &middot; dimmers', card='Lighting &amp; ceiling fans',
      card_p='Recessed and under-cabinet lighting, exterior and landscape fixtures, fan installs with proper bracing, and dimmers that actually match the bulbs.',
      service_type='Lighting installation', title='Lighting and Ceiling Fan Installation',
      h1=f'Lighting and ceiling fan installation in {TOWN_SHORT} and nearby towns',
      desc=f'Recessed LED lighting, under-cabinet lights, chandeliers, exterior and landscape lighting, ceiling fans and dimmers in {TOWN_SHORT}, MA and nearby towns. Clean installs with patching included.',
      intro='Good lighting is the cheapest renovation there is. We add recessed and under-cabinet lighting where there was none, hang fixtures on high ceilings, brace and wire ceiling fans properly, and set up dimmers that do not flicker.',
      includes=['Recessed LED lighting with slim wafer or can fixtures, laid out for even light',
                'Under-cabinet, pendant and chandelier installation, including vaulted and two-story ceilings',
                'Exterior, landscape, motion and security lighting',
                'Ceiling fans on fan-rated boxes with proper bracing',
                'Bathroom exhaust fans vented outside, with humidity sensors',
                'Dimmers, timers and smart switches (Lutron, Leviton) matched to your bulbs',
                'Wire fished with minimal openings, and drywall patched paint-ready'],
      price=('$150 to $300', 'per recessed fixture installed. A six-light kitchen with a dimmer is typically $1,200 to $2,000. Ceiling fan on an existing box: $200 to $450.'),
      signs_h='Popular projects',
      signs=['Kitchen: six to eight recessed lights plus under-cabinet strips on separate dimmers',
             'Living room and basement: recessed lighting to replace one center fixture',
             'Bedrooms: ceiling fans with light kits and wall controls',
             'Exterior: front entry, garage floods and path lighting on a timer or photocell',
             'Bathrooms: quiet exhaust fans that actually clear the mirror'],
      faqs=[('Can you add lights where there is no wiring?', 'Yes. We fish wire through finished ceilings and walls with small openings and patch them paint-ready.'),
            ('What color temperature should I pick?', '2700K to 3000K for living areas and bedrooms, 3000K to 3500K for kitchens and baths. We bring samples so you can see them in your room.'),
            ('My dimmer flickers with LED bulbs. Why?', 'The dimmer and the bulbs are not compatible. A dimmer rated for LED loads, matched to the bulbs, fixes it.'),
            ('Can you install a smart switch with no neutral wire?', 'There are models that work without a neutral, and we can often add one. We check the box before we recommend a switch.')],
      related=['electrical-repairs', 'remodeling-contractor', 'ev-charger-installation']),
 dict(slug='electrical-repairs', nav='Repairs &amp; troubleshooting', icon='bolt', spec='Same-week scheduling', card='Troubleshooting &amp; repairs',
      card_p='Tripping breakers, dead outlets, flickering lights, buzzing at the panel. We find the cause, fix it, and tell you what we found.',
      service_type='Electrical repair', title='Electrical Repairs and Troubleshooting',
      h1=f'Electrical repairs and troubleshooting in {TOWN_SHORT} and nearby towns',
      desc=f'Electrical troubleshooting and repairs in {TOWN_SHORT}, MA and nearby towns: tripping breakers, dead outlets, flickering lights, GFCI and AFCI problems, aluminum wiring, home inspection repair lists.',
      intro='A breaker that keeps tripping is telling you something. We find the cause, fix it properly and explain what we found, with a clear first-hour rate and a written quote for anything bigger.',
      includes=['Tripping breakers, dead outlets and circuits, flickering or dimming lights',
                'GFCI and AFCI breakers and receptacles that will not reset',
                'Buzzing, warm or discolored panels and devices',
                'Aluminum branch wiring repairs with approved connectors',
                'Outlet, switch and dimmer replacement, including tamper-resistant and USB outlets',
                'Hardwired, interconnected smoke and carbon monoxide detectors',
                'Code corrections from home inspection reports, with a letter for the closing',
                'Knob-and-tube assessment and replacement planning'],
      price=('$175 to $250', 'for the first hour of diagnosis, then by the hour plus materials. Anything that takes more than one visit gets a fixed written quote first.'),
      signs_h='Call today, not next week',
      signs=['Burning smell, scorch marks or a warm spot at the panel or an outlet',
             'Sparks or a buzzing sound from a switch, outlet or the panel',
             'A breaker that trips again right after you reset it',
             'Lights that dim when the furnace, well pump or air conditioner starts',
             'Two-prong outlets, no GFCI near water, or missing smoke and CO detectors'],
      faqs=[('Can you come the same day?', 'We keep room in the schedule for urgent calls and take emergencies first. For a burning smell or sparks, shut off the main if you can reach it safely and call.'),
            ('Can you fix the items on my home inspection report?', 'Yes. We work from the report, fix what is real, explain what is not, and provide a letter for the buyer or seller.'),
            ('My house has aluminum wiring. Do I need a rewire?', 'Usually not. Approved connector repairs at every device and junction are accepted by insurers and far cheaper than a rewire.'),
            ('Do you charge a trip fee?', 'No separate trip fee inside our service area. The first-hour rate covers travel and diagnosis.')],
      related=['panel-upgrades', 'lighting-installation', 'generator-installation']),
 dict(slug='remodeling-contractor', nav='Remodels &amp; additions', icon='house', spec='Kitchens &middot; baths &middot; basements', card='Remodels &amp; additions',
      card_p='New circuits, relocated outlets, GFCI and AFCI protection, and the framing, drywall, and finish work around it. One contractor, one schedule.',
      service_type='Home remodeling', title='Kitchen, Bath and Basement Remodels',
      h1=f'Kitchen, bath and basement remodels in {TOWN_SHORT} and nearby towns',
      desc=f'Kitchen, bathroom and basement remodeling in {TOWN_SHORT}, MA and nearby towns by a licensed electrician and registered home improvement contractor. One contractor for the wiring and the walls.',
      intro='Most remodels are electrical, plumbing and the walls around them. As a licensed master electrician and registered home improvement contractor, we run the job from permit to paint-ready, so you are not scheduling three contractors for one room.',
      includes=['Kitchen and bath electrical: dedicated appliance circuits, GFCI protection, under-cabinet lighting, exhaust fans',
                'Basement finishing: framing, insulation, electrical, drywall, lighting, egress review',
                'Additions, garage conversions and bonus rooms',
                'Framing, drywall and patching after electrical work',
                'Trim, doors and finish carpentry',
                'Permits, inspections and scheduling of plumbers and HVAC',
                'A written contract with a fixed price and a schedule, as Massachusetts home improvement law requires'],
      price=('$40 to $75 per sq ft', 'for a finished basement. Kitchen remodels typically $30,000 to $80,000 and bathrooms $15,000 to $35,000, depending on scope and finishes. Fixed-price written contract.'),
      signs_h='How we protect you',
      signs=['Written contract with scope, price, start and finish dates, as required for home improvement work over $1,000 in Massachusetts',
             'Deposits limited to one-third of the contract price, except for special-order materials',
             'Registered with the Massachusetts Home Improvement Contractor program, which backs the Guaranty Fund',
             'Permits pulled in our name, so the responsibility is ours',
             'Change orders in writing before the work changes'],
      faqs=[('Do you handle the permits for a remodel?', 'Yes. Building, electrical and any other permits are pulled in our name and inspections are scheduled by us.'),
            ('Are you a registered home improvement contractor?', f'Yes, {HIC}, in addition to the master electrician license. Both are required for this work in Massachusetts.'),
            ('How are payments scheduled?', 'A deposit of up to one-third at signing, progress payments tied to milestones in the contract, and the balance at completion after your walkthrough.'),
            ('Can you do just the electrical part of my remodel?', 'Yes. We work with homeowners and other contractors on the electrical scope alone, with the same permits and inspections.')],
      related=['lighting-installation', 'panel-upgrades', 'electrical-repairs']),
]
SP = {s['slug']: s for s in SERVICE_PAGES}

def service_cards():
    out = []
    for s in SERVICE_PAGES:
        out.append(f'''      <article class="service-card">
        {ICON[s['icon']]}
        <span class="spec">{s['spec']}</span>
        <h3><a href="{s['slug']}.html">{s['card']}</a></h3>
        <p>{s['card_p']}</p>
        <a class="text-link" href="{s['slug']}.html">Learn more</a>
      </article>''')
    return '\n'.join(out)

def related_block(slugs):
    cards = '\n'.join(f'''      <a class="related-card" href="{SP[s]['slug']}.html">{SP[s]['title']}<span>{SP[s]['spec']}</span></a>''' for s in slugs)
    return f'''<section class="section">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Related</p>
      <h2>Other work we do</h2>
    </div>
    <div class="related-grid">
{cards}
    </div>
  </div>
</section>
'''

def service_page(sp):
    lds = [service_ld(sp), breadcrumb_ld([('Home', ''), ('Services', 'services.html'), (sp['title'], sp['slug'] + '.html')]), faq_ld(sp['faqs'])]
    return head(sp['title'] + f' in {TOWN_SHORT}, MA', sp['desc'], sp['slug'] + '.html', lds) + header('services') + f'''
<section class="page-hero">
  <div class="wrap">
    <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><a href="services.html">Services</a><span>/</span>{sp['title']}</nav>
    <h1>{sp['h1']}</h1>
    <p>{sp['intro']}</p>
  </div>
</section>

<section class="section">
  <div class="wrap service-layout">
    <div>
      <h2>What is included</h2>
      {checklist(sp['includes'])}
      <h2 class="mt">{sp['signs_h']}</h2>
      {checklist(sp['signs'])}
      <h2 class="mt">How it works</h2>
      <ol class="steps">
        <li><strong>Call or send the form.</strong> Tell us what you have in mind and send a photo of the panel if you can.</li>
        <li><strong>Site visit and written quote.</strong> We check the panel, the run and the finish work, then send a fixed quote.</li>
        <li><strong>Work, permit, inspection.</strong> We pull the permit, do the work and meet the inspector.</li>
        <li><strong>Walkthrough.</strong> We show you what was done, label everything and clean up.</li>
      </ol>
    </div>
    <aside class="price-box" aria-label="Pricing">
      <p class="label">Typical price</p>
      <p class="price">{sp['price'][0]}</p>
      <p>{sp['price'][1]}</p>
      <a class="btn btn-primary" href="contact.html">Get a written quote</a>
      <p class="small">Or call <a href="tel:{PHONE_TEL}">{PHONE}</a>. Serving {TOWNS_SHORT}.</p>
      <p class="small">{WARRANTY}. Licensed and insured. Permit included.</p>
    </aside>
  </div>
</section>

''' + faq_block(sp['faqs'], f"{sp['title']}: questions we get") + related_block(sp['related']) + cta_strip(
        f"Ready to talk about {sp['nav'].replace('&amp;', '&').lower()}?", f"Send a photo and a few details and we will come back with a number. No charge for the conversation.") + footer()

# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------
HOME_FAQS = [
 ('Are you licensed and insured?', f'Yes. Massachusetts master electrician {LICENSE}, home improvement contractor {HIC}, general liability and workers\' compensation. Certificates on request.'),
 ('Do you pull permits?', 'Yes, for every job that needs one. The permit, the inspection and meeting the inspector are included in the quote.'),
 ('How fast can you come out?', 'Repairs are usually scheduled within the week, emergencies the same day when we can. Installs are scheduled after the site visit, typically within two to three weeks.'),
 ('How do you price work?', 'Installs and remodels get a fixed written quote after a site visit. Troubleshooting is a stated first-hour rate, then hourly plus materials, with a quote before anything bigger.'),
 ('Where do you work?', f'Based in {TOWN}, serving {", ".join(TOWN_NAMES[:-1])} and {TOWN_NAMES[-1]}, and about 30 miles around for larger projects.'),
 ('Do you take small jobs?', 'Yes. Outlets, switches, a ceiling fan, a bathroom fan, a dead circuit. Small jobs are how most customers meet us.'),
 ('What warranty do you offer?', f'A {WARRANTY.lower()} on our work, plus the manufacturer warranty on equipment we install.'),
 ('How do payments work?', 'Service calls are paid at completion. Installs take a deposit (no more than one-third in Massachusetts) and the balance at completion. Card, check or bank transfer.'),
]

INDEX = head("", f"Licensed electrician and general contractor in {TOWN}. Panel upgrades, EV chargers, generators, lighting, troubleshooting and remodels. Owner on every job, written quotes before work starts.", "", [faq_ld(HOME_FAQS)]) + header('home') + f'''
<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <p class="eyebrow">Licensed electrician + general contractor &middot; {TOWN}</p>
      <h1>Electrical work done right, by the person who answers the phone.</h1>
      <p class="lede">{NAME} handles residential and light-commercial electrical, and the remodel work that goes with it. The owner is on every job, and you get a written quote before anything starts.</p>
      <div class="btn-row">
        <a class="btn btn-primary btn-lg" href="contact.html">Get a free quote</a>
        <a class="btn btn-outline-light btn-lg" href="tel:{PHONE_TEL}">{ICON['phone']}Call {PHONE}</a>
      </div>
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
      <p class="eyebrow">Why JEMCO</p>
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
        <p>Every job is permitted where required, inspected, and backed by our {WARRANTY.lower()}.</p>
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

<section class="section" id="reviews">
  <div class="wrap reviews-inner">
    <div>
      <p class="eyebrow">Reviews</p>
      <h2>What customers say</h2>
      <p class="muted">Our Google reviews are public and unedited. Read them, and if we have worked for you, leave one. It is the best thank-you a small company can get.</p>
      <div class="btn-row">
        <a class="btn btn-navy" href="{GBP_URL}" rel="noopener">Read our Google reviews</a>
        <a class="btn btn-outline-navy" href="{GBP_URL}" rel="noopener">Leave a review</a>
      </div>
    </div>
    <div class="review-badge" aria-hidden="true">
      <div class="stars">{ICON['star'] * 5}</div>
      <p>Google reviews</p>
    </div>
  </div>
</section>

<section class="section section-alt" id="area">
  <div class="wrap area-inner">
    <div>
      <p class="eyebrow">Service area</p>
      <h2>Serving {TOWN_SHORT} and the towns around it.</h2>
      <p>Based in {TOWN}. We cover {", ".join(TOWN_NAMES[:-1])} and {TOWN_NAMES[-1]}, and travel farther for larger projects. Not sure if you are in range? Call and ask.</p>
      <p><a class="text-link" href="service-area.html">See the full service area</a></p>
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

''' + faq_block(HOME_FAQS) + cta_strip("Breaker keeps tripping? Burning smell at the panel?", "Those are the calls to make today, not next week.") + footer()

# ---------------------------------------------------------------------------
# Services overview
# ---------------------------------------------------------------------------
SERVICES_PAGE = head("Services", f"Residential and commercial electrical services plus remodels in {TOWN}: panel upgrades, EV chargers, generators, lighting, rewiring, troubleshooting and finish work.", "services.html",
                     [breadcrumb_ld([('Home', ''), ('Services', 'services.html')])]) + header('services') + f'''
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Services</p>
    <h1>What we do</h1>
    <p>Residential, light-commercial, and the contracting work that goes with it. If it is not on the list, ask. It probably is.</p>
  </div>
</section>

<section class="section" id="main-services">
  <div class="wrap">
    <div class="services-grid">
{service_cards()}
    </div>
  </div>
</section>

<section class="service-section" id="residential">
  <div class="wrap">
    <div class="section-head">
      <h2>Residential electrical</h2>
      <p>Most of our work is in homes: upgrades, repairs, and the new circuits that modern living keeps adding.</p>
    </div>
    {checklist([
      '<a href="panel-upgrades.html">Panel upgrades and service changes</a>, 100A to 200A, meter and main combos',
      'Whole-house rewiring and knob-and-tube or aluminum wiring replacement',
      'New circuits for ranges, dryers, hot tubs, mini-splits, and workshops',
      '<a href="ev-charger-installation.html">EV charger circuits</a>, NEMA 14-50 outlets, and hardwired chargers',
      '<a href="generator-installation.html">Generator inlets, interlock kits, and automatic transfer switches</a>',
      '<a href="lighting-installation.html">Recessed, under-cabinet, and exterior lighting</a>',
      'Ceiling fans and bathroom exhaust fans',
      'Outlets, switches, dimmers, and smart controls',
      'GFCI and AFCI protection and code corrections',
      'Hardwired, interconnected smoke and CO detectors',
      '<a href="electrical-repairs.html">Troubleshooting</a>: tripping breakers, dead circuits, flickering lights',
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
      '<a href="remodeling-contractor.html">Kitchen and bathroom remodels</a>',
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
          <tr><td><a href="panel-upgrades.html">200-amp panel upgrade</a></td><td>New panel and breakers, grounding and bonding, utility coordination, permit and inspection</td><td>1 day</td></tr>
          <tr><td><a href="ev-charger-installation.html">Level 2 EV charger</a></td><td>Load calculation, dedicated 40 to 60A circuit, NEMA 14-50 outlet or hardwired unit</td><td>Half day</td></tr>
          <tr><td><a href="generator-installation.html">Standby generator</a></td><td>Pad, transfer switch, wiring to the panel, gas contractor coordination, inspection</td><td>1 to 2 days</td></tr>
          <tr><td><a href="lighting-installation.html">Recessed lighting, 6 to 8 fixtures</a></td><td>Layout, wiring, dimmers, drywall patching, paint-ready finish</td><td>1 day</td></tr>
          <tr><td>Whole-house rewire</td><td>Room-by-room replacement of old wiring, new devices, patching included</td><td>3 to 7 days</td></tr>
          <tr><td><a href="remodeling-contractor.html">Basement finish</a></td><td>Framing, electrical, insulation, drywall, trim, lighting, egress review</td><td>3 to 6 weeks</td></tr>
        </tbody>
      </table>
    </div>
    <p class="table-note">Times assume normal access and no surprises behind the walls. If we find something, you hear about it before we touch it.</p>
  </div>
</section>

''' + cta_strip("Not sure which one you need?", "Describe the problem and we will point you the right way. No charge for the conversation.") + footer()

# ---------------------------------------------------------------------------
# Service area
# ---------------------------------------------------------------------------
towns_li = '\n'.join(f'      <li>{t}, {STATE}{("<small>" + n + "</small>") if n else ""}</li>' for t, n in TOWNS)
AREA = head("Service Area", f"{NAME_PLAIN} serves {TOWN_SHORT}, {', '.join(TOWN_NAMES[1:8])} and nearby Massachusetts towns with electrical and remodeling work.", "service-area.html",
            [breadcrumb_ld([('Home', ''), ('Service area', 'service-area.html')])]) + header('area') + f'''
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Service area</p>
    <h1>Serving {TOWN_SHORT} and the towns around it</h1>
    <p>We are based in {TOWN} and work within about 30 miles. For panel upgrades, generators and remodels we travel farther. If your town is not listed, call; the answer is usually yes.</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <h2>Towns we serve</h2>
      <p>Same pricing and same crew everywhere on this list. No trip fee inside the service area.</p>
    </div>
    <ul class="towns-grid">
{towns_li}
    </ul>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap area-inner">
    <div>
      <h2>What we do in every town</h2>
      {checklist([f'<a href="{s["slug"]}.html">{s["title"]}</a>' for s in SERVICE_PAGES])}
    </div>
    <div class="hours-card">
      <h3>Hours</h3>
      <dl>
        {''.join(f'<dt>{d}</dt><dd>{h}</dd>' for d, h in HOURS)}
      </dl>
      <p class="note">Emergencies outside these hours: call <a href="tel:{PHONE_TEL}">{PHONE}</a> and leave a message.</p>
    </div>
  </div>
</section>

''' + cta_strip(f"In {TOWN_SHORT} or nearby? Let's talk.", "Call, text or send the form and we will come back with a number.") + footer()

# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------
ABOUT = head("About", f"{NAME_PLAIN} is an owner-operated electrical and contracting company in {TOWN}. Licensed, insured, and built on years in the trade.", "about.html",
             [breadcrumb_ld([('Home', ''), ('About', 'about.html')])]) + header('about') + f'''
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
      <p>{NAME} is owner-operated. After years running crews and large projects, <strong>[Owner name]</strong> started JEMCO to get back to what he likes best: doing the work himself, for people he will see again around town.</p>
      <p>That means a smaller crew, a direct line to the person responsible for your job, and the same face at the estimate, the install, and the walkthrough.</p>
      <p>We do residential and light-commercial electrical, and we handle the remodel work around it so you are not coordinating three contractors for one project. Every job is quoted in writing, permitted where required, and inspected.</p>
      <p><a class="text-link" href="contact.html">Get in touch</a></p>
    </div>
    <aside class="cred-card" aria-label="Credentials">
      <h3>Credentials</h3>
      <ul>
        <li>Massachusetts Master Electrician, {LICENSE}</li>
        <li>Home Improvement Contractor registration, {HIC}</li>
        <li>General liability insured, workers' compensation, commercial auto</li>
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
# Contact
# ---------------------------------------------------------------------------
CONTACT = head("Get a quote", f"Request a quote from {NAME_PLAIN} in {TOWN}. Call, text, or send the form. We reply within one business day.", "contact.html",
               [breadcrumb_ld([('Home', ''), ('Contact', 'contact.html')])]) + header('contact') + f'''
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
      <fieldset class="field fieldset-plain">
        <legend>Best way to reach you</legend>
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
      <p class="form-note">No mailing lists and no sales calls. We only use this to reply about your job. See our <a href="privacy.html">privacy policy</a>.</p>
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
          <p>{TOWN} and about 30 miles around it. <a href="service-area.html">See the towns</a>.</p>
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
# Privacy and 404
# ---------------------------------------------------------------------------
PRIVACY = head("Privacy Policy", f"How {NAME_PLAIN} handles the information you send through this website.", "privacy.html") + header('') + f'''
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Privacy</p>
    <h1>Privacy policy</h1>
    <p>Short version: we use what you send us to reply about your job, and nothing else.</p>
  </div>
</section>
<section class="section">
  <div class="wrap prose">
    <h2>What we collect</h2>
    <p>When you use the quote form, call, text or email us, we receive the details you provide: your name, phone number, email address, address or town, and the description of the work. If you send photos, we keep them with your job record.</p>
    <h2>How we use it</h2>
    <p>To reply to your request, prepare a quote, schedule and perform the work, send invoices, and follow up about the job, including warranty service. We may ask you for a review after the work is done. We do not sell or rent your information, and we do not add you to a marketing list without asking.</p>
    <h2>Who sees it</h2>
    <p>Only the people who need it to do the job: the owner, our crew, and the services we use to run the business (form handling, scheduling and invoicing software, email). Permit applications filed with your town include the job address as required by law.</p>
    <h2>Website analytics</h2>
    <p>This site may use Google Analytics or similar tools to count visits and understand which pages are useful. These tools use cookies and collect anonymous usage data. You can block cookies in your browser without affecting the site.</p>
    <h2>Your choices</h2>
    <p>Ask us at any time to see, correct or delete the information we hold about you, or to stop any follow-up messages. Email <a href="mailto:{EMAIL}">{EMAIL}</a> or call <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p>
    <h2>Changes</h2>
    <p>If this policy changes, the new version will be posted here with the date. This version was posted in 2026.</p>
  </div>
</section>
''' + footer()

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

# ---------------------------------------------------------------------------
# Write everything
# ---------------------------------------------------------------------------
pages = {'index.html': INDEX, 'services.html': SERVICES_PAGE, 'service-area.html': AREA, 'about.html': ABOUT,
         'contact.html': CONTACT, 'privacy.html': PRIVACY, '404.html': NOTFOUND}
for sp in SERVICE_PAGES:
    pages[sp['slug'] + '.html'] = service_page(sp)

for name, html in pages.items():
    with open(os.path.join(REPO, name), 'w') as f:
        f.write(html)
    print('wrote', name, len(html), 'bytes')

# sitemap.xml and robots.txt stay in sync with the page list
prio = {'index.html': '1.0', 'services.html': '0.9', 'contact.html': '0.9', 'service-area.html': '0.7', 'about.html': '0.6', 'privacy.html': '0.2'}
urls = []
for name in pages:
    if name == '404.html': continue
    loc = SITE_URL + '/' + ('' if name == 'index.html' else name)
    urls.append(f'  <url><loc>{loc}</loc><priority>{prio.get(name, "0.8")}</priority></url>')
with open(os.path.join(REPO, 'sitemap.xml'), 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n')
with open(os.path.join(REPO, 'robots.txt'), 'w') as f:
    f.write(f'User-agent: *\nAllow: /\nDisallow: /brand/\nDisallow: /site-src/\n\nSitemap: {SITE_URL}/sitemap.xml\n')
print('wrote sitemap.xml with', len(urls), 'urls')
