#!/usr/bin/env python3
"""Transform venue CSV into gift-adjustment data-schema API payload."""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from csv_to_json import parse_adjustment_date, parse_sales_rank_cell

RANK_COLUMN_START = 13
RANK_COLUMN_END = 64  # columns 1-51 (0-based indices 13-63)


def compact(data: Dict[str, Any]) -> Dict[str, Any]:
    """Drop keys whose values are None."""
    return {key: value for key, value in data.items() if value is not None}


def infer_layout_type(venue_name: str) -> Optional[str]:
    if "_" not in venue_name:
        return None
    suffix = venue_name.rsplit("_", 1)[-1]
    if suffix in {"双", "2双", "混2双", "1双"}:
        return "背靠背"
    if suffix == "混双":
        return "L型"
    if suffix in {"四", "混四"}:
        return "分开两组"
    return None


def infer_project_type(project_type: str) -> Optional[str]:
    if not project_type:
        return None
    if project_type.startswith("全国"):
        return "全国项目"
    return "非全国项目"


def infer_withdrawal_risk(venue_status: str) -> Optional[bool]:
    if not venue_status:
        return None
    return venue_status in {"计划撤场", "续签处理中", "已撤场"}


def infer_slot_layer(machine_slot: str) -> Optional[str]:
    if "双上" in machine_slot:
        return "上层"
    if "双下" in machine_slot:
        return "下层"
    match = re.search(r"01-(\d+)", machine_slot)
    if match:
        return "上层" if int(match.group(1)) % 2 == 1 else "下层"
    if machine_slot.endswith("上"):
        return "上层"
    if machine_slot.endswith("下"):
        return "下层"
    return None


def canonical_gift_id(gift_name: str, gift_id: str) -> str:
    return f"{gift_name}_{gift_id}"


def parse_price_coins(gift_id: str) -> Optional[int]:
    try:
        return int(round(float(gift_id)))
    except ValueError:
        return None


def infer_slot_index(machine_slot: str) -> Optional[int]:
    match = re.search(r"01-(\d+)", machine_slot)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d+)号机", machine_slot)
    if match:
        return int(match.group(1))
    return None


def load_venue_rows(input_path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader)
        for row in reader:
            venue_id = re.sub(r"\.0$", "", row[2].strip())
            slots: List[Dict[str, Any]] = []
            for col_idx in range(RANK_COLUMN_START, RANK_COLUMN_END):
                if col_idx >= len(row):
                    break
                parsed = parse_sales_rank_cell(row[col_idx])
                if parsed:
                    bottom_rank = col_idx - RANK_COLUMN_START + 1
                    parsed["bottom_rank"] = bottom_rank
                    slots.append(parsed)

            records.append(
                {
                    "venue_id": venue_id,
                    "venue_name": row[0].strip(),
                    "location": row[1].strip() or None,
                    "days_since_last": int(row[8]) if row[8].strip().isdigit() else None,
                    "update_notes": row[9].strip() or None,
                    "project_type_raw": row[10].strip() or None,
                    "venue_status": row[11].strip() or None,
                    "last_adjustment_date": parse_adjustment_date(row[12]),
                    "slots": slots,
                }
            )
    return records


