import csv, io, os, re, time, json, math, shutil, zipfile, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from PIL import Image

# Final reviewed candidate set outside Edinburgh additions.
# Churches/cathedrals/abbeys/chapels and alcohol/whisky/gin/distillery venues are intentionally excluded.
PLACES = [
('الحدائق المخفية','The Hidden Gardens','حديقة','غلاسكو'),
('مسار جداريات وسط غلاسكو','City Centre Mural Trail','فن شوارع','غلاسكو'),
('كوينز بارك','Queen\'s Park Glasgow','حديقة ومطل','غلاسكو'),
('ذا هيدن لين','The Hidden Lane','حي فني','غلاسكو'),
('بروفاندز لوردشيب','Provand\'s Lordship','منزل تاريخي','غلاسكو'),
('متحف شرطة غلاسكو','Glasgow Police Museum','متحف','غلاسكو'),
('داماسكينو','Damasqino Restaurant & Cafe','مطعم حلال','غلاسكو'),
('رانجيتس كيتشن','Ranjit\'s Kitchen','مطعم نباتي','غلاسكو'),
('أوتومان كوفي هاوس','Ottoman Coffeehouse','مقهى','غلاسكو'),
('حدائق إنفرنيس النباتية','Inverness Botanic Gardens','حديقة نباتية','إنفرنيس'),
('جزر نيس','Ness Islands','منتزه','إنفرنيس'),
('ممشى نهر نيس','River Ness Walk','ممشى','إنفرنيس'),
('مسار لوخ نيس 360','Loch Ness 360 Trail','مسار','لوخ نيس'),
('أقفال دوخغاروخ','Dochgarroch Locks','قناة وأقفال','إنفرنيس'),
('شاطئ دوريس','Dores Beach','شاطئ','لوخ نيس'),
('غابة خليج أوركهارت','Urquhart Bay Woods','غابة','لوخ نيس'),
('شلالات بلودا','Plodda Falls','شلال','الهايلاند'),
('شلالات شين','Falls of Shin','شلال','الهايلاند'),
('مطل بيلاك نا با','Bealach na Ba Viewpoint','مطل','الهايلاند'),
('شاطئ أكميلفيتش','Achmelvich Beach','شاطئ','الهايلاند'),
('شاطئ بالناكيل','Balnakeil Beach','شاطئ','الهايلاند'),
('ميناء أولابول','Ullapool Harbour','ميناء','أولابول'),
('قرية شيلديغ','Shieldaig','قرية','الهايلاند'),
('إمبير كافيه','Ember Kafe Inverness','مقهى ومطعم حلال','إنفرنيس'),
('فيري غلين','The Fairy Glen Skye','طبيعة','جزيرة سكاي'),
('منارة نيست بوينت','Neist Point Lighthouse','منارة ومطل','جزيرة سكاي'),
('شاطئ كورال','Coral Beach Skye','شاطئ','جزيرة سكاي'),
('متحف ستافين للديناصورات','Staffin Dinosaur Museum','متحف','جزيرة سكاي'),
('متحف حياة الجزيرة','Skye Museum of Island Life','متحف','جزيرة سكاي'),
('شلالات ليلت','Lealt Falls','شلال','جزيرة سكاي'),
('براذرز بوينت','Brother\'s Point','ساحل وممشى','جزيرة سكاي'),
('ميناء إلجول','Elgol Harbour','ميناء ومطل','جزيرة سكاي'),
('جسر سليغاشان القديم','Sligachan Old Bridge','جسر ومعلم','جزيرة سكاي'),
('سلم نبتون','Neptune\'s Staircase','قناة وأقفال','فورت ويليام'),
('متحف ويست هايلاند','West Highland Museum','متحف','فورت ويليام'),
('شلال ستيل','Steall Waterfall','شلال','فورت ويليام'),
('مركز زوار غلين نيفيس','Glen Nevis Visitor Centre','مركز زوار','فورت ويليام'),
('غلينكو لوخان','Glencoe Lochan','بحيرة وممشى','غلينكو'),
('سيغنال روك','Signal Rock Glencoe','غابة وممشى','غلينكو'),
('مطل بواخيل إتيف مور','Buachaille Etive Mor Viewpoint','مطل','غلينكو'),
('مطل لوخ أختريوختان','Loch Achtriochtan Viewpoint','مطل','غلينكو'),
('شاطئ لوخ مورليتش','Loch Morlich Beach','بحيرة وشاطئ','أفيمور'),
('غابة روثيميركوس','Rothiemurchus Forest','غابة','أفيمور'),
('لوخ آن إيليين','Loch an Eilein','بحيرة وممشى','أفيمور'),
('مركز لوخ غارتن للطبيعة','RSPB Loch Garten Nature Centre','محمية وطبيعة','أفيمور'),
('متحف هايلاند الشعبي','Highland Folk Museum','متحف مفتوح','نيوتنمور'),
('هايلاند وايلد لايف بارك','Highland Wildlife Park','حديقة حيوان','كينغوسي'),
('ثكنات روثفن','Ruthven Barracks','معلم تاريخي','كينغوسي'),
('لاغان وولف تراكس','Laggan Wolftrax','دراجات ومغامرات','لاغان'),
('لاند مارك فورست أدفنتشر بارك','Landmark Forest Adventure Park','ملاهي ومغامرات','كاربرج'),
('غابة فاسكالي','Faskally Wood','غابة','بيتلوتشري'),
('مضيق كيليكرانكي','Killiecrankie Gorge','مضيق وممشى','بيتلوتشري'),
('قفزة الجندي','Soldier\'s Leap Killiecrankie','معلم طبيعي','كيليكرانكي'),
('شلال بلاك سباوت','Black Spout Waterfall Pitlochry','شلال','بيتلوتشري'),
('مركز سد بيتلوتشري','Pitlochry Dam Visitor Centre','سد ومركز زوار','بيتلوتشري'),
('بحيرة فاسكالي','Loch Faskally','بحيرة وممشى','بيتلوتشري'),
('حديقة المستكشفين','Explorers Garden Pitlochry','حديقة','بيتلوتشري'),
('هايلاند شوكولاتير','The Highland Chocolatier','شوكولاتة ومقهى','غراندتولي'),
('متحف بيرث','Perth Museum','متحف','بيرث'),
('سجن ستيرلنغ القديم','Stirling Old Town Jail','معلم تاريخي','ستيرلنغ'),
('تل دميات','Dumyat','مطل ومسار','ستيرلنغ'),
('غو إيب أبيرفويل','Go Ape Aberfoyle','مغامرات','أبيرفويل'),
('ذا لودج فورست فيزيتور سنتر','The Lodge Forest Visitor Centre','غابة ومركز زوار','أبيرفويل'),
('طريق البحيرات الثلاث','Three Lochs Forest Drive','طريق بانورامي','تروساكس'),
('ذا باينابل','The Pineapple Dunmore','معلم وحديقة','فالكيرك'),
('حديقة سانت أندروز النباتية','St Andrews Botanic Garden','حديقة نباتية','سانت أندروز'),
('ويست ساندز','West Sands St Andrews','شاطئ','سانت أندروز'),
('أكواريوم سانت أندروز','St Andrews Aquarium','أكواريوم','سانت أندروز'),
('متحف واردلو','Wardlaw Museum','متحف','سانت أندروز'),
('متحف عالم الغولف','World Golf Museum','متحف رياضي','سانت أندروز'),
('رصيف سانت أندروز','St Andrews Pier','رصيف','سانت أندروز'),
('ميناء كريل','Crail Harbour','ميناء','فايف'),
('بيتنكريف بارك','Pittencrieff Park','منتزه','دنفرملين'),
('المتحف الاسكتلندي لمصايد الأسماك','Scottish Fisheries Museum','متحف','أنستروثر'),
('ميناء سانت مونانز','St Monans Harbour','ميناء','فايف'),
('مسارات أوبن كلوز دندي','Open Close Dundee','فن شوارع','دندي'),
('دندي لو','Dundee Law','مطل','دندي'),
('مرصد ميلز','Mills Observatory','مرصد','دندي'),
('كامبرداون كانتري بارك','Camperdown Country Park','منتزه','دندي'),
('كامبرداون وايلد لايف سنتر','Camperdown Wildlife Centre','حديقة حيوان','دندي'),
('فيردانت ووركس','Verdant Works','متحف صناعي','دندي'),
('وايلد شور دندي','Wildshore Dundee','ترفيه مائي','دندي'),
('شاطئ بروتي فيري','Broughty Ferry Beach','شاطئ','دندي'),
('منحدرات أربروث','Arbroath Cliffs','ساحل وممشى','أربروث'),
('كرومبي كانتري بارك','Crombie Country Park','منتزه وغابة','أنغوس'),
('كوري في','Corrie Fee','وادي ومسار','أنغوس'),
('شاطئ أبردين','Aberdeen Beach','شاطئ','أبردين'),
('فوتدي','Footdee Fittie','قرية صيد تاريخية','أبردين'),
('داثي بارك','Duthie Park','حديقة','أبردين'),
('حدائق ديفيد ويلش الشتوية','David Welch Winter Gardens','حديقة نباتية','أبردين'),
('جونستون غاردنز','Johnston Gardens Aberdeen','حديقة','أبردين'),
('شارع يونيون','Union Street Aberdeen','شارع وتسوق','أبردين'),
('بروفوست سكينز هاوس','Provost Skene\'s House','منزل تاريخي','أبردين'),
('بطارية توري','Torry Battery','مطل ساحلي','أبردين'),
('غريهوب باي','Greyhope Bay','مطل ساحلي','أبردين'),
('شاطئ بالميدي','Balmedie Beach','شاطئ','أبردينشير'),
('شاطئ نيوبرغ للأختام','Newburgh Beach Aberdeenshire','شاطئ وحياة برية','أبردينشير'),
('بيرن أو فات','Burn O\'Vat','معلم طبيعي','أبردينشير'),
('النسيج العظيم لاسكتلندا','The Great Tapestry of Scotland','متحف وتجربة ثقافية','غالا شيلز'),
('أبوتسفورد هاوس','Abbotsford House','منزل تاريخي','الحدود الاسكتلندية'),
('محمية سانت أبس هيد','St Abb\'s Head National Nature Reserve','محمية ساحلية','الحدود الاسكتلندية'),
('مطل سكوت','Scott\'s View','مطل','الحدود الاسكتلندية'),
('قلعة فلورز','Floors Castle','قلعة وحدائق','كيلسو'),
('بو هيل هاوس','Bowhill House','قصر وحدائق','سيلكيرك'),
('سجن قلعة جيدبرغ','Jedburgh Castle Jail and Museum','متحف تاريخي','جيدبرغ'),
('هاريستانز','Harestanes Countryside Visitor Centre','مركز ريفي','الحدود الاسكتلندية'),
('غلينتريس فورست','Glentress Forest','غابة ودراجات','بيبلز'),
('جسر ليدرفوت','Leaderfoot Viaduct','جسر تاريخي','الحدود الاسكتلندية'),
('قلعة كيرلافروك','Caerlaverock Castle','قلعة تاريخية','دومفريز'),
('حديقة لوغان النباتية','Logan Botanic Garden','حديقة نباتية','دومفريز وغالاوي'),
('غالاوي فورست بارك','Galloway Forest Park','غابة ومنتزه','دومفريز وغالاوي'),
('غري ميرز تيل','Grey Mare\'s Tail Nature Reserve','شلال ومحمية','موفات'),
('قلعة وحدائق دراملانريغ','Drumlanrig Castle and Gardens','قلعة وحدائق','دومفريز وغالاوي'),
('متجر الحداد الشهير في غريتنا غرين','Gretna Green Famous Blacksmiths Shop','معلم تاريخي ومتجر','غريتنا غرين'),
('كراويك ملتيفيرس','Crawick Multiverse','منتزه فني','سانكوهار'),
('موات براي','Moat Brae','مركز أدب وقصص','دومفريز'),
('ويغتاون بلدة الكتب','Wigtown Book Town','بلدة ثقافية','ويغتاون'),
('منارة مول أوف غالاوي','Mull of Galloway Lighthouse','منارة ومطل','دومفريز وغالاوي'),
('ميناء بورتباتريك','Portpatrick Harbour','ميناء','بورتباتريك'),
('كيتشن كوز آند يوز','Kitchen Coos and Ewes','مزرعة وتجربة','دومفريز وغالاوي'),
('متحف مسقط رأس روبرت برنز','Robert Burns Birthplace Museum','متحف','أير'),
('دين كاسل كانتري بارك','Dean Castle Country Park','قلعة ومنتزه','كيلمارنوك'),
('كيلبورن كاسل إستيت','Kelburn Castle and Estate','قلعة وحدائق','أيرشاير'),
('قلعة دونيور','Dunure Castle','قلعة ساحلية','أيرشاير'),
('هيدز أوف أير فارم بارك','Heads of Ayr Farm Park','مزرعة وترفيه','أير'),
('المتحف البحري الاسكتلندي','Scottish Maritime Museum','متحف بحري','إرفاين'),
('قلعة وحدائق بروديك','Brodick Castle Garden and Country Park','قلعة ومنتزه','جزيرة أران'),
('دوائر ماتشري مور الحجرية','Machrie Moor Stone Circles','موقع أثري','جزيرة أران'),
('شلالات غليناشديل','Glenashdale Falls','شلال','جزيرة أران'),
('شاطئ كيلدونان','Kildonan Beach Arran','شاطئ','جزيرة أران'),
('وست كيلبرايد بلدة الحرف','West Kilbride Craft Town','بلدة وتسوق','أيرشاير'),
('أوبان شوكولات كومباني','Oban Chocolate Company','شوكولاتة ومقهى','أوبان'),
('قلعة ومتحف دونولي','Dunollie Museum Castle and Grounds','قلعة ومتحف','أوبان'),
('غانافان ساندز','Ganavan Sands','شاطئ','أوبان'),
('بولبيت هيل','Pulpit Hill Oban','مطل','أوبان'),
('مركز كروشان لتوليد الطاقة','Cruachan Visitor Centre','مركز زوار وهندسة','أرغيل'),
('حديقة بنمور النباتية','Benmore Botanic Garden','حديقة نباتية','أرغيل'),
('سجن إنفيراري','Inveraray Jail','متحف تاريخي','إنفيراري'),
('متحف كيلمارتن','Kilmartin Museum','متحف آثار','أرغيل'),
('كيلمارتن غلين','Kilmartin Glen','موقع أثري','أرغيل'),
('ميناء توبرموري','Tobermory Harbour','ميناء','جزيرة مول'),
('خليج كالغاري','Calgary Bay Mull','شاطئ','جزيرة مول'),
('أروس بارك','Aros Park','منتزه وغابة','جزيرة مول'),
('قلعة ومتحف لويس','Lews Castle Museum nan Eilean','قصر ومتحف','جزيرة لويس'),
('شاطئ لوسكنتير','Luskentyre Beach','شاطئ','هاريس'),
('قرية غيرانان بلاك هاوس','Gearrannan Blackhouse Village','قرية تراثية','جزيرة لويس'),
('بروخ دون كارلواي','Dun Carloway Broch','موقع أثري','جزيرة لويس'),
('بلاك هاوس أرنول','The Blackhouse Arnol','متحف تراثي','جزيرة لويس'),
('بات أوف لويس','Butt of Lewis Lighthouse','منارة ومطل','جزيرة لويس'),
('ميناء ستورنوواي','Stornoway Harbour','ميناء','جزيرة لويس'),
('مطل سيليبوست','Seilebost Viewpoint','مطل','هاريس'),
('شاطئ هوشينيس','Huisinis Beach','شاطئ','هاريس'),
('سانت كيلدا','St Kilda Scotland','جزيرة وموقع طبيعي','هبرديس الخارجية'),
('حلقة برودغار','Ring of Brodgar','موقع أثري','أوركني'),
('أحجار ستينيس القائمة','Standing Stones of Stenness','موقع أثري','أوركني'),
('مايشو','Maeshowe','موقع أثري','أوركني'),
('بروخ أوف غيرنيس','Broch of Gurness','موقع أثري','أوركني'),
('برو أوف بيرساي','Brough of Birsay','موقع أثري ساحلي','أوركني'),
('منحدرات يسنابي','Yesnaby Cliffs','ساحل ومطل','أوركني'),
('الرجل العجوز في هوي','Old Man of Hoy','صخرة بحرية','أوركني'),
('متحف سكابا فلو','Scapa Flow Museum','متحف بحري','أوركني'),
('متحف سترومنيس','Stromness Museum','متحف','أوركني'),
('جارلسهوف','Jarlshof Prehistoric and Norse Settlement','موقع أثري','شيتلاند'),
('منارة سومبورغ هيد','Sumburgh Head Lighthouse','منارة ومطل','شيتلاند'),
('جزيرة سانت نينيان والممر الرملي','St Ninian\'s Isle','شاطئ وممشى','شيتلاند'),
('متحف وأرشيف شيتلاند','Shetland Museum and Archives','متحف','شيتلاند'),
('قلعة سكالاواي','Scalloway Castle','قلعة تاريخية','شيتلاند'),
('منحدرات إشانيس','Eshaness Cliffs','ساحل ومطل','شيتلاند'),
('محمية هيرمانيس','Hermaness National Nature Reserve','محمية ساحلية','شيتلاند'),
('مطل موكل فلوغا','Muckle Flugga Viewpoint','مطل','شيتلاند'),
('بروخ كليكمين','Clickimin Broch','موقع أثري','شيتلاند'),
('شاطئ ميل','Meal Beach Shetland','شاطئ','شيتلاند'),
]

