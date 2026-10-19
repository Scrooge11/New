# JEMCO Contracting & Electrical Services

Brand package and website for JEMCO Contracting & Electrical Services.

> **Name change, October 18, 2026.** The company was going to be called JS Contracting & Electrical Services; it is now JEMCO Contracting & Electrical Services. The website, the logo files and the brand guide carry the new name. The business plan, marketing playbook, financial model and research PDFs in `business/deliverables/` still carry the old name until they are re-cut.

- **Website**: plain HTML, CSS and a little JavaScript. No build step, no framework. Open `index.html` in a browser or drop the folder on any static host.
- **Brand**: logo files, colors, type and usage rules. Open `brand/index.html` for the guidelines.
- **Business plan**: `business/README.md` links the client-ready plan and holds the three-year financial model and the research behind it.

## What is where

```
index.html, services.html, about.html, contact.html, 404.html   the site
css/styles.css                                                   all styling (brand colors are the variables at the top)
js/main.js                                                       mobile menu, footer year, quote form submit
assets/logo/                                                     SVG logos the site uses
assets/favicon*.png, favicon.svg, apple-touch-icon.png, og-image.png
brand/index.html                                                 brand guidelines (logo usage, colors, fonts, mockups)
brand/logo/svg/                                                  every logo variant as vector art
brand/logo/png/                                                  same logos as transparent PNG, print resolution
brand/source/                                                    the script that draws the logos (see "Regenerating the logos")
site-src/                                                        the scripts that generated the HTML pages and the brand guide
business/                                                        business plan link, financial model (xlsx), research memos
```

## Before going live: fill in the placeholders

Every business fact lives at the top of `site-src/gen_site.py`. Edit the constants there and run `python3 site-src/gen_site.py .` to rewrite all 13 pages, the sitemap and robots.txt. Editing the HTML directly also works.

| Constant | Currently | Replace with |
|---|---|---|
| `PHONE`, `PHONE_TEL` | `(000) 000-0000`, `+10000000000` | the business phone (the `tel:` version is country code plus digits) |
| `EMAIL` | `office@jemcoelectric.com` | the business email, once the domain is bought |
| `TOWN`, `TOWN_SHORT`, `TOWNS` | Westford, MA and 16 nearby towns (assumed) | the real home base and the towns actually served |
| `LICENSE`, `HIC` | `Lic. #00000000`, `HIC #000000` | master electrician license and Home Improvement Contractor registration numbers |
| `SITE_URL` | `https://www.jemcoelectric.com` | the final domain once bought (feeds canonical tags, sitemap, schema). jemcoelectric.com was available on October 18, 2026; confirm at the registrar before relying on it |
| `GBP_URL` | placeholder | the Google Business Profile review link (Google Business Profile, "Ask for reviews") |
| `WARRANTY` | `2-year workmanship warranty` | the real warranty term |
| `HOURS` | Mon to Fri 7 to 5 | real hours |
| Prices on the six service pages | typical Massachusetts ranges | the owner's own ranges (`price=` in each `SERVICE_PAGES` entry) |
| `[Owner name]`, credentials | about page | the owner's name and real credentials |
| `assets/hero.jpg` | an AI-generated placeholder photo of a New England house at dusk | a real photo of the owner's work or truck, 1600 px wide or more, landscape |

Also decide whether the site should mention the previous company. It currently does not.

### Pages

| Page | Purpose |
|---|---|
| `index.html` | Home: hero, services, why JEMCO, process, reviews, service area, FAQ |
| `services.html` | All services with the common-jobs table |
| `panel-upgrades.html`, `ev-charger-installation.html`, `generator-installation.html`, `lighting-installation.html`, `electrical-repairs.html`, `remodeling-contractor.html` | One landing page per money service, each with pricing, FAQ, Service and FAQPage schema |
| `service-area.html` | Towns served |
| `about.html`, `contact.html`, `privacy.html`, `404.html` | Company, quote form, privacy policy (needed for Google Ads and Local Services Ads), not-found page |

## Previewing

Open `index.html` directly, or for a local server:

```
npx http-server . -p 8080
```

## Hosting

Any static host works. Two easy options:

**Netlify (recommended, free tier, the quote form works out of the box).** Create a site from this repo or drag the folder onto app.netlify.com. The form on `contact.html` is already marked up for Netlify Forms, so submissions show up in the Netlify dashboard and can be emailed to the owner (Site settings, Forms, Notifications). `netlify.toml` is included.

**GitHub Pages.** Settings, Pages, deploy from the `main` branch root. The `.nojekyll` file is already there. GitHub Pages cannot process forms, so either point the form's `action` at a service like Formspree (`https://formspree.io/f/your-id`) or keep the phone and email as the contact path. If the form cannot send, the page shows the phone and email instead.

After the domain is live, submit `sitemap.xml` in Google Search Console and create a Google Business Profile using `brand/logo/png/jemco-icon-1024.png` as the profile image and `assets/og-image.png` as a cover.

## Fonts

Headlines use **Saira**, body text uses **Barlow**. Both are free under the SIL Open Font License and load from Google Fonts. For print work, download them from fonts.google.com and install them. The logo files have the type converted to outlines, so they do not need the fonts installed.

## Regenerating the logos

The logos are drawn by `brand/source/logo.py`. To change colors or geometry and re-export:

```
pip install fonttools uharfbuzz
mkdir -p fonts && cd fonts
curl -sSLo "Saira[wdth,wght].ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/saira/Saira%5Bwdth%2Cwght%5D.ttf"
curl -sSLo "Saira-Italic[wdth,wght].ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/saira/Saira-Italic%5Bwdth%2Cwght%5D.ttf"
cd ..
python3 brand/source/logo.py brand/logo/svg          # expects ../fonts relative to the script; adjust FONTS in logo.py if needed
node brand/source/export.js brand/logo/svg brand/logo/png assets   # needs Playwright: npm i -g playwright
```
