"""Builds static/admin/web/config.yml (Sveltia CMS, the forms admin at www.VENDAVAL.cat/admin/web/).

Every form is generated from the Catalan files, so every key gets a field and nothing is dropped on save:
  content/i18n/ca.json, content/easy/ca.json, content/data.json, dossiers/<folder>/ca.json and the Markdown dossiers.
Run again after adding or removing keys:   python3 tools/make_config.py      (pip install pyyaml)
Not in the forms on purpose: content/facts.json (checker), content/extracted.json, site.form_access_key, originals,
substitutes, artist_gender, languages; dossier templates and fonts."""
import json, pathlib, re, yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT/'static'/'admin'/'web'/'config.yml'
LANGS = ['ca', 'es', 'en', 'de', 'fr', 'it', 'ja']
LANG_NAMES = {'ca': 'Català', 'es': 'Castellano', 'en': 'English', 'de': 'Deutsch', 'fr': 'Français', 'it': 'Italiano', 'ja': '日本語', 'all': 'All languages'}
load = lambda p: json.loads((ROOT/p).read_text(encoding='utf-8'))
data = load('content/data.json')

TOP = {  # friendly labels for the web texts (content/i18n/<lang>.json), in file order
 'html_lang': ('Language code (don’t change)', None), 'lang_name': ('Language name (language menu)', None),
 'skip': ('Interface · “Skip to content” link', None), 'meta': ('Search engines · title and description', None),
 'nav': ('Menu names', None), 'hero': ('Home · top (big photo)', None), 'glance': ('Home · at a glance', None),
 'why': ('Home · why we play in the street', None), 'about': ('Home · the company', None),
 'shows': ('Shows · common texts', None), 'show': ('Shows · each show page', 'One block per show: name, kicker, text, facts…'),
 'video': ('Video', None), 'workshops': ('Workshops', None), 'agenda': ('Agenda · titles', 'The dates themselves are in “Site data → Agenda”.'),
 'artists': ('Artists', None), 'downloads': ('Downloads · labels', None), 'contact': ('Contact and booking form', None),
 'footer': ('Footer', None), 'a11y': ('Accessibility menu', None), 'home_order': ('Home · order of the sections', 'Section ids in the order they appear on the home page of this language. Don’t rename them.'),
}
COLS = {  # dossier table columns (stored as {a, b, c})
 'figures': ('Number', 'Label'), 'kf': ('Number', 'Label'), 'festivals': ('Logo file', 'Festival', 'Place · year'),
 'getin': ('Title', 'Text'), 'tech': ('Title', 'Text'), 'credits': ('Role', 'Name'), 'cred': ('Role', 'Name'),
 'track': ('When', 'What'), 'gigs': ('When', 'What'), 'r_kf': ('Title', 'Text'), 'mt': ('Step', 'Time'), 'dm': ('Step', 'Time'),
 'items': ('Title', 'Text'),
}
def human(k): return str(k).replace('_', ' ').capitalize()
NOTE_EASY = 'Easy read: short sentences, one idea per sentence, numbers as digits.'

