# JS Contracting & Electrical Services

Brand package and website for JS Contracting & Electrical Services.

- **Website**: plain HTML, CSS and a little JavaScript. No build step, no framework. Open `index.html` in a browser or drop the folder on any static host.
- **Brand**: logo files, colors, type and usage rules. Open `brand/index.html` for the guidelines.

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
```

## Before going live: fill in the placeholders

Everything below is a placeholder. Search the project for `000-0000`, `yourdomain`, `Your Town`, `00000000` and `[Owner name]`.

| Placeholder | Where | Replace with |
|---|---|---|
| `(000) 000-0000` and `+10000000000` | header, footer, hero, contact page, `site-src/gen_site.py` | the business phone (the `tel:` version needs country code, digits only) |
| `office@yourdomain.com` | footer, contact page | the business email |
| `Your Town, ST` | service area section, footer, contact page | the town and state, plus the real service radius (currently "about 30 miles") |
| `Lic. #00000000` and `#00000000` | footer, about page | electrical license and contractor registration numbers |
| `[Owner name]` | about page, brand guide mockups | the owner's name |
| `20+ years in the electrical trade`, manufacturer training line | about page | real credentials, or delete the lines that do not apply |
| Hours | home and contact pages | real hours |
| `https://www.yourdomain.com` | every page `<head>`, `sitemap.xml`, `robots.txt` | the final domain |

The fastest way is to edit the constants at the top of `site-src/gen_site.py` and run `python3 site-src/gen_site.py .` which rewrites all five pages. Editing the HTML files directly works too.

Also decide whether the site should mention the previous company. It currently does not.

## Previewing

Open `index.html` directly, or for a local server:

```
npx http-server . -p 8080
```

## Hosting

Any static host works. Two easy options:

**Netlify (recommended, free tier, the quote form works out of the box).** Create a site from this repo or drag the folder onto app.netlify.com. The form on `contact.html` is already marked up for Netlify Forms, so submissions show up in the Netlify dashboard and can be emailed to the owner (Site settings, Forms, Notifications). `netlify.toml` is included.

**GitHub Pages.** Settings, Pages, deploy from the `main` branch root. The `.nojekyll` file is already there. GitHub Pages cannot process forms, so either point the form's `action` at a service like Formspree (`https://formspree.io/f/your-id`) or keep the phone and email as the contact path. If the form cannot send, the page shows the phone and email instead.

After the domain is live, submit `sitemap.xml` in Google Search Console and create a Google Business Profile using `brand/logo/png/js-icon-1024.png` as the profile image and `assets/og-image.png` as a cover.

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
