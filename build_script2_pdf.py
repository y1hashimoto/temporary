# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('JP', '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf'))
NAVY=colors.HexColor('#2b3a55'); GREY=colors.HexColor('#555555'); TEAL=colors.HexColor('#0e6b6b')

def S(n,**k):
    b=dict(fontName='JP',fontSize=10.5,leading=16,textColor=colors.HexColor('#111111'),alignment=TA_LEFT,spaceAfter=3)
    b.update(k); return ParagraphStyle(n,**b)

title=S('t',fontSize=18,leading=23,alignment=TA_CENTER,spaceAfter=2)
subt =S('s',fontSize=10,leading=14,alignment=TA_CENTER,textColor=GREY,spaceAfter=2)
discl=S('d',fontSize=9,leading=13,alignment=TA_CENTER,textColor=GREY)
beat =S('b',fontSize=11,leading=15,textColor=colors.white)
sub  =S('su',fontSize=10.5,leading=15,textColor=NAVY,spaceBefore=5,spaceAfter=2)
act  =S('a',fontSize=10,leading=15,textColor=colors.HexColor('#333333'),spaceAfter=3)
line =S('l',fontSize=10.5,leading=16,leftIndent=10,spaceAfter=2)
note =S('n',fontSize=9,leading=13,textColor=GREY,spaceAfter=3)
h1   =S('h',fontSize=14,leading=18,textColor=NAVY,spaceBefore=8,spaceAfter=4)
pt   =S('p',fontSize=10.5,leading=15.5,leftIndent=6,spaceAfter=4)

story=[]
def bar(txt,color=NAVY):
    p=Paragraph(txt,beat); t=Table([[p]],colWidths=[None])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),color),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(Spacer(1,7)); story.append(t); story.append(Spacer(1,3))
def L(sp,tx): story.append(Paragraph('<b>%s</b>「%s」'%(sp,tx),line))
def A(tx): story.append(Paragraph(tx,act))
def NB(tx): story.append(Paragraph('※ %s'%tx,note))
def SU(tx): story.append(Paragraph(tx,sub))

story.append(Paragraph('『サイバークライシス ～あの時、私は…～』',title))
story.append(Paragraph('改訂版2（信頼経路版・台詞付き骨子）　／　約7分＋解説ブロック',subt))
story.append(Spacer(1,3))
story.append(Paragraph('※この物語はフィクションです。実在の企業・団体・人物とは一切関係ありません。',discl))
story.append(Paragraph('※「穴」＝見過ごされた脆弱性。社会インフラは「予防的停止・手動切替」に限定して描く。',discl))

story.append(Paragraph('設定（現実性を担保するための前提）',h1))
for t in [
 '<b>木川精機</b>：自動車部品に加え、制御盤部品・保守部材を各種事業者に納める中小サプライヤ。',
 '取引先（鉄道・電力・銀行などの“設備保守を担う協力会社”や同業製造業）向けに、保守部材・図面・納期・請求を確認し、<b>保守ツールや帳票テンプレの「更新ファイル」を配布する</b>ポータル <b>「KIGAWA-Link」</b> を運用。',
 '木川精機は社会インフラを直接制御しない。<b>“保守・部材・データ連携のハブ”</b>。インフラへの影響は<b>協力会社を1〜2段経由した二次波及</b>として描く。',
 '感染は「閲覧」では起きない。<b>更新ファイルをダウンロードして“適用／実行”したとき</b>に起きる（前作「コンテンツの有効化」と一貫）。',
]:
    story.append(Paragraph('・ '+t,pt))

story.append(Paragraph('7分尺・本編',h1))

bar('0:00–0:45　導入：見える穴と、見えない穴')
A('○街・雑踏。歩道の『穴』を人々が避けて通る。')
L('穴のM','目に見える穴なら、誰だって避ける')
A('○点描：監視カメラ映像、VPNログイン画面、KIGAWA-Link、保守部材の納入予定表→線がのびて鉄道の保守倉庫・電力の保守受付・銀行の設備管理窓口へ。')
L('穴のM','だが、見えない穴は――“信頼”を伝って、社会の下でつながっていく')

