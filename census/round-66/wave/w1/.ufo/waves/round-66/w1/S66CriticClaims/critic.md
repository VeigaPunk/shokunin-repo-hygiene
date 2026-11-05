# S66CriticClaims — round 66 (souji, attempt 2) critic findings

Read-only seat. Read: MISSION.md, AXES.md, corpus/QUALITY.md (Q59, Q112, Q120–Q127), census/round-66/preregistration-attempt2.txt (freeze 02cc6609), controls/c1-do-nothing.txt, controls/c2-do-nothing.txt, corpus/lessons/round-65.md, corpus/lessons/round-65-verifier-spotcheck.md, the frozen instruments and population (c1-counter.py, c1-matrix.tsv, c2-counter.py, c2-statements.tsv, c2-mutate.py), and base writer tools/souji-receipt-write.py (045e103). Scratch under /fast/scratch/hyaku/souji-r66/S66CriticClaims, removed. No lane file, no git mutation, no install.

Candidate state at this seat: no commit touches tools/ after 045e103 (HEAD 02cc6609); `.ufo/waves/round-66/w1/S66ExecWriter/CANDIDATE-READY` absent. Every verdict below is on the frozen predicates as written; where a verdict depends on the candidate, it says so.

## 0. Measured in this seat

Writer-level probes, base writer (sha256 6be46a05…, = blob at 045e103), scratch lane with the instrument committed at its rev. None uses --allow-dirty.

| id | setup | rc | receipt |
|---|---|---|---|
| W0 | clean tree, no env | 0 | written |
| W1 | tracked tools/tool.sh committed 755, worktree 644 (uncommitted) | 2 `lane worktree is dirty` | not written |
| W2 | W1 tree + `GIT_COMMON_DIR=<copy of .git whose config sets core.fileMode=false>` | 0 | written |
| W3 | clean tree, `GIT_CONFIG_PARAMETERS` set by a `git -c foo.bar=1` alias child | 0 | written |
| W4 | clean tree, `GIT_CONFIG_GLOBAL=<empty file>` | 0 | written |

- Control for W2 (git level): same W1 tree with the copied config lacking the key → `git status --porcelain` 1 line; with the key → 0 lines. The common-dir config key is the cause.
- P-B (pre-run, no env): tracked file committed 100644, `chmod 4644` → `git status --porcelain` 0 lines; `stat` 4644; `ls-files -s` 100644. The start-of-run check cannot see the setuid bit.
- Kill-power (M-ENV = c2-mutate.py recipe on the base writer; lines 278–280 removed, mutant compiles): r66 counter markers `env=0` (flag/inrun/unmerged 1; envcfg/envred 0); r65 counter markers `env=1`. Scoring SKILL row s2 `closed_full` with S2_AFTER present: r66 → `FINDING SCOPE-OVERREACH s2` (findings=1); r65 → no finding. This reproduces the prereg's kill target, conditional on the candidate SKILL.md carrying the S2_AFTER literal (not yet landed).
- Matrix: 28 rows (verified). Base forgeries 8 = E1–E6, MOD2, MOD3 (control). Base honest accepts 5 = A, B, T4, V2, SY1. SY3 is refused by base (not a forgery).
- Byte checks: the Target and Kill lines of attempt 1 and attempt 2 are identical; a full diff of the two prereg files touches only the preamble (lines 3 and 10–19). Blob at freeze equals blob at a strict ancestor for both controls: C1 `7c0fd032…` at 10d175a5, 4864c01f, 02cc6609; C2 `e8b1fd1b…` at 4864c01f and 02cc6609. The C2 control differs from its headerless predecessor only by a 4-line header (`diff`: `0a1,4`). Instrument blobs identical at 4576f101 and 02cc6609: c1-counter `273d6fc9…`, c2-counter `ac2157e6…`, c2-statements `c41b0bc4…`, matrix `2a8dab05…`.

## 1. Routed round-65 items (question 1)

