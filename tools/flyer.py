"""One-page A4 catalogue/flyer (all shows + workshops + contact), for office printing (no bleed).
Usage: python3 tools/flyer.py ca es en   ->  flyer/VENDAVAL_catalogue_<LANG>_<yyyy-mm>.pdf
Texts come from content/i18n (same as the website) plus the few flyer-only lines below."""
import json, sys, pathlib, datetime, html
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS, OUT = ROOT/'docs', ROOT/'flyer'
data = json.loads((ROOT/'content/data.json').read_text())

# flyer-only texts (short versions); add a language here before building it
X = {
 'ca': {'title': 'Espectacles i tallers', 'concert': 'Concert enmig del públic',
        'concert_kicker': "Concert amplificat a la plaça, davant de l'escenari",
        'concert_facts': ["Passis de 30 minuts durant els canvis d'escenari, diversos al dia", 'La banda toca enmig del públic, amb xanques i jocs', '8 micròfons sense fils propis; PA del festival'],
        'ws_kicker': 'Per a joves i adults, amb artistes en actiu', 'web': 'Fotos, vídeos, dossiers i fitxes tècniques'},
 'es': {'title': 'Espectáculos y talleres', 'concert': 'Concierto entre el público',
        'concert_kicker': 'Concierto amplificado en la plaza, frente al escenario',
        'concert_facts': ['Pases de 30 minutos en los cambios de escenario, varios al día', 'La banda toca entre el público, con zancos y juegos', '8 micrófonos inalámbricos propios; PA del festival'],
        'ws_kicker': 'Para jóvenes y adultos, con artistas en activo', 'web': 'Fotos, vídeos, dosieres y fichas técnicas'},
 'en': {'title': 'Shows and workshops', 'concert': 'Concert in the audience',
        'concert_kicker': 'Amplified concert on the square in front of the stage',
        'concert_facts': ['30-minute sets during stage changeovers, several a day', 'The band plays among the audience, with stilts and games', '8 wireless mics of our own; festival PA'],
        'ws_kicker': 'For young people and adults, led by working artists', 'web': 'Photos, videos, dossiers and technical riders'},
}
FACTS = {'brass': [0, 2, 3], 'friend': [0, 2, 3, 4], 'joc': [0, 2, 3], 'freakfrac': [0, 2]}
PHOTO = {'brass': 'vendaval-passecalles-000', 'concert': 'vendaval-firavapor002', 'friend': 'amigui-7',
         'joc': 'el-joc-etern-drawing-swap', 'freakfrac': 'freak-frac-3', 'workshops': 'tallers-zancos-1'}

def img(name): return (DOCS/'img'/f'{name}-800.webp').as_uri()
e = html.escape

def card(name, kicker, items, photo, tag=None, sub=None):
    lis = ''.join(f'<li>{e(i)}</li>' for i in items)
    return f'''<article class="card">
  <div class="ph"><img class="bg" src="{img(photo)}" alt=""><img class="fg" src="{img(photo)}" alt=""></div>
  <div class="tx">{f'<span class="tag">{e(tag)}</span>' if tag else ''}
    <h2>{e(name)}</h2>{f'<p class="sub">{e(sub)}</p>' if sub else ''}
    <p class="kick">{e(kicker)}</p><ul>{lis}</ul></div>
</article>'''

