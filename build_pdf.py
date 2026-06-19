# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                ListFlowable, ListItem, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Japanese fonts ---
pdfmetrics.registerFont(TTFont('JP', '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf'))
pdfmetrics.registerFont(TTFont('JPm', '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'))

NAVY = colors.HexColor('#2b3a55')
RED  = colors.HexColor('#c0392b')
GREEN= colors.HexColor('#1e7d34')
LBG  = colors.HexColor('#f2f4f8')
LBG2 = colors.HexColor('#f5f7fb')
YEL  = colors.HexColor('#fff8e1')
GREY = colors.HexColor('#555555')

styles = getSampleStyleSheet()
def S(name, **kw):
    base = dict(fontName='JP', fontSize=10.5, leading=16, textColor=colors.HexColor('#111111'),
                alignment=TA_LEFT, spaceAfter=4)
    base.update(kw)
    return ParagraphStyle(name, **base)

body   = S('body')
small  = S('small', fontSize=8.8, leading=12.5, textColor=GREY)
meta   = S('meta', fontSize=9, leading=13, textColor=GREY)
h1     = S('h1', fontName='JP', fontSize=17, leading=21, textColor=colors.HexColor('#111111'), spaceAfter=2)
h3     = S('h3', fontName='JP', fontSize=11.5, leading=16, textColor=colors.HexColor('#111111'),
           spaceBefore=10, spaceAfter=3, leftIndent=6, borderColor=NAVY)
lead   = S('lead', fontSize=10, leading=15.5)
note   = S('note', fontSize=10, leading=15)
cell   = S('cell', fontSize=9.0, leading=12.5, spaceAfter=0)
cellh  = S('cellh', fontSize=9.2, leading=12.5, textColor=colors.white, spaceAfter=0)
cellb  = S('cellb', fontSize=9.0, leading=12.5, textColor=colors.HexColor('#8a1f1f'), spaceAfter=0)
cella  = S('cella', fontSize=9.0, leading=12.5, textColor=colors.HexColor('#14532d'), spaceAfter=0)

story = []

def H2(text):
    p = Paragraph(text, S('h2', fontSize=13, leading=17, textColor=colors.white, spaceBefore=0, spaceAfter=0))
    t = Table([[p]], colWidths=[None])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),NAVY),
        ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    story.append(Spacer(1,12)); story.append(t); story.append(Spacer(1,7))

def H3(text):
    p = Paragraph(text, h3)
    t = Table([[p]], colWidths=[None])
    t.setStyle(TableStyle([
        ('LINEBEFORE',(0,0),(0,-1),5,NAVY),
        ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
    ]))
    story.append(Spacer(1,7)); story.append(t); story.append(Spacer(1,2))

def P(text, st=body):
    story.append(Paragraph(text, st))

def box(text, bg, border, st=note):
    p = Paragraph(text, st)
    t = Table([[p]], colWidths=[None])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),bg),('BOX',(0,0),(-1,-1),0.8,border),
        ('LEFTPADDING',(0,0),(-1,-1),11),('RIGHTPADDING',(0,0),(-1,-1),11),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
    ]))
    story.append(t); story.append(Spacer(1,4))

def UL(items):
    flow = [ListItem(Paragraph(it, body), value='•', leftIndent=14) for it in items]
    story.append(ListFlowable(flow, bulletType='bullet', start='•', leftIndent=10, bulletColor=NAVY))

def OL(items):
    flow = [ListItem(Paragraph(it, body)) for it in items]
    story.append(ListFlowable(flow, bulletType='1', leftIndent=14))

def badge(text, color=RED):
    return ('<font name="JP" size="8" color="white"> %s </font>' % text)  # placeholder, replaced below

