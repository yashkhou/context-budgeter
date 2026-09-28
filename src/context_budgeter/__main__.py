import argparse,json
from .core import allocate
p=argparse.ArgumentParser(); p.add_argument('file'); p.add_argument('--budget',type=int,required=True); a=p.parse_args(); print(json.dumps(allocate(json.load(open(a.file)),a.budget),indent=2))
