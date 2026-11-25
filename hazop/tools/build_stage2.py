# -*- coding: utf-8 -*-
import sys
import re
from collections import defaultdict, Counter
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
import stage2_logic as L

OUT = sys.argv[1]
FN = "Meiryo"
thin = Side(style="thin", color="A0A0A0")
BD = Border(left=thin, right=thin, top=thin, bottom=thin)
HF = PatternFill("solid", fgColor="1F3864")
HFONT = Font(name=FN, bold=True, color="FFFFFF", size=9)
F9 = Font(name=FN, size=9)
F9B = Font(name=FN, size=9, bold=True)
NOTE = Font(name=FN, size=9, color="444444")
WR = Alignment(wrap_text=True, vertical="top")
CEN = Alignment(wrap_text=True, vertical="center", horizontal="center")
RED = PatternFill("solid", fgColor="F8CBAD")
YEL = PatternFill("solid", fgColor="FFF2CC")
GRN = PatternFill("solid", fgColor="E2EFDA")
BLU = PatternFill("solid", fgColor="DDEBF7")
GRY = PatternFill("solid", fgColor="F2F2F2")
FREQFMT = '0.0E+00" /年"'
PFMT = "0.0E+00"

S02, S03, S04, S05, S06 = "02_原因事象マスタ", "03_結果事象マスタ", "04_結果―原因_AND_ORツリー", "05_要追加候補・要確認", "06_重大度・頻度マトリクス"
Q = lambda s: f"'{s}'"

causes, results, paths, unused = L.build()
CL_ = list(causes.values())
RL = list(results.values())

# ---------- 中間事象型の原因（上流偏差の記述）を判定 ----------
INTER = re.compile(r"（上記）|（下記）|上流ゾーンの|上流の流量|上流の軽質分|からのガス吹抜け|からの逆流|制御の失敗|設定値の異常|制御の不調|による高温|による軽質分|過大流量|流量の低下|流量喪失|過熱（上流|V-01の液位上昇|V-01液位の上昇|同時途絶|冷却喪失|冷却能力の低下|加熱不足|加熱喪失|による液同伴|循環ガスへの液同伴|液を伴う放出|背圧上昇|K-02停止による|補給水素の過大|補給水素の途絶|容量低下|下流の閉塞|閉塞による上流側|状態でのP-02停止|受槽圧力の低下|液位上昇による|非凝縮ガスの蓄積と|軽質分除去不良|圧力の異常低下|H-01の失火・燃料不足|液偏流")
for c in CL_:
    c["inter"] = bool(INTER.search(c["text"]))
    if c["inter"]:
        c["why"] += "／【要確認】上流側の偏差を記述した中間事象型の原因。上流の物理的原因と重複計上となる可能性"
COMMON = re.compile(r"計装空気|電源|受電|冷却水の喪失|冷却水ポンプ停止|冷却水ヘッダ|熱媒供給源|コントローラCPU|制御ネットワーク|地震|外部火災|閉鎖ガス処理系の背圧|他装置からの大量放出|HMI")
HUMAN = re.compile(r"手順逸脱|閉め忘れ|離席|誤操作|誤閉止|誤開放|判断誤り|再点火|過剰張込み|置換|誤判定|未実施|許可")

# ---------- 絞り込み（スクリーニング）：除外は削除せず 07シートに理由とともに記録 ----------
SCREEN = []     # dict(kind, r, p, reason, rep)
for r in RL:
    s_, e_, b_, *_ = L.severity(r["text"])
    r["sev0"] = max(x for x in (s_, e_, b_) if x)
for p in paths:
    p["H0"] = 1.0
    for c, _ in p["causes"]:
        p["H0"] *= c["freq"]
    p["H0"] *= eval("*".join(str(L.COND[c][1]) for c in p["conds"])) if p["conds"] else 1.0
byR0 = defaultdict(list)
for p in paths:
    byR0[p["result"]["id"]].append(p)
REP_PAT = [("フラッシュ火災により", "同じ放出源の『噴流火災（設備損傷）』『作業員1名の死亡』『蒸気雲爆発』で代表（着火形態の違いのみで、影響は代表シナリオに包含）"),
           ("プール火災", "同じ放出源の『噴流火災』『火災曝露による容器破裂（BLEVE相当）』『連鎖損傷』で代表"),
           ("大量に流出し、フラッシュ蒸発", "同じ放出源の『蒸気雲爆発』『複数死亡』の前段の中間事象（大量放出はADD-C02として条件化済み）")]
rid_by_text = {r["text"]: r["id"] for r in RL}


def rep_ids(t):
    loc = t.split("から")[0]
    return "、".join(r["id"] for r in RL if r["text"].startswith(loc) and r["text"] != t and
                    any(k in r["text"] for k in ("即時着火し、噴流火災", "遅延着火して蒸気雲爆発", "作業員1名が巻き込まれ", "BLEVE")))[:200]


for r in RL:
    if not byR0[r["id"]]:
        continue
    if r["sev0"] <= 2:
        r["screened"] = "低重大度"
        SCREEN.append(dict(kind="低重大度（S≦2）", r=r, p=None, reason=f"採用重大度{r['sev0']}。人身影響を含まず、第3段の対策検討対象から除外（暫定基準の受容頻度{'1E+0' if r['sev0'] == 1 else '1E-1'}/年）。上位の結果事象（漏洩・火災等）は別に保持", rep="—"))
        continue
    for pat, why_ in REP_PAT:
        if pat in r["text"]:
            r["screened"] = "代表シナリオに包含"
            SCREEN.append(dict(kind="代表シナリオに包含", r=r, p=None, reason=why_, rep=rep_ids(r["text"])))
            break
kept = [p for p in paths if not p["result"].get("screened")]
k2 = []
for p in kept:
    if all(c["freq"] >= 1.0 for c, _ in p["causes"]):
        SCREEN.append(dict(kind="潜在条件のみの経路", r=p["result"], p=p, reason="設計上の潜在条件は単独で偏差を発生させない。起動操作等とのAND経路でのみ扱う", rep="同じ偏差群のAND経路"))
    else:
        k2.append(p)
kept = k2
byK = defaultdict(list)
for p in kept:
    byK[p["result"]["id"]].append(p)
k3 = []
for p in kept:
    inter = any(c.get("inter") for c, _ in p["causes"])
    others = [q for q in byK[p["result"]["id"]] if q is not p and not any(c.get("inter") for c, _ in q["causes"])]
    if inter and others:
        SCREEN.append(dict(kind="中間事象型原因の重複", r=p["result"], p=p, reason="原因が上流側の偏差（中間事象）の記述であり、同じ結果事象に至る物理的原因の経路が別に存在するため二重計上を避けて除外", rep=f"{len(others)}本の物理的原因の経路"))
    else:
        k3.append(p)
