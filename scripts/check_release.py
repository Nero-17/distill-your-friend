"""Release allowlist: reject extra files rather than guessing whether data is private."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'README.md','SKILL.md','.gitignore','agents/openai.yaml','references/data-contract.md','references/learning-loop.md','references/evaluation.md','references/memory.md','scripts/prepare.py','scripts/memory.py','scripts/score.py','scripts/check_release.py','tests/test_tools.py'}
def check():
    files={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not any(v in ['.git','__pycache__'] for v in p.relative_to(ROOT).parts)}
    if files != ALLOWED:raise ValueError(f'Unexpected files: {sorted(files-ALLOWED)}; missing: {sorted(ALLOWED-files)}')
    if (ROOT/'.git').exists():
        tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines())
        if tracked-ALLOWED:raise ValueError('Git tracks files outside release allowlist')
        for commit in subprocess.check_output(['git','rev-list','--all'],cwd=ROOT,text=True).splitlines():
            past=set(subprocess.check_output(['git','ls-tree','-r','--name-only',commit],cwd=ROOT,text=True).splitlines())
            if past-ALLOWED:raise ValueError('Git history contains files outside release allowlist')
    print(f'PASS: {len(files)} method-only allowlisted files; manually review content before publishing.')
if __name__=='__main__':check()
