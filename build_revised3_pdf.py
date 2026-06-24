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
place=S('pl',fontSize=10.2,leading=14.5,textColor=NAVY,spaceBefore=3,spaceAfter=2)
act  =S('a',fontSize=10,leading=14.5,textColor=colors.HexColor('#2d2d2d'),spaceAfter=2,leftIndent=2)
line =S('l',fontSize=10.4,leading=15.8,leftIndent=12,spaceAfter=2)
note =S('n',fontSize=8.9,leading=12.8,textColor=GREY,spaceAfter=3)
h1   =S('h',fontSize=13.5,leading=17,textColor=NAVY,spaceBefore=7,spaceAfter=4)
li   =S('li',fontSize=10.2,leading=15,leftIndent=8,spaceAfter=4)
warn =S('w',fontSize=9.6,leading=14,textColor=colors.HexColor('#7a1f1f'))

story=[]
def bar(t):
    p=Paragraph(t,scn); tb=Table([[p]],colWidths=[None])
    tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),NAVY),('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(Spacer(1,7)); story.append(tb); story.append(Spacer(1,3))
def PL(t): story.append(Paragraph(t,place))
def A(t): story.append(Paragraph(t,act))
def L(sp,t): story.append(Paragraph('<b>%s</b>「%s」'%(sp,t),line))
def NB(t): story.append(Paragraph('※ '+t,note))
def LI(t): story.append(Paragraph(t,li))

story.append(Paragraph('『サイバークライシス ～あの時、私は…～』改訂版3（等身大版）',title))
story.append(Paragraph('中小企業“等身大”版・台詞付き／本編 約7分＋解説ブロック',subt))
story.append(Spacer(1,3))
story.append(Paragraph('※この物語はフィクションです。実在の企業・団体・人物とは一切関係ありません。',discl))
story.append(Spacer(1,4))
box=Paragraph('<b>本稿は「社会インフラ停止」系（初稿・改訂版2・撮影台本ドラフト）を撤回し置き換える決定方針版。</b>'
    '社会インフラは描かず、被害を「自社の操業停止＋取引先の一時停止（取り返せるが信頼と損害は重い）」に限定する。',warn)
tb=Table([[box]],colWidths=[None])
tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#fdecea')),('BOX',(0,0),(-1,-1),0.8,RED),
    ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
story.append(tb)

story.append(Paragraph('設計方針（同僚指摘の反映）',h1))
for t in [
 '<b>社会インフラ（鉄道・電力・銀行）は一切描かない</b>。重要インフラは多重化・フェイルセーフ・手動運用で設計され“一社の事故では社会サービスは止まりにくい”ため、煽らない。',
 '被害は<b>「自社の操業停止」＋「取引先（製造業）の一時停止」</b>に限定。後者は<b>“取り返せるが、信頼と損害は重い”</b>（小島プレス→トヨタの本質に忠実）。',
 '事故は<b>ランサムウェア型</b>。最大の教訓を<b>「バックアップで“戻せる”備え」</b>に置く。',
 'テーマ：恐怖でなく<b>等身大の現実を正しく</b>。「対策コスト ≪ 被害コスト」。',
]:
    LI('・'+t)

story.append(Paragraph('本編（約7分）',h1))

bar('＃1　アバン　0:00–0:45')
A('○街・雑踏。歩道の『穴』。多田啓二（29）が避けて通る。')
L('穴のM','目に見える穴は、避けて通れる')
A('○木川精機の日常（点描）：受発注端末、在庫データ、生産ラインの稼働モニタ、図面。すべてデジタル。')
L('穴のM','だが――止まって困るものほど、見えない穴の上に、乗っている')
A('○多田、振りかえる。タイトルイン。')

bar('＃2　油断　0:45–1:45')
A('○社長室。パター練習の木川宗吾（65）に、多田が進言。')
L('多田','社長。せめて“止まっても戻せる”備えだけでも。<b>オフラインのバックアップ</b>と、ログインの<b>多要素認証</b>。それと古い受発注サーバの更新を')
L('木川','うちは部品屋だ。そんな金、どこにある。今まで何もなかっただろう')
L('多田','“今まで”が続く保証は、ありません')
L('木川','来期だ、来期')
NB('確立：バックアップは半年前のものだけ／MFAなし／受発注サーバは旧式。')

bar('＃3　侵入（二重の穴）　1:45–2:35')
A('○請求書を装ったメール。「内容を表示するには〔コンテンツの有効化〕を」。')
L('多田','その添付、開かないでください。“有効化”は――')
L('木川','（かぶせて）取引先からだ。後にしろ')
A('○木川、面倒そうにクリック。画面が一瞬ちらつく。')
A('○廊下。清掃員「あのカメラ、勝手に動くのよ」。多田は<b>見過ごさず</b>管理画面を確認＝初期パスのまま、付箋ID、VPNにMFAなし。')
L('多田','（青ざめ）……鍵を、何本も外に置いてたようなものだ')
L('穴のM','鍵は、とうに渡っていた')

bar('＃4　発症　2:35–3:35')
A('○翌朝。受発注端末に身代金メッセージ。ファイルが暗号化。生産管理が止まる。')
L('多田','やられた……受発注も、生産管理も全部。バックアップは――（声を落とし）<b>半年前の</b>しか、ない')
L('鈴木','ラインは回せる。だが“何を、いくつ、どこへ出すか”が分からん。これじゃ<b>出荷できない</b>')
L('木川','金を払えば、戻るのか')
L('多田','払っても戻る保証はありません。それに――<b>“次”を呼びます</b>')

bar('＃5　取引先への影響（等身大）　3:35–4:35')
A('○取引先・メイユー自動車（架空）の資材担当から電話。')
L('メイユー資材','（電話OFF）木川さん、今日ぶんの部品が来ない。<b>うちのラインが止まる</b>。状況を、正確に教えてくれ')
A('○多田、隠さず。')
L('多田','不正アクセスを受け、出荷管理が止まっています。見込みが立ち次第ご連絡します。今分かっていることだけ、先に')
A('○受話器を置き、多田、ひとりごちる。')
L('多田M','一日ラインを止めても、向こうは取り返せる。……でも“<b>また止めるかもしれない会社</b>”だと思われたら、次の発注は、来ない')
NB('社会インフラには波及させない。被害は「取引先の一時停止（取り返せる）＋信頼・損害」。')

bar('＃6　葛藤と判断　4:35–5:25')
A('○社長室。')
L('木川','公表すれば、取引を切られる。……静かに、金で済ませられないのか')
L('多田','隠して払って、また同じことが起きたら、<b>今度こそ切られます</b>。今できるのは、正直に伝えて、警察と専門機関に相談すること。それが、信頼を残す道です')
A('○多田のスマホに、臨月の妻から（「無理しないでね」）。多田、ぐっと顔を上げる。')
L('木川','……（長い間）連絡しろ。<b>払わない。正直に話す</b>')

bar('＃7　復旧と代償　5:25–6:15')
A('○JPCERT/警察へ連絡、ログ保全。半年前バックアップ＋手作業で受発注を再構築。残業、混乱、費用。')
L('多田','（電話）JPCERTさんですか。木川精機です。ランサムウェアの被害で――はい、身代金は払いません。ログは保全しています')
A('○後日。メイユー資材が訪れる。')
L('メイユー資材','正直に来てくれたのは、大きい。……次も頼むかは、<b>これからの再発防止次第</b>だ')
A('○木川、疲れた顔で多田に。')
L('木川','お前が言ってた、あのバックアップ……いくらだった')
L('多田','月、数万円です')
A('木川「…………」（復旧費用は、その何百倍だった――の含み）')

bar('＃8　ラストと問いかけ　6:15–7:00')
A('○夜の街。多田、朝に避けたあの『穴』の前で立ち止まり、今度は避けず、踏み外さないようまたぐ。')
L('多田M','うちは、社会を止めたわけじゃない。でも、<b>自分たちを止めかけて、信じてくれた人に、迷惑をかけた</b>。……それは、十分に、重い')
L('穴のM','穴は、派手な大事件の顔をしていない。ある日――いつもの仕事を、静かに止める')
L('穴のM','その穴を塞いでおけるのは、今日の、あなただけだ。――<b>あなたに、できることは？</b>')
A('<b>～ 本編 おわり ～</b>')

story.append(Paragraph('解説ブロック',h1))
A('○会議室（後日）。VTRを見た社員と講師・穴吹衛。')
L('穴吹','怖がらせたいのではありません。等身大の現実を、正しく。6つだけ')
for t in [
 '<b>① バックアップ（3-2-1／オフライン）</b> ―ランサムから“戻せる”最重要の備え。「止まっても戻せる」かが運命を分ける（＃4）。',
 '<b>② 多要素認証（MFA）・パスワード管理</b> ―付箋PW・使い回しは厳禁、VPN・管理画面にMFA（＃3）。',
 '<b>③ 更新・EDR・添付の“有効化”</b> ―心当たりのない添付は開かない／有効化しない。初期設定の見直し（＃3）。',
 '<b>④ すぐ報告・相談／身代金は払わない</b> ―IPA／JPCERT/CC／警察#9110。払っても戻る保証はなく“次”を呼ぶ（＃4・＃7）。',
 '<b>⑤ サプライチェーン責任と“正直な初動”</b> ―自社の停止は取引先の操業に響く。隠さず分けて伝えることが信頼を守る（＃5・＃7）。',
]:
    LI(t)
# ⑥ correction highlighted
corr=Paragraph('<b>⑥【よくある誤解の訂正】</b>「中小企業の事故で、電車や銀行や電気まで止まる？」――実際の重要インフラは'
    '<b>多重化・フェイルセーフ・手動運用</b>で設計され、<b>一社の事故では社会サービスは止まりにくい</b>。'
    '<b>現実的で深刻なリスクは「自社の事業停止」と「取引先への損害・信頼の毀損」</b>。そこに集中を。',S('cw',fontSize=10,leading=14.5))
tb=Table([[corr]],colWidths=[None])
tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#eaf5ec')),('BOX',(0,0),(-1,-1),0.8,GREEN),
    ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
story.append(Spacer(1,2)); story.append(tb); story.append(Spacer(1,4))
L('穴吹','最後にひとつ。多田さんが断られた備えは、月に数万円。復旧にかかったのは、その何百倍でした。<b>対策コストは、被害コストより、ずっと安い</b>')
L('多田','（カメラ目線）――あなたの会社の“穴”、塞ぎませんか')
A('<b>～ おわり ～</b>')
NB('社名は架空。社会インフラは描かない。④の方針・窓口名は放送時点で技術＋法務監修を推奨。旧稿（社会インフラ停止系）は本稿で撤回。'
   '絵コンテ・設定書・尺ロック表は本稿の場面（＃5・＃6中心）に合わせ差し替えが必要。')

def footer(c,doc):
    c.saveState(); c.setFont('JP',8); c.setFillColor(GREY)
    c.drawCentredString(A4[0]/2,10*mm,'%d'%doc.page)
    c.drawString(16*mm,10*mm,'『サイバークライシス』改訂版3（等身大版）')
    c.restoreState()
doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_改訂版3_等身大版_台詞付き.pdf',
    pagesize=A4,topMargin=16*mm,bottomMargin=16*mm,leftMargin=17*mm,rightMargin=16*mm,
    title='サイバークライシス 改訂版3 等身大版')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('done')
