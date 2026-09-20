local M={}
function M.slot(epoch)
    local local_time=epoch+28800
    local day=math.floor(local_time/86400)
    local seconds=local_time%86400
    if seconds<32400 then return day*2-1 end
    if seconds<61200 then return day*2 end
    return day*2+1
end
function M.due(epoch,state)
    local attempt=type(state.last_attempt)=='number' and state.last_attempt or 0
    return state.slot~=M.slot(epoch) and (epoch-attempt>=1800 or epoch<attempt)
end
function M.valid(data)
    if type(data)~='table' or type(data.daily)~='table' or data.utc_offset_seconds~=28800 then return false end
    local units=data.daily_units
    if type(units)~='table' or units.temperature_2m_max~='°C' or units.temperature_2m_min~='°C' or units.precipitation_probability_max~='%' or units.wind_speed_10m_max~='km/h' then return false end
    local d=data.daily
    if type(d.time)~='table' or #d.time<2 then return false end
    local ranges={weather_code={0,99},temperature_2m_min={-80,65},temperature_2m_max={-80,65},precipitation_probability_max={0,100},wind_speed_10m_max={0,300}}
    local seen={}
    for i,date in ipairs(d.time) do
        if type(date)~='string' or not date:match('^%d%d%d%d%-%d%d%-%d%d$') or seen[date] then return false end
        seen[date]=true
        for key,range in pairs(ranges) do
            if type(d[key])~='table' then return false end
            local value=d[key][i]
            if type(value)~='number' or value~=value or value<range[1] or value>range[2] then return false end
        end
        if d.temperature_2m_min[i]>d.temperature_2m_max[i] then return false end
    end
    return true
end
local labels={[0]='晴',[1]='晴间多云',[2]='多云',[3]='阴',[45]='雾',[48]='雾凇',
 [51]='小毛毛雨',[53]='毛毛雨',[55]='较强毛毛雨',[56]='冻毛毛雨',[57]='冻毛毛雨',
 [61]='小雨',[63]='中雨',[65]='大雨',[66]='冻雨',[67]='冻雨',
 [71]='小雪',[73]='中雪',[75]='大雪',[77]='雪粒',[80]='阵雨',[81]='较强阵雨',[82]='强阵雨',
 [85]='阵雪',[86]='较强阵雪',[95]='雷雨',[96]='雷雨伴冰雹',[99]='雷雨伴冰雹'}
function M.day(data,date)
    if not M.valid(data) then return nil end
    local d=data.daily
    for i,value in ipairs(d.time) do
        if value==date then
            local code=d.weather_code[i]
            local low,high=d.temperature_2m_min[i],d.temperature_2m_max[i]
            local tips={}
            if (code>=71 and code<=77) or code==85 or code==86 then tips[#tips+1]='雨雪带伞，注意防滑'
            elseif code>=95 then tips[#tips+1]='带伞，留意雷雨'
            elseif code>=51 or d.precipitation_probability_max[i]>=40 then tips[#tips+1]='出门记得带伞' end
            if low<=10 then tips[#tips+1]='早晚添衣保暖'
            elseif low<=17 then tips[#tips+1]='带件薄外套'
            elseif high>=30 then tips[#tips+1]='防晒补水' end
            if #tips<2 and d.wind_speed_10m_max[i]>=39 then tips[#tips+1]='风大注意防风' end
            if #tips==0 then tips[1]='适合日常出行' end
            return {condition=labels[code] or '天气待确认',low=low,high=high,advice=table.concat(tips,'，',1,math.min(2,#tips))}
        end
    end
end
return M
