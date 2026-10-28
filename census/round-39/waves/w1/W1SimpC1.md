# W1SimpC1 — YAGNI review of `census/round-39/c1-counter.py`

role: simplifier (leaf; no subagent dispatch)
lane: /home/vgpnk/Projects/shokunin/souji-shokunin (base ed30b7f5b77939c9073348d810730bc4f355708d, HEAD 2201778e7736af82e7d8a42dec2494f115bf3923 at review time)
scratch: /fast/scratch/hyaku/souji-r39/W1SimpC1 (412K, still on disk — see §9)
target bytes reviewed: `census/round-39/c1-counter.py`, sha256 `f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed`, 265 lines, identical in the worktree and at HEAD.

Axes named: (1) calibration — a counter that prints a number it did not derive is a defect of the same class C1 polices; (2) operability — how many processes and how many bytes of code a reader must trust; (3) coverage — nothing here.

Verdict in one line: **seven deletions, 265 -> 263 lines, every reading byte-identical** (`open=16`, `items_sha=d892b74f8358`, all 14 matrix cases). Two further candidates are measured and *not* proposed (§6, §7). No lane byte was written.

---

## 1. Method

Every claim below is a command I ran. All runs are read-only over the lane (`git show` inside the counter); the patched copies live in scratch and were never installed into the lane.

```
S=/fast/scratch/hyaku/souji-r39/W1SimpC1
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
BASE=ed30b7f5b77939c9073348d810730bc4f355708d
```

Setup:

```
mkdir -p "$S"
cp "$LANE/census/round-39/c1-counter.py" "$S/c1-counter-before.py"
cp "$LANE/census/round-39/c1-counter.py" "$S/c1-counter-after.py"
sha256sum "$S"/c1-counter-before.py "$S"/c1-counter-after.py "$LANE"/census/round-39/c1-counter.py
```
```
f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed  .../c1-counter-before.py
f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed  .../c1-counter-after.py
f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed  .../census/round-39/c1-counter.py
```
`census/round-39/c1-counter.py` does not exist at the base revision (`git show ed30b7f...:census/round-39/c1-counter.py` -> `fatal: path ... exists on disk, but not in ed30b7f...`), so "before" is the round's authored bytes at HEAD and the base-revision *control* is the counter run with `--rev ed30b7f...`.

Semantic-caller proof: no `lsp` device is mounted in this seat (`read xd://lsp` -> `No such tool: xd://lsp`; device list re-read, no language-server tool). Fallback used, recorded as such: an AST probe that reports bindings never loaded, plus a text grep for callers.

```
python3 -B "$S/ast-probe.py" "$LANE/census/round-39/c1-counter.py"
```
```
FILE /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-counter.py
DEAD-LOCAL .../c1-counter.py:156 register_leg() binds 'cells', never loads it
used-import .../c1-counter.py:34 import argparse
used-import ...:35 import os      ... (all seven imports used)
```
```
grep -rn "parse_register" "$LANE" --include=*.py
```
```
.../census/round-39/c1-counter.py:129:def parse_register(raw):
.../census/round-39/c1-counter.py:156:    cells, distinct = parse_register(reg_src)
```
One caller, and it discards the first element — the whole `cells` accumulator inside `parse_register` (lines 131, 141, 145) has no live consumer.

Static tools (already installed, nothing new installed this seat):

```
pyflakes "$LANE/census/round-39/c1-counter.py"                      # rc 0, no output
vulture "$LANE/census/round-39/c1-counter.py" --min-confidence 60   # no output
ruff check --select F,ARG,B,RET,SIM,PIE --output-format concise "$LANE/census/round-39/c1-counter.py"
```
```
census/round-39/c1-counter.py:115:20: B905 `zip()` without an explicit `strict=` parameter
Found 1 error.
```
(`ruff --select E501`: 31 findings before, 30 after. Style only; not touched.)

---

## 2. The seven deletions (applied in scratch, verified)

`diff -u "$S/c1-counter-before.py" "$S/c1-counter-after.py"` -> 7 hunks, 265 -> 263 lines:

