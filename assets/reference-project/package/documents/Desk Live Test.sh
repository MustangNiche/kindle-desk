#!/bin/sh
# Name: Desk Live - 3 minute test
# Author: Personal Dashboard
# DontUseFBInk

# Bounded offline trial: no service, sleep, system clock, or network changes.
BASE=/mnt/us/dashboard/live
LOG=/mnt/us/dashboard/live-test.log
[ -d "$BASE" ] || exit 1
exec >>"$LOG" 2>&1
printf '\n=== LIVE_TEST_REVISION=3 ===\n'
date
LOCK=/tmp/kindle-desk-live.lock
if ! mkdir "$LOCK" 2>/dev/null; then
    printf 'Already running (or stale lock); restart device if necessary.\n'
    exit 1
fi
finish() {
    result=$?
    trap - EXIT
    printf 'LIVE_EXIT=%s\n' "$result"
    date
    rm -f "$LOCK/fbink"
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
sleep 2
"$FBINK" -q -f -c -g "file=$BASE/base.png,w=-1,h=-1" || exit 1
draw_day "$day"
minute=$(clock_key)
draw_patch "clock/$minute.png" 58 242
printf 'MINUTE=%s\n' "$minute"
start=$(uptime_seconds)
frame=0
frame_count=0
while [ $(( $(uptime_seconds) - start )) -lt 180 ]; do
    today=$(date '+%Y-%m-%d')
    if [ "$today" != "$day" ]; then draw_day "$today"; day=$today; fi
    now=$(clock_key)
    if [ "$now" != "$minute" ]; then
        draw_patch "clock/$now.png" 58 242
        minute=$now
        printf 'MINUTE=%s\n' "$minute"
    fi
    # Wait for each monochrome partial update and log actual renderer results.
    "$FBINK" -q -w -W DU -g "file=$BASE/steam/$frame.png,x=$STEAM_X,y=$STEAM_Y"
    steam_result=$?
    printf 'STEAM_FRAME=%s RESULT=%s ELAPSED=%s\n' "$frame" "$steam_result" "$(( $(uptime_seconds) - start ))"
    [ "$steam_result" -eq 0 ] || exit "$steam_result"
    frame_count=$((frame_count + 1))
    frame=$(( (frame + 1) % 6 ))
    sleep 1
done
printf 'STEAM_FRAME_COUNT=%s\n' "$frame_count"
printf 'Completed bounded 180-second trial.\n'
exit 0
