"""Change one language, the others follow — VENDAVAL version (7 languages).

After a push, finds every text that changed in ONE language and:
  · CA, ES, EN: translates it into the other two of CA/ES/EN with Softcatalà's open-source neural models
    (run here, no account, no key, no Google/Amazon). Changed in two of them = translated by hand: left alone.
  · DE, FR, IT, JA: never machine-translated. The old text stays online and the key goes on the list
    content/i18n/_needs-translation.json (shown in CHECK-REPORT.md §8) until a person or a Claude session
    translates it and removes the entry. A language changed in the same push is taken off the list.
A value that was the same in every language (a number, a file name, a link) is copied to all languages as it is.

  python3 tools/translate.py <old-commit>            (pip install ctranslate2 sentencepiece)
  python3 tools/translate.py <old-commit> --dry-run  (shows what it would do)
  python3 tools/translate.py <old-commit> --only=content    (web texts only; --only=dossiers: dossier texts only)
  python3 tools/translate.py --download              (fetch the models once)

Covers (each file one per language): web texts content/i18n, easy read content/easy, dossier/rider texts
dossiers/brass, concert, riders-brass (JSON, key by key) and the Markdown dossiers (paragraph by paragraph).
Run by .github/workflows/build.yml and dossiers.yml. A commit message containing [no-translate] skips it."""
import json, os, re, subprocess, sys, urllib.request, datetime, difflib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# ---- settings ----
LANGS = ["ca", "es", "en", "de", "fr", "it", "ja"]   # the first one is the reference for which keys exist
AUTO = ["ca", "es", "en"]                            # machine-translated among themselves (Softcatalà)
JSON_FILES = ["content/i18n/{lang}.json", "content/easy/{lang}.json",
              "dossiers/brass/{lang}.json", "dossiers/concert/{lang}.json", "dossiers/riders-brass/{lang}.json"]
MD_FILES = ["dossiers/imaginary-friend/{lang}.md", "dossiers/el-joc-etern/{lang}.md", "dossiers/ani-arqui/{lang}.md",
            "dossiers/easy-brass/{lang}.md", "dossiers/easy-friend/{lang}.md", "dossiers/easy-stilts/{lang}.md",
            "dossiers/stilts-workshops/{lang}.md"]
NEEDS = "content/i18n/_needs-translation.json"
SKIP = re.compile(r"^(html_lang|lang_name|home_order(\..*)?|show\.[a-z]+\.status)$")   # keys never translated
# ------------------
FACTS = json.loads((ROOT / "content/facts.json").read_text())
KEEP = sorted(set(FACTS.get("names", {})) | {"VENDAVAL", "VENDAVAL Brass", "Amigui Imaginari", "El Joc Etern", "Freak Frac",
              "Windy", "Chimera Opera", "Ani Arqui", "tyle fernández {elli}", "Cia. Filigranes", "La Senyal", "Jordi Torrens",
              "Stefano Ferraro", "Juan Lichter"}, key=len, reverse=True)
# names and words with a fixed form per language (the model must not invent its own):
TERMS = [FACTS["frankfurt"],
         {"ca": "Amigui Imaginari", "es": "Amigui Imaginari", "en": "Imaginary Friend"},
         {"ca": "xanquista", "es": "zanquista", "en": "stilt walker"},
         {"ca": "xanquistes", "es": "zanquistas", "en": "stilt walkers"},
         {"ca": "xanques", "es": "zancos", "en": "stilts"},
         {"ca": "monocicle", "es": "monociclo", "en": "unicycle"},
         {"ca": "peluix", "es": "peluche", "en": "soft toy"},
         {"ca": "cercavila", "es": "pasacalles", "en": "walkabout"},
         {"ca": "diversitat funcional", "es": "diversidad funcional", "en": "differently abled people"},
         {"ca": "totes les persones", "es": "todas las personas", "en": "everyone"}]
EASY_NOTE = "check easy-read rules (short sentences, digits)"

