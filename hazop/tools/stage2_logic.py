# -*- coding: utf-8 -*-
"""HAZOP 第2段：原因―結果の関係づけロジック（第1段データ hazop_data.py を入力とする）"""
import re
import csv
import os
from collections import defaultdict, OrderedDict
import hazop_data as h

# ------------------------------------------------------------------
# 第1段レビュー判定の読込（任意）：stage1_review.csv（第1段ID,判定,コメント）
# 未受領の場合は全件「採用（仮）」として扱う
# ------------------------------------------------------------------
REVIEW = {}
REVIEW_FILE = os.environ.get("STAGE1_REVIEW", "stage1_review.csv")
if os.path.exists(REVIEW_FILE):
    with open(REVIEW_FILE, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            REVIEW[row["第1段ID"].strip()] = (row["判定"].strip(), row.get("コメント", "").strip())
REVIEW_RECEIVED = bool(REVIEW)
DEFAULT_J = ("採用（仮）", "受講生レビュー結果は未受領。全件を仮採用として扱った。レビュー受領後に stage1_review.csv で再生成する。")


def judg(sid):
    return REVIEW.get(sid, DEFAULT_J)


def adopted(sid):
    j = judg(sid)[0]
    return j.startswith("採用") or j.startswith("修正") or j.startswith("要確認")


# ------------------------------------------------------------------
# 機器タグ → ゾーン、ゾーン接続（PFD上の境界）
# ------------------------------------------------------------------
TAGZ = {}
for z, tags in {
    1: "V-00 P-01 LV-002 FV-001 PV-003 LC-002 FC-001 PC-003",
    2: "T-01 E-101 D-101 P-101 E-102 E-103 PV-101H PC-101 TC-105 TV-105 TC-104 LC-103 LC-102 TC-109 HV-101V TI-107",
    3: "T-02 E-201 D-201 P-201 E-202 E-203 PV-201H PC-201 TC-205 TV-205 TC-204 LC-203 LC-202 HV-201V",
    4: "P-02 FV-702 FC-702 V-701 E-701 K-02 FC-701 H-01 TC-401",
    5: "R-01 PI-402",
    6: "E-501 V-01 LV-501 FV-601 FV-602 FC-601 FC-602 PC-502 HS-602 SP-603 TC-503 LC-501",
    7: "T-03 E-301 D-301 P-301 E-302 E-003 TC-306 PC-301 LC-302 LV-302 TC-304 LC-303 LV-303",
}.items():
    for t in tags.split():
        TAGZ[t] = z
TAGRE = re.compile("|".join(sorted(map(re.escape, TAGZ), key=len, reverse=True)))
BND = {"B01": (None, 1), "B02": (1, 2), "B03": (2, 3), "B04": (3, 4), "B05": (4, 5), "B06": (5, 6), "B07": (6, 4), "B08": (6, 4),
       "B09": (6, 7), "B10": (7, 1), "B11": (2, None), "B12": (3, None), "B13": (1, 0), "B14": (2, 0), "B15": (None, 6),
       "B16": (6, 0), "B17": (7, 0), "B18": (4, 0), "B19": (3, 0)}
ADJ = defaultdict(set)
for b, (a, c) in BND.items():
    if a is not None and c is not None:
        ADJ[a].add(c); ADJ[c].add(a)
for z in range(1, 8):
    ADJ[0].add(z); ADJ[z].add(0)
FLOW = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 1}  # 主流れ方向（組成・物質の伝播）
ZNAME = {k: v.split(" ")[0] + " " + v.split(" ")[1].split("（")[0] for k, v in h.ZN.items()}
ZSHORT = {0: "Z0 共通・補助境界", 1: "Z1 原料受入", 2: "Z2 脱イソブタン塔", 3: "Z3 脱ブタン塔", 4: "Z4 昇圧・加熱", 5: "Z5 反応", 6: "Z6 冷却・分離", 7: "Z7 スタビライザー"}


def zone_of_text(t, default):
    m = re.search(r"（Z(\d)で詳細検討）", t)
    if m:
        return int(m.group(1))
    m = TAGRE.search(t)
    return TAGZ[m.group(0)] if m else default


