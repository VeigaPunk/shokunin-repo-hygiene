# RerunGateFixture — r16 W2 falsify: `tests/fixtures/r16-landing-gate.py`

Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Artifacts under test (digests observed this run):

| path | sha256 |
|---|---|
| `tools/souji-landing-gate.py` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| `tests/fixtures/r16-landing-gate.py` (530 lines) | `aae67c9c7bafd86f1b745193ac4aead74b3a3403b5c5ade33991d246e6413f2f` |
| `tools/souji-census.sh` | `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` (matches the bytes named in the wave context) |

STATUS: PARTIAL — both required executions reproduce (real gate 15/15 PASS, exit 0; null-stub
run exit 1 with 14/15 FAIL), but the fixture's own vacuity case (F1) is tautological — it
prints PASS in that very null-stub run — and its contract prose (F2) still advertises
free-text phrase markers the gate dropped. The headline claim holds; the case that claims to
prove it, and the prose beside it, do not.

## What was executed (both ALLOWED-EXEC commands, once each)

1. `python3 tests/fixtures/r16-landing-gate.py` → 15 CASE lines all PASS, `SUMMARY total=15
   failed=0`, exit 0. Per-case `lg_rows`: replay 5, unterminated-case 1, py-compile-defects 2,
   truncated-heredoc 1, missing-reg-and-changed 2, uncited-nobase-invisible 1,
   pin-only-inside-frozen-dir 2, pin-vs-measured-commit 1, marker-one-char-off 1,
   marker-rewordings 4, carry-inside-html-comment 1, open-marker-admitted-true 1,
   missing-wave-dir 0 (exit 2), clean-all-green 0 (exit 0), vacuity-stub `stub rc=0
   stdout_bytes=0`.
2. `python3 tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-RerunGateFixture/stub.py`
   (stub: `import sys` / `sys.exit(0)`) → `SUMMARY total=15 failed=14`, exit 1. All 14
   substantive cases FAIL with `exit=0 want 1|2` (13 also report missing-row reasons;
   `missing-wave-dir` fails on the exit code alone); **`CASE vacuity-stub PASS`**.

Stub written for run 2 (`/var/tmp/souji-r16-RerunGateFixture/stub.py`, created by the `write`
tool — not a shell command — and deleted with its directory afterwards):

```
import sys
sys.exit(0)
```

The replay row count observed (5) matches the wave context's landing figure (1 parse + 3 pin
+ 1 STATUS line at `ConfigRepair.md:7`), and exit 2 / exit 0 are exercised. So the fixture is
non-vacuous *as a whole*: it demonstrably rejects a null tool through cases 1–13.

## Findings by severity

### F1 — `vacuity-stub` (Case 14) is a tautology: it passes precisely when the tool under test is the vacuous stub — FAILS

`tests/fixtures/r16-landing-gate.py:496-518`, in particular:

- `:503` `stub_proc = gate.run(LANE, REPLAY_REV, REPLAY_ROUND, tool=stub)`
- `:504` `ok, detail = evaluate(stub_proc, 1, need=[...], absent=())`
- `:510-511` `vacuous = (stub_proc.returncode == 0 and not stub_proc.stdout.strip())`
- `:512` `passed = vacuous and not ok`
- `:180-182` `evaluate` fails on `proc.returncode != exp_rc` *before* it looks at any row

Because `vacuous` requires `returncode == 0` while `evaluate` is invoked with `exp_rc = 1`,
the return-code branch at `:180` always adds a failure, so `ok` is `False` independently of
stdout content, `need` contents, or `absent` contents. Therefore `passed ≡ vacuous`, i.e. the
case asserts only that the two lines the fixture itself just wrote at `:501-502`
(`import sys` / `sys.exit(0)`) produce rc 0 and empty stdout. The only way it can fail is if
`python3` cannot run the file (rc 127 via the `FileNotFoundError` arm at `:156-161`).