bar('0:45–1:45　木川精機：中小の油断')
A('○社長室。パター練習の木川宗吾（65）に多田が進言。')
L('多田','KIGAWA-Linkは、うちだけのシステムじゃありません。取引先も保守会社も、ここから<b>更新ファイルを取り込んでいる</b>。万一のとき、止める手順を決めておかないと危険です')
L('木川','うちは部品屋だぞ。電力や鉄道を動かしてるわけじゃない')
L('多田','直接は動かしていません。でも“信頼されている”。そこが穴になります')
L('木川','大げさだ')

bar('1:45–2:30　侵入の伏線（二重の穴）')
A('○廊下。清掃員が防犯カメラの異常を指摘。多田は<b>見過ごさず</b>管理画面を確認。')
L('多田','カメラが初期設定のままだ。ホワイトボードの管理画面や、VPNのメモまで映ってる。外から見られた可能性があります')
A('○津山が付箋のID/パスワードを指摘。')
L('多田','しかもVPNに<b>多要素認証が掛かっていない</b>。IDとパスワードだけで入られる')
A('木川は予算と納期を理由に後回し。')
L('穴のM','穴は、ひとつではなかった')

bar('2:30–3:30　足場化（派手な描写はしない）')
A('○夜・サーバ室。テロップ「数週間前から、不審なログインが続いていた」。攻撃者は盗んだ認証情報でVPNに侵入し<b>潜伏</b>。深夜の通信、管理者権限の利用だけを淡々と。')
A('○翌週。KIGAWA-Linkが悪用され、各社へ<b>更新通知</b>が配信。画面「保守ツールを更新しました／図面ビューアの更新があります」')
L('穴のM','いつもの木川精機からの、いつもの更新。誰も疑わなかった')

bar('3:30–4:30　異変')
A('○木川精機。共有ファイルが開けない。取引先から電話が相次ぐ。')
L('鉄道系保守会社','木川さんの<b>更新を適用した端末</b>が動かない。保守倉庫の在庫端末にも出てる')
L('銀行系設備管理会社','うちの設備保守端末を一部止めた。念のためだ')
L('電力系保守会社','停電対応の<b>作業指示システム</b>を切り離した。復旧手配が遅れるかもしれん')
L('木川','なんで、うちからそんなところまで……')
L('多田','KIGAWA-Linkです。うちが<b>信頼された配布元</b>として悪用されている。……ただ<b>断定はできません</b>。どこまで汚染されたか、まだ切り分けられない')

bar('4:30–5:30　社会インフラ“側”の予防的停止')
A('○ニュース速報。')
L('アナウンサー','複数企業でシステム障害。鉄道会社の一部は<b>保守・駅務系の一部を予防的に停止</b>し安全確認中。運行は本数を減らして継続')
A('○駅。自動改札の一部閉鎖、駅員が手動案内。')
L('アナウンサー','一部の銀行は<b>設備保守の都合で一部ATMを休止</b>。勘定系には影響していないとしています')
A('○ATMに「メンテナンス中」の貼り紙。')
L('アナウンサー','電力会社は<b>停電対応の受付と保守手配の一部を手動運用に切替</b>')
A('○コールセンター。紙と電話で対応。')
L('穴のM','壊れたのではない。“どこまで汚れたか分からない”から、止めるしかなかった')
NB('信号機・実停電・勘定系・本人確認系は描かない。')

bar('5:30–6:15　社長の葛藤')
L('木川','公表したら終わりだ。うちが止めたなんて知られたら……')
L('多田','隠せば、もっと止まります。今は<b>分かっていることを出す</b>しかありません')
L('木川','うちは被害者だぞ')
L('多田','はい。でも<b>踏み台にもされています</b>。両方なんです')
A('木川、沈黙――やがて。')
L('木川','警察と専門機関、取引先に連絡しろ。KIGAWA-Linkは止める')
L('鈴木','止めたら出荷も止まります')
L('木川','止める。<b>安全が確認できないものは使わない</b>')