def mk_table(header, rows, widths, header_style=cellh, body_cell=cell, zebra=True, before_after=False):
    data = []
    data.append([Paragraph(h, header_style) for h in header])
    for r in rows:
        row = []
        for i, c in enumerate(r):
            stl = body_cell
            if before_after:
                if i == len(r)-1: stl = cella
                elif i == 1 and len(r) >= 4: stl = cellb
            row.append(Paragraph(c, stl))
        data.append(row)
    t = Table(data, colWidths=widths, repeatRows=1)
    ts = [
        ('BACKGROUND',(0,0),(-1,0),NAVY),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#99a0b0')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
    ]
    if zebra:
        for ri in range(1, len(data)):
            if ri % 2 == 0:
                ts.append(('BACKGROUND',(0,ri),(-1,ri),LBG2))
    t.setStyle(TableStyle(ts))
    story.append(t); story.append(Spacer(1,10))

# ===================== CONTENT =====================
story.append(Paragraph('『サイバークライシス』初稿（0612）レビューと改訂提案', h1))
story.append(Spacer(1,4))
story.append(Paragraph('対象：サイバーセキュリティ啓発ドラマ（内容尺7分）＋解説ブロック ／ 脚本：水野宗徳', meta))
story.append(Paragraph('作成日：2026-06-19 ／ 観点：①現象の無理 ②シナリオの流れ ③放送上の懸念 ④改善提案 ＋ 改訂版構成案・赤入れ', meta))

H2('0. 総評')
box('啓発の狙い（「自分は関係ないと思っている中小企業こそ穴がある」）と、「落とし穴＝見えない脆弱性」というメタファーの着想は良い。'
    '最大の弱点は<b>「1社の標的型メール1通が、同日中に全国の電力・鉄道・金融・信号まで停止させる」という因果の飛躍</b>で、'
    '技術的破綻・放送リスク・啓発効果の低下がここに集約している。被害規模を<b>「木川精機 → 取引先 → 業界（サプライチェーン）」</b>に'
    '現実的に絞るだけで多くの問題が同時に解決する。また、啓発の核である<b>「最初の侵入経路（視聴者が学ぶべき落とし穴）」が一切描かれていない</b>'
    '点の補強が必須。', LBG, colors.HexColor('#ccd3df'), st=lead)

H2('1. 技術的に「無理がある」点')

H3('① 1通のメールから全国インフラ崩壊への飛躍　【最重要】')
UL([
 'メールの宛先はアドレス帳内（取引先）に限られ、金融・鉄道・電力など<b>無関係セクターへ届く経路が存在しない</b>。',
 'オフィスのIT系感染が、工場の生産ライン（OT系）や電力網・信号といった<b>物理インフラへ同日中に自動波及するのは非現実的</b>（本来分離されたネットワークを多段で越える必要がある）。',
 '特に「信号機が消える」「電光掲示が消える」「オフィスの電気が消える」＝<b>停電はメールのマクロでは起こせない</b>。サイバー侵害（情報）と物理破壊（電力供給）の混同。',
])

H3('② 「停電なのにPCが点いている」　【指摘を取り下げ】')
box('ご指摘の通り、<b>ノートPC（バッテリー駆動）であれば停電中も稼働するのは自然</b>。本指摘は取り下げる。'
    'デスクトップPC前提で描く場合のみ、UPS等の説明があると無難、という注記に留める。', YEL, colors.HexColor('#e0c97a'))

H3('③ 政府の特殊部隊が被害企業を“急襲”する　【事実誤認リスク】')
UL([
 '能動的サイバー防御／サイバー対処能力強化法（2025年成立）は、基本的に<b>攻撃者側インフラへの対処</b>や重要インフラ事業者の<b>報告義務</b>等を枠組みとするもので、<b>被害企業（踏み台にされた被害者）へ武装部隊が物理的に突入する建付けではない</b>。',
 '木川精機は<b>加害者ではなく被害者</b>。犯人扱いのように急襲し「もっと早く連絡を」と叱責する展開は、法制度・被害者対応の実態とずれる。',
 '脚本に「自衛隊の制服（？）」と「？」が付いている＝書き手も不確かと自覚。<b>法務・政策の監修が必須</b>。',
])