# Explicit known pre-existing exclusions discovered in prior audits.
EXISTING_EN = {
 'The Hunterian','Stirling Smith Art Gallery and Museum','Battle of Bannockburn Experience','Blair Drummond Safari and Adventure Park',
 'Edinburgh Castle','Holyrood Palace','Craigmillar Castle','Forth Bridge','Stirling Castle','Linlithgow Palace','Doune Castle','Wallace Monument',
 'The Kelpies','Falkirk Wheel','Scone Palace','Fort William','Glencoe','Old Man of Storr','Mealt Falls','Armadale Castle','Inverness Castle','Dunnottar Castle'
}

BANNED = re.compile(r'(?i)\b(church|cathedral|abbey|chapel|whisky|whiskey|distillery|gin|brewery|beer|wine|bar\b|pub\b)')

# Scotland broad bounds incl. islands.
def valid_scotland(lat, lon):
    return 54.45 <= lat <= 61.1 and -8.75 <= lon <= -0.4

def norm(s):
    return re.sub(r'[^a-z0-9]+','',s.lower())

existing_norm = {norm(x) for x in EXISTING_EN}

def geocode(en, region):
    queries = [f'{en}, {region}, Scotland, United Kingdom', f'{en}, Scotland, United Kingdom']
    for q in queries:
        url='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({'q':q,'format':'jsonv2','limit':5,'addressdetails':1,'countrycodes':'gb'})
        req=urllib.request.Request(url,headers={'User-Agent':'TouristMapsScotlandAudit/2026 info@touristmapspro.com'})
        try:
            with urllib.request.urlopen(req,timeout=30) as r:
                arr=json.load(r)
        except Exception:
            arr=[]
        time.sleep(1.05)
        for item in arr:
            try: lat=float(item['lat']); lon=float(item['lon'])
            except Exception: continue
            if valid_scotland(lat,lon):
                return lat,lon,item.get('display_name',''),item.get('type','')
    return None

