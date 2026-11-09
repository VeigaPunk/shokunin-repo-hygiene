# R94ReviewerC2 — C2 probe setup discipline & arms counter review

Axes: (A) setup-discipline closure — does r94 probe exit 1 on any setup failure; (B) arm-label fidelity — does each arm test what its label says; (C) stream check — does the arms counter's `line` check read the right stream; (D) claim-number grounding — is '7 of 8' / 'before 3' what the filed control shows; (E) sentence width — any claim sentence wider than the predicate.

Instrument pins (from my runs, matching prereg pins): probe `e3ebe6e9318a9a55…`, arms counter `3bb8c1b9c128c135…`, fixtures/tool/before pins all match. Arms-counter re-run on r94 probe: `ARMS-SUMMARY arms=10 conform=10`, exit 0 (`arms-r94.log`, 58.91 s, all 10 arms `conform=yes`).

## Q1 — exit 1 on setup failure (receipts: `probe-edge-fast.log`, `probe-edge.log`, `probe-edge2.log`)

- Unreadable-but-present fixture (`chmod 000`): exit **2**, `C2-FORGERY-FATAL: --fixture … is not a readable regular file`. OK — the `os.path.isfile` + `os.access(R_OK)` gate (probe lines 102–105) catches it.
- Fixture is a directory: exit **2**, same gate. OK.
- Dangling-symlink `--work`: exit **2** (`--work … exists and is not a directory`, line 95 uses `lexists`). OK.
- `--work` symlink to existing empty dir: runs normally (exit 0 with real fixture, exit 2 with mute fixture). No guard, but behaves as empty dir — benign, and SOPC limits (i) names `--work` symlink as wave's to try, not as a claim leg. No falsification.
- `--work` parent is a regular file (`$S/block/leaf`): **OBSERVED exit 1 with `Traceback: NotADirectoryError` from `os.makedirs(work, exist_ok=True)` at probe line 106.** This is a genuine setup failure that exits 1 (Python uncaught-exception exit code), indistinguishable from a surviving forgery, with no `C2-FORGERY-FATAL:` line. The `lexists`/`isdir` guards (lines 95–100) do not cover this case because the parent path is not a directory, so `lexists(work)`/`isdir(work)` both return False and code falls to `makedirs`. Reproducer: `probe-edge-fast.log` T3 — recorded. Not in the 10 arms; limits (i) invites the wave to try "other setup failures" but the CLAIM sentence says the probe "refuses every other setup arm with exit 2" — see Q5 wording analysis. Rating: real defect, bounded (missing/uncreatable `--work` parent path), contradicts the spirit of "setup failures exit 2" but the arms cover only the 10 named arms. FALSIFIES-WORDING (see below).
- Non-UTF-8 tool or before bytes: **OBSERVED exit 1 with `UnicodeDecodeError` traceback at probe line 109** (`open(..., encoding="utf-8").read()` is outside any guard). Same class as above: a present-but-unreadable-in-practice file (it IS readable, and passes the line-103 check) crashes the probe with exit 1. Receipts T6/T7 in `probe-edge2.log`. FALSIFIES-WORDING per claim sentence; not an arms leg.
- Read-only existing empty `--work` (chmod 555): exit 2, `C2-FORGERY-FATAL: … no SUMMARY line for the positive control (exit 1)`. OK (fixture subprocess cannot write its own case dir, prints no SUMMARY). The probe never attempts a write to `--work` itself before the positive control which fails cleanly.
- Hanging fixture on positive control: probe has **no timeout** on its `subprocess.run` (probe line 77) — killed externally via `timeout 5` (exit 137 from timeout, T9). The probe itself would wait forever. Limits (i) explicitly lists "a fixture that hangs" as "the wave's to try", so this is disclosed, not hidden. Not a falsification of any stated sentence (claim says nothing about hangs), but a live gap: a hang reads as neither exit 1 nor 2, it reads as silence.
- Missing intermediate `--work` path (`$S/nope/deep/work`): created by `makedirs`, runs normally, exit 0. OK.

Verdict Q1: two uncaught-exception paths exit 1 on present-but-broken inputs (work-parent-not-a-dir, non-UTF-8 tool/before). All other probed setup failures correctly exit 2.

## Q2 — arm-label fidelity

- S8 "fixture-crash": verified directly (T8, `probe-edge2.log`). The synthetic crash fixture compares `--tool` against the filed tool path (matched string in arms source line 39/75); on the positive control it prints `SUMMARY cases=1 tool_pass=1 before_pass=0` and exits 0 (positive passes: `tool_pass=1/1 pass`); on forgery F1 (different path) it raises `RuntimeError` → no SUMMARY → probe exit 2 with `C2-FORGERY-FATAL: … for forgery F1 (exit 1)`. Label `crash` (crashes on forgeries) is exact; positive-control fidelity confirmed.
- S7 "fixture-mute" (`sys.exit(1)`, prints nothing, sha `2239d46e…` matches filed control `# fixture-mute sha256=2239d46e…`): on positive control probe exits 2 with `no SUMMARY line for the positive control (exit 1)`. Label exact.
- S1 "work-empty": existing empty dir; exit 0 + PASS8. Exact (r93 aborted here; confirms line-98/106 fix on r94).
- S2/S3/S4/S5/S6 all match labels (nonempty dir / regular file / missing fixture / missing tool / missing before → exit 2 + FATAL).
- Mute/crash fixture shas in my arms run (`2239d46e…`, `c959e718…`) match the filed r93-probe control shas in `c2-control-r93-probe.txt`. Same synthetic bytes — cross-run consistency confirmed.
- One subtlety: S8's synthetic fixture never reaches forgeries beyond F1 (probe returns 2 at F1) — fine for its purpose; label says "raises (no SUMMARY) for any other tool" which is true for all forgeries, only F1 exercised. Not a label defect.

