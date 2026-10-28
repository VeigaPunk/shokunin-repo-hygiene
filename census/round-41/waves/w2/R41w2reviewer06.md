# R41w2reviewer06 — audit of `corpus/lessons/round-41.md` § Mistakes and § Named limits

Seat: R41w2reviewer06 (reviewer, leaf, wave 2). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Lesson read at tip `1d41c13574db80fdd9a4bde490b712da7ce2a85f` (`git show 1d41c13…:corpus/lessons/round-41.md` is byte-identical to the working file; `git status --short` empty). No commit, push, or mutating git/jj command run; no tool installed or upgraded; no subagent dispatched. Scratch: `/fast/scratch/hyaku/souji-r41/R41w2reviewer06/` (deleted before yield; receipts copied into this seat directory).

## Verdict

**NOT CLEAN.** The failures the two sections describe reproduce from committed bytes (C3 candidate invocation counts, the C2 do-nothing controls, the dead-seat error-text absence, the landing-gate blind spot, the K1/S146 registry red). But the sections also carry phantom citations, a wrong figure, a miscount, two misattributions, one false "only" claim, and one unanchored compensating check. Calibration-wise the lesson overstates its own evidence in those places and should be corrected (append-only addendum) before admission.

Defects, most serious first:

1. **Phantom QUALITY ids.** The lesson cites `QUALITY Q98` (line 35), `QUALITY Q99` (line 106), and `QUALITY Q100` (lines 135 and 143) as committed records of rules. `corpus/QUALITY.md` has no such entries: `git grep -n -E '\bQ(98|99|100)\b' 1d41c13…` matches only the lesson itself; the highest id at tip and at `bffcc0f` is `Q97`. Five citations, three ids, zero committed targets.
2. **Wrong figure.** M41-1 says the sweep `grep -n -iE 'freez|frozen|pre-?data|population|preregist' corpus/QUALITY.md` gives "27 lines". It gives **25** at `bffcc0f` and at `1d41c13` (case-sensitive: 23).
3. **Miscount.** M41-3: "R41critic01 built eight lessons the frozen C1 counter scored green". A7 is the control that scored `exit 1` (`corrected=2 uncorrected=1 junk=1 sourced=0`, critic01 table row A7). Seven scored green (A1–A6, A8).
4. **Misattribution (NOT OPENED).** M41-3 credits "a registry row that says 'NOT OPENED' (A1, A8)". A8 is a fenced `S258` row inside a ```` ```text ```` block; only A1 is the NOT OPENED placeholder (critic01 table rows A1, A8; N2 in the lesson itself gets this right).
5. **Misattribution (K5).** M41-3 credits "R41critic02 K2/K4/K5: a quote-less S258 row and a rewritten S033 row". K2 and K4 match; K5 is the junk-check gap for the `source=` token of an I1 line (critic02 line 15, K5a/K5b), which is N3, not either row case.
6. **False "only".** M41-2: "The only committed Codex error text in the lane is a different message (`census/round-20/recovery-seat-outcomes.json`)." `git grep -n -E 'Codex error|Invalid prompt' bffcc0f -- .` also returns `.ufo/waves/round-21/provider-error-excerpts.json:6`, `corpus/lessons/round-22.md:187`, and `census/round-26/…` and `.ufo/waves/round-26/…` copies of the round-22 lesson. The narrower claim that holds: the text `Invalid prompt` occurs in committed bytes only at `LOG.md:1909`.
7. **Unanchored compensating check.** N2: "the registry census exits 0". The only registry tool in the lane, `tools/souji-registry-agreement.py --root . --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804`, exits **1** (`K1 cited-no-row S146`, which N11 itself names). `census/round-41/records/census-before.txt` ends with `exit 0` but has no command or revision header; its rows are W04 duplicate-URL lines and the final line is `ok …/corpus/SOURCES.md`. Which census the sentence means cannot be determined from committed bytes.
8. **Receipt names the other commit.** M41-1: "the tool is absent at the freeze commit (pass=0)". The receipt `census/round-41/controls/c2-control.txt` records the absence at `6682b98…` ("Instruments commit … does not exist there"), not at freeze `e2a7431`. The claim is true at `e2a7431` (`git show e2a7431:tools/souji-freeze-check.py` → `fatal: … exists on disk, but not in 'e2a7431'`); the receipt just does not show it.
9. **Ambiguous repo for a path.** M41-2 cites `.ufo/reports/round-40/souji.md:79` without naming the repo. It is a fleet-root path (tracked in the fleet repo, not in the lane). Line 79 holds the text (verified at fleet HEAD `1d315d6f`, blob `HEAD:.ufo/reports/round-40/souji.md`).

## Item-by-item check

Legend: OK = reproduced from committed bytes or a re-run I executed; PARTIAL = part checked; NOT-CHECKED = taken from a wave report, not re-derived; FAIL = contradicted.

### § Mistakes — M41-1 (round-40 claims froze predicates, not artifacts)

| Cited item | Check run | Result |
|---|---|---|
| `census/round-40/preregistration.txt` sha256 `7218101a…b4758c` | `git show 128e412:census/round-40/preregistration.txt \| sha256sum`; same at `bffcc0f` | OK |
| "first added at `128e412`" | `git show 128e412 --stat` lists `census/round-40/preregistration.txt \| 13 +` | OK |
| `grep -n -iE 'sha256\|digest'` finds nothing | `git show 128e412:…preregistration.txt \| grep -n -iE 'sha256\|digest'` → rc=1 | OK |
| C2 quote "verifies all observed class/trigger pairs in the frozen list" | prereg line 8 | OK |
| C3 quote "the r39 base fixture" | prereg line 11 ("…survive the r39 base fixture") | OK |
| C1 quote "each anchored item line" | prereg line 5 | OK |
| Q93/Q94/Q95 "first committed at `994de3b`" | `git log -S'Q93' -- corpus/QUALITY.md` → `994de3b`; `git merge-base --is-ancestor 128e412 994de3b` → yes | OK |
| "QUALITY.md:8 ('a quote its location')" | `git show 1d41c13:corpus/QUALITY.md \| sed -n 8p` contains the phrase | OK |
| sweep "27 lines" | `grep -n -iE 'freez\|frozen\|pre-?data\|population\|preregist' corpus/QUALITY.md` → 25 (bffcc0f and tip) | **FAIL** (figure) |
| `tools/souji-axis-check.py` has no population/digest/sha256/freez match | `git show bffcc0f:tools/souji-axis-check.py \| grep -c -iE …` → 0 | OK |
| "QUALITY Q99" | `git grep -E '\bQ(98\|99\|100)\b' 1d41c13 -- .` → only the lesson | **FAIL** (phantom id) |
| C2 fix: tool `tools/souji-freeze-check.py`; 21 cases in `c2-counter.py` | `git show 1d41c13:census/round-41/c2-cases.tsv \| wc -l` → 22 (21 cases + header) | OK |
| `controls/c2-control.txt`: always-clean stub 2 of 21 pass | `SUMMARY cases=21 pass=2 fail=19 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL` | OK |
| tool absent at freeze commit (pass=0) | `git cat-file -e e2a7431:tools/souji-freeze-check.py` → fatal; receipt header names `6682b98` | OK (claim), **FAIL** (receipt cites another commit; defect 8) |

### § Mistakes — M41-2 (dead-seat error text filed with no committed occurrence)

| Cited item | Check run | Result |
|---|---|---|
| `LOG.md:1909` records the text `Codex error event: Invalid prompt: …` and "All wave evidence is captured under `census/round-40/waves/`" | `git show bffcc0f:LOG.md \| awk 'NR==1909'` | OK |
| occurrences of `flagged as potentially` under `census/round-40/waves/` = 0 (136 files) | `git ls-tree -r --name-only bffcc0f census/round-40/waves/ \| wc -l` → 136; per-file `grep -c` summed → 0 | OK |
| "lane at bffcc0f has no other carrier" (for this text) | `git grep -n 'flagged as potentially' bffcc0f -- .` → `LOG.md:1` only; `git grep 'Invalid prompt' bffcc0f` → `LOG.md:1909` only | OK |
| `census/round-40/waves/w2-results.json` holds both seats' partial outputs, no error text | `grep -c -E 'R40w2reviewer0[14]'` → 2; `grep -c 'flagged as potentially'` → 0 | OK |
| no `R40w2reviewer01`/`04` report file in `census/round-40/waves/w2/` | `git ls-tree -r --name-only bffcc0f census/round-40/waves/w2/ \| grep -E 'reviewer0[14]'` → no match (rc=1) | OK |
| `.ufo/waves/round-40/w2-run.err` empty and untracked | `stat -c %s` → 0; `git ls-files` → none; `.gitignore:1: .ufo/waves/` ignores it (gitignored, so "untracked" is true but ignored) | OK (note) |
| "the only committed Codex error text … is census/round-20/recovery-seat-outcomes.json" | `git grep -n -E 'Codex error\|Invalid prompt' bffcc0f -- .` → 4 files with "Codex error" besides LOG.md | **FAIL** (defect 6) |
| `corpus/QUALITY.md:8` should have caught it | line 8 quoted | OK |
| landing gate `status_lines=0 carry_heading=0` at bffcc0f | `python3 -B tools/souji-landing-gate.py --root <lane> --rev bffcc0f… --round 40` (run by me, scratch cwd) → `SUMMARY findings=3 … status_lines=0 carry_heading=0 checked_reports=117`, rc=1 (three `LG-DANGLING-PTR`, not mentioned by the lesson) | OK |
| fleet report `.ufo/reports/round-40/souji.md:79` | fleet repo `HEAD:.ufo/reports/round-40/souji.md` line 79 contains `Invalid prompt: your prompt was flagged as potentially violating our usage policy` | OK (defect 9: repo not named) |
| "R41scribe09" (landing gate receipt) | `.ufo/waves/round-41/w1/R41scribe09/landing-r40.txt` exists but is gitignored (`git ls-files` → none) | NOT-CHECKED against bytes beyond my own gate run above |
| I4 CORRECTION line `derived=occurrences=0` | `c1-after.txt` line for `ITEM I4 … derived=occurrences=0 corrections=1 intact=yes` | OK |

### § Mistakes — M41-3 (counter fooled by right-shaped artifacts)

| Cited item | Check run | Result |
|---|---|---|
| A1 placeholder "NOT OPENED" row, scored green | critic01 table row A1 | OK |
| A2 prose "filed statement stands" | critic01 row A2; line 60 | OK |
| A3 lines inside a code fence | critic01 row A3 | OK |
| A4 duplicates | critic01 row A4 | OK |
| A5 malformed/indented lines skip junk; A7 control | critic01 rows A5, A7 | OK |
| A6 combined | critic01 row A6 | OK |
| "eight lessons … scored green" | critic01 row A7 scores `exit 1`; green set is A1–A6, A8 | **FAIL** (defect 3) |
| "A1, A8" for NOT OPENED | critic01 row A8 is the fenced row | **FAIL** (defect 4) |
| K2 quote-less S258 row, `sourced=1` | critic02 K2 row: `SUMMARY … sourced=1`, exit 0 | OK |
| K4 rewritten S033 row, `sourced=1` | critic02 K4 row | OK |
| K5 | critic02 line 15 is the junk-check/`source=` token gap | **FAIL** as cited for the row case (defect 5); K5 itself is real |
| R41critic03 C2 candidates never run the tool | critic03 table T1–T4 (dirname, path-oracle, author/subject, fingerprint) | OK (not re-run by me) |
| R41critic04 C3 candidates never run the tool (`ZZ-MUTANT` label, `mut-S<NN>.py` name) | critic04 sniffers A–C; counter `c3-counter.py:105` writes `ZZ-MUTANT` | OK (label half re-derived; path-name half not re-run) |
| shim audit: each C3 candidate invoked the tool 21 times | see "Re-runs" R-1 below | **OK, reproduced** |
| `R41executor04` is the smallest all-target candidate | sizes: executor01 6859, 02 9714, 03 10166, **04 3725**, 05 13417, 06 11321; all six 21/21 on re-run | OK |
| QUALITY Q100 records the rule | see defect 1 | **FAIL** |
| S258 quote and snapshot "re-opened by a second seat in wave 2" | `R41w2executor06.md:11`: `PASS K3-S258-row-quote-sha … quote_occurrences=1 sha_match=True snapshot=census/round-41/sources/git-v2.56.0-builtin-worktree.c` | PARTIAL: it re-checks the committed snapshot's sha and quote; no fresh upstream fetch is shown in that line |
| "hidden-case audit" of the C2 tool in wave 2 | `grep -l -i 'hidden-case'` hits in `R41w2reviewer01/04/07/08` | NOT-CHECKED (other seats' work) |

### § Mistakes — M41-4

| Cited item | Check run | Result |
|---|---|---|
| R41reviewer03 F-I4-1 (scope: counter reads `census/round-40/waves/`, population names LOG.md) | `c1-counter.py:88` `tree_files(root, MEASURED, "census/round-40/waves/")`; `c1-items.tsv` row I4 file `LOG.md` | OK |
| R41reviewer03 F-I4-2 (unscoped `occurrences=0`) | `c1-after.txt` ITEM I4 line | OK |
| "true under `census/round-40/waves/` and false across the lane" | 0 under waves; 1 (`LOG.md:1909`) across lane | OK |

### § Named limits

| Item | Cited source | Check run | Result |
|---|---|---|---|
| N1 C1 accepts duplicates, fenced lines, retraction prose; skips malformed | critic01 A2–A6 | rows A2–A6 | OK |
| N2 substring `sourced`; "NOT OPENED"; fenced row; rewritten row passes; pure append; "registry census exits 0" | critic01 A1/A8, critic02 K2/K4 | rows; `git diff --numstat 7eebc18 1d41c13 -- corpus/SOURCES.md` → `4 0` (pure append); S258 quote: `grep -n -F` → line 255 of `census/round-41/sources/git-v2.56.0-builtin-worktree.c`, sha `af2bd523e1c8…babc`, 1541 lines | OK for quote/append; **FAIL** for "registry census exits 0" (defect 7) |
| N3 junk does not validate `source=` on I1 | critic02 K5a/K5b | line 15, 57–58 | OK |
| N4 I4 derives over `census/round-40/waves/`, population names LOG.md | reviewer03; `c1-counter.py:88`; `c1-items.tsv` | OK |
| N5 C2 legs/cases; `cand-<case>`; `*.ready` branch passes 21/21 | critic03 (legs, selection); critic06 control E | `c2-counter.py:288` `score_tool(tool, scratch, "cand")`; `:119` `os.path.join(scratch, name)`; the "`cand-`" prefix string itself was not located by grep; critic06 control E **not re-run** | PARTIAL |
| N6 C3 does not execute the tool; `mut-S<NN>.py` leak; trigger discarded | critic04 L86, L16–21 | `c3-counter.py:86` `sid, cls, probes, _trigger = line.split("\t", 3)`; `:105` `ZZ-MUTANT` | OK (trigger, label); `mut-S<NN>` NOT-CHECKED |
| N7 R1 "alone" docstring not enforced; PRIOR omits four drift fixtures | critic05 F1; critic07 | `r1-counter.py:24` "…by the r40 fixture alone"; PRIOR at `:50–52` lists six fixtures (r36, r37, r38×2, r39, r40) | OK (PRIOR set shape); four omitted fixtures NOT-CHECKED |
| N8 preregistration Targets are printed prefixes with `(exit 0)` | reviewer05 F1 | prereg lines 23, 33, 43, 52 end in `(exit 0)` | PARTIAL (the Target text verified; "no counter prints `(exit 0)`" NOT-CHECKED) |
| N9 `score-candidate.sh` takes any dest, writes through symlinks, unconfined fixtures | sentinel01 F2–F6 | `census/round-41/score-candidate.sh:27–30`: `dest` taken verbatim, `mkdir -p`, `cp "$src" "$C/$dest"`; no allowlist in the script | OK |
| N10 `souji-worktree-drift.py` follows leaf symlink in `--json` | sentinel01 F1 | not re-run | NOT-CHECKED (cited, consistent) |
| N11 pre-existing registry red `K1 cited-no-row S146` | critic07 | `python3 -B tools/souji-registry-agreement.py --root . --rev 1d41c13… --list-rev b8cb4b31…` → `K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md`, `SUMMARY k1=1 k2=0 mismatches=1`, rc=1 | OK |
| N12 each claim reachable by a partial-work control | critic06 | critic06 sizing section | OK (paraphrase: critic06 says "never executes the tool", lesson says "never executes a refusal") |
| Routed M40-12 (`backslashreplace` survives) | connector02 §2 | connector02 line 22 | OK (not re-run) |
| Routed R39-D1/D2 | connector02 §4–5 | connector02 lines 34–38 | OK |
| Routed "count-before-last-append (r38-r40)" | connector02 §6 | connector02 line 42 says r38 → r39 → r40 | OK |
| Routed "receipts naming scratch paths" | connector02 §7 | connector02 line 47 | OK |
| Routed "in-place edits of append-only artifacts (r38, r39)" | connector02 §8 | connector02 line 51 | OK |

## Re-runs (commands and observed output)

Shell prefix in all: `cd /home/vgpnk/Projects/shokunin/souji-shokunin`. Pinned tool sha: `git show 1d41c13…:tools/souji-worktree-drift.py | sha256sum` → `b2a603cf4247…`.

**R-1 — C3 committed fixture under a counting shim (landed candidate).** `git show 1d41c13…:tests/fixtures/r41-refusal-sites.py` (sha `f32022e28fe2`, equals `a1144120` and the audit's `fixture_sha`) run as `python3 -B fx.py --tool shim.py --work <dir>`, where `shim.py` appends `json(argv)` to a log and `os.execv`s `python3 -B tools/souji-worktree-drift.py`:
```
probe-P19=PASS rc=2
SUMMARY probes=21 pass=21 fail=0
tool_invocations=21   (wc -l shim.log)
```
Exit 0. The shim log lines are `["--root", …, "--record", …, "--skip-unrecorded"]`-shaped, one per probe.

**R-2 — the other five C3 candidates (uncommitted; bytes from `.ufo/waves/round-41/w1/R41executorNN/r41-refusal-sites.py`).** Same harness, per-candidate shim with the log path hard-coded (the candidates' env whitelist drops `SHIM_LOG`; my first attempt failed for that reason, not for a candidate defect):

| candidate | sha256 prefix (file) | audit `sha256=` | SUMMARY (re-run) | invocations |
|---|---|---|---|---|
| R41executor01 | 8bf040106df7 | 8bf040106df7 | probes=21 pass=21 fail=0 | 21 |
| R41executor02 | bf403b2b5a75 | bf403b2b5a75 | 21/21 | 21 |
| R41executor03 | 1020e5f28eb3 | 1020e5f28eb3 | 21/21 | 21 |
| R41executor04 | f32022e28fe2 | f32022e28fe2 | 21/21 | 21 |
| R41executor05 | 841d8562e409 | 841d8562e409 | 21/21 | 21 |
| R41executor06 | 86659db9b037 | 86659db9b037 | 21/21 | 21 |

Only executor04's bytes are committed (`git show 1d41c13:tests/fixtures/r41-refusal-sites.py`). The other five exist only as untracked files under the gitignored `.ufo/waves/`; their match to the audit is verified against those files, not against committed bytes.

**R-3 — registry tool, full revision.** `python3 -B tools/souji-registry-agreement.py --root . --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804` → `K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md` / `SUMMARY k1=1 k2=0 mismatches=1 rev=1d41c13…`, rc=1. (The short revision was rejected with `COULD-NOT-EVALUATE rev must be a full 40-hex revision`; not a finding.)

**R-4 — landing gate at bffcc0f.** `python3 -B tools/souji-landing-gate.py --root <lane> --rev bffcc0f660ff36eb8add3f61582748a7af019a5b --round 40` → `SUMMARY findings=3 checked_reg=100 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=0 status_lines=0 carry_heading=0 checked_reports=117`, rc=1. Matches R41scribe09's receipt.

**R-5 — counts.** `git show bffcc0f:corpus/QUALITY.md | grep -c -iE 'freez|frozen|pre-?data|population|preregist'` → 25; same at `1d41c13`. `git show bffcc0f:corpus/QUALITY.md | grep -o -E '\bQ[0-9]+\b' | sort -u | sort -V | tail -2` → `Q96 Q97`. `git grep -n -E '\bQ(98|99|100)\b' 1d41c13… -- .` → four lines, all in `corpus/lessons/round-41.md` (35, 106, 135, 143).

**R-6 — receipts.** `c1-after.txt`, `c2-after.txt`, `c3-after.txt`, `r1-after.txt` each end `EXIT=0`. `c3-after.txt` carries `fixture_sha=f32022e28fe2` and `tool_sha=b2a603cf4247`. `r1-after.txt` carries `prior=6/6` (`SUMMARY … prior=6/6 cases=12 tool_sha=b2a603cf4247 fixture_sha=a2880a914106`).

## Verification gaps

- N5's `cand-<case>` naming, N6's `mut-S<NN>.py` leak, N7's four omitted PRIOR fixtures, N8's "no counter prints (exit 0)", N10, and the critic06 `*.ready` control E were taken from wave reports and not re-run.
- The "hidden-case audit" and the second-seat S258 re-open are wave-2 work by other seats; this seat checked only the `R41w2executor06.md:11` line.
- `census-before.txt`'s `exit 0` is unanchored; I could not tie it to a command.

## Required corrections (append-only, before admission)

1. Replace the three phantom QUALITY ids: either add Q98–Q100 with committed text, or state in the lesson that the rules are not recorded in QUALITY and cite where they are (lines 35, 106, 135, 143).
2. M41-1: "27 lines" → "25 lines".
3. M41-3: "eight lessons … scored green" → "seven lessons scored green; A7 is the control that scored red".
4. M41-3: "NOT OPENED (A1, A8)" → "(A1)"; A8 is the fenced-row case.
5. M41-3: drop K5 from the "quote-less row / rewritten row" list; K5 belongs with N3.
6. M41-2: restrict the "only committed Codex error text" sentence to the exact text `Invalid prompt`, or list the four other committed `Codex error` carriers.
7. N2: name the census command and revision for "registry census exits 0", or remove it; the lane registry tool exits 1 at tip.
8. M41-1: cite `e2a7431` (or a receipt at that commit) for "tool absent at the freeze commit".
9. M41-2: name the fleet repo for `.ufo/reports/round-40/souji.md:79`.

## Evidence files (this seat)

Copied into `.ufo/waves/round-41/w2/R41w2reviewer06/`: `fixture.out`, `shim.log` (R-1), `ex01-out.txt`…`ex06-out.txt` and `ex01-shim.log`…`ex06-shim.log` (R-2), `reg.out` (R-3), `gate.out` (R-4). Scratch deleted after copying.

## Tool installs

None.
