# W1SimpFixtures — YAGNI review of the two r39 fixtures

Seat: W1SimpFixtures (role: simplifier, UFO-FSD). Advisory: I made **no** edit to the lane and ran no
mutating git/jj command. Every experiment ran in `/fast/scratch/hyaku/souji-r39/W1SimpFixtures`
against bytes extracted with `git show` into that scratch.

Axes named: **weight** (bytes a reader must hold), **operability** (does a deletion keep the
counter contract runnable), **coverage** (assertions lost). A move is kept only if it improves one
and harms none.

## Pinned revisions

```
$ git rev-parse HEAD
d4c17557b92fd98044e4c8f0ddc79c6d75701b15
$ git log --oneline -1
d4c1755 round-39: C3/scratch — honour the caller's TMPDIR in c3-counter git children and the r39-citation-rev tool child (wave-1 W1ExecScratch)
$ git cat-file -t ed30b7f5b77939c9073348d810730bc4f355708d
commit
$ git ls-tree --name-only HEAD tests/fixtures/ | grep r39
tests/fixtures/r39-citation-rev.py
tests/fixtures/r39-drift-record-rules.py
$ git diff --stat 2201778..HEAD -- tests/fixtures/ tools/ census/round-39/
 census/round-39/c3-counter.py      | 9 +++++----
 tests/fixtures/r39-citation-rev.py | 3 ++-
```

The lane moved under this seat between my first and second call (`HEAD` read `2201778e...`, then
`d4c1755...`); every number below is at `d4c17557b92fd98044e4c8f0ddc79c6d75701b15` with base
`ed30b7f5b77939c9073348d810730bc4f355708d`. Both r39 fixtures are tracked at that revision.

## Check 1 — cross-fixture duplication inventory

```
$ wc -l tests/fixtures/r39-drift-record-rules.py tests/fixtures/r39-citation-rev.py
141 tests/fixtures/r39-drift-record-rules.py
129 tests/fixtures/r39-citation-rev.py
$ python3 - <<'PY'   # difflib.SequenceMatcher over the two fixture sources
lines a=142 b=130          # split("\n") elements, i.e. 141 / 129 lines + trailing ""
shared contiguous blocks (>=2 lines): 9
  20 lines: '"""'
  11 lines: '    for name, ok, detail in results:'
   7 lines: '    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"'
   5 lines: '    out = proc.stdout + proc.stderr'
total shared lines in blocks: 59
$ diff <(sed -n '/^def main/,/^if __name__/p' r39-drift-record-rules.py) \
       <(sed -n '/^def main/,/^if __name__/p' r39-citation-rev.py)
7c7
<     tool = args.tool or os.path.join(lane_root, "tools", "souji-worktree-drift.py")
---
>     tool = args.tool or os.path.join(lane_root, "tools", "souji-citation-reconcile.py")
15c15,31
<     results = run_cases(tool, work)
```

Measured duplicated units, and their status:

| unit | drift fixture | citation fixture | identical? | verdict |
|---|---|---|---|---|
| `ENV` | line 28 | line 32 | **byte-identical**, 11 lines | deliberate isolation (Check 2) |
| `sh` | `sh(cmd)` line 44 | `sh(cmd, cwd=None)` line 54 | same subprocess call; differs only by a **dead** `cwd` | isolation; `cwd` is dead (Check 6) |
| repo builder | `make_repo(path)` line 49 | **inlined** in `build()` lines 62-71 | same 4-step `git init -q -b main` / write / add / `commit -qm base` | isolation |
| record-case runner | `run_case(...)` line 67 | `case(...)` line 74 | same `out = stdout+stderr`, same `ok = rc == want_rc and not missing`, same detail format `"rc=%d want=%d missing=%r out=%r"` | isolation |
| `main()` scaffolding | 13 lines | 13 lines | differs in the tool default and the case list only | isolation |
| `SUMMARY` printer | 3 lines | 3 lines | byte-identical | isolation |

```
$ python3 -c "..."   # helper-block comparison
ENV byte-identical: True | lines 11
sh bodies equal: False        # only because of the cwd parameter
detail-format string shared: True
SUMMARY print shared: True
```

**Verdict: duplication across the two fixtures is deliberate isolation — and it is structurally
required, not merely customary (proved in Check 2). Not removable.**

## Check 2 — is the isolation deliberate, or just copied?

Three independent proofs that a shared helper module cannot exist here.

