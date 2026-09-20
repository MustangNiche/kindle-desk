import json,time,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from weather_launcher import add_weather
ROOT=Path(__file__).resolve().parent
out=ROOT/'package/dashboard/weather';out.mkdir(exist_ok=True)
image=Image.open(ROOT/'package/dashboard/live/base-always.png').crop((0,600,1072,862))
draw=ImageDraw.Draw(image)
for x0,x1 in [(58,500),(572,1014)]:draw.rectangle((x0,68,x1,261),fill=255)
image.save(out/'blank.png')
shutil.copyfile('C:/Windows/Fonts/georgia.ttf',out/'serif.ttf')
forecast=json.loads((ROOT/'todo-service/private/haidian-forecast.json').read_text('utf-8'))
(out/'initial-cache.json').write_text(json.dumps({'forecast':forecast,'updated':int(time.time()),'slot':-1,'last_attempt':0}),encoding='utf-8')
small=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',23)
for name,label in [('connecting','待办连接中'),('online','待办已同步'),('offline','连接暂断 · 完成操作已保存'),('pending','完成待上传')]:
    notice=Image.new('L',(460,48),255)
    ImageDraw.Draw(notice).text((0,7),label,font=small,fill=0,anchor='lt')
    notice.save(ROOT/f'todo-service/private/direct/{name}.png')
for name in ['Desk Direct.sh','Desk Upside Down.sh','Desk Upright.sh']:
    path=ROOT/'package/documents'/name
    path.write_bytes(add_weather(path.read_text('utf-8')).encode('utf-8'))
print('Built live forecast area and twice-daily weather hooks.')
