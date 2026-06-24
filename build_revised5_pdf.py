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
title=S('t',fontSize=16.5,leading=20.5,alignment=TA_CENTER,spaceAfter=2)
subt =S('s',fontSize=9.4,leading=13,alignment=TA_CENTER,textColor=GREY,spaceAfter=2)
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

story.append(Paragraph('『サイバークライシス ～あの時、私は…～』改訂版5（責任を正しく描く版）',title))
story.append(Paragraph('“専門家レベルは求めない／賠償は断定しない”／本編 約7分＋解説',subt))
story.append(Spacer(1,3))
story.append(Paragraph('※この物語はフィクションです。実在の企業・団体・人物とは一切関係ありません。',discl))
story.append(Spacer(1,3))
cbox(Paragraph('<b>本稿は改訂版4を、「中小企業に専門家レベルを求めない／損害賠償を断定しない」よう正した版。</b>'
    '視聴者の「素人に無理」「賠償が本当に起きるのか」という反論を、作品内（＃2・＃5）と解説で正面から受け止める。',S('w',fontSize=9.6,leading=14,textColor=colors.HexColor('#7a1f1f'))),
    colors.HexColor('#fdecea'),RED)

story.append(Paragraph('設計方針（“無責任”と退けられないために）',h1))
for t in [
 '責任の所在を<b>「専門知識の欠如」ではなく「警告された“基本”の放置」</b>に固定する。',
 '損害賠償は<b>“確定”でなく“争点・リスク”</b>として描く（弁護士が「専門家であることは求められない／問われるのは基本を怠ったか」と明言）。',
 '<b>確実なコスト（自社復旧・取引停止・信用毀損）</b>と<b>状況次第の賠償リスク</b>を分けて提示。断定しない。',
 '求める対策は<b>「誰でもできる・安い・相談先がある」基本</b>に限定。「専門家になれ」とは言わない。',
]:
    LI('・'+t)

story.append(Paragraph('本編（約7分）',h1))
bar('＃1　アバン　0:00–0:45')
A('○街・雑踏。歩道の『穴』。多田啓二（29）が避けて通る。')
L('穴のM','目に見える穴は、避けて通れる')
A('○木川精機の点描：受発注端末、在庫、生産ライン、取引先とつながるVPN画面。')
L('穴のM','見えない穴も――特別な知識がなくても、ふさげる。“基本”さえ、知っていれば')
A('○多田、振りかえる。タイトルイン。')

bar('＃2　油断（“基本”の提示）　0:45–1:45')
A('○社長室。パター練習の木川宗吾（65）に、多田が進言。')
L('多田','社長。これは専門的な、難しい話じゃないんです。<b>IPA――国の機関も中小企業向けに勧めている“基本のキ”</b>です。パスワードの使い回しをやめる、ログインに<b>多要素認証</b>、<b>こまめな更新</b>、それと<b>バックアップ</b>')
L('木川','うちみたいな素人に、そんなのできるか')
L('多田','<b>“専門家になってくれ”とは言っていません</b>。基本だけです。月、数万円。<b>相談できる先</b>もあります。……やらずに何かあれば、“知らなかった”では済まないかもしれない')
L('木川','考えすぎだ。来期に検討する')
NB('警告された“基本”（MFA・更新・バックアップ・PW管理）を社長が放置＝後の争点。')

bar('＃3　侵入（二重の穴）　1:45–2:30')
A('○請求書を装うメール「コンテンツの有効化」。多田が制止するも踏まれる。')
A('○多田、廊下のカメラ異常を<b>見過ごさず</b>確認＝初期パスのまま、付箋ID、VPNにMFAなし。')
L('多田','（青ざめ）……全部、この前“やりましょう”と言った、基本のところだ')
A('○攻撃者は盗んだ認証情報で<b>木川のVPNに侵入し、潜伏</b>。')
L('穴のM','鍵は、とうに渡っていた。難しい鍵では、なかった')

bar('＃4　踏み台、そして取引先の発症　2:30–3:25')
A('○数週間後。攻撃者は木川の<b>信頼された接続</b>を使い、取引先・メイユー自動車（架空）へ侵入。基幹が暗号化され<b>操業が長期停止</b>。')
A('○多田、ログを追い顔色を失う。')
L('多田','……うちが、入口だ。<b>うちのVPN経由で、メイユーさんに入られてる</b>')
L('鈴木','向こうのラインは、いつ戻る')
L('多田','分かりません。基幹がやられたら、長引きます')

bar('＃5　賠償は“争点”（クライマックス）　3:25–4:40')
A('○木川精機にメイユー自動車から連絡。会議室。先方の担当者と<b>弁護士</b>が同席。')
L('メイユー（法務）','弊社の損害は甚大です。侵入経路が御社であった以上、<b>損害賠償を含めて協議させていただく</b>ことになります')
L('木川','（気色ばみ）うちは素人だぞ！ <b>専門家でもないのに、そこまで責任を負えと</b>？')
A('○弁護士、静かに。')
L('弁護士','<b>“専門家であれ”とは、誰も申しません</b>。問われるのは――<b>多要素認証や更新といった、広く知られた“基本”を、警告がありながら取っていたか</b>。そこが争点です')
A('○多田、目を伏せる。木川、言葉を失う。')
L('多田','（小声）……“やりましょう”と、言ったのに')
L('穴のM','問われるのは、難しさではない。“知られていたのに、やらなかった”かどうか')
NB('賠償は確定でなく“協議・争点”として描く。金額は出さない／ぼかす。')