def flow_path(a, b):
    """物質流れ方向（主流れ）でaからbへのゾーン列"""
    if a == b:
        return [a]
    if 0 in (a, b):
        return [a, b]
    if b in ADJ[a]:
        return [a, b]
    p = [a]
    while p[-1] != b and len(p) < 9:
        p.append(FLOW[p[-1]])
    return p


# ------------------------------------------------------------------
# 原因事象の年間発生頻度（概略・演習用）
# ------------------------------------------------------------------
FREQ_RULES = [
    (r"地震", 1e-3, "地震による損傷：演習用一般値 1E-3/年（地域・耐震設計で大きく変動）"),
    (r"落雷|豪雨|浸水", 1e-2, "自然現象：演習用一般値 1E-2/年"),
    (r"外部火災|隣接設備・他装置の火災", 1e-3, "外部火災の曝露：演習用一般値 1E-3/年"),
    (r"停止時の.*逆止弁|時の.*逆止弁", 1e-2, "ポンプ・圧縮機停止(1E-1/年)×逆止弁の要求時失敗(0.1)を単一頻度1E-2/年で代表（内部AND）"),
    (r"逆止弁", 1e-2, "逆止弁不全を伴う逆流：停止頻度×要求時失敗を1E-2/年で代表"),
    (r"計装空気", 1e-1, "計装空気喪失・電磁弁故障：LOPA初期事象の一般値 1E-1/年"),
    (r"電源喪失|受電の停止|瞬時電圧低下|非常用電源|制御系電源", 1e-1, "電源喪失・瞬停：一般値 1E-1/年"),
    (r"冷却水の喪失|冷却水ポンプ停止|冷却水ヘッダ|冷却水供給", 1e-1, "冷却水喪失：LOPA初期事象の一般値 1E-1/年"),
    (r"熱媒供給の喪失|熱媒供給源|熱媒温度|熱媒供給側", 1e-1, "熱媒の喪失・異常：一般値 1E-1/年"),
    (r"の停止（モータ故障", 1e-1, "ポンプ・圧縮機の停止：LOPA初期事象の一般値 1E-1/年"),
    (r"メカニカルシール|軸封|潤滑油|軸受", 1e-1, "回転機のシール・軸受故障：一般値 1E-1/年"),
    (r"弁体固着|開固着|閉固着|制御弁の閉固着|制御弁の開固着", 5e-2, "制御弁の固着：BPCSループ故障1E-1/年のうち弁起因分として5E-2/年"),
    (r"発信器故障・誤指示|計器誤指示|液面計の誤指示|誤指示", 5e-2, "発信器故障・誤指示：BPCSループ故障1E-1/年のうち計器起因分として5E-2/年"),
    (r"コントローラCPU|制御ネットワーク|HMI|カスケード信号", 2e-2, "制御システム機器の故障：演習用 2E-2/年"),
    (r"誤校正|レンジ設定誤り", 1e-2, "誤校正（保全頻度×誤り確率）：演習用 1E-2/年"),
    (r"手動モード放置|設定値誤入力|制御パラメータの誤変更|ロジック.*誤変更|設定誤り（変更管理", 1e-2, "設定・モードの人的誤り：演習用 1E-2/年"),
    (r"伝熱管|管束|管板", 1e-2, "熱交換器伝熱管の漏洩・損傷：一般値 1E-2/年"),
    (r"フランジ|ガスケット", 1e-2, "フランジ・ガスケット漏洩：一般値 1E-2/年（小規模漏洩主体）"),
    (r"小口径配管.*疲労|振動による", 1e-3, "小口径配管の振動疲労破断：演習用 1E-3/年"),
    (r"誤材料|材料取り違え", 1e-3, "保全後の誤材料取付け：演習用 1E-3/年（保全頻度に依存）"),
    (r"腐食|減肉|エロージョン|クリープ|浸炭|材料劣化", 1e-3, "腐食・減肉・材料劣化による漏洩：演習用 1E-3/年（検査計画に依存）"),
    (r"重機|車両|落下物", 1e-3, "外部衝撃：演習用 1E-3/年"),
    (r"閉め忘れ|開放放置|離席|開け忘れ|誤閉止|誤開放|取外し忘れ|誤操作|誤った|切替誤り|手順逸脱|操作順序|開操作遅れ|見逃し|見落とし|排液.*遅れ|終了遅れ|解除忘れ|早すぎる開放|未実施|誤判定|判断誤り|再点火|入槽|開始（手順|過剰張込み|順序誤り|置換不十分|パージ不十分|置換・気密", 1e-2,
     "運転員・保全員の人的誤り：作業機会（年数回〜数十回）×誤り確率から演習用 1E-2/年"),
    (r"誤接続|誤タンク|誤ライン|誤ガス|取り違え", 1e-3, "誤接続・誤受入：演習用 1E-3/年"),
    (r"閉塞|ストレーナ|スケール|汚れ|凍結|コーク|微粉", 1e-1, "閉塞・汚れ・凍結：運転中に発生し得る劣化として演習用 1E-1/年"),
    (r"液封未確立", 1e-2, "起動時の手順逸脱（液封確立前の運転開始）：演習用 1E-2/年（絞り込みで潜在条件から人的誤りへ修正）"),
    (r"不備|測定範囲|未設計", 1.0, "設計上の潜在条件（存在すれば常時成立）：頻度ではなく条件確率1として扱う。単独では経路を構成しない"),
    (r"上流|供給源|供給圧力|供給設備|組成|混入|残存|破過|変動|上昇（|低下（|増加|夏季|寒冷|冬季|過冷却|副反応|吸込不足|性能低下|部分閉塞|摩耗", 1e-1,
     "上流・運転条件の変動：プロセス擾乱として演習用 1E-1/年"),
]


