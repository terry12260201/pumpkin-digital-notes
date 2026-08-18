#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YT 圖文報告生產線 — 前段（下載 → 抽格 → 縮圖總表 → 字幕整理）
給 Claude 讀 frames/ 與 subs.txt 後，寫出圖文報告 HTML。

用法：
  python3 yt_report_prep.py "<YouTube 連結或本地影片路徑>" [每幾秒抽一張,預設10]
"""
import sys, os, re, json, subprocess, glob, shutil
from pathlib import Path

def run(cmd, **kw):
    print("→", " ".join(str(c) for c in cmd))
    kw.setdefault("check", True)
    return subprocess.run(cmd, **kw)

def sh(cmd):
    return subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True).stdout

def main():
    if len(sys.argv) < 2:
        sys.exit("用法: python3 yt_report_prep.py <YT連結或影片路徑> [抽格秒數]")
    src = sys.argv[1]
    step = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    work = Path(__file__).parent / "yt_job"
    frames = work / "frames"
    if frames.exists():
        shutil.rmtree(frames)
    frames.mkdir(parents=True)

    is_url = src.startswith("http")
    already = list(work.glob("video.mp4"))

    # ---- 1. 取得影片 + 官方字幕 ----
    if is_url:
        print("\n=== 1. yt-dlp 下載影片 + 官方字幕 ===")
        # 影片（限制 1080p 以內，省空間）
        if already:
            print("影片已存在，略過下載:", already[0].name)
        else:
            run(["yt-dlp", "-f", "bv*[height<=1080]+ba/b[height<=1080]/b",
                 "--merge-output-format", "mp4",
                 "-o", str(work / "video.%(ext)s"), src])
        # 字幕：優先繁中→中→英，人工字幕優先，退回自動字幕
        run(["yt-dlp", "--skip-download",
             "--write-subs", "--write-auto-subs",
             "--sub-langs", "zh-Hant,zh-TW,zh,zh-Hans,en.*",
             "--sub-format", "vtt",
             "-o", str(work / "video.%(ext)s"), src], check=False)
        # 影片標題/上傳日等 metadata
        info = sh(f'yt-dlp --skip-download --print "%(title)s|||%(uploader)s|||%(duration)s|||%(upload_date)s|||%(webpage_url)s" {json.dumps(src)}').strip()
        (work / "meta.txt").write_text(info, encoding="utf-8")
        print("影片資訊:", info)
    else:
        p = Path(src).expanduser()
        if not p.exists():
            sys.exit(f"找不到檔案: {p}")
        shutil.copy(p, work / ("video" + p.suffix))

    video = next(iter(glob.glob(str(work / "video.*"))
                      and [f for f in glob.glob(str(work / "video.*"))
                           if Path(f).suffix.lower() in (".mp4", ".mkv", ".webm", ".mov")]),
                 None)
    if not video:
        sys.exit("下載後找不到影片檔")
    video = Path(video)

    # ---- 2. ffprobe 讀時長/解析度 ----
    print("\n=== 2. ffprobe 讀 metadata ===")
    probe = json.loads(sh(f'ffprobe -v quiet -print_format json -show_format -show_streams {json.dumps(str(video))}'))
    dur = float(probe["format"]["duration"])
    vstream = next(s for s in probe["streams"] if s["codec_type"] == "video")
    w, h = vstream["width"], vstream["height"]
    print(f"時長 {dur/60:.1f} 分鐘, 解析度 {w}x{h}")

    # ---- 3. ffmpeg 抽格（每 step 秒一張）----
    print(f"\n=== 3. ffmpeg 抽格（每 {step} 秒一張）===")
    run(["ffmpeg", "-y", "-i", str(video),
         "-vf", f"fps=1/{step},scale=1280:-2", "-q:v", "5",
         str(frames / "f_%04d.jpg")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    imgs = sorted(frames.glob("f_*.jpg"))
    print(f"共抽出 {len(imgs)} 張畫面")

    # 幀號 N 的時間 = (N-1)*step 秒
    def ts(n):
        s = (n - 1) * step
        return f"{s//3600:d}:{(s%3600)//60:02d}:{s%60:02d}" if s >= 3600 else f"{(s%3600)//60:d}:{s%60:02d}"

    # ---- 4. PIL 縮圖總表（5×6 一頁）----
    print("\n=== 4. PIL 縮圖總表 ===")
    from PIL import Image, ImageDraw, ImageFont
    cols, rows = 5, 6
    per = cols * rows
    tw, th = 320, 180
    pad, lab = 8, 22
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
    sheets = []
    for pg in range((len(imgs) + per - 1) // per):
        sheet = Image.new("RGB", (cols*(tw+pad)+pad, rows*(th+lab+pad)+pad), "#101010")
        d = ImageDraw.Draw(sheet)
        for i in range(per):
            idx = pg*per + i
            if idx >= len(imgs):
                break
            n = idx + 1
            im = Image.open(imgs[idx]).resize((tw, th))
            cx = pad + (i % cols)*(tw+pad)
            cy = pad + (i // cols)*(th+lab+pad)
            sheet.paste(im, (cx, cy))
            d.text((cx+3, cy+th+3), f"#{n:03d}  {ts(n)}", fill="#7fe0d0", font=font)
        out = work / f"contact_{pg+1:02d}.jpg"
        sheet.save(out, quality=80)
        sheets.append(out)
    print(f"縮圖總表 {len(sheets)} 頁:", *[s.name for s in sheets])

    # ---- 5. 整理字幕成帶時間戳的純文字 ----
    print("\n=== 5. 整理字幕 ===")
    vtts = sorted(work.glob("*.vtt"))
    subs_txt = work / "subs.txt"
    if vtts:
        vtt = vtts[0]
        lines, seen = [], set()
        cur_t = None
        for ln in vtt.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = re.match(r"(\d+):(\d+):(\d+)\.\d+\s*-->", ln)
            if m:
                hh, mm, ss = map(int, m.groups())
                total = hh*3600+mm*60+ss
                cur_t = f"{hh}:{mm:02d}:{ss:02d}" if hh else f"{mm}:{ss:02d}"
            elif ln.strip() and not ln.startswith(("WEBVTT", "Kind:", "Language:")) and "-->" not in ln:
                txt = re.sub(r"<[^>]+>", "", ln).strip()
                if txt and txt not in seen:
                    seen.add(txt)
                    lines.append(f"[{cur_t}] {txt}" if cur_t else txt)
        subs_txt.write_text("\n".join(lines), encoding="utf-8")
        print(f"字幕來源: {vtt.name}，共 {len(lines)} 段")
    else:
        subs_txt.write_text("(此影片無官方字幕，需 Whisper 或純看畫面)", encoding="utf-8")
        print("⚠️ 無官方字幕")

    # ---- 摘要給 Claude ----
    print("\n" + "="*50)
    print("✅ 前段完成，產物在:", work)
    print(f"  - 影片: {video.name}  ({dur/60:.1f} 分, {w}x{h})")
    print(f"  - 截圖: {len(imgs)} 張  (frames/)")
    print(f"  - 縮圖總表: {len(sheets)} 頁  (contact_XX.jpg)")
    print(f"  - 字幕: subs.txt")
    print("下一步：Claude 讀 contact_XX.jpg 定位重點 → 讀個別 frames + subs.txt → 寫圖文報告 HTML")

if __name__ == "__main__":
    main()
