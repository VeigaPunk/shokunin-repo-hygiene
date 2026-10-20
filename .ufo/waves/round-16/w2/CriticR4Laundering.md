# CriticR4Laundering — r16 w2: is the R4 re-pin oracle-fitting or a first execution?

Target: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff b410186 HEAD -- tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-evidence.py tests/fixtures/r15-preservation-frozen`
(commits `c6207bd` R4 repair and `7a79dc2` regenerated record). I also read the R4 commit's other edit, `tests/fixtures/r15-census-config.py` (detail cap), because it changes the subject the checker judges.
Axis judged: **calibration**. I did not execute any lane code. All verdicts come from reading files, `git show`/`diff`, digests, and my own parse of `record.json` and the two matrix JSONs.

## Verdict

**PARTIAL.** R4 is two different moves, and they need two separate verdicts.

1. **Byte and transcript re-measurement: holds.** This was a real first execution, and it avoids the RevengeFrozenPin D5 trap. `regenerate.py` re-runs each arm from `git show <rev>:tools/souji-census.sh` and does not do a digest-only re-pin. I confirmed every pinned commit/blob pair with `git show <rev>:<path>` hashed:
   - a31642d → `6a000c59…`
   - cc21683 → `fcff8b05…`
   - c6207bd → `64a60fd0…` (same as HEAD)
   - fixture at c6207bd/HEAD → `27474396…`
   - `record.json` → `173db777…`, which equals `expected.json:7`

   Per-case statuses in the record are identical, all 60 of them (20 ids × 3 arms), to `c1-matrix-final.json` (fixture `85de2a43`) and to `c1-matrix-landing.json` (fixture `27474396`). So three runs reproduce the same statuses.
2. **Class-table re-pin: fails as an independent oracle. This is oracle-fitting by construction.** The four r16 classes are exactly the four cells of the observed (preharm, harm) PASS/FAIL 2×2:
   - benign = P/F
   - refusal = F/P
   - safety = F/F
   - preserve = P/P

   The tables were filled in from `census/round-16/c1-matrix-final.json` (`tools/souji-preservation-evidence.py:310-322`). Re-deriving them from that observation **cannot reject any baseline observation**, so the baseline status checks have zero rejecting power at pin time.

   The frozen `clean` depends on this. I replayed the r15 oracle (b410186 checker tables) on the regenerated record:
   - **8 `case-status-unexpected`** + 1 `case-finding-mismatch` (07 changed arm, token `none`).
   - 4 of the 8 are backed by an r16 fixture contract revision: harm 03, harm 07, harm 14, preharm 07.
   - **4 have no contract change at all: preharm 20, harm 18, harm 19, harm 20.** `case_18`/`case_19`/`case_20` have no hunk in `git diff -U0 b410186 HEAD -- tests/fixtures/r15-census-config.py`. The only nearby helper change is `trace_access` (EACCES/faccessat2), and that is not the observed failure reason for any of them.

   So those 4 are **falsified r15 predictions**, quietly turned into new class labels. For example, the r15 checker said "Confirmed by the fixture author: a31642d … lacks the strict malformed-compare guard (20)", but the record shows preharm 20 PASS. Even a contract-honest table (r15 classes + the 03/07/14 r16 revisions) gives `failed` (4× case-status-unexpected), not `clean`.

The verdict on the **changed tool** is not laundered: `_expected_status` returns `pass` for every changed-arm id no matter what the tables say (`:1316`). What was laundered is the **discrimination and baseline record**: r15's claims about which ids the r14 harm build and the a31642d pre-harm build pass. Those claims now read "clean" when four of them were refuted.

## Per-hunk judgment

| # | Hunk | Verdict | Evidence / counterexample | Smallest fix |
|---|------|---------|---------------------------|--------------|
| H1 | `CASE_LINE_RE` `[^\t]*` → `(.*)` (`tools/souji-preservation-evidence.py:923`) | **holds** (legitimate first-execution bug) | The r15 checker contradicts itself. The live regex at b410186 `:916` forbids TAB in detail, but the token rule at b410186 `:1482` searches for `\tobserved_finding=` *inside* detail, so no real CASE line could ever both parse and pass. The pinned r15 fixture (`6314d45d`, b410186 `tests/fixtures/r15-census-config.py:1367`) emits TAB details. Extra trailing TAB fields are now accepted, but the first `observed_finding=` wins and stdout is sha-bound, so this opens no new hole. | none |
| H1b | Dead duplicate regexes, still present (`:287-290`) | **fails (minor, duplicate authority)** | `TOOL_LINE_RE`/`TOOL_KIND_RE`/`CASE_LINE_RE`/`SUMMARY_LINE_RE` are defined twice at module level. The `:289` copy (`\tCASE…(.*)`, leading TAB) is shadowed by `:923` and never used, so an edit to `:289` would silently do nothing. It existed at b410186 `:287-290` too; R4 fixed the second copy and left the first. | Delete `:287-290`. |
| H2 | Declared detail stored TAB→space; comparator does `.replace("\t"," ")` (`:1388-1392`, `_arm` `:1848`, `regenerate.py` `run_arm`, external fixture `:133`) | **holds, lossy** | A transcript detail `ok observed_exit=0\tobserved_finding=none` (mixed space/TAB) equals the declared rendering. This only weakens the *redundant* declared field: stdout is digest-bound, and the token rule still needs a real TAB, so an r15-style all-space hand-written transcript still gets `case-finding-mismatch`. JSON can hold `\t`, so the lossy rendering isn't needed. | Store raw details and compare exactly. |
| H3 | Class tables re-pinned (`:310-357`); external fixture literals (`tests/fixtures/r15-preservation-evidence.py:47-61`) | **fails (oracle-fitting + false provenance)** | (a) The tables are the observed 2×2 cells (see above; my replay matches all 60 statuses). (b) The 18/19/20 moves have no fixture contract change. (c) **Two authorities disagree.** The fixture's own "pinned, non-adaptive" `CASE_CLASSES` (`r15-census-config.py:168-176`) still says 18=preserve, 19=refusal, 20=preserve (and 03=degrade, a class the checker lacks), while the checker says safety/safety/benign. The fixture's observation-derived `HARM_CASES` (`:161-165`) leaves out 19, but harm fails 19 in all three runs (`store: contract: synthetic store path in output`, record `runs.baseline`). (d) The checker still claims independence: `:310` "Independent literal case universe", `_expected_status` docstring `:1303` "Independent oracle", the module docstring `:111-116` (still the stale r15 matrix: refusal 02,03,07,11,14,17,19; preserve 18,20 fail preharm) and `:221` ("agreed with the fixture author … never derived"). (e) The 19 comment was rewritten after the fact to fit the observed failure ("refusal **without echoing the store**", `:346`). (f) The external harness copies the same observation, by the same author, in the same commit (`:47-48`, "observed per-arm statuses … independent of the checker"). Its 8/8 detects drift between the two copies; it does not corroborate the classes. The R4 commit body is empty (`git log -1 --format=%B c6207bd`), and `DistillRoutedEvidence.md:83-95` does not mention the reclassification. | Label the tables "observed baseline pin (r16 matrix), not an independent oracle" at `:310`, `:1303`, `:111-116`, `:221`. In the r16 lesson/R4 row, carry the replay result as a STATUS line: "r15 class oracle on the real record: 8 case-status-unexpected + 1 finding-mismatch; 4 contract-revised (03, 07×2, 14), 4 falsified with unchanged case code (preharm 20; harm 18/19/20)". Reconcile fixture `CASE_CLASSES`/`HARM_CASES` (add 19) with the checker, with an explicit falsification note, or have the landing gate assert they agree. Qualify the frozen `clean` as "clean against observation-pinned baseline classes". |
| H4 | `refusal_ids = CONFIG_TOKEN_IDS` (`:1495`, `:361-363`) | **partial** | The token set {02,03,11,14,17,19} is exactly the set of changed-arm ids whose observed finding is non-`none` (`c1-matrix-final.json:71-142`), so it is observation-derived too. The rule checks only "non-none", not the contract family (`path-protected:*` for 02/11/17/19, `config-unsupported:*` for 03, `status-skipped:*` for 14). The fixture's own oracles catch the family mismatches, so the effect is low. | Pin per-id token prefixes from the fixture's r16 header contract. |
| H5 | `_default_detail` / external `detail()` emit TABs (`:1816-1823`, external `:104-110`) | **holds** | Synthetic selftest transcripts now match the real fixture format. | none |
| H6 | `duplicate-id` selftest expectation changed (`:2137-2140`) | **partial (expectation matched to output; wrong rationale)** | The comment says the two `run-inconsistent` come from "declared/parsed disagreement". They can't: `setdefault` keeps the first row (`:1377`), so declared and parsed statuses and details are equal (`:1381-1392`). The two `run-inconsistent` are the `stdout_sha256` (`:1337-1340`) and `stdout_bytes_total` (`:1341-1344`) mismatches, because the mutation edits stdout without updating the digests. The case still pins `case-duplicate`, but it is mixed up with a digest-tamper signal. [static reading; not executed] | Recompute `stdout_sha256`/`stdout_bytes_total` after the mutation, expect `[case-duplicate, summary-mismatch]`, and fix the comment. |
| H7 | `finding-mismatch` selftest uses `CONFIG_TOKEN_IDS` (`:2535-2543`) | **holds** | Follows from H4. | — |
| H8 | `expected.json` pins (census `64a60fd0`, fixture `27474396`, `record_sha256` `173db777`, verdict `clean`) | **holds (bytes)** | Every pin matches a committed blob at c6207bd and at HEAD, and my `sha256sum` of the worktree files agrees. `regenerate.py` writes `"verdict": "clean"` without running the checker, but `--frozen` re-checks it (`snapshot-verdict-mismatch`, `:1754-1759`), so a wrong prediction would surface as exit 2. What `clean` *means* depends on H3. | Keep. Record the actual `--frozen` stdout with its revision next to it. |
| H9 | `record.json` regenerated | **holds, one false-provenance field** | Arm paths `/var/tmp/souji-r16-repin.scjidogf/<arm>/tools/souji-census.sh`, `stdout_sha256`/bytes self-consistent, `tool.commit` blobs verified. However, `regenerate.py` hard-codes `"stderr": ""` and never looks at `proc.stderr` (`run_arm`). The record asserts an empty stderr that nothing measured. Whether it really was empty is unknown: the fixture prints nothing to stderr in its case loop (`:1504-1525`) [INFERENCE]. | `"stderr": proc.stderr`. |
| H10 | R4 commit `c6207bd` also edits the C1 fixture: CASE detail capped at 397+"..." "to stay within the preservation checker's 512-character reason bound" (`r15-census-config.py:1515-1521`) | **partial (fits the subject to the checker; makes a gate clause unreachable)** | `baseline-reason-weak` (`:1512-1521`) fires on `len(detail) > 512` or a missing `REASON_TOKENS` (`:371`). The fixture appends both tokens to every detail unconditionally, and the cap keeps every detail ≤ ~475 chars. So for fixture output this rule can now fire only on the strings "Traceback"/"Exception". In the frozen record, 7 of 24 baseline FAIL rows were truncated. Harm 03 (in `CONFIG_HARM_FAILS`) is truncated at 471 chars. Its uncapped list repeats ~130 chars for each of 5 repos plus the mixed-degrade tail, so it is >512 [INFERENCE] and would have made the frozen verdict `failed` without the cap. The comment "the --json record keeps the full problem list" doesn't help R4: `regenerate.py` never passes `--json`, so the full problem lists are not in the frozen evidence. | Be explicit: either delete the length clause from `baseline-reason-weak` (it measured verbosity, not concreteness) and remove the fixture cap, or keep the cap and document the clause as unreachable. Record the change as a checker/fixture co-edit in the R4 row. |
| H11 | Checker comment says fixture "at 0a70bef"; the frozen record uses c6207bd bytes | **holds (status-neutral)** | The table source is `85de2a43` (`c1-matrix-final.json:664`); the record is `27474396`. All statuses are identical across both (checked above). | Cite both digests. |

## Strongest counterexample

Take the regenerated record exactly as committed and apply the r15 oracle, i.e. the tables the checker carried *before* it ever ran (b410186 `tools/souji-preservation-evidence.py:310-348`). The result is not `clean`:

- `baseline_preharm`: R15CFG-07 pass (want fail), R15CFG-20 pass (want fail).
- `baseline` (harm): R15CFG-03, 07, 14, 18, 19, 20 fail (want pass).
- `changed`: R15CFG-07 PASS with `observed_finding=none`, but 07 was in the r15 refusal set → finding mismatch.

The 03/07/14 moves are backed by the fixture's r16 contract header (`r15-census-config.py:13-27`) and by changed case code. The 18/19/20 moves are not: the case code is unchanged, the fixture's own `CASE_CLASSES` still disagrees, and the checker comment was rewritten to fit. With honest tables (r15 classes + only the contract-backed r16 moves), the frozen verdict would be `failed` (preharm 20; harm 18, 19, 20). The `clean` therefore depends on 4 labels chosen to match observation.

## Impacted axes

- **calibration** (primary): r15 predictions that were falsified got erased instead of reported; the class tables are presented as an "independent oracle" when they are an observation pin.
- **duplicate authority**: checker tables vs fixture `CASE_CLASSES`/`HARM_CASES` vs external harness literals; plus the shadowed regexes at `:287-290`.
- **false provenance**: `"stderr": ""`; the duplicate-id comment; the stale module docstring.

Not affected: the changed-tool verdict, and the byte/commit binding of the frozen snapshot.

## Cross-axis note (C1, for L1)

The fixture's `HARM_CASES` (`r15-census-config.py:161-165`, "expected to FAIL under the r14 harm tool from OBSERVED behavior") leaves out R15CFG-19, yet r14 harm fails 19 in every run. "r14-harm fails every HARM_CASES id" is true only as a subset claim: harm fails 16 ids, and `HARM_CASES` lists 15.

STATUS: PARTIAL — the R4 byte/transcript re-measurement is a real first execution (pins match committed blobs; statuses reproduce across 3 runs), but the r16 class tables are fitted to the observed 2×2 cells and called an independent oracle. Replaying the r15 oracle on the real record gives 8 case-status-unexpected + 1 case-finding-mismatch; 4 of the 8 (preharm 20; harm 18/19/20) are r15 predictions falsified with no contract change, relabelled into a `clean` with no disclosure. The fixture's own CASE_CLASSES still disagrees with the checker on 18/19/20.

## Commands

Shell (`bash`), verbatim:

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat b410186 HEAD -- tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-evidence.py tests/fixtures/r15-preservation-frozen
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline b410186..HEAD -- tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-evidence.py tests/fixtures/r15-preservation-frozen
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff b410186 HEAD -- tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-evidence.py tests/fixtures/r15-preservation-frozen/expected.json tests/fixtures/r15-preservation-frozen/regenerate.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat c6207bd 7a79dc2
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show c6207bd -- tests/fixtures/r15-census-config.py
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-preservation-frozen/record.json /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat b410186 0a70bef -- tests/fixtures/r15-census-config.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline b410186..HEAD -- tests/fixtures/r15-census-config.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff b410186 0a70bef -- tests/fixtures/r15-census-config.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff -U0 b410186 HEAD -- tests/fixtures/r15-census-config.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -1 --format=%B c6207bd
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tools/souji-preservation-evidence.py
```

