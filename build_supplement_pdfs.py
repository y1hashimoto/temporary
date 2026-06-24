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
BLUE=colors.HexColor('#1f6feb')

def S(n,**k):
    b=dict(fontName='JP',fontSize=10.3,leading=15.5,textColor=colors.HexColor('#111111'),alignment=TA_LEFT,spaceAfter=3)
    b.update(k); return ParagraphStyle(n,**b)
title=S('t',fontSize=16.5,leading=20.5,alignment=TA_CENTER,spaceAfter=2)
subt =S('s',fontSize=9.4,leading=13,alignment=TA_CENTER,textColor=GREY,spaceAfter=2)
discl=S('d',fontSize=8.8,leading=12.5,alignment=TA_CENTER,textColor=GREY)
h1   =S('h',fontSize=13.5,leading=17,textColor=NAVY,spaceBefore=8,spaceAfter=4)
body =S('b')
li   =S('li',fontSize=10.2,leading=15,leftIndent=8,spaceAfter=4)
cell =S('c',fontSize=8.9,leading=12.3,spaceAfter=0)
cellh=S('ch',fontSize=9.1,leading=12.3,textColor=colors.white,spaceAfter=0)
qst  =S('q',fontSize=10.6,leading=15,textColor=colors.white,spaceAfter=0)
note =S('n',fontSize=8.8,leading=12.5,textColor=GREY,spaceAfter=3)

def footer_maker(label):
    def f(c,doc):
        c.saveState(); c.setFont('JP',8); c.setFillColor(GREY)
        c.drawCentredString(A4[0]/2,10*mm,'%d'%doc.page)
        c.drawString(15*mm,10*mm,label); c.restoreState()
    return f