def field(k, v, labels=None, i18n=True):
    lab, hint = (labels or {}).get(k, (human(k), None))
    f = {'name': k, 'label': lab}
    if hint: f['hint'] = hint
    if isinstance(v, str):
        f['widget'] = 'text' if len(v) > 70 or '\n' in v else 'string'
        f['required'] = False
    elif isinstance(v, bool):
        f.update(widget='boolean', required=False)
    elif isinstance(v, (int, float)) and not isinstance(v, bool):
        f.update(widget='number', value_type='int' if isinstance(v, int) else 'float', required=False)
    elif v is None:
        f.update(widget='string', required=False)
    elif isinstance(v, list) and (not v or all(isinstance(x, str) for x in v)):
        f.update(widget='list', required=False)
    elif isinstance(v, list) and all(isinstance(x, dict) for x in v):
        keys = []
        for x in v:
            for kk in x:
                if kk not in keys: keys.append(kk)
        sample = {kk: next((x[kk] for x in v if kk in x), '') for kk in keys}
        if set(keys) <= set('abcdef'):
            names = COLS.get(k, ())
            sub = [dict(field(kk, sample[kk], i18n=i18n), label=(names[i] if i < len(names) else f'Column {i + 1}')) for i, kk in enumerate(keys)]
            f.update(widget='list', collapsed=True, fields=sub, summary='{{fields.a}} · {{fields.b}}', required=False)
        else:
            sub = [field(kk, sample[kk], i18n=i18n) for kk in keys]
            first = next((kk for kk in keys if isinstance(sample[kk], str)), keys[0])
            f.update(widget='list', collapsed=True, fields=sub, summary='{{fields.%s}}' % first, required=False)
    elif isinstance(v, dict) and v and all(isinstance(x, str) for x in v.values()) and not all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', kk) for kk in v):
        f.update(widget='keyvalue', required=False, key_label='Name', value_label='Text')   # keys like file names
    elif isinstance(v, dict):
        f.update(widget='object', collapsed=True, fields=[field(kk, vv, i18n=i18n) for kk, vv in v.items()])
    else:
        raise SystemExit(f'unexpected {k}: {v!r}')
    if i18n: mark(f)
    return f

def mark(f):
    f['i18n'] = True
    for g in f.get('fields', []): mark(g)
    return f

def texts_fields(path, top=None):
    ca = load(path)
    return [field(k, v, top) for k, v in ca.items()]

# ---------- site data (content/data.json): one form, one group per list
def opt(values): return [{'label': str(v), 'value': v} for v in values]
SHOW_IDS = [s['id'] for s in data['shows']]
def per_lang(name, label, hint=None, widget='string'):
    f = {'name': name, 'label': label, 'widget': 'object', 'collapsed': True, 'required': False,
         'summary': '{{fields.all}}{{fields.ca}}',
         'fields': [{'name': l, 'label': LANG_NAMES[l], 'widget': widget, 'required': False} for l in ['all'] + LANGS]}
    f['hint'] = (hint + ' ' if hint else '') + '“All languages” is used when a language is empty.'
    return f
PHOTO_HINT = ('Choose or upload a photo (original, never cropped). The website makes the web sizes itself. '
              'Existing entries show a short name (e.g. amigui-1): that is the photo, keep it or choose another.')
def photo(name, label, hint=None):
    return {'name': name, 'label': label, 'widget': 'image', 'required': False, 'choose_url': False,
            'media_folder': '/source-images', 'public_folder': '/source-images', 'hint': hint or PHOTO_HINT}
def photos(name, label, hint=None):
    return {'name': name, 'label': label, 'widget': 'list', 'required': False, 'collapsed': True,
            'hint': (hint or 'In order; drag to reorder.') + ' Each one: a photo from “Photos (originals)”.',
            'field': photo('photo', 'Photo')}
def hidden(k, v):
    return {'name': k, 'label': human(k), 'widget': 'hidden', 'default': v}

site_fields = []
for k, v in data['site'].items():
    if k == 'form_access_key': site_fields.append(hidden(k, v)); continue
    f = field(k, v, i18n=False); f['required'] = False
    if k == 'domain_live': f['hint'] = 'Only true once vendaval.cat points to GitHub.'
    site_fields.append(f)

