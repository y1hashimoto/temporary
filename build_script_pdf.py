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
NAVY = colors.HexColor('#2b3a55'); GREY=colors.HexColor('#555555')

def S(name, **kw):
    base = dict(fontName='JP', fontSize=10.5, leading=16, textColor=colors.HexColor('#111111'),
                alignment=TA_LEFT, spaceAfter=3)
    base.update(kw); return ParagraphStyle(name, **base)

title   = S('title', fontSize=18, leading=23, alignment=TA_CENTER, spaceAfter=2)
subt    = S('subt', fontSize=10, leading=14, alignment=TA_CENTER, textColor=GREY, spaceAfter=2)
discl   = S('discl', fontSize=9, leading=13, alignment=TA_CENTER, textColor=GREY)
scene   = S('scene', fontSize=11.5, leading=16, textColor=colors.white, spaceBefore=0, spaceAfter=0)
sub     = S('sub', fontSize=10.5, leading=15, textColor=NAVY, spaceBefore=6, spaceAfter=2)
act     = S('act', fontSize=10, leading=15, textColor=colors.HexColor('#333333'), spaceAfter=3)
line    = S('line', fontSize=10.5, leading=16, leftIndent=10, spaceAfter=2)
mono    = S('mono', fontSize=10.5, leading=16, leftIndent=10, textColor=colors.HexColor('#5a3a00'), spaceAfter=2)
note    = S('note', fontSize=9, leading=13, textColor=GREY, leftIndent=10, spaceAfter=3)
h1      = S('h1', fontSize=14, leading=18, textColor=NAVY, spaceBefore=8, spaceAfter=4)

story=[]
def scene_bar(txt):
    p=Paragraph(txt, scene)
    t=Table([[p]],colWidths=[None])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),NAVY),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(Spacer(1,8)); story.append(t); story.append(Spacer(1,4))

story.append(Paragraph('『サイバークライシス ～あの時、私は…～』', title))
story.append(Paragraph('改訂版（台詞付き・初稿リライト）　／　内容尺 約7分＋解説ブロック', subt))
story.append(Spacer(1,4))
story.append(Paragraph('※この物語はフィクションです。実在の企業・団体・人物とは一切関係ありません。', discl))
story.append(Paragraph('※「穴」は一貫して「見過ごされた脆弱性（落とし穴）」を指す。', discl))
story.append(Spacer(1,4))

def L(speaker, text):
    story.append(Paragraph('<b>%s</b>「%s」' % (speaker, text), line))
def A(text):
    story.append(Paragraph(text, act))
def NB(text):
    story.append(Paragraph('※ %s' % text, note))

# ===== 本編 =====
scene_bar('○街・雑踏')
A('歩道の一角に、ぽっかり開いた『穴』。人々は自然に避けて通る。多田啓二（29）もその一人。')
L('穴のM','目に見える穴は、誰だって避けて通る')

scene_bar('○デジタル社会（点描）')
A('パソコン。複合機。スマートフォン。工場の生産ライン。矢継ぎ早に。')
L('穴のM','だが――気づかれないまま、ずっと放置されている穴がある')
A('オフィス。<b>付箋に書かれたパスワード</b>。開きっぱなしの共有フォルダ。警告を“確認せず”閉じる指。')
L('穴のM','あなたの会社の、その小さな穴に。誰かが手を伸ばす前に――気づけるか？')
A('多田が振りかえる。タイトルイン。<b>『サイバークライシス ～あの時、私は…～』</b>')

scene_bar('○木川精機・社長室（午前10時）')
A('パターでホールイン。練習中の社長・木川宗吾（65）。総務部・セキュリティ担当の多田が向き合う。')
L('多田','社長。セキュリティ対策の件、もう一度ご検討いただけませんか')
L('木川','またその話か。サイバー攻撃なんて、うちみたいな下請けを狙うヤツがいるのか？')
L('多田','いえ、むしろ逆なんです。大手は守りが固い。だから――取引先の、中小がまず狙われる')
story.append(Paragraph('○同・部品工場（カットイン）', sub))
A('ITで管理された生産ライン。工場長・鈴木。')
L('鈴木','うちは受発注も在庫管理も全部システム頼みだろ？ 止まったら一発で出荷できなくなる。大丈夫なのか？')
story.append(Paragraph('○同・管理部（カットイン）', sub))
L('津山','共有フォルダのパスワード、付箋で貼ってる人もいるのよ。前から気になってて')
story.append(Paragraph('○社長室（戻り）', sub))
L('多田','……と、現場も不安を感じています')
L('木川','心配しすぎだ。うちだって、それなりに対策はしてるだろう')

scene_bar('○同・社長室（侵入の瞬間）　※新規')
A('多田、社長デスク脇の<b>付箋パスワード</b>に気づく。')
L('多田','社長、このパスワードの付箋は……外しましょう。それと')
A('社長PCに一通のメール。件名「【至急】請求書の差し戻しについて」。本文「内容を表示するには〔コンテンツの有効化〕を押してください」。')
L('多田','この添付、開かないでください。“有効化”は絶対に押さないで――')
L('木川','（かぶせて）忙しいんだ。取引先からだろう、後にしてくれ')
A('木川、面倒そうに<b>〔コンテンツの有効化〕をクリック</b>。一瞬、画面がちらつく。')
L('多田','！')
A('だが木川はもうパター練習に戻っている。')
L('多田','（小声）……今の、よくなかったな')