def cause_freq(t):
    for pat, f, why in FREQ_RULES:
        if re.search(pat, t):
            return f, why
    return 1e-2, "個別根拠なし：演習用既定値 1E-2/年（要確認）"


# ------------------------------------------------------------------
# 必要条件（第1段で原因として採用されていない条件）＝ 要追加候補
# ------------------------------------------------------------------
COND = OrderedDict([
    ("ADD-C01", ("偏差が機器損傷・漏洩に至る（設計余裕・機器強度を超える）条件", 0.1)),
    ("ADD-C02", ("大口径破損・大量放出となる条件（破損規模）", 0.1)),
    ("ADD-C03", ("即時着火の条件（放出点近傍の着火源、H2含有時は高め）", 0.1)),
    ("ADD-C04", ("可燃性ガス雲の滞留・拡散と遅延着火の条件", 0.1)),
    ("ADD-C05", ("蒸気雲爆発に至る混雑度・閉囲度の条件", 0.3)),
    ("ADD-C06", ("影響範囲内に作業員1名が在場・曝露する条件", 0.1)),
    ("ADD-C07", ("影響範囲内に複数の作業員が在場・曝露する条件", 0.05)),
    ("ADD-C08", ("計器室・仮設事務所等が影響範囲内に配置・在室している条件", 0.1)),
    ("ADD-C09", ("火災が継続し容器が冷却されず破裂に至る条件（BLEVE相当）", 0.1)),
    ("ADD-C10", ("火炎が隣接設備に衝突・輻射し連鎖損傷に至る条件", 0.1)),
    ("ADD-C11", ("影響が構外に到達する条件（規模・距離・気象）", 0.1)),
    ("ADD-C12", ("過圧が放圧装置の設定圧に到達する条件", 0.3)),
    ("ADD-C13", ("放圧装置の不作動・容量不足（要求時失敗確率）", 0.01)),
    ("ADD-C14", ("閉鎖ガス処理系の受入能力を超える条件", 0.1)),
    ("ADD-C15", ("液を伴う放出となり閉鎖ガス処理系で液が溢流する条件", 0.3)),
    ("ADD-C16", ("燃焼設備が存在し液滴燃焼が降下する条件", 0.1)),
    ("ADD-C17", ("流出液が防液堤・遮断を越えて排水系・土壌へ流入する条件", 0.3)),
    ("ADD-C18", ("消火排水が貯留されず排水系・水域へ流出する条件", 0.3)),
    ("ADD-C19", ("寒冷気象（凍結条件）の存在", 0.2)),
    ("ADD-C20", ("偏差が操業損失（規格外・減産・停止）に至る条件", 0.5)),
])

