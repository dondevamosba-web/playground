#!/usr/bin/env python3
"""
Record today's follower/media snapshot for all 4 accounts, so the dashboard
(tools/social_dashboard_server.py) can chart day-by-day growth.

The dashboard also auto-snapshots on page load, so running this via cron is
optional — it just guarantees a data point even on days nobody opens the
dashboard.

Usage:
  python3 tools/snapshot_social_stats.py
"""
from tools.social_stats import ACCOUNT_CONFIG, DISPLAY_NAMES, fetch_account_stats, record_snapshot


def main():
    for account in ACCOUNT_CONFIG:
        stats = fetch_account_stats(account)
        if not stats:
            print(f"⚠️  {DISPLAY_NAMES[account]}: no configurado en .env, se salteó")
            continue
        record_snapshot(stats)
        print(f"✅ {DISPLAY_NAMES[account]} (@{stats['username']}): "
              f"{stats['followers_count']} seguidores, {stats['media_count']} posts")


if __name__ == "__main__":
    main()
