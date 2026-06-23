# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('JP','/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf'))
NAVY=colors.HexColor('#2b3a55'); GREY=colors.HexColor('#555555')

def S(n,**k):
    b=dict(fontName='JP',fontSize=10.3,leading=15.5,textColor=colors.HexColor('#111111'),alignment=TA_LEFT,spaceAfter=3)
    b.update(k); return ParagraphStyle(n,**b)
title=S('t',fontSize=17,leading=21,alignment=TA_CENTER,spaceAfter=2)
subt =S('s',fontSize=9.6,leading=13,alignment=TA_CENTER,textColor=GREY,spaceAfter=2)
name =S('nm',fontSize=12,leading=16,textColor=NAVY,spaceBefore=8,spaceAfter=2)
body =S('b')
cell =S('c',fontSize=9,leading=12.5,spaceAfter=0)
cellh=S('ch',fontSize=9.2,leading=12.5,textColor=colors.white,spaceAfter=0)
h1   =S('h',fontSize=14,leading=18,textColor=NAVY,spaceBefore=6,spaceAfter=4)
small=S('sm',fontSize=8.8,leading=12.5,textColor=GREY)

def footer_maker(label):
    def f(c,doc):
        c.saveState(); c.setFont('JP',8); c.setFillColor(GREY)
        c.drawCentredString(A4[0]/2,10*mm,'%d'%doc.page)
        c.drawString(16*mm,10*mm,label); c.restoreState()
    return f

