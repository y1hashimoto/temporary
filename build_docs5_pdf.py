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
title=S('t',fontSize=16.5,leading=21,alignment=TA_CENTER,spaceAfter=2)
subt=S('s',fontSize=9.4,leading=13,alignment=TA_CENTER,textColor=GREY,spaceAfter=2)
name=S('nm',fontSize=12,leading=16,textColor=NAVY,spaceBefore=8,spaceAfter=2)
body=S('b'); h1=S('h',fontSize=14,leading=18,textColor=NAVY,spaceBefore=6,spaceAfter=4)
small=S('sm',fontSize=8.8,leading=12.5,textColor=GREY)
cell=S('c',fontSize=9,leading=12.5,spaceAfter=0); cellh=S('ch',fontSize=9.2,leading=12.5,textColor=colors.white,spaceAfter=0)

def footer_maker(label):
    def f(c,doc):
        c.saveState(); c.setFont('JP',8); c.setFillColor(GREY)
        c.drawCentredString(A4[0]/2,10*mm,'%d'%doc.page)
        c.drawString(15*mm,10*mm,label); c.restoreState()
    return f
def tbl(story,header,rows,widths,zebra=True):
    data=[[Paragraph(h,cellh) for h in header]]
    for r in rows: data.append([Paragraph(c,cell) for c in r])
    t=Table(data,colWidths=widths,repeatRows=1)
    ts=[('BACKGROUND',(0,0),(-1,0),NAVY),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#99a0b0')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]
    if zebra:
        for i in range(1,len(data)):
            if i%2==0: ts.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#f5f7fb')))
    t.setStyle(TableStyle(ts)); story.append(t); story.append(Spacer(1,8))

# ============ 1) CHARACTER BIBLE (rev5) ============
st=[]
st.append(Paragraph('『サイバークライシス』登場人物設定書（改訂版5 rev.1 準拠）',title))
st.append(Paragraph('社名・人物は架空。社会インフラ各社（鉄道/電力/銀行の声）は不採用。弁護士・取引先情シスを追加。',subt))
def CH(nm, items):
    st.append(Paragraph(nm,name))
    for k,v in items: st.append(Paragraph('<b>%s</b>：%s'%(k,v),body))
CH('多田 啓二／29歳 ― 主人公（総務部・セキュリティ担当）',[
 ('人物像','生真面目で観察眼。社内では“煙たがられる正論”担当だが芯がある'),
 ('役割','＃2で「専門家でなくてもできる“基本”」を進言→却下される。＃4で自社の不審ログインに気づき、取引先の一報後に経路を裏付け'),
 ('口調','丁寧でロジカル。「専門家になれとは言っていません。基本だけです」'),
 ('アーク','見過ごす側→見過ごさない側→正直に対応し信頼を残す側。冒頭は穴を避け、ラストは踏み外さずまたぐ'),
])
CH('木川 宗吾／65歳 ― 社長',[
 ('人物像','職人気質。ITは「コスト」。プライドが高く“下請けの矜持”が裏目に'),
 ('役割','＃2で基本対策を却下。＃3で添付を開く。＃5賠償通告で「素人にそこまで」と動揺→＃6で正直対応を決断'),
 ('注意','悪人でなく“よくある油断の象徴”。経営層が自分を重ねられるよう断罪しすぎない'),
])
CH('鈴木 工場長／50代 ― 現場責任者',[
 ('機能','現場のリアル（出荷・操業）を背負う。＃4で「うちがやられたのか？」と素朴な疑問を代弁'),
])
CH('津山 郁美／30代 ― 管理部社員',[
 ('機能','付箋PWを最初に指摘する“気づき”役。解説ブロックでは<b>司会（質問役）</b>を務める'),
])
CH('多田 由香／20代後半 ― 多田の妻（妊娠中）',[
 ('機能','多田の動機（守りたいもの）。サイバー被害の直接の犠牲にはしない。短く温かく'),
])
CH('メイユー自動車・情報システム担当 ― 取引先（被害者側）【新規】',[
 ('役割','＃4で「弊社が不正アクセス調査中。侵入の起点が御社経由の可能性が高い」と<b>一報を入れる</b>。冷静に協力要請'),
 ('機能','侵入経路は“取引先の調査で判明し、指摘される”という現実を担う。被害者でありながら理性的'),
])
CH('メイユー自動車・弁護士（代理人） ― 【新規】',[
 ('役割','＃5で損害賠償を<b>“協議・争点”として</b>提示。「“専門家であれ”とは申しません。基本を、警告がありながら怠ったかが争点」と説明'),
 ('機能','視聴者の「素人に酷では？」という反論を、作品内で正しく受け止める。<b>威圧的にせず、断定しない</b>'),
 ('注意','台詞は法務監修で確定。注意義務・責任範囲を言い過ぎない'),
])
CH('穴吹 衛 ― 解説講師',[
 ('機能','Q&A形式で解説進行。「専門家でなく“基本”を／賠償は自動ではない／相談先がある」を脅さず伝える'),
])
CH('穴のM ― ナレーション／象徴',[
 ('正体','擬人化された“見過ごされた脆弱性”の声。問いかけで引く'),
 ('rev5の核台詞','「自分の穴は、自分では気づきにくい。教えてくれたのは――つながった、相手だった」'),
])
CH('攻撃者 ― 顔は出さない',[
 ('方針','人物化しない。盗んだVPN認証情報で木川に潜伏→取引先へ。ログ・痕跡のみ。動機/国籍は断定しない'),
])
st.append(Paragraph('※旧版にいた「鉄道/電力/銀行 保守会社の声」は社会インフラ不採用に伴い削除。代わりに取引先メイユー（情シス・弁護士）を採用。',small))
doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_登場人物設定書_改訂版5準拠.pdf',
    pagesize=A4,topMargin=16*mm,bottomMargin=16*mm,leftMargin=18*mm,rightMargin=16*mm,
    title='登場人物設定書 改訂版5準拠')