def build_schema_payload(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    venues: List[Dict[str, Any]] = []
    venue_sales: List[Dict[str, Any]] = []
    venue_gifts: List[Dict[str, Any]] = []
    adjustment_log: List[Dict[str, Any]] = []
    problem_venues: List[Dict[str, Any]] = []

    gift_catalog_map: Dict[str, Dict[str, Any]] = {}
    gift_venue_ranks: Dict[str, List[int]] = defaultdict(list)
    gift_total_sales: Dict[str, int] = defaultdict(int)

    for record in records:
        venue_id = record["venue_id"]
        slot_count = len(record["slots"])

        venues.append(
            compact(
                {
                    "venue_id": venue_id,
                    "venue_name": record["venue_name"],
                    "location": record["location"],
                    "project_type": infer_project_type(record["project_type_raw"] or ""),
                    "slot_count": slot_count,
                    "layout_type": infer_layout_type(record["venue_name"]),
                    "withdrawal_risk": infer_withdrawal_risk(record["venue_status"] or ""),
                }
            )
        )

        adjustment_log.append(
            compact(
                {
                    "venue_id": venue_id,
                    "adjustment_date": record["last_adjustment_date"],
                    "days_since_last": record["days_since_last"],
                }
            )
        )

        if record["venue_status"] == "异常挂起":
            problem_venues.append(
                compact(
                    {
                        "venue_id": venue_id,
                        "reason": record["update_notes"],
                    }
                )
            )

        for slot in record["slots"]:
            gift_name = slot["gift_name"]
            gift_price = slot["gift_id"]
            if not gift_name or not gift_price or gift_name == "null" or gift_price == "null":
                continue

            price_coins = parse_price_coins(gift_price)
            if price_coins is None:
                continue

            gift_key = canonical_gift_id(gift_name, gift_price)
            rank_in_venue = slot_count - slot["bottom_rank"] + 1
            rank_percentile = (
                (rank_in_venue - 1) / (slot_count - 1) if slot_count > 1 else 0.0
            )
            coin_count = int(slot["coin_count"]) if slot["coin_count"] == int(slot["coin_count"]) else slot["coin_count"]
            slot_layer = infer_slot_layer(slot["machine_slot"])

            venue_sales.append(
                compact(
                    {
                        "venue_id": venue_id,
                        "gift_id": gift_key,
                        "slot_layer": slot_layer,
                        "period_days": 90,
                        "coin_count": coin_count,
                        "rank_in_venue": rank_in_venue,
                        "rank_percentile": round(rank_percentile, 4),
                    }
                )
            )

            venue_gifts.append(
                compact(
                    {
                        "venue_id": venue_id,
                        "gift_id": gift_key,
                        "gift_name": gift_name,
                        "slot_layer": slot_layer,
                        "slot_index": infer_slot_index(slot["machine_slot"]),
                        "price_coins": price_coins,
                    }
                )
            )

            if gift_key not in gift_catalog_map:
                gift_catalog_map[gift_key] = compact(
                    {
                        "gift_id": gift_key,
                        "gift_name": gift_name,
                        "price_standard": price_coins,
                    }
                )

            gift_venue_ranks[gift_key].append(rank_in_venue)
            gift_total_sales[gift_key] += int(coin_count)

    ranked_gifts = sorted(
        gift_total_sales.items(),
        key=lambda item: (-item[1], item[0]),
    )
    national_ranking: List[Dict[str, Any]] = []
    for national_rank, (gift_key, _) in enumerate(ranked_gifts, start=1):
        ranks = gift_venue_ranks[gift_key]
        top2_count = sum(1 for rank in ranks if rank <= 2)
        national_ranking.append(
            {
                "gift_id": gift_key,
                "period_days": 90,
                "national_rank": national_rank,
                "top2_ratio": round(top2_count / len(ranks), 4),
                "total_venues": len(ranks),
            }
        )

    return {
        "skill": "gift-adjustment",
        "triggered_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": {
            "venues": venues,
            "venue_sales": venue_sales,
            "venue_gifts": venue_gifts,
            "adjustment_log": adjustment_log,
            "problem_venues": problem_venues,
            "gift_catalog": list(gift_catalog_map.values()),
            "national_ranking": national_ranking,
        },
        "_meta": {
            "source": "ref/东部中部南部东南华东-表格 1.csv",
            "omitted_fields_without_source": [
                "venues.price_level",
                "venues.semi_annual_profit_per_machine",
                "venue_sales.coin_count_30d",
                "venue_sales.coin_count_60d",
                "venue_gifts.inventory",
                "venue_gifts.is_tail_stock",
                "venue_gifts.audience_type",
                "gift_catalog.profit_tier",
                "gift_catalog.audience_type",
                "gift_catalog.is_tail_stock",
                "gift_catalog.is_available",
                "gift_catalog.price_min",
                "gift_catalog.category",
                "problem_venues.added_date",
            ],
            "derived_fields": {
                "project_type": "由所属项目列映射：全国* -> 全国项目，其余有值 -> 非全国项目",
                "layout_type": "由场地名后缀映射，无法映射时省略",
                "slot_layer": "由 machine_slot 推断，无法推断时省略",
                "rank_in_venue": "由销售额倒数列位反推",
                "rank_percentile": "由 rank_in_venue 计算",
                "national_ranking": "由场地销售数据聚合计算",
            },
            "record_counts": {
                "venues": len(venues),
                "venue_sales": len(venue_sales),
                "venue_gifts": len(venue_gifts),
                "adjustment_log": len(adjustment_log),
                "problem_venues": len(problem_venues),
                "gift_catalog": len(gift_catalog_map),
                "national_ranking": len(national_ranking),
            },
        },
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    input_path = repo_root / "ref" / "东部中部南部东南华东-表格 1.csv"
    output_path = repo_root / "ref" / "东部中部南部东南华东-gift-adjustment-data.json"

    if len(sys.argv) >= 2:
        input_path = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])

    records = load_venue_rows(input_path)
    payload = build_schema_payload(records)

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    counts = payload["_meta"]["record_counts"]
    print(f"Wrote schema payload -> {output_path}")
    for key, value in counts.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
