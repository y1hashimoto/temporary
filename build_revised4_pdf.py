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
NAVY=colors.HexColor('#2b3a55'); GREY=colors.HexColor('#555555'); RED=colors.HexColor('#c0392b'); GREEN=colors.HexColor('#1e7d34')

def S(n,**k):
    b=dict(fontName='JP',fontSize=10.4,leading=15.8,textColor=colors.HexColor('#111111'),alignment=TA_LEFT,spaceAfter=3)
    b.update(k); return ParagraphStyle(n,**b)
title=S('t',fontSize=17,leading=21,alignment=TA_CENTER,spaceAfter=2)
subt =S('s',fontSize=9.6,leading=13,alignment=TA_CENTER,textColor=GREY,spaceAfter=2)
discl=S('d',fontSize=8.8,leading=12.5,alignment=TA_CENTER,textColor=GREY)
scn  =S('sc',fontSize=11,leading=15,textColor=colors.white)
act  =S('a',fontSize=10,leading=14.5,textColor=colors.HexColor('#2d2d2d'),spaceAfter=2,leftIndent=2)
line =S('l',fontSize=10.4,leading=15.8,leftIndent=12,spaceAfter=2)
note =S('n',fontSize=8.9,leading=12.8,textColor=GREY,spaceAfter=3)
h1   =S('h',fontSize=13.5,leading=17,textColor=NAVY,spaceBefore=7,spaceAfter=4)
li   =S('li',fontSize=10.2,leading=15,leftIndent=8,spaceAfter=4)

story=[]
def bar(t):
    p=Paragraph(t,scn); tb=Table([[p]],colWidths=[None])
    tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),NAVY),('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(Spacer(1,7)); story.append(tb); story.append(Spacer(1,3))
def A(t): story.append(Paragraph(t,act))
def L(sp,t): story.append(Paragraph('<b>%s</b>「%s」'%(sp,t),line))
def NB(t): story.append(Paragraph('※ '+t,note))
def LI(t): story.append(Paragraph(t,li))
def cbox(p,bg,bc):
    tb=Table([[p]],colWidths=[None])
    tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),bg),('BOX',(0,0),(-1,-1),0.8,bc),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(Spacer(1,2)); story.append(tb); story.append(Spacer(1,4))

story.append(Paragraph('『サイバークライシス ～あの時、私は…～』改訂版4（損害賠償版）',title))
story.append(Paragraph('中小企業“等身大”版／中心リスク＝取引先への損害賠償／本編 約7分＋解説',subt))
story.append(Spacer(1,3))
story.append(Paragraph('※この物語はフィクションです。実在の企業・団体・人物とは一切関係ありません。',discl))
story.append(Spacer(1,3))
cbox(Paragraph('<b>本稿は改訂版3を発展させ、中小企業の中心リスクを「損害賠償（取引先への加害責任）」に置いた決定方針版。</b>'
    '社会インフラ停止は描かない（撤回済み）。劇中の社名・金額は架空。',S('w',fontSize=9.6,leading=14,textColor=colors.HexColor('#7a1f1f'))),
    colors.HexColor('#fdecea'),RED)

story.append(Paragraph('設計方針',h1))
for t in [
 '中小企業の最大リスクを<b>損害賠償（取引先への加害責任）</b>に設定。社会インフラ被害の代わりに据える。',
 '構図：<b>木川精機の弱いセキュリティが侵入口（踏み台）になり、取引先（大手）が大きな被害</b>→木川精機が<b>多額の損害賠償請求</b>を受け存亡の危機。',
 '現実の足場：給食委託先経由で病院が被害を受けた<b>大阪急性期・総合医療センター事例（2022）</b>型。',
 'テーマ：恐怖でなく等身大。<b>対策コスト ≪（賠償＋復旧）コスト</b>。',
]:
    LI('・'+t)

story.append(Paragraph('本編（約7分）',h1))
bar('＃1　アバン　0:00–0:45')
A('○街・雑踏。歩道の『穴』。多田啓二（29）が避けて通る。')
L('穴のM','目に見える穴は、避けて通れる')
A('○木川精機の点描：受発注端末、在庫、生産ライン、そして<b>取引先とつながる専用線／VPNの画面</b>。')
L('穴のM','だが――その穴は、あなたの会社から、“つながった相手”へと続いている')
A('○多田、振りかえる。タイトルイン。')