H3('④ PCがGUIを自分で操作する“ハリウッド描写”')
P('カーソルが勝手に動きメールソフトが開く見せ方は、実際のマルウェア（バックグラウンドで静かに送信）と異なる。目の前の社長がカーソルの暴走に気づかないのも不自然。')

H3('⑤ 「送信済み5000件超」')
P('中小企業のアドレス帳で5000件・同一文面の大量送信は、メールサーバ／プロバイダの<b>レート制限・スパム判定で早期にブロック</b>されるのが普通。ここまで“成功”し続けるのは無理がある。')

H3('⑥ 監視カメラのレンズが激しく動く')
P('ビジュアルは良いが、乗っ取られたカメラがレンズを激しく動かす必然性は薄く、<b>この伏線は回収されない</b>（後段の攻撃と無関係）。')

H3('⑦ .xlsm を開いた瞬間に感染')
P('近年のOfficeはネット／メール由来のマクロを<b>既定でブロック</b>し「コンテンツの有効化」を押させる一手間が要る。ここは<b>最大の“教える価値がある落とし穴”</b>なので、省略せず啓発ポイントに転化すべき。')

H3('⑧ 誤記・表記の揺れ（校正）')
P('「平常可動」→「平常<b>稼働</b>」／「早押すする」→「早押しする」／多田の年齢が<b>(28)と(29)で揺れ</b>。')

story.append(PageBreak())
H2('2. シナリオ・構成の問題')

H3('① 「最初の感染経路」が描かれていない　【啓発として致命的】')
P('物語開始時点で社長PCは既に感染済み。<b>“どの落とし穴を踏んで侵入されたのか”＝視聴者が学ぶべき一番大事な点が空白</b>。ラストの独白「どこに落とし穴があったんだ」も答えが出ない。')

H3('② 主人公（セキュリティ担当）が有効な行動をしない')
P('多田は異常なカメラに気づいても「前からそんな感じでは」と立ち去る。担当者として受け身で、「正しく動けば防げた／軽減できた」という<b>啓発の手本になっていない</b>。')

H3('③ 妻の出産サブプロットの因果が強引')
UL([
 '攻撃と同日に陣痛、停電でエレベーター停止・救急も不通…と危機を盛るが、<b>サイバー被害と個人の危機の結びつきが作為的</b>。',
 'エレベーターで倒れた後、停電下でどう病院へ運ばれたか説明がなく、次は無事ベッドに。<b>危機の演出だけして処理を省略</b>しており御都合主義に見える。',
])

H3('④ 回収されない伏線・宙づりの要素')
P('監視カメラ／掃除のおばさんは張られて放置。攻撃者の正体・動機も不明のまま（ドラマとしては可だが「穴」メタファーと混線）。')

H3('⑤ メタファーの混線')
P('「穴」が (a)外部の攻撃者 (b)自社の脆弱性 (c)運命的な落とし穴 の間で揺れ、ナレーション「穴のM」が誰／何の声か曖昧。'
  '<b>「あなた自身の中の穴」（内的要因）と「乗っ取る外敵」（外的要因）が一つの記号に同居</b>してメッセージがぼやける。')

H3('⑥ 解説ブロックが未完・内部メモの残存')
P('肝心の対策解説とQ&amp;Aが「あとで記述します」。さらに<b>「越島先生の監修はどのタイミングか？」という社内メモが原稿に残存</b>。実在名らしき記載が成果物に混入しないよう除去を。')

