import os
import subprocess
import tempfile
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BIN=Path('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/usr/bin')
def unix(path):
    p=path.resolve().as_posix();return '/'+p[0].lower()+p[2:]

for step, expected in [(1,(140,300)),(2,(940,1120))]:
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        folder=Path(tmp);lock=folder/'lock';lock.mkdir()
        mocks=folder/'bin';mocks.mkdir()
        # Bundled Git omits dd/od; emulate their binary I/O only, not the parser.
        (mocks/'dd').write_bytes((f'#!/bin/sh\n"{unix(Path(sys.executable))}" -c \'import os; os.write(1,os.read(0,16))\'\n').encode())
        (mocks/'od').write_bytes((f'#!/bin/sh\n"{unix(Path(sys.executable))}" -c \'import sys,struct; b=open(sys.argv[-1],"rb").read(); print(*struct.unpack("<II",b[8:16])) if len(b)==16 else None\' "$@"\n').encode())
        (lock/'view-id').write_text('1\n')
        source=(ROOT/'package/dashboard/touch-reader.sh').read_text('utf-8')
        source=source.replace('/tmp/kindle-desk-always.lock',unix(lock))
        source=source.replace('/dev/input/event1',unix(ROOT/f'touch-results/touch-{step}.bin'))
        script=folder/'run.sh';script.write_bytes(source.encode())
        env=dict(os.environ);env['PATH']=str(mocks)+os.pathsep+str(BIN)+os.pathsep+env['PATH']
        result=subprocess.run([str(BIN/'dash.exe'),'-x',str(script)],env=env,capture_output=True,timeout=30)
        assert (lock/'action').exists(),result.stderr.decode(errors='replace')[-5000:]
        x,y,view=(lock/'action').read_text().split()
        assert abs(int(x)-expected[0])<35 and abs(int(y)-expected[1])<35,(x,y)
        assert view=='1'
        print(f'PASS: real capture {step} produces a released tap at the expected target')
