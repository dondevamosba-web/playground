#!/usr/bin/env python3
"""
Meta Ads budget pacing tool.

Compares each active ad set's spend-so-far today against where it should be
at this time of day, given its daily budget. Flags what to scale or throttle.

Pacing logic:
  expected_spend = daily_budget × (current_hour / 24)
  pacing_ratio   = actual_spend / expected_spend

  AHEAD    pacing_ratio > 1.20  → consider pausing or reducing budget
  ON TRACK 0.80 – 1.20          → all good
  BEHIND   pacing_ratio < 0.80  → consider increasing budget or checking delivery

Requires in .env:
  META_ACCESS_TOKEN    — token with ads_read permission
  META_AD_ACCOUNT_ID   — comma-separated (e.g. act_123,act_456)

Usage:
  python3 tools/budget_pacer.py              # check + create Gmail draft
  python3 tools/budget_pacer.py --dry-run    # print only, no draft
  python3 tools/budget_pacer.py --ahead      # show only overspending ad sets
  python3 tools/budget_pacer.py --behind     # show only underspending ad sets
"""
import argparse
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.claude_call import call_claude
from tools.gmail_draft import create_draft, build_html_body

GRAPH_URL = "https://graph.facebook.com/v19.0"
AHEAD_THRESHOLD  = 1.20   # 20% over expected
BEHIND_THRESHOLD = 0.80   # 20% under expected
MIN_BUDGET = 5.0          # ignore ad sets with daily budget < $5


# ── API helpers ───────────────────────────────────────────────────────────────

def get_adsets(account_id: str, token: str) -> list:
    """Fetch active ad sets with their daily budgets."""
    fields = "name,campaign_id,campaign{name},daily_budget,budget_remaining,status,effective_status"
    params = {
        "fields": fields,
        "filtering": '[{"field":"effective_status","operator":"IN","value":["ACTIVE"]}]',
        "limit": 200,
        "access_token": token,
    }
    rows = []
    url = f"{GRAPH_URL}/{account_id}/adsets"
    while url:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            err = resp.json().get("error", {})
            print(f"  API error ({account_id}): {err.get('message', resp.text)}")
            return []
        data = resp.json()
        rows.extend(data.get("data", []))
        url = data.get("paging", {}).get("next")
        params = {}
    return rows


def get_today_spend(account_id: str, token: str) -> dict:
    """Return {adset_id: spend_today} for all ad sets."""
    today = date.today().isoformat()
    params = {
        "level": "adset",
        "fields": "adset_id,adset_name,spend",
        "time_range": f'{{"since":"{today}","until":"{today}"}}',
        "limit": 200,
        "access_token": token,
    }
    spend_map = {}
    url = f"{GRAPH_URL}/{account_id}/insights"
    while url:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            break
        data = resp.json()
        for row in data.get("data", []):
            spend_map[row["adset_id"]] = float(row.get("spend", 0))
        url = data.get("paging", {}).get("next")
        params = {}
    return spend_map


# ── Pacing calculation ────────────────────────────────────────────────────────

def pacing_ratio(spend: float, daily_budget: float, hour_utc: int) -> float:
    """How much should have been spent by now vs actual."""
    if daily_budget <= 0:
        return 1.0
    # Meta distributes spend across the day; use current hour as fraction
    expected = daily_budget * (hour_utc / 24)
    if expected == 0:
        return 1.0
    return spend / expected


def classify(ratio: float) -> str:
    if ratio > AHEAD_THRESHOLD:
        return "AHEAD"
    if ratio < BEHIND_THRESHOLD:
        return "BEHIND"
    return "ON TRACK"


# ── Summary generation ────────────────────────────────────────────────────────

def build_summary(results: list, hour_utc: int, today: str) -> str:
    flags = [r for r in results if r["status"] != "ON TRACK"]
    if not flags:
        return f"All ad sets on track as of {hour_utc}:00 UTC on {today}."

    lines = []
    for r in flags:
        lines.append(
            f"- [{r['status']}] {r['campaign']} / {r['adset']}: "
            f"${r['spend']:.2f} spent of ${r['budget']:.2f} daily budget "
            f"(pacing {r['ratio']:.0%}, expected {r['expected']:.2f})"
        )
    prompt = (
        f"You are a Meta Ads manager. It is {hour_utc}:00 UTC on {today}. "
        "These ad sets have pacing issues:\n\n"
        + "\n".join(lines)
        + "\n\nWrite a concise 3-bullet action plan for the account manager. "
        "Each bullet: ad set name, issue, specific action (pause / reduce budget by X% / check delivery). "
        "No intro, no conclusion — just the 3 bullets."
    )
    # haiku: mechanical formatting of flagged data into bullets
    return call_claude(prompt, model="haiku")


