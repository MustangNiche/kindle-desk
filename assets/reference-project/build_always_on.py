"""Build an explicitly launched, reversible, offline always-on dashboard."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
DOC=ROOT/'package/documents'
source=(DOC/'Desk Live Test.sh').read_text(encoding='utf-8')
def replace(old,new):
    global source
    assert old in source, old
    source=source.replace(old,new)

replace('# Name: Desk Live - 3 minute test','# Name: Desk Always On - 常驻信息屏')
replace('# Bounded offline trial: no service, sleep, system clock, or network changes.',
        '# Explicitly launched offline session; temporarily inhibits automatic sleep.')
replace('live-test.log','always-on.log')
replace('LIVE_TEST_REVISION=3','ALWAYS_ON_REVISION=2')
replace('/tmp/kindle-desk-live.lock','/tmp/kindle-desk-always.lock')
replace('finish() {','PREVIOUS_SLEEP=\nSLEEP_CHANGED=0\nprintf \'%s\\n\' "$$" > "$LOCK/pid"\nfinish() {')
replace('    rm -f "$LOCK/fbink"', '''    if [ "$SLEEP_CHANGED" -eq 1 ]; then
        lipc-set-prop com.lab126.powerd preventScreenSaver "$PREVIOUS_SLEEP"
        printf 'Restored preventScreenSaver=%s\\n' "$PREVIOUS_SLEEP"
    fi
    rm -f "$LOCK/fbink" "$LOCK/pid" "$LOCK/stop"''')
replace('sleep 2\n"$FBINK"', '''# Fail closed if this firmware cannot provide a reversible keep-awake setting.
PREVIOUS_SLEEP=$(lipc-get-prop com.lab126.powerd preventScreenSaver) || exit 1
case "$PREVIOUS_SLEEP" in 0|1) ;; *) printf 'ERROR: unknown sleep property\\n'; exit 1;; esac
SLEEP_CHANGED=1
lipc-set-prop com.lab126.powerd preventScreenSaver 1 || exit 1
actual=$(lipc-get-prop com.lab126.powerd preventScreenSaver) || exit 1
[ "$actual" = 1 ] || { printf 'ERROR: keep-awake verification failed\\n'; exit 1; }
printf 'KEEP_AWAKE_VERIFIED=1 PREVIOUS=%s\\n' "$PREVIOUS_SLEEP"
# The library launcher may use SIGKILL when leaving the app. An independent
# watchdog restores the temporary property even when EXIT cannot run.
MAIN_PID=$$
(
    trap '' HUP
    while [ -d "/proc/$MAIN_PID" ]; do
        [ "$(cat "$LOCK/pid" 2>/dev/null)" = "$MAIN_PID" ] || exit 0
        sleep 2
    done
    if [ "$(cat "$LOCK/pid" 2>/dev/null)" = "$MAIN_PID" ]; then
        lipc-set-prop com.lab126.powerd preventScreenSaver "$PREVIOUS_SLEEP"
        rm -f "$LOCK/pid" "$LOCK/stop" "$LOCK/fbink"
        rmdir "$LOCK"
    fi
) </dev/null >/tmp/kindle-desk-watchdog.log 2>&1 &
sleep 2
"$FBINK"''')
replace('file=$BASE/base.png','file=$BASE/base-always.png')
replace('while [ $(( $(uptime_seconds) - start )) -lt 180 ]; do',
        'while [ ! -f "$LOCK/stop" ]; do')
replace('    printf \'STEAM_FRAME=%s RESULT=%s ELAPSED=%s\\n\' "$frame" "$steam_result" "$(( $(uptime_seconds) - start ))"',
'''    if [ "$steam_result" -ne 0 ]; then
        printf 'STEAM_ERROR=%s FRAME=%s\\n' "$steam_result" "$frame"
    fi
    if [ $((frame_count % 60)) -eq 0 ]; then
        if [ "$(wc -c < "$LOG")" -gt 262144 ]; then : > "$LOG"; fi
        printf 'HEARTBEAT FRAMES=%s KEEP_AWAKE=%s\\n' "$frame_count" "$(lipc-get-prop com.lab126.powerd preventScreenSaver)"
    fi''')
replace("printf 'Completed bounded 180-second trial.\\n'", "printf 'Always-on session stopped.\\n'")
# Restore UI both on normal exit and in the independent SIGKILL watchdog.
replace('finish() {', '''restore_ui() {
    if [ -f "$LOCK/touch-pid" ]; then
        touch_pid=$(cat "$LOCK/touch-pid")
        kill "$touch_pid" 2>/dev/null
        rm -f "$LOCK/touch-pid"
    fi
    if [ -f "$LOCK/awesome-pid" ]; then
        awesome_pid=$(cat "$LOCK/awesome-pid")
        if [ "$(cat "/proc/$awesome_pid/comm" 2>/dev/null)" = awesome ]; then
            kill -CONT "$awesome_pid"
        fi
        rm -f "$LOCK/awesome-pid"
    fi
    if [ -f "$LOCK/pillow-disabled" ]; then
        lipc-set-prop com.lab126.pillow disableEnablePillow enable
        rm -f "$LOCK/pillow-disabled"
    fi
    rm -f "$LOCK/touch-event"
}
finish() {''')
replace('    if [ "$SLEEP_CHANGED" -eq 1 ]; then', '    restore_ui\n    if [ "$SLEEP_CHANGED" -eq 1 ]; then')
replace('        lipc-set-prop com.lab126.powerd preventScreenSaver "$PREVIOUS_SLEEP"\n        rm -f',
        '        restore_ui\n        lipc-set-prop com.lab126.powerd preventScreenSaver "$PREVIOUS_SLEEP"\n        rm -f')
replace('sleep 2\n"$FBINK"', '''sleep 2
# Paperwhite 3 touch device, confirmed against KOReader's model mapping.
[ -c /dev/input/event1 ] || { printf 'ERROR: touch exit unavailable\\n'; exit 1; }
awesome_pid=$(pidof awesome)
case "$awesome_pid" in ''|*[!0-9]*) printf 'ERROR: ambiguous window manager\\n'; exit 1;; esac
# Register restoration before changing either UI component.
touch "$LOCK/pillow-disabled"
lipc-set-prop com.lab126.pillow disableEnablePillow disable || exit 1
printf '%s\\n' "$awesome_pid" > "$LOCK/awesome-pid"
kill -STOP "$awesome_pid" || exit 1
dd if=/dev/input/event1 of="$LOCK/touch-event" bs=16 count=1 2>/dev/null &
printf '%s\\n' "$!" > "$LOCK/touch-pid"
printf 'SYSTEM_UI_PAUSED=1 TOUCH_TO_EXIT=1\\n'
"$FBINK"''')
replace('clock_key() {', '''update_battery() {
    level=$(lipc-get-prop com.lab126.powerd battLevel 2>/dev/null)
    case "$level" in ''|*[!0-9]*) level=unknown;; esac
    if [ "$level" != unknown ] && [ "$level" -gt 100 ]; then level=unknown; fi
    if [ "$level" != "$last_battery" ]; then
        draw_patch "battery/$level.png" 774 1357
        last_battery=$level
        printf 'BATTERY=%s\\n' "$level"
    fi
}
clock_key() {''')
replace('start=$(uptime_seconds)', 'last_battery=\nupdate_battery\nstart=$(uptime_seconds)')
replace('while [ ! -f "$LOCK/stop" ]; do', '''while [ ! -f "$LOCK/stop" ]; do
    [ ! -s "$LOCK/touch-event" ] || break
    [ -d "$BASE" ] || break''')
replace('        minute=$now', '        minute=$now\n        update_battery')
(DOC/'Desk Always On.sh').write_bytes(source.encode('utf-8'))
base=Image.open(ROOT/'package/dashboard/live/base.png').copy()
draw=ImageDraw.Draw(base)
draw.rectangle((58,1350,860,1410),fill=255)
draw.text((58,1364),'轻触退出 · 天气/待办为示例',font=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',23),fill=0,anchor='lt')
base.save(ROOT/'package/dashboard/live/base-always.png')
battery_dir=ROOT/'package/dashboard/live/battery'
battery_dir.mkdir(exist_ok=True)
for level in list(range(101))+['unknown']:
    patch=Image.new('L',(120,48),255);pd=ImageDraw.Draw(patch)
    label='--%' if level=='unknown' else f'{level}%'
    font=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',23)
    l,t,r,b=pd.textbbox((0,0),label,font=font)
    # Keep an 8px optical gap at every percentage, with the group right aligned.
    icon_x=118-(r-l)-8-38
    pd.rectangle((icon_x,16,icon_x+34,33),outline=0,width=2)
    pd.rectangle((icon_x+35,21,icon_x+38,28),fill=0)
    if level!='unknown' and level>0:
        pd.rectangle((icon_x+4,20,icon_x+4+round(26*level/100),29),fill=0)
    pd.text((118-r,round((48-b+t)/2-t)),label,font=font,fill=0)
    patch.save(battery_dir/f'{level}.png')
preview=base.copy();preview.paste(Image.open(battery_dir/'78.png'),(774,1357))
preview.resize((536,724),Image.Resampling.LANCZOS).save(ROOT/'always-on-battery-preview.png')
assert '-lt 180' not in source
assert 'KEEP_AWAKE_VERIFIED=1' in source
assert b'\r' not in (DOC/'Desk Always On.sh').read_bytes()
print('Built always-on launcher and background; temporary sleep inhibition with cleanup watchdog.')
