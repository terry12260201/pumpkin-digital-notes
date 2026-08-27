# CLAUDE.md — pumpkin-digital-notes（小南瓜數位筆記 · 發佈站）

## 這是什麼
「小南瓜數位筆記」的**線上分享空間**：影片變成國小生也讀得懂的白話圖文報告，發佈到 GitHub Pages。

**這裡是產出的落地站，不是方法。** 方法（怎麼做報告）在 skill：`/pumpkin-digital-notes`。
操作手冊：`小南瓜數位筆記_完整操作手冊.md`（給 Ann 也能照著跑的版本）。

## ⚠️ 鐵則

1. **截圖 = 重點錨點**。每張截圖要配「重點 + 可點的時間戳 + 名詞辭典」，不是隨便配圖。
2. **雙版本輸出**：HTML 圖文報告（這裡）＋ Obsidian 筆記（落 `Terry 知識庫系統/影片筆記/<平台夾>/`）。兩邊都要有。
3. **公開 repo 但 unlisted**：`terry12260201/pumpkin-digital-notes`。內容是個人學習用途，**連結不要公開張貼**，README 要保留這句警語。
4. 別跟隔壁搞混：
   - `~/xiaomi-digital-notes` = 小秘數位筆記（**祥成行／Ann 的內容**），同方法換品牌配色
   - 只要純文字重點、不需截圖也不需分享網址 → 改用 skill `/yt-digest`（小玉米，靠字幕更省 token）

## 結構
```
index.html        分類索引首頁（GitHub Pages）
reports.json      報告清單資料
build_hub.py      重建首頁索引
scripts/          處理腳本
youtube/          YouTube 來源報告
gaiconf-2026/     需登入平台的報告
assets/
```

## 常見任務
新增一份報告 → 放進對應平台夾 → 更新 `reports.json` → 跑 `build_hub.py` 重建索引 → commit push

## 驗收
1. **雙擊 `index.html` 用 `file://` 直開**，確認索引與新報告都開得起來、截圖與時間戳連結可點
2. push 後開 GitHub Pages 網址複驗一次