| # | original lines | what dies | why it is dead |
|---|---|---|---|
| D1 | 130-131, 141, 145 | `cells` accumulator + first return element of `parse_register` | only caller (156) discards it; AST probe: bound, never loaded |
| D2 | 155, 156 | `"REGISTER-ABSENT"` string sentinel + tuple unpack of a dead name | replaced by the same value it decoded to (`0`) |
| D3 | 175 + 235 | `"ok:%d" % distinct` encode and `int(note.split(":")[1]) if note.startswith("ok:") else 0` decode | a value encoded to a string and parsed straight back in the same call chain |
| D4 | 34, 202 | `__import__("hashlib")` inline hack | hoisted to the import block; the module-level import was missing |
| D5 | 119 | `in ("", "-")` | `"".split(",")` is `[""]`, filtered to `[]` — the `""` arm is redundant with the comprehension |
| D6 | 19-22 | docstring claim "parsed for its row count" | after D1 the row count comes only from the frozen tool's `SUMMARY cells=`; the docstring would otherwise state a parse that no longer happens (R13-class stale literal) |
| D7 | 149 | docstring return contract `(cells, mismatches)` | the function returns three values; the docstring named two |

Exact patch (unified diff as produced):

```diff
@@ -17,10 +17,10 @@
-at `--register-rev` (default `--rev`) is parsed for its row count and for the rows whose `commit`
-differs from `receipt_rev`, and the frozen `tools/souji-citation-reconcile.py` bytes at `--rev` are
-extracted into a private scratch directory and run over `--rev`; its `SUMMARY cells=`
-`mismatches=` line carries the register verdict.
+at `--register-rev` (default `--rev`) is parsed for the rows whose `commit` differs from
+`receipt_rev`, and the frozen `tools/souji-citation-reconcile.py` bytes at `--rev` are extracted
+into a private scratch directory and run over `--rev`; its `SUMMARY cells=` `mismatches=` line
+carries the row count and the register verdict.
@@ -32,6 +32,7 @@
 import argparse
+import hashlib
 import os
@@ -116,7 +117,7 @@
-        row["mustnot"] = [] if row["mustnot"] in ("", "-") else [t for t in row["mustnot"].split(",") if t]
+        row["mustnot"] = [] if row["mustnot"] == "-" else [t for t in row["mustnot"].split(",") if t]
@@ -127,8 +128,7 @@
 def parse_register(raw):
-    """Row count and the rows whose commit differs from receipt_rev (8-column schema)."""
-    cells = 0
+    """The rows whose commit differs from receipt_rev (8-column schema)."""
     distinct = 0
@@ -138,22 +138,21 @@
-        cells += 1
         commit = parts[7] if len(parts) > 7 else ""
         if commit and commit != parts[6]:
             distinct += 1
-    return cells, distinct
+    return distinct
@@ -174,7 +173,7 @@
-    return int(match.group(1)), int(match.group(2)), "ok:%d" % distinct
+    return int(match.group(1)), int(match.group(2)), distinct
@@ -199,7 +198,7 @@
-    items_sha = __import__("hashlib").sha256(items_raw.encode("utf-8")).hexdigest()[:12]
+    items_sha = hashlib.sha256(items_raw.encode("utf-8")).hexdigest()[:12]
@@ -227,12 +226,11 @@
-            cells, mismatches, note = register_leg(
+            cells, mismatches, distinct = register_leg(
                 root, args.rev, args.register, register_rev, scratch)
         except ValueError as exc:
             sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
             return 2
-        distinct = int(note.split(":")[1]) if note.startswith("ok:") else 0
         print("REGISTER cells=%d mismatches=%d commit_distinct=%d" % (cells, mismatches, distinct))
```
(plus, inside `register_leg`, `return 0, 0, "REGISTER-ABSENT"` -> `return 0, 0, 0` and `cells, distinct = parse_register(reg_src)` -> `distinct = parse_register(reg_src)`; both appear in the hunk at `@@ -138,22` context and `@@ -174`.)

Retained on purpose — each one is reachable by a frozen predicate or a documented CLI:

- `if len(parts) < 7: raise ValueError("register row with %d fields" % len(parts))` (line 138-139). Not dead: the malformed-register refusal class. Proved live by matrix case `a6` below (rc 2, `register row with 5 fields`, identical in both arms).
- `if reg_src is None` branch (absent register) — reachable by the frozen predicate itself at `--rev ed30b7f`, where `census/round-39/cells.tsv` does not exist (matrix `a1`/`a2`).
- `--register-rev`, `--min-cells`, `--min-commit-distinct`, `--scratch` — all four are named in the frozen prereg's CLI line (`census/round-39/preregistration.txt`, CLI block) or in the C1 predicate; deleting a documented flag would be contract drift, not simplification.
- `has_token`, `REV`, `git_resolves`, `child_env` — all called; probe reports every import used.

