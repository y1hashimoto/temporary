# -*- coding: utf-8 -*-
"""HAZOP 第3段ワークブックの生成"""
import sys
import re
import time
from collections import defaultdict, Counter, OrderedDict
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.formatting.rule import FormulaRule, CellIsRule
import stage3_model as M
import stage3_opt as O

STAGE2, OUT = sys.argv[1], sys.argv[2]
LOG = []
log = lambda s: (LOG.append(s), print(s))

RES_ALL = M.load_stage2(STAGE2)
inst = M.build_catalog(RES_ALL)
M.attach_mitigation(RES_ALL, inst)
# 安全／操業損失の分離：人身・環境の影響がなく、漏洩・火災・爆発・死傷・汚染を含まない結果事象を「操業損失」とする
LOCRE = re.compile(r"漏洩|漏入|放出|火災|爆発|破裂|火球|BLEVE|蒸気雲|流出|噴出|溢流|溢出|着火|火炎|焼損|死亡|重傷|傷害|凍傷|熱傷|汚染|酸素欠乏")
for r in RES_ALL.values():
    r["cat"] = "操業損失" if ("人身" not in r["kinds"] and "環境" not in r["kinds"] and not LOCRE.search(r["text"])) else "安全"
res = OrderedDict((k, v) for k, v in RES_ALL.items() if v["cat"] == "安全")
RO = OrderedDict((k, v) for k, v in RES_ALL.items() if v["cat"] == "操業損失")
log(f"safety {len(res)} operational {len(RO)}")
ACC = M.ACC_PROV   # 依頼により暫定基準を採用（組織基準は参考比較）
infoA = O.solve(res, inst, ACC, "A", log)
infoB = O.solve(res, inst, ACC, "B", log)
# 参考：組織基準（重大度マトリクスの受容可能頻度）での選定
for r in res.values():
    r.pop("status0", None)
infoPA = O.solve(res, inst, M.ACC_ORG, "A", log)
infoPB = O.solve(res, inst, M.ACC_ORG, "B", log)
O.prepare(res, inst, ACC)   # 採用基準（暫定基準）の状態へ戻す
selA, selB = set(infoA["sel"]), set(infoB["sel"])


# ---------- 比較用の貪欲法（採用判断には使わない） ----------
def greedy(mode):
    targets = [r for r in res.values() if r.get("status0") == "対策で受容可能"]
    cost = {k: inst[k]["ini"] + 10 * inst[k]["ann"] for k in inst if inst[k]["f"]}
    sel = set()

    def fr(r):
        return sum(p["H"] * M.path_factor([k for k, c, _ in p["app"] if c and k in sel], inst) for p in r["paths"])
    cur = {r["id"]: fr(r) for r in targets}
    byk = defaultdict(list)
    for r in targets:
        for p in r["paths"]:
            for k, c, _ in p["app"]:
                if c:
                    byk[k].append(r)
    while True:
        bad = {rid for rid, v in cur.items() if v > res[rid]["A"] * (1 + 1e-9)}
        if not bad:
            break
        best, bs = None, 0
        for k, rs in byk.items():
            if k in sel:
                continue
            sel.add(k)
            red = 0.0
            for r in {id(x): x for x in rs}.values():
                if r["id"] in bad:
                    red += max(0.0, min(cur[r["id"]], res[r["id"]]["A"] * 1e3) - fr(r)) / res[r["id"]]["A"]
            sel.discard(k)
            sc = red / (cost[k] if mode == "B" else 1)
            if sc > bs:
                best, bs = k, sc
        if best is None:
            break
        sel.add(best)
        for r in {id(x): x for x in byk[best]}.values():
            cur[r["id"]] = fr(r)
    return dict(count=len(sel), cost=sum(cost[k] for k in sel), ok=not any(v > res[rid]["A"] * (1 + 1e-9) for rid, v in cur.items()))


t0 = time.time()
gA, gB = greedy("A"), greedy("B")
log(f"greedy A {gA} B {gB} {time.time() - t0:.1f}s")
infoOA = O.solve(RO, inst, ACC, "B", log, fixed=frozenset(selA))
infoOB = O.solve(RO, inst, ACC, "B", log, fixed=frozenset(selB))
opA, opB = set(infoOA["sel"]), set(infoOB["sel"])
log(f"operational add-on: baseA {len(opA)} {infoOA['cost']:.1f} / baseB {len(opB)} {infoOB['cost']:.1f}")

# ---------- 対策番号の採番 ----------
freqm = [k for k in inst if inst[k]["f"]]
freqm.sort(key=lambda k: (inst[k]["f"], -len(inst[k]["paths"]), -len(inst[k]["results"]), k[0], k[1]))
mitig = [k for k in inst if not inst[k]["f"]]
ORDER = freqm + mitig
NO = {k: i + 1 for i, k in enumerate(ORDER)}
NCAT = len(ORDER)


def status(k):
    a, b = k in selA, k in selB
    return "両案で採用" if a and b else "対策数最少案のみで採用" if a else "コスト最少案のみで採用" if b else "いずれの案でも未採用"


FN = "Meiryo"
thin = Side(style="thin", color="A0A0A0")
BD = Border(left=thin, right=thin, top=thin, bottom=thin)
HF = PatternFill("solid", fgColor="1F3864")
HFONT = Font(name=FN, bold=True, color="FFFFFF", size=9)
F9 = Font(name=FN, size=9)
F9B = Font(name=FN, size=9, bold=True)
REDF = Font(name=FN, size=9, bold=True, color="C00000")
WR = Alignment(wrap_text=True, vertical="top")
CEN = Alignment(wrap_text=True, vertical="center", horizontal="center")
ST_FILL = {"両案で採用": PatternFill("solid", fgColor="E2EFDA"), "対策数最少案のみで採用": PatternFill("solid", fgColor="DDEBF7"),
           "コスト最少案のみで採用": PatternFill("solid", fgColor="FCE4E4"), "いずれの案でも未採用": PatternFill("solid", fgColor="EDEDED")}
RED = PatternFill("solid", fgColor="F8CBAD")
YEL = PatternFill("solid", fgColor="FFF2CC")
OPF = PatternFill("solid", fgColor="FFE699")   # 操業損失の追加対策
HATCH = PatternFill(patternType="lightUp", fgColor="C00000", bgColor="FFFFFF")
FREQ = '0.0E+00" /年"'
MONEY = '#,##0.0" 百万円"'
MONEYY = '#,##0.0" 百万円/年"'
FRAC = '?/???'
S02, S03, S04, S05, S06, S07, S08 = ("02_対策カタログ", "03_経路別対策_対策数最少案", "04_経路別対策_コスト最少案", "05_二方式比較・採用対策集計",
                                     "06_対策共通性マトリクス", "07_未達・要確認・追加検討", "08_受容基準・適用関係")
Q = lambda s: f"'{s}'"


def put(ws, r, j, v, fmt=None, fill=None, font=F9, al=WR):
    c = ws.cell(row=r, column=j, value=v)
    c.font = font; c.alignment = al; c.border = BD
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


def header(ws, heads, widths, h=48):
    for j, (t, w) in enumerate(zip(heads, widths), 1):
        c = ws.cell(row=1, column=j, value=t)
        c.font = HFONT; c.fill = HF; c.alignment = CEN; c.border = BD
        ws.column_dimensions[CL(j)].width = w
    ws.row_dimensions[1].height = h


def frac(f):
    return {1 / 3: "1/3", 1 / 10: "1/10", 1 / 30: "1/30", 1 / 100: "1/100"}.get(f, "—")


def mname(k):
    return f"【{NO[k]}】{inst[k]['name']}"


wb = Workbook()
# =================== 01 ===================
ws = wb.active
ws.title = "01_第3段プロンプト"
ws.column_dimensions["A"].width = 150
ws.cell(row=1, column=1, value="第3段プロンプト（改訂版：重大度低減・安全／操業損失の分離・共通原因と閉鎖系の候補網羅・未達時のギャップ分析を反映）").font = HFONT
ws["A1"].fill = HF
for i, ln in enumerate(open("prompt3_v2.txt", encoding="utf-8").read().rstrip("\n").split("\n"), 2):
    c = ws.cell(row=i, column=1, value=ln or None)
    c.font = Font(name=FN, size=10, bold=ln.startswith("#"))
    c.alignment = Alignment(wrap_text=True, vertical="top")
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:A{i}"

