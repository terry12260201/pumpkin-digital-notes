#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""讀 reports.json（schema 2）→ 產生首頁 index.html。
首頁功能：書架分區 → 場次子分區 → 卡片；頂部有搜尋框＋三族標籤篩選（多選＝同時符合）。
新增文章只要在 reports.json 加一列再跑這支（publish.py 會自動幫你做）。"""
import json, html, re
from pathlib import Path
from datetime import date

R = Path(__file__).parent
data = json.loads((R / "reports.json").read_text(encoding="utf-8"))
site = data.get("site", {})
fams = data.get("tag_families", [])
shelves = data.get("shelves", data.get("categories", []))
reports = data["reports"]

SRC_EMOJI = {"gaiconf": "🎤", "YouTube": "📺", "錄影檔": "🎬"}
E = html.escape


def fam_of(tag):
    return tag.split("/", 1)[0] if "/" in tag else "主題"


def leaf(tag):
    return tag.split("/", 1)[1] if "/" in tag else tag


FAM_IDX = {f["id"]: f for f in fams}


def chip(tag, clickable=False):
    f = FAM_IDX.get(fam_of(tag), {})
    cls = "chip" + (" ck" if clickable else "")
    attr = f' data-tag="{E(tag)}" tabindex="0" role="button"' if clickable else ""
    return (f'<span class="{cls}" style="--c:{f.get("color","#5f747a")};--t:{f.get("tint","#eef2f2")}"{attr}>'
            f'{E(leaf(tag))}</span>')


def card(rp):
    emoji = SRC_EMOJI.get(rp.get("source", ""), "📄")
    cv = rp.get("cover", "")
    cover_html = (f'<div class="cv"><img loading="lazy" src="{E(cv)}" alt=""></div>'
                  if cv else '<div class="cv nocv"><span>🎃</span></div>')
    tags = rp.get("tags", [])
    hay = " ".join([rp.get("title", ""), rp.get("speaker", ""), rp.get("summary", ""),
                    " ".join(leaf(t) for t in tags)]).lower()
    return f"""<a class="card" href="{E(rp['file'])}" data-tags="{E('|'.join(tags))}" data-hay="{E(hay)}">
  {cover_html}
  <div class="cbody">
  <div class="ct"><span class="src">{emoji} {E(rp.get('source',''))}</span>
    <span class="dur">{E(rp.get('duration',''))}</span></div>
  <h3>{E(rp['title'])}</h3>
  <p class="spk">{E(rp.get('speaker',''))}</p>
  <p class="sum">{E(rp.get('summary',''))}</p>
  <div class="tags">{''.join(chip(t) for t in tags)}</div>
  <p class="date">閱讀 {E(rp.get('date',''))}</p>
  </div>
</a>"""


def grid_of(items):
    items = sorted(items, key=lambda r: r.get("date", ""), reverse=True)
    return f'<div class="grid">{"".join(card(r) for r in items)}</div>'


# ── 書架 → 場次 ─────────────────────────────────────────────
sections_html = ""
for sh in shelves:
    items = [r for r in reports if r.get("shelf", r.get("category")) == sh["id"]]
    if not items:
        continue
    inner = ""
    secs = sh.get("sections", [])
    used = set()
    for sec in secs:
        sub = [r for r in items if r.get("section") == sec["id"]]
        if not sub:
            continue
        used.update(id(r) for r in sub)
        inner += (f'<div class="sec" data-sec><h3 class="sech">{E(sec["name"])}'
                  f'<span class="count">{len(sub)}</span></h3>{grid_of(sub)}</div>')
    rest = [r for r in items if id(r) not in used]
    if rest:
        inner += (f'<div class="sec" data-sec>{"" if not secs else f"<h3 class=sech>其他<span class=count>{len(rest)}</span></h3>"}'
                  f'{grid_of(rest)}</div>')
    sections_html += f"""<section class="shelf" data-shelf>
  <h2>{sh.get('emoji','')} {E(sh['name'])} <span class="count">{len(items)} 篇</span></h2>
  <p class="cdesc">{E(sh.get('desc',''))}</p>
  {inner}
