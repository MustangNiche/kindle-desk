"""Generate a reversible 180-degree launcher without rebuilding private assets."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
source=(ROOT/'package/documents/Desk Upright.sh').read_text('utf-8')
source=source.replace('# Name: Desk Upright - 正向信息屏', '# Name: Desk Upside Down - 充电口朝上')
source=source.replace('DIRECT_REVISION=1','UPSIDE_DOWN_REVISION=2').replace('direct.log','upside-down.log')
old='restore_ui() {\n'
assert old in source
source=source.replace(old,'. /mnt/us/dashboard/screen-rotation.sh || exit 1\n'+old+'    restore_rotation\n',1)
old='"$FBINK" -q -f -c -g "file=/mnt/us/dashboard/direct/base.png,w=-1,h=-1"'
assert old in source
source=source.replace(old,'start_rotation || exit 1\n'+old,1)
(ROOT/'package/documents/Desk Upside Down.sh').write_bytes(source.encode('utf-8'))
(ROOT/'package/documents/Desk Direct.sh').write_bytes(source.replace('# Name: Desk Upside Down - 充电口朝上','# Name: Desk Direct - 充电口朝上').encode('utf-8'))
assert source.index('restore_rotation') < source.index('while [ -d "/proc/$MAIN_PID" ]')
print('Built reversible upside-down launcher with watchdog restoration.')
