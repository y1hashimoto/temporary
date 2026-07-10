# GO DX / 楽々データ共有（らくらくデータ共有） — 演習用ベンダー・製品一式
# GO DX / "Rakuraku Data Share" — Fictional vendor & product kit for the exercise

> ⚠️ **教育・防御演習専用 / For education & defensive training only.**
> 「GO DX株式会社」および製品「楽々データ共有 / Rakuraku Data Share」は、
> ペネトレーション演習を現実味のあるものにするために作られた **架空のベンダー・製品** です。
> 実在しません。悪用を目的としたものではありません。
> "GO DX Corporation" and the product "Rakuraku Data Share" are **fictitious**, created solely
> to make the penetration exercise believable. They do not exist and are not intended for misuse.

---

## 1. これは何か / What this is

名古屋NUC演習（サイバークライシス）の侵入シナリオで、**PC_A（業務革新／DX推進担当PC）が
日常的に使っている正規のDXツール**という「設定」を作り込むための素材一式です。

In the intrusion scenario, PC_A (the business-innovation / DX PC) routinely uses a **legitimate DX
tool** to read plant data from the SCADA (FUXA) server over HTTP. This kit builds out that
legitimate tool and its vendor so the later phishing lure (a fake "urgent patch from GO DX") is
convincing.

```
  正規の日常業務            →   フェイクメール（別素材）          →   攻撃ツール実行
  legitimate daily use          fake "GO DX security patch" mail        malware executed
  ┌───────────────┐            ┌───────────────┐                       ┌───────────────┐
  │ 楽々データ共有  │  ……偽装…▶ │「GO DXから緊急  │  ……騙されて…▶        │ reverse shell │
  │ (this kit)     │  spoofed   │  パッチ」メール │  tricked              │ to Kali       │
  └───────────────┘            └───────────────┘                       └───────────────┘
```

このツール自体は **読み取り専用** で無害です。攻撃はこのツールの脆弱性ではなく、
**ベンダーを騙るフィッシング** と **利用者がコマンドを実行してしまうこと** によって成立します。
The tool itself is **read-only and benign**. The compromise comes from **vendor-impersonation
phishing** and **the user running a command**, not from any flaw in this tool.

---

## 2. 中身 / Contents

| ファイル / File | 役割 / Role |
|---|---|
| `logo/godx_logo.svg` | GO DX 社ロゴ（前進を表すシェブロン＋ワードマーク） / GO DX logo (forward chevrons + wordmark) |
| `web/index_ja.html` | 製品紹介Webページ（日本語版） / product landing page (Japanese) |
| `web/index_en.html` | 製品紹介Webページ（英語版） / product landing page (English) |
| `app/rakuraku_core.py` | アプリ本体（GUI＋FUXA読み取りクライアント） / app core (GUI + FUXA read client) |
| `app/rakuraku_share_ja.py` | 「楽々データ共有」日本語版ランチャ / Japanese edition launcher |
| `app/rakuraku_share_en.py` | "Rakuraku Data Share" 英語版ランチャ / English edition launcher |
| `phishing/gmail_inbox_ja.html` | Gmail風メール閲覧画面（日本語版） / Gmail-style email view (Japanese) |
| `phishing/gmail_inbox_en.html` | Gmail風メール閲覧画面（英語版） / Gmail-style email view (English) |
| `phishing/godx_emergency_ja.html` | 偽パッチ着地ページ（日本語版） / fake-patch landing page (Japanese) |
| `phishing/godx_emergency_en.html` | 偽パッチ着地ページ（英語版） / fake-patch landing page (English) |

---

## 3. アプリの動作 / How the app works

製品風のGUI（Tkinter）に、GO DXロゴ・製品名「楽々 データ共有」・操業データ取得インターフェイスを表示します。
A product-style Tkinter GUI showing the GO DX logo, the product name, and an operational-data interface.

- 監視テーブルの列 / table columns: **工場 / ライン / 装置 / タグ / 値**（Factory / Line / Device / Tag / Value）
- 表示される3行 / the three rows: **工場A・ラインB・装置C** の **温度制御SV / 温度制御PV / 温度制御OUT**
- **GET** ボタンで、SCADA(FUXA)の無認証REST APIから現在値を取得し「値」列に表示します。
  The **GET** button reads current values from the FUXA REST API and fills the "Value" column.