# Icon donor mapping from Tourist Maps Austria map family.
ICON_MAP={
 'قلعة':'images/icon-33.png','قصر':'images/icon-29.png','معلم':'images/icon-29.png','متحف':'images/icon-29.png','منزل':'images/icon-29.png','موقع أثري':'images/icon-29.png',
 'حديقة':'images/icon-8.png','منتزه':'images/icon-8.png','غابة':'images/icon-8.png','محمية':'images/icon-8.png','وادي':'images/icon-8.png','طبيعة':'images/icon-8.png',
 'شاطئ':'images/icon-17.png','بحيرة':'images/icon-17.png','شلال':'images/icon-25.png','ساحل':'images/icon-17.png',
 'مطل':'images/icon-4.png','منارة':'images/icon-4.png','صخرة':'images/icon-4.png',
 'شارع':'images/icon-7.png','ممشى':'images/icon-7.png','مسار':'images/icon-7.png','طريق':'images/icon-7.png','حي':'images/icon-19.png','قرية':'images/icon-1.png','بلدة':'images/icon-19.png',
 'ميناء':'images/icon-48.png','رصيف':'images/icon-48.png','قناة':'images/icon-48.png',
 'مقهى':'images/icon-15.png','شوكولاتة':'images/icon-79.png','مطعم':'images/icon-3.png','مزرعة':'images/icon-78.png','متجر':'images/icon-35.png','تسوق':'images/icon-35.png',
 'ملاهي':'images/icon-12.png','مغامرات':'images/icon-12.png','ترفيه':'images/icon-12.png','أكواريوم':'images/icon-24.png','حديقة حيوان':'images/icon-24.png','دراجات':'images/icon-12.png','مرصد':'images/icon-29.png','مركز زوار':'images/icon-29.png','سد':'images/icon-29.png','فن شوارع':'images/icon-7.png','فن':'images/icon-29.png'
}

