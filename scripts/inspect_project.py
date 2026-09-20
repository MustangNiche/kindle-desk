"""Read-only dashboard inventory. Does not read credentials or task content."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--project',type=Path,required=True)
p.add_argument('--device',type=Path)
a=p.parse_args();root=a.project/'package'
def inspect(root):
    report={'root':str(root.resolve()),'files':{},'launchers':{}}
    for name in ['direct-client.lua','direct-core.lua','direct-geometry.lua','touch-reader.sh','screen-rotation.sh','gre-schedule.lua','weather-update.lua','weather-core.lua','live/base-always.png','direct/base.png','direct/song.ttf','direct/ca.pem','direct/project.json','direct/curl.conf','weather/blank.png','weather/serif.ttf']:
        report['files'][name]=(root/'dashboard'/name).is_file()
    for name in ['Desk Direct.sh','Desk Upside Down.sh','Desk Upright.sh']:
        file=root/'documents'/name
        if not file.is_file():report['launchers'][name]={'present':False};continue
        content=file.read_bytes()
        report['launchers'][name]={'present':True,'LF_only':b'\r' not in content,'gre_hooks':content.count(b'lua /mnt/us/dashboard/gre-update.lua'),'weather_hooks':content.count(b'lua /mnt/us/dashboard/weather-update.lua'),'fixed_rotation_module':b'screen-rotation.sh' in content}
    for area in ['gre','live']:
        path=root/'dashboard'/area/'manifest.json'
        if path.is_file():
            try:
                m=json.loads(path.read_text('utf-8'))
                if area=='gre':
                    n=m.get('count',0);order=m.get('order',[])
                    report['gre']={'count':n,'permutation_valid':isinstance(n,int) and sorted(order)==list(range(1,n+1)),'missing_cards':sum(not (path.parent/f'{i:03d}.png').is_file() for i in range(1,n+1))}
                else:report['date_coverage']={k:m.get(k) for k in ['start','end','day_count']}
            except (ValueError,TypeError):report[area]={'manifest_valid':False}
    return report
result={'project':inspect(root)}
private=a.project/'todo-service/private/direct'
if private.is_dir():
    result['local_private_asset_presence']={name:(private/name).is_file() for name in ['base.png','tasks-empty.png','song.ttf','ca.pem','project.json','curl.conf','initial.json']}
if a.device:result['device']=inspect(a.device)
print(json.dumps(result,ensure_ascii=False,indent=2))