通信構造は `scada_read.py` と同一です（`/api/project` でタグ検出 → `/api/getTagValue` で現在値）。
The comms follow the same structure as `scada_read.py` (`/api/project` to discover tags →
`/api/getTagValue` for current values).

### 実行 / Run

```bash
cd app

# 日本語版 / Japanese edition
python3 rakuraku_share_ja.py                       # 実機(FUXA)へ接続 / connect to live FUXA
python3 rakuraku_share_ja.py --host 192.168.111.11:1881
python3 rakuraku_share_ja.py --demo                # デモ値で動作（FUXA不要）/ demo values, no server

# 英語版 / English edition
python3 rakuraku_share_en.py
python3 rakuraku_share_en.py --demo
```

- 依存 / Dependencies: Python 3 標準ライブラリのみ（`tkinter` を含む）/ Python 3 standard library only (incl. `tkinter`).
- 接続先の既定値 / Default host: `192.168.111.11:1881`（演習本番のSCADA / the exercise-run SCADA）。
- FUXAに到達できない場合は自動的に **DEMOモード** の値を表示します（授業でサーバ無しでも画面を見せられる）。
  If FUXA is unreachable it automatically shows **DEMO mode** values so the screen is presentable without a server.

### タグ名の調整 / Adjusting tag names

各行は FUXA のタグ名を **部分一致（大文字小文字無視）** で探します（`rakuraku_core.py` の `ROWS`）。
実機のタグ名（例: `SV`/`SP`, `PV`, `OUT`/`MV`）に合わせてキーワードを編集してください。
Each row matches a FUXA tag by **case-insensitive substring** (see `ROWS` in `rakuraku_core.py`).
Edit the keywords to fit your controller's tag names.

---

## 4. フィッシング体験画面 / Phishing-experience screens

受講者が「ブラウザのGmailで実際にメールを読んでいる」感覚を得られるよう、Gmail風のメール閲覧画面を
再現しています。メール内の「修正パッチをダウンロード」リンクをクリックすると、GO DXブランドの
**偽パッチ着地ページ**（`godx_emergency_*.html`）が別タブで開きます。

A Gmail-style reading view so trainees feel they are reading the mail in a real browser. Clicking the
"Download patch" link in the message opens the GO DX-branded **fake-patch landing page**
(`godx_emergency_*.html`) in a new tab.

```
gmail_inbox_ja.html  ──(リンククリック / click link)──▶  godx_emergency_ja.html
gmail_inbox_en.html  ──(link click)───────────────────▶  godx_emergency_en.html
```

### 使い方 / Usage

- ブラウザで `phishing/gmail_inbox_ja.html`（または `_en.html`）を開くだけ。追加ソフト不要。
  Just open `phishing/gmail_inbox_ja.html` (or `_en.html`) in a browser. No extra software.
- **4ファイルは同じ `phishing/` フォルダに置いたまま**にしてください（相対リンクで着地ページを開くため）。
  Keep all four files together in `phishing/` (the landing page opens via a relative link).
- 着地ページのコマンド内ホスト（既定 `192.168.11.7:8888`）は、`godx_emergency_*.html` を編集して
  演習環境に合わせてください。Edit the host in the landing page's command to match your range.

> ⚠️ Gmailの見た目を模した**モックアップ**であり、Google／Gmail とは無関係です。本物のフィッシングでは
> なく、危険を安全に体験させるための教材です。A **mockup** imitating Gmail's look; unaffiliated with
> Google/Gmail. Not real phishing — training material to experience the lure safely.

---

## 5. 演習での位置づけ（検討メモ）/ Role in the exercise (discussion notes)

- **信頼の悪用 / Abuse of trust:** 攻撃はGO DXという「見慣れたベンダー」への信頼を突く。日常的に本物のツールを
  使っているほど、偽パッチメールに引っかかりやすい。
- **正規と偽物の対比 / Genuine vs fake:** この正規サイト（`web/`）と、別素材のフィッシングページ／メールを
  並べて見せると、受講者に「本物そっくりの偽物」の怖さを実感させられる。
- **防御の学び / Defensive takeaway:** ベンダー連絡の正当性確認、ソフト更新の正規経路、
  端末でのコマンド実行に対する警戒——を議論する導入に使える。

*(このメモは演習ファシリテーター向けの検討たたき台です。)*