def tbl(story,header,rows,widths,zebra=True,hcolor=NAVY):
    data=[[Paragraph(h,cellh) for h in header]]
    for r in rows: data.append([Paragraph(c,cell) for c in r])
    t=Table(data,colWidths=widths,repeatRows=1)
    ts=[('BACKGROUND',(0,0),(-1,0),hcolor),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#99a0b0')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]
    if zebra:
        for i in range(1,len(data)):
            if i%2==0: ts.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#f5f7fb')))
    t.setStyle(TableStyle(ts)); story.append(t); story.append(Spacer(1,8))

# ===================================================================
# DOC 1: 弁護士台詞 精緻化シート（法務監修用）
# ===================================================================
st=[]
st.append(Paragraph('『サイバークライシス』台詞精緻化シート（法務監修用）',title))
st.append(Paragraph('改訂版5準拠／損害賠償・注意義務に関する台詞のたたき台。最終表現は法務監修で確定する。',subt))
st.append(Spacer(1,3))
st.append(Paragraph('※本シートは監修用のドラフト。確定前の表現であり、放送可否・最終文言は弁護士監修の判断による。',discl))

st.append(Paragraph('A. 前提として共有したい法的フレーム（番組での扱い方）',h1))
tbl(st,['論点','要旨','番組での扱い方（断定回避）'],
 [['責任の根拠','損害賠償は通常、債務不履行（契約違反）または不法行為（過失）で問われる','「必ず賠償」とは言わない。“問われうる/争点”と表現'],
  ['注意義務の水準','“専門家レベル”ではなく、その立場で通常期待される合理的・基本的対策','「基本を尽くしたか」を軸に。高度防御は求めない'],
  ['契約上の責任','取引契約のセキュリティ要件・SLA・責任制限条項が影響','「契約で定めがある場合がある」と一般化して触れる'],
  ['因果関係/予見可能性','侵入経路・損害との因果、予見できたかが争点','劇中は断定せず“協議・調査”で進める'],
  ['過失相殺','被害側の対策不足等で割合が調整されうる','解説で「双方の事情で変わる」と一言'],
  ['緩和要素','誠実な初動・事実保全・協力・再発防止が考慮されうる','「有利になりうる」程度に。確約しない'],
  ['備え','サイバー保険・契約見直しでリスク移転/限定','解説で前向きな選択肢として提示']],
 widths=[26*mm,None,58*mm])

st.append(Paragraph('B. 台詞の精緻化（現行→監修用案）',h1))
tbl(st,['場面','現行（改訂版5）','精緻化案（監修用・選択肢）','狙い／監修確認'],
 [['＃5 弁護士',
   '“専門家であれ”とは申しません。問われるのは、多要素認証や更新といった広く知られた“基本”を、警告がありながら取っていたか。そこが争点です',
   '案A：御社に高度な専門知識までは求められません。ただ、契約や一般に期待される水準として、基本的な安全対策を講じる注意義務はあります。それを尽くしていたかが、責任の有無を左右します。<br/>案B：責任が当然に生じるわけではありません。基本的な対策を、相応の理由なく怠っていたか――そこが、これからの協議の争点になります。',
   '「専門家性の欠如」でなく「基本＋注意義務」に。“当然/必ず”を避ける。注意義務の言い回しを監修'],
  ['＃2 多田',
   'やらずに何かあれば、“知らなかった”では済まないかもしれない',
   '案：これは“知っていてやらなかった”ことになりかねません。基本だけでも、やっておきたいんです。',
   '脅し表現を避け、事実ベースに。断定しない'],
  ['＃6 多田',
   '事実を保全し協力する姿勢は、これからの協議でも必ず効いてきます',
   '案：事実を保全して、正直に協力する。それが、信頼を守るうえでも、今後の協議でも、きっとプラスになります。',
   '“必ず”を“プラスになりうる”に弱める（法的効果を確約しない）'],
  ['＃5 木川',
   'うちは素人だぞ！ 専門家でもないのに、そこまで責任を負えと？',
   '（維持推奨）視聴者の本音を代弁するセリフ。弁護士の応答とセットで成立',
   'このまま残す。視聴者の反論を作品内で受け止める機能'],
  ['解説②',
   '損害賠償は“自動”ではない…ただし広く知られた基本を警告がありながら怠った場合はリスクが現実に',
   '（維持）＋一文追加案：「実際の判断はケースごとに異なります。心配な場合は、弁護士や専門機関にご相談を」',
   '相談誘導で締め、断定を回避']],
 widths=[20*mm,None,None,40*mm])

st.append(Paragraph('C. 監修者へのチェック依頼項目',h1))
for t in ['「注意義務」「争点」「協議」など、断定を避けた表現が法的に適切か',
          '実例（医療センター事例）の事実関係・損害賠償/和解の有無・引用可否（金額は出さない方針）',
          '“身代金は払わない”の表現（推奨だが状況依存。番組としての言い切り可否）',
          'サイバー保険・契約条項に関する一般化表現の妥当性',
          '相談窓口・ガイドライン名（IPA／JPCERT/CC／SECURITY ACTION／警察#9110）の最新・正確性']:
    st.append(Paragraph('☐ '+t,li))
st.append(Paragraph('※社名・金額は架空。本シートは改訂版5本編・解説の該当箇所に対応。',note))

doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_台詞精緻化シート_法務監修用.pdf',
    pagesize=A4,topMargin=15*mm,bottomMargin=15*mm,leftMargin=15*mm,rightMargin=14*mm,
    title='台詞精緻化シート 法務監修用')
doc.build(st,onFirstPage=footer_maker('台詞精緻化シート（法務監修用）'),onLaterPages=footer_maker('台詞精緻化シート（法務監修用）'))
print('doc1 done')

# ===================================================================
# DOC 2: 解説 Q&A版
# ===================================================================
st=[]
st.append(Paragraph('『サイバークライシス』解説ブロック（Q&A版）',title))
st.append(Paragraph('改訂版5準拠／司会（社員役）の質問に、講師・穴吹衛が答える形式',subt))
st.append(Spacer(1,4))
st.append(Paragraph('○木川精機・会議室（後日）。本編VTRを見た社員と、講師・穴吹衛。司会は津山が務める。',body))

