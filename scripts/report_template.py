#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""圖文報告 v2：國小生也讀得懂的白話版 + 專有名詞小辭典（內文可連結對照）+ 手機友善排版。"""
import base64, io, html
from pathlib import Path
from PIL import Image

JOB = Path(__file__).parent / "yt_job"
FRAMES = JOB / "frames"
VID = "tuVu8HuJHMc"                       # YouTube 影片 ID（時間戳深連結用）
OUTDIR = Path("/Users/chennanhong/Documents/Pumpapa/知識庫/影片筆記/2026-08-18_Hermes接LINE")
OUT = OUTDIR / "報告.html"
READ_DATE = "2026-08-18"

def yt_at(clock):
    """把 '6:10' / '1:07:10' 轉成 YouTube ...&t=370s 深連結的秒數"""
    parts = [int(x) for x in clock.split(":")]
    sec = parts[0]*3600+parts[1]*60+parts[2] if len(parts)==3 else parts[0]*60+parts[1]
    return f"https://www.youtube.com/watch?v={VID}&t={sec}s"

# ---------- 專有名詞小辭典（id: (詞, 白話解釋)）----------
GLOSSARY = {
    "agent":   ("AI Agent（AI 代理人）", "一個會幫你做事的 AI 小助手。你交代它一句話，它會自己想辦法、動手完成，不只是回答問題。"),
    "skill":   ("Skill（技能）", "AI 學會的一項本領。學會之後，下次你叫它，它就能直接做，不用重教一次。"),
    "line-dev":("LINE Developers", "LINE 官方給工程師用的後台網站。想讓程式跟 LINE 連在一起，就要來這裡申請。"),
    "provider":("Provider（提供者）", "你在 LINE 後台的「開發者身分證」。之後做的東西都掛在這個身分底下。"),
    "channel": ("Channel（頻道）", "一條讓你的程式跟 LINE 對話的專線。這支影片建的是「訊息類」的專線。"),
    "msgapi":  ("Messaging API", "LINE 提供的一組「傳訊息的管道」。有了它，程式才能自動幫你收發 LINE 訊息。"),
    "secret":  ("Channel Secret（頻道密鑰）", "一組 32 個字的密碼，用來證明「這條專線真的是你的」。要保密。"),
    "token":   ("Channel Access Token（存取金鑰）", "另一把很長的鑰匙，程式拿它才能用你的名義發 LINE 訊息。跟密碼一樣要藏好。"),
    "webhook": ("Webhook（網路門鈴）", "把它想成門鈴。有人在 LINE 傳訊息，LINE 就會自動「按你電腦的門鈴」，通知它：有新訊息囉！"),
    "ngrok":   ("ngrok（臨時公開地址）", "幫你家（你的電腦）裝一條「臨時的公開門牌」，外面的人才找得到你家、按得到門鈴。"),
    "https":   ("HTTPS 網址", "一個「有加密、比較安全」的網站地址，開頭是 https://。"),
    "port":    ("Port（連接埠）", "電腦上的一個「門號」。不同程式用不同門號，這支影片的 AI 用的是 8646 號門。"),
    "allowed": ("Allowed IDs（白名單）", "一張「准許名單」。只有名單上的人，才能跟你的 AI 用 LINE 聊天。"),
    "userid":  ("LINE User ID", "每個 LINE 使用者的一組專屬編號，像身分證號。把自己的填進白名單，AI 才會回你。"),
    "gateway": ("Hermes Gateway（閘道）", "Hermes 這個 AI 對外的「大門」。改完設定要把大門重開一次，新設定才會生效。"),
    "gptimg":  ("GPT Image 2", "OpenAI 做的一個「用文字畫圖」的 AI。你打字描述，它就畫出圖片。"),
    "verify":  ("Verify（驗證）", "LINE 後台的一個「測試連線」按鈕。按下去，確認門鈴真的按得到你電腦。"),
}

def img(n, maxw=1000, q=72):
    im = Image.open(FRAMES / f"f_{n:04d}.jpg").convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def T(gid, label=None):
    """內文專有名詞 → 連到小辭典的連結"""
    term, _ = GLOSSARY[gid]
    txt = label or term.split("（")[0]
    return f'<a class="term" href="#g-{gid}" title="點我看解釋">{txt}</a>'

def fig(n, cap, tclock):
    return (f'<figure><img loading="lazy" src="{img(n)}" alt="{html.escape(cap)}">'
            f'<figcaption><a class="t" href="{yt_at(tclock)}" target="_blank" '
            f'rel="noopener" title="點我跳到影片這一段">▶ {tclock}</a> {cap}</figcaption></figure>')

