from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'package' / 'dashboard'
OUT.mkdir(parents=True, exist_ok=True)
im = Image.new('L', (1072, 1448), 255)
d = ImageDraw.Draw(im)
fonts = {'cn': 'C:/Windows/Fonts/simsun.ttc', 'num': 'C:/Windows/Fonts/arial.ttf', 'serif': 'C:/Windows/Fonts/georgia.ttf', 'italic': 'C:/Windows/Fonts/georgiai.ttf'}
def text(x,y,s,size=28,font='cn',align='left',color=0):
    f=ImageFont.truetype(fonts[font],size)
    width=d.textlength(s,font=f)
    if align=='right': x-=width
    if align=='center': x-=width/2
    assert x >= 0 and x+width <= 1072, (s,x,width)
    d.text((x,y),s,font=f,fill=color,anchor='lt')
def rule(y,width=2): d.line((58,y,1014,y),fill=0,width=width)
def centered(box,s,size=28,font='cn',color=0):
    f=ImageFont.truetype(fonts[font],size)
    l,t,r,b=d.textbbox((0,0),s,font=f)
    x0,y0,x1,y1=box
    assert r-l <= x1-x0 and b-t <= y1-y0, (s,box)
    x=(x0+x1-(r-l))/2-l
    y=(y0+y1-(b-t))/2-t
    d.text((round(x),round(y)),s,font=f,fill=color)
def diamond(x,y,r=5):
    d.polygon([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],fill=0)

def stack(box, rows, gap, align='center'):
    """Space visible glyph bounds equally, independent of font ascenders."""
    x0,y0,x1,y1=box
    measured=[]
    for s,size,font in rows:
        f=ImageFont.truetype(fonts[font],size)
        l,t,r,b=d.textbbox((0,0),s,font=f)
        measured.append((s,f,l,t,r,b))
    height=sum(b-t for _,_,l,t,r,b in measured)+gap*(len(rows)-1)
    assert height <= y1-y0
    y=round((y0+y1-height)/2)
    for s,f,l,t,r,b in measured:
        assert r-l <= x1-x0
        x=x1-(r-l) if align=='right' else (x0+x1-(r-l))/2
        d.text((round(x-l),y-t),s,font=f,fill=0)
        y+=b-t+gap
def star(x,y,r=10):
    d.polygon([(x,y-r),(x+2,y-2),(x+r,y),(x+2,y+2),(x,y+r),(x-2,y+2),(x-r,y),(x-2,y-2)],fill=0)

# A compact double-peak seal with a crescent: decorative, not a live moon reading.
d.ellipse((497,62,585,150),outline=0,width=2)
d.arc((504,69,578,143),205,335,fill=0,width=1)
d.polygon([(509,129),(530,94),(543,114),(555,97),(575,129)],fill=0)
d.line([(520,112),(530,94),(538,106)],fill=255,width=2)
d.line([(549,108),(555,97),(562,110)],fill=255,width=2)
d.ellipse((543,73,560,90),fill=0)
d.ellipse((549,70,564,85),fill=255)
star(489,102,5)
star(595,102,5)
diamond(541,162,4)

# Keep the upper 64 pixels free for the Kindle system status bar.
text(58,74,'GRE · DAILY WORD',20,'serif')
text(58,105,'tenacious',54,'serif')
text(58,165,'/təˈneɪʃəs/',21,'num')
text(181,165,'adj. 坚韧的；执着的',21)
ANNIVERSARY_BOX=(650,64,1014,194)
ANNIVERSARY_SIZES=(28,48,20)
ANNIVERSARY_GAP=12
stack(ANNIVERSARY_BOX,[
    ('Surreal, but nice',ANNIVERSARY_SIZES[0],'serif'),
    ('1,972 days',ANNIVERSARY_SIZES[1],'serif'),
    ('since 2021.04.24',ANNIVERSARY_SIZES[2],'num')],gap=ANNIVERSARY_GAP,align='right')
rule(201,2)
rule(207,1)
# Shared top and bottom anchors keep the clock and calendar visually balanced.
centered((58,242,614,411),'09:41',173,'serif')
centered((58,413,614,445),'白露时节  /  下一节气 · 秋分',27)
centered((58,454,614,481),'丙午年 · 农历八月初七',24)
# English-only date plaque inspired by the Double R Diner roadside sign.
plaque=[(694,242),(998,242),(1014,258),(1014,462),(998,478),(694,478),(678,462),(678,258)]
d.polygon(plaque,fill=255,outline=0,width=3)
inner=[(699,250),(993,250),(1006,263),(1006,457),(993,470),(699,470),(686,457),(686,263)]
d.line(inner+[inner[0]],fill=0,width=1)
d.rectangle((698,259,994,316),fill=0)
centered((709,259,817,316),'RR',44,'italic',color=255)
centered((821,259,985,316),'DINER',29,'serif',color=255)
centered((702,323,854,423),'17',96,'serif')
centered((854,332,992,367),'THURSDAY',19,'serif')
centered((854,373,992,407),'SEPT.',24,'serif')
d.line((705,425,987,425),fill=0,width=1)
centered((699,428,993,464),'SEPTEMBER · 2026',22,'serif')

