import os, json, time, zipfile, shutil, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

SRC='scotland-edinburgh-glasgow-food-additions-2026.kmz'
OUT='scotland-edinburgh-glasgow-food-additions-2026-final.kmz'
REPORT='scotland-food-additions-final-report.txt'
TMP='_food_patch'

# Exact street addresses selected for unresolved candidates and obvious mis-geocodes.
P=[
('باتينا بيكري','Patina Bakery','مخبز ومقهى','Edinburgh','2 Airborne Place, Edinburgh Park, Edinburgh EH12 9GR'),
('نايس تايمز بيكري','Nice Times Bakery','مخبز وحلويات','Edinburgh','147 Morrison Street, Edinburgh EH3 8AG'),
('شوغر داديز بيكري','SugarDaddy’s Bakery','مخبز وحلويات','Edinburgh','8 Roseneath Street, Edinburgh EH9 1JH'),
('راز باتيسري','Razz Patisserie','حلويات حلال','Edinburgh','57A Home Street, Edinburgh EH3 9JP'),
('أوريجن كوفي','Origin Coffee South College Street','مقهى مختص','Edinburgh','6-8 South College Street, Edinburgh EH8 9AA'),
('تانتروم دونتس','Tantrum Doughnuts','دونات وحلويات','Glasgow','28 Gordon Street, Glasgow G1 3PU'),
('بيرنفيلد بيكري','Burnfield Bakery','مخبز وحلويات','Glasgow','717 Pollokshaws Road, Glasgow G41 2AA'),
('ميبل ليف بيكري','Maple Leaf Bakery','مخبز ومقهى','Glasgow','16 Water Row, Glasgow G51 2LQ'),
('غرانتس ذا بيكرز','Grants the Bakers','مخبز','Glasgow','100 Bellgrove Street, Glasgow G31 1AA'),
('ميديناز كوفي','Medina’s Coffee','مقهى','Glasgow','1001 Pollokshaws Road, Glasgow G41 3YF'),
('ريست','Rest Coffee','مقهى ومخبوزات','Glasgow','285 High Street, Glasgow G4 0QS'),
('برامبل كافيه','Bramble Cafe','مقهى وبرنش','Glasgow','924 Pollokshaws Road, Glasgow G41 2ET'),
('بابا توني رستورانتي إيتاليانو','Papa Tony’s Ristorante Italiano','مطعم إيطالي حلال','Glasgow','283 Sauchiehall Street, Glasgow G2 3HQ'),
('كانوتو بيتزا','Canotto Pizza Glasgow','بيتزا إيطالية حلال','Glasgow','3 Torbreck Street, Glasgow G52 1DR'),
('لوكوز بيتزا','Loco’s Pizza','بيتزا حلال','Glasgow','4 Tullis Street, Bridgeton, Glasgow G40 1HN'),
('إيزي بيتزا','Easy Pizza','بيتزا حلال','Glasgow','917 Springfield Road, Glasgow G31 4HZ'),
]

def style_for(cat):
    if any(x in cat for x in ['مخبز','مخبوزات','دونات','حلويات','جيلاتو','كوكيز']): return 'bakery'
    if any(x in cat for x in ['مقهى','محمصة','برنش']): return 'coffee'
    return 'dining'
def emoji(cat):
    if 'جيلاتو' in cat:return '🍨'
    if 'دونات' in cat:return '🍩'
    if 'حلويات' in cat:return '🍰'
    if 'مخبز' in cat or 'مخبوزات' in cat:return '🥐'
    if 'بيتزا' in cat:return '🍕'
    if 'مطعم' in cat:return '🍽️'
    return '☕'

def geocode(addr):
    url='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({'q':addr+', Scotland, United Kingdom','format':'jsonv2','limit':1,'countrycodes':'gb'})
    req=urllib.request.Request(url,headers={'User-Agent':'TouristMapsPro/1.0 info@touristmapspro.com'})
    try:
        with urllib.request.urlopen(req,timeout=15) as r: a=json.load(r)
    except Exception:return None
    time.sleep(1.05)
    return (float(a[0]['lat']),float(a[0]['lon']),a[0].get('display_name','')) if a else None

shutil.rmtree(TMP,ignore_errors=True); os.makedirs(TMP)
with zipfile.ZipFile(SRC) as z:z.extractall(TMP)
root=ET.parse(os.path.join(TMP,'doc.kml')).getroot()
NS='http://www.opengis.net/kml/2.2'; ET.register_namespace('',NS)
def loc(t):return t.split('}',1)[-1]
# Remove earlier versions of candidates being replaced.
replace={x[0] for x in P}
for folder in list(root.iter()):
    if loc(folder.tag)!='Folder':continue
    for pm in list(folder):
        if loc(pm.tag)!='Placemark':continue
        nm=''
        for c in pm:
            if loc(c.tag)=='name':nm=c.text or '';break
        if any(nm.startswith(ar+' –') for ar in replace): folder.remove(pm)
folders=[x for x in root.iter() if loc(x.tag)=='Folder']
folder=folders[0]
resolved=[];failed=[]
for ar,en,cat,city,addr in P:
    g=geocode(addr)
    if not g:
        failed.append((ar,en,addr));continue
    lat,lon,disp=g
    pm=ET.SubElement(folder,'{%s}Placemark'%NS)
    ET.SubElement(pm,'{%s}name'%NS).text=f'{ar} – {cat} {emoji(cat)}'
    ET.SubElement(pm,'{%s}description'%NS).text=(f'الاسم الرسمي بالإنجليزية: {en}<br/>من الأماكن المرشحة ضمن فئة {cat} في {city}، ومضاف للمراجعة والمطابقة قبل الاعتماد النهائي.<br/><br/>جميع الحقوق محفوظة للخرائط السياحية.')
    ET.SubElement(pm,'{%s}styleUrl'%NS).text='#'+style_for(cat)
    pt=ET.SubElement(pm,'{%s}Point'%NS);ET.SubElement(pt,'{%s}coordinates'%NS).text=f'{lon:.7f},{lat:.7f},0'
    resolved.append((ar,en,lat,lon,disp))
ET.ElementTree(root).write(os.path.join(TMP,'doc.kml'),encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    for r,d,fs in os.walk(TMP):
        for f in fs:
            rel=os.path.relpath(os.path.join(r,f),TMP)
            z.write(os.path.join(r,f),rel)
with open(REPORT,'w',encoding='utf-8') as f:
    f.write(f'المرشحون الأصليون: 47\nالإضافات/التصحيحات اليدوية: {len(P)}\nتم حلها: {len(resolved)}\nتعذر: {len(failed)}\n\n')
    if failed:
        f.write('FAILED:\n');[f.write(' | '.join(x)+'\n') for x in failed]
    f.write('\nPATCHED:\n');[f.write(f'{x[0]} | {x[1]} | {x[2]:.7f},{x[3]:.7f} | {x[4]}\n') for x in resolved]
print('patched',len(resolved),'failed',len(failed))