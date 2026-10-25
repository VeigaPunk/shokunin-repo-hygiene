# RevImplA — raw evidence (round 22, attempt 2, w1) — C1 declared-evidence tool

Companion to `.ufo/waves/round-22/attempt2/w1/RevImplA.md`.
Read-only review: no lane file was edited. Fixtures were built only under `/var/tmp/revimpla/`.

## 0. Target resolution

```
$ ls .ufo/waves/round-22/attempt2/w1/evidence/
snap-filetrash.raw  snap-mv1.raw  snap-statx2.raw  snap-trashspec.raw
$ ls .ufo/waves/round-22/attempt2/w1/evidence/impl-a/
ls: cannot access '.../evidence/impl-a/': No such file or directory
```

The assigned path does not exist. The candidate is the committed artifact the frozen
counter command names:

```
$ git log --oneline --follow -- tools/souji-declared-evidence.py
a211e4d round-22: declared-evidence audit tool, assimilation entries and gate checker
$ git rev-parse a211e4d:tools/souji-declared-evidence.py
f388642ca182cae9dbe82f07a53f5fd7cc8f274c
$ git rev-parse HEAD:tools/souji-declared-evidence.py
f388642ca182cae9dbe82f07a53f5fd7cc8f274c
$ git merge-base --is-ancestor a211e4d HEAD && echo yes
yes
$ git diff --stat HEAD -- tools/souji-declared-evidence.py     # (empty)
$ sha256sum tools/souji-declared-evidence.py
58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2  tools/souji-declared-evidence.py
```

HEAD = `2a130b47db43eb4b3d80b2e7a5112d6b4b021899`; base = `4edb25dfe262515d0da63224bbba71e02e36cba5`
(`git cat-file -e <base>^{commit}` ok; `SCORECARD.md` present at both).

## 1. Frozen counter line and exit codes (executed)

```
$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md \
    --rev 4edb25dfe262515d0da63224bbba71e02e36cba5 --format counts
assertions=56 resolved=53 skipped=33 mismatches=3
RC=1

$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md \
    --rev 2a130b47db43eb4b3d80b2e7a5112d6b4b021899 --format counts
assertions=56 resolved=56 skipped=36 mismatches=0
RC=0

$ ... --rev 4edb25d --format counts        # abbreviated rev
assertions=56 resolved=53 skipped=33 mismatches=3
RC=1

$ ... --rev 0000000000000000000000000000000000000000
stdout=''   stderr='revision does not resolve: 0000...'   rc=1
```

Base mismatches (tsv, filtered):

```
3	AXES.md	A	mismatch:path-absent	not in tree at 4edb25d...
63	reason-after.txt	A	mismatch:path-absent	not in tree at 4edb25d...
77	.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md	A	mismatch:path-absent	not in tree at 4edb25d...
assertions=56 resolved=53 skipped=33 mismatches=3
```

HEAD class B rows:

```
14	4edb25dfe262515d0da63224bbba71e02e36cba5	B	resolved	commit/object resolves
38	6f8ee0f	B	resolved	commit/object resolves
54	31984f4	B	resolved	commit/object resolves
64	5fa6017	B	resolved	commit/object resolves
114	29c1f7e8df849be8ee1b2d62d2351e17ec9d21a8	B	resolved	commit/object resolves
```

Token-set delta base -> HEAD (`cut -f2,3 | sort` diff):

```
3c3   < 41553adb139d06511dc386bb3ce4326aebfba675	B
      > 4edb25dfe262515d0da63224bbba71e02e36cba5	B
6,8c6 < AXES.md	A          (removed)
      > census/round-21/reason-after.txt	A   (was: reason-after.txt	A)
28a27,29 > census/round-22/attempt2/declared-evidence-before.tsv	A   (x2)
44a46    > corpus/lessons/round-22-verifier-spotcheck.md	A
56d56    < .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md	A  (removed)
```

## 2. Selftest transcript (executed)

