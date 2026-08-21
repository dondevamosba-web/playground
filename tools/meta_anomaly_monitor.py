#!/usr/bin/env python3
"""
Meta Ads anomaly monitor.

Pulls yesterday's campaign performance vs the prior 7-day average.
Flags anomalies and creates a 3-bullet Gmail draft summary.

Anomaly thresholds:
  CPA spike    > 30% above baseline
  ROAS drop    > 20% below baseline
  Spend over   > 25% above daily baseline
  Spend under  > 25% below daily baseline  (only if yesterday spend > $20)

Requires in .env:
  META_ACCESS_TOKEN    — long-lived user or system user token (ads_read scope)
  META_AD_ACCOUNT_ID   — one or more account IDs, comma-separated (e.g. act_123,act_456)

Get your token at: https://developers.facebook.com/tools/explorer
  → Add permission: ads_read → Generate token → extend via /oauth/access_token

Usage:
  python3 tools/meta_anomaly_monitor.py              # check + create draft
  python3 tools/meta_anomaly_monitor.py --dry-run    # print only, no draft
  python3 tools/meta_anomaly_monitor.py --days 14    # change baseline window (default 7)
"""
import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.claude_call import call_claude
from tools.gmail_draft import create_draft, build_html_body

GRAPH_URL = "https://graph.facebook.com/v19.0"
MIN_SPEND = 20.0       # ignore campaigns spending < $20/day
CPA_SPIKE_PCT = 0.30
ROAS_DROP_PCT  = 0.20
SPEND_DEV_PCT  = 0.25

CONVERSION_ACTIONS = [
    "purchase",
    "offsite_conversion.fb_pixel_purchase",
    "lead",
    "offsite_conversion.fb_pixel_lead",
    "complete_registration",
]


# ── API helpers ───────────────────────────────────────────────────────────────

def get_insights(account_id: str, token: str, date_start: str, date_end: str) -> list:
    """Pull campaign-level daily insights for a date range."""
    fields = "campaign_name,spend,impressions,clicks,actions,action_values"
    params = {
        "level": "campaign",
        "fields": fields,
        "time_increment": 1,
        "date_start": date_start,
        "date_end": date_end,
        "access_token": token,
        "limit": 200,
    }
    rows = []
    url = f"{GRAPH_URL}/{account_id}/insights"
    while url:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            err = resp.json().get("error", {})
            print(f"  API error ({account_id}): {err.get('message', resp.text)}")
            return []
        data = resp.json()
        rows.extend(data.get("data", []))
        paging = data.get("paging", {})
        url = paging.get("next")
        params = {}  # next URL already has params baked in
    return rows


def extract_conversions(row: dict) -> float:
    actions = {a["action_type"]: float(a["value"]) for a in row.get("actions") or []}
    for key in CONVERSION_ACTIONS:
        if key in actions:
            return actions[key]
    return 0.0


def extract_revenue(row: dict) -> float:
    values = {a["action_type"]: float(a["value"]) for a in row.get("action_values") or []}
    for key in CONVERSION_ACTIONS:
        if key in values:
            return values[key]
    return 0.0


# ── Metric aggregation ────────────────────────────────────────────────────────

def aggregate(rows: list) -> dict:
    """Sum a list of daily rows into campaign-level totals. Returns {campaign_name: metrics}."""
    campaigns = {}
    for row in rows:
        name = row.get("campaign_name", "Unknown")
        spend = float(row.get("spend", 0))
        conversions = extract_conversions(row)
        revenue = extract_revenue(row)
        if name not in campaigns:
            campaigns[name] = {"spend": 0, "conversions": 0, "revenue": 0, "days": 0}
        campaigns[name]["spend"] += spend
        campaigns[name]["conversions"] += conversions
        campaigns[name]["revenue"] += revenue
        campaigns[name]["days"] += 1
    return campaigns


def derived(metrics: dict, days: int = 1) -> dict:
    spend = metrics["spend"]
    conv = metrics["conversions"]
    rev = metrics["revenue"]
    return {
        "spend": spend,
        "daily_spend": spend / days if days else spend,
        "cpa": spend / conv if conv else None,
        "roas": rev / spend if spend else None,
        "conversions": conv,
    }


# ── Anomaly detection ─────────────────────────────────────────────────────────