def git_show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

# ---------- translation engine: Softcatalà's open neural models (no Google, no Amazon) ----------
# https://github.com/Softcatala/nmt-models — MIT licence, the same models as softcatala.org/traductor,
# downloaded from softcatala.org and run here with CTranslate2. CA↔ES and CA↔EN directly; ES↔EN via CA.
import unicodedata, zipfile, shutil
MODELS = {"cat-eng": "cat-eng-2024-09-29", "eng-cat": "eng-cat-2024-09-24",
          "cat-spa": "cat-spa-2022-11-17", "spa-cat": "spa-cat-2022-11-16"}
MODEL_URL = "https://www.softcatala.org/pub/softcatala/opennmt/models/2022-11-22/{}.zip"
CODE = {"ca": "cat", "es": "spa", "en": "eng"}
MODELS_DIR = Path(os.environ.get("NMT_MODELS", Path.home() / ".cache/vendaval-nmt"))
_loaded = {}

def model(pair):
    if pair in _loaded: return _loaded[pair]
    import ctranslate2, sentencepiece as spm
    d = MODELS_DIR / pair
    if not (d / "ctranslate2").exists():
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        z = MODELS_DIR / f"{pair}.zip"
        print(f"downloading model {MODELS[pair]} …", flush=True)
        urllib.request.urlretrieve(MODEL_URL.format(MODELS[pair]), z)
        with zipfile.ZipFile(z) as zf:
            for n in zf.namelist():
                parts = n.split("/")
                if len(parts) > 1 and parts[1] in ("ctranslate2", "tokenizer") and not n.endswith("/"):
                    out = d / "/".join(parts[1:]); out.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(n) as src, open(out, "wb") as dst: shutil.copyfileobj(src, dst)
        z.unlink()
    _loaded[pair] = (ctranslate2.Translator(str(d / "ctranslate2"), device="cpu", inter_threads=2),
                     spm.SentencePieceProcessor(model_file=str(d / "tokenizer" / "sp_m.model")))
    return _loaded[pair]

SYMBOL = re.compile(r"([\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]+)")   # emoji runs: kept as they are
SENT = re.compile(r"(?<=[.!?…])\s+(?=[\"«“¿¡(]?[A-ZÀ-ÖØ-Þ0-9])")

def _raw(pair, sentences):
    tr, sp = model(pair)
    batch = [sp.encode(t, out_type=str) for t in sentences]
    res = tr.translate_batch(batch, beam_size=4, max_decoding_length=512)
    return [sp.decode(r.hypotheses[0]) for r in res]

def _fix_unknown(src, out):
    """The English model can't write some letters (e.g. á) and prints ⁇: copy those words from the source."""
    if "⁇" not in out: return out
    out = re.sub(r"\s*⁇\s*", "⁇", out)
    words = re.findall(r"[\w'’·-]+", src)
    def repl(m):
        tok = m.group(0)
        pat = re.compile("^" + ".+?".join(re.escape(x) for x in tok.split("⁇")) + "$")
        return next((w for w in words if pat.match(w)), tok.replace("⁇", ""))
    return re.sub(r"[\w'’·-]*⁇[\w'’·-]*", repl, out)