H2('3. 放送する上での懸念')
OL([
 '<b>実在法制度の誤解を広げるリスク</b>：被害企業を武装急襲する描写は、施行直後の法への誤ったイメージ（過剰な萎縮・反発）を植え付けかねない。<b>法務・政策監修を必須</b>に。',
 '<b>実在企業との誤認</b>：「東海自動車」は地域名＋業種で実在メーカーを想起させる。<b>明確な架空名＋「フィクション」表示</b>を。',
 '<b>過度な恐怖・無力感の助長</b>：「中小1社のミスで全国崩壊＋倒産＋家族の危機＋政府急襲」は、対象である中小企業に「どうせ防げない」という<b>諦め</b>を与え、狙い（=「あなたにできることがある」）と逆効果になりうる。',
 '<b>被害者への過度な帰責トーン</b>：被害企業を“元凶”として断罪する描き方は被害者非難に傾き、<b>相談・通報をためらわせる逆メッセージ</b>になりうる。',
 '<b>妊婦の危機演出への配慮</b>：センシティブな題材を恐怖演出に使う是非。放送基準・視聴者の受け止めを考慮。',
 '<b>専門家視聴者からの信頼低下</b>：メール→全国停電の飛躍は監修者・スポンサー・詳しい視聴者の信用を損ね、番組全体の説得力を下げる。',
 '<b><font color="#1e7d34">（プラス評価）模倣リスクは低い</font></b>：具体的な攻撃手順・ツール・コマンドが出ておらず how-to 流出の懸念は小さい。この長所は維持を。',
])

story.append(PageBreak())
H2('4. 改善提案（方針）')
mk_table(
 ['項目','提案'],
 [
  ['<b>A. 規模を現実化</b>','全国インフラ崩壊・停電をやめ、<b>サプライチェーン波及型</b>（木川精機→取引先→業界の操業停止）に限定。技術破綻が消え、「下請けの穴が大手と業界を止める」という対象に刺さる説得力が出る。'],
  ['<b>B. 侵入経路を描く</b>','感染のきっかけ（付箋パスワード／マクロ有効化を促す不審メール／放置された管理者権限など）を具体的に1つ見せ、解説で回収。<b>学びの核</b>を作る。'],
  ['<b>C. 主人公を能動に</b>','多田に「検知→進言→阻まれる→通報判断」の選択を与え、<b>分かれ目の一手</b>を描く。視聴者が自己投影できる担当者へ。'],
  ['<b>D. 政府パート修正</b>','武装急襲ではなく<b>専門機関（JPCERT/CC・警察・所管省庁等）と連携した隔離・封じ込め支援</b>へ。台詞は「早く相談・報告を」という前向きな教訓に。'],
  ['<b>E. 家族は“動機”に</b>','出産危機をサイバー被害の直接結果にせず、<b>守りたい家族＝多田が穴を放置できない動機</b>として軽く配置。'],
  ['<b>F. メタファー整理</b>','「穴＝見過ごされた脆弱性」に意味を一本化。監視カメラ伏線は<b>侵入経路として回収</b>するか削除。'],
  ['<b>G. 放送上の安全装置</b>','冒頭/末尾に<b>「フィクション」表示</b>、社名は完全架空。<b>技術・法務の二系統の監修クレジット</b>。解説側でドラマの演出部分を「ここは演出。実際は～」と補正。内部メモの除去。'],
 ],
 widths=[32*mm, None])