# =================== 08（参照先） ===================
ws8 = wb.create_sheet(S08)
header(ws8, ["経路ID", "結果事象ID", "対策番号", "対策名称", "適用ゾーン", "判定（有効／要確認）", "結果事象×対策の初出（1）", "備考", "区分（安全／操業損失）",
             "重大度レベル", "受容年間発生頻度（採用：プロンプト暫定基準）", "参考：組織基準（重大度マトリクス）"], [11, 11, 8, 40, 14, 12, 10, 50, 10, 10, 16, 16])
for i, s_ in enumerate(range(1, 6), 2):
    put(ws8, i, 10, s_, "0"); put(ws8, i, 11, ACC[s_], FREQ, YEL); put(ws8, i, 12, M.ACC_ORG[s_], FREQ)
put(ws8, 7, 10, "根拠"); put(ws8, 7, 11, "第3段プロンプトの暫定基準（演習依頼者の指示により採用）")
put(ws8, 7, 12, "重大度マトリクスの『受容可能な事故発生頻度』（100倍厳しい。参考比較のみ）")
for j, (t, w) in enumerate([("重大度低減の対象：結果事象ID", 12), ("重大度低減対策の番号", 10), ("低減する側面", 10)], 14):
    c = ws8.cell(row=1, column=j, value=t); c.font = HFONT; c.fill = HF; c.alignment = CEN; c.border = BD
    ws8.column_dimensions[CL(j)].width = w
ACCR = f"{Q(S08)}!$K$2:$K$6"
r8 = 2
seen = set()
for r in RES_ALL.values():
    for p in r["paths"]:
        for k, cred, note in p["app"]:
            fl = 0
            if cred and (r["id"], k) not in seen:
                seen.add((r["id"], k)); fl = 1
            for j, v in enumerate([p["pid"], r["id"], NO[k], inst[k]["name"], M.ZSH[k[1]], "有効" if cred else "要確認", fl, note, r["cat"]], 1):
                c = ws8.cell(row=r8, column=j, value=v); c.font = F9
            r8 += 1
LAST8 = r8 - 1
rm = 2
for r in RES_ALL.values():
    for k in r.get("Mit", []):
        for j, v in enumerate([r["id"], NO[k], {"S": "人身・安全", "E": "環境", "B": "ビジネス"}[M.MIT_RULES[k[0]][0]]], 14):
            ws8.cell(row=rm, column=j, value=v).font = F9
        rm += 1
LASTM = max(rm - 1, 2)
ws8.freeze_panes = "A2"
ws8.auto_filter.ref = f"A1:I{LAST8}"
APP_B, APP_C, APP_F, APP_G, APP_I = (f"{Q(S08)}!${c}$2:${c}${LAST8}" for c in "BCFGI")

# =================== 02 対策カタログ ===================
ws2 = wb.create_sheet(S02, 1)
h2 = ["対策番号", "対策名称", "適用ゾーン", "対策の種類", "遮断または作用する物理的位置", "対象原因事象ID", "対象中間事象または対象パス", "対象結果事象ID",
      "有効な経路数", "有効な結果事象数", "残余頻度倍率", "独立性クラス", "独立性・共通原因故障の評価", "効果設定の根拠・演習上の仮定",
      "初期投資額（百万円）", "年間ランニングコスト（百万円／年）", "10年分ランニングコスト（百万円）", "10年必要コスト（百万円）",
      "対策数最少案での採用状態", "コスト最少案での採用状態", "総合採用状態", "要確認・追加情報", "レビューコメント", "内部キー"]
header(ws2, h2, [7, 42, 13, 11, 34, 28, 26, 30, 8, 8, 8, 12, 48, 44, 11, 11, 11, 12, 11, 11, 16, 40, 16, 12])
IND = {}
for k in ORDER:
    m = inst[k]
    if not m["f"]:
        IND[k] = ("頻度低減には計上せず、対象結果事象の重大度を1段階低減する（" + M.MIT_RULES[k[0]][3] + "）。複数の重大度低減対策の重ね掛けはせず、1段階までとした。"
                  if k[0] in M.MIT_RULES else "頻度・重大度のいずれにも計上しない（第2段で放圧装置の要求時失敗を仮定済みのため二重計上となる）")
    elif m["cls"].startswith("SIS-Z"):
        IND[k] = (f"専用センサー・専用遮断弁・BPCSと独立したSIS論理を前提に、BPCSの計器・制御弁とは独立と評価。同一ゾーンのSIFは論理演算器・遮断弁の共用可能性があるため同一クラス（{m['cls']}）として積をとらない。"
                  "計装空気・電源喪失を原因とする経路では遮断弁・電源の共通依存の可能性があるため要確認として計算から除外。")
    elif m["cls"] == "ESD":
        IND[k] = ("フェイルセーフ設計（電源・計装空気の喪失で安全側へ作動）、専用UPS、BPCSから独立した論理を前提に、計装空気・電源・冷却水・制御系の喪失を原因とする経路にも独立に作用すると評価。"
                  "個別SIS（SIS-Z*）とは遮断弁を共用しない前提。共用する場合は同一クラスとして単一効果のみとする（要確認）。")
    elif m["cls"] in ("閉鎖系SIS", "保全隔離"):
        IND[k] = f"{m['cls']}：専用の検出器・遮断手段を前提に、上流機器のBPCS・SISとは作用位置が異なるため独立と評価。計装空気・電源喪失を原因とする経路では要確認として計算から除外。"
    elif m["cls"] == "H-01燃料遮断弁":
        IND[k] = "SIS-H01F（H-01コイル低流量・出口高温）とSIS-R01T（R-01高温）は同一のH-01燃料遮断弁に依存するため、同一経路では積をとらず単一効果のみ。"
    elif m["cls"] in ("BMS", "K-02機械保護"):
        IND[k] = f"{m['cls']}は専用の検出器・遮断手段を前提に独立と評価（設計確認が必要）。"
    else:
        alts = sorted({inst[x]["name"].split("（")[0] for x in inst if inst[x]["cls"] == m["cls"] and x[0] != k[0] and inst[x]["f"]})[:4]
        IND[k] = (f"独立性クラス『{m['cls']}』。同クラスの対策（{'、'.join(alts)}等）と同一経路に重なる場合は同一の保全活動・運転班・計器等への依存があるため単一効果のみ。"
                  "異なるクラス（SIS、他の原因に作用する対策）とは作用位置・作用原理が異なるため独立と仮定。")
