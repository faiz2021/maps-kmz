import os, re, io, sys, shutil, zipfile, urllib.request
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

SRC_KML = 'edinburgh-additions-2026.kml'
DONOR_KMZ = 'Austria.kmz'
OUT_KMZ = 'edinburgh-additions-2026.kmz'
REPORT = 'edinburgh-icon-map.txt'
TMP = '_edinburgh_build'
DONOR = os.path.join(TMP, 'donor')
OUT = os.path.join(TMP, 'out')
ICONS = os.path.join(OUT, 'icons')

KW = {
    'walk': ['ممشى','مسار','ممر','walk','trail','promenade','path','hike','hiking'],
    'landmark': ['قلعة','قصر','برج','متحف','معلم','castle','palace','museum','tower','schloss','burg'],
    'park': ['حديقة','منتزه','غابة','park','garden','garten','forest','wald'],
    'water': ['شاطئ','بحيرة','شلال','نهر','lake','beach','waterfall','river','wasserfall','see'],
    'shopping': ['سوق','تسوق','مول','متجر','أوتلت','اوتلت','market','shopping','mall','outlet','store'],
    'coffee': ['مقهى','كافيه','مخبز','حلويات','coffee','cafe','café','bakery','conditorei'],
    'dining': ['مطعم','restaurant','grill','pizzeria','trattoria','gasthaus','ristorante'],
    'entertainment': ['ترفيه','مغامر','تلفريك','زحليقة','كوستر','ملاهي','نشاط','adventure','coaster','cable car','fun','play','rope','zipline'],
    'camera': ['شارع','حي','قرية','بلدة','street','village','old town','district','lane','quarter'],
    'ferry': ['قارب','عبارة','رصيف','ميناء','رحلة بحرية','boat','ferry','pier','harbour','harbor','cruise','schiff'],
}
FALLBACK = {
    'walk':'camera', 'water':'park', 'shopping':'landmark', 'coffee':'dining',
    'dining':'landmark', 'entertainment':'landmark', 'camera':'landmark', 'ferry':'water'
}

shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(DONOR, exist_ok=True)
os.makedirs(ICONS, exist_ok=True)

with zipfile.ZipFile(DONOR_KMZ) as z:
    z.extractall(DONOR)

kml_files=[]
for root, dirs, files in os.walk(DONOR):
    for f in files:
        if f.lower().endswith('.kml'):
            kml_files.append(os.path.join(root,f))
if not kml_files:
    raise RuntimeError('No KML found inside donor KMZ')
donor_kml=max(kml_files, key=os.path.getsize)
base_dir=os.path.dirname(donor_kml)

def local(tag):
    return tag.split('}',1)[-1]

def child_text(elem, name):
    for x in elem.iter():
        if local(x.tag)==name and x.text:
            return x.text.strip()
    return ''

tree=ET.parse(donor_kml)
root=tree.getroot()
styles={}
stylemaps={}
for e in root.iter():
    if local(e.tag)=='Style' and e.get('id'):
        href=''
        for x in e.iter():
            if local(x.tag)=='href' and x.text:
                href=x.text.strip(); break
        if href: styles[e.get('id')]=href
    elif local(e.tag)=='StyleMap' and e.get('id'):
        normal=''
        for p in e:
            if local(p.tag)!='Pair': continue
            key=child_text(p,'key')
            su=child_text(p,'styleUrl')
            if key=='normal' and su:
                normal=su.lstrip('#'); break
        if normal: stylemaps[e.get('id')]=normal

def resolve_style(sid):
    seen=set()
    while sid and sid not in seen:
        seen.add(sid)
        if sid in styles: return styles[sid]
        sid=stylemaps.get(sid,'')
    return ''

samples=[]
for pm in root.iter():
    if local(pm.tag)!='Placemark': continue
    name=child_text(pm,'name')
    desc=child_text(pm,'description')
    su=child_text(pm,'styleUrl').lstrip('#')
    href=resolve_style(su)
    if not href:
        for e in pm.iter():
            if local(e.tag)=='Style':
                for x in e.iter():
                    if local(x.tag)=='href' and x.text:
                        href=x.text.strip(); break
    if href:
        samples.append((name, desc, href))

