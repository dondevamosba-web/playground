#!/usr/bin/env python3
"""FEBA (Fiestas Electrónicas BA) review page.

Self-contained HTML with base64 images: last 3 posted (IG API) + scheduled
posts (unified sheet) + queue candidates, each with approve/skip buttons
wired to the approval server on localhost:8765.

Output: .tmp/fiestas_upcoming_review.html
"""
import sys, os, base64, html, requests
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
from sheets_client import get_services
from datetime import date

sheets,_=get_services()
today=str(date.today())
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'}

def img64(url):
    if not url or not url.startswith('http'): return None
    try:
        r=requests.get(url,headers=UA,timeout=20)
        if r.status_code!=200 or len(r.content)<5000: return None
        mime='image/png' if '.png' in url.lower() else 'image/jpeg'
        return f'data:{mime};base64,'+base64.b64encode(r.content).decode()
    except Exception: return None

cards_sched, cards_pend = [], []

# últimos 3 posteados — directo de la API de IG
cards_last=[]
tok=os.environ['INSTAGRAM_ACCESS_TOKEN']
ig=os.environ['FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID']
media=requests.get(f'https://graph.facebook.com/v21.0/{ig}/media',
    params={'fields':'media_url,thumbnail_url,timestamp,caption,permalink','limit':3,'access_token':tok},timeout=20).json().get('data',[])
for m in media:
    cards_last.append(dict(sheet='IG',row='—',when=m['timestamp'][:16].replace('T',' ')+' UTC',
        cap=(m.get('caption') or '(sin caption)'),img=m.get('media_url') or m.get('thumbnail_url',''),st='posted'))

sid=os.environ['UNIFIED_APPROVAL_SHEET_ID']
rows=sheets.spreadsheets().values().get(spreadsheetId=sid,range="'Fiestas'!A1:H200").execute().get('values',[])
for i,r in enumerate(rows[1:],start=2):
    st=(r[4] if len(r)>4 else '').strip().lower()
    sched=(r[3] if len(r)>3 else '')
    if st=='approved' and sched[:10]>=today:
        cards_sched.append(dict(sheet='UNIFICADA',row=i,when=sched,cap=r[1] if len(r)>1 else '',img=r[2] if len(r)>2 else '',st=st))

qid=os.environ['FIESTAS_APPROVAL_SHEET_ID']
rows=sheets.spreadsheets().values().get(spreadsheetId=qid,range='Queue!A1:N300').execute().get('values',[])
posted={(r[2].strip()[:40].lower()) for r in rows[1:] if len(r)>11 and r[11].strip()=='posted'}
for i,r in enumerate(rows[1:],start=2):
    st=(r[11] if len(r)>11 else '').strip().lower()
    evd=(r[3] if len(r)>3 else '')
    name=(r[2] if len(r)>2 else '')
    if st in ('pending','approved') and (not evd or evd>=today) and name.strip()[:40].lower() not in posted:
        cards_pend.append(dict(sheet='QUEUE',row=i,when=evd,cap=name+' — '+(r[7] if len(r)>7 else '')[:180],img=r[9] if len(r)>9 else '',st=st))

cards_sched.sort(key=lambda c:c['when']); cards_pend.sort(key=lambda c:c['when'])

def render(cards):
    out=[]
    for c in cards:
        b64=img64(c['img'])
        imgtag=f'<img src="{b64}">' if b64 else f'<div class="noimg">sin imagen / no descargable<br><small>{html.escape(c["img"][:80])}</small></div>'
        if c['sheet']=='IG':
            btns=''
        else:
            key='unified-fiestas' if c['sheet']=='UNIFICADA' else 'fiestas-queue'
            btns=(f'<div class="btns">'
                  f'<button class="ok" onclick="act(this,\'approve\',\'{key}\',{c["row"]})">✅ aprobar</button>'
                  f'<button class="no" onclick="act(this,\'skip\',\'{key}\',{c["row"]})">🚫 no va</button></div>')
        out.append(f'''<div class="card"><div class="head">{'FILA ' if c['sheet']!='IG' else ''}{c['row']} · {c['sheet']} · {c['when']} · <span class="st">{c['st']}</span></div>{imgtag}<p>{html.escape(c['cap'][:400])}</p>{btns}</div>''')
    return '\n'.join(out) or '<p>— nada —</p>'

page=f'''<!doctype html><html><head><meta charset="utf-8"><title>Fiestas — próximos</title><style>
body{{background:#0d0a14;color:#eee;font-family:Helvetica,Arial;margin:20px}}
h1,h2{{color:#a56bff}} .card{{display:inline-block;vertical-align:top;width:340px;margin:10px;background:#17121f;border:1px solid #2c2340;border-radius:10px;overflow:hidden}}
.card img{{width:100%;display:block}} .card p{{padding:10px;font-size:13px;line-height:1.4}}
.head{{background:#231a33;padding:8px 10px;font-weight:bold;font-size:13px;color:#c9a6ff}}
.st{{color:#7CFC9A}} .noimg{{padding:40px 10px;text-align:center;color:#888;background:#111}}
.btns{{padding:8px 10px 12px}} .btns button{{border:0;border-radius:6px;padding:8px 14px;margin-right:8px;font-weight:bold;cursor:pointer}}
.ok{{background:#7CFC9A}} .no{{background:#ff7b7b}} .done{{opacity:.45}}
</style></head><body>
<h1>Fiestas Electrónicas BA — contenido próximo ({today})</h1>
<h2>🔵 Últimos 3 posteados (feed real)</h2>{render(cards_last)}
<h2>🟢 Programados — salen solos vía publish-approved ({len(cards_sched)})</h2>{render(cards_sched)}
<h2>🟡 En Queue — decime cuáles aprobar ("fila X aprobala / no va") ({len(cards_pend)})</h2>{render(cards_pend)}
<script>
function act(btn,action,sheet,row){{
  fetch('http://127.0.0.1:8765/'+action+'?sheet='+sheet+'&row='+row)
    .then(r=>r.json()).then(j=>{{
      const card=btn.closest('.card');
      card.classList.add('done');
      card.querySelector('.head').innerHTML+=j.ok?(' → '+j.msg):(' ⚠️ '+j.msg);
    }}).catch(e=>alert('approval server no responde: '+e));
}}
</script></body></html>'''
open(ROOT/'.tmp'/'fiestas_upcoming_review.html','w').write(page)
print('scheduled:',len(cards_sched),'| pending queue:',len(cards_pend))