scene_bar('○同・廊下')
A('掃除中のおばさんが防犯カメラを不思議そうに見上げる。')
L('おばさん','ねえ、あのカメラ。さっきから勝手に動くのよ')
A('多田、足を止める。レンズが不自然に動く。今度は<b>見過ごさない</b>。')
L('多田','……前は、こんな動きはしてなかった。あとで記録を確認しよう')
NB('スマホにメモ＝後の伏線回収。')

scene_bar('○社長デスクのパソコン')
A('木川がスマホで取引先と電話。背後のPCで<b>送信済みフォルダの件数が静かに増えていく</b>。木川は気づかない。')
L('木川','（電話）恒例のゴルフコンペ、関連各社にもお声がけしようと。ぜひメイユー自動車さんにも――')
A('PC画面。送信先「メイユー自動車」。添付「ゴルフコンペ案内.xlsm」。送信。')
story.append(Paragraph('○メイユー自動車・フロア', sub))
L('担当者','木川精機さんからゴルフコンペの案内か。お、もう来てる')
A('何気なく開き、〔コンテンツの有効化〕をクリックしてしまう。')

scene_bar('○多田家・リビング')
A('臨月の妻・由香。お腹を抱え、スマホを手に。')
L('由香','（電話）あなた？ ……うん、ちょっとお腹が張ってて。まだ大丈夫だと思うけど')
story.append(Paragraph('○木川精機・オフィスフロア', sub))
L('多田','無理しないで。何かあったらすぐ連絡して。すぐ帰るから')
L('由香','ありがとう。……あ、また連絡する')
A('そこへ津山が駆け寄る。')
L('津山','多田君、テレビ！')

scene_bar('○同・オフィス（テレビ）')
L('アナウンサー','速報です。自動車部品大手・メイユー自動車は、社内システムの障害により国内の一部工場で生産を停止したと発表しました。サイバー攻撃の可能性も含めて確認を進めています')
story.append(Paragraph('○同・社長室', sub))
L('木川','やっぱり大手は狙われるんだなあ')
A('多田が入ってくる。')
L('多田','社長、今のニュース……うちの取引先です')
L('アナウンサー','続報です。メイユー自動車の障害について、<b>同社の取引先や関連企業でも同様のシステム障害が確認されている</b>ことが分かりました')

scene_bar('○同・オフィス（発覚）')
A('多田、社長PCの送信済みフォルダを確認。<b>取引先宛ての不正メールが止まらず送信され続けている</b>。')
L('多田','……ウソだろ')
L('木川','（来て）どうした')
L('多田','社長。<b>感染源は、うちです</b>。さっきの“有効化”で、ここから取引先にばらまかれた')
L('木川','なんだと！？')
L('多田','乗っ取られてる。……すぐ、専門機関と警察に届け出ましょう。IPAやJPCERTにも連絡を')
A('その手を木川が止める。')
L('木川','待て！ うちが感染源だと公表されたら、取引先に何と言われる。会社が終わるぞ！')
L('多田','でも、黙っていたら被害が広がるんです！ ここで止めないと――')
L('木川','……っ')

scene_bar('○多田家・玄関〜外（インサート・短く）')
A('由香、陣痛の波。自分でタクシーを呼び、気丈にゆっくり玄関を出る。')
L('由香','（自分に言い聞かせ）大丈夫……一歩ずつ')
NB('サイバー被害が直接の原因ではない。多田が「守りたいもの」を思い出す動機として配置。')
story.append(Paragraph('○木川精機・オフィス', sub))
A('多田のスマホに由香から「これから病院へ向かう」。多田、意を決して顔を上げる。')
L('多田','社長。隠して守れる会社なら、とっくに守れてます。<b>今すぐ報告して、被害を最小限にする</b>。それが取引先への、いちばんの誠意です')
A('木川、苦しげに目を閉じ――やがて小さく頷く。')
L('木川','……分かった。お前に任せる')
L('多田','<b>外部との通信を遮断してください。感染した端末はネットワークから外す</b>。落ち着いて、順番に！')
L('津山','は、はい！')
L('多田','（電話）JPCERTコーディネーションセンターですか。木川精機の多田です。当社が踏み台にされ、取引先へ不正メールが――はい、ログは保全しています')

scene_bar('○同・オフィス（封じ込め・夜）')
A('時間経過。専門機関の担当者と、サイバー事案担当の警察官が来訪。社員と連携し淡々と作業。<b>武装した部隊ではない</b>。')
L('担当者','ご連絡ありがとうございます。発信元サーバとの通信を遮断し、感染端末を隔離します。御社のログのおかげで経路がかなり特定できました')
L('木川','……被害は、止められますか')
L('担当者','<b>早い段階で報告いただけたのが大きい</b>。これ以上の拡散は抑えられる見込みです。取引先各社にも、いま注意喚起が回っています')
A('多田、画面の攻撃者アイコン<b>『ホールインワンの穴』</b>を見つめる。担当者が隔離を実行すると、アイコンがふっと消える。')
L('多田','（小声）……塞いだぞ')
A('そのとき、多田のスマホが震える。表示「由香」。')

