import copy,json,sys
from pathlib import Path
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'todo-service/private/test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
core=lua.execute((ROOT/'package/dashboard/weather-core.lua').read_text('utf-8'))
def table(v):
    if isinstance(v,dict):return lua.table_from({k:table(x) for k,x in v.items()})
    if isinstance(v,list):return lua.table_from([table(x) for x in v])
    return v
def epoch(v):return datetime.fromisoformat(v).replace(tzinfo=timezone(timedelta(hours=8))).timestamp()
def slot(v):return core.slot(epoch(v))
assert slot('2026-09-20T08:59:59')+1==slot('2026-09-20T09:00:00')
assert slot('2026-09-20T16:59:59')+1==slot('2026-09-20T17:00:00')
assert slot('2026-09-20T17:00:00')==slot('2026-09-21T08:59:59')
now=epoch('2026-09-20T17:00:00')
assert not core.due(now,table({'slot':core.slot(now),'last_attempt':now-3600}))
assert core.due(now,table({'slot':core.slot(now)-1,'last_attempt':now-1800}))
assert not core.due(now,table({'slot':core.slot(now)-1,'last_attempt':now-1799}))
sample=json.loads((ROOT/'todo-service/private/haidian-forecast.json').read_text('utf-8'))
assert core.valid(table(sample))
assert core.day(table(sample),'2000-01-01') is None
for field,value in [('temperature_2m_max',None),('weather_code',100),('precipitation_probability_max',-1)]:
    bad=copy.deepcopy(sample);bad['daily'][field][0]=value
    assert not core.valid(table(bad))
bad=copy.deepcopy(sample);bad['daily_units']['temperature_2m_min']='°F'
assert not core.valid(table(bad))
for code,low,high,expected in [(61,8,20,'带伞'),(73,-5,0,'防滑'),(0,24,35,'防晒'),(1,15,25,'薄外套')]:
    item=copy.deepcopy(sample)
    for key,value in [('weather_code',code),('temperature_2m_min',low),('temperature_2m_max',high)]:item['daily'][key][0]=value
    assert expected in core.day(table(item),item['daily']['time'][0]).advice
lua.execute('assert(loadstring(...))',(ROOT/'package/dashboard/weather-update.lua').read_text('utf-8'))
from weather_launcher import add_weather
for name in ['Desk Direct.sh','Desk Upside Down.sh','Desk Upright.sh']:
    source=(ROOT/'package/documents'/name).read_text('utf-8')
    assert add_weather(source)==source
    assert source.count('lua /mnt/us/dashboard/weather-update.lua')==2
    assert source.count('lua /mnt/us/dashboard/gre-update.lua')==2
print('PASS: Beijing 09/17 boundaries, overnight, success/no repeat, failure retry, real forecast validation, stale dates, advice, Lua 5.1 syntax and all launcher hooks')
lua.globals().weather_core=core
lua.globals().forecast_sample=table(sample)
lua.globals().test_now=now
lua.execute('''
files={};commands={};serial=0;objects={};network_ok=false
package.preload.cjson=function() return {
 encode=function(v)
  serial=serial+1;local key='json'..serial
  local function clone(x) if type(x)~='table' then return x end local y={} for k,v in pairs(x) do y[k]=clone(v) end return y end
  objects[key]=clone(v);return key
 end,
 decode=function(s) assert(objects[s]);return objects[s] end
} end
local json=require('cjson')
cache_path='/mnt/us/dashboard/weather/cache.json'
files[cache_path]=json.encode({forecast=forecast_sample,updated=test_now-7200,slot=weather_core.slot(test_now)-1,last_attempt=0})
dofile=function() return weather_core end
io.open=function(path,mode)
 if mode=='rb' then if not files[path] then return nil end return {read=function() return files[path] end,close=function() return true end} end
 return {write=function(_,s) files[path]=s;return true end,close=function() return true end}
end
os.rename=function(a,b) files[b]=files[a];files[a]=nil;return true end
os.time=function() return test_now end
os.execute=function(cmd)
 commands[#commands+1]=cmd
 if cmd:match('^curl ') then
  if not network_ok then return 1 end
  files['/tmp/kindle-desk-always.lock/weather-response.json']=json.encode(forecast_sample)
 end
 return 0
end
arg={'/test/fbink'}
get_cache=function() return json.decode(files[cache_path]) end
''')
updater=(ROOT/'package/dashboard/weather-update.lua').read_text('utf-8')
lua.execute(updater)
assert lua.globals().get_cache().updated==now-7200
assert lua.globals().get_cache().slot==core.slot(now)-1
assert 'Authorization' not in next(c for c in lua.globals().commands.values() if c.startswith('curl '))
lua.execute('commands={};test_now=test_now+60')
lua.execute(updater)
assert not any(c.startswith('curl ') for c in lua.globals().commands.values())
lua.execute('network_ok=true;test_now=test_now+1740;commands={}')
lua.execute(updater)
assert lua.globals().get_cache().updated==now+1800
assert lua.globals().get_cache().slot==core.slot(now+1800)
lua.execute('commands={};test_now=test_now+60')
lua.execute(updater)
assert not any(c.startswith('curl ') for c in lua.globals().commands.values())
print('PASS: actual updater retains cached forecast after network failure, backs off, recovers and avoids repeat downloads')
