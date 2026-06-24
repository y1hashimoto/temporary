# -*- coding: utf-8 -*-
"""改訂版5 rev.1 準拠の簡易絵コンテ。社会インフラ描写を排し、VPN直結・取引先からの一報・賠償協議・コスト対比を作画。"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
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
title=S('t',fontSize=16.5,leading=21)
subt=S('s',fontSize=9.3,leading=13,textColor=GREY)
cap=S('c',fontSize=8.6,leading=11.6)
capb=S('cb',fontSize=9,leading=12,textColor=NAVY)
small=S('sm',fontSize=8,leading=10.6,textColor=GREY)

W,H=72*mm,40*mm
def frame():
    d=Drawing(W,H); d.add(Rect(0,0,W,H,strokeColor=INK,strokeWidth=1,fillColor=colors.white)); return d
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
    d.add(String(x+w/2,y-9,label,fontName='JP',fontSize=6.3,fillColor=GREY,textAnchor='middle'))
def keyicon(d,x,y,col=ACC):
    d.add(Circle(x,y,2.2,strokeColor=col,fillColor=None,strokeWidth=0.9))
    d.add(Line(x+2,y,x+9,y,strokeColor=col,strokeWidth=0.9))
    d.add(Line(x+9,y,x+9,y-2.5,strokeColor=col,strokeWidth=0.9))
    d.add(Line(x+6,y,x+6,y-2,strokeColor=col,strokeWidth=0.9))

def P1():
    d=frame()
    d.add(Line(4,12,W-4,12,strokeColor=INK,strokeWidth=0.8))
    d.add(Ellipse(W/2,12,9,3.2,strokeColor=INK,fillColor=INK))
    for x in (W/2-14,W/2+15,W/2-24): stick(d,x,20)
    d.add(String(8,H-10,'C1 俯瞰：街の穴を人が避ける（朝）',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def P2():
    d=frame()
    d.add(Rect(8,H/2-9,16,18,strokeColor=INK,strokeWidth=1,fillColor=colors.HexColor('#f0ead6')))
    for i in range(3): d.add(Line(10,H/2-5+i*5,22,H/2-5+i*5,strokeColor=GOLD,strokeWidth=0.7))
    d.add(String(16,H/2-15,'木川精機',fontName='JP',fontSize=6,fillColor=GREY,textAnchor='middle'))
    bld(d,W-26,H/2-9,18,18,'メイユー自動車',SKY)
    d.add(Line(24,H/2,W-26,H/2,strokeColor=ACC,strokeWidth=1.6))
    keyicon(d,(24+W-26)/2-4,H/2+5)
    d.add(String((24+W-26)/2,H/2+11,'VPN 直結',fontName='JP',fontSize=6.5,fillColor=ACC,textAnchor='middle'))
    d.add(String(8,H-10,'C(新) 取引先とVPNで“直結”＝信頼の通路',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def P3():
    d=frame()
    # door
    d.add(Rect(10,8,20,26,strokeColor=INK,strokeWidth=1,fillColor=colors.HexColor('#eef2f7')))
    d.add(Circle(26,20,1.2,strokeColor=INK,fillColor=INK))  # knob
    # keys left outside
    items=[('初期PWのカメラ',H-12),('付箋のID',H/2),('MFA無しのVPN',14)]
    for label,yy in items:
        keyicon(d,40,yy)
        d.add(String(52,yy-1.5,label,fontName='JP',fontSize=6.3,fillColor=ACC))
    d.add(String(8,H-10,'＃3 二重(三重)の穴＝鍵を外に置きっぱなし',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def P4():
    d=frame()
    stick(d,18,16)
    d.add(Rect(20,22,3,6,strokeColor=INK,strokeWidth=0.7,fillColor=colors.HexColor('#dfe6ee')))  # phone
    # speech bubble
    d.add(Rect(30,18,W-36,14,strokeColor=SKY,strokeWidth=0.9,fillColor=colors.HexColor('#eef5fb')))
    d.add(Polygon([30,24,26,22,30,20],strokeColor=SKY,fillColor=colors.HexColor('#eef5fb')))
    d.add(String(33,26,'弊社の侵入の起点が',fontName='JP',fontSize=6.6,fillColor=INK))
    d.add(String(33,20.5,'御社経由の可能性が高い',fontName='JP',fontSize=6.6,fillColor=INK))
    d.add(String(8,H-10,'＃4 取引先からの一報で“判明”（電話）',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def P5():
    d=frame()
    d.add(Rect(14,14,W-28,6,strokeColor=INK,strokeWidth=0.9,fillColor=colors.HexColor('#dfe6ee')))  # table
    stick(d,22,22); stick(d,32,22)            # 木川側
    stick(d,W-22,22); stick(d,W-32,22)        # メイユー+弁護士
    d.add(Rect(W/2-8,21,16,7,strokeColor=ACC,strokeWidth=0.8,fillColor=colors.white))
    d.add(String(W/2,23.2,'損害賠償',fontName='JP',fontSize=5.6,fillColor=ACC,textAnchor='middle'))
    d.add(String(22,9,'木川・多田',fontName='JP',fontSize=5.8,fillColor=GREY,textAnchor='middle'))
    d.add(String(W-27,9,'メイユー＋弁護士',fontName='JP',fontSize=5.8,fillColor=GREY,textAnchor='middle'))
    d.add(String(8,H-10,'＃5 賠償“協議”（弁護士同席）＝クライマックス',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def P6():
    d=frame()
    fx=W/2
    d.add(Polygon([fx-6,12,fx+6,12,fx,26],strokeColor=INK,fillColor=colors.HexColor('#dfe6ee')))  # fulcrum
    # beam tilted: left up, right down
    lx,ly=fx-22,30; rx,ry=fx+22,20
    d.add(Line(lx,ly,rx,ry,strokeColor=INK,strokeWidth=1.2))
    d.add(Line(fx,26,fx,(ly+ry)/2,strokeColor=INK,strokeWidth=0.8))
    # pans
    d.add(Rect(lx-9,ly,18,3,strokeColor=INK,strokeWidth=0.7,fillColor=colors.HexColor('#eaf5ec')))
    d.add(Rect(rx-9,ry,18,3,strokeColor=INK,strokeWidth=0.7,fillColor=colors.HexColor('#fdecea')))
    d.add(String(lx,ly+6,'対策 月数万円',fontName='JP',fontSize=6.2,fillColor=colors.HexColor('#1e7d34'),textAnchor='middle'))
    d.add(String(rx,ry-7,'復旧＋賠償',fontName='JP',fontSize=6.6,fillColor=ACC,textAnchor='middle'))
    d.add(String(8,H-10,'＃7 コスト対比＝対策は一番安い保険',fontName='JP',fontSize=7,fillColor=NAVY))
    return d
def P7():
    d=frame()
    d.add(Rect(0,0,W,H,strokeColor=INK,strokeWidth=1,fillColor=colors.HexColor('#10141c')))
    d.add(Line(4,12,W-4,12,strokeColor=colors.HexColor('#5a6470'),strokeWidth=0.8))
    d.add(Ellipse(W/2,12,9,3.2,strokeColor=colors.HexColor('#5a6470'),fillColor=colors.black))
    stick(d,W/2-3,20,col=colors.HexColor('#e6e6e6'))
    d.add(PolyLine([W/2-6,13,W/2,18,W/2+8,13],strokeColor=GOLD,strokeWidth=1))
    d.add(String(8,H-10,'＃8 夜：穴を避けず、踏み外さずまたぐ（C1と対）',fontName='JP',fontSize=7,fillColor=colors.HexColor('#cfd6df')))
    return d

PANELS=[
 (P1,'C1 / ＃1','S/俯瞰','街の穴を人々が避ける。多田も避ける（朝）。','穴のM「目に見える穴は、避けて通れる」'),
 (P2,'＃1 / 点描','図/合成','木川精機と取引先メイユーが<b>VPNで直結</b>。社会インフラは出さない。','穴のM「その穴は“つながった相手”へ続いている」'),
 (P3,'＃3','寄り/小物','カメラ初期PW・付箋ID・MFA無し＝<b>鍵を外に置きっぱなし</b>。','多田「全部、“やりましょう”と言った基本のところだ」'),
 (P4,'＃4','バストアップ','自社では“VPNに不審ログイン”まで。<b>取引先の一報で経路が判明</b>。','メイユー情シス「起点が御社経由の可能性が高い」'),
 (P5,'＃5','会議/引き','弁護士同席の<b>賠償“協議”</b>。断定でなく争点として。','弁護士「“専門家であれ”とは申しません。基本を怠ったかが争点」'),
 (P6,'＃7','図/概念','月数万円の対策 ≪ 復旧＋賠償。<b>天秤で対比</b>。','木川「あの基本……いくらだった」／多田「月、数万円です」'),
 (P7,'C/＃8','夜・ローアングル','朝避けた穴を、今度は避けず踏み外さずまたぐ。','穴のM「専門家でなくても、ふさげる。あなたにできることは？」'),
]

story=[]
story.append(Paragraph('『サイバークライシス』簡易絵コンテ（改訂版5 rev.1 準拠）',title))
story.append(Paragraph('社会インフラ描写は不採用。VPN直結／取引先からの一報／賠償協議／コスト対比を主要カットに。※作画はラフ・スキーマ。',subt))
story.append(Spacer(1,5))
rows=[[Paragraph('画（ラフ）',S('h',fontSize=9,textColor=colors.white)),
       Paragraph('カット/サイズ',S('h2',fontSize=9,textColor=colors.white)),
       Paragraph('内容（ト書き）/ セリフ',S('h3',fontSize=9,textColor=colors.white))]]
for fn,cid,size,act,serif in PANELS:
    rows.append([fn(),Paragraph('<b>%s</b><br/><font size=8 color="#555555">%s</font>'%(cid,size),capb),
                 Paragraph('<b>ト書き：</b>%s<br/><b>言：</b>%s'%(act,serif),cap)])
t=Table(rows,colWidths=[W+4*mm,24*mm,None],repeatRows=1)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#99a0b0')),
    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
    ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story.append(t); story.append(Spacer(1,5))
story.append(Paragraph('※旧稿の「信頼の線が鉄道・電力・銀行へ」モンタージュ、駅・ATM等は不採用。C1（朝）とP7（夜）の対構図は維持。',small))

def footer(c,doc):
    c.saveState(); c.setFont('JP',8); c.setFillColor(GREY)
    c.drawCentredString(A4[0]/2,10*mm,'%d'%doc.page)
    c.drawString(16*mm,10*mm,'『サイバークライシス』絵コンテ（改訂版5 rev.1 準拠）')
    c.restoreState()
doc=SimpleDocTemplate('/home/user/temporary/サイバークライシス_絵コンテ_改訂版5準拠.pdf',
    pagesize=A4,topMargin=14*mm,bottomMargin=15*mm,leftMargin=12*mm,rightMargin=12*mm,
    title='サイバークライシス 絵コンテ 改訂版5準拠')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('storyboard5 done')
