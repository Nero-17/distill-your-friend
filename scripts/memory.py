"""Local source-aware episodic retrieval and session persistence; standard library only."""
import argparse,collections,json,math,re
from pathlib import Path
ROOT=None
REPO=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def tokens(t):
    t=re.sub(r'[^\w\u4e00-\u9fff]','',t.lower());return set(t[i:i+2] for i in range(len(t)-1))
def retrieve(query,before,limit=4):
    if not isinstance(before,(int,float)) or isinstance(before,bool) or before<=0:raise ValueError('before must be a positive Unix timestamp')
    allrows=read(ROOT/'episodes.json');observations=ROOT/'observations.jsonl'
    if observations.exists():allrows += [json.loads(l) for l in observations.read_text(encoding='utf-8').splitlines() if l.strip()]
    eligible=[x for x in allrows if x['end_time']<before]
    superseded={x['supersedes'] for x in eligible if x.get('supersedes')}
    rows=[x for x in eligible if x['id'] not in superseded]
    sets=[tokens(' '.join(m['text'] for m in e['messages'])) for e in rows]
    df=collections.Counter(t for ts in sets for t in ts);q=tokens(query);rank=[]
    for e,ts in zip(rows,sets):
        common=q&ts
        if len(common)<2:continue
        score=sum(math.log(1+len(rows)/(1+df[t])) for t in common)/math.sqrt(max(1,len(ts)))
        rank.append((score,e))
    rank.sort(key=lambda x:-x[0]);result=[]
    for score,e in rank:
        if any(e['date']==x['date'] and abs(e['end_time']-x['end_time'])<1200 for x in result):continue
        result.append(dict(**e,retrieval_score=round(score,4)))
        if len(result)>=limit:break
    return result
def remember(x):
    if x.get('source') not in ['user_message','user_correction']:raise ValueError('Only source-attributed user observations may enter real memory')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',x.get('id','')):raise ValueError('Invalid id')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',x.get('date','')):raise ValueError('Invalid date')
    if not isinstance(x.get('end_time'),(int,float)) or not x.get('messages'):raise ValueError('Timestamp and messages required')
    for m in x['messages']:
        if not isinstance(m.get('text'),str) or not m.get('speaker') or not isinstance(m.get('timestamp'),(int,float)):raise ValueError('Each source message needs text, speaker and timestamp')
        if m['timestamp']>x['end_time']:raise ValueError('Source time exceeds record time')
        if re.search(r'https?://|密码|验证码|password|api[_ -]?key|\b\d{9,}\b',m['text'],re.I):raise ValueError('Remove sensitive values before storing')
    ROOT.mkdir(parents=True,exist_ok=True);p=ROOT/'observations.jsonl'
    existing=read(ROOT/'episodes.json')+([json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()] if p.exists() else [])
    if x['id'] in {e['id'] for e in existing}:raise ValueError('Duplicate id')
    if x.get('supersedes') and x['supersedes'] not in {e['id'] for e in existing}:raise ValueError('Unknown superseded record')
    with p.open('a',encoding='utf-8') as f:f.write(json.dumps(x,ensure_ascii=False)+'\n')
    return {'saved':x['id'],'source':x['source']}
def main():
    global ROOT
    p=argparse.ArgumentParser();p.add_argument('--store',type=Path,required=True);p.add_argument('command',choices=['retrieve','remember','state']);p.add_argument('--input',type=Path,required=True);p.add_argument('--session');a=p.parse_args();x=read(a.input)
    ROOT=a.store.resolve()
    if ROOT==REPO or REPO in ROOT.parents:raise ValueError('Private memory store must be outside the skill repository')
    if a.command=='retrieve':result=retrieve(x['query'],x['before'],max(1,min(10,int(x.get('limit',4)))))
    elif a.command=='remember':result=remember(x)
    else:
        if not a.session or not re.fullmatch(r'[A-Za-z0-9_-]{1,60}',a.session):raise ValueError('Safe session name required')
        d=ROOT/'sessions';d.mkdir(parents=True,exist_ok=True);(d/(a.session+'.json')).write_text(json.dumps(dict(source='synthetic_session',state=x),ensure_ascii=False,indent=2),encoding='utf-8');result={'session':a.session,'source':'synthetic_session'}
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
