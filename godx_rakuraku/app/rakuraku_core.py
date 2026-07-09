#!/usr/bin/env python3
# ============================================================================
# rakuraku_core.py  --  「楽々データ共有」/ "Rakuraku Data Share" 共通コア
#                       GO DX Corporation (架空ベンダー / fictional vendor)
#
#   演習用DXツール「楽々データ共有」の本体。GUI(Tkinter)と、SCADA(FUXA)から
#   操業データを *読み取り専用* で取得するクライアントをまとめたモジュール。
#   日本語版 rakuraku_share_ja.py / 英語版 rakuraku_share_en.py から
#   言語リソース(STRINGS)を渡して起動する。
#
#   通信は scada_read.py と同じ構造:
#     ・タグ検出 : GET /api/project
#     ・現在値   : GET /api/getTagValue?ids=[...]
#   Python 3 標準ライブラリのみ(pip 不要 / tkinter 同梱)。
#
#   ※ GO DX / 楽々データ共有 はサイバーセキュリティ教育・防御演習のための
#     架空のベンダー・製品です。教育・防御演習専用。
#     Fictional vendor/product for education & defensive training only.
# ============================================================================
import argparse
import json
import math
import threading
import urllib.request
import urllib.parse
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox

DEFAULT_HOST = "192.168.111.11:1881"   # SCADA PC 上の FUXA / FUXA on the SCADA PC

# --- ブランドカラー / brand palette ------------------------------------------
BRAND1 = "#00b8d4"
BRAND2 = "#0091ea"
BRAND3 = "#3949ab"
INK    = "#12203a"
BG     = "#f5f8fc"
LINE   = "#d7e0ee"

# 監視対象の行定義 / monitored rows.  各行の tag_keys は FUXA タグ名の候補
# (大文字小文字を無視して部分一致で探す)。実機のタグ名に合わせて調整可。
ROWS = [
    {"tag_keys": ["SV", "SP"],  "id": None},   # 温度制御SV / Temp Ctrl SV (setpoint)
    {"tag_keys": ["PV"],        "id": None},   # 温度制御PV / Temp Ctrl PV (process value)
    {"tag_keys": ["OUT", "MV"], "id": None},   # 温度制御OUT / Temp Ctrl OUT (output)
]


# ---------------------------------------------------------------------------
# FUXA 読み取りクライアント / read-only client (scada_read.py と同構造)
# ---------------------------------------------------------------------------
class FuxaClient:
    def __init__(self, host):
        self.host = host

    def _get(self, path, query=None, timeout=5):
        url = "http://%s%s" % (self.host, path)
        if query is not None:
            url += "?" + urllib.parse.urlencode(query)
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))

    def discover_tags(self):
        """FUXA プロジェクトから (tagId, tagName) を自動検出。"""
        prj = self._get("/api/project")
        out = []
        for dev in (prj.get("devices") or {}).values():
            for tid, t in (dev.get("tags") or {}).items():
                out.append((tid, t.get("name") or tid))
        return out

    def get_current(self, ids):
        q = {"ids": json.dumps(ids)}
        rows = self._get("/api/getTagValue", q)   # [{id,value,ts}]
        return {r["id"]: r for r in rows}


def resolve_row_ids(client, rows):
    """検出タグ名から各行の tagId を解決。見つからない行は id=None のまま。"""
    tags = client.discover_tags()
    for row in rows:
        row["id"] = None
        for tid, name in tags:
            up = (name or "").upper()
            if any(k in up for k in row["tag_keys"]):
                row["id"] = tid
                break
    return rows


def demo_values(tick):
    """サーバ未接続時のデモ値 / plausible values when no server is reachable."""
    pv = 39.8 + 0.4 * math.sin(tick / 3.0)
    out = 32.5 + 3.0 * math.sin(tick / 3.0 + 1.0)
    return ["40.0", "%.1f" % pv, "%.1f" % out]