def QA(q, a_lines):
    p=Paragraph('Q　'+q, qst)
    t=Table([[p]],colWidths=[None])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BLUE),('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    st.append(Spacer(1,7)); st.append(t); st.append(Spacer(1,2))
    for sp,tx in a_lines:
        st.append(Paragraph('<b>%s</b>「%s」'%(sp,tx),li))

QA('うちみたいな素人に、そこまで責任を負えと言われても困ります。',[
 ('穴吹','まず安心してください。中小企業に“専門家レベル”は求められていません。求められるのは、誰でもできる「基本」。それを尽くしていたか、が大事なんです'),
 ('津山','基本、というと？'),
 ('穴吹','パスワードの使い回しをやめる、ログインに多要素認証、こまめな更新、バックアップ。IPA――国の機関が、中小企業向けに無料で手引きを出しています（SECURITY ACTION など）'),
])
QA('正直なところ、損害賠償なんて、本当に起きるんですか？',[
 ('穴吹','“自動的に発生する”ものではありません。賠償は、契約違反や過失――つまり注意義務を怠ったか、因果関係はあるか、といった点が争点になります。中小だから必ず、というものではない'),
 ('津山','じゃあ、心配しすぎ？'),
 ('穴吹','いいえ。“広く知られた基本”を、警告がありながら怠っていた場合は、責任を問われるリスクが現実になります。実際、委託先が侵入口になった事例で、責任が問題になったケースもあります。判断はケースごと――不安なら、弁護士や専門機関にご相談を'),
])
QA('難しいことは無理です。何から始めれば？',[
 ('穴吹','3つだけ。①多要素認証を「オン」に ②自動更新を「オン」に ③バックアップを1つ、ネットから切り離して持つ。これだけで、入られにくく・戻せるようになります'),
 ('津山','自分たちでできないときは？'),
 ('穴吹','ITベンダーやMSSPに任せる、IPAやお近くの相談窓口に聞く。“分からないから相談する”は、立派な対策です'),
])
QA('お金がないんです。コストが心配で。',[
 ('穴吹','基本の多くは、月に数万円――無料の手引きや相談先もあります。一方、起きてしまうと、復旧費に、取引先対応に、場合によっては賠償まで。桁が変わります'),
 ('穴吹','対策費は、いちばん安い保険だと思ってください。心配なら、サイバー保険という選択肢もあります'),
])
QA('もし、起きてしまったら？',[
 ('穴吹','隠さないこと。すぐに相談・報告です。IPA、JPCERTコーディネーションセンター、警察（#9110）。そして、身代金は払わない――払っても戻る保証はなく、次を呼びます'),
 ('穴吹','証拠（ログ）を消さずに残し、取引先には“分かること・分からないこと”を分けて正直に。その姿勢が、信頼を守ります'),
])
QA('そもそも、うちが原因だなんて、どうやって分かるんですか？',[
 ('穴吹','正直、自社“だけ”では気づきにくいんです。最初に分かるのは、せいぜい「自社のVPNに不審なログインがある」というところまで'),
 ('津山','取引先に入られた、というのは？'),
 ('穴吹','それは、取引先側の調査で「侵入の起点が御社経由らしい」と分かり、連絡が来て初めて見えてきます。その後、両社のフォレンジック調査やJPCERTの連携で、経路が裏付けられる'),
 ('穴吹','だからこそ、普段からログを残し、おかしな兆候に気づける備えと、すぐ相談できる先を持っておくことが大事なんです'),
])
QA('うちが原因で、電車や銀行や電気が止まったりは？',[
 ('穴吹','そこは誤解されがちですが――電力・鉄道・金融などの重要インフラは、多重化やフェイルセーフで設計されていて、一社の事故で社会のサービスが止まることは、まず起きにくい'),
 ('穴吹','現実に深刻なのは、“自社が止まること”と“取引先に損害を与えること”。等身大のここに、力を入れましょう'),
])
st.append(Spacer(1,6))
st.append(Paragraph('○締め', h1))
st.append(Paragraph('<b>穴吹</b>「“専門家になってください”ではありません。“基本”を、今日から。難しければ、相談していい先がある。それで、足元の穴はふさげます」',li))
st.append(Paragraph('<b>多田</b>「（カメラ目線）――あなたの会社の“穴”、塞ぎませんか」',li))
st.append(Paragraph('※司会・質問は社員役（津山）。賠償・実例の表現は法務監修で確定。窓口/ガイドライン名は最新確認。社名・金額は架空。',note))

doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_解説QA版.pdf',
    pagesize=A4,topMargin=15*mm,bottomMargin=15*mm,leftMargin=17*mm,rightMargin=16*mm,
    title='解説ブロック Q&A版')
doc.build(st,onFirstPage=footer_maker('解説ブロック（Q&A版）'),onLaterPages=footer_maker('解説ブロック（Q&A版）'))
print('doc2 done')

