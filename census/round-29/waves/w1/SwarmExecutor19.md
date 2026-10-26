# SwarmExecutor19 — round 29 (r29) stale-statement sweep, lane-wide

## Status

STATUS: PASS — swept the lane's own self-assessment records for statements that disagree with observed state beyond the four frozen stale statements: 41 rows scored (34 agree, 5 disagree, 2 unverifiable), 5 of them the requested backticked path/command resolution checks; every lane-relative backticked path in SHONEN.md and the SCORECARD axes/capabilities tables resolves at the lane tip. Deliverable written to `.ufo/waves/round-29/w1/deliver-stale-sweep.tsv`. Nothing was added to the frozen C1 list and no frozen row was edited.

## Evidence

Revision swept: `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (HEAD, branch `master`, preregistration commit; lane base `691dd29` is its parent). The worktree had exactly one pre-existing modification, not mine: `.ufo/waves/round-26/w1/ScribeGateDraft.md` (see Finding 7).

### Enumeration and screening

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
grep -icE 'manifest|sha256sum|newline|improperly|malformed|152|1382' LOG.md SCORECARD.md SHONEN.md \
  corpus/README.md corpus/lessons/round-25.md corpus/lessons/round-26.md corpus/lessons/round-27.md corpus/lessons/round-28.md
LOG.md:21  SCORECARD.md:19  SHONEN.md:0  corpus/README.md:7  corpus/lessons/round-25.md:7
corpus/lessons/round-26.md:1  corpus/lessons/round-27.md:2  corpus/lessons/round-28.md:4      (61 hits)
```

In class (r26/r27/r28 wave-evidence manifest, receipt or `sha256sum -c` statement) = 19 hits: LOG.md 1748, 1757, 1758, 1763; SCORECARD.md 22, 23, 25; `corpus/lessons/round-28.md` 5, 21, 22, 26, 27, 28, 29, 40; `corpus/lessons/round-25.md` 78; `corpus/lessons/round-26.md` 15; `corpus/lessons/round-27.md` 5, 7. The other 42 hits describe other rounds (r4, r14, r17-r25) or unrelated `malformed`/`manifest` prose and were screened out, not scored. `1382` occurs in none of the target files; it is the r26 manifest record count.

### Manifest ground truth (frozen r29 C2 counter, committed bytes)

```
python3 -B census/round-29/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
r26 records=1382 failed=152 uncovered=14 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=b8cb4b31ce80e2e3314b88e85d40ea9873180804
rc=1
```

Path breakdown of the 152 absent records (classifier below; run against the same revision):

```
records=1382 verified=1230 absent=152 shadir=0 escaped=2
escaped_present= [('./assimilation/validate/tests/vault/vadv54-run/r/nl/first\nsecond.md', False),
                  ('./assimilation/validate/tests/vault/vadv54-run/r/scratch/.scratch/old\nname.log', False)]
absent_top_buckets= [('assimilation/validate/tests/vault/vadv-49', 140),
                     ('assimilation/validate/tests/vault/case-V6', 6),
                     ('assimilation/validate/tests/fixtures/__pycache__', 1),
                     ('assimilation/validate/tests/fixtures/case-F7', 1),
                     ('assimilation/validate/tests/fixtures/case-F8', 1)]
uncovered=14   (every one mode=120000, i.e. a committed symlink)
```

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --name-status 765fe8b^ 765fe8b -- census/round-26/waves/
-> 1245 A, 0 M   (the capture commit added files; it modified no tracked r26 wave file)
git check-ignore -v census/round-26/waves/assimilation/validate/tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc
-> .gitignore:3:__pycache__/
git check-ignore -v census/round-26/waves/assimilation/validate/tests/vault/vadv54-run/r/nl/first<newline>second.md
-> rc=1 (not ignored) ;  os.path.lexists -> True ;  committed tree -> absent
cat census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore
-> fixture/ , shims/        (158 files on disk under vadv-49, 18 tracked)
git ls-tree -r --name-only HEAD -- census/round-26/waves/symlinks.tsv
-> (empty)                  (no symlinks.tsv exists for r26, r27 or r28)
```

### On-disk `sha256sum -c` (the r28 receipt's method)

```
cd census/round-26/waves && sha256sum -c manifest.sha256
-> rc=0 ; 1380 OK ; WARNING: 2 line(s) are improperly formatted
cd census/round-27/waves && sha256sum -c manifest.sha256
-> rc=0 ; 124 OK ; no warnings
cd census/round-28/waves && sha256sum -c manifest.sha256
-> rc=0 ; 75 OK ; no warnings
cd <lane> && sha256sum -c census/round-26/waves/manifest.sha256
-> rc=1 ; 1380 FAILED open or read (records carry bare filenames)
```

The 1380 "OK" include the 152 files that are not in any commit; the two escaped records are skipped by this host's `sha256sum`, so 1380 of 1382 records verified and 152 of the verified files are uncommitted.

### Sources pins

```
cd census/round-25/sources && sha256sum -c SHA256SUMS   -> 5/5 OK rc=0
cd census/round-26/sources && sha256sum -c SHA256SUMS   -> 7/7 OK rc=0
cd census/round-27/sources && sha256sum -c SHA256SUMS   -> 2/2 OK rc=0
cd census/round-28/sources && sha256sum -c SHA256SUMS   -> 4/4 OK rc=0
cd <lane> && sha256sum -c census/round-25/sources/SHA256SUMS -> rc=1, 5 listed files could not be read
```

### Re-derived counts and receipt replays

```
for r in 3a2a80d 765fe8b de478b4 ed270c4; do python3 -B tools/souji-coverage-agreement.py --root . --rev $r; done
-> 3a2a80d: grounded=11 mapped=11 dangling=0 mismatches=0
   765fe8b, de478b4, ed270c4: grounded=13 mapped=13 dangling=0 mismatches=0
