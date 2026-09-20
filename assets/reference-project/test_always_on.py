"""Exercise keep-awake lifecycle with fake device commands in isolated folders."""
import os
import subprocess
import tempfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BIN=Path('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/usr/bin')
source=(ROOT/'package/documents/Desk Always On.sh').read_text(encoding='utf-8')
def unix(path):
    p=path.resolve().as_posix()
    return '/'+p[0].lower()+p[2:]

for previous, failure in [('0','none'),('1','none'),('0','draw'),('0','set'),('0','kill'),('0','pillow'),('0','touch')]:
    with tempfile.TemporaryDirectory(dir=ROOT,prefix='power-test-') as tmp:
        folder=Path(tmp);base=folder/'live';base.mkdir();(base/'day').mkdir()
        (base/'day/2026-09-17-calendar.png').touch()
        (base/'positions.conf').write_bytes(b'STEAM_X=279\nSTEAM_Y=486\n')
        (folder/'state').write_text(previous)
        (folder/'awesome-comm').write_bytes(b'awesome\n')
        (folder/'touch-input').touch()
        (folder/'ui').write_text('running')
        (folder/'pillow').write_text('enable')
        mocks=folder/'bin';mocks.mkdir()
        commands={
            'lipc-get-prop':'if [ "$2" = battLevel ]; then echo 78; else cat "$TEST_ROOT/state"; fi',
            'lipc-set-prop':'''if [ "$2" = disableEnablePillow ]; then
    if [ "$FAILURE" = pillow ] && [ "$3" = disable ]; then exit 1; fi
    printf '%s' "$3" > "$TEST_ROOT/pillow"; exit 0
fi
if [ "$FAILURE" = set ] && [ "$3" = 1 ]; then exit 1; fi
printf '%s' "$3" > "$TEST_ROOT/state"''',
            'pidof':'echo 999999',
            'mock-signal':'if [ "$1" = -STOP ]; then echo paused > "$TEST_ROOT/ui"; else echo running > "$TEST_ROOT/ui"; fi',
            'dd':f'exec "{unix(BIN/"sleep.exe")}" 5',
            'date':'''case "$1" in '+%Y-%m-%d') echo 2026-09-17;; '+%H%M') echo 1500;; *) echo simulated-date;; esac''',
            'sleep':f'"{unix(BIN/"sleep.exe")}" 0.02',
            'status':'exit 0',
            'xrefresh':'exit 0',
            'fbink':'''case "$*" in *steam/*)
    [ "$FAILURE" = draw ] && exit 1
    if [ "$FAILURE" = kill ]; then touch "$TEST_ROOT/ready"; exit 0; fi
    if [ "$FAILURE" = touch ]; then printf touched > "$TEST_ROOT/lock/touch-event"; exit 0; fi
    touch "$TEST_ROOT/lock/stop";; esac
exit 0''',
        }
        for name,body in commands.items():
            (mocks/name).write_bytes(('#!/bin/sh\n'+body+'\n').encode())
        script=source.replace('/mnt/us/dashboard/live',unix(base)).replace('/mnt/us/dashboard',unix(folder))
        script=script.replace('/tmp/kindle-desk-always.lock',unix(folder/'lock'))
        script=script.replace('/tmp/kindle-desk-watchdog.log',unix(folder/'watchdog.log'))
        script=script.replace('/var/local/kmc/bin/fbink',unix(mocks/'fbink'))
        script=script.replace('[ -c /dev/input/event1 ]','[ -f "$TEST_ROOT/touch-input" ]')
        script=script.replace('"/proc/$awesome_pid/comm"','"$TEST_ROOT/awesome-comm"')
        script=script.replace('kill -STOP','mock-signal -STOP').replace('kill -CONT','mock-signal -CONT')
        path=folder/'run.sh';path.write_bytes(script.encode('utf-8'))
        env=os.environ.copy();env.update(TEST_ROOT=unix(folder),FAILURE=failure)
        env['PATH']=str(mocks)+os.pathsep+str(BIN)+os.pathsep+env['PATH']
        if failure=='kill':
            process=subprocess.Popen([str(BIN/'dash.exe'),str(path)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            deadline=time.monotonic()+10
            while not (folder/'ready').exists() and time.monotonic()<deadline:
                time.sleep(.05)
            assert (folder/'ready').exists()
            pid=(folder/'lock/pid').read_text().strip()
            subprocess.run([str(BIN/'dash.exe'),'-c',f'kill -9 {int(pid)}'],env=env,check=True)
            process.wait(timeout=5)
            while (folder/'lock').exists() and time.monotonic()<deadline:
                time.sleep(.05)
            result=None
        else:
            result=subprocess.run([str(BIN/'dash.exe'),str(path)],env=env,capture_output=True,timeout=15)
        log=(folder/'always-on.log').read_text(encoding='utf-8',errors='replace')
        assert (folder/'state').read_text()==previous,(failure,log)
        assert not (folder/'lock').exists(),log
        assert (folder/'ui').read_text().strip()=='running',log
        assert (folder/'pillow').read_text()=='enable',log
        if result is not None:
            assert result.returncode==(0 if failure in ('none','touch') else 1),(result,log)
        print('PASS:',previous,failure,'sleep setting restored; lock cleaned')
