from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict
from ..utils.date_utils import month_key


def basic_stats(items: List[dict]) -> Dict[str, Any]:
    """
    Calculates average, minimum and maximum price from list of price entries.
    """
    prices = [x["price"] for x in items]
    if not prices:
        return {"avg": None, "min": None, "max": None}

    return {
        "avg": sum(prices) / len(prices),
        "min": min(prices),
        "max": max(prices),
    }


def month_averages(items: List[dict]) -> Dict[str, float]:
    """
    Groups price entries by month (YYYY-MM),
    Returns monthly average values.
    """
    monthly_map = defaultdict(list)

    for record in items:
        monthly_map[month_key(record["date"])].append(record["price"])

    return {m: sum(v) / len(v) for m, v in monthly_map.items()}


def mom_change(monthly_map: Dict[str, float]) -> Dict[str, Any]:
    """
    Calculate MoM (Month-over-month) percentage change.
    Returns:
        current month avg
        previous month avg
        % change
    """
    if not monthly_map:
        return {"current_month": None, "previous_month": None, "pct_change": None}

    sorted_months = sorted(monthly_map.keys())

    # not enough data to compute MoM
    if len(sorted_months) < 2:
        last = sorted_months[-1]
        return {"current_month": {"month": last, "avg": monthly_map[last]},
                "previous_month": None,
                "pct_change": None}

    curr = sorted_months[-1]
    prev = sorted_months[-2]

    current_avg = monthly_map[curr]
    prev_avg = monthly_map[prev]

    pct = None if prev_avg == 0 else ((current_avg - prev_avg) / prev_avg) * 100

    return {
        "current_month": {"month": curr, "avg": current_avg},
        "previous_month": {"month": prev, "avg": prev_avg},
        "pct_change": pct
    }


def compare_periods(items: List[dict], startA: datetime, endA: datetime, startB: datetime, endB: datetime) -> Dict[str, Any]:
    """
    Compare Period A vs Period B.
    Calculates avg/min/max + difference + % difference.
    """

    def in_range(record, start, end):
        return start <= record["date"] <= end

    a = [r for r in items if in_range(r, startA, endA)]
    b = [r for r in items if in_range(r, startB, endB)]

    stats_a = basic_stats(a)
    stats_b = basic_stats(b)

    result = {
        "A": stats_a,
        "B": stats_b,
        "diff": None,
        "pct_diff": None,
    }

    if stats_a["avg"] is not None and stats_b["avg"] is not None:
        result["diff"] = stats_b["avg"] - stats_a["avg"]
        result["pct_diff"] = (result["diff"] / stats_a["avg"]) * 100 if stats_a["avg"] != 0 else None

    return result