story.append(PageBreak())
H2('5. 改訂版 構成案（ビート表・全7分＋解説）')
P('方針：被害を<b>サプライチェーンに限定</b>／<b>侵入経路を可視化</b>／<b>主人公を能動化</b>／<b>政府パートを実態化</b>／<b>家族は動機づけ</b>。', small)
mk_table(
 ['尺目安','シーン','内容・狙い'],
 [
  ['0:00–0:40','アバン（街の穴／デジタル社会）','既存の「穴」メタファーを活用。ただし<b>「穴＝見過ごされた脆弱性」に一本化</b>。ナレーション主体（穴のM）を「見過ごされた弱点の声」と明確化。'],
  ['0:40–1:30','木川精機・社長室／現場','多田の進言と社長の拒否（「下請けを狙うヤツいるか」）。工場長・津山の不安。<b>※既存を活用</b>。法律への言及は正確な表現に。'],
  ['1:30–2:30','<b>【新規】侵入経路を見せる</b>','多田が具体的な“穴”を目撃：付箋パスワード／「コンテンツの有効化」を促す不審添付／管理者権限の放置 等。だが予算却下で対処を見送る＝<b>後で回収する学びの核</b>。監視カメラ異常も侵入兆候として提示。'],
  ['2:30–3:20','感染の進行','社長PCが取引先へ不正メール送信。GUIを派手に操らず<b>「送信済みが静かに増える」示唆</b>に。件数は具体数を出さない。一部はブロックされるが取引先には届く現実感。'],
  ['3:20–4:30','取引先で被害顕在化','<b>架空名の取引先</b>で部品ラインが停止→納入が止まり<b>業界に波及</b>。報道は「取引先・関連企業で同様の被害」までに限定。<b>全国インフラ崩壊・停電点描は削除</b>。'],
  ['4:30–5:30','気づきと葛藤（ドラマの山）','多田が自社が踏み台と気づく→<b>通報・報告を進言</b>→社長が信用失墜を恐れ制止。家族（臨月の妻）の存在を<b>動機として軽く挿入</b>（危機の直接因果にしない）。'],
  ['5:30–6:20','封じ込めと代償','<b>専門機関と連携</b>したネットワーク隔離・封じ込め支援（武装急襲は削除）。班長相当の台詞は「<b>早く相談していれば被害を抑えられた</b>」という前向き教訓へ。取引先の操業停止・契約問題という現実的な代償。'],
  ['6:20–7:00','余韻と問いかけ','記者会見での反省。多田の独白「どこに落とし穴が」→<b>第3シーンの穴に視線が戻る</b>形で回収準備。妻子の無事は短く。「あなたにできることは？」で締め。'],
  ['—','解説ブロック','穴吹講師が<b>第3シーンの穴を名指しで回収</b>。具体策：①マクロ無効化／添付の扱い ②多要素認証・パスワード管理（付箋禁止）③EDR等の検知 ④<b>インシデント時の報告先（IPA／JPCERT/CC／警察）</b> ⑤サプライチェーン上の責任。演出誇張は「ここは演出、実際は～」と補正。<b>技術＋法務監修</b>を明記。'],
 ],
 widths=[18*mm, 38*mm, None])