doc.build(st,onFirstPage=footer_maker('登場人物設定書（改訂版5 rev.1 準拠）'),onLaterPages=footer_maker('登場人物設定書（改訂版5 rev.1 準拠）'))
print('chars5 done')

# ============ 2) TIMING-LOCK + NARRATION (rev5) ============
st=[]
st.append(Paragraph('『サイバークライシス』尺ロック表（7:00）＋ナレーション演出（改訂版5 rev.1）',title))
st.append(Paragraph('社会インフラ不採用／侵入経路は取引先の一報で判明／賠償は争点。本編ちょうど7:00。',subt))

st.append(Paragraph('A. 尺ロック表（本編 7:00 ＝ 420秒）',h1))
tbl(st,['シーン','IN–OUT','秒','内容（要点）'],
 [['＃1 アバン','0:00–0:45','45','街の穴／木川と取引先のVPN直結／タイトル'],
  ['＃2 油断（基本の提示）','0:45–1:45','60','多田が“基本”を進言→社長が却下'],
  ['＃3 侵入（二重の穴）','1:45–2:30','45','添付の有効化／カメラ初期設定・付箋・MFA無し'],
  ['＃4 異変と取引先からの一報','2:30–3:40','70','自社の不審ログイン→取引先が経路を指摘→共同調査で裏付け'],
  ['＃5 賠償は“争点”','3:40–4:55','75','弁護士同席の賠償協議（断定しない）＝クライマックス'],
  ['＃6 葛藤と判断','4:55–5:45','50','隠す誘惑→正直・報告を決断'],
  ['＃7 代償と教訓','5:45–6:25','40','長引く協議／コスト対比（月数万円 vs 復旧＋賠償）'],
  ['＃8 ラストと問いかけ','6:25–7:00','35','夜の街・穴をまたぐ／問いかけ'],
  ['合計','0:00–7:00','420','']],
 widths=[40*mm,24*mm,12*mm,None])
st.append(Paragraph('伸縮代：超過時は＃4の共同調査説明、＃7協議描写を圧縮。不足時は＃5の弁護士説明を一往復追加。',small))

st.append(Paragraph('B. ナレーション「穴のM」演出指定（rev5の台詞に対応）',h1))
st.append(Paragraph('基本トーン：低め・中性的／オフ気味クローズ／遅めで間をとる／脅さず、問いかけで引く（旧演出指定を踏襲）。',body))
tbl(st,['#','TC','セリフ','演出'],
 [['①','0:06','目に見える穴は、避けて通れる','当たり前を確認するように。軽く'],
  ['②','0:35','見えない穴も、特別な知識がなくても、ふさげる。“基本”さえ知っていれば','“基本”に軽くアクセント。希望を残す'],
  ['③','2:25','鍵は、とうに渡っていた。難しい鍵では、なかった','囁き。“難しい鍵では”を冷たく'],
  ['④','3:35','自分の穴は、自分では気づきにくい。教えてくれたのは――つながった、相手だった','本作の肝。しみじみと、相手＝取引先を示しつつ'],
  ['⑤','4:50','問われるのは、難しさではない。“知られていたのに、やらなかった”かどうか','静かに芯を置く。断罪調にしない'],
  ['⑥','6:35','穴は、難しい場所にあるとは限らない。いつもの“基本”を後回しにした足元にある','余韻。夜の街'],
  ['⑦','6:55','専門家でなくても、ふさげる。――あなたに、できることは？','問いかけ。上げず静かに引く→暗転']],
 widths=[8*mm,16*mm,None,46*mm])
st.append(Paragraph('多田M（＃8）「“基本”を、後回しにした。それだけで、信じてくれた人に迷惑をかけた」は、穴のMと声色を変える（多田＝胸の内）。',small))

st.append(Paragraph('C. 旧・尺ロック表からの主な変更',h1))
for t in ['社会インフラの「予防的停止」点描（駅・ATM・コールセンター）を<b>全削除</b>。',
          '＃4を「踏み台→取引先発症（自社で断定）」から<b>「取引先の一報で判明」</b>に変更し70秒に拡張。',
          '＃5を「記者会見」から<b>「賠償協議（弁護士同席）」</b>に変更＝クライマックス。',
          '合計7:00は維持。']:
    st.append(Paragraph('・'+t,body))
st.append(Paragraph('※賠償・注意義務の台詞は法務監修で確定。窓口/ガイドライン名は最新確認。',small))
doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_尺ロック_ナレーション_改訂版5準拠.pdf',
    pagesize=A4,topMargin=16*mm,bottomMargin=16*mm,leftMargin=16*mm,rightMargin=15*mm,
    title='尺ロック ナレーション 改訂版5準拠')
doc.build(st,onFirstPage=footer_maker('尺ロック＋ナレーション（改訂版5 rev.1 準拠）'),onLaterPages=footer_maker('尺ロック＋ナレーション（改訂版5 rev.1 準拠）'))
print('timing5 done')