def detect_anomalies(account_id: str, yesterday_rows: list, baseline_rows: list, baseline_days: int) -> list:
    yesterday = aggregate(yesterday_rows)
    baseline = aggregate(baseline_rows)
    flags = []

    for campaign, yd in yesterday.items():
        y = derived(yd)
        if y["spend"] < MIN_SPEND:
            continue

        bl = baseline.get(campaign)
        if not bl or bl["spend"] == 0:
            flags.append({"account": account_id, "campaign": campaign, "flag": "new_spend",
                          "detail": f"${y['spend']:.0f} spend (no prior baseline)"})
            continue

        b = derived(bl, days=baseline_days)

        # CPA spike
        if y["cpa"] and b["cpa"] and y["cpa"] > b["cpa"] * (1 + CPA_SPIKE_PCT):
            pct = (y["cpa"] / b["cpa"] - 1) * 100
            flags.append({"account": account_id, "campaign": campaign, "flag": "cpa_spike",
                          "detail": f"CPA ${y['cpa']:.2f} vs baseline ${b['cpa']:.2f} (+{pct:.0f}%)"})

        # ROAS drop
        if y["roas"] is not None and b["roas"] and y["roas"] < b["roas"] * (1 - ROAS_DROP_PCT):
            pct = (1 - y["roas"] / b["roas"]) * 100
            flags.append({"account": account_id, "campaign": campaign, "flag": "roas_drop",
                          "detail": f"ROAS {y['roas']:.2f}x vs baseline {b['roas']:.2f}x (-{pct:.0f}%)"})

        # Spend deviation
        if b["daily_spend"] > 0:
            spend_delta = (y["spend"] - b["daily_spend"]) / b["daily_spend"]
            if spend_delta > SPEND_DEV_PCT:
                flags.append({"account": account_id, "campaign": campaign, "flag": "overspend",
                              "detail": f"${y['spend']:.0f} vs avg ${b['daily_spend']:.0f}/day (+{spend_delta*100:.0f}%)"})
            elif spend_delta < -SPEND_DEV_PCT:
                flags.append({"account": account_id, "campaign": campaign, "flag": "underspend",
                              "detail": f"${y['spend']:.0f} vs avg ${b['daily_spend']:.0f}/day ({spend_delta*100:.0f}%)"})

    return flags


# ── Summary generation ────────────────────────────────────────────────────────

def build_summary(flags: list, yesterday: str) -> str:
    if not flags:
        return f"No anomalies detected for {yesterday}. All campaigns within normal range."

    flag_lines = "\n".join(f"- [{f['flag'].upper()}] {f['campaign']}: {f['detail']}" for f in flags)
    prompt = (
        f"You are a performance marketing analyst. Here are Meta Ads anomalies detected for {yesterday}:\n\n"
        f"{flag_lines}\n\n"
        "Write a concise 3-bullet executive summary for the account manager. Each bullet covers one key issue, "
        "the metric, and a one-line recommended action. Be direct — no fluff, no intro sentence."
    )
    # sonnet: interpreting anomalies + recommending actions requires judgment, not just formatting
    return call_claude(prompt, model="sonnet")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--days", type=int, default=7, help="Baseline window in days (default: 7)")
    args = parser.parse_args()

    token = os.getenv("META_ACCESS_TOKEN")
    account_ids_raw = os.getenv("META_AD_ACCOUNT_ID", "")

    if not token or not account_ids_raw:
        print("Missing credentials. Add to .env:")
        print("  META_ACCESS_TOKEN=<your token>")
        print("  META_AD_ACCOUNT_ID=act_XXXXXXXXX   (comma-separated for multiple accounts)")
        print("\nGet a token at: https://developers.facebook.com/tools/explorer")
        print("Required permission: ads_read")
        sys.exit(1)

    account_ids = [a.strip() for a in account_ids_raw.split(",") if a.strip()]
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    baseline_end = (date.today() - timedelta(days=2)).isoformat()
    baseline_start = (date.today() - timedelta(days=1 + args.days)).isoformat()

    print(f"Checking {len(account_ids)} account(s) — yesterday: {yesterday}, baseline: {baseline_start} → {baseline_end}")

    all_flags = []

    for account_id in account_ids:
        print(f"\n  {account_id}")
        yd_rows = get_insights(account_id, token, yesterday, yesterday)
        bl_rows = get_insights(account_id, token, baseline_start, baseline_end)
        flags = detect_anomalies(account_id, yd_rows, bl_rows, args.days)
        if flags:
            print(f"    {len(flags)} anomaly(ies) detected")
            for f in flags:
                print(f"    [{f['flag'].upper()}] {f['campaign']}: {f['detail']}")
        else:
            print(f"    All clear")
        all_flags.extend(flags)

    print(f"\n{'='*50}")
    print(f"Total anomalies: {len(all_flags)}")

    summary = build_summary(all_flags, yesterday)
    print(f"\nSummary:\n{summary}")

    if not args.dry_run:
        subject = f"Meta Ads Alert — {yesterday} ({len(all_flags)} flag(s))"
        html = build_html_body(summary)
        result = create_draft(to="dondevamosba@gmail.com", subject=subject, body=html, html=True)
        print(f"\nGmail draft created: {result['draft_id']}")
    else:
        print("\n[dry-run] No draft created.")


if __name__ == "__main__":
    main()
