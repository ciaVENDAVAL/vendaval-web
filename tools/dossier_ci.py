#!/usr/bin/env python3
"""Rebuild only the dossier/rider PDFs whose texts changed (run by .github/workflows/dossiers.yml).

  python3 tools/dossier_ci.py <old-commit> [--force]

1. Finds which dossiers/<folder>/<lang>.(json|md) changed since <old-commit> (also uncommitted changes, e.g. the
   auto-translation). A changed template / dossier.json in a folder = every language of that folder.
2. Runs the folder's build script for those languages. PDFs replaced by hand ("manual" in content/data.json) are
   kept unless --force (dossiers/manual.py).
3. Layout check on each new PDF against the old one: the page count must stay the same, and page 1 must not get more
   text over a photo strip at the bottom of the page. A PDF that fails is put back to the old version.
4. Warns about PDFs over 3 MB (APCC limit).
Writes a Markdown summary to $GITHUB_STEP_SUMMARY (or stdout). Exit 1 if a layout check failed."""
import os, re, subprocess, sys, pathlib, json
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT/'dossiers'; PDF = ROOT/'static'/'pdf'
MD_FOLDERS = ['imaginary-friend', 'el-joc-etern', 'ani-arqui', 'easy-brass', 'easy-friend', 'easy-stilts']
SCRIPTS = {'brass': 'dossiers/brass/build.py', 'concert': 'dossiers/concert/build.py',
           'riders-brass': 'dossiers/riders-brass/build.py', 'stilts-workshops': 'dossiers/stilts-workshops/build.py'}
LANGS = json.loads((ROOT/'content'/'data.json').read_text())['languages']

def sh(*a, **k): return subprocess.run(a, cwd=ROOT, capture_output=True, text=True, **k)

def changed_jobs(old):
    files = set(sh('git', 'diff', '--name-only', old, '--', 'dossiers').stdout.split())
    files |= set(sh('git', 'diff', '--name-only', '--', 'dossiers').stdout.split())
    files |= set(sh('git', 'ls-files', '--others', '--exclude-standard', 'dossiers').stdout.split())
    jobs = {}
    for f in files:
        parts = f.split('/')
        if len(parts) < 3 or parts[1] == 'assets': continue
        folder, name = parts[1], parts[-1]
        if folder not in SCRIPTS and folder not in MD_FOLDERS: continue
        stem, ext = os.path.splitext(name)
        if stem in LANGS and ext in ('.json', '.md') and len(parts) == 3: jobs.setdefault(folder, set()).add(stem)
        else: jobs[folder] = {'*'}
    out = {}
    for folder, langs in jobs.items():
        have = sorted(p.stem for p in (D/folder).glob('*.md' if folder in MD_FOLDERS or folder == 'stilts-workshops' else '*.json')
                      if p.stem in LANGS)
        out[folder] = have if '*' in langs else sorted(l for l in langs if l in have)
    return {k: v for k, v in out.items() if v}

def snapshot():
    return {p.name: p.stat().st_mtime for p in PDF.glob('*.pdf')}

def layout(path, old_bytes):
    import pymupdf
    new = pymupdf.open(path)
    if not old_bytes: return None
    old = pymupdf.open(stream=old_bytes, filetype='pdf')
    if len(new) != len(old): return f'page count changed {len(old)} → {len(new)}'
    def over(doc):
        pg = doc[0]; H = pg.rect.height; n = 0
        strips = [pymupdf.Rect(i['bbox']) for i in pg.get_image_info() if i['bbox'][3] >= H - 4 and (i['bbox'][3] - i['bbox'][1]) < H * 0.6]
        for b in pg.get_text('blocks'):
            r = pymupdf.Rect(b[:4])
            if b[4].strip() and any(r.intersects(s) and (r & s).height > 2 for s in strips): n += 1
        return n
    a, b = over(old), over(new)
    if b > a: return f'text runs into the photo strip at the bottom of page 1 ({b} blocks, was {a})'
    return None

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    force = '--force' in sys.argv
    old = args[0] if args else 'HEAD~1'
    jobs = changed_jobs(old)
    rep = ['## Dossier PDFs', '']
    if not jobs:
        rep.append('No dossier text changed.'); finish(rep); return 0
    before = {p.name: p.read_bytes() for p in PDF.glob('*.pdf')}
    t0 = snapshot(); fail = False
    for folder, langs in sorted(jobs.items()):
        cmd = [sys.executable, SCRIPTS[folder]] + langs if folder in SCRIPTS else [sys.executable, 'dossiers/build_dossiers.py', folder] + langs
        if force: cmd.append('--force')
        r = sh(*cmd)
        rep.append(f'**{folder}** · {", ".join(l.upper() for l in langs)}')
        rep += [f'- {x.strip()}' for x in (r.stdout + r.stderr).splitlines() if 'skipped' in x]
        if r.returncode:
            fail = True; rep.append(f'- ❌ build failed:\n```\n{(r.stderr or r.stdout)[-1500:]}\n```')
    for p in sorted(PDF.glob('*.pdf')):
        if t0.get(p.name) == p.stat().st_mtime: continue
        msg = layout(p, before.get(p.name))
        mb = p.stat().st_size / 1e6
        if msg:
            fail = True
            if p.name in before: p.write_bytes(before[p.name])
            rep.append(f'- ❌ {p.name}: {msg} — the old PDF stays online. Shorten the text (or ask a Claude session).')
        else:
            rep.append(f'- ✓ {p.name} ({mb:.1f} MB)' + (' — ⚠ over 3 MB (APCC limit)' if mb > 3 else ''))
    finish(rep)
    return 1 if fail else 0

def finish(rep):
    out = os.environ.get('GITHUB_STEP_SUMMARY')
    text = '\n'.join(rep) + '\n'
    if out: open(out, 'a').write(text)
    print(text)

if __name__ == '__main__':
    sys.exit(main())
