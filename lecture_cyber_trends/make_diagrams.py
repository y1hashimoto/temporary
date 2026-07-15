#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""講義スライド用の自作図解を生成する(テンプレート配色のフラットデザイン)。
出力先: assets/gen/*.png (200dpi)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Wedge, Polygon, Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "gen")
os.makedirs(OUT, exist_ok=True)

REG = fm.FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
BOLD = fm.FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")

NAVY = "#1F497D"       # テンプレートの見出し色
NAVY2 = "#3A6EA5"
NAVY3 = "#7A9CC6"
NAVY4 = "#B7C9E0"
NAVY_LT = "#E8EEF6"
INK = "#262626"
MUT = "#595959"
RED = "#B03A2E"        # 攻撃・危険(ステータス色)
RED_LT = "#F5E0DD"
GREEN = "#4E7A3A"      # 安全・拠り所(ステータス色)
GREEN_LT = "#E6EFDF"
GRAY = "#8C8C8C"
GRAY_LT = "#EFEFEF"


def dot(ax, fig, x, y, rx, fc):
    """横長figでも正円に見える点を描く(rxはx軸データ単位)。"""
    from matplotlib.patches import Ellipse
    w, h = fig.get_size_inches()
    ax.add_patch(Ellipse((x, y), 2 * rx, 2 * rx * w / h, fc=fc, ec="white", lw=1.2))

def fig_ax(w, h):
    fig = plt.figure(figsize=(w, h), dpi=200)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax

def t(ax, x, y, s, size=11, weight="reg", color=INK, ha="center", va="center", lh=1.25):
    ax.text(x, y, s, fontproperties=(BOLD if weight == "bold" else REG),
            fontsize=size, color=color, ha=ha, va=va, linespacing=lh)

def rbox(ax, x, y, w, h, fc, ec="none", lw=1.2, r=2.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, mutation_aspect=1))

def arrow(ax, x1, y1, x2, y2, color=NAVY, lw=2.2, style="-|>", ms=16):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=ms, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("saved", name)

# ------------------------------------------------------------------ S3 導入
def three_shifts():
    fig, ax = fig_ax(8.8, 2.0)
    items = [
        ("①", "攻撃の常態化・物理化", "ランサムウェアの操業影響\nOT・安全系への攻撃、戦争との融合"),
        ("②", "AIの参戦", "AIが攻撃を「自律実行」する時代へ\n(いわゆる “Mythos問題”)"),
        ("③", "量子の時限爆弾", "「今盗んで、後で復号」(HNDL)は\n既に始まっている"),
    ]
    for i, (num, title, sub) in enumerate(items):
        x = 1.5 + i * 33.2
        rbox(ax, x, 8, 30.5, 84, NAVY_LT)
        dot(ax, fig, x + 4.8, 72, 3.0, NAVY)
        t(ax, x + 4.8, 71.5, num, 12, "bold", "white")
        t(ax, x + 17.5, 72, title, 13, "bold", NAVY, ha="center")
        t(ax, x + 15.2, 34, sub, 10.5, "reg", INK, ha="center")
    save(fig, "three_shifts.png")

# ------------------------------------------------------------------ S4 時間配分
def agenda_time():
    fig, ax = fig_ax(8.8, 1.15)
    segs = [("導入", 5), ("第1章", 15), ("第2章 AI・Mythos", 25), ("第3章 量子", 15),
            ("第4章 規制", 10), ("第5章 対策", 7), ("まとめ", 3)]
    colors = [NAVY4, NAVY3, NAVY, NAVY2, NAVY3, NAVY2, NAVY4]
    x = 2.0
    total = 80.0
    for (label, minutes), c in zip(segs, colors):
        w = minutes / total * 96.0 - 0.6
        rbox(ax, x, 34, w, 40, c, r=1.5)
        tc = "white" if c in (NAVY, NAVY2, NAVY3) else INK
        if w > 4.5:
            t(ax, x + w / 2, 54, f"{minutes}分", 10.5, "bold", tc)
        else:
            t(ax, x + w / 2, 84, f"{minutes}分", 9, "bold", NAVY)
        t(ax, x + w / 2, 14, label, 9.5, "reg", MUT)
        x += w + 0.6
    t(ax, 2, 92, "80分の時間配分", 10, "bold", NAVY, ha="left")
    save(fig, "agenda_time.png")

# ------------------------------------------------------------------ S12 AI年表
def ai_timeline():
    fig, ax = fig_ax(8.8, 1.9)
    y = 42
    ax.plot([4, 96], [y, y], color=NAVY4, lw=3, solid_capstyle="round")
    arrow(ax, 90, y, 97, y, NAVY4, 3)
    nodes = [
        (10, "2022.11", "ChatGPT-3.5登場", "会話だけでプログラムも\nシナリオも作成", False),
        (35, "2023-25", "実用化・エージェント化", "コード生成・脆弱性解析が\n実用レベルに", True),
        (60, "2025.11", "初のAI実行型攻撃", "GTG-1002\n(次スライド)", False),
        (85, "2026", "“Mythos問題”", "東大入試にほぼ完答する水準\n脆弱性発見の桁が変わる", True),
    ]
    for x, date, title, sub, below in nodes:
        dot(ax, fig, x, y, 1.1, NAVY)
        if below:
            t(ax, x, y - 14, date, 10, "bold", NAVY)
            t(ax, x, y - 27, title, 10.5, "bold", INK)
            ty = y - 44
        else:
            t(ax, x, y + 16, date, 10, "bold", NAVY)
            t(ax, x, y + 29, title, 10.5, "bold", INK)
            ty = y + 46
        t(ax, x, ty, sub, 8.5, "reg", MUT)
    save(fig, "ai_timeline.png")

# ------------------------------------------------------------------ S13 GTG-1002
def gtg_flow():
    fig, ax = fig_ax(8.8, 1.8)
    boxes = [
        (2, 30, 18, "攻撃者\n(中国国家系グループ)", RED_LT, RED),
        (27, 30, 21, "タスクを無害な小片に分解\n(ジェイルブレイク)", GRAY_LT, INK),
        (55, 30, 20, "AIエージェント\n(Claude Code)", NAVY_LT, NAVY),
        (82, 30, 16, "世界約30組織\nへ侵入試行", RED_LT, RED),
    ]
    for x, y, w, label, fc, tc in boxes:
        rbox(ax, x, y, w, 42, fc)
        t(ax, x + w / 2, y + 21, label, 10, "bold", tc)
    for x1, x2 in [(20, 27), (48, 55), (75, 82)]:
        arrow(ax, x1 + 0.5, 51, x2 - 0.5, 51, NAVY)
    rbox(ax, 44, 80, 32, 17, RED, r=3)
    t(ax, 60, 88.5, "攻撃工程の 80〜90% をAIが自律実行", 10.5, "bold", "white")
    t(ax, 60, 12, "人間は指示と数カ所の判断のみ ― 攻撃の速度と数が「人間の頭数」の制約を離れた", 9.5, "reg", MUT)
    save(fig, "gtg_flow.png")

# ------------------------------------------------------------------ S14 Mythos統計
def mythos_stats():
    fig, ax = fig_ax(8.8, 1.75)
    tiles = [
        ("全主要OS・ブラウザ", "ゼロデイ脆弱性を発見\n(Windows/macOS/Linux/BSD)"),
        ("27年", "人間のレビューを生き延びた\nOpenBSDのバグを摘出"),
        ("72.4%", "発見した脆弱性を動作する\nエクスプロイトへ自動変換"),
        ("4連鎖", "脆弱性を連鎖させ\nサンドボックスを脱出"),
    ]
    for i, (num, label) in enumerate(tiles):
        x = 1.5 + i * 24.6
        rbox(ax, x, 6, 22.6, 88, NAVY_LT)
        t(ax, x + 11.3, 70, num, 15 if len(num) > 6 else 20, "bold", NAVY)
        t(ax, x + 11.3, 30, label, 8.8, "reg", INK)
    save(fig, "mythos_stats.png")

# ------------------------------------------------------------------ S15 サンドボックス脱出
def sandbox_escape():
    fig, ax = fig_ax(3.7, 3.5)
    # 上段: 脱出の模式図
    t(ax, 50, 96, "安全性テスト中の出来事", 10.5, "bold", INK)
    rbox(ax, 8, 56, 52, 32, GRAY_LT, ec=MUT, lw=1.4)
    t(ax, 34, 82, "隔離環境(サンドボックス)", 8.5, "reg", MUT)
    ax.add_patch(Circle((28, 69), 7, fc=NAVY, ec="none"))
    t(ax, 28, 68.5, "AI", 10, "bold", "white")
    arrow(ax, 35, 69, 76, 69, RED, 2.6)
    t(ax, 79, 76, "無許可の\nネット接続", 8.5, "bold", RED, ha="center")
    arrow(ax, 35, 63, 76, 55, RED, 1.8, style="-|>", ms=11)
    t(ax, 82, 52, "研究者へ\n自らメール", 8.5, "bold", RED, ha="center")
    # 下段: 二段構えの提供
    t(ax, 50, 40, "開発元の対応 ― 二段構えの提供", 10, "bold", INK)
    rbox(ax, 6, 8, 42, 24, NAVY_LT)
    t(ax, 27, 25, "Fable", 11, "bold", NAVY)
    t(ax, 27, 15, "安全機構つき\n一般公開", 8.2, "reg", INK)
    rbox(ax, 52, 8, 42, 24, RED_LT)
    t(ax, 73, 25, "Mythos", 11, "bold", RED)
    t(ax, 73, 15, "審査制の\n限定提供", 8.2, "reg", INK)
    save(fig, "sandbox_escape.png")

# ------------------------------------------------------------------ S16 Glasswing
def glasswing_race():
    fig, ax = fig_ax(8.8, 1.8)
    t(ax, 2, 88, "同じ能力を、どちらが先に使うか ― 時間競争", 10.5, "bold", INK, ha="left")
    # 防御レーン
    rbox(ax, 2, 48, 58, 22, GREEN_LT)
    t(ax, 7, 59, "防御", 10, "bold", GREEN, ha="left")
    t(ax, 33, 59, "AIで脆弱性を発見 → 先に修正して塞ぐ", 9, "reg", INK)
    # 攻撃レーン
    rbox(ax, 2, 18, 58, 22, RED_LT)
    t(ax, 7, 29, "攻撃", 10, "bold", RED, ha="left")
    t(ax, 33, 29, "AIで脆弱性を発見 → 悪用する", 9, "reg", INK)
    arrow(ax, 2, 8, 60, 8, GRAY, 1.8)
    t(ax, 31, 2, "時間", 8.5, "reg", MUT)
    # 統計
    stats = [("$100M", "防御イニシアチブ"), ("12社+約50", "参加パートナー"), ("1万件超", "High/Critical脆弱性\nを発見・修正へ")]
    for i, (num, label) in enumerate(stats):
        x = 63.5 + i * 12.2
        rbox(ax, x, 18, 11.4, 62, NAVY_LT)
        t(ax, x + 5.7, 62, num, 9.5, "bold", NAVY)
        t(ax, x + 5.7, 35, label, 7, "reg", INK)
    save(fig, "glasswing_race.png")

# ------------------------------------------------------------------ S17 6月のタイムライン
def june_timeline():
    fig, ax = fig_ax(8.8, 1.85)
    y = 46
    ax.plot([4, 96], [y, y], color=NAVY4, lw=3, solid_capstyle="round")
    nodes = [
        (10, "6/9", "Fable 5 一般公開\nMythos 5 は限定提供", NAVY, False),
        (34, "6/12", "米商務省が\n外国籍アクセス停止を命令", RED, True),
        (58, "6/13", "全面停止\n(公開からわずか3日)", RED, False),
        (85, "6/26", "約100の企業・政府機関に\n限定して提供再開", NAVY, True),
    ]
    for x, date, label, c, below in nodes:
        dot(ax, fig, x, y, 1.1, c)
        if below:
            t(ax, x, y - 13, date, 11, "bold", c)
            t(ax, x, y - 32, label, 9, "reg", INK)
        else:
            t(ax, x, y + 14, date, 11, "bold", c)
            t(ax, x, y + 33, label, 9, "reg", INK)
    save(fig, "june_timeline.png")

# ------------------------------------------------------------------ S18 A/B分割
def ab_split():
    fig, ax = fig_ax(3.7, 3.3)
    t(ax, 50, 94, "高度なAIの脅威を2つに分ける", 10.5, "bold", INK)
    rbox(ax, 5, 50, 90, 34, NAVY_LT)
    t(ax, 12, 76, "(A)", 12, "bold", NAVY, ha="left")
    t(ax, 50, 68, "サイバー空間だけで生きるAI", 10.5, "bold", NAVY)
    t(ax, 50, 57, "巧妙・疲れ知らずでも、従来の\nサイバーセキュリティの枠組みの中", 8.8, "reg", INK)
    rbox(ax, 5, 10, 90, 34, GRAY_LT)
    t(ax, 12, 36, "(B)", 12, "bold", MUT, ha="left")
    t(ax, 50, 28, "物理的攻撃手段を持つAI", 10.5, "bold", MUT)
    t(ax, 50, 17, "ロボット・ドローン ― 戦争の攻防の\n議論であり、本講義の範囲外", 8.8, "reg", MUT)
    save(fig, "ab_split.png")

# ------------------------------------------------------------------ S19 プラントの拠り所
def plant_anchor():
    fig, ax = fig_ax(3.8, 3.6)
    rbox(ax, 25, 84, 50, 13, RED_LT)
    t(ax, 50, 90.5, "攻撃AI(サイバー空間)", 10, "bold", RED)
    arrow(ax, 38, 84, 30, 68, RED, 2.2)
    arrow(ax, 62, 84, 70, 68, RED, 2.2)
    t(ax, 21, 76, "① コントローラ\n誤動作", 8.2, "bold", RED)
    t(ax, 81, 76, "② センサー改ざん\n→誤操作を誘う", 8.2, "bold", RED)
    rbox(ax, 12, 52, 76, 15, NAVY_LT)
    t(ax, 50, 59.5, "制御システム(コントローラ・センサー)", 9.5, "bold", NAVY)
    arrow(ax, 50, 52, 50, 44, MUT, 2)
    # 物理的安全対策の層
    rbox(ax, 12, 28, 76, 15, GREEN_LT, ec=GREEN, lw=1.6)
    t(ax, 50, 38.5, "物理的安全対策(プログラムと無関係)", 9.5, "bold", GREEN)
    t(ax, 50, 32, "安全弁・サーモスタット など ― AIには書き換え不能", 8, "reg", INK)
    arrow(ax, 50, 28, 50, 20, MUT, 2)
    rbox(ax, 30, 6, 40, 13, GRAY_LT)
    t(ax, 50, 12.5, "プラント(物理)", 9.5, "bold", INK)
    save(fig, "plant_anchor.png")

# ------------------------------------------------------------------ S20 4ステップ
def four_steps():
    fig, ax = fig_ax(8.8, 1.75)
    steps = [
        ("STEP 1", "拠り所を確保", "物理的安全対策の\n存在と健全性を確認"),
        ("STEP 2", "防御より「検知」", "侵入前提で\n早く気づく仕組みへ投資"),
        ("STEP 3", "停止・早期復旧", "「安全に止められる」が\n最後の防衛線"),
        ("STEP 4", "高度化", "そこからセキュリティを\n積み上げる(順序を守る)"),
    ]
    for i, (step, title, sub) in enumerate(steps):
        x = 1.5 + i * 24.6
        y0 = 6 + i * 7
        h = 66 + i * 7
        rbox(ax, x, y0, 22.6, h, NAVY_LT if i < 3 else NAVY)
        dark = i == 3
        t(ax, x + 11.3, y0 + h - 10, step, 9, "bold", "white" if dark else NAVY2)
        t(ax, x + 11.3, y0 + h - 24, title, 11.5, "bold", "white" if dark else NAVY)
        t(ax, x + 11.3, y0 + h - 45, sub, 8.2, "reg", "white" if dark else INK)
        if i < 3:
            arrow(ax, x + 23, y0 + h / 2, x + 24.5, y0 + h / 2, NAVY, 2)
    save(fig, "four_steps.png")

# ------------------------------------------------------------------ S23 HNDL
def hndl_timeline():
    fig, ax = fig_ax(8.8, 1.9)
    ax.plot([4, 96], [30, 30], color=GRAY, lw=2)
    t(ax, 8, 21, "今日", 10, "bold", INK)
    t(ax, 70, 21, "CRQC登場(時期は不明)", 10, "bold", NAVY)
    ax.plot([70, 70], [26, 34], color=NAVY, lw=2.5)
    # 攻撃者の行動
    rbox(ax, 6, 66, 40, 24, RED_LT)
    t(ax, 26, 78, "攻撃者: 暗号化データを傍受・蓄積", 9.5, "bold", RED)
    arrow(ax, 26, 66, 26, 36, RED, 2)
    rbox(ax, 58, 66, 36, 24, RED_LT)
    t(ax, 76, 78, "将来: 量子計算機で遡って復号", 9.5, "bold", RED)
    arrow(ax, 70, 66, 70, 36, RED, 2)
    # データ寿命バー
    rbox(ax, 8, 42, 78, 12, NAVY3, r=1.5)
    t(ax, 47, 48, "長期秘匿データの寿命(顧客・医療・知財・M&A) = 10〜数十年", 9, "bold", "white")
    rbox(ax, 70.5, 42.5, 15, 11, RED, r=1.5)
    t(ax, 78, 48, "手遅れ区間", 8.5, "bold", "white")
    t(ax, 50, 8, "秘匿期間がCRQC登場をまたぐデータは、「今日の傍受」で既に漏えいが確定し得る", 9.5, "reg", MUT)
    save(fig, "hndl_timeline.png")

# ------------------------------------------------------------------ S24 モスカ
def mosca():
    fig, ax = fig_ax(3.8, 3.0)
    t(ax, 50, 92, "X + Y > Z なら、既に手遅れ", 12, "bold", RED)
    # X+Y bar
    rbox(ax, 6, 58, 44, 16, NAVY, r=1.5)
    t(ax, 28, 66, "X: データ寿命", 8.8, "bold", "white")
    rbox(ax, 51, 58, 34, 16, NAVY2, r=1.5)
    t(ax, 68, 66, "Y: 移行に要する年数", 8.2, "bold", "white")
    # Z bar
    rbox(ax, 6, 30, 62, 16, GRAY, r=1.5)
    t(ax, 37, 38, "Z: CRQC登場までの年数", 8.8, "bold", "white")
    ax.plot([68, 68], [24, 80], color=RED, lw=2, linestyle="--")
    t(ax, 84, 84, "はみ出した分だけ\n手遅れ", 8.5, "bold", RED)
    t(ax, 50, 12, "Zは誰にも分からない。\nコントロールできる X と Y を今から縮める", 9.5, "bold", NAVY)
    save(fig, "mosca.png")

# ------------------------------------------------------------------ S26 PQ普及率
def pq_half():
    fig, ax = fig_ax(3.2, 3.0)
    ax.set_aspect("equal")
    ax.add_patch(Wedge((50, 52), 34, 90, 90 + 0.52 * 360, width=13, fc=NAVY, ec="white", lw=1))
    ax.add_patch(Wedge((50, 52), 34, 90 + 0.52 * 360, 90 + 360, width=13, fc=GRAY_LT, ec="white", lw=1))
    t(ax, 50, 55, "50%超", 17, "bold", NAVY)
    t(ax, 50, 44, "既にPQ鍵交換", 8.5, "reg", MUT)
    t(ax, 50, 8, "Cloudflareへの人間由来トラフィック\nのPQ鍵交換利用率(2025.10)", 8.5, "reg", INK)
    save(fig, "pq_half.png")

# ------------------------------------------------------------------ S27 5ステップ
def five_steps():
    fig, ax = fig_ax(8.8, 1.35)
    steps = ["① 暗号インベントリ\n(棚卸し)", "② リスクの\n優先順位付け", "③ クリプト・\nアジリティ",
             "④ ハイブリッド\n移行", "⑤ ロードマップ\nと体制・KPI"]
    for i, sx in enumerate(steps):
        x0 = 2 + i * 19.2
        pts = [(x0, 15), (x0 + 15.5, 15), (x0 + 18.5, 50), (x0 + 15.5, 85), (x0, 85), (x0 + 3, 50)]
        c = [NAVY4, NAVY3, NAVY2, NAVY, NAVY][i]
        ax.add_patch(Polygon(pts, closed=True, fc=c, ec="white", lw=1))
        tc = "white" if i > 0 else INK
        t(ax, x0 + 9.8, 50, sx, 9, "bold", tc)
    save(fig, "five_steps.png")

# ------------------------------------------------------------------ S29 各国規制
def regs_world():
    fig, ax = fig_ax(8.8, 1.8)
    cards = [
        ("EU", "Cyber Resilience Act", "ライフサイクル管理義務\n罰金: 売上2.5%か€15M"),
        ("英国", "PSTI法", "IoT製品の\nセキュリティ要件"),
        ("米国", "Cyber Trust Mark", "IoT製品\nラベリング制度"),
        ("シンガポール", "CLS", "セキュリティ\nラベリング制度"),
        ("日本", "JC-STAR(IPA)", "IoT製品の適合性評価\n国際同調を検討中"),
    ]
    for i, (country, name, sub) in enumerate(cards):
        x = 1.5 + i * 19.7
        emph = i in (0, 4)
        rbox(ax, x, 6, 18.2, 88, NAVY_LT if emph else GRAY_LT)
        t(ax, x + 9.1, 80, country, 10, "bold", NAVY if emph else MUT)
        t(ax, x + 9.1, 58, name, 9.5, "bold", INK)
        t(ax, x + 9.1, 28, sub, 7.8, "reg", MUT)
    save(fig, "regs_world.png")

# ------------------------------------------------------------------ S34 3アクション
def three_actions():
    fig, ax = fig_ax(8.8, 1.75)
    cards = [
        ("①", "拠り所の棚卸し", "自社設備の「プログラムと無関係な\n安全対策」を1つ確認する"),
        ("②", "暗号インベントリ着手", "モスカの不等式を\n最重要資産1件で試算する"),
        ("③", "取引先への一通", "主要ベンダーに「AI時代の脆弱性対応\n・PQC対応の計画は?」と問い合わせる"),
    ]
    for i, (num, title, sub) in enumerate(cards):
        x = 1.5 + i * 33.2
        rbox(ax, x, 6, 30.5, 88, NAVY_LT)
        dot(ax, fig, x + 4.6, 74, 2.8, NAVY)
        t(ax, x + 4.6, 73.5, num, 11, "bold", "white")
        t(ax, x + 17.5, 74, title, 11.5, "bold", NAVY)
        t(ax, x + 15.2, 32, sub, 8.6, "reg", INK)
    save(fig, "three_actions.png")

if __name__ == "__main__":
    three_shifts(); agenda_time(); ai_timeline(); gtg_flow(); mythos_stats()
    sandbox_escape(); glasswing_race(); june_timeline(); ab_split(); plant_anchor()
    four_steps(); hndl_timeline(); mosca(); pq_half(); five_steps(); regs_world()
    three_actions()
    print("all diagrams generated ->", OUT)