INTEGRITY_GW = re.compile(r"健全性|腐食|伝熱管漏洩|作業時の漏洩|チューブ劣化|機械故障|保全作業")


NONLEAK = re.compile(r"潤滑油喪失|異常振動|サージング|支持金物|熱媒喪失|汚れによる伝熱低下|熱伸縮")


def conditions(rtext, group, ctexts=()):
    """結果事象の文言から、第1段原因の後に必要な条件（要追加候補）を返す。
    機器健全性の群で、原因自体が漏洩をもたらす場合はADD-C01（偏差→損傷）を適用しない"""
    t = rtext
    integ = bool(INTEGRITY_GW.search(group["gw"])) and not any(NONLEAK.search(c) for c in ctexts)
    c01 = [] if integ else ["ADD-C01"]
    # --- 放圧・閉鎖ガス処理系 ---
    if "放圧装置が作動" in t:
        return ["ADD-C12"]
    if "受入能力を超え、ヘッダ背圧" in t:
        return ["ADD-C12", "ADD-C14"]
    if "液を伴う放出となり" in t:
        return ["ADD-C12", "ADD-C15"]
    if "火の雨" in t:
        return ["ADD-C12", "ADD-C15", "ADD-C16"]
    if "放出先の能力不足・不全により" in t:
        return ["ADD-C12", "ADD-C13"]
    if "大気放出された蒸気雲が遅延着火" in t:
        return ["ADD-C12", "ADD-C13", "ADD-C04", "ADD-C05"]
    if "放出点周辺の蒸気雲爆発により、複数" in t:
        return ["ADD-C12", "ADD-C13", "ADD-C04", "ADD-C05", "ADD-C07"]
    if "大量の未燃炭化水素・黒煙" in t:
        return ["ADD-C12"]
    if "放圧が不足・不全の場合" in t:
        return ["ADD-C12", "ADD-C13"]
    if "の破裂による圧力波・破片飛散" in t:
        return ["ADD-C12", "ADD-C13"]
    if "の破裂破片・圧力波により近傍の作業員" in t:
        return ["ADD-C12", "ADD-C13", "ADD-C06"]
    # --- 漏洩後の終端事象ラダー ---
    if "が外部へ漏洩し、大気中に放出" in t:
        return c01
    if "大量に流出し、フラッシュ蒸発" in t:
        return c01 + ["ADD-C02"]
    if "即時着火し、噴流火災" in t or "即時着火しやすく" in t:
        return c01 + ["ADD-C03"]
    if "フラッシュ火災により" in t:
        return c01 + ["ADD-C04"]
    if "プール火災" in t:
        return c01 + ["ADD-C02", "ADD-C03"]
    if "遅延着火して蒸気雲爆発が発生し" in t:
        return c01 + ["ADD-C02", "ADD-C04", "ADD-C05"]
    if "蒸気雲爆発の爆風・飛来物により、複数" in t:
        return c01 + ["ADD-C02", "ADD-C04", "ADD-C05", "ADD-C07"]
    if "計器室・仮設事務所" in t and "爆風" in t and "起因" in t:
        return c01 + ["ADD-C02", "ADD-C04", "ADD-C05", "ADD-C08"]
    if "近傍の作業員1名が巻き込まれ" in t:
        return c01 + ["ADD-C03", "ADD-C06"]
    if "BLEVE" in t:
        return c01 + ["ADD-C03", "ADD-C09"]
    if "二次破裂・延焼による連鎖損傷" in t:
        return c01 + ["ADD-C03", "ADD-C10"]
    if "構外に及び" in t and "起因" in t:
        return c01 + ["ADD-C02", "ADD-C04", "ADD-C05", "ADD-C11"]
    if "起因の火災・爆発による設備損壊" in t:
        return c01 + ["ADD-C03"]
    if "流出した液炭化水素・油分が側溝" in t:
        return c01 + ["ADD-C02", "ADD-C17"]
    if "消火排水" in t:
        return c01 + ["ADD-C03", "ADD-C18"]
    if "未燃の炭化水素（VOC）" in t:
        return c01
    # --- 個別の結果事象：文言で判断 ---
    cs = []
    if re.search(r"漏洩|漏入|放出|流出|噴出|溢出", t) and not integ:
        cs.append("ADD-C01")
    if re.search(r"破裂|破損|損傷|損壊|焼損|焼損|破断|クリープ", t) and "ADD-C01" not in cs and not integ:
        cs.append("ADD-C01")
    if re.search(r"着火|火災|火炎|火球", t):
        cs.append("ADD-C03")
    if re.search(r"爆発", t) and "内部爆発" not in t:
        cs.append("ADD-C04")
    if "複数" in t and re.search(r"死亡|重傷", t):
        cs.append("ADD-C07")
    elif re.search(r"死亡|重傷|熱傷|凍傷|曝露し", t):
        cs.append("ADD-C06")
    if re.search(r"土壌|水域|排水系", t) and "消火排水" not in t:
        cs.append("ADD-C17")
    if "構外" in t:
        cs.append("ADD-C11")
    if "凍結" in t:
        cs.append("ADD-C19")
    if not cs and re.search(r"規格外|減産|停止|損失|収率|性能|交換|寿命|経済", t):
        cs.append("ADD-C20")
    return cs


