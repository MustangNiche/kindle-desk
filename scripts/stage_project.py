"""Copy a reference source project into a NEW directory; never touch a Kindle."""
import argparse,shutil
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--destination',type=Path,required=True)
a=p.parse_args()
source=Path(__file__).resolve().parents[1]/'assets/reference-project'
if a.destination.exists():p.error('Destination exists; choose a new folder to preserve existing work.')
shutil.copytree(source,a.destination)
print('Reference source staged. Configure fonts, device, credentials, vocabulary and generated assets before installation.')