bar('＃6　葛藤と判断　4:40–5:30')
A('○社長室。')
L('木川','……隠せば、穏便に済んだか')
L('多田','いいえ。隠せば<b>もっと重くなります</b>。今やるべきは、警察と専門機関に届け、正直に協力すること。<b>事実を保全し協力する姿勢は、これからの協議でも必ず効いてきます</b>')
A('○多田のスマホに、臨月の妻から（「無理しないで」）。多田、顔を上げる。')
L('木川','……（長い間）連絡しろ。逃げない。<b>正直に、頭を下げに行く</b>')

bar('＃7　代償と教訓　5:30–6:20')
A('○JPCERT/警察へ連絡、ログ保全、メイユーへ全面協力。弁護士、<b>サイバー保険</b>の確認。協議は長引き、<b>結末はまだ見えない</b>。')
A('○後日。木川、疲れた顔で多田に。')
L('木川','お前が言ってた、あの基本……いくらだった')
L('多田','月、数万円です。……それと、相談先は、無料のところもありました')
A('木川「…………」（失ったものとの差を噛みしめる）')

bar('＃8　ラストと問いかけ　6:20–7:00')
A('○夜の街。多田、朝に避けた『穴』の前で立ち止まり、今度は避けず、踏み外さないようまたぐ。')
L('多田M','うちは、社会を止めたわけじゃない。難しいことを間違えたわけでもない。……ただ、<b>“基本”を、後回しにした</b>。それだけで、信じてくれた人に迷惑をかけた')
L('穴のM','穴は、難しい場所にあるとは限らない。いつもの“基本”を後回しにした足元にある')
L('穴のM','専門家でなくても、ふさげる。――<b>あなたに、できることは？</b>')
A('<b>～ 本編 おわり ～</b>')

story.append(Paragraph('解説ブロック',h1))
A('○会議室（後日）。VTRを見た社員と講師・穴吹衛。')
L('穴吹','まず、はっきりさせます。<b>中小企業に“専門家レベル”は求められていません</b>。求められるのは、誰でもできる“基本”です')
LI('<b>① 求められるのは“専門家”でなく“基本”</b> ―PW使い回し回避、多要素認証、更新、バックアップ。<b>IPAの中小企業向けガイドライン／SECURITY ACTION</b>など無料の手引きと相談窓口がある。専門知識がなくても始められる。')
cbox(Paragraph('<b>②【賠償は“自動”ではない】</b> 損害賠償は<b>過失（注意義務違反）や契約違反</b>があって初めて問われ、因果関係・予見可能性・過失相殺・契約上の責任制限なども絡む<b>争点</b>。'
    '「中小だから必ず多額賠償」ではない。<b>ただし“広く知られた基本”を警告がありながら怠った場合は、責任を問われるリスクが現実に</b>。'
    '<font color="#7a1f1f">※具体的判断は法務監修・専門家相談を。</font>',S('c2',fontSize=9.8,leading=14)),
    colors.HexColor('#eef3f8'),NAVY)
for t in [
 '<b>③ 確実なコストと追加リスクを分ける</b> ―ほぼ確実なのは自社の復旧費・操業停止・信用毀損。<b>損害賠償は状況次第の“追加リスク”</b>。煽らず、この切り分けで備える。',
 '<b>④ 誠実な初動</b> ―すぐ報告・相談（IPA／JPCERT/CC／警察#9110）、身代金は払わない、事実保全と協力。信頼維持に加え、万一の協議でも有利。',
 '<b>⑤ 契約とお金の備え</b> ―取引契約のセキュリティ要件・責任範囲の確認、サイバー保険の検討。',
]:
    LI(t)
cbox(Paragraph('<b>⑥【誤解の訂正】</b>「中小の事故で電車や銀行や電気が止まる？」 重要インフラは多重化・フェイルセーフ設計で'
    '<b>一社の事故では社会サービスは止まりにくい</b>。現実的に深刻なのは<b>自社の停止と、取引先への損害</b>。',S('c6',fontSize=9.8,leading=14)),
    colors.HexColor('#eaf5ec'),GREEN)
LI('<b>⑦ コストの現実</b> ―“基本”は月<b>数万円</b>＋無料の相談先。後悔の代償はその何倍にも。対策はいちばん安い保険。')
L('穴吹','“専門家になってください”ではありません。“基本”を、今日から。難しければ、相談していい先がある。それで足元の穴はふさげます')
L('多田','（カメラ目線）――あなたの会社の“穴”、塞ぎませんか')
A('<b>～ おわり ～</b>')
NB('肝は「専門性の欠如を責めない／賠償を断定しない」。賠償・実例の事実関係・注意義務の水準・責任範囲の表現は放送前に法務監修で必ず確認。'
   '金額は出さない／架空。窓口・ガイドライン名は最新確認。社会インフラは描かない。旧稿は撤回。')

def footer(c,doc):
    c.saveState(); c.setFont('JP',8); c.setFillColor(GREY)
    c.drawCentredString(A4[0]/2,10*mm,'%d'%doc.page)
    c.drawString(16*mm,10*mm,'『サイバークライシス』改訂版5（責任を正しく描く版）')
    c.restoreState()
doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_改訂版5_責任を正しく描く版_台詞付き.pdf',
    pagesize=A4,topMargin=16*mm,bottomMargin=16*mm,leftMargin=17*mm,rightMargin=16*mm,
    title='サイバークライシス 改訂版5 責任を正しく描く版')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('done')