kept = k3
best = {}
for p in kept:
    key = (p["result"]["id"], tuple(sorted(c["id"] for c, _ in p["causes"])))
    if key not in best or p["H0"] > best[key]["H0"]:
        best[key] = p
k4 = []
for p in kept:
    key = (p["result"]["id"], tuple(sorted(c["id"] for c, _ in p["causes"])))
    if best[key] is p:
        k4.append(p)
    else:
        q = best[key]
        SCREEN.append(dict(kind="重複経路の統合", r=p["result"], p=p, reason="同一の原因（組合せ）が別の偏差経由で同じ結果事象に至る重複経路。OR和の過大評価を避け、頻度の最も大きい代表経路のみ残した", rep=f"{q['group']['id']}経由の経路"))
for r in RL:
    if byR0[r["id"]] and not r.get("screened") and not any(p["result"] is r for p in k4):
        r["lost"] = True
N_BEFORE_P, N_BEFORE_R = len(paths), sum(1 for r in RL if byR0[r["id"]])
paths = k4

# ---------- 経路属性の計算 ----------
cond_prob = lambda cs: eval("*".join(str(L.COND[c][1]) for c in cs)) if cs else 1.0
key_count = Counter((p["result"]["id"], tuple(sorted(c["id"] for c, _ in p["causes"]))) for p in paths)
for p in paths:
    g = p["group"]
    p["cp"] = cond_prob(p["conds"])
    p["H"] = 1.0
    for c, _ in p["causes"]:
        p["H"] *= c["freq"]
    p["H"] *= p["cp"]
    flags, indep = [], []
    cs = [c for c, _ in p["causes"]]
    if any(COMMON.search(c["text"]) for c in cs):
        flags.append("共通原因"); indep.append("共通原因：ユーティリティ・制御系・外部要因は複数ループ／複数機器に同時に作用し、他経路と独立でない")
    if any(c["inter"] for c in cs):
        flags.append("重複計上"); indep.append("中間事象型原因：上流ゾーンの物理的原因と同じ事象を二重に数えている可能性")
    if any("逆止弁" in c["text"] for c in cs):
        flags.append("内部AND"); indep.append("単一原因内に『停止』×『逆止弁不全』のANDを含む（停止頻度×要求時失敗確率で再設定が必要）")
    if len(cs) >= 2:
        if any(c["freq"] >= 1.0 for c in cs):
            flags.append("条件付き確率"); indep.append("設計上の潜在条件を条件確率1として乗算（存在の有無を実機確認）")
        if sum(1 for c in cs if c["freq"] < 1.0) >= 2:
            flags.append("AND次元"); indep.append("年頻度×年頻度は次元が不整合。一方を要求時確率（要求頻度・曝露時間）へ換算する必要がある")
        if sum(1 for c in cs if HUMAN.search(c["text"])) >= 2 or any(HUMAN.search(c["text"]) for c in cs):
            flags.append("時間順序"); indep.append("時間順序依存：先行事象の継続中に後続事象が起こる必要がある／人的誤りの従属性")
    if key_count[(p["result"]["id"], tuple(sorted(c["id"] for c in cs)))] > 1:
        flags.append("重複経路"); indep.append("同一原因が別の偏差経由で同じ結果に寄与（OR和は過大評価）")
    p["flags"] = list(dict.fromkeys(flags))
    p["indep"] = "／".join(dict.fromkeys(indep)) if indep else "単一の独立原因として扱った（独立性の確認は第3段前に実施）"

# ---------- 結果事象：重大度・頻度（Python側で並べ替え用に計算） ----------
byR = defaultdict(list)
for p in paths:
    byR[p["result"]["id"]].append(p)
for r in RL:
    s, e, b, kinds, why = L.severity(r["text"])
    r.update(S=s, E=e, B=b, kinds=kinds, swhy=why, sev=max(x for x in (s, e, b) if x))
    r["G"] = sum(p["H"] for p in byR[r["id"]])
    G = r["G"]
    r["F"] = 5 if G >= 0.1 else 4 if G >= 0.01 else 3 if G >= 0.001 else 2 if G >= 0.0001 else 1
    r["risk"] = r["sev"] * r["F"]
    r["zone"] = r["zones"][0]
    rj = [L.judg(sid) for sid in r["refs"]]
    adopted_refs = [sid for sid in r["refs"] if L.adopted(sid)]
    r["adopted"] = bool(adopted_refs)
    r["judg"] = rj[0][0] if len({j[0] for j in rj}) == 1 else "／".join(sorted({j[0] for j in rj}))
    r["jcom"] = rj[0][1] if not L.REVIEW_RECEIVED else "；".join(f"{sid}:{L.judg(sid)[1]}" for sid in r["refs"] if L.judg(sid)[1])
order = sorted([r for r in RL if r["adopted"] and not r.get("screened")], key=lambda r: (-r["risk"], -r["sev"], -r["G"], r["id"]))

wb = Workbook()
# =========================== 01 ===========================
ws = wb.active
ws.title = "01_第2段プロンプト"
ws.column_dimensions["A"].width = 150
for i, ln in enumerate(open("prompt2.txt", encoding="utf-8").read().rstrip("\n").split("\n"), 1):
    c = ws.cell(row=i, column=1, value=ln or None)
    c.font = Font(name=FN, size=10, bold=ln in ("入力資料", "実施目的", "第1段結果の扱い", "因果関係の作成規則", "年間発生頻度とAND／OR計算", "重大度とリスク評価", "作成するExcelワークシート", "品質要件"))
    c.alignment = Alignment(wrap_text=True, vertical="top")
n = i + 2
ws.cell(row=n, column=1, value="【追加入力】重大度マトリクス（結果事象の深刻度の評価指標）およびリスクマトリックス（発生可能性VH〜VL×被害重大度）を受領。内容は06シートに転記した。").font = NOTE
ws.cell(row=n + 1, column=1, value=("【第1段レビュー判定】受講生のレビュー結果（採用・修正・除外・要確認）は本作成時点で未受領のため、第1段の全原因・結果を「採用（仮）」として扱った。"
                                    if not L.REVIEW_RECEIVED else "【第1段レビュー判定】stage1_review.csv の判定を反映した。")).font = Font(name=FN, size=10, bold=True, color="C00000")