```
$ python3 -B tools/souji-declared-evidence.py --selftest
PASS fixture1 all-good -> 0 [assertions=2 resolved=2 skipped=0 mismatches=0]
PASS fixture2 absent path -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture3 dangling rev -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture4 wrong digest -> mismatch [assertions=3 resolved=2 skipped=0 mismatches=1]
PASS fixture5 path only at other rev -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture6 correct digest -> resolved [assertions=3 resolved=3 skipped=0 mismatches=0]
PASS control always-zero -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
PASS fixture7 command span -> skipped, not asserted [assertions=0 resolved=0 skipped=1 mismatches=0]
selftest=8/8
SELFTEST_RC=0
```

## 3. Compile / lint (executed)

```
$ python3 -m py_compile tools/souji-declared-evidence.py        -> rc=0
$ pyflakes tools/souji-declared-evidence.py                     -> rc=0 (clean)
$ ruff --version                                                -> ruff 0.17.2
$ pyflakes --version                                            -> 4.0.3 Python 3.14.8 on Linux
$ file tools/souji-declared-evidence.py
tools/souji-declared-evidence.py: Python script, Unicode text, UTF-8 text executable   # shellcheck N/A

$ ruff check --no-cache tools/souji-declared-evidence.py
Found 31 errors.   per-code: UP031 x19, C408 x5, PLW1510 x3, UP022 x2, FURB167 x1, SIM115 x1
$ ruff check --no-cache --select E9,F63,F7,F82,S,B tools/souji-declared-evidence.py
54:15: S603 subprocess call: check for execution of untrusted input
206:15: S603
274:13: B007 Loop control variable `key` not used within loop body
275:19: S603
287:9: S603
287:24: S607 Starting a process with a partial executable path
```

No E9/F63/F7/F82 diagnostics. All findings are style/robustness.

## 4. Adversarial fixtures (executed, all under /var/tmp)

### P1 — declaration absent at `--rev` is silently read from the worktree
```
repo: c1 = {docs/a.md}; c2 = {docs/b.md, SCORECARD.md asserting docs/b.md}
worktree SCORECARD.md then overwritten to assert docs/a.md (uncommitted)
$ tool --root repo --file SCORECARD.md --rev c1 --format counts
rc=0  assertions=1 resolved=1 skipped=0 mismatches=0
```
Contract: SCORECARD.md is not tracked at c1, so no committed bytes exist to audit.
Observed: green, on uncommitted bytes.

### P2 — class A ignores the worktree (correct)
```
c1 = {tools/keep.py, SCORECARD.md asserting tools/ghost.py}; tools/ghost.py created untracked
rc=1  assertions=1 resolved=0 skipped=0 mismatches=1
```

### P3 — class C is over `git show` bytes, not the worktree (correct, airtight)
```
committed tools/f.txt sha256 = cc2e4bb5... ; worktree tools/f.txt sha256 = abe9c207...
declaration (committed, rev 658cc5f) declares the WORKTREE digest abe9c207...
rc=1
3	tools/f.txt	A	resolved	present at 658cc5f...
3	abe9c207...	C	mismatch:digest	sha256 is cc2e4bb5...
3	a59a3ec	B	resolved	commit/object resolves
assertions=3 resolved=2 skipped=0 mismatches=1
```
Positive direction: with the worktree dirty and the declaration (committed) declaring the
committed digest, the run is `mismatches=0`.

### C3/C4 — uppercase 64-hex digest is skipped
```
| sha256 `AAAA...A` (64 x 'A', wrong) on `tools/f.txt` | measured commit 092748a |
rc=0  assertions=2 resolved=2 skipped=1 mismatches=0
| sha256 `<true sha, uppercased>` on `tools/f.txt` | measured commit 092748a |
rc=0  assertions=2 resolved=2 skipped=1 mismatches=0
```

### C5 — punctuation after a hex token removes it from both N and S
```
| measured at deadbeef. | x |   -> rc=0  assertions=0 resolved=0 skipped=0 mismatches=0
| measured at deadbeef- | x |   -> rc=0  assertions=0 resolved=0 skipped=0 mismatches=0
| measured at deadbeef_ | x |   -> rc=0  assertions=0 resolved=0 skipped=0 mismatches=0
| measured at deadbeef, | x |   -> rc=1  assertions=1 ... mismatches=1
| measured at deadbeef; | x |   -> rc=1  mismatches=1
| measured at deadbeef) | x |   -> rc=1  mismatches=1
| measured at deadbeef: | x |   -> rc=1  mismatches=1
| measured at `deadbeef` | x |  -> rc=1  mismatches=1
```