def tbl(header,rows,widths,zebra=True):
    data=[[Paragraph(h,cellh) for h in header]]
    for r in rows: data.append([Paragraph(c,cell) for c in r])
    t=Table(data,colWidths=widths,repeatRows=1)
    ts=[('BACKGROUND',(0,0),(-1,0),NAVY),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#99a0b0')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]
    if zebra:
        for i in range(1,len(data)):
            if i%2==0: ts.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#f5f7fb')))
    t.setStyle(TableStyle(ts)); return t

# ============ 1) CHARACTER BIBLE ============
st=[]
st.append(Paragraph('『サイバークライシス』登場人物設定書',title))
st.append(Paragraph('キャラクターバイブル／信頼経路版・作り込み稿準拠（社名・人物は架空）',subt))
def CH(nm, items):
    st.append(Paragraph(nm,name))
    for k,v in items:
        st.append(Paragraph('<b>%s</b>：%s'%(k,v),body))
CH('多田 啓二（ただ けいじ）／29歳 ― 主人公',[
 ('役割','総務部サイバーセキュリティ担当（実質ひとり情シス）'),
 ('人物像','生真面目で観察眼。社内では“煙たがられる正論”担当。声は大きくないが芯がある'),
 ('背景','中途3年目。前職で小インシデントを目撃し危機感。妻の出産を控え「守りたいもの」が明確'),
 ('口調','丁寧でロジカル。追い込まれると短く強く（「黙る理由には、ならない」）'),
 ('アーク','見過ごす側→見過ごさない側→声を上げつなぐ側。冒頭は穴を“避け”、ラストは“踏み外さずまたぐ”'),
 ('関係','木川＝突破すべき壁／津山＝現場の味方／由香＝行動の動機'),
])
CH('木川 宗吾（きかわ そうご）／65歳 ― 社長',[
 ('役割','代表取締役。創業家二代目'),
 ('人物像','職人気質で情に厚いがITは「コスト」。プライドが高く“下請けの矜持”が裏目に'),
 ('口調','断定調（「大げさだ」）→覚悟（「安全が確認できないものは使わない。それがものづくりだろう」）'),
 ('アーク','否認→動揺→葛藤→決断（公表・停止）。物語のもう一人の主人公'),
 ('注意','悪人でなく“よくある油断の象徴”。経営層が自分を重ねられるよう断罪しすぎない'),
])
CH('鈴木 工場長／50代 ― 現場責任者',[
 ('機能','「止めたら出荷も止まる」という現場のリアルを背負う。最後は社長の決断に深く頷く'),
])
CH('津山 郁美／30代 ― 管理部社員',[
 ('機能','現場の“気づき”役（付箋PWを最初に指摘）。「専門家でなくても気づける」象徴。多田の理解者'),
])
CH('多田 由香／20代後半 ― 多田の妻（妊娠中）',[
 ('機能','多田の“守りたいもの”。サイバー被害の直接の犠牲にはしない。出産は無事に（救いの提示）'),
 ('注意','危機を煽る道具にしない。短く、温かく'),
])
CH('穴吹 衛 ― 解説講師',[
 ('機能','解説進行。用語をかみ砕き、作中カットと対策を紐づけ。脅さず行動可能な助言に'),
])
CH('穴のM ― ナレーション／象徴',[
 ('正体','擬人化された“見過ごされた脆弱性”の声（特定人物でない）'),
 ('機能','テーマ提示と回収。説教にならず、問いかけで引く（演出詳細は決定稿C参照）'),
])
CH('攻撃者 ― 顔は出さない',[
 ('方針','人物として描かない。ログ・配信改ざん・攻撃者アイコンの“痕跡”のみ。動機/国籍は断定しない'),
])
CH('取引先（声の出演）― 鉄道/銀行/電力 保守会社・アナウンサー',[
 ('機能','被害連鎖を“電話の声”でリアルに。アナは「予防的停止」「勘定系に影響なし」など正確な言い回し'),
])
doc1=SimpleDocTemplate('/home/user/temporary/サイバークライシス_登場人物設定書.pdf',
    pagesize=A4,topMargin=16*mm,bottomMargin=16*mm,leftMargin=18*mm,rightMargin=16*mm,
    title='サイバークライシス 登場人物設定書')
doc1.build(st,onFirstPage=footer_maker('『サイバークライシス』登場人物設定書'),
              onLaterPages=footer_maker('『サイバークライシス』登場人物設定書'))
print('characters done')

# ============ 2) FINAL LOCKED + NARRATION ============
st=[]
st.append(Paragraph('『サイバークライシス』決定稿 進行台本（尺ロック 7:00）',title))
st.append(Paragraph('＋ナレーション「穴のM」演出指定／信頼経路版・作り込み稿準拠',subt))

st.append(Paragraph('A. 尺ロック表（本編 7:00 ＝ 420秒）',h1))
st.append(tbl(['シーン','IN–OUT','秒','カット','内容（要点）'],
 [['＃1 アバン','0:00–0:50','50','C1–C9','街の穴／“信頼の線”モンタージュ／タイトルイン'],
  ['＃2 油断','0:50–1:48','58','C10–C14','多田の進言、社長の否認'],
  ['＃3 二重の穴','1:48–2:40','52','C15–C21','カメラ初期設定＋付箋＋MFA不在'],
  ['＃4 潜伏','2:40–3:22','42','C22–C25','数週間前の侵入→更新配信の改ざん'],
  ['＃5 異変','3:22–4:25','63','C26–C31','電話一斉／取引先の声／断定しない'],
  ['＃6 予防的停止','4:25–5:18','53','C32–C36','鉄道・銀行・電力の“側”の停止'],
  ['＃7 葛藤','5:18–6:05','47','C37–C40','公表をめぐる対立→社長の決断'],
  ['＃8 封じ込め＋ラスト','6:05–7:00','55','C41–C48','JPCERT連絡／会見／夜の街（対の画）'],
  ['合計','0:00–7:00','420','','']],
 widths=[34*mm,24*mm,12*mm,22*mm,None]))

st.append(Paragraph('アバン内訳（＃1の詰め）',name))
st.append(tbl(['TC','秒','中身'],
 [['0:00–0:07','7','C1 街の穴・俯瞰'],
  ['0:07–0:12','5','C2 多田が避ける＋穴のM①'],
  ['0:12–0:18','6','C3 配信管理画面'],
  ['0:18–0:40','22','C4–C8 “信頼の線”モンタージュ（本作の画の顔）＋穴のM②'],
  ['0:40–0:50','10','C9 多田カメラ目線→タイトルイン']],
 widths=[26*mm,12*mm,None]))
st.append(Paragraph('伸縮代：超過時は＃6を3社→2社（−8〜10秒）、＃1モンタージュ−4秒。不足時は＃5に電話1社追加、＃8会見の質問+1。',small))

st.append(Paragraph('B. ナレーション「穴のM」演出指定',h1))
st.append(Paragraph('基本トーン',name))
for t in ['<b>声質</b>：低め・中性的。悪役にしない。静かで、すぐ隣にいる距離感',
          '<b>マイク</b>：オフ気味クローズ。微かに息。リバーブ薄め（床下を想起する程度）',
          '<b>テンポ</b>：遅め。句点でたっぷり間。煽らない',
          '<b>方向性</b>：脅し×／気づきへの誘い○。最後は問いかけで引く',
          '<b>NG</b>：説教口調、語尾を強く張る、過剰な笑い']:
    st.append(Paragraph('・'+t,body))
st.append(Paragraph('ライン別ディレクション（全7カ所）',name))
st.append(tbl(['#','TC','セリフ','演出'],
 [['①','0:08','目に見える穴なら――誰だって、避けて通る','当たり前を確認するように。軽く'],
  ['②','0:30','見えない穴は“信頼”を伝って、社会の下でつながっていく','「信頼」を少し置く。線の増殖に合わせ静かに高揚'],
  ['③','3:05','盗んだ鍵で静かに入り込んでいた。壊さず、ただ待っていた','ほぼ囁き。“待っていた”を冷たく。秒針SEと重ねる'],
  ['④','3:18','いつもの相手からの、いつもの更新。誰も疑わなかった','平熱で淡々と。皮肉を込めすぎない'],
  ['⑤','5:12','壊れたのではない。汚れの範囲が分からないから、止めるしかなかった','本作の主題。ゆっくり噛んで含める'],
  ['⑥','6:48','穴は一社の中だけにあるとは限らない。つながった先で深くなる','余韻。映像は夜の街'],
  ['⑦','6:56','その一歩を踏み外さないために――あなたに、できることは？','問いかけ。最後は上げず静かに引く→暗転']],
 widths=[8*mm,16*mm,None,52*mm]))
st.append(Paragraph('多田M（C47）「気づいて、声を上げて、つないだ」は穴のMと声色を変える（穴のM＝床下から／多田M＝胸の内から）。',small))

st.append(Paragraph('C. 音楽・音響の指針（尺連動）',h1))
for t in ['<b>M</b>：単一モチーフ（4音）を＃1提示→＃4不穏に変奏→＃8で解決（赦し）',
          '<b>無音の使いどころ</b>：＃3「MFAが無い」直後／＃7の長い沈黙。台詞の重みを音で消さない',
          '<b>SE設計の山</b>：＃5「電話一本→一斉」がサスペンスのピーク']:
    st.append(Paragraph('・'+t,body))

st.append(Paragraph('D. 放送前チェック（運用）',h1))
for t in ['冒頭・末尾に「フィクション」表示',
          '社名・窓口名・制度名の最終確認（技術監修＋法務監修）',
          '「予防的停止」表現の誤解防止（勘定系・信号・実停電を描いていないか）',
          '相談窓口（IPA／JPCERT/CC／警察#9110）の最新情報',
          '字幕・テロップの可読時間（特にアバンの情報量）']:
    st.append(Paragraph('☐ '+t,body))

doc2=SimpleDocTemplate('/home/user/temporary/サイバークライシス_決定稿_尺ロック_ナレーション演出.pdf',
    pagesize=A4,topMargin=16*mm,bottomMargin=16*mm,leftMargin=16*mm,rightMargin=15*mm,
    title='サイバークライシス 決定稿 尺ロック ナレーション演出')
doc2.build(st,onFirstPage=footer_maker('『サイバークライシス』決定稿（尺ロック＋ナレーション演出）'),
              onLaterPages=footer_maker('『サイバークライシス』決定稿（尺ロック＋ナレーション演出）'))
print('final done')
