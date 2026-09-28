import re
from collections import defaultdict
def estimate(text): return max(1,(len(text)+3)//4)
def similarity(a,b):
 A=set(re.findall(r'[a-z0-9]+',a.lower())); B=set(re.findall(r'[a-z0-9]+',b.lower())); return len(A&B)/max(1,len(A|B))
def duplicates(chunks,threshold=.8):
 out=[]
 for i,a in enumerate(chunks):
  for j in range(i+1,len(chunks)):
   s=similarity(a['text'],chunks[j]['text'])
   if s>=threshold: out.append({'a':a['id'],'b':chunks[j]['id'],'similarity':round(s,3)})
 return out
def collisions(chunks):
 facts=defaultdict(set)
 for c in chunks:
  m=re.match(r'\s*(allow|deny)\s+(.+?)\s*$',c['text'],re.I)
  if m:facts[m.group(2).lower()].add(m.group(1).lower())
 return [{'subject':k,'decisions':sorted(v)} for k,v in facts.items() if len(v)>1]
def allocate(chunks,budget):
 rows=[{**c,'estimated_tokens':estimate(c['text'])} for c in chunks]; used=0; selected=[]
 for c in sorted(rows,key=lambda x:(-int(x.get('priority',0)),x['id'])):
  reserve=min(int(c.get('reserve',0)),c['estimated_tokens']); take=min(c['estimated_tokens'],max(reserve,budget-used)) if used<budget else 0
  if take and used+take<=budget: selected.append({**c,'allocated_tokens':take}); used+=take
 return {'budget':budget,'used':used,'remaining':budget-used,'selected':selected,'duplicates':duplicates(rows),'policy_collisions':collisions(rows),'by_source':_by_source(rows)}
def _by_source(rows):
 d=defaultdict(int)
 for r in rows:d[r.get('source','unknown')]+=r['estimated_tokens']
 return dict(sorted(d.items()))
