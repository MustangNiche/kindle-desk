"""Build an opt-in Todoist launcher; preserve the working offline launcher."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
DOC=ROOT/'package/documents'
source=(DOC/'Desk Always On.sh').read_text('utf-8')
source=source.replace('# Name: Desk Always On - 常驻信息屏','# Name: Desk Todo - 同步待办信息屏')
source=source.replace('ALWAYS_ON_REVISION=2','TODO_REVISION=2').replace('always-on.log','todo.log')
source=source.replace('file=$BASE/base-always.png','file=/mnt/us/dashboard/todo/base.png')
source=source.replace('restore_ui() {','''restore_network() {
    if [ -f "$LOCK/network-active" ]; then
        lipc-set-prop com.lab126.wifid enable 0
        lipc-set-prop com.lab126.cmd wirelessEnable 0
        if [ "$(lipc-get-prop com.lab126.wifid enable 2>/dev/null)" = 0 ]; then
            for service in otaupd otav3; do
                if [ -f "$LOCK/restore-$service" ]; then start "$service"; fi
            done
        fi
        rm -f "$LOCK/network-active" "$LOCK/restore-otaupd" "$LOCK/restore-otav3"
    fi
}
restore_ui() {
    restore_network
    if [ -f "$LOCK/event-read-pid" ]; then kill "$(cat "$LOCK/event-read-pid")" 2>/dev/null; fi
''')
source=source.replace('    rm -f "$LOCK/touch-event"','''    rm -f "$LOCK/touch-event" "$LOCK/event-read-pid" "$LOCK/input-event" "$LOCK/action" "$LOCK/action.tmp" "$LOCK/view-id" "$LOCK/drawing" "$LOCK/ack" "$LOCK/view.tar" "$LOCK/last.tar" "$LOCK/cached.tar" "$LOCK/network-reported"
    rm -f "$LOCK/new-view/tasks.png" "$LOCK/new-view/rows" "$LOCK/new-view/page"
    rmdir "$LOCK/new-view" 2>/dev/null
    rm -f "$LOCK/current/tasks.png" "$LOCK/current/rows" "$LOCK/current/page"
    rmdir "$LOCK/current" 2>/dev/null
''')
start=source.index('dd if=/dev/input/event1')
end=source.index('"$FBINK" -q -f -c',start)
source=source[:start]+'''# Suppress automatic update services only for this network session.
# The watchdog disables Wi-Fi before restoring their prior running state.
status ota-update 2>/dev/null | grep -q 'stop/waiting' || exit 1
touch "$LOCK/network-active"
for service in otaupd otav3; do
    state=$(status "$service" 2>/dev/null)
    case "$state" in
        *start/running*) touch "$LOCK/restore-$service"; stop "$service";;
        *stop/waiting*) ;;
        *) printf 'ERROR: unknown update service state\\n'; exit 1;;
    esac
    status "$service" 2>/dev/null | grep -q 'stop/waiting' || exit 1
done
lipc-set-prop com.lab126.cmd wirelessEnable 1 || exit 1
lipc-set-prop com.lab126.wifid enable 1 || exit 1
printf 'NETWORK_ENABLED_WITH_OTA_SERVICES_STOPPED=1\\n'
''' + source[end:]
source=source.replace('start=$(uptime_seconds)', '. /mnt/us/dashboard/todo-runtime.sh || exit 1\nstart=$(uptime_seconds)')
source=source.replace('    [ ! -s "$LOCK/touch-event" ] || break','''    todo_action || exit 1
    [ ! -f "$LOCK/stop" ] || break
    if [ $((frame_count % 15)) -eq 0 ]; then todo_sync || exit 1; fi''')
(DOC/'Desk Todo.sh').write_bytes(source.encode('utf-8'))
out=ROOT/'todo-service/private/kindle'
out.mkdir(parents=True,exist_ok=True)
base=Image.open(ROOT/'package/dashboard/live/base-always.png').copy()
draw=ImageDraw.Draw(base)
draw.rectangle((58,1350,760,1410),fill=255)
font=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',23)
draw.text((58,1364),'点此退出',font=font,fill=0,anchor='lt')
draw.text((300,1364),'天气为示例 · 待办可勾选',font=font,fill=0,anchor='lt')
base.save(out/'base.png')
Image.new('L',(1072,48),255).save(out/'blank-row.png')
pending=Image.new('L',(190,62),255)
pd=ImageDraw.Draw(pending)
pd.text((50,20),'待同步',font=font,fill=0,anchor='lt')
pending.save(out/'pending.png')
for name,label in [('offline','未连接电脑 · 天气为示例'),('online','已连接电脑 · 天气为示例')]:
    notice=Image.new('L',(460,48),255)
    ImageDraw.Draw(notice).text((0,7),label,font=font,fill=0,anchor='lt')
    notice.save(out/f'{name}.png')
print('Built separate Todoist launcher; Wi-Fi turns off on exit.')
