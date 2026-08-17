import os, io, time, json, math, shutil, zipfile, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from PIL import Image

PLACES = [
('لانان بيكري','Lannan Bakery','مخبز وحلويات','إدنبرة'),
('باتينا بيكري','Patina Bakery','مخبز ومقهى','إدنبرة'),
('ديون بيكري','Dune Bakery','مخبز فرنسي','South Queensferry, Edinburgh'),
('تويلف تراينغلز','Twelve Triangles','مخبز ومقهى','إدنبرة'),
('ذا وي بولانجيري','The Wee Boulangerie','مخبز فرنسي','إدنبرة'),
('ذا باستري سيكشن','The Pastry Section','حلويات ومخبوزات','Stockbridge, Edinburgh'),
('نايس تايمز بيكري','Nice Times Bakery','مخبز وحلويات','إدنبرة'),
('شوغر داديز بيكري','SugarDaddy’s Bakery','مخبز وحلويات','Marchmont, Edinburgh'),
('بيبي فيسد بيكر','Babyfaced Baker','مخبز وحلويات','إدنبرة'),
('راز باتيسري','Razz Patisserie','حلويات حلال','Edinburgh'),
('غوردون ستريت كوفي','Gordon St Coffee','مقهى ومحمصة','Edinburgh'),
('آرتيزان روست','Artisan Roast Broughton Street','مقهى ومحمصة','Edinburgh'),
('فورتيتيود كوفي','Fortitude Coffee Abbey Mount','مقهى مختص','Edinburgh'),
('لوداون كوفي','Lowdown Coffee','مقهى مختص','George Street, Edinburgh'),
('ذا ميلكمان','The Milkman','مقهى','Cockburn Street, Edinburgh'),
('ويلينغتون كوفي','Wellington Coffee','مقهى مختص','George Street, Edinburgh'),
('كيرنغورم كوفي','Cairngorm Coffee','مقهى مختص','Edinburgh'),
('أوريجن كوفي','Origin Coffee South College Street','مقهى مختص','Edinburgh'),
('ليتل فيتزروي','Little Fitzroy','مقهى','Easter Road, Edinburgh'),
('كباب محل','Kebab Mahal','مطعم حلال','Edinburgh'),
('موسك كيتشن','Mosque Kitchen','مطعم حلال','Edinburgh'),
('تانتروم دونتس','Tantrum Doughnuts','دونات وحلويات','Glasgow'),
('ذا دوركي فرنش','The Dorky French','مخبز فرنسي نباتي','Glasgow'),
('دو','Doh Doughnuts Glasgow','دونات ومخبوزات','Glasgow'),
('بارتينوبي','Partenope','مخبز إيطالي ومقهى','Glasgow'),
('بيرنفيلد بيكري','Burnfield Bakery','مخبز وحلويات','Strathbungo, Glasgow'),
('ميبل ليف بيكري','Maple Leaf Bakery','مخبز ومقهى','Glasgow'),
('هاني تراب','Honey Trap Bakery','مخبز نباتي','Glasgow'),
('بيغ بير بيكري','Big Bear Bakery','مخبز','Battlefield, Glasgow'),
('نيو لاندز هوم بيكري','Newlands Home Bakery','مخبز','Glasgow'),
('دينستون بيكري','Deanston Bakery','مخبز وحلويات','Glasgow'),
('جيجو بيكد غودز','Jeju Baked Goods','مخبوزات وحلويات','Victoria Road, Glasgow'),
('سويت جين بيك هاوس','Sweet Jane Bakehouse','مخبز وحلويات','Dennistoun, Glasgow'),
('غرانتس ذا بيكرز','Grants the Bakers','مخبز','Glasgow'),
('أكارا','Akara Bakery','مخبز ومقهى','Dennistoun, Glasgow'),
('ميديناز كوفي','Medina’s Coffee','مقهى','Glasgow'),
('ريست','Rest Coffee Glasgow','مقهى ومخبوزات','High Street, Glasgow'),
('برامبل كافيه','Bramble Cafe Glasgow','مقهى وبرنش','Glasgow'),
('كافيه سترينج برو','Cafe Strange Brew','مقهى','Glasgow'),
('شورت لونغ بلاك','Short Long Black','مقهى ومخبوزات','Glasgow'),
('جينيسي أرتيزان جيلاتو','Ginesi’s Artisan Gelato','جيلاتو وحلويات','Glasgow'),
('لا جيلاتيسا','La Gelatessa','جيلاتو إيطالي','Glasgow'),
('رود كوكيز','Rude Cookies','كوكيز وحلويات','Glasgow'),
('بابا توني رستورانتي إيتاليانو','Papa Tony’s Ristorante Italiano','مطعم إيطالي حلال','Glasgow'),
('كانوتو بيتزا','Canotto Pizza Glasgow','بيتزا إيطالية حلال','Glasgow'),
('لوكوز بيتزا','Locos Pizza Bridgeton','بيتزا حلال','Glasgow'),
('إيزي بيتزا','Easy Pizza Springfield Road','بيتزا حلال','Glasgow'),
]