for i, k in enumerate(ORDER, 2):
    m = inst[k]
    st = status(k)
    fill = ST_FILL[st]
    cids = sorted(m["causes"]); rids = sorted(m["results"])
    put(ws2, i, 1, NO[k], "0", fill, F9B)
    put(ws2, i, 2, mname(k), fill=fill, font=F9B)
    put(ws2, i, 3, M.ZSH[k[1]]); put(ws2, i, 4, m["kind"]); put(ws2, i, 5, m["pos"])
    put(ws2, i, 6, ("、".join(cids[:15]) + (f" ほか{len(cids) - 15}件" if len(cids) > 15 else "")) if cids else ("—（偏差位置で作用）" if m["f"] else "—"))
    put(ws2, i, 7, ("偏差：" + "、".join(sorted(m["groups"]))) if m["groups"] else (f"対象原因を含む経路（{len(m['paths'])}経路）" if m["f"] else m["pos"]))
    put(ws2, i, 8, ("、".join(rids[:12]) + (f" ほか{len(rids) - 12}件（06シート参照）" if len(rids) > 12 else "")) if rids else "—")
    put(ws2, i, 9, f'=COUNTIFS({APP_C},A{i},{APP_F},"有効",{APP_I},"安全")', "0")
    put(ws2, i, 10, f'=COUNTIFS({APP_C},A{i},{APP_F},"有効",{APP_G},1,{APP_I},"安全")', "0")
    if m["f"]:
        put(ws2, i, 11, m["f"], FRAC, font=F9B)
    else:
        put(ws2, i, 11, "頻度は計上しない（重大度1段階低減）" if k[0] in M.MIT_RULES else "計上しない")
    put(ws2, i, 12, m["cls"]); put(ws2, i, 13, IND[k]); put(ws2, i, 14, m["why"])
    put(ws2, i, 15, m["ini"], MONEY); put(ws2, i, 16, m["ann"], MONEYY)
    put(ws2, i, 17, f"=10*P{i}", MONEY); put(ws2, i, 18, f"=O{i}+10*P{i}", MONEY, font=F9B)
    put(ws2, i, 19, "採用" if k in selA else "未採用"); put(ws2, i, 20, "採用" if k in selB else "未採用")
    put(ws2, i, 21, f'=IF(AND(S{i}="採用",T{i}="採用"),"両案で採用",IF(S{i}="採用","対策数最少案のみで採用",IF(T{i}="採用","コスト最少案のみで採用","いずれの案でも未採用")))',
        fill=fill, font=F9B)
    need = []
    if m["f"] == 1 / 100:
        need.append("効果1/100の根拠（SIL検証・専用遮断弁の設置可否）を要確認" if m["kind"] == "伝播遮断" else "効果1/100の根拠が弱い（演習仮定）")
    if m["kind"] == "伝播遮断":
        need.append("BPCSの既存計器・制御弁との共用不可（共用すると二重計上）")
    if m["f"] and not m["paths"]:
        need.append("頻度計算上で有効な経路なし（要確認経路のみ）")
    if not m["f"]:
        need.append("重大度1段階低減の根拠（検知・隔離時間、耐火時間、建屋耐爆性能、貯留容量）を要確認" if k[0] in M.MIT_RULES else "頻度・重大度に計上しない（二重計上防止）")
    put(ws2, i, 22, "／".join(need) or None, fill=RED if need and m["f"] else None, font=REDF if need and m["f"] else F9)
    put(ws2, i, 23, None)
    put(ws2, i, 24, f"{k[0]}@Z{k[1]}")
    put(ws2, i, 25, f'=COUNTIFS({APP_C},A{i},{APP_F},"有効",{APP_I},"操業損失")', "0")
    put(ws2, i, 26, "追加採用" if k in opB else ("安全対策で採用済" if k in selB and any(k == kk for r in RO.values() for p in r["paths"] for kk, c, _ in p["app"] if c) else "—"),
        fill=OPF if k in opB else None)
LAST2 = 1 + len(ORDER)
ws2.freeze_panes = "C2"
for i, k in enumerate(ORDER, 2):
    put(ws2, i, 27, f"=COUNTIF({Q(S08)}!$O$2:$O${LASTM},A{i})" if k[0] in M.MIT_RULES else None, "0")
    put(ws2, i, 28, M.MIT_RULES[k[0]][3] if k[0] in M.MIT_RULES else None)
for j, (t, w) in enumerate([("操業損失で有効な経路数", 9), ("操業損失の追加対策（案B基準、09・10シート）", 16), ("重大度低減の対象結果事象数", 9), ("重大度低減の内容", 40)], 25):
    c = ws2.cell(row=1, column=j, value=t); c.font = HFONT; c.fill = PatternFill("solid", fgColor="7F6000"); c.alignment = CEN; c.border = BD
    ws2.column_dimensions[CL(j)].width = w
ws2.auto_filter.ref = f"A1:AB{LAST2}"
CAT_A, CAT_K, CAT_J = (f"{Q(S02)}!${c}$2:${c}${LAST2}" for c in "AKJ")

# =================== 03 / 04 ===================
NSLOT = 6
CNT_SLOTS = Counter()


