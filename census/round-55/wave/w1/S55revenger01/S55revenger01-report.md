# S55revenger01 — r54 routed-items vengeance (souji round 55, wave w1)

Role: revenger. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Seat: `.ufo/waves/round-55/w1/S55revenger01/` (receipts under `receipts/`).
Scratch: `/fast/scratch/hyaku/souji-r55/S55revenger01/` (deleted after yield).
No frozen byte was edited; no git/jj mutation was issued anywhere except inside
scratch fixture clones (each preceded by a `rev-parse --show-toplevel` assertion).

## 0. Pre-flight

- Frozen pins: all six sha256 match the prereg exactly (`c1-counter.py`
  `944feafa…`, `c2-counter.py` `e4eb34e6…`, `build-fixtures.py` `e629a2e9…`,
  `run-matrix.sh` `ce13d4ff…`, `c1-selftest-expected.tsv` `ca096117…`,
  `c2-selftest-expected.tsv` `63391afa…`). No mismatch → no stop-and-report.
- Fixture determinism: rebuilding all 27 C1 + 13 C2 fixtures from the frozen
  builder reproduces every rev in all four committed matrices
  (`# REPRO … OK` ×4, `receipts/results-v3-v4-matrix.txt`); the committed
  `records/*-matrix-*.tsv` are byte-identical to `records/matrix-dryrun/*`
  (`cmp` ×4 → IDENTICAL).
- Pinned selftests, run from committed bytes with the pinned builder/expected
  digests: C1 `SELFTEST pass cases=27` EXIT=0; C2 `SELFTEST pass cases=15`
  EXIT=0 (`receipts/c1-selftest-v4.txt`, `receipts/c2-selftest-v4.txt`).
  Wrong pins refuse before exec: both return `CANNOT-EVALUATE PIN-MISMATCH`
  rc 2 and create no fixture directory (`receipts/*-selftest-wrongpin.txt`).
- Real lane, v4 counter, from committed bytes: C1 exit 0 and C2 exit 0 at
  **both** the receipted measured revision `4b10ddd1741a…` and the current
  lane tip `3ce0ba036275…`, printing the frozen field string verbatim
  (`unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0
  bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0`; `receipt=ok
  sorted=ok tool_pin=ok`). Receipts `c1-real-lane-*.txt`, `c2-real-lane-*.txt`.
- Environment: `bash scripts/hyaku/disk-guard.sh status` before the heavy pass
  (`/fast/scratch/hyaku` 50% used, 408.9G free). No installs were needed;
  no tool version changed. pacman untouched.

## 1. Headline

24 of the 27 routed items are closed by committed instrument bytes, committed
fixture coverage, or committed disclosure. **Three are OPEN and unchanged —
S4, S5, N6.** They are exactly the three that required *prose* landings
(a builder guard, a docstring sentence, a prereg named-limit line): the round's
instrument work did not reach them, and the r55 prereg's "Named limits carried
into v4" list names none of them. One further item (§5.1) has its mechanism in
place but its `corpus/QUALITY.md` criterion is not yet in the tree (the report
and lesson do not exist), so only the mechanism half verifies today.

Verdict counts: INSTRUMENTED 21 · REPAIRED-BY-DISCLOSURE 2 · OPEN 3 ·
§5.1 mechanism INSTRUMENTED / criterion pending.

## 2. Item-by-item table

Evidence column: `R` = `receipts/results-v3-v4-matrix.txt` (one live run per
fixture under both frozen counters, same build, revs reproduced); other files
named. "v3 → v4" is the measured exit code (and first finding-id) of the frozen
r54 counter vs the r55 v4 counter on the same committed fixture.

