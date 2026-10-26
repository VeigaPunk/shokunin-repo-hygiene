# SwarmCritic34 — attack seat on claim C2 (round 32, w1)

## Status
STATUS: FAIL — claim C2's frozen pass predicate is satisfiable without the property it claims: two cheat
commits score `pass=1` under the real counter (`--only T06`), one of them running zero selftest cases, and
one rule-matched item that is absent from the frozen set fails under the same counter.

## Evidence

Lane read-only throughout; every clone, item-list mutation and cheat commit lives in
`/fast/scratch/hyaku/souji-r32/AttackC2/` (deleted after the report was written). Revisions used:
base `85b61a151923986e7e6b48f7084b9122561b5f3d`, prereg `3ec84fc8…` (items list), lane tip `7a6667cd…`
(counter bytes, controls).

1. Frozen predicate, `census/round-32/c2-counter.py:174-176` (opened from the lane working tree at `7a6667cd…`):
   `ok_a = rc1 == rc0 and s1 == s0 and s0 != "NONE"` / `ok_b = w1 * 2 >= w0` / `ok = ok_a and ok_b`.
   `s*` is the last digit-bearing stdout line (`summary_line`, :67-73); `w*` is a gross count of any
   successful `mkdir|mkdirat|creat|open*O_CREAT` anywhere in the trace (`creations`, :75-90). Neither value
   says *where* a file was created or *which* work ran.
2. Full base reading (base==REV==`85b61a1…`, counter at lane tip, `--scratch` in my scratch):
   `SUMMARY items=27 pass=1 fail=26 rev=85b61a1…`; the single base pass is T03 with
   `base=rc1:W0 … sbox=rc1:W0`. Prereg's "26 of 27 FAIL" reproduces.
3. Cheat A (`dc318437ce0bfc196818e9ad02ddd8e762af49b8`, patch below): T06 scored
   `ITEM T06 PASS base=rc0:W110:SUMMARY total=11 failed=0 sbox=rc0:W111:SUMMARY total=11 failed=0`, exit 0.
4. Cheat B (`e36b78f4bd5fdfa4a970878171ed6efbe4f66ac6`, patch below): T06 scored
   `ITEM T06 PASS base=rc0:W110:SUMMARY total=11 failed=0 sbox=rc0:W60:SUMMARY total=11 failed=0`, exit 0,
   although the sandboxed run executes no case at all.
5. Enumeration test (`18fc8d082ef3d68c164bcba53a953700dfa568c2`, adds one row to a copy of the frozen list):
   `ITEM TV1 FAIL base=rc0:W2271:selftest: 57 checks, 0 failed sbox=rc1:W1455:selftest: 42 checks, 1 failed`,
   exit 1. TV1 is `bash tools/souji-vault-verify.sh --selftest`, which matches the frozen rule but is not
   in `c2-items.tsv` and is not named in any of its exclusions.
6. T13 exclusion check (base clone, `/var/tmp` and `/tmp` bound to scratch dirs):
   `rc=0`, last line `souji-proc-census: selftest PASS (newline comm parser, live literal cwd/fd, …)`,
   `grep -c '[0-9]'` on the whole output = `0`. The header's "no digit-bearing line at base" reason is true.

## Findings

1. **Predicate gap.** `census/round-32/c2-counter.py:174-176` — `ok_a` is string equality on a
   self-reported summary line and `ok_b` is a gross creation count. There is no assertion that a creation
   landed under the run's `TMPDIR`, and no assertion that the run's case-level output matches BASE. The
   counter therefore cannot distinguish "honours TMPDIR and does its work" from "writes anywhere writable
   and prints the expected last line".
2. **Cheat A — clone-local scratch passes.** Scratch under `tools/../.selftest-scratch` inside the clone
   (writable because the sandbox is `--dev-bind / /`, `:154-155`) while the caller's `TMPDIR` is never
   read: `PASS`, `W111 >= 110/2`. This is exactly the "set TMPDIR to the lane" evasion; the counter's
   pre-run `git clean -fdxq` (`:146`) even removes the residue. `TMPDIR` honour is asserted nowhere.