---

## 3. Base control, before vs after (the acceptance check)

```
TMPDIR=$S/tmp-before python3 -B "$S/c1-counter-before.py" --root "$LANE" \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv
TMPDIR=$S/tmp-after  python3 -B "$S/c1-counter-after.py"  --root "$LANE" \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv
```
before, rc 1, stdout tail:
```
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```
after, rc 1, stdout tail:
```
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```
`diff` of the two full stdouts: identical (all 16 `ITEM ... OPEN` lines included). Both lines equal the last line of the committed control `census/round-39/records/c1-before.txt` (`SUMMARY items=16 open=16 ... items_sha=d892b74f8358`). The current `c1-items.tsv` hashes to `d892b74f8358` (`sha256sum census/round-39/c1-items.tsv | cut -c1-12`), so the receipt's `items_sha` still binds.

**V1 PASS** — before arm reproduces the committed control byte for byte.
**V2 PASS** — after arm reproduces the before arm byte for byte: `open=16`, `items_sha` unchanged, rc unchanged.

---

## 4. Reading-parity matrix (14 cases, `sh $S/harness.sh`)

Each case runs both arms with the same argv and diffs stdout, stderr and exit code.

```
TAG                rc_before rc_after stdout_diff stderr_diff | SUMMARY / refusal
a1-base-control    1   1   same  same  | SUMMARY items=16 open=16 register_cells=0 ... items_sha=d892b74f8358
a2-head-absent     1   1   same  same  | SUMMARY items=16 open=2  register_cells=0 ... items_sha=d892b74f8358
a3-head-r38reg     1   1   same  same  | REGISTER cells=10 mismatches=0 commit_distinct=0 / open=2
a4-base-r38reg     1   1   same  same  | REGISTER cells=10 mismatches=0 commit_distinct=0 / open=16
a5-head-r37reg     1   1   same  same  | REGISTER cells=11 mismatches=0 commit_distinct=0 / open=2
a6-head-r31reg     2   2   same  same  | REFUSAL COULD-NOT-EVALUATE: register row with 5 fields
r1-badrev          2   2   same  same  | REFUSAL USAGE: --rev must be 40-hex
r2-gone-rev        2   2   same  same  | REFUSAL COULD-NOT-EVALUATE: --rev 000...000 does not resolve to a commit
r3-badroot         2   2   same  same  | REFUSAL USAGE: --root /nonexistent-r39 is not a directory
r4-noitems         1   1   same  DIFF  | FileNotFoundError: ... absent-items.tsv   (traceback path only)
r5-noheader        2   2   same  same  | REFUSAL USAGE: items ... has no header before line 1
r6-badregrev       2   2   same  same  | REFUSAL COULD-NOT-EVALUATE: --register-rev nothex does not resolve
m1-empty-mustnot   1   1   same  same  | SUMMARY items=2 open=2 ... items_sha=e9be4b5495fb
m2-dash-mustnot    1   1   same  same  | SUMMARY items=1 open=1 ... items_sha=67702ae4d4ad
```
`a2` item lines: 14 `CLOSED` in both arms (`grep -c CLOSED` -> 14 / 14).
`m1` (empty `mustnot` field) and `m2` (`-`) both print `ITEM X1 OPEN PREDICATE-MISSING corpus/QUALITY.md missing=['axis', 'score'] hits=1` and `ITEM X1 OPEN PREDICATE-MISSING corpus/QUALITY.md missing=['axis'] hits=1` respectively — identical in both arms, which is the D5 equivalence test, run rather than asserted.
`r4` stderr differs only because the traceback names `c1-counter-before.py` vs `c1-counter-after.py`; normalised (`sed 's/[0-9]\+/N/g;s#/fast[^:]*##g'` on both) the two stderr files are identical and both exit 1.

**V3 PASS** — 13/14 cases byte-identical on all three channels; the 14th differs only in the interpreter's own file path.

---

## 5. The `commit_distinct` arm with a non-zero value

