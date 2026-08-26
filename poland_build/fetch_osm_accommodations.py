from __future__ import annotations

import gzip
import json
import time
from pathlib import Path
from typing import Any

import requests

OUT_DIR = Path("poland_build")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

# Poland split into 12 moderate bounding boxes. Only the accommodation types
# represented in the official CWOH selection are fetched, keeping responses small.
LAT_EDGES = [49.0, 51.0, 53.0, 55.0]
LON_EDGES = [14.0, 16.75, 19.5, 22.25, 25.0]
TOURISM_RE = "^(hotel|motel|guest_house)$"


def query_bbox(south: float, west: float, north: float, east: float) -> str:
    return f"""[out:json][timeout:240];
(
  nwr[\"tourism\"~\"{TOURISM_RE}\"][\"name\"]({south},{west},{north},{east});
);
out center tags qt;"""


def compact_element(el: dict[str, Any]) -> dict[str, Any] | None:
    tags = el.get("tags") or {}
    name = tags.get("name")
    if not name:
        return None
    if el.get("type") == "node":
        lat, lon = el.get("lat"), el.get("lon")
    else:
        center = el.get("center") or {}
        lat, lon = center.get("lat"), center.get("lon")
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return None
    keep_keys = (
        "name", "name:en", "alt_name", "official_name", "brand", "operator",
        "tourism", "stars", "addr:city", "addr:place", "addr:street",
        "addr:housenumber", "addr:postcode", "website", "contact:website",
    )
    return {
        "osm_type": el.get("type"),
        "osm_id": el.get("id"),
        "lat": round(float(lat), 7),
        "lng": round(float(lon), 7),
        "tags": {k: tags[k] for k in keep_keys if tags.get(k) not in (None, "")},
    }


def main() -> None:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "TouristMaps-PolandHotelMapBuilder/2026 (one-time cached data enrichment)",
        "Accept": "application/json",
    })
    records: dict[str, dict[str, Any]] = {}
    report: list[str] = []
    failed_cells: list[str] = []
    cell = 0
    total_cells = (len(LAT_EDGES) - 1) * (len(LON_EDGES) - 1)

    for i in range(len(LAT_EDGES) - 1):
        for j in range(len(LON_EDGES) - 1):
            cell += 1
            south, north = LAT_EDGES[i], LAT_EDGES[i + 1]
            west, east = LON_EDGES[j], LON_EDGES[j + 1]
            q = query_bbox(south, west, north, east)
            payload = None
            last_error = ""
            for attempt in range(1, 10):
                endpoint = ENDPOINTS[(cell + attempt) % len(ENDPOINTS)]
                try:
                    response = session.post(endpoint, data={"data": q}, timeout=330)
                    if response.status_code == 200:
                        payload = response.json()
                        break
                    last_error = f"HTTP {response.status_code}: {response.text[:160]}"
                except Exception as exc:
                    last_error = repr(exc)
                time.sleep(min(4 * attempt, 24))
            if payload is None:
                failed = f"cell={cell}/{total_cells} bbox={south},{west},{north},{east} failed={last_error}"
                print(failed, flush=True)
                report.append(failed)
                failed_cells.append(failed)
                continue

            elements = payload.get("elements") or []
            added = 0
            for el in elements:
                item = compact_element(el)
                if item is None:
                    continue
                key = f"{item['osm_type']}/{item['osm_id']}"
                if key not in records:
                    records[key] = item
                    added += 1
            line = (
                f"cell={cell}/{total_cells} bbox={south},{west},{north},{east} "
                f"received={len(elements)} added={added} total={len(records)}"
            )
            print(line, flush=True)
            report.append(line)
            time.sleep(2)

    if not records:
        raise RuntimeError("No OSM records were fetched")

    output = {
        "source": "OpenStreetMap via Overpass API",
        "license": "ODbL",
        "record_count": len(records),
        "failed_cell_count": len(failed_cells),
        "records": list(records.values()),
    }
    raw = json.dumps(output, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.open(OUT_DIR / "poland_osm_accommodations.json.gz", "wb", compresslevel=9) as fh:
        fh.write(raw)
    report.extend([
        f"final_record_count={len(records)}",
        f"failed_cell_count={len(failed_cells)}",
        f"json_bytes={len(raw)}",
    ])
    (OUT_DIR / "poland_osm_report.txt").write_text("\n".join(report), encoding="utf-8")
    print(f"Saved {len(records)} OSM accommodation records; failed cells={len(failed_cells)}", flush=True)


if __name__ == "__main__":
    main()
