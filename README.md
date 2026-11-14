# JEMCO Contracting & Electrical Services

Brand package and website for JEMCO Contracting & Electrical Services.

> **Name change, October 18, 2026.** The company was going to be called JS Contracting & Electrical Services; it is now JEMCO Contracting & Electrical Services. The website, the logo files and the brand guide carry the new name. The business plan, marketing playbook, financial model and research PDFs in `business/deliverables/` still carry the old name until they are re-cut.

- **Website**: plain HTML, CSS and a little JavaScript in `site/`. No build step, no framework. Open `site/index.html` in a browser or drop the `site/` folder on any static host. Only `site/` is published; the brand files, business plan and scripts stay private.
- **Brand**: logo files, colors, type and usage rules. Open `brand/index.html` for the guidelines.
- **Business plan**: `business/README.md` links the client-ready plan and holds the three-year financial model and the research behind it.

## Working on this from another computer

Everything the site needs is in this repository: pages, styles, fonts, photos and the scripts that build them. There is nothing to install with npm, no account keys and no files to copy across by hand.

**One-time setup**

1. Install Git and Python 3.9 or newer.
   - Mac: run `xcode-select --install` in Terminal. That installs both.
   - Windows: install [Git for Windows](https://git-scm.com/download/win) and Python from [python.org](https://www.python.org/downloads/) (tick "Add python.exe to PATH").
2. Sign in to GitHub on that computer (the first `git clone` or `git push` asks; the Cursor and GitHub Desktop apps can do it for you).
3. Get the code. The JEMCO work lives on a branch, not on `main`, which holds only a short README:

   ```
   git clone --branch claude/js-contracting-branding-website-xtl811 https://github.com/Scrooge11/New.git jemco
   cd jemco
   ```

   Work that is still waiting in a pull request sits on its own branch. To pick that up instead, run `git switch` with the branch name shown at the top of the pull request, for example `git switch cursor/jemco-site-enhancements-8194`. `git branch -a` lists every branch.

**Every time**

```
git pull                           # pick up what was done on the other computer
python3 site-src/preview.py        # Windows: py site-src\preview.py
```

The preview opens the site at `http://localhost:8080` and keeps running. Edit `site-src/gen_site.py` (wording, prices, phone, towns), `site/css/styles.css` (looks) or `site/js/main.js` (behaviour), then refresh the browser. Quote forms can be submitted in the preview: nothing is sent, and the fields are printed in the terminal window.

When a piece of work is done:

```
git add -A
git commit -m "What changed, in a few words"
git push
```

Pull before you start and push when you finish, and the two computers never drift apart. `.gitattributes` keeps line endings the same on Windows and Mac, so switching between them does not create noise in the history.

Only two jobs need more than Git and Python: redrawing the logos (see "Regenerating the logos") and re-cutting photos.

## What is where

```
site/index.html, services.html, about.html, contact.html, ...    the site (14 pages, listed under "Pages")
site/css/styles.css                                              all styling (brand colors and the light and dark themes are the variables at the top)
site/js/main.js                                                  menus, theme button, quote forms, town checker, scroll effects
site/js/theme-init.js                                            runs first on every page: applies the visitor's saved light or dark choice before anything is drawn
site/assets/logo/                                                SVG logos the site uses
site/assets/fonts/                                               Saira and Barlow, served from the site, with their licences
site/assets/favicon*.png, favicon.svg, apple-touch-icon.png, og-image.jpg
netlify.toml                                                     publish folder, security headers, cache rules
brand/index.html                                                 brand guidelines (logo usage, colors, fonts, mockups)
brand/logo/svg/                                                  every logo variant as vector art
brand/logo/png/                                                  same logos as transparent PNG, print resolution
brand/source/                                                    the script that draws the logos (see "Regenerating the logos")
site-src/gen_site.py                                             builds every page from the business facts at the top of the file
site-src/preview.py                                              local preview server (see "Previewing")
site-src/                                                        also holds the script for the brand guide
business/                                                        business plan link, financial model (xlsx), research memos
```

## Before going live: fill in the placeholders

Every business fact lives at the top of `site-src/gen_site.py`. Edit the constants there and run `python3 site-src/gen_site.py site` to rewrite all 14 pages, the sitemap and robots.txt. Editing the HTML directly also works, but the next run of the script overwrites it.

Each run ends with a "Not ready to launch" list while any of these are still in place: the placeholder phone number, licence numbers, review link or owner name, a page title or description too long for search results, a service page whose `form_type` is not one of the choices in the quote form, or dark-theme colors in `styles.css` that differ between the two places they are written. `python3 site-src/gen_site.py site --strict` exits with an error until that list is empty, which makes it usable as a pre-launch check.

| Constant | Currently | Replace with |
|---|---|---|
| `PHONE`, `PHONE_TEL` | `(000) 000-0000`, `+10000000000` | the business phone (the `tel:` version is country code plus digits) |
| `EMAIL` | `office@jemcoelectric.com` | the business email, once the domain is bought |
| `TOWN`, `TOWN_SHORT`, `TOWNS` | Westford, MA and 16 nearby towns (assumed) | the real home base and the towns actually served |
| `LICENSE`, `HIC` | `Lic. #00000000`, `HIC #000000` | master electrician license and Home Improvement Contractor registration numbers |
| `SITE_URL` | `https://www.jemcoelectric.com` | the final domain once bought (feeds canonical tags, sitemap, schema). jemcoelectric.com was available on October 18, 2026; confirm at the registrar before relying on it |
| `GBP_URL` | placeholder | the Google Business Profile review link (Google Business Profile, "Ask for reviews"). Until it is set, the two review buttons on the home page and the footer link go to a dead address |
| `WARRANTY` | `2-year workmanship warranty` | the real warranty term. It is the headline of the guarantee card on the home page and appears on every service page |
| `HOURS` | Mon to Fri 7 to 5 | real hours |
| Prices on the six service pages | typical Massachusetts ranges | the owner's own ranges (`price=` in each `SERVICE_PAGES` entry) |
| `[Owner name]`, credentials | about page | the owner's name and real credentials |
| `site/assets/hero.jpg` | an AI-generated placeholder photo of a New England house at dusk | a real photo of the owner's work or truck, 1600 px wide or more, landscape |
| `site/assets/work/panel-upgrade.jpg`, `ev-charger.jpg`, `generator.jpg`, `lighting.jpg`, `repairs.jpg`, `remodel.jpg` (plus `.webp` and `-640.webp` versions) | AI-generated placeholder photos for the home page work band | the owner's own job photos, landscape 4:3, 1200 px wide or more. They must not be presented as JEMCO's own jobs until they are |

Also decide whether the site should mention the previous company. It currently does not.

### Pages

| Page | Purpose |
|---|---|
| `index.html` | Home: hero, services, why JEMCO, process, reviews, service area, FAQ |
| `services.html` | All services with the common-jobs table |
| `panel-upgrades.html`, `ev-charger-installation.html`, `generator-installation.html`, `lighting-installation.html`, `electrical-repairs.html`, `remodeling-contractor.html` | One landing page per money service, each with pricing, FAQ, Service and FAQPage schema |
| `service-area.html` | Towns served, with a "check your town" box |
| `about.html`, `contact.html`, `privacy.html` | Company, quote form, privacy policy (needed for Google Ads and Local Services Ads) |
| `thanks.html` | Confirmation page after a quote request, for visitors whose browser has JavaScript off or blocked. Not indexed, not in the sitemap |
| `404.html` | Not-found page. Not indexed. Its links start at the site root so it works for a mistyped address at any depth, which also means it only looks right through a server, not opened as a file |

## Previewing

```
python3 site-src/preview.py        # Windows: py site-src\preview.py
```

This rebuilds the pages, serves `site/` at `http://localhost:8080` and opens the browser. It sends the same security headers as the live host, shows `404.html` for a wrong address and `thanks.html` after a form is submitted, so what works here works once deployed. `--port 8081` picks another port; `--no-open` leaves the browser alone.

Opening `site/index.html` straight from the folder also works for a quick look, apart from the 404 page.

The site follows the visitor's light or dark system setting until they press the moon or sun button in the header; after that it keeps their choice. Press the same button to see the other theme while previewing.

## How the site behaves

- **Light and dark.** The header button switches theme and the choice is remembered on that device (browser storage, key `jemco-theme`; nothing is sent anywhere). The dark colors are written twice at the top of `styles.css`, once for "system is dark" and once for "visitor chose dark". Change both together; the generator lists it under "Not ready to launch" if they differ.
- **Services menu.** On a computer, "Services" opens a menu of the six service pages on hover, on click of the small arrow, or from the keyboard (Escape closes it). On a phone the menu button opens a full-width sheet with the same links.
- **Quote forms.** A missing name, phone or description is explained under that field instead of in a browser pop-up. A ten-digit phone number is tidied to `(978) 555-0100` style. After a successful send the form is replaced by a confirmation; if sending fails, the typed request stays and the phone and email are offered instead.
- **Service preselected.** Buttons on a service page link to `contact.html?type=...`, so the "Type of work" list is already set when the visitor arrives. The choices are `FORM_TYPES` in `gen_site.py`, and each `SERVICE_PAGES` entry names its own with `form_type=`. Add a new service to both.
- **Check your town.** On the service area page, typing a town marks it in the list. A town that is not listed gets the "call; the answer is usually yes" line. The towns come from `TOWNS`.
- **Movement.** Sections fade up as they scroll into view, cards lift on hover, FAQ answers slide open and pages cross-fade in browsers that support it. All of it is switched off for visitors whose system asks for reduced motion.
- **Without JavaScript.** Everything is still reachable: the phone menu becomes a plain list of links, the forms use the browser's own checks and land on `thanks.html`, and the theme follows the system setting. The theme button and town box are hidden because they would do nothing.

## Hosting

Any static host works. Two easy options:

**Netlify (recommended, free tier).** Create a site from this repo; `netlify.toml` already points it at `site/`. Then:

1. In the Netlify dashboard open Forms and choose "Enable form detection", then redeploy. Without this step the quote forms are not picked up.
2. Add an email notification under Forms, Submission notifications, so requests reach the owner.

The quote forms on the home page and `contact.html` are marked up for Netlify Forms and post to `thanks.html`. With JavaScript the confirmation appears in place; without it the visitor lands on `thanks.html`.

`netlify.toml` also sets the security headers. The Content-Security-Policy allows only files served from the site itself, so **before adding Google Analytics, Tag Manager, a map embed or any other third-party script, add its hosts to the policy in `netlify.toml`** or the browser will block it silently.

**GitHub Pages.** Pages publishes only the repository root or a `docs/` folder from a branch, so `site/` needs a GitHub Actions workflow that uploads that folder. The `.nojekyll` file is already there. GitHub Pages cannot process forms and does not apply the headers in `netlify.toml`, so either point the forms' `action` at a service like Formspree (`https://formspree.io/f/your-id`) or keep the phone and email as the contact path. If a form cannot send, the page shows the phone and email instead.

After the domain is live, submit `sitemap.xml` in Google Search Console and create a Google Business Profile using `brand/logo/png/jemco-icon-1024.png` as the profile image and `site/assets/og-image.jpg` as a cover.

## Fonts

Headlines use **Saira**, body text uses **Barlow**. Both are free under the SIL Open Font License and are served from `site/assets/fonts/`, so the site makes no requests to Google or any other third party. For print work, download them from fonts.google.com and install them. The logo files have the type converted to outlines, so they do not need the fonts installed.

## Regenerating the logos

The logos are drawn by `brand/source/logo.py`. To change colors or geometry and re-export:

```
pip install fonttools uharfbuzz
mkdir -p fonts && cd fonts
curl -sSLo "Saira[wdth,wght].ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/saira/Saira%5Bwdth%2Cwght%5D.ttf"
curl -sSLo "Saira-Italic[wdth,wght].ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/saira/Saira-Italic%5Bwdth%2Cwght%5D.ttf"
cd ..
python3 brand/source/logo.py brand/logo/svg          # expects ../fonts relative to the script; adjust FONTS in logo.py if needed
node brand/source/export.js brand/logo/svg brand/logo/png   # needs Playwright: npm i -g playwright
```

`export.js` accepts a third folder argument and then also draws a logo-only share image named `og-image.png`. The site does not use that file; it uses `site/assets/og-image.jpg`, the version with the hero photo.

## Credit and images

- The footer on every page carries the Next Wave Digital Consulting credit (wave mark plus "Site Designed By: Next Wave Digital Consulting", linking to nextwavedigitalconsulting.com). The mark lives in `site/assets/nwdc/`. Keep it on every build.
- Image log: `site/assets/hero.jpg` and the six photos in `site/assets/work/` were generated with AI image tools (Figma, file "JEMCO website hero photo") as placeholders. Replace them with the owner's job photos before launch.

## Images and performance

Every photo ships as JPEG plus WebP at two widths (640 px and full size), served through `<picture>` with `srcset`, so phones download the small WebP. The home hero is preloaded. To swap in real photos, replace the JPEG in `site/assets/work/` with the same file name and regenerate the WebP versions (any image tool; quality 72 to 75 is right). Photos are not cached long-term, so a replaced photo shows up on the next visit. The social share image is `site/assets/og-image.jpg` (1200 x 630, about 95 KB); it uses the placeholder hero photo, so re-cut it when the real photo arrives.

The home page has a short quote form (`#quote`) that posts to the same Netlify form as the contact page. A hidden `source` field records which page a request came from.
