# Attack17 — `summary/r19-seat-audit-shapes/extra` (want=False) and paired positive

Seat: SoujiR22.Attack17. Source-only leaf review of candidate `4f83fd222ffbd8825340221a8c426550ef891191` (HEAD).
No tests, builds, runner or oracle execution, mutation execution, delegation, or installs. Read-only commands
were limited to `sha256sum`, `git show`/`git diff`/`git log` on named paths, and stdlib JSON extraction/diff
of the named data files (no code under test imported).

## STATUS

**PASS (source-only), non-discriminating control.** The stored delta reconstructs exactly from the pinned
public record. The literal `want=False` is correct, and the fixture really feeds that input. Under the
candidate the vector is rejected by the **unchanged** exact summary-list predicate. The only R22 change in
the summary branch (`and not stderr`) is not what decides it. Base `41553adb` rejects it through the same
line, so this vector is a no-harm control and gives no calibration-improvement evidence. Paired
`positive/r19-seat-audit-shapes` is correctly `True` under both base and candidate. I found no concrete
mismatch between oracle, fixture and predicate for this vector. Limits: there is no runtime observation;
L1's 214-vector run is the authority. The gaps listed at the end are inherited and fall within the
lesson's declared exclusions.

## Input binding (observed)

| file | sha256 | binding |
|---|---|---|
| `census/round-21/final-out-S1.json` | `bc53a752…25738fe` | equals oracle `source_receipt_sha256` |
| `census/round-21/step-inventory.json` | `8b7b1cd8…7d1310` | equals oracle `frozen_inventory_sha256` |
| `tests/fixtures/r22-result-oracle.json` | `292442a6…0dcd0651` | equals `git show 4f83fd2:` copy |
| `tests/fixtures/r22-result-oracle.py` | `3c0776ae…697a604` | equals `git show 4f83fd2:` copy |
| `census/round-21/run-acceptance.py` | `00d0e9c2…e080a6` | equals `git show 4f83fd2:` copy; `git diff 4f83fd2` on the five named paths is empty |

## Step 1 — delta reconstruction (done before reading the predicate)

- Pinned record `commands[name=r19-seat-audit-shapes]` (exactly 1 record) has `returncode=0`, `stderr=""`,
  `failure_lines=[]`, `matched=true` and a stdout of 1954 chars. Its re-hash with
  `utf-8/surrogateescape` is `4a92ef43…86750138`, which equals the recorded `stdout_sha256`.
- Frozen inventory step (exactly 1): `expected_summary="SUMMARY total=17 failed=0 base_discriminating=12"`,
  `pass_pattern="^CASE\tpass\tchanged/"`, `pass_count=17`, `kind="summary"`. There is no
  `baseline_mismatch_count` and no auxiliary lines. This is identical to the live `make_steps` row at
  `run-acceptance.py:317-319`.
- Oracle vector (exactly 1, keys `group,id,step_name,stdout,want`, `want=false`,
  `group="summary-control"`): its stdout is 1988 chars. `stdout.startswith(original)` is True, and the delta
  is exactly the 34-char suffix `'SUMMARY invalid synthetic summary\n'`. The other 35 lines are byte-identical
  to the pinned output.
- The vector is present with the same want/delta in both committed oracle revisions (`36c78ba`: 212 cases;
  `4f83fd2`: 214 cases). Limit: the oracle first appears in the same commit as the implementation, so git
  alone cannot prove the "frozen before editing" ordering. That rests on the lesson
  (`corpus/lessons/round-22.md:33`) and the bindings receipt, which this seat was not permitted to open.

**Correct expected decision, independent of the predicate:** the producer contract is one summary line,
exactly `SUMMARY total=17 failed=0 base_discriminating=12`. The fabricated output asserts a second,
contradictory `SUMMARY` record. A result carrying two summary claims, one of them "invalid", is not the
accepted outcome. Literal `False` is right.

## Step 2 — does the fixture feed it? (`tests/fixtures/r22-result-oracle.py`)

- Line 58: `records` is keyed by `receipt['commands'][].name`, which resolves the pinned record.
- Line 68: `stdout = case.get('stdout', record['stdout'])`, so the vector's full stdout replaces the record.
  There are no `stdout_nested_array_depth` or `json_set` keys, so lines 69-82 do not apply.
- Lines 87-91: `returncode` falls back to the record (`0`) and `stderr` falls back to the record (`""`),
  both encoded `utf-8/surrogateescape`.
- Lines 59-60, 83-85: the step comes from the frozen inventory via `replace_revision`. The step has no
  revision tokens and is not `cache-demo`.
- Line 97: the check passes only if `type(observed) is bool and observed is False`. An exception yields
  `observed=None`, which fails the vector. **Yes, the fixture feeds exactly the reconstructed input.**

