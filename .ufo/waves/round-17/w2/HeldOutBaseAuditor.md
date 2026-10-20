STATUS: DONE — before/after measurement: the ddb7347 48-case severity-exact table scores base(5fa6017) 30/48, new(ddb7347) 48/48; +wave-summary 31/49 vs 49/49; 18 base failures decompose into 7 full false negatives, 2 missing-class partials, 7 class/severity mismatches (one severity flip), 1 false positive; beyond-table probes 3/7 base vs 7/7 new, with two residual gaps shared by both auditors.

# HeldOutBaseAuditor — C2 "before" measurement on the round-17 selftest shapes

Seat: `SoujiR17-3.HeldOutBaseAuditor-2` (executor lane member, leaf).
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` @ ddb7347 (base of round 5fa6017).
Wrote only this report; all execution in `/var/tmp/souji-r17-HeldOutBaseAuditor/`.

## 1. Method (exact commands)

Sources extracted read-only from the lane, imported with importlib — no lane tool executed:

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ddb7347:tools/souji-seat-audit.py > new_audit.py    # sha256 8268212db158186d…f54, 389 lines
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 5fa6017:tools/souji-seat-audit.py > base_audit.py   # sha256 c9ff355c6bca3119…3b3, 237 lines
```

Case extraction: AST-parse `new_audit.py`'s `selftest()`, compile/evaluate only its `cases = [...]` literal with `lane=/home/u/P/f/lane`, `rep=<lane>/.ufo/waves/round-9/w1/S.md`, `seat_scratch=/var/tmp/souji-r9-S/`. This yields **48** audit_seat cases (the 49th assertion, `wave-summary`, is run-level and measured separately). Each case ran against:

- base: `base_audit.audit_seat(line, role, rep, [lane/tools/x.py], lane, fleet)` — its own 6-arg signature; **no scratch parameter exists in the base**, so the case's scratch is recorded but unusable there;
- new: `new_audit.audit_seat(..., scratch=<case scratch or /var/tmp/>)`.

Comparison is **exact (class, severity) multiset** — the same predicate as new `selftest()` at `tools/souji-seat-audit.py:331` (`sorted((v["class"], v["severity"]) …)`). The base's own table compares class sets only at `tools/souji-seat-audit.py:179` (`sorted({v["class"] …})`).

```
$ python3 new_audit.py --selftest   → SELFTEST pass=49 fail=0   (rc 0)
$ python3 base_audit.py --selftest  → SELFTEST pass=20 fail=0   (rc 0; 19 audit_seat cases + wave-summary, class-only)
$ python3 run_heldout.py            → TOTALS cases=48  base=30/48  new=48/48   (rc 0)
$ python3 probe2.py                 → PROBE-TOTALS 7  base=3/7  new=7/7
```

## 2. Primary result

| measure | base 5fa6017 | new ddb7347 |
|---|---|---|
| new table, audit_seat cases, severity-exact | **30/48** | **48/48** |
| + run-level `wave-summary` | **31/49** | **49/49** |
| native `--selftest` | 20/20 (class-only, 19 cases + summary) | 49/49 (severity-exact) |