</section>"""

# ── 篩選列 ─────────────────────────────────────────────────
filters = ""
for f in fams:
    tags = sorted({t for r in reports for t in r.get("tags", []) if fam_of(t) == f["id"]},
                  key=lambda t: (-sum(1 for r in reports if t in r.get("tags", [])), t))
    if not tags:
        continue
    filters += (f'<div class="frow"><span class="flab">{f.get("emoji","")} {E(f["name"])}</span>'
                f'<div class="fchips">{"".join(chip(t, True) for t in tags)}</div></div>')

DOC = f"""<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>小南瓜數位筆記</title>
<style>
:root{{--ink:#20343a;--mut:#5f747a;--teal:#0e6e63;--teal2:#0b5a51;--bg:#f5f8f8;--line:#e0e9e8;--card:#fff;--tint:#eef6f4;}}
*{{box-sizing:border-box}} html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif;line-height:1.8;font-size:17px}}
.wrap{{max-width:960px;margin:0 auto;padding:22px 16px 70px}}
header.hero{{background:linear-gradient(135deg,#0b3f39,#128577);color:#fff;border-radius:18px;padding:30px 24px;margin-bottom:18px}}
header.hero h1{{margin:0 0 8px;font-size:1.7rem}}
header.hero p{{margin:4px 0;color:#dbeeeb;font-size:.95rem}}

/* 搜尋＋篩選 */
.panel{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin-bottom:22px}}
.sbox{{display:flex;align-items:center;gap:10px;border:1.5px solid var(--line);border-radius:10px;padding:8px 12px;background:#fbfdfd}}
.sbox:focus-within{{border-color:var(--teal)}}
.sbox input{{border:0;outline:0;background:transparent;font-size:1rem;flex:1;font-family:inherit;color:var(--ink);min-width:0}}
.ficon{{color:var(--mut)}}
.ftoggle{{margin-top:10px;background:none;border:0;color:var(--teal2);font:inherit;font-size:.88rem;cursor:pointer;padding:2px 0;font-weight:600}}
.fbody{{display:none;margin-top:6px}} .fbody.on{{display:block}}
.frow{{display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-top:1px dashed var(--line)}}
.flab{{flex:0 0 118px;font-size:.85rem;color:var(--mut);padding-top:3px}}
.fchips{{display:flex;flex-wrap:wrap;gap:6px;flex:1}}
.chip{{display:inline-block;font-size:.75rem;line-height:1.5;padding:2px 9px;border-radius:20px;background:var(--t);color:var(--c);border:1px solid transparent;white-space:nowrap}}
.chip.ck{{cursor:pointer;user-select:none}}
.chip.ck:hover{{border-color:var(--c)}}
.chip.on{{background:var(--c);color:#fff}}
.bar{{display:flex;align-items:center;gap:12px;margin-top:10px;font-size:.85rem;color:var(--mut)}}
.clr{{background:none;border:0;color:var(--teal2);font:inherit;font-size:.85rem;cursor:pointer;text-decoration:underline;padding:0}}
.hid{{display:none !important}}
.empty{{display:none;text-align:center;color:var(--mut);padding:40px 0}}
.empty.on{{display:block}}

.shelf{{margin-bottom:30px}}
h2{{font-size:1.3rem;color:var(--teal2);border-left:6px solid var(--teal);padding-left:12px;margin:10px 0 4px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.count{{font-size:.78rem;background:var(--tint);color:var(--teal2);border-radius:20px;padding:2px 10px;font-weight:400}}
.cdesc{{color:var(--mut);font-size:.9rem;margin:0 0 14px 18px}}
.sec{{margin:0 0 20px}}
.sech{{font-size:1rem;color:var(--mut);margin:0 0 10px 18px;display:flex;align-items:center;gap:8px;font-weight:600}}
.sech::before{{content:"";width:8px;height:8px;border-radius:50%;background:var(--teal);opacity:.55}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media(max-width:680px){{.grid{{grid-template-columns:1fr}} .frow{{flex-direction:column;gap:4px}} .flab{{flex:none}}}}
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
.tags{{display:flex;flex-wrap:wrap;gap:5px;margin:0 0 10px}}
.date{{font-size:.76rem;color:var(--mut);margin:0}}
footer{{color:var(--mut);font-size:.83rem;margin-top:24px;text-align:center}}
</style></head><body><div class="wrap">
<header class="hero">
<h1>{E(site.get('title','🎃 小南瓜數位筆記'))}</h1>
<p>{E(site.get('tagline',''))}</p>
<p style="opacity:.8">{E(site.get('sub',''))}</p>
<p style="opacity:.7">共 {len(reports)} 篇｜更新於 {date.today().isoformat()}</p>
</header>

<div class="panel">
  <label class="sbox"><span class="ficon">🔍</span>
    <input id="q" type="search" placeholder="搜尋標題、講者、重點、標籤…" autocomplete="off"></label>
  <button class="ftoggle" id="ft">🏷️ 用標籤篩選 ▾</button>
  <div class="fbody" id="fb">{filters}</div>
  <div class="bar"><span id="cnt">共 {len(reports)} 篇</span><button class="clr" id="clr">清除全部條件</button></div>
</div>

{sections_html}
<div class="empty" id="empty">😶 沒有符合的筆記，換個關鍵字或少選幾個標籤試試。</div>
<footer>🔒 這是私人分享頁（未被搜尋引擎收錄）。連結請勿公開張貼。<br>由「小南瓜數位筆記」自動化生產線產出。</footer>
</div>
<script>
(function(){{
  var q=document.getElementById('q'),fb=document.getElementById('fb'),ft=document.getElementById('ft');
  var cards=[].slice.call(document.querySelectorAll('.card'));
  var picked=[];
  ft.onclick=function(){{fb.classList.toggle('on');ft.textContent=fb.classList.contains('on')?'🏷️ 用標籤篩選 ▴':'🏷️ 用標籤篩選 ▾';}};
  function apply(){{
    var kw=(q.value||'').trim().toLowerCase(), n=0;
    cards.forEach(function(c){{
      var tags=(c.dataset.tags||'').split('|');
      var ok=(!kw||c.dataset.hay.indexOf(kw)>=0) && picked.every(function(t){{return tags.indexOf(t)>=0;}});
      c.classList.toggle('hid',!ok); if(ok)n++;
    }});
    [].forEach.call(document.querySelectorAll('[data-sec]'),function(s){{
      var v=s.querySelectorAll('.card:not(.hid)').length;
      s.classList.toggle('hid',!v);
      var b=s.querySelector('.sech .count'); if(b)b.textContent=v;}});
    [].forEach.call(document.querySelectorAll('[data-shelf]'),function(s){{
      var v=s.querySelectorAll('.card:not(.hid)').length;
      s.classList.toggle('hid',!v);
      var b=s.querySelector('h2 .count'); if(b)b.textContent=v+' 篇';}});
    document.getElementById('cnt').textContent=(kw||picked.length)?('找到 '+n+' 篇'):('共 '+n+' 篇');
    document.getElementById('empty').classList.toggle('on',n===0);
  }}
  function toggle(el){{
    var t=el.dataset.tag,i=picked.indexOf(t);
    if(i>=0){{picked.splice(i,1);}}else{{picked.push(t);}}
    [].forEach.call(document.querySelectorAll('.chip.ck[data-tag="'+t.replace(/"/g,'\\\\"')+'"]'),
      function(c){{c.classList.toggle('on',i<0);}});
    apply();
  }}
  [].forEach.call(document.querySelectorAll('.chip.ck'),function(el){{
    el.addEventListener('click',function(){{toggle(el);}});
    el.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' '){{e.preventDefault();toggle(el);}}}});
  }});
  q.addEventListener('input',apply);
  document.getElementById('clr').onclick=function(){{
    q.value='';picked=[];
    [].forEach.call(document.querySelectorAll('.chip.ck'),function(c){{c.classList.remove('on');}});
    apply();
  }};
  apply();
}})();
</script>
</body></html>"""

(R / "index.html").write_text(DOC, encoding="utf-8")
ntags = len({t for r in reports for t in r.get("tags", [])})
print(f"✅ index.html 產出：{len(reports)} 篇 / {len(shelves)} 書架 / {ntags} 個標籤")
