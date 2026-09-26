# Biocity Healthcare — Website

Static marketing website for Biocity Healthcare (NABL-accredited diagnostics, home sample
collection, full-body health checkups). Plain HTML, CSS and JavaScript — no build step, no
framework, no npm install. Clone it and open it.

## Structure

```
.
├── index.html            # Home page
├── pages/                # 25 inner pages (about, contact, blog, tests, policies, …)
├── assets/
│   ├── site.css          # All shared styling
│   ├── site.js           # All shared behaviour (nav, theme, search, carousels)
│   ├── data/catalog.json # Test catalog, loaded at runtime by the Find-a-Test search
│   └── awards|certs|lab|social|team|welfare/   # Images
├── docs/                 # Internal notes — not part of the published site
├── robots.txt            # Currently blocks search engines (see "Before going live")
├── .nojekyll             # Tells GitHub Pages to serve files exactly as written
└── .github/workflows/pages.yml   # Publishes the site automatically
```

All links are relative, so the folder can be served from any static host as-is.

## Run locally

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Opening `index.html` directly also works, except the Find-a-Test search — browsers block
`catalog.json` from loading over `file://`, so use the local server for that.

## How it gets published

Pushing to `main` triggers `.github/workflows/pages.yml`, which uploads the whole repository
to GitHub Pages. There is nothing to build and nothing to run manually — push, wait about a
minute, refresh.

Live at: https://nikhilgupta24.github.io/biocity-healthcare/

## Before going live on the real domain

Two things in this repo exist only because it is currently a preview/UAT build:

1. **`robots.txt` blocks every search engine.** That is deliberate — it stops the preview from
   competing with the live site in Google. Delete the file when this becomes the real site.
2. **No custom domain is configured.** To serve this on a domain, add a `CNAME` file containing
   the domain (or set it under *Settings → Pages*), **and** add the matching DNS record at the
   registrar. Both halves are required — doing only the first makes the site unreachable.