def choose_icon(category):
    for key,path in ICON_MAP.items():
        if key in category: return path
    return 'images/icon-29.png'

def emoji(category):
    for k,e in [('قلعة','🏰'),('قصر','🏛️'),('متحف','🏛️'),('حديقة','🌳'),('منتزه','🌳'),('غابة','🌲'),('محمية','🌿'),('شاطئ','🏖️'),('شلال','🌊'),('بحيرة','🌊'),('مطل','🌄'),('منارة','🌊'),('ميناء','⚓'),('رصيف','⚓'),('مقهى','☕'),('مطعم','🍴'),('شوكولاتة','🍫'),('مزرعة','🐮'),('ملاهي','🎢'),('مغامرات','🧗'),('أكواريوم','🐧'),('حديقة حيوان','🐾'),('شارع','🚶'),('ممشى','🚶'),('مسار','🚶'),('قرية','🏘️'),('بلدة','🏘️'),('موقع أثري','🗿'),('مرصد','🔭'),('جسر','🌉')]:
        if k in category:return e
    return '📍'

def generic_desc(ar,en,cat,region):
    return f'الاسم الرسمي بالإنجليزية: {en}<br/>موقع سياحي في منطقة {region} ضمن فئة {cat}، ويستحق الإضافة إلى خريطة اسكتلندا السياحية لتميزه وقيمته للزائر. يُنصح بالتحقق من أوقات العمل أو شروط الزيارة عند الحاجة.<br/><br/>جميع الحقوق محفوظة للخرائط السياحية.'

