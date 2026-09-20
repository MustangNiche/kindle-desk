import json
import sys
from datetime import datetime,timezone,timedelta
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'todo-service/private/test-deps'))
from lupa.lua51 import LuaRuntime
runtime=LuaRuntime(unpack_returned_tuples=True)
schedule=runtime.execute((ROOT/'package/dashboard/gre-schedule.lua').read_text('utf-8'))
manifest=json.loads((ROOT/'package/dashboard/gre/manifest.json').read_text())
order=runtime.table_from(manifest['order'])
assert sorted(manifest['order'])==list(range(1,manifest['count']+1))
assert manifest['order']!=sorted(manifest['order'])
tz=timezone(timedelta(hours=8))
def select(value):
    return schedule.select(datetime.fromisoformat(value).replace(tzinfo=tz).timestamp(),manifest['count'],manifest['anchor'],order)[0]
assert select('2026-09-20T08:59:59')!=select('2026-09-20T09:00:00')
assert select('2026-09-20T09:00:00')==select('2026-09-21T08:59:59')
assert select('2026-09-21T09:00:00')==manifest['order'][1]
cycle=[schedule.select((manifest['anchor']+i)*86400+3600,manifest['count'],manifest['anchor'],order)[0] for i in range(manifest['count'])]
assert len(set(cycle))==manifest['count']
assert cycle==manifest['order']
print('PASS: full shuffled cycle has no duplicates and restarts select the same day')
assert select('2026-12-31T23:59:59')==select('2027-01-01T08:59:59')
assert select('2027-01-01T09:00:00')!=select('2027-01-01T08:59:59')
for index in range(1,manifest['count']+1):
    with Image.open(ROOT/f'package/dashboard/gre/{index:03d}.png') as im:
        im.load();assert im.size==(412,130)
assert manifest['count']==len({line.split('|')[0] for line in (ROOT/'gre-words.txt').read_text('utf-8').splitlines() if line.strip()})
print('PASS: Beijing 09:00 boundary, midnight/year boundary, deterministic restart, all',manifest['count'],'unique assets')
from gre_launcher import add_gre
for name in ['Desk Direct.sh','Desk Upside Down.sh','Desk Upright.sh']:
    text=(ROOT/'package/documents'/name).read_text('utf-8')
    assert add_gre(text)==text
    assert text.count('lua /mnt/us/dashboard/gre-update.lua')==2
print('PASS: both orientations update on startup and each clock minute; build is idempotent')