# ===================================================================
# DOC 3: 版マップ／整理（決定方針）
# ===================================================================
st=[]
st.append(Paragraph('『サイバークライシス』稿の整理と決定方針（版マップ）',title))
st.append(Paragraph('どの稿を本線とするか／旧稿の扱い／付随資料と納品の段取り',subt))

st.append(Paragraph('A. 稿の一覧と扱い',h1))
tbl(st,['稿','内容の要点','扱い','理由'],
 [['初稿（0612）','メール1通→全国インフラ崩壊・政府が急襲','撤回','技術的破綻・誇張・法制度誤認'],
  ['改訂版2（信頼経路）','共同ポータル悪用→社会インフラ予防停止','撤回','社会インフラ波及が過大／中小が多業界ポータル運営は非現実的'],
  ['撮影台本ドラフト','改訂版2を作り込み（絵作り/SE）','撤回（参考）','前提が社会インフラのため'],
  ['改訂版3（等身大）','社会インフラ撤回／自社ランサム＋取引先1日停止','参考','正しい縮小だが、賠償リスク未反映'],
  ['改訂版4（損害賠償）','踏み台→取引先大損害→多額賠償','参考','賠償を断定気味＝“煽り”批判の余地'],
  ['改訂版5（責任を正しく描く）rev.1','専門性でなく“基本の放置”／賠償は争点／侵入経路は取引先の指摘で判明','★本線（決定方針）','断定回避・他人事化回避＋経路特定を現実化'],
  ['台詞精緻化シート','＃5弁護士台詞ほかの監修用案','付属（必須）','放送には法務監修が前提'],
  ['解説Q&A版','改訂版5解説のQ&A形式','付属（任意採用）','視聴者の反論に直接回答']],
 widths=[34*mm,None,26*mm,46*mm])

st.append(Paragraph('B. 付随資料（絵コンテ・登場人物設定書・尺ロック表）の扱い',h1))
for t in ['いずれも旧稿（社会インフラ系）準拠のため、<b>改訂版5の場面に合わせて差し替えが必要</b>。',
          '特に：絵コンテの“信頼の線”モンタージュ→“取引先と直結するVPN”の見せ方に変更。＃5は「会見」でなく「賠償協議（弁護士同席）」に。',
          '登場人物：<b>弁護士（メイユー側）</b>を追加。社会インフラ各社（鉄道/電力/銀行の声）は不要に。',
          '尺ロック表：＃4踏み台・＃5賠償協議の配分に更新（合計7:00は維持）。',
          '＃4は「自社単独で断定」でなく<b>取引先の指摘→フォレンジック/JPCERT連携で判明</b>に修正済み（rev.1）。絵コンテ＃4もこの“指摘されて分かる”流れに合わせる。']:
    st.append(Paragraph('・'+t,li))
st.append(Paragraph('※ご希望あれば、改訂版5準拠で絵コンテ・設定書・尺ロック表を作り直します。',note))

st.append(Paragraph('C. 放送前 最終チェック',h1))
for t in ['冒頭・末尾に「フィクション」表示／社名・金額は架空',
          '<b>技術監修</b>（侵入経路・ランサム挙動・基本対策の妥当性）',
          '<b>法務監修</b>（注意義務・損害賠償の表現、実例の事実関係、身代金不払いの言い切り可否）',
          '社会インフラを描いていないか（誤認防止）',
          '相談窓口・ガイドライン名の最新確認（IPA／JPCERT/CC／SECURITY ACTION／#9110）',
          '“基本”の提示が「実行可能・安価・相談先あり」になっているか']:
    st.append(Paragraph('☐ '+t,li))

st.append(Paragraph('D. 納品・PR反映の段取り',h1))
for t in ['本リポジトリ（PR #1）に全稿・全PDFを集約。<b>本線＝改訂版5</b>、旧稿は検討過程として保管。',
          'GitHubへの反映は、最新一式を含む<b>bundle</b>で受領→お手元で push が確実（パッチ未着問題の回避）。',
          'または、セッションに書き込み権限を付与いただければ当方から直接 push 可能。']:
    st.append(Paragraph('・'+t,li))

doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_版マップと決定方針.pdf',
    pagesize=A4,topMargin=15*mm,bottomMargin=15*mm,leftMargin=15*mm,rightMargin=14*mm,
    title='版マップと決定方針')
doc.build(st,onFirstPage=footer_maker('版マップと決定方針'),onLaterPages=footer_maker('版マップと決定方針'))
print('doc3 done')
