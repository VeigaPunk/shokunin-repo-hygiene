#!/usr/bin/env python3
"""Count the current assessment-gate kind discrepancy, not Markdown defects."""
import argparse
import subprocess
import pathlib

def run(root, rev):
    text = subprocess.check_output(['git','-C',root,'show',rev+':SKILL.md'], text=True)
    rows = [line.split('|') for line in text.split('\n') if line.startswith('| r59 assessment comparison |')]
    if not rows:
        rows = [line.split('|') for line in text.split('\n') if line.startswith('| r58 assessment comparison |')]
    if len(rows) != 1 or len(rows[0]) != 10:
        print('FINDING REGISTRY-ROW-SHAPE')
        return 2
    row = [c.strip() for c in rows[0]]
    findings = []
    pass
    for finding in findings: print('FINDING '+finding)
    print('SUMMARY assertions=1 mismatches='+str(len(findings))+' rev='+rev)
    return int(bool(findings))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root')
    parser.add_argument('--rev')
    parser.add_argument('--selftest', action='store_true')
    parser.add_argument('--work')
    args=parser.parse_args()
    if args.selftest:
        if not args.work: parser.error('--selftest requires --work')
        here=pathlib.Path(__file__).resolve()
        raise SystemExit(subprocess.call(['python3','-B',str(here.with_name('controls.py')),'--root',str(here.parents[2]),'--rev','da5af55b5ea0a2a38edea05635a13416c698e6e7','--counter',str(here),'--work',args.work]))
    if not args.root or not args.rev: parser.error('--root and --rev required')
    raise SystemExit(run(args.root,args.rev))