```
$ ls tests/fixtures/*.py | xargs -n1 basename | grep -v "^r[0-9]"
                       # (empty) — no shared helper module among the 49 fixture scripts
$ grep -rn "^import r[0-9]\|^from r[0-9]\|import r39\|import r38" tests/fixtures/*.py
                       # (empty) — no fixture imports another
$ grep -n "candidate = os.path.join\|handle.write(candidate_src)\|\[\"python3\", \"-B\", candidate" \
      census/round-39/c3-counter.py
135:        candidate = os.path.join(scratch, "r39-rules.py")
137:            handle.write(candidate_src)
142:            ["python3", "-B", candidate, "--tool", pristine_tool, "--work", scratch]
$ grep -n "fix = os.path.join(base_scratch\|handle.write(fix_src)\|def run_fixture" \
      census/round-39/c2-counter.py
147:def run_fixture(fixture, tool, scratch, work, extra=None):
238:        fix = os.path.join(base_scratch, "r39-citation-rev.py")
240:            handle.write(fix_src)
```

Both counters copy **only the fixture file** into a scratch directory and execute it there, so
`sys.path[0]` is the scratch directory, not `tests/fixtures/`. Demonstrated directly:

```
$ cp rules.py importdemo/candidate.py && printf 'def shared():\n    return 1\n' > importdemo/r39_shared.py
$ # add `import r39_shared` to candidate.py
$ python3 -B importdemo/candidate.py --tool drift-new.py --work $S
case-indented-comment=PASS
case-comments-total-only=PASS
SUMMARY cases=7 pass=7 fail=0
$ cp importdemo/candidate.py importdemo/scratch/r39-rules.py     # the counter's model: only the fixture is copied
$ python3 -B importdemo/scratch/r39-rules.py --tool drift-new.py --work $S
  File ".../importdemo/scratch/r39-rules.py", line 27, in <module>
    import r39_shared
ModuleNotFoundError: No module named 'r39_shared'
```

**Verdict: KEEP the duplicated `ENV`/`sh`/repo-builder/runner/`main` blocks.** Consolidating them
into a shared module would make C2 L5, C2 L6 and C3 unrunnable — the counter copies the fixture and
nothing else. Removing this duplication would harm operability for zero net weight gain (the shared
module is new bytes in a new file). This is the case my role is supposed to refuse: a deletion that
creates a second convention *and* breaks the measurement rig.

## Check 3 — in-file duplication that IS removable

`run_case` already declares a `newline` parameter that no caller passes, and the `crlf` case
hand-rolls the identical run/assert block instead of using it:

```
$ grep -n "run_case(\|newline" tests/fixtures/r39-drift-record-rules.py
67:def run_case(tool, root, path, body, name, want_rc, want_tokens, results, newline=None):
70:    with open(record, "w", encoding="utf-8", newline=newline) as handle:
88:        run_case(... "good" ...)
89:        run_case(... "trailing-space" ...)
92:        run_case(... "total-before-rows" ...)
105:        run_case(... "outside-root" ...)
108:        run_case(... "indented-comment" ...)
110:        run_case(... "comments-total-only" ...)
$ grep -n "def run_case\|def case\|newline" tests/fixtures/r38-drift-record.py
74:def run_case(tool, root, path, body, name, want_rc, want_tokens, results):
```

