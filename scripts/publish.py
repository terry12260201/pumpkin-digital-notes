#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一篇報告 HTML 發佈到 GitHub Pages 分享庫：複製→更新 manifest→重建首頁→commit push。

用法：
  python3 publish.py \
    --html "/path/報告.html" \
    --category gaiconf-2026 \
    --slug limuyue-46-to-90 \
    --title "從 46 分寫到 90 分 — AI 代理人寫作" \
    --speaker "李慕約" --source gaiconf --duration 20:02 --date 2026-08-18 \
    --summary "把請 AI 寫文章做成流水線…"

分類若不存在會自動新增（需另給 --cat-name / --cat-emoji / --cat-desc）。
發佈後印出線上網址。
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

REPO = Path.home() / "pumpkin-digital-notes"
PAGES = "https://terry12260201.github.io/pumpkin-digital-notes/"

def sh(cmd, cwd=REPO):
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--category", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--speaker", default="")
    ap.add_argument("--source", default="")
    ap.add_argument("--duration", default="")
    ap.add_argument("--date", required=True)
    ap.add_argument("--summary", default="")
    ap.add_argument("--cat-name", default="")
    ap.add_argument("--cat-emoji", default="🗂️")
    ap.add_argument("--cat-desc", default="")
    a = ap.parse_args()

    if not REPO.exists():
        sys.exit(f"❌ 找不到分享庫 {REPO}，請先 git clone。")

    manifest = REPO / "reports.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))

    # 分類：不存在就新增
    if not any(c["id"] == a.category for c in data["categories"]):
        if not a.cat_name:
            sys.exit(f"❌ 分類 {a.category} 不存在，請給 --cat-name（和可選 --cat-emoji/--cat-desc）")
        data["categories"].append({"id": a.category, "name": a.cat_name,
                                    "emoji": a.cat_emoji, "desc": a.cat_desc})

    # 複製 HTML
    dest_rel = f"{a.category}/{a.slug}.html"
    dest = REPO / dest_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(a.html, dest)

    # 更新 manifest（同 file 就覆蓋那筆）
    data["reports"] = [r for r in data["reports"] if r.get("file") != dest_rel]
    data["reports"].append({
        "category": a.category, "file": dest_rel, "title": a.title,
        "speaker": a.speaker, "source": a.source, "duration": a.duration,
        "date": a.date, "summary": a.summary,
    })
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # 重建首頁
    sh(["python3", "build_hub.py"])

    # commit + push
    sh(["git", "add", "-A"])
    sh(["git", "-c", "user.name=terry12260201", "-c", "user.email=terry12260201@hotmail.com",
        "commit", "-m", f"新增報告：{a.title}"])
    sh(["git", "push"])

    url = PAGES + dest_rel
    print("✅ 已發佈")
    print("🌐 線上網址:", url)
    print("🏠 分享首頁:", PAGES)

if __name__ == "__main__":
    main()