git show 3a2a80d:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'          -> 135
git show ed270c4:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'          -> 139  (tip 139)
git grep -lE '^ground: F4' <rev> -- corpus/knowledge/ | wc -l   -> 3a2a80d 4 ; ed270c4 6 ; tip 6
python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries \
  corpus/knowledge/origin-record-exclusivity-r28.md corpus/knowledge/origin-record-durability-r28.md \
  --snapshot-dir census/round-28/sources --slice census/round-28/waves/w1/quarantine-slice.tsv \
  --slice-verdicts census/round-28/waves/w1/slice-verdicts.tsv
-> entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0  rc=0
python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev 9301d98c... --format counts
-> assertions=63 resolved=63 skipped=40 mismatches=0  rc=0
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
-> souji ok /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md  rc=0
TMPDIR=<seat scratch> bash tests/fixtures/r28-wave-evidence-capture.sh
-> case-1..6 PASS ; cases=6 pass=6 control=TAMPER-REJECTED ; rc=0
cat census/round-28/records/c3-before.tsv -> dirty_waves=163 ; manifests_26=absent ; manifests_27=absent
cat census/round-28/records/c3-after.tsv  -> revision=ed270c4 ; dirty_ufo_waves=0 ; round2{6,7,8}_manifest_present=true
     ; round26_sha256sum_check=rc0; 1380 OK; WARNING 2 improperly formatted newline-path records
cat census/round-28/records/c2-after.tsv  -> SOURCES_rows=139 (frozen target=138; miss) ; grounded_F4_entries=6
     ; coverage_agreement=grounded=13 mapped=13 ... ; gate=entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
git cat-file -e 3a2a80d:census/round-{26,27,28}/waves/manifest.sha256   -> all ABSENT at base
git cat-file -e 3a2a80d:tools/souji-wave-evidence-capture.sh            -> ABSENT
git status --porcelain | awk '$2 ~ /^\.ufo\/waves\// {n++} END{print n+0}'   -> 1 at tip
```

### Classifier used for the absent/uncovered breakdown (read-only; reproduced here because the seat scratch was removed)

```python
#!/usr/bin/env python3
import re, subprocess, hashlib, collections
LANE='/home/vgpnk/Projects/shokunin/souji-shokunin'; REV='b8cb4b31ce80e2e3314b88e85d40ea9873180804'
def git(*a):
    p=subprocess.run(['git','-C',LANE,'-c','core.fsmonitor=false','-c','core.hooksPath=/dev/null',*a],capture_output=True)
    if p.returncode: raise SystemExit(p.stderr.decode())
    return p.stdout
def unesc(s): return re.sub(r'\\([\\n])', lambda m: '\n' if m.group(1)=='n' else '\\', s)
ents={}
for rec in git('ls-tree','-r','-z',REV,'--','census/round-26/waves').split(b'\0'):
    if not rec: continue
    meta,path=rec.split(b'\t',1); mode,typ,sha=meta.decode().split()
    ents[path.decode('utf-8','surrogateescape')]=(mode,typ,sha)