# Resolve points.
resolved=[]; failed=[]; filtered=[]
seen_names=set()
for ar,en,cat,region in PLACES:
    if BANNED.search(en) or BANNED.search(ar):
        filtered.append((ar,en,'banned'))
        continue
    if norm(en) in existing_norm:
        filtered.append((ar,en,'known-existing'))
        continue
    if norm(en) in seen_names:
        filtered.append((ar,en,'duplicate-name'))
        continue
    seen_names.add(norm(en))
    g=geocode(en,region)
    if not g:
        failed.append((ar,en,cat,region))
        continue
    lat,lon,display,otype=g
    resolved.append({'ar':ar,'en':en,'cat':cat,'region':region,'lat':lat,'lon':lon,'display':display,'otype':otype})

# Coordinate near-duplicate safety inside this additions set: only remove if names are also strongly similar.
def hav(a,b):
    R=6371000
    p1=math.radians(a['lat']); p2=math.radians(b['lat']); dp=math.radians(b['lat']-a['lat']); dl=math.radians(b['lon']-a['lon'])
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(x))

def tokens(s): return set(re.findall(r'[a-z0-9]+',s.lower()))
final=[]
for p in resolved:
    dup=False
    for q in final:
        if hav(p,q)<80:
            a=tokens(p['en']); b=tokens(q['en']); sim=len(a&b)/max(1,len(a|b))
            if sim>=0.5:
                filtered.append((p['ar'],p['en'],'near-duplicate'))
                dup=True;break
    if not dup: final.append(p)

