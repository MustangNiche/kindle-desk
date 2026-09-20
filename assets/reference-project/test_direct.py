"""Execute the production state machine on Lua 5.1, including offline retries."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'todo-service/private/test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
core=lua.execute((ROOT/'package/dashboard/direct-core.lua').read_text('utf-8'))
lua.globals().core=core
lua.execute('''
local function copy(t)
    if type(t)~='table' then return t end
    local out={} for k,v in pairs(t) do out[k]=copy(v) end return out
end
local function setup()
    local e={project='p',remote={{id='a',project_id='p',content='中文任务'}},calls={},counter=0}
    e.save=function(s) e.saved=copy(s) end
    e.uuid=function() e.counter=e.counter+1;return 'uuid-'..e.counter end
    e.request=function(path,commands)
        if not commands then
            if e.offline then return nil end
            return {results=copy(e.remote)}
        end
        local cmd=commands[1];e.calls[#e.calls+1]=copy(cmd)
        if e.fail_close then return nil end
        e.remote={}
        return {sync_status={[cmd.uuid]='ok'}}
    end
    local c=core.new(e)
    assert(c:sync());return e,c
end
local e,c=setup()
assert(c:view().total==1)
assert(c:complete('a','a'));assert(c:view().total==0)
assert(not c:complete('a','a'))
assert(e.saved.outbox['uuid-1'])
e.offline=true;c=core.new(e,copy(e.saved));assert(not c:sync());assert(c:view().total==0)
e.offline=false;e.fail_close=true;assert(not c:sync())
c=core.new(e,copy(e.saved));e.fail_close=false;assert(c:sync())
assert(#e.calls==2 and e.calls[1].uuid==e.calls[2].uuid)
assert(c:view().total==0 and next(c.state.outbox)==nil)
print('PASS: durable offline completion, duplicate taps, stable UUID retries')

e,c=setup();e.remote[1].due={is_recurring=true,date='2026-09-18'};assert(c:sync())
assert(c:complete('a','a:2026-09-18'))
e.remote[1].due.date='2026-09-19';assert(c:sync())
assert(#e.calls==0 and c:view().total==1 and next(c.state.outbox)==nil)
print('PASS: old recurring occurrence cannot complete the next occurrence')

e,c=setup();assert(c:complete('a','a'))
e.remote[1].due={date='2026-09-19',is_recurring=false};assert(c:sync())
assert(#e.calls==1 and c:view().total==0)
print('PASS: edited due date does not discard completion of a nonrecurring task')

e,c=setup()
local calls=0
e.request=function(path)
    calls=calls+1
    if calls==1 then return {results={{id='b',project_id='p',content='new'}},next_cursor='next'} end
    return nil
end
assert(not c:sync());assert(c:view().tasks[1].id=='a')
e.request=function(path) return {results={{id='b',project_id='p',content='new'}},next_cursor='loop'} end
assert(not c:sync());assert(c:view().tasks[1].id=='a')
e.request=function(path) return {results={{id='b',project_id='wrong',content='new'}}} end
assert(not c:sync());assert(c:view().tasks[1].id=='a')
print('PASS: failed pagination, repeated cursor and wrong project preserve the cache')

e,c=setup();e.remote={}
for i=1,10 do e.remote[i]={id=tostring(i),project_id='p',content='task '..i} end
assert(c:sync());assert(#c:view().tasks==7)
c:next_page();assert(c:view().offset==7 and #c:view().tasks==3)
for i=8,10 do assert(c:complete(tostring(i),tostring(i))) end
assert(c:view().offset==0 and c:view().total==7)
print('PASS: seven-row paging and clamping after completion')
''')
compiler=lua.eval('function(s) local f,e=loadstring(s);return f~=nil,e end')
for name in ['direct-core.lua','direct-client.lua']:
    ok,error=compiler((ROOT/'package/dashboard'/name).read_text('utf-8'))
    assert ok,error
print('PASS: production Lua files compile on Lua 5.1')
