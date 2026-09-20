DIRECT=/mnt/us/dashboard/direct-client.lua
lua "$DIRECT" init "$FBINK" || exit 1
sh /mnt/us/dashboard/touch-reader.sh &
printf '%s\n' "$!" > "$LOCK/touch-pid"
todo_action() {
    [ -f "$LOCK/action" ] || return 0
    lua "$DIRECT" action "$FBINK"
}
todo_sync() {
    lua "$DIRECT" sync "$FBINK"
}
