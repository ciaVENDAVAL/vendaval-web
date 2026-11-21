# VENDAVAL — update protocol

Use this every time new information arrives (a date, a name, a link, a photo, a change to a show).
Goal: one change → every language, every PDF and the website say the same thing.

## 1. Record the fact once
1. Write it in the project doc `master/VENDAVAL master fact sheet.md` (the reference for people).
2. If it is a name spelling, contact detail, place name or style rule: add it to `content/facts.json` (the reference for the checker).

## 2. Find every place that uses it
`python3 tools/check.py --find "old text"` lists every PDF and web page that contains it, in all languages.

## 3. Change the sources, in all 7 languages at once
| What | Where |
|---|---|
| Website texts | `content/i18n/<lang>.json` (ca es en de fr it ja) |
| Dates, shows, photos, links, credits, downloads | `content/data.json` |
| Dossiers made here | `dossiers/<name>/<lang>.md` and the copies in the project |
| PDFs made elsewhere | see "Made outside this generator" at the end of the check report: these need a manual edit or a rebuild |

Never update one language only. If a translation is unsure, write it anyway and add it to the list of texts that still need a native-speaker check.

## 4. Rebuild
```
python3 dossiers/build_dossiers.py <name>   # only for dossiers that changed
python3 build.py
python3 tools/check.py                      # writes CHECK-REPORT.md
```

## 5. Read the report
- **Section 1:** missing languages → add to the to-do list.
- **Sections 2, 3, 5:** contact data, house style, broken links → fix now (or note it if the PDF is made elsewhere).
- **Section 4:** a number or link that is only in some languages usually means a fact changed in one language only. Fix the others, or add the item to `ignore_cross_language` in `content/facts.json` if the difference is intended.
- **Section 6:** web text missing in a language → translate.

## 6. Publish and save
1. Look at the changed pages (phone and computer width).
2. Commit with a message saying what changed; push to GitHub once it is linked.
3. Update the preview.
4. Copy the changed dossier texts to the project.
5. Update `master/VENDAVAL email templates.md` if links or file names changed.

## House style the checker enforces
- VENDAVAL always in capitals, also in displayed addresses (www.VENDAVAL.cat, VENDAVAL@anartist.org); tyle fernández always lowercase.
- Performers are not called clowns (clown/pallasso/payaso…). Clown is fine as a discipline or skill (workshops, artist skills, lists like "stilts, unicycle, clown") and in "Pallassos sense Fronteres"; the checker allows those.
- Catalan: no "walkact", no "tothom".
- Frankfurt am Main in each language: Frankfurt del Main (CA), Fráncfort del Meno (ES), Francfort-sur-le-Main (FR), Francoforte sul Meno (IT), Frankfurt am Main (EN, DE), フランクフルト (JA).
- Name spellings: see `names` in `content/facts.json`.
- Prices never on the website or in public PDFs.
- Dossiers short, website long.

## Link previews and icons
- `tools/og.py` (run by build.py) makes the favicon/app icons from the logo and a 1200×630 preview per page in `docs/og/`:
  photo pages = whole photo on a blurred copy (never cropped); agenda, artists, downloads, crew = screenshot per language.
- Previews are only made when missing. After changing a page's text or photo: `python3 build.py --og`.
- Domain: while `site.domain_live` is false in content/data.json, links and previews use the GitHub address.
  When vendaval.cat points to GitHub, set it to true, rebuild and push (this adds the CNAME file), then tick "Enforce HTTPS".

## Editing without code (admin, on-page editor, workflows) — since 21 Nov 2026
- **www.VENDAVAL.cat/admin/** — start page; forms (Sveltia CMS, served from this site) for web texts, easy read, site data
  (agenda, photos, artists, downloads, credits) and the dossier/rider texts. Each Save = 1 commit. Login: one GitHub
  fine-grained token (only `vendaval-web`, Contents: read and write) — steps on the start page. Only tyle has one.
- **Any page + `#edit`** — tap a text, a photo or a PDF link; Publish = 1 commit. Same token.
- After every push **build.yml** runs: `tools/translate.py --only=content` (CA↔ES↔EN with Softcatalà, the only "model", run inside
  the GitHub job) → `build.py` → `check.py` → commits `docs/` → Pages build. House-style problems open a GitHub issue.
  **dossiers.yml** (push to `dossiers/**`): translate dossier texts → `tools/dossier_ci.py` rebuilds only the changed
  folders/languages → layout check (page count, text over the bottom photo strip; on failure the old PDF stays) → site build.
- DE, FR, IT, JA are never machine-translated: see CHECK-REPORT.md §8. Translate, remove the entry from
  `content/i18n/_needs-translation.json`; for dossiers, the PDF of that language is rebuilt when its text file changes.
- Photos: originals in `source-images/`; `docs/img/.sources.json` remembers their hashes, so a replaced original (same name)
  gets new web sizes and its ready-made copy in `static/img/` is removed. Photo fields accept a slug or a file name.
- Calendar gigs (entries with `uid`) are changed in the Nextcloud calendar, not in the admin.
- Forms changed? `python3 tools/make_config.py` (validates nothing by itself: check with Sveltia's JSON schema,
  `npm pack @sveltia/cms` → `schema/sveltia-cms.json`). Update Sveltia: copy `dist/sveltia-cms.js` + `dist/chunks/` into
  `static/admin/web/sveltia/`.
