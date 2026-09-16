"""Score frozen local judgments; this tool is not an AI judge."""
import argparse, json, math
from pathlib import Path

def score(keys, predictions):
    k={x['id']:x for x in keys}; p={x['id']:x for x in predictions}
    if len(k)!=len(keys) or len(p)!=len(predictions) or k.keys()!=p.keys():
        raise ValueError('Unique, matching IDs required')
    rows=[]
    for ident,x in k.items():
        y=p[ident];prob=y['p_synthetic']
        if x['label'] not in ['real','synthetic'] or y['label'] not in ['real','synthetic'] or not isinstance(prob,(int,float)) or not math.isfinite(prob) or not 0<=prob<=1:
            raise ValueError('Invalid label or probability')
        rows.append(dict(real=x['label']=='real', predicted_real=y['label']=='real', correct=x['label']==y['label'], probability=prob, control=x.get('control',False)))
    normal=[x for x in rows if not x['control']];controls=[x for x in rows if x['control']]
    if not normal:raise ValueError('No non-control items')
    n=len(normal);c=sum(x['correct'] for x in normal);rate=c/n;z=1.96
    center=(rate+z*z/(2*n))/(1+z*z/n);half=z*math.sqrt(rate*(1-rate)/n+z*z/(4*n*n))/(1+z*z/n)
    return dict(n=n,correct=c,accuracy=rate,wilson95=[center-half,center+half],real_called_real=sum(x['real'] and x['predicted_real'] for x in normal),real_called_synthetic=sum(x['real'] and not x['predicted_real'] for x in normal),synthetic_called_real=sum(not x['real'] and x['predicted_real'] for x in normal),synthetic_called_synthetic=sum(not x['real'] and not x['predicted_real'] for x in normal),brier=sum((x['probability']-(not x['real']))**2 for x in normal)/n,control_count=len(controls),controls_correct=sum(x['correct'] for x in controls))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--labels',type=Path,required=True);p.add_argument('--predictions',type=Path,required=True);a=p.parse_args()
    print(json.dumps(score(json.loads(a.labels.read_text(encoding='utf-8-sig')),json.loads(a.predictions.read_text(encoding='utf-8-sig'))),indent=2))
