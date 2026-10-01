#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拉取汇率 + 生成走廊数据 → dist/data.json"""
import json, urllib.request, os, time, subprocess, sys

BASE = "/var/minis/workspace/remit-cost"
os.makedirs(f"{BASE}/dist", exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}


def get(u, tries=5):
    last = None
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25).read())
        except Exception as e:
            last = e
            time.sleep(3 * (i + 1))
    raise last


# ── 走廊（gen_corridors.py 生成：成本基准 + 国家/币种）──
subprocess.run([sys.executable, f"{BASE}/gen_corridors.py"], check=True)
CORRIDORS = json.load(open("/tmp/corridors.json"))

# ── 汇率（抓不到就用缓存，出口抖动是常态）──
CACHE = f"{BASE}/.fx-cache.json"
try:
    fx = get("https://open.er-api.com/v6/latest/USD")
    json.dump(fx, open(CACHE, "w"))
    print("汇率已刷新:", fx.get("time_last_update_utc"))
except Exception as e:
    print("汇率抓取失败，用缓存:", str(e)[:70])
    fx = json.load(open(CACHE))

rates = fx["rates"]
missing = set()
for c in CORRIDORS:
    c["rate"] = rates.get(c["cur"])
    if c["rate"] is None:
        missing.add(c["cur"])
if missing:
    print("⚠ 缺汇率:", missing)

data = {
    "updated": fx.get("time_last_update_utc"),
    "base": "USD",
    "benchmark": {"global_avg": 6.2, "bank": 11.4, "mto": 5.6,
                  "mobile": 4.1, "digital": 3.1, "sdg_target": 3.0},
    "corridors": CORRIDORS,
}

json.dump(data, open(f"{BASE}/dist/data.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(f"生成 dist/data.json  {len(CORRIDORS)} 条走廊 / {len(rates)} 币种")