story.append(PageBreak())
H2('6. 赤入れ（修正前 → 修正後）')
mk_table(
 ['箇所','現状（修正前）','問題','修正案（修正後）'],
 [
  ['P5–6 街のパニック点描','ATM不可／鉄道「運転見合わせ」／物流大渋滞／「金融・鉄道・物流の一部システムに影響」','無関係セクターへ波及する経路なし。過度な恐怖。','<b>削除</b>。代わりに「取引先・関連企業で同様の被害が確認」までに限定し、サプライチェーン波及に絞る。'],
  ['P7 停電点描','信号機が消える／電光掲示が消える／フロアの電気が消える','メールのマクロでは停電は起こせない（IT侵害≠物理破壊）。','<b>削除</b>。緊迫感は「取引先からの操業停止連絡が殺到」「契約解除の示唆」など<b>事業影響</b>で出す。'],
  ['P8–9 特殊部隊突入','自衛隊の制服（？）の特殊部隊が突入／「政府サイバー対策本部です」／隔離・無害化措置','被害企業への武装急襲は法の建付けと異なる。事実誤認。','武装急襲を<b>専門機関（JPCERT/CC・警察・所管省庁）との連携による封じ込め支援</b>に変更。遠隔対応＋担当者来訪程度に。<b>法務監修必須</b>。'],
  ['P9 班長の台詞','「もっと早く連絡をいただけていれば、被害は抑えられたかもしれません」','被害者非難に傾く／通報を萎縮させる。','「<b>気づいた時点ですぐ報告・相談していれば、影響をここまで広げずに済みました。次に活かしましょう</b>」＝前向きな教訓へ。'],
  ['全編 取引先名','東海自動車（本社）','実在メーカーを想起。誤認リスク。','明確な架空名（例：「<b>メイユー自動車</b>」等）＋冒頭/末尾に<b>「この物語はフィクションです」表示</b>。木川精機も実在確認を。'],
  ['P4 社長PCの送信','カーソルが勝手に動く／メール画面／送信','実マルウェア挙動と異なる“ハリウッド描写”。','派手なGUI操作を控え、<b>「送信済みが静かに増えていく」</b>カット＋通知音程度の示唆に。'],
  ['P7 送信件数','『送信済みアイテム』が5000件を超えている','レート制限・スパム判定で非現実的。','具体数を出さず<b>「送信済みが止まらない」</b>程度に。または「一部はブロックされたが取引先には届いた」と補う。'],
  ['P4–5 .xlsm 開封','添付「ゴルフコンペ案内.xlsm」を開いた瞬間に感染が進む','既定でマクロはブロック。一手間が要る。','<b>「コンテンツの有効化」をクリックしてしまう描写</b>を入れ、解説で「これが落とし穴」と回収＝<b>教材化</b>。'],
  ['P3–4 監視カメラ','レンズが激しく動く／多田「前からあんな感じでは」と立ち去る','伏線未回収／担当者が受け身。','カメラ異常を<b>侵入兆候として回収</b>（解説で言及）。多田は<b>不審に思い報告・調査を進言</b>する側に。'],
  ['P7–8 妻の危機','陣痛中に停電でエレベーター停止／救急もタクシーアプリも不通／倒れる','サイバー被害との因果が強引／処理を省略。','サイバー被害の<b>直接結果にしない</b>。妻子は多田の<b>動機づけ</b>として短く描き、出産は無事に。'],
  ['全編 侵入経路','物語開始時点で社長PCが既に感染済み（経緯なし）','学びの核が空白。','<b>新規シーン（ビート表1:30–2:30）を追加</b>し、最初の落とし穴を可視化→解説で回収。'],
  ['P11 解説ブロック','「あとで記述します。越島先生の監修はどのタイミングか？」','内部メモが原稿に残存／対策内容が未定。','<b>内部メモを削除</b>。具体策（マクロ無効化・多要素認証・パスワード管理・報告先・サプライチェーン責任）を明記し<b>技術＋法務監修</b>を入れる。'],
  ['P2/P3 ほか 校正','多田(28)/(29)の揺れ／「平常可動」／「早押すする」','表記の誤り。','年齢を統一／「平常<b>稼働</b>」／「早押しする」。'],
  ['②（再掲）停電とPC','停電後もPCが点いている','<font color="#1e7d34">指摘取り下げ</font>','<b>ノートPC前提なら矛盾なし</b>。デスクトップ前提で描く場合のみUPS等の説明を補う。'],
 ],
 widths=[24*mm, 46*mm, 26*mm, None], before_after=True)

story.append(Spacer(1,10))
P('― 本書は初稿（0612）に対するレビューと改訂提案。最終稿化に際しては、技術監修（インシデント対応・マルウェア挙動）および'
  '法務・政策監修（サイバー対処能力強化法／能動的サイバー防御の正確な記述）を併せて受けることを推奨する。―', small)

# ---- footer with page numbers ----
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('JP', 8)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(A4[0]/2, 10*mm, '%d' % doc.page)
    canvas.drawString(16*mm, 10*mm, '『サイバークライシス』初稿 レビューと改訂提案')
    canvas.restoreState()

doc = SimpleDocTemplate('/home/user/temporary/サイバークライシス_初稿_レビューと改訂提案.pdf',
                        pagesize=A4, topMargin=18*mm, bottomMargin=16*mm,
                        leftMargin=16*mm, rightMargin=16*mm,
                        title='サイバークライシス 初稿 レビューと改訂提案')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print('done')
