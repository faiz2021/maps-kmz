import csv, io, os, shutil, zipfile
import xml.etree.ElementTree as ET
from PIL import Image

MANUAL=[
 {'ar':'داماسكينو','en':'Damasqino Restaurant & Cafe','cat':'مطعم حلال','region':'غلاسكو','lat':55.85549,'lon':-4.245318,'display':'94 Saltmarket, Glasgow G1 5LD, Scotland'},
 {'ar':'شاطئ كورال','en':'Coral Beach Skye','cat':'شاطئ','region':'جزيرة سكاي','lat':57.50085,'lon':-6.63713,'display':'Coral Beach, Claigan, Isle of Skye, Scotland'},
 {'ar':'رصيف سانت أندروز','en':'St Andrews Pier','cat':'رصيف','region':'سانت أندروز','lat':56.339722,'lon':-2.783056,'display':'Pier, St Andrews, Fife, Scotland'},
 {'ar':'ميناء سانت مونانز','en':'St Monans Harbour','cat':'ميناء','region':'فايف','lat':56.20372,'lon':-2.76561,'display':'St Monans Harbour, Fife, Scotland'},
 {'ar':'النسيج العظيم لاسكتلندا','en':'The Great Tapestry of Scotland','cat':'متحف وتجربة ثقافية','region':'غالا شيلز','lat':55.617406,'lon':-2.809538,'display':'14-20 High Street, Galashiels TD1 1SD, Scotland'},
 {'ar':'غالاوي فورست بارك','en':'Galloway Forest Park','cat':'غابة ومنتزه','region':'دومفريز وغالاوي','lat':55.126944,'lon':-4.430278,'display':'Galloway Forest Park, Scotland'},
 {'ar':'كيتشن كوز آند يوز','en':'Kitchen Coos and Ewes','cat':'مزرعة وتجربة','region':'دومفريز وغالاوي','lat':54.921194,'lon':-4.879194,'display':'High Airyolland Farm, New Luce, Newton Stewart DG8 0AU, Scotland'},
 {'ar':'شاطئ كيلدونان','en':'Kildonan Beach Arran','cat':'شاطئ','region':'جزيرة أران','lat':55.44010,'lon':-5.14500,'display':'Kildonan Beach, Isle of Arran, Scotland'},
 {'ar':'ميناء توبرموري','en':'Tobermory Harbour','cat':'ميناء','region':'جزيرة مول','lat':56.62017,'lon':-6.06647,'display':'Tobermory Harbour, Isle of Mull, Scotland'},
]

rows=[]
with open('scotland-additions-final.csv',encoding='utf-8-sig') as f:
    for r in csv.DictReader(f): rows.append({'ar':r['Arabic'],'en':r['English'],'cat':r['Category'],'region':r['Region'],'lat':float(r['Latitude']),'lon':float(r['Longitude']),'display':r['OSM display']})
existing={r['en'].lower() for r in rows}
for p in MANUAL:
    if p['en'].lower() not in existing: rows.append(p);existing.add(p['en'].lower())

ICON_MAP={'قلعة':'images/icon-33.png','قصر':'images/icon-29.png','معلم':'images/icon-29.png','متحف':'images/icon-29.png','منزل':'images/icon-29.png','موقع أثري':'images/icon-29.png','حديقة':'images/icon-8.png','منتزه':'images/icon-8.png','غابة':'images/icon-8.png','محمية':'images/icon-8.png','وادي':'images/icon-8.png','طبيعة':'images/icon-8.png','شاطئ':'images/icon-17.png','بحيرة':'images/icon-17.png','شلال':'images/icon-25.png','ساحل':'images/icon-17.png','مطل':'images/icon-4.png','منارة':'images/icon-4.png','صخرة':'images/icon-4.png','شارع':'images/icon-7.png','ممشى':'images/icon-7.png','مسار':'images/icon-7.png','طريق':'images/icon-7.png','حي':'images/icon-19.png','قرية':'images/icon-1.png','بلدة':'images/icon-19.png','ميناء':'images/icon-48.png','رصيف':'images/icon-48.png','قناة':'images/icon-48.png','مقهى':'images/icon-15.png','شوكولاتة':'images/icon-79.png','مطعم':'images/icon-3.png','مزرعة':'images/icon-78.png','متجر':'images/icon-35.png','تسوق':'images/icon-35.png','ملاهي':'images/icon-12.png','مغامرات':'images/icon-12.png','ترفيه':'images/icon-12.png','أكواريوم':'images/icon-24.png','حديقة حيوان':'images/icon-24.png','دراجات':'images/icon-12.png','مرصد':'images/icon-29.png','مركز زوار':'images/icon-29.png','سد':'images/icon-29.png','فن شوارع':'images/icon-7.png','فن':'images/icon-29.png'}
def icon(cat):
 for k,v in ICON_MAP.items():
  if k in cat:return v
 return 'images/icon-29.png'
