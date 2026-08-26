from __future__ import annotations

import gzip
import json
import time
from pathlib import Path
from typing import Any

import requests

OUT_DIR = Path('poland_build')
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUERIES = [
    ('Qubus Hotel Wrocław', 'Wrocław'),
    ('Tulip Hotels Wroclaw Centre', 'Wrocław'),
    ('Karczma Rzym', 'Wrocław'),
    ('Hotel SPA Dr Irena Eris Wzgórza Dylewskie', 'Wysoka Wieś'),
    ('Hotel Karolinka', 'Karpacz'),
    ('Gold Hotel', 'Złotoryja'),
    ('Hotel Książ', 'Wałbrzych'),
    ('Hotel Juvena Wellness SPA', 'Międzywodzie'),
    ('Holiday Inn Gdansk City Centre', 'Gdańsk'),
    ('Crowne Plaza Warsaw The HUB', 'Warsaw'),
    ('Hyatt Place Krakow', 'Kraków'),
    ('AC Hotel by Marriott Krakow', 'Kraków'),
    ('AC Hotel by Marriott Wroclaw', 'Wrocław'),
    ('voco Katowice', 'Katowice'),
    ('Radisson Blu Hotel Sopot', 'Sopot'),
    ('Radisson Blu Resort Swinoujscie', 'Świnoujście'),
    ('Radisson Blu Szczecin', 'Szczecin'),
    ('Radisson Resort Kołobrzeg', 'Kołobrzeg'),
    ('Radisson Hotel Szklarska Poręba', 'Szklarska Poręba'),
    ('Andersia Hotel Spa Poznan', 'Poznań'),
    ('Radisson Blu Sobieski', 'Warsaw'),
    ('NYX Hotel Warsaw', 'Warsaw'),
]


def first_value(address: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = address.get(key)
        if value:
            return str(value)
    return ''


def compact(result: dict[str, Any], requested_name: str, requested_city: str) -> dict[str, Any] | None:
    try:
        lat = float(result['lat'])
        lng = float(result['lon'])
    except (KeyError, TypeError, ValueError):
        return None
    if not (48.8 <= lat <= 55.1 and 13.7 <= lng <= 24.4):
        return None
    address = result.get('address') or {}
    namedetails = result.get('namedetails') or {}
    extratags = result.get('extratags') or {}
    display_first = str(result.get('display_name') or '').split(',')[0].strip()
    name = str(namedetails.get('name') or result.get('name') or display_first).strip()
    if not name:
        return None
    tags = {
        'name': name,
        'name:en': str(namedetails.get('name:en') or '').strip(),
        'official_name': str(namedetails.get('official_name') or '').strip(),
        'brand': str(extratags.get('brand') or '').strip(),
        'operator': str(extratags.get('operator') or '').strip(),
        'tourism': str(extratags.get('tourism') or result.get('type') or '').strip(),
        'stars': str(extratags.get('stars') or '').strip(),
        'addr:city': first_value(address, ('city', 'town', 'village', 'municipality')),
        'addr:place': first_value(address, ('suburb', 'neighbourhood', 'quarter', 'hamlet')),
        'addr:street': first_value(address, ('road', 'pedestrian', 'square')),
        'addr:housenumber': str(address.get('house_number') or '').strip(),
        'addr:postcode': str(address.get('postcode') or '').strip(),
        'website': str(extratags.get('website') or extratags.get('contact:website') or '').strip(),
    }
    tags = {k: v for k, v in tags.items() if v}
    osm_type = str(result.get('osm_type') or '').lower()
    return {
        'osm_type': osm_type,
        'osm_id': result.get('osm_id'),
        'lat': round(lat, 7),
        'lng': round(lng, 7),
        'tags': tags,
        'requested_name': requested_name,
        'requested_city': requested_city,
        'display_name': result.get('display_name'),
        'importance': result.get('importance'),
    }


def main() -> None:
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'TouristMaps-PolandHotelMapBuilder/2026 (contact: touristmaps.com.sa)',
        'Accept': 'application/json',
    })
    records: dict[str, dict[str, Any]] = {}
    report: list[str] = []
    endpoint = 'https://nominatim.openstreetmap.org/search'

    for number, (name, city) in enumerate(QUERIES, 1):
        params = {
            'q': f'{name}, {city}, Poland',
            'format': 'jsonv2',
            'addressdetails': 1,
            'namedetails': 1,
            'extratags': 1,
            'countrycodes': 'pl',
            'limit': 5,
        }
        results = None
        last_error = ''
        for attempt in range(1, 5):
            try:
                response = session.get(endpoint, params=params, timeout=60)
                if response.status_code == 200:
                    results = response.json()
                    break
                last_error = f'HTTP {response.status_code}: {response.text[:120]}'
            except Exception as exc:
                last_error = repr(exc)
            time.sleep(3 * attempt)
        if results is None:
            report.append(f'{number:02d} {name} | ERROR {last_error}')
            continue

        added = 0
        for raw in results:
            item = compact(raw, name, city)
            if item is None:
                continue
            key = f"{item['osm_type']}/{item['osm_id']}"
            if key not in records:
                records[key] = item
                added += 1
        line = f'{number:02d} {name}, {city} | results={len(results)} added={added}'
        print(line, flush=True)
        report.append(line)
        time.sleep(1.2)

    output = {
        'source': 'OpenStreetMap Nominatim targeted verification',
        'license': 'ODbL',
        'record_count': len(records),
        'records': list(records.values()),
    }
    raw = json.dumps(output, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    with gzip.open(OUT_DIR / 'poland_targeted_osm.json.gz', 'wb', compresslevel=9) as fh:
        fh.write(raw)
    report.extend([f'final_record_count={len(records)}', f'json_bytes={len(raw)}'])
    (OUT_DIR / 'poland_targeted_osm_report.txt').write_text('\n'.join(report), encoding='utf-8')
    print(f'Saved {len(records)} targeted OSM records', flush=True)


if __name__ == '__main__':
    main()
