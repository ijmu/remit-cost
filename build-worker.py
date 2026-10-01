#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 src/index.html + dist/data.json 打包成单文件 Worker（零后端部署）"""
import json, os

BASE = "/var/minis/workspace/remit-cost"
html = open(f"{BASE}/src/index.html", encoding="utf-8").read()
data = open(f"{BASE}/dist/data.json", encoding="utf-8").read()

assert "__DATA__" in html, "模板缺 __DATA__ 占位符"
page = html.replace("__DATA__", data)

SEC = {
    "content-type": "text/html; charset=utf-8",
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "x-frame-options": "DENY",
    "cache-control": "public, max-age=3600",
}

worker = f'''/* 汇款成本计算器 · 单文件 Worker
   数据以 JSON 内联，无后端依赖。汇率刷新 = 重跑 fetch_data.py + 重新部署。 */
const PAGE = {json.dumps(page)};

export default {{
  async fetch(req) {{
    const p = new URL(req.url).pathname;
    const H = {json.dumps(SEC)};
    if (p === "/" || p === "/index.html") return new Response(PAGE, {{ headers: H }});
    if (p === "/robots.txt")
      return new Response("User-agent: *\\nAllow: /\\nSitemap: /sitemap.xml\\n",
        {{ headers: {{ "content-type": "text/plain" }} }});
    if (p === "/healthz")
      return new Response(JSON.stringify({{ ok: true, corridors: {len(json.loads(data)["corridors"])} }}),
        {{ headers: {{ "content-type": "application/json" }} }});
    return new Response("Not Found", {{ status: 404 }});
  }},
}};
'''

out = f"{BASE}/remit-worker.mjs"
open(out, "w", encoding="utf-8").write(worker)
print(f"生成 remit-worker.mjs  {os.path.getsize(out)/1024:.1f}KB")