| # | item (r54 source) | verdict | committed bytes / fixture | measured v3 → v4 | receipt |
|---|---|---|---|---|---|
| 1 | **S1** HIGH exotic line separators defeat the fence refusal (sentinel) | **INSTRUMENTED** | `census/round-55/c1-counter.py` `hidden_lines()` — one line model, `text.split('\n')` everywhere incl. the correction's own line number; fixture `F7-FF` (two `\x0b` lines above a `~~~` fence) | `F7-FF` rc 0 `-` → rc 1 `CORRECTION-IN-FENCE` (`fenced=2`) | R; plus `\u2028` and `\x85` variants (same shape): v3 rc 0 → v4 rc 1 `CORRECTION-IN-FENCE`, `receipts/c1-separator-and-c2-nl2-probes.txt` |
| 2 | **R1** hidden-correction swallow (2-space indent; one-line `<!--…-->` wrapper) | INSTRUMENTED | `CORR_RE`/`CORR2_RE` `^ {0,3}(?:<!--\s*)?…` + "a hidden line that lexes as a correction is audited like any filing"; `F20-R1-INDENT-SWALLOW`, `F21-R1-ONELINE-SWALLOW` | F20 rc 0 → rc 1 `BOGUS-RECOMPUTED` (`bogus=2`); F21 rc 0 → rc 1 `BOGUS-RECOMPUTED` (`bogus=2 fenced=2`) | R |
| 3 | **R2** dual-anchor aliasing | INSTRUMENTED | `line_zones()` per occurrence + `ANCHOR-ALIAS-MISMATCH`; `F13-DUAL-ANCHOR` | rc 0 → rc 1 `ANCHOR-ALIAS-MISMATCH` (`alias=1`) | R |
| 4 | **R3** pair-filing stale drop | INSTRUMENTED | `PAIR-FILING-INERT` branch over `pair_filings`; `F14-PAIR-STALE-FILING` | rc 0 → rc 1 `PAIR-FILING-INERT` (`pairinert=1`) | R |
| 5 | **R4** rows-word dodge | INSTRUMENTED | `PAIR_ANNOT_RE` unit word optional; `F15-PAIR-NOROWS` | rc 0 → rc 1 `UNFILED-SOURCES-ANNOTATION` (`logunfiled=1`) | R |
| 6 | **R5** fence over-hide vs CommonMark 0.31.2 (4-space indent; backtick in info string) | INSTRUMENTED (false positives removed) | fence start conditions in `hidden_lines()`; `F17-INDENT4-FENCE`, `F18-BTINFO-FENCE` | rc 1 `CORRECTION-IN-FENCE` → rc 0 (both) | R |
| 7 | **R6** PAIR_SITES scan does not hide-fence | INSTRUMENTED | `phidden = hidden_lines(ptext)` in the pair loop; `F19-PAIR-IN-FENCE` | rc 1 `UNFILED-SOURCES-ANNOTATION` → rc 0 | R |
| 8 | **S2** MEDIUM pair scan ASCII-only | INSTRUMENTED | `PAIR_ANNOT_RE` accepts `->` or `→`; `F16-PAIR-ARROW` | rc 0 → rc 1 `UNFILED-SOURCES-ANNOTATION` (`logunfiled=1`) | R |
| 9 | **S3** MEDIUM unknown-receipt-key regex uppercase-only | INSTRUMENTED | `RECEIPT_KV = \s*#\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\S+?)\s*`, key upper-cased on read; `FB2-LOWER-KEY` | rc 0 → rc 1 `RECEIPT-UNKNOWN-KEY` | R |
| 10 | **S4** LOW builder `--work` guard accepts a relative path | **OPEN** | `census/round-55/fixtures/build-fixtures.py` `main()`: `work = Path(ns.work); if not work.is_dir(): …` — no absolute-path requirement; `init_repo`/`main` byte-identical to the r54 builder (`diff` → IDENTICAL) | relative `--work rel55` → guard accepts → `git -C rel55 init rel55/<name>` builds the repo at `rel55/rel55/<name>`, leaves `rel55/<name>` behind, then aborts `RuntimeError: fixture cmd failed … not a git repository` at `rev-parse`; identical failure in the r54 builder | `receipts/s4-relative-work-probe.txt` |
| 11 | **S5** LOW C1 docstring promises a `PRISTINE FAIL` class the counter never emits | **OPEN** | `census/round-55/c1-counter.py:75` still reads `Exit 1: any finding (PRISTINE FAIL included).`; no code path prints `PRISTINE FAIL`; the r55 prereg has no named-limit line for it | token scan: `PRISTINE printed-by-code: no`; an exit-1-with-zero-FINDING state is reachable (`unfiled=2`, rc 1, 0 FINDING lines) so the *exit class* exists but nobody names it | `receipts/docstring-vs-emitted-ids.txt`, `receipts/c1-pristine-exit-class.txt` |
| 12 | **S6** LOW `--scratch` accepted and ignored | INSTRUMENTED | `--scratch` is `alias of --work`; `work = ns.work or ns.scratch`; docstring names "the r54 sentinel S6 routed fix: the argument steers writes" | `--selftest --scratch DIR` alone builds all 27 fixtures under DIR (`SELFTEST pass cases=27`); measure mode writes nothing by design | `receipts/c1-selftest-s6-scratch-steers.txt` |
| 13 | **PTR** pointer exemption path-unscoped (connector) | INSTRUMENTED | `PTR_RE = (?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{1,5}:\d` (dot extension required); `F22-PTR-TIMESTAMP`, `F12c-LOG-POINTER-EXEMPT` | F22 rc 0 → rc 1 `UNFILED-SOURCES-ANNOTATION`; F12c stays rc 0 (real `…ws-drift-vs-r46.tsv:2` pointer still exempt) | R |
| 14 | **NL-1** `#`-row with four tabs silently dropped | INSTRUMENTED | `COMMENT-AMBIGUOUS-NAME` widened to *any* tab-bearing `#` line; the dead `DATA_LIKE_COMMENT` fullmatch removed; `FB1-TAB4-ROW` | rc 0 → rc 1 `COMMENT-AMBIGUOUS-NAME` | R |
| 15 | **NL-2** ≥5-tab rule is shape-only (prose comment refused; tabless prose accepted) | **REPAIRED-BY-DISCLOSURE** | v4 C2 docstring named limits: "free-form comments without tabs are still accepted (NL-2 stays: the rule cannot read intent)"; prereg "Named limits carried into v4" says the same | tabless prose comment accepted (rc 0, receipt rebound); 5-tab prose comment refused `COMMENT-AMBIGUOUS-NAME` | `receipts/c1-separator-and-c2-nl2-probes.txt` |
| 16 | **NL-3** `RECEIPT-UNKNOWN-KEY` uppercase-only | INSTRUMENTED | widened `RECEIPT_KV`; `FB2-LOWER-KEY` | rc 0 → rc 1 `RECEIPT-UNKNOWN-KEY` | R |
| 17 | **NL-4** `#  KEY=` / `#KEY=` evade detection | INSTRUMENTED | `\s*#\s*KEY\s*=\s*VALUE` fullmatch; known keys in those shapes are recognized/validated; `FB3-NOSPACE-KEY` | rc 0 → rc 1 `RECEIPT-UNKNOWN-KEY` | R |
| 18 | **NL-5** `--tool-sha256` shapes exit 2 generically | INSTRUMENTED | named `CANNOT-EVALUATE TOOL-SHA-ARG-MALFORMED`; selftest arm `FB4-PIN-SHAPE` | arm rc 2 `TOOL-SHA-ARG-MALFORMED` (uppercase pin) | `receipts/c2-selftest-v4.txt` |
| 19 | **M2** closing-fence length rule survivor (mutation01) | INSTRUMENTED | `hidden_lines()` closing rule `set(body) == {ch} and len(body) >= n`; `F8b-BT4-SHORT-RUN` | v4 rc 1 `CORRECTION-IN-FENCE`; mutant `len(body) >= 1` → rc 0 → **killed** | R; `receipts/kill-power-mutants.txt` |
| 20 | **M7** pointer-exemption survivor | INSTRUMENTED | as PTR; `F12c-LOG-POINTER-EXEMPT` | v4 rc 0; mutant dropping `PTR_RE.search(ln)` → rc 1 `UNFILED-SOURCES-ANNOTATION` → **killed** | R; `receipts/kill-power-mutants.txt` |
| 21 | **M11** `--tool-sha256` mismatch branch unreachable from `--selftest` | INSTRUMENTED | selftest arm `FA9-WRONG-TOOL-PIN` passes `'0'*64` for `FH-HONEST` | arm rc 1 `TOOL-SHA-ARG-MISMATCH`; mutant removing the finding → rc 0 → **killed** | `receipts/c2-selftest-v4.txt`, `receipts/kill-power-mutants.txt` |
| 22 | **N5** `SOURCES-RECOMPUTE-MISMATCH` had no committed fixture | INSTRUMENTED | `F23-SOURCES-RECOMP` (`recomputed=3->4` vs grep `3->3`, `sources_revs=SELF`) | v4 rc 1 `SOURCES-RECOMPUTE-MISMATCH` (`logrecomp=1`); mutant removing the branch → rc 0 → **killed** | R; `receipts/kill-power-mutants.txt` |
| 23 | **N1** docstring names a class no code path emits (`SOURCES-ANNOTATION-DRIFT`) | INSTRUMENTED | v4 docstring "v3 findings carried over … v4 findings added …" — 11 names, all emitted | set-diff both directions empty; v3 arm shows `SOURCES-ANNOTATION-DRIFT` in the docstring and not in the emitted set | `receipts/docstring-vs-emitted-ids.txt` |
| 24 | **N6** R12 exit-code ambiguity (exit 1 PRISTINE FAIL vs exit 2 bad revision) has no named-limit line in the prereg | **OPEN** | `census/round-55/preregistration.txt` "Named limits carried into v4" — no exit-code line; the v4 C1 Exit legend is the r54 text verbatim | classes confirmed by probe: C1 short rev → rc 2 `CANNOT-EVALUATE full 40-hex revisions required`; C2 absent capture → rc 1 `PRISTINE FAIL FLEET-CENSUS-ABSENT` | `receipts/exitcode-probe-c1-shortrev.txt`, `receipts/exitcode-probe-c2-absent.txt` |
| 25 | **spot-check §5.1** a report's measured revisions must carry receipts | **INSTRUMENTED (mechanism); criterion pending** | see §3 ledger: every revision the round currently cites as measured has a committed `rev=` receipt; `corpus/QUALITY.md` carries no round-55 criterion yet and `.ufo/reports/round-55/` does not exist | ledger: `c1-tip.txt`/`c2-tip.txt` → `rev=4b10ddd1741a…`; `c1-real-lane-base-preflight.txt`/`c2-r54-capture-preflight.txt` → `rev=f056aaa031bb…`; selftests+matrices → fixture revs | `records/` listing, §3 |
| 26 | **spot-check §5.2** a counted kill row must name its finding | INSTRUMENTED | `records/c1-matrix-v4.tsv` 21 exit-1 rows, `c2-matrix-v4.tsv` 11 — **0** with `finding=-`; FA8 now `CLASS-MISMATCH` (v3 arm prints the raw `class`); `run-matrix.sh` `finof()` extracts token `$2` of the first `FINDING` line | audit command in §4; residual named in §5 | R; `records/*-matrix-v4.tsv` |
| 27 | **spot-check §5.4** ~60 W04 duplicate-URL warnings, pre-existing | **REPAIRED-BY-DISCLOSURE** (disclosure of a pre-existing condition; no repair claimed) | `records/census-before-receipt.txt`: `DIR-WARN-W04=61`, `CONF-RC=0`, `DIR-RC=0`, `ADAPTER-EXIT=0`, final line `ok …/corpus/SOURCES.md`; live re-run at the tip: 61 W04, exit 0, no S278 duplicate URL | `W04=61`; `docs.python.org/3.12/library/stdtypes.html` appears 0× in the warnings (S278 adds no new W04) | `receipts/census-validate-tip.txt` |