def path_sheet(title, sel, plan, resset=None, extra=frozenset()):
    resset = res if resset is None else resset
    ws = wb.create_sheet(title)
    heads = ["結果事象番号", "結果事象", "結果発生ゾーン", "重大度", "リスク種類", "受容年間発生頻度（/年）", "対策前の結果事象年間発生頻度（/年）",
             "対策前の当該AND経路成立頻度（/年）", "対策後の当該AND経路成立頻度（/年）", "対策後の結果事象年間発生頻度（/年）", "受容可否", "未達時の区分（全候補での到達可否）"]
    for n in range(1, NSLOT + 1):
        heads += [f"対策{n}", f"対策{n}の適用ゾーン", f"対策{n}の残余頻度倍率"]
    heads += ["原因ゾーンから結果ゾーンへの物理的伝播経路", "対策が遮断する位置", "独立性・共通原因故障の扱い", "計算上の仮定", "レビューコメント", "要確認区分",
              "結果事象ID", "経路ID", "塊の先頭（1）"] + [f"計上対策番号{n}" for n in range(1, NSLOT + 1)] + ["共通対策の適用（1）", "塊内で共通対策あり（1）", "重大度低減対策（採用、事故進展抑制・被害軽減）", "低減後の重大度（受容頻度の判定に使用）"]
    widths = [8, 40, 12, 6, 12, 11, 12, 12, 12, 12, 8, 16] + [26, 10, 8] * NSLOT + [40, 36, 44, 30, 14, 22, 9, 9, 6] + [6] * NSLOT + [7, 7, 34, 9]
    header(ws, heads, widths, 60)
    fcols = [CL(13 + 3 * n + 2) for n in range(NSLOT)]   # O,R,U,X,AA,AD
    c_pr, c_ass, c_rid, c_pid, c_head = 31, 34, 37, 38, 39
    c_n0 = 40
    c_com, c_bcom = c_n0 + NSLOT, c_n0 + NSLOT + 1
    c_mit, c_sev2 = c_bcom + 1, c_bcom + 2
    r = 2
    blocks = []
    for res_ in resset.values():
        plist = res_["paths"] or [None]
        s0, e0 = r, r + len(plist) - 1
        blocks.append((res_["id"], s0, e0))
        for idx, p in enumerate(plist):
            put(ws, r, 1, res_["no"], "0", font=F9B); put(ws, r, 2, res_["text"]); put(ws, r, 3, res_["zone"])
            put(ws, r, 4, res_["S"], "0"); put(ws, r, 5, res_["kinds"])
            mits = [k for k in res_.get("Mit", []) if k in sel or k in extra]
            put(ws, r, c_mit, "、".join(mname(k) for k in sorted(mits, key=lambda k: NO[k])) or None,
                fill=(OPF if all(k in extra and k not in sel for k in mits) else ST_FILL[status(mits[0])]) if mits else None)
            put(ws, r, c_sev2, f'=IF({CL(c_mit)}{r}="",D{r},MAX(1,D{r}-1))', "0", font=F9B if mits else F9)
            put(ws, r, 6, f"=INDEX({ACCR},{CL(c_sev2)}{r})", FREQ)
            put(ws, r, 7, f"=SUM($H${s0}:$H${e0})", FREQ)
            put(ws, r, 10, f"=SUM($I${s0}:$I${e0})", FREQ, font=F9B)
            put(ws, r, 11, f'=IF(J{r}<=F{r}*(1+1E-9),"受容","未達")', font=F9B, al=CEN)
            st0 = res_.get("status0", "")
            put(ws, r, 12, {"追加検討が必要": "追加検討が必要（全候補を採用しても未達）", "原因未確定": "原因未確定（第2段から継承）", "重大度低減との組合せで受容可能": "重大度低減との組合せで受容可能"}.get(st0, "全候補で受容可能" if st0 == "対策で受容可能" else "対策前に受容"),
                fill=RED if st0 in ("追加検討が必要", "原因未確定") else None)
            put(ws, r, c_rid, res_["id"]); put(ws, r, c_head, 1 if idx == 0 else 0, "0")
            if p is None:
                put(ws, r, 8, 0, FREQ); put(ws, r, 9, f"=H{r}", FREQ)
                for j in range(13, 13 + 3 * NSLOT):
                    put(ws, r, j, None)
                put(ws, r, c_pr, "—（原因未確定）"); put(ws, r, 32, "—"); put(ws, r, 33, "—")
                put(ws, r, c_ass, "原因未確定のため頻度を算定できない。0と表示しているが実頻度が0という意味ではない")
                put(ws, r, 35, None); put(ws, r, 36, "要確認：原因未確定", fill=RED, font=REDF)
                put(ws, r, c_pid, None)
                for j in range(NSLOT):
                    put(ws, r, c_n0 + j, None)
                put(ws, r, c_com, 0, "0")
                r += 1
                continue
            put(ws, r, 8, p["H"], FREQ)
            put(ws, r, 9, f"=H{r}*PRODUCT(1,{','.join(f'{c}{r}' for c in fcols)})", FREQ, font=F9B)
            # 適用される採用対策
            app = []
            for k, cred, note in p["app"]:
                if (k in sel or k in extra) and all(k != a[0] for a in app):
                    app.append((k, cred, note))
            app.sort(key=lambda a: NO[a[0]])
            # 同一クラス：最小倍率の1件のみ計上
            credited = [a for a in app if a[1]]
            bycls = defaultdict(list)
            for a in credited:
                bycls[inst[a[0]]["cls"]].append(a[0])
            keep = {min(v, key=lambda x: (inst[x]["f"], NO[x])) for v in bycls.values()}
            CNT_SLOTS[len(app)] += 1
            notes_ind, pos = [], []
            nums = []
            for n in range(NSLOT):
                col = 13 + 3 * n
                if n < len(app):
                    k, cred, note = app[n]
                    fill = OPF if (k in extra and k not in sel) else ST_FILL[status(k)]
                    put(ws, r, col, mname(k), fill=fill)
                    put(ws, r, col + 1, M.ZSH[k[1]], fill=fill)
                    if not cred:
                        put(ws, r, col + 2, "要確認（計算除外）", fill=HATCH, font=REDF)
                        notes_ind.append(f"【{NO[k]}】{note}")
                    elif k not in keep:
                        put(ws, r, col + 2, "従属（単一効果のみ）", fill=HATCH, font=REDF)
                        other = [x for x in keep if inst[x]["cls"] == inst[k]["cls"]][0]
                        notes_ind.append(f"【{NO[k]}】は【{NO[other]}】と同一クラス（{inst[k]['cls']}）のため倍率を計上しない")
                    else:
                        put(ws, r, col + 2, f"=INDEX({CAT_K},MATCH({NO[k]},{CAT_A},0))", FRAC, fill=fill, font=F9B)
                        nums.append(NO[k])
                    pos.append(f"【{NO[k]}】{inst[k]['pos']}")
                else:
                    for j in range(3):
                        put(ws, r, col + j, None)
            if len(app) > NSLOT:
                notes_ind.append(f"適用対策が{len(app)}件あり、{NSLOT}件を超える分は表示していない（計算にも含めない：保守側）")
            if len(keep) >= 2:
                notes_ind.insert(0, "計上した対策は作用位置・独立性クラスが異なるため倍率の積をとった：" + "、".join(f"【{NO[x]}】({inst[x]['cls']})" for x in sorted(keep, key=lambda x: NO[x])))
            put(ws, r, c_pr, p["route"])
            put(ws, r, 32, "／".join(pos) if pos else "採用対策なし")
            fl = [f for f in p["flags"].replace("要確認：", "").split("・") if f]
            if any(x in fl for x in ("共通原因", "重複経路", "重複計上")):
                notes_ind.append("第2段の要確認（" + "・".join(fl) + "）を継承：OR和・積は確定値ではない")
            put(ws, r, 33, "／".join(notes_ind) if notes_ind else ("採用対策なし" if not app else "単一対策のみ計上"),
                fill=RED if any(not a[1] for a in app) or (app and len(keep) < len(credited)) else None)
            put(ws, r, c_ass, "対策前頻度は第2段の当該AND経路成立頻度（必要条件の仮値を含む）を変更せず使用。残余頻度倍率は演習仮定。被害軽減・事故進展抑制は計上しない。概略評価。")
            put(ws, r, 35, None)
            newfl = []
            if any(not a[1] for a in app):
                newfl.append("共通原因（SIS計算除外）")
            if app and len(keep) < len(credited):
                newfl.append("従属対策")
            allfl = fl + newfl
            put(ws, r, 36, ("要確認：" + "・".join(allfl)) if allfl else None, fill=RED if allfl else None, font=REDF if allfl else F9)
            put(ws, r, c_pid, p["pid"])
            for j in range(NSLOT):
                put(ws, r, c_n0 + j, nums[j] if j < len(nums) else None, "0")
            put(ws, r, c_com, f'=IF(SUMPRODUCT(COUNTIFS({CAT_A},{CL(c_n0)}{r}:{CL(c_n0 + NSLOT - 1)}{r},{CAT_J},">=2"))>0,1,0)', "0")
            r += 1
        put(ws, s0, c_bcom, f"=MAX({CL(c_com)}{s0}:{CL(c_com)}{e0})", "0")
        for rr in range(s0 + 1, e0 + 1):
            put(ws, rr, c_bcom, None)
        for j in range(1, c_sev2 + 1):
            c = ws.cell(row=e0, column=j)
            c.border = Border(left=thin, right=thin, top=thin, bottom=Side(style="medium", color="1F3864"))
    last = r - 1
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:{CL(c_sev2)}{last}"
    ws.conditional_formatting.add(f"K2:K{last}", CellIsRule(operator="equal", formula=['"未達"'], fill=RED, font=REDF))
    ws.conditional_formatting.add(f"J2:J{last}", FormulaRule(formula=["$K2=\"未達\""], fill=RED))
    return ws, last, c_head, c_com, c_bcom, c_mit


ws3, LAST3, CH, CC, CB, CM = path_sheet(S03, selA, "A")
ws4, LAST4, _, _, _, _ = path_sheet(S04, selB, "B")
log(f"slots {sorted(CNT_SLOTS.items())}")

