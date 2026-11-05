# S65MutKill — round 65 wave w1: kill-power, C2 live read, mode polarity

Seat: S65MutKill (leaf, no subagents). Scratch removed before yield. Deliver: `.ufo/waves/round-65/w1/S65MutKill/`.
Writer under test: landed `tools/souji-receipt-write.py` at 16da2445…, blob sha256 `be344a7d…` (identical at 40a371d8…; verified by `git show | sha256sum`). Base blob at 4a43a4d9…: `9fb55f35…`. C1 counter sha256 `6401b35d…` (frozen); C2 counter sha256 `afd4cb54…` (verified).
Lane master at my reads: `ef00ac57…` (moved since round start; my measurements bind 4a43a4d9 / 40a371d8, unaffected). Lane untouched by this seat; only pre-existing untracked `census/round-65/records/` present.
Installs: none.

## 1. Pristine reproduction (post-freeze, frozen predicates unchanged)

| Check | Target | Reproduced |
|---|---|---|
| C1 `SUMMARY` | matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS, EXIT=0 | **matches** (`mutants/` … `pristine.c1.out`, receipt `pristine.c1.receipt`) |
| C2 `SUMMARY` | rows=4 findings=0 verdict=PASS, EXIT=0 @40a371d8 | **matches** (`pristine.c2.out`) |

## 2. Mutant kill table (C1 counter, `--new-tool` each mutant, `--base-rev 4a43a4d9…`, `--work` scratch)

Each run prints the mutant's `sha256` in its `# slot new=` line; receipts in `mutants/`. Diffs vs landed bytes: `mutants/<m>.diff`; sha list: `mutants/SHA256SUMS.txt`.

| Mutant | sha256 (prefix) | new_forgeries | new_honest | class_mismatches | Rows that flip | Verdict |
|---|---|---|---|---|---|---|
| m1 (literal: remove the two pre-run overrides, L136 `_status_z` + L333 dirty check; post-run L435 kept) | `73a91b79…` | 0 | **4** | 1 | V1: refuse with `RECEIPT-STATE-CHANGED-DURING-RUN` instead of `lane worktree is dirty` (class-only kill); SY1 (honest): now refuses `RECEIPT-STATE-CHANGED-DURING-RUN` | killed (class + honest over-refusal) |
| m1x (remove all three overrides, L136/L333/L435) | `61765529…` | **1** | 5 | 1 | V1: accept (hidden untracked file, forgery) | **killed** |
| m2 (`_snapshot_entry` returns digest without mode prefix) | `a7125ebc…` | **1** | 5 | 1 | MOD: accept | **killed**; honest B, T4, V2, SY1 still pass (no over-refusal) |
| **m3** (symlink read-through: drop `islink` branch, hash target) | `df22e16f…` | **0** | 5 | **0** | none: SY2 still refuses (its retarget changes the target's bytes, so read-through still sees it) | **SURVIVES the frozen matrix** → HIGH coverage gap; see §3 |
| m4 (remove GIT_INDEX_FILE refusal, L276–278) | `dba55cc1…` | **2** | 5 | 2 | N3 and P13: accept | **killed** |
| m5 (`if False:` wrap of the env refusal, line kept) | `b9a8efea…` | **2** | 5 | 2 | N3 and P13: accept (behavioral kill) | **C1 kills**; C2 passes (§4, polarity pair) |

Every mutant C1 outcome is the frozen-claim failure set; no honest row beyond m1's SY1 was disturbed.

Void run (recorded, not counted): a background run of `m1x` executed before my edit had landed on that copy (edit errored); its output is renamed `mutants/VOID-m1x-unedited-bgrun.c1.*` and not used.

## 3. m3 survivor and follow-up probe (HIGH, coverage)

Frozen matrix: SY2 retargets the symlink to `../instr.sh`, whose bytes differ from `../notes.txt`, so the content digest changes under *both* record-by-target (landed) and read-through (m3). The matrix therefore cannot distinguish the two.

Follow-up (outside the frozen matrix, `mutants/m3probe.sh`, output `m3probe-*.out`): untracked symlink `tools/extra/link` → `../notes.txt`; retarget in-run to `../copy.txt`, a byte-identical untracked copy; `--allow-dirty`.
- landed: `refused: RECEIPT-STATE-CHANGED-DURING-RUN: content tools/extra/link changed during the wrapped command; no receipt written` (rc=2).
- m3: rc=0, receipt written. **Forgery** — the mutant is killed by a same-content retarget, which the frozen matrix lacks.

Recommendation to L1/judge: a same-content retarget row would kill read-through. Not amending the frozen predicate here.

## 4. C2 live-marker read and polarity pair (HIGH, kill-power)

Named limit (frozen): an `if False:` refusal keeps its live line and is the C1 matrix's kill. Measured:
- m5 (`if False:` wrap): live markers `flag=1 inrun=1 env=1 unmerged=1`, C2 findings=0. Limit holds as named. C1 kills behaviorally (N3, P13 forgeries). **Polarity pair: C1 kills, C2 passes.**

**Unnamed hole (HIGH):** the emission token `return` is a bare substring match. The landed writer's own self-test has `if r.returncode != 2 or os.path.exists(out3) or "RECEIPT-INDEX-ENV-SET" not in r.stderr:` at **L1127** (`returncode` contains `return`). So the env needle is "live" from a test line, independent of the real refusal at L276–278.
- m4 (env refusal deleted outright): markers `env=1`, C2 **findings=0 → PASS**. C2 does not catch deletion of the env refusal; C1 does (N3, P13).
- The frozen predicate is literal (`uncommented line carrying refuse( or return`), so the counter did what its predicate says; the defect is the substring token. I did not amend it. Evidence: `c2-polarity.txt`.
- Recommended fix for L1 (not applied): match `return` as a word/statement token (e.g. `return ` / `return(`), or require `refuse(` or a return statement on the same line; then re-pin.

## 5. Mode-polarity battery (landed writer, `--allow-dirty`, in-run change)

Fixture: tracked `tools/notes.txt` dirty (appended `dirty`), `tools/instr.sh` committed and clean. Raw outputs: `mode-matrix.txt`, `mode-*.out`.

Hypothesis: "the mode payload catches EVERY in-run mode change on a snapshotted dirty file."

| Arm | Result | Reading |
|---|---|---|
| 644 → 0600 | rc=2 `RECEIPT-STATE-CHANGED-DURING-RUN: mode tools/notes.txt` | holds |
| 644 → 0444 | rc=2, same `mode tools/notes.txt` row | holds |
| 644 → 0755 | rc=2, same `mode tools/notes.txt` row | holds |
| 644 → 4755 | rc=2, same `mode tools/notes.txt` row | holds (low bits changed) |
| 755 → 4755 (setuid only) | **rc=0, receipt written** | **falsifies "every in-run mode change"** |
| 644 → 4644 (setuid only) | **rc=0, receipt written** | **falsifies** |
| in-run `os.chown(…, 0, 0)` on dirty file (uid 1000, no sudo) | rc=1 (`PermissionError: Operation not permitted`), receipt written with `EXIT=1`, no state change | EPERM, no state change; nothing to refuse |
| boundary, clean tracked file, no `--allow-dirty`: 644 → 0600 | rc=0, accept | not snapshotted; porcelain blind to non-exec bits |
| boundary, clean tracked file, no `--allow-dirty`: 644 → 0755 | rc=2 `RECEIPT-STATE-CHANGED-DURING-RUN: worktree status … changed` | porcelain catches exec bit |
| boundary, clean tracked file, `--allow-dirty`: 644 → 0600 | rc=0, accept | same blind spot |
| boundary, clean tracked file, `--allow-dirty`: 644 → 0755 | rc=2 `worktree status … and content tools/clean.txt changed` | caught |

Cause of the setuid miss (verified at L161): `_snapshot_entry` records `oct(st_mode & 0o777)`, dropping setuid/setgid/sticky. Git does not track those bits either, so porcelain is blind too.

Reading: the four frozen-target arms support the hypothesis. The unqualified claim "every in-run mode change" is false (setuid/setgid/sticky, and the non-exec clean-file boundary, are invisible). Recorded HIGH against the claim wording; the frozen C1 matrix does not cover it.

## 6. Findings, by severity

1. **HIGH — C2 live read defeated by self-test text.** `return` substring matches `returncode` at landed L1127; m4 (env refusal deleted) passes C2 (`findings=0`). Kill-power gap for the C2 claim. (§4)
2. **HIGH — frozen C1 matrix does not kill read-through symlink hashing.** m3 survives; a same-content retarget kills it. (§3)
3. **HIGH — mode claim wording.** "Every in-run mode change" is false for setuid/setgid/sticky (mask at L161). Writer gap, not a matrix gap. (§5)
4. **MEDIUM — partial override removal yields honest over-refusal (m1).** Dropping only the pre-run overrides makes honest SY1 refuse, so the three override reads must stay consistent. Landed writer is consistent; a guard row would protect this. (§2)
5. Named-limit consistency: m5's C1 kill and C2 pass match the frozen named limit exactly. (§4)

Not done (out of this seat's scope): SOURCES/S297 opening, knowledge/lesson drafts, scope audit, sibling overlap. No SOURCES row opened by this seat.

## 7. Artifacts (deliver dir `.ufo/waves/round-65/w1/S65MutKill/`)

- `pristine.c1.out` / `.receipt`, `pristine.c2.out`
- `mutants/` — per-mutant `*.c1.out` / `*.c1.receipt`, `*.diff` vs landed, `SHA256SUMS.txt`, `m3probe.sh`, `modematrix.sh`, `VOID-m1x-unedited-bgrun.*` (void)
- `mode-matrix.txt` plus `mode-*.out` (raw arm outputs), `m3probe-landed.out`, `m3probe-m3.out`
- `c2-polarity.txt`
