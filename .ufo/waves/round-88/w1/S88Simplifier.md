# S88Simplifier — dead-arm and duplication audit of the r88 instruments

Seat: souji round 88, wave 1, seat S88Simplifier. Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Scope: the four named candidates (harness `where=ledger` `cls`/`target`; `RESOLVING_NOT` for the ledger
branch; battery `--mutants`/`--expect-killed` defaults; `_one_line`'s duplicate of `_stderr_tail`'s bound),
plus two adjacent arms met while proving them. Nothing in the lane was edited, committed or staged by this
seat; every variant and receipt is filed under `.ufo/waves/round-88/w1/S88Simplifier/` (`variants/`,
`receipts/`), and all scratch work lived in /fast/scratch/hyaku/souji-r88/S88Simplifier (deleted before
yield).

Instrument hashes re-measured at audit start against the preregistration (all twelve matched), then re-checked
at yield:

    c1-false-rows.tsv        b710e368...a68c3 (53 rows)          OK
    c1-mutants.json          baec8026...cec9c (12 members)       OK
    c1-mutants-dead.json     e7963787...15281 (13 members)       OK
    c1-false-row-harness.py  1ae0cd39...4042b                   OK
    c1-clause-battery.py     6842ca47...c5ff7                   OK
    c1-pointer-counter.py    fd0a8e24...5220b (UNCHANGED r87)   OK
    c1-items.tsv             ce80195d...d2e9 (UNCHANGED r87)    OK
    r88-k4-flagfail.py       aa79133a...e8335d                  OK
    tools/souji-record-agreement.py  c0604b4a...4fdef at start; **3e1fc030...ca2bb at yield** (see below)
    controls/c2-before-tool.py e1b00e8a...67ccc (r87 bytes)     OK
    controls/c2-before.txt   28e5ad68...133dc2                  OK
    controls/c1-before.txt   ce1352d2...b35c7f                  OK