# ------------------------------------------------------------------
# 重大度（添付の重大度マトリクスに準拠）
# ------------------------------------------------------------------
SCALE_NAME = {"S": "小規模放出源（シール・継手・取付部等）", "M": "中規模放出源（配管・熱交換器・圧縮機等）", "L": "大規模放出源（塔・ドラム・反応器等の容器）"}


def source_scale(t):
    """結果事象の放出源（文頭の場所）から規模を判定：L=容器在庫、M=配管・機器、S=シール・継手等"""
    loc = re.split(r"起因|からの|から|の火災|の火炎", t)[0]
    if re.search(r"本体|塔頂系|塔体|塔・ドラム|放出点|貯蔵|外部受入|T-0\d・|・D-\d01|D-\d01・|D-\d01本体|容器|閉鎖排液系受槽|閉鎖ガス処理ヘッダ|複数の|複数機器|V-00破損部|R-01過熱部|底部ドレン", loc):
        return "L"
    if re.search(r"配管|ライン|ヘッダ|合流部|コイル|チューブ|管板|リボイラ|K-02|E-\d|ドレン|排液", loc):
        return "M"
    if re.search(r"シール部|サンプリング点|取付部|継手|計装取出し|開放部|保護管", loc):
        return "S"
    return "M"


def severity(t):
    """重大度（受領した重大度マトリクスに準拠）。
    ビジネス・環境は放出源の規模で段階づけ（第2段の重大度見直し）。人身（安全）は死傷の内容で判定し規模に依存させない"""
    s = e = b = None
    why = []
    sc = source_scale(t)
    if "複数" in t and re.search(r"死亡", t):
        s = 5; why.append("安全5：複数のオンサイト死亡")
    elif re.search(r"死亡", t):
        s = 4; why.append("安全4：単独のオンサイト死亡")
    elif re.search(r"重傷|熱傷|凍傷|火傷|負傷", t):
        s = 3; why.append("安全3：記録すべき傷害")
    elif re.search(r"酸素欠乏", t):
        s = 4; why.append("安全4：死亡")
    # 環境
    if re.search(r"土壌・公共水域|公共水域・土壌|排水系・土壌|土壌・排水系", t) and "消火" not in t:
        e = 3 if sc == "S" else 4
        why.append(f"環境{e}：土壌・水域汚染（{SCALE_NAME[sc]}のため{'流出量は限定的で数週間の浄化' if e == 3 else '数か月〜数年の浄化'}）")
    elif re.search(r"消火排水|冷却水ブローダウン|排水系・水域|使用済触媒|凝縮水・熱媒が排水系", t):
        e = 3; why.append("環境3：一時的放出、数週間での浄化")
    elif re.search(r"大気へ直接放出|大規模な可燃性蒸気雲|大量の未燃", t):
        e = 3; why.append("環境3：一時的な大量放出")
    elif re.search(r"VOC|黒煙|大気環境汚染|一酸化炭素|大気中に放出|大気へ排出", t):
        e = 2; why.append("環境2：軽微な大気排出")
    # ビジネス（放出源の規模で段階づけ）
    if re.search(r"構外に及び|BLEVE", t):
        b = 5; why.append("ビジネス5：広域設備損壊・社会的影響（1億ドル以上）")
    elif "連鎖損傷" in t:
        b = 5 if sc == "L" else 4
        why.append(f"ビジネス{b}：火災による連鎖損傷（{SCALE_NAME[sc]}）")
    elif "蒸気雲爆発" in t:
        b = 4 if sc == "S" else 5
        why.append(f"ビジネス{b}：蒸気雲爆発による設備破壊（{SCALE_NAME[sc]}）")
    elif re.search(r"長期操業停止|長期停止|プラント全体の長期停止", t):
        if re.search(r"火災|爆発", t):
            b = {"L": 5, "M": 4, "S": 3}[sc]
            why.append(f"ビジネス{b}：火災・爆発後の停止（{SCALE_NAME[sc]}："
                       + {"L": "容器・塔の損壊で半年以上の停止を想定", "M": "配管・機器の損傷で数か月の停止を想定", "S": "局所火災で数週間の停止を想定"}[sc] + "）")
        else:
            b = 4; why.append("ビジネス4：長期停止")
    elif re.search(r"火炉爆発|内部爆発|破裂|冷却塔の火災", t):
        b = 4; why.append("ビジネス4：主要設備の損壊（2500万〜1億ドル）")
    elif re.search(r"噴流火災|プール火災|火球", t):
        b = 4 if sc == "L" else 3
        why.append(f"ビジネス{b}：火災による設備損傷（{SCALE_NAME[sc]}）")
    elif re.search(r"K-02.*(破損|損傷)|圧縮機.*破損", t):
        b = 4; why.append("ビジネス4：圧縮機の損傷と長期停止")
    elif re.search(r"触媒交換|触媒の抜出し|触媒寿命|触媒.*失活|触媒性能", t):
        b = 3; why.append("ビジネス3：触媒交換・性能低下（100万〜2500万ドル規模と仮定）")
    elif re.search(r"フラッシュ火災|火災|焼損|爆発", t):
        b = 3; why.append("ビジネス3：中規模の設備損傷")
    elif re.search(r"規格外|出荷停止|プラント全体|全装置|反応系が停止|反応系の長期|複数装置|全塔停止", t):
        b = 3; why.append("ビジネス3：操業停止・出荷停止")
    elif re.search(r"損傷|破損|過熱|コーキング|閉塞|液撃|サージング|汚染", t):
        b = 2; why.append("ビジネス2：機器損傷・軽微な操業影響")
    elif re.search(r"減産|損失|収率|性能低下|負荷|過圧|過充填|吹き抜け|放出|漏洩|流入|上昇|低下", t):
        b = 2; why.append("ビジネス2：軽微な操業影響")
    else:
        b = 1; why.append("ビジネス1：軽微")
    kinds = [k for k, v in (("人身・安全", s), ("環境", e), ("ビジネス", b)) if v]
    return s, e, b, "／".join(kinds), "；".join(why)


