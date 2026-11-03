# S54sentinel01 — souji round 54 write-scope & hardening review of the frozen instruments

Seat: `S54sentinel01` (role: sentinel, leaf member — no subagent dispatch).
Lane (read-only): `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Seat dir: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-54/w1/S54sentinel01/`.
Scratch (deleted before yield): `/fast/scratch/hyaku/souji-r54/S54sentinel01`.
Review target (read-only, never edited): `census/round-54/c1-counter.py`, `census/round-54/c2-counter.py`,
`census/round-54/fixtures/build-fixtures.py`, `census/round-54/fixtures/run-matrix.sh`,
`census/round-54/controls/c1-control-donothing.txt`, `census/round-54/controls/c2-control-donothing.txt`,
`census/round-54/preregistration.txt` (freeze commit `3c394cab0cd406bbab72b8d365e0f3deed4ef98a`).

## VERDICT

**CONDITIONAL PASS — 4 findings (1 HIGH, 2 MEDIUM, 1 LOW) + 2 named-limit observations.**

The **host trust boundary is intact**. Nothing in the round's new bytes executes repo-controlled
configuration, escapes the scratch, reaches the network, reads a secret, or writes a fleet file.
Every write I could reach lands under `--work`; every subprocess is list-form with a timeout and a
scrubbed environment; the counters' command whitelist (`git show`, `git diff --numstat`) plus
`GIT_NO_LAZY_FETCH=1` closes the git-config and network vectors (proved below). **No HIGH-bar
sandbox-escape or repo-config code-execution vector exists.**

The HIGH finding is a **measurement-integrity** defect, not a host-compromise defect: the C1 v3
counter's fenced-correction refusal (the r53 R1 surface the round's C1 claim is built on) is
**defeated by a single exotic line separator** in the very file it audits, because the counter
computes line numbers two different ways. On a fixture that is the F7 shape verbatim plus two
form-feed bytes, `c1-counter.py` exits **0** with `fenced=0 filed=2` — i.e. it credits corrections
that live inside a `~~~` fence as valid filings. The same defect also manufactures a **false
`INERT-CORRECTION`** on an honest lane. Severity follows the r53 sentinel's own precedent
(S53 S1 = HIGH: "the counter's own stated property does not hold; it verifies green").

| id | severity | finding | class |
|----|----------|---------|-------|
| **S1** | **HIGH** | `c1-counter.py` numbers the lines of the audited file two different ways — `hidden_lines()` uses `str.splitlines()` (which also breaks on `\x0b \x0c \x1c \x1d \x1e \x85 \u2028 \u2029`), the correction's own line number uses a plain `'\n'` count. The two disagree by the number of exotic separators in the file, so a `~~~`-fenced correction (r53 R1, the surface C1 claims) is **credited as a valid filing** and the counter exits **0** on the F7 shape. | routed-defect (instrument, frozen) |
| **S2** | MEDIUM | `UNFILED-SOURCES-ANNOTATION` (the r53 R4 misread class C1 claims) only matches the **ASCII** `->` pair form. The lane's own corpus uses the **Unicode arrow `→`** in the identical `corpus/SOURCES.md N → M rows` idiom (LOG.md:1727, 1845, 1858), so the same misread written with `→` is **invisible to the scan** and the counter exits 0. | routed-defect (instrument, frozen) |
| **S3** | MEDIUM | The C2 unknown-receipt-key check is `RECEIPT_KV = re.compile(r'# ([A-Z0-9_]+)=(\S+)')` — **uppercase-only**. A receipt carrying `# generator=fixture-builder` or `# MY-KEY=1` is silently accepted (`receipt=ok`, exit 0), while the same key in uppercase is refused. | routed-defect (instrument, frozen) |
| **S4** | LOW | The builder's `--work` guard accepts a **relative** path: `git(d.parent,'init',...)` then `git -C d rev-parse --show-toplevel` resolves relative to the *new* cwd, producing a nested `rel2/rel2/<fixture>` tree and a confusing `fatal: not a git repository`. No write escapes the process cwd and the run still fails closed (rc=1), so this is hardening polish, not an escape. | hardening |
| **S5** | LOW / named limit | The C1 counter's docstring promises a `PRISTINE FAIL` class at exit 1, but `c1-counter.py` emits **no** `PRISTINE FAIL` line at all (only the C2 counter does). Its absent-record path returns `CANNOT-EVALUATE` / exit 2. The prereg's C1 kill clause is written against exit codes, so the claim is unaffected; the docstring is stale. | named limit (doc) |
| **S6** | LOW / named limit | The counters' `--scratch` argument is accepted and **ignored** (help text: "accepted; nothing is written outside --work"). Only `--work` steers writes; `TMPDIR` is never read by either counter. The prereg's own recompute commands pass `--scratch DIR`, which therefore has no effect. Disclosed-by-behaviour, but it is a name that implies an effect it does not have. | named limit (doc) |

> **Every finding above is a defect in bytes that the prereg freezes.** Per the round's own
> discipline ("a defect an attack finds is a named limit, never an edit"), **I made no edit to any
> committed file.** These are routed to the L1 for the round's named-limit record.

---

## Check 1 — Scratch discipline: no hardcoded `/tmp`, `/var/tmp`, `/dev/shm`; TMPDIR/`--work`/`--scratch` honoured

**PASS.** Scoped grep over exactly the four committed scripts:

```
$ for f in census/round-54/c1-counter.py census/round-54/c2-counter.py \
           census/round-54/fixtures/build-fixtures.py census/round-54/fixtures/run-matrix.sh; do
    echo "--- $f ---"
    grep -n -E '/var/tmp|/tmp|/dev/shm|mkdtemp|tempfile|TemporaryDirectory|gettempdir' "$f" || echo "  (no hits)"
  done
--- census/round-54/c1-counter.py ---
  (no hits)
--- census/round-54/c2-counter.py ---
  (no hits)
--- census/round-54/fixtures/build-fixtures.py ---
65:Writes nothing outside --work. No network. Honours --work (never /tmp).
449:    ap.add_argument('--work', required=True, help='existing scratch dir (never /tmp defaults)')
--- census/round-54/fixtures/run-matrix.sh ---
  (no hits)
```

Both `/tmp` hits are **prose in a docstring / a help string**. There is **no** `mkdtemp`, no
`tempfile`, no `TemporaryDirectory`, no `gettempdir` anywhere in the four files. `run-matrix.sh`
passes `TMPDIR="$S"` explicitly to every counter invocation and `--scratch "$S"`; the builder
requires `--work` and never defaults to a system temp dir.

**`--scratch` is honoured only nominally (S6).** `c1-counter.py:430` and `c2-counter.py:346`:

```
    ap.add_argument('--scratch', default=None, help='accepted; nothing is written outside --work')
```

Neither counter ever reads `ns.scratch`. Every write goes to `--work` (`work / 'c1-fixtures'`,
`work / 'c2-fixtures'`). The prereg's recompute commands therefore pass an argument with no
effect — harmless, but the name promises an effect it does not have.

