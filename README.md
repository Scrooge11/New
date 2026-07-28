# Blue Water Pool — Website

White-glove weekly pool cleaning for Palm Beach County, FL.
Static, dependency-free site built by Next Wave Digital & Consulting (SIGNATURE package).

## Stack

- Hand-authored semantic HTML5 — no framework, no build step
- Token-driven CSS design system (`assets/css/styles.css`), light + dark themes
- Vanilla JS (`assets/js/`): nav, theme toggle, reduced-motion-safe scroll reveal
- Netlify: forms (`booking`, `newsletter` — both honeypot-protected), security headers via `netlify.toml`

## Deploy

Connect the repo to Netlify; publish directory is the repo root, no build command.

Before go-live, search-and-replace the placeholder domain `bluewaterpoolfl.com`
with the final domain (canonicals, OG tags, JSON-LD, `sitemap.xml`, `robots.txt`),
and set the GA4 Measurement ID (staged, commented out in every page `<head>` —
the required CSP additions are noted in `netlify.toml`).

## Pages (12)

Home · Weekly Pool Cleaning · Service Areas hub · West Palm Beach · Boca Raton ·
Delray Beach · Jupiter · About · Contact/Booking · Blog index · 2 blog posts
(+ `thanks/` confirmation and `404.html`, both noindex)

## Support

90-day support period from launch. Contact: Next Wave Digital & Consulting.
