# -*- coding: utf-8 -*-
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import hazop_data as h

OUT = sys.argv[1]
FN = "Meiryo"
thin = Side(style="thin", color="999999")
BD = Border(left=thin, right=thin, top=thin, bottom=thin)
HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(name=FN, bold=True, color="FFFFFF", size=10)
F10 = Font(name=FN, size=10)
WRAP = Alignment(wrap_text=True, vertical="top")
CEN = Alignment(wrap_text=True, vertical="center", horizontal="center")

wb = Workbook()

# ---------------- Sheet1: 指示プロンプト ----------------
ws1 = wb.active
ws1.title = "1_指示プロンプト"
ws1.column_dimensions["A"].width = 140
lines = open("prompt.txt", encoding="utf-8").read().rstrip("\n").split("\n")
for i, ln in enumerate(lines, 1):
    c = ws1.cell(row=i, column=1, value=ln if ln else None)
    c.font = Font(name=FN, size=10, bold=ln in ("第1段で実施すること", "重大結果の見落とし防止ルール", "出力形式", "最終品質確認"))
    c.alignment = Alignment(wrap_text=True, vertical="top")

# ---------------- Sheet2: 第1段結果表 ----------------
ws2 = wb.create_sheet("2_第1段_原因・結果洗い出し")
ws2["A1"] = "HAZOP Study 第1段：原因事象・結果事象の網羅的洗い出し（イソブタン製造プラント／通常連続操業＋起動・停止・保全移行）"
ws2["A1"].font = Font(name=FN, size=12, bold=True)
notes = [
    "・検討番号の末尾「-C」は原因事象行、「-R」は結果事象行。同一検討項目（例：Z1-01）内の原因と結果は並列に列挙したもので、対応関係・AND/OR・確率・重大度・対策は示さない（第2段・第3段で扱う）。",
    "・「実機確認が必要」と記したものは、本入力資料で実在・仕様が確認できない設備・放圧経路・触媒成分等に関する候補であり、事実として断定していない。結果事象中の（〜により成立）は成立条件を示す。",
    "・設計圧力・設計温度・内容積・放圧装置・弁のフェイル位置・閉鎖ガス処理／閉鎖排液の能力は未提示のため、過圧・破裂・放出能力超過は候補として記載している。",
]
for i, n in enumerate(notes, 2):
    ws2.cell(row=i, column=1, value=n).font = Font(name=FN, size=9, color="444444")
    ws2.merge_cells(start_row=i, start_column=1, end_row=i, end_column=7)
    ws2.cell(row=i, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    ws2.row_dimensions[i].height = 26
HR = 6
headers = ["検討番号", "検討対象ゾーン", "検討対象装置またはインターフェース", "ガイドワード適用対象（入流、流出、内部）", "ガイドワード", "原因事象", "結果事象"]
widths = [13, 20, 34, 13, 22, 52, 70]
for j, (t, w) in enumerate(zip(headers, widths), 1):
    c = ws2.cell(row=HR, column=j, value=t)
    c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CEN; c.border = BD
    ws2.column_dimensions[get_column_letter(j)].width = w
ws2.row_dimensions[HR].height = 34

band = [PatternFill("solid", fgColor="FFFFFF"), PatternFill("solid", fgColor="F2F5FA")]
cfill = PatternFill("solid", fgColor="E8F1FB")
rfill = PatternFill("solid", fgColor="FDF1E7")
r = HR + 1
nC = nR = 0
for gi, g in enumerate(h.GROUPS):
    bf = band[gi % 2]
    rows = [("C", i + 1, t, None) for i, t in enumerate(g["causes"])] + [("R", i + 1, t, cats) for i, (t, cats) in enumerate(g["results"])]
    for kind, n, text, cats in rows:
        vals = [f"{g['id']}-{kind}{n:02d}", g["zone"], g["equip"], g["target"], g["gw"],
                text if kind == "C" else None, text if kind == "R" else None]
        for j, v in enumerate(vals, 1):
            c = ws2.cell(row=r, column=j, value=v)
            c.font = F10; c.alignment = WRAP; c.border = BD; c.fill = bf
        ws2.cell(row=r, column=6 if kind == "C" else 7).fill = cfill if kind == "C" else rfill
        if kind == "C":
            nC += 1
        else:
            nR += 1
        r += 1
LAST2 = r - 1
ws2.freeze_panes = ws2.cell(row=HR + 1, column=6)
ws2.auto_filter.ref = f"A{HR}:G{LAST2}"

# ---------------- Sheet3: 重大結果網羅性チェック ----------------
ws3 = wb.create_sheet("3_重大結果網羅性チェック")
ws3["A1"] = "重大結果網羅性チェック（第2シートの結果事象行を対象に確認）"
ws3["A1"].font = Font(name=FN, size=12, bold=True)
ws3["A2"] = "「結果事象あり」の括弧内は該当する検討番号（代表）。「該当なし」は物理的根拠、「実機情報不足」は不足情報と関連する検討番号を記載。"
ws3["A2"].font = Font(name=FN, size=9, color="444444")
TARGETS = [
    ("ゾーン", "Z1", "Z1 原料受入・送液（V-00、P-01）"),
    ("ゾーン", "Z2", "Z2 脱イソブタン塔系（T-01 19 bar(a)、D-101）"),
    ("ゾーン", "Z3", "Z3 脱ブタン塔系（T-02 16 bar(a)、D-201）"),
    ("ゾーン", "Z4", "Z4 昇圧・混合・加熱（P-02、V-701、K-02、H-01）"),
    ("ゾーン", "Z5", "Z5 触媒異性化反応（R-01）"),
    ("ゾーン", "Z6", "Z6 冷却・気液分離・ガス収支（E-501、V-01、補給H2、パージ）"),
    ("ゾーン", "Z7", "Z7 スタビライザー系（T-03、D-301）"),
    ("ゾーン", "Z0", "Z0 共通・補助境界（計装空気、電源、冷却水、熱媒、閉鎖系、制御系）"),
    ("高圧・可燃性IF", "IF-B02", "B02/S05 P-01吐出〜T-01供給（液C4、19.2 bar(a)）"),
    ("高圧・可燃性IF", "IF-B03", "B03/S12 T-01塔底減圧〜T-02供給（二相、102.8°C、16.2 bar(a)）"),
    ("高圧・可燃性IF", "IF-B04", "B04/S16 D-201〜P-02〜FV-702（液C4、90°C、昇圧液）"),
    ("高圧・可燃性IF", "IF-K02", "K-02吸込〜吐出・液ガス合流部（H2+C4、18.5 bar(a)）"),
    ("高圧・可燃性IF", "IF-H01", "H-01 加熱炉（コイル・燃焼系）"),
    ("高圧・可燃性IF", "IF-B05", "B05/S25 反応器入口（150°C、17.5 bar(a)、H2 9.5 mol%）"),
    ("高圧・可燃性IF", "IF-B06", "B06/S26 反応器出口〜E-501（180.8°C、16.5 bar(a)）"),
    ("高圧・可燃性IF", "IF-B07", "B07/S22 循環ガス（H2 63.7 mol%、14.6 bar(a)）"),
    ("高圧・可燃性IF", "IF-H2", "B15/S20・B08/S21 補給水素インターフェース（FV-601を含む、25→14.6 bar(a)）"),
    ("高圧・可燃性IF", "IF-H2P", "補給水素配管単体（H2 99.9 mol%／CH4 0.1 mol%）"),
    ("高圧・可燃性IF", "IF-B09", "B09/S31 LV-501減圧部（15→6.7 bar(a)、二相）"),
    ("高圧・可燃性IF", "IF-B10", "B10/S38 LV-303〜E-003〜V-00（二相、3.5 bar(a)）"),
    ("高圧・可燃性IF", "IF-B11", "B11/S10 液イソブタン製品（18.4 bar(a)）"),
    ("高圧・可燃性IF", "IF-B12", "B12/S19 重質分抜出し（15.0 bar(a)）"),
    ("放圧・ベント・ドレン・パージ", "IF-VENT", "閉鎖ガス処理への排出（B13・B14・B16・B17・B19）・放圧系"),
    ("放圧・ベント・ドレン・パージ", "IF-DRAIN", "閉鎖排液・ドレン（B18、V-00水ドレン、各機器ドレン）"),
    ("放圧・ベント・ドレン・パージ", "IF-SP", "SP-603 循環ガス閉鎖採取・GC分析・追加パージ操作"),
    ("補助境界", "IF-CW", "冷却水系（E-101/E-201/E-103/E-203/E-501/E-301/E-003）"),
    ("補助境界", "IF-HM", "加熱媒体系（E-102/E-202/E-302、E-701）"),
    ("補助境界", "IF-UTIL", "計装空気・電源・制御システム・外部要因"),
]
CATS = [("LEAK", "漏洩・大量放出"), ("FIRE", "即時着火火災"), ("VCE", "遅延着火・蒸気雲爆発"), ("SD", "単独死亡"),
        ("MD", "複数死亡"), ("ENV", "環境汚染（土壌・排水系・水域）"), ("RELIEF", "放圧・ベント・ドレン・パージ系の重大放出"), ("ESC", "火災による連鎖損傷")]

gid = {g["id"]: g for g in h.GROUPS}


def zid(i):
    return f"Z{gid[i]['z']}"


OVR = {
    ("IF-H01", "RELIEF"): ("実機情報不足", "H-01コイル・火炉の放圧経路（コイル側放圧装置、火炉防爆扉等）は未提示。コイル上流の過圧放出はK-02吐出〜H-01入口の候補として記載（{k02}）。"),
    ("IF-B11", "RELIEF"): ("実機情報不足", "外部製品貯蔵の放圧・受入設計は境界外で未提示。D-101からのガス吹抜け・高温製品による貯蔵過圧は結果事象として記載（{b11}）。"),
    ("IF-H2P", "ENV"): ("該当なし", "H2 99.9 mol%・CH4 0.1 mol%の気相で、液・油分・VOCを含まず、燃焼生成物は水のため、土壌・排水系・水域汚染の物理的経路がない。隣接C4設備への延焼時の消火排水汚染はZ6（V-01等）で結果事象あり。"),
    ("IF-H2P", "RELIEF"): ("実機情報不足", "補給水素配管自体の放圧装置の有無は未提示。FV-601開固着時のループ過圧放出は補給水素IFで結果事象あり（{h2}）。"),
}

hdr3 = ["区分", "検討対象（ゾーン／インターフェース）"] + [c[1] for c in CATS] + ["備考（根拠・関連する検討番号）"]
w3 = [16, 40] + [20] * 8 + [50]
R3 = 4
for j, (t, w) in enumerate(zip(hdr3, w3), 1):
    c = ws3.cell(row=R3, column=j, value=t)
    c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CEN; c.border = BD
    ws3.column_dimensions[get_column_letter(j)].width = w
ws3.row_dimensions[R3].height = 48
fill_ok = PatternFill("solid", fgColor="E2EFDA")
fill_na = PatternFill("solid", fgColor="EDEDED")
fill_ins = PatternFill("solid", fgColor="FFF2CC")


def ids_for(key, cat):
    return [g["id"] for g in h.GROUPS if key in g["keys"] and any(cat in cs for _, cs in g["results"])]


cov_stats = {"あり": 0, "該当なし": 0, "不足": 0}
r = R3 + 1
for kind, key, label in TARGETS:
    ws3.cell(row=r, column=1, value=kind)
    ws3.cell(row=r, column=2, value=label)
    remarks = []
    for j, (cat, cname) in enumerate(CATS, 3):
        ids = ids_for(key, cat)
        if (key, cat) in OVR:
            st, why = OVR[(key, cat)]
            why = why.format(k02=", ".join(ids_for("IF-K02", "RELIEF")[:3]), b11=", ".join(ids_for("IF-B11", "LEAK")[:3]),
                             h2=", ".join(ids_for("IF-H2", "RELIEF")[:3]))
            txt = st
            remarks.append(f"【{cname}】{why}")
            fill = fill_na if st == "該当なし" else fill_ins
            cov_stats["該当なし" if st == "該当なし" else "不足"] += 1
        elif ids:
            shown = ", ".join(ids[:5]) + (f" ほか{len(ids) - 5}件" if len(ids) > 5 else "")
            txt = f"結果事象あり\n({shown})"
            fill = fill_ok
            cov_stats["あり"] += 1
        else:
            txt = "要検討（未記載）"
            fill = PatternFill("solid", fgColor="F8CBAD")
        c = ws3.cell(row=r, column=j, value=txt)
        c.fill = fill
    ws3.cell(row=r, column=11, value="\n".join(remarks) if remarks else "全項目について第2シートに結果事象行あり。")
    for j in range(1, 12):
        c = ws3.cell(row=r, column=j)
        c.font = Font(name=FN, size=9); c.alignment = WRAP; c.border = BD
    ws3.row_dimensions[r].height = 64
    r += 1
LAST3 = r - 1
r += 1
ws3.cell(row=r, column=1, value="判定の集計").font = Font(name=FN, size=10, bold=True)
for i, (lab, pat) in enumerate([("結果事象あり", "結果事象あり*"), ("該当なし", "該当なし"), ("実機情報不足", "実機情報不足")], 1):
    ws3.cell(row=r + i, column=1, value=lab).font = F10
    c = ws3.cell(row=r + i, column=2, value=f'=COUNTIF($C${R3 + 1}:$J${LAST3},"{pat}")')
    c.font = F10; c.number_format = "0"
ws3.cell(row=r + 4, column=1, value="合計（対象×8項目）").font = F10
c = ws3.cell(row=r + 4, column=2, value=f"=SUM(B{r + 1}:B{r + 3})"); c.font = F10
ws3.cell(row=r + 4, column=3, value=f"=ROWS(A{R3 + 1}:A{LAST3})*8").font = F10
ws3.cell(row=r + 4, column=4, value="← 対象数×8（左と一致すれば全セル判定済み）").font = Font(name=FN, size=9, color="444444")
ws3.freeze_panes = "C5"

# ---------------- Sheet4: 最終品質確認 ----------------
ws4 = wb.create_sheet("4_最終品質確認")
ws4["A1"] = "最終品質確認（出力前の自己点検結果）"
ws4["A1"].font = Font(name=FN, size=12, bold=True)
hdr4 = ["No", "点検項目（指示プロンプトより）", "確認結果", "確認内容・根拠"]
for j, (t, w) in enumerate(zip(hdr4, [6, 52, 12, 95]), 1):
    c = ws4.cell(row=3, column=j, value=t)
    c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CEN; c.border = BD
    ws4.column_dimensions[get_column_letter(j)].width = w


def cnt(word):
    return sum(1 for g in h.GROUPS for t, _ in g["results"] if word in t)


def cntc(cat):
    return sum(1 for g in h.GROUPS for _, cs in g["results"] if cat in cs)


S2 = "'2_第1段_原因・結果洗い出し'"
checks = [
    ("高圧C4、水素、循環ガス、反応器入口・出口、塔、ドラム、圧縮機、加熱炉、減圧部、放圧・ベント・ドレン・パージ部について、重大終端事象を確認したか。",
     "確認済", f"第3シートで7ゾーン＋共通境界および{sum(1 for t in TARGETS if t[0] != 'ゾーン')}の高圧・可燃性・放出系・補助境界インターフェースについて8項目を判定。全{len(TARGETS) * 8}判定のうち「要検討（未記載）」は0件。該当なし・情報不足は備考に根拠を記載。"),
    ("漏洩・破裂を結果の終点にしていないか。",
     "確認済", "漏洩・破裂を挙げた検討項目には、同一項目内に即時着火（噴流・フラッシュ・プール火災）、遅延着火（蒸気雲爆発）、人身（単独・複数）、連鎖損傷、事業、環境の各終端結果を別行で列挙している（定型ラダーを全LOC項目に適用）。"),
    ("蒸気雲爆発を「設備破壊」のみに限定せず、人身影響と連鎖損傷を別結果として挙げたか。",
     "確認済", "蒸気雲爆発の設備破壊行に加え、「爆風・飛来物による複数のオンサイト作業員の死亡・重傷」「計器室・仮設事務所の損壊による屋内人員の死亡（Texas City型）」「隣接設備への連鎖損傷」「構外影響・避難」を別行として記載。"),
    ("人身影響を単独死亡だけに限定せず、複数死亡の候補を評価対象に含めたか。",
     "確認済", "単独死亡（火災巻込み、破裂破片、サンプリング作業、ドレン作業、入槽時酸欠等）と、複数死亡（蒸気雲爆発、建屋損壊、火炉爆発、救助者を含む酸欠、起動作業中の内部爆発等）を別行で記載。"),
    ("環境影響をVOC排出だけに限定せず、土壌・排水系・水域への流入を検討したか。",
     "確認済", "VOC・黒煙の大気排出に加え、液炭化水素・油分の側溝・排水系流入による土壌・公共水域汚染、消火排水の流出、冷却水・熱媒系への漏入とブローダウン流出、使用済触媒・洗浄排水を別行で記載。"),
    ("第2段の因果関係、確率、重大度、対策を混入させていないか。",
     "確認済", "原因行と結果行は別行とし対応付けをしていない（「-C」「-R」で区分）。確率・頻度・重大度ランク・対策（保護層、推奨事項）は記載していない。「（Z5で詳細検討）」は他ゾーンへの参照であり、因果パスの整理ではない。"),
]
for i, (q, res, why) in enumerate(checks, 1):
    for j, v in enumerate([i, q, res, why], 1):
        c = ws4.cell(row=3 + i, column=j, value=v)
        c.font = F10; c.alignment = WRAP; c.border = BD
    ws4.row_dimensions[3 + i].height = 62
rr = 11
ws4.cell(row=rr, column=2, value="第2シートの件数（数式で集計）").font = Font(name=FN, size=10, bold=True)
stats = [
    ("検討項目（偏差）数", None, len(h.GROUPS)),
    ("原因事象行数", f'=COUNTA({S2}!F7:F{LAST2})', None),
    ("結果事象行数", f'=COUNTA({S2}!G7:G{LAST2})', None),
    ("結果事象のうち「蒸気雲爆発」を含む行", f'=COUNTIF({S2}!G7:G{LAST2},"*蒸気雲爆発*")', None),
    ("結果事象のうち「複数」（複数死亡等）を含む行", f'=COUNTIF({S2}!G7:G{LAST2},"*複数*")', None),
    ("結果事象のうち「BLEVE」を含む行", f'=COUNTIF({S2}!G7:G{LAST2},"*BLEVE*")', None),
    ("結果事象のうち「水域」（土壌・水域汚染）を含む行", f'=COUNTIF({S2}!G7:G{LAST2},"*水域*")', None),
    ("結果事象のうち「実機確認」を明記した行", f'=COUNTIF({S2}!G7:G{LAST2},"*実機確認*")', None),
]
for i, (lab, f, v) in enumerate(stats, 1):
    ws4.cell(row=rr + i, column=2, value=lab).font = F10
    c = ws4.cell(row=rr + i, column=3, value=f if f else v)
    c.font = F10; c.number_format = "#,##0"
    if v is not None:
        ws4.cell(row=rr + i, column=4, value="データ定義から集計した値（検討番号の項目単位）").font = Font(name=FN, size=9, color="444444")

wb.save(OUT)
print("C", nC, "R", nR, "groups", len(h.GROUPS), cov_stats)