def grid(*figs):
    return '<div class="grid2">' + "".join(figs) + '</div>'

glossary_rows = "".join(
    f'<tr id="g-{gid}"><td><b>{html.escape(term)}</b></td><td>{html.escape(desc)}</td></tr>'
    for gid, (term, desc) in GLOSSARY.items()
)

DOC = f"""<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>白話圖文報告．把 AI 助手裝進 LINE</title>
<style>
:root{{--ink:#20343a;--mut:#5f747a;--teal:#0e6e63;--teal2:#0b5a51;--bg:#f5f8f8;--line:#e0e9e8;--card:#fff;--warn:#8a5a08;--tint:#eef6f4;}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif;
  line-height:1.9;font-size:17px;word-break:break-word}}
.wrap{{max-width:820px;margin:0 auto;padding:20px 16px 70px}}
header.hero{{background:linear-gradient(135deg,#0b3f39,#128577);color:#fff;border-radius:18px;padding:26px 22px 22px;margin-bottom:22px}}
header.hero h1{{margin:0 0 12px;font-size:1.55rem;line-height:1.45}}
.facts{{display:grid;grid-template-columns:1fr 1fr;gap:8px 16px;margin:14px 0 4px;font-size:.92rem}}
@media(max-width:560px){{.facts{{grid-template-columns:1fr}}}}
.facts div{{color:#dbeeeb}} .facts b{{color:#fff}}
.hero .one{{background:rgba(255,255,255,.14);border-radius:12px;padding:12px 15px;margin-top:14px;font-size:.98rem;line-height:1.75}}
nav.toc{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 18px;margin-bottom:22px;font-size:.95rem}}
nav.toc b{{color:var(--teal2);display:block;margin-bottom:6px;font-size:.85rem}}
nav.toc a{{color:var(--teal);text-decoration:none;margin:0 12px 6px 0;white-space:nowrap;display:inline-block}}
section{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px 20px;margin-bottom:20px}}
h2{{font-size:1.28rem;margin:4px 0 12px;color:var(--teal2);border-left:6px solid var(--teal);padding-left:12px;line-height:1.4}}
h3{{font-size:1.08rem;margin:22px 0 6px;color:#123c37}}
p{{margin:10px 0}}
figure{{margin:14px 0}}
figure img{{width:100%;max-width:100%;border-radius:10px;border:1px solid var(--line);display:block}}
figcaption{{font-size:.84rem;color:var(--mut);margin-top:6px;line-height:1.6}}
.t{{background:var(--teal);color:#fff;padding:2px 10px;border-radius:20px;font-size:.74rem;margin-right:6px;white-space:nowrap;text-decoration:none;display:inline-block}}
a.t:hover{{background:var(--teal2)}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
@media(max-width:640px){{.grid2{{grid-template-columns:1fr}}}}
.tbl-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
table{{border-collapse:collapse;width:100%;font-size:.92rem;margin:12px 0;min-width:min(100%,420px)}}
th,td{{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}}
th{{background:var(--tint);color:#123c37}}
.term{{color:var(--teal2);text-decoration:none;border-bottom:1.5px dotted var(--teal);font-weight:600;cursor:help}}
.term:after{{content:"❓";font-size:.7em;vertical-align:super;margin-left:1px;opacity:.7}}
.quote{{background:var(--tint);border-left:4px solid var(--teal);padding:12px 16px;border-radius:0 10px 10px 0;margin:14px 0;font-size:.97rem}}
.note{{background:#fbf3e6;border-left:4px solid #d99a2b;padding:11px 15px;border-radius:0 10px 10px 0;font-size:.93rem;color:#5c4a1e;margin:14px 0}}
.step{{background:var(--tint);border-radius:12px;padding:4px 16px;margin:12px 0}}
:target{{animation:hl 2s ease}} @keyframes hl{{0%{{background:#fff2cc}}100%{{background:transparent}}}}
.small{{font-size:.85rem;color:var(--mut)}}
a{{color:var(--teal)}}
footer{{color:var(--mut);font-size:.84rem;margin-top:24px;padding:0 4px}}
</style></head><body><div class="wrap">

<header class="hero">
<h1>把「AI 小助手」裝進 LINE，用手機就能使喚它</h1>
<div class="facts">
<div>🎬 <b>影片</b>：Hermes Agent 接上 LINE！把 AI 秘書放進口袋裡（完整教學）</div>
<div>📺 <b>來源頻道</b>：網際之星開發實驗室 @CyberstarLab</div>
<div>🔗 <b>出處</b>：<a href="https://www.youtube.com/watch?v=tuVu8HuJHMc" style="color:#bfe9e2">youtube.com/watch?v=tuVu8HuJHMc</a></div>
<div>⏱️ <b>影片總長</b>：15 分 47 秒</div>
<div>📅 <b>影片上傳</b>：2026-08-07</div>
<div>👀 <b>閱讀日期</b>：{READ_DATE}</div>
</div>
<div class="one">📖 <b>一句話大綱</b>：這支影片教你把一個「會幫你做事的 AI」裝進 LINE，之後你在 LINE 打字，它就能幫你查資料、畫漫畫、記事情，全部在手機上完成。整件事分成 <b>4 個步驟</b>，最容易出錯的地方也只有 3 個。</div>
</header>

<nav class="toc">
<b>這份報告有什麼（點了會跳過去）</b>
<a href="#outline">📋 大綱總結</a>
<a href="#what">🤔 這是在做什麼</a>
<a href="#s1">1️⃣ 申請鑰匙</a>
<a href="#s2">2️⃣ 開一條路</a>
<a href="#s3">3️⃣ 填設定</a>
<a href="#s4">4️⃣ 手機試玩</a>
<a href="#keys">⚠️ 三個常見錯誤</a>
<a href="#glossary">📖 專有名詞小辭典</a>
</nav>

<section id="outline">
<h2>📋 大綱總結（30 秒看完）</h2>
<div class="tbl-wrap"><table>
<tr><th style="width:76px">步驟</th><th>白話說的話</th><th style="width:96px">影片時間</th></tr>
<tr><td><b>準備</b></td><td>先搞懂：我們要把一個「AI 小幫手」裝進大家每天都在用的 LINE。</td><td>0:00–0:53</td></tr>
<tr><td><b>第 1 步</b></td><td>去 LINE 的官方網站申請，拿到<b>兩把鑰匙</b>（等一下程式要用）。</td><td>0:53–5:07</td></tr>
<tr><td><b>第 2 步</b></td><td>幫你的電腦開一條「外面找得到的臨時通道」，LINE 才連得進來。</td><td>5:07–6:40</td></tr>
<tr><td><b>第 3 步</b></td><td>把兩把鑰匙和通道網址，<b>填進 AI 小幫手的設定裡</b>，存檔重開。</td><td>6:40–8:07</td></tr>
<tr><td><b>第 4 步</b></td><td>拿手機加它好友、傳訊息，<b>它真的會回你了！</b>還示範查颱風、畫漫畫。</td><td>8:07–13:50</td></tr>
<tr><td><b>收尾</b></td><td>整理最容易卡住的 3 件事，以及這個 AI 為什麼比一般聊天 AI 更聰明。</td><td>13:50–15:47</td></tr>
</table></div>
<p class="small">💡 兩個小撇步：① 內文有 <a class="term" href="#glossary">底線加問號</a> 的詞是專有名詞，點了跳到最下面的小辭典。② 每張截圖左邊綠色的 <span class="t" style="font-size:.7rem">▶ 時間</span> 可以點，會直接跳到 YouTube 影片那一段，方便你想細看時自己去看。</p>
</section>

<section id="what">
<h2>🤔 這到底在做什麼？（用生活例子講）</h2>
<p>假設你家裡有一個很聰明的小幫手（就是那個 {T('agent')}），它平常只待在你的電腦裡。你不在電腦前的時候，就沒辦法叫它做事，很可惜。</p>
<p>這支影片就是要把這個小幫手，接到大家每天都在用的 <b>LINE</b> 上面。接好以後，你走到哪裡，只要打開手機的 LINE 打幾個字，它就會在背後幫你做事，再把結果傳回你的 LINE。就像有個小秘書一直跟在你身邊。</p>
<div class="tbl-wrap">{fig(6,"整件事的地圖：① 去 LINE 網站拿鑰匙 → ② 幫電腦開一條路 → ③ 把鑰匙填進 AI 設定 → ④ 用手機測試","0:50")}</div>
<p class="quote">🎯 <b>為什麼要這樣做？</b>影片說：「你不可能隨時盯著電腦，但 LINE 是我們每天都在用、幾乎人手一個的東西。如果 AI 能直接在 LINE 裡回你，那就完全不一樣了。」</p>
</section>

<section id="s1">
<h2>1️⃣ 第一步：去拿兩把鑰匙（0:53–5:07）</h2>
<p>要讓程式跟 LINE 講話，得先去 {T('line-dev')} 這個官方網站報到，最後拿到<b>兩把很重要的鑰匙</b>。過程有點像去辦一張新的 LINE 官方帳號：</p>
<div class="step">
<p>① 先建一個 {T('provider','Provider')}（你的開發者身分），影片取名叫「HermesBot」。<br>
② 在底下再開一條 {T('msgapi','Messaging API')} 類型的 {T('channel','專線')}。<br>
③ 過程中系統會順便幫你開一個 LINE 官方帳號（名字隨便取、種類選「軟體／網路」那類、不用申請認證）。</p>
</div>
{grid(fig(11,"在 LINE 官網建立一個叫 HermesBot 的「開發者身分」","1:40"),
      fig(20,"重要：先把 LINE 內建的「歡迎訊息」和「自動回應」關掉，不然會跟 AI 搶著回話","3:10"))}
<p>接著就是拿鑰匙。<b>第一把鑰匙</b>叫 {T('secret','Channel Secret')}（一串 32 個字的密碼），<b>第二把鑰匙</b>叫 {T('token','Channel Access Token')}（一串很長的字），要按一下「Issue（生成）」按鈕才會出現。</p>
{fig(29,"按下 Issue，生出第二把鑰匙 Channel Access Token（綠色框框處）","4:40")}
<p class="note">🔒 <b>老師特別叮嚀</b>：這兩把鑰匙就等於你的帳號密碼，一定要複製到安全的地方，<b>絕對不要讓它出現在公開的影片或截圖裡</b>。（連老師自己錄影時都把鑰匙打上馬賽克。）</p>
</section>

<section id="s2">
<h2>2️⃣ 第二步：幫電腦開一條「外面進得來的路」（5:07–6:40）</h2>
<p>這一步的觀念最重要，我用門鈴來比喻。</p>
<p>當有人在 LINE 傳訊息給你，LINE 會想辦法「<b>按你電腦的門鈴</b>」，通知它有新訊息——這個門鈴機制就叫 {T('webhook','Webhook')}。可是問題來了：你的 AI 小幫手住在你家電腦裡，<b>外面的人根本不知道你家在哪、按不到門鈴</b>。</p>
<p>所以要用一個工具 {T('ngrok','ngrok')}，幫你家裝一條「臨時的公開門牌（一個 {T('https','HTTPS 網址')}）」，這樣 LINE 才找得到你、按得到門鈴。</p>
{grid(fig(31,"第二步的主題：幫電腦弄一個外面連得到的公開網址","5:00"),
      fig(38,"實際做法：① 打一行指令 ngrok http 8646 ② 把跑出來的網址貼到 LINE ③ 網址最後面要加上 /line/webhook","6:10"))}
<p>做法很簡單，打開終端機打一行字：<code>ngrok http 8646</code>（{T('port','8646')} 是這個 AI 用的門號）。它會給你一個 <code>https://xxxxx.ngrok-free.app</code> 的網址。<b>最關鍵的小地方：把這個網址貼到 LINE 的時候，結尾一定要加上 <code>/line/webhook</code>。</b></p>
</section>

<section id="s3">
<h2>3️⃣ 第三步：把鑰匙填進 AI 的設定裡（6:40–8:07）</h2>
<p>現在回到 AI 小幫手（Hermes）的畫面，把剛剛拿到的東西填進去。它內建就支援 LINE，不用另外裝東西。要填三格：</p>
<div class="step">
<p>• <b>第二把鑰匙</b>（{T('token','Channel Access Token')}）<br>
• <b>第一把鑰匙</b>（{T('secret','Channel Secret')}）<br>
• <b>准許名單</b>（{T('allowed','Allowed IDs')}）← 這格最多人忘記！</p>
</div>
{grid(fig(46,"在 AI 的設定頁，把兩把鑰匙和「准許名單」填進去","7:30"),
      fig(51,"填完存檔、把 AI 的大門重開一次，回 LINE 按驗證——這次成功了（變綠色）","8:20"))}
<p class="note">⚠️ <b>最容易踩的雷</b>：那個「准許名單」({T('allowed','Allowed IDs')}) 如果空著不填，<b>就算你把 AI 加成好友，它也不會理你</b>。要把你自己的 {T('userid','LINE User ID')}（你的 LINE 專屬編號）填進去。填完存檔後，還要下指令把 {T('gateway','Hermes 的大門')} 重開一次，再回 LINE 後台按 {T('verify','Verify（驗證）')} 就會成功。</p>
</section>

<section id="s4">
<h2>4️⃣ 第四步：拿手機來玩玩看（8:07–13:50）</h2>
<p>用手機掃 QR Code 或搜尋，把這個官方帳號加成好友，傳一句話試試。<b>如果它沒回，先別緊張</b>——最常見的原因是後台有一個 <b>「Use Webhook（使用門鈴）」的開關忘了打開</b>（它預設是關的）。打開後再傳，它就會乖乖回你了。</p>
{grid(fig(56,"成功了！左邊是手機的 LINE，右邊是 AI 的畫面。你在 LINE 說話，AI 在背後想，再把答案傳回你的 LINE","9:10"),
      fig(61,"很實用的例子：在 LINE 問「現在西太平洋有颱風嗎？」，AI 不是隨便亂答，而是自己上網查最新資料再回你","10:00"))}
<p>還有更好玩的：老師在 AI 裡裝了一個「畫四格漫畫」的 {T('skill','技能')}。你只要在 LINE 打字說想要什麼（例如「說一個關於職場的笑話」），AI 就會先想好每一格要畫什麼，再用會畫圖的 {T('gptimg','GPT Image 2')} 一格一格畫出來，最後拼成一張四格漫畫傳回 LINE 給你。</p>
{grid(fig(73,"在 LINE 打一句話，AI 就規劃劇情、畫出一整張「職場笑話」四格漫畫","12:00"),
      fig(85,"整個流程的總覽圖：拿鑰匙 → 開通道 → 填設定 → 手機使用","14:00"))}
<p class="note">🖼️ <b>小提醒</b>：如果你要讓 AI 傳「圖片」回 LINE，還要多填一格叫 LINE Public URL 的欄位，一樣把 ngrok 那個網址填進去（但這次結尾<b>不要</b>加 /line/webhook，只填最前面的部分）。不然圖會傳不出來。</p>
</section>

<section id="keys">
<h2>⚠️ 三個最常卡住的地方（照做就不會錯）</h2>
{fig(87,"老師最後整理的重點：這三件事確認好，基本上就不會有問題","14:20")}
<div class="tbl-wrap"><table>
<tr><th style="width:150px">容易出錯的地方</th><th>正確做法（白話）</th></tr>
<tr><td>① 網址結尾</td><td>那個公開網址的<b>最後面要加 <code>/line/webhook</code></b>，忘了加就連不上。</td></tr>
<tr><td>② 門鈴開關</td><td>後台的 <b>「Use Webhook」開關要打開</b>（預設是關的），不開 LINE 不會通知 AI。</td></tr>
<tr><td>③ 准許名單</td><td>要把<b>你自己的 LINE 編號填進准許名單</b>，不然加了好友它也不理你。</td></tr>
<tr><td>④（有圖片才要）</td><td>要傳圖回 LINE，記得多填一格 LINE Public URL。</td></tr>
</table></div>
<p class="quote">🌟 <b>這個 AI 跟一般聊天 AI（像 ChatGPT）差在哪？</b>影片結尾說：一般聊天 AI 很強，但每次聊天都是<b>從頭開始，不會記得你</b>。這個 Hermes 不一樣的兩點是——① 它能把你教它的做法<b>存成一項{T('skill','技能')}</b>，下次直接用；② 它會<b>越用越懂你</b>，每次你給的回饋都變成它下次做更好的養分。這才像真正的私人秘書。</p>
</section>

<section id="glossary">
<h2>📖 專有名詞小辭典（看不懂的詞來這裡查）</h2>
<p class="small">內文有底線加問號的詞，點了就會跳到這裡對應那一列。</p>
<div class="tbl-wrap"><table>
<tr><th style="width:210px">專有名詞</th><th>白話解釋</th></tr>
{glossary_rows}
</table></div>
</section>

<footer>
<p><b>這份報告怎麼來的</b>：用程式自動下載這支 YouTube 影片和它的繁體中文字幕，每 10 秒截一張畫面（總共 95 張），再由 AI 把畫面和字幕對在一起，挑出重點、改寫成白話，做成這一頁。影片裡的鑰匙等機密資料，原片就已經打上馬賽克。</p>
<p>閱讀日期 {READ_DATE}｜這是「影片 → 白話圖文報告」自動化工具的範本成品。</p>
</footer>
</div></body></html>"""

OUTDIR.mkdir(parents=True, exist_ok=True)
OUT.write_text(DOC, encoding="utf-8")
print(f"✅ 白話版報告產出: {OUT}")
print(f"   大小: {OUT.stat().st_size/1024/1024:.2f} MB｜辭典詞條: {len(GLOSSARY)} 個｜可點時間戳: 已啟用")
