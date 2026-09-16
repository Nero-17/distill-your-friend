"""Prepare private, grouped data and training-only memory. No model or network calls."""
import argparse, datetime, json, math, random, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

def external(path):
    path = Path(path).resolve()
    if path == REPO or REPO in path.parents:
        raise ValueError('Private output must be outside the skill repository')
    return path

def prepare(source, output, seed=17):
    output = external(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use an empty private output directory')
    raw = json.loads(Path(source).read_text(encoding='utf-8-sig'))['messages']
    seen = {}; groups = {}; removed = 0
    sessions = [bool(m.get('session_id')) for m in raw]
    if any(sessions) and not all(sessions):
        raise ValueError('session_id must be provided for every message or none')
    for m in raw:
        if not all(isinstance(m.get(k), str) and m[k] for k in ['id', 'speaker', 'text']):
            raise ValueError('id, speaker and text must be nonempty strings')
        t = m.get('timestamp')
        if isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) or not 0 < t < 100_000_000_000:
            raise ValueError('timestamp must be finite Unix seconds')
        if m.get('quote') is not None and not isinstance(m['quote'], str):
            raise ValueError('quote must be a string or null')
        if m['id'] in seen:
            if seen[m['id']] != m:
                raise ValueError('Conflicting duplicate message id')
            continue
        seen[m['id']] = m
        content = m['text'] + ' ' + (m.get('quote') or '')
        if re.search(r'https?://|password|api[_ -]?key|密码|验证码|[\w.+-]+@[\w.-]+\.\w+|\b\d{9,}\b', content, re.I):
            removed += 1
            continue
        day = datetime.datetime.fromtimestamp(t, datetime.timezone.utc).date().isoformat()
        key = m.get('session_id') or day
        if not isinstance(key, str):
            raise ValueError('session_id must be a string')
        groups.setdefault(key, []).append(dict(m, date=day))
    keys = sorted(groups)
    if len(keys) < 10:
        raise ValueError('Need at least ten usable groups; choose a manual split for smaller inputs')
    random.Random(seed).shuffle(keys)
    a = int(len(keys) * .75); b = min(len(keys)-1, a + max(1, int(len(keys)*.15)))
    split = dict(train=keys[:a], dev=keys[a:b], test=keys[b:])
    output.mkdir(parents=True, exist_ok=True)
    counts = {}; episodes = []
    for name, selected in split.items():
        messages = sorted((m for k in selected for m in groups[k]), key=lambda m:m['timestamp'])
        counts[name] = len(messages)
        (output/(name+'.json')).write_text(json.dumps({'messages':messages}, ensure_ascii=False, indent=2), encoding='utf-8')
        if name == 'train':
            for key in selected:
                ms = sorted(groups[key], key=lambda m:m['timestamp'])
                for i in range(0,len(ms),12):
                    chunk = ms[i:i+12]
                    episodes.append(dict(id='episode-'+str(len(episodes)+1), date=chunk[0]['date'], end_time=chunk[-1]['timestamp'], source='real_training', messages=chunk))
    (output/'memory').mkdir()
    (output/'memory/episodes.json').write_text(json.dumps(episodes,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest = dict(seed=seed, grouping='session_id' if all(sessions) else 'UTC date', groups=split, message_counts=counts, removed_sensitive_candidates=removed)
    (output/'split.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(groups={k:len(v) for k,v in split.items()}, messages=counts, removed=removed)

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--input',type=Path,required=True); p.add_argument('--output',type=Path,required=True); p.add_argument('--seed',type=int,default=17); a=p.parse_args()
    print(json.dumps(prepare(a.input,a.output,a.seed)))
