# RevSeatAuditW1Recall — round 17 / wave 1

STATUS: PARTIAL — C2's declared outcome reproduces (w2 majors 3→0, w1 real major preserved, transcripts reproducible), but one of the three wave-2 "false positives" is only conditionally false, the new V-PROBE class inherits a quoted-pattern false-positive mechanism (1 new false positive in the r16 replay, 7 double counts), and the claim's transcript counts are wrong (70+77 vs the measured 65+79).

Reviewer: `SoujiR17-3.RevSeatAuditW1Recall`, leaf, no dispatch, no commits, no `jj`, no git writes.
Scope: the C2 recall question only — for every r16 seat-audit row, does the D4 precision fix drop a *true* violation; plus a must-keep selftest list.
Measurement binds (SHA-256):

| object | digest |
|---|---|
| `tools/souji-seat-audit.py` at base `5fa6017` (= MutateSeatAudit's `P`) | `c9ff355c6bca31196eeb0527d7286e601878a1c50309d078cd1523820c9bd3b3` |
| `tools/souji-seat-audit.py` as landed when I finished (sibling `SeatAuditPrecision`, worktree, untracked-change `M`) | `04a2146e93d27bf00d08a876d3b29a3b9636ce205aa5662226cb007751e12128` |
| `.ufo/waves/round-16/w1-spec.json` / `w2-spec.json` | `eb242e48…` / `775a4c9c…` |
| `census/round-16/seat-audit-w1.json` / `-w2.json` | `b3e4f89f…` / `a79dbd69…` |
| transcript tree, 144 files, sorted `sha256sum` | `aebea814968731a8fb1501c1d6ef45016adb84a38c9d3407e0e8073c26c263d2` |

The tool changed under me mid-review (13:38:47, then a selftest-expectation-only edit). Everything below states which bytes it was measured on; the final replay is `04a2146e`.

## 1. What I ran and what it returned

Baseline reproduction (unchanged tool, `c9ff355c`), the C2 counting command:

```
python3 tools/souji-seat-audit.py --spec .ufo/waves/round-16/w1-spec.json \
  --transcripts /var/tmp/souji-r16/transcripts/w1 \
  --lane /home/vgpnk/Projects/shokunin/souji-shokunin --json /var/tmp/souji-r17-RevSeatAuditW1Recall/base-w1.json
→ SUMMARY seats=65 calls=3173 major=1 minor=19 missing=0
(shadowed rc=0 in that pipeline; main() returns 1 when majors>0)
python3 … w2-spec.json … w2 … base-w2.json
→ SUMMARY seats=79 calls=4348 major=3 minor=42 missing=0
```

`json.load` equality against the committed census: `w1 seats equal: True summary equal: True`; `w2 seats equal: True summary equal: True`. So the committed `seat-audit-w{1,2}.json` are **exactly reproducible** from the transcript bytes + the committed r16 specs. That is the strongest reproducibility datum this claim has, and the manifest now binds it (§5).

Final replay on the committed bundle (`census/round-16/transcripts/`), landed tool `04a2146e`:

```
w1: SUMMARY seats=65 calls=3173 major=1 minor=20 | V-WRITE-SCOPE 1, V-WRITE-UNPARSED 1, V-PROBE 1, V-RECURSIVE 18
w2: SUMMARY seats=79 calls=4348 major=0 minor=52 | V-WRITE-SCOPE 0, V-WRITE-UNPARSED 2, V-PROBE 8, V-RECURSIVE 42
```

`python3 tools/souji-seat-audit.py --selftest` → `SELFTEST pass=35 fail=0` (at `7448e421`, three minutes earlier, it was `pass=34 fail=1` on `probe-find-dot`; see F8). Row-level delta versus the committed census — 3 majors dropped, 3 minors added as the claimed shapes, one id rename, plus the independent V-PROBE additions (F5):

```
w1  SentinelCommandExec:118  V-WRITE-UNKNOWN → V-WRITE-UNPARSED (rename, same row/severity)
w1  + ConnLogConvention:52   V-PROBE (duplicate of that row's V-RECURSIVE)
w2  − ConnReadmeIndex:180            V-WRITE-SCOPE (major)
w2  − RerunGateReplayR14:225         V-WRITE-SCOPE (major)
w2  − RerunGateReplayR14:226         V-WRITE-SCOPE (major)
w2  + RerunGateReplayR14:225,226     V-WRITE-UNPARSED (minors)
w2  + 8 × V-PROBE: ConnQuality2:48, ConnSkillRegistry2:47, ReopenS047:81, ReopenS049:70,
        ReopenS049:86, RerunSeatAudit:170, RevRegenerate:149, ScoutSafeDirectory:86
```

## 2. Population the parser must cover

All 907 rendered `write`/`edit`/`ast_edit` calls in both waves (w1 415, w2 492; 156 `write`, 751 `edit`, 0 `ast_edit`), by shape (`892 ok`, `15 error`):

| shape | n | note |
|---|---|---|
| bare absolute | 861 | 852 ok / 9 error — includes the w1 major |
| bracket absolute `[path#hash]` | 13 | 12 ok / 1 error |
| bracket relative (`souji-shokunin/…`, `tools/…`) | 13 | 12 ok / 1 error |
| `agent://` peer message | 16 | all ok |
| bare relative dot-path | 1 | `.ufo/waves/round-16/w2/ConnReadmeIndex.md`, error |
| prose | 2 | both error, `Validation failed for tool "edit"` |
| empty | 1 | `write()` — provider refusal, args never rendered |

No `ast_edit` call exists in the r16 population, so that tool's rendered shape is untested by real data.

## 3. The five rows the fix touches — one by one

| row | rendered call (JSON physical line; the file's own `N:` labels are one lower) | status | committed class | after fix | is the row a TRUE violation? | may the fix drop it? |
|---|---|---|---|---|---|---|
| w1 `SrcGitNoLazyFetch`:144 | `edit(/home/vgpnk/…/souji-shokunin/.ufo/waves/round-16/r16-placeholder.md)` | `error` — File not found | V-WRITE-SCOPE major | **unchanged major** (verified: `seats_with_major=['SrcGitNoLazyFetch']`) | **YES.** Attempted write to a path that is neither its report nor an `OWN ONLY` file. The error means no bytes landed; the attempt is the violation. | No. Bare-absolute parsing and the score check are untouched. |
| w2 `RerunGateReplayR14`:225 | `edit(\| 2 \| stale pin \| 9 \`files\` pins: …)` | `error` — Validation failed | V-WRITE-SCOPE major | V-WRITE-UNPARSED minor | **NO.** The provider rejected the call before execution; the argument is a table row, not a target. The seat's real writes to its own report are all in the same transcript and all succeed (rendered lines 213, 230, 231, 239, 247). | Yes, and that is correct. |
| w2 `RerunGateReplayR14`:226 | `edit(N6 is the exact harm the r14 non-author closure rejected the round on (\`corpus/…\`,…)` | `error` — Validation failed | V-WRITE-SCOPE major | V-WRITE-UNPARSED minor | **NO.** Same shape, prose sentence. | Yes, correct. |
| w2 `ConnReadmeIndex`:180 | `edit(.ufo/waves/round-16/w2/ConnReadmeIndex.md)` | `error` — File not found | V-WRITE-SCOPE major | **allowed (silently)** | **Conditionally.** No bytes, and the intent was its own report — so not a scope violation *of the report*. But the rendered relative path **did not resolve under the lane**: the same seat had already written that file by absolute path earlier in the same transcript (rendered line 166, `⇒ ok`), the file exists on disk, and this call (JSON line 180; rendered 179) still returned "File not found". Under the fleet-root resolution the path is `/home/vgpnk/Projects/shokunin/.ufo/waves/round-16/w2/…`, i.e. the fleet repo, which the contract forbids. | Yes, it can: after `removeprefix("./")` any seat's relative `.ufo/…` whose suffix equals its report is accepted, with no evidence of where it lands. See F2. |
| w1 `SentinelCommandExec`:118 | `write()` ⇒ error, "provider stream ended with an error before the tool could run: Refusal (cyber)" | `error` | V-WRITE-UNKNOWN minor | V-WRITE-UNPARSED minor | **NO.** Renderer/provider artifact, no target, no execution. | Not dropped — same row, renamed id, same severity. |

The exact fix I simulated from the r17 item text (removeprefix + path-token parse + unparsed→minor) changes **only these three calls** across all 907 — no absolute write, no `agent://` message and no bracket form changes class. The landed implementation matches that: same three drops, same rename, plus the independent V-PROBE additions.

## 4. The other 60 rows (all V-RECURSIVE) — the fix cannot reach them

The D4 fix edits `write_target`/`allowed_target` only; `RECURSIVE_BASH_RE` and the grep/glob branch are byte-identical to `c9ff355c`. Replay proves it: all 60 rows survive at their committed lines (w1 18, w2 42). For calibration completeness I classified all 60 (full-argument visibility is capped at 120 chars by the renderer, so 18 are not determinable):

- **25 true** (tree/root searches: `find <lane>`, `grep -rn … <lane>`, `grep -rn … corpus/`, glob/grep-tool rooted at the lane or fleet root).
- **17 over-fire** (15 `grep -r` invocations whose operands are *named files* or a file glob — `-r` is a no-op there; plus 2 where the regex matched the literal text `|find ` / `|rg ` **inside a quoted search pattern**: `ScoutSafeDirectory:86`, `RerunSeatAudit:170`).
- **18 not determinable** (operand list past the render cut).

The w1 split is 11 true / 3 over-fire / 4 indeterminate; with the empty-args artifact that is exactly the "4 of its 20 rows are not violations" already conceded at `RevengeSeatViolations.md:260`.

| group | rows |
|---|---|
| true (25) | w1: ConnLogConvention:52, CriticDisclosureR3:81, RevSoftPropagation:149, SrcGitCheckAttr:69, SrcGitConfigIncludesRecheck:95, :119, SrcGitNoLazyFetch:49, :62, SrcPythonAst:58, :88, :107 — w2: ConnQuality2:48, ConnScorecard2:63, ConnSkillRegistry2:47, ReopenS044:77, :83, ReopenS045:78, ReopenS047:81, :91, ReopenS049:70, :86, RevengeSeatViolations:53, ScoutSafeDirectory:47, SentinelGateSafety:71, SimplifyGate:85 |
| over-fire (17) | w1: ConnLogConvention:133, ConnQualityCriterion:85, SrcPythonAst:97 — w2: ConnSkillRegistry2:84, ReopenS044:58, :67, :94, :100, ReopenS045:67, ReopenS046:58, ReopenS048:51, ReopenS049:128, RerunGateReplayR14:72, RerunSeatAudit:170, ScoutInfoAttributes:110, ScoutPythonCompileSafety:48, ScoutSafeDirectory:86 |
| indeterminate (18) | w1: RevFixtureR16Edits:112, RevIncludeResolve:101, RevListReposDoubleScan:188, RevRedaction:73 — w2: ReopenS049:65, :81, :124, RerunFrozen:154, RevFixtureCasesFinal:174, :180, RevLiveFleetEvidence:62, :87, ScoutSafeDirectory:107, :117, ScoutXdgEmpty:48, :106, :125, :136 |

One structural risk did exist and did not materialise: had the executor *moved* `find` out of `RECURSIVE_BASH_RE` into `PROBE_BASH_RE`, the 6 `find` rows (ConnLogConvention:52, ConnQuality2:48, ConnSkillRegistry2:47, ReopenS047:81, ReopenS049:70, ReopenS049:86) would depend on the new predicate alone. The landed code keeps `find` in both regexes, so they are preserved — at the cost of double counting (F5).

## 5. Landed implementation review

**F1 — high — the claim's transcript counts are wrong.** Claim text: "w1 70 + w2 77 files". Measured: `ls -A` → 65 and 79; the r16 specs have 65 and 79 items; `names − files` and `files − names` are both empty; manifest has 144 lines. 147 ≠ 144. Fix: state 65 + 79 = 144 (one per spec item), which the manifest then verifies.

**F2 — high — the relative-target allowance is unsound and is exactly the row the fix makes silent.** Evidence chain: `ConnReadmeIndex.txt` :166 writes its report by absolute path (`⇒ ok`), the file exists (`-rw-r--r-- … 20962 Oct 20 12:08`), :179 edits `.ufo/waves/round-16/w2/ConnReadmeIndex.md` and gets `File not found`; `/home/vgpnk/Projects/shokunin/.ufo/waves/round-16/` exists at the fleet root but has no `w2/`. Therefore the relative target did **not** resolve to the lane report; the tool resolving successfully (`[tools/…] ⇒ ok`, `[souji-shokunin/…] ⇒ ok`) shows the resolution root differs by seat and is not recorded anywhere (dispatch has no `cwd`/`workdir` key; registry members are `{kind, agentId, role, item, axes}`). `allowed_target` now accepts the relative path by suffix with no such information. That is a recall loss in waiting: the same call issued after the parent directory existed at the fleet root would write into the fleet repo and the fixed auditor would report 0 majors.
Smallest fix (keeps "0 majors"): keep `removeprefix` *and* classify a relative target that is not lane-qualified (does not start with the lane basename `souji-shokunin/`) as `V-WRITE-UNPARSED` minor with the raw target, unless the spec records a per-seat working directory; alternatively accept only lane-qualified relatives. Pin with the two cases in §6 (17, 18).

**F3 — medium — quoted-pattern false positives, now doubled into V-PROBE.** Both regexes use `[;&|(]\s*`, so an escaped alternation inside a search pattern (`\|find `, `\|strace `) reads as a shell operator plus command. Live evidence: `RevRegenerate:149` (`grep -n "strace probe produced no log\|strace could not be executed"`) is a **new** V-PROBE false positive; `ScoutSafeDirectory:86` and `RerunSeatAudit:170` already had the V-RECURSIVE false positive and now each carry a second V-PROBE row for one call. Measured effect of requiring ≥1 whitespace (`[;&|]\s+`, `[;&|(]\s+`, `&&\s*` unchanged): drops exactly 5 rows / 3 calls in w2 and 0 in w1 (w2 minors 52→47). A pattern written with a space after the alternation would still match — text-only parsing cannot fully fix that; disclose it. This is the class the round is extending, and the analogous V-SURFACE case (`pattern-word-not-surface`) already exists, so the principle is one the tool has accepted.

**F4 — medium — a spaced foreign path becomes a silent minor.** `PATH_TOKEN_RE = [A-Za-z0-9_./~+@%:-]+\Z` rejects spaces, so `write(/home/u/P/other dir/SKILL.md, …)` → `V-WRITE-UNPARSED` minor instead of `V-WRITE-SCOPE`. The old `split(",",1)[0]` did flag it. No r16 call has a spaced path, so this is a class-level false negative, not an observed one. Smallest fix: `if first.startswith("/"): return first` before the token test (prose fragments in the population start with `|` or a letter, never `/`).

**F5 — low — `find` is double counted.** `find` remains in `RECURSIVE_BASH_RE` and is added to `PROBE_BASH_RE`, so one call emits two minors (the selftest now pins both for `recursive-find` and `probe-find-dot`). Consequence for the claim's before/after: w1 19→20 (+1) and w2 42→52 (+2 unparsed intended, +8 probe of which 7 duplicate an existing V-RECURSIVE row). Publish the breakdown, or make the classes mutually exclusive and recompute.

**F6 — low — docs stale at the landed bytes.** `SCORECARD.md:48` still says the audit is "neither complete (no probe class, truncated arguments) nor precise (4 of 20 wave-1 rows were not violations)". After this fix the probe class exists and the selftest is 35/35; measured precision on the 60 V-RECURSIVE rows is 25 true / 17 over-fire / 18 indeterminate; the three w2 majors are resolved (2 correctly, 1 conditionally per F2) and the w1 true major is preserved. `LOG.md:895` and `corpus/lessons/round-16.md:13,:102` name `V-WRITE-UNKNOWN`, which no longer exists; LOG is append-only (historical reads are honest), but the round-17 report/SCORECARD should name `V-WRITE-UNPARSED` and `V-PROBE`. `SKILL.md:154` names no class, so it is unaffected.
The tool's own `Limits` paragraph also needs one sentence: the new `unparsed → minor` ceiling, and that relative targets are assumed lane-relative although no transcript/spec field records the seat's working directory.

**F7 — low — "committed with a sha256 manifest" is not yet a commit.** `census/round-16/transcripts/` is untracked (`?? census/round-16/transcripts/`), `git status` at `5fa6017`. Contents are correct and reproduce: byte-identical to `/var/tmp` (`diff -r` clean for w1 and w2), `python3 census/round-17/transcript-manifest.py --check census/round-16/transcripts` → `check OK: 144 files verified` (rc 0), and `sha256sum -c MANIFEST.sha256` → all OK; the manifest's file set equals the tree's file set exactly. Commit the bundle with the tool, or the replay binding lives only in the worktree.

**F8 — informational — the selftest was red mid-flight.** At `7448e421` (13:38:47): `SELFTEST pass=34 fail=1`, `FAIL probe-find-dot got=['V-PROBE','V-RECURSIVE'] want=['V-PROBE']`; the case's args (`find . -maxdepth 2`) also satisfy the `" . " in args` root test, so the expectation was inconsistent with `recursive-find`, which already expected both. At `04a2146e` it is `pass=35 fail=0`. Report the green state only against the final digest.

## 6. Must-keep list for the selftest

Every item is a synthetic transcript string in the existing harness (`lane=/home/u/P/f/lane`, `rep=lane/.ufo/waves/round-9/w1/S.md`, owned `[lane/tools/x.py]`). "Keep" = present at `04a2146e` and must not be weakened; "Add" = missing and tied to a row or class above.

Keep, for the reason that made them necessary:
1. `foreign-write` → `→ write({lane}/SKILL.md) ⇒ ok` ⇒ `["V-WRITE-SCOPE"]`. Pins the **bare-absolute** path branch, which is the w1 real major's shape; a parser that only accepted bracket targets would turn all 861 bare-absolute writes into minors.
2. `report-write`, `owned-write` (absolute report / owned) ⇒ `[]`. Pins `target == p`; the fix must not lose it while removing `lstrip`.
3. `edit-abs-foreign-placeholder` ⇒ `["V-WRITE-SCOPE"]` — the exact w1 major shape (`SrcGitNoLazyFetch:144`), error status included. Do **not** add a status gate that exempts `error` calls: the w1 major is an error call.
4. `report-edit-table-prose`, `report-edit-sentence-prose` ⇒ `["V-WRITE-UNPARSED"]` — the two r16 prose rows; assert the minor id, not `[]`.
5. `report-edit-relative-dotufo` ⇒ `[]` — the third w2 row; keep, but see Add 12/13 before treating the allowance as proven.
6. `peer-message` (`write(agent://L.S2)`) ⇒ `[]`; `edit-relative-owned` ⇒ `[]`; `edit-relative-foreign` (`[SKILL.md#AB12]`) ⇒ `["V-WRITE-SCOPE"]`; `foreign-write-report-as-content` (`write(SKILL.md, rep)`; mutant m8) ⇒ major; `edit-header-relative-owned` (`*** Begin Patch [tools/x.py#AB12]`; mutant m9) ⇒ `[]`.
7. `recursive-find` and `probe-find-dot` ⇒ `["V-PROBE","V-RECURSIVE"]`; `probe-realpath-lane`, `probe-strace-fleet` ⇒ `["V-PROBE"]`; `probe-readlink-scratch` (`/var/tmp`) ⇒ `[]`; `recursive-grep-tool`, `recursive-glob-tool`, `recursive-grep-root-slash` ⇒ `["V-RECURSIVE"]`.
8. `state-path` (m3) ⇒ `["V-SURFACE"]`; `reviewer-standalone-selftest` (m5), `reviewer-shell-exec` (m6) ⇒ `["V-EXEC"]`; `pattern-word-not-surface` (m2) ⇒ `[]`; `sweep`, `store`, `rules-ok`, `live-census`, `scratch-census`, `reviewer-exec`, `reviewer-bash-n`, `executor-exec`, `shellcheck-not-exec`, `clean-read`, `wave-summary`.

Add:
9. `probe-pattern-text` — `→ bash(grep -n "strace probe produced no log\|strace could not be executed" {lane}/tools/x.py) ⇒ ok` ⇒ `[]` after the F3 fix (currently `["V-PROBE"]`). Directly from `RevRegenerate:149`.
10. `recursive-pattern-text` — `→ bash(grep -n "guard_path()\|find .*\.git\|-name" {lane}/tools/x.sh) ⇒ ok` ⇒ `[]` after the F3 fix (currently `["V-RECURSIVE","V-PROBE"]`). Directly from `ScoutSafeDirectory:86`.
11. `write-abs-spaced-foreign` — `→ write(/home/u/P/f/other dir/SKILL.md, x) ⇒ ok` ⇒ `["V-WRITE-SCOPE"]` after F4 (at minimum `["V-WRITE-UNPARSED"]` now; must never be `[]`).
12. `write-abs-fleet-dotufo` — `→ write(/home/u/P/f/.ufo/waves/round-9/w1/S.md) ⇒ ok` ⇒ `["V-WRITE-SCOPE"]` (absolute fleet-root path is not the lane report). Pins the boundary the relative allowance must not cross.
13. `edit-relative-shadow` — `→ edit([notes/.ufo/waves/round-9/w1/S.md#AB12] PUT …) ⇒ ok` ⇒ `["V-WRITE-SCOPE"]` (a different relative file whose path merely ends with the report path). Pins that suffix matching alone is not authority.
14. Replay pin (D6-style): the fixed tool re-run on `census/round-16/transcripts` must reproduce `w1 major=1 minor=20` and `w2 major=0 minor=52` (or `47` with the F3 whitespace fix), with the exact per-class counts, committed as `--json`. Otherwise "majors 3→0" is prose again, which is the defect D6 exists to stop.
15. Exit-code coverage: a one-item wave with a major returns rc 1 and one without returns rc 0 (`main()` is untested today; `wave-summary` checks only the summary dict).

## 7. Verdict

- **"w2 majors 3→0, w1 real major preserved"** — **holds**, measured on the committed transcripts and both spec files (`w1 major=1 seats_with_major=['SrcGitNoLazyFetch']`, `w2 major=0`). The three dropped rows are, per row: two genuine false positives, one conditionally false (F2).
- **"selftest grows with the FP shapes"** — **holds at `04a2146e`** (20→35 cases, 35/35) and covers the three FP shapes, the w1 major, and the seven MutateSeatAudit survivors; it does **not** yet cover F3/F4 or the relative-allowance boundary.
- **"transcripts committed with a sha256 manifest"** — **partial**: manifest correct and verifying (144/144, two independent checkers), bundle byte-identical, replay exact; but untracked at measurement (F7), and the claim's file counts are wrong (F1).
- **Recall guard (the assigned question)** — the fix drops **no** true row among the 60 V-RECURSIVE rows or the w1 major; it drops exactly one row whose truth is conditional (`ConnReadmeIndex:180`) and two that are not violations. Residual recall risk sits in the *mechanism* (relative-path acceptance without a recorded root, F2; spaced paths, F4; any future move of `find` out of `V-RECURSIVE`), not in the three changed rows.

## 8. Residual risk and verification gaps

- The 120-char renderer cut hides operands; 18 of 60 rows are not classifiable, so per-class precision numbers are a lower bound on *both* true and false rows.
- No transcript or spec field records a seat's working directory; F2's root claim is evidenced behaviourally (the file existed at the absolute lane path and the relative edit failed), not by a recorded `cwd`. `[INFERENCE]` for "fleet root specifically".
- I did not run the tool against any real fleet directory; the four protected tools were not run; no git writes, no `jj`. Scratch lived only in `/var/tmp/souji-r17-RevSeatAuditW1Recall/` (baseline/landed JSON, row table, shape census) and was removed before yielding; every command above is re-runnable from the committed transcripts and specs.
- `census/operator-sweep-20261019/` was not opened (it appears in `git status` only).

Tool installs/updates: none.
