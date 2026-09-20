-- Lua 5.1-compatible task state machine. Network and persistence are injected.
local M = {}
local function occurrence(task)
    local due = task.due
    if type(due) == 'table' and due.is_recurring then
        return task.id .. ':' .. tostring(due.datetime or due.date or '')
    end
    return task.id
end
M.occurrence = occurrence
local function encode_url(s)
    return (s:gsub('([^%w%-%_%.%~])', function(c) return string.format('%%%02X', string.byte(c)) end))
end
function M.new(env, state)
    state = state or {tasks={}, outbox={}, offset=0}
    assert(type(state.tasks)=='table' and type(state.outbox)=='table', 'invalid saved task state')
    local self = {state=state}
    function self:view()
        local pending, visible = {}, {}
        for _, item in pairs(state.outbox) do pending[item.occurrence] = true end
        for _, task in ipairs(state.tasks) do
            if not pending[occurrence(task)] then visible[#visible+1]=task end
        end
        state.offset=math.min(state.offset or 0, math.max(0, math.floor((#visible-1)/7)*7))
        local rows={}
        for i=state.offset+1, math.min(state.offset+7,#visible) do rows[#rows+1]=visible[i] end
        return {tasks=rows, total=#visible, offset=state.offset}
    end
    function self:complete(id, expected)
        for _, item in pairs(state.outbox) do
            if item.occurrence==expected then return false end
        end
        for _, task in ipairs(state.tasks) do
            if task.id==id and occurrence(task)==expected then
                local uuid=env.uuid()
                state.outbox[uuid]={id=id, occurrence=expected, uuid=uuid}
                env.save(state) -- Commit before any visual acknowledgement or HTTP call.
                return true
            end
        end
        return false
    end
    function self:next_page()
        local current=self:view()
        state.offset=state.offset+7
        if state.offset>=current.total then state.offset=0 end
        env.save(state)
    end
    function self:sync()
        local staged, ids, cursors, cursor = {}, {}, {}, nil
        repeat
            local path='tasks?project_id='..encode_url(env.project)..'&limit=100'
            if cursor then path=path..'&cursor='..encode_url(cursor) end
            local page=env.request(path)
            if type(page)~='table' or type(page.results)~='table' then return false end
            for _, task in ipairs(page.results) do
                if type(task)~='table' or type(task.id)~='string' or task.project_id~=env.project or type(task.content)~='string' then return false end
                if not ids[task.id] then staged[#staged+1]=task;ids[task.id]=task end
            end
            cursor=type(page.next_cursor)=='string' and page.next_cursor~='' and page.next_cursor or nil
            if cursor then
                if cursors[cursor] then return false end
                cursors[cursor]=true
            end
        until not cursor
        state.tasks=staged
        env.save(state)
        local keys={}
        for key in pairs(state.outbox) do keys[#keys+1]=key end
        table.sort(keys)
        local all_ok=true
        for _, key in ipairs(keys) do
            local item=state.outbox[key]
            local current=ids[item.id]
            if not current or occurrence(current)~=item.occurrence then
                -- Already completed/deleted elsewhere, or a newer recurring instance.
                state.outbox[key]=nil
                env.save(state)
            else
                local result=env.request('sync',{{type='item_close',uuid=item.uuid,args={id=item.id}}})
                if type(result)=='table' and type(result.sync_status)=='table' and result.sync_status[item.uuid]=='ok' then
                    local remaining={}
                    for _, task in ipairs(state.tasks) do
                        if occurrence(task)~=item.occurrence then remaining[#remaining+1]=task end
                    end
                    state.tasks=remaining
                    state.outbox[key]=nil
                    env.save(state)
                else all_ok=false end
            end
        end
        return all_ok
    end
    return self
end
return M