ws.cell(row=n + 2, column=1, value="【絞り込み（スクリーニング）】依頼者の指示により第2段で検討対象を絞った（低重大度、代表シナリオへの包含、潜在条件のみの経路、中間事象型原因の重複、重複経路の統合）。除外は07シートに理由とともに記録し、削除していない。"
        "【重大度の見直し】ビジネス・環境重大度を放出源の規模（小：シール・継手等／中：配管・熱交換器・圧縮機／大：塔・ドラム・反応器）で段階づけた。人身（安全）重大度は変更していない。"
        "あわせて、漏洩起因の蒸気雲爆発・複数死亡・建屋被害・構外影響に大量放出の条件（ADD-C02）を追加し、液封未確立の原因を潜在条件から人的誤り（1E-2/年）へ修正した。").font = Font(name=FN, size=10, bold=True, color="1F3864")


def header(ws, row, heads, widths, height=40):
    for j, (t, w) in enumerate(zip(heads, widths), 1):
        c = ws.cell(row=row, column=j, value=t)
        c.font = HFONT; c.fill = HF; c.alignment = CEN; c.border = BD
        ws.column_dimensions[CL(j)].width = w
    ws.row_dimensions[row].height = height


def put(ws, r, j, v, fmt=None, fill=None, font=F9):
    c = ws.cell(row=r, column=j, value=v)
    c.font = font; c.alignment = WR; c.border = BD
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


# =========================== 02 ===========================
ws2 = wb.create_sheet(S02)
ws2["A1"] = "原因事象マスタ（第1段の原因事象を同一文言で統合。年間発生頻度は演習用の概略値であり、厳密な故障率ではない）"
ws2["A1"].font = Font(name=FN, size=11, bold=True)
header(ws2, 3, ["原因事象ID", "第1段のゾーン", "原因事象", "年間発生頻度（/年）", "頻度設定の根拠・演習上の仮定", "第1段レビュー判定", "レビューコメント", "第1段参照ID", "使用経路数", "要確認区分"],
       [11, 16, 60, 14, 60, 14, 40, 30, 9, 18])
use_cnt = Counter(c["id"] for p in paths for c, _ in p["causes"])
for i, c in enumerate(CL_, 4):
    rj = [L.judg(s) for s in c["refs"]]
    put(ws2, i, 1, c["id"]); put(ws2, i, 2, "、".join(L.ZNAME[z] for z in c["zones"]))
    put(ws2, i, 3, c["text"]); put(ws2, i, 4, c["freq"], FREQFMT, BLU)
    put(ws2, i, 5, c["why"]); put(ws2, i, 6, rj[0][0]); put(ws2, i, 7, rj[0][1] if not L.REVIEW_RECEIVED else "；".join(x[1] for x in rj if x[1]))
    put(ws2, i, 8, "、".join(c["refs"]))
    put(ws2, i, 9, f'=COUNTIF({Q(S04)}!$I:$I,A{i}&"*")+COUNTIF({Q(S04)}!$L:$L,A{i}&"*")+COUNTIF({Q(S04)}!$O:$O,A{i}&"*")', "0")
    fl = []
    if c["inter"]:
        fl.append("要確認：中間事象型")
    if c["freq"] >= 1:
        fl.append("要確認：潜在条件")
    if c["why"].startswith("個別根拠なし"):
        fl.append("要確認：頻度既定値")
    if use_cnt[c["id"]] == 0:
        fl.append("要確認：単独で経路なし")
    put(ws2, i, 10, "／".join(fl) or None, fill=RED if fl else None)
LAST2 = 3 + len(CL_)
ws2.freeze_panes = "D4"
ws2.auto_filter.ref = f"A3:J{LAST2}"

# =========================== 03 ===========================
ws3 = wb.create_sheet(S03)
ws3["A1"] = "結果事象マスタ（第1段の結果事象を同一文言で統合。重大度は受領した重大度マトリクスに準拠、採用重大度は3側面の最大値＝数式）"
ws3["A1"].font = Font(name=FN, size=11, bold=True)
header(ws3, 3, ["結果事象ID", "結果事象", "発生ゾーン", "リスク種類", "人身・安全重大度", "環境重大度", "ビジネス重大度", "採用重大度", "重大度設定の根拠", "第1段レビュー判定", "レビューコメント", "第1段参照ID", "OR経路数", "ツリー状態"],
       [11, 62, 16, 16, 9, 9, 9, 9, 50, 14, 34, 30, 9, 14])
RROW = {}
for i, r in enumerate(RL, 4):
    RROW[r["id"]] = i
    put(ws3, i, 1, r["id"]); put(ws3, i, 2, r["text"]); put(ws3, i, 3, "、".join(L.ZNAME[z] for z in r["zones"]))
    put(ws3, i, 4, r["kinds"])
    for j, v in ((5, r["S"]), (6, r["E"]), (7, r["B"])):
        put(ws3, i, j, v, "0", BLU if v else None)
    put(ws3, i, 8, f"=MAX(E{i}:G{i})", "0", font=F9B)
    put(ws3, i, 9, r["swhy"]); put(ws3, i, 10, r["judg"]); put(ws3, i, 11, r["jcom"])
    put(ws3, i, 12, "、".join(r["refs"]))
    put(ws3, i, 13, f'=COUNTIF({Q(S04)}!$AB:$AB,A{i})-COUNTIFS({Q(S04)}!$AB:$AB,A{i},{Q(S04)}!$Z:$Z,"原因未確定*")', "0")
    st = "除外" if not r["adopted"] else (f"絞り込み：{r['screened']}" if r.get("screened") else ("原因未確定" if not byR[r["id"]] else "ツリー作成済"))
    put(ws3, i, 14, st, fill=RED if st == "原因未確定" else (GRY if st.startswith("絞り込み") else None))
LAST3 = 3 + len(RL)
ws3.freeze_panes = "C4"
ws3.auto_filter.ref = f"A3:N{LAST3}"

# =========================== 06（先に作成：参照セル） ===========================
ws6 = wb.create_sheet(S06)
ws6.column_dimensions["A"].width = 14
for col, w in zip("BCDEFGH", [34, 34, 34, 16, 14, 14, 14]):
    ws6.column_dimensions[col].width = w
ws6["A1"] = "重大度・頻度マトリクス、計算規則、演習上の限界"
ws6["A1"].font = Font(name=FN, size=12, bold=True)
ws6["A3"] = "1. 重大度レベルの定義（受領した『結果事象の深刻度の評価指標』を転記）"; ws6["A3"].font = F9B
hd = ["重大度レベル", "ビジネス", "環境", "安全（人身・安全）", "受容可能な事故発生頻度（/年）"]
for j, t in enumerate(hd, 1):
    c = ws6.cell(row=4, column=j, value=t); c.font = HFONT; c.fill = HF; c.alignment = CEN; c.border = BD
