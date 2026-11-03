import sys, os, importlib.util, re, subprocess, tempfile
from pathlib import Path
BUILDER='/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-55/fixtures/build-fixtures.py'
spec=importlib.util.spec_from_file_location('bf', BUILDER); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
CUR=re.compile(r'\s*#\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\S+?)\s*')
WID=re.compile(r'\s*#\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*(\S+?)\s*')
KEYS=['RECEIPT_VERSION','TOOL_SHA256','FLEET_HEAD','CAPTURE_SHA256','ENTRIES']
def scan(txt, rx):
    unk=[]; known=set()
    for ln in txt.split('\n'):
        kv=rx.fullmatch(ln)
        if not kv: continue
        k=kv.group(1).upper()
        if k in KEYS: known.add(k)
        elif not unk: unk.append(kv.group(1))
    return known, unk
work=tempfile.mkdtemp(prefix='widen-', dir='/fast/scratch/hyaku/souji-r55/S55connector01')
fdir=Path(work)/'c2-fixtures'; fdir.mkdir(parents=True, exist_ok=True)
print("fixture\told_unknown\tnew_unknown\told_keys_complete\tnew_keys_complete\tverdict_delta")
deltas=0
for name in mod.C2_FIXTURES:
    info=mod.build_one(name, fdir)
    # find the receipt file the fixture committed
    p=subprocess.run(['git','-C',info['dir'],'ls-tree','-r','--name-only',info['tip']],capture_output=True,text=True).stdout.split('\n')
    rc=[x for x in p if x.endswith('run.txt') or 'receipt' in x.lower()]
    txt=''
    if rc:
        txt=subprocess.run(['git','-C',info['dir'],'show','%s:%s'%(info['tip'],rc[0])],capture_output=True).stdout.decode('utf-8','replace')
    ko,uo=scan(txt,CUR); kn,un=scan(txt,WID)
    delta = (uo!=un)
    if delta: deltas+=1
    print("%-22s %-14s %-14s %-18s %-18s %s" % (name, uo or '-', un or '-',
          len(ko)==5, len(kn)==5, 'CHANGED' if delta else 'same'))
print("\nfixtures whose receipt verdict changes under the widened charset: %d" % deltas)
