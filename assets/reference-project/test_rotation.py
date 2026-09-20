import os
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BIN=Path('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/usr/bin')
sys.path.insert(0,str(ROOT/'todo-service/private/test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
geometry=lua.execute((ROOT/'package/dashboard/direct-geometry.lua').read_text('utf-8'))
for x,y in [(0,0),(1071,1447),(75,990),(800,1280),(940,920),(130,1370)]:
    flipped=geometry.touch(x,y,True)
    assert geometry.touch(*flipped,True)==(x,y)
    assert geometry.touch(x,y,False)==(x,y)
print('PASS: corners, task rows, pagination and exit touch coordinates')
def unix(path):
    value=path.resolve().as_posix();return '/'+value[0].lower()+value[2:]
for rotation in range(4):
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        folder=Path(tmp);lock=folder/'lock';lock.mkdir()
        register=folder/'rotate';register.write_text(str(rotation))
        source=(ROOT/'package/dashboard/screen-rotation.sh').read_text('utf-8').replace('/sys/class/graphics/fb0/rotate',unix(register))
        source='LOCK="'+unix(lock)+'"\n'+source
        source+='\nstart_rotation || exit 1\n[ "$(cat "$ROTATION_PATH")" = 1 ] || exit 2\nstart_rotation || exit 4\n[ "$(cat "$ROTATION_PATH")" = 1 ] || exit 5\nrestore_rotation || exit 3\n'
        script=folder/'test.sh';script.write_bytes(source.encode())
        env=dict(os.environ);env['PATH']=str(BIN)+os.pathsep+env['PATH']
        result=subprocess.run([str(BIN/'dash.exe'),str(script)],env=env,capture_output=True)
        assert result.returncode==0,result.stderr
        assert register.read_text().strip()=='3'
        assert not list(lock.iterdir())
print('PASS: all initial orientations select upside=1, repeated starts stay upside, exit restores normal=3')
ok=lua.eval('function(s) return loadstring(s)~=nil end')((ROOT/'package/dashboard/direct-client.lua').read_text('utf-8'))
assert ok
direct=(ROOT/'package/documents/Desk Direct.sh').read_text('utf-8')
upside=(ROOT/'package/documents/Desk Upside Down.sh').read_text('utf-8')
assert direct.replace('# Name: Desk Direct - 充电口朝上','# Name: Desk Upside Down - 充电口朝上')==upside
assert direct.count('start_rotation || exit 1')==1
assert direct.count('lua /mnt/us/dashboard/gre-update.lua')==2
assert 'start_rotation' not in (ROOT/'package/documents/Desk Upright.sh').read_text('utf-8')
print('PASS: both usual launchers use identical upside-down behavior and retain daily GRE')