# Permanent quotation with an outlined steaming diner coffee cup.
quote='A damn fine cup of coffee.'
quote_font=ImageFont.truetype(fonts['italic'],38)
quote_width=d.textlength(quote,font=quote_font)
group_width=84+quote_width
cup_x=round((1072-group_width)/2)
cup_y=520
d.rounded_rectangle((cup_x,cup_y,cup_x+46,cup_y+30),radius=7,outline=0,width=3)
d.rectangle((cup_x+2,cup_y,cup_x+44,cup_y+10),fill=255)
d.line((cup_x,cup_y,cup_x+46,cup_y),fill=0,width=3)
d.arc((cup_x+38,cup_y+3,cup_x+62,cup_y+24),-90,90,fill=0,width=3)
d.line((cup_x-7,cup_y+37,cup_x+56,cup_y+37),fill=0,width=3)
for dx in (9,23,37):
    d.line([(cup_x+dx,cup_y-8),(cup_x+dx-3,cup_y-14),(cup_x+dx+2,cup_y-20),(cup_x+dx,cup_y-27)],fill=0,width=2)
text(cup_x+84,514,quote,38,'italic')
d.line((68,533,cup_x-35,533),fill=0,width=1)
diamond(68,533,4)
quote_right=round(cup_x+84+quote_width)
d.line((quote_right+26,533,1004,533),fill=0,width=1)
diamond(1004,533,4)
rule(588,1)
rule(594,2)
# Symmetrical diner-menu notes; forecast location remains Beijing Haidian.
for x0,x1,label,condition,temp,advice in [
    (58,500,'TODAY','多云','18° / 27°','早晚微凉，带件薄外套'),
    (572,1014,'TOMORROW','小雨','15° / 22°','记得带伞，降温添衣')]:
    stack((x0,625,x1,834),[
        (label,24,'serif'),(condition,26,'cn'),
        (temp,64,'serif'),(advice,25,'cn')],gap=24)
d.line((536,638,536,714),fill=0,width=1)
diamond(536,735,4)
d.line((536,756,536,832),fill=0,width=1)
rule(866,1)
rule(872,2)
# All three header elements share one optical center, including actual glyph ink.
todo_font=ImageFont.truetype(fonts['serif'],38)
todo_bbox=d.textbbox((0,0),'TO DO',font=todo_font)
centered((58,896,58+todo_bbox[2]-todo_bbox[0],946),'TO DO',38,'serif')
centered((943,896,1014,946),'07 条',23)
star(536,921,8)
d.line((497,921,518,921),fill=0,width=1)
d.line((554,921,575,921),fill=0,width=1)
tasks=[('整理项目方案','11:00 前'),('回复合作方邮件','上午'),('给家里打个电话','午休时'),('背一组 GRE 单词','15:00'),('预约周末体检','今天'),('取快递，顺路买牛奶','下班路上'),('散步半小时','晚饭后')]
for i,(task,due) in enumerate(tasks):
    y=975+i*48
    centered((58,y,94,y+34),f'{i+1:02}',25,'serif')
    task_font=ImageFont.truetype(fonts['cn'],29)
    task_width=d.textbbox((0,0),task,font=task_font)[2]
    centered((126,y,126+task_width,y+34),task,29)
rule(1330,1)
text(58,1364,'排版测试 · 示例数据 · 60 秒后退出',23)

cats=Image.new('L',(54,24),255)
cd=ImageDraw.Draw(cats)
def cat(offset,black):
    ink=23;fur=36 if black else 222;stripe=102;inner=170
    def r(x,y,w,h,c): cd.rectangle((offset+x,y,offset+x+w-1,y+h-1),fill=c)
    for q in [(3,5,2,4),(5,6,2,3),(7,7,2,2),(19,5,2,4),(17,6,2,3),(15,7,2,2),(3,8,18,10),(1,10,22,6),(5,18,14,2),(8,20,8,1)]:r(*q,ink)
    for q in [(4,7,1,3),(5,8,2,2),(7,8,2,2),(19,7,1,3),(17,8,2,2),(15,8,2,2),(4,9,16,8),(2,11,20,4),(6,17,12,2)]:r(*q,fur)
    r(5,8,1,1,inner);r(18,8,1,1,inner)
    if not black:
        for q in [(10,9,1,3),(12,9,1,4),(14,9,1,3),(3,13,3,1),(18,13,3,1),(4,15,2,1),(18,15,2,1)]:r(*q,stripe)
    r(7,12,2,2,255 if black else ink);r(16,12,2,2,255 if black else ink)
    r(9,15,7,3,238 if black else 250);r(11,14,3,2,238 if black else 250)
    for q in [(11,15,2,1),(12,16,1,1),(10,17,2,1),(13,17,2,1)]:r(*q,ink)
    r(0,14,4,1,136 if black else stripe);r(20,14,4,1,136 if black else stripe)
cat(1,True);cat(29,False)
im.paste(cats.resize((108,48),Image.Resampling.NEAREST),(906,1357))
im.save(OUT/'preview.png',optimize=True)
im.resize((536,724),Image.Resampling.LANCZOS).save(ROOT/'preview-review.png')
im.crop((658,222,1034,482)).resize((564,390),Image.Resampling.LANCZOS).save(ROOT/'calendar-detail.png')
print('Built 1072 x 1448 grayscale screen:',OUT/'preview.png')