## Step 3 — predicate trace, candidate (`census/round-21/run-acceptance.py`)

- `:118` `SUMMARY_RE = ^(?:SUMMARY|SELFTEST)(?:\t| ).*$`. Both `SUMMARY total=17 …` and `SUMMARY invalid
  synthetic summary` match (space separator).
- `:395` `summary_lines = [real, "SUMMARY invalid synthetic summary"]` (len 2).
- `:396` and `:356-359` `failure_lines`: there are no `FAIL\t`, `CASE\tFAIL\t` or `CASE\t*\tFAIL` lines, so
  the result is `[]`.
- `:410` `matched = (0 == 0) and not [] = True`.
- `:415-416` expected is a `str`, so `summary_match = summary_lines == [expected]`, which is **False**.
- `:432-436` INVENTORY lines `[] == []`, so `auxiliary_match=True`; `summary_match` stays False.
- `:440`: no `baseline_mismatch_count`, so skipped. `:446-450`: 17 `^CASE\tpass\tchanged/` lines, so
  `pass_match=True`.
- `:463` `matched = True and False and True and not "" = False`. `:464` is not this step.
  `:537` `bool(False)`, so observed is `False`, which equals want. No exception path is reachable (string
  branch, no regex groups, ASCII input).

**Changed predicate for this vector.** From `git diff 41553adb..4f83fd2`, the only edit inside the summary
branch that this vector can reach is `:463`, which appends `and not stderr`. Here stderr is `""`, so that
term is True and inert. The deciding term is `:416`, which is unchanged from base (base `:373` is the
identical expression). Base `:417` `matched = matched and summary_match and pass_match` therefore also gives
False. The `:426-431` `try/except ValueError` edit is reachable only for dict `expected_summary` with
`baseline_mismatch_group` (`r20-input-binding`), not this step. **Base decision: False. Candidate
decision: False. The vector does not discriminate.** It is valid as a no-harm/operability control, and it
must not be counted as a calibration improvement.

## Paired positive `positive/r19-seat-audit-shapes` (want=True)

This vector has no overrides, so it uses the record's `rc=0`, `stderr=""` and original stdout.
`summary_lines` is exactly `[expected]`, failures are `[]`, INVENTORY is `[]==[]`, and the pass count is
17/17. The new `not stderr` term is True. Candidate gives True (`:463`); base gives True (`:417`). That
matches the pinned historical `matched=true`. No harm.

## Drafted mutation (not executed)

- **Mutation:** `run-acceptance.py:416`, change
  `summary_match = summary_lines == ([expected] if expected else [])` to
  `summary_match = (expected in summary_lines) if expected else not summary_lines`.
- **Expected killed vector:** `summary/r19-seat-audit-shapes/extra` (observed True, want False). The paired
  positive survives as True.
- [INFERENCE] The same mutation should also kill the other string-expected `summary/*/extra` controls. It
  should not affect `summary/r20-input-binding/extra`, which takes the dict branch with its own
  `len(summary_lines) == 1` at `:419`.
- Dropping `and not stderr` at `:463` would **not** be killed by this vector. Only the `stderr/*` group
  covers that edit.

## Residual gaps (inherited, base-identical; not a C1 falsification)

All of these are accepted equally by base and candidate, so none is harm introduced by `4f83fd2`.

- **Undetected extra separators.** An appended line not shaped by `SUMMARY_RE` is ignored. Examples: a bare
  `SUMMARY` with no tab or space after it, `SUMMARY:…`, or a leading-space ` SUMMARY …`. The output would
  then be accepted. The oracle's control uses only the space-separated form.
- **Summary not checked against body.** `total=17` and `base_discriminating=12` are never checked against
  the body. Deleting all 12 `CASE\tdiscriminates\tbase/…` lines, or the 5 `same` lines, still matches
  (`:416` compares only text, and `:447` counts only `changed/` passes).
- **Lowercase failure marker.** An appended lowercase `CASE\tfail\tchanged/x …` line is not a failure line,
  because `:358-359` matches only the case-sensitive `FAIL`. [INFERENCE] Lowercase is this producer's
  status style.
- **Already excluded by the lesson.** These fall within the lesson's explicit exclusions,
  "arbitrary stdout failure-marker semantics, repeated pass-line identity"
  (`corpus/lessons/round-22.md:35`). They should stay non-claims and must not be presented as covered.
  Coverage for this step is: one exact summary line, an exact pass count, empty stderr, rc=0, and no
  uppercase FAIL markers.

## Tooling

No installs or updates. `jq` rejected the oracle JSON at byte 164988 ("invalid character").
[INFERENCE] This is a lone-surrogate escape in another vector's synthetic invalid-UTF-8 stderr; Python's
stdlib `json` decodes it. This is a tool-strictness difference only and does not affect this vector.

Report: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/w2/Attack17.md