# =================== 05 比較 ===================
ws5 = wb.create_sheet(S05)
header(ws5, ["比較項目", "案A：全体対策数最少案", "案B：全体コスト最少案", "差（B−A）", "備考"], [40, 46, 46, 14, 60])
HEADC, KC, LC, COMC, BCOMC, CMC = CL(CH), "K", "L", CL(CC), CL(CB), CL(CM)
rows5 = [
    ("採用対策数", f'=COUNTIF({Q(S02)}!$S$2:$S${LAST2},"採用")', f'=COUNTIF({Q(S02)}!$T$2:$T${LAST2},"採用")', "0", "02シートの採用状態から集計"),
    ("初期投資合計", f'=SUMIF({Q(S02)}!$S$2:$S${LAST2},"採用",{Q(S02)}!$O$2:$O${LAST2})', f'=SUMIF({Q(S02)}!$T$2:$T${LAST2},"採用",{Q(S02)}!$O$2:$O${LAST2})', MONEY, ""),
    ("年間ランニングコスト合計", f'=SUMIF({Q(S02)}!$S$2:$S${LAST2},"採用",{Q(S02)}!$P$2:$P${LAST2})', f'=SUMIF({Q(S02)}!$T$2:$T${LAST2},"採用",{Q(S02)}!$P$2:$P${LAST2})', MONEYY, ""),
    ("10年分ランニングコスト合計", f'=SUMIF({Q(S02)}!$S$2:$S${LAST2},"採用",{Q(S02)}!$Q$2:$Q${LAST2})', f'=SUMIF({Q(S02)}!$T$2:$T${LAST2},"採用",{Q(S02)}!$Q$2:$Q${LAST2})', MONEY, ""),
    ("10年必要コスト合計", f'=SUMIF({Q(S02)}!$S$2:$S${LAST2},"採用",{Q(S02)}!$R$2:$R${LAST2})', f'=SUMIF({Q(S02)}!$T$2:$T${LAST2},"採用",{Q(S02)}!$R$2:$R${LAST2})', MONEY, "割引なし（初期投資＋10×年間ランニング）"),
    ("受容頻度以下を達成した結果事象数", f'=COUNTIFS({Q(S03)}!${HEADC}$2:${HEADC}${LAST3},1,{Q(S03)}!$K$2:$K${LAST3},"受容")',
     f'=COUNTIFS({Q(S04)}!${HEADC}$2:${HEADC}${LAST4},1,{Q(S04)}!$K$2:$K${LAST4},"受容")', "0", "原因未確定（頻度0表示）を含む"),
    ("未達の結果事象数", f'=COUNTIFS({Q(S03)}!${HEADC}$2:${HEADC}${LAST3},1,{Q(S03)}!$K$2:$K${LAST3},"未達")',
     f'=COUNTIFS({Q(S04)}!${HEADC}$2:${HEADC}${LAST4},1,{Q(S04)}!$K$2:$K${LAST4},"未達")', "0", "下行の『全候補でも未達』を含む"),
    ("　うち全候補を採用しても未達（追加検討が必要）", f'=COUNTIFS({Q(S03)}!${HEADC}$2:${HEADC}${LAST3},1,{Q(S03)}!$L$2:$L${LAST3},"追加検討*")',
     f'=COUNTIFS({Q(S04)}!${HEADC}$2:${HEADC}${LAST4},1,{Q(S04)}!$L$2:$L${LAST4},"追加検討*")', "0", "07シートに一覧"),
    ("重大度低減対策（事故進展抑制・被害軽減）の採用数", f'=COUNTIFS({Q(S02)}!$S$2:$S${LAST2},"採用",{Q(S02)}!$K$2:$K${LAST2},"頻度は計上しない*")',
     f'=COUNTIFS({Q(S02)}!$T$2:$T${LAST2},"採用",{Q(S02)}!$K$2:$K${LAST2},"頻度は計上しない*")', "0", "採用対策数の内数"),
    ("重大度低減が適用され受容となった結果事象数（低減なしでも受容のものを含む）", f'=COUNTIFS({Q(S03)}!${HEADC}$2:${HEADC}${LAST3},1,{Q(S03)}!${CMC}$2:${CMC}${LAST3},"<>",{Q(S03)}!$K$2:$K${LAST3},"受容")',
     f'=COUNTIFS({Q(S04)}!${HEADC}$2:${HEADC}${LAST4},1,{Q(S04)}!${CMC}$2:${CMC}${LAST4},"<>",{Q(S04)}!$K$2:$K${LAST4},"受容")', "0", "低減後の重大度で受容頻度を判定"),
    ("共通対策によって防御される結果事象数", f'=COUNTIFS({Q(S03)}!${HEADC}$2:${HEADC}${LAST3},1,{Q(S03)}!${BCOMC}$2:${BCOMC}${LAST3},1)',
     f'=COUNTIFS({Q(S04)}!${HEADC}$2:${HEADC}${LAST4},1,{Q(S04)}!${BCOMC}$2:${BCOMC}${LAST4},1)', "0", "共通対策＝有効な結果事象数が2以上の採用対策"),
    ("共通対策によって防御される経路数", f'=COUNTIF({Q(S03)}!${COMC}$2:${COMC}${LAST3},1)', f'=COUNTIF({Q(S04)}!${COMC}$2:${COMC}${LAST4},1)', "0", ""),
]
for i, (lab, fa, fb, fmt, note) in enumerate(rows5, 2):
    put(ws5, i, 1, lab, font=F9B); put(ws5, i, 2, fa, fmt); put(ws5, i, 3, fb, fmt); put(ws5, i, 4, f"=C{i}-B{i}", fmt); put(ws5, i, 5, note)
r5 = 2 + len(rows5)
ida = "、".join(f"【{NO[k]}】" for k in sorted(selA, key=lambda k: NO[k]))
idb = "、".join(f"【{NO[k]}】" for k in sorted(selB, key=lambda k: NO[k]))
put(ws5, r5, 1, "採用対策ID一覧", font=F9B); put(ws5, r5, 2, ida); put(ws5, r5, 3, idb); put(ws5, r5, 4, None); put(ws5, r5, 5, "番号は02シートの対策番号")
big = [k for k in freqm if k not in selA and k not in selB and (inst[k]["f"] <= 1 / 30 or len(inst[k]["results"]) >= 20)]
big.sort(key=lambda k: (inst[k]["f"], -len(inst[k]["results"])))
txt = "、".join(f"{mname(k)}（{frac(inst[k]['f'])}、{len(inst[k]['results'])}結果）" for k in big[:25]) + (f" ほか{len(big) - 25}件" if len(big) > 25 else "")
r5 += 1
put(ws5, r5, 1, "未採用であるが効果が大きい対策一覧", font=F9B); put(ws5, r5, 2, txt); ws5.merge_cells(start_row=r5, start_column=2, end_row=r5, end_column=3)
put(ws5, r5, 5, "残余頻度倍率1/30以下、または20以上の結果事象に有効で、両案とも未採用の対策。採用されない理由：他の採用対策で受容頻度を満たすか、全候補でも未達の結果にのみ有効")
onlyA = sorted(selA - selB, key=lambda k: NO[k]); onlyB = sorted(selB - selA, key=lambda k: NO[k])
r5 += 1
cst = lambda ks: sum(inst[k]["ini"] + 10 * inst[k]["ann"] for k in ks)
desc = lambda ks: "、".join(f"{mname(k)}（{frac(inst[k]['f'])}、{cst([k]):.1f}百万円）" for k in ks) or "なし"
why = ("案Aのみで採用：" + desc(onlyA) + "。案Bのみで採用：" + desc(onlyB) + "。"
       + f"案Aは同じ原因・経路に対して低減効果の大きい対策1件で受容頻度を満たし、採用数を{len(selB) - len(selA)}件少なくした（10年コストは案Bより{cst(onlyA) - cst(onlyB):+.1f}百万円）。"
       + "案Bは効果の小さい安価な代替策を組み合わせて同じ制約を満たし、採用数は増えるが10年コストを下げた。"
       + f"両案に共通の{len(selA & selB)}件は、代替のない原因・偏差に対する唯一の手段、または複数の結果事象に共通して必要な対策である。")
if not onlyA and not onlyB:
    why = (f"両案は同一の対策集合（{len(selA)}件・{cst(selA):.1f}百万円）となった。対策数最少の解のうち10年コストが最小のもの（案Aの第2目的）が、"
           "コスト最少の解（案B）とも一致したため。安価な代替策（1/3）に置き換えると、必要な低減量を満たすために別の対策の追加が必要となり、件数・コストとも下がらない。"
           f"参考：貪欲法では対策数優先 {gA['count']}件・{gA['cost']:.1f}百万円、コスト効率優先 {gB['count']}件・{gB['cost']:.1f}百万円となり、いずれも最適化解より劣る。")
