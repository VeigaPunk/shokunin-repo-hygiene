# RerunGateSelftest — C2 landing gate selftest, case-vacuity attack (round 16, W2)

Lane HEAD at assignment `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`; L1 advanced it to
`163158a706352f1c0ee3521c4da2e5289970db57` (lesson/SOURCES/LOG) while this seat ran.
`tools/souji-landing-gate.py` is byte-identical at both revisions — sha256
`e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`
(1005 lines; `git diff --quiet HEAD` clean) — so every line cited below is the committed
blob in both cases.

## Attack and answer

Item: does each `--selftest` case actually assert the finding id it names, or could it
pass vacuously?

- **Named-id assertion is real, not exit-code-only.** Every case that names ids goes
  through `check()` at `tools/souji-landing-gate.py:766-771`:
  `res["exit"] == expect_exit and all(i in ids for i in expect_ids)` where `ids` is
  the deduped actual finding-id set (769). Ten of the eighteen cases carry `expect_ids`;
  none can pass on exit code alone. This direction **holds**.
- **Four cases can pass with the mechanism they name dead**, and one of them
  (`fenced-and-table-ignored`) exercises neither of the two mechanisms in its name.
  This direction **fails/partial**.
- The numeric claim is true: I reproduced `SELFTEST pass=18 fail=0` (exit 0) exactly.

Verdict on the attack: **partial** — false-pass risk is not in the id membership check;
it is in case construction and in the absence of any negative control for two branches.

## Findings

### F1 (high) — `fenced-and-table-ignored` asserts neither fences nor tables
`tools/souji-landing-gate.py:931-939` builds the report body at 933-938:

- fenced content (934): `syntax error inside a fenced block`
- table row (935): `| note | snapshot_tampered quoted in a table |`

Neither line begins with `STATUS`, so `status_value()` (250-255, regex 71) returns
`None` for both and `is_failure_line()` (257-271) returns `False` at 261-262 **before**
reaching the `if in_fence or in_table: return False` guard at 263. The only `STATUS`
lines in that fixture are outside the fence/table (934 `STATUS: none`, 936
`STATUS — done`) and are rejected by the vocabulary test (`FAILURE_STATUS_WORDS`,
72-79), not by fence/table tracking.

