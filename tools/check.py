#!/usr/bin/env python3
"""Cross-check every PDF and every web page for inconsistencies.

    python3 tools/check.py            → writes CHECK-REPORT.md
    python3 tools/check.py --find "60 minuts"   → shows every PDF/page containing a phrase

Checks:
 1. Coverage: which document exists in which of the 8 languages.
 2. Contact data (email, phone, web) present in every PDF.
 3. House style: VENDAVAL in capitals, tyle lowercase, no "clown" words, place-name translations, name spellings.
 4. Same document, different languages: numbers and links that appear in some languages but not in others.
 5. Broken-looking links inside PDFs.
 6. Web text keys missing in a language (from build.py).
"""
import json, re, sys, pathlib, html, collections
import pymupdf

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = json.loads((ROOT / 'content' / 'facts.json').read_text())
DATA = json.loads((ROOT / 'content' / 'data.json').read_text())
LANGS = DATA['languages']
PDF = ROOT / 'static' / 'pdf'
WEB = ROOT / 'docs'

def norm(t):
    t = t.replace('­', '').replace('’', "'")
    # letter-spaced headings ("D O S S I E R") → "DOSSIER"
    t = re.sub(r'(?<!\S)((?:\S ){3,}\S)(?!\S)', lambda m: m.group(1).replace(' ', ''), t)
    return re.sub(r'[ \t]+', ' ', t)

def pdf_lang(name):
    m = re.search(r'_([A-Z]{2})_', name)
    return m.group(1).lower() if m else None

def load_pdfs():
    out = {}
    for f in sorted(PDF.glob('*.pdf')):
        d = pymupdf.open(f)
        text = norm('\n'.join(p.get_text() for p in d))
        links = [l.get('uri') for p in d for l in p.get_links() if l.get('uri')]
        out[f.name] = {'lang': pdf_lang(f.name), 'text': text, 'links': links, 'pages': d.page_count}
    return out

def load_web():
    out = {}
    for l in LANGS:
        for f in sorted((WEB / l).rglob('index.html')):
            s = f.read_text()
            s = re.sub(r'<(script|style|svg)\b.*?</\1>', ' ', s, flags=re.S)
            links = re.findall(r'href="(https?://[^"]+)"', s)
            text = html.unescape(re.sub(r'<[^>]+>', ' ', s))
            out[str(f.relative_to(WEB))] = {'lang': l, 'text': norm(text), 'links': links}
    return out

I18N = {l: json.loads((ROOT / 'content' / 'i18n' / f'{l}.json').read_text()) for l in LANGS}
def allowed_removed(text, lang):
    # workshop tags on the website ("Clown Soap bubbles …") and "workshops in … clown" in PDFs are allowed
    tags = ' '.join(I18N[lang]['workshops']['groups']['circus']['items']) if lang in I18N else ''
    if tags: text = re.sub(r'\s+'.join(map(re.escape, tags.split())), ' ', text)
    for pat in F.get('allowed', {}).get('patterns', []):
        text = re.sub(pat, ' ', text)
    return text

def style_issues(text, lang):
    found = []
    text = allowed_removed(text, lang)
    for pat in F['banned'].get('*', []) + F['banned'].get(lang, []):
        for m in re.finditer(pat, text):
            ctx = text[max(0, m.start() - 30):m.end() + 30].replace('\n', ' ')
            found.append(f'`{m.group(0)}` … {ctx.strip()}')
    for good, bads in F['names'].items():
        for b in bads:
            for m in re.finditer(re.escape(b), text):
                if text[m.start():m.start() + len(good)] == good: continue
                found.append(f'`{b}` → should be **{good}**')
    want = F['frankfurt'].get(lang)
    if want and any(x in text for x in ('Frankfurt', 'Fráncfort', 'Francfort', 'Francoforte', 'フランクフルト')):
        if want not in text:
            found.append(f'Frankfurt written differently (should be **{want}**)')
    return sorted(set(found))

NUM = re.compile(r'(?<![\d+])(\d{1,4}(?:[.,]\d+)?)(?![\d])')
def numbers(t):
    t = re.sub(r'\+?34[\s\d]{9,}|644[\s\d]{6,}', ' ', t)  # phone
    return {n for n in NUM.findall(t)}