base='census/round-26/waves/'
text=git('cat-file','blob',ents[base+'manifest.sha256'][2]).decode('utf-8','surrogateescape')
recs={}; escaped=[]
for l in text.split('\n'):
    if not l: continue
    esc=l.startswith('\\'); m=re.match(r'^([0-9a-f]{64})  (.*)$', l[1:] if esc else l)
    if not m: continue
    n=unesc(m.group(2)) if esc else m.group(2)
    if esc: escaped.append(n)
    n=n[2:] if n.startswith('./') else n
    recs[n]=m.group(1)
absent=[]; shadir=[]; verified=0
for name,sha in recs.items():
    key=base+name
    if key not in ents: absent.append(name); continue
    if ents[key][1]!='blob': shadir.append(name); continue
    if hashlib.sha256(git('cat-file','blob',ents[key][2])).hexdigest()!=sha: shadir.append(name)
    else: verified+=1
print('records=%d verified=%d absent=%d shadir=%d escaped=%d'%(len(recs),verified,len(absent),len(shadir),len(escaped)))
print('absent_buckets=',collections.Counter('/'.join(n.split('/')[:5]) for n in absent).most_common(5))
print('uncovered=',[p[len(base):] for p in ents if p.startswith(base)
      and p!=base+'manifest.sha256' and p[len(base):] not in recs])
```

### Backtick resolution sweep (SHONEN.md + SCORECARD axes/capabilities)

```python
#!/usr/bin/env python3
import os, re, subprocess
LANE='/home/vgpnk/Projects/shokunin/souji-shokunin'; REV='b8cb4b31ce80e2e3314b88e85d40ea9873180804'
TARGETS=[('SHONEN.md',None),('SCORECARD.md',(11,15)),('SCORECARD.md',(145,176))]
PATHISH=re.compile(r'[A-Za-z0-9_.~/-]*/[A-Za-z0-9_.~/-]*|[A-Za-z0-9_.-]+\.(?:md|py|sh|tsv|json|txt|html|c|1|5|7)')
tree={r.decode() for r in subprocess.run(['git','-C',LANE,'-c','core.fsmonitor=false',
      '-c','core.hooksPath=/dev/null','ls-tree','-r','-z','--name-only',REV],
      capture_output=True).stdout.split(b'\0') if r}
def check(p):
    p=p.lstrip('./').rstrip('/')
    return 'committed' if p in tree or any(t.startswith(p+'/') for t in tree) else ('worktree' if os.path.lexists(os.path.join(LANE,p)) else 'MISSING')
for fn,span in TARGETS:
    lines=open(os.path.join(LANE,fn),encoding='utf-8').read().split('\n')
    lo,hi=span if span else (1,len(lines))
    for i in range(lo,min(hi,len(lines))+1):
        for m in re.finditer(r'`([^`]+)`',lines[i-1]):
            for tok in {t.strip('.,;:()') for t in PATHISH.findall(m.group(1))}:
                if tok and re.search(r'[A-Za-z]',tok) and (tok.count('/') or re.search(r'\.(md|py|sh|tsv|json|txt|html)$',tok)):
                    print('%s\t%d\t%s\t%s'%(fn,i,tok,check(tok)))
