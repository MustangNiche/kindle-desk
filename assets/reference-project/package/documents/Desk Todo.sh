#!/bin/sh
# Name: Desk Todo - 同步待办信息屏
# Author: Personal Dashboard
# DontUseFBInk

# Explicitly launched offline session; temporarily inhibits automatic sleep.
BASE=/mnt/us/dashboard/live
LOG=/mnt/us/dashboard/todo.log
[ -d "$BASE" ] || exit 1
exec >>"$LOG" 2>&1
printf '\n=== TODO_REVISION=2 ===\n'
date
LOCK=/tmp/kindle-desk-always.lock
if ! mkdir "$LOCK" 2>/dev/null; then
    printf 'Already running (or stale lock); restart device if necessary.\n'
    exit 1
fi
PREVIOUS_SLEEP=
SLEEP_CHANGED=0
printf '%s\n' "$$" > "$LOCK/pid"
restore_network() {
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
    rm -f "$LOCK/touch-event" "$LOCK/event-read-pid" "$LOCK/input-event" "$LOCK/action" "$LOCK/action.tmp" "$LOCK/view-id" "$LOCK/drawing" "$LOCK/ack" "$LOCK/view.tar" "$LOCK/last.tar" "$LOCK/cached.tar" "$LOCK/network-reported"
    rm -f "$LOCK/new-view/tasks.png" "$LOCK/new-view/rows" "$LOCK/new-view/page"
    rmdir "$LOCK/new-view" 2>/dev/null
    rm -f "$LOCK/current/tasks.png" "$LOCK/current/rows" "$LOCK/current/page"
    rmdir "$LOCK/current" 2>/dev/null

}
finish() {
    result=$?
    trap - EXIT
    printf 'LIVE_EXIT=%s\n' "$result"
    date
    restore_ui
    if [ "$SLEEP_CHANGED" -eq 1 ]; then
        lipc-set-prop com.lab126.powerd preventScreenSaver "$PREVIOUS_SLEEP"
        printf 'Restored preventScreenSaver=%s\n' "$PREVIOUS_SLEEP"
    fi
    rm -f "$LOCK/fbink" "$LOCK/pid" "$LOCK/stop"
    rmdir "$LOCK"
    if command -v xrefresh >/dev/null 2>&1; then xrefresh -display :0.0; fi
}
trap finish EXIT
trap 'exit 0' INT TERM HUP
FBINK=/var/local/kmc/bin/fbink
if ! "$FBINK" --help >/dev/null 2>&1; then
    cp /mnt/us/libkh/bin/fbink "$LOCK/fbink" || exit 1
    chmod 700 "$LOCK/fbink" || exit 1
    FBINK="$LOCK/fbink"
    "$FBINK" --help >/dev/null 2>&1 || exit 1