def adversarial_check(summary: str, results: list, hour_utc: int, today: str) -> tuple[bool, str]:
    """
    Attempt to refute the recommended actions in summary.
    Returns (passed, refutation_log).
    passed=True means the summary survived scrutiny and can go to the draft.
    passed=False means a concern was raised that warrants human review.
    """
    flags = [r for r in results if r["status"] != "ON TRACK"]
    data_lines = "\n".join(
        f"- {r['campaign']} / {r['adset']}: pacing {r['ratio']:.0%} at hour {hour_utc} UTC, "
        f"budget ${r['budget']:.2f}, spent ${r['spend']:.2f}"
        for r in flags
    )
    prompt = (
        f"You are an adversarial reviewer. It is {hour_utc}:00 UTC on {today}.\n\n"
        "A Meta Ads manager has proposed the following actions:\n\n"
        f"{summary}\n\n"
        "Raw pacing data:\n"
        f"{data_lines}\n\n"
        "Your job is to find reasons these actions could be WRONG or premature. Consider:\n"
        "- Is it too early in the day to judge pacing (before hour 8 UTC)?\n"
        "- Could a BEHIND ad set be in the learning phase or have a schedule start delay?\n"
        "- Could an AHEAD ad set be intentionally front-loaded by Meta's delivery algorithm?\n"
        "- Is the budget difference small enough to be noise (under $5 deviation)?\n"
        "- Would pausing now harm an in-flight auction?\n\n"
        "If you find a legitimate concern: start with REFUTED, then explain in 1-2 lines.\n"
        "If the actions look sound: start with PASSED, then confirm why in 1 line.\n"
        "Be concise and direct."
    )
    # sonnet: adversarial judgment call, not formatting
    verdict = call_claude(prompt, model="sonnet")
    passed = verdict.strip().upper().startswith("PASSED")
    return passed, verdict


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ahead",  action="store_true", help="Show only overspending")
    parser.add_argument("--behind", action="store_true", help="Show only underspending")
    args = parser.parse_args()

    token = os.getenv("META_ACCESS_TOKEN")
    account_ids_raw = os.getenv("META_AD_ACCOUNT_ID", "")
    if not token or not account_ids_raw:
        print("Missing credentials. Add to .env:")
        print("  META_ACCESS_TOKEN=<token>")
        print("  META_AD_ACCOUNT_ID=act_XXXXXXXXX")
        sys.exit(1)

    account_ids = [a.strip() for a in account_ids_raw.split(",") if a.strip()]
    now_utc = datetime.now(timezone.utc)
    hour_utc = now_utc.hour
    today = date.today().isoformat()

    print(f"Budget pacing check — {today} {hour_utc}:00 UTC")
    all_results = []

    for account_id in account_ids:
        print(f"\n  {account_id}")
        adsets = get_adsets(account_id, token)
        spend_map = get_today_spend(account_id, token)

        for adset in adsets:
            budget_cents = int(adset.get("daily_budget", 0) or 0)
            budget = budget_cents / 100  # Meta returns budget in cents
            if budget < MIN_BUDGET:
                continue

            adset_id = adset["id"]
            spend = spend_map.get(adset_id, 0.0)
            expected = budget * (hour_utc / 24)
            ratio = pacing_ratio(spend, budget, hour_utc)
            status = classify(ratio)
            campaign_name = (adset.get("campaign") or {}).get("name", adset.get("campaign_id", ""))

            all_results.append({
                "account": account_id,
                "campaign": campaign_name,
                "adset": adset["name"],
                "budget": budget,
                "spend": spend,
                "expected": expected,
                "ratio": ratio,
                "status": status,
            })

    # Filter
    display = all_results
    if args.ahead:
        display = [r for r in all_results if r["status"] == "AHEAD"]
    elif args.behind:
        display = [r for r in all_results if r["status"] == "BEHIND"]

    display.sort(key=lambda r: (r["status"] == "ON TRACK", -abs(r["ratio"] - 1)))

    # Print table
    counts = {"AHEAD": 0, "ON TRACK": 0, "BEHIND": 0}
    for r in all_results:
        counts[r["status"]] += 1

    print(f"\n{'Status':<10} {'Campaign':<30} {'Ad Set':<35} {'Budget':>8} {'Spent':>8} {'Expected':>9} {'Pacing':>8}")
    print("-" * 115)
    for r in display:
        print(
            f"{r['status']:<10} {r['campaign'][:28]:<30} {r['adset'][:33]:<35} "
            f"${r['budget']:>7.2f} ${r['spend']:>7.2f} ${r['expected']:>8.2f} {r['ratio']:>7.0%}"
        )

    print(f"\nSummary: {counts['AHEAD']} ahead  |  {counts['ON TRACK']} on track  |  {counts['BEHIND']} behind  ({len(all_results)} total active)")

    summary = build_summary(all_results, hour_utc, today)
    print(f"\n{summary}")

    if not args.dry_run and any(r["status"] != "ON TRACK" for r in all_results):
        passed, refutation_log = adversarial_check(summary, all_results, hour_utc, today)
        print(f"\n[adversarial] {refutation_log}")

        flags_count = counts["AHEAD"] + counts["BEHIND"]
        if passed:
            subject = f"Meta Budget Pacing — {today} {hour_utc}:00 UTC ({flags_count} flag(s))"
            body_text = summary + f"\n\n---\n[adversarial check] {refutation_log}"
            html = build_html_body(body_text)
            result = create_draft(to="dondevamosba@gmail.com", subject=subject, body=html, html=True)
            print(f"\nGmail draft created: {result['draft_id']}")
        else:
            subject = f"[HELD] Meta Budget Pacing — {today} {hour_utc}:00 UTC ({flags_count} flag(s)) — adversarial refuted"
            body_text = (
                "The following actions were proposed but held by adversarial review.\n\n"
                f"PROPOSED ACTIONS:\n{summary}\n\n"
                f"ADVERSARIAL REFUTATION:\n{refutation_log}\n\n"
                "Review manually before acting."
            )
            html = build_html_body(body_text)
            result = create_draft(to="dondevamosba@gmail.com", subject=subject, body=html, html=True)
            print(f"\nDraft held (adversarial refuted) — created for manual review: {result['draft_id']}")
    elif not args.dry_run:
        print("\nAll on track — no draft needed.")


if __name__ == "__main__":
    main()
