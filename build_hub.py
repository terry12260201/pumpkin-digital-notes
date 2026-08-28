#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""讀 reports.json → 產生分類索引首頁 index.html。新增文章只要在 reports.json 加一列再跑這支。"""
import json, html
from pathlib import Path
from datetime import date

R = Path(__file__).parent
data = json.loads((R / "reports.json").read_text(encoding="utf-8"))
cats = data["categories"]
reports = data["reports"]

SRC_EMOJI = {"gaiconf": "🎤", "YouTube": "📺", "錄影檔": "🎬"}

def card(rp):
    emoji = SRC_EMOJI.get(rp.get("source", ""), "📄")
    cv = rp.get("cover", "")
    cover_html = (f'<div class="cv"><img loading="lazy" src="{html.escape(cv)}" alt=""></div>'
                  if cv else '<div class="cv nocv"><span>🎃</span></div>')
    return f"""<a class="card" href="{html.escape(rp['file'])}">
  {cover_html}
  <div class="cbody">
  <div class="ct"><span class="src">{emoji} {html.escape(rp.get('source',''))}</span>
    <span class="dur">{html.escape(rp.get('duration',''))}</span></div>
  <h3>{html.escape(rp['title'])}</h3>
  <p class="spk">{html.escape(rp.get('speaker',''))}</p>
  <p class="sum">{html.escape(rp.get('summary',''))}</p>
  <p class="date">閱讀 {html.escape(rp.get('date',''))}</p>
  </div>
</a>"""

sections = ""
for c in cats:
    items = [r for r in reports if r["category"] == c["id"]]
    if not items:
        continue
    items.sort(key=lambda r: r.get("date", ""), reverse=True)
    sections += f"""<section class="cat">
  <h2>{c.get('emoji','')} {html.escape(c['name'])} <span class="count">{len(items)} 篇</span></h2>
  <p class="cdesc">{html.escape(c.get('desc',''))}</p>
  <div class="grid">{''.join(card(r) for r in items)}</div>
</section>"""

DOC = f"""<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>小南瓜數位筆記</title>
<style>
:root{{--ink:#20343a;--mut:#5f747a;--teal:#0e6e63;--teal2:#0b5a51;--bg:#f5f8f8;--line:#e0e9e8;--card:#fff;--tint:#eef6f4;}}
*{{box-sizing:border-box}} html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif;line-height:1.8;font-size:17px}}
.wrap{{max-width:960px;margin:0 auto;padding:22px 16px 70px}}
header.hero{{background:linear-gradient(135deg,#0b3f39,#128577);color:#fff;border-radius:18px;padding:30px 24px;margin-bottom:24px}}
header.hero h1{{margin:0 0 8px;font-size:1.7rem}}
header.hero p{{margin:4px 0;color:#dbeeeb;font-size:.95rem}}
.cat{{margin-bottom:30px}}
h2{{font-size:1.3rem;color:var(--teal2);border-left:6px solid var(--teal);padding-left:12px;margin:10px 0 4px;display:flex;align-items:center;gap:10px}}
.count{{font-size:.8rem;background:var(--tint);color:var(--teal2);border-radius:20px;padding:2px 10px;font-weight:400}}
.cdesc{{color:var(--mut);font-size:.9rem;margin:0 0 14px 18px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media(max-width:680px){{.grid{{grid-template-columns:1fr}}}}
.card{{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;text-decoration:none;color:var(--ink);transition:.15s;box-shadow:0 1px 2px rgba(0,0,0,.03)}}
.cbody{{padding:14px 18px 16px}}
.cv{{aspect-ratio:16/9;background:#0b3f39;line-height:0;overflow:hidden}}
.cv img{{width:100%;height:100%;object-fit:cover;display:block;transition:.25s}}
.card:hover .cv img{{transform:scale(1.03)}}
.nocv{{display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#0b3f39,#128577)}}
.nocv span{{font-size:2.4rem;line-height:1;opacity:.85}}
.card:hover{{border-color:var(--teal);box-shadow:0 4px 16px rgba(14,110,99,.12);transform:translateY(-2px)}}
.ct{{display:flex;justify-content:space-between;font-size:.78rem;color:var(--mut);margin-bottom:8px}}
.src{{font-weight:600;color:var(--teal2)}}
.card h3{{font-size:1.05rem;margin:2px 0 4px;line-height:1.4;color:#123c37}}
.spk{{font-size:.85rem;color:var(--teal2);margin:0 0 8px;font-weight:600}}
.sum{{font-size:.88rem;color:var(--mut);margin:0 0 10px;line-height:1.6}}
.date{{font-size:.76rem;color:var(--mut);margin:0}}
footer{{color:var(--mut);font-size:.83rem;margin-top:24px;text-align:center}}
</style></head><body><div class="wrap">
<header class="hero">
<h1>🎃 小南瓜數位筆記</h1>
<p>影片圖文報告典藏庫——把演講、教學、競品影片，變成一眼看懂的圖文重點。</p>
<p style="opacity:.85">共 {len(reports)} 篇｜更新於 {date.today().isoformat()}</p>
</header>
{sections}
<footer>🔒 這是私人分享頁（未被搜尋引擎收錄）。連結請勿公開張貼。<br>由「小南瓜數位筆記」自動化生產線產出。</footer>
</div></body></html>"""

(R / "index.html").write_text(DOC, encoding="utf-8")
print(f"✅ index.html 產出，{len(reports)} 篇 / {len(cats)} 分類")
