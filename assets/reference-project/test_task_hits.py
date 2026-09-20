"""Exercise production touch mapping and arbitrary task completion order."""
import itertools
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'todo-service/private/test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.globals().geometry=lua.execute((ROOT/'package/dashboard/direct-geometry.lua').read_text('utf-8'))
lua.globals().core=lua.execute((ROOT/'package/dashboard/direct-core.lua').read_text('utf-8'))
check=lua.eval('''function(order,upside)
    local serial=0
    local state={tasks={{id='a',content='A'},{id='b',content='B'},{id='c',content='C'}},outbox={},offset=0}
    local client=core.new({save=function() end,uuid=function() serial=serial+1;return tostring(serial) end},state)
    for _,id in ipairs(order) do
        local view=client:view()
        local index
        for i,t in ipairs(view.tasks) do if t.id==id then index=i end end
        assert(index)
        -- Test both the checkbox and the far end of the text line.
        for _,x in ipairs({74,180,900}) do
            local y=992+(index-1)*48
            local raw_x,raw_y=geometry.touch(x,y,upside)
            local mapped_x,mapped_y=geometry.touch(raw_x,raw_y,upside)
            assert(geometry.task_row(mapped_x,mapped_y,#view.tasks)==index)
        end
        assert(client:complete(id,id))
        local after=client:view()
        assert(after.total==view.total-1)
        for _,task in ipairs(after.tasks) do assert(task.id~=id) end
    end
    assert(client:view().total==0)
end''')
for order in itertools.permutations('abc'):
    for upside in (False,True):check(lua.table_from(order),upside)
print('PASS: all six completion orders, upright/upside-down, checkbox and text hit targets')
geometry=lua.globals().geometry
for index in range(1,8):
    top,bottom=geometry.row_bounds(index)
    assert geometry.task_row(74,top,7)==index
    assert geometry.task_row(74,bottom-1,7)==index
assert geometry.task_row(74,960,7) is None
assert geometry.task_row(74,1304,7) is None
print('PASS: seven row boundaries, no overlapping targets')
