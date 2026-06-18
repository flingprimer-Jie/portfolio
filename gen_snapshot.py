#!/usr/bin/env python3
"""Bake fresh IBKR data into index.html between the IBKR_SNAPSHOT markers.
Usage: python3 gen_snapshot.py positions.json summary.json index.html
positions.json = raw output of get_account_positions
summary.json   = raw output of get_account_summary
"""
import json, re, sys, datetime

pos_f, sum_f, html_f = sys.argv[1], sys.argv[2], sys.argv[3]
positions = json.load(open(pos_f)).get("positions", [])
summary = json.load(open(sum_f))
net = summary.get("net_liquidation", 0)
cash = summary.get("total_cash_value", summary.get("cash_balance", summary.get("available_funds", 0)))

def r(x, n=2):
    return round(float(x), n)

lines = ["const IB_FALLBACK = {positions:["]
for p in positions:
    if not p.get("position"):
        continue
    lines.append(
        '  {{contract_description:"{d}",position:{q},market_price:{mp},market_value:{mv},'
        'average_price:{ap},unrealized_pnl:{pl}}},'.format(
            d=p["contract_description"], q=r(p["position"], 4),
            mp=r(p["market_price"], 2), mv=r(p["market_value"], 2),
            ap=r(p["average_price"], 5), pl=r(p["unrealized_pnl"], 2),
        )
    )
lines.append("]};")
lines.append("const IB_NET_FALLBACK = {};".format(r(net)))
lines.append("const IB_CASH_FALLBACK = {};".format(r(cash)))
stamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
lines.append('const IB_SNAPSHOT_TIME = "{}";'.format(stamp))
block = "/*IBKR_SNAPSHOT_START*/\n" + "\n".join(lines) + "\n/*IBKR_SNAPSHOT_END*/"

html = open(html_f, encoding="utf-8").read()
new = re.sub(r"/\*IBKR_SNAPSHOT_START\*/.*?/\*IBKR_SNAPSHOT_END\*/",
             block.replace("\\", "\\\\"), html, count=1, flags=re.S)
if new == html and "/*IBKR_SNAPSHOT_START*/" not in html:
    sys.exit("ERROR: snapshot markers not found in " + html_f)
open(html_f, "w", encoding="utf-8").write(new)
print("Snapshot baked:", stamp, "| positions:", len([p for p in positions if p.get('position')]), "| net:", r(net), "| cash:", r(cash))
