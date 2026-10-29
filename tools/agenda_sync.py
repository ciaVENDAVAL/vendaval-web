"""Add gigs from the public VENDAVAL calendar (Nextcloud) to content/data.json → agenda.

Usage (from the repo root):  python3 tools/agenda_sync.py [--dry]
Then:  python3 build.py && python3 tools/check.py, commit, push.

How events are read (keep the calendar like this):
- Title: the show + the place, e.g. "VENDAVAL Brass · Fira del Vapor, Sant Vicenç de Castellet".
  The show is found by a word in the title: Brass / Concert → brass · Amigui / Imaginary / peluix → friend ·
  Freak → freakfrac · Joc Etern → joc. A title with taller / workshop / Workshop also gets the workshop line.
- Location (optional): replaces the place part of the title.
- URL field, or the first link in the description (optional): the link on the website.
- Status "tentative" or "cancelled": left out. Only confirmed gigs go public.
- All-day events or timed events both work; a multi-day event becomes a date range.
Events are matched by their calendar UID, so editing an event in the calendar updates it on the website.
Gigs typed by hand into data.json (no uid) are never deleted; one with the same show and start date as a calendar event is linked to it (its notes and link are kept).
"""
import json, re, sys, pathlib, urllib.request, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'content' / 'data.json'
ICS_URL = 'https://cloud.anartist.org/remote.php/dav/public-calendars/WeEdbbXadxEbp4Q2?export'
SHOWS = [(r'\bjoc etern\b', 'joc'), (r'\bfreak', 'freakfrac'), (r'amigui|imaginary|imaginari|peluix|peluche', 'friend'),
         (r'brass|concert|vendaval', 'brass')]
WORKSHOP = r'taller|workshop|tallere'
WS_TEXT = {'ca': 'Tallers', 'es': 'Talleres', 'en': 'Workshops', 'de': 'Workshops', 'fr': 'Ateliers', 'it': 'Laboratori', 'pt': 'Oficinas', 'ja': 'ワークショップ'}

def unfold(text):
    return re.sub(r'\r?\n[ \t]', '', text).splitlines()

def events(text):
    ev, out = None, []
    for line in unfold(text):
        if line == 'BEGIN:VEVENT': ev = {}
        elif line == 'END:VEVENT': out.append(ev); ev = None
        elif ev is not None and ':' in line:
            k, v = line.split(':', 1); name = k.split(';')[0].upper()
            v = v.replace('\\,', ',').replace('\\;', ';').replace('\\n', '\n').replace('\\N', '\n')
            ev[name] = (v, k)
    return out

def day(v, k, end=False):
    d = datetime.date(int(v[:4]), int(v[4:6]), int(v[6:8]))
    if end and ('VALUE=DATE' in k.upper() or len(v) == 8): d -= datetime.timedelta(days=1)   # all-day DTEND is exclusive
    return d.isoformat()

def to_gig(e):
    if e.get('STATUS', ('',))[0].upper() in ('TENTATIVE', 'CANCELLED'): return None
    title = e.get('SUMMARY', ('',))[0].strip()
    low = title.lower()
    show = next((s for pat, s in SHOWS if re.search(pat, low)), None)
    if not show or 'DTSTART' not in e: return None
    start = day(*e['DTSTART'])
    end = day(*e['DTEND'], end=True) if 'DTEND' in e else start
    if end < start: end = start
    place = e.get('LOCATION', ('',))[0].strip()
    if not place:
        parts = re.split(r'\s+[·|–—-]\s+', title, maxsplit=1)
        place = parts[1].strip() if len(parts) > 1 else title
    url = e.get('URL', ('',))[0].strip()
    if not url:
        m = re.search(r'https?://\S+', e.get('DESCRIPTION', ('',))[0]); url = m.group(0) if m else None
    return dict(start=start, end=end, show=show, url=url or None, precision='day', place=place, note='',
                ws=dict(WS_TEXT) if re.search(WORKSHOP, low) else '', uid=e.get('UID', ('',))[0])

def main(dry):
    text = urllib.request.urlopen(ICS_URL, timeout=30).read().decode('utf-8', 'replace')
    gigs = [g for g in map(to_gig, events(text)) if g]
    data = json.loads(DATA.read_text(encoding='utf-8'))
    agenda = data['agenda']; by_uid = {g.get('uid'): i for i, g in enumerate(agenda) if g.get('uid')}
    added = changed = 0
    for g in gigs:
        if g['uid'] in by_uid:
            old = agenda[by_uid[g['uid']]]
            keep = {k: old[k] for k in ('note', 'ws') if old.get(k)}   # translations added by hand stay
            new = dict(g, **keep)
            if new != old: agenda[by_uid[g['uid']]] = new; changed += 1
        else:
            # a gig already typed by hand (same show, same start date): link it to the calendar instead of adding it twice
            twin = next((i for i, o in enumerate(agenda) if not o.get('uid') and o['show'] == g['show'] and o['start'] == g['start']), None)
            if twin is not None:
                old = agenda[twin]; keep = {k: old[k] for k in ('note', 'ws', 'url') if old.get(k)}
                agenda[twin] = dict(g, **keep); by_uid[g['uid']] = twin; changed += 1
            else:
                agenda.append(g); added += 1
    agenda.sort(key=lambda g: (g['start'], g['end']))
    print(f'{len(gigs)} confirmed gigs in the calendar · {added} new · {changed} updated')
    for g in gigs: print(f"  {g['start']}–{g['end']}  {g['show']:9}  {g['place']}")
    if not dry and (added or changed):
        DATA.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
        print('content/data.json updated')

if __name__ == '__main__':
    main('--dry' in sys.argv)
