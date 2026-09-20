def add_gre(source):
    if '/mnt/us/dashboard/gre-update.lua' in source:
        return source
    init='. /mnt/us/dashboard/direct-runtime.sh || exit 1'
    minute='        minute=$now\n        update_battery'
    assert init in source and minute in source
    source=source.replace(init,init+'\nlua /mnt/us/dashboard/gre-update.lua "$FBINK" || exit 1',1)
    source=source.replace(minute,minute+'\n        lua /mnt/us/dashboard/gre-update.lua "$FBINK" || exit 1',1)
    source=source.replace('restore_ui() {\n','restore_ui() {\n    rm -f "$LOCK/gre-day"\n',1)
    # Check the local clock/word before starting another potentially slow request.
    poll='    if [ $((frame_count % 15)) -eq 0 ]; then todo_sync || exit 1; fi\n'
    assert poll in source
    source=source.replace(poll,'',1)
    marker='    # Wait for each monochrome partial update and log actual renderer results.'
    assert marker in source
    return source.replace(marker,poll+marker,1)