dl_fields = []
for key, d in data['downloads'].items():
    sub = [
        {'name': 'show', 'label': 'Show', 'widget': 'string', 'readonly': True, 'required': False},
        {'name': 'kind', 'label': 'Kind', 'widget': 'string', 'readonly': True, 'required': False},
    ]
    for extra in ('variant', 'label', 'draft'):
        if extra in d: sub.append(field(extra, d[extra], i18n=False))
    sub += [
        {'name': 'short', 'label': 'Short link name', 'widget': 'string', 'readonly': True, 'required': False,
         'hint': f'www.VENDAVAL.cat/{"rider" if d["kind"] in ("rider", "green", "access") else "dossier"}/{d["short"]}/<lang>/ always gives the PDF below.'},
        {'name': 'files', 'label': 'PDF per language', 'widget': 'object', 'required': False,
         'hint': 'Path of each PDF (pdf/… = static/pdf/… in the repo). To replace a PDF keep the same file name: Assets → PDFs → upload with the same name → Replace.',
         'fields': [{'name': l, 'label': LANG_NAMES[l], 'widget': 'string', 'required': False} for l in LANGS]},
        {'name': 'manual', 'label': 'Replaced by hand on (per language)', 'widget': 'object', 'required': False, 'collapsed': True,
         'hint': 'Fill in the date (yyyy-mm-dd) for a language whose PDF you replaced with a file made elsewhere: the build scripts then keep it. Empty = built from the text in “Dossiers & riders”.',
         'fields': [{'name': l, 'label': LANG_NAMES[l], 'widget': 'string', 'required': False} for l in LANGS]},
    ]
    dl_fields.append({'name': key, 'label': key.replace('_', ' '), 'widget': 'object', 'collapsed': True, 'required': False, 'fields': sub})

