# `tools/souji-axis-check.py --selftest` — design specification

Round 26 C3 (`operability`, surface-class `instrument-acquisition`). Prose spec only: this file
changes no code. The tool and fixture belong to the C3 owner(s); §9 lists the tool edits the
shipped case table implies.

Frozen contract read this run: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/preregistration.txt`
(C3 artifacts, counters K1/K2, kill rules), plus amendments 1 and 2. Both instruments were
committed while this spec was being written; every statement below is against the blob bytes first
committed at `0833de9591a7db81cdfa4efda2cdad2e75606f58` and verified unchanged at lane HEAD
`d6c13b0f00066cbb342fdc50167849a5f1c726e5`:

- `tools/souji-axis-check.py` — sha256 `14bc9632e88ef58f18108011f6645bd970cd825d0ffc1664369dc60b0d579332`,
  zero occurrences of the string `selftest`.
- `tests/fixtures/r26-axis-check.py` — sha256 `2ffc18289fc82b9075ad3580cb9bec6a80384061c7d294b5aa17dbf9ca93c8da`,
  11 cases.

---

## 1. Shape: what "lane convention" means here

Two conventions exist and the design takes one clause from each.

| Source | Convention | Taken |
|---|---|---|
| `tools/souji-rev-pin.py:252-264` | per-case verdict line `CASE` + TAB + `pass`/`FAIL`; a failed case carries `ExceptionType: message`; the temp world is removed in `finally`; `--selftest` short-circuits **before** any argument validation (`:386-389`) | per-case line format, short-circuit, cleanup |
| `tools/souji-gate-check.py:288-290` | per-case `PASS name [detail]` then a terminal numeric line `selftest=%d/%d` | a single terminal count line |

Terminal line is the literal named by this seat's assignment: `selftest=N/N pass`.
Numeric semantics are `gate-check`'s (pass/total), spelled with the word `pass`.

**Interop warning (finding F7 in `ExecAxisSelftest.md`).** `tools/souji-receipt-run.py:69-77`
recognizes only a selftest spelling of the form `selftest=` plus PASS-or-FAIL plus ` ids=` plus two
integers — it does **not** match `selftest=N/N pass`. A `c3-counter.sh`
that echoes the tool's terminal line therefore yields no counts line for a receipt. If the C3
counter is to bind the selftest, it must print its own `cases=NN pass=NN` (also in `COUNTS_RE`) or
the tool must additionally print the receipt-matched spelling. The assigned literal is kept here;
the remedy is a counter-side line, not a second convention inside the tool.

---

## 2. CLI contract

```
python3 -B tools/souji-axis-check.py --selftest
python3 -B tools/souji-axis-check.py --prereg PATH --scorecard PATH
```

- `--prereg` and `--scorecard` must become **not** `required=True` (they are today, `:134-135`, so
  `--selftest` alone currently dies in argparse with exit 2 — measured; finding F1 in
  `ExecAxisSelftest.md`). Missing them in
  check mode is diagnosed in `main`, mirroring `souji-rev-pin.py:391-392`:
  `souji-axis-check: --prereg and --scorecard are required (usage exit 2)` on stderr, stdout empty,
  return 2.
- `--selftest` present ⇒ run the selftest, ignore other options, read **no** file outside its own
  scratch root. No git, no network, no env dependency.
- The selftest must call the tool as a **subprocess** (`sys.executable`, `-B`, `os.path.abspath(__file__)`)
  in the scratch root as cwd, because the exit contract and the `claims=`/`FLAG` stdout shape are
  part of what it must verify. In-process calls to `check()` cannot observe either.
- In-process imports are used **only** for the rule-table assertions (§4): constants are not
  observable through the CLI.

---

## 3. Scratch world

```
top = tempfile.mkdtemp(prefix="souji-axis-check-selftest-", dir="/var/tmp")
try:      ... one subdirectory per case, generated prereg + scorecard files ...
finally:  shutil.rmtree(top, ignore_errors=True)
```

`dir="/var/tmp"` is literal (`souji-rev-pin.py:253`); never `/tmp`, never the repo. The selftest
asserts that it read nothing under a repo path: every path it hands the subprocess is
`os.path.join(top, ...)`, and a final case asserts `os.path.exists(top) is False` after cleanup.

---

## 4. Rule-table cases (the "verifies its own rule table" clause)

The table is restated **independently** in the selftest and compared to the module's constants. A
surface class added to `SURFACE_AXIS` is a rule change, not a convenience, so equality is exact —
`==`, not `⊆`.

| id | assertion |
|---|---|
| T1 `rule-table-owned-axes` | `set(OWNED_AXES) == {"calibration","operability","coverage"}` and `len(OWNED_AXES) == 3` (order free) |
| T2 `rule-table-surface-map` | `SURFACE_AXIS == {"fixture-expansion":"coverage","bookkeeping-file":"calibration","knowledge-entry":"coverage","registry-append":"coverage","instrument-acquisition":"operability"}` |
| T3 `rule-table-table-wellformed` | every value of `SURFACE_AXIS` is in `OWNED_AXES`; `set(SURFACE_AXIS) & NEUTRAL_SURFACES == set()` |
| T4 `rule-table-universal-words` | `set(UNIVERSAL_WORDS) == {"all","every","complete","none","no"}` |
| T5 `rule-table-neutral-set-declared` | `NEUTRAL_SURFACES == {"receipt-binding","measurement"}` — the frozen text names no neutral class, so this case pins the tool's **declared extension** and the docstring must carry the same two words |

T2/T5 are the ones that catch the failure mode this instrument exists for: a silently widened map,
or a neutral class that quietly absorbs a real surface class.

---

## 5. Synthetic worlds

Preregistration skeleton (identical to what the parser requires: `## MACHINE BLOCK` … `END`):

