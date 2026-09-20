local M = {}
function M.row_bounds(index)
    local top=975+(index-1)*48
    return top-7,top+41
end
function M.task_row(x,y,count)
    if x<45 or x>1014 then return nil end
    for index=1,count do
        local top,bottom=M.row_bounds(index)
        if y>=top and y<bottom then return index end
    end
    return nil
end
function M.touch(x, y, upside_down)
    if upside_down then return 1071-x, 1447-y end
    return x, y
end
return M