# Build KML with internal Tourist Maps icons extracted from Austria.kmz.
TMP='_scotland_add_build'; shutil.rmtree(TMP,ignore_errors=True); os.makedirs(TMP)
with zipfile.ZipFile('Austria.kmz') as z: z.extractall(os.path.join(TMP,'donor'))
# Find icon donor files by suffix path.
def donor_bytes(rel):
    bn=os.path.basename(rel)
    for root,dirs,files in os.walk(os.path.join(TMP,'donor')):
        if bn in files and root.replace('\\','/').endswith('/images'):
            with open(os.path.join(root,bn),'rb') as f:return f.read()
    raise FileNotFoundError(rel)

used_icons={choose_icon(p['cat']) for p in final}
os.makedirs(os.path.join(TMP,'out','icons'),exist_ok=True)
icon_local={}
for rel in used_icons:
    bn=os.path.basename(rel)
    outname=bn
    data=donor_bytes(rel)
    im=Image.open(io.BytesIO(data)).convert('RGBA').resize((30,30),Image.Resampling.LANCZOS)
    im.save(os.path.join(TMP,'out','icons',outname),'PNG')
    icon_local[rel]='icons/'+outname

K='http://www.opengis.net/kml/2.2'; ET.register_namespace('',K)
kml=ET.Element('{%s}kml'%K); doc=ET.SubElement(kml,'{%s}Document'%K); ET.SubElement(doc,'{%s}name'%K).text='إضافات خريطة اسكتلندا السياحية 2026'
# styles per donor icon
style_ids={}
for i,rel in enumerate(sorted(used_icons),1):
    sid=f's{i}'; style_ids[rel]=sid
    st=ET.SubElement(doc,'{%s}Style'%K,{'id':sid}); isty=ET.SubElement(st,'{%s}IconStyle'%K); ET.SubElement(isty,'{%s}scale'%K).text='1.0'; ic=ET.SubElement(isty,'{%s}Icon'%K); ET.SubElement(ic,'{%s}href'%K).text=icon_local[rel]