def translate_line(text, src, dst):
    """One line of plain text (no markdown): keeps emojis, names, {placeholders}, sentence by sentence."""
    if not text.strip(): return text
    lead, core, trail = re.match(r"^(\s*)(.*?)(\s*)$", text, re.S).groups()
    parts = SYMBOL.split(core)
    out = []
    for i, part in enumerate(parts):
        if i % 2 or not part.strip(): out.append(part); continue
        l2, mid, t2 = re.match(r"^(\s*)(.*?)(\s*)$", part, re.S).groups()
        holds = {}
        def hold(v):
            k = f"Zq{len(holds)}x"; holds[k] = v; return k
        # links and **bold**/*italic* are translated on their own and put back; addresses, {n}, 6 × 4… stay
        m = re.sub(r"\[([^\]]*)\](\([^)]*\))", lambda x: hold(f"[{translate_line(x.group(1), src, dst)}]{x.group(2)}"), mid)
        m = re.sub(r"(\*\*|__|\*)(?=\S)(.+?)(?<=\S)\1", lambda x: hold(f"{x.group(1)}{translate_line(x.group(2), src, dst)}{x.group(1)}"), m)
        m = re.sub(r"\{\w+\}|\d+(?:[.,]\d+)?\s*[×x]\s*\d+(?:[.,]\d+)?|https?://[^\s)]+|`[^`]*`", lambda x: hold(x.group(0)), m)
        for term in sorted(TERMS, key=lambda t: -len(t.get(src, ""))):   # fixed names: held, put back in the target form
            if term.get(src) and term.get(dst) and term[src][0].isupper():
                m = re.sub(rf"(?<!\w){re.escape(term[src])}(?!\w)", lambda x: hold(term[dst]), m)
            elif term.get(src) and term.get(dst):
                m = re.sub(rf"(?<!\w){re.escape(term[src])}(?!\w)", term[dst], m)
        for k in KEEP:
            m = re.sub(rf"(?<!\w){re.escape(k)}(?!\w)", lambda x: hold(x.group(0)), m)
        sents = SENT.split(m)
        pair_path = [(src, dst)] if "ca" in (src, dst) else [(src, "ca"), ("ca", dst)]
        res = sents
        for a, b in pair_path:
            prev = res
            res = _raw(f"{CODE[a]}-{CODE[b]}", res)
            res = [_fix_unknown(p, r) for p, r in zip(prev, res)]
        t = " ".join(res)
        for k, v in holds.items():
            if k in t: t = t.replace(k, v)
            else: t = re.sub(re.escape(k[:-1]) + r"\s*x?", v, t, flags=re.I) if re.search(re.escape(k[:-1]), t, re.I) else t + " " + v
        for k in KEEP:   # names must come out exactly as written
            if k in mid and k not in t:
                loose = re.compile(r"\s*".join(re.escape(w) for w in k.split()), re.I)
                t = loose.sub(k, t)
        out.append(l2 + t + t2)
    return lead + "".join(out) + trail

def translate_markdown(text, src, dst):
    """Line by line; list/heading/quote markers are kept, links keep their address (see translate_line)."""
    lines = []
    for line in text.split("\n"):
        prefix, rest = re.match(r"^(\s*(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+|>\s*)*)(.*)$", line).groups()
        lines.append(prefix + (translate_line(rest, src, dst) if rest.strip() else rest))
    return "\n".join(lines)

def translate(texts, src, dst):
    return [translate_markdown(t, src, dst) if "\n" in t else translate_line(t, src, dst) for t in texts]


# ---------- only the sentences that changed are translated again (the rest of a hand-polished text stays) ----------
def sentences(t): return [x for x in SENT.split(t.strip())] if t and t.strip() else []
def update(old_src, new_src, old_dst, src, dst):
    if not old_src or not old_dst or "\n" in new_src:
        return translate([new_src], src, dst)[0]
    a, b, d = sentences(old_src), sentences(new_src), sentences(old_dst)
    if len(a) != len(d): return translate([new_src], src, dst)[0]
    out = []
    for op, a1, a2, b1, b2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == "equal": out += d[a1:a2]
        elif op != "delete": out += translate([" ".join(b[b1:b2])], src, dst)
    return " ".join(out)

# ---------- helpers ----------
def leaves(x, path=()):
    if isinstance(x, dict):
        for k, v in x.items(): yield from leaves(v, path + (k,))
    elif isinstance(x, list):
        for i, v in enumerate(x): yield from leaves(v, path + (i,))
    elif isinstance(x, str): yield path, x

def get(x, path):
    for p in path:
        try: x = x[p]
        except (KeyError, IndexError, TypeError): return None
    return x

