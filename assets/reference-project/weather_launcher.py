def add_weather(source):
    if '/mnt/us/dashboard/weather-update.lua' in source:return source
    init='lua /mnt/us/dashboard/gre-update.lua "$FBINK" || exit 1'
    assert source.count(init)==2
    lines=[]
    for line in source.splitlines():
        lines.append(line)
        if line.strip()==init:
            indent=line[:len(line)-len(line.lstrip())]
            lines.append(indent+'lua /mnt/us/dashboard/weather-update.lua "$FBINK" || printf "WEATHER_UPDATE_ERROR=1\\n"')
    result='\n'.join(lines)+'\n'
    return result.replace('restore_ui() {\n','restore_ui() {\n    rm -f "$LOCK/weather-view" "$LOCK/weather-view.next" "$LOCK/weather-response.json"\n',1)
