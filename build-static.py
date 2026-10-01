#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成静态站点（Pages 用）：public/ 目录即部署产物"""
import json, os, shutil

BASE = "/var/minis/workspace/remit-cost"
PUB = f"{BASE}/public"
os.makedirs(PUB, exist_ok=True)

html = open(f"{BASE}/src/index.html", encoding="utf-8").read()
data = open(f"{BASE}/dist/data.json", encoding="utf-8").read()
meta = json.loads(data)

assert "__DATA__" in html, "模板缺 __DATA__ 占位符"
page = html.replace("__DATA__", data)

open(f"{PUB}/index.html", "w", encoding="utf-8").write(page)
open(f"{PUB}/data.json", "w", encoding="utf-8").write(data)
open(f"{PUB}/robots.txt", "w", encoding="utf-8").write(
    "User-agent: *\nAllow: /\nSitemap: https://remitcalc.pages.dev/sitemap.xml\n")

# sitemap：首页 + 每个走廊的静态落地页（SEO 长尾）
corridors = meta["corridors"]
urls = ["https://remitcalc.pages.dev/"] + [
    f"https://remitcalc.pages.dev/send-money-to/{c['c'].lower()}/" for c in corridors
]
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    sm.append(f"  <url><loc>{u}</loc><changefreq>weekly</changefreq></url>")
sm.append("</urlset>")
open(f"{PUB}/sitemap.xml", "w", encoding="utf-8").write("\n".join(sm))

# 404
open(f"{PUB}/404.html", "w", encoding="utf-8").write(
    page.replace("<body>", '<body style="padding-top:40px">'
    '<div style="text-align:center;padding:20px 0"><b>页面不存在</b><br>'
    '<a href="/" style="color:#58a6ff">返回计算器</a></div>', 1))

# ── 走廊落地页（SEO 长尾：每个国家一个静态页）──
os.makedirs(f"{PUB}/send-money-to", exist_ok=True)
made = 0
for c in corridors:
    cc = c["c"].lower()
    d = f"{PUB}/send-money-to/{cc}"
    os.makedirs(d, exist_ok=True)
    t_zh = f"汇款到{c['n']}手续费多少？{c['trad']}% vs {c['dig']}% 对比"
    t_en = f"Cost to send money to {c.get('en') or c['n']}: {c['trad']}% vs {c['dig']}%"
    yr_save = round(2000 * (c["trad"] - c["dig"]) / 100)
    dz = (f"汇款到{c['n']}的平均成本 {c['trad']}%，数字渠道最优 {c['dig']}%。"
          f"每年寄 $2000 回家，差额 ${yr_save} 是你能多带回家的钱。实时计算，免费，不用注册。")
    de = (f"Sending to {c['n']} costs {c['trad']}% on average, versus {c['dig']}% "
          f"through the cheapest digital channel. Enter your amount and see what you keep.")
    pg = (page
          .replace("<title>汇款成本计算器 · 你寄回家的钱，路上少了多少</title>",
                   f"<title>{t_en}</title>")
          .replace('<meta name="description" content="',
                   f'<meta name="description" content="{dz} ')
          .replace("https://remitcalc.pages.dev/", f"https://remitcalc.pages.dev/send-money-to/{cc}/")
          .replace('value="200"', 'value="200" data-preset="' + c["c"] + '"')
          .replace("let FREQ = 12;", f'let FREQ = 12; let PRESET = "{c["c"]}";')
          .replace('const c=DATA.corridors.find(x=>x.c===($("#to").value));',
                   'const c=DATA.corridors.find(x=>x.c===($("#to").value))||DATA.corridors.find(x=>x.c===PRESET);')
          .replace('render();\n</script>',
                   'if(PRESET){$("#to").value=PRESET;}\nrender();\n</script>'))
    open(f"{d}/index.html", "w", encoding="utf-8").write(pg)
    made += 1

print(f"public/ 生成完毕：{made} 条走廊落地页 + 首页")
for f in sorted(os.listdir(PUB)):
    p = os.path.join(PUB, f)
    sz = os.path.getsize(p) if os.path.isfile(p) else 0
    print(f"  {f:16s} {sz:>8} B")
