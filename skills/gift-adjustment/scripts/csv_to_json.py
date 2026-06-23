#!/usr/bin/env python3
"""Convert venue CSV export to JSON aligned with gift-adjustment data-schema."""

import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def parse_adjustment_date(value: str) -> Optional[str]:
    """Parse Y/m/d dates like 2024/4/19."""
    value = value.strip()
    if not value:
        return None

    parts = value.split("/")
    if len(parts) == 3 and parts[0].isdigit() and len(parts[0]) == 4:
        year, month, day = (int(p) for p in parts)
        return f"{year:04d}-{month:02d}-{day:02d}"
    return value


def parse_launch_date(value: str) -> Optional[str]:
    """Parse YY/m/d dates like 23/11/30 -> 2023-11-30."""
    value = value.strip()
    if not value:
        return None

    parts = value.split("/")
    if len(parts) != 3:
        return value

    year_raw, month_raw, day_raw = parts
    if not (year_raw.isdigit() and month_raw.isdigit() and day_raw.isdigit()):
        return value

    year = int(year_raw)
    month = int(month_raw)
    day = int(day_raw)

    if len(year_raw) == 2:
        year += 2000
    elif len(year_raw) != 4:
        return value

    return f"{year:04d}-{month:02d}-{day:02d}"


def parse_gift_ref(raw: str) -> Dict[str, Optional[str]]:
    """Split e.g. 木鱼三代_16 into gift_name and gift_id (suffix after _)."""
    raw = raw.strip()
    if not raw or "_" not in raw:
        return {"gift_name": raw or None, "gift_id": None}

    gift_name, gift_id = raw.rsplit("_", 1)
    return {
        "gift_name": gift_name or None,
        "gift_id": gift_id or None,
    }


def parse_sales_rank_cell(cell: str) -> Optional[Dict[str, Any]]:
    """Parse multiline rank cell: machine_slot, gift ref, launch_date, coin_count."""
    cell = cell.strip()
    if not cell:
        return None

    lines = [line.strip() for line in cell.splitlines() if line.strip()]
    if len(lines) < 4:
        return None

    machine_slot, gift_raw, launch_date_raw, coin_count_raw = lines[:4]
    gift = parse_gift_ref(gift_raw)

    coin_count: Union[int, float]
    try:
        coin_count = int(coin_count_raw)
    except ValueError:
        coin_count = float(coin_count_raw)

    return {
        "machine_slot": machine_slot,
        "gift_name": gift["gift_name"],
        "gift_id": gift["gift_id"],
        "launch_date": parse_launch_date(launch_date_raw),
        "coin_count": coin_count,
    }


def convert_row(row: List[str]) -> Dict[str, Any]:
    venue_id = row[2].strip()
    if venue_id:
        venue_id = re.sub(r"\.0$", "", venue_id)

    record: Dict[str, Any] = {
        "venue_name": row[0].strip(),
        "location": row[1].strip(),
        "venue_id": venue_id,
        "days_since_last": int(row[8]) if row[8].strip().isdigit() else row[8].strip() or None,
        "update_notes": row[9].strip() or None,
        "project_type": row[10].strip(),
        "venue_status": row[11].strip(),
        "last_adjustment_date": parse_adjustment_date(row[12]),
    }

    for rank in range(1, 12):
        col_idx = 12 + rank
        cell = row[col_idx] if col_idx < len(row) else ""
        parsed = parse_sales_rank_cell(cell)
        record[f"bottom_sales_rank_{rank}"] = parsed

    return record


def convert_csv(input_path: Path, output_path: Path) -> int:
    with input_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        records = [convert_row(row) for row in reader]

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return len(records)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    input_path = repo_root / "ref" / "东部中部南部东南华东-表格 1.csv"
    output_path = repo_root / "ref" / "东部中部南部东南华东-venues.json"

    if len(sys.argv) >= 2:
        input_path = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])

    count = convert_csv(input_path, output_path)
    print(f"Converted {count} records -> {output_path}")


if __name__ == "__main__":
    main()
