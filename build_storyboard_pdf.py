# -*- coding: utf-8 -*-
"""簡易絵コンテ（schematic storyboard）。主要カットを図形で作画。"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, String, Polygon, Ellipse, PolyLine
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('JP','/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf'))
NAVY=colors.HexColor('#2b3a55'); GREY=colors.HexColor('#555555'); INK=colors.HexColor('#1a1a1a')
ACC=colors.HexColor('#c0392b'); SKY=colors.HexColor('#2e6fb0'); GOLD=colors.HexColor('#caa23a')

def S(n,**k):
    b=dict(fontName='JP',fontSize=9,leading=12.5,textColor=INK,alignment=TA_LEFT,spaceAfter=1)
    b.update(k); return ParagraphStyle(n,**b)
title=S('t',fontSize=17,leading=21,alignment=TA_CENTER)
subt =S('s',fontSize=9.5,leading=13,alignment=TA_CENTER,textColor=GREY)
cap  =S('c',fontSize=8.6,leading=11.5)
capb =S('cb',fontSize=9,leading=12,textColor=NAVY)
small=S('sm',fontSize=8,leading=10.5,textColor=GREY)

W,H=72*mm,40*mm  # 16:9 picture box

def frame():
    d=Drawing(W,H)
    d.add(Rect(0,0,W,H,strokeColor=INK,strokeWidth=1,fillColor=colors.white))
    return d
def stick(d,x,y,s=5,col=INK):
    d.add(Circle(x,y+s*1.4,s*0.5,strokeColor=col,fillColor=None,strokeWidth=0.8))
    d.add(Line(x,y+s*0.9,x,y-s*0.6,strokeColor=col,strokeWidth=0.8))
    d.add(Line(x,y+s*0.4,x-s*0.6,y-s*0.1,strokeColor=col,strokeWidth=0.8))
    d.add(Line(x,y+s*0.4,x+s*0.6,y-s*0.1,strokeColor=col,strokeWidth=0.8))
    d.add(Line(x,y-s*0.6,x-s*0.5,y-s*1.4,strokeColor=col,strokeWidth=0.8))
    d.add(Line(x,y-s*0.6,x+s*0.5,y-s*1.4,strokeColor=col,strokeWidth=0.8))
def bld(d,x,y,w,h,label,col=INK):
    d.add(Rect(x,y,w,h,strokeColor=col,strokeWidth=0.9,fillColor=colors.HexColor('#eef2f7')))
    for i in range(1,int(h//6)):
        d.add(Line(x+2,y+i*6,x+w-2,y+i*6,strokeColor=colors.HexColor('#b9c4d2'),strokeWidth=0.4))
    d.add(String(x+w/2,y-9,label,fontName='JP',fontSize=6.5,fillColor=GREY,textAnchor='middle'))

# ---- panel drawings ----
def C1():
    d=frame()
    d.add(Line(4,12,W-4,12,strokeColor=INK,strokeWidth=0.8))       # road
    d.add(Ellipse(W/2,12,9,3.2,strokeColor=INK,fillColor=INK))      # hole
    for x in (W/2-14,W/2+15,W/2-24): stick(d,x,20)
    d.add(PolyLine([W/2-9,22,W/2-3,16,W/2+3,16,W/2+9,22],strokeColor=GREY,strokeWidth=0.6))  # avoid arc
    d.add(String(8,H-10,'C1 俯瞰：街の穴を人が避ける',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def C4():
    d=frame()
    # server box left
    d.add(Rect(6,H/2-9,16,18,strokeColor=INK,strokeWidth=1,fillColor=colors.HexColor('#f0ead6')))
    for i in range(3): d.add(Line(8,H/2-5+i*5,20,H/2-5+i*5,strokeColor=GOLD,strokeWidth=0.7))
    d.add(String(14,H/2-15,'KIGAWA-Link',fontName='JP',fontSize=6,fillColor=GREY,textAnchor='middle'))
    bld(d,W-22,H-20,16,12,'鉄道 保守倉庫',SKY)
    bld(d,W-22,H/2-6,16,12,'電力 保守受付',SKY)
    bld(d,W-22,8,16,12,'銀行 設備管理',SKY)
    for ty in (H-14,H/2,14):
        d.add(Line(22,H/2,W-22,ty,strokeColor=ACC,strokeWidth=1.4))
        d.add(Circle((22+W-22)/2,(H/2+ty)/2,1.3,strokeColor=None,fillColor=ACC))
    d.add(String(8,H-9,'C4–C8 “信頼の線”が各社へ（合成）',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def C22():
    d=frame()
    d.add(Rect(8,8,18,H-16,strokeColor=INK,strokeWidth=1,fillColor=colors.HexColor('#1f2733')))  # rack
    import random
    for i in range(7):
        cy=12+i*4
        c=GOLD if i%3 else ACC
        d.add(Circle(12,cy,1,strokeColor=None,fillColor=c))
        d.add(Circle(16,cy,1,strokeColor=None,fillColor=colors.HexColor('#3fae6b')))
    # log lines
    d.add(Rect(32,H/2-12,W-40,24,strokeColor=GREY,strokeWidth=0.6,fillColor=colors.HexColor('#0f1115')))
    for i in range(4):
        col=ACC if i==2 else colors.HexColor('#8fd19e')
        d.add(String(35,H/2+6-i*6,'login %02d:%02d  admin'%( (2+i),(11+i*7)%60),fontName='JP',fontSize=5.4,fillColor=col))
    d.add(String(8,H-9,'C22–C23 深夜の不審ログイン（潜伏）',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def C26():
    d=frame()
    d.add(Line(4,12,W-4,12,strokeColor=INK,strokeWidth=0.7))
    for i,x in enumerate((16,34,52,W-14)):
        d.add(Rect(x-6,14,12,8,strokeColor=INK,strokeWidth=0.8,fillColor=colors.HexColor('#eef2f7')))  # desk phones
        d.add(Ellipse(x,22,5,2,strokeColor=INK,fillColor=None))  # handset
        # ring marks
        d.add(String(x-7,26,'))',fontName='JP',fontSize=7,fillColor=ACC))
        d.add(String(x+3,26,'((',fontName='JP',fontSize=7,fillColor=ACC))
    stick(d,W/2,30)
    d.add(String(8,H-9,'C26–C27 電話が一斉に鳴る',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def C33():
    d=frame()
    for i in range(4):
        x=12+i*15
        closed = i in (1,2)
        d.add(Rect(x,14,11,16,strokeColor=INK,strokeWidth=0.9,fillColor=colors.HexColor('#eef2f7')))
        if closed:
            d.add(Line(x,14,x+11,30,strokeColor=ACC,strokeWidth=1.2))
            d.add(Line(x+11,14,x,30,strokeColor=ACC,strokeWidth=1.2))
            d.add(String(x+5.5,9,'閉鎖',fontName='JP',fontSize=5.5,fillColor=ACC,textAnchor='middle'))
    stick(d,W-12,22)
    d.add(String(8,H-9,'C33 改札の一部閉鎖／駅員が手動案内',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def C34():
    d=frame()
    for i in range(3):
        x=14+i*18
        d.add(Rect(x,12,13,20,strokeColor=INK,strokeWidth=0.9,fillColor=colors.HexColor('#eef2f7')))
        d.add(Rect(x+2,24,9,5,strokeColor=GREY,strokeWidth=0.5,fillColor=colors.white))  # screen
        d.add(String(x+6.5,7,'ATM',fontName='JP',fontSize=5.5,fillColor=GREY,textAnchor='middle'))
        if i!=1:
            d.add(Rect(x-1,18,15,6,strokeColor=ACC,strokeWidth=0.7,fillColor=colors.HexColor('#fde8e3')))
            d.add(String(x+6.5,19.5,'メンテ中',fontName='JP',fontSize=5,fillColor=ACC,textAnchor='middle'))
    d.add(String(8,H-9,'C34 一部ATM休止（勘定系は無事）',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def C44():
    d=frame()
    d.add(Rect(W/2-14,12,28,9,strokeColor=INK,strokeWidth=0.9,fillColor=colors.HexColor('#dfe6ee')))  # podium
    # bowing figure
    x,y=W/2,24
    d.add(Circle(x,y+3,2,strokeColor=INK,fillColor=None,strokeWidth=0.8))
    d.add(Line(x,y+1,x+5,y-2,strokeColor=INK,strokeWidth=0.8))  # bent torso
    d.add(Line(x+5,y-2,x+5,y-7,strokeColor=INK,strokeWidth=0.8))
    for sx,sy in ((10,H-10),(20,H-16),(W-12,H-9),(W-22,H-16)):
        d.add(Polygon([sx,sy+3,sx+1,sy+1,sx+3,sy,sx+1,sy-1,sx,sy-3,sx-1,sy-1,sx-3,sy,sx-1,sy+1],
                      strokeColor=None,fillColor=GOLD))  # flash stars
    d.add(String(8,H-9 if False else 9,'C44 記者会見：木川が謝罪／フラッシュ',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def C47():
    d=frame()
    d.add(Rect(0,0,W,H,strokeColor=INK,strokeWidth=1,fillColor=colors.HexColor('#10141c')))  # night
    d.add(Line(4,12,W-4,12,strokeColor=colors.HexColor('#5a6470'),strokeWidth=0.8))
    d.add(Ellipse(W/2,12,9,3.2,strokeColor=colors.HexColor('#5a6470'),fillColor=colors.black))
    # figure stepping over
    stick(d,W/2-3,20,col=colors.HexColor('#e6e6e6'))
    d.add(PolyLine([W/2-6,13,W/2,18,W/2+8,13],strokeColor=GOLD,strokeWidth=1))  # stride over hole
    d.add(String(8,H-9,'C47 夜：今度は“穴”を避けず、踏み外さずまたぐ',fontName='JP',fontSize=7,fillColor=colors.HexColor('#cfd6df')))
    return d

PANELS=[
 (C1,'C1 / ＃1','S/俯瞰','街の穴を人々が避けて通る。多田も避ける。','穴のM「目に見える穴なら、誰だって避ける」／SE:雑踏・M:静パッド'),
 (C4,'C4–C8 / ＃1','合成/MG','配信画面→“信頼の線”が鉄道・電力・銀行の保守側へ枝分かれ。','穴のM「見えない穴は“信頼”を伝ってつながる」'),
 (C22,'C22–C23 / ＃4','INSERT/寄り','無人サーバ室。深夜の海外IPログイン成功→管理者権限。派手にしない。','T「――数週間前」／SE:秒針のみ・M:不穏'),
 (C26,'C26–C27 / ＃5','フロア/横移動','共有ファイルが開けない→電話が一本、やがて一斉に鳴る。','SE:電話ベル多重／社員の困惑'),
 (C33,'C33 / ＃6','駅/引き','自動改札の一部閉鎖。駅員が拡声器で手動案内。運行は減便継続。','アナ「保守・駅務系を予防的に停止」'),
 (C34,'C34 / ＃6','ATM/寄り','数台に「メンテナンス中」。利用者は隣店舗へ。勘定系は無事。','アナ「設備保守の都合で一部ATM休止」'),
 (C44,'C44 / ＃8','会見/正面','フラッシュ。木川が深く一礼。','木川「安全が確認できるまでKIGAWA-Linkを停止します」'),
 (C47,'C47 / ＃8','夜・街/ローアングル','＃1と対の画。朝避けた穴を、今度は避けず踏み外さずまたぐ。','多田M「気づいて、声を上げて、つないだ」'),
]

story=[]
story.append(Paragraph('『サイバークライシス』簡易絵コンテ（主要カット）',title))
story.append(Paragraph('信頼経路版・作り込み稿より抜粋／※作画は配置・意図を示すスキーマ。本作画前のラフ。',subt))
story.append(Spacer(1,5))

rows=[]
hdr=[Paragraph('画（ラフ）',S('h',fontSize=9,textColor=colors.white)),
     Paragraph('カット/尺・サイズ',S('h2',fontSize=9,textColor=colors.white)),
     Paragraph('内容（ト書き）/ セリフ・SE',S('h3',fontSize=9,textColor=colors.white))]
rows.append(hdr)
for fn,cid,size,act,serif in PANELS:
    pic=fn()
    meta=Paragraph('<b>%s</b><br/><font size=8 color="#555555">%s</font>'%(cid,size),capb)
    txt=Paragraph('<b>ト書き：</b>%s<br/><b>音/言：</b>%s'%(act,serif),cap)
    rows.append([pic,meta,txt])
t=Table(rows,colWidths=[W+4*mm,26*mm,None],repeatRows=1)
ts=[('BACKGROUND',(0,0),(-1,0),NAVY),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#99a0b0')),
    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
    ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]
t.setStyle(TableStyle(ts))
story.append(t)
story.append(Spacer(1,5))
story.append(Paragraph('※C4–C8の「信頼の線」は本作品の“画の顔”。モーショングラフィックスで、線が増殖→各社の端末アイコンが赤く反転、までを一連で。'
    '※C1とC47は朝/夜の対構図でブックエンドに。',small))

def footer(c,doc):
    c.saveState(); c.setFont('JP',8); c.setFillColor(GREY)
    c.drawCentredString(A4[0]/2,10*mm,'%d'%doc.page)
    c.drawString(16*mm,10*mm,'『サイバークライシス』簡易絵コンテ')
    c.restoreState()
doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_絵コンテ_主要カット.pdf',
    pagesize=A4,topMargin=14*mm,bottomMargin=15*mm,leftMargin=12*mm,rightMargin=12*mm,
    title='サイバークライシス 簡易絵コンテ')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('done')
