# ConnQuality2 — final Q25/Q26 text matched to the gate and audit as built

Role: connector. Axis in scope: **calibration** (the only declared axis for this seat).
Revision bound: lane HEAD `163158a706352f1c0ee3521c4da2e5289970db57` (L1 landed the r16
integration while this seat read; `R16-M6` is therefore live, not hypothetical). Tool bytes
measured here: `tools/souji-landing-gate.py` sha256 `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`,
`tools/souji-seat-audit.py` sha256 `c9ff355c6bca31196eeb0527d7286e601878a1c50309d078cd1523820c9bd3b3`,
`tests/fixtures/r16-landing-gate.py` sha256 `aae67c9c7bafd86f1b745193ac4aead74b3a3403b5c5ade33991d246e6413f2f`
(both tools byte-identical to `a6ec781`; `git show a6ec781:<path>` digests agree).

**Probe class.** Source-only: no execution of either tool, the fixture, or any lane fixture.
Only the always-allowed read checks were run: `git show`/`git ls-tree`/`git diff` on named
paths, `sha256sum`, and a read-only `ast.parse` parse sweep (no `py_compile`, which would
write `__pycache__` into the lane). One deviation is disclosed at the end of **Risks**.

`corpus/QUALITY.md` is **not** edited (leaf: owned file is this report). The block below is
paste-ready and replaces the two rows landed at `corpus/QUALITY.md:64-65`; the section
heading, header row and delimiter at `:60-63` are already correct and stay.

## Paste-ready `## Round 16 criteria` section (replaces lines 60-65's rows, same header)