folder=ET.SubElement(doc,'{%s}Folder'%K); ET.SubElement(folder,'{%s}name'%K).text='إضافات اسكتلندا الجديدة'
for p in final:
    pm=ET.SubElement(folder,'{%s}Placemark'%K); ET.SubElement(pm,'{%s}name'%K).text=f"{p['ar']} – {p['cat']} {emoji(p['cat'])}"; ET.SubElement(pm,'{%s}styleUrl'%K).text='#'+style_ids[choose_icon(p['cat'])]
    ET.SubElement(pm,'{%s}description'%K).text=generic_desc(p['ar'],p['en'],p['cat'],p['region'])
    pt=ET.SubElement(pm,'{%s}Point'%K); ET.SubElement(pt,'{%s}coordinates'%K).text=f"{p['lon']:.7f},{p['lat']:.7f},0"

ET.ElementTree(kml).write(os.path.join(TMP,'out','doc.kml'),encoding='utf-8',xml_declaration=True)
OUT='scotland-additions-2026.kmz'
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(TMP,'out','doc.kml'),'doc.kml')
    for f in os.listdir(os.path.join(TMP,'out','icons')): z.write(os.path.join(TMP,'out','icons',f),'icons/'+f)

# Reports.
with open('scotland-additions-report.txt','w',encoding='utf-8') as f:
    f.write(f'المرشحون: {len(PLACES)}\n')
    f.write(f'تمت إضافتهم بعد الفلترة والتحقق: {len(final)}\n')
    f.write(f'تعذر تحديدهم تلقائيًا: {len(failed)}\n')
    f.write(f'مستبعدون/مكررون: {len(filtered)}\n\n')
    f.write('FAILED GEOCODE:\n')
    for x in failed:f.write(' | '.join(x)+'\n')
    f.write('\nFILTERED:\n')
    for x in filtered:f.write(' | '.join(x)+'\n')
    f.write('\nFINAL:\n')
    for p in final:f.write(f"{p['ar']} | {p['en']} | {p['cat']} | {p['lat']:.7f},{p['lon']:.7f} | {p['display']}\n")

with open('scotland-additions-resolved.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f); w.writerow(['Arabic','English','Category','Region','Latitude','Longitude','OSM display'])
    for p in final:w.writerow([p['ar'],p['en'],p['cat'],p['region'],p['lat'],p['lon'],p['display']])

print(json.dumps({'candidates':len(PLACES),'final':len(final),'failed':len(failed),'filtered':len(filtered)},ensure_ascii=False))
