"""PDFs replaced by hand (from the admin or the on-page editor) are marked in content/data.json:
downloads.<key>.manual = "yyyy-mm-dd" (all languages) or {"de": "yyyy-mm-dd", …}.
Build scripts call skip(path) before writing a PDF: a marked file is kept unless the script runs with --force
(or the commit message has [rebuild-pdf] in the dossiers workflow, which passes --force).
Importing this module removes --force from sys.argv, so the scripts' language arguments stay as they were."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
FORCE = '--force' in sys.argv
sys.argv[:] = [a for a in sys.argv if a != '--force']
SKIPPED = []

def manual_files():
    data = json.loads((ROOT/'content'/'data.json').read_text(encoding='utf-8'))
    out = {}
    for key, d in data['downloads'].items():
        m = d.get('manual')
        if not m: continue
        for lang, url in d['files'].items():
            day = m if isinstance(m, str) else m.get(lang)
            if day: out[pathlib.Path(url).name] = (key, lang, day)
    return out

def skip(path):
    """True if this PDF was replaced by hand and must not be overwritten."""
    if FORCE: return False
    hit = manual_files().get(pathlib.Path(path).name)
    if hit:
        SKIPPED.append(pathlib.Path(path).name)
        print(f'  skipped {pathlib.Path(path).name}: replaced by hand on {hit[2]} (run with --force to rebuild)')
        return True
    return False
