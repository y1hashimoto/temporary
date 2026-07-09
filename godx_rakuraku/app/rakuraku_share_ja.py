#!/usr/bin/env python3
# ============================================================================
# rakuraku_share_ja.py  --  「楽々データ共有」日本語版 / Japanese edition
#   GO DX Corporation（架空ベンダー / fictional vendor）
#
#   起動 / Run:
#     python3 rakuraku_share_ja.py                 実機(FUXA)へ接続
#     python3 rakuraku_share_ja.py --demo          デモ値で動作
#     python3 rakuraku_share_ja.py --host 192.168.111.11:1881
#
#   ※ 教育・防御演習専用の架空製品です。
# ============================================================================
import rakuraku_core

STRINGS_JA = {
    "title":     "楽々データ共有 — GO DX",
    "product":   "楽々 データ共有",
    "tagline":   "操業データ共有ツール",
    "provided":  "provided by GO DX",
    "host":      "接続先(SCADA)：",
    "get":       "GET  現在値を取得",
    "demo_badge": "DEMO モード",
    "columns":   ("工場", "ライン", "装置", "タグ", "値"),
    "rows": {
        "factory": "工場A",
        "line":    "ラインB",
        "device":  "装置C",
        "tags":    ("温度制御SV", "温度制御PV", "温度制御OUT"),
    },
    "ready":       "準備完了。GETボタンで現在値を取得します。",
    "reading":     "取得中…",
    "no_tags":     "対象タグが見つかりません",
    "status_ok":   "取得成功  {host}  @ {time}",
    "status_demo": "デモ値を表示中（{host} に接続できません）  @ {time}",
}

if __name__ == "__main__":
    rakuraku_core.run(STRINGS_JA)