```

Result: SHONEN.md contains **0 backticked spans** (its 8 path tokens are bare prose and all resolve committed); the two SCORECARD tables yield 84 candidate spans. Every lane-relative path resolves. The non-resolving strings are not lane paths: `info/attributes`, `refs/jj/*`, `objects/pack/*.promisor` (git-internal), `/dev/null`, `/var/tmp` (host), `status.showUntrackedFiles` (config key), `knowledge/<name>` / `knowledge/` (map grammar template). Contextual resolutions: `c1-control-stub.tsv`, `c2-after.tsv`, `c2-fixture-after.tsv` are siblings of the cited `census/round-24/records/...` paths and all three are committed; `census/round-17/jj-receipts-*.txt` matches 2 committed files; `census/round-23/records/*.tsv` matches committed files; `census/round-16/transcripts` is a committed directory of 145 files.

## Findings

1. **The r26 capture claim is false over committed bytes** — `LOG.md:1758` "rounds 26/27 captured into `census/round-{26,27}/waves/`" and `corpus/lessons/round-28.md:22` "C3 captured round-26 and round-27 wave bytes". Observed: r27 is complete (124/124). r26 records 1382 files in the manifest but commits only 1230 of them; 152 records name paths absent from the committed tree — 140 under `assimilation/validate/tests/vault/vadv-49/{fixture,shims}/` (that directory's own `.gitignore` lists `fixture/` and `shims/`; 158 files on disk, 18 tracked), 6 under `case-V6`, 1 `__pycache__` name and 2 `.scratch` names. The r28 receipt `census/round-28/records/c3-after.tsv` records `round26_sha256sum_check=rc0; 1380 OK`, i.e. it verified the working tree — the exact disk-not-committed-bytes defect the r29 C2 prereg names. This is the same underlying defect as the frozen phrase but a distinct, wider sentence; it is a r30 candidate, not a C1 amendment.
2. **`corpus/lessons/round-28.md:21` reports a base-revision number as the after-state** — "Coverage agreement at the revision read returned global `grounded=11 mapped=11 dangling=0 mismatches=0`". `grounded=11 mapped=11` is the reading at base `3a2a80d`; `765fe8b`, `de478b4` and `ed270c4` all return `grounded=13 mapped=13 …`. The sentence names no revision and contradicts `LOG.md:1757` and `SCORECARD.md:22`, which both carry 13/13.
3. **The r28 limitation is scoped too narrowly** — `corpus/lessons/round-28.md:22` "tool-internal generation/recheck alone does not establish an independently consumable manifest for those paths". "Those paths" = the two newline-named records; the manifest is in fact not consumable over committed bytes for 152 records, and 14 committed symlinks under `census/round-26/waves` have no record and no `symlinks.tsv` entry (no `symlinks.tsv` exists in r26, r27 or r28). The escape-quoting defect and the dropped-files defect are independent.
4. **A recorded `sha256sum -c` command does not reproduce as written** — `corpus/lessons/round-25.md:78` "Opened-source snapshots verify `sha256sum -c census/round-25/sources/SHA256SUMS` → 5/5". Run from the lane root that command exits 1 with `WARNING: 5 listed file(s) could not be read`; 5/5 OK is reached only with the cwd inside `census/round-25/sources`. The same class defect affects every r26/r27/r28 waves manifest and the r26-r28 sources `SHA256SUMS`: all record bare filenames, so the `sha256sum -c <path-from-lane-root>` form fails. The counts are right; the commands as recorded are not reproducible.
5. **Two escaped records are unverifiable for two independent reasons** — `SCORECARD.md:25` "C3 has an independently unverifiable pair of newline-path manifest rows" is true, but the pair is unverifiable both because this host's `sha256sum` skips the escaped lines and because the two named files, though present on disk and **not** gitignored, were never committed. `sha256sum -c` from inside the wave dir reports `1380 OK` and silently omits both.
6. **`LOG.md:1748` "36 r26 leftovers" could not be re-derived** — `.ufo/` is gitignored and no committed receipt records the r27-close count; at tip `.ufo/waves/round-26/w1/` holds 118 files (90 tracked). Unverifiable, not contradicted.
7. **`corpus/lessons/round-28.md:22` "restored the 11 modified tracked r26 wave files"** — consistent with the commit (`765fe8b` has 0 modifications under `census/round-26/waves`) but the count is a working-tree observation with no committed receipt; unverifiable.
8. **Observation for the L1 (not a stale statement):** the frozen dirty-wave counter prints `1` at the current tip because a wave-29 seat modified the tracked file `.ufo/waves/round-26/w1/ScribeGateDraft.md` (+2/-1, mtime 2026-10-25 20:45:43). The r28 "163→0" claim holds only at its measured commit; the frozen counter is touched by any edit to a committed r26/r27 wave file, not only by new untracked ones.
9. **Path/command resolution is clean** — SHONEN.md has no backticked spans; its 8 bare path tokens all resolve, `S100`-`S103` rows exist, and `LOG.md:362` heads the section carrying the 96-artifact claim. In the SCORECARD axes and capabilities tables, every lane-relative backticked path resolves at `b8cb4b3`; the two executed commands reproduce (`declared-evidence` 63/63/40/0 rc 0; `coverage-agreement` 13/13/0/0 rc 0). Zero unresolved lane paths — negative claim carried by the sweep in Evidence.
10. **Screening** — of 61 keyword hits, 19 are in the r26/r27/r28 manifest/receipt/`sha256sum -c` class and were scored; the other 42 concern other rounds or unrelated prose and were excluded. The four frozen phrases (`LOG.md:1758`, `SCORECARD.md:23`, `corpus/lessons/round-28.md:22` and `:40`) were not re-scored and are absent from the TSV.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-stale-sweep.tsv` — 41 rows (34 agree, 5 disagree, 2 unverifiable), columns `file  line  statement  observed  verdict  command`.
- `.ufo/waves/round-29/w1/SwarmExecutor19.md` — this report.

No tools installed or updated. No file outside `.ufo/waves/round-29/w1/` was written; seat scratch (`/var/tmp/souji-r29-SwarmExecutor19`) held the two analysis scripts and the fixture TMPDIR and was removed.