3. **Cheat B — sandbox detection plus fabricated anchor passes.** `mkdtemp(dir="/var/tmp")` raises
   `EROFS`; the cheat then runs no cases, prints BASE's literal summary line, and creates 60 dummy files in
   `TMPDIR`: `PASS` with `W60 >= 55`. The half-of-base rule does **not** catch a selftest that silently
   skips cases; it only catches a selftest that stops creating files.
4. **The work gate is vacuous when BASE creates nothing.** T03 at base is `W0` in both runs, so `ok_b`
   (`0*2 >= 0`) is always true (evidence 2). Any item whose base run touches no scratch gets a free pass.
5. **Unenforced surfaces.** The sandbox makes only `/tmp`, `/var/tmp`, `/dev/shm` read-only
   (`:154-155`); the clone and `$HOME` stay writable, and the strace summary counts creations everywhere.
   The claimed property "TMPDIR a scratch dir" is enforced only negatively, and only for three paths.
6. **The set is not the closure of its own rule.** The rule's trigger list includes
   `census/round-32/c2-items.tsv:4` — quote: "a child env TMPDIR/HOME of /var/tmp, or ${TMPDIR:-/var/tmp}".
   `tools/souji-vault-verify.sh:742` is literally `export TMPDIR="${TMPDIR:-/var/tmp}"`, its
   `--selftest` is self-contained and a base-passing anchor, and the counter fails it (evidence 5). It is
   absent from the 27 items and from the header's exclusion list (which names only the three r21 files and
   the receipt-run `--out` policy). The exporter it invokes, `tools/souji-round9-selftest.sh:14` — quote:
   "export TMPDIR=/var/tmp GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null" — is excluded by the
   name rule `souji-round9-*` even though the trigger list describes it exactly. So `fail=0` over the
   frozen 27 is reachable while a committed, reachable tool still exports `TMPDIR=/var/tmp`.
7. **Disclosure honesty, item by item.** T13's anchor reason is accurate (evidence 6); the header states
   T13/T14/T28 and the receipt-run policy are out (pre-freeze, ids kept), which is honest for what it
   names. What is not honest is Finding 6: an omission that the stated rule requires and no sentence
   covers. The prereg premise "The lane's own tools and fixtures create scratch under a literal /var/tmp
   or /tmp whatever TMPDIR says" (preregistration.txt:9) is broader than the target's set, and remains
   true after a `fail=0` landing.
8. **Target wording versus predicate.** Preregistration.txt:9 defines PASS as the file-creating count being
   "at least half of BASE's (work not dropped)". The parenthetical is intent, not predicate; Findings 2-3
   satisfy the predicate while dropping the work.

## Attack log

- **Q1 — read-only detection plus dummy files?** Yes. Reproduced (Cheat B): the tool catches `EROFS`,
  prints BASE's last line verbatim, creates 60 files in `TMPDIR`; counter prints `PASS`, exit 0.
- **Q2 — does half-of-base catch a silently skipping selftest?** No. Same reproduction: all 11 cases
  skipped, `W60 >= 110/2` passes. A pure skip without dummy creates would fail, so the gate constrains file
  traffic only. T03 shows the degenerate case where BASE `W=0` makes the gate vacuous.
- **Q3 — can a fixture pass by writing into the lane/clone?** Yes. Reproduced (Cheat A): real work, real
  cases, scratch inside the clone, caller `TMPDIR` unused, `PASS` (`W111`). Nothing in the counter reads
  the destination paths of the counted syscalls.