fi
"$FBINK" --help > /mnt/us/dashboard/fbink-help.txt 2>&1
for svc in otaupd otav3 ota-update; do status "$svc" 2>/dev/null; done
# Confirm exact local timezone/date in the log, without adjusting device time.
date '+DEVICE_DATE=%Y-%m-%d %H:%M:%S %Z'
. "$BASE/positions.conf"
case "$STEAM_X" in ''|*[!0-9]*) printf 'ERROR: invalid STEAM_X\n'; exit 1;; esac
case "$STEAM_Y" in ''|*[!0-9]*) printf 'ERROR: invalid STEAM_Y\n'; exit 1;; esac
draw_patch() {
    "$FBINK" -q -g "file=$BASE/$1,x=$2,y=$3" || exit 1
}
update_battery() {
    level=$(lipc-get-prop com.lab126.powerd battLevel 2>/dev/null)
    case "$level" in ''|*[!0-9]*) level=unknown;; esac
    if [ "$level" != unknown ] && [ "$level" -gt 100 ]; then level=unknown; fi
    if [ "$level" != "$last_battery" ]; then
        draw_patch "battery/$level.png" 774 1357
        last_battery=$level
        printf 'BATTERY=%s\n' "$level"
    fi
}
clock_key() { date '+%H%M'; }
draw_day() {
    if [ ! -f "$BASE/day/$1-calendar.png" ]; then
        printf 'ERROR: calendar outside packaged range: %s\n' "$1"
        exit 1
    fi
    draw_patch "day/$1-anniversary.png" 650 64
    draw_patch "day/$1-calendar.png" 678 242
    draw_patch "day/$1-lunar.png" 58 413
    printf 'DAY=%s\n' "$1"
}
uptime_seconds() { cut -d. -f1 /proc/uptime; }
day=$(date '+%Y-%m-%d')
[ -f "$BASE/day/$day-calendar.png" ] || { printf 'ERROR: unsupported device date %s\n' "$day"; exit 1; }
# Fail closed if this firmware cannot provide a reversible keep-awake setting.
PREVIOUS_SLEEP=$(lipc-get-prop com.lab126.powerd preventScreenSaver) || exit 1
case "$PREVIOUS_SLEEP" in 0|1) ;; *) printf 'ERROR: unknown sleep property\n'; exit 1;; esac
SLEEP_CHANGED=1
lipc-set-prop com.lab126.powerd preventScreenSaver 1 || exit 1
actual=$(lipc-get-prop com.lab126.powerd preventScreenSaver) || exit 1
[ "$actual" = 1 ] || { printf 'ERROR: keep-awake verification failed\n'; exit 1; }
printf 'KEEP_AWAKE_VERIFIED=1 PREVIOUS=%s\n' "$PREVIOUS_SLEEP"
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
        restore_ui
        lipc-set-prop com.lab126.powerd preventScreenSaver "$PREVIOUS_SLEEP"
        rm -f "$LOCK/pid" "$LOCK/stop" "$LOCK/fbink"
        rmdir "$LOCK"
    fi
) </dev/null >/tmp/kindle-desk-watchdog.log 2>&1 &
sleep 2
# Paperwhite 3 touch device, confirmed against KOReader's model mapping.
[ -c /dev/input/event1 ] || { printf 'ERROR: touch exit unavailable\n'; exit 1; }
awesome_pid=$(pidof awesome)
case "$awesome_pid" in ''|*[!0-9]*) printf 'ERROR: ambiguous window manager\n'; exit 1;; esac
# Register restoration before changing either UI component.
touch "$LOCK/pillow-disabled"
lipc-set-prop com.lab126.pillow disableEnablePillow disable || exit 1
printf '%s\n' "$awesome_pid" > "$LOCK/awesome-pid"
kill -STOP "$awesome_pid" || exit 1
# Suppress automatic update services only for this network session.
# The watchdog disables Wi-Fi before restoring their prior running state.
status ota-update 2>/dev/null | grep -q 'stop/waiting' || exit 1
touch "$LOCK/network-active"
for service in otaupd otav3; do
    state=$(status "$service" 2>/dev/null)
    case "$state" in
        *start/running*) touch "$LOCK/restore-$service"; stop "$service";;
        *stop/waiting*) ;;
        *) printf 'ERROR: unknown update service state\n'; exit 1;;
    esac
    status "$service" 2>/dev/null | grep -q 'stop/waiting' || exit 1
done
lipc-set-prop com.lab126.cmd wirelessEnable 1 || exit 1
lipc-set-prop com.lab126.wifid enable 1 || exit 1
printf 'NETWORK_ENABLED_WITH_OTA_SERVICES_STOPPED=1\n'
"$FBINK" -q -f -c -g "file=/mnt/us/dashboard/todo/base.png,w=-1,h=-1" || exit 1
draw_day "$day"
minute=$(clock_key)
draw_patch "clock/$minute.png" 58 242
printf 'MINUTE=%s\n' "$minute"
last_battery=
update_battery
. /mnt/us/dashboard/todo-runtime.sh || exit 1
start=$(uptime_seconds)
frame=0
frame_count=0
while [ ! -f "$LOCK/stop" ]; do
    todo_action || exit 1
    [ ! -f "$LOCK/stop" ] || break
    if [ $((frame_count % 15)) -eq 0 ]; then todo_sync || exit 1; fi
    [ -d "$BASE" ] || break
    today=$(date '+%Y-%m-%d')
    if [ "$today" != "$day" ]; then draw_day "$today"; day=$today; fi
    now=$(clock_key)
    if [ "$now" != "$minute" ]; then
        draw_patch "clock/$now.png" 58 242
        minute=$now
        update_battery
        printf 'MINUTE=%s\n' "$minute"
    fi
    # Wait for each monochrome partial update and log actual renderer results.
    "$FBINK" -q -w -W DU -g "file=$BASE/steam/$frame.png,x=$STEAM_X,y=$STEAM_Y"
    steam_result=$?
    if [ "$steam_result" -ne 0 ]; then
        printf 'STEAM_ERROR=%s FRAME=%s\n' "$steam_result" "$frame"
    fi
    if [ $((frame_count % 60)) -eq 0 ]; then
        if [ "$(wc -c < "$LOG")" -gt 262144 ]; then : > "$LOG"; fi
        printf 'HEARTBEAT FRAMES=%s KEEP_AWAKE=%s\n' "$frame_count" "$(lipc-get-prop com.lab126.powerd preventScreenSaver)"
    fi
    [ "$steam_result" -eq 0 ] || exit "$steam_result"
    frame_count=$((frame_count + 1))
    frame=$(( (frame + 1) % 6 ))
    sleep 1
done
printf 'STEAM_FRAME_COUNT=%s\n' "$frame_count"
printf 'Always-on session stopped.\n'
exit 0