DONOR='Austria.kmz'
OUT='scotland-edinburgh-glasgow-food-additions-2026.kmz'
REPORT='scotland-food-additions-report.txt'
TMP='_food_build'
DONOR_DIR=os.path.join(TMP,'donor')
OUT_DIR=os.path.join(TMP,'out')
ICON_DIR=os.path.join(OUT_DIR,'icons')

ALIASES={
 'SugarDaddy’s Bakery':['SugarDaddy’s Edinburgh','Sugar Daddys Bakery Edinburgh'],
 'Babyfaced Baker':['Babyfaced Baker Edinburgh','Babyfaced Baker Leith'],
 'Razz Patisserie':['Razz Patisserie Edinburgh Home Street'],
 'Artisan Roast Broughton Street':['Artisan Roast 57 Broughton Street Edinburgh'],
 'Fortitude Coffee Abbey Mount':['Fortitude Coffee 3C York Place Edinburgh','Fortitude Coffee Edinburgh'],
 'Cairngorm Coffee':['Cairngorm Coffee Melville Place Edinburgh','Cairngorm Coffee Frederick Street Edinburgh'],
 'Mosque Kitchen':['The Original Mosque Kitchen Edinburgh','Mosque Kitchen Nicolson Square Edinburgh'],
 'The Dorky French':['Dorky French Glasgow'],
 'Doh Doughnuts Glasgow':['Doh Glasgow doughnuts'],
 'Partenope':['Partenope Glasgow bakery'],
 'Honey Trap Bakery':['Honeytrap Bakery Glasgow','Honey Trap Glasgow bakery'],
 'Grants the Bakers':['Grant’s Bakery Glasgow','Grants Bakers Glasgow'],
 'Akara Bakery':['Akara Bakery Glasgow','Akara Dennistoun'],
 'Medina’s Coffee':['Medinas Coffee Glasgow'],
 'Rest Coffee Glasgow':['Rest Glasgow High Street cafe'],
 'Short Long Black':['Short Long Black Glasgow cafe'],
 'Ginesi’s Artisan Gelato':['Ginesi Artisan Gelato Glasgow'],
 'Papa Tony’s Ristorante Italiano':['Papa Tonys Glasgow Italian'],
 'Canotto Pizza Glasgow':['Canotto Pizza Glasgow Torbreck Street'],
 'Locos Pizza Bridgeton':['Loco’s Pizza Bridgeton Glasgow','Locos Pizza Glasgow'],
 'Easy Pizza Springfield Road':['Easy Pizza Glasgow Springfield Road'],
}

CAT_STYLE={
 'مقهى':'coffee','محمصة':'coffee','برنش':'coffee',
 'مخبز':'bakery','مخبوزات':'bakery','دونات':'bakery','حلويات':'bakery','جيلاتو':'bakery','كوكيز':'bakery',
 'مطعم':'dining','بيتزا':'dining'
}

def style_for(cat):
    for k,v in CAT_STYLE.items():
        if k in cat: return v
    return 'dining'

def icon_emoji(cat):
    if 'جيلاتو' in cat: return '🍨'
    if 'كوكيز' in cat: return '🍪'
    if 'دونات' in cat: return '🍩'
    if 'حلويات' in cat: return '🍰'
    if 'مخبز' in cat or 'مخبوزات' in cat: return '🥐'
    if 'بيتزا' in cat: return '🍕'
    if 'مطعم' in cat: return '🍽️'
    return '☕'

def geocode(q):
    url='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({'q':q,'format':'jsonv2','limit':5,'countrycodes':'gb','addressdetails':1})
    req=urllib.request.Request(url,headers={'User-Agent':'TouristMapsPro/1.0 contact info@touristmapspro.com'})
    try:
        with urllib.request.urlopen(req,timeout=35) as r: data=json.load(r)
    except Exception:
        return []
    time.sleep(1.05)
    return data

def resolve(en,city):
    qs=[f'{en}, {city}, Scotland',f'{en}, {city}',f'{en}, Scotland']
    for a in ALIASES.get(en,[]): qs += [f'{a}, {city}, Scotland', f'{a}, Scotland']
    seen=set()
    for q in qs:
        if q in seen: continue
        seen.add(q)
        arr=geocode(q)
        for x in arr:
            disp=x.get('display_name','').lower()
            if 'scotland' in disp or 'alba' in disp or any(c.lower() in disp for c in ['edinburgh','glasgow','south queensferry']):
                return float(x['lat']),float(x['lon']),x.get('display_name',''),q
    return None

shutil.rmtree(TMP,ignore_errors=True)
os.makedirs(DONOR_DIR,exist_ok=True); os.makedirs(ICON_DIR,exist_ok=True)
with zipfile.ZipFile(DONOR) as z: z.extractall(DONOR_DIR)
kmls=[]
for r,d,fs in os.walk(DONOR_DIR):
    for f in fs:
        if f.lower().endswith('.kml'): kmls.append(os.path.join(r,f))