## 3. §5.1 — the receipt ledger (mechanism check)

Receipts in `census/round-55/records/` and the revisions they pin:

| receipt | pins | result |
|---|---|---|
| `c1-tip.txt` | real lane `rev=4b10ddd1741a`, `base=f056aaa031bb` | exit 0, frozen C1 field string |
| `c2-tip.txt` | real lane `rev=4b10ddd1741a` | exit 0, `receipt=ok sorted=ok tool_pin=ok` |
| `c1-real-lane-base-preflight.txt` | real lane `rev=f056aaa031bb`, `base=fe12daad2549` | exit 0, same field string |
| `c2-r54-capture-preflight.txt` | real lane `rev=f056aaa031bb` (r54 capture) | exit 0 |
| `c1-selftest.txt` / `c2-selftest.txt` | fixture revs only (27 / 15 cases) | pass |
| `c1-matrix-v3.tsv`, `c1-matrix-v4.tsv`, `c2-matrix-v3.tsv`, `c2-matrix-v4.tsv` | one `rev` (and `base`) per fixture row | v3/v4 arms |
| `records/matrix-dryrun/*.tsv` | byte-identical copies of the four matrices | freeze-time dry run = post-freeze run |
| `sources-count-pinned-revs.txt` | registry counts at `f056aaa0` (201), `f778b9d1` (198), `9bf9234a` (199) | matches the prereg's recompute command |
| `base-note.txt`, `porcelain-at-base.txt`, `freeze-check-at-freeze.txt`, `census-before-receipt.txt` | base revision, clean worktree, freeze self-check (`SUMMARY claims=2 findings=0`), round-start census | — |

