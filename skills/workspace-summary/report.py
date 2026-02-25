#!/usr/bin/env python3
"""Generate a compact status report from STATE.json and memory.db"""
import json, sqlite3
from pathlib import Path

def main():
    with open('./STATE.json') as f:
        state = json.load(f)
    sys = state['system']
    fin = state['finances']
    tasks = state['tasks']

    print("=== Genesis-01 Status ===")
    print(f"Phase: {sys['phase']}  |  Heartbeats: {sys['heartbeat_count']}  |  Health: {sys['health']}")
    print(f"Tasks: {len(tasks['active'])} active, {len(tasks['queued'])} queued, {len(tasks['completed'])} completed")
    print(f"Finances: £{fin['current_balance_gbp']} balance  (£{fin['total_revenue_gbp']} earned)")

    conn = sqlite3.connect('./memory/memory.db')
    rows = conn.execute("SELECT timestamp, type, description, outcome FROM events ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    print("\nRecent Events:")
    for r in rows:
        print(f"  {r[0][:19]} [{r[1]}] {r[2]} ({r[3]})")

if __name__ == '__main__':
    main()
