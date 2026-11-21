"""Reads a dossier text file (dossiers/<folder>/<lang>.json).

Table rows are stored as objects {"a": …, "b": …, "c": …} so the admin (Sveltia CMS) can edit them as forms;
the templates still get plain rows [a, b, c]. Rows written as lists still work."""
import json

COLS = 'abcdef'
def _rows(x):
    if isinstance(x, list):
        return [list(v.get(k, '') for k in COLS[:len(v)]) if isinstance(v, dict) and v and set(v) <= set(COLS) else _rows(v) for v in x]
    if isinstance(x, dict): return {k: _rows(v) for k, v in x.items()}
    return x

def load(path):
    return _rows(json.loads(open(path, encoding='utf-8').read()))
