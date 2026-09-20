"""Build the standalone Kindle Todoist package, retaining private data locally."""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
PRIVATE=ROOT/'todo-service/private'
sys.path.insert(0,str(PRIVATE/'test-deps'))
from fontTools.ttLib import TTFont
out=PRIVATE/'direct';out.mkdir(exist_ok=True)
config=json.loads((PRIVATE/'todoist.json').read_text('utf-8'))
initial=json.loads(Path('F:/dashboard/cloud-test/tasks.json').read_text('utf-8'))
assert isinstance(initial.get('results'),list)
assert all(t['project_id']==config['project_id'] for t in initial['results'])
(out/'initial.json').write_text(json.dumps(initial,ensure_ascii=False),encoding='utf-8')
(out/'project.json').write_text(json.dumps({'project':config['project_id']}),encoding='ascii')
(out/'curl.conf').write_text((PRIVATE/'cloud-test/curl.conf').read_text('ascii').replace('/cloud-test/','/direct/'),encoding='ascii')
(out/'ca.pem').write_bytes((PRIVATE/'cloud-test/ca.pem').read_bytes())
font=TTFont('C:/Windows/Fonts/simsun.ttc',fontNumber=0)
font.save(out/'song.ttf')
# Validate the extracted font using the renderer already used for the design.
ImageFont.truetype(str(out/'song.ttf'),27)
base=Image.open(ROOT/'package/dashboard/live/base-always.png').copy()
draw=ImageDraw.Draw(base)
draw.rectangle((58,1350,760,1410),fill=255)
small=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',23)
draw.text((58,1364),'点此退出',font=small,fill=0,anchor='lt')
base.save(out/'base.png')
patch=base.crop((0,880,1072,1330))
pd=ImageDraw.Draw(patch)
pd.rectangle((58,70,1014,449),fill=255)
pd.rectangle((825,8,1014,69),fill=255)
patch.save(out/'tasks-empty.png')
box=Image.new('L',(20,20),255)
ImageDraw.Draw(box).rectangle((0,0,19,19),outline=0,width=2)
box.save(out/'checkbox.png')
for name,label in [('connecting','待办连接中'),('online','待办已同步'),
                   ('offline','连接暂断 · 完成操作已保存'),('pending','完成待上传')]:
    notice=Image.new('L',(460,48),255)
    ImageDraw.Draw(notice).text((0,7),label,font=small,fill=0,anchor='lt')
    notice.save(out/f'{name}.png')
source=(ROOT/'package/documents/Desk Todo.sh').read_text('utf-8')
source=source.replace('# Name: Desk Todo - 同步待办信息屏','# Name: Desk Direct - Todoist直连信息屏')
source=source.replace('TODO_REVISION=2','DIRECT_REVISION=1').replace('todo.log','direct.log')
source=source.replace('file=/mnt/us/dashboard/todo/base.png','file=/mnt/us/dashboard/direct/base.png')
source=source.replace('. /mnt/us/dashboard/todo-runtime.sh','. /mnt/us/dashboard/direct-runtime.sh')
source=source.replace('    restore_network\n','''    restore_network
    rm -f "$LOCK/commands.json" "$LOCK/commands.json.next" "$LOCK/response.json" "$LOCK/drawing.next" "$LOCK/stop.next" "$LOCK/view-id.next" "$LOCK/direct-map.json" "$LOCK/direct-map.json.next" "$LOCK/direct-signature" "$LOCK/direct-signature.next" "$LOCK/direct-notice" "$LOCK/direct-notice.next"
''')
from gre_launcher import add_gre
from weather_launcher import add_weather
(ROOT/'package/documents/Desk Upright.sh').write_bytes(add_weather(add_gre(source)).replace('# Name: Desk Direct - Todoist直连信息屏','# Name: Desk Upright - 正向信息屏').encode('utf-8'))
import runpy
runpy.run_path(str(ROOT/'build_upside_down.py'))
print('Built direct client, extracted Chinese font, and verified initial task project.')