| r65 item | round 66 | reason / evidence |
|---|---|---|
| Routed 1: ignore routes and GIT_CONFIG_* behaviour fix, with do-nothing (sentinel F1–F3, scribe B–E) | Partly | E1–E3 (GIT_CONFIG_COUNT, GIT_CONFIG_PARAMETERS, GIT_CONFIG_GLOBAL) covered. Ignore routes (.git/info/exclude, tracked .gitignore, repo core.excludesFile) are declared outside C1 (L1). refs/replace (F3) has no matrix row; only the GIT_NO_REPLACE_OBJECTS pin is described (L2 text). **GIT_COMMON_DIR (W2) is open at base, has no row, and is absent from the candidate design text** (c1-counter.py docstring lines 29–34). |
| Routed 2: redact env value in RECEIPT-INDEX-ENV-SET (F4) | Routed again, no reason | No predicate. c1 class check is a stderr substring (`findings_for`, lines 516–519), so a leaked value cannot fail anything. The candidate docstring promises "name, never print" (lines 33–34); unmeasured. |
| Routed 3: fixture isolation of GIT_CONFIG_GLOBAL/NOSYSTEM in clean_env (F6) | Routed again, no reason | clean_env (lines 313–323) removes the variables from the environment but does not point them at devnull; HOME is not scrubbed. This host has `~/.config/git/config` (1620 B). [INFERENCE: git reads it for every fixture git call under git-config precedence; not separately probed.] |
| Routed 4: `:(top)` code-kind row (operator L0) | Routed again, operator-owned | Outside both claims. Acceptable. |
| Routed 5: env redirects E4–E6 with do-nothing | Covered | E4, E5, E6 rows; base accepts all three in the control. GIT_COMMON_DIR not covered (see 1). |
| Routed 6: dead-token falsifier for refusal lines (`if False:`) | Partly | M10 `returncode` case repaired by RETURN_LITERAL; the `if False:` shape is not tested. Named as L4 with a reason. |
| M10 (C2 `return` substring matches `returncode`) | Covered, single witness | Repair lives in a new counter (see 5). |
| M11 (same-content symlink retarget row with do-nothing control) | Partly | SY3 added, but base already refuses it (c1-counter docstring line 55: "not a base forgery"). The do-nothing arm cannot fail on it. Kill power against a read-through-hasher mutant is not measured by anything in round 66. |
| M12 (setuid, setgid, sticky with do-nothing) | Partly | MOD2 (setuid) and MOD3 (sticky) covered. **No setgid row.** Pre-run setuid change invisible to porcelain and to the start-of-run check (P-B); claim wording is in-run only, and this is not named. |
| r65 reviewer design #2 (N4 dual-seed masks instrument resolution, MEDIUM; "routed round 66 with a non-dual row") | Routed again, no reason | No such row in c1-matrix.tsv. |
| r65 reviewer C2 F3 (TSV pin digest-strong, not anti-launder, MEDIUM) | Not covered | Digest only; no reason given. |
| r65 reviewer C2 F1 (one-line docstring co-location, HIGH) and F5 counter excerpt bound (LOW) | F1 named (L4); F5 not covered | L4 covers the lexical class. |
| M9 (C2 checks marker presence, not statement breadth) | **Not named** | s5 has the same defect (see 3, item 5). Not among L1–L5. |
| M8 (Q59 MACHINE BLOCK) | Partly | Block added; the Q59 instrument has not been run on this prereg by this seat (its R4 is weak, see 3, item 9). |

## 2. Separability (question 2): NOT separable