doc=max(kmls,key=os.path.getsize); base=os.path.dirname(doc)
root=ET.parse(doc).getroot()
def local(t): return t.split('}',1)[-1]
def text(el,n):
    for x in el.iter():
        if local(x.tag)==n and x.text: return x.text.strip()
    return ''
styles={}; maps={}
for e in root.iter():
    if local(e.tag)=='Style' and e.get('id'):
        h=''
        for x in e.iter():
            if local(x.tag)=='href' and x.text: h=x.text.strip(); break
        if h: styles[e.get('id')]=h
    elif local(e.tag)=='StyleMap' and e.get('id'):
        for p in e:
            if local(p.tag)=='Pair' and text(p,'key')=='normal': maps[e.get('id')]=text(p,'styleUrl').lstrip('#')
def resolve_style(s):
    seen=set()
    while s and s not in seen:
        seen.add(s)
        if s in styles: return styles[s]
        s=maps.get(s,'')
    return ''
# Donor house icons known from Tourist Maps family: coffee icon-15, bakery icon-79, dining icon-3.
WANTED={'coffee':'images/icon-15.png','bakery':'images/icon-79.png','dining':'images/icon-3.png'}
def find_icon(rel):
    bn=os.path.basename(rel)
    for r,d,fs in os.walk(DONOR_DIR):
        if bn in fs: return os.path.join(r,bn)
    raise FileNotFoundError(rel)
for cat,rel in WANTED.items():
    im=Image.open(find_icon(rel)).convert('RGBA').resize((30,30),Image.Resampling.LANCZOS)
    im.save(os.path.join(ICON_DIR,cat+'.png'))

resolved=[]; failed=[]
for ar,en,cat,city in PLACES:
    r=resolve(en,city)
    if r: resolved.append((ar,en,cat,city,*r))
    else: failed.append((ar,en,cat,city))

NS='http://www.opengis.net/kml/2.2'; ET.register_namespace('',NS)
k=ET.Element('{%s}kml'%NS); docel=ET.SubElement(k,'{%s}Document'%NS)
ET.SubElement(docel,'{%s}name'%NS).text='إضافات مقاهي ومخابز وحلويات ومطاعم إدنبرة وغلاسكو 2026'
for st in ['coffee','bakery','dining']:
    s=ET.SubElement(docel,'{%s}Style'%NS,{'id':st}); isty=ET.SubElement(s,'{%s}IconStyle'%NS)
    ET.SubElement(isty,'{%s}scale'%NS).text='1.0'; ic=ET.SubElement(isty,'{%s}Icon'%NS); ET.SubElement(ic,'{%s}href'%NS).text='icons/'+st+'.png'
folder=ET.SubElement(docel,'{%s}Folder'%NS); ET.SubElement(folder,'{%s}name'%NS).text='إضافات الطعام والمقاهي - إدنبرة وغلاسكو'
for ar,en,cat,city,lat,lon,disp,q in resolved:
    pm=ET.SubElement(folder,'{%s}Placemark'%NS)
    ET.SubElement(pm,'{%s}name'%NS).text=f'{ar} – {cat} {icon_emoji(cat)}'
    desc=(f'الاسم الرسمي بالإنجليزية: {en}<br/>'
          f'من الأماكن المرشحة ضمن فئة {cat} في {city}، ومضاف في هذا الملف للمراجعة والمطابقة مع خريطة اسكتلندا السياحية الحالية قبل الاعتماد النهائي.<br/><br/>'
          'جميع الحقوق محفوظة للخرائط السياحية.')
    ET.SubElement(pm,'{%s}description'%NS).text=desc
    ET.SubElement(pm,'{%s}styleUrl'%NS).text='#'+style_for(cat)
    pt=ET.SubElement(pm,'{%s}Point'%NS); ET.SubElement(pt,'{%s}coordinates'%NS).text=f'{lon:.7f},{lat:.7f},0'

os.makedirs(OUT_DIR,exist_ok=True)
ET.ElementTree(k).write(os.path.join(OUT_DIR,'doc.kml'),encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(OUT_DIR,'doc.kml'),'doc.kml')
    for f in os.listdir(ICON_DIR): z.write(os.path.join(ICON_DIR,f),'icons/'+f)
with open(REPORT,'w',encoding='utf-8') as f:
    f.write(f'المرشحون: {len(PLACES)}\nتم تحديد الإحداثيات وإدراجهم: {len(resolved)}\nتعذر تحديدهم: {len(failed)}\n\n')
    if failed:
        f.write('FAILED:\n')
        for x in failed: f.write(' | '.join(x)+'\n')
    f.write('\nRESOLVED:\n')
    for x in resolved: f.write(f'{x[0]} | {x[1]} | {x[2]} | {x[4]:.7f},{x[5]:.7f} | {x[6]}\n')
print('resolved',len(resolved),'failed',len(failed))