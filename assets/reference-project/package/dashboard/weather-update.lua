package.path='/usr/lib/lua/?.lua;'..package.path
package.cpath='/usr/lib/lua/?.so;'..package.cpath
local json=require('cjson')
local weather=dofile('/mnt/us/dashboard/weather-core.lua')
local root='/mnt/us/dashboard/weather'
local lock='/tmp/kindle-desk-always.lock'
local function read(path)
    local f=io.open(path,'rb');if not f then return nil end
    local value=f:read('*a');f:close();return value
end
local function write(path,value)
    local f=assert(io.open(path..'.next','wb'));assert(f:write(value));assert(f:close())
    assert(os.rename(path..'.next',path))
end
local function quote(s) return "'"..tostring(s):gsub("'","'\\''").."'" end
local function run(command) local r=os.execute(command);return r==0 or r==true end
local now=os.time()
local state={slot=-1,last_attempt=0}
local ok,saved=pcall(json.decode,read(root..'/cache.json') or '')
if ok and type(saved)=='table' then state=saved end
local slot=weather.slot(now)
if type(state.updated)~='number' then state.updated=nil end
if weather.due(now,state) then
    state.last_attempt=now
    write(root..'/cache.json',json.encode(state))
    -- Do NOT reuse the Todoist curl config or send its Authorization header here.
    local url='https://api.open-meteo.com/v1/forecast?latitude=39.96&longitude=116.30&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max&timezone=Asia%2FShanghai&forecast_days=3'
    local command='curl --silent --show-error --fail --proto '..quote('=https')..' --connect-timeout 5 --max-time 12 --cacert /mnt/us/dashboard/direct/ca.pem '..quote(url)..' -o '..quote(lock..'/weather-response.json')
    if run(command) then
        local parsed,forecast=pcall(json.decode,read(lock..'/weather-response.json') or '')
        if parsed and weather.valid(forecast) then
            state.forecast=forecast;state.updated=now;state.slot=slot
            print('WEATHER_SYNC_OK=1 SLOT='..slot)
        else print('WEATHER_INVALID_RESPONSE=1') end
    else print('WEATHER_SYNC_DEFERRED=1') end
    write(root..'/cache.json',json.encode(state))
end
local today=os.date('!%Y-%m-%d',now+28800)
local key=today..':'..tostring(state.updated)
if read(lock..'/weather-view')==key then return end
local fbink=assert(arg[1])
local function text(value,size,x,y,width,height,font)
    local options='regular='..font..',px='..size..',top='..y..',bottom='..(1448-y-height)..',left='..x..',right='..(1072-x-width)
    assert(run(quote(fbink)..' -q -m -t '..quote(options)..' -- '..quote(value)))
end
assert(run(quote(fbink)..' -q -g '..quote('file='..root..'/blank.png,x=0,y=600')))
for i,x in ipairs({58,572}) do
    local date=os.date('!%Y-%m-%d',now+28800+(i-1)*86400)
    local forecast=weather.day(state.forecast,date)
    local condition,temperature,advice='预报待更新','--° / --°','联网后自动更新'
    if forecast then
        condition=forecast.condition
        temperature=string.format('%d° / %d°',math.floor(forecast.low+0.5),math.floor(forecast.high+0.5))
        advice=forecast.advice
    end
    text(condition,26,x,673,442,40,'/mnt/us/dashboard/direct/song.ttf')
    text(temperature,59,x,722,442,74,root..'/serif.ttf')
    text(advice,22,x,801,442,36,'/mnt/us/dashboard/direct/song.ttf')
end
local stamp=state.updated and ('更新 '..os.date('!%m/%d %H:%M',state.updated+28800)..' · Open-Meteo') or '天气尚未更新 · Open-Meteo'
text(stamp,16,58,842,956,22,'/mnt/us/dashboard/direct/song.ttf')
write(lock..'/weather-view',key)