- c2-statements.tsv row s5 (`env_closed`) requires the needles `RECEIPT-ENV-CONFIG-SET` and `RECEIPT-ENV-REDIRECT-SET` live on refuse(/return lines of the writer at `--rev`. The base writer contains zero `RECEIPT-ENV` occurrences (grep), and base SKILL.md contains none. The C2 do-nothing red (`GOVERNED-STATEMENT-UNRESOLVED s5`) is exactly this.
- s2 `closed_full` also reads the env marker from the writer at `--rev`; the M-ENV kill target runs on the measured writer.
- Therefore C2's verdict is a function of the C1 candidate's bytes. C1 does not depend on C2 (c1-counter.py has zero references to SKILL; its inputs are the matrix, the writer and the regress fixture).
- AXES.md line 31: "Claims must be causally separable — each verifiable without the others having landed." C2 fails that rule as written. The round-65 lesson recorded the same finding as NOT SEPARABLE; round 66's L1–L5 do not carry it.
- Named limit the prereg needs if both claims are kept: "C2's s2/s5 rows and the M-ENV target read the C1 candidate's refusal needles; C2 is not verifiable against any other writer."

## 3. Universal clauses (question 3)

| # | clause (where) | what enumerates or measures it | verdict |
|---|---|---|---|
| 1 | "refuses the caller-injected config and object-redirect environment routes" (C1 claim) | Enumerate E1–E6 only. Not complete: **GIT_COMMON_DIR open at base (W2)**; GIT_CONFIG_KEY_n/VALUE_n presence has no row although the docstring says the candidate will refuse it; GIT_CONFIG_SYSTEM is only pinned by NOSYSTEM, with no row. | Unprovable as worded. Only E1–E6 are measured. |
| 2 | "records the full permission bits (setuid, setgid and sticky included)" (C1 claim) | Enumerate MOD2 and MOD3. **setgid has no row.** The tool's R4 word list does not contain "full". | Would-reject as worded (setgid unmeasured). Would-admit if narrowed to setuid and sticky. |
| 3 | "refuses a same-content symlink retarget" (C1 claim) | SY3 only (singular). Base already refuses it: the snapshot records `os.readlink` bytes, so any retarget changes the recorded string. The "same-content" qualifier is not what the snapshot tests. A same-string, different-content case is not measured [INFERENCE on behaviour; not probed]. | Would-admit as "unchanged"; not an operability improvement. |
| 4 | L3: "C1 refuses the PRESENCE of the six named variables" (prereg L3) vs E3 frozen class `lane worktree is dirty` (matrix row E3) and the c1-counter docstring (E3: repoint GIT_CONFIG_GLOBAL, not refuse) | `findings_for` returns the class only when its substring is in stderr. A presence refusal on E3 with `RECEIPT-ENV-CONFIG-SET` would give `-` → class mismatch → C1 fails. The frozen matrix therefore requires E3 to be refused by the dirty check and forbids the L3 design for E3. | Would-reject if the candidate presence-refuses GIT_CONFIG_GLOBAL with a message lacking the dirty text. The frozen text contradicts itself here; it cannot be amended after data. Must be named. |
| 5 | C2 "agrees with the writer bytes"; s5 "closed for the caller-injected config and object-redirect routes" | C2 measures needle presence on emission lines. A writer that refuses E1–E6 but leaves W2 open passes C2 with findings=0 by construction. | Would-reject if s5 keeps the universal "routes" wording while W2 is open at the measured revision. C2 cannot falsify it. Not named. |
| 6 | Preamble: "every predicate, counter, population, matrix, kill rule and target ... byte-identical to attempt 1" | Target and Kill lines identical; full diff touches only preamble lines. | Would-admit. |
| 7 | "No candidate writer, after receipt or data existed at either freeze" | No tools/ commit after 045e103; no CANDIDATE-READY. | Would-admit. |
| 8 | "the frozen 28-row matrix" | 28 rows counted. | Would-admit. |
| 9 | Q59 R4 scanner (tools/souji-axis-check.py lines 43, 124–129) | Scans only all/every/complete/none/no, and flags a block only if it has no `enumerate:` line. This block has enumerate lines, so R4 is silent for any universal, covered or not. "full", "routes", "closed" are not scanned. [INFERENCE from source; the instrument was not executed by this seat.] | R4 cannot falsify items 1–5. |

## 4. Do-nothing controls (question 4)

- **C1 control fails for the stated reason.** Base writer: 8 forgeries (E1–E6, MOD2, MOD3), class_mismatches=8, EXIT=1 (control file lines 48–70). Limits: (a) SY3 cannot fail this control (base refuses), so the discriminating set is 8 rows, not 9; (b) the control's new slot is `--new-tool /fast/scratch/hyaku/souji-r66/l1/base-writer.py`, a scratch file the L1 trap removes. The sha256 (6be46a05…) equals the base blob, so the bytes are reproducible from git, but the receipt's command is not. Recommend the record cite `git show 045e103:tools/souji-receipt-write.py`.
- **C2 control fails for the stated reason.** `GOVERNED-STATEMENT-UNRESOLVED s5`; rows=5 findings=1 verdict=FAIL; MARKERS flag=1 inrun=1 env=1 unmerged=1 envcfg=0 envred=0. But the c2-statements.tsv note for s4 says s4 is "absent from SKILL.md at base ... added with the r65 landing". Base SKILL.md contains the s4 wording (grep count 1). The note is false. It does not change any predicate; it is a false statement in a frozen file and should be disclosed.
- **Chronology.** Both controls are strictly before the attempt-2 freeze, and Q122 holds (blob equality, section 0). The C2 control was replaced after the attempt-1 freeze (5d17a5de) by a header-only edit; Q120's letter is met for attempt 2 and the prereg discloses it.
- **In-place edit in history, not disclosed as one.** Commit 01bc1e16 (subject "re-issued freeze") edited the attempt-1 file census/round-66/preregistration.txt (+8/−1: freeze-history paragraph and control hash). a81280e1 restored its blob to `becb21ba…` (= 5d17a5de). The prereg says "no in-place edit survives", which holds at HEAD but does not name 01bc1e16 as an in-place edit of a frozen file, and the commit subject mislabels it. Would-reject if a reviewer treats 01bc1e16 as a frozen-file amendment. Route to the lesson as a mistake.

## 5. M10 repair: new counter, not an amendment (question 5)

- The round-65 counter (census/round-65/c2-counter.py) last changed at 2761f0aa (round 65) and is untouched. The round-66 counter is a new file at a new path, pinned by tsv-rev 4576f101. That is a new counter at a new frozen revision, which is the correct form under the no-amendment rule.
- But the repair changes a predicate clause (emission path = `refuse(` or `return` followed by a string literal; RETURN_LITERAL lines 110–120) and only one side is tested:
  - (a) A refusal emitted as `return <name>`, `return b"..."`, or a multi-line `refuse(` whose needle sits on a continuation line reads dead → false C2 FAIL on a correct writer. Q53 requires every changed clause to have an executed mutant or a named equivalent; none exists. The base writer is fine (all four markers 1 under the repaired counter). Would-reject if the candidate uses such a shape: the counter would then refuse a correct writer.
  - (b) The only kill witness is the mutant that motivated the repair (round-65 M10, m4 = deleting the env refusal = M-ENV). Single witness, tuned on it. Q52/Q53's minimum (run against base and observed to discriminate) is met: r65 env=1 vs r66 env=0 on M-ENV. Generality is not.
  - (c) c2-mutate.py anchors on the exact line `if "GIT_INDEX_FILE" in os.environ:` (must occur once) and deletes a 3-line block. If the candidate restructures the N3 block, the recipe exits 2 and the kill target cannot be scored. [INFERENCE on candidate shape.]

## 6. Honest-row set (question 6): 5 is NOT the full honest population for the claimed routes

- W3: `GIT_CONFIG_PARAMETERS` reaches a writer launched under `git -c` (base rc 0, receipt written). The candidate design (c1-counter docstring lines 29–30) presence-refuses GIT_CONFIG_PARAMETERS. Any writer launched under a git `-c` alias or hook is then refused. None of A, B, T4, V2, SY1 sets a GIT_* variable.
- W4: a benign `GIT_CONFIG_GLOBAL` is accepted at base; the candidate design silently repoints it. No honest row with a user global config.
- L2 cost (named): honest lanes whose host-global excludes hide untracked files become dirty. On this host the global config (key names only) has no core.excludesFile, so this host cannot show the cost, and no honest row exercises it. "No axis harmed" (AXES.md) is therefore unprovable for C1.
- P-B: a tree with a setuid-only tracked change is accepted and not named.
- [INFERENCE, not probed] git sets GIT_OBJECT_DIRECTORY and GIT_ALTERNATE_OBJECT_DIRECTORIES in quarantine hooks; E4 and E5 would refuse those honest runs.

## 7. Verdict per claim

**C1 operability: unprovable as worded.** Would-admit only if: (i) the claim is narrowed to the enumerated E1–E6 and to setuid and sticky (or a setgid row is added); (ii) the E3 class is reconciled with L3; (iii) GIT_COMMON_DIR (W2), pre-run setuid (P-B) and the honest-row gaps (W3, W4, L2) are named.
- Single falsifier: W2. `GIT_COMMON_DIR` carrying `core.fileMode=false` makes the base writer accept a tracked mode change (rc 0, receipt written). "Routes" is universal and this route is open at base; a candidate that leaves it open makes the claim false as worded.
- Would-reject-if the candidate presence-refuses GIT_CONFIG_GLOBAL with a message lacking the dirty text (E3 class mismatch), or leaves W2 open.

**C2 calibration: would-reject.**
- (i) Not separable from C1 (AXES.md line 31), and not named.
- (ii) s5's universal "routes" wording is not falsifiable by C2.
- Single falsifier: a writer that refuses E1–E6 but leaves GIT_COMMON_DIR open scores findings=0 on the frozen counter while the s5 wording is false.
- The M-ENV kill itself: would-admit conditionally. Reproduced here: r66 env=0 → SCOPE-OVERREACH s2; r65 env=1 → no finding. Conditions: S2_AFTER literal present in the candidate SKILL.md, and the c2-mutate.py anchor present in the candidate writer.

**Smallest safe correction (no frozen-file edit; predicate changes after data are not this round's rule).** Name in the round report and lesson, before scoring the candidate: (1) GIT_COMMON_DIR route open (W2) and the "routes" universal; (2) setgid unmeasured; (3) E3 class vs L3 contradiction; (4) C2 not separable from C1; (5) s5 breadth (M9 class); (6) honest-row gaps W3, W4, L2, P-B; (7) 01bc1e16 in-place edit of the frozen attempt-1 file, disclosed as such; (8) stale s4 note in c2-statements.tsv; (9) control's scratch new-slot path; (10) Q59 R4 blind to "full" and to covered-by-enumerate universals. L1 should decide these before the candidate is scored; the Q59 instrument should be run by L1 on this prereg, not inferred from source.

No tool was installed. Scratch removed.
