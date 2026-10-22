# vendaval-web (PUBLIC)

Website vendaval.cat and all promoter material of Cia. VENDAVAL (show dossiers, riders, flyer). This repo is public: never add fees, budgets, NIF, personal data or application answers. Those go in the private repo `ciaVENDAVAL/vendaval-docs` (see its `INDEX.md` for where every document lives).

- Facts: Project doc `master/VENDAVAL master fact sheet.md` (claude.ai Project "VENDAVAL"). Update it and every language when a fact changes.
- How to update: `UPDATING.md`. Check before pushing: `python3 tools/check.py`.
- Build: `python3 build.py` (site) · `python3 dossiers/build_dossiers.py <folder> [langs]` (imaginary-friend, el-joc-etern, ani-arqui, easy-brass, easy-friend, easy-stilts) · `python3 dossiers/stilts-workshops/build.py` · `python3 dossiers/brass/build.py` · `python3 tools/flyer.py ca es en`.
- Push: build, commit (author tyle fernández <VENDAVAL@anartist.org>), `git push origin HEAD:main`. GitHub Pages serves `docs/`.
- Easy read: web texts in `content/easy/<lang>.json` (shown with the accessibility option), easy-read dossiers in `dossiers/easy-*/`. Not validated by easy-read users yet: no official Lectura Fàcil / Leichte Sprache logo.
- House style: VENDAVAL always in capitals, also in addresses as displayed (www.VENDAVAL.cat, VENDAVAL@anartist.org; URL paths stay lowercase); no salsa in the genre lists (funk, Balkan, swing, cumbia); tyle fernández lowercase; never "tothom"; don't call performers clowns in show texts; never crop photos; prices never public; place names in each language's form; 8 languages kept consistent.