def main():
    if '--find' in sys.argv:
        q = sys.argv[sys.argv.index('--find') + 1].lower()
        for name, d in {**load_pdfs(), **load_web()}.items():
            n = d['text'].lower().count(q)
            if n: print(f'{n:3}  {name}')
        return
    pdfs, web = load_pdfs(), load_web()
    R = ['# Cross-check report', '', f'{len(pdfs)} PDFs · {len(web)} web pages · languages: {", ".join(LANGS)}', '']

    # 1 coverage
    R += ['## 1. Which documents exist in which language', '', '| Document | ' + ' | '.join(l.upper() for l in LANGS) + ' |', '|---|' + '---|' * len(LANGS)]
    fam_files = {}
    for fam, pat in F['families'].items():
        row, fam_files[fam] = [], {}
        for l in LANGS:
            rx = re.compile(pat.replace('{L}', l.upper()))
            hit = [n for n in pdfs if rx.search(n)]
            if hit: fam_files[fam][l] = hit[0]
            row.append('✓' if hit else '—')
        R.append(f'| {fam} | ' + ' | '.join(row) + ' |')
    R.append('')

    # 2 contact
    R += ['## 2. Contact data missing in PDFs', '']
    c = F['contact']; miss = []
    for n, d in pdfs.items():
        t = d['text'].lower(); digits = re.sub(r'\D', '', d['text'])
        lacks = [k for k, ok in (('email', c['email'].lower() in t), ('phone', c['phone_digits'] in digits), ('web', c['web'] in t)) if not ok]
        if lacks: miss.append(f'- {n}: no {", ".join(lacks)}')
    R += (miss or ['- none']) + ['']

    # 3 style
    R += ['## 3. House style (VENDAVAL capitals, tyle lowercase, no "clown" words, names, Frankfurt)', '']
    any3 = False
    for group, docs in (('PDF', pdfs), ('Web', web)):
        for n, d in docs.items():
            if not d['lang']: continue
            iss = style_issues(d['text'], d['lang'])
            if iss:
                any3 = True; R.append(f'**{group} · {n}**')
                R += [f'- {x}' for x in iss[:12]] + ([f'- … {len(iss) - 12} more'] if len(iss) > 12 else []) + ['']
    if not any3: R += ['- none', '']

    # 4 cross-language
    R += ['## 4. Same document, different languages: numbers or links not in every version', '',
          'A number or link that is only in some languages often means a fact was updated in one language only.', '']
    def compare(label, versions):
        out = []
        if len(versions) < 2: return out
        nums = {l: numbers(t) for l, (t, _) in versions.items()}
        lk = {l: {re.sub(r'^https?://(www\.)?', '', u).rstrip('/').lower() for u in ls} for l, (_, ls) in versions.items()}
        for kind, sets in (('number', nums), ('link', lk)):
            allv = set().union(*sets.values())
            for v in sorted(allv):
                if v in F.get('ignore_cross_language', []): continue
                have = [l for l in sets if v in sets[l]]
                if 0 < len(have) < len(sets) and len(have) >= len(sets) / 2:
                    out.append(f'- {kind} `{v}` missing in: {", ".join(l.upper() for l in sets if l not in have)}')
        return out
    any4 = False
    for fam, files in fam_files.items():
        out = compare(fam, {l: (pdfs[f]['text'], pdfs[f]['links']) for l, f in files.items()})
        if out: any4 = True; R += [f'**{fam}**'] + out[:25] + ([f'- … {len(out) - 25} more'] if len(out) > 25 else []) + ['']
    pages = collections.defaultdict(dict)
    for n, d in web.items():
        pages[n.split('/', 1)[1]][d['lang']] = (d['text'], d['links'])
    for p, versions in sorted(pages.items()):
        out = compare(p, versions)
        if out: any4 = True; R += [f'**Web · /{p}**'] + out[:25] + ['']
    if not any4: R += ['- none', '']

    # 5 links
    R += ['## 5. Broken-looking links in PDFs', '']
    bad = []
    for n, d in pdfs.items():
        for u in d['links']:
            if u.startswith('mailto:'): continue
            host = re.sub(r'^https?://', '', u).split('/')[0]
            if '%20' in u or ' ' in u or '.' not in host:
                bad.append(f'- {n}: `{u}`')
    R += (sorted(set(bad)) or ['- none']) + ['']

    # 6 web keys
    R += ['## 6. Web texts missing in a language', '']
    def keys(d, p=''):
        return {p + k for k in d} | {x for k, v in d.items() if isinstance(v, dict) for x in keys(v, p + k + '.')}
    i18n = {l: json.loads((ROOT / 'content' / 'i18n' / f'{l}.json').read_text()) for l in LANGS}
    ref = keys(i18n['ca']); m6 = []
    for l in LANGS:
        ms = ref - keys(i18n[l])
        if ms: m6.append(f'- {l.upper()}: {", ".join(sorted(ms))}')
    R += (m6 or ['- none']) + ['']

    R += ['## Made outside this generator (update by hand)', ''] + [f'- **{k}**: {v}' for k, v in F['external_pdfs'].items()]
    (ROOT / 'CHECK-REPORT.md').write_text('\n'.join(R) + '\n')
    print('\n'.join(R))

if __name__ == '__main__':
    main()
