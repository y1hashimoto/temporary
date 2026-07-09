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

## 4. 演習での位置づけ（検討メモ）/ Role in the exercise (discussion notes)

- **信頼の悪用 / Abuse of trust:** 攻撃はGO DXという「見慣れたベンダー」への信頼を突く。日常的に本物のツールを
  使っているほど、偽パッチメールに引っかかりやすい。
- **正規と偽物の対比 / Genuine vs fake:** この正規サイト（`web/`）と、別素材のフィッシングページ／メールを
  並べて見せると、受講者に「本物そっくりの偽物」の怖さを実感させられる。
- **防御の学び / Defensive takeaway:** ベンダー連絡の正当性確認、ソフト更新の正規経路、
  端末でのコマンド実行に対する警戒——を議論する導入に使える。

*(このメモは演習ファシリテーター向けの検討たたき台です。)*