### P6 — glob `*` crosses `/`
```
tracked: corpus/knowledge/x.md only ; declaration `corpus/*.md`
tool   rc=0  assertions=1 resolved=1 skipped=0 mismatches=0
shell  bash -c 'ls corpus/*.md'  -> rc=2 (no match at that depth)
```

### P7 — hex in a non-table prose line becomes class B
```
declaration: "We measured commit deadbeefdeadbeefdeadbeefdeadbeefdeadbeef earlier."
rc=1  assertions=1 resolved=0 skipped=0 mismatches=1
```

### P8 — `rev:path` resolves against a revision other than `--rev`
```
c1 has docs/old.md; c2 has SCORECARD.md with `7425453:docs/old.md` and NO docs/old.md
$ tool --rev c2
rc=0  assertions=1 resolved=1 skipped=1 mismatches=0
```

### P9 — `:line` suffix (correct)
```
| `tools/x.md:1` | see |  | `tools/nope.md:9` | see |
rc=1  assertions=2 resolved=1 skipped=0 mismatches=1
```

### C6/C7 — class C "exactly one path" (correct)
```
digest + two paths   -> rc=0 assertions=2 resolved=2 skipped=2 mismatches=0   (no C assertion)
digest + no path     -> rc=0 assertions=0 resolved=0 skipped=2 mismatches=0   (no C assertion)
```

### Path-charset probes (absent paths, none exist)
```
| `docs/a+b.md` | see |   -> rc=0 assertions=0 resolved=0 skipped=1 mismatches=0
| `docs/a@b.md` | see |   -> rc=0 assertions=0 resolved=0 skipped=1 mismatches=0
| `docs/a b.md` | see |   -> rc=0 assertions=0 resolved=0 skipped=1 mismatches=0
| `census/round-[0-9]*/x.json` | see | -> rc=0 assertions=0 skipped=1 mismatches=0
| `AXES.md` (absent) | see |        -> rc=1 mismatches=1   (correct)
| `corpus/round-21/reason-after.txt` (absent) | see | -> rc=1 mismatches=1  (correct)
```

### C8 — same revision, relative vs absolute `--file`
```
relative (committed bytes): rc=0  assertions=1 resolved=1 skipped=0 mismatches=0
absolute (worktree bytes):  rc=1  assertions=1 resolved=0 skipped=0 mismatches=1
```
All selftest fixtures pass absolute paths, so the committed-branch is never exercised there.

### Missing declaration file
```
$ tool --root . --file DOES-NOT-EXIST.md --rev HEAD --format counts
Traceback ... FileNotFoundError: [Errno 2] ... DOES-NOT-EXIST.md
RC=1
```

## 5. Read-only audit — every write/git site (source read)

```
79:   with open(path, "r", ...)                             read only
184-185: out.write(...)                                     caller's stream (stdout / StringIO)
201,212: os.makedirs(repo / repo/tools)                     inside base = mkdtemp(dir=/var/tmp)
213-230: open(..., "w") / _write                            inside base
242:   base = tempfile.mkdtemp(prefix=..., dir="/var/tmp")
287:   subprocess.run(["rm","-rf",base])                    base only
290-291: out.write(...)                                     selftest report to stream
55:    git -C <root> -c maintenance.auto=false <plumbing>
       subcommands issued by the measurement path: rev-parse --show-toplevel,
       cat-file -e <rev>^{commit}, ls-tree -r --name-only, show <rev>:<path>
```
No write path exists outside the `/var/tmp` mktemp (selftest only) and the output stream.
`/tmp` occurrences: lines 17 (comment "scratch under /var/tmp") and 242 (`dir="/var/tmp"`) only.

## 6. Tooling record (this review)

- `~/.local/share/uv/tools/` was removed on the host mid-review (broken symlinks
  `/home/vgpnk/.local/bin/{ruff,pyflakes}`); `uv tool install` reported success then the tree was
  gone again. No pacman transaction was attempted (transactions paused host-wide).
- Final channel: `uv venv /var/tmp/revimpla/venv` + `uv pip install ruff pyflakes`
  -> ruff 0.17.2, pyflakes 4.0.3 (runtime Python 3.14.8). Reason: Q9 lint requirement.
- No other installs; no repo writes.