counts={k:Counter() for k in KW}
examples={k:defaultdict(list) for k in KW}
for name,desc,href in samples:
    text=(name+' '+desc).lower()
    for cat,words in KW.items():
        if any(w.lower() in text for w in words):
            counts[cat][href]+=1
            if len(examples[cat][href])<4:
                examples[cat][href].append(name)

selected={}
for cat in KW:
    if counts[cat]:
        selected[cat]=counts[cat].most_common(1)[0][0]

# Fill missing categories from the closest available house style.
for cat in KW:
    if cat in selected: continue
    fb=FALLBACK.get(cat)
    if fb and fb in selected:
        selected[cat]=selected[fb]
    elif selected:
        selected[cat]=next(iter(selected.values()))
    else:
        raise RuntimeError('No donor icons could be resolved')

# Import selected donor icons and normalize them to exact 30x30 PNG.
from PIL import Image

def get_bytes(href):
    if href.startswith('http://') or href.startswith('https://'):
        req=urllib.request.Request(href, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    rel=href.replace('\\','/').lstrip('./')
    candidates=[os.path.join(base_dir,rel), os.path.join(DONOR,rel)]
    for c in candidates:
        if os.path.isfile(c):
            with open(c,'rb') as f: return f.read()
    # basename fallback for KMZs with unusual relative paths
    bn=os.path.basename(rel)
    for r,d,fs in os.walk(DONOR):
        if bn in fs:
            with open(os.path.join(r,bn),'rb') as f: return f.read()
    raise FileNotFoundError(href)

for cat,href in selected.items():
    data=get_bytes(href)
    im=Image.open(io.BytesIO(data)).convert('RGBA')
    im=im.resize((30,30), Image.Resampling.LANCZOS)
    im.save(os.path.join(ICONS,cat+'.png'),'PNG')

# Rewrite only the style icon hrefs in the additions KML.
src=ET.parse(SRC_KML)
sroot=src.getroot()
ns='http://www.opengis.net/kml/2.2'
ET.register_namespace('',ns)
style_ids=set(KW)
for e in sroot.iter():
    if local(e.tag)=='Style' and e.get('id') in style_ids:
        sid=e.get('id')
        scale=None; href_el=None
        for x in e.iter():
            if local(x.tag)=='scale': scale=x
            elif local(x.tag)=='href': href_el=x
        if scale is not None: scale.text='1.0'
        if href_el is not None: href_el.text='icons/'+sid+'.png'

os.makedirs(OUT, exist_ok=True)
src.write(os.path.join(OUT,'doc.kml'), encoding='utf-8', xml_declaration=True)

with zipfile.ZipFile(OUT_KMZ,'w',zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(OUT,'doc.kml'),'doc.kml')
    for f in sorted(os.listdir(ICONS)):
        z.write(os.path.join(ICONS,f),'icons/'+f)

# Validate output.
with zipfile.ZipFile(OUT_KMZ) as z:
    if 'doc.kml' not in z.namelist(): raise RuntimeError('doc.kml missing')
    for cat in KW:
        if 'icons/'+cat+'.png' not in z.namelist(): raise RuntimeError('missing icon '+cat)

with open(REPORT,'w',encoding='utf-8') as f:
    f.write('Tourist Maps icon mapping used for Edinburgh additions\n')
    f.write('Donor: Austria.kmz (same Tourist Maps map family)\n\n')
    for cat in KW:
        href=selected[cat]
        f.write(f'{cat}: {href}\n')
        ex=examples[cat].get(href,[])
        if ex: f.write('  examples: '+' | '.join(ex)+'\n')
        f.write('  output: icons/'+cat+'.png (30x30)\n')

print('Built',OUT_KMZ,'with',len(KW),'Tourist Maps icon categories')
