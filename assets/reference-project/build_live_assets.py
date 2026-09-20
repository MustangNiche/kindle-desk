"""Offline assets for the bounded Kindle clock/partial-refresh trial."""
import contextlib
import io
import json
import math
import runpy
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'package/dashboard/live'
for folder in ('clock','day','steam'):
    (OUT/folder).mkdir(parents=True,exist_ok=True)
with contextlib.redirect_stdout(io.StringIO()):
    s=runpy.run_path(str(ROOT/'build_preview.py'))
base=s['im'].copy()
d=ImageDraw.Draw(base)
d.rectangle((58,1350,860,1410),fill=255)
d.text((58,1364),'离线动态测试 · 天气/待办为示例 · 3分钟退出',
       font=ImageFont.truetype(s['fonts']['cn'],22),fill=0,anchor='lt')
base.save(OUT/'base.png')

def center(image,box,value,size,font='serif'):
    draw=ImageDraw.Draw(image)
    f=ImageFont.truetype(s['fonts'][font],size)
    l,t,r,b=draw.textbbox((0,0),value,font=f)
    x0,y0,x1,y1=box
    assert r-l<=x1-x0 and b-t<=y1-y0,(value,box)
    draw.text((round((x0+x1-r+l)/2-l),round((y0+y1-b+t)/2-t)),value,font=f,fill=0)

for hour in range(24):
    for minute in range(60):
        patch=Image.new('L',(556,169),255)
        center(patch,(0,0,556,169),f'{hour:02}:{minute:02}',173)
        patch.save(OUT/'clock'/f'{hour:02}{minute:02}.png',optimize=True)

# Apparent solar longitude (Meeus low-order solar model), solved in UTC.
# Only the Beijing civil date is displayed, never a claim of exact term time.
def longitude(dt):
    jd=dt.timestamp()/86400+2440587.5
    t=(jd-2451545)/36525
    mean=(280.46646+36000.76983*t+0.0003032*t*t)%360
    m=math.radians((357.52911+35999.05029*t-0.0001537*t*t)%360)
    c=(1.914602-.004817*t-.000014*t*t)*math.sin(m)+(.019993-.000101*t)*math.sin(2*m)+.000289*math.sin(3*m)
    return (mean+c-.00569-.00478*math.sin(math.radians(125.04-1934.136*t)))%360

names='春分 清明 谷雨 立夏 小满 芒种 夏至 小暑 大暑 立秋 处暑 白露 秋分 寒露 霜降 立冬 小雪 大雪 冬至 小寒 大寒 立春 雨水 惊蛰'.split()
terms=[]
for year in (2026,2027,2028):
    cursor=datetime(year,1,1,tzinfo=timezone.utc)
    for i in range(366):
        end=cursor+timedelta(days=1)
        a,b=longitude(cursor),longitude(end)
        if int(a//15)!=int(b//15):
            target=(int(a//15)+1)*15%360
            lo,hi=cursor,end
            for _ in range(30):
                mid=lo+(hi-lo)/2
                if (longitude(mid)-target+180)%360-180<0: lo=mid
                else: hi=mid
            terms.append(((hi+timedelta(hours=8)).date(),names[target//15]))
        cursor=end
terms=sorted(set(terms))
assert (date(2026,9,23),'秋分') in terms
months='正 二 三 四 五 六 七 八 九 十 冬 腊'.split()
days=['初'+x for x in '一二三四五六七八九十']+['十'+x for x in '一二三四五六七八九']+['二十']+['廿'+x for x in '一二三四五六七八九']+['三十']
weekdays='MONDAY TUESDAY WEDNESDAY THURSDAY FRIDAY SATURDAY SUNDAY'.split()
enmonths='JANUARY FEBRUARY MARCH APRIL MAY JUNE JULY AUGUST SEPTEMBER OCTOBER NOVEMBER DECEMBER'.split()
rows=json.loads((ROOT/'lunar-dates.json').read_text(encoding='utf-8-sig'))
for row in rows:
    day=date.fromisoformat(row['date'])
    patch=Image.new('L',(364,130),255)
    draw=ImageDraw.Draw(patch)
    sizes=s['ANNIVERSARY_SIZES']
    gap=s['ANNIVERSARY_GAP']
    lines=[('Surreal, but nice',sizes[0],'serif'),(f'{(day-date(2021,4,24)).days:,} days',sizes[1],'serif'),('since 2021.04.24',sizes[2],'num')]
    measurements=[]
    for value,size,font in lines:
        f=ImageFont.truetype(s['fonts'][font],size)
        bounds=draw.textbbox((0,0),value,font=f)
        measurements.append((value,f,bounds))
    y=round((130-sum(b-t for _,_,(l,t,r,b) in measurements)-2*gap)/2)
    for value,f,(l,t,r,b) in measurements:
        assert r-l<=364
        draw.text((364-r,y-t),value,font=f,fill=0);y+=b-t+gap
    patch.save(OUT/'day'/f'{day}-anniversary.png',optimize=True)
    patch=base.crop((678,242,1015,479));draw=ImageDraw.Draw(patch)
    draw.rectangle((20,78,316,181),fill=255)
    center(patch,(24,81,176,181),str(day.day),96)
    center(patch,(176,90,314,125),weekdays[day.weekday()],19)
    center(patch,(176,131,314,165),enmonths[day.month-1][:3]+'.',24)
    draw.rectangle((21,186,315,222),fill=255)
    center(patch,(21,186,315,222),f'{enmonths[day.month-1]} · {day.year}',22)
    patch.save(OUT/'day'/f'{day}-calendar.png',optimize=True)
    patch=Image.new('L',(556,68),255)
    current=[v for v in terms if v[0]<=day][-1][1]
    upcoming=[v for v in terms if v[0]>day][0][1]
    center(patch,(0,0,556,32),f'{current}时节  /  下一节气 · {upcoming}',27,'cn')
    cyc=row['year']-4
    lunar=f"{'甲乙丙丁戊己庚辛壬癸'[cyc%10]}{'子丑寅卯辰巳午未申酉戌亥'[cyc%12]}年 · 农历{'闰' if row['leap'] else ''}{months[row['month']-1]}月{days[row['day']-1]}"
    center(patch,(0,41,556,68),lunar,24,'cn')
    patch.save(OUT/'day'/f'{day}-lunar.png',optimize=True)

cx,cy=s['cup_x'],s['cup_y']
for i in range(6):
    patch=Image.new('L',(44,34),255);draw=ImageDraw.Draw(patch)
    for column,offset in enumerate((9,23,37)):
        phase=i/6
        points=[(round(offset-1+3.5*math.sin(step/4+phase*math.tau+column*.4)),round(31-14*phase-step)) for step in range(15)]
        draw.line(points,fill=0,width=3)
    patch.save(OUT/'steam'/f'{i}.png')
(OUT/'positions.conf').write_bytes(f'STEAM_X={cx+1}\nSTEAM_Y={cy-34}\n'.encode('ascii'))
manifest={'start':rows[0]['date'],'end':rows[-1]['date'],'clock_images':1440,'day_count':len(rows),'steam_frames':6}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(manifest)