def put(x, path, value):
    for i, p in enumerate(path[:-1]):
        nxt = path[i + 1]
        if isinstance(x, dict) and p not in x: x[p] = [] if isinstance(nxt, int) else {}
        x = x[p]
    if isinstance(x, list) and isinstance(path[-1], int):
        while len(x) <= path[-1]: x.append("")
    x[path[-1]] = value

needs = {}   # (file, key) -> entry
def load_needs():
    p = ROOT / NEEDS
    for e in (json.loads(p.read_text()) if p.exists() else []): needs[(e["file"], e["key"])] = e
def flag(file, key, langs, text, note=None):
    if not langs: return
    e = needs.setdefault((file, key), {"file": file, "key": key, "langs": [], "date": TODAY, "text": ""})
    e["langs"] = [l for l in LANGS if l in set(e["langs"]) | set(langs)]
    e["text"] = text[:400]; e["date"] = TODAY
    if note: e["note"] = note
def unflag(file, key, langs):
    e = needs.get((file, key))
    if not e: return
    e["langs"] = [l for l in e["langs"] if l not in langs]
    if not e["langs"]: del needs[(file, key)]
def save_needs():
    p = ROOT / NEEDS
    items = sorted(needs.values(), key=lambda e: (e["file"], e["key"]))
    if items or p.exists(): p.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n")

TODAY = datetime.date.today().isoformat()
done = []

def decide(changed, src_lang_text):
    """Which languages get a machine translation, from which source."""
    auto_changed = [l for l in AUTO if l in changed]
    src = auto_changed[0] if len(auto_changed) == 1 else None
    targets = [l for l in AUTO if l != src and l not in changed] if src else []
    return src, targets

# ---------- JSON files: key by key ----------
def do_json(tpl, old_rev, dry):
    paths = {l: tpl.format(lang=l) for l in LANGS if (ROOT / tpl.format(lang=l)).exists()}
    if not paths: return
    old = {l: json.loads(git_show(old_rev, p) or "{}") for l, p in paths.items()}
    new = {l: json.loads((ROOT / p).read_text()) for l, p in paths.items()}
    ref = LANGS[0] if LANGS[0] in new else next(iter(new))
    easy = "/easy/" in tpl
    touched = set()
    keyset = {p for l in new for p, _ in leaves(new[l])}
    for path in sorted(keyset, key=lambda p: [str(x) for x in p]):
        key = ".".join(map(str, path))
        if SKIP.match(key) or get(new[ref], path) is None and all(get(new[l], path) is None for l in new if l != ref): continue
        changed = [l for l in new if get(new[l], path) != get(old[l], path)]
        if not changed: continue
        unflag(tpl, key, changed)
        olds = {get(old[l], path) for l in new}
        # language-neutral value (same everywhere before: a number, a link, a file name): copy it
        if len(changed) == 1 and len(olds) == 1 and None not in olds:
            v = get(new[changed[0]], path)
            for l in new:
                if l not in changed:
                    if not dry: put(new[l], path, v)
                    touched.add(l)
            done.append(f"{tpl.format(lang='*')} · {key}: copied to every language (same in all before)")
            continue
        src, targets = decide(changed, None)
        if src and isinstance(get(new[src], path), str):
            text = get(new[src], path)
            for dst in targets:
                if dst not in new: continue
                if not dry: put(new[dst], path, update(get(old[src], path), text, get(new[dst], path), src, dst))
                touched.add(dst)
                done.append(f"{tpl.format(lang='*')} · {key}: {src.upper()} → {dst.upper()}")
        rest = [l for l in new if l not in changed and l not in targets]
        if rest:
            first = next(l for l in changed if l in new)
            flag(tpl, key, rest, str(get(new[first], path) or ""), EASY_NOTE if easy else None)
            done.append(f"{tpl.format(lang='*')} · {key}: needs translation → {', '.join(x.upper() for x in rest)}")
    if not dry:
        for l in touched:
            p = ROOT / paths[l]; txt = p.read_text()
            ind = (re.search(r'\n( +|\t)"', txt) or [None, "  "])[1]
            p.write_text(json.dumps(new[l], ensure_ascii=False, indent=ind) + ("\n" if txt.endswith("\n") else ""))

