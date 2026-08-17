import os,zipfile,shutil,xml.etree.ElementTree as ET
SRC='scotland-edinburgh-glasgow-food-additions-2026-final.kmz';OUT='scotland-edinburgh-glasgow-food-additions-47.kmz';TMP='_food_last'
P=[('راز باتيسري','Razz Patisserie','حلويات حلال','Edinburgh',55.942590,-3.203315,'bakery','🍰'),('أوريجن كوفي','Origin Coffee South College Street','مقهى مختص','Edinburgh',55.946964,-3.186622,'coffee','☕')]
shutil.rmtree(TMP,ignore_errors=True);os.makedirs(TMP)
with zipfile.ZipFile(SRC) as z:z.extractall(TMP)
NS='http://www.opengis.net/kml/2.2';ET.register_namespace('',NS);tree=ET.parse(os.path.join(TMP,'doc.kml'));root=tree.getroot()
def loc(t):return t.split('}',1)[-1]
folder=next(x for x in root.iter() if loc(x.tag)=='Folder')
for ar,en,cat,city,lat,lon,style,emo in P:
    pm=ET.SubElement(folder,'{%s}Placemark'%NS);ET.SubElement(pm,'{%s}name'%NS).text=f'{ar} – {cat} {emo}'
    ET.SubElement(pm,'{%s}description'%NS).text=f'الاسم الرسمي بالإنجليزية: {en}<br/>من الأماكن المرشحة ضمن فئة {cat} في {city}، ومضاف للمراجعة والمطابقة قبل الاعتماد النهائي.<br/><br/>جميع الحقوق محفوظة للخرائط السياحية.'
    ET.SubElement(pm,'{%s}styleUrl'%NS).text='#'+style;pt=ET.SubElement(pm,'{%s}Point'%NS);ET.SubElement(pt,'{%s}coordinates'%NS).text=f'{lon:.7f},{lat:.7f},0'
tree.write(os.path.join(TMP,'doc.kml'),encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    for r,d,fs in os.walk(TMP):
        for f in fs:z.write(os.path.join(r,f),os.path.relpath(os.path.join(r,f),TMP))
print('built',OUT)