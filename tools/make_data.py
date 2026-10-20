import json, pathlib
C = pathlib.Path('content'); x = json.loads((C/'extracted.json').read_text())
L = ['ca','es','en','de','fr','it','pt','ja']
def squash(d):
    vals = set(d.values())
    return next(iter(vals)) if len(vals) == 1 and len(d) == len(L) else d
agenda = []
for e in x['agenda']:
    e['place'] = squash(e['place'])
    e['note'] = squash(e['note']) if any(e['note'].values()) else ''
    e['ws'] = squash(e['ws']) if e['ws'] else ''
    if 'Clownic' in json.dumps(e['place']): e['url'] = 'https://clownic.cat/'
    agenda.append(e)
agenda.sort(key=lambda e: e['start'])
shows = []
for sid, slug in [('brass','brass'),('joc','el-joc-etern'),('freakfrac','freak-frac'),('friend','imaginary-friend')]:
    s = x['shows'][sid]; shows.append({'id': sid, 'slug': slug, **s})
for g in x['workshop_groups']:
    if g['id'] == 'circus':
        g['url'] = {'ca': 'https://ciafiligranes.net/tallers/', 'es': 'https://ciafiligranes.net/es/talleres', '*': 'https://ciafiligranes.net/en/workshops'}
P = 'pdf/'
def files(pattern, langs): return {l: P + pattern.format(L=l.upper()) for l in langs}
data = {
 'site': {'domain': 'vendaval.cat', 'email': 'VENDAVAL@anartist.org', 'phone': '+34 644 389 757', 'phone_link': '+34644389757',
          'form_endpoint': 'https://api.web3forms.com/submit', 'form_access_key': '14340506-b525-497b-9cee-8ec2dc00c07d', 'default_lang': 'ca'},
 'languages': L,
 'socials': [{'id': 'instagram', 'label': 'Instagram', 'url': 'https://www.instagram.com/vendaval.brass/'},
             {'id': 'youtube', 'label': 'YouTube', 'url': 'https://www.youtube.com/@VENDAVAL.YOUTUBE'},
             {'id': 'telegram', 'label': 'Telegram', 'url': 'https://t.me/+34644389757'},
             {'id': 'whatsapp', 'label': 'WhatsApp', 'url': 'https://wa.me/34644389757'},
             {'id': 'email', 'label': 'Email', 'url': 'mailto:VENDAVAL@anartist.org'}],
 'hero_slides': [{'show': 'brass', 'image': 'vendaval-firavapor002', 'pos': '50% 35%'}, {'show': 'joc', 'image': 'windy-vespa-grinding', 'pos': '50% 50%'},
                 {'show': 'freakfrac', 'image': 'freak-frac-9', 'pos': '50% 40%'}, {'show': 'friend', 'image': 'amigui-5', 'pos': '50% 40%'}],
 'about_image': 'vendaval-firavapor001',
 'shows': shows,
 'video': {'id': 'HpkRH-YxNXE', 'poster': 'vendaval-unterwegs002', 'key': 'brass_trailer'},
 'downloads': {
   'brass_dossier': {'show': 'brass', 'kind': 'dossier', 'short': 'brass', 'files': files('VENDAVAL-Brass_{L}_dossier_2026-09.pdf', ['ca','es','en','de','ja'])},
   'brass_rider': {'show': 'brass', 'kind': 'rider', 'short': 'brass', 'files': files('VENDAVAL-Brass_{L}_rider_2026-09.pdf', ['ca','es','en','de'])},
   'concert_dossier': {'show': 'brass', 'kind': 'dossier', 'variant': 'concert', 'short': 'brass-concert', 'files': files('VENDAVAL-Brass-Concert-Placa_{L}_dossier_2026-10.pdf', L)},
   'concert_rider': {'show': 'brass', 'kind': 'rider', 'variant': 'concert', 'short': 'brass-concert', 'files': files('VENDAVAL-Brass-Concert-Placa_{L}_rider_2026-10.pdf', L)},
   'joc_dossier': {'show': 'joc', 'kind': 'dossier', 'short': 'el-joc-etern', 'files': files('VENDAVAL_El-Joc-Etern_{L}_dossier.pdf', ['ca','en'])},
   'friend_dossier': {'show': 'friend', 'kind': 'dossier', 'short': 'imaginary-friend', 'files': files('VENDAVAL_Imaginary-Friend_{L}_dossier_2026-10.pdf', L)},
   'friend_rider': {'show': 'friend', 'kind': 'rider', 'short': 'imaginary-friend',
                    'files': {'ca': P+'VENDAVAL_Amigui-Imaginari_CA_rider.pdf', 'es': P+'VENDAVAL_Amigui-Imaginari_ES_rider.pdf',
                              'en': P+'VENDAVAL_Imaginary-Friend_EN_rider.pdf', 'de': P+'VENDAVAL_Imaginary-Friend_DE_rider.pdf'}},
   'xanques_dossier': {'show': 'xanques', 'kind': 'workshop', 'short': 'stilts-workshops',
                       'files': {'ca': P+'VENDAVAL_Tallers-Xanques_CA_dossier.pdf', 'es': P+'VENDAVAL_Talleres-Zancos_ES_dossier.pdf', 'en': P+'VENDAVAL_Stilts-Workshops_EN_dossier.pdf'}}},
 'download_boxes': [
   {'id': 'brass', 'items': ['brass_dossier', 'brass_rider', 'concert_dossier', 'concert_rider'], 'press': 'brass'},
   {'id': 'joc', 'items': ['joc_dossier'], 'press': 'joc'},
   {'id': 'friend', 'items': ['friend_dossier', 'friend_rider'], 'press': 'friend'},
   {'id': 'freakfrac', 'link': 'https://ciafiligranes.net/en/shows/freak-frac', 'link_label': 'ciafiligranes.net'},
   {'id': 'xanques', 'title': 'xanques', 'items': ['xanques_dossier'], 'press': 'xanques'},
   {'id': 'yiflauki', 'title': 'yiflauki', 'link': 'https://yiflauki.com/', 'link_label': 'yiflauki.com'}],
 'press': {
   'brass': ['vendaval-firavapor002','vendaval-firavapor001','vendaval-passecalles-000','vendaval-003-400px','vendaval-unterwegs001','vendaval-unterwegs002','vendaval-unterwegs003','vendaval-unterwegs004','vendaval-bobila001','vendaval-102','img-0677','img-0780','photo-2026-09-09-20-43-56','img-0622'],
   'joc': ['el-joc-etern-drawing-swap','windy-vespa-grinding','img-0780','creating-windy-1','creating-windy-2','creating-windy-3','creating-windy-4','creating-windy-5','creating-el-joc-etern-8','creating-el-joc-etern-13','boat-chicken-rudder','masks-boat-drummer','mask-owlcat-sail'],
   'friend': ['amigui-5','amigui-7','amigui-mg-7306','amigui-footer-12','amigui-2','amigui-4','amigui-1'],
   'xanques': ['tallers-zancos-1','tallers-zancos-2']},
 'agenda': agenda,
 'artists': x['artists'],
 'artist_gender': {'tyle': 'x', 'albert': 'm', 'jordi': 'm', 'alian': 'm', 'juan': 'm', 'stefano': 'm', 'lucas': 'm', 'facu': 'm'},
 'substitutes': x['substitutes'],
 'workshop_groups': x['workshop_groups'],
 'workshops_gallery': x['workshops_gallery'],
}
(C/'data.json').write_text(json.dumps(data, ensure_ascii=False, indent=1))
print(len(agenda))
