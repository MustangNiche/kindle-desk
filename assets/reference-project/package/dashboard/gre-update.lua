package.path='/usr/lib/lua/?.lua;'..package.path
package.cpath='/usr/lib/lua/?.so;'..package.cpath
local json=require('cjson')
local schedule=dofile('/mnt/us/dashboard/gre-schedule.lua')
local root='/mnt/us/dashboard/gre'
local lock='/tmp/kindle-desk-always.lock'
local function read(path)
    local f=io.open(path,'rb');if not f then return nil end
    local value=f:read('*a');f:close();return value
end
local manifest=json.decode(assert(read(root..'/manifest.json')))
local index,day=schedule.select(os.time(),manifest.count,manifest.anchor,manifest.order)
local key=tostring(day)..':'..tostring(index)
if read(lock..'/gre-day')~=key then
    local function quote(s) return "'"..s:gsub("'","'\\''").."'" end
    local path=root..'/'..string.format('%03d',index)..'.png'
    local result=os.execute(quote(assert(arg[1]))..' -q -g '..quote('file='..path..',x=58,y=64'))
    assert(result==0 or result==true,'Daily word drawing failed')
    local f=assert(io.open(lock..'/gre-day','wb'));assert(f:write(key));f:close()
    print('GRE_WORD_INDEX='..index..' DAY_KEY='..day)
end