The only committed register that carries the optional eighth `commit` cell is `census/round-38/cells.tsv` (header `id file anchor expected stale receipt receipt_rev commit`), and every one of its 10 rows reads `commit == receipt_rev` (`commit_distinct=0`) — that is the r38 limit this round closes. `census/round-37/citation-cells.tsv` is 7-column (no commit arm, `commit_distinct=0` by construction) and `census/round-31/c1-cells.tsv` is a different, 5-column schema the counter refuses. So the deleted encode/decode is additionally exercised on a value no committed lane register currently produces, using a git fixture (rule-compliant: `mktemp -d`, `git -C "$D" init -q`, toplevel asserted equal to `$D` before the first commit, `trap 'rm -rf -- "$D"' EXIT`):

```
sh "$S/fixture.sh"
```
```
toplevel=/fast/scratch/hyaku/souji-r39/W1SimpC1/fixture.9bgCcI
fixture=.../fixture.9bgCcI rev=b9fca76e1b0dbe33092e84071e6fc95d398c1f23 commit1=d0e04d9a802c32fca29e32b362f2473884837800
before rc=1
ITEM I1 CLOSED
REGISTER cells=2 mismatches=2 commit_distinct=2
SUMMARY items=1 open=0 register_cells=2 register_mismatches=2 commit_distinct=2 items_sha=bb3972f31c97
after rc=1
ITEM I1 CLOSED
REGISTER cells=2 mismatches=2 commit_distinct=2
SUMMARY items=1 open=0 register_cells=2 register_mismatches=2 commit_distinct=2 items_sha=bb3972f31c97
fixture stdout identical
fixture stderr identical
```
(the fixture's two rows carry `receipt_rev` = the tip and `commit` = the parent, so `distinct=2`; the `mismatches=2` are the fixture's own rows, identical on both sides. The fixture directory was removed by its trap.)

**V4 PASS** — `commit_distinct=2` and `cells=2` read identically after deleting the string round-trip; `--min-cells 2 --min-commit-distinct 2` also read identically.

---

## 6. Duplicate git invocations — measured, not proposed

A PATH shim logs every `git` argv (the shim bakes its log path because the counter passes a whitelisted child env, so an env var would be dropped):

```
sh "$S/shim.sh"
```
```
before rc=1 git_calls=20 git_show=18 distinct_show_args=12 cat_file=2
after  rc=1 git_calls=20 git_show=18 distinct_show_args=12 cat_file=2
cache  rc=1 git_calls=14 git_show=18→12 distinct_show_args=12 cat_file=2
```
(before/after: `-C <lane> cat-file -e <rev>^{commit}` twice + 18 `show`; 12 distinct `show` args. The 16 item rows name 10 distinct files — `corpus/lessons/round-38.md` x3, `corpus/lessons/round-39.md` x3, `census/round-38/preregistration.txt` x2, `LOG.md` x2 — so **6 of the 18 `show` calls re-fetch a blob already fetched in the same run**.)

A third scratch copy (`$S/c1-counter-cache.py`, 268 lines) memoises `git_show` per `(rev, path)` for the item loop: 20 -> 14 git calls, `SUMMARY items=16 open=16 ... items_sha=d892b74f8358` identical.

**Verdict: FINDING, deferred.** The 6 redundant `show` calls are real, and the fix is measured at -30 % process count. It is *not* proposed: it adds a mutable cache parameter, a two-mode branch and 5 lines to a helper that is otherwise pure, to save ~6 forks on a counter that runs once per claim. That trades the maintainability axis for operability the predicate cannot see. If the L1 wants it, the copy is at `$S/c1-counter-cache.py` and its reading is already proven identical; I recommend against.

---

## 7. Candidate not proposed: the `try` that can never catch `open`

`run()` wraps `open(args.items)` and `parse_items` in one `except ValueError`. `open` raises `OSError` for every reachable path (`FileNotFoundError`, `IsADirectoryError`, `EACCES`); its only `ValueError` is the embedded-NUL one, and a NUL byte cannot reach `argv` (POSIX `execve`; shell control: `python3 -c 'import sys; print(repr(sys.argv[1]))' "$(printf 'a\0b')"` -> `'ab'` with `warning: command substitution: ignored null byte in input`). So the `open` statement sits inside a handler that cannot catch anything it raises.