put(ws5, r5, 1, "両案の選定差の理由", font=F9B); put(ws5, r5, 2, why); ws5.merge_cells(start_row=r5, start_column=2, end_row=r5, end_column=3)
ws5.row_dimensions[r5].height = 120
r5 += 2
put(ws5, r5, 1, "選定方法の記録", font=F9B, fill=YEL)
method = [
    ("選定方法", "混合整数線形計画（HiGHS 1.16、相対ギャップ0）。経路ごとに『採用対策の組合せ』を補助変数で列挙し、結果事象ごとのOR和≦受容頻度を線形制約化。辞書式最適化（第1目的を解いて固定→第2目的＋第3目的の微小重み）。貪欲法は比較のみに使用。"),
    ("対策候補数（頻度計上可能）", f"{len(freqm)}件（うち最適化対象＝未受容かつ到達可能な結果事象に有効なもの {infoA['nbin']}件）。2^{infoA['nbin']}通りの組合せを分枝限定法で暗黙に評価"),
    ("最適化モデルの規模", f"変数 {infoA['nvar']:,}（二値 {infoA['nbin']}）、集約経路ユニット {infoA['nunits']:,}、制約対象の結果事象 {infoA['ntarget']}件"),
    ("求解状況（案A）", f"第1段 {infoA['status'][0]}（対策数 {infoA['count']}）→ 第2段 {infoA['status'][1]}、探索ノード {infoA['nodes']}、{infoA['secs']:.1f}秒"),
    ("求解状況（案B）", f"第1段 {infoB['status'][0]}（10年コスト {infoB['cost']:.1f}百万円）→ 第2段 {infoB['status'][1]}、探索ノード {infoB['nodes']}、{infoB['secs']:.1f}秒"),
    ("同点時の優先順位", "案A：対策数→10年コスト→重大度4以上の経路への適用数（多い方を優先）。案B：10年コスト→対策数→重大度4以上の経路への適用数。"),
    ("比較：貪欲法の結果", f"対策数優先の貪欲法 {gA['count']}件・{gA['cost']:.1f}百万円／コスト効率優先の貪欲法 {gB['count']}件・{gB['cost']:.1f}百万円（参考：貪欲法は頻度低減のみで、重大度低減との組合せで受容となる結果事象を含まない小さい問題を解いている）"),
    ("受容頻度の基準", "第3段プロンプトの暫定基準（S1:1E+0〜S5:1E-4 /年）を採用（演習依頼者の指示）。重大度マトリクスの『受容可能な事故発生頻度』（S1:1E-2〜S5:1E-6 /年、100倍厳しい）は参考比較のみ。"),
    ("参考：組織基準で選定した場合", f"案A {infoPA['count']}件・{infoPA['cost']:.1f}百万円、案B {infoPB['count']}件・{infoPB['cost']:.1f}百万円。全候補でも未達となる結果事象 {infoPA['nunach']}件（暫定基準では {infoA['nunach']}件）。"),
    ("対象範囲", f"安全の結果事象（人身・環境の影響、または漏洩・火災・爆発・死傷・汚染を含むもの）{len(res)}件を対象に選定。操業損失（品質・触媒・機器損傷・停止）{len(RO)}件は分離し、09・10シートで追加対策を別に評価した。"),
    ("候補の補完（ギャップ分析）", "前回の未達13件を分析し、共通原因経路に作用するフェイルセーフ型プラントESD、避雷・浸水対策、閉鎖ガス処理系の強化（ノックアウトドラムのインターロック、ヘッダのトレース、隔離弁の施錠管理、背圧監視・能力増強）、保全時の確実な隔離、フレアの無煙化、プラント全体の耐火被覆を候補に追加した。"
     "あわせて第2段で中間事象型の原因『上流機器の過充填』を上流各容器・塔の過充填経路へ結び直した。"),
    ("重大度低減の扱い", "事故進展抑制・被害軽減（ガス検知・ESD隔離、耐火被覆・散水、計器室耐爆化、防液堤・排水遮断、消火排水貯留、緊急時対応）は頻度を下げず、対象結果事象の重大度を1段階下げる（受容頻度は10倍に緩和）。"
     "対象は採用重大度を単独で決めている側面に作用する場合のみ、重ね掛けなし。放圧装置の容量検証は第2段の仮定との二重計上となるため計上しない。最適化では重大度低減の採否も同時に選定した。"),
    ("従属対策の扱い", "同一独立性クラスの対策が同一経路に重なる場合は倍率の積をとらず単一効果のみ計上（追加採用で計算上のリスクが増える逆転を避けるため、採用済みのうち1件の効果）。"),
    ("免責", "本成果は演習用の概略評価である。実設備への導入判断には、設計仕様、独立保護層の要件（SIL検証）、共通原因故障、保全性、詳細コスト、変更管理の追加確認が必要。"),
]
for j, (a, b) in enumerate(method, r5 + 1):
    put(ws5, j, 1, a, font=F9B); put(ws5, j, 2, b); ws5.merge_cells(start_row=j, start_column=2, end_row=j, end_column=5)
    ws5.row_dimensions[j].height = 36
ws5.freeze_panes = "B2"
ws5.auto_filter.ref = f"A1:E{2 + len(rows5) + 2}"

# =================== 06 共通性マトリクス ===================
ws6 = wb.create_sheet(S06)
cols6 = [k for k in freqm if inst[k]["results"] or any(not c for r in res.values() for p in r["paths"] for kk, c, _ in p["app"] if kk == k)]
heads6 = ["結果事象番号", "結果事象ID", "結果事象", "重大度", "全経路数"] + [NO[k] for k in cols6]
header(ws6, heads6, [7, 9, 40, 5, 6] + [6] * len(cols6), 30)
for j, k in enumerate(cols6, 6):
    c = ws6.cell(row=1, column=j); c.number_format = '"【"0"】"'; c.fill = ST_FILL[status(k)]; c.font = F9B
    c.alignment = Alignment(text_rotation=90, horizontal="center")
ws6.row_dimensions[1].height = 40
colj = {k: j for j, k in enumerate(cols6, 6)}
n6 = 0
for i, r in enumerate(res.values(), 2):
    put(ws6, i, 1, r["no"], "0"); put(ws6, i, 2, r["id"]); put(ws6, i, 3, r["text"]); put(ws6, i, 4, r["S"], "0")
    put(ws6, i, 5, f'=COUNTIF({Q(S03)}!$AK$2:$AK${LAST3},B{i})-COUNTIFS({Q(S03)}!$AK$2:$AK${LAST3},B{i},{Q(S03)}!$AL$2:$AL${LAST3},"")', "0")
    cnt = defaultdict(lambda: [0, 0])
    for p in r["paths"]:
        ks = {}
        for k, cred, _ in p["app"]:
            ks[k] = ks.get(k, False) or cred
        for k, cred in ks.items():
            cnt[k][0 if cred else 1] += 1
    for k, (ok_, ng) in cnt.items():
        if k not in colj:
            continue
        j = colj[k]
        h = CL(j)
        if ng:
            f = f'=COUNTIFS({APP_B},$B{i},{APP_C},{h}$1,{APP_F},"有効")&"／"&$E{i}&"（要確認）"'
            c = put(ws6, i, j, f, fill=HATCH, font=REDF, al=CEN)
        else:
            f = f'=COUNTIFS({APP_B},$B{i},{APP_C},{h}$1,{APP_F},"有効")&"／"&$E{i}'
            c = put(ws6, i, j, f, fill=ST_FILL[status(k)], al=CEN)
        n6 += 1
LAST6 = 1 + len(res)
ws6.freeze_panes = "F2"
ws6.auto_filter.ref = f"A1:{CL(5 + len(cols6))}{LAST6}"
log(f"matrix cells {n6}")

# =================== 07 未達・要確認 ===================
ws7 = wb.create_sheet(S07)
header(ws7, ["区分", "対象（結果事象ID／対策番号）", "内容", "対策前の結果事象頻度（/年）", "全候補採用時の最小到達頻度（/年）", "受容年間発生頻度（/年）", "必要な追加検討・追加情報", "関連ID", "受講生判断"],
       [22, 18, 54, 13, 13, 13, 60, 26, 12])
r7 = 2


def row7(kind, tgt, txt, g=None, mn=None, s=None, need=None, rel=None, red=False):
    global r7
    put(ws7, r7, 1, kind, fill=RED if red else None, font=REDF if red else F9B)
    put(ws7, r7, 2, tgt); put(ws7, r7, 3, txt)
    put(ws7, r7, 4, g, FREQ); put(ws7, r7, 5, mn, FREQ)
    put(ws7, r7, 6, f"=INDEX({ACCR},{s})" if s else None, FREQ)
    put(ws7, r7, 7, need); put(ws7, r7, 8, rel); put(ws7, r7, 9, None)
    r7 += 1


un = [r for r in res.values() if r.get("status0") == "追加検討が必要"]
un.sort(key=lambda r: (-r["S"], -(r["minfreq"] / r["A"])))
for r in un:
    nomeas = sum(1 for p in r["paths"] if not any(c for _, c, _ in p["app"]))
    need = (f"全候補を採用しても受容頻度の{r['minfreq'] / r['A']:.0f}倍。" + (f"対策候補のない経路が{nomeas}本（中間事象型原因・外部要因・境界外操作など）。" if nomeas else "")
            + "効果を創作せず追加検討とする：事故進展抑制・被害軽減（重大度低減）の評価、第2段の必要条件（仮値）の精査、原因頻度の根拠確認、追加の独立保護層の検討。")
    row7("受容頻度を達成できない結果事象（追加検討が必要）", f"{r['id']}（No.{r['no']}）", r["text"], r["G"], r["minfreq"], r["S"], need, r["zone"], True)
for r in res.values():
    if r.get("status0") == "原因未確定":
        row7("受容頻度を達成できない結果事象（原因未確定）", r["id"], r["text"], None, None, r["S"], "第2段で原因未確定。原因事象の追加（第1段への差戻し）が必要。頻度を算定できないため受容判定不能。", r["zone"], True)
