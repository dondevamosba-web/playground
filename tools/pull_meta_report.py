"""
Pulls campaign performance data from Meta Ads API.

Requires in .env:
  META_ACCESS_TOKEN   — long-lived system user token or user token
  META_AD_ACCOUNT_ID  — format: act_XXXXXXXXXX

How to get a token:
  1. Go to business.facebook.com → Settings → System Users → Create system user
  2. Assign the system user Admin access to your Ad Account
  3. Generate a token with ads_read, ads_management permissions
  4. Paste the token and account ID into .env

Usage:
  python3 tools/pull_meta_report.py                    # last 7 days
  python3 tools/pull_meta_report.py --days 30          # last 30 days
  python3 tools/pull_meta_report.py --days 7 --out .tmp/meta_report.json
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import date, timedelta

from dotenv import load_dotenv
load_dotenv()

ACCESS_TOKEN  = os.getenv("META_ACCESS_TOKEN", "")
AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID", "")
API_VERSION   = "v21.0"
BASE_URL      = f"https://graph.facebook.com/{API_VERSION}"

TMP_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp")


def api_get(path: str, params: dict) -> dict:
    params["access_token"] = ACCESS_TOKEN
    url = f"{BASE_URL}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "storm-digital-reporter/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"API error {e.code}: {body}")
        sys.exit(1)


def date_range(days: int) -> tuple[str, str]:
    end   = date.today() - timedelta(days=1)   # yesterday (data is complete)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def fetch_campaigns(since: str, until: str) -> list[dict]:
    fields = (
        "campaign_name,spend,impressions,clicks,ctr,"
        "cpc,cpm,actions,cost_per_action_type"
    )
    params = {
        "fields": fields,
        "time_range": json.dumps({"since": since, "until": until}),
        "level": "campaign",
        "limit": 200,
    }
    data = api_get(f"/{AD_ACCOUNT_ID}/insights", params)
    return data.get("data", [])


def fetch_account_summary(since: str, until: str) -> dict:
    params = {
        "fields": "spend,impressions,clicks,ctr,cpc,cpm,actions,cost_per_action_type",
        "time_range": json.dumps({"since": since, "until": until}),
        "level": "account",
    }
    data = api_get(f"/{AD_ACCOUNT_ID}/insights", params)
    rows = data.get("data", [])
    return rows[0] if rows else {}


def extract_leads(row: dict) -> int:
    actions = row.get("actions", [])
    for a in actions:
        if a.get("action_type") in ("lead", "offsite_conversion.fb_pixel_lead",
                                     "onsite_conversion.lead_grouped"):
            return int(float(a.get("value", 0)))
    return 0


def extract_cpl(row: dict) -> float | None:
    cpa = row.get("cost_per_action_type", [])
    for a in cpa:
        if a.get("action_type") in ("lead", "offsite_conversion.fb_pixel_lead",
                                     "onsite_conversion.lead_grouped"):
            return round(float(a.get("value", 0)), 2)
    return None


def build_report(days: int) -> dict:
    since, until = date_range(days)
    # Also pull prior period for comparison
    prior_until_dt = date.fromisoformat(since) - timedelta(days=1)
    prior_since_dt = prior_until_dt - timedelta(days=days - 1)
    prior_since = prior_since_dt.isoformat()
    prior_until = prior_until_dt.isoformat()

    print(f"Fetching period: {since} → {until}")
    summary  = fetch_account_summary(since, until)
    campaigns = fetch_campaigns(since, until)

    print(f"Fetching prior period: {prior_since} → {prior_until}")
    prior_summary = fetch_account_summary(prior_since, prior_until)

    # Parse campaigns
    parsed_campaigns = []
    for c in campaigns:
        leads = extract_leads(c)
        cpl = extract_cpl(c)
        parsed_campaigns.append({
            "name":        c.get("campaign_name", "—"),
            "spend":       round(float(c.get("spend", 0)), 2),
            "impressions": int(c.get("impressions", 0)),
            "clicks":      int(c.get("clicks", 0)),
            "ctr":         round(float(c.get("ctr", 0)), 2),
            "cpc":         round(float(c.get("cpc", 0)), 2),
            "cpm":         round(float(c.get("cpm", 0)), 2),
            "leads":       leads,
            "cpl":         cpl,
        })

    # Sort by spend desc
    parsed_campaigns.sort(key=lambda x: x["spend"], reverse=True)

    def safe_float(v): return round(float(v), 2) if v else 0.0

    report = {
        "period": {"since": since, "until": until, "days": days},
        "prior_period": {"since": prior_since, "until": prior_until},
        "account_id": AD_ACCOUNT_ID,
        "generated": date.today().isoformat(),
        "summary": {
            "spend":       safe_float(summary.get("spend")),
            "impressions": int(summary.get("impressions", 0)),
            "clicks":      int(summary.get("clicks", 0)),
            "ctr":         safe_float(summary.get("ctr")),
            "cpc":         safe_float(summary.get("cpc")),
            "cpm":         safe_float(summary.get("cpm")),
            "leads":       extract_leads(summary),
            "cpl":         extract_cpl(summary),
        },
        "prior_summary": {
            "spend":       safe_float(prior_summary.get("spend")),
            "leads":       extract_leads(prior_summary),
            "cpl":         extract_cpl(prior_summary),
        },
        "campaigns": parsed_campaigns,
    }

    return report


def main():
    if not ACCESS_TOKEN or not AD_ACCOUNT_ID:
        print(
            "Missing credentials. Add to .env:\n"
            "  META_ACCESS_TOKEN=your_token\n"
            "  META_AD_ACCOUNT_ID=act_XXXXXXXXXX\n\n"
            "See tool docstring for how to generate a token."
        )
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    report = build_report(args.days)

    os.makedirs(TMP_DIR, exist_ok=True)
    out = args.out or os.path.join(TMP_DIR, f"meta_report_{report['period']['since']}.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)

    s = report["summary"]
    p = report["prior_summary"]
    print(f"\n── Summary ({report['period']['since']} → {report['period']['until']}) ──")
    print(f"  Spend:       ${s['spend']:,.2f}  (prior: ${p['spend']:,.2f})")
    print(f"  Leads:       {s['leads']}        (prior: {p['leads']})")
    print(f"  CPL:         ${s['cpl']:,.2f}" if s["cpl"] else "  CPL:         —")
    print(f"  CTR:         {s['ctr']}%")
    print(f"  CPM:         ${s['cpm']:,.2f}")
    print(f"\n  Campaigns:   {len(report['campaigns'])}")
    print(f"\nSaved → {out}")


if __name__ == "__main__":
    main()
