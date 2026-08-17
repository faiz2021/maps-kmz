import csv, io, os, re, time, json, math, shutil, zipfile, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from PIL import Image

FAILED = [
('مسار جداريات وسط غلاسكو','City Centre Mural Trail','فن شوارع','غلاسكو',['Glasgow City Centre Mural Trail','Mural Trail Glasgow']),
('داماسكينو','Damasqino Restaurant & Cafe','مطعم حلال','غلاسكو',['Damasqino Glasgow','Damasqino Restaurant Glasgow']),
('مسار لوخ نيس 360','Loch Ness 360 Trail','مسار','لوخ نيس',['Loch Ness 360° Trail','Loch Ness 360']),
('أقفال دوخغاروخ','Dochgarroch Locks','قناة وأقفال','إنفرنيس',['Dochgarroch Lock','Dochgarroch Locks Inverness']),
('شاطئ بالناكيل','Balnakeil Beach','شاطئ','الهايلاند',['Balnakeil Bay','Balnakeil Beach Durness']),
('ميناء أولابول','Ullapool Harbour','ميناء','أولابول',['Ullapool Ferry Terminal','Ullapool Pier','Ullapool Harbour']),
('إمبير كافيه','Ember Kafe Inverness','مقهى ومطعم حلال','إنفرنيس',['Ember Kafe','Ember Cafe Inverness']),
('فيري غلين','The Fairy Glen Skye','طبيعة','جزيرة سكاي',['Fairy Glen Uig','The Fairy Glen Uig']),
('شاطئ كورال','Coral Beach Skye','شاطئ','جزيرة سكاي',['Claigan Coral Beach','Coral Beach Claigan']),
('براذرز بوينت','Brother\'s Point','ساحل وممشى','جزيرة سكاي',['Rubha nam Brathairean','Brothers Point Skye']),
('ميناء إلجول','Elgol Harbour','ميناء ومطل','جزيرة سكاي',['Elgol Pier','Elgol Jetty','Elgol']),
('مطل بواخيل إتيف مور','Buachaille Etive Mor Viewpoint','مطل','غلينكو',['Buachaille Etive Mor','Buachaille Etive Mòr']),
('مطل لوخ أختريوختان','Loch Achtriochtan Viewpoint','مطل','غلينكو',['Loch Achtriochtan','Loch Achtriochtan Glencoe']),
('شاطئ لوخ مورليتش','Loch Morlich Beach','بحيرة وشاطئ','أفيمور',['Loch Morlich','Loch Morlich Beach']),
('غابة روثيميركوس','Rothiemurchus Forest','غابة','أفيمور',['Rothiemurchus','Rothiemurchus Forest']),
('مركز لوخ غارتن للطبيعة','RSPB Loch Garten Nature Centre','محمية وطبيعة','أفيمور',['Loch Garten Osprey Centre','RSPB Loch Garten','Loch Garten Nature Centre']),
('مضيق كيليكرانكي','Killiecrankie Gorge','مضيق وممشى','بيتلوتشري',['Pass of Killiecrankie','Killiecrankie']),
('قفزة الجندي','Soldier\'s Leap Killiecrankie','معلم طبيعي','كيليكرانكي',['Soldier’s Leap','Soldiers Leap Killiecrankie']),
('هايلاند شوكولاتير','The Highland Chocolatier','شوكولاتة ومقهى','غراندتولي',['Iain Burnett Highland Chocolatier','Highland Chocolatier Grandtully']),
('ذا لودج فورست فيزيتور سنتر','The Lodge Forest Visitor Centre','غابة ومركز زوار','أبيرفويل',['The Lodge Forest Visitor Centre Aberfoyle','The Lodge Aberfoyle']),
('رصيف سانت أندروز','St Andrews Pier','رصيف','سانت أندروز',['St Andrews Harbour Pier','St Andrews Pier']),
('ميناء سانت مونانز','St Monans Harbour','ميناء','فايف',['St Monans Harbour','St Monans Pier']),
('مسارات أوبن كلوز دندي','Open Close Dundee','فن شوارع','دندي',['Open Close Dundee','Open/Close Dundee']),
('وايلد شور دندي','Wildshore Dundee','ترفيه مائي','دندي',['Wild Shore Dundee','Wildshore Dundee']),
('النسيج العظيم لاسكتلندا','The Great Tapestry of Scotland','متحف وتجربة ثقافية','غالا شيلز',['Great Tapestry of Scotland Galashiels','The Great Tapestry of Scotland']),
('غالاوي فورست بارك','Galloway Forest Park','غابة ومنتزه','دومفريز وغالاوي',['Galloway Forest Park','Galloway Forest']),
('غري ميرز تيل','Grey Mare\'s Tail Nature Reserve','شلال ومحمية','موفات',['Grey Mare’s Tail','Grey Mares Tail Waterfall Moffat']),
('قلعة وحدائق دراملانريغ','Drumlanrig Castle and Gardens','قلعة وحدائق','دومفريز وغالاوي',['Drumlanrig Castle','Drumlanrig Castle and Gardens']),
('متجر الحداد الشهير في غريتنا غرين','Gretna Green Famous Blacksmiths Shop','معلم تاريخي ومتجر','غريتنا غرين',['Famous Blacksmiths Shop Gretna Green','Gretna Green Blacksmiths Shop']),
('ويغتاون بلدة الكتب','Wigtown Book Town','بلدة ثقافية','ويغتاون',['Wigtown','Scotland’s National Book Town Wigtown']),
('كيتشن كوز آند يوز','Kitchen Coos and Ewes','مزرعة وتجربة','دومفريز وغالاوي',['Kitchen Coos & Ewes','Kitchen Coos and Ewes']),
('كيلبورن كاسل إستيت','Kelburn Castle and Estate','قلعة وحدائق','أيرشاير',['Kelburn Castle','Kelburn Estate']),
('قلعة وحدائق بروديك','Brodick Castle Garden and Country Park','قلعة ومنتزه','جزيرة أران',['Brodick Castle','Brodick Castle and Country Park']),
('دوائر ماتشري مور الحجرية','Machrie Moor Stone Circles','موقع أثري','جزيرة أران',['Machrie Moor','Machrie Moor Stone Circles']),
('شاطئ كيلدونان','Kildonan Beach Arran','شاطئ','جزيرة أران',['Kildonan Beach','Kildonan Bay Arran']),
('وست كيلبرايد بلدة الحرف','West Kilbride Craft Town','بلدة وتسوق','أيرشاير',['West Kilbride','Craft Town Scotland West Kilbride']),
('قلعة ومتحف دونولي','Dunollie Museum Castle and Grounds','قلعة ومتحف','أوبان',['Dunollie Castle','Dunollie Museum Castle and Grounds']),
('ميناء توبرموري','Tobermory Harbour','ميناء','جزيرة مول',['Tobermory Harbour Mull','Tobermory Isle of Mull']),
('خليج كالغاري','Calgary Bay Mull','شاطئ','جزيرة مول',['Calgary Bay','Calgary Beach Mull']),
('قلعة ومتحف لويس','Lews Castle Museum nan Eilean','قصر ومتحف','جزيرة لويس',['Lews Castle','Museum nan Eilean Lews Castle']),
('مطل سيليبوست','Seilebost Viewpoint','مطل','هاريس',['Seilebost','Seilebost Beach Viewpoint']),
('منحدرات يسنابي','Yesnaby Cliffs','ساحل ومطل','أوركني',['Yesnaby','Yesnaby Cliffs Orkney']),
('منحدرات إشانيس','Eshaness Cliffs','ساحل ومطل','شيتلاند',['Eshaness','Eshaness Cliffs Shetland']),
('مطل موكل فلوغا','Muckle Flugga Viewpoint','مطل','شيتلاند',['Muckle Flugga','Muckle Flugga Lighthouse']),
]

