-- Device-only Todoist client. All command arguments are shell-quoted.
package.path='/usr/lib/lua/?.lua;'..package.path
package.cpath='/usr/lib/lua/?.so;'..package.cpath
local json=require('cjson')
local core=dofile('/mnt/us/dashboard/direct-core.lua')
local geometry=dofile('/mnt/us/dashboard/direct-geometry.lua')
local ROOT='/mnt/us/dashboard/direct'
local LOCK='/tmp/kindle-desk-always.lock'
local FBINK=arg[2] or '/var/local/kmc/bin/fbink'
local function read(path)
    local file=io.open(path,'rb');if not file then return nil end
    local value=file:read('*a');file:close();return value
end
local function write(path, value)
    local file=assert(io.open(path..'.next','wb'))
    assert(file:write(value));assert(file:close())
    assert(os.rename(path..'.next',path))
end
local function quote(s) return "'"..tostring(s):gsub("'","'\\''").."'" end
local function run(command)
    local result=os.execute(command)
    return result==0 or result==true
end
local function uuid()
    local value=assert(read('/proc/sys/kernel/random/uuid')):gsub('%s','')
    assert(value:match('^[0-9a-f%-]+$') and #value==36)
    return value
end
local function save(state)
    write(ROOT..'/state.json',json.encode(state))
    assert(run('sync'))
end
local function request(path, commands)
    local command='curl --config '..quote(ROOT..'/curl.conf')
    if commands then
        write(LOCK..'/commands.json',json.encode(commands))
        command=command..' --data-urlencode '..quote('commands@'..LOCK..'/commands.json')
    end
    command=command..' '..quote('https://api.todoist.com/api/v1/'..path)..' -o '..quote(LOCK..'/response.json')
    if not run(command) then return nil end
    local ok,result=pcall(json.decode,read(LOCK..'/response.json') or '')
    if not ok then return nil end
    return result
end
local raw=read(ROOT..'/state.json')
local state=raw and json.decode(raw) or {tasks=json.decode(assert(read(ROOT..'/initial.json'))).results,outbox={},offset=0}
local config=json.decode(assert(read(ROOT..'/project.json')))
local client=core.new({project=config.project,request=request,save=save,uuid=uuid},state)
local function image(name,x,y)
    assert(run(quote(FBINK)..' -q -g '..quote('file='..ROOT..'/'..name..',x='..x..',y='..y)))
end
local function text(value,px,x,y,width,height)
    local opts='regular='..ROOT..'/song.ttf,px='..px..',top='..y..',bottom='..(1448-y-height)..',left='..x..',right='..(1072-x-width)
    assert(run(quote(FBINK)..' -q -t '..quote(opts)..' -- '..quote(value)))
end
local function shorten(value)
    value=value:gsub('%c',' '):gsub('%s+',' ')
    local chars={}
    for c in value:gmatch('[%z\1-\127\194-\244][\128-\191]*') do chars[#chars+1]=c end
    if #chars>32 then return table.concat(chars,'',1,31)..'…' end
    return value
end
local function render(force)
    local view=client:view()
    local signature=tostring(view.offset)..'/'..view.total
    for _, task in ipairs(view.tasks) do signature=signature..'|'..#task.id..':'..task.id..#task.content..':'..task.content..core.occurrence(task) end
    if not force and read(LOCK..'/direct-signature')==signature then return end
    write(LOCK..'/drawing','1')
    local generation=uuid()
    write(LOCK..'/view-id',generation)
    image('tasks-empty.png',0,880)
    local count=view.total<=7 and string.format('%02d 条',view.total) or string.format('%d/%d',view.offset/7+1,math.ceil(view.total/7))
    text(count,23,924,907,90,36)
    local map={generation=generation,rows={}}
    for i, task in ipairs(view.tasks) do
        local y=975+(i-1)*48
        image('checkbox.png',64,y+8)
        text(shorten(task.content),27,126,y,888,42)
        map.rows[i]={id=task.id,occurrence=core.occurrence(task)}
    end
    if view.total==0 then text('暂时没有待办，喝杯咖啡吧。',27,126,989,888,42) end
    write(LOCK..'/direct-map.json',json.encode(map))
    write(LOCK..'/direct-signature',signature)
    os.remove(LOCK..'/drawing')
end
local function notice(name)
    if read(LOCK..'/direct-notice')~=name then
        image(name..'.png',300,1357)
        write(LOCK..'/direct-notice',name)
    end
end
if arg[1]=='init' then
    save(state);render(true);notice('connecting')
elseif arg[1]=='action' then
    local action=read(LOCK..'/action')
    if action then
        os.remove(LOCK..'/action')
        local x,y,generation=action:match('^(%d+) (%d+) ([0-9a-f%-]+)')
        x=tonumber(x);y=tonumber(y)
        local raw_x,raw_y=x,y
        if x and y then x,y=geometry.touch(x,y,read(LOCK..'/rotation-180')~=nil) end
        local map=json.decode(read(LOCK..'/direct-map.json') or '{}')
        local row=x and geometry.task_row(x,y,#(map.rows or {})) or nil
        print(string.format('TOUCH_ACTION RAW=%s,%s LOGICAL=%s,%s ROW=%s CURRENT_VIEW=%s',tostring(raw_x),tostring(raw_y),tostring(x),tostring(y),tostring(row),tostring(generation==map.generation)))
        if x and generation==map.generation then
            if x>=58 and x<=260 and y>=1340 then write(LOCK..'/stop','1')
            elseif row then
                local item=map.rows[row]
                local accepted=item and client:complete(item.id,item.occurrence)
                print('TOUCH_COMPLETE_ACCEPTED='..tostring(accepted))
                if accepted then render(true);notice('pending') end
            elseif x>=825 and y>=896 and y<=946 then client:next_page();render(true) end
        end
    end
elseif arg[1]=='sync' then
    local ok=client:sync()
    render(false)
    notice(ok and 'online' or 'offline')
    print(ok and 'DIRECT_SYNC_OK=1' or 'DIRECT_SYNC_DEFERRED=1')
else error('Unknown operation') end