SEVDEF = [
    (1, "軽微な影響を生じる侵害（5万ドル未満）", "環境に軽微な影響を生じる侵害", "安全に軽微な影響を生じる侵害", 1e-2),
    (2, "アクセスが妨害され、ビジネスに軽微な悪影響が生じる（5万〜100万ドル）", "アクセスが妨害され、制御を監視できず、環境に軽微な悪影響が生じる", "アクセスが妨害され、制御の停止で設備に軽微な悪影響が生じる", 1e-3),
    (3, "情報漏洩が発生し、ビジネスに中程度の悪影響が生じる（100万〜2500万ドル）", "制御が不調になり、一時的に放出、および数週間での浄化", "制御の誤動作で、記録すべき傷害が生じる", 1e-4),
    (4, "ビジネスに大きな悪影響が生じる（2500万〜1億ドル）", "一時的な環境破壊と、数か月から数年間での浄化", "単独のオンサイト死亡事故", 1e-5),
    (5, "ビジネスに重大な悪影響が生じる（1億ドル以上）", "重大な環境破壊、10年以上での浄化", "複数のオンサイト死亡事故", 1e-6),
]
for k, row in enumerate(SEVDEF, 5):
    for j, v in enumerate(row, 1):
        put(ws6, k, j, v, FREQFMT if j == 5 else None, YEL if j == 1 else None)
ACC = f"{Q(S06)}!$E$5:$E$9"
ws6["A11"] = ("本演習での適用：安全欄は人身（死亡・傷害）の結果に適用し、設備損壊・停止の金額規模はビジネス欄で評価した。採用重大度は3側面の最大値。"
              "ビジネス・環境は放出源の規模で段階づけ：火災・爆発後の長期停止は 大（塔・ドラム・反応器）5／中（配管・熱交換器・圧縮機）4／小（シール・継手・取付部）3、噴流火災の設備損傷は 大4／中・小3、"
              "蒸気雲爆発は 大・中5／小4、連鎖損傷は 大5／中・小4、土壌・水域汚染は 小3／中・大4。")
ws6["A11"].font = NOTE

ws6["A13"] = "2. 頻度区分（第2段プロンプトの規定：リスク評価値の計算に使用）"; ws6["A13"].font = F9B
for j, t in enumerate(["頻度区分", "範囲（/年）", "下限値（/年）"], 1):
    c = ws6.cell(row=14, column=j, value=t); c.font = HFONT; c.fill = HF; c.alignment = CEN; c.border = BD
FCL = [("F5", "1E-1 /年以上", 1e-1), ("F4", "1E-2 /年以上、1E-1 /年未満", 1e-2), ("F3", "1E-3 /年以上、1E-2 /年未満", 1e-3), ("F2", "1E-4 /年以上、1E-3 /年未満", 1e-4), ("F1", "1E-4 /年未満", 0)]
for k, (a, b, c_) in enumerate(FCL, 15):
    put(ws6, k, 1, a, fill=YEL); put(ws6, k, 2, b); put(ws6, k, 3, c_, FREQFMT)

ws6["A21"] = "3. リスク評価値の計算規則"; ws6["A21"].font = F9B
rules = ["リスク評価値 ＝ 採用重大度S（1〜5）× 頻度区分F（1〜5）（04シートD列＝数式）。",
         "結果事象の年間発生頻度（04シートG列）＝ 同じ結果事象番号のOR行のAND経路成立頻度（H列）の和（各OR行に同一数式）。",
         "AND経路成立頻度（H列）＝ 同一行の原因事象の年間発生頻度の積 × 必要条件の条件確率（U列：要追加候補の仮値）。下のスイッチで必要条件を除外できる。",
         "結果事象の塊は、リスク評価値の降順 → 重大度の降順 → 年間発生頻度の降順で配置（必要条件スイッチ＝1の状態で並べ替え済み。スイッチ変更後は値のみ更新され、並び順は更新されない）。",
         "参考：添付リスクマトリックスの値（04シートAD列）と、重大度レベル別の受容可能頻度との比（AF列）を併記した。並べ替えには使用していない。"]
for k, t in enumerate(rules, 22):
    ws6.cell(row=k, column=1, value=f"・{t}").font = F9
ws6["A28"] = "必要条件の条件確率を計算に含める（1＝含める／0＝含めない）"; ws6["A28"].font = F9B
ws6["E28"] = 1
ws6["E28"].fill = YEL; ws6["E28"].font = Font(name=FN, size=11, bold=True, color="0000FF"); ws6["E28"].border = BD
SW = f"{Q(S06)}!$E$28"
dv = DataValidation(type="list", formula1='"0,1"', allow_blank=False); ws6.add_data_validation(dv); dv.add("E28")
ws6["A29"] = "0にすると、第1段で採用された原因事象の頻度のみの積（必要条件を全て1とみなす保守側の上限値）となる。必要条件は第1段の原因として未採用のため、値は05シートで受講生が判断する仮値。"
ws6["A29"].font = NOTE

ws6["A31"] = "4. 参考：受領したリスクマトリックス（発生可能性×被害重大度）"; ws6["A31"].font = F9B
for j, t in enumerate(["発生可能性", "発生確率（/年）", "判定下限（/年）", "S=1", "S=2", "S=3", "S=4", "S=5"], 1):
    c = ws6.cell(row=32, column=j, value=t); c.font = HFONT; c.fill = HF; c.alignment = CEN; c.border = BD
RM = [("VH", 10, 10, [5, 9, 12, 13, 16]), ("H", 1, 1, [4, 8, 9, 12, 13]), ("M", 0.1, 0.1, [4, 5, 8, 9, 12]), ("L", 0.03, 0.03, [1, 4, 5, 8, 9]), ("VL", 0.01, 0, [1, 1, 4, 5, 8])]
cmap = {1: GRN, 4: GRN, 5: YEL, 8: YEL, 9: PatternFill("solid", fgColor="F4B183"), 12: PatternFill("solid", fgColor="F4B183"), 13: PatternFill("solid", fgColor="FF6600"), 16: PatternFill("solid", fgColor="FF6600")}
for k, (a, p_, lo, vals) in enumerate(RM, 33):
    put(ws6, k, 1, a, fill=YEL); put(ws6, k, 2, p_, FREQFMT); put(ws6, k, 3, lo, FREQFMT)
    for j, v in enumerate(vals, 4):
        put(ws6, k, j, v, "0", cmap.get(v))
