from __future__ import annotations

import gzip
import json
import time
from pathlib import Path
from typing import Any

import requests

BASE_URL = "https://api.turystyka.gov.pl/registers/open/cwoh"
OUT_DIR = Path("poland_build")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_page(payload: Any) -> tuple[list[dict[str, Any]], bool, int | None]:
    """Return records, is_last, total_pages for common Spring Page response shapes."""
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)], True, 1
    if not isinstance(payload, dict):
        raise RuntimeError(f"Unexpected API payload type: {type(payload)!r}")

    records = payload.get("content")
    if not isinstance(records, list):
        for key in ("items", "results", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                records = value
                break
    if not isinstance(records, list):
        raise RuntimeError(f"Could not locate records in response keys: {sorted(payload.keys())}")

    total_pages = payload.get("totalPages")
    if not isinstance(total_pages, int):
        total_pages = payload.get("total_pages") if isinstance(payload.get("total_pages"), int) else None

    is_last = bool(payload.get("last", False))
    if total_pages is not None:
        number = payload.get("number", 0)
        if isinstance(number, int):
            is_last = number + 1 >= total_pages
    elif len(records) == 0:
        is_last = True

    return [x for x in records if isinstance(x, dict)], is_last, total_pages


def fetch_all() -> tuple[list[dict[str, Any]], list[str]]:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "User-Agent": "TouristMaps-PolandHotelMapBuilder/2026",
        }
    )

    report: list[str] = []
    all_records: list[dict[str, Any]] = []
    seen_uids: set[str] = set()
    page = 0
    size = 500
    max_pages = 1000

    while page < max_pages:
        params = {"page": page, "size": size, "processed": "true"}
        response = None
        for attempt in range(1, 6):
            try:
                response = session.get(BASE_URL, params=params, timeout=90)
                if response.status_code == 200:
                    break
                report.append(f"page={page} attempt={attempt} status={response.status_code}")
            except requests.RequestException as exc:
                report.append(f"page={page} attempt={attempt} error={exc}")
            time.sleep(min(2**attempt, 20))

        if response is None or response.status_code != 200:
            raise RuntimeError(f"Failed to fetch CWOH page {page}")

        payload = response.json()
        records, is_last, total_pages = extract_page(payload)
        added = 0
        for record in records:
            uid = str(record.get("uid") or record.get("id") or "")
            key = uid or json.dumps(record, ensure_ascii=False, sort_keys=True)
            if key in seen_uids:
                continue
            seen_uids.add(key)
            all_records.append(record)
            added += 1

        report.append(
            f"page={page} received={len(records)} added={added} total={len(all_records)} "
            f"total_pages={total_pages} last={is_last}"
        )
        print(report[-1], flush=True)

        if is_last or not records:
            break
        page += 1
    else:
        raise RuntimeError("Safety page limit reached")

    return all_records, report


def main() -> None:
    records, report = fetch_all()
    payload = {
        "source": BASE_URL,
        "retrieved_for": "Tourist Maps Poland hotel map",
        "record_count": len(records),
        "records": records,
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.open(OUT_DIR / "cwoh.json.gz", "wb", compresslevel=9) as fh:
        fh.write(raw)
    (OUT_DIR / "cwoh_report.txt").write_text(
        "\n".join(report + [f"final_record_count={len(records)}", f"json_bytes={len(raw)}"]),
        encoding="utf-8",
    )
    print(f"Saved {len(records)} records", flush=True)


if __name__ == "__main__":
    main()