Consequence: deleting 263-264 (and the whole `in_fence` toggle at 277-281) changes no
case outcome; F1 is an [INFERENCE] from the cited control flow, not a mutation run
(mutation was not in this seat's ALLOWED-EXEC).

What the case does assert, truthfully: two benign first words (`none`, `done`) are not
failure-channel words. Its name overclaims both mechanisms.

Smallest fix: move a failure line inside each construct — e.g. fenced
`STATUS: FAIL — quoted from another seat` and table row `| 2 | STATUS: FAIL |` — and add
an outside-fence copy expected to be flagged, so the case cannot also pass via a dead
detector.

Compensating coverage: the external fixture `tests/fixtures/r16-landing-gate.py:397-400`
puts `STATUS: FAIL inside fence` and a table `STATUS: FAIL` in SeatF and asserts
`absent` at 412-415; `SeatH` blockquote at 402. So the *gate* is covered at fixture
level; the embedded selftest is not.

### F2 (high) — no case exercises a clean `measured_commit`; an always-firing measured check passes 18/18
`_frozen_world` writes `record = {"measured_commit": "0" * 40}` (725). `0…0` is
deliberately treated as dangling: it matches the hex shape, fails `rev-parse --verify`
(462-474), `measured_ok` is `False` (474-476) and the comparisons are skipped by the
`if measured_ok:` gate at 477. Therefore `clean-pass`
(783-784) and all pin cases run **zero** measured comparisons.

The only case that reaches the measured block is `frozen-measured` (857-881), which
asserts `LG-FROZEN-MEASURED` is *present*. No case has a resolvable `measured_commit`
whose pins match, so a regression that emits `LG-FROZEN-MEASURED` for every pin it
compares (false positive, e.g. inverted comparison at 491) passes all 18 cases.

Smallest fix: build `clean-pass` in two commits — commit pinned bytes, then a second
commit that rewrites only `expected.json` with `measured_commit` = first commit and the
same pins — so the clean run proves a matching measured check emits nothing.

### F3 (medium) — `frozen-measured` cannot distinguish "absent at measured" from "hash differs"
Case 857-881: `old_rev` is created with only `tools/good.sh = "old-good-bytes\n"`
(864); `data.txt` never exists at `old_rev`. At `rev`, `data.txt` is present. So the
finding set contains `data.txt` absent-at-measured (branch 482-488) **and**
`tools/good.sh` digest-differs (branch 491-503). Removing either branch body still
leaves the other, so the case passes; it binds the id, not the comparison. The same
holds for truncating the measured loop to its first key (`data.txt` alone fires).

Smallest fix: at `old_rev`, also write `data.txt` with the bytes it has at `rev`, so
only the mismatch branch (491) can fire; keep a second case for the absent branch.

### F4 (medium) — `carried-resolved` tests bold decor only through a zero-finding assertion
Case 902-912: the marker is `**STATUS:** FAILED — guard refuses` (904) and the assertion
is exit 0 (912). If `STATUS_PREFIX_RE` (71) lost bold acceptance, `status_value()`
(250-255) returns `None`, no failure line is seen, `ids=[]`, and the case still passes.
No selftest case positively asserts a bold STATUS line is a failure channel:
`uncarried-marker` (883-889) and `open-admitted` (914-923) both use `## STATUS:`.
(`carried-open` at 891-900 is not affected in this way: dropping the `\bopen\b` carry
token at 83 turns the case into `LG-SEAT-UNCARRIED` and it fails.)

Smallest fix: add one positive bold case (bold STATUS failure, no lesson line) expecting
`LG-SEAT-UNCARRIED`.

Compensating coverage: fixture 392-408 requires `LG-SEAT-UNCARRIED` for SeatA
(`**STATUS:** INCOMPLETE`).

### F5 (minor) — `forbid_ids` is dead; two expected-id worlds carry extra findings
`check()` declares `forbid_ids=()` at 766 and applies it only at 771; no call site
passes it (784, 790, 796, 802, 810-817, 839, 847, 855, 881, 889, 900, 912, 923, 929,
939). Consequently no case can assert an id is *absent*, and extra findings are invisible.

Observed live (run output): `nonparsing-cited-sh` returns
`['LG-FROZEN-PIN', 'LG-PARSE-REG']`; `changed-nonparsing-with-base` returns three ids.
Cause: `_frozen_world` pins `tools/good.sh` from `GOOD_SH` (720-736) and 788 then
overwrites the bytes with `BAD_SH`, so the sh case's world is dirty by construction
(pins frozen before the mutation). The named ids are still genuinely asserted, but the
case cannot attribute them narrowly.

Smallest fix: reorder 786-788 so `_frozen_world` runs after the byte swap (pins match
apart from the parse defect); use `forbid_ids` in the parse cases to assert no carry/pin
leak.

Dead structures of the same kind: `cases = []` (750) never appended;
`_frozen_world(record_extra=…)` (716, 726-727) never passed a value.

### F6 (minor) — exit-2 cases assert only the exit class
`missing-wave-dir` (925-929), `bad-rev` (941-949), `no-skill` (951-966) assert only
`res["exit"] == 2`. The distinguishing error strings exist — 314
`no .md reports under …`, 166 `cannot resolve revision …`, 536 `no SKILL.md …` — and are
printed in `err=` (772) but never compared. Any `EvalError` path satisfies the case.

Smallest fix: assert the error substring for each.

## What holds (positive verification)

- 18/18 reproduced, byte-identical file at HEAD, exit 0.
- Ten id-bearing cases assert real membership (766-771), and `LG-PARSE-REG`,
  `LG-MISSING-REG`, `LG-PARSE-CHANGED`, `LG-FROZEN-PIN`, `LG-FROZEN-MEASURED`,
  `LG-SEAT-UNCARRIED`, `LG-OPEN-ADMITTED` are each bound to at least one case:
  - `LG-PARSE-REG` 786-796; `LG-MISSING-REG` 798-802 (missing must not surface as parse);
  - `LG-PARSE-CHANGED` and `LG-PARSE-REG` together at 810-817;
  - `LG-FROZEN-PIN` via three distinct causes — mismatch 833-839, absent path 841-847,
    `record_sha256` 849-855 — each case fails (exit 0) if its branch is removed, because
    no other cause exists in that world;
  - `LG-FROZEN-MEASURED` 857-881 (id bound; branch conflation is F3);
  - `LG-SEAT-UNCARRIED` 883-889 (detector-dead and matcher-always-true both fail it);
  - `LG-OPEN-ADMITTED` 914-923 (a `\bopen\b` regression degrades it to
    `LG-SEAT-UNCARRIED`, i.e. fails).
- `uncited-nonparsing-not-flagged` (819-831) is a genuine negative control: exit 0
  requires `findings == []` (585), and `tools/uncited-bad.sh` is present but uncited.
- `clean-pass` (783-784) requires exit 0, i.e. globally zero findings, so spurious
  emission from any channel breaks it — except the measured channel, which never runs
  (F2).

## Residual risk (ordered)

1. F2: a false-positive `LG-FROZEN-MEASURED` would ship with 18/18 green. This is the
   only surviving defect with direct landing-gate consequence.
2. F1/F4: selftest-local blind spots are compensated by the fixture (source-cited above)
   *if* the fixture is part of measured C2 evidence; I did not execute the fixture
   (sibling seat's item).
3. F3/F5: id-level binding is honest; branch-level and absence assertions are absent.

## Verification gaps

- No mutation testing performed: only the ALLOWED-EXEC command was run. Survivor claims
  in F1/F2/F3/F4 are static control-flow derivations from the cited lines.
- Fixture suite (`tests/fixtures/r16-landing-gate.py`) not run; its 15-case result is
  taken from the wave-1 claim, not re-measured here.

## Commands

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-landing-gate.py && wc -l tools/souji-landing-gate.py && git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain | head -50
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --selftest; echo "EXIT=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --quiet HEAD -- tools/souji-landing-gate.py && echo "WORKTREE_EQ_HEAD" ; git log -1 --format='%H %s' -- tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -e 'forbid_ids' -e 'record_extra' -e 'cases = ' -e 'cases.append' -e 'in_fence or in_table' -e 'CASE fenced' -e 'syntax error inside' -e 'snapshot_tampered' -e 'carried-resolved' -e 'marker = ' -e 'CASE frozen-measured' -e 'CASE open-admitted' -e 'CASE uncarried' -e 'CASE carried-open' -e 'def is_failure_line' -e 'def seat_failure_lines' -e 'def check(' -e 'ok = ' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -e 'STATUS' -e 'fence' -e 'table' -e 'bold' -e '\*\*STATUS' tests/fixtures/r16-landing-gate.py | head -60; echo ---; wc -l tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -e 'landing-gate' -e 'selftest' -e 'fixture' census/round-16/run-matrix.py | head -40; echo ---; grep -n -e 'carried-open' -e 'carried-resolved' -e 'fenced-and-table' -e 'uncarried-marker' -e 'open-admitted' -e 'frozen-measured' -e 'record-sha256' -e 'pin-missing' -e 'pin-mismatch' -e 'no-wave-dir' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -e '^    case(' -e 'def case' -e 'need=' -e 'absent=' tests/fixtures/r16-landing-gate.py | head -40; echo ---; grep -c '^    case(' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -e '"measured_commit": "0"' -e 'blob is None' -e 'elif sha256(blob) != pinned' -e 'measured_ok = verify.returncode' -e 'if record_bytes :=' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -e 'check("nonparsing-cited-sh"' -e 'check("nonparsing-cited-py"' -e 'check("missing-cited-path"' -e 'check("changed-nonparsing-with-base"' -e 'check("clean-pass"' -e 'bad-rev' -e 'no-skill' -e 'ok = res\["exit"\] == 2' -e 'f\["tools/good.sh"\] = BAD_SH' -e 'extra_commits=' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -e 'result\["exit"\] = 1 if findings' -e 'findings.sort' -e 'raise EvalError("no .md reports' -e 'raise EvalError("no SKILL.md' -e 'cannot resolve revision' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -e 'LG-PARSE-CHANGED' -e 'base=commits\[0\]' -e 'rev=commits\[1\]' -e 'check($' tools/souji-landing-gate.py
```

STATUS: PARTIAL — 18/18 reproduced and the ten named ids are genuinely asserted, but fenced-and-table-ignored exercises neither fence nor table, and two cases pass with the named mechanism dead (no clean measured check; bold-only resolved carry).
