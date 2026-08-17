import os, re, shutil, zipfile, xml.etree.ElementTree as ET

SRC='scotland-edinburgh-glasgow-food-additions-47.kmz'
OUT='scotland-edinburgh-glasgow-food-additions-47-natural.kmz'
TMP='_food_desc_patch'
shutil.rmtree(TMP,ignore_errors=True)
os.makedirs(TMP,exist_ok=True)
with zipfile.ZipFile(SRC) as z: z.extractall(TMP)

kml=os.path.join(TMP,'doc.kml')
NS='http://www.opengis.net/kml/2.2'; ET.register_namespace('',NS)
tree=ET.parse(kml); root=tree.getroot()

# Known city grouping from the approved candidate list.
ED_EN={
'Lannan Bakery','Patina Bakery','Dune Bakery','Twelve Triangles','The Wee Boulangerie','The Pastry Section','Nice Times Bakery','SugarDaddy’s Bakery','Babyfaced Baker','Razz Patisserie','Gordon St Coffee','Artisan Roast Broughton Street','Fortitude Coffee Abbey Mount','Lowdown Coffee','The Milkman','Wellington Coffee','Cairngorm Coffee','Origin Coffee South College Street','Little Fitzroy','Kebab Mahal','Mosque Kitchen'}

def extract_name_and_cat(pm):
    n=pm.find('{%s}name'%NS)
    title=n.text if n is not None and n.text else ''
    parts=title.split(' – ',1)
    ar=parts[0].strip()
    cat=parts[1].strip() if len(parts)>1 else ''
    cat=re.sub(r'[☕🥐🍰🍩🍨🍪🍕🍽️]+','',cat).strip()
    return ar,cat

def make_desc(ar,en,cat,city):
    loc='إدنبرة' if city=='Edinburgh' else 'غلاسكو'
    if 'حلال' in cat and ('مطعم' in cat or 'بيتزا' in cat):
        text=f'يُعد {ar} ({en}) من الخيارات المميزة لمحبي الطعام الحلال في {loc}، ويقدم أطباقًا تناسب فئته ضمن أجواء مريحة وموقع مناسب للزوار.'
    elif 'إيطالي' in cat:
        text=f'يُعد {ar} ({en}) من الوجهات الإيطالية المميزة في {loc}، ويشتهر بتقديم نكهات ومخبوزات أو أطباق مستوحاة من المطبخ الإيطالي ضمن أجواء محببة للزوار.'
    elif 'جيلاتو' in cat:
        text=f'يُعد {ar} ({en}) من محلات الجيلاتو والحلويات المعروفة في {loc}، ويقدم مجموعة من النكهات والحلويات المناسبة للتوقف أثناء الجولة في المدينة.'
    elif 'مخبز' in cat or 'مخبوزات' in cat or 'دونات' in cat or 'حلويات' in cat or 'كوكيز' in cat:
        text=f'يُعد {ar} ({en}) من المخابز ومحلات الحلويات المميزة في {loc}، ويشتهر بالمخبوزات الطازجة والحلويات المتنوعة، ويُعد محطة جميلة للفطور أو القهوة أثناء التجول.'
    elif 'مقهى' in cat or 'محمصة' in cat or 'برنش' in cat:
        text=f'يُعد {ar} ({en}) من المقاهي المميزة في {loc}، ويشتهر بالقهوة والمشروبات والمخبوزات ضمن أجواء مناسبة للاستراحة أثناء استكشاف المدينة.'
    else:
        text=f'يُعد {ar} ({en}) من الأماكن المميزة في {loc} ضمن فئة {cat}، ويستحق التوقف خلال زيارة المدينة.'
    return text+'<br/><br/>جميع الحقوق محفوظة للخرائط السياحية.'

for pm in root.findall('.//{%s}Placemark'%NS):
    ar,cat=extract_name_and_cat(pm)
    d=pm.find('{%s}description'%NS)
    if d is None: continue
    old=d.text or ''
    m=re.search(r'الاسم الرسمي بالإنجليزية:\s*([^<]+)',old)
    if not m: continue
    en=m.group(1).strip()
    city='Edinburgh' if en in ED_EN else 'Glasgow'
    d.text=make_desc(ar,en,cat,city)

tree.write(kml,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    for r,ds,fs in os.walk(TMP):
        for f in fs:
            p=os.path.join(r,f); arc=os.path.relpath(p,TMP)
            z.write(p,arc)
print('built',OUT)