**Write-scope proof (selftest mode).** Snapshot of the lane tree before/after running **both**
selftests with `-B`:

```
$ find $LANE/census/round-54 -type f | sort > $S/lane-before.txt
$ python3 -B census/round-54/c1-counter.py --selftest --work $S/st5 --builder-sha256 ae5881f8… --expected-sha256 4e73c495… >/dev/null 2>&1
$ python3 -B census/round-54/c2-counter.py --selftest --work $S/st6 --builder-sha256 ae5881f8… --expected-sha256 e32f7934… >/dev/null 2>&1
$ find $LANE/census/round-54 -type f | sort > $S/lane-after.txt
$ diff $S/lane-before.txt $S/lane-after.txt && echo "LANE TREE UNCHANGED by the two selftests (-B)"
LANE TREE UNCHANGED by the two selftests (-B)
--- files written under --work ---
/fast/scratch/hyaku/souji-r54/S54sentinel01/st5
/fast/scratch/hyaku/souji-r54/S54sentinel01/st5/c1-fixtures
/fast/scratch/hyaku/souji-r54/S54sentinel01/st6
/fast/scratch/hyaku/souji-r54/S54sentinel01/st6/c2-fixtures
```

**One caveat, and it is the r53 S4 finding again.** `load_builder()` does
`spec.loader.exec_module(mod)` on the builder **in the lane tree**. Running the counter **without**
`-B` writes a bytecode cache into the lane:

```
$ python3 -B $S/lanecopy/census/round-54/c1-counter.py --selftest --work $S/stB >/dev/null 2>&1
with -B:
(empty above => -B suppressed it)
$ python3 $S/lanecopy/census/round-54/c1-counter.py --selftest --work $S/stC >/dev/null 2>&1
without -B:
/fast/scratch/hyaku/souji-r54/S54sentinel01/lanecopy/census/round-54/fixtures/__pycache__
/fast/scratch/hyaku/souji-r54/S54sentinel01/lanecopy/census/round-54/fixtures/__pycache__/build-fixtures.cpython-314.pyc
```

The lane's committed run paths all use `-B`, and `.gitignore:3` is `__pycache__/`, so the residue is
inert and untracked (`git check-ignore -v` confirms). The lane currently carries exactly one such
directory (`census/round-54/fixtures/__pycache__/`, ignored). **Not a finding** — same disposition
as r53 S4 — but the write still lands outside `--work` in the counter's own terms.

---

## Check 2 — Builder sandbox

### (a) every `subprocess.run` carries `timeout=` — **PASS**

`build-fixtures.py` has exactly **one** `subprocess.run` call site, and it carries a timeout:

```
$ grep -n "subprocess" census/round-54/fixtures/build-fixtures.py
77:import subprocess
$ sed -n '129,133p' census/round-54/fixtures/build-fixtures.py
def run(cmd, cwd=None, env=None):
    e = dict(env or os.environ)
    p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, timeout=120)
```

Both counters likewise: `c1-counter.py:101` and `c2-counter.py:88` carry `timeout=120`.
**This closes r53's S3 timeout gap.**

### (b) every git invocation carries `-c core.fsmonitor=false -c core.hooksPath=/dev/null` — **PASS**

All git traffic in the builder funnels through one wrapper; there is no second git code path:

```
$ grep -n "subprocess\|'git'\|\"git\"\|def git\|def run" census/round-54/fixtures/build-fixtures.py
129:def run(cmd, cwd=None, env=None):
131:    p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, timeout=120)
139:def git_env():
159:def git(d: Path, *args, date=None):
164:    return run(['git', '-C', str(d),
165:                '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null'] + list(args), env=e)
```

`init_repo`, `commit_all`, `rev-parse`, `config`, `add`, `commit` all call `git()`. The counters
use the identical flag pair (`c1-counter.py:99-101`, `c2-counter.py:86-88`).
**This closes r53's S3 flag gap.**

### (c) the toplevel-verify guard precedes the first commit — **PASS**

`init_repo()` runs `git init`, then `git rev-parse --show-toplevel`, then compares to the fixture
dir **before** `commit_all()` is ever reached:

```
def init_repo(workdir: Path, name: str) -> Path:
    d = workdir / name
    ...
    git(d.parent, 'init', '-q', str(d))
    top = git(d, 'rev-parse', '--show-toplevel')
    if Path(top) != d:
        raise SystemExit('fixture toplevel mismatch %s != %s' % (top, d))
```

The guard is load-bearing — a symlinked `--work` is refused:

```
$ python3 -B $LANE/census/round-54/fixtures/build-fixtures.py --work $S/sym/link --manifest $S/sym/m.tsv
fixture toplevel mismatch /fast/scratch/hyaku/souji-r54/S54sentinel01/sym/real/F1-HONEST-TIP != /fast/scratch/hyaku/souji-r54/S54sentinel01/sym/link/F1-HONEST-TIP
rc=1
```

### (d) `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` are pinned — **PASS**

```
$ grep -n "T0 =\|T1 =" census/round-54/fixtures/build-fixtures.py
T0 = '2026-11-04T12:00:00+00:00'
T1 = '2026-11-04T12:01:00+00:00'
```

`git_env()` sets `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` to `T0`, and `git(..., date=…)` overrides
both to `T1` for the tip commit. **Reproducibility proven**: I rebuilt all 23 fixtures from
scratch and my revs are **byte-identical** to the L1's committed matrix revs (see Check 6).

### (e) it writes only under `--work` — **PASS with one caveat (S4)**

All builder writes are `path.write_bytes()` under `d` (= `<work>/<fixture>`), plus the manifest at
`ns.manifest or str(work / 'fixture-manifest.tsv')`. The one escape is operator-chosen
`--manifest`:

```
$ python3 -B $LANE/census/round-54/fixtures/build-fixtures.py --work $S/wd --manifest $S/outside-manifest.tsv
  rc 0 | MANIFEST /fast/scratch/hyaku/souji-r54/S54sentinel01/outside-manifest.tsv
-rw-r--r-- 1 vgpnk vgpnk 4580 Nov  3 17:46 /fast/scratch/hyaku/souji-r54/S54sentinel01/outside-manifest.tsv
```

Identical to r53's disposition: an explicit CLI argument, so **operator-controlled, not a defect** —
but the docstring at `build-fixtures.py:65` ("Writes nothing outside --work") is literally false
when `--manifest` is passed. r53 recommended correcting that wording; it is unchanged in r54.

### r53 sentinel S3 shape: does any code path write outside `--work`? — **NO**

Trace (no dangerous execution): the builder's only writes are `write()` under the fixture dir, the
`init_repo` `mkdir`/`rmtree` under `--work`, and the manifest path above. `git_env()` sets
`HOME` to `HYAKU_SCRATCH_HOME` or the inherited `HOME` — but `GIT_CONFIG_GLOBAL=/dev/null` and
`GIT_CONFIG_SYSTEM=/dev/null` mean **no global or system config is read or written**:

```
$ git -C $S/work/F1-HONEST-TIP config --local --list
core.repositoryformatversion=0
core.filemode=true
core.bare=false
core.logallrefupdates=true
core.fsmonitor=false
user.name=fixture
user.email=fixture@invalid
commit.gpgsign=false
$ ls -la /home/vgpnk/.gitconfig 2>/dev/null || echo "no ~/.gitconfig (good)"
no ~/.gitconfig (good)
```

**The fixture identity is repo-local only.** No global config file is created; `$HOME` is unchanged
after every builder run I made. The lane's `git status --porcelain` is unchanged by my runs
(only the L1's own untracked artifacts appear).

---

## Check 3 — Pin integrity

### Pins vs. the prereg — **PASS, all eight match**

```
$ sha256sum census/round-54/fixtures/build-fixtures.py census/round-54/fixtures/run-matrix.sh \
           census/round-54/records/c1-selftest-expected.tsv census/round-54/records/c2-selftest-expected.tsv \
           census/round-54/c1-counter.py census/round-54/c2-counter.py
ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba  census/round-54/fixtures/build-fixtures.py
f9d277636d6642de7b287678a145e8916f84f0c9cba00f4768aa16feaca80799  census/round-54/fixtures/run-matrix.sh
4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7  census/round-54/records/c1-selftest-expected.tsv
e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d  census/round-54/records/c2-selftest-expected.tsv
f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e  census/round-54/c1-counter.py
84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09  census/round-54/c2-counter.py
```

```
preregistration.txt:146: - census/round-54/fixtures/build-fixtures.py  ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba
preregistration.txt:147: - census/round-54/fixtures/run-matrix.sh  f9d277636d6642de7b287678a145e8916f84f0c9cba00f4768aa16feaca80799
preregistration.txt:148: - census/round-54/records/c1-selftest-expected.tsv  4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7
preregistration.txt:149: - census/round-54/records/c2-selftest-expected.tsv  e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d
preregistration.txt:29:  Counter: census/round-54/c1-counter.py sha256=f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e
preregistration.txt:93:  Counter: census/round-54/c2-counter.py sha256=84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09
preregistration.txt:150: - census/round-51/records/ws-drift-vs-r46.tsv at base  2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30
preregistration.txt:151: - tools/souji-fleet-root-census.py at base  e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b
```

The two **base-revision** pins also verify against the tree at base `fe12daad`:

```
$ git show fe12daad2549f534650d406ebdbac9113d59313f:census/round-51/records/ws-drift-vs-r46.tsv | sha256sum
2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30  -
$ git show fe12daad2549f534650d406ebdbac9113d59313f:tools/souji-fleet-root-census.py | sha256sum
e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b  -
```

**The committed bytes are the pinned bytes.** The working tree and the freeze commit `3c394cab`
hash identically for all six instrument files:

```
$ for f in census/round-54/fixtures/build-fixtures.py census/round-54/fixtures/run-matrix.sh \
           census/round-54/records/c1-selftest-expected.tsv census/round-54/records/c2-selftest-expected.tsv \
           census/round-54/c1-counter.py census/round-54/c2-counter.py; do
    printf "%s  %s\n" "$(git show 3c394cab:$f | sha256sum | cut -d' ' -f1)" "$f"; done
ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba  census/round-54/fixtures/build-fixtures.py
f9d277636d6642de7b287678a145e8916f84f0c9cba00f4768aa16feaca80799  census/round-54/fixtures/run-matrix.sh
4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7  census/round-54/records/c1-selftest-expected.tsv
e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d  census/round-54/records/c2-selftest-expected.tsv
f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e  census/round-54/c1-counter.py
84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09  census/round-54/c2-counter.py
```

### Wrong-pin selftests — **PASS, both refuse before exec**

The r53 S4 routed fix (pins verified **BEFORE** `exec_module`) is live in both counters.

```
$ python3 -B census/round-54/c1-counter.py --selftest --work $S/st1 \
    --builder-sha256 0000000000000000000000000000000000000000000000000000000000000000 \
    --expected-sha256 4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7
CANNOT-EVALUATE PIN-MISMATCH builder sha256 ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba != pinned 0000000000000000000000000000000000000000000000000000000000000000
rc=2

$ python3 -B census/round-54/c2-counter.py --selftest --work $S/st2 \
    --builder-sha256 ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba \
    --expected-sha256 0000000000000000000000000000000000000000000000000000000000000000
CANNOT-EVALUATE PIN-MISMATCH expected sha256 e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d != pinned 0000000000000000000000000000000000000000000000000000000000000000
rc=2
```

Both directions, both counters, all four probes refuse with rc=2 and no fixture is built:

```
$ python3 -B census/round-54/c1-counter.py --selftest --work $S/st3 --builder-sha256 ae5881f8… --expected-sha256 000…0
CANNOT-EVALUATE PIN-MISMATCH expected sha256 4e73c495… != pinned 000…0     rc=2
$ python3 -B census/round-54/c2-counter.py --selftest --work $S/st4 --builder-sha256 000…0 --expected-sha256 e32f7934…
CANNOT-EVALUATE PIN-MISMATCH builder sha256 ae5881f8… != pinned 000…0       rc=2
```

Correct pins → green:

```
$ python3 -B census/round-54/c1-counter.py --selftest --work $S/st1 --builder-sha256 ae5881f8… --expected-sha256 4e73c495…
SELFTEST-CASE F1-HONEST-TIP pass rc=0 want_rc=0 finding=- want_finding=-
… (13 cases) …
SELFTEST pass cases=13
rc=0
$ python3 -B census/round-54/c2-counter.py --selftest --work $S/st2 --builder-sha256 ae5881f8… --expected-sha256 e32f7934…
… (10 cases) …
SELFTEST pass cases=10
rc=0
```

**Real-lane pin**: the committed capture's `TOOL_SHA256` header equals the tool bytes at the tip,
which equals the base pin:

```
$ git show bfdbb336…:tools/souji-fleet-root-census.py | sha256sum
e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b  -
$ git show bfdbb336…:census/round-54/records/fleet-root-census.tsv | head -4
# souji round-52 fleet-root census (read-only; dry-run)
# SCOPE=top-level entries of the fleet root, dotfiles included, .git excluded
# TOOL_SHA256=e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b
# FLEET_HEAD=3b0d5329147d3b05d3aec5e908c75405ae3bc05a
```

and the counter agrees on the live lane:

```
$ python3 -B census/round-54/c2-counter.py --root $LANE --rev bfdbb336… --capture census/round-54/records/fleet-root-census.tsv \
    --receipt census/round-54/records/fleet-root-census-run.txt --tool-sha256 e7e79952… --scratch $S
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=bfdbb336329e
rc=0
```

A wrong tool pin refuses with the named class and rc=1:

```
$ python3 -B census/round-54/c2-counter.py --root $LANE --rev bfdbb336… --capture … --receipt … --tool-sha256 0000000000000000000000000000000000000000000000000000000000000000 --scratch $S
FINDING TOOL-SHA-ARG-MISMATCH pinned=000000000000 observed=e7e79952f783
SUMMARY … tool_pin=FAIL …
rc=1
```

---

## Check 4 — Receipt staging outside the fleet root

**PASS.** The census tool refuses an `--out` that resolves inside the fleet root. The refusal code
path (`tools/souji-fleet-root-census.py:258-270`):

```python
def capture(root, out, home=None):
    """Write the census of `root` to `out` (O_EXCL).  Returns a process exit code."""
    if os.path.lexists(out):
        sys.stderr.write('%s: REFUSED --out already exists: %s\n' % (PROG, out))
        return 2
    try:
        out_real_parent = os.path.realpath(os.path.dirname(os.path.abspath(out)))
        real_root = os.path.realpath(os.path.abspath(root))
        if out_real_parent == real_root or out_real_parent.startswith(real_root + os.sep):
            raise Refused('--out resolves inside the fleet-root: %s' % out)
        data, counts, n = build(root, home)
    except Refused as exc:
        sys.stderr.write('%s: REFUSED %s\n' % (PROG, exc))
        return 2
```

I exercised that path on a **scratch** root (never the fleet root):

```
$ python3 -B $LANE/tools/souji-fleet-root-census.py --fleet-root $S/censusroot --out $S/censusroot/capture-inside.tsv
souji-fleet-root-census: REFUSED --out resolves inside the fleet-root: /fast/scratch/hyaku/souji-r54/S54sentinel01/censusroot/capture-inside.tsv
rc=2
$ ls -A $S/censusroot
.git
=== same tool, --out OUTSIDE the scratch root ===
CENSUS ENTRIES=0 tracked=0 ignored=0 untracked-stray=0 symlink=0 out=/fast/scratch/hyaku/souji-r54/S54sentinel01/capture-outside.tsv
rc=0
```

**Refused with nothing created inside.** The same tool, run against a scratch root with an
out-of-root `--out`, writes normally — so the refusal is the out-root check, not a blanket refusal.

**The committed round-54 capture receipt names its staging path** — the receipt states it was
staged outside the fleet root, in scratch, and that the tool refuses an in-root `--out`
(`census/round-54/records/fleet-root-census-run.txt`):

```
# round-54 fleet-root capture — run receipt (machine-readable block, RECEIPT_VERSION=1)
# RECEIPT_VERSION=1
# TOOL_SHA256=e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b
# FLEET_HEAD=3b0d5329147d3b05d3aec5e908c75405ae3bc05a
# CAPTURE_SHA256=0c3f42e000e00fd8165e99aee5d42908ccd63cdc3d7461ca840fb1f22f09e1f9
# ENTRIES=49
command: python3 -B tools/souji-fleet-root-census.py --fleet-root /home/vgpnk/Projects/shokunin --out <staging outside the fleet root>
run stdout: CENSUS ENTRIES=49 tracked=22 ignored=22 untracked-stray=5 symlink=0 out=/fast/scratch/hyaku/souji-r54/capture/fleet-root-census.tsv
staging path: /fast/scratch/hyaku/souji-r54/capture/fleet-root-census.tsv (outside the fleet root; the tool refuses an --out inside it)
staged sha256: 0c3f42e000e00fd8165e99aee5d42908ccd63cdc3d7461ca840fb1f22f09e1f9
committed copy: census/round-54/records/fleet-root-census.tsv
```

The staged digest equals the committed copy's digest — the copy is byte-exact:

```
$ sha256sum census/round-54/records/fleet-root-census.tsv
0c3f42e000e00fd8165e99aee5d42908ccd63cdc3d7461ca840fb1f22f09e1f9  census/round-54/records/fleet-root-census.tsv
```

`FLEET_HEAD=3b0d5329…` is the fleet HEAD **at capture time**; the fleet has since advanced to
`9b0320b2…` and `3b0d5329` is an ancestor of it, so the receipt's head is a historical fact, not a
stale pin. The C2 counter only *format-checks* `FLEET_HEAD` (a disclosed named limit).

**The `census-before-receipt.txt` is a different artifact** (the `souji-census-receipt.py` v1
receipt form, not the fleet-root capture). It carries no staging-path line — but neither do the r52
and r53 receipts of the same kind, so this is the lane's established shape, not a r54 regression:

```
$ for f in census/round-52/records/census-before-receipt.txt census/round-53/records/census-before-receipt.txt census/round-54/records/census-before-receipt.txt; do
    printf '%-50s lines=%s  staging-mentions=%s\n' "$f" "$(wc -l < $LANE/$f)" "$(grep -ci 'stag\|/fast/scratch\|/tmp' $LANE/$f)"; done
census/round-52/records/census-before-receipt.txt  lines=139  staging-mentions=0
census/round-53/records/census-before-receipt.txt  lines=141  staging-mentions=0
census/round-54/records/census-before-receipt.txt  lines=143  staging-mentions=0
```

That tool has its own in-lane-root refusal (`tools/souji-census-receipt.py:122-129`), i.e. the
"staged outside the repo, copied in by the caller" discipline:

```python
    resolved_out = os.path.realpath(args.out)
    root = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if resolved_out == root or resolved_out.startswith(root + os.sep) or root.startswith(resolved_out + os.sep):
        sys.stderr.write("ERROR: --out resolves inside the lane root; receipts are staged "
                         "outside the repo (r48 receipt-staging discipline) and copied in "
                         "by the caller before a commit\n")
        return 2
```

And the committed receipt re-verifies under the tool's own verifier:

```
$ python3 -B tools/souji-census-receipt.py verify --receipt census/round-54/records/census-before-receipt.txt
VERIFY ok receipt=census/round-54/records/census-before-receipt.txt lane=souji conf_rc=0 dir_rc=0 w04=61 result=ok checks=grammar,digest,raw-section,rc,w04,result,adapter-sha adapter=ok
rc=0
```

---

## Check 5 — Counter hygiene

### `git_env` scrubs config — **PASS, both counters**

`c1-counter.py:87-94` and `c2-counter.py:75-82` are identical:

```
'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_LAZY_FETCH': '1',
'GIT_TERMINAL_PROMPT': '0',
```

### No network calls — **PASS**

```
$ grep -cE 'urllib|requests|socket|http|urlopen|ftp' census/round-54/c1-counter.py census/round-54/c2-counter.py census/round-54/fixtures/build-fixtures.py census/round-54/fixtures/run-matrix.sh
urllib     census/round-54/c1-counter.py:0 census/round-54/c2-counter.py:0 census/round-54/fixtures/build-fixtures.py:0 census/round-54/fixtures/run-matrix.sh:0
requests   census/round-54/c1-counter.py:0 census/round-54/c2-counter.py:0 census/round-54/fixtures/build-fixtures.py:0 census/round-54/fixtures/run-matrix.sh:0
socket     census/round-54/c1-counter.py:0 census/round-54/c2-counter.py:0 census/round-54/fixtures/build-fixtures.py:0 census/round-54/fixtures/run-matrix.sh:0
http       census/round-54/c1-counter.py:0 census/round-54/c2-counter.py:0 census/round-54/fixtures/build-fixtures.py:0 census/round-54/fixtures/run-matrix.sh:0
urlopen    census/round-54/c1-counter.py:0 census/round-54/c2-counter.py:0 census/round-54/fixtures/build-fixtures.py:0 census/round-54/fixtures/run-matrix.sh:0
ftp        census/round-54/c1-counter.py:0 census/round-54/c2-counter.py:0 census/round-54/fixtures/build-fixtures.py:0 census/round-54/fixtures/run-matrix.sh:0
```

**Zero** network-API occurrences in any of the four files (each alternative checked separately, so
there is no pattern ambiguity). A broader sweep that also matched the word *"token"* (which occurs
only inside identifiers such as `ok_tokens`, `zone_tokens`, and in the prose "count token") shows
those hits are all identifier/prose matches — e.g. `c1-counter.py:14` `ZONE-TOKEN-STRADDLES-EDGE`,
`c1-counter.py:152` `def zone_tokens(...)`, `build-fixtures.py:26` `F10-STRADDLE a `-> 79` token
planted…`. **No `urllib`, `requests`, `socket`, `urlopen`, `ftp`, `http://` or `https://` appears in
any of the four files.** A secret-material sweep (`api[_-]?key|secret|password|BEGIN [A-Z ]*PRIVATE
KEY`) returns nothing beyond the same "token" prose hits.

The only network-capable path is git's lazy fetch, closed by `GIT_NO_LAZY_FETCH=1`.

### No writes outside `--work` in selftest mode — **PASS** (see Check 1's before/after diff)

### Exit-code map matches the prereg's verdict map (0/1/2) — **PASS**

| condition | counter | exit | prereg verdict |
|---|---|---|---|
| every check holds | both | 0 | "the v3 counter exits 0 on any attack fixture F7-F12" (C1); "v3 exit 0 on FA4 or FA5" is the *kill* clause, i.e. v3 must exit 1 there — see below |
| a finding | both | 1 | 1 |
| could-not-evaluate (bad CLI, missing file, zero/duplicate anchor, no annotation in zone, flagged filing without pinned source revs, pin mismatch) | both | 2 | 2 |

Measured:

```
C1 v3, real lane at the content tip (bfdbb336):
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=bfdbb336329e base=fe12daad2549
rc=0
```
(identical to the prereg's promised line: `unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0`)

```
C2 v3, real lane capture:  rc=0  tool_pin=ok receipt=ok sorted=ok   (prereg-promised: "receipt=ok sorted=ok tool_pin=ok")
C1 v3, rev whose record is absent:  CANNOT-EVALUATE record absent at 000000000000: …   rc=2
C1 v3, non-hex rev:                 CANNOT-EVALUATE full 40-hex revisions required      rc=2
C2 v3, absent capture:              PRISTINE FAIL FLEET-CENSUS-ABSENT d097c70e3cbd:…    rc=1
C1 v3, pair filing but no --sources-rev-*:  CANNOT-EVALUATE flagged filing at LOG.md:2 needs --sources-rev-before/after   rc=2
```

**Poisoned repo-config probe (the scrub is load-bearing).** I poisoned a fixture's **local** config
with every vector that could execute repo-controlled code, then ran both v3 counters:

```
=== poisoned config: core.repositoryformatversion=0 … diff.external=sh -c 'echo EXTERNAL > …/M-external' … core.hooksPath=…/hooks …
=== run C1 v3 ===
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=55b56e65f805 base=55b56e65f805
rc=0
=== run C2 v3 ===
PRISTINE FAIL FLEET-CENSUS-ABSENT 55b56e65f805:census/round-52/records/fleet-root-census.tsv
=== markers written by repo-controlled config? ===
NONE (no repo-controlled command executed)
=== ambient GIT_CONFIG_COUNT injection attempt ===
NONE (ambient env not inherited; env fully replaced)
```

`diff.external`, `diff.<drv>.textconv`, `core.fsmonitor`, `core.pager`,
`uploadpack.packObjectsHook`, `include.path` and `core.hooksPath` were all neutralised. The
counters' env is **replaced, not merged**, so an ambient `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`
cannot reach git. The reachable git command set is `show` and `diff --numstat` only.

---

## Check 6 — Control files

### Final line parses as `EXIT=<nonzero>` — **PASS**

```
$ tail -1 census/round-54/controls/c1-control-donothing.txt | cat -A
EXIT=1$
$ tail -1 census/round-54/controls/c2-control-donothing.txt | cat -A
EXIT=1$
```

Both are `EXIT=1` (nonzero) and both are the **last** line.

### Embedded v2-arm rows match a fresh run of the frozen v2 counters — **PASS, byte-identical**

I rebuilt all fixtures from scratch (my own manifest) and re-ran the **frozen r53** counters over
F7-F12b and FA4/FA5, then diffed against the rows embedded in the control files.

```
$ diff <(tail -n +2 $S/fresh-c1-v2-F7-F12b.tsv) $S/emb-c1.tsv && echo "IDENTICAL"
IDENTICAL
$ diff <(tail -n +2 $S/fresh-c2-v2-FA4-FA5.tsv) $S/emb-c2.tsv && echo "IDENTICAL"
IDENTICAL
```

Fresh v2 rows (the control's embedded rows, verbatim):

```
F7-TILDE-FENCE	v2-r53	2daa874557c2	2daa874557c2	0	-	SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 recomputed=79 rev=2daa874557c2 base=2daa874557c2
F8-BT4-PARITY	v2-r53	5a0fafb73fe6	5a0fafb73fe6	0	-	…
F9-HTML-COMMENT	v2-r53	fafd3a2e582f	fafd3a2e582f	0	-	…
F10-STRADDLE	v2-r53	aa36dab9c2ca	aa36dab9c2ca	0	-	…
F11-BOGUS-RECOMP	v2-r53	7325d506da78	7325d506da78	0	-	SUMMARY … mismatches=1 filed=1 unfiled=0 …
F12-LOG-UNFILED	v2-r53	ea328890f5c1	ea328890f5c1	0	-	…
F12b-LOG-FILED	v2-r53	2f6ce4b930a0	2f6ce4b930a0	0	-	…
FA4-SPACE-NAME	v2-r53	e0aabc60013d	-	0	-	SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok rev=e0aabc60013d
FA5-EXTRA-KEY	v2-r53	2a6fdc6df02b	-	0	-	SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok rev=2a6fdc6df02b
```

**Every rev matches the control byte-for-byte** — the pinned dates reproduce the fixture revs, and
the v2 arm is genuinely a vacuity control (v2 exits **0** on every new attack fixture, so the v3
kills are not v2 kills in disguise).

### v3 arm over the same fixtures — **kills as claimed, and reproduces the L1's matrix exactly**

```
F7-TILDE-FENCE	v3-r54	…	1	CORRECTION-IN-FENCE	SUMMARY … fenced=2 …
F8-BT4-PARITY	v3-r54	…	1	CORRECTION-IN-FENCE	…
F9-HTML-COMMENT	v3-r54	…	1	CORRECTION-IN-FENCE	…
F10-STRADDLE	v3-r54	…	1	ZONE-TOKEN-STRADDLES-EDGE	…
F11-BOGUS-RECOMP	v3-r54	…	1	BOGUS-RECOMPUTED	…
F12-LOG-UNFILED	v3-r54	…	1	UNFILED-SOURCES-ANNOTATION	…
F12b-LOG-FILED	v3-r54	…	0	-	…
FA4-SPACE-NAME	v3-r54	…	1	COMMENT-AMBIGUOUS-NAME	…
FA5-EXTRA-KEY	v3-r54	…	1	RECEIPT-UNKNOWN-KEY	…
```

Reproducibility of the L1's committed matrices (my rebuild vs. `records/c1-matrix-v3.tsv` /
`c2-matrix-v3.tsv`):

```
$ diff <(tail -n +2 $S/mine-c1-v3.tsv) <(tail -n +2 census/round-54/records/c1-matrix-v3.tsv) && echo "IDENTICAL"
IDENTICAL
$ diff <(tail -n +2 $S/mine-c2-v3.tsv) <(tail -n +2 census/round-54/records/c2-matrix-v3.tsv) && echo "IDENTICAL"
IDENTICAL
```

**FA6 CRLF ordering — confirmed.** The control claims v3 prints `CAPTURE-CRLF` first while v2
drowns it. Measured:

```
v2 on FA6 (18 FINDING lines; the first is the spurious receipt mismatch):
FINDING CAPTURE-RECEIPT-MISMATCH TOOL_SHA256 receipt=f509d0cb0d6d tool=f509d0cb0d6d capture=-
FINDING CAPTURE-RECEIPT-MISMATCH FLEET_HEAD receipt=0123456789ab capture=-
…
v3 on FA6 (first line is the named class):
FINDING CAPTURE-CRLF capture bytes carry CR (carriage return)
FINDING CAPTURE-RECEIPT-MISMATCH TOOL_SHA256 …
```

---

## S1 (HIGH) — the C1 fence refusal is defeated by an exotic line separator

**Exploit path.** `c1-counter.py` computes the line number of a correction two different ways:

* `hidden_lines()` enumerates the file with `text.splitlines()` and returns the 1-based indices of
  the *hidden* (fenced / HTML-commented) lines;
* the correction's own line number is `corr.count('\n', 0, m.start()) + 1` — a plain **newline**
  count.

`str.splitlines()` breaks on `\x0b \x0c \x1c \x1d \x1e \x85 \u2028 \u2029` **as well as** `\n`.
Any of those bytes in `SCORECARD.md` shifts the two numbering schemes apart by one per separator.
The fence check then tests `corr_no in hidden` — and the correction's real line number is not in
the hidden set, so **a correction that lives inside a `~~~` fence is not recognised as fenced**.

Minimal repro against the frozen counter's own functions:

```
$ python3 - <<'PYEOF'   # execs the frozen c1-counter.py's hidden_lines()
body = "# header\n\n| C1 | (78) |\n"
corr = "R52-CORRECTION SCORECARD.md:4 stale=78 recomputed=79\n"
text_plain = body + "```text\n" + corr + "```\n"
text_ff   = body + "\x0c\n```text\n" + corr + "```\n"
plain (no exotic separator)      hidden=[5]   corr_line_no(newline-count)=5  -> in hidden? True
one form feed U+000C             hidden=[7]   corr_line_no(newline-count)=6  -> in hidden? False
splitlines() boundary chars: ['0xb', '0xc', '0x1c', '0x1d', '0x1e', '0x85', '0x2028', '0x2029']
str.splitlines() splits on all of the above; corr_line_no counts ONLY '\n'.
PYEOF
```

End-to-end on a real fixture repo: **P16 is the F7 shape verbatim** (both corrections inside a
`~~~` tilde fence) **plus two `U+000C` bytes**:

```
$ GIT_OPTIONAL_LOCKS=0 git -C $P/P16-F7-TILDE-FF2 show HEAD:SCORECARD.md | cat -A
# fixture SCORECARD (probe, P16-F7-TILDE-FF2)$
$
| row | note |$
|---|---|$
| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |$
$
^L$
^L$
~~~$
R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79$
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79$
~~~$
$
$ python3 -B census/round-54/c1-counter.py --root $d --rev $r --base $r --record-sha256 d55ffd7f… --scratch $S
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=c802abe1fd9c base=c802abe1fd9c
rc=0
```

**`fenced=0`, `filed=2`, `unfiled=0`, exit 0.** The two corrections that live inside a `~~~` fence
are credited as **valid filings** and the counter reports the lane green. Compare the *same*
fixture without the form feeds — the committed F7 shape, which the round correctly kills:

```
$ python3 -B census/round-54/c1-counter.py --root <F7> --rev … --base … --record-sha256 … --scratch $S
FINDING CORRECTION-IN-FENCE …
SUMMARY … filed=0 unfiled=2 … fenced=2 …          rc=1
```

**Two form feeds are enough because the offset must exceed the distance from the fence's hidden
lines to the correction's lines.** With one `U+000C` the offset is 1 and only one of the two
corrections slips past (P1/P8/P9: `fenced=1`, one correction mis-credited as a filing,
`unfiled=1`, rc=1 — a *false* result in the other direction); with two the offset is 2 and both
slip past. The same holds for the HTML-comment variant (P24: `<!-- … -->` + 2×`U+000C` → the
`CORRECTION-IN-FENCE` finding survives but is attached to the wrong correction,
`FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:11 (site census/round-51/preregistration.txt:3)`).

**Second consequence — a false positive on an honest lane.** Put the separator *before* the
anchor line instead (P17) and the honest, unfenced correction is judged against the wrong line:

```
$ python3 -B census/round-54/c1-counter.py --root <P17> …
FINDING INERT-CORRECTION SCORECARD.md:5 line 5 of SCORECARD.md carries no anchor
SITE path=SCORECARD.md line=7 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 … rc=1
```

The counter's own `SITE … line=7` proves it is reading a **different line numbering** than the
one a reader (or a filing) uses.

**Impact.** The C1 claim's headline is "the annotation-agreement counter v3 instruments the r53
routed filing surfaces", and F7/F8/F9 are precisely the hidden-filing grammar. A single control
byte in the audited file removes the refusal. It also means the counter's **`filed=` accounting is
not trustworthy** on such a file — and `filed` is what the summary and the prereg's promised
`unfiled=0` line are built on.

**Reachability.** The audited bytes are `SCORECARD.md` at a revision — content the lane's own
agents write. Any writer that emits a form feed (a `^L` page break, a stray `\u2028` line
separator, a VT from a copied table) before a fenced correction silently disables the check. I
checked the real lane at the tip: **0 such bytes in `SCORECARD.md`, `LOG.md`,
`corpus/README.md`, `census/round-51/preregistration.txt`** — so the *current* tip is not
exploited, and the round's committed receipts are unaffected. But the counter's stated property
("corrections hidden in a fence are refused") does **not** hold in general, which is exactly r53's
HIGH bar restated.

**Smallest remediation (routed to the L1 as a named limit — I made no edit).** Number the hidden
lines the same way the corrections are numbered: derive the correction's line number from the
`splitlines()` enumeration rather than from a `'\n'` count (or, equivalently, split the file on
`\n` only and treat `\r`/other separators as ordinary characters). One-line class of change in
`hidden_lines()`/`measure()`; no fixture, pin, or prereg change is needed to state the limit.

---

## S2 (MEDIUM) — the UNFILED-SOURCES-ANNOTATION scan only matches the ASCII arrow

**Exploit path.** `c1-counter.py` matches the misread class with

```
PAIR_ANNOT_RE = re.compile(r'(\d+)\s*->\s*(\d+)\s*rows?\b')
```

— **ASCII `->` only**. The lane's own corpus writes the identical idiom with the **Unicode arrow
`→`**, in the very files the scan reads:

```
$ python3 - <<'PYEOF'   # scans LOG.md + corpus/README.md at the tip for any arrow form
  LOG.md  line 1727  UNICODE-ARROW pair=123→127 rows
  LOG.md  line 1845  UNICODE-ARROW pair=156 → 159 rows
  LOG.md  line 1858  UNICODE-ARROW pair=159 → 162 rows
  …
  total pair-annotation lines = 19
PYEOF
```

The same misread class written with `→` is **invisible to the scan**, so the counter exits 0:

```
$ python3 -B census/round-54/c1-counter.py --root <P22, "corpus/SOURCES.md 274 → 275 rows"> --rev … --base … --record-sha256 … --sources-rev-before … --sources-rev-after … --scratch $S
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 … logunfiled=0 logrecomp=0 …
rc=0
```

versus the ASCII spelling of the **same** sentence, which the counter kills:

```
$ python3 -B census/round-54/c1-counter.py --root <P21, "corpus/SOURCES.md 274 -> 275 rows"> --rev … --base … --record-sha256 … --sources-rev-before … --sources-rev-after … --scratch $S
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 274 -> 275 rows but the registry holds 3; no pair-form filing names it
SUMMARY … logunfiled=1 …
rc=1
```

**Impact.** F12-LOG-UNFILED is the r53 R4 misread class the C1 claim names. The instrument covers
one of the two arrow spellings the lane actually uses, so a misread that happens to be written with
`→` — the spelling three existing lane rows use — passes green. **This is exactly the shape of r53's
routed defects**: the r53 misread (LOG.md:2527 / corpus/README.md:870) is itself a *pair* claim,
and the class's own detector is spelling-sensitive.

**Reachability / current state.** On the real lane at the tip the two *over-registry* pairs
(`274 -> 275` at LOG.md:2527 and corpus/README.md:870) are both ASCII and both **filed**
(`R53-CORRECTION LOG.md:2527 stale=274->275 recomputed=198->199`,
`R53-CORRECTION corpus/README.md:870 stale=274->275 recomputed=198->199`), and the recompute is
genuinely re-derived (registry rows at the pinned revs are **198 → 199**, matching the filing's
`recomputed=198->199`):

```
$ for r in f778b9d13157… 9bf9234ae4d1… bfdbb336329e…; do git show $r:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'; done
198
199
200
```

So the real-lane tip is green **for the right reason**, and the claim is not falsified. The gap is
in the instrument's coverage of the class it claims to add.

**A second, narrower gap in the same scan** (same finding, disclosed): the scan only looks at
lines containing the literal `corpus/SOURCES.md`, and the `PTR_RE` pointer exemption
(`[A-Za-z0-9_.\-]+:\d`) exempts a line carrying *any* `word:digits` — so the misread restated as
`SOURCES.md 274 -> 275 rows` (no `corpus/` prefix, P14) or a line that merely mentions a
`path:line` pointer (P10) is also unscanned. Both are **already disclosed** in the prereg's named
limits ("the SOURCES scan is line-based and exempts lines carrying a path:line pointer"); the
**arrow spelling is not** disclosed anywhere. That is why I rate the arrow gap MEDIUM and the other
two as named-limit observations.

**Smallest remediation (routed; no edit made).** Accept both arrow forms in `PAIR_ANNOT_RE`
(`->` and `→`), or normalise the arrow before matching.

---

## S3 (MEDIUM) — the unknown-receipt-key check is uppercase-only

**Exploit path.** `c2-counter.py` detects an unknown receipt key with

```
RECEIPT_KEYS = ['RECEIPT_VERSION', 'TOOL_SHA256', 'FLEET_HEAD', 'CAPTURE_SHA256', 'ENTRIES']
RECEIPT_KV = re.compile(r'# ([A-Z0-9_]+)=(\S+)')
```

`[A-Z0-9_]+` matches **uppercase only**. A receipt key written in any other case or with a dash
is not recognised as a key at all — it is neither counted as one of the five (so it does not make
the receipt malformed) nor flagged as unknown. The counter reports `receipt=ok`:

```
$ # receipt carrying '# generator=fixture-builder' (lowercase)
$ python3 -B census/round-54/c2-counter.py --root <P4> --rev … --capture … --receipt … --scratch $S
SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=n/a …
rc=0

$ # receipt carrying '# MY-KEY=1' (dash)
$ python3 -B census/round-54/c2-counter.py --root <P5> --rev … --capture … --receipt … --scratch $S
SUMMARY entries=3 rows=3 … receipt=ok sorted=ok tool_pin=n/a …
rc=0
```

whereas the **same** key in uppercase is refused — this is the committed FA5 fixture:

```
FA5-EXTRA-KEY  # GENERATOR=fixture-builder
→ FINDING RECEIPT-UNKNOWN-KEY receipt carries unknown key GENERATOR
→ rc=1
```

**Impact.** The r53 R5 surface ("a receipt carrying an unknown `# KEY=VALUE` line is refused") is
covered for exactly one spelling. A receipt whose extra metadata is lowercase or dashed — a
plausible authoring variation, and one a hostile receipt author would choose — passes the
receipt-grammar check green.

**Reachability / current state.** The committed round-54 receipt carries exactly the five expected
keys, so the real-lane receipt is unaffected and the C2 claim is not falsified. Note also that the
capture-side header is **still** allowed to carry unknown keys (a disclosed named limit), so this
gap is receipt-side only.

**Smallest remediation (routed; no edit made).** Match the key with `[A-Za-z0-9_]+` (case-
insensitive) in the *unknown-key* test, while keeping the known-key set uppercase.

---

## S4 (LOW) — the builder's `--work` guard accepts a relative path

**Exploit path.** `init_repo()` does `git(d.parent, 'init', '-q', str(d))` and then
`git(d, 'rev-parse', '--show-toplevel')` and compares `Path(top) != d`. With a **relative**
`--work`, the `git -C <relative>` form resolves against the *new* cwd, so the toplevel comes back
as a doubled path and the guard fires on the wrong comparison:

```
$ cd $S && python3 -B $LANE/census/round-54/fixtures/build-fixtures.py --work rel2 --manifest $S/rel2/m.tsv
fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).
rc=1
$ find $S/rel2 -maxdepth 3 -name '.git' -o -maxdepth 3 -type d | sort
/fast/scratch/hyaku/souji-r54/S54sentinel01/rel2
/fast/scratch/hyaku/souji-r54/S54sentinel01/rel2/F1-HONEST-TIP
/fast/scratch/hyaku/souji-r54/S54sentinel01/rel2/rel2
/fast/scratch/hyaku/souji-r54/S54sentinel01/rel2/rel2/F1-HONEST-TIP
/fast/scratch/hyaku/souji-r54/S54sentinel01/rel2/rel2/F1-HONEST-TIP/.git
```

**No write escapes the process cwd** (the stray tree is under the cwd, not elsewhere), and the
run **fails closed** with rc=1 — the toplevel guard is doing its job, just with a confusing
message. The counter's selftest inherits the same fragility: a relative `--work` makes the
selftest die with the same git error rather than a clean refusal.

**No reachable exploit** — a hardening item. **Smallest remediation (routed; no edit made).**
Resolve `--work` to an absolute path (`Path(ns.work).resolve()`) before use, and compare the
toplevel against the resolved path.

---

## S5 (LOW / named limit) — the C1 docstring promises a `PRISTINE FAIL` it never emits

`c1-counter.py:46` — "Exit 1: any finding (**PRISTINE FAIL** included)." — but the file contains
no `PRISTINE FAIL` emitter:

```
$ grep -n "PRISTINE" census/round-54/c1-counter.py
46:Exit 1: any finding (PRISTINE FAIL included).
```

The C1 absent-record path is `CANNOT-EVALUATE` / exit **2**, not a `PRISTINE FAIL` / exit 1:

```
$ python3 -B census/round-54/c1-counter.py --root <d> --rev 0000000000000000000000000000000000000000 --base <r> --record-sha256 d55ffd7f… --scratch $S
CANNOT-EVALUATE record absent at 000000000000: census/round-51/records/ws-drift-vs-r46.tsv
rc=2
```

The C2 counter does emit one (`c2-counter.py:123`, `PRISTINE FAIL FLEET-CENSUS-ABSENT …`, rc=1),
so the C1 docstring is a copy-paste leftover. The prereg's C1 kill clauses are written against
exit codes, not against the class name, so **the claim is unaffected**; the docstring is stale.
Disclosed as a named limit (documentation), not an edit.

---

## S6 (LOW / named limit) — `--scratch` is accepted and ignored by both counters

See Check 1. `ns.scratch` is never read; only `--work` steers writes. The prereg's own recompute
commands pass `--scratch DIR`:

```
preregistration.txt:  python3 -B census/round-54/c1-counter.py --root LANE --rev FULL40 --base fe12daad… --record-sha256 2b90a26… --sources-rev-before f778b9d1… --sources-rev-after 9bf9234a… --scratch DIR.
preregistration.txt:  python3 -B census/round-54/c2-counter.py --root LANE --rev FULL40 --capture … --receipt … --tool-sha256 e7e79952… --scratch DIR.
```

so the flag is inert in the very commands the prereg prescribes. Harmless (the counters write
nothing at all in non-selftest mode), but the name implies an effect it does not have.

---

## Standing checks I re-verified (read-only)

```
$ python3 -B census/round-54/c1-counter.py --root $LANE --rev bfdbb336… --base fe12daad… --record-sha256 2b90a26… --sources-rev-before f778b9d1… --sources-rev-after 9bf9234a… --scratch $S
SUMMARY … unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 …
rc=0
$ python3 -B census/round-54/c2-counter.py --root $LANE --rev bfdbb336… --capture census/round-54/records/fleet-root-census.tsv --receipt census/round-54/records/fleet-root-census-run.txt --tool-sha256 e7e79952… --scratch $S
SUMMARY entries=49 rows=49 … receipt=ok sorted=ok tool_pin=ok rev=bfdbb336329e
rc=0
$ python3 -B tools/souji-census-receipt.py verify --receipt census/round-54/records/census-before-receipt.txt
VERIFY ok … conf_rc=0 dir_rc=0 w04=61 result=ok … rc=0
```

- The lane's `git status --porcelain` shows **only the L1's own untracked artifacts**; I created
  none and modified none.
- `git show 3c394cab:…` hashes equal the working-tree hashes for all six instruments (Check 3).
- The fleet root was touched **read-only** (`git rev-parse HEAD`, `git log`, `git merge-base
  --is-ancestor`); its HEAD is `9b0320b2d56e1bfc5bc5ba94bbb463381d551860`, and the capture's
  `FLEET_HEAD=3b0d5329…` is an ancestor of it.

---

## Scope discipline

- **No subagent dispatched** (leaf member).
- **No committed lane file edited.** `census/`, `tools/`, `tests/`, `corpus/`, `SCORECARD.md`,
  `LOG.md`, `SKILL.md`, `PROVINCE.md` are untouched; the fleet root, sibling lane repos, the git
  index / jj state, `.ufo/state`, `.ufo/watchdog.log`, fleet `templates/` and `scripts/`, and
  `/home/vgpnk/Projects/shokuknow` were never written.
- **No mutating git or jj command** was run against any repo. Every git call in this report is
  read-only (`log`, `show`, `diff`, `status`, `ls-files`, `rev-parse`, `cat-file`, `grep`,
  `check-ignore`, `merge-base --is-ancestor`, `config --local --list`) with
  `GIT_OPTIONAL_LOCKS=0` where the repo is not mine. The **only** commits I made were inside
  throwaway fixture repos I created under my own scratch, with a repo-local fixture identity
  (`user.name=fixture`, `user.email=fixture@invalid`) and pinned dates — exactly as the task
  prescribes; each fixture repo's toplevel was asserted equal to the fixture dir before its first
  commit.
- **Scratch deleted before yield** (`/fast/scratch/hyaku/souji-r54/S54sentinel01`, removed with
  `rm -rf`); all receipts quoted above are in this report. **No tree of mine remains on disk.**
- **No tool installs** were needed this seat: `git`, `python3` (3.14), `sha256sum`, `diff`,
  `grep` on the host were sufficient. Nothing was installed, so there is no tool/channel/reason
  record to report.

## Deliverables

- This report: `.ufo/waves/round-54/w1/S54sentinel01/report.md`
- Lane-relative report path (per the task's `Report:` trailer convention):
  `.ufo/waves/round-54/w1/S54sentinel01.md`