ws6["A38"] = ("判定方法（本演習での読み替え）：年間発生頻度が判定下限以上となる最上位の区分を採用（10以上VH、1以上H、0.1以上M、0.03以上L、それ未満VL）。"
              "VLは0.01/年が代表値であり、それ未満の頻度を区別できないため、低頻度・高重大度の結果は重大度別の受容可能頻度（1章）との比較も併せて参照すること。")
ws6["A38"].font = NOTE
RMV = f"{Q(S06)}!$D$33:$H$37"

ws6["A40"] = "5. 演習上の頻度計算の限界"; ws6["A40"].font = F9B
lims = ["計算値はFTA・定量的リスク評価の最終値ではなく、演習用の概略スクリーニング値である。",
        "原因事象の頻度はLOPA等で用いられる一般的な初期事象頻度を参考にした演習上の仮定であり、当該設備の故障実績・保全履歴に基づかない。",
        "必要条件（着火、在場、放圧不作動など）の条件確率は第1段で原因として採用されていない要追加候補の仮値であり、受講生の判断で採否・値を決める。",
        "ユーティリティ喪失・計装空気・制御系・外部要因は共通原因であり、複数経路の単純なOR和は過大評価となる。",
        "同一原因が複数の偏差経由で同じ結果に至る重複経路、上流偏差を記述した中間事象型原因は二重計上となる可能性がある（要確認表示）。",
        "AND経路で年頻度同士を乗じた値は次元が整合しない。一方を要求時確率・曝露時間・要求頻度へ換算する必要がある（要確認表示）。",
        "既存の制御器・計器・弁・閉鎖ガス処理系は設備情報として記載したが、独立保護層としての頻度低減はクレジットしていない。",
        "OR和は稀事象近似（単純和）であり、和が大きい場合は1/年を超える値が生じ得る。"]
for k, t in enumerate(lims, 41):
    ws6.cell(row=k, column=1, value=f"・{t}").font = F9

# =========================== 04 ===========================
ws4 = wb.create_sheet(S04, 3)
ws4["A1"] = "結果事象―原因事象 AND／ORツリー（1行＝最小AND経路、同一結果事象番号の複数行＝OR経路）"
ws4["A1"].font = Font(name=FN, size=12, bold=True)
ws4["A2"] = ("【演習用の概略スクリーニング値】FTA・定量リスク評価の最終値ではない。H列＝原因頻度の積×必要条件の条件確率（仮値、06シートのスイッチで除外可）。"
             "既存の制御器・計器・弁・閉鎖ガス処理系は独立保護層としてクレジットしていない。赤色のZ列は要確認（共通原因・重複・時間順序・次元不整合など）。")
ws4["A2"].font = Font(name=FN, size=9, bold=True, color="C00000")
ws4.merge_cells("A2:Q2"); ws4.row_dimensions[2].height = 30; ws4["A2"].alignment = WR
heads = ["結果事象番号（リスク順の通し番号）", "結果事象", "結果発生ゾーン", "リスク評価値（S×F）", "重大度レベル", "リスク種類", "結果事象の年間発生頻度（/年）", "当該AND経路の成立頻度（/年）",
         "原因事象1", "原因事象1の発生ゾーン", "原因事象1の年間発生頻度", "原因事象2", "原因事象2の発生ゾーン", "原因事象2の年間発生頻度",
         "原因事象3", "原因事象3の発生ゾーン", "原因事象3の年間発生頻度",
         "物理的伝播経路（原因発生ゾーン → 中間ゾーン → 結果発生ゾーン）", "中間事象", "必要条件・要追加候補", "必要条件の条件確率（仮値・未採用）",
         "独立性・共通原因", "計算上の仮定", "根拠・参照ID（第1段）", "レビューコメント", "要確認区分", "頻度区分F", "結果事象ID", "経路ID",
         "参考：添付リスクマトリックス値", "参考：重大度別の受容可能頻度（/年）", "参考：受容可能頻度に対する比"]
widths = [9, 46, 13, 8, 7, 12, 12, 12, 36, 11, 11, 30, 11, 11, 22, 11, 11, 44, 40, 50, 11, 46, 34, 26, 16, 18, 7, 10, 10, 10, 12, 10]
HR = 4
header(ws4, HR, heads, widths, 56)
ws4.freeze_panes = ws4.cell(row=HR + 1, column=3)
r = HR + 1
pid = 0
GRP_FILL = [PatternFill("solid", fgColor="FFFFFF"), GRY]
ASSUME = "概略スクリーニング値。原因頻度は演習用一般値。必要条件の条件確率は仮値（06スイッチ）。保護層の頻度低減はクレジットしない。"


def zl(z):
    return L.ZSHORT[z]


