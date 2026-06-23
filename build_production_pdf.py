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
NAVY=colors.HexColor('#2b3a55'); GREY=colors.HexColor('#555555'); RUST=colors.HexColor('#7a3b00')

def S(n,**k):
    b=dict(fontName='JP',fontSize=10.3,leading=15.5,textColor=colors.HexColor('#111111'),alignment=TA_LEFT,spaceAfter=3)
    b.update(k); return ParagraphStyle(n,**b)

title=S('t',fontSize=17.5,leading=22,alignment=TA_CENTER,spaceAfter=2)
subt =S('s',fontSize=9.6,leading=13,alignment=TA_CENTER,textColor=GREY,spaceAfter=2)
discl=S('d',fontSize=8.8,leading=12.5,alignment=TA_CENTER,textColor=GREY)
scn  =S('sc',fontSize=11,leading=15,textColor=colors.white)
place=S('pl',fontSize=10.3,leading=14.5,textColor=NAVY,spaceBefore=4,spaceAfter=2)
act  =S('a',fontSize=10,leading=14.5,textColor=colors.HexColor('#2d2d2d'),spaceAfter=2,leftIndent=2)
line =S('l',fontSize=10.3,leading=15.5,leftIndent=12,spaceAfter=2)
note =S('n',fontSize=8.8,leading=12.5,textColor=GREY,spaceAfter=3)
h1   =S('h',fontSize=13.5,leading=17,textColor=NAVY,spaceBefore=8,spaceAfter=4)
cell =S('c',fontSize=8.8,leading=12,spaceAfter=0)
cellh=S('ch',fontSize=9,leading=12,textColor=colors.white,spaceAfter=0)
legend=S('lg',fontSize=8.8,leading=12.5,textColor=GREY,spaceAfter=2)

story=[]
def bar(txt):
    p=Paragraph(txt,scn); t=Table([[p]],colWidths=[None])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),NAVY),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(Spacer(1,7)); story.append(t); story.append(Spacer(1,3))
def PL(t): story.append(Paragraph(t,place))
def A(t): story.append(Paragraph(t,act))
def L(sp,t): story.append(Paragraph('<b>%s</b>「%s」'%(sp,t),line))
def NB(t): story.append(Paragraph('※ '+t,note))

story.append(Paragraph('『サイバークライシス ～あの時、私は…～』',title))
story.append(Paragraph('撮影台本ドラフト（信頼経路版・作り込み稿）　／　本編 約7分＋解説ブロック',subt))
story.append(Spacer(1,3))
story.append(Paragraph('※この物語はフィクションです。実在の企業・団体・人物とは一切関係ありません。',discl))
story.append(Spacer(1,3))
story.append(Paragraph('凡例：SE=効果音／M=音楽／T=テロップ／(OFF)=画面外の声／INSERT=差し込み。攻撃描写は派手にしない。'
    '社会インフラは「予防的停止・手動切替」に限定（信号・実停電・勘定系・本人確認系は描かない）。',legend))

bar('＃1　アバン　0:00–0:50')
PL('○街・雑踏（朝）')
A('<b>C1</b>　歩道のアスファルトに工事用の『穴』。三角コーン。人々が無意識に避けて流れる。俯瞰。 <b>SE</b>雑踏／<b>M</b>静かなパッド。')
A('<b>C2</b>　流れの中、多田啓二（29）が穴を一瞥し避けて通る。歩きながらスマホ。')
L('穴のM','（OFF・低い声）目に見える穴なら――誰だって、避けて通る')
PL('○モンタージュ：見えない“線”（点描）')
A('<b>C3</b>　木川精機サーバ室。ラックのLED。画面「KIGAWA-Link 配信管理」＝「保守ツール 更新パッケージ」一覧。')
A('<b>C4</b>　画面から<b>光の線が一本</b>のびる（合成）。地図上を走り――')
A('<b>C5</b>　→ 鉄道の<b>保守倉庫</b>：作業員がタブレットで部材在庫確認。')
A('<b>C6</b>　→ 電力の<b>保守受付</b>：作業手配画面を操作。')
A('<b>C7</b>　→ 銀行設備の<b>管理窓口</b>：ATM筐体の点検記録を入力。')
A('<b>C8</b>　線は枝分かれし無数の端末へ。すべてが木川精機の“更新”を信頼して受け取る。')
L('穴のM','だが、見えない穴は――“信頼”を伝って、社会の下で、つながっていく')
A('<b>C9</b>　多田が振り返りレンズを見据える。<b>M</b>ストップ。 <b>T</b>タイトルイン『サイバークライシス ～あの時、私は…～』')