Measured on a fourth scratch copy with the `try` narrowed to `parse_items` (`$S/c1-counter-narrow.py`): `a1`, `a2`, `a5`, `m1` stdouts identical to the before arm; `r5` still `REFUSAL USAGE: ... has no header before line 1`, rc 2; `r4` same exception class and rc 1, differing only in traceback line numbers.

**Verdict: no reading change, zero bytes saved — not proposed.** It only relocates two lines. It does expose a pre-existing gap worth routing, not fixing here: a missing `--items` file yields an uncaught traceback with rc 1, while the docstring promises exit 2 for "usage, malformed input" (matrix `r4`). Catching `OSError` -> `REFUSAL USAGE`/exit 2 would be an operability improvement but it *changes* a reading, so it needs its own claim, not a simplifier's patch.

---

## 8. Preserved contract

- The C1 predicate string is untouched: `SUMMARY items=16 open=16 ... items_sha=d892b74f8358` at `--rev ed30b7f` in both arms, and `register_cells`/`register_mismatches`/`commit_distinct` still come from the frozen reconciler's own `SUMMARY` line, not from local parsing.
- Every refusal class exercised still fires with the same class and exit code (6 of 6: bad rev, gone rev, bad root, missing items (unchanged traceback), no header, bad `--register-rev`), plus the malformed-register guard (`register row with 5 fields`, rc 2).
- CLI surface unchanged: no flag added or removed, so the frozen prereg's CLI block and the C1 predicate command stay literally true.
- Tradeoff accepted with D1: the counter no longer computes its own register row count. It never compared that count to the tool's, so it was never a cross-check — the row count now has exactly one source (the frozen tool bytes), which is what C1's "each register row verifies through the frozen `tools/souji-citation-reconcile.py` bytes at `--rev`" asks for.
- `B905` (`zip()` without `strict=`) is pre-existing and harmless here: `parse_items` validates `len(parts) != 5` two lines earlier, so truncation is unreachable. Left alone; `strict=True` would be an addition.

---

## 9. Hygiene

- Lane bytes: untouched by me. `git -C "$LANE" status --porcelain=v1` at review start showed only sibling-owned entries (`?? census/round-39/make-cells.py`, `?? census/round-39/records/{c2-after,c3-after,census-after,census-before}.txt`); the same command at review end additionally showed `M LOG.md`, `M SKILL.md`, `M corpus/QUALITY.md` — sibling seats writing during my run, not me (I opened no lane file for writing; my only lane write is this report). `census/round-39/c1-counter.py` still hashes to `f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed`, i.e. the bytes I reviewed are the bytes on disk. No git/jj mutation, no commit, no push, no `~/.local/bin` or PATH write.
- Tooling: nothing installed; `ruff`, `pyflakes`, `vulture` and `python3` were already present (`command -v` recorded above).
- Scratch **still on disk**: `/fast/scratch/hyaku/souji-r39/W1SimpC1` (412K) — `c1-counter-{before,after,cache,narrow}.py`, `harness.sh`, `shim.sh`, `fixture.sh`, `ast-probe.py`, `reconciler-head.py`, three items fixtures, `out/` (110 files: per-case stdout/stderr/rc and three git logs), `shim/git`, four `tmp-*` dirs. The git fixture directory was removed by its trap (`ls -d "$S"/fixture.*` -> none).
- Files read only: `census/round-39/preregistration.txt`, `census/round-39/c1-counter.py`, `census/round-39/records/c1-before.txt`, `census/round-39/c1-items.tsv`, `tools/souji-citation-reconcile.py` (extracted at HEAD into scratch).

## 10. Recommendation

Land the seven deletions as one cleanup hunk on `census/round-39/c1-counter.py` **before** the C1 landing measurement, so the counter the predicate quotes is the counter that ships. The landing `open=` value is not something I measured (it depends on the L1's item closures); what I measured is that the patch cannot move it: every item, register and refusal reading is identical at the base revision, at HEAD, and on a populated/malformed/absent register. [INFERENCE] the landing `SUMMARY` will therefore be the same with or without the patch. If the L1 prefers zero churn on a frozen-contract counter, the deletions are also safe to skip: they change no reading, which is exactly what this review establishes. Either way, route `r4` (missing `--items` -> traceback, rc 1, contradicting the documented exit 2) to the C2 operability seat, since fixing it changes a reading and needs its own claim.