# ------------------------------------------------------------------
# 原因→結果の対応（群内の物理的関係を確認したうえでの上書き定義）
#   (原因番号タプル, 結果判定関数)  ※原因番号は第1段の C番号
# ------------------------------------------------------------------
def kw(*ws):
    return lambda t: any(w in t for w in ws)


ALL = lambda t: True
OVERRIDES = {
    # 組成異常：異常の種類ごとに到達する結果が異なる。受入分析の誤り(C4)は単独では組成異常を生まない
    "Z1-05": [((5,), kw("C3等軽質分", "規格外")), ((3,), ALL), ((1,), kw("不飽和分", "規格外")), ((2,), kw("遊離水", "触媒被毒", "規格外"))],
    # Feyzin型：運転員の閉止忘れ(C1)・弁座損傷(C4)は単独、凍結(C2)は単弁操作(C3)とのANDで閉止不能
    "Z1-16": [((1,), ALL), ((4,), ALL), ((2, 3), ALL)],
    # 置換不十分(C1)は確認分析の誤り(C2)とのANDで見逃される／受入弁の早すぎる開放(C3)は単独
    "Z1-22": [((1, 2), ALL), ((3,), ALL)],
    # 塔の過充填：計器配置の不備(C3)は起動時の過剰張込み(C6)とのAND／加熱不足(C7)は液位計誤指示(C1)とのAND
    "Z2-14": [((1,), ALL), ((2,), ALL), ((4,), ALL), ((5,), ALL), ((3, 6), ALL), ((7, 1), ALL)],
    "Z3-14": [((1,), ALL), ((2,), ALL), ((4,), ALL), ((5,), ALL), ((3, 6), ALL), ((7, 1), ALL)],
    "Z7-14": [((1,), ALL), ((2,), ALL), ((3,), ALL), ((4,), ALL), ((5, 6), ALL)],
    # 起動・停止：内部爆発は置換不十分(C4)のみ、過充填・過圧系は他の原因
    "Z2-23": [((4,), kw("内部爆発")), ((1,), lambda t: "内部爆発" not in t), ((2,), lambda t: "内部爆発" not in t),
              ((3,), lambda t: "内部爆発" not in t), ((5,), lambda t: "内部爆発" not in t)],
    "Z3-23": [((4,), kw("内部爆発")), ((1,), lambda t: "内部爆発" not in t), ((2,), lambda t: "内部爆発" not in t),
              ((3,), lambda t: "内部爆発" not in t), ((5,), lambda t: "内部爆発" not in t)],
    "Z7-20": [((3,), kw("内部爆発")), ((1,), lambda t: "内部爆発" not in t), ((2,), lambda t: "内部爆発" not in t),
              ((4,), lambda t: "内部爆発" not in t)],
    # V-701液位：液の持込み(C3)と、排液遅れ(C1)または液面計誤指示(C2)のAND
    "Z4-11": [((3, 1), ALL), ((3, 2), ALL)],
    # 加熱炉燃焼系：失火(C1)・停止中の燃料流入(C3)と再点火時パージ不十分(C4)のAND、失火未検知(C1&C5)、空気喪失(C2&C5)
    "Z4-21": [((1, 4), lambda t: "一酸化炭素" not in t), ((3, 4), lambda t: "一酸化炭素" not in t),
              ((1, 5), lambda t: "一酸化炭素" not in t), ((2, 5), lambda t: "一酸化炭素" not in t),
              ((2,), kw("一酸化炭素")), ((1,), kw("一酸化炭素"))],
    # H2比：低下(C1,C3)→コーキング、上昇(C2)→副反応
    "Z5-04": [((1,), kw("H2比低下", "触媒寿命")), ((3,), kw("H2比低下", "触媒寿命")), ((2,), kw("H2比上昇", "触媒寿命"))],
    # 触媒交換：パージ不十分→フラッシュ火災、自己発熱→触媒火災、酸欠は不活性雰囲気(C3)と許可手順逸脱(C4)のAND
    #           使用済触媒・洗浄排水の不適切処理による汚染は第1段に対応原因がない → 原因未確定
    "Z5-11": [((1,), kw("フラッシュ火災")), ((2,), kw("自己発熱")), ((3, 4), kw("酸素欠乏"))],
    # V-01水分・微粉：微粉(C2)→閉塞、水分(C1)と水抜き未実施(C3)のAND
    "Z6-23": [((2,), kw("閉塞")), ((1, 3), ALL)],
    # E-701：熱媒喪失(C1)・汚れ(C3)は吸込温度低下→K-02液吸込み、伝熱管漏洩(C2)のみが熱媒側漏入・外部放出
    "Z4-13": [((1,), kw("K-02吸込ガス温度")), ((3,), kw("K-02吸込ガス温度")), ((2,), lambda t: "K-02吸込ガス温度" not in t)],
    # 塔内部品の脱落(C6)は塔内の分離不良であり外部漏洩の経路を構成しない
    "Z2-22": [((i,), ALL) for i in (1, 2, 3, 4, 5)],
    "Z3-22": [((i,), ALL) for i in (1, 2, 3, 4, 5)],
}