for n, res in enumerate(order, 1):
    plist = byR[res["id"]]
    s0 = r
    e0 = r + max(len(plist), 1) - 1
    bf = GRP_FILL[n % 2]
    rows = plist if plist else [None]
    for p in rows:
        rr = RROW[res["id"]]
        put(ws4, r, 1, n, "0", bf, F9B)
        put(ws4, r, 2, res["text"], fill=bf)
        put(ws4, r, 3, "、".join(L.ZNAME[z] for z in res["zones"]), fill=bf)
        put(ws4, r, 4, f"=E{r}*AA{r}", "0", font=F9B)
        put(ws4, r, 5, f"=INDEX({Q(S03)}!$H$4:$H${LAST3},MATCH(AB{r},{Q(S03)}!$A$4:$A${LAST3},0))", "0")
        put(ws4, r, 6, f"=INDEX({Q(S03)}!$D$4:$D${LAST3},MATCH(AB{r},{Q(S03)}!$A$4:$A${LAST3},0))")
        put(ws4, r, 7, f"=SUM($H${s0}:$H${e0})", FREQFMT, font=F9B)
        put(ws4, r, 27, f"=IF(G{r}>=0.1,5,IF(G{r}>=0.01,4,IF(G{r}>=0.001,3,IF(G{r}>=0.0001,2,1))))", "0")
        put(ws4, r, 28, res["id"])
        put(ws4, r, 30, f"=INDEX({RMV},IF(G{r}>=10,1,IF(G{r}>=1,2,IF(G{r}>=0.1,3,IF(G{r}>=0.03,4,5)))),E{r})", "0")
        put(ws4, r, 31, f"=INDEX({ACC},E{r})", FREQFMT)
        put(ws4, r, 32, f"=IF(AE{r}>0,G{r}/AE{r},\"\")", "0.0E+00")
        if p is None:
            put(ws4, r, 8, None, FREQFMT)
            put(ws4, r, 9, "（原因未確定：第1段で採用された原因事象から物理的経路を構成できない）", fill=RED)
            for j in range(10, 18):
                put(ws4, r, j, None)
            put(ws4, r, 18, "—"); put(ws4, r, 19, "—"); put(ws4, r, 20, "05シートの要追加候補を参照"); put(ws4, r, 21, None)
            put(ws4, r, 22, "—"); put(ws4, r, 23, "原因未確定のため頻度0として表示（実際の頻度が0という意味ではない）")
            put(ws4, r, 24, "、".join(res["refs"])); put(ws4, r, 25, res["jcom"] if L.REVIEW_RECEIVED else None)
            put(ws4, r, 26, "原因未確定", fill=RED, font=F9B)
            put(ws4, r, 29, None)
            r += 1
            continue
        pid += 1
        g = p["group"]
        gz = g["z"]
        fcols = []
        for k, (c, sid) in enumerate(p["causes"][:3]):
            col = 9 + 3 * k
            cz = L.zone_of_text(c["text"], gz)
            put(ws4, r, col, f"{c['id']}｜{c['text']}")
            put(ws4, r, col + 1, zl(cz))
            put(ws4, r, col + 2, f"=INDEX({Q(S02)}!$D$4:$D${LAST2},MATCH(LEFT({CL(col)}{r},7),{Q(S02)}!$A$4:$A${LAST2},0))", FREQFMT, BLU)
            fcols.append(f"{CL(col + 2)}{r}")
        for k in range(len(p["causes"]), 3):
            for j in range(3):
                put(ws4, r, 9 + 3 * k + j, None)
        put(ws4, r, 8, f"=PRODUCT({','.join(fcols)})*IF({SW}=1,U{r},1)", FREQFMT, font=F9B)
        # 物理的伝播経路
        cz = L.zone_of_text(p["causes"][0][0]["text"], gz)
        seq = L.flow_path(cz, gz) + L.flow_path(gz, p["rz"])[1:]
        seq = [z for i_, z in enumerate(seq) if i_ == 0 or z != seq[i_ - 1]]
        bnd = re.findall(r"B\d\d/S\w+", g["equip"])
        txt = " → ".join(zl(z) for z in seq)
        if bnd:
            txt += f"（境界 {'、'.join(bnd)}）"
        if p["rz"] == 0 and gz != 0:
            txt += "（放圧・排出配管経由で閉鎖ガス処理系）"
        mech = "機器健全性" if L.INTEGRITY_GW.search(g["gw"]) else "物質・圧力" if re.search(r"圧力|流量|吹抜|逆流|液位|過充填|液同伴", g["gw"]) else "組成" if "組成" in g["gw"] else "温度・エネルギー" if re.search(r"温度|加熱|冷却", g["gw"] + g["equip"]) else "作業・操作" if re.search(r"操作|作業|保全|起動|サンプリング|ドレン", g["equip"] + g["gw"]) else "物質・エネルギー"
        put(ws4, r, 18, f"[{mech}] {txt}")
        chain = " → ".join(L.COND[c_][0].split("（")[0] for c_ in p["conds"])
        put(ws4, r, 19, f"{g['id']} {g['equip']}：{g['gw']}" + (f" ⇒ {chain}" if chain else ""))
        put(ws4, r, 20, "；".join(f"{c_} {L.COND[c_][0]}（仮 {L.COND[c_][1]}）" for c_ in p["conds"]) or "なし（第1段の原因のみで成立）",
            fill=YEL if p["conds"] else None)
        put(ws4, r, 21, f"={'*'.join(f'{Q(S05)}!$F${5 + list(L.COND).index(c_)}' for c_ in p['conds'])}" if p["conds"] else 1, PFMT, YEL if p["conds"] else None)
        put(ws4, r, 22, p["indep"], fill=RED if p["flags"] else None)
        put(ws4, r, 23, ASSUME)
        put(ws4, r, 24, "、".join([sid for _, sid in p["causes"]] + [p["rsid"]]))
        put(ws4, r, 25, "；".join(x for x in [L.judg(sid)[1] for _, sid in p["causes"]] + [L.judg(p["rsid"])[1]] if x) if L.REVIEW_RECEIVED else None)
        put(ws4, r, 26, ("要確認：" + "・".join(p["flags"])) if p["flags"] else None, fill=RED if p["flags"] else None, font=F9B if p["flags"] else F9)
        put(ws4, r, 29, f"P-{pid:05d}")
        r += 1
    # ブロックの区切り線
    for j in range(1, 33):
        c = ws4.cell(row=e0, column=j)
        c.border = Border(left=thin, right=thin, top=thin, bottom=Side(style="medium", color="1F3864"))
LAST4 = r - 1
ws4.auto_filter.ref = f"A{HR}:AF{LAST4}"
red_font = Font(name=FN, size=9, bold=True, color="C00000")
ws4.conditional_formatting.add(f"D{HR + 1}:D{LAST4}", FormulaRule(formula=[f"D{HR + 1}>=20"], fill=PatternFill("solid", fgColor="FF9999")))
ws4.conditional_formatting.add(f"D{HR + 1}:D{LAST4}", FormulaRule(formula=[f"AND(D{HR + 1}>=12,D{HR + 1}<20)"], fill=PatternFill("solid", fgColor="FFD966")))

