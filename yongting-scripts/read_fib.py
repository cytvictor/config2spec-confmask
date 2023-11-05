import sys
import pandas as pd

with open(sys.argv[1], 'r') as fp:
  content = fp.read()
df = pd.DataFrame({'prefix': [], 'if': [], 'type': []})

router_fibs = {}
last_router = None
for l in content.splitlines():
  if l.startswith('# '):
    last_router = l.split('# ')[1]
    router_fibs[last_router] = []
  elif not l.startswith('#'):
    router_fibs[last_router].append(l)
    df.loc[len(df.index)] = [l.split(';')[0], l.split(';')[1], l.split(';')[2]]

print(df)