bar('6:15–7:00　封じ込めと教訓')
A('○会議室。ホワイトボード「KIGAWA-Link停止／影響範囲確認／取引先へ“更新を適用しないで”連絡／代替手段／復旧優先順位」。')
A('○外部専門家・警察と連携。多田が電話。')
L('多田','（電話）JPCERTです。当社のポータルが配布元として悪用され、更新ファイルに不正コードが――はい、ログは保全しています')
A('○取引先向け説明。木川が頭を下げる。')
L('木川','当社のサーバーが不正に利用された可能性があります。警察と外部専門家で調査中です。安全が確認できるまで、KIGAWA-Linkを停止します')
A('○厳しい声「いつ復旧する」「なぜ早く知らせなかった」。')
L('木川','分かっていること、分かっていないことを分けて、必ずお伝えします')
L('穴のM','穴は、一社の中だけにあるとは限らない。<b>つながった先で、さらに深くなる</b>')
L('穴のM','その一歩を踏み外さないために――<b>あなたに、できることは？</b>')
SU('◆ 最も自然な一文（多田）')
L('多田','社長、うちが電車や銀行を止めたわけじゃない。でも、<b>うちが配った“更新ファイル”を各社が信頼して取り込んだ</b>。だから、どこまで汚れたか分かるまで、各社は止めるしかないんです')
A('<b>～ 本編 おわり ～</b>')

story.append(Paragraph('解説ブロック',h1))
A('○会議室（後日）。VTRを見終えた社員と講師・穴吹衛。')
L('穴吹','“つながっているからこそ”の事故でした。5つで整理します')
for t in [
 '<b>① 入口：更新ファイル／添付の“適用・実行”</b> ―「閲覧」では感染しない。ダウンロードして実行・適用する瞬間が分かれ目。配布元が信頼できても署名・ハッシュ・配信元の確認を。',
 '<b>② 認証：多要素認証（MFA）</b> ―VPNや管理ポータルにMFAを。付箋パスワードは論外、使い回しもやめる。',
 '<b>③ 機器設定：監視カメラ等の初期設定</b> ―初期ID/パスワードの変更、外部公開の遮断。“見られている”前提で機密を映さない。',
 '<b>④ 検知と備え：EDR・更新・ログ</b> ―深夜の不審通信・管理者権限の異常を検知。ログ保全が調査と封じ込めを早める。',
 '<b>⑤ サプライチェーン／信頼経路の責任</b> ―自社が“信頼された配布元”になっている自覚を。インシデント時はすぐ報告・相談（IPA／JPCERT/CC／警察#9110）。隠さず「分かること・分からないこと」を分けて伝える。',
]:
    story.append(Paragraph('　'+t,pt))
L('穴吹','“うちは下請けだから狙われない”は、もう通用しません。<b>つながっているから、あなたの対策が全体を守る</b>')
L('多田','（カメラ目線）あなたの会社の“穴”、塞ぎませんか')
A('<b>～ おわり ～</b>')
NB('社名はすべて架空。冒頭・末尾にフィクション表示。制度・窓口名と保守停止表現は放送時点で技術監修・法務監修の確認を推奨。')

def footer(c,doc):
    c.saveState(); c.setFont('JP',8); c.setFillColor(GREY)
    c.drawCentredString(A4[0]/2,10*mm,'%d'%doc.page)
    c.drawString(16*mm,10*mm,'『サイバークライシス』改訂版2（信頼経路版）')
    c.restoreState()

doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_改訂版2_信頼経路版_台詞付き.pdf',
    pagesize=A4,topMargin=16*mm,bottomMargin=16*mm,leftMargin=18*mm,rightMargin=16*mm,
    title='サイバークライシス 改訂版2 信頼経路版 台詞付き')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('done')