bar('＃2　木川精機・中小の油断　0:50–1:50')
PL('○木川精機・社長室（午前10時）')
A('<b>C10</b>　パターマット。ボールがカランとカップイン。練習中の社長・木川宗吾（65）。')
A('<b>C11</b>　ドア横で資料を抱えた多田。やや緊張。')
L('多田','社長。KIGAWA-Linkの件、もう一度だけ。あれは“うちだけ”のシステムじゃありません。取引先も保守会社も――電力さんや鉄道さんの<b>協力会社まで</b>、あそこから<b>更新ファイルを取り込んでいます</b>')
A('<b>C12</b>　木川、構えたまま振り向きもせず。')
L('木川','うちは部品屋だぞ。電車や電気を動かしてるわけじゃない')
L('多田','動かしてはいません。でも“信頼されている”。……その信頼が、穴になることがあるんです')
A('<b>C13</b>　ボールがカップに。木川、満足げ。')
L('木川','大げさだ。だいたい、うちみたいな下請けを、誰が狙う')
L('多田','（小さく）狙うんです。<b>大手より、入りやすいから</b>')
A('<b>C14</b>　木川には届かない。多田、ひとつ息をつく。')

bar('＃3　二重の穴（侵入の伏線）　1:50–2:40')
PL('○同・廊下')
A('<b>C15</b>　清掃員の女性が天井の防犯カメラを不審そうに見上げる。')
L('清掃員','ねえ、お兄さん。あのカメラ、さっきから勝手に動くのよ。気味が悪くて')
A('<b>C16</b>　多田、足を止める。レンズが不自然にパン。今度は見過ごさない。')
PL('○同・防犯設備の管理端末（小部屋）')
A('<b>C17</b>　管理画面。設定一覧に「初期パスワードのまま」に近い表示。')
A('<b>C18</b>　カメラのプレビューに映り込む<b>ホワイトボード</b>＝「KIGAWA-Link 管理URL」「共有ID」、付箋で<b>VPN接続メモ</b>。')
L('多田','……これ、<b>外から丸見え</b>だ')
A('<b>C19</b>　管理部。津山が共有PC脇を指す。')
L('津山','これも前から気になってて。パスワード、付箋で貼ってあるの')
L('多田','（青ざめ）VPNに<b>多要素認証も掛かってない</b>……IDとパスワードだけで、誰でも入れる')
A('<b>C20</b>　社長室。')
L('木川','今は決算前だ。納期もある。予算の話は来期に')
A('<b>C21</b>　多田、引き下がるしかない。')
L('穴のM','穴は、ひとつではなかった')

bar('＃4　足場化（潜伏）　2:40–3:25')
PL('○同・サーバ室（深夜）')
A('<b>T</b>「――数週間前」　<b>C22</b>　無人。ラックのLEDだけが瞬く。派手な描写はしない。')
A('<b>C23</b>　ログ画面（INSERT）。深夜帯に<b>見慣れない海外IPからのVPNログイン成功</b>→<b>管理者権限の使用</b>。 <b>SE</b>秒針のみ／<b>M</b>不穏に持続。')
L('穴のM','攻撃者は、盗んだ鍵で、静かに入り込んでいた。壊さず、ただ待っていた')
PL('○同・KIGAWA-Link 配信管理（後日・昼）')
A('<b>C24</b>　配信スケジュールが<b>書き換わる</b>（カーソルは見せず、値だけ切替）。「保守ツール v3.2 更新」「図面ビューア 更新」。')
A('<b>C25</b>　各社端末にポップアップ（モンタージュ）「木川精機より更新があります」。')
L('穴のM','いつもの相手からの、いつもの更新。誰も、疑わなかった')