# =========================== 05 ===========================
ws5 = wb.create_sheet(S05, 4)
ws5["A1"] = "要追加候補・要確認（正式ツリーへ混入させない項目。受講生が採否を判断する）"
ws5["A1"].font = Font(name=FN, size=12, bold=True)
ws5["A2"] = "F列の仮値は04シートU列（必要条件の条件確率）から参照される。値を変更すると04シートの頻度・リスク評価値が再計算される（並び順は再生成が必要）。"
ws5["A2"].font = NOTE
h5 = ["候補ID", "区分", "内容", "関連する結果事象・経路・第1段ID", "確認すべき理由・必要な追加情報", "仮値（条件確率）", "使用経路数", "受講生判断（採用／修正／除外／要確認）", "受講生コメント"]
header(ws5, 4, h5, [10, 20, 52, 34, 56, 11, 10, 16, 30])
r5 = 5
dv5 = DataValidation(type="list", formula1='"採用,修正,除外,要確認"', allow_blank=True)
ws5.add_data_validation(dv5)
cond_use = Counter(c_ for p in paths for c_ in p["conds"])
COND_WHY = {
    "ADD-C01": "偏差の程度と機器の設計圧力・設計温度・強度余裕が未提示。偏差→損傷の条件確率を設計情報で確認する。",
    "ADD-C02": "配管径・機器内容積・液在庫が未提示。放出規模（小漏洩／大口径破損）の区分が必要。",
    "ADD-C03": "着火源（加熱炉H-01、高温面、電気機器、車両）の配置が未提示。H2含有流れは着火確率を別設定する必要。",
    "ADD-C04": "滞留域・風況・遅延着火源が未提示。ガス雲規模と着火の条件。",
    "ADD-C05": "設備の混雑度・閉囲度（架構、圧縮機ハウス）が未提示。VCE成立の条件。",
    "ADD-C06": "巡回・作業頻度、作業員の在場時間割合が未提示（曝露時間）。",
    "ADD-C07": "起動・保全時の在場人数、同時作業の有無が未提示。",
    "ADD-C08": "計器室・仮設事務所の位置・耐爆設計が未提示（Texas City型の着眼点：今回設備の配置は未確認）。",
    "ADD-C09": "耐火被覆・散水設備の有無は対策側の情報だが、火災継続時間・容器の受熱条件として設計情報が必要。",
    "ADD-C10": "設備間距離・配置が未提示。",
    "ADD-C11": "敷地境界までの距離・周辺状況が未提示。",
    "ADD-C12": "放圧装置の設定圧、偏差時の到達圧力が未提示。",
    "ADD-C13": "安全弁・破裂板の設置有無・容量が未提示（実機確認が必要な候補）。",
    "ADD-C14": "閉鎖ガス処理系の受入能力・同時放出シナリオが未提示。",
    "ADD-C15": "閉鎖ガス処理系の気液分離設備の構成・容量が未提示。",
    "ADD-C16": "フレア等燃焼設備の有無が未提示（大気ベントスタックの存在は根拠がないため経路に加えていない）。",
    "ADD-C17": "防液堤・排水系の遮断設備・油水分離の構成が未提示。",
    "ADD-C18": "消火排水の貯留設備の有無・容量が未提示。",
    "ADD-C19": "立地の気象条件（最低気温・凍結期間）が未提示。",
    "ADD-C20": "偏差の継続時間と製品規格・操業許容範囲が未提示。",
}
for k, (cid, (txt, v)) in enumerate(L.COND.items()):
    vals = [cid, "必要条件（中間事象・条件確率）", txt, "04シートT列に記載の経路", COND_WHY[cid], v, f'=COUNTIF({Q(S04)}!$T:$T,"*{cid}*")', None, None]
    for j, x in enumerate(vals, 1):
        put(ws5, r5, j, x, PFMT if j == 6 else ("0" if j == 7 else None), YEL if j == 6 else None)
    dv5.add(f"H{r5}")
    r5 += 1
extra = []
for res in RL:
    if res["adopted"] and not byR[res["id"]]:
        extra.append(("要追加：原因事象", f"{res['id']}「{res['text']}」の原因となる事象（例：使用済触媒・洗浄排水の取扱い手順の逸脱、廃触媒の仮置き場の漏洩）",
                      f"{res['id']}／" + "、".join(res["refs"]), "第1段の原因事象に対応するものがなく、04シートで『原因未確定』として残した。触媒成分も未確認。", None))
_u = {}
for c, sid, g in unused:
    _u.setdefault(c["id"], [c, []])[1].append(sid)
for c, sids in _u.values():
    extra.append(("要確認：単独で経路を構成しない原因", f"{c['id']}「{c['text']}」", "、".join(sids),
                  ("受入分析の誤りは組成異常を発生させず、検知失敗の条件にあたる。受入分析による受入停止の運用が資料に記載されていないため、AND条件としても採用しなかった。運用を確認のうえ採否を判断する。"
                   if "受入分析" in c["text"] else
                   "塔内部品の脱落・損傷は塔内の分離性能低下であり、同じ群の外部漏洩の結果へ至る物理的経路を構成しない。対応する結果事象（分離不良・製品規格外）を要追加候補とする。"
                   if "塔内部品" in c["text"] else "同じ群の結果事象へ至る物理的経路を構成できなかった。"), None))
inter = [c for c in CL_ if c["inter"]]
extra.append(("要確認：中間事象型の原因", f"上流側の偏差（例：『FC-702の過大流量』『H-01の加熱不足（上記）』『循環ガスへの液同伴』）を記述した原因 {len(inter)}件",
              "02シートJ列『要確認：中間事象型』", "上流ゾーンの物理的原因（弁固着・計器故障等）からの経路と二重計上になる。中間事象として扱い、上流の原因に置換するか判断する。", None))
lat = [c for c in CL_ if c["freq"] >= 1]
extra.append(("要確認：潜在条件の扱い", "計器配置の不備・液封配管の未設計など、頻度ではなく存在の有無で成立する条件（" + "、".join(c["id"] for c in lat) + "）",
              "02シート", "条件確率1として乗算している。実機での存在確認が必要。", None))