Post-freeze movement (not this seat's): the tool was `c0604b4a` (the prereg pin) when this audit started.
At 08:36 the L1 landed commit `72edae40` ("C2 docstring names the escape set it has (C0/DEL/NEL/LS/PS),
receipts re-run on the new bytes"), changing the tool to **`3e1fc030`** and re-filing
`records/c2-after.txt` on the new bytes (`tool sha256=3e1fc030...`, `SUMMARY cases=7 tool_pass=7
before_pass=3`, EXIT=0). `git diff 01a2fa55 72edae40 -- tools/souji-record-agreement.py` is five lines of
`_one_line`'s docstring only; `_stderr_tail` and `_one_line`'s bodies are untouched, so every measurement
below holds. The §6/§7 diffs are regenerated against the current bytes and the fixture re-run on a
current-derived variant (sha `3c45eca9`, 7/7, EXIT 0). The prereg pin `c0604b4a` no longer matches the
working tree — recorded for the L1's reconciler; the cause is the L1's own commit, not this seat's work.

Method: copy the instrument under `variants/`, apply one candidate deletion, run the frozen command
verbatim against the scratch copy, compare every printed number and the exit code with the pristine run.

Baselines reproduced on the lane bytes, all four frozen commands:
C1 after: `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`, `pop=r88 rows=53 mismatches=0
errors=0 exit=0`, `SUMMARY mutants=12 sets=r87,r88 ... killed_r87=10 killed_r88=12 killed_total=22`,
EXIT=0 (21m09s, `receipts/c1-after-baseline.txt`).
C1 before: 51/0/0, ten killed, `m17-duplicate-id`/`m18-whole-before` alive, `killed_r87=10`, EXIT=0
(`receipts/c1-before-baseline.txt`).
C2 after: `SUMMARY cases=7 tool_pass=7 before_pass=3`, EXIT=0. C2 before arm: `tool_pass=3 before_pass=3`,
EXIT=1.
After stripping the `#` path lines, the only difference from the filed
`census/round-88/records/c1-after.txt`, `census/round-88/controls/c1-before.txt`,
`census/round-88/records/c2-after.txt` and `census/round-88/controls/c2-before.txt` is each receipt's
trailing `EXIT=` line (my runner printed the exit separately): every ARM / MUTANT / MUTANT-PAIR / CASE /
SUMMARY line is byte-identical.

## Verdict table

| # | Deletion tested | C1 after | C1 before | C2 after | C2 before | Verdict |
|---|---|---|---|---|---|---|
| 1 | harness: LD1 `cls`/`target` columns reach judgement | inert-pop 53 rows/0/0 EXIT 0 (code unchanged) | not re-run (same harness bytes) | – | – | **belt** (schema-held, inert) |
| 2 | harness: `RESOLVING_NOT` + `accepted`/`refused_true` | dies at the same r87 pristine run (first set) | `BATTERY-FATAL` EXIT 1 (measured on `--only r87`) | – | – | **load-bearing** (SUMMARY parse contract) |
| 3 | battery: drop `--mutants` default (required) | **EXIT 2** at argparse | **EXIT 2** | – | – | **load-bearing** |
| 4 | battery: drop `--expect-killed` default (required) | 51/0/0 & 53/0/0, 22 kills, EXIT 0 (byte-identical) | 51/0/0, ten killed, EXIT 0 (byte-identical) | – | – | **dead** (land) |
| 5 | battery: stale `--only` default `r85,r86` | same run as row 4 | same run as row 4 | – | – | **dead name** (land, same hunk as 4) |
| 6 | tool: `_one_line`/`_stderr_tail` duplicate bound → `_both_ends` | – | – | 7/7, EXIT 0 | 3/3, EXIT 1 | **dead duplication** (land) |
| 7 | tool: `_one_line` calls `_stderr_tail` directly | – | – | 7/7, EXIT 0 | 3/3 | **reject** (not behaviour-preserving) |
| 8 | tool: `limit` parameter of `_stderr_tail`/`_one_line` | – | – | – | – | **belt** (no caller passes it) |
| 9 | harness: ledger trailing-newline guard | – (code-read + file tail; no run needed) | – | – | – | **belt** (inert on frozen ledger) |

Where a variant was run under a frozen command, the pinned populations stay at `mismatches=0 errors=0` and
the after arm keeps `killed_r87=10 killed_r88=12 killed_total=22`; the only red results are the deletions
that are load-bearing (rows 2 and 3).

## 1. `where=ledger` `cls`/`target` — belt, not dead

The columns are already outside the judged path: the ledger branch builds the duplicate ledger and reads
only the counter's `LEDGER-REFUSED id=<item>` marker plus the exit code; `cls` is printed for the reader,
`target` is not read at all. Proven by feeding a re-pinned population where LD1's `cls`/`target` are
replaced with `REFUSED` / `../injected-target`:

    ROW LD1 where=ledger rev=BASE item=P01 class=REFUSED expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
    SUMMARY rows=53 mismatches=0 accepted=0 refused_true=0 errors=0          (EXIT 0)

(receipt `receipts/harness-inert.txt`, variant `variants/harness-inert.py` + `variants/pop-inert.tsv`.)

Deleting the columns is not available: the population is a pinned 53-row, 10-column TSV, and the harness's
well-formedness gate rejects any other shape. A 9-column population (LD1 without `cls`/`target`) is refused
before a single row is judged:

    C1-HARNESS-FATAL: population is not 53 well-formed rows            (EXIT 2)

(receipt `receipts/harness-9col.txt`.) Verdict: keep. The belt is the frozen schema, not harness code.

## 2. `RESOLVING_NOT` and the ledger branch — the non-use is correct; the fields are a parse contract

The ledger branch never consults `RESOLVING_NOT`, and adding the generic accounting there would be a
literal no-op for LD1: `got` is `LEDGER-REFUSED` or `-`, `exp_got` is `LEDGER-REFUSED`, none of them in
`RESOLVING_NOT`, so `reft += got in RESOLVING_NOT` is `+= 0`. There is nothing dead to remove from the
ledger branch; the omission is the minimal form.

Deleting `RESOLVING_NOT` and the two SUMMARY fields it feeds is **load-bearing**, not dead: the battery
parses a positional SUMMARY line and dies without it. A harness with the accounting and the fields removed
(`variants/harness-nodeadfields.py`) makes the frozen C1 before command fail at its first pristine run:

    BATTERY-FATAL: r87 run of .../c1-pointer-counter.py printed no SUMMARY: ''
    EXIT=1

(receipt `receipts/c1-schema-break.txt`.) The two fields read 0 on every green run; they carry failure
direction on a red run and they hold the column positions the battery anchors on. Keep as a belt.

## 3. Battery `--mutants` default — load-bearing, keep

The frozen after and before commands omit `--mutants`, so the `HERE/c1-mutants.json` default is the only
thing that selects the twelve-member file. Making it required kills both commands before any work:

    battery-required-mutants.py: error: the following arguments are required: --mutants    (EXIT 2)

(receipt `receipts/battery-required-mutants.txt`.) Do not touch.

## 4+5. Battery `--expect-killed` / `--only` defaults — dead on the frozen commands, land fail-closed

Parser defaults as filed: `only='r85,r86'`, `expect_killed=None`, `mutants=<lane>/census/round-88/c1-mutants.json`
(receipt `receipts/battery-defaults.txt`). All three frozen commands pass `--only` and `--expect-killed`, so
neither default is exercised; `r85,r86` is a stale r86-era name that would silently score the wrong
populations for any future invocation that forgets the flag, and `expect_killed=None` lets a run pass with
no stated expectation. The scratch variant makes both required and collapses the guarded exit; the frozen
before command under the variant (harness/mutants/population copied byte-identically beside it, shas
`1ae0cd39`/`baec8026`/`b710e368`) reports

    ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0
    MUTANT-PAIR m17-duplicate-id ... killed=no ... | MUTANT-PAIR m18-whole-before ... killed=no ...
    SUMMARY mutants=12 sets=r87 pristine_r87=ok killed_r87=10 killed_total=10        (EXIT 0)

and its numeric lines are byte-identical to `controls/c1-before.txt` (`diff` clean after dropping `#` lines).
The frozen after command under the same variant reproduces `census/round-88/records/c1-after.txt` exactly:
`ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`, `pop=r88 rows=53 ... exit=0`, all twelve
MUTANT-PAIR lines identical, `SUMMARY mutants=12 sets=r87,r88 pristine_r87=ok pristine_r88=ok killed_r87=10
killed_r88=12 killed_total=22`, EXIT 0 (621s, `receipts/c1-after-required-expect.txt`; the only difference
from the filed receipt is its trailing `EXIT=` line). So the diff is number-neutral on all frozen inputs.

Exact diff (also `receipts/diff-battery.diff`):

```diff
--- a/census/round-88/c1-clause-battery.py
+++ b/census/round-88/c1-clause-battery.py
@@ -94,9 +94,9 @@
     ap.add_argument("--lane", default="/home/vgpnk/Projects/shokunin/souji-shokunin")
     ap.add_argument("--work", required=True, help="empty scratch dir (never under /tmp)")
     ap.add_argument("--mutants", default=os.path.join(HERE, "c1-mutants.json"))
-    ap.add_argument("--only", default="r85,r86",
-                    help="comma list of the pinned population labels to score (r83, r84, r85, r86, r87)")
-    ap.add_argument("--expect-killed", type=int, default=None,
+    ap.add_argument("--only", required=True,
+                    help="comma list of the pinned population labels to score (r83, r84, r85, r86, r87, r88)")
+    ap.add_argument("--expect-killed", type=int, required=True,
                     help="exit 1 unless this many mutants are killed on the scored population set")
     ns = ap.parse_args(argv)
     lane, work = os.path.abspath(ns.lane), os.path.abspath(ns.work)
@@ -151,9 +151,7 @@
     kl = " ".join(f"killed_{l}={killed[l]}" for l in sets)
     tot = sum(killed[l] for l in sets)
     print(f"SUMMARY mutants={len(members)} sets={','.join(sets)} {pr} {kl} killed_total={tot}")
-    if ns.expect_killed is not None:
-        return 0 if tot == ns.expect_killed else 1
-    return 0
+    return 0 if tot == ns.expect_killed else 1
```

Note: this is a post-r88 change. In r88 the battery is the hashed instrument `6842ca47...`; landing the
diff now would move that hash and every receipt that names it. Recommend for r89.

## 6. `_one_line` duplicates `_stderr_tail`'s bound — dead duplication, land the extraction

`_stderr_tail` and `_one_line` each carry the same four lines (`head = limit // 2`, `keep = limit - head - 1`,
`text[:head] + "…" + text[-keep:]`). The claim's wording ("the same head-100 / `…` / tail-99 bound
`_stderr_tail` uses") is made literally true by one owner for the bound. The extraction is output-identical
on 25 inputs (empty, whitespace-only, CR/LF/tab, C0/C1/NEL/U+2028, 100/199/200/201/400-character lines,
backslash spellings) for **both** functions, and the fixture still reports `cases=7 tool_pass=7 before_pass=3`,
EXIT 0 on the current-derived variant (`receipts/diff-one-line.txt`, `receipts/c2-both-ends.txt`).

Exact diff (also `receipts/diff-tool.diff`):

```diff
--- a/tools/souji-record-agreement.py
+++ b/tools/souji-record-agreement.py
@@ -247,6 +247,15 @@
     return tally
 
 
+def _both_ends(text: str, limit: int) -> str:
+    """r87 wave repair (S87Critic), extracted r88 so one function owns the bound: a long exception line carries its
+    type name FIRST ("AttributeError: ...") and its message last, so the cut keeps head-100 / `…` / tail-99 and
+    loses only the middle. `_stderr_tail` and `_one_line` both cut through here."""
+    head = limit // 2
+    keep = limit - head - 1
+    return text[:head] + "\u2026" + text[-keep:]
+
+
 def _stderr_tail(text: str, limit: int = 200) -> str:
     """r87: the reader's only handle on a failed delegation is the LAST non-empty stderr line, where an exception
     names itself; a 200-character prefix can end inside the traceback frame list and show
@@ -257,11 +266,7 @@
         return ""
     tail = lines[-1]
     if len(tail) > limit:
-        # r87 wave repair (S87Critic): a long exception line carries its type name FIRST ("AttributeError: ...") and
-        # its message last, so a tail-only cut loses the name the detail exists for. Keep both ends.
-        head = limit // 2
-        keep = limit - head - 1
-        tail = tail[:head] + "\u2026" + tail[-keep:]
+        tail = _both_ends(tail, limit)
     return tail
 
 
@@ -275,9 +280,7 @@
     if not boxed:
         return "no stderr"
     if len(boxed) > limit:
-        head = limit // 2
-        keep = limit - head - 1
-        boxed = boxed[:head] + "\u2026" + boxed[-keep:]
+        boxed = _both_ends(boxed, limit)
     return boxed
```

Provenance is kept: the r87 S87Critic attribution moves into `_both_ends`'s docstring. The tool bytes are
hashed evidence for this wave (now `3e1fc030`), so landing the diff moves them again; it belongs to the next
round, not to r88.

## 7. Rejected variant: `_one_line` delegating to `_stderr_tail`

The one-line delegation `_stderr_tail(_escape_text(text or ""), limit) or "no stderr"` looks smaller but is
**not** behaviour-preserving: `_stderr_tail` strips each line and drops empty ones, so the escaped spelling
loses leading/trailing spaces and collapses whitespace-only input to `no stderr`. Four diffs on the matrix:

    DIFF delegate in=' '        old=' '      new='no stderr'
    DIFF delegate in='  \t '    old='  \\t ' new='\\t'
    DIFF delegate in='  x  '    old='  x  '  new='x'
    DIFF delegate in='  bbb…  ' old='  bbb…  new='bbb…'

(receipt `receipts/diff-one-line.txt`.) The claim's stated limit leans on the detail being "an injective
spelling": stripping makes `"x"` and `" x "` share a spelling and `' '` stop saying what the writer wrote,
so the composed rendering would lose the property at the whitespace edges. The fixture still passes 7/7
because it never exercises whitespace edges — a green fixture is not a proof here. Reject.

## 8. The `limit` parameter — belt

No caller passes `limit`: `_one_line` is called once (line 387) and `_stderr_tail` twice (lines 401, 608),
all with the default 200. Deleting the parameter would be behaviour-preserving on the frozen C2 command, but
it is the knob the fixture and the claim name ("200-character excerpt bound") and it costs nothing. Keep as
a belt; `_both_ends(text, limit)` takes it explicitly.

## 9. Adjacent: the ledger duplicate's trailing-newline guard — belt

`if base and not base.endswith(b"\n"): base += b"\n"` is inert on the frozen input: `tail -c 1
census/round-77/c2-pointer-ledger.tsv | xxd` is `0a` (32 rows), and LD1 is the only `where=ledger` row in
the 53-row population, so the `+= b"\n"` branch never fires under any frozen command. It is the correct
guard for any other ledger; keep, do not delete.

## 10. Adjacent observation: the battery's no-SUMMARY path exits 1, not the documented 2

Measured while breaking the SUMMARY schema (§2): `run()` does
`raise SystemExit(f"BATTERY-FATAL: ...")`, and a string `SystemExit` exits **1**, while the module
docstring promises "2 on usage, a pin mismatch, an edit that does not apply exactly once, or an unreadable
harness". The frozen commands never reach the arm (all green), so no stated wording is touched, but a
future consumer that separates 1 (a mutant survived) from 2 (the instrument is broken) would misread it.
Minimal fix if the r89 cleanup takes this file:

```diff
     if not m:
-        raise SystemExit(f"BATTERY-FATAL: {pop_label} run of {counter} printed no SUMMARY: {err[:300]!r}")
+        print(f"BATTERY-FATAL: {pop_label} run of {counter} printed no SUMMARY: {err[:300]!r}", file=sys.stderr)
+        raise SystemExit(2)
```

Not part of the four candidates; reported because the measurement produced it.

## Land / keep / why

- **Land (r89, exact diffs above):** the `_both_ends` extraction (one authority for the 200/100/…/99 bound,
  output-identical; also removes the second copy of the rationale comment); the battery `--only` /
  `--expect-killed` fail-closed diff (stale `r85,r86` name removed, no silent no-expectation pass).
- **Keep as belts:** harness `where=ledger` `cls`/`target` (frozen 10-column schema; proven inert);
  `RESOLVING_NOT` + `accepted`/`refused_true` (battery's positional SUMMARY contract, failure-direction
  diagnostic); battery `--mutants` default (the frozen after/before commands rely on it); `_one_line`/
  `_stderr_tail` `limit` parameter; the ledger trailing-newline guard.
- **Reject:** `_one_line` → `_stderr_tail` whole-function delegation (strips; weakens the injective spelling).

No deletion is recommended for r88 itself: every remaining candidate is either frozen by a hash or a belt
whose removal buys nothing measurable. The two landable diffs are number-neutral on all four frozen commands.

## Receipts and reproducers

All receipts named above and the exact variant files are under
`.ufo/waves/round-88/w1/S88Simplifier/` (`receipts/`, `variants/`); `variants/` also holds byte-identical
copies of `c1-false-row-harness.py` (`1ae0cd39`), `c1-mutants.json` (`baec8026`) and `c1-false-rows.tsv`
(`b710e368`) so the battery variants resolve their `HERE` pins from the seat dir. Reproduce, from the lane
root (`V=.ufo/waves/round-88/w1/S88Simplifier/variants`), with an empty work dir outside /tmp:

    $V/battery-required-expect.py --counter census/round-87/c1-pointer-counter.py --work DIR --only r87,r88 --expect-killed 22
    $V/battery-required-mutants.py --counter census/round-87/c1-pointer-counter.py --work DIR --only r87,r88 --expect-killed 22   # EXIT 2
    $V/harness-inert.py --counter census/round-87/c1-pointer-counter.py --lane $PWD --fleet-root /home/vgpnk/Projects/shokunin --work DIR --population $V/pop-inert.tsv
    $V/harness-inert.py ... --population $V/pop-9col.tsv                                                                              # EXIT 2
    tests/fixtures/r88-k4-flagfail.py --tool $V/tool-both-ends.py --before census/round-88/controls/c2-before-tool.py --work DIR
    $V/diff_one_line.py

Scratch: /fast/scratch/hyaku/souji-r88/S88Simplifier was deleted before yield; nothing left behind. No lane
file was touched by this seat. The only lane hash that moved during the audit is the tool, by the L1's own
commit `72edae40` (`c0604b4a` → `3e1fc030`, docstring-only), recorded at the top; the other eleven pins still
match the preregistration at yield.