Group split of base's 18 failures:
- **reused shapes** (the base table's own 19, re-expressed with severity): 17/19 pass — the 2 failures are `recursive-find` (new V-PROBE class) and `edit-relative-foreign` (RELATIVE vs SCOPE).
- **new-only shapes** (29 cases introduced at ddb7347): base 13/29, **16 fail**.

Failure decomposition (base): 7 full false negatives (`base=[]`), 2 partials (only V-RECURSIVE emitted where V-PROBE is also required), 7 class-only mismatches, 1 class+severity flip (`h5b`, base major where expected minor), 1 false positive (`scratch-trunc-header`).

## 3. Per-case table (48 rows, generated from `heldout-results.json`)

Expected = new table; base/new = observed (class, severity); PASS means exact match with expected.

| # | case | expected | base 5fa6017 | new ddb7347 |
|---|---|---|---|---|
| 1 | `clean-read` | [] | [] PASS | [] PASS |
| 2 | `report-write` | [] | [] PASS | [] PASS |
| 3 | `owned-write` | [] | [] PASS | [] PASS |
| 4 | `foreign-write` | [V-WRITE-SCOPE:major] | [V-WRITE-SCOPE:major] PASS | [V-WRITE-SCOPE:major] PASS |
| 5 | `sweep` | [V-SURFACE:major] | [V-SURFACE:major] PASS | [V-SURFACE:major] PASS |
| 6 | `store` | [V-SURFACE:major] | [V-SURFACE:major] PASS | [V-SURFACE:major] PASS |
| 7 | `rules-ok` | [] | [] PASS | [] PASS |
| 8 | `live-census` | [V-LIVE-CENSUS:major] | [V-LIVE-CENSUS:major] PASS | [V-LIVE-CENSUS:major] PASS |
| 9 | `scratch-census` | [] | [] PASS | [] PASS |
| 10 | `reviewer-exec` | [V-EXEC:major] | [V-EXEC:major] PASS | [V-EXEC:major] PASS |
| 11 | `reviewer-bash-n` | [] | [] PASS | [] PASS |
| 12 | `executor-exec` | [] | [] PASS | [] PASS |
| 13 | `recursive-find` | [V-PROBE:minor, V-RECURSIVE:minor] | [V-RECURSIVE:minor] FAIL | [V-PROBE:minor, V-RECURSIVE:minor] PASS |
| 14 | `recursive-grep-tool` | [V-RECURSIVE:minor] | [V-RECURSIVE:minor] PASS | [V-RECURSIVE:minor] PASS |
| 15 | `peer-message` | [] | [] PASS | [] PASS |
| 16 | `edit-relative-owned` | [] | [] PASS | [] PASS |
| 17 | `edit-relative-foreign` | [V-WRITE-RELATIVE:major] | [V-WRITE-SCOPE:major] FAIL | [V-WRITE-RELATIVE:major] PASS |
| 18 | `shellcheck-not-exec` | [] | [] PASS | [] PASS |
| 19 | `pattern-word-not-surface` | [] | [] PASS | [] PASS |
| 20 | `report-edit-relative-dotufo` | [V-WRITE-RELATIVE:major] | [V-WRITE-SCOPE:major] FAIL | [V-WRITE-RELATIVE:major] PASS |
| 21 | `report-edit-table-prose` | [V-WRITE-UNPARSED:minor] | [V-WRITE-SCOPE:major] FAIL | [V-WRITE-UNPARSED:minor] PASS |
| 22 | `report-edit-sentence-prose` | [V-WRITE-UNPARSED:minor] | [V-WRITE-SCOPE:major] FAIL | [V-WRITE-UNPARSED:minor] PASS |
| 23 | `edit-abs-foreign-placeholder` | [V-WRITE-SCOPE:major] | [V-WRITE-SCOPE:major] PASS | [V-WRITE-SCOPE:major] PASS |
| 24 | `state-path` | [V-SURFACE:major] | [V-SURFACE:major] PASS | [V-SURFACE:major] PASS |
| 25 | `reviewer-standalone-selftest` | [V-EXEC:major] | [V-EXEC:major] PASS | [V-EXEC:major] PASS |
| 26 | `reviewer-shell-exec` | [V-EXEC:major] | [V-EXEC:major] PASS | [V-EXEC:major] PASS |
| 27 | `foreign-write-report-as-content` | [V-WRITE-SCOPE:major] | [V-WRITE-SCOPE:major] PASS | [V-WRITE-SCOPE:major] PASS |
| 28 | `edit-header-relative-owned` | [] | [] PASS | [] PASS |
| 29 | `recursive-glob-tool` | [V-RECURSIVE:minor] | [V-RECURSIVE:minor] PASS | [V-RECURSIVE:minor] PASS |
| 30 | `recursive-grep-root-slash` | [V-RECURSIVE:minor] | [V-RECURSIVE:minor] PASS | [V-RECURSIVE:minor] PASS |
| 31 | `probe-realpath-lane` | [V-PROBE:minor] | [] FAIL | [V-PROBE:minor] PASS |
| 32 | `probe-strace-fleet` | [V-PROBE:minor] | [] FAIL | [V-PROBE:minor] PASS |
| 33 | `probe-readlink-scratch` | [] | [] PASS | [] PASS |
| 34 | `probe-find-dot` | [V-PROBE:minor, V-RECURSIVE:minor] | [V-RECURSIVE:minor] FAIL | [V-PROBE:minor, V-RECURSIVE:minor] PASS |
| 35 | `h1-rel-write-ok` | [V-WRITE-RELATIVE:major] | [V-WRITE-SCOPE:major] FAIL | [V-WRITE-RELATIVE:major] PASS |
| 36 | `h2-bare-write-ok` | [V-WRITE-RELATIVE:major] | [] FAIL | [V-WRITE-RELATIVE:major] PASS |
| 37 | `h3-trunc-foreign-abs` | [V-WRITE-SCOPE:major] | [V-WRITE-SCOPE:major] PASS | [V-WRITE-SCOPE:major] PASS |
| 38 | `h3b-trunc-header-foreign` | [V-WRITE-SCOPE:major] | [V-WRITE-SCOPE:major] PASS | [V-WRITE-SCOPE:major] PASS |
| 39 | `h4-trunc-lane-report` | [V-WRITE-UNPARSED:major] | [V-WRITE-SCOPE:major] FAIL | [V-WRITE-UNPARSED:major] PASS |
| 40 | `h5-unparsed-ok` | [V-WRITE-UNPARSED:major] | [V-WRITE-SCOPE:major] FAIL | [V-WRITE-UNPARSED:major] PASS |
| 41 | `h5b-unparsed-error` | [V-WRITE-UNPARSED:minor] | [V-WRITE-SCOPE:major] FAIL | [V-WRITE-UNPARSED:minor] PASS |
| 42 | `h6-multi-header` | [V-WRITE-SCOPE:major] | [] FAIL | [V-WRITE-SCOPE:major] PASS |
| 43 | `h7-dotdot-scratch` | [V-WRITE-SCOPE:major] | [] FAIL | [V-WRITE-SCOPE:major] PASS |
| 44 | `h8-trunc-header-rel` | [V-WRITE-RELATIVE:major] | [] FAIL | [V-WRITE-RELATIVE:major] PASS |
| 45 | `scratch-seat-write` | [] | [] PASS | [] PASS |
| 46 | `scratch-other-seat` | [V-WRITE-SCOPE:major] | [] FAIL | [V-WRITE-SCOPE:major] PASS |
| 47 | `scratch-unscoped-executor` | [] | [] PASS | [] PASS |
| 48 | `scratch-trunc-header` | [] | [V-WRITE-SCOPE:major] FAIL | [] PASS |

## 4. Findings at ddb7347

**F1 — base severity blindness is real and measurable.** `tools/souji-seat-audit.py:179` compares `sorted({v["class"] …})`; new compares `(class, severity)` at `:331`. The base's 20/20 therefore cannot see the one severity inversion in the new table: `h5b-unparsed-error` (base emits major for a failed unresolved write; expected minor). The other 17 base failures are class errors it also cannot see (class-only table asserts the old classes).

**F2 — base suffix matching is the dominant false-negative source.** `allowed_target` at `tools/souji-seat-audit.py:76-82` uses `rel = target.lstrip("./")` then `p.endswith("/" + rel)`.
- `h2-bare-write-ok` (`write(S.md)`): report `…/w1/S.md` ends with `/S.md` → **base returns []** for a fleet-root-relative attempt.
- `h8-trunc-header-rel` (`[tools/x.py#AB12] … [tools/…`): owned path ends with `/tools/x.py` → **base returns []**; new flags the truncated header V-WRITE-RELATIVE major.
- `h6-multi-header`: base's `EDIT_TARGET_RE` (`:68`) is `^`-anchored, so only the first of two headers is audited; the second header names the lane's `SKILL.md` → **base returns []**, new V-WRITE-SCOPE major.

**F3 — base blanket-allows anything starting `/var/tmp/`, without normalizing.** `tools/souji-seat-audit.py:78` (`if target.startswith("/var/tmp/"): return True`). Measured false negatives: `h7-dotdot-scratch` (`/var/tmp/../home/u/P/f/lane/SKILL.md` → base []), `scratch-other-seat` (`/var/tmp/souji-r9-Other/out.txt` under scratch `/var/tmp/souji-r9-S/` → base []), and beyond-table `p1` (`/var/tmp/souji-r9-S/../souji-r9-Other/out.txt` → base []). New normalizes (`_norm`/`_under`, `:87-93`, `:138`) and flags SCOPE major in all three.

**F4 — base has no V-PROBE class.** `recursive-find`, `probe-realpath-lane`, `probe-strace-fleet`, `probe-find-dot` are expected to produce V-PROBE minor; base emits nothing (realpath/strace/readlink) or only V-RECURSIVE (find). New's `PROBE_BASH_RE` at `:73` supplies it; 4 of the 18 base failures trace to class absence.

**F5 — base collapses relative attempts and unparseable targets into V-WRITE-SCOPE.** 7 cases: `h1`, `edit-relative-foreign`, `report-edit-relative-dotufo` (SCOPE vs RELATIVE, same severity) and `h4`, `h5`, `report-edit-table-prose`, `report-edit-sentence-prose` (SCOPE vs UNPARSED, same severity), plus `h5b` where the severity also flips. New separates attempt semantics from resolution failure (`target_verdict`, `:138-175`), including the truncated branch `:146-155` and its prefix compatibility test.

**F6 — base false positive on a legitimate scratch write.** `scratch-trunc-header` (`[/var/tmp/souji-r…)` under the seat's own scratch) → base V-WRITE-SCOPE major, because the leading `[` defeats the `/var/tmp/` prefix test and there is no scratch notion. New returns [] (allowed). This is the only base failure that is over-reporting rather than under-reporting.

## 5. Beyond-table probes (not in the ddb7347 table)

```
p1 scratch dotdot escape   want [V-WRITE-SCOPE:major]  base [] FAIL              new [V-WRITE-SCOPE:major] PASS
p2 header dotdot escape    want [V-WRITE-RELATIVE:major] base [V-WRITE-SCOPE:major] FAIL  new [V-WRITE-RELATIVE:major] PASS
p3 bare edit relative      want [V-WRITE-RELATIVE:major] base [V-WRITE-SCOPE:major] FAIL  new [V-WRITE-RELATIVE:major] PASS
p4 trunc other-seat scratch want [V-WRITE-SCOPE:major] base [] FAIL              new [V-WRITE-SCOPE:major] PASS
p5 trunc own scratch       want []                     base [] PASS              new [] PASS
p6 agent://all broadcast   want [] (gap probe)         base [] PASS              new [] PASS
p7 second write arg foreign want [] (gap probe)        base [] PASS              new [] PASS
```

- p1–p4 confirm the new normalization/attempt split on shapes the table does not contain (no overfit-to-table effect observed).
- **Residual gap A (both auditors, pre-existing):** `write(agent://all)` is never flagged; the contract forbids the broadcast but no class covers it. Not a C2 regression; no fix proposed here (out of C2's stated classes).
- **Residual gap B (both auditors, pre-existing):** `write(<report>, <foreign path>)` audits only the first rendered token (`write_targets` docstring does not claim multi-arg coverage); the foreign second argument is invisible. L1 may decide whether C2 should own this.
- `p3` also shows the base's suffix bug is not report-name-specific: any bare relative edit is silently allowed when its tail matches an allowed path.

## 5b. Held-out precision probes (CriticC2Precision predictions, not in the table)

The critic's five source-derived predictions were run as written (six rendered lines; `probe3.py`). Every prediction is confirmed, and they reveal that the 48-case table does not bound the new auditor's false-positive rate:

```
c1 relative-report-style     write(lane/.ufo/waves/round-9/w1/S.md)        base []   new [V-WRITE-RELATIVE:major]  FP
c2 shell-bracket-in-content  edit(<owned header> … + if [ -n "$foo…)       base []   new [V-WRITE-UNPARSED:major]  FP
c3 markdown-link-in-content  edit(<report header> … + see [README.md](x))   base []   new [V-WRITE-RELATIVE:major]  FP
c4a trunc-slash-v            edit([/var/tmp/souji-r9-S/a#AB12] … [/v…)      base []   new []                        by design
c4b trunc-slash              edit([/var/tmp/souji-r9-S/a#AB12] … [/…)       base []   new []                        by design
c5 xd-device                 write(xd://report_issue)                      base [V-WRITE-SCOPE:major]  new [V-WRITE-RELATIVE:major]  FP
```

- c1 is the sharpest: `fleet = Path(lane).parent`, so a bare target prefixed with the lane's basename (`lane/...`) resolves at the contract fleet root **to the allowed report**. The code comment at `tools/souji-seat-audit.py:166-168` ("Bare targets resolve at the contract's fleet root, which cannot reach a lane path") is factually wrong whenever the lane is a child of the fleet root, and the non-header branch never tries that resolution. The class's severity is still defensible as a procedural violation (the contract mandates absolute paths), but the stated reason is not.
- c2/c3 are content false positives: a `[` in the rendered argument tail is treated as a truncated header (c2), and any bracketed token containing `.` is treated as a header (c3, `m.group(2) or "/" in tok or "." in tok` at `:113`), so an ordinary markdown link inside edit content is audited as a write target.
- c4 is a **disclosure error, not a count error** (CriticC2Precision's distinction, adopted): `:150-152` states the visible prefix "resolves inside the one region seats may write freely", which is false for `/v` and `/`, and the earlier claim "fail-open inside /var/tmp only" is false in the same way. The table's own `scratch-trunc-header` (`:325`, `/var/tmp/souji-r…`) pins lexical prefix compatibility — that prefix is not *inside* `/var/tmp/souji-r9-S/` either — so narrowing the rule (critic fix 7) requires changing the pinned case first. Count impact on r16: none in the major column; 4 rows take this branch and pass by prefix. If L1 keeps `:325`, the P4 fix shrinks to correcting the comment at `:150-152` and the tool's Limits text.
- c5: `xd://report_issue` is the harness QA device the contract instructs seats to write to; `:144` only exempts `agent://`, so a mandatory action is a major write-relative violation.

**Smallest fix (measured on a scratch copy, 4 hunks, lane untouched):**

1. `:144` exempt `xd://` like `agent://` → `target.startswith(("agent://", "xd://"))`.
2. `:169-174` resolve a bare relative target at the fleet root only, and return `None` if that normalized path is allowed (keep `V-WRITE-RELATIVE` otherwise — `h1`/`h2` unchanged).
3. `:113` drop the `or "." in tok` header heuristic (a `#TAG` or a `/` is required); markdown links stop being headers.
4. `:126` do not emit the unparsed-truncated fallback for a tail fragment that cannot be a path token; a truncated *path* after a resolved header must still be audited. Two equivalent spellings were measured (§5c): CriticC2Precision's first-character test (adopted as primary — a `[` followed by a character that can start a path) and my `elif not headers`. CriticC2Precision's stated risk ("would hide real truncated targets that come after a good header") does not reproduce: both variants still flag X1 (foreign absolute) and X2 (relative path) truncations after a resolved header.

Measured on `fixed_critic.py` / `fixed_mine.py`: **TABLE 48/48 each, PROBES 15/15 each** (the 13 above plus X1/X2). The patch is a proposal for L1, not applied to the lane.

## 5c. Variant comparison for the P2 fix (measured)

CriticC2Precision's first-character rule and my `elif not headers` rule are behaviorally identical on every measured input: the 48-case table (48/48 each) and 15 probes (15/15 each), including the two hidden-target cases X1 `[<owned> … [/home/u/P/f/other/…)` → V-WRITE-SCOPE major and X2 `[<owned> … [souji-shokunin/…)` → V-WRITE-RELATIVE major. The first-character rule is preferred because it does not depend on whether an earlier header resolved, so its rationale is local to the fragment.

One correction to my earlier §5b wording: the rule as measured suppresses only tail fragments that are **not path tokens**; a truncated path tail (h8, X1, X2) is still emitted and audited. The "hide real truncated targets" risk was in the prose, not in the measured behavior.

## 6. Scratch-derivation cross-check

`run()` computes `scratch = "/var/tmp/" + <"souji-rN-"> + name + "/"` (`:231`, `:246`). Verified against the wave-2 registry (`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-17/w2/swarm-registry.json`, key `HeldOutBaseAuditor`): spec item names are short, so the derived scratch is exactly the contract's `/var/tmp/souji-r17-<SeatName>/` and matches this seat's ALLOWED-EXEC directory. No scratch false positive from the roster suffix (`-2` appears only in the agent id, not the spec name).

## 7. Verdict

- **C2 claim "severity-exact selftest 49/49": HOLDS** — reproduced 49/49 natively and 48/48 + wave-summary when the table is re-evaluated via importlib.
- **"was 20/20 severity-blind": HOLDS** — base reproduces 20/20, its comparator is class-set-only (`:179`), and on the same 48 shapes it scores 30/48 severity-exact.
- **Transfer beyond the table: PARTIAL** — H1–H8 are **not held-out**: the wave-1 critic authored them and the code was tuned until they passed, so they are regression pins (CriticC2Precision's relabel is correct and should land in the report/claims). The only genuinely out-of-table inputs are this seat's p1–p7 and c1–c5. On those, the new rules hold 4/4 clean-vs-flaggable shapes (p1–p4) and 4/6 precision shapes fail (c1, c2, c3, c5). 16 of the 18 base failures are still new-only shapes, which shows the pins discriminate against the base.
- **Precision outside the table: PARTIAL** — 4 of 6 independently derived content/path shapes (c1, c2, c3, c5) are false positives in the new auditor, including one (`write(xd://report_issue)`, mandated by the contract) that is flagged major. The four-hunk fix in §5b closes all four while keeping the table at 48/48; until it or an equivalent lands, "precision" should be read as table-local.
- **Smallest fix required: none for the table claim; four hunks for the precision counterexamples** (§5b/§5c, two variants measured 48/48 + 15/15 each on scratch copies).

Caveat for L1 (not refuted, just disclosed): the table was authored in the same commit as the fix, so it cannot by itself prove the *class taxonomy* is complete; the two shared residual gaps in §5 are the known uncovered surface, and both predate C2.

## 8. Evidence and tooling

No tool installs or upgrades were needed (probe rule tooling unused). Python 3.14.8.

Retained under `/var/tmp/souji-r17-HeldOutBaseAuditor/` during the wave (deleted at close per contract; sources are recoverable with the two `git show` commands in §1):

| file | sha256 |
|---|---|
| `new_audit.py` (ddb7347) | `8268212db158186d3d6dedc22ffb4755c89d7e62cfff2210b7c6329ca58d5f54` |
| `base_audit.py` (5fa6017) | `c9ff355c6bca31196eeb0527d7286e601878a1c50309d078cd1523820c9bd3b3` |
| `heldout-results.json` | `c80fdd0bddb6d7b67eb2e99ec64b6d1fd4056688b91976f196b65b1af8e2a5ea` |
| `heldout-run.txt` | `3aa1b6dc1d63355e1a8df500716ef063805ce256eb1093c4fd5166ee0479119b` |
| `probe2-run.txt` | `2a65c33dcc0fff54b38f1ed2a3b568af1ba1d108e3e0be460e374cfbe2bc4f3a` |
| `new-selftest.txt` | `3f5895727d9d01db631f4a459d313682bfeabbbc77555865d035dea010dad4fb` |
| `base-selftest.txt` | `7e1d909ea46366eb558f8eb6571466dbaa7031584c06c3e1a74582d0faa08f0c` |
| `run_heldout.py` | `81d1cc26824b895835d63ae85f89761fc1b83d99770dde4c723e21014883d993` |
| `probe2.py` | `acc340a423d9b3ceb64ca27ae3d95214867ea0bb648c25d714861d0df656768c` |
| `probe3.py` | `probe3-run.txt` `e5c991505f702d59d114b982b2dafa16b622d7e1e1a24c7b0648df673ebf62cf` |
| `probe_fix.py` | `probe-fix-run.txt` `7e40219f6fc21654f71a4ae5a948aa80c90526ef7736d86b8934d2d599bb9417` |
| `fixed_critic.py` (candidate, scratch only) | `77188ab85f7ff9638c5a9b63446ec8f0d85cb4038ea3eaf88b7e24a40372ed77` |
| `fixed_mine.py` (identical to earlier `fixed_audit.py`) | `06f2929ba5a9e7af8991c1726422b74d9046b781029ab9ab821104cc1859dce0` |
| `variant.py` | `84ddf19101cdfe93a8ef8ab583cb846d1432790c17f0c87508c6445f6b6f9dcf` |
| `variant-run.txt` | `5d439c3d76f5cd07bc56e682099cc9bd6d525bd06ab6dad6bf0bfa975a40629a` |

Exactly what was exercised: both `--selftest` entry points, the AST-extracted 48-case table against both `audit_seat` implementations, both `run()` implementations on one synthetic spec/transcript pair, 7 beyond-table probes, 6 critic-prediction lines, and the two 4-hunk candidate-fix variants against the table plus 15 probes. No lane tool, fixture, receipt script, census, or network surface was run; no git write occurred.