for k in ORDER:
    if k[0] in M.MIT_RULES and (k in selA or k in selB):
        row7("効果倍率の根拠が弱い対策", f"【{NO[k]}】", inst[k]["name"] + f"（{M.ZSH[k[1]]}、重大度1段階低減）",
             need="重大度1段階低減は演習仮定。検知・隔離の応答時間、耐火時間、建屋の耐爆性能、貯留容量などの設計根拠で確認する。", rel=status(k), red=True)
for k in freqm:
    m = inst[k]
    if m["f"] <= 1 / 30 or m["kind"] == "伝播遮断":
        row7("効果倍率の根拠が弱い対策", f"【{NO[k]}】", m["name"] + f"（{M.ZSH[k[1]]}、{frac(m['f'])}）", need=m["why"] + "。SIL検証・試験間隔・応答時間・遮断弁の漏れ量などの設計根拠で確認する。" if m["kind"] == "伝播遮断" else m["why"],
             rel=status(k), red=k in selA or k in selB)
combos = [
    ("フェイルセーフ型プラントESD × 個別SIS", "遮断弁・論理を共用すると独立でない。本評価は共用しない前提で、ユーティリティ喪失経路ではESDのみを計上（個別SISは計算除外）。", "ESDと個別SIFの最終要素の割当て確認。"),
    ("【%s】と【%s】" % (NO.get(("SIS-H01F", 4), "-"), NO.get(("SIS-R01T", 5), "-")), "H-01コイル低流量・出口高温インターロックとR-01高温インターロックは同一のH-01燃料遮断弁に依存。同一経路では単一効果のみ計上した。", "燃料遮断弁の二重化（異種弁）を行えば独立となる可能性。"),
    ("SIS全般 × 計装空気・電源喪失", "SISの遮断弁が計装空気・電源に依存するため、計装空気喪失・電源喪失を原因とする経路ではSISの効果を計算から除外（要確認）。", "遮断弁のフェイルセーフ方向・アキュムレータの有無の確認。"),
    ("同一ゾーンの複数SIF", "同一ゾーンのSIFは論理演算器・遮断弁の共用可能性があるため同一クラスとして積をとらない。", "SIF構成（センサー・論理・最終要素）の個別設計による独立性の確認。"),
    ("運転チェックリスト・自動化・起動手順（人的クラス）", "同一運転班・同一手順体系に依存するため、同一経路では単一効果のみ。", "人的信頼性評価（HRA）による従属性の評価。"),
    ("計器冗長化 × 計器の定期比較点検（BPCS計器クラス）", "同一発信器の誤指示に作用する代替策。併用しても単一効果のみ。", "導圧管・取付ノズルの共用による共通原因故障の確認。"),
    ("RBI × 常設肉厚監視（検査クラス）", "同一の減肉事象に作用する代替策。", "—"),
    ("ユーティリティ冗長化 × 同一ユーティリティに依存する対策", "予備圧縮機・非常用発電機は同一受電系統に依存する可能性がある。", "電源系統・計装空気系統の単線結線図による確認。"),
]
for a, b, c in combos:
    row7("共通原因故障により独立性が確認できない対策組合せ", a, b, need=c, red=True)
dbl = [
    ("伝播遮断（SIS）全般", "第2段で既存のLC・PC・TC・制御弁を偏差の原因として扱っている。SISがこれらのBPCS計器・制御弁を共用すると、原因と対策が同一機器となり二重計上となる。本評価は専用センサー・専用遮断弁を前提。"),
    (f"【{NO[('RLV', 0)]}】放圧装置の容量検証", "第2段で放圧装置の要求時失敗確率（ADD-C13＝0.01）を必要条件として既に仮定しているため、頻度低減として追加計上すると二重計上となる。頻度計算に含めていない。"),
    ("閉鎖ガス処理系", "第2段では放出先として扱い、保護層としてクレジットしていない。第3段でも頻度低減に計上していない。"),
    ("計器冗長化（INST）とSISの液位計", "同一ノズル・同一導圧管を用いる場合は独立でない。"),
]
for a, b in dbl:
    row7("既存制御との二重計上のおそれがある対策", a, b, need="設計段階で計器・弁の割当てを確認する。", red=True)
info = [
    ("設計情報", "フェイルセーフ型プラントESDの構成（専用UPS容量、遮断弁のフェイル方向・アキュムレータ、個別SISとの遮断弁共用の有無、SIL）", "共通原因経路への1/10の効果の根拠"),
    ("放出・処理系情報", "閉鎖ガス処理系に接続する他装置を含む同時放出シナリオ、ノックアウトドラム容量、フレアの有無と無煙化能力", "閉鎖ガス処理系の強化対策と無煙化の効果の根拠"),
    ("設計情報", "機器の設計圧力・設計温度・材質・内容積、配管径", "偏差→損傷（第2段ADD-C01）、放出規模（ADD-C02）の妥当性、SIS設定値の設定"),
    ("設計情報", "各制御弁のフェイル位置、専用遮断弁の設置可否、K-02の形式と容量制御方式", "SISの遮断方式と計装空気喪失時の挙動"),
    ("保全情報", "計器・制御弁の故障履歴、試験間隔、シール故障履歴、腐食・検査履歴", "原因頻度（第2段）と残余頻度倍率の根拠"),
    ("配置情報", "計器室・仮設建屋・作業場所の配置、設備間距離、混雑度", "複数死亡・蒸気雲爆発の結果（多くが未達）の重大度低減策の評価"),
    ("放出・処理系情報", "安全弁・破裂板の設置と容量、閉鎖ガス処理系・閉鎖排液系の構成と受入能力、燃焼設備の有無", "放圧・ベント・ドレン系の重大放出の評価"),
    ("触媒情報", "触媒の種類・被毒物質・副反応特性、使用済触媒の性状", "R-01系の結果事象と原因未確定の結果事象"),
]
for a, b, c in info:
    row7("追加の設計・保全・配置・放出処理系情報が必要", a, b, need=c)
adds = [
    ("中間事象型の原因（第2段で要確認）", "上流偏差を記述した原因は対策を割り当てられない（対策候補なしの経路の主因）。上流の物理的原因への置換が必要。"),
    ("外部要因・境界外操作", "外部火災、上流・外部貯蔵の操作などは本プラント内の対策で頻度を下げられない。境界条件として扱うか追加対策を検討。"),
    ("使用済触媒の取扱いに関する原因事象", "RS-1252（原因未確定）に対応する原因事象の追加。"),
    ("塔内部品の脱落に対応する結果事象", "第2段で単独で経路を構成しないとした原因に対応する結果（分離不良・製品規格外）の追加。"),
    ("事故進展抑制・被害軽減の評価方法", "ガス検知・ESD隔離、耐火被覆、計器室耐爆化などは頻度に計上していない。重大度低減として扱う評価ルールの設定が必要。"),
]
for a, b in adds:
    row7("原因・結果・中間事象の追加が必要", a, b, need="第1段・第2段へ差し戻して受講生が判断")
su = [
    ("T-01・T-02・T-03の起動時液張込み", "起動時の過剰張込み・塔底排出開始遅れ（Texas City型）。起動手順の改訂・塔全高液位計・高高液位SISの起動時バイパス管理を別途検討。"),
    ("SISのバイパス・試験中の運転", "起動・保全時にSISをバイパスする場合、本評価の倍率は成立しない。バイパス管理手順の検討が必要。"),
    ("保全後の材料確認・置換・気密", "保全後の誤材料取付け、置換不十分のまま炭化水素導入。PMI・PSSRの運用確認。"),
    ("R-01触媒交換・入槽", "不活性ガスの使用有無、入槽許可、使用済触媒の取扱い。"),
    ("ドレン・サンプリング作業", "V-00水ドレン、V-701排液、SP-603サンプリングは作業時のみ成立する経路。作業頻度・曝露時間の確認が必要。"),
]
for a, b in su:
    row7("起動・停止・保全時に別途検討すべき事項", a, b, need="操業モード別のHAZOP（手順HAZOP）で検討")