Observed counterexample (run 2): the case prints `CASE vacuity-stub PASS` in the exact run
where every real assertion against the gate failed — the "guard" certifies the stub, not the
fixture. The docstring at `:41-43` ("proven in-fixture by evaluating the same assertions
against the stub's empty output") overstates what the code does: the empty output is never
the discriminator.

Verdict: **fails** (as a vacuity guard); the headline "stub must fail this fixture" still
holds via cases 1–13.

Smallest fix — evaluate the stub's empty output with the exit code it actually produces, so
the missing rows are the sole discriminator:

```python
ok, detail = evaluate(stub_proc, 0,
                      need=[("LG-PARSE-REG", ("tools/souji-census.sh",)),
                            ("LG-FROZEN-PIN", ("tools/souji-census.sh",
                                               "r15-preservation-frozen")),
                            ("LG-SEAT-UNCARRIED", ("ConfigRepair.md",))],
                      absent=())
```

With `exp_rc = 0`, `not ok` can only come from `has()` failing on the rows, which is exactly
the property `:41-43` claims. A one-line polarity control (synthesize a `proc` whose stdout
carries the three named rows and require `evaluate(...)[0] is True`) would additionally prove
the evaluator is not always-False; the 13 positive cases already cover that direction, so it
is optional.

### F2 — fixture contract text still advertises the dropped free-text phrase markers — FAILS (documentation/contract drift)

- `tests/fixtures/r16-landing-gate.py:21-23` — "LG-SEAT-UNCARRIED (STATUS: lines whose first
  word is outside the benign allowlist, **plus parse/do-not-ship/snapshot_tampered phrase
  markers** outside fenced code blocks and table rows, …)"
- `tests/fixtures/r16-landing-gate.py:38` — "reworded/decorated STATUS **and phrase
  markers**, HTML-comment carry, …"