bar('＃2　油断　0:45–1:40')
A('○社長室。パター練習の木川宗吾（65）に、多田が進言。')
L('多田','社長。せめて取引先とつなぐVPNに<b>多要素認証</b>を。それと<b>バックアップ</b>と<b>EDR</b>。うちは大手さんと直結しています。<b>うちが破られたら、向こうまで通じてしまう</b>')
L('木川','うちは部品屋だぞ。狙うヤツがいるか')
L('多田','“うち”が目的じゃないんです。<b>大手に入るための、入口</b>にされる')
L('木川','考えすぎだ。来期に検討する')

bar('＃3　侵入（二重の穴）　1:40–2:30')
A('○請求書を装うメール、「コンテンツの有効化」。多田が制止するも踏まれる。')
A('○多田、廊下のカメラ異常を<b>見過ごさず</b>確認＝初期パスのまま、付箋ID、VPNにMFAなし。')
L('多田','（青ざめ）VPNの鍵が、外に置きっぱなしだ……')
A('○攻撃者は盗んだ認証情報で<b>木川のVPNに侵入し、潜伏</b>。')
L('穴のM','鍵は、とうに渡っていた。狙いは――この会社の、先にある')

bar('＃4　踏み台、そして取引先の発症　2:30–3:35')
A('○数週間後。攻撃者は木川の<b>信頼された接続</b>を使い、取引先・メイユー自動車（架空）へ侵入。メイューの基幹が暗号化され<b>操業が長期停止</b>。')
A('○木川精機にも影響。多田、ログを追い顔色を失う。')
L('多田','……うちが、入口だ。<b>うちのVPN経由で、メイユーさんに入られてる</b>')
L('鈴木','向こうのラインは、いつ戻る')
L('多田','分かりません。基幹がやられたら、<b>数週間――下手をすれば、もっと</b>')

bar('＃5　賠償通告（クライマックス）　3:35–4:45')
A('○木川精機にメイユー自動車から正式な連絡。会議室、重い空気。')
L('メイユー（法務）','（OFF/来訪）弊社の操業停止と復旧、逸失利益。被害は甚大です。<b>侵入経路が御社であったことを踏まえ、損害賠償を含めて協議させていただく</b>')
A('○木川、言葉を失う。多田がメモの数字を見て、声を落とす。')
L('多田','社長……この規模だと、<b>うちの売上の、何年分</b>です')
L('木川','……っ。う、うちは、被害者じゃないのか')
L('多田','被害者です。でも――<b>“備えを怠った入口”だった、と問われています</b>')
L('穴のM','穴の代償は、自分の痛みだけでは、終わらない')

bar('＃6　葛藤と判断　4:45–5:35')
A('○社長室。')
L('木川','もう、終わりだ……隠せなかったのか。せめて、穏便に')
L('多田','隠せば、<b>もっと重くなります</b>。今やるべきは、警察と専門機関に届け、正直に、誠実に対応すること。<b>事実を保全し協力する姿勢が、賠償の協議でも効いてきます</b>')
A('○多田のスマホに、臨月の妻から（「無理しないで」）。多田、顔を上げる。')
L('木川','……（長い間）連絡しろ。逃げない。<b>正直に、頭を下げに行く</b>')

bar('＃7　代償と教訓　5:35–6:25')
A('○JPCERT/警察へ連絡、ログ保全、メイユーへ全面協力。弁護士、サイバー保険の確認。長い協議。')
L('メイユー（法務）','正直に動いていただいた点は、考慮します。……ただ、<b>御社の責任が消えるわけではありません</b>')
A('○後日。木川、疲れ切った顔で多田に。')
L('木川','お前が言ってた、あのMFAとバックアップ……いくらだった')
L('多田','月、数万円です')
A('木川「…………」（賠償と復旧は、その<b>何千倍</b>――の含み）')