## Q3 — stream check (arms line 107–108)

`stream = p.stderr if line == FATAL else p.stdout` then `any(l.startswith(line) for …)`. Probe prints `C2-FORGERY-FATAL:` to **stderr** (probe lines 93, 96, 99, 104, 112, 123, 133 — all `file=sys.stderr`) and verdict summaries to **stdout** — channels match exactly which stream is checked. Confirmed by per-arm `.out` files (arms counter writes combined for 0.7 GB harness? no, it's small): any mismatch would have shown `line=no`; all 10 are `line=yes`. One quality note: for verdict arms, a `C2-FORGERY-FATAL:` on stderr would not be checked against, but that's irrelevant — FATAL would produce exit 2 ≠ want. Stream logic correct. Q3: PASS.

## Q4 — claim numbers vs filed control `census/round-94/controls/c2-control-r93-probe.txt`

Control receipt shows: P1 exit=0, P2 exit=1, S1 exit=1, S2 exit=2, S3 exit=1, S4 exit=1, S5 exit=1, S6 exit=1, S7 exit=1, S8 exit=1; `ARMS-SUMMARY arms=10 conform=3`, EXIT 1. Conform arms = P1 (exit 0 + PASS8), P2 (exit 1 + FAIL5), S2 (exit 2 + FATAL) — exactly 3. Claim: "exits 1 on 7 of the 8 setup arms" — the 8 setup arms are S1–S8; exit 1 observed on S1, S3, S4, S5, S6, S7, S8 = 7 of 8, with S2 correctly exit 2 (r93 probe already had line 86 nonempty check). Claim "before 3, after 10" matches: conform=3 in control, conform=10 in my r94 re-run. "Counted quantity: conforming arms of 10 — before 3, after 10" — verified verbatim. Q4: numbers exact.

The illustrative parenthetical in the claim — "(an existing empty --work aborts with a FileExistsError traceback; a --work that is a regular file, a missing --fixture/--tool/--before, a fixture that prints nothing, and a fixture that crashes on forgeries all end in exit 1)" — matches control S1 exit 1, S3–S8 exit 1. R93 probe line 89 `os.makedirs(work)` (no exist_ok) explains the FileExistsError. All accurate.

## Q5 — sentence width

Claim sentence: "The r94 probe … runs on an existing empty --work and refuses every other setup arm with exit 2 and a `C2-FORGERY-FATAL:` line". As written this sentence is about "setup arms" (the 10), and within that set it's fully true (10/10 confirm). The probes' own docstring widens slightly: "Every setup failure exits 2 with one `C2-FORGERY-FATAL:` line on stderr" (probe line 5–6). My Q1 results show that docstring sentence is too wide — two setup failure shapes (work-parent-not-a-dir, non-UTF-8 tool/before) exit 1 with a traceback. The PREREGISTRATION claim sentence is narrower than the docstring; limits (i) explicitly scopes to the 10 arms and lists hang/unreadable/symlink as wave-tried territory, so these findings are "other setup failures" — which are disclosed as not-covered, not claimed-covered. Still, the claim sentence "refuses every other setup arm" could be read (and was likely intended) as a general discipline statement; my two reproducible counterexamples falsify the general reading while the bounded predicate (10/10) holds.

## Findings, by severity

1. **FALSIFIES-WORDING (docstring, general-reading)**: probe lines 5–6 — "Every setup failure exits 2 with one `C2-FORGERY-FATAL:` line on stderr". Counterexamples: (a) `--work` with a regular-file parent → `NotADirectoryError` traceback, exit 1 (`probe-edge-fast.log` T3); (b) non-UTF-8 `--tool`/`--before` bytes → `UnicodeDecodeError` traceback, exit 1 (`probe-edge2.log` T6/T7). Reproducers appended to seat receipts below.
2. **Gap (disclosed, not falsifying)**: hanging fixture — no subprocess timeout, probe waits indefinitely. Limits (i) flags hangs as wave territory; no claim sentence promises hang handling.
3. Nothing else.

## NO-FALSIFICATION where absent

Assess NO-FALSIFICATION per axis: B (labels) — fully confirmed including S8 positive-control fidelity; C (stream) — confirmed; D (numbers 7-of-8, before 3) — confirmed against filed control receipt line by line. The enumerated examples in the claim parenthetical all reproduce.

## Residual risk / verification gaps

- My T3/T6/T7 reproducers ran against the working-tree probe; tool/before/fixture pins match prereg, so this is a defect in the frozen instrument, not a drifting file. Amendment 59 routes them to `plans/round-94.md` as a narrowing amendment; I commit nothing per seat rules.
- Full C1 predicate not re-run by this seat (out of scope for a C2 reviewer seat; executor seats own it).
- No tool installs/updates performed (none needed). No scratch left behind (deleted `/fast/scratch/hyaku/souji-r94/R94ReviewerC2`). No git/jj mutation anywhere.