Mechanism verdict: **present and exercised** for every revision the round can
currently cite as measured (`4b10ddd1`, `f056aaa0`, plus fixture revs). Two
gaps, both disclosure-side, not byte-side:

1. `.ufo/reports/round-55/` does not exist and `corpus/QUALITY.md` has no
   round-55 criterion row (the prereg routes the criterion to land with the
   round-55 lesson). Until that lands, §5.1 is a promise, not a checked rule.
2. The selftest receipts cannot *witness* that the pin arguments were passed:
   `c1-selftest.txt` is byte-identical to an unpinned run (the pin check is a
   silent pre-exec guard). A pinned run and an unpinned run produce the same
   receipt bytes; only re-running with the pins (as done here) proves the guard.
   If §5.1 is to be auditable from receipts alone, the selftest should print the
   pinned digests or a `PIN ok` line.

## 4. §5.2 — named kill rows (re-measured)

```
awk -F'\t' 'NR>1 && $5==1 && $6=="-"' census/round-55/records/{c1,c2}-matrix-v4.tsv | wc -l  -> 0
awk -F'\t' 'NR>1 && $5==1'            census/round-55/records/c1-matrix-v4.tsv | wc -l  -> 21
awk -F'\t' 'NR>1 && $5==1'            census/round-55/records/c2-matrix-v4.tsv | wc -l  -> 11
```
The v3 acceptance-control matrix still carries the raw lowercase `class` token
on FA8 (the historical defect, frozen arm); the v4 arm carries
`CLASS-MISMATCH`. `run-matrix.sh` fixes the extraction (`finof()`: second
whitespace token of the first `FINDING` line), so a counted kill row names its
finding by construction.