nflag = sum(1 for r in res.values() for p in r["paths"] if p["flags"])
row7("操業損失の分離", "09・10シート", f"操業損失{len(RO)}件は安全の対策選定・受容判定から分離した。未達の操業損失は10シートに記載。", need="事業判断（費用対効果）で採否を決める")
row7("第2段から継承した未解決事項", "第2段04シートZ列", f"第2段で要確認（共通原因・重複計上・重複経路・AND次元・内部AND・時間順序・条件付き確率）とされた経路 {nflag}本は、第3段でも解消せず要確認として継承した。",
     need="第2段のレビュー（最小カットセット整理、共通原因の別ツリー化）が必要", red=True)
LAST7 = r7 - 1
ws7.freeze_panes = "C2"
ws7.auto_filter.ref = f"A1:I{LAST7}"

# =================== 09 操業損失：経路別対策 ===================
S09, S10 = "09_操業損失_経路別対策", "10_操業損失_集計"
ws9, LAST9, _, _, _, _ = path_sheet(S09, selB, "B", RO, frozenset(opB))

# =================== 10 操業損失：集計 ===================
ws10 = wb.create_sheet(S10)
header(ws10, ["項目", "案B（コスト最少）の安全対策を前提", "参考：案A（対策数最少）を前提", "備考"], [44, 30, 30, 70])
H9 = f"{Q(S09)}!$AM$2:$AM${LAST9}"
K9 = f"{Q(S09)}!$K$2:$K${LAST9}"
L9 = f"{Q(S09)}!$L$2:$L${LAST9}"
Z2 = f"{Q(S02)}!$Z$2:$Z${LAST2}"


def frq_with(r, ks):
    return sum(p["H"] * M.path_factor([k for k, c, _ in p["app"] if c and k in ks], inst) for p in r["paths"])


okB = sum(1 for r in RO.values() if r["paths"] and frq_with(r, selB) <= r["A"] * (1 + 1e-9))
okA = sum(1 for r in RO.values() if r["paths"] and frq_with(r, selA) <= r["A"] * (1 + 1e-9))
costm = lambda ks: sum(inst[k]["ini"] + 10 * inst[k]["ann"] for k in ks)
rows10 = [
    ("操業損失の結果事象数", f"=COUNTIF({H9},1)", len(RO), "0", "人身・環境の影響がなく、漏洩・火災・爆発・死傷・汚染を含まない結果事象（品質・触媒・機器損傷・停止）"),
    ("対策前に受容頻度以下", f'=COUNTIFS({H9},1,{L9},"対策前に受容")', sum(1 for r in RO.values() if r.get("status0") == "対策前に受容"), "0", "受容頻度は安全と同じ暫定基準（重大度別）"),
    ("安全対策の波及効果だけで受容（静的集計）", okB, okA, "0", "安全のために採用した対策が操業損失の経路にも作用する効果"),
    ("追加対策後に受容頻度以下", f'=COUNTIFS({H9},1,{K9},"受容")', None, "0", "09シートの判定（数式）"),
    ("未達", f'=COUNTIFS({H9},1,{K9},"未達")', None, "0", ""),
    ("　うち全候補を採用しても未達（追加検討が必要）", f'=COUNTIFS({H9},1,{L9},"追加検討*")', None, "0", "効果を創作せず追加検討とする（下表）"),
    ("追加対策数", f'=COUNTIF({Z2},"追加採用")', len(opA), "0", "安全対策で採用済みの対策は費用・件数に含めない"),
    ("追加対策の初期投資合計", f'=SUMIF({Z2},"追加採用",{Q(S02)}!$O$2:$O${LAST2})', sum(inst[k]["ini"] for k in opA), MONEY, ""),
    ("追加対策の年間ランニングコスト合計", f'=SUMIF({Z2},"追加採用",{Q(S02)}!$P$2:$P${LAST2})', sum(inst[k]["ann"] for k in opA), MONEYY, ""),
    ("追加対策の10年必要コスト合計", f'=SUMIF({Z2},"追加採用",{Q(S02)}!$R$2:$R${LAST2})', costm(opA), MONEY, "案A前提の列は静的集計値（参考）"),
]
for i, (lab, vb, va, fmt, note) in enumerate(rows10, 2):
    put(ws10, i, 1, lab, font=F9B); put(ws10, i, 2, vb, fmt); put(ws10, i, 3, va, fmt); put(ws10, i, 4, note)
r10 = 2 + len(rows10)
put(ws10, r10, 1, "追加対策一覧（案B前提）", font=F9B)
put(ws10, r10, 2, "、".join(f"{mname(k)}（{M.ZSH[k[1]]}、{frac(inst[k]['f'])}）" for k in sorted(opB, key=lambda k: NO[k])) or "なし", fill=OPF)
ws10.merge_cells(start_row=r10, start_column=2, end_row=r10, end_column=4); ws10.row_dimensions[r10].height = 60
r10 += 1
put(ws10, r10, 1, "選定方法", font=F9B)
put(ws10, r10, 2, f"安全の案Bで採用した{len(selB)}件を採用済み（費用0・固定）とし、操業損失の結果事象だけを制約として、追加対策の10年必要コストを最小化（同額時は件数最少）する整数最適化（HiGHS）。"
    f"案B前提 {infoOB['status'][0]}／{infoOB['status'][1]}、案A前提 {infoOA['status'][0]}／{infoOA['status'][1]}。")
ws10.merge_cells(start_row=r10, start_column=2, end_row=r10, end_column=4); ws10.row_dimensions[r10].height = 48
r10 += 1
put(ws10, r10, 1, "位置づけ", font=F9B)
put(ws10, r10, 2, "安全HAZOP（人身・環境・プロセス安全事故）の対策選定から操業損失を分離した。操業損失は事業判断（費用対効果）で採否を決める参考資料であり、安全対策の受容判定には含めない。"
    "セル色：薄黄（濃）＝操業損失のための追加対策、その他の色＝02シートの安全対策の採用状態。")
ws10.merge_cells(start_row=r10, start_column=2, end_row=r10, end_column=4); ws10.row_dimensions[r10].height = 48
ws10.freeze_panes = "A2"
ws10.auto_filter.ref = f"A1:D{1 + len(rows10)}"
r10 += 2
hd = ["結果事象ID", "結果事象", "重大度", "受容年間発生頻度（/年）", "対策前の年間発生頻度（/年）", "対策後の年間発生頻度（/年）", "受容可否", "区分"]
for j, t in enumerate(hd, 1):
    c = ws10.cell(row=r10, column=j, value=t); c.font = HFONT; c.fill = HF; c.alignment = CEN; c.border = BD
for c_, w in zip("EFGH", [14, 14, 9, 30]):
    ws10.column_dimensions[c_].width = w
for r in sorted(RO.values(), key=lambda r: (-r["S"], -r["G"])):
    r10 += 1
    put(ws10, r10, 1, r["id"]); put(ws10, r10, 2, r["text"]); put(ws10, r10, 3, r["S"], "0")
    put(ws10, r10, 4, f"=INDEX({ACCR},C{r10})", FREQ)
    put(ws10, r10, 5, f"=SUMIFS({Q(S09)}!$H$2:$H${LAST9},{Q(S09)}!$AK$2:$AK${LAST9},A{r10})", FREQ)
    put(ws10, r10, 6, f"=SUMIFS({Q(S09)}!$I$2:$I${LAST9},{Q(S09)}!$AK$2:$AK${LAST9},A{r10})", FREQ)
    put(ws10, r10, 7, f'=IF(F{r10}<=D{r10}*(1+1E-9),"受容","未達")', al=CEN)
    st0 = r.get("status0", "")
    put(ws10, r10, 8, {"追加検討が必要": "追加検討が必要（全候補でも未達）"}.get(st0, st0), fill=RED if st0 == "追加検討が必要" else None)
ws10.conditional_formatting.add(f"G2:G{r10}", CellIsRule(operator="equal", formula=['"未達"'], fill=RED, font=REDF))

wb._sheets = [wb[n] for n in ["01_第3段プロンプト", S02, S03, S04, S05, S06, S07, S08, S09, S10]]
wb.save(OUT)
log(f"saved {OUT}: catalog {len(ORDER)} (freq {len(freqm)}), A {len(selA)} B {len(selB)}, unach {len(un)}")
open("stage3_log.txt", "w").write("\n".join(LOG))