agenda_item = [
    {'name': 'start', 'label': 'First day', 'widget': 'datetime', 'type': 'date', 'format': 'YYYY-MM-DD'},
    {'name': 'end', 'label': 'Last day', 'widget': 'datetime', 'type': 'date', 'format': 'YYYY-MM-DD', 'hint': 'Same as the first day for one day.'},
    {'name': 'show', 'label': 'Show', 'widget': 'select', 'options': opt(SHOW_IDS), 'required': False},
    {'name': 'precision', 'label': 'Dates shown as', 'widget': 'select', 'default': 'day', 'required': False,
     'options': [{'label': 'Exact days', 'value': 'day'}, {'label': 'Only month and year', 'value': 'month'}]},
    per_lang('place', 'Place', 'Venue, town (in each language’s form, e.g. Frankfurt del Main / Fráncfort del Meno).'),
    per_lang('note', 'Note (optional)', 'e.g. “Premiere”. {W} = link to the workshops page.'),
    per_lang('ws', 'Workshops line (optional)'),
    {'name': 'url', 'label': 'Link (optional)', 'widget': 'string', 'required': False},
    {'name': 'uid', 'label': 'Calendar ID', 'widget': 'string', 'readonly': True, 'required': False,
     'hint': 'Filled in = this gig comes from the Nextcloud calendar: change its date and place in the calendar (here they are overwritten at the next sync). Note, workshops line and link can be changed here.'},
]
data_fields = [
    hidden('languages', data['languages']),
    {'name': 'site', 'label': 'Site · contact', 'widget': 'object', 'collapsed': True, 'fields': site_fields},
    {'name': 'socials', 'label': 'Social links (footer icons)', 'widget': 'list', 'collapsed': True, 'summary': '{{fields.label}}',
     'fields': [{'name': 'id', 'label': 'Icon', 'widget': 'select', 'options': opt([s['id'] for s in data['socials']])},
                {'name': 'label', 'label': 'Name', 'widget': 'string'}, {'name': 'url', 'label': 'Link', 'widget': 'string'}]},
    {'name': 'hero_slides', 'label': 'Home · big photos (slides)', 'widget': 'list', 'collapsed': True, 'summary': '{{fields.show}} · {{fields.image}}',
     'fields': [{'name': 'show', 'label': 'Show', 'widget': 'select', 'options': opt(SHOW_IDS)}, photo('image', 'Photo'),
                {'name': 'pos', 'label': 'Focus point (x% y%)', 'widget': 'string', 'required': False, 'hint': 'Which part stays visible on narrow screens, e.g. 50% 35%. The photo is never cropped in the file.'}]},
    photo('about_image', 'Home · photo next to “The company”'),
    {'name': 'shows', 'label': 'Shows · photos and links', 'widget': 'list', 'collapsed': True, 'summary': '{{fields.id}}',
     'allow_add': False, 'allow_remove': False, 'hint': 'Texts of each show: “Web texts → Shows · each show page”. Order = selling order.',
     'fields': [{'name': 'id', 'label': 'Show id', 'widget': 'string', 'readonly': True},
                {'name': 'slug', 'label': 'Web address', 'widget': 'string', 'readonly': True},
                photo('cover', 'Cover photo'), photos('side', 'Photos next to the text'), photos('gallery', 'Gallery'),
                {'name': 'link', 'label': 'Extra link (optional)', 'widget': 'string', 'required': False}]},
    {'name': 'video', 'label': 'Video (home)', 'widget': 'object', 'collapsed': True, 'fields': [
        {'name': 'id', 'label': 'YouTube video id', 'widget': 'string', 'hint': 'The part after watch?v= in the YouTube link.'},
        photo('poster', 'Cover photo (before it plays)'), {'name': 'key', 'label': 'Title key', 'widget': 'string', 'readonly': True}]},
    {'name': 'downloads', 'label': 'Downloads · PDFs', 'widget': 'object', 'collapsed': True, 'fields': dl_fields},
    {'name': 'download_boxes', 'label': 'Downloads · boxes', 'widget': 'list', 'collapsed': True, 'summary': '{{fields.id}}',
     'fields': [{'name': 'id', 'label': 'Box id', 'widget': 'string', 'readonly': True},
                {'name': 'items', 'label': 'PDFs in this box (in order)', 'widget': 'select', 'multiple': True, 'options': opt(list(data['downloads']))},
                {'name': 'press', 'label': 'Press photos (ZIP)', 'widget': 'select', 'required': False, 'options': opt(list(data['press']))},
                {'name': 'title', 'label': 'Title key (optional)', 'widget': 'string', 'required': False},
                photo('thumb', 'Small photo (optional)'),
                per_lang('link', 'Link “more at” (optional)'), {'name': 'link_label', 'label': 'Link text', 'widget': 'string', 'required': False}]},
    {'name': 'press', 'label': 'Press photos (ZIPs on the downloads page)', 'widget': 'object', 'collapsed': True,
     'fields': [photos(k, k) for k in data['press']]},
    {'name': 'agenda', 'label': 'Agenda', 'widget': 'list', 'collapsed': True, 'add_to_top': True, 'label_singular': 'date',
     'summary': '{{fields.start}} · {{fields.show}} · {{fields.place.all}}{{fields.place.ca}}',
     'hint': 'Dates move to “past” by themselves. Confirmed gigs normally come from the calendar (Calendar ID filled in).',
     'fields': agenda_item},
    {'name': 'artists', 'label': 'Artists', 'widget': 'list', 'collapsed': True, 'summary': '{{fields.name}}',
     'hint': 'Origin and roles of each artist: “Web texts → Artists → People”.',
     'fields': [{'name': 'id', 'label': 'Id', 'widget': 'string', 'readonly': True, 'required': False},
                {'name': 'name', 'label': 'Name', 'widget': 'string'}, photo('photo', 'Portrait'),
                {'name': 'link', 'label': 'Web / social link', 'widget': 'string', 'required': False},
                {'name': 'bands', 'label': 'Also in (bands)', 'widget': 'list', 'required': False, 'summary': '{{fields.name}}',
                 'fields': [{'name': 'name', 'label': 'Name', 'widget': 'string'}, {'name': 'url', 'label': 'Link', 'widget': 'string', 'required': False}]}]},
    hidden('artist_gender', data['artist_gender']),
    hidden('substitutes', data['substitutes']),
    {'name': 'workshop_groups', 'label': 'Workshops · groups', 'widget': 'list', 'collapsed': True, 'summary': '{{fields.id}}',
     'fields': [{'name': 'id', 'label': 'Id', 'widget': 'string', 'readonly': True},
                {'name': 'kind', 'label': 'Kind', 'widget': 'select', 'options': opt(sorted({g['kind'] for g in data['workshop_groups']}))},
                photo('photo', 'Photo'), {'name': 'by', 'label': 'By', 'widget': 'string'},
                per_lang('url', 'Link'),
                {'name': 'dossier', 'label': 'Dossier', 'widget': 'select', 'required': False, 'options': opt(list(data['downloads']))}]},
    photos('workshops_gallery', 'Workshops · photo gallery'),
    hidden('originals', data['originals']),
    {'name': 'credits', 'label': 'Credits (footer)', 'widget': 'list', 'collapsed': True, 'summary': '{{fields.role}}',
     'fields': [{'name': 'role', 'label': 'Role', 'widget': 'select', 'options': opt(sorted({c['role'] for c in data['credits']}))},
                {'name': 'people', 'label': 'People', 'widget': 'list', 'summary': '{{fields.name}}',
                 'fields': [{'name': 'name', 'label': 'Name', 'widget': 'string'}, {'name': 'url', 'label': 'Link', 'widget': 'string', 'required': False}]}]},
    {'name': 'festival_links', 'label': 'Festival links (names linked in “The company”)', 'widget': 'keyvalue', 'required': False,
     'key_label': 'Name as written in the text', 'value_label': 'Link'},
]
def optional(fs):   # site data: entries differ (not every box has PDFs…), so nothing is required except the agenda dates
    for f in fs:
        if f.get('widget') != 'hidden' and 'required' not in f and f['name'] not in ('start', 'end'): f['required'] = False
        optional(f.get('fields', []))
        if 'field' in f: optional([f['field']])