def build():
    causes = OrderedDict()   # text -> dict
    results = OrderedDict()  # text -> dict
    unused_cause_refs = []
    paths = []
    for g in h.GROUPS:
        gz = g["z"]
        cids = []
        for i, t in enumerate(g["causes"], 1):
            sid = f"{g['id']}-C{i:02d}"
            if t not in causes:
                f, why = cause_freq(t)
                causes[t] = dict(id=f"CS-{len(causes) + 1:04d}", text=t, zones=[], refs=[], freq=f, why=why)
            c = causes[t]
            if gz not in c["zones"]:
                c["zones"].append(gz)
            c["refs"].append(sid)
            cids.append((i, c, sid))
        rlist = []
        for i, (t, cats) in enumerate(g["results"], 1):
            sid = f"{g['id']}-R{i:02d}"
            if t not in results:
                results[t] = dict(id=f"RS-{len(results) + 1:04d}", text=t, zones=[], refs=[], cats=set(cats))
            r = results[t]
            rz = zone_of_text(t, gz)
            if any(k in t for k in ("閉鎖ガス処理系の受入能力", "放出先の能力不足", "大気放出された蒸気雲", "放出点周辺の蒸気雲爆発", "大量の未燃炭化水素", "燃焼設備へ液が持ち込まれ")):
                rz = 0
            if rz not in r["zones"]:
                r["zones"].append(rz)
            r["refs"].append(sid)
            rlist.append((i, r, sid, rz))
        spec = OVERRIDES.get(g["id"], [((i,), ALL) for i, _, _ in cids])
        cmap = {i: (c, sid) for i, c, sid in cids}
        used = set()
        for ctuple, pred in spec:
            for ri, r, rsid, rz in rlist:
                if not pred(r["text"]):
                    continue
                if not adopted(rsid):
                    continue
                cs = [cmap[k] for k in ctuple]
                if not all(adopted(sid) for _, sid in cs):
                    continue
                used.update(ctuple)
                paths.append(dict(group=g, causes=cs, result=r, rsid=rsid, rz=rz, conds=conditions(r["text"], g, [c["text"] for c, _ in cs])))
        for i, c, sid in cids:
            if i not in used and adopted(sid):
                unused_cause_refs.append((c, sid, g))
    # ---- 中間事象型原因「上流機器の過充填」の結び直し（第3段の検討で追加）----
    # Z0-06の結果事象へ、上流の各容器・塔の過充填偏差（物理的原因）からの経路を追加する。
    # 経路の偏差群は上流側（例：Z1-11）とし、その位置の高高液位インターロック等が遮断位置となる。
    gz06 = next(g for g in h.GROUPS if g["id"] == "Z0-06")
    up_groups = ["Z1-11", "Z2-07", "Z2-14", "Z3-07", "Z3-14", "Z6-06", "Z7-08", "Z7-14"]
    seen_k = set()
    add = []
    for p in paths:
        if p["group"]["id"] in up_groups:
            key = (p["group"]["id"], tuple(sid for _, sid in p["causes"]))
            if key in seen_k:
                continue
            seen_k.add(key)
            for i, (t, cats) in enumerate(gz06["results"], 1):
                rsid = f"Z0-06-R{i:02d}"
                if not adopted(rsid):
                    continue
                r = results[t]
                add.append(dict(group=p["group"], causes=p["causes"], result=r, rsid=rsid, rz=0,
                                conds=conditions(t, gz06, [c["text"] for c, _ in p["causes"]]), relink="Z0-06"))
    paths.extend(add)
    return causes, results, paths, unused_cause_refs