def page(lang):
    t = json.loads((ROOT/f'content/i18n/{lang}.json').read_text()); x = X[lang]; S = t['show']; site = data['site']
    cards = [card(S['brass']['name'], S['brass']['kicker'], [S['brass']['facts'][i] for i in FACTS['brass']], PHOTO['brass']),
             card(x['concert'], x['concert_kicker'], x['concert_facts'], PHOTO['concert'], sub='VENDAVAL Brass')]
    for k in ('friend', 'joc', 'freakfrac'):
        s = S[k]; st = s.get('status')
        cards.append(card(s['name'], s['kicker'], [s['facts'][i] for i in FACTS[k]], PHOTO[k],
                          tag=t['shows']['status'][st] if st else None))
    W = t['workshops']
    cards.append(card(W['title'], x['ws_kicker'],
                      [f"{g['title']}: {', '.join(i[0].lower() + i[1:] for i in g['items'])}" if g['items'] != [g['title']] else g['title'] for g in W['groups'].values()],
                      PHOTO['workshops']))
    web = 'vendaval.cat'
    fonts = ''.join(f"@font-face{{font-family:{fam};font-weight:{w};src:url({(ROOT/'static/fonts'/f).as_uri()})}}"
                    for fam, w, f in [('Brico', 800, 'bricolage-grotesque-latin-800-normal.woff2'), ('Brico', 800, 'bricolage-grotesque-latin-ext-800-normal.woff2'),
                                      ('Brico', 700, 'bricolage-grotesque-latin-700-normal.woff2'), ('Brico', 700, 'bricolage-grotesque-latin-ext-700-normal.woff2'),
                                      ('Atk', 400, 'atkinson-hyperlegible-latin-400-normal.woff2'), ('Atk', 400, 'atkinson-hyperlegible-latin-ext-400-normal.woff2'),
                                      ('Atk', 700, 'atkinson-hyperlegible-latin-700-normal.woff2'), ('Atk', 700, 'atkinson-hyperlegible-latin-ext-700-normal.woff2')])
    logo = (DOCS/'img'/'logo.webp').as_uri()
    return f'''<!doctype html><html lang="{t['html_lang']}"><meta charset="utf-8"><title>Cia. VENDAVAL · {e(x['title'])}</title>
<style>{fonts}
@page{{size:A4;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:210mm;height:297mm;overflow:hidden}}
body{{font:400 9pt/1.28 Atk,sans-serif;color:#1d2a30;padding:10mm 10mm 0;display:flex;flex-direction:column;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
header{{display:flex;align-items:center;gap:6mm;padding-bottom:4mm;border-bottom:1.2mm solid #f4b740}}
header img{{height:24mm}}
header h1{{font:800 21pt/1 Brico,sans-serif;color:#082f40}}
header p{{font-size:10pt;color:#4f5e65;margin-top:1.5mm;max-width:120mm}}
main{{flex:1;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,minmax(0,1fr));min-height:0;gap:4mm;padding:5mm 0}}
.card{{display:flex;min-height:0;border:.4mm solid #e3d6c3;border-radius:3mm;overflow:hidden;background:#fff}}
.ph{{position:relative;flex:0 0 42mm;overflow:hidden;background:#082f40}}
.ph .bg{{position:absolute;inset:-4mm;width:calc(100% + 8mm);height:calc(100% + 8mm);object-fit:cover;filter:blur(2.5mm) brightness(.8)}}
.ph .fg{{position:relative;width:100%;height:100%;object-fit:contain}}
.tx{{padding:3.2mm 3.5mm;display:flex;flex-direction:column;gap:1.2mm}}
.tag{{align-self:flex-start;font:700 6.8pt Atk;text-transform:uppercase;letter-spacing:.06em;background:#e8492e;color:#fff;padding:.4mm 1.8mm;border-radius:1.5mm}}
h2{{font:800 14pt/1.05 Brico,sans-serif;color:#082f40}}
.sub{{font:700 7.5pt Atk;text-transform:uppercase;letter-spacing:.06em;color:#0f8a94;margin-top:-.8mm}}
.kick{{font-weight:700;color:#c43a22}}
ul{{list-style:none;display:flex;flex-direction:column;gap:.9mm}}
li{{padding-left:3mm;position:relative}}
li::before{{content:"";position:absolute;left:0;top:1.3mm;width:1.4mm;height:1.4mm;background:#1ab3bf;transform:rotate(45deg)}}
footer{{margin:0 -10mm;background:#082f40;color:#fff;padding:5mm 10mm 7mm;display:grid;grid-template-columns:auto 1fr;gap:2mm 8mm;align-items:center}}
footer h2{{color:#fff;font-size:15pt;grid-row:span 2}}
footer .c{{display:flex;flex-wrap:wrap;gap:1mm 6mm;font:700 10.5pt Atk}}
footer .c span b{{color:#f4b740;font-weight:700;margin-right:1.5mm}}
footer .n{{font-size:8pt;color:#cfe3e8}}
</style>
<header><img src="{logo}" alt="VENDAVAL"><div><h1>{e(x['title'])}</h1><p>{e(t['shows']['intro'])}</p></div></header>
<main>{''.join(cards)}</main>
<footer><h2>{e(t['contact']['title'])}</h2>
  <div class="c"><span><b>✉</b>{e(site['email'])}</span><span><b>☎</b>{e(site['phone'])}</span><span><b>⌂</b>{web}</span><span><b>◎</b>@vendaval.brass</span></div>
  <p class="n">{e(x['web'])}: {web} · {e(t['contact']['invoice'])}</p>
</footer></html>'''

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True); stamp = datetime.date.today().strftime('%Y-%m')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        for lang in sys.argv[1:] or ['ca', 'es', 'en']:
            f = OUT/f'flyer_{lang}.html'; f.write_text(page(lang), encoding='utf-8')
            pg.goto(f.as_uri(), wait_until='networkidle')
            n = pg.evaluate('document.body.scrollHeight')
            out = OUT/f'VENDAVAL_catalogue_{lang.upper()}_{stamp}.pdf'
            pg.pdf(path=str(out), format='A4', print_background=True, prefer_css_page_size=True)
            print(out.name, 'height px', n)
        b.close()