Python eval cells (my own analysis code; no lane script imported or executed). Through `subprocess` they issued only these git commands:

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show <rev>:tools/souji-census.sh            # rev ∈ a31642d cc21683 b410186 0a70bef c6207bd HEAD, piped to hashlib.sha256
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show <rev>:tests/fixtures/r15-census-config.py # same revs, hashlib.sha256; b410186 copy scanned for observed_exit/CASE print lines
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tools/souji-preservation-evidence.py  # regex/docstring line scan
```

Beyond that they only read and parsed JSON from `tests/fixtures/r15-preservation-frozen/record.json`, `census/round-16/c1-matrix-final.json` and `census/round-16/c1-matrix-landing.json` (status replay, detail lengths, matrix-vs-record agreement), and read `tools/souji-preservation-evidence.py` at HEAD as text.

Non-shell reads (exact files only): `skill://godspeed`; `tools/souji-preservation-evidence.py` (ranges 108-118, 280-292, 308-366, 1300-1523, 2110-2145; greps); `tests/fixtures/r15-preservation-evidence.py:44-62`; `tests/fixtures/r15-census-config.py` (1490-1530; greps); `census/round-16/c1-matrix-final.json` (greps); `census/round-16/c1-matrix-landing.json` (grep); `tests/fixtures/r15-preservation-frozen/record.json` (grep); `.ufo/waves/round-16/w1/RevengeFrozenPin.md:120-242`; `.ufo/waves/round-16/w1/DraftR15Correction.md` (grep, no match); `.ufo/waves/round-16/w1/DistillRoutedEvidence.md:80-100`.

No tool was installed or updated. No `/var/tmp` scratch was created. Nothing under census/operator-sweep-*, ~/.omp, .ufo/state, MANIFEST.json or sibling lanes was touched.
