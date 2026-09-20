from pathlib import Path
from datetime import datetime,timezone
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
out=ROOT/'package/dashboard/gre';out.mkdir(exist_ok=True)
words=[line.split('|') for line in (ROOT/'gre-words.txt').read_text('utf-8').splitlines() if line.strip()]
assert len({row[0] for row in words})==len(words)
for index,(word,pos,meaning) in enumerate(words,1):
    im=Image.new('L',(412,130),255);draw=ImageDraw.Draw(im)
    heading=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',20)
    draw.text((0,10),'GRE · DAILY WORD',font=heading,fill=0,anchor='lt')
    size=54
    while True:
        font=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',size)
        if draw.textlength(word,font=font)<=408:break
        size-=1
    draw.text((0,41),word,font=font,fill=0,anchor='lt')
    small=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',23)
    definition=pos+' '+meaning
    if draw.textlength(definition,font=small)>408:
        small=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',21)
    if draw.textlength(definition,font=small)>408:
        while definition and draw.textlength(definition+'…',font=small)>408:
            definition=definition[:-1]
        definition+='…'
    assert draw.textlength(definition,font=small)<=408,word
    draw.text((0,101),definition,font=small,fill=0,anchor='lt')
    im.save(out/f'{index:03d}.png')
anchor=int(datetime(2026,9,20,tzinfo=timezone.utc).timestamp())//86400
from gre_manifest import make_manifest
(out/'manifest.json').write_text(json.dumps(make_manifest(len(words),anchor)),encoding='ascii')
print('Built daily GRE cards:',len(words))
from gre_launcher import add_gre
for name in ['Desk Direct.sh','Desk Upside Down.sh','Desk Upright.sh']:
    path=ROOT/'package/documents'/name
    path.write_bytes(add_gre(path.read_text('utf-8')).encode('utf-8'))
