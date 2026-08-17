import os, io, shutil, zipfile
import xml.etree.ElementTree as ET
from PIL import Image

SRC_KML='edinburgh-additions-2026.kml'
DONOR_KMZ='Austria.kmz'
OUT_KMZ='edinburgh-additions-2026.kmz'
REPORT='edinburgh-icon-map.txt'
TMP='_edinburgh_build'; DONOR=os.path.join(TMP,'donor'); OUT=os.path.join(TMP,'out'); ICONS=os.path.join(OUT,'icons')

# Same Tourist Maps icon family used in our country maps.
ICON_SRC={
 'street':'icon-7.png',       # pedestrian streets / roads
 'landmark':'icon-29.png',    # historic/cultural landmark
 'castle':'icon-33.png',      # castles
 'town':'icon-19.png',        # towns / districts
 'village':'icon-1.png',      # villages
 'viewpoint':'icon-4.png',    # viewpoints
 'park':'icon-8.png',         # parks / gardens / nature
 'water':'icon-17.png',       # lakes / beaches / water
 'shopping':'icon-35.png',    # malls / markets / shopping
 'coffee':'icon-15.png',      # cafes
 'bakery':'icon-79.png',      # bakeries
 'dining':'icon-3.png',       # restaurants
 'entertainment':'icon-12.png',# entertainment / rides / activities
 'ferry':'icon-48.png',       # boats / ferries / piers
 'farm':'icon-78.png',        # farms / dairy / farm shops
}

# Classification by the approved Arabic title. This is intentionally explicit so each place gets the correct house icon.
def classify(name):
    if 'قلعة كريغميلار' in name: return 'castle'
    if any(x in name for x in ['نصب نيلسون','النصب الوطني','روسلين تشابل','جوبيتر آرتلاند']): return 'landmark'
    if any(x in name for x in ['حي ستوكبريدج','حي ليث','بورتوبيلو – منطقة']): return 'town'
    if 'قرية سوانستون' in name: return 'village'
    if any(x in name for x in ['تل بلاكفورد','ذا فينيل']): return 'viewpoint'
    if any(x in name for x in ['حديقة فيغيت','حدائق سوغتون','تلال بنتلاند','دالكيث كانتري بارك','روسلين غلين','حديقة دكتور نيل']): return 'park'
    if any(x in name for x in ['شاطئ بورتوبيلو','شاطئ كراموند']): return 'water'
    if any(x in name for x in ['شارع فيكتوريا','شارع كاندل','شارع ويست بورت','شارع كونستيتيوشن','سيركس لين','ممشى ووتر أوف ليث']): return 'street'
    if 'سوق أوشن تيرمينال' in name: return 'shopping'
    if any(x in name for x in ['برنت ووركس كوفي','كافيه برالين','ماشينا مارشمونت','كافيه بوميلو']): return 'coffee'
    if any(x in name for x in ['سودربيرغ ستوكبريدج','كونفيليسيتي بيكري']): return 'bakery'
    if any(x in name for x in ['ذا كيتشن','مطعم مارتن ويشارت','ذا براهنا','تشاو فرايا','إدنبرة ستريت فود','بوني آند وايلد']): return 'dining'
    if any(x in name for x in ['روكسي لينز','فلايت كلوب','ألباين كوستر','غو إيب','ذا شوكولاتاريوم']): return 'entertainment'
    if any(x in name for x in ['ميناء نيوهافن','هاوز بير','ميد أوف ذا فورث']): return 'ferry'
    if any(x in name for x in ['مزرعة كريغيز','مزرعة سوانستون']): return 'farm'
    return 'landmark'

shutil.rmtree(TMP,ignore_errors=True); os.makedirs(DONOR,exist_ok=True); os.makedirs(ICONS,exist_ok=True)
with zipfile.ZipFile(DONOR_KMZ) as z: z.extractall(DONOR)

# Locate icon files from the donor map, resize to exact 30x30, and embed them locally in this KMZ.
located={}
for root,dirs,files in os.walk(DONOR):
    for f in files:
        if f in ICON_SRC.values(): located[f]=os.path.join(root,f)
missing=[f for f in ICON_SRC.values() if f not in located]
if missing: raise RuntimeError('Missing donor Tourist Maps icons: '+', '.join(missing))
for cat,bn in ICON_SRC.items():
    im=Image.open(located[bn]).convert('RGBA').resize((30,30),Image.Resampling.LANCZOS)
    im.save(os.path.join(ICONS,cat+'.png'),'PNG')

ns='http://www.opengis.net/kml/2.2'; ET.register_namespace('',ns)
def local(tag): return tag.split('}',1)[-1]
src=ET.parse(SRC_KML); root=src.getroot(); doc=None
for e in root.iter():
    if local(e.tag)=='Document': doc=e; break
if doc is None: raise RuntimeError('Document element not found')

# Remove old generic Style blocks and replace them with our house-icon styles.
for child in list(doc):
    if local(child.tag)=='Style': doc.remove(child)
for cat in ICON_SRC:
    st=ET.Element('{%s}Style'%ns, {'id':cat})
    isty=ET.SubElement(st,'{%s}IconStyle'%ns)
    ET.SubElement(isty,'{%s}scale'%ns).text='1.0'
    icon=ET.SubElement(isty,'{%s}Icon'%ns)
    ET.SubElement(icon,'{%s}href'%ns).text='icons/'+cat+'.png'
    doc.insert(2,st)

assignments=[]
for pm in root.iter():
    if local(pm.tag)!='Placemark': continue
    name=''
    style_el=None
    for ch in pm:
        if local(ch.tag)=='name' and ch.text: name=ch.text.strip()
        elif local(ch.tag)=='styleUrl': style_el=ch
    cat=classify(name)
    if style_el is None:
        style_el=ET.SubElement(pm,'{%s}styleUrl'%ns)
    style_el.text='#'+cat
    assignments.append((name,cat))

os.makedirs(OUT,exist_ok=True)
src.write(os.path.join(OUT,'doc.kml'),encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(OUT_KMZ,'w',zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(OUT,'doc.kml'),'doc.kml')
    for f in sorted(os.listdir(ICONS)): z.write(os.path.join(ICONS,f),'icons/'+f)

# Validate 48 places, embedded icons, and 30x30 dimensions.
if len(assignments)!=48: raise RuntimeError(f'Expected 48 placemarks, got {len(assignments)}')
with zipfile.ZipFile(OUT_KMZ) as z:
    names=z.namelist()
    if 'doc.kml' not in names: raise RuntimeError('doc.kml missing')
    for cat in ICON_SRC:
        p='icons/'+cat+'.png'
        if p not in names: raise RuntimeError('Missing '+p)
        im=Image.open(io.BytesIO(z.read(p)))
        if im.size!=(30,30): raise RuntimeError(f'{p} is {im.size}, not 30x30')

with open(REPORT,'w',encoding='utf-8') as f:
    f.write('إضافات إدنبرة وضواحيها — مطابقة رموز الخرائط السياحية حسب نوع المكان\n')
    f.write('عدد المواقع: 48\n')
    f.write('جميع الرموز المضمنة: 30x30 بكسل\n\n')
    for cat,bn in ICON_SRC.items(): f.write(f'{cat}: {bn} -> icons/{cat}.png\n')
    f.write('\nتوزيع المواقع:\n')
    for name,cat in assignments: f.write(f'- {name} => {cat}\n')
print('Built',OUT_KMZ,'with 48 placemarks and exact Tourist Maps icons by type')
