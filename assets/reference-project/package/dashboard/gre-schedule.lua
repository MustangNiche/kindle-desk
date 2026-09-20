local M={}
-- 09:00 Beijing is 01:00 UTC. Do not depend on the device's timezone label.
function M.select(epoch,count,anchor,order)
    assert(count>0)
    local day=math.floor((epoch-3600)/86400)
    local slot=(day-anchor)%count+1
    local index=order and order[slot] or slot
    assert(type(index)=='number' and index>=1 and index<=count)
    return index,day
end
return M