bar('＃8　ラストと問いかけ　6:25–7:00')
A('○夜の街。多田、朝に避けた『穴』の前で立ち止まり、今度は避けず、踏み外さないようまたぐ。')
L('多田M','うちは、社会を止めたわけじゃない。でも、<b>信じて、つないでくれた相手に、損害を与えた</b>。その責任は――会社ごと、背負うことになる')
L('穴のM','穴は、あなたの会社の中だけの問題じゃない。<b>つながった相手の損害を、あなたが負う</b>こともある')
L('穴のM','その穴を塞いでおけるのは、今日の、あなただけだ。――<b>あなたに、できることは？</b>')
A('<b>～ 本編 おわり ～</b>')

story.append(Paragraph('解説ブロック',h1))
A('○会議室（後日）。VTRを見た社員と講師・穴吹衛。')
L('穴吹','中小企業にとって一番現実的で重いリスク。それは“自社が止まる”ことだけではありません。<b>取引先に損害を与え、その賠償を問われる</b>ことです')
LI('<b>① “踏み台”は加害になりうる</b> ―自社の備え不足が侵入口になると、取引先の被害＝<b>損害賠償責任</b>を負うことがある。')
cbox(Paragraph('<b>実例（要旨）</b>：2022年、ある総合医療センターが<b>給食委託事業者経由</b>で侵入され、電子カルテ暗号化で外来・手術を停止、'
    '通常復旧まで約2か月、被害は数十億円規模と報道。<b>委託先の責任・損害賠償が問題化</b>。'
    '<font color="#7a1f1f">※金額・和解等の詳細は法務監修で要確認。劇中は架空の規模に留める。</font>',S('ex',fontSize=9.6,leading=14)),
    colors.HexColor('#eef3f8'),NAVY)
for t in [
 '<b>② “戻せる／入られない”備え</b> ―オフラインのバックアップ（3-2-1）、MFA、EDR、更新、添付の“有効化”注意。取引先接続は分離・最小権限。',
 '<b>③ 誠実な初動</b> ―すぐ報告・相談（IPA／JPCERT/CC／警察#9110）、身代金は払わない、事実保全と協力。信頼維持に加え<b>賠償協議でも有利</b>。',
 '<b>④ 契約とお金の備え</b> ―取引契約のセキュリティ要件・責任範囲の確認。<b>サイバー保険</b>の検討。',
]:
    LI(t)
cbox(Paragraph('<b>⑤【誤解の訂正】</b>「中小の事故で電車や銀行や電気が止まる？」 重要インフラは<b>多重化・フェイルセーフ設計</b>で'
    '<b>一社の事故では社会サービスは止まりにくい</b>。現実的に深刻なのは<b>自社の停止と、取引先への損害・賠償</b>。',S('c5',fontSize=9.8,leading=14)),
    colors.HexColor('#eaf5ec'),GREEN)
LI('<b>⑥ コストの現実</b> ―断られた備えは月<b>数万円</b>。事故後は復旧費に<b>損害賠償</b>まで上乗せ。<b>対策は、はるかに安い保険</b>。')
L('穴吹','怖がらせたいのではありません。起きうる現実を、正しく。今日できることから')
L('多田','（カメラ目線）――あなたの会社の“穴”、塞ぎませんか')
A('<b>～ おわり ～</b>')
NB('社名・金額は架空。社会インフラは描かない。実例の事実関係・損害賠償／和解の有無や金額は放送前に法務監修で必ず確認。'
   '旧稿（社会インフラ停止系）は撤回。絵コンテ・設定書・尺ロック表は本稿（＃4・＃5中心）に合わせ差し替えが必要。')

def footer(c,doc):
    c.saveState(); c.setFont('JP',8); c.setFillColor(GREY)
    c.drawCentredString(A4[0]/2,10*mm,'%d'%doc.page)
    c.drawString(16*mm,10*mm,'『サイバークライシス』改訂版4（損害賠償版）')
    c.restoreState()
doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_改訂版4_損害賠償版_台詞付き.pdf',
    pagesize=A4,topMargin=16*mm,bottomMargin=16*mm,leftMargin=17*mm,rightMargin=16*mm,
    title='サイバークライシス 改訂版4 損害賠償版')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('done')