Residual: the C1 counter has an exit-1 state with **no** `FINDING` line
(`unfiled > 0`, `findings` empty — measured: rc 1, 0 FINDING lines,
`receipts/c1-pristine-exit-class.txt`). A future fixture in that state produces
a counted kill row with `finding=-` and no name exists to print. This is the
same hole as S5/N6 (nobody has named the `PRISTINE FAIL` exit class); the
matrix convention cannot fix it, only the counter or the prereg can.

## 5. Detailed notes on the three OPEN items

**S4 — builder `--work` guard accepts a relative path (still true).**
`main()` accepts any existing directory, relative or not; `init_repo()` then
runs `git -C <relative-parent> init <relative-dir>`, so the repository is
created one level deeper (`rel55/rel55/<name>`), the intended directory is left
empty, and the build aborts with a raw `RuntimeError` at the toplevel check.
`init_repo` and `main` are byte-identical to the r54 builder (`diff` →
IDENTICAL), so the routed hardening fix did not land. No escape (writes stay
under the caller's relative cwd), but the guard neither refuses a relative path
by name nor contains it. The r55 prereg and the builder docstring both omit it.
Where it should have landed: `main()` (`--work`/`--scratch` resolved and
compared against the scratch root, or an explicit "must be absolute" refusal)
and one named-limit line in `census/round-55/preregistration.txt`.

**S5 — C1 docstring still promises a `PRISTINE FAIL` class the counter never
emits.** Line 75 is unchanged from v3: `Exit 1: any finding (PRISTINE FAIL
included).` No code path prints `PRISTINE FAIL` in the C1 counter (C2's does,
for `FLEET-CENSUS-ABSENT`). The N1 repair corrected the *class list* paragraph,
not this sentence. The exit class itself is real and reachable (`unfiled>0`,
zero FINDING lines); the defect is that the legend implies an emitted label and
nothing — docstring, prereg, or matrix — says otherwise. Where it should have
landed: the docstring sentence rewritten (e.g. "exit 1 also covers an unfiled
site, which prints no FINDING line") or a named-limit line in the prereg.

**N6 — exit-code ambiguity still has no prereg named-limit line.** The v4 C1
Exit block is the v3 text verbatim; the r55 prereg's named-limits list has no
exit-code entry. Both classes were measured: exit 2 for an unevaluable input
(short revision) and exit 1 for a pristine fail (absent capture in C2). A
reader of the frozen prereg alone still cannot tell which of the two an exit 1
means without opening the docstring.

## 6. Additional observations (named, not edited)

- **O1 — `PTR_RE` narrows to extension-bearing tokens, but `x.md:1` still
  exempts** (disclosed in the prereg: "a pointer-shaped fake such as `x.md:1`
  still does"). Measured: F12c green, F22 red — the disclosed boundary matches
  behaviour. No action.
- **O2 — straddle summary count changes**: on `F10-STRADDLE` v4 prints
  `mismatches=1 filed=1` where v3 printed `mismatches=2 filed=2` (the
  straddling site is refused and dropped from the stated-count tally). Exit
  code and first finding are unchanged (`ZONE-TOKEN-STRADDLES-EDGE`), so the
  carry-over rule holds; the summary arithmetic differs by one site and is not
  disclosed. [INFERENCE] benign — the site is refused either way.
- **O3 — matrix finding column for a pristine fail** (see §4 residual): the
  §5.2 convention assumes every kill row has a FINDING line, which C1's
  unfiled-only failure does not.
- **O4 — fixture builder determinism** verified positively: all four matrices'
  revs reproduced, and the frozen commit dates reproduce byte-identical
  histories across a fresh build directory.

## 7. Confidence

- Instrument/fixture verdicts (items 1–9, 12–23, 26): **high** — measured
  live with the frozen bytes, both arms, and mutant kill-power for M2/M7/M11/N5.
- OPEN verdicts (S4, S5, N6): **high** — code/byte inspection plus reproduced
  behaviour; nothing in the r55 prereg or instruments contradicts them.
- §5.1 mechanism: **high** for the receipt ledger; the criterion half is
  absent by inspection, not by inference.
- §5.4: **high** — round-start receipt and a live re-run agree (61 W04, exit 0,
  no new duplicate from S278).

## 8. Write scope / hygiene

Wrote only `.ufo/waves/round-55/w1/S55revenger01/` (report + `receipts/`) and
`/fast/scratch/hyaku/souji-r55/S55revenger01/` (deleted before yield). No lane
file, no fleet file, no sibling seat, no `.ufo/state/`, no `watchdog.log`.
No commits, no pushes, no mutating git/jj outside scratch fixture clones.