BANNED=re.compile(r'(?i)\b(church|cathedral|abbey|chapel|whisky|whiskey|distillery|gin|brewery|beer|wine|bar\b|pub\b)')
def valid(lat,lon): return 54.45<=lat<=61.1 and -8.75<=lon<=-0.4

def geocode(aliases,region):
    for alias in aliases:
        for q in [f'{alias}, {region}, Scotland, United Kingdom', f'{alias}, Scotland, United Kingdom']:
            url='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({'q':q,'format':'jsonv2','limit':5,'addressdetails':1,'countrycodes':'gb'})
            req=urllib.request.Request(url,headers={'User-Agent':'TouristMapsScotlandAudit/2026 info@touristmapspro.com'})
            try:
                with urllib.request.urlopen(req,timeout=25) as r: arr=json.load(r)
            except Exception: arr=[]
            time.sleep(1.05)
            for x in arr:
                try: lat=float(x['lat']);lon=float(x['lon'])
                except: continue
                if valid(lat,lon): return lat,lon,x.get('display_name','')
    return None

# Read the already-verified 128 from previous pass.
rows=[]
with open('scotland-additions-resolved.csv',encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        rows.append({'ar':r['Arabic'],'en':r['English'],'cat':r['Category'],'region':r['Region'],'lat':float(r['Latitude']),'lon':float(r['Longitude']),'display':r['OSM display']})

existing={re.sub(r'[^a-z0-9]+','',r['en'].lower()) for r in rows}
unresolved=[]
for ar,en,cat,region,aliases in FAILED:
    if BANNED.search(en) or BANNED.search(ar):
        unresolved.append((ar,en,'blocked'));continue
    key=re.sub(r'[^a-z0-9]+','',en.lower())
    if key in existing: continue
    g=geocode(aliases,region)
    if g:
        lat,lon,display=g; rows.append({'ar':ar,'en':en,'cat':cat,'region':region,'lat':lat,'lon':lon,'display':display}); existing.add(key)
    else: unresolved.append((ar,en,'unresolved'))

# Donor Tourist Maps icon mapping.
ICON_MAP={
 'قلعة':'images/icon-33.png','قصر':'images/icon-29.png','معلم':'images/icon-29.png','متحف':'images/icon-29.png','منزل':'images/icon-29.png','موقع أثري':'images/icon-29.png','حديقة':'images/icon-8.png','منتزه':'images/icon-8.png','غابة':'images/icon-8.png','محمية':'images/icon-8.png','وادي':'images/icon-8.png','طبيعة':'images/icon-8.png','شاطئ':'images/icon-17.png','بحيرة':'images/icon-17.png','شلال':'images/icon-25.png','ساحل':'images/icon-17.png','مطل':'images/icon-4.png','منارة':'images/icon-4.png','صخرة':'images/icon-4.png','شارع':'images/icon-7.png','ممشى':'images/icon-7.png','مسار':'images/icon-7.png','طريق':'images/icon-7.png','حي':'images/icon-19.png','قرية':'images/icon-1.png','بلدة':'images/icon-19.png','ميناء':'images/icon-48.png','رصيف':'images/icon-48.png','قناة':'images/icon-48.png','مقهى':'images/icon-15.png','شوكولاتة':'images/icon-79.png','مطعم':'images/icon-3.png','مزرعة':'images/icon-78.png','متجر':'images/icon-35.png','تسوق':'images/icon-35.png','ملاهي':'images/icon-12.png','مغامرات':'images/icon-12.png','ترفيه':'images/icon-12.png','أكواريوم':'images/icon-24.png','حديقة حيوان':'images/icon-24.png','دراجات':'images/icon-12.png','مرصد':'images/icon-29.png','مركز زوار':'images/icon-29.png','سد':'images/icon-29.png','فن شوارع':'images/icon-7.png','فن':'images/icon-29.png'}
def icon(cat):
    for k,v in ICON_MAP.items():
        if k in cat:return v
    return 'images/icon-29.png'
def emo(cat):
    for k,e in [('قلعة','🏰'),('قصر','🏛️'),('متحف','🏛️'),('حديقة','🌳'),('منتزه','🌳'),('غابة','🌲'),('محمية','🌿'),('شاطئ','🏖️'),('شلال','🌊'),('بحيرة','🌊'),('مطل','🌄'),('منارة','🌊'),('ميناء','⚓'),('رصيف','⚓'),('مقهى','☕'),('مطعم','🍴'),('شوكولاتة','🍫'),('مزرعة','🐮'),('ملاهي','🎢'),('مغامرات','🧗'),('أكواريوم','🐧'),('حديقة حيوان','🐾'),('شارع','🚶'),('ممشى','🚶'),('مسار','🚶'),('قرية','🏘️'),('بلدة','🏘️'),('موقع أثري','🗿'),('مرصد','🔭'),('جسر','🌉')]:
        if k in cat:return e
    return '📍'

TMP='_scotland_final';shutil.rmtree(TMP,ignore_errors=True);os.makedirs(os.path.join(TMP,'out','icons'),exist_ok=True)
with zipfile.ZipFile('Austria.kmz') as z:z.extractall(os.path.join(TMP,'donor'))
def donor(rel):
    bn=os.path.basename(rel)
    for root,ds,fs in os.walk(os.path.join(TMP,'donor')):
        if bn in fs and root.replace('\\','/').endswith('/images'):
            return open(os.path.join(root,bn),'rb').read()
    raise FileNotFoundError(rel)
used={icon(r['cat']) for r in rows}; locals={}
for rel in used:
    bn=os.path.basename(rel);im=Image.open(io.BytesIO(donor(rel))).convert('RGBA').resize((30,30),Image.Resampling.LANCZOS);im.save(os.path.join(TMP,'out','icons',bn));locals[rel]='icons/'+bn
K='http://www.opengis.net/kml/2.2';ET.register_namespace('',K);root=ET.Element('{%s}kml'%K);doc=ET.SubElement(root,'{%s}Document'%K);ET.SubElement(doc,'{%s}name'%K).text='إضافات خريطة اسكتلندا السياحية 2026'
styles={}
for i,rel in enumerate(sorted(used),1):
    sid='s'+str(i);styles[rel]=sid;s=ET.SubElement(doc,'{%s}Style'%K,{'id':sid});isx=ET.SubElement(s,'{%s}IconStyle'%K);ET.SubElement(isx,'{%s}scale'%K).text='1.0';ic=ET.SubElement(isx,'{%s}Icon'%K);ET.SubElement(ic,'{%s}href'%K).text=locals[rel]
folder=ET.SubElement(doc,'{%s}Folder'%K);ET.SubElement(folder,'{%s}name'%K).text='إضافات اسكتلندا الجديدة'
for r in rows:
    pm=ET.SubElement(folder,'{%s}Placemark'%K);ET.SubElement(pm,'{%s}name'%K).text=f"{r['ar']} – {r['cat']} {emo(r['cat'])}";ET.SubElement(pm,'{%s}styleUrl'%K).text='#'+styles[icon(r['cat'])]
    ET.SubElement(pm,'{%s}description'%K).text=f"الاسم الرسمي بالإنجليزية: {r['en']}<br/>موقع سياحي في منطقة {r['region']} ضمن فئة {r['cat']}، تمت إضافته بعد التحقق من موقعه. يُنصح بالتحقق من أوقات العمل أو شروط الزيارة عند الحاجة.<br/><br/>جميع الحقوق محفوظة للخرائط السياحية."
    pt=ET.SubElement(pm,'{%s}Point'%K);ET.SubElement(pt,'{%s}coordinates'%K).text=f"{r['lon']:.7f},{r['lat']:.7f},0"
ET.ElementTree(root).write(os.path.join(TMP,'out','doc.kml'),encoding='utf-8',xml_declaration=True)
OUT='scotland-additions-2026-final.kmz'
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(TMP,'out','doc.kml'),'doc.kml')
    for f in os.listdir(os.path.join(TMP,'out','icons')):z.write(os.path.join(TMP,'out','icons',f),'icons/'+f)
with open('scotland-additions-final-report.txt','w',encoding='utf-8') as f:
    f.write(f'إجمالي المرشحين الأصلي: 172\nالمدرجون في الملف النهائي: {len(rows)}\nالمتبقي غير محسوم تلقائيًا: {len(unresolved)}\n\n')
    for x in unresolved:f.write(' | '.join(x)+'\n')
with open('scotland-additions-final.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['Arabic','English','Category','Region','Latitude','Longitude','OSM display']);
    for r in rows:w.writerow([r['ar'],r['en'],r['cat'],r['region'],r['lat'],r['lon'],r['display']])
print(json.dumps({'final':len(rows),'unresolved':len(unresolved)},ensure_ascii=False))