optional(data_fields)
missing = [k for k in data if k not in {f['name'] for f in data_fields}]
if missing: raise SystemExit(f'data.json keys without a field: {missing} — add them (hidden if not edited)')

# ---------- dossiers
DOSSIERS_JSON = [('brass', 'VENDAVAL Brass · dossier + rider'), ('concert', 'VENDAVAL Brass · Concert in the audience (dossier + rider)'),
                 ('riders-brass', 'VENDAVAL Brass · green rider + access rider')]
DOSSIERS_MD = [('imaginary-friend', 'Amigui Imaginari · dossier'), ('el-joc-etern', 'El Joc Etern · dossier'),
               ('ani-arqui', 'Ani Arqui · dossier'), ('stilts-workshops', 'Stilts workshops · dossier'),
               ('easy-brass', 'Easy read · VENDAVAL Brass'), ('easy-friend', 'Easy read · Amigui Imaginari'),
               ('easy-stilts', 'Easy read · stilts workshops')]
def locales_of(folder, ext):
    return [l for l in LANGS if (ROOT/'dossiers'/folder/f'{l}.{ext}').exists()]
dossier_files = []
for folder, label in DOSSIERS_JSON:
    dossier_files.append({'name': folder, 'label': label, 'file': f'dossiers/{folder}/{{{{locale}}}}.json',
                          'i18n': {'locales': locales_of(folder, 'json')}, 'fields': texts_fields(f'dossiers/{folder}/ca.json')})
for folder, label in DOSSIERS_MD:
    locs = locales_of(folder, 'md')
    dossier_files.append({'name': folder, 'label': label, 'file': f'dossiers/{folder}/{{{{locale}}}}.md', 'format': 'frontmatter',
                          'i18n': {'locales': locs, 'default_locale': 'ca' if 'ca' in locs else locs[0]},
                          'fields': [{'name': 'body', 'label': 'Text (Markdown)', 'widget': 'markdown', 'i18n': True,
                                      'modes': ['raw'], 'buttons': [], 'editor_components': [],
                                      'hint': ('# title, ## section, **bold**, - list. Keep the <!-- … --> note at the top. ' + (NOTE_EASY if folder.startswith('easy-') else '')).strip()}]})

cfg = {
 'app_title': 'VENDAVAL · admin',
 'logo': {'src': '/admin/logo.png'},
 'backend': {'name': 'github', 'repo': 'ciaVENDAVAL/vendaval-web', 'branch': 'main', 'auth_methods': ['token'],
             'commit_messages': {'create': 'Admin: create {{collection}} “{{slug}}”', 'update': 'Admin: update {{collection}} “{{slug}}”',
                                 'delete': 'Admin: delete {{collection}} “{{slug}}”', 'uploadMedia': 'Admin: upload “{{path}}”',
                                 'deleteMedia': 'Admin: delete “{{path}}”'}},
 'site_url': 'https://vendaval.cat/',
 'media_folder': 'source-images', 'public_folder': '/source-images',
 'media_libraries': {'default': {'config': {'slugify_filename': False, 'max_file_size': 25000000}}},
 'slug': {'encoding': 'ascii', 'clean_accents': True},
 'editor': {'preview': False},
 'output': {'json': {'indent_style': 'space', 'indent_size': 1}, 'omit_empty_optional_fields': True},
 'i18n': {'structure': 'multiple_folders', 'locales': LANGS, 'default_locale': 'ca'},
 'asset_collections': [
   {'name': 'photos', 'label': 'Photos (originals)', 'media_folder': 'source-images', 'public_folder': '/source-images', 'icon': 'photo_library'},
   {'name': 'pdfs', 'label': 'PDFs', 'media_folder': 'static/pdf', 'public_folder': '/pdf', 'icon': 'picture_as_pdf'},
 ],
 'collections': [
   {'name': 'texts', 'label': 'Web texts (7 languages)', 'icon': 'translate', 'i18n': True,
    'description': 'Every text of the website. Catalan is the reference. A change in CA, ES or EN is translated into the other two automatically; DE, FR, IT, JA keep their old text until someone translates it (list in CHECK-REPORT.md).',
    'files': [{'name': 'all', 'label': 'All web texts', 'file': 'content/i18n/{{locale}}.json', 'i18n': True, 'fields': texts_fields('content/i18n/ca.json', TOP)},
              {'name': 'easy', 'label': 'Easy read (accessibility option)', 'file': 'content/easy/{{locale}}.json', 'i18n': True,
               'fields': [dict(f, hint=NOTE_EASY) for f in texts_fields('content/easy/ca.json')]}]},
   {'name': 'data', 'label': 'Site data (agenda, photos, artists, PDFs…)', 'icon': 'tune',
    'files': [{'name': 'data', 'label': 'Site data', 'file': 'content/data.json', 'fields': data_fields}]},
   {'name': 'dossiers', 'label': 'Dossiers & riders (PDF texts)', 'icon': 'picture_as_pdf', 'i18n': True,
    'description': 'Texts of the PDFs. After saving, the changed PDFs are rebuilt automatically (3–5 minutes). A PDF replaced by hand is kept (see Site data → Downloads → Replaced by hand).',
    'files': dossier_files},
 ],
}
def radios(x):   # phones: short selects as radio buttons, not a search box that opens the keyboard
    if isinstance(x, dict):
        if x.get('widget') == 'select' and len(x.get('options', [])) <= 12: x['dropdown_threshold'] = 12
        for v in x.values(): radios(v)
    elif isinstance(x, list):
        for v in x: radios(v)
radios(cfg)

class D(yaml.SafeDumper): pass
D.add_representer(str, lambda d, s: d.represent_scalar('tag:yaml.org,2002:str', s, style='"' if s in ('on', 'off', 'yes', 'no', '*') else None))
head = '# Sveltia CMS config for vendaval-web — generated by tools/make_config.py — edit that script, not this file.\n# Docs: https://sveltiacms.app/en/docs\n'
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(head + yaml.dump(cfg, Dumper=D, sort_keys=False, allow_unicode=True, width=200))
print('ok →', OUT.relative_to(ROOT))