bar('＃5　異変　3:25–4:25')
PL('○木川精機・オフィス（朝）')
A('<b>C26</b>　多田が共有ファイルを開こうとする→「ファイルを開けません」。顔が曇る。')
A('<b>SE</b>　固定電話が一本、二本、三本――<b>フロア中の電話が一斉に鳴り出す</b>。')
A('<b>C27</b>　社員が次々受話器を取る。困惑の声が重なる。')
L('鉄道系保守会社','（電話OFF）木川さん、おたくの<b>更新を“適用”した端末</b>が軒並み固まった。保守倉庫の在庫照会が止まってる。部材が出せないと、明日の点検が回らない')
A('<b>C28</b>　別の島。津山が受話器を握りしめる。')
L('銀行系設備管理会社','（電話OFF）念のため、ウチの<b>設備保守端末を切り離した</b>。……ATMの予防保守がいくつか止まる。利用者向けは“メンテナンス”で出すしかない')
A('<b>C29</b>　さらに別の島。')
L('電力系保守会社','（電話OFF）<b>停電対応の作業指示</b>が出せない。今夜もし停電が起きたら、手配が遅れる。……勘弁してくれよ')
A('<b>C30</b>　受話器を置いた多田。木川が駆けてくる。')
L('木川','なんで――うちから、そんなところまで広がるんだ！？')
L('多田','<b>KIGAWA-Linkです</b>。うちが“信頼された配布元”として悪用されてる。……ただ、社長')
A('<b>C31</b>　多田、あえて冷静に。')
L('多田','<b>“感染源はうち”と、まだ断定はできません</b>。どこまで汚染されたか、切り分けが終わってない。それも含めて、すぐ動くべきです')

bar('＃6　予防的停止（社会の“側”）　4:25–5:15')
PL('○オフィスのテレビ／街頭ビジョン（INSERT集）')
A('<b>C32</b>　ニュース速報テロップ。')
L('アナウンサー','（OFF）複数の企業でシステム障害。<b>鉄道各社は保守・駅務系の一部を“予防的に”停止</b>し安全確認中。運行は本数を絞って継続――')
A('<b>C33</b>　駅。自動改札の半分に「閉鎖」。駅員が拡声器で手動案内。乗客の列。')
L('アナウンサー','（OFF）一部の銀行は<b>設備保守の都合で一部ATMを休止</b>。<b>勘定系には影響していない</b>としています')
A('<b>C34</b>　ATMコーナー。数台に「メンテナンス中」。利用者が隣店舗へ。')
L('アナウンサー','（OFF）電力会社は<b>停電対応の受付と保守手配の一部を手動運用に切り替えた</b>と発表')
A('<b>C35</b>　コールセンター。モニターを伏せ、<b>紙の台帳と電話</b>で対応。')
A('<b>C36</b>　多田、テレビを見つめる。')
L('穴のM','壊れたのではない。“どこまで汚れたか分からない”から、止めるしかなかった')

bar('＃7　社長の葛藤　5:15–6:00')
PL('○木川精機・社長室')
A('<b>C37</b>　窓の外、夕暮れ。木川、デスクに両手をつきうつむく。')
L('木川','……公表したら、終わりだ。“木川精機が止めた”なんて知られたら、取引が全部――')
L('多田','隠せば、<b>もっと止まります</b>。今できるのは、分かっていることを、正直に出すこと。それだけです')
L('木川','うちは、被害者だぞ')
L('多田','はい。被害者です。<b>でも同時に、踏み台にされた。両方なんです</b>。だから――黙る理由には、ならない')
A('<b>C38</b>　長い沈黙。木川、ゆっくり顔を上げる。覚悟の表情。')
L('木川','……鈴木を呼べ。警察と、専門機関と、取引先に連絡しろ。<b>KIGAWA-Linkは止める</b>')
A('<b>C39</b>　駆けつけた鈴木工場長。')
L('鈴木','止めたら、うちの<b>出荷も止まりますよ</b>')
L('木川','止める。――<b>安全が確認できないものは、使わない</b>。それが、ものづくりだろう')
A('<b>C40</b>　鈴木、深く頷く。')