# ---------- Markdown dossiers: paragraph by paragraph ----------
def blocks(t): return [b for b in re.split(r"\n\s*\n", (t or "").strip("\n"))] if t and t.strip() else []
def is_neutral(b): return b.lstrip().startswith("<!--") or not re.search(r"[A-Za-zÀ-ÿ぀-ヿ一-鿿]{3}", b)
def do_md(tpl, old_rev, dry):
    paths = {l: tpl.format(lang=l) for l in LANGS if (ROOT / tpl.format(lang=l)).exists()}
    if not paths: return
    old = {l: git_show(old_rev, p) for l, p in paths.items()}
    new = {l: (ROOT / p).read_text() for l, p in paths.items()}
    changed = [l for l in paths if new[l] != old[l]]
    if not changed: return
    for l in changed: unflag(tpl, "(whole file)", [l])
    src, targets = decide(changed, None)
    easy = "/easy-" in tpl
    if src:
        ob, nb = blocks(old[src]), blocks(new[src])
        sm = difflib.SequenceMatcher(a=ob, b=nb, autojunk=False)
        for dst in targets:
            db = blocks(new[dst])
            if old[src] is None or len(db) != len(ob):
                flag(tpl, "(whole file)", [dst], f"{src.upper()} changed; {dst.upper()} has a different number of paragraphs: translate by hand")
                done.append(f"{tpl.format(lang='*')}: {src.upper()} → {dst.upper()} not possible (paragraphs differ) — needs translation")
                continue
            out = []
            for op, a1, a2, b1, b2 in sm.get_opcodes():
                if op == "equal": out += db[a1:a2]
                elif op == "delete": pass
                else:
                    seg = nb[b1:b2]
                    if dry: out += seg
                    elif op == "replace" and a2 - a1 == b2 - b1:   # same paragraphs, edited: only the changed sentences
                        out += [b if is_neutral(b) else update(o, b, x, src, dst) for o, b, x in zip(ob[a1:a2], seg, db[a1:a2])]
                    else: out += [b if is_neutral(b) else translate([b], src, dst)[0] for b in seg]
            if not dry: (ROOT / paths[dst]).write_text("\n\n".join(out) + "\n")
            done.append(f"{tpl.format(lang='*')}: {src.upper()} → {dst.upper()} ({sum(1 for o in sm.get_opcodes() if o[0] != 'equal')} change(s))")
    rest = [l for l in paths if l not in changed and l not in targets]
    if rest:
        first = changed[0]
        ob, nb = blocks(old[first]), blocks(new[first])
        diff = [b for b in nb if b not in ob]
        flag(tpl, "(whole file)", rest, (f"{first.upper()} changed: " + " ¶ ".join(diff))[:400], EASY_NOTE if easy else None)
        done.append(f"{tpl.format(lang='*')}: needs translation → {', '.join(x.upper() for x in rest)}")

if __name__ == "__main__":
    if "--download" in sys.argv:
        for pair in MODELS: model(pair)
        raise SystemExit(0)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if not args: raise SystemExit(__doc__)
    if dry:   # no models needed to list the jobs
        translate = lambda texts, s, d: texts
    only = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--only=")), None)   # --only=content | --only=dossiers
    pick = lambda ts: [t for t in ts if not only or t.startswith(only + "/")]
    load_needs()
    for t in pick(JSON_FILES): do_json(t, args[0], dry)
    for t in pick(MD_FILES): do_md(t, args[0], dry)
    if not dry: save_needs()
    print("\n".join(done) or "Nothing to translate.")
    Path(os.environ.get("TRANSLATED_LIST", "/dev/null")).write_text("\n".join(done))