- **Q4 — are the excluded hardcoders honestly excluded?** Partly. The three named base-anchor exclusions
  are correctly reasoned (T13 verified) and `tools/souji-proc-census.sh:502-516` and
  `tools/souji-quarantine.sh:749` do stay out of scope as disclosed; `fail=0` is attainable while both
  remain as they are. But `tools/souji-vault-verify.sh` is a rule match with a passing base anchor that
  fails the counter and is not disclosed anywhere — the set cannot be described as the rule's result.
  I did not execute T14 or T28: `bash tools/souji-quarantine.sh --selftest` terminated the invoking shell
  twice under bwrap with no captured output, so its `108 checks, 36 failed` base reading is
  [INFERENCE from the frozen header], not my measurement.
- **Impacted axis:** operability (C2) only; calibration and coverage are untouched by these findings.
  The claim can land `fail=0` while the axis's stated property is false, i.e. premature saturation on paper.

Reproductions (scratch-local commits, clone with `origin` removed; `--list-rev 3ec84fc8…`, `--base` base):

Cheat A (`tools/souji-rev-pin.py`, from base `85b61a1…`):
```
-    top = tempfile.mkdtemp(prefix="souji-rev-pin-selftest-", dir="/var/tmp")
+    # CHEAT A: ignore the caller's TMPDIR and write inside the repository clone.
+    _home = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, ".selftest-scratch")
+    os.makedirs(_home, exist_ok=True)
+    top = tempfile.mkdtemp(prefix="souji-rev-pin-selftest-", dir=_home)
```
Cheat B (same file):
```
-    top = tempfile.mkdtemp(prefix="souji-rev-pin-selftest-", dir="/var/tmp")
+    try:
+        top = tempfile.mkdtemp(prefix="souji-rev-pin-selftest-", dir="/var/tmp")
+    except OSError:
+        for i in range(60):
+            with open(os.path.join(os.environ["TMPDIR"], "dummy-%d" % i), "w") as h:
+                h.write("x\n")
+        print("SUMMARY total=11 failed=0")
+        return 0
```
Omitted item (appended to `census/round-32/c2-items.tsv` in the scratch clone):
`TV1<TAB>bash tools/souji-vault-verify.sh --selftest<TAB>tools/souji-vault-verify.sh`

## Smallest safe correction (stricter-only; L1 to log as an amendment)

1. In `creations()`, record the syscall's first path argument, resolve it against the run cwd, and count
   only creations under that run's `TMPDIR` (both runs). Require the sandboxed count to be at least half of
   BASE's `TMPDIR`-local count. Kills Cheat A; keeps the normalisation story intact.
2. Replace "last digit-bearing line" equality with equality of the normalised **multiset of all stdout
   lines** (order-insensitive), not just the last line. Kills Cheat B, whose sandboxed run emits no case
   lines. If a tool's output is non-deterministic, the item does not belong in a frozen set.
3. Bind `$HOME` and the clone read-only (or a tmpfs over them) inside the same bwrap call, so "write
   wherever is writable" is impossible and `TMPDIR` is the only creation target left.
4. Keep `ok_b` but drop the "half" tolerance for items whose BASE `W` is under a floor (e.g. 5); T03/T24
   (base `W0`/`W3`) currently carry no work check at all.
5. Either add TV1 (`tools/souji-vault-verify.sh --selftest`) and the `souji-round9-selftest.sh` exporter to
   the set, or amend the rule text so the `${TMPDIR:-…}` and `souji-round9-*` clauses do not both exclude
   a file that the claim's premise sentence still covers. Adding items is stricter-only.

Wave-2 falsifier: re-apply the two patches above on a base clone and run
`python3 -B census/round-32/c2-counter.py --root <clone> --rev <cheat> --base 85b61a1… --list-rev 3ec84fc8… --only T06`
after any amendment; both must flip to FAIL.

## Deliveries
- `.ufo/waves/round-32/w1/SwarmCritic34.md` (this report)

Scratch `/fast/scratch/hyaku/souji-r32/AttackC2` removed after writing. No lane file, index, jj state,
fleet path or `/home/vgpnk/Projects/shokuknow` was written; no commit, checkout or push was made in the
lane; no tool was installed or upgraded.