# ---------------------------------------------------------------------------
# GUI アプリ / product-style Tkinter application
# ---------------------------------------------------------------------------
class RakurakuApp:
    def __init__(self, root, s, host, demo=False):
        self.root = root
        self.s = s                    # 言語リソース / string resources
        self.demo = demo
        self.tick = 0
        self.host_var = tk.StringVar(value=host)

        root.title(s["title"])
        root.configure(bg=BG)
        root.geometry("800x560")
        root.minsize(720, 520)

        self._build_header()
        self._build_toolbar()
        self._build_table()
        self._build_statusbar()

    # --- ヘッダ(ロゴ＋製品名) / branded header ------------------------------
    def _build_header(self):
        head = tk.Frame(self.root, bg=BRAND3, height=88)
        head.pack(fill="x")
        head.pack_propagate(False)

        # GO DX ロゴを Canvas で描画 / draw the GO DX logo (stdlib only)
        logo = tk.Canvas(head, width=218, height=88, bg=BRAND3, highlightthickness=0)
        logo.pack(side="left", padx=(18, 0))
        # ロゴバッジ / badge
        logo.create_rectangle(12, 22, 60, 70, fill=BRAND2, outline="")
        for i, off in enumerate((0, 14)):
            col = "#18ffb0" if i == 0 else "#7ff0d8"
            logo.create_line(22 + off, 32, 34 + off, 46, 22 + off, 60,
                             fill=col, width=5, capstyle="round", joinstyle="round")
        logo.create_text(74, 37, text="GO DX", anchor="w", fill="white",
                         font=("Segoe UI", 19, "bold"))
        logo.create_text(75, 61, text="DIGITAL TRANSFORMATION", anchor="w",
                         fill="#c5cae9", font=("Segoe UI", 6, "bold"))

        # 区切り線 / divider between logo and product name
        tk.Frame(head, bg="#5c6bc0", width=1).pack(side="left", fill="y", pady=20)

        # 製品名 / product name
        titlebox = tk.Frame(head, bg=BRAND3)
        titlebox.pack(side="left", padx=16)
        tk.Label(titlebox, text=self.s["product"], bg=BRAND3, fg="white",
                 font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(titlebox, text=self.s["tagline"], bg=BRAND3, fg="#c5cae9",
                 font=("Segoe UI", 10)).pack(anchor="w")

        tk.Label(head, text=self.s["provided"], bg=BRAND3, fg="#9fa8da",
                 font=("Segoe UI", 9)).pack(side="right", padx=18)

    # --- ツールバー(接続先＋GET) / toolbar --------------------------------
    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=18, pady=(16, 8))

        tk.Label(bar, text=self.s["host"], bg=BG, fg=INK,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Entry(bar, textvariable=self.host_var, width=22,
                 font=("Consolas", 11)).pack(side="left", padx=(8, 16))

        self.get_btn = tk.Button(bar, text=self.s["get"], command=self.on_get,
                                 bg=BRAND2, fg="white", activebackground=BRAND3,
                                 activeforeground="white", relief="flat",
                                 font=("Segoe UI", 11, "bold"), padx=22, pady=6,
                                 cursor="hand2")
        self.get_btn.pack(side="left")

        if self.demo:
            tk.Label(bar, text=self.s["demo_badge"], bg="#fff8e1", fg="#7a5b00",
                     font=("Segoe UI", 9, "bold"), padx=8, pady=2).pack(side="right")

    # --- 監視テーブル / monitoring table -----------------------------------
    def _build_table(self):
        wrap = tk.Frame(self.root, bg="white", highlightbackground=LINE,
                        highlightthickness=1)
        wrap.pack(fill="both", expand=True, padx=18, pady=8)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("RK.Treeview", font=("Segoe UI", 11), rowheight=34,
                        fieldbackground="white", background="white")
        style.configure("RK.Treeview.Heading", font=("Segoe UI", 10, "bold"),
                        background="#eef3fb", foreground="#33456b")

        cols = ("factory", "line", "device", "tag", "value")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings",
                                 style="RK.Treeview", height=3)
        headers = self.s["columns"]
        widths = (110, 100, 100, 150, 110)
        anchors = ("center", "center", "center", "w", "e")
        for c, h, w, a in zip(cols, headers, widths, anchors):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor=a, stretch=True)

        # 3行を初期化 / seed the three rows
        r = self.s["rows"]
        self.iids = []
        for i in range(3):
            iid = self.tree.insert("", "end", values=(
                r["factory"], r["line"], r["device"], r["tags"][i], "—"))
            self.iids.append(iid)
        self.tree.tag_configure("val", font=("Consolas", 12, "bold"))
        self.tree.pack(fill="both", expand=True, padx=1, pady=1)

    # --- ステータスバー / status bar ---------------------------------------
    def _build_statusbar(self):
        self.status = tk.StringVar(value=self.s["ready"])
        bar = tk.Frame(self.root, bg="#eef1f6")
        bar.pack(fill="x", side="bottom")
        tk.Label(bar, textvariable=self.status, bg="#eef1f6", fg="#5b6b86",
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=14, pady=5)

    # --- GET 処理 / read handler (worker thread) ---------------------------
    def on_get(self):
        self.get_btn.config(state="disabled")
        self.status.set(self.s["reading"])
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self):
        host = self.host_var.get().strip() or DEFAULT_HOST
        self.tick += 1
        try:
            if self.demo:
                raise ConnectionError("demo mode")
            client = FuxaClient(host)
            resolve_row_ids(client, ROWS)
            ids = [r["id"] for r in ROWS if r["id"]]
            if not ids:
                raise LookupError(self.s["no_tags"])
            cur = client.get_current(ids)
            values = []
            for r in ROWS:
                v = cur.get(r["id"], {}).get("value") if r["id"] else None
                values.append("—" if v is None else str(v))
            self.root.after(0, self._apply_values, values, host, False, None)
        except Exception as e:
            # 未接続・デモ時はデモ値を表示 / fall back to demo values
            values = demo_values(self.tick)
            self.root.after(0, self._apply_values, values, host, True, str(e))

    def _apply_values(self, values, host, is_demo, err):
        for iid, v in zip(self.iids, values):
            vals = list(self.tree.item(iid, "values"))
            vals[4] = v
            self.tree.item(iid, values=vals, tags=("val",))
        stamp = datetime.now().strftime("%H:%M:%S")
        if is_demo:
            self.status.set(self.s["status_demo"].format(host=host, time=stamp))
        else:
            self.status.set(self.s["status_ok"].format(host=host, time=stamp))
        self.get_btn.config(state="normal")


def run(strings):
    """言語リソースを受け取ってアプリを起動 / entry point given a strings dict."""
    ap = argparse.ArgumentParser(description=strings["title"])
    ap.add_argument("--host", default=DEFAULT_HOST,
                    help="FUXA host:port (default %s)" % DEFAULT_HOST)
    ap.add_argument("--demo", action="store_true",
                    help="デモ値で動作 / run with simulated demo values")
    args = ap.parse_args()

    root = tk.Tk()
    RakurakuApp(root, strings, host=args.host, demo=args.demo)
    root.mainloop()
