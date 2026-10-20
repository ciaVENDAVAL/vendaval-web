# vendaval.cat

Multilingual static website for Cia. VENDAVAL, served by GitHub Pages from `docs/`.

- Texts: `content/i18n/<lang>.json` (one per language; all strings are HTML)
- Facts: `content/data.json` (shows, agenda, artists, downloads, press photos)
- Layout: `src/page.html` (+ `agenda_item.html`, `dlbox.html`, `contact.html`), `src/style.css`, `src/site.js`, `src/icons/`
- Ready-made web images, fonts and PDFs: `static/` · original photos: `source-images/`
- Dossier PDFs: `dossiers/<name>/<lang>.md` + `dossier.json` → `python3 dossiers/build_dossiers.py <name>`

Build: `pip install jinja2 pillow markdown pymupdf playwright && python3 build.py`
Short links for emails: see `LINKS.txt`.