extra += [
    ("中間事象：要追加候補", "放圧装置作動中の閉鎖ガス処理ヘッダ内の液溜まり（低点ドレン未実施）", "Z0系の経路", "同時放出時の液撃・ヘッダ破損の中間事象として第1段に原因が明示されていない。", None),
    ("結果事象：要追加候補", "H2を含む漏洩の水素脆化・小分子漏洩による継手からの持続的微小漏洩と、圧縮機ハウス等の閉囲空間での蓄積", "IF-K02、補給水素配管", "圧縮機の設置形態（屋内／屋外）が未提示。", None),
    ("追加設計情報", "機器の設計圧力・設計温度・材質、内容積・液在庫、配管径", "全ゾーン", "偏差→損傷（ADD-C01）、放出規模（ADD-C02）の判断に必要。", None),
    ("追加設計情報", "弁のフェイル位置（計装空気喪失時）、K-02形式（遠心／往復）と容量制御方式、逆止弁の設置位置", "Z0計装空気、Z4", "共通原因経路の結果（過圧・過充填・吹抜け）の向きが弁フェイル位置で決まる。", None),
    ("追加設計情報", "安全弁・破裂板の設置、閉鎖ガス処理系・閉鎖排液系の構成と受入能力、燃焼設備の有無", "IF-VENT、IF-DRAIN", "放圧・ベント・ドレン系の重大放出経路の成否を決める（ADD-C12〜C16）。", None),
    ("追加設計情報", "触媒の種類・被毒物質・副反応特性、H2／炭化水素比の運転許容範囲", "Z5", "R-01の温度上昇・副反応・塩化物腐食の経路はいずれも触媒成分が未確認の候補。", None),
    ("独立性・共通原因", "計装空気喪失・電源喪失・冷却水喪失・制御システム故障は、複数ゾーンの経路に同時に作用する", "04シートZ列『共通原因』", "OR和で単純加算すると過大評価。共通原因として別建てのツリーで扱うかを判断する。", None),
    ("独立性・共通原因", "同一原因が複数の偏差経由で同一結果に至る重複経路", "04シートZ列『重複経路』", "OR和の重複部分の除去方法（最小カットセットへの整理）を決める。", None),
    ("時間順序・条件付き確率", "AND経路の年頻度×年頻度（例：失火×再点火時パージ不十分、液同伴×排液遅れ、不活性雰囲気×入槽許可逸脱）", "04シートZ列『AND次元』『時間順序』",
     "後続事象は要求時確率（1回の操作あたりの誤り確率）または曝露時間で表す必要がある。要求頻度・継続時間を確認する。", None),
    ("起動・停止・保全", "T-01・T-02・T-03の起動時の液張込みと塔底排出開始のタイミング（Texas City事例の着眼点）", "Z2-14、Z3-14、Z7-14、Z2-23、Z3-23、Z7-20", "起動手順・液位計の測定範囲・要員配置を確認し、起動モードを別ツリーとして扱うかを判断する。", None),
    ("起動・停止・保全", "保全後の再起動時の置換・気密確認、誤材料部品の復旧（保全後の高温水素系の材料確認）", "Z1-22、Z4-23、Z6-02", "保全作業の手順・材料管理（PMI）の運用を確認。今回設備で高温水素による材料劣化機構が成立するかは材料・水素分圧の情報が必要で、根拠なく経路に加えていない。", None),
    ("起動・停止・保全", "R-01触媒交換時の入槽・不活性ガス使用、使用済触媒の取扱い", "Z5-11", "不活性ガスの使用有無・入槽手順が未提示。", None),
    ("異常操作", "追加パージ（10 kmol/h×1時間）の開始・終了遅れ、HS-602への組成要求の解除忘れ", "Z6系", "運転員操作の頻度（GC 8時間ごと、CH4判定の発生頻度）が未提示。", None),
]
for k, (kind, txt, rel, why, v) in enumerate(extra, 1):
    vals = [f"ADD-X{k:02d}", kind, txt, rel, why, v, None, None, None]
    for j, x in enumerate(vals, 1):
        put(ws5, r5, j, x, fill=RED if kind.startswith("要確認") or kind.startswith("要追加：原因") else None)
    dv5.add(f"H{r5}")
    r5 += 1
ws5.freeze_panes = "D5"

wb.move_sheet(S06, offset=0)
# =========================== 07 絞り込み記録 ===========================
S07 = "07_絞り込み記録"
ws7 = wb.create_sheet(S07)
header(ws7, 1, ["絞り込みID", "区分", "結果事象ID", "結果事象", "採用重大度", "除外した経路（原因事象ID）", "第1段参照ID", "除外した経路の頻度（仮値込み）", "理由", "代表する結果事象・経路", "受講生判断（採用／修正／除外／要確認）"],
       [10, 18, 10, 50, 8, 34, 26, 13, 58, 30, 16])
dv7 = DataValidation(type="list", formula1='"採用,修正,除外,要確認"', allow_blank=True)
ws7.add_data_validation(dv7)
for i, sc in enumerate(SCREEN, 2):
    r, p = sc["r"], sc["p"]
    put(ws7, i, 1, f"SC-{i - 1:05d}"); put(ws7, i, 2, sc["kind"], fill=GRY); put(ws7, i, 3, r["id"]); put(ws7, i, 4, r["text"])
    put(ws7, i, 5, r["sev0"], "0")
    if p is None:
        put(ws7, i, 6, f"結果事象全体（{len(byR0[r['id']])}経路）"); put(ws7, i, 7, "、".join(r["refs"]))
        put(ws7, i, 8, sum(q["H0"] for q in byR0[r["id"]]), FREQFMT)
    else:
        put(ws7, i, 6, "＋".join(f"{c['id']}｜{c['text'][:40]}" for c, _ in p["causes"]) + f"（{p['group']['id']}経由）")
        put(ws7, i, 7, "、".join([sid for _, sid in p["causes"]] + [p["rsid"]]))
        put(ws7, i, 8, p["H0"], FREQFMT)
    put(ws7, i, 9, sc["reason"]); put(ws7, i, 10, sc["rep"]); put(ws7, i, 11, None)
    dv7.add(f"K{i}")
L7 = 1 + len(SCREEN)
ws7.freeze_panes = "D2"
ws7.auto_filter.ref = f"A1:K{L7}"
cnt7 = Counter(sc["kind"] for sc in SCREEN)
r0 = L7 + 2
ws7.cell(row=r0, column=1, value="絞り込みの集計").font = F9B
summ = [("絞り込み前の経路数", N_BEFORE_P), ("絞り込み後の経路数（04シート）", len(paths)), ("絞り込み前の結果事象数（経路あり）", N_BEFORE_R),
        ("絞り込み後の結果事象数（04シート）", len(order))] + [(f"区分：{k}", v) for k, v in cnt7.items()] + \
       [("絞り込みで全経路を失い原因未確定となった結果事象", sum(1 for r in RL if r.get("lost")))]
for j, (a_, v_) in enumerate(summ, r0 + 1):
    ws7.cell(row=j, column=2, value=a_).font = F9
    ws7.cell(row=j, column=3, value=v_).font = F9B
ws7.cell(row=j + 2, column=2, value=("絞り込みの方針：第1段の網羅的な洗い出しは保持し、第2段で物理的な成立性・重複・代表性・重大度に基づいて検討対象を絞った。"
                                     "除外は削除ではなく本シートに理由と代表シナリオを記録しており、受講生レビューで復帰（採用）できる。")).font = NOTE

wb._sheets = [wb[n] for n in ["01_第2段プロンプト", S02, S03, S04, S05, S06, S07]]
wb.save(OUT)
print("causes", len(CL_), "results", len(RL), "paths", len(paths), "rows", LAST4 - HR, "unlinked", sum(1 for x in RL if x["adopted"] and not byR[x["id"]]))
print(Counter(r_["risk"] for r_ in order).most_common())
print(Counter(f for p in paths for f in p["flags"]))
