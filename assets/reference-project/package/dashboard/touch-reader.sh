#!/bin/sh
# PW3 little-endian 32-bit input_event; preserve the open evdev descriptor.
LOCK=/tmp/kindle-desk-always.lock
reader_child=
trap 'kill "$reader_child" 2>/dev/null; exit 0' TERM INT HUP
exec 3</dev/input/event1 || exit 1
active=0
x=0; y=0; first=0; moved=0; released=0
while [ -d "$LOCK" ]; do
    dd bs=16 count=1 <&3 > "$LOCK/input-event" 2>/dev/null &
    reader_child=$!
    printf '%s\n' "$reader_child" > "$LOCK/event-read-pid"
    wait "$reader_child" || exit 0
    set -- $(od -An -tu4 -j8 -N8 "$LOCK/input-event")
    [ "$#" -eq 2 ] || exit 1
    type=$(( $1 & 65535 )); code=$(( $1 >> 16 )); value=$2
    if [ "$type" -eq 1 ] && [ "$code" -eq 330 ]; then
        if [ "$value" -eq 1 ]; then
            active=1; first=1; moved=0; released=0
            view=$(cat "$LOCK/view-id" 2>/dev/null)
        else released=1; fi
    fi
    if [ "$type" -eq 3 ]; then
        case "$code" in
            53) x=$value;;
            54) y=$value;;
            47) [ "$value" -eq 0 ] || moved=1;;
        esac
    fi
    if [ "$type" -eq 0 ] && [ "$code" -eq 0 ] && [ "$active" -eq 1 ]; then
        if [ "$first" -eq 1 ]; then start_x=$x; start_y=$y; first=0; fi
        dx=$((x-start_x)); dy=$((y-start_y))
        if [ "$dx" -gt 30 ] || [ "$dx" -lt -30 ] || [ "$dy" -gt 30 ] || [ "$dy" -lt -30 ]; then moved=1; fi
        if [ "$released" -eq 1 ]; then
            drawing=0; queued=0
            [ ! -f "$LOCK/drawing" ] || drawing=1
            [ ! -f "$LOCK/action" ] || queued=1
            printf 'TOUCH_RELEASE X=%s Y=%s MOVED=%s DRAWING=%s QUEUED=%s\n' "$x" "$y" "$moved" "$drawing" "$queued"
            if [ "$moved" -eq 0 ] && [ ! -f "$LOCK/action" ] && [ ! -f "$LOCK/drawing" ]; then
                printf '%s %s %s\n' "$x" "$y" "$view" > "$LOCK/action.tmp"
                mv "$LOCK/action.tmp" "$LOCK/action"
            fi
            active=0; released=0
        fi
    fi
done