def emo(cat):
 for k,e in [('قلعة','🏰'),('قصر','🏛️'),('متحف','🏛️'),('حديقة','🌳'),('منتزه','🌳'),('غابة','🌲'),('محمية','🌿'),('شاطئ','🏖️'),('شلال','🌊'),('بحيرة','🌊'),('مطل','🌄'),('منارة','🌊'),('ميناء','⚓'),('رصيف','⚓'),('مقهى','☕'),('مطعم','🍴'),('شوكولاتة','🍫'),('مزرعة','🐮'),('ملاهي','🎢'),('مغامرات','🧗'),('أكواريوم','🐧'),('حديقة حيوان','🐾'),('شارع','🚶'),('ممشى','🚶'),('مسار','🚶'),('قرية','🏘️'),('بلدة','🏘️'),('موقع أثري','🗿'),('مرصد','🔭'),('جسر','🌉')]:
  if k in cat:return e
 return '📍'

TMP='_scotland_manual';shutil.rmtree(TMP,ignore_errors=True);os.makedirs(os.path.join(TMP,'out','icons'),exist_ok=True)
with zipfile.ZipFile('Austria.kmz') as z:z.extractall(os.path.join(TMP,'donor'))
def donor(rel):
 bn=os.path.basename(rel)
 for root,ds,fs in os.walk(os.path.join(TMP,'donor')):
  if bn in fs and root.replace('\\','/').endswith('/images'): return open(os.path.join(root,bn),'rb').read()
 raise FileNotFoundError(rel)
used={icon(r['cat']) for r in rows};local={}
for rel in used:
 bn=os.path.basename(rel);Image.open(io.BytesIO(donor(rel))).convert('RGBA').resize((30,30),Image.Resampling.LANCZOS).save(os.path.join(TMP,'out','icons',bn));local[rel]='icons/'+bn
K='http://www.opengis.net/kml/2.2';ET.register_namespace('',K);root=ET.Element('{%s}kml'%K);doc=ET.SubElement(root,'{%s}Document'%K);ET.SubElement(doc,'{%s}name'%K).text='إضافات خريطة اسكتلندا السياحية 2026'
styles={}
for i,rel in enumerate(sorted(used),1):
 sid='s'+str(i);styles[rel]=sid;s=ET.SubElement(doc,'{%s}Style'%K,{'id':sid});isx=ET.SubElement(s,'{%s}IconStyle'%K);ET.SubElement(isx,'{%s}scale'%K).text='1.0';ic=ET.SubElement(isx,'{%s}Icon'%K);ET.SubElement(ic,'{%s}href'%K).text=local[rel]
folder=ET.SubElement(doc,'{%s}Folder'%K);ET.SubElement(folder,'{%s}name'%K).text='إضافات اسكتلندا الجديدة'
for r in rows:
 pm=ET.SubElement(folder,'{%s}Placemark'%K);ET.SubElement(pm,'{%s}name'%K).text=f"{r['ar']} – {r['cat']} {emo(r['cat'])}";ET.SubElement(pm,'{%s}styleUrl'%K).text='#'+styles[icon(r['cat'])]
 ET.SubElement(pm,'{%s}description'%K).text=f"الاسم الرسمي بالإنجليزية: {r['en']}<br/>موقع سياحي في منطقة {r['region']} ضمن فئة {r['cat']}، تمت إضافته بعد التحقق من موقعه. يُنصح بالتحقق من أوقات العمل أو شروط الزيارة عند الحاجة.<br/><br/>جميع الحقوق محفوظة للخرائط السياحية."
 pt=ET.SubElement(pm,'{%s}Point'%K);ET.SubElement(pt,'{%s}coordinates'%K).text=f"{r['lon']:.7f},{r['lat']:.7f},0"
ET.ElementTree(root).write(os.path.join(TMP,'out','doc.kml'),encoding='utf-8',xml_declaration=True)
OUT='scotland-additions-2026-final-verified.kmz'
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
 z.write(os.path.join(TMP,'out','doc.kml'),'doc.kml')
 for f in os.listdir(os.path.join(TMP,'out','icons')):z.write(os.path.join(TMP,'out','icons',f),'icons/'+f)
with open('scotland-additions-verified-report.txt','w',encoding='utf-8') as f:
 f.write(f'المرشحون الأصليون: 172\nالمدرجون النهائيون بإحداثيات مؤكدة: {len(rows)}\nالمستبعدون لعدم توفر نقطة دقيقة واحدة: 2 (City Centre Mural Trail, Open Close Dundee)\nالمستبعد بسبب ارتباط المكان بتصنيف بار/كحول: 1 (Gretna Green Famous Blacksmiths Shop)\n')
with open('scotland-additions-final-verified.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Arabic','English','Category','Region','Latitude','Longitude','Source display']);
 for r in rows:w.writerow([r['ar'],r['en'],r['cat'],r['region'],r['lat'],r['lon'],r['display']])
print('final',len(rows))
