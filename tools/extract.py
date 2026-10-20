# One-off: rebuild content/*.json from the published single-page site (recovery 2026-10-19)
import json, re, pathlib, sys
from bs4 import BeautifulSoup, NavigableString
R = pathlib.Path('/home/claude/recover')
OUT = pathlib.Path('/home/claude/vendaval-site/content'); (OUT/'i18n').mkdir(parents=True, exist_ok=True)
LANGS = ['ca','es','en','de','fr','it','pt','ja']
def T(el): return el.get_text(' ', strip=True) if el else ''
def inner(el):
    return ''.join(str(c) for c in el.contents).strip()
def img(el): return re.sub(r'^\.\./img/|-(800|1600)\.webp$', '', el['src'])
SHOWS = ['brass','joc','freakfrac','friend']
data = {'shows': {}, 'agenda': [], 'artists': [], 'workshop_groups': []}
for l in LANGS:
    s = BeautifulSoup((R/l/'index.html').read_text(), 'html.parser')
    t = {}
    t['html_lang'] = s.html['lang']
    t['lang_name'] = s.select_one('.langs summary').contents[0].strip()
    t['skip'] = T(s.select_one('.skip'))
    t['meta'] = {'title': s.title.string.strip(), 'description': s.select_one('meta[name=description]')['content']}
    nav = {}
    for a in s.select('#nav li a'): nav[a['href'].lstrip('#')] = T(a)
    nav['menu'] = T(s.select_one('.menu-btn span')); nav['language'] = s.select_one('.langs summary')['aria-label']
    t['nav'] = nav
    h = s.select_one('.hero-in')
    ctas = h.select('.ctas a')
    t['hero'] = {'kicker': T(h.select_one('.kicker')), 'title': T(h.h1), 'sub': T(h.select_one('.sub')), 'cta_book': T(ctas[0]), 'cta_video': T(ctas[1])}
    ab = s.select_one('#about')
    t['about'] = {'title': T(ab.h2), 'p': [inner(p) for p in ab.select('.two > div > p')]}
    sh = s.select_one('#shows')
    t['shows'] = {'title': T(sh.h2), 'intro': T(sh.select_one('.lead')), 'back': T(sh.select_one('.back-shows a')).lstrip('↑ ').strip(),
                  'photos': sh.select_one('.gallery')['aria-label'].split(' – ')[0], 'status': {}}
    t['show'] = {}
    for art in sh.select('article.show'):
        sid = art['id'][5:]; st = {}
        b = art.select_one('.badge')
        if b: st['status'] = b['class'][1][6:]; t['shows']['status'][st['status']] = T(b)
        st['name'] = T(art.h3); st['kicker'] = T(art.select_one('.show-text > .kicker'))
        st['text'] = [inner(p) for p in art.select('.show-text > p') if not p.get('class')]
        fx = art.select('.facts')
        t['shows']['facts'] = T(fx[0].h4)
        st['facts'] = [T(li) for li in fx[0].select('li')]
        for f in fx[1:]:
            st['extra_title'] = T(f.h4); st['extra_text'] = T(f.p)
        acc = art.select_one('.access')
        if acc:
            st['access_title'] = T(acc.strong).rstrip(':'); st['access'] = acc.get_text().split(':',1)[1].strip()
        em = art.select_one('.show-links em')
        if em: st['dossier_soon'] = T(em)
        more = art.select_one('.show-links a.btn-line')
        if more: t['shows']['more'] = T(more)
        t['show'][sid] = st
        if l == 'ca':
            md = art.select('.show-media img')
            data['shows'][sid] = {'cover': img(md[0]), 'side': [img(i) for i in md[1:]],
                                  'gallery': [img(i) for i in art.select('.gallery img')],
                                  'link': more['href'] if more else None}
    v = s.select_one('#video')
    play = v.select_one('.play')['aria-label']
    t['video'] = {'title': T(v.h2), 'intro': T(v.select_one('.lead')), 'play': play.split(':')[0].strip(), 'consent': T(v.select_one('.consent')),
                  'watch_on': T(v.select_one('figcaption a')).replace('YouTube','').strip(), 'items': {'brass_trailer': play.split(':',1)[1].strip()}}
    w = s.select_one('#workshops')
    t['workshops'] = {'title': T(w.h2), 'intro': T(w.select_one('.lead')), 'groups': {}}
    note = w.select_one('.note'); t['workshops']['ask'] = T(note.a); t['workshops']['note'] = note.contents[0].strip()
    for i, g in enumerate(w.select('.ws-group')):
        gid = ['stilts','circus','music'][i]
        t['workshops']['groups'][gid] = {'title': g.h3.contents[0].strip(), 'items': [T(li) for li in g.select('.tags li')]}
        if l == 'ca':
            a = g.select_one('h3 small a')
            data['workshop_groups'].append({'id': gid, 'kind': g['class'][1][3:], 'photo': img(g.img), 'by': T(a), 'url': a['href'],
                                            'dossier': 'xanques_dossier' if g.select_one('p a') else None})
    if l == 'ca': data['workshops_gallery'] = [img(i) for i in w.select('.gallery img')]
    ag = s.select_one('#agenda')
    hs = ag.select('h3')
    t['agenda'] = {'title': T(ag.h2), 'upcoming': T(hs[0]), 'past': T(hs[1]), 'none': T(ag.select_one('.none'))}
    for i, li in enumerate(ag.select('.timeline li')):
        whats = li.select('.what')
        main = whats[0]; showa = main.find('a')
        rest = inner(main)[len(str(showa)):] if showa else inner(main)
        rest = re.sub(r'^\s*·\s*', '', rest)
        rest = re.sub(r'href="#workshops"', 'href="{W}"', rest)
        ws = re.sub(r'href="#workshops"', 'href="{W}"', inner(whats[1])) if len(whats) > 1 else ''
        place = li.select_one('.place'); pa = place.find('a')
        if l == 'ca':
            tm = li.time
            data['agenda'].append({'start': tm['datetime'] if len(tm['datetime'])==10 else tm['datetime'], 'end': li['data-end'],
                                   'show': showa['href'][6:] if showa else None, 'url': pa['href'] if pa else None,
                                   'precision': 'month' if re.match(r'^\D', T(tm)) else 'day', 'place': {}, 'note': {}, 'ws': {}})
        e = data['agenda'][i]
        e['place'][l] = T(place); e['note'][l] = rest.strip()
        if ws: e['ws'][l] = ws
    ar = s.select_one('#artists')
    t['artists'] = {'title': T(ar.h2), 'intro': T(ar.select_one('.lead')), 'link': T(ar.select_one('.artist > a')),
                    'subs_title': T(ar.select_one('.subs-title')), 'people': {}}
    for a in ar.select('.artist'):
        aid = img(a.img).replace('portrait-','')
        t['artists']['people'][aid] = {'origin': T(a.select_one('.origin')), 'roles': T(a.select('p')[1])}
        if l == 'ca':
            lk = a.select_one('a')
            data['artists'].append({'id': aid, 'name': T(a.h3), 'photo': img(a.img), 'link': lk['href'] if lk else None})
    if l == 'ca': data['substitutes'] = [T(x) for x in ar.select('.subs span')]
    d = s.select_one('#downloads')
    cards = d.select('.dlcard')
    kick = [T(k) for k in cards[0].select('.kicker')]
    photos = cards[0].select('.dl-row')[-1].select('a')
    t['downloads'] = {'title': T(d.h2), 'intro': T(d.select_one('.lead')), 'note': T(d.select_one('.note')),
                      'kinds': {'dossier': kick[0], 'rider': kick[1], 'photos': kick[-1], 'workshop': T(cards[4].select_one('.kicker'))},
                      'photos_web': photos[0].contents[-2].strip() if False else re.sub(r'\s+\d+ · [\d.]+ MB$','',T(photos[0])),
                      'photos_print': re.sub(r'\s+\d+ · [\d.]+ MB$','',T(photos[1])),
                      'missing': T(cards[2].select_one('.dl-missing')),
                      'more_at': cards[3].select_one('.dl-row').contents[0].strip(),
                      'titles': {'xanques': T(cards[4].h3), 'yiflauki': T(cards[5].h3)}}
    t['downloads']['concert'] = kick[2].split(' · ')[0]
    c = s.select_one('#contact'); f = c.select_one('form')
    labs = [x.contents[0].strip() if isinstance(x.contents[0], NavigableString) else '' for x in f.select('label > span')]
    opts = [T(o) for o in f.select('option')]
    t['contact'] = {'title': T(c.h2), 'intro': T(c.select_one('.two > div > p')), 'invoice': T(c.select_one('.note')), 'morse': T(c.select_one('.morse a')),
                    'form': {'name': labs[0], 'email': labs[1], 'phone': labs[2], 'org': labs[3], 'date': labs[4], 'place': labs[5], 'show': labs[6], 'message': labs[7],
                             'required': f.select_one('abbr')['title'], 'show_any': opts[-1], 'privacy': T(f.select_one('.privacy')), 'submit': T(f.button),
                             'ok': f['data-ok'], 'err': f['data-err'], 'sending': f['data-sending']}}
    ft = s.select('footer p')
    t['footer'] = {'credits': T(ft[0]), 'hosted': T(ft[1]).replace('© Cia. VENDAVAL · ',''), 'top': T(ft[2])}
    p = s.select_one('#a11y-panel')
    t['a11y'] = {'title': T(p.select_one('.a11y-title')), 'size': T(p.select_one('.a11y-size span')),
                 **{b['data-a']: (b.get('aria-label') or T(b)) for b in p.select('button')}}
    (OUT/'i18n'/f'{l}.json').write_text(json.dumps(t, ensure_ascii=False, indent=1))
(OUT/'extracted.json').write_text(json.dumps(data, ensure_ascii=False, indent=1))
print('ok')