```
synthetic round — preregistration

## MACHINE BLOCK
CLAIM C1
axis: <axis>
surface-class: <surface-class>
enumerate: <counting command>
END
```

Scorecards. `SC_MAIN` mirrors the real table's scores; `parse_scores` needs a `## Axes` section
terminated by the next `## ` heading, so each world carries one.

```
## Axes
| axis | score | verdict |
|---|---|---|
| calibration | 7 | synthetic |
| operability | 8 | synthetic |
| coverage | 8 | synthetic |

## Measurements
```

- `SC_TIE` — `calibration 7`, `operability 8`, `coverage 7`.
- `SC_RETIRED` — `SC_MAIN` plus `freshness 2` (a retired, non-owned axis with the lowest score).
- `SC_DECOY` — `SC_MAIN` plus a `### Round 25 measurements` table whose row is `coverage 2`; the
  decoy must not become the lowest axis.
- `SC_NOAXES` — no `## Axes` section at all (refusal world).

---

## 6. Behaviour case table (C1–C22)

Expected `flags` is the exact count in the `claims=C flags=F` line. `rule` must appear in at least
one `FLAG <claim> <rule> <detail>` line. Cases marked `EXT` assert behaviour the frozen text does
not name (the tool's stricter/neutral extension); they are kept so the extension is *pinned* rather
than ambient, and the L1 can drop them by deleting rows, not by editing prose.

| id | world | expected | pins |
|---|---|---|---|
| C1 `r1-foreign-axis-flagged` | C1 `axis: freshness`, `surface-class: measurement` | rc 1, flags 1, rule R1 | R1 positive |
| C2 `r1-owned-axis-clean` | C1 `axis: coverage`, `surface-class: measurement` | rc 0, flags 0 | R1 negative |
| C3 `r2-fixture-expansion-on-operability-flagged` | C1 `axis: operability`, `surface-class: fixture-expansion` | rc 1, flags 1, rule R2 | R2 positive **and the r25-C2 replica shape** |
| C4 `r2-bookkeeping-on-coverage-flagged` | C1 `axis: coverage`, `surface-class: bookkeeping-file` | rc 1, flags 1, rule R2 | R2 positive |
| C5 `r2-instrument-on-calibration-flagged` | C1 `axis: calibration`, `surface-class: instrument-acquisition` | rc 1, flags 1, rule R2 | R2 positive |
| C6 `r2-knowledge-and-registry-on-coverage-clean` | C1 `knowledge-entry` on coverage, C2 `registry-append` on coverage | rc 0, flags 0 | R2 negative, both right-hand pair |
| C7 `r2-neutral-surface-passthrough` | C1 `axis: calibration`, `surface-class: receipt-binding` | rc 0, flags 0 | `EXT` neutral passthrough |
| C8 `r2-missing-surface-class-flagged` | C1 `axis: calibration` with **no** `surface-class:` line | rc 1, flags 1, rule R2 | `EXT` missing-line strictness |
| C9 `r3-no-lowest-axis-flagged` | C1 `axis: operability`, `SC_MAIN` | rc 1, flags 1, rule R3, claim token `-` | R3 positive |
| C10 `r3-lowest-axis-present-clean` | C1 `axis: calibration`, `SC_MAIN` | rc 0, flags 0 | R3 negative |
| C11 `r3-retired-lower-score-ignored` | C1 `axis: calibration`, `SC_RETIRED` | rc 0, flags 0 | R3 "non-retired" limb |
| C12 `r3-tie-minima-set` | C1 `axis: coverage`, `SC_TIE` | rc 0, flags 0 | R3 tie rule (§7 D4) |
| C13 `scorecard-decoy-row-ignored` | C1 `axis: calibration`, `SC_DECOY` | rc 0, flags 0 | axes-table scan bound (§7 D5) |
| C14 `r4-missing-enumerate-flagged` | C1 `axis: coverage`, `surface-class: measurement`, no `enumerate:` | rc 1, flags 1, rule R4 | `EXT` unconditional enumerate requirement |
| C15 `r4-universal-inside-enumerate-flagged` | C1 `enumerate: bash census/all-claims.sh` | rc 1, flags 1, rule R4 | tool's substitute for frozen R4 (§8 U6) |
| C16 `r4-enumerate-names-counter-clean` | C1 `enumerate: bash census/round-26/c3-counter.sh` | rc 0, flags 0 | R4 negative |
| C17 `three-claim-well-formed-clean` | C1 `bookkeeping-file`/calibration, C2 `knowledge-entry`/coverage, C3 `instrument-acquisition`/operability, all with enumerate, `SC_MAIN` | rc 0, `claims=3 flags=0` | K1's self-hosting literal, reproduced in shape |
| C18 `refuse-no-axes-section` | C1 clean, `SC_NOAXES` | rc 2, stdout empty, no FLAG line | input refusal shape |
| C19 `refuse-claim-missing-axis` | C1 with `surface-class` + `enumerate`, no `axis:` | rc 2, stdout empty, no FLAG line | malformed prereg (frozen fixture case 11 analogue) |
| C20 `refuse-missing-prereg-arg` | invoke with `--scorecard` only | rc 2, stdout empty, stderr names `--prereg` | usage refusal |
| C21 `flag-order-and-shape` | C1 R1 + C2 R2 + C3 R4, `SC_MAIN` | rc 1, flags 3, FLAG lines in claim order, `claims=3 flags=3` terminal, every line matches `^FLAG \S+ R[1-4] \S` | stdout grammar |
| C22 `control-always-green-stub-rejected` | the whole C1–C21 table re-run against a generated stub script in `top` that prints `claims=1 flags=0` and exits 0 | at least one must-flag case (C1·C3·C4·C5·C8·C9·C14·C15·C21) **fails** under the stub, and every must-refuse case (C18·C19·C20) fails | lane's `FALSE-GREEN-REJECTED` control arm |

`N = 27` (T1–T5 plus C1–C22).

---

## 7. Tool edits this case table implies

Ordered by blast radius, against `0833de9:tools/souji-axis-check.py`.

1. argparse, `:134-135` — `--prereg` and `--scorecard` are `required=True` and no `--selftest`
   exists (the string does not occur in the committed file). Add the flag, make both paths optional
   at parse time, and enforce them in `main` for check mode only. **This is the only blocker**:
   `python3 -B tools/souji-axis-check.py --selftest` currently exits 2 in argparse.
2. `check`, `:126` — R3 compares against one `min(scores, key=...)`. Under a tie the winner is dict
   order, so a claim on the *other* tied lowest axis is flagged for no defect. Compare against the
   **set** of minimum-scoring owned axes:
   `minima = {a for a in scores if scores[a] == min(scores.values())}`.
   This is an undefined-input clarification, not a predicate relaxation: both tied axes *are* the
   lowest-scoring axis, and R3's purpose (a claim must sit on the weakest axis) is discharged by
   either. The real SCORECARD has no tie, so K1's literal is unchanged either way. If the L1 wants
   it recorded, it belongs in an amendment-3 line as a clarification, pre-data.
3. `parse_scores`, `:89` — the section span runs to the next `## ` heading, so `###` subsections
   (the measurements tables, which sit between `## Axes` and `## Capabilities`) are scanned, and a
   row shaped `coverage 2` there would overwrite the axis score. Bound the scan to the table
   immediately under `## Axes`: stop at the first line that is not a table row or separator, and do
   not descend into any heading.
4. R4, `:115-123` — no code change proposed. The predicate as implemented is a substitution for the
   frozen sentence (see U6); state the substitution in the docstring so C14/C15 pin documented
   behaviour rather than an accident.

Not a delta any more: the `KeyError: 0` that made every check-mode run traceback at exit 1
(`parse_scores` returned a bare dict at `:98` while `main` indexed `scores_out[0]`) was present in
the untracked draft this spec started from and is fixed in the landed bytes — `:98` now reads
`return scores, None`, and the real-prereg run returns `claims=3 flags=0`, exit 0.

---

## 8. Frozen C3 checks this selftest leaves unexercised

U1–U4 are unreachable **by construction** (the selftest is hermetic and additive); U5–U7 are gaps in
the case table above that a stricter table could close.

| # | frozen literal left unproven | why the selftest cannot prove it | what does |
|---|---|---|---|
| U1 | K1 base half: "`git cat-file -e 0eca7c8:tools/souji-axis-check.py` -> fails at base" | needs git and a revision; the selftest reads no repo state | `census/round-26/c3-counter.sh` at base (red receipt) |
| U2 | K1 tip half: the real `--prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md` exits 0 printing `claims=3 flags=0` | C17 reproduces the *shape* against synthetic files; a MACHINE BLOCK/`END` drift, a fourth CLAIM, or a real-SCORECARD parse failure is invisible to it | K1 at the tip |
| U3 | K2: fixture terminal `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, exit 0 | additive instrument; it cannot assert another artifact's case inventory, and the frozen 12 include a case 1 (r25-C2 replica discriminator) and a case 12 (control arm) whose *existence* only the fixture proves. C22's control runs the selftest's own table. Measured at `0833de9`: the normal run ends `cases=11 pass=11` with **no** `control=` field, exit 0; the control field appears only under `--stub`, as a separate line `control=FALSE-GREEN-REJECTED` after `cases=11 pass=4`, exit 1 — so the frozen single-line literal is not producible by any one invocation of the committed fixture, and 11 ≠ 12 | the fixture |
| U4 | K2 kill rule: "any fixture case lacking an isolated /var/tmp world" | the selftest proves only its own root is under `/var/tmp` and removed | the fixture's own inspection |
| U5 | R2's full "declared on **any** axis other than X" | 5 surface classes × 2 wrong axes = 10 off-axis pairs; the table covers 3 (C3, C4, C5). Unexercised: fixture-expansion-on-calibration; bookkeeping-file-on-operability; knowledge-entry-on-calibration; knowledge-entry-on-operability; registry-append-on-calibration; registry-append-on-operability; instrument-acquisition-on-coverage — 7 pairs | extend C3–C5 to the cross product |
| U6 | R4's antecedent: "a claim text containing a whole-word all/every/complete/none/no" | the tool never reads claim text — the MACHINE BLOCK carries only `axis:`, `surface-class:`, `enumerate:`. The implemented predicate is the substitute: a missing `enumerate:` always flags, and a universal word *inside the `enumerate:` value* flags. The frozen "naming its counting command" limb is also unchecked (any non-universal enumerate value passes) | needs either a claim-text source in the parser or an amended R4 text |
| U7 | "exit 2 on usage/**input** refusal" for an unreadable-but-present file | C18/C19/C20 exercise shape refusals; the `OSError` branch is not driven (the selftest has no permission-denied world) | one case writing a directory where a file is expected |

Also outside every artifact here: the frozen kill rule "the tool flags its own round's frozen prereg
for any reason other than a genuine defect" is a property of U2, and the amendment rule that no
predicate may relax after data — both are L1 judgements, not instrument output.

---

## 9. Pseudocode

```python
def run_selftest(out=sys.stdout) -> int:
    top = tempfile.mkdtemp(prefix="souji-axis-check-selftest-", dir="/var/tmp")
    passed = failed = 0

    def case(cid, fn):
        nonlocal passed, failed
        try:
            fn()
            passed += 1
            out.write("CASE\tpass\t%s\n" % cid)
        except Exception as exc:                       # selftest reports the reason
            failed += 1
            out.write("CASE\tFAIL\t%s\t%s: %s\n"
                      % (cid, type(exc).__name__, str(exc).replace("\t", " ").replace("\n", " ")))

    def probe(case_dir, prereg_text, score_text):
        world = os.path.join(top, case_dir)
        os.makedirs(world)
        p = os.path.join(world, "prereg.txt")
        s = os.path.join(world, "scorecard.md")
        write(p, prereg_text); write(s, score_text)
        proc = subprocess.run([sys.executable, "-B", os.path.abspath(__file__),
                               "--prereg", p, "--scorecard", s],
                              capture_output=True, text=True, cwd=world)
        return proc.returncode, proc.stdout, proc.stderr

    def expect(cid, prereg_text, score_text, rc, nflags, rule=None, claims=None):
        def run():
            assert_case_only(prereg_text, score_text, rc, nflags, rule, claims)
        case(cid, run)

    def assert_case_only(...):
        got_rc, stdout, _ = probe(...)
        lines = stdout.splitlines()
        flaglines = [l for l in lines if l.startswith("FLAG ")]
        terminal = lines[-1] if lines else ""
        assert got_rc == rc, "rc %d != %d" % (got_rc, rc)
        assert len(flaglines) == nflags, "%d FLAG lines != %d" % (len(flaglines), nflags)
        assert re.fullmatch(r"claims=\d+ flags=%d" % nflags, terminal), terminal
        if claims is not None:
            assert terminal.startswith("claims=%d " % claims), terminal
        if rule is not None:
            assert any(re.match(r"^FLAG \S+ %s \S" % rule, l) for l in flaglines), flaglines
        for l in flaglines:
            assert "|" not in l
        assert all(re.match(r"^FLAG (\S+) (R[1-4]) (.+)$", l) for l in flaglines)

    try:
        # ---- rule table (in-process) -------------------------------------
        case("rule-table-owned-axes",        lambda: assert_table_owned())
        case("rule-table-surface-map",       lambda: assert_table_map())
        case("rule-table-table-wellformed",  lambda: assert_table_wellformed())
        case("rule-table-universal-words",   lambda: assert_table_words())
        case("rule-table-neutral-set-declared", lambda: assert_table_neutral())
        # ---- behaviour (subprocess) --------------------------------------
        for spec in CASES:                 # the 21 rows of §6
            expect(spec.cid, prereg(spec), scorecard(spec), spec.rc, spec.flags,
                   spec.rule, spec.claims)
        # ---- control arm --------------------------------------------------
        def control():
            stub = write(os.path.join(top, "stub.py"),
                         "import sys\nprint('claims=1 flags=0')\nsys.exit(0)\n")
            survivors = 0
            for spec in CASES:
                if spec.rc == 0 and spec.flags == 0:
                    continue               # nothing to discriminate
                proc = subprocess.run([sys.executable, "-B", stub],
                                      capture_output=True, text=True, cwd=top)
                if proc.returncode == spec.rc and spec.flags == 0:
                    survivors += 1
            assert survivors == 0, "stub survived a must-flag case: FALSE-GREEN-ACCEPTED"
        case("control-always-green-stub-rejected", control)
    finally:
        shutil.rmtree(top, ignore_errors=True)

    out.write("selftest=%d/%d pass\n" % (passed, passed + failed))
    return 0 if failed == 0 else 1
```

---

## 10. stdout grammar and exit contract (normative)

```
case-line := "CASE" TAB ( "pass" TAB id | "FAIL" TAB id TAB reason ) NL
terminal  := "selftest=" N "/" M " pass" NL
```

- `terminal` is the last stdout line, exactly once; nothing follows it.
- `N == M` exactly when the exit status is 0; `N < M` on 1.
- `reason` carries no TAB and no newline (flattened), so the line stays one record.
- No other stdout: the subprocess captures its own `FLAG`/`claims=` lines, which never reach the
  selftest's stdout.

| invocation / condition | stdout | stderr | exit |
|---|---|---|---|
| `--selftest`, all cases pass | case lines + `selftest=N/N pass` | empty | 0 |
| `--selftest`, ≥1 case fails | case lines incl. `CASE\tFAIL…` + `selftest=N/M pass` | optional | 1 |
| check, no flags | (FLAG lines absent) + `claims=C flags=0` | empty | 0 |
| check, ≥1 flag | one `FLAG <claim> <rule> <detail>` per finding + `claims=C flags=F` | empty | 1 |
| check, usage or input refusal | empty | `souji-axis-check: refused: …` or `… required (usage exit 2)` | 2 |

A case whose *expected* code is 2 is a **pass**; the selftest itself never exits 2 — 2 is reserved
for the tool's own usage/input refusal, and a selftest that returned 2 could not be distinguished
from a broken invocation.

---

## 11. What this spec is not

- Not a second tool, and not a substitute for `tests/fixtures/r26-axis-check.py`. K2's counter is
  unchanged and still requires the fixture's own 12-case run. The selftest is the "run with no
  fixture" arm: `python3 -B tools/souji-axis-check.py --selftest`.
- Not an amendment. Every row marked `EXT` in §6 pins behaviour the frozen text does not name; if
  the L1 prefers the frozen text literally, delete those rows rather than relax a rule.
