# Session-only framebuffer rotation; the normal exit and watchdog both restore it.
ROTATION_PATH=/sys/class/graphics/fb0/rotate
# PW3 native framebuffer values verified on this device: normal=3, upside=1.
# Always select the desired orientation, including after a USB/forced exit.
NORMAL_ROTATION=3
UPSIDE_ROTATION=1
restore_rotation() {
    if [ -f "$LOCK/rotation-previous" ]; then
        previous_rotation=$(cat "$LOCK/rotation-previous")
        case "$previous_rotation" in
            0|1|2|3) printf '%s\n' "$previous_rotation" > "$ROTATION_PATH";;
            *) printf 'ROTATION_RESTORE_INVALID=1\n'; return 1;;
        esac
        [ "$(cat "$ROTATION_PATH")" = "$previous_rotation" ] || return 1
        rm -f "$LOCK/rotation-previous" "$LOCK/rotation-180"
        printf 'ROTATION_RESTORED=%s\n' "$previous_rotation"
    fi
}
start_rotation() {
    [ -r "$ROTATION_PATH" ] && [ -w "$ROTATION_PATH" ] || {
        printf 'ERROR: framebuffer rotation interface unavailable\n'; return 1;
    }
    previous_rotation=$(cat "$ROTATION_PATH")
    case "$previous_rotation" in 0|1|2|3) ;; *) return 1;; esac
    target_rotation=$UPSIDE_ROTATION
    printf '%s\n' "$NORMAL_ROTATION" > "$LOCK/rotation-previous" || return 1
    printf '%s\n' "$target_rotation" > "$ROTATION_PATH" || return 1
    actual_rotation=$(cat "$ROTATION_PATH")
    [ "$actual_rotation" = "$target_rotation" ] || {
        printf 'ERROR: rotation verification failed\n'; return 1;
    }
    touch "$LOCK/rotation-180" || return 1
    printf 'ROTATION_180_VERIFIED=1 PREVIOUS=%s CURRENT=%s\n' "$previous_rotation" "$actual_rotation"
}