bar('＃8　封じ込めと教訓　6:00–7:00')
PL('○同・会議室（夜）')
A('<b>C41</b>　ホワイトボード（手書き）「KIGAWA-Link停止」「影響範囲の切り分け」「取引先へ：<b>“その更新を適用しないで”</b>」「代替手段／復旧の優先順位」「ログ保全」。')
A('<b>C42</b>　多田、受話器を握りメモを見ながら。')
L('多田','（電話）JPCERTコーディネーションセンターさんですか。木川精機の多田です。当社のポータルが<b>配布元として悪用され</b>、配った更新ファイルに不正なコードが――はい、<b>ログは保全しています</b>。攻撃元との通信もこちらで遮断を……')
A('<b>C43</b>　壁の時計。夜が更ける。社員が手分けして電話とリスト潰し。')
PL('○記者会見（同・夜）')
A('<b>C44</b>　フラッシュ。木川、一礼して頭を下げ、ゆっくり戻す。')
L('木川','当社のサーバーが、不正に利用された可能性があります。現在、警察および外部の専門家とともに調査しています。<b>安全が確認できるまで、KIGAWA-Linkを停止します</b>')
A('<b>C45</b>　記者席から厳しい声。')
L('記者A／B','（OFF）いつ復旧するんですか／なぜもっと早く知らせなかった')
L('木川','分かっていること、分かっていないことを分けて、隠さずお伝えします。――それが、今できる、せめてものことです')
A('<b>C46</b>　壇上下で見守る多田。その横顔。')
PL('○街・雑踏（夜）→ ＃1と対の画')
A('<b>C47</b>　帰路の多田。朝、避けたあの『穴』の前で立ち止まる。今度は避けず、踏み外さないようまたぐ。')
L('多田M','俺は、何ができたんだろう。……いや。<b>気づいて、声を上げて、つないだ</b>。それが、できることだった')
L('穴のM','穴は、一社の中だけにあるとは限らない。つながった先で、さらに深くなる')
A('<b>C48</b>　多田、夜の街へ歩き出す。')
L('穴のM','その一歩を、踏み外さないために――<b>あなたに、できることは？</b>')
A('<b>T／M</b>　暗転。')
story.append(Paragraph('◆ キーとなる一文（＃5 or ＃7で多田に言わせてもよい）',place))
L('多田','社長、うちが電車や銀行を止めたわけじゃない。でも、<b>うちが配った“更新ファイル”を、各社が信頼して取り込んだ</b>。だから、どこまで汚れたか分かるまで、各社は止めるしかないんです')
A('<b>～ 本編 おわり ～</b>')

story.append(Paragraph('解説ブロック',h1))
PL('○木川精機・会議室（後日）')
A('VTRを見終えた社員たち。空気は少し軽い。')
L('木川','いやはや。まったく、他人事じゃなかった')
L('多田','社長。あの付箋のパスワード、剥がしました？')
L('木川','うっ……剥がした。剥がしたとも')
A('講師・穴吹衛がモニター横へ。')
L('穴吹','“つながっているからこそ”起きた事故でした。振り返って、5つだけ')
# table
rows=[
 ['①','更新ファイル・添付は“適用／実行”が分かれ目。閲覧では感染しない。配布元が信頼できても署名・配信元・ハッシュを確認','＃4→＃5'],
 ['②','多要素認証（MFA）をVPN・管理ポータルに。付箋PW・使い回しは厳禁','＃3'],
 ['③','監視カメラ等の初期設定を変更し外部公開を遮断。“見られている”前提で機密を映さない','＃3'],
 ['④','EDR・更新・ログ。深夜の不審通信や管理者権限の異常を検知。ログ保全が封じ込めを早める','＃4'],
 ['⑤','サプライチェーン／信頼経路の責任。自社が“信頼された配布元”の自覚を。起きたら即報告・相談（IPA／JPCERT/CC／警察#9110）','＃8'],
]
data=[[Paragraph('',cellh),Paragraph('ポイント',cellh),Paragraph('作中',cellh)]]
for r in rows:
    data.append([Paragraph(r[0],cell),Paragraph(r[1],cell),Paragraph(r[2],cell)])
t=Table(data,colWidths=[8*mm,None,16*mm],repeatRows=1)
ts=[('BACKGROUND',(0,0),(-1,0),NAVY),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#99a0b0')),
    ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
    ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]
for i in range(1,len(data)):
    if i%2==0: ts.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#f5f7fb')))
t.setStyle(TableStyle(ts)); story.append(Spacer(1,4)); story.append(t); story.append(Spacer(1,6))
L('穴吹','“うちは下請けだから狙われない”は、もう通用しません。つながっているから、あなたの対策が、全体を守る')
L('多田','（カメラ目線）――あなたの会社の“穴”、塞ぎませんか')
A('<b>～ おわり ～</b>')
NB('社名はすべて架空。冒頭・末尾にフィクション表示。C4〜C8の光の線は合成/MG。停止表現・制度名は放送時点で技術＋法務監修を推奨。'
   '尺の伸縮代：＃1アバン（±10秒）、＃6 INSERT集（社数を2社に削れば短縮可）。')

def footer(c,doc):
    c.saveState(); c.setFont('JP',8); c.setFillColor(GREY)
    c.drawCentredString(A4[0]/2,10*mm,'%d'%doc.page)
    c.drawString(16*mm,10*mm,'『サイバークライシス』撮影台本ドラフト（信頼経路版）')
    c.restoreState()

doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_撮影台本ドラフト_信頼経路版.pdf',
    pagesize=A4,topMargin=16*mm,bottomMargin=16*mm,leftMargin=16*mm,rightMargin=15*mm,
    title='サイバークライシス 撮影台本ドラフト 信頼経路版')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('done')