scene_bar('○記者会見（夜）')
A('フラッシュ。木川が頭を下げる。')
L('木川','当社の確認不足により、取引先の皆様に多大なご迷惑をおかけしました。誠に申し訳ございません。原因と再発防止策を、包み隠さず公表してまいります')
L('記者の声','被害の拡大は止まったんですか？')
L('木川','専門機関と連携し、<b>現在は封じ込めが完了しています</b>。取引先とも復旧に向けて協力しています')
A('壇上を見上げる多田。スマホがまた震える。')

scene_bar('○街（夜）')
A('多田が走る。')
L('多田M','俺は、何ができたんだろう。……いや。<b>気づいて、声を上げて、つないだ</b>。それが、できることだった')
A('例の街の『穴』を、今度は<b>避けながら</b>駆け抜けていく。')

scene_bar('○病院・病室（夜）')
A('ベッドの由香。多田が飛び込んでくる。')
L('多田','由香！ ごめん、遅くなって')
L('由香','……来てくれた。間に合ったよ')
A('由香、傍らの赤ん坊に目をやる。')
L('由香','見て。元気な男の子')
L('多田','（我が子を見つめ）よかった……本当に、よかった')
L('由香','新しい家族の、一歩だね')
A('涙ぐみ、頷く多田。')
L('穴のM','見過ごされた穴は――気づけば、塞げる')

scene_bar('○街の穴')
A('人々が行き交う。穴から声が響く。')
L('穴のM','その一歩を、踏み外さないために。<b>あなたに、できることは？</b>')
A('<b>～ ドラマ本編 おわり ～</b>')

# ===== 解説ブロック =====
story.append(Paragraph('解説ブロック', h1))
scene_bar('○木川精機・会議室（後日）')
A('モニターで本編VTRを見終えた社員たち。')
L('木川','いやはや。まったく、他人事じゃなかったな')
L('多田','そうですよ、社長。付箋のパスワード、まだ残ってませんか？')
L('木川','うっ……剥がす、剥がすから')
A('モニター横に立つ講師・穴吹衛。')
L('穴吹','では、こうならないために何ができたのか。VTRを振り返りながら、5つのポイントで整理しましょう')
story.append(Paragraph('① 入口：メールの添付と「コンテンツの有効化」', sub))
L('穴吹','最初の落とし穴は社長が押した〔コンテンツの有効化〕。今のOfficeはメールやネット経由のマクロを既定でブロックします。“有効化”を促すメッセージは立ち止まる合図。心当たりのない添付は開かない、開いても有効化しない。これで多くの侵入は防げます')
story.append(Paragraph('② パスワードと認証', sub))
L('穴吹','付箋パスワードは論外。使い回しをやめ、多要素認証（MFA）を有効に。共有フォルダのアクセス権も必要な人だけに')
story.append(Paragraph('③ 検知と備え', sub))
L('穴吹','OSやソフトは常に最新に。EDRなどで“おかしな動き”を検知できれば、送信済みが増え続ける前に気づけます。ログを残すことも後の調査で効きます')
story.append(Paragraph('④ 起きた“後”：すぐ報告・相談する', sub))
L('穴吹','隠すと被害は広がります。困ったら――IPA 情報セキュリティ安心相談窓口／JPCERTコーディネーションセンター／警察（サイバー事案・#9110）へ。早い報告ほど被害は小さくできます')
story.append(Paragraph('⑤ サプライチェーンの責任', sub))
L('穴吹','自社の小さな穴が取引先や業界全体を止めることがあります。“うちは下請けだから”は狙われない理由になりません。つながっているからこそ、一人ひとりの対策が全体を守ります')
L('穴吹','『あの時、私は』――そう後悔しないために。今日できることから、一つずつ')
L('多田','（カメラ目線で）あなたの会社の“穴”、塞ぎませんか')
A('<b>～ おわり ～</b>')
NB('社名はすべて架空。冒頭・末尾に「フィクション」表示を。③④の制度・窓口名は放送時点で技術監修・法務監修の確認を推奨。')

def footer(canvas, doc):
    canvas.saveState(); canvas.setFont('JP',8); canvas.setFillColor(GREY)
    canvas.drawCentredString(A4[0]/2, 10*mm, '%d' % doc.page)
    canvas.drawString(16*mm,10*mm,'『サイバークライシス』改訂版（台詞付き）')
    canvas.restoreState()

doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_改訂版_台詞付き脚本.pdf',
    pagesize=A4, topMargin=16*mm, bottomMargin=16*mm, leftMargin=18*mm, rightMargin=16*mm,
    title='サイバークライシス 改訂版 台詞付き脚本')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print('done')