`newline` was added this wave (r38's `run_case` has no such parameter) and is dead: the `crlf` case
writes bytes with a separate `mkstemp`/`open(..., "wb")`/`subprocess.run`/assert block, 11 lines
that repeat `run_case` verbatim except for the input encoding.

Proposed deletion (unified diff, measured):

```
$ diff -u rules.py rules-consolidated.py
@@ -91,17 +91,8 @@
                  "trailing-space", 2, ["RECORD-MALFORMED", "does not match the census schema"], results)
         run_case(tool, root, path, TOTAL + ROWS, "total-before-rows", 0,
                  ["SUMMARY", "record_repos=2"], results)
-        fd, crlf = tempfile.mkstemp(prefix="record-crlf-", suffix=".tsv", dir=root)
-        os.close(fd)
-        with open(crlf, "wb") as handle:
-            handle.write((ROWS + TOTAL).replace("\n", "\r\n").encode("utf-8"))
-        proc = subprocess.run(
-            ["python3", "-B", tool, "--root", path, "--record", crlf, "--timeout", "30"],
-            env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
-        )
-        out = proc.stdout + proc.stderr
-        results.append(("crlf", proc.returncode == 0 and "record_repos=2" in out,
-                        "rc=%d out=%r" % (proc.returncode, out.replace("\n", " ")[:160])))
+        run_case(tool, root, path, (ROWS + TOTAL).replace("\n", "\r\n"), "crlf", 0,
+                 ["SUMMARY", "record_repos=2"], results, newline="")
         run_case(tool, root, path,
                  "REPO\t../escape\tregs=1\tprunable=0\n",
                  "outside-root", 2, ["RECORD-OUTSIDE-ROOT"], results)
$ # old block lines=11 new lines=2 ; wc -l total 141 -> 132  (split("\n") elements: 142 -> 133)
```

Behaviour equivalence, pristine plus every frozen mutant, before vs after:

```
$ python3 -B consolidate.py
source lines: original=142 consolidated=133 delta=-9
PRISTINE  orig rc=0 ('7','7','0') failing=[] | cons rc=0 ('7','7','0') failing=[] | identical=True
M11       orig rc=1 ('7','6','1') failing=['trailing-space'] | cons rc=1 ('7','6','1') failing=['trailing-space'] | identical=True
M12       orig rc=1 ('7','6','1') failing=['crlf']          | cons rc=1 ('7','6','1') failing=['crlf']          | identical=True
M13       orig rc=1 ('7','6','1') failing=['outside-root']  | cons rc=1 ('7','6','1') failing=['outside-root']  | identical=True
M14       orig rc=1 ('7','6','1') failing=['indented-comment'] | cons rc=1 ('7','6','1') failing=['indented-comment'] | identical=True
```

And the real counter, pointed at the consolidated bytes via `--fixture`:

```
$ TMPDIR=$S python3 -B census/round-39/c3-counter.py --root . --rev d4c1755... --base-rev ed30b7f... \
      --scratch $S --fixture $S/rules-consolidated.py
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=5d9723003a76
rc=0
```

Against the unmodified fixture the same command reads `fixture_sha=567c37a679f5` and is otherwise
line-for-line identical. The case count (7), the kill map (M11→trailing-space, M12→crlf,
M13→outside-root, M14→indented-comment) and the pristine control are unchanged; the assertion on
`crlf` is marginally **tighter** (it now also requires the `SUMMARY` token). `newline=""` is
required and correct because the body is pre-transformed to `\r\n` and must be written verbatim.

**Verdict: RECOMMEND — delete the 11-line inline block, route `crlf` through `run_case(newline="")`.**
−9 source lines, one runner instead of two, dead parameter revived, battery byte-identical.
This is the only deletion I recommend.

## Check 4 — does any pair assert the same behaviour twice?

```
$ python3 -B matrix.py            # full fixture vs M11-M14
M11 rc=1 cases/pass/fail=('7','6','1') killed=True failing=['trailing-space']
M12 rc=1 cases/pass/fail=('7','6','1') killed=True failing=['crlf']
M13 rc=1 cases/pass/fail=('7','6','1') killed=True failing=['outside-root']
M14 rc=1 cases/pass/fail=('7','6','1') killed=True failing=['indented-comment']
PRISTINE rc=0 cases/pass/fail=('7','7','0') failing=[]
```

The frozen battery is a clean 1:1 map — each rule case is the unique killer of exactly one mutant.

| pair | same expected output? | deletion loses a kill? | verdict |
|---|---|---|---|
| `trailing-space` / `indented-comment` (drift) | yes — rc 2 + `RECORD-MALFORMED` + `does not match the census schema` | **yes**: M11 / M14 respectively → `killed=3` | **not deletable** (breaks C3 `killed=4`) |
| `good` / `total-before-rows` (drift) | yes — rc 0 + `SUMMARY` + `record_repos=2`; inputs differ only in row order | no — counter still reads 4/4 at `cases=6` | keep (see below) |
| `rev-blob` / `rev-tree` (cite) | yes — rc 2 + `REV-UNRESOLVED`; both fail the base arm | no kill notion, but C2 L5 pins 8 cases | not deletable |
| `rev-short` / `rev-symbolic` (cite) | yes — rc 2 + `USAGE`; both **pass** the base arm | no base-arm discrimination lost | not deletable |
| `comments-total-only` (drift) | — not a duplicate; only `RECORD-EMPTY` case | **yes**, for a mutant outside the frozen battery | keep |

Deletion arithmetic, measured with the real counter:

```
$ c3-counter ... --fixture rules-minus-comments-total-only.py
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=6 tool_sha=e48ed08e6728 fixture_sha=f3b06e2ba1d3
$ c3-counter ... --fixture rules-minus-total-before-rows.py
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=6 tool_sha=e48ed08e6728 fixture_sha=57a46a21d7db
$ c3-counter ... --fixture rules-minus-good.py
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=6 tool_sha=e48ed08e6728 fixture_sha=d7b9bc65a057
```

**All three deletions leave the frozen battery green** — the counter cannot see the coverage loss.
That is why each one is judged on its own assertion, not on the summary line.

**`good` / `total-before-rows` — the one genuine same-behaviour pair.** They differ only in row
order and expect the same rc and the same token. Deleting either keeps `cases>=6` and all four
kills, so neither is frozen-battery-load-bearing. I still reject both deletions:

- `total-before-rows` is the **only** case asserting the acceptance class the fixture docstring
  names ("a TOTAL row placed before the REPO rows is accepted"). Deleting it without also deleting
  the docstring sentence would leave the fixture documenting a behaviour it no longer asserts —
  exactly the calibration defect class C1 exists to close. Harm: calibration + coverage, for 2 lines.
- `good` is the only plain-LF baseline; `crlf` covers its assertion only through a transformed
  input. Harm: the fixture loses its readable happy-path anchor, for 1 line.

Polarity probe used to check both directions of the ordering class:

```
$ python3 -B polarity.py
full                     PRISTINE         rc=0 killed=False failing=[]
full                     Y-total-first    rc=1 killed=True failing=['good','crlf']
full                     Y-total-last     rc=1 killed=True failing=['total-before-rows','comments-total-only']
minus-good               Y-total-first    rc=1 killed=True failing=['crlf']
minus-total-before-rows  Y-total-last     rc=1 killed=True failing=['comments-total-only']
```

Neither ordering mutant survives without the pair, so neither case is a pure no-op; they overlap in
coverage rather than duplicating it.

**`comments-total-only` is not a duplicate and is load-bearing against an unfrozen class.** Probe
`X-empty` (tolerates "only a comment + TOTAL" as a non-empty record) survives every other case:

```
minus-comments-total-only  ... X-empty:ok
full / minus-total-before-rows / minus-good ... X-empty:KILL
```

Deleting it would leave a documented refusal class (`RECORD-EMPTY`) asserted nowhere in the r39
fixture while the counter still printed `killed=4`. **Reject.**

**Citation fixture: no deletion is admissible at all.** C2 L5 pins the case count exactly —
`census/round-39/c2-counter.py:244` reads `new_f is not None and new_f[0] == 8` — and prereg
Amendment A1 freezes "the case count (8)". Measured effect of dropping one case:

```
$ python3 -B cite_del.py
full               arm=new  rc=0 cases/pass/fail=('8','8','0') base_fail_ge_2=False failing=[]
full               arm=base rc=1 cases/pass/fail=('8','4','4') base_fail_ge_2=True failing=['rev-unknown','rev-blob','rev-tree','register-rev-gone']
rev-tree           arm=new  rc=0 cases/pass/fail=('7','7','0')   # L5 would read new_f[0]==8 -> False
rev-tree           arm=base rc=1 cases/pass/fail=('7','4','3') base_fail_ge_2=True failing=['rev-unknown','rev-blob','register-rev-gone']
rev-blob           arm=base rc=1 cases/pass/fail=('7','4','3') base_fail_ge_2=True failing=['rev-unknown','rev-tree','register-rev-gone']
register-rev-gone  arm=base rc=1 cases/pass/fail=('7','4','3') base_fail_ge_2=True failing=['rev-unknown','rev-blob','rev-tree']
rev-short          arm=base rc=1 cases/pass/fail=('7','3','4') base_fail_ge_2=True failing=['rev-unknown','rev-blob','rev-tree','register-rev-gone']
rev-symbolic       arm=base rc=1 cases/pass/fail=('7','3','4') base_fail_ge_2=True failing=['rev-unknown','rev-blob','rev-tree','register-rev-gone']
```

Note the asymmetry: the `fail>=2` half of L5 survives every single-case deletion; only the exact
`== 8` half blocks it. So a deletion here would be caught by the counter but *not* by the
discrimination predicate — worth knowing, since the two halves of L5 are doing different work.

**`rev-short` / `rev-symbolic` carry no base-arm discrimination** (both pass at `ed30b7f`); they
guard the 40-hex regex gate against a *new* defect, not against the base defect. They are not
duplicates of each other: a widened-prefix mutant (`^[0-9a-f]{7,40}$`) accepts `rev[:12]` and still
rejects `v1`.

## Check 5 — battery readings my deletions were verified against

```
$ TMPDIR=$S python3 -B census/round-39/c3-counter.py --root . --rev d4c1755... --base-rev ed30b7f... --scratch $S
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
rc=0
$ TMPDIR=$S python3 -B census/round-39/c2-counter.py --root . --rev d4c1755... --base-rev ed30b7f... --scratch $S
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
rc=0
$ cat census/round-39/records/c3-before.txt | tail -1
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
$ tail -1 census/round-39/records/c2-before.txt
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=e555d8281484
```

The `c3-after.txt` SUMMARY line matches my HEAD run on both hashes, so the after-receipt is current
at this revision. Independent base-arm run of the citation fixture reproduces the C2 before-state:

```
$ TMPDIR=$S python3 -B $S/cite.py --tool $S/cit-base.py --work $S
case-rev-unknown=FAIL rc=1 want=2 missing=['REV-UNRESOLVED'] ...
case-rev-blob=FAIL rc=1 want=2 missing=['REV-UNRESOLVED'] ...
case-rev-tree=FAIL rc=1 want=2 missing=['REV-UNRESOLVED'] ...
case-register-rev-gone=FAIL rc=2 want=2 missing=['REV-UNRESOLVED'] out='REFUSAL USAGE: register ... is not at 1111...'
SUMMARY cases=8 pass=4 fail=4
rc=1
```

**Verdict: battery green at HEAD for C2 and C3; the recommended deletion keeps it green.**

## Check 6 — operability observations (no deletion proposed)

1. **Dead `cwd` parameter in `r39-citation-rev.py:54`.** `grep -n "cwd=" tests/fixtures/r36-worktree-drift.py tests/fixtures/r37-drift-discrimination.py tests/fixtures/r39-citation-rev.py`
   returns only the two `def`/`return` lines of each file — no caller passes `cwd` anywhere. The
   same dead parameter pre-exists in r36 and r37, so removing it from the new fixture would not
   converge the lane (two `sh` shapes exist either way: `sh(cmd)` in r38/r39-drift, `sh(cmd, cwd=None)`
   in r36/r37/r39-cite). **Optional, low value; leave to the L1's judgement — it saves 2 characters
   and buys no uniformity.**
2. **No `rev-parse --show-toplevel` assertion in either new fixture.**
   `grep -rn "show-toplevel" tests/fixtures/*.py` matches only r24, r29 and r30 — the lane does not
   require it, and both new fixtures name `-C <path>` on every git call after `git init <path>`, so
   a commit cannot land in an enclosing repo. Not a defect; recorded so the L1 knows the seat-level
   git-fixture rule is satisfied in intent, not literally.

## Verdict summary

| check | verdict |
|---|---|
| cross-fixture `ENV`/`sh`/`make_repo`/runner/`main` duplication | **KEEP — deliberate isolation, structurally required** (counters execute a lone copied file; sibling import raises `ModuleNotFoundError`) |
| in-file `crlf` block vs `run_case(newline=...)` | **DELETE — 11 lines → 2, battery byte-identical** |
| `trailing-space` / `indented-comment` | **KEEP** — each is a frozen mutant's unique killer |
| `good` / `total-before-rows` | **KEEP** — same-behaviour pair, but deleting either drops a documented acceptance class the docstring names; 1-2 lines saved is not worth it |
| `rev-blob` / `rev-tree`, `rev-short` / `rev-symbolic` | **KEEP** — C2 L5 pins `cases == 8` (`c2-counter.py:244`); `rev-short`/`rev-symbolic` also guard a new-defect class |
| `comments-total-only` | **KEEP** — only `RECORD-EMPTY` case; deleting it lets an unfrozen mutant survive invisibly |
| dead `cwd` in `sh` | optional, not recommended this wave |
| battery at HEAD | `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7`; `legs=6 pass=6 fail=0 harm=0` |

Preserved contract: nothing in C1/C2/C3 changes under the one recommended deletion — case counts
(7 drift / 8 citation), kill map, base-arm discrimination, and both counters' summary lines are
unchanged. Tradeoff: the recommended edit is a weight-only improvement inside one file; the
cross-fixture duplication stays, because removing it would trade readable isolation for a rig that
cannot execute.

Scratch: **still on disk** at `/fast/scratch/hyaku/souji-r39/W1SimpFixtures` — it holds the
extracted tool bytes, the mutant matrix scripts, the four deletion variants and
`rules-consolidated.py` (the recommended edit, ready to copy). Deliberately retained so the L1 can
re-run the evidence or apply the diff without re-deriving it.

Write scope: this seat wrote exactly one path — `.ufo/waves/round-39/w1/W1SimpFixtures.md` (gitignored
by `.gitignore:1`), plus its own scratch. No lane byte was modified **by this seat**; `git status`
at the end of the seat shows `M LOG.md`, `M SKILL.md`, `M corpus/QUALITY.md` and five untracked
`census/round-39/` files, all of which are other seats' in-flight edits (the lane also gained
commit `d4c1755` mid-seat). No mutating git/jj command was run. No tool installed.