```markdown
## Round 16 criteria

| id | criterion | applies-to | test | lesson |
|---|---|---|---|---|
| Q25 | Landing claims are checked at the commit that lands them, against committed bytes rather than prose. (a) Every `.sh`/`.py` path of the one-segment citation shapes `tools/<name>`, `tests/fixtures/<name>`, `census/round-<n>/<name>` that `SKILL.md` names must exist at the revision and parse — `bash -n` with rc 0 and empty stderr, or Python `compile()`; a nested `tests/fixtures/<dir>/<name>.py` cite is outside that shape and is not checked. (b) Every pin in a `tests/fixtures/*-frozen/expected.json` — each `files` value and `record_sha256` — must equal the digest of the path it names at the checked revision, with a `files` key starting `tools/`, `tests/`, `census/` or `corpus/` resolving at the repository root and any other key inside the frozen directory; a declared `measured_commit` that resolves must hold every pinned path at the pinned digest, while one that does not resolve contributes no checks and leaves the record unestablished, never green — pins outside that file shape are not discovered. (c) Every failure-channel line of every `.md` report under `.ufo/waves/round-<N>/` — a line whose stripped text starts with `STATUS` after optional heading/emphasis decoration, outside fenced blocks and table rows, whose first value word is one of `incomplete`, `fail`, `failed`, `fails`, `failing`, `failure`, `blocked`, `broken`, `partial`, `harmed`, `red`, `unrun`, `error`, `regression`, `known` — must be carried verbatim (NFC; `*` and backticks dropped; whitespace collapsed; HTML comments ignored) as a substring of one line under the round lesson's `## Seat-reported failures` heading that also carries `open` or `resolved@<7+hex>`; a line carried `open` while the lesson declares `admitted: true` is a finding. Exit 0 is consistency at one revision, not behaviour: a parsing script can still be wrong and a coherent record still needs its measured run. Extends Q17 and Q23. | landing commits, frozen fixtures, round lessons | `python3 tools/souji-landing-gate.py --root <lane> --rev <landing> --round <N>` exits 0 with `checked_reports` > 0; able to fail: `--rev b410186 --round 15` exits 1 with 5 findings — LG-PARSE-REG `tools/souji-census.sh`, LG-FROZEN-PIN and 2× LG-FROZEN-MEASURED in `r15-preservation-frozen/expected.json`, LG-SEAT-UNCARRIED `.ufo/waves/round-15/w1/ConfigRepair.md:7`; `--rev a31642d --round 13` and `--rev cc21683 --round 14` exit 0; `--selftest` 18/18; held-out `python3 tests/fixtures/r16-landing-gate.py` 15/15, whose vacuity case requires a gate stub that exits 0 with no output to fail its assertions. `--base <pre-wave>` adds the changed-script arm (LG-PARSE-CHANGED); exit 2 is could-not-evaluate (usage, unknown rev, no `SKILL.md`, no report under `.ufo/waves/round-<N>/`). | corpus/lessons/round-16.md R16-M1, R16-M2, R16-M4; corpus/lessons/round-15-verifier-spotcheck.md routed R1, R3, R4 |
| Q26 | The seat probe rule is enforced from the exported transcripts, not from each report's `## Commands`: one `<SeatName>.txt` per wave-spec item, one rendered call per line (`→ tool(args…) ⇒ status`), every call classified by pinned class against the wave contract, never against the seat's self-description. Major — V-SURFACE (a forbidden path in the arguments: `census/operator-sweep-<date>`, `.ufo/state/`, an absolute `watchdog.log`, or a `~/.omp` path other than `agent/RULES.md`; `MANIFEST.json` and sibling-lane reads are not machine-classified and stay a human duty), V-LIVE-CENSUS (`souji-census.sh` with `--root` outside `/var/tmp`), V-WRITE-SCOPE (a `write`/`edit`/`ast_edit` target on a filesystem path that is neither the seat's report, a path its item declares `OWN ONLY`, nor under `/var/tmp`; absent a declaration the report is the only writable file, and `agent://` messages or non-file devices are not file writes), V-EXEC (a seat whose role is neither executor nor mutation-tester and whose item grants no `ALLOWED-EXEC:`, running a lane tool, fixture or `--selftest`; `bash -n`, `py_compile` and `ast` are exempt). Minor — V-RECURSIVE (a `find`/`rg`/`grep -r`/`ls -R` over, or a `grep`/`glob` rooted at, the lane or fleet root) and V-WRITE-UNKNOWN (an unparseable write target). Voiding is dependency-scoped and is not the exit code: V-SURFACE and V-RECURSIVE void the findings that used that output; V-LIVE-CENSUS, V-EXEC, V-WRITE-SCOPE and V-WRITE-UNKNOWN void the seat's evidence; L1 re-derives what it still needs. Exit 0 means no major class only — a minor still voids — and a seat with no transcript or zero parsed calls is unestablished, never clean. The audit is a lower bound: rendered arguments truncate, only direct `bash` invocations are classified, and `summary.major`, `summary.minor`, `missing_transcripts` and each seat's `calls` belong in the record; the wave close records `git status --porcelain` so untracked process-created files (bytecode caches, tool scratch) are attributed, since no transcript class can see them. Extends Q24. | round process, seat evidence | `python3 tools/souji-seat-audit.py --spec .ufo/waves/round-<N>/<wave>-spec.json --transcripts <dir> --lane <lane> --json census/round-<N>/seat-audit-<wave>-<run>.json` (a fresh filename per run: `--json` refuses to overwrite) with `missing_transcripts` empty and nonzero `calls` for every seat; `--selftest` 20/20 with flagged and unflagged controls; wave 1: 65 seats, 3173 calls, 1 major (`V-WRITE-SCOPE`, an attempted report-external write) and 19 minor (18 `V-RECURSIVE`, 1 `V-WRITE-UNKNOWN`) in `census/round-16/seat-audit-w1.json`. Exit 0 is not clean — read `summary.major`, `summary.minor` and the per-seat classes; the wave-close `git status --porcelain` shows no untracked path outside the report dirs. | corpus/lessons/round-16.md R16-M5; corpus/lessons/round-15-verifier-spotcheck.md routed R5; corpus/lessons/round-14-verifier-spotcheck.md routed defect 4 |
```

Lesson pointers were checked to exist at `163158a`: `corpus/lessons/round-16.md:9-12` (M1,
M2, M4) and `:13` (M5); `corpus/lessons/round-15-verifier-spotcheck.md:120-126` (routed R1–R5; R5 at `:126`); `corpus/lessons/round-14-verifier-spotcheck.md:158-164` (routed defects 1–5, defect 4
at `:163`). No criterion cites an `S0xx` row, so the not-yet-landed-source hazard the wave-1
draft avoided stays avoided.

## Falsification — Q25 against the gate as built

| # | landed clause | as-built behaviour (file:line) | verdict | smallest fix |
|---|---|---|---|---|
| F1 | "every script a `SKILL.md` registry row cites" | `CITED_PATH_RE` (`tools/souji-landing-gate.py:58-60`) matches **one** segment under `tools/`, `tests/fixtures/`, `census/round-<n>/` anywhere in `SKILL.md`. At `163158a` that set is 21 distinct paths: 19 are registry-table cites (`SKILL.md:137-154`), 2 are prose-only (`census/round-13/run-verification.py`, `census/round-14/cache-demonstration.py`); a nested cite such as `tests/fixtures/<dir>/<name>.py` is not matched. | **partial** — the check is both narrower (nested cites) and wider (prose-only cites) than the clause, so a literal implementation cannot reproduce the run. | (a)'s "one-segment citation shapes … that `SKILL.md` names". |
| F2 | "a record's `measured_commit` must hold the bytes the record pins" | `tools/souji-landing-gate.py:457-476`: when `measured_commit` does not resolve, `measured_ok` is false and **no** `LG-FROZEN-MEASURED` check runs; the in-code rationale is "A dangling measured_commit contributes no checks". A record with `measured_commit: deadbeef` therefore yields exit 0 and no finding. | **fails** — the absolute clause is satisfied vacuously; a false measurement anchor is invisible. | Criterion: "one that does not resolve contributes no checks and leaves the record unestablished, never green" (drafted). Optional hardening: emit `LG-FROZEN-MEASURED` `measured_commit <hex> does not resolve` (one branch, ~5 lines). |
| F3 | "every frozen pin" | `EXPECTED_JSON_RE` (`:92`) is `tests/fixtures/[^/]+-frozen/expected\.json$`; any frozen record outside that exact shape is never opened. | **partial** — overclaims discovery. | Name the file shape; state the rest is not discovered. |
| F4 | "carried verbatim" | `norm_line` (`:239-246`) applies NFC, drops `*` and backticks, collapses whitespace; `check_carry` (`:307-357`) then requires the normalized report line as a **substring** of one lesson line plus `open`/`resolved@`. | **partial** — "verbatim" is exact enough for the one-character-off case (`tests/fixtures/r16-landing-gate.py:370-381`) but not literally byte equality. | Spell the normalization in the clause. |
| F5 | "`STATUS:` + failure word" | `FAILURE_STATUS_WORDS` (`:72-78`) is a pinned 15-word set; `STATUS: SURVIVED`, `STATUS: unattested`, `STATUS: PROBE RULE breach` are **not** channel lines. | **fails** — "a failure word" is not reproducible; a reader would carry lines the gate does not require and could omit lines it does. | List the 15 words (drafted). Note the contract's mandated `FAIL`/`INCOMPLETE`/`BLOCKED`/`PARTIAL` are all in the set, so a contract-conforming seat is always in the channel. |
| F6 | (c) as a whole | `check_carry` also emits `LG-OPEN-ADMITTED` when a carried `open` line coexists with lesson text `admitted: true` (`:347-356`); the criterion never mentions it. | **partial** — the gate enforces an obligation the bar does not state. | Add the `admitted: true` clause (drafted). |
| F7 | test cell | The landed cell names 4 ids but not the 5-finding count, omits the r13/r14 zero replays and `--selftest` 18/18, and does not state exit 2. | **partial** — Q23: the capability wording is narrower than what was exercised. | New test cell (drafted). |

Replay arithmetic, re-derived from committed bytes (no execution): at `b410186`
`tools/souji-census.sh` = `dab4122c…` ≠ pin `b5187351…` (LG-FROZEN-PIN, 1);
`tests/fixtures/r15-census-config.py` = `6314d45d…` = pin and
`tests/fixtures/r14-census-boundary.py` = `e6a984b1…` = pin (no finding). At the record's
`measured_commit fc3a8d4`: census = `fcff8b05…` ≠ pin (LG-FROZEN-MEASURED, 1) and the r15
config fixture is **absent** at that commit (LG-FROZEN-MEASURED, 1); the r14 boundary fixture
matches. So 3 pin findings, consistent with the lesson's "5 findings: 1 parse + 3 pin + 1
carry" (`corpus/lessons/round-16.md:19-21`). Only the pin half is independently re-derived
here; the parse and carry halves are the lesson's stated measurement, not re-run.

## Falsification — Q26 against the audit as built

| # | landed clause | as-built behaviour (file:line) | verdict | smallest fix |
|---|---|---|---|---|
| G1 | "enforced … not self-report" | `run` (`tools/souji-seat-audit.py:121-150`) records a missing `<SeatName>.txt` in `missing_transcripts` and adds **no** violation; exit is unchanged. `CALL_RE` (`:39`) must match the rendered line, so a transcript in any other format yields `calls=0` and a clean seat. | **fails** — silent false-clean path; the audit can pass a wave it never read. | Criterion requires `missing_transcripts` empty and nonzero `calls` per seat; zero-call or absent transcript is unestablished (drafted). |
| G2 | voiding rule | `main` (`:203-237`) exits 1 iff `summary.major`; `V-RECURSIVE` is **minor** yet read-only, so it voids findings under the criterion while leaving exit 0. `V-SURFACE` is **major** yet read-only, so it voids only dependent findings. | **fails** — exit code and voiding map are disjoint; a landing note reading "audit exit 0" would be false as a cleanliness claim. | "Exit 0 means no major class only — a minor still voids" (drafted). |
| G3 | "writes outside its report/OWNED files" | `owned_paths` (`:61-66`) reads only `OWN ONLY (...)` in the item prompt: 3/65 items in w1, **1/79** in w2. Absent a declaration the allowed set is the report plus `/var/tmp` (fail-closed, `allowed_target` `:76-83`). | **partial** — "OWNED files" implies a declaration the spec rarely carries. | State the writable set as report + declared `OWN ONLY`; absent a declaration, report only (drafted). |
| G4 | write scope, non-file targets | only `agent://` is special-cased (`:104-105`); `write(xd://report_issue)`, `local://…`, `proc://…` fall through to `V-WRITE-SCOPE` **major**. The harness system prompt invites `xd://report_issue`; w1 happened to contain 0 such calls. | **partial** — latent false-major class against a sanctioned channel. | Criterion: `agent://` messages and non-file devices are not file writes (drafted). Tool delta: one scheme exemption in `allowed_target`; if declined, the criterion must say `agent://` only. |
| G5 | "test execution without `ALLOWED-EXEC:`" | `EXEC_ROLES = {executor, mutation-tester}` (`:58`); `eff_role` (`:136`) upgrades any item whose prompt contains `ALLOWED-EXEC:`. Role-based exemption exists independently of the flag. | **partial** — the clause omits the role arm. | Name both arms (drafted). |
| G6 | "forbidden surfaces as paths" | `SURFACE_RE` (`:43-46`) covers 4 classes: `census/operator-sweep-<date>`, `.ufo/state/`, absolute `…/.ufo/watchdog.log`, `~/.omp` (except `agent/RULES.md`). The wave contract also forbids `MANIFEST.json` and sibling-lane reads; neither is matched. | **partial** — "forbidden surfaces" is the contract's full list, not the checked set. | Name the 4 checked classes and leave `MANIFEST.json`/sibling lanes to human review (drafted). |
| G7 | test cell `--json census/round-<N>/seat-audit-<wave>.json` | `main` (`:222-227`) refuses an existing `--json` path with exit 2. `census/round-16/seat-audit-w1.json` already exists, so a rerun to the landed cell's path fails. | **partial** — the named command fails on its second run. | Fresh `<run>` filename per run (drafted). |
| G8 | lower bound | Docstring limits are real: rendered arguments truncate, and only direct `bash` invocations match `EXEC_RE` (`:49-52`) — `bash -c '…souji-census.sh…'`, `sh -c`, or a Python wrapper are invisible. | **partial** — one truncation limit is stated, the wrapper limit is not. | Add "only direct `bash` invocations are classified" (drafted). |
| G9 | write scope, process-created files | `V-WRITE-SCOPE` inspects only `WRITE_TOOLS = {write, edit, ast_edit}` (`tools/souji-seat-audit.py:57`, `:102-109`); a file created by a `bash`/`eval` command is invisible. Live at `163158a`: untracked `tools/__pycache__/souji-landing-gate.cpython-314.pyc` (12:08:03) and `tools/__pycache__/souji-preservation-evidence.cpython-314.pyc` (12:02:48) — bytecode caches from importing lane tools, i.e. lane writes no transcript class can see. They are **not** this seat's (its only Python calls are stdlib `json`/`ast`/`re` readers on bytes). | **fails** — the write scope is unenforced for process-created files, and the stray paths would enter the landing commit if `tools/` were staged. | Wave close records `git status --porcelain`; any untracked path outside the report dir is a write-scope finding (drafted criterion sentence); the stray files must not be committed (Q7 named paths, Q13). |

Exercise record checked: `census/round-16/seat-audit-w1.json` → 65 seats, all `calls` > 0,
`missing_transcripts: []`, `major: 1`, `minor: 19`; classes: `V-WRITE-SCOPE` 1 (major),
`V-RECURSIVE` 18, `V-WRITE-UNKNOWN` 1. JSON schema is top-level `seats`/`summary`/
`missing_transcripts`; `summary` holds `calls`, `major`, `minor`, `seats_audited`,
`seats_with_major` — hence the criterion names `missing_transcripts` separately, not
"`summary.missing`".

## `corpus/README.md` — the QUALITY-range lines

At `163158a`, `corpus/README.md` carries six lines that index QUALITY ranges. Four are
dated history under dated sections and are accurate *for their section*; one is the live
index and is **stale**; one is the r16 section and is correct.

| line | text (excerpt) | disposition |
|---|---|---|
| `:31` | "`QUALITY.md` — the admission bar (Q1–Q15), each criterion citing its lesson." | **FAIL.** It is the only line that presents itself as the current index, and it contradicts `:200` ("`QUALITY.md` now runs Q1–Q26") in the same file. Stale since Q16 (it was already wrong at `a6ec781`, whose `QUALITY.md` ran Q1–Q24). One-line fix: `(Q1–Q15)` → `(Q1–Q26)`. |
| `:62` | "`QUALITY.md` now runs Q1–Q16 (Q16 withdraws Q15)." | Historical, inside `### Corrections (r12 post-review, 2026-10-19)`. Accurate for that correction. Leave; if a zero-ambiguity grep target is wanted, "then ran Q1–Q16". |
| `:72-74` | "Admission bar now includes Q17/Q18 … QUALITY Q16 continues to withdraw Q15." | Historical r13 section. Leave. |
| `:100` | "Q19 replaces Q8's marker-count test with behavior and independent expected finding ids." | Historical r13 section. Leave. |
| `:113` | "QUALITY Q20 and round-14 R14-M1." | Historical r14 section. Leave. |
| `:154` | "`lessons/round-15.md` and QUALITY Q22–Q24 turn that disagreement …" | Historical r15 section; Q25/Q26 are introduced in the r16 section at `:200-201`. Leave. |
| `:200-201` | "`QUALITY.md` now runs Q1–Q26 (Q25 landing claims, Q26 transcript-audited probe rule)." | **Correct at `163158a`** (QUALITY.md has 26 `Q` rows). Its promise is only true if the Q25/Q26 rows keep their testable content — this report's block does. |

`corpus/README.md:197-199` already satisfies Q10's "or the README says where": it names
`census/round-16/` and `.ufo/waves/round-16`. No other README edit is required by Q25/Q26.

## Two calibration defects outside the two rows (advisory to L1)

1. **`corpus/lessons/round-16.md:13` (R16-M5) misstates the audit's own record.** It says
   "19 minor whole-lane recursive reads"; `census/round-16/seat-audit-w1.json` is 18
   `V-RECURSIVE` plus 1 `V-WRITE-UNKNOWN` (`SentinelCommandExec`, empty write target).
   One-class overstatement under Q23. Smallest fix: "18 whole-lane recursive reads and 1
   unparseable write target".
2. **`tests/fixtures/r16-landing-gate.py:21-24` still documents the dropped contract.** Its
   header describes "STATUS: lines whose first word is outside the benign allowlist, plus
   parse/do-not-ship/snapshot_tampered phrase markers"; the code's own case comment at
   `:384-388` and the gate at `:62-80` implement the 15-word vocabulary with **no** phrase
   markers (the gate's docstring records that phrases matched 42 quotation lines). The
   fixture's assertions are current (case 9 at `:383-407` asserts `STATUS: fails …`, the
   em-dash form, and the `SeatC`/`SeatD` prose non-findings), so this is prose-vs-behaviour,
   not a failed case — but Q25's test cell cites the fixture, and its header must not
   describe a different tool. Smallest fix: rewrite `:21-24` to the as-built carry rule.

## Affected axes

- **calibration: improves.** Every clause now names the exact resolvable set (one-segment
  citations, `*-frozen/expected.json`, the 15-word channel, the 18/1 minor split, the
  major/minor-vs-voiding split) and its declared blind spots, so a non-author can falsify a
  landing claim with `git show`, `bash -n`/`ast.parse` and the committed JSON without reading
  either tool's source. Two absolute clauses that the tools do not enforce ("every frozen
  pin", "a failure word") are removed rather than smoothed.
- **operability, coverage, depth, freshness, adjacency: no change.** Nothing executes the
  census, no knowledge entry or source row moves, no fixture changes, certification stays
  OFF, K5 stays HELD. The drafts are read-only claims about bytes already committed.

## Proposed move (one bounded proposal)

**Make the admitted claim carry its own bytes: one committed replay record with the tool
digest, per run.** C2's admission claim ("the gate detects all three r15 landing classes")
and R5's audit claim currently rest on prose — `corpus/lessons/round-16.md:18-21` — plus
`census/round-16/seat-audit-w1.json`, which records no digest of the tool that produced it.
Under Q6 (a verdict names the sha256 of the bytes it measured) and Q17 (a claimed evidence
fragment resolves to a contained file), the Q25 test cell's `--rev b410186 --round 15`
replay is a claim with no fragment: `ls census/round-16/` holds the C1 matrices, the live
fleet rows, `run-matrix.py` and `seat-audit-w1.json` — no gate replay, no selftest output.
Smallest fix: commit `census/round-16/gate-replay.json` with, per run
(`b410186`/round 15, `a31642d`/round 13, `cc21683`/round 14, landing/round 16), the resolved
rev, exit, the TSV findings verbatim and the SUMMARY line, plus
`"tool_sha256": "e7d2439d…"` and the `--selftest`/fixture tails; add the same
`tool_sha256` to the audit JSON (or a sibling `seat-audit-w1.sha256`). This is the compatible
synthesis of C2, R4 and R5: **a verdict is a (revision, tool digest, stored output) triple**,
and Q25/Q26 become checkable without re-running anything. It improves calibration only;
nothing else moves. Note `--json` refuses overwrite, so the record must be written once to a
new path.

## Risks / contradictions (stated, not smoothed)

- **Q25(b) has two defensible readings and the tool only supports one.** As built, a
  dangling `measured_commit` is silently skipped. The drafted clause makes it
  "unestablished, never green" — true of the tool, but a reader must still notice that
  `checked_pins` does not distinguish resolved from skipped. If L1 wants the stronger bar,
  the 5-line `LG-FROZEN-MEASURED` finding is the fix; the criterion should not claim it
  before it lands.
- **Q25(c)'s channel is the gate's vocabulary, not the wave contract's.** The four words the
  contract mandates (`FAIL`, `INCOMPLETE`, `BLOCKED`, `PARTIAL`) are all in the 15; a seat
  that reports a known failure as `STATUS: SURVIVED` or `STATUS: unattested` is a contract
  breach that **neither** tool sees — the gate does not classify it and the audit reads
  commands, not status prose. Stated as a residual, not closed by these rows.
- **Q26's write-scope has a live false-positive class** (G4: `xd://`, `local://`, `proc://`).
  Latent in w1 (0 calls) but the harness explicitly offers `xd://report_issue`; a seat that
  uses it would be reported major and its evidence voided. Either the one-line scheme
  exemption lands or the criterion must be read as `agent://` only — the rows above take the
  stricter bar.
- **Q26 remains a lower bound.** Wrapper execution is invisible (G8), and a transcript
  export in a different rendered format is a false-clean (G1). The criterion now says both;
  it cannot fix either. Process-created writes (G9) are live evidence: `tools/__pycache__/`
  at `163158a` (12:02, 12:08) is a lane write no class sees, and it must not be committed.
- **Moving target.** L1 landed `163158a` during this read (the r16 lesson, SOURCES, Q25/Q26,
  LOG, SCORECARD, SKILL, README). All claims here are bound to `163158a`; a later revision
  that edits either tool or either fixture invalidates the digests above, not the reasoning.
- **Seat deviation, disclosed under Q26.** Early in the read I ran one depth-limited
  `find . -maxdepth 3 -iname '*quality*' -not -path './.git/*'` in the lane root — a
  filesystem walk over the lane root, the V-RECURSIVE (minor, read-only) class. Its output
  (`./corpus/QUALITY.md`, `./census/round-14/quality-proposal.json`) was already established
  in the same batch by `git ls-tree -r --name-only HEAD | grep -i qual`; **no finding in this
  report uses the `find` output**, and no other recursive read was run. Everything else was
  exact-file reads, named-path `git` plumbing, `sha256sum`, or the read-only parse sweep.
- No tool install or update was made (nothing was needed). No pacman transaction.

## Verification

Run this session (all read-only; nothing executed from the lane):

1. `sha256sum tools/souji-landing-gate.py tools/souji-seat-audit.py tests/fixtures/r16-landing-gate.py`
   → `e7d2439d…`, `c9ff355c…`, `aae67c9c…`; `git show a6ec781:<tool> | sha256sum` equals both
   tool digests, i.e. the seeded bytes are the landed bytes.
2. Read-only `ast.parse` over the three cited files → `parse-ok` each (no `__pycache__`
   written; `py_compile` was avoided for that reason).
3. Pin disambiguation: `git show b410186:{tools/souji-census.sh,tests/fixtures/r15-census-config.py,tests/fixtures/r14-census-boundary.py} | sha256sum`
   → `dab4122c…`, `6314d45d…`, `e6a984b1…`; same paths at `fc3a8d4` → `fcff8b05…`, **absent**,
   `e6a984b1…`; pins `b5187351…`, `6314d45d…`, `e6a984b1…` → 3 pin findings as derived.
4. Citation set: `grep -oE '(tools\|tests/fixtures\|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh\|py)'`
   inside `SKILL.md:135-157` (19 paths) vs outside it (11 paths, 2 unique) → 21 distinct.
5. Audit record: `census/round-16/seat-audit-w1.json` → 65 seats, 3173 calls, 1 major
   (`V-WRITE-SCOPE`), 18 `V-RECURSIVE` + 1 `V-WRITE-UNKNOWN`, `missing_transcripts: []`,
   no zero-call seat.

Not run here (no `ALLOWED-EXEC:` on this item; L1's acceptance, not this seat's): the gate
replays, gate `--selftest`, the held-out fixture, the audit `--selftest`, and the audit over
wave-2 transcripts. The drafted test cells are prescriptions for those runs; the counts in
them come from `corpus/lessons/round-16.md:18-21` (author measurement) and
`census/round-16/seat-audit-w1.json` (committed artifact), not from an execution by this
seat.

STATUS: FAIL — corpus/README.md:31 indexes the admission bar as "Q1–Q15" while corpus/README.md:200 says "Q1–Q26" and corpus/QUALITY.md carries 26 rows at 163158a; the one-line fix is in the README table above and this line must be carried into the round lesson; untracked tools/__pycache__/ (12:02, 12:08) is an unattributed lane write that must not be committed.

The two Q25/Q26 rows and the README survey in this report are complete; this failure is the repository's, not the draft's, and it closes when `corpus/README.md:31` reads `(Q1–Q26)` (then `resolved@<rev>`).

## Commands

```sh
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/QUALITY.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/README.md 2>&1; echo "---"; ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/ 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && echo "--- tree ---" && git ls-tree -r --name-only HEAD | grep -i qual
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls corpus/ && echo "--- qualify anywhere ---" && find . -maxdepth 3 -iname '*quality*' -not -path './.git/*' 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l corpus/QUALITY.md corpus/README.md && echo "=== QUALITY headings ===" && grep -n '^#' corpus/QUALITY.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls tools/ | grep -E 'landing|seat-audit|census|preservation' ; echo "=== Q refs in README ==="; grep -n 'QUALITY\|Q2[0-9]\|Q1[0-9]' corpus/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tools/souji-landing-gate.py tools/souji-seat-audit.py && sha256sum tools/souji-landing-gate.py tools/souji-seat-audit.py && echo "=== tracked? ===" && git ls-tree -r --name-only HEAD | grep -E 'landing-gate|seat-audit'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'def \|^# ---\|add_argument\|sys.exit\|print(' tools/souji-landing-gate.py | sed -n '1,140p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=59 && NR<=65 {print NR"|"$0}' corpus/QUALITY.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -6 -- corpus/QUALITY.md && echo "=== README ranges ===" && awk 'NR>=28 && NR<=34 {print NR": "$0}' corpus/README.md && echo "---" && awk 'NR>=56 && NR<=66 {print NR": "$0}' corpus/README.md && echo "---" && awk 'NR>=70 && NR<=76 {print NR": "$0}' corpus/README.md && echo "---" && awk 'NR>=96 && NR<=102 {print NR": "$0}' corpus/README.md && echo "---" && awk 'NR>=110 && NR<=116 {print NR": "$0}' corpus/README.md && echo "---" && awk 'NR>=148 && NR<=160 {print NR": "$0}' corpus/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain corpus/QUALITY.md corpus/README.md tools/souji-landing-gate.py tools/souji-seat-audit.py tests/fixtures/r16-landing-gate.py census/round-16/ ; echo "=== HEAD QUALITY lines ==="; git show HEAD:corpus/QUALITY.md | wc -l; git show HEAD:corpus/QUALITY.md | tail -3 | cut -c1-120; echo "=== worktree vs HEAD diffstat ==="; git diff --stat -- corpus/QUALITY.md corpus/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la corpus/lessons/round-16.md 2>&1; echo "=== R16-M ids ==="; grep -nE 'R16-M[0-9]' corpus/lessons/round-16.md 2>/dev/null | cut -c1-160; echo "=== lessons dir ==="; ls corpus/lessons/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
for w in ('w1','w2'):
    d=json.load(open(f'.ufo/waves/round-16/{w}-spec.json'))
    items=d['items']
    roles={}
    own=0; allowed=0
    for it in items:
        roles[it['role']]=roles.get(it['role'],0)+1
        if 'OWN ONLY' in it.get('prompt',''): own+=1
        if 'ALLOWED-EXEC:' in it.get('prompt',''): allowed+=1
    print(w,'reportDir=',d.get('reportDir'),'items=',len(items),'roles=',roles,'OWN ONLY=',own,'ALLOWED-EXEC=',allowed)
# my item
d=json.load(open('.ufo/waves/round-16/w2-spec.json'))
for it in d['items']:
    if it['name']=='ConnQuality2':
        print('=== my item ===')
        print('role:',it['role'])
        print(it['prompt'][:1500])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^## \|^### \|admitted' corpus/lessons/round-16.md | cut -c1-140; echo "=== seat-reported section ==="; awk '/^## Seat-reported failures/{f=1} f&&/^## /&&!/Seat-reported/{if(++n>1)exit} f' corpus/lessons/round-16.md | cut -c1-200 | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la census/round-16/ && echo "=== landing json ===" && python3 -c "
import json;d=json.load(open('census/round-16/c1-matrix-landing.json'));print(json.dumps(d,indent=1)[:900])" && echo "=== seat audit summary ===" && python3 -c "
import json;d=json.load(open('census/round-16/seat-audit-w1.json'));print(json.dumps(d.get('summary'),indent=1));print('missing:',d.get('missing_transcripts')[:5], len(d.get('missing_transcripts',[])))"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tests/fixtures/r16-landing-gate.py && grep -n 'allowlist\|phrase\|snapshot_tampered\|does not parse\|FAILURE_STATUS\|SURVIVED\|import ' tests/fixtures/r16-landing-gate.py | cut -c1-180
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== all SKILL.md cites of tools|tests/fixtures|census/round-N .sh/.py ==="; grep -oE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh|py)' SKILL.md | sort -u | nl | sed -n '1,60p'; echo "=== registry table rows ==="; awk '/^\| name \| kind \| entry/{f=1} f&&/^\|/{c++} f&&!/^\|/{if(c>0)exit} END{print "rows:",c-2}' SKILL.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '370,420p' tests/fixtures/r16-landing-gate.py; echo "=== summary tail ==="; tail -30 tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^| name | kind | entry\|^## ' SKILL.md | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c 'results.append' tests/fixtures/r16-landing-gate.py; echo "=== case names ==="; grep -oE 'case\("[a-z0-9-]+"|results.append\(\("[a-z0-9-]+"' tests/fixtures/r16-landing-gate.py | sed -E 's/.*\("//; s/"$//' | nl
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== cited inside registry (135-157) ==="; sed -n '135,157p' SKILL.md | grep -oE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh|py)' | sort -u; echo "=== cited OUTSIDE registry ==="; { sed -n '1,134p' SKILL.md; sed -n '158,$p' SKILL.md; } | grep -oE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh|py)' | sort -u
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== expected.json at b410186 ==="; git show b410186:tests/fixtures/r15-preservation-frozen/expected.json; echo "=== record.json at b410186 (keys) ==="; git show b410186:tests/fixtures/r15-preservation-frozen/record.json | python3 -c "import json,sys;d=json.load(sys.stdin);print('measured_commit:',d.get('measured_commit'));print('keys:',sorted(d))"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for rev in b410186 fc3a8d4; do echo "== $rev"; for p in tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py; do printf '%s ' "$p"; git show $rev:$p 2>/dev/null | sha256sum | cut -c1-16 || echo ABSENT; done; done; echo "pins:"; echo "census b51873514d1f6d34 / r15cfg 6314d45db6be7281 / r14bnd e6a984b1daf1f79a"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/seat-audit-w1.json'))
for n,s in d['seats'].items():
    for v in s['violations']:
        if v['class'] in ('V-WRITE-SCOPE','V-WRITE-UNKNOWN'):
            print(v['severity'],v['class'],n,'|',v['args'][:150])
" ; echo "=== any xd:// or local:// in args? ==="; grep -c 'xd://\|local://' census/round-16/seat-audit-w1.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'Q[0-9]{1,2}' corpus/README.md | cut -c1-200; echo "=== tail 160-187 ==="; awk 'NR>=160 {print NR": "$0}' corpus/README.md | cut -c1-220
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "admitted:true lines:"; grep -n 'admitted: *true' corpus/lessons/round-16.md | cut -c1-120; echo "=== major violation ==="; python3 -c "
import json;d=json.load(open('census/round-16/seat-audit-w1.json'))
for n,s in d['seats'].items():
    for v in s['violations']:
        if v['severity']=='major': print(n, v['class'], v['line'], v['args'][:160])
print('--- minor classes:', sorted({v['class'] for s in d['seats'].values() for v in s['violations'] if v['severity']=='minor'}))
"; echo "=== fixture header ==="; sed -n '1,40p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^\s+check\(' tools/souji-landing-gate.py | wc -l; grep -nE 'CASE\t|passed \+= 1|failed \+= 1' tools/souji-landing-gate.py | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w2-spec.json'))
for it in d['items']:
    if it['name'] in ('ConnLessonCarry','ConnSkillRegistry2','CriticC2Dodges','SentinelGateSafety'):
        print('#####',it['name'],it['role'])
        print(it['prompt'][it['prompt'].find('Draft') if 'Draft' in it['prompt'] else 0:][:900])
        print()
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/README.md | awk 'NR>=189 && NR<=203 {print NR": "$0}' | cut -c1-240; echo "=== HEAD QUALITY Q rows ==="; git show HEAD:corpus/QUALITY.md | grep -cE '^\| Q[0-9]+'; git show HEAD:corpus/QUALITY.md | grep -oE '^\| Q[0-9]+' | tail -3
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json,collections
d=json.load(open('census/round-16/seat-audit-w1.json'))
c=collections.Counter(v['class'] for s in d['seats'].values() for v in s['violations'])
sev=collections.Counter((v['class'],v['severity']) for s in d['seats'].values() for v in s['violations'])
print('by class:',dict(c)); print('by class+sev:',dict(sev))
print('seats with calls==0:',[n for n,s in d['seats'].items() if s['calls']==0])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -4 && echo "=== HEAD quality lines ===" && git show HEAD:corpus/QUALITY.md | wc -l && git show HEAD:corpus/QUALITY.md | grep -E '^## ' && echo "=== status ===" && git status --porcelain corpus/QUALITY.md corpus/README.md && echo "=== worktree vs HEAD ===" && git diff --stat HEAD -- corpus/QUALITY.md corpus/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff a6ec781..163158a --stat && echo "=== QUALITY diff ===" && git diff a6ec781..163158a -- corpus/QUALITY.md | cut -c1-300
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== HEAD README Q refs ==="; grep -nE 'Q[0-9]{1,2}[–-]Q?[0-9]{0,2}|Q[0-9]{1,2}' corpus/README.md | cut -c1-190; echo; echo "=== HEAD qual range sentences ==="; grep -nE 'Q1–Q|Q1-Q|Q2[0-9]–Q2[0-9]|Q22' corpus/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^#{2,4} |^\*\*R[0-9]|^\| R[0-9]|^- \*\*R[0-9]' corpus/lessons/round-15-verifier-spotcheck.md | cut -c1-170; echo "=== R1/R3/R4 text ==="; awk 'NR>=110 && NR<=130 {print NR": "$0}' corpus/lessons/round-15-verifier-spotcheck.md | cut -c1-230
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'defect 4|^## |^### |^\*\*[0-9]' corpus/lessons/round-14-verifier-spotcheck.md | cut -c1-160; echo "=== around 160-170 ==="; awk 'NR>=158 && NR<=172 {print NR": "$0}' corpus/lessons/round-14-verifier-spotcheck.md | cut -c1-200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'regenerate' SKILL.md | cut -c1-220; echo "=== Q25/Q26 mentions in SCORECARD/LOG/SKILL ==="; grep -n 'Q25\|Q26' SCORECARD.md LOG.md SKILL.md | cut -c1-200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'souji-landing-gate\|souji-seat-audit\|r16-landing-gate' SKILL.md | cut -c1-260
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-landing-gate.py tools/souji-seat-audit.py tests/fixtures/r16-landing-gate.py; echo "=== a6ec781 digests ==="; for p in tools/souji-landing-gate.py tools/souji-seat-audit.py; do printf '%s ' "$p"; git show a6ec781:$p | sha256sum | cut -d' ' -f1; done; echo "=== md reports at HEAD under round-16 ==="; git ls-tree -r --name-only HEAD -- .ufo/waves/round-16 | grep -c '\.md$'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json;d=json.load(open('census/round-16/seat-audit-w1.json'));print('top keys:',sorted(d));print('summary keys:',sorted(d['summary']));print('seat keys:',sorted(next(iter(d['seats'].values()))))"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c 'import ast,sys
for p in sys.argv[1:]:
    try:
        ast.parse(open(p,"rb").read()); print("parse-ok",p)
    except SyntaxError as e:
        print("parse-FAIL",p,e)' tools/souji-landing-gate.py tools/souji-seat-audit.py tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== gate anchors =="; grep -n 'CITED_PATH_RE = \|FAILURE_STATUS_WORDS = \|EXPECTED_JSON_RE = \|def norm_line\|def check_carry\|def check_frozen_pins\|measured_ok = \|def evaluate\|def main' tools/souji-landing-gate.py; echo "== audit anchors =="; grep -n 'CALL_RE = \|SURFACE_RE = \|LIVE_CENSUS_RE = \|EXEC_RE = \|OWN_RE = \|WRITE_TOOLS = \|EXEC_ROLES = \|def owned_paths\|def allowed_target\|agent://\|eff_role = \|def run\|def main\|refusing to overwrite' tools/souji-seat-audit.py; echo "== fixture anchors =="; grep -n 'benign allowlist\|L1 revision 2' tests/fixtures/r16-landing-gate.py | cut -c1-140
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^def \|^        return findings\|^    return result\|^    return calls\|^    return out' tools/souji-seat-audit.py tools/souji-landing-gate.py; echo "== fixture docstring =="; sed -n '18,26p' tests/fixtures/r16-landing-gate.py | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^def ' tools/souji-seat-audit.py; echo ---; awk 'NR>=84 && NR<=100 {print NR": "$0}' tools/souji-seat-audit.py | cut -c1-100; echo "--- run tail ---"; awk 'NR>=150 && NR<=170 {print NR": "$0}' tools/souji-seat-audit.py | cut -c1-100
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'measured_commit cross-check\|lesson_admitted\|LG-OPEN-ADMITTED\|a.out\|len(reports)' tools/souji-landing-gate.py | sed -n '1,20p'; echo "--- audit json block ---"; awk 'NR>=218 && NR<=236 {print NR": "$0}' tools/souji-seat-audit.py | cut -c1-110; echo "--- agent:// + eff_role ---"; awk 'NR>=102 && NR<=110 {print NR": "$0}' tools/souji-seat-audit.py | cut -c1-90; awk 'NR>=132 && NR<=138 {print NR": "$0}' tools/souji-seat-audit.py | cut -c1-110
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=72 && NR<=80 {print NR": "$0}' tools/souji-landing-gate.py; echo ---; awk 'NR>=58 && NR<=60 {print NR": "$0}' tools/souji-landing-gate.py; echo ---; awk 'NR>=43 && NR<=54 {print NR": "$0}' tools/souji-seat-audit.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'F1\|F2\|F3\|F4\|F5\|F6\|F7\|G1\|G2\|G3\|G4\|G5\|G6\|G7\|G8\|20-24\|384-389\|444-458\|55-58\|129-158\|225-237\|63-68\|92-96\|107-108\|:60\|143-148\|35-39\|213-218\|38-40\|:23`' .ufo/waves/round-16/w2/ConnQuality2.md | cut -c1-120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import re
p='.ufo/waves/round-16/w2/ConnQuality2.md'
t=open(p).read().splitlines()
inb=False; rows=[]
for i,l in enumerate(t,1):
    if l.startswith('```markdown'): inb=True; continue
    if inb and l.startswith('```'): inb=False; continue
    if inb and l.startswith('|'): rows.append((i,l))
print('rows:',len(rows))
for i,l in rows:
    print(i,'pipes=',l.count('|'),'cells=',len(l.strip().strip('|').split('|')))
print('fence balanced:', sum(1 for l in t if l.startswith('```'))%2==0)
# any status line in fenced block? (should not be)
print('STATUS lines:',[i for i,l in enumerate(t,1) if re.match(r'^\s*STATUS',l)])
print('## Commands present:', any(l.strip()=='## Commands' for l in t))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tools/__pycache__/ && stat -c '%n %y' tools/__pycache__/* 2>/dev/null | cut -c1-160; echo "--- now ---"; date -Is
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain corpus/QUALITY.md corpus/README.md tools/ tests/fixtures/r16-landing-gate.py .ufo/waves/round-16/w2/ConnQuality2.md; echo "--- HEAD ---"; git rev-parse --short HEAD
```