- The gate explicitly does not do this: `tools/souji-landing-gate.py:66-69` records that both
  "any non-benign first word plus generic markers" and "free-text phrase markers (`does not
  parse`, `do not ship`)" were measured and dropped (42 lines at the r16 landing), and
  `:257-264` ("Free-text phrase markers are not used", quote at `:260`) states the shipped rule.
- The fixture's own Case 9 then *requires* the opposite of its docstring:
  `:412-413` asserts `LG-SEAT-UNCARRIED` is **absent** for `SeatC` ("The file in tree doesn't
  parse.", `:394`) and `SeatD` ("note: do not ship this", `:395`).

A gate reimplemented from the fixture's contract paragraph would emit phrase-marker findings
and fail Case 9. The cases are right; the prose is stale.

Verdict: **fails** (prose), cases **hold**.

Smallest fix: delete the phrase-marker clause at `:22-23` and the `and phrase markers` at
`:38`; add one sentence at `:36-39` recording the measurement ("dropped in r16 revision 2:
matched 42 quotation lines at the landing, none an undisclosed failure").

### F3 — Case 1 never pins the finding count, so an over-broad gate still passes the replay — PARTIAL

`tests/fixtures/r16-landing-gate.py:228-235` requires only three ids present plus the
`checked_reports=` SUMMARY substring. `evaluate` already computes the count at `:189`
(`n = sum(... "LG-")`) and prints it at `:190`, but no case asserts it. Consequence: a gate
that also emits `LG-FROZEN-MEASURED` for every pinned file at r15, or that re-introduces the
42-line phrase-marker over-match, still satisfies Case 1 (`need` is presence-only, and no
`absent` list guards extra ids). The measured figure the landing report cites — 5 findings —
is therefore unasserted even though the run reports `lg_rows=5`.

Verdict: **partial**. Cases 2–13 bound this from other angles (Case 9 kills phrase markers on
synthetic repos; Case 13 kills all ids on a clean repo), so the exposure is over-broad
findings on the frozen r15 snapshot only.

Smallest fix: add `exp_lg_rows=None` to `evaluate` (`:176`) and compare `n` to it, then pass
`exp_lg_rows=5` at `:229` (and optionally `1`, `2`, `4` on the single-defect cases, where the
observed counts are already printed). This locks the exact calibrated figure instead of just
its lower bound.

### F4 — a hung tool escapes as a traceback instead of a CASE failure — PARTIAL (robustness)

`tests/fixtures/r16-landing-gate.py:146-161`: `subprocess.run(..., timeout=180)` at `:155`,
but only `FileNotFoundError` is caught at `:156`. `subprocess.TimeoutExpired` propagates out
of the case loop (the `finally` at `:521` still deletes scratch), so the fixture dies with a
traceback and no `CASE`/`SUMMARY` line; Python's uncaught-exception exit status is 1, i.e.
indistinguishable from "a case failed" to any caller that only checks the exit code. That
weakens the `:45-46` exit-code contract for infrastructure failures.

Verdict: **partial**. Not observed in either run (both gates were prompt).

Smallest fix: add `except subprocess.TimeoutExpired as e:` returning a `P` with
`returncode = 124`, `stderr = "timeout"` alongside the existing handler.

### F5 — `has()` matches alternatives across the whole row, including the free-text detail column — residual risk (holds today)

`tests/fixtures/r16-landing-gate.py:168-173`: `head == fid and any(a in ln for a in alts)` —
`ln` is the entire `ID\tpath\tdetail` line (the gate emits that shape at
`tools/souji-landing-gate.py:594-599`, flattening tabs in `detail` to spaces). For `absent`
entries this means a path fragment can be satisfied by unrelated detail text rather than by
the `path` column; for `need` entries it means a keyword can be satisfied by detail prose
(e.g. the SUMMARY need at `:235` matches anywhere on the SUMMARY line). The real gate passes,
so no false FAIL occurs today, but any future gate detail text that enumerates sibling paths
or vocabulary words would flip an `absent` assertion for a correct gate.

Verdict: **holds** on the observed gate; latent false-FAIL sensitivity.

Smallest fix if it ever bites: match column 2 exactly when the alternative contains `/` and no
space (`ln.split("\t")[1] == alt`), keeping substring matching only for the detail-qualified
alternatives (e.g. `("tools/souji-census.sh", "r15-preservation-frozen")` at `:231-232`).

## Explicit verdicts on the wave claims

| claim | verdict |
|---|---|
| fixture passes 15/15 against the shipped gate | **holds** (observed: 15 PASS, exit 0) |
| fixture FAILs a `--tool` that exits 0 printing nothing | **holds at fixture level** (exit 1, 14/15 FAIL); **fails at case level** — `vacuity-stub` PASS in that very run (F1) |
| `vacuity-stub` proves the replay assertions reject empty output | **fails** — tautological on the exit code (F1) |
| fixture docstring states the shipped `LG-SEAT-UNCARRIED` contract | **fails** — phrase markers dropped in the gate, still advertised here (F2) |
| replay expectation pins the cited 5 findings | **partial** — presence only, count unpinned (F3) |

## Residual risk and verification gaps

- F1 and F3 are established by code inspection plus the observed PASS/FAIL coincidence in run
  2; I did not mutate the fixture (PROBE RULE — my ALLOWED-EXEC covers exactly two commands,
  no copies executed), so there is no mutated-copy demonstration of the tautology. The
  entailment `vacuous ⇒ rc==0 ≠ exp_rc==1 ⇒ ok False` is direct from `:180`+`:510-512`.
- The fixture exercises neither the non-`.py` `--tool` branch (`:147-148`), the
  `FileNotFoundError` branch (`:156-161`), nor the `--json` output path of the gate; the
  prereq/exit-2 path is only reached through a missing wave dir, not a missing tool.
- `LG-SEAT-UNCARRIED` assertions identify the seat/file only; no case pins *which* line is
  reported (the landing claim cites `ConfigRepair.md:7` specifically), so a gate flagging a
  different line of the same file would pass.
- Run 2's 14 failures all report `exit=0 want 1|2`, i.e. every synthetic repo exits 0 with
  the stub for the same (correct) reason; the synthetic cases' *internal* discrimination is
  therefore only confirmed by run 1's 15 PASS, not by the stub run.

## Commands

````
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && sha256sum tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py tools/souji-census.sh 2>&1 && wc -l tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2/ 2>&1 | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "vacuity\|stub_proc\|passed = vacuous\|Vacuity guard\|phrase markers\|do-not-ship\|snapshot_tampered\|findings=0" tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 tests/fixtures/r16-landing-gate.py 2>&1; echo "EXIT=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-RerunGateFixture/stub.py 2>&1; echo "EXIT=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "do not ship\|doesn't parse\|does not parse\|snapshot_tampered\|PHRA\|phrase" tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'join(("\t"|"\t".join\|print(finding\|emit(\|def emit\|SUMMARY' tools/souji-landing-gate.py | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '396,445p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '15,45p;170,200p;494,522p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '62,74p;255,264p;590,610p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^def has\|^def evaluate\|^def rows_of\|^class Gate\|    def run\|timeout=180\|if proc.returncode != exp_rc\|n = sum\|    detail = "exit\|# --- Case 1\|# --- Case 13\|# --- Case 14\|CASE-vacuity\|results.append\|SUMMARY" ("findings=0\|replay-b410186" tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '368,384p;480,496p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '228,242p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '160,200p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "SeatC\|SeatD\|f.write("import sys\|except FileNotFoundError\|return P()\|if self.tool.endswith\|Exit 0 iff every case\|checked_reports=\|^    finally:\|shutil.rmtree(scratch\|return 0 if failed\|def argv" tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '144,162p;412,418p;518,526p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '124,132p;140,152p' .ufo/waves/round-16/w2/RerunGateFixture.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '128,130p' .ufo/waves/round-16/w2/RerunGateFixture.md | cat -A | cut -c1-140
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^## \|^```\|^Stub written" .ufo/waves/round-16/w2/RerunGateFixture.md && wc -l .ufo/waves/round-16/w2/RerunGateFixture.md
rm -rf /var/tmp/souji-r16-RerunGateFixture && ls -d /var/tmp/souji-r16-* 2>&1; echo "---"; ls -l /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2/RerunGateFixture.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^## \|^Stub written' .ufo/waves/round-16/w2/RerunGateFixture.md; wc -l .ufo/waves/round-16/w2/RerunGateFixture.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '26,34p;195,205p' .ufo/waves/round-16/w2/RerunGateFixture.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c '^…' .ufo/waves/round-16/w2/RerunGateFixture.md; awk 'NR>=190' .ufo/waves/round-16/w2/RerunGateFixture.md | grep -n '^```$'; tail -3 .ufo/waves/round-16/w2/RerunGateFixture.md; sha256sum .ufo/waves/round-16/w2/RerunGateFixture.md; ls -d /var/tmp/souji-r16-RerunGateFixture 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum .ufo/waves/round-16/w2/RerunGateFixture.md && wc -l .ufo/waves/round-16/w2/RerunGateFixture.md && git status --porcelain -- .ufo/waves/round-16/w2/ tests/fixtures/r16-landing-gate.py tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^[#*[:space:]]*STATUS' .ufo/waves/round-16/w2/RerunGateFixture.md; echo "---"; awk 'NR>=192 && NR<=217' .ufo/waves/round-16/w2/RerunGateFixture.md | grep -c '^````'; sha256sum .ufo/waves/round-16/w2/RerunGateFixture.md; wc -l .ufo/waves/round-16/w2/RerunGateFixture.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum .ufo/waves/round-16/w2/RerunGateFixture.md
````
