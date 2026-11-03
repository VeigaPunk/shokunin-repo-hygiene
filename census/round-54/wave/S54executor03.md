# S54executor03 — r54 w1 standing receipts at the capture commit

Seat: S54executor03 (executor). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Measured revision: `bfdbb336329e6afba3ab1ca83cbd6d9759271062` (lane tip == capture commit;
verified `git rev-parse HEAD`). Frozen claims read first: `census/round-54/preregistration.txt`
(freeze commit `3c394cab0cd406bbab72b8d365e0f3deed4ef98a`).
Scratch: `/fast/scratch/hyaku/souji-r54/S54executor03/` (deleted before yield; receipts copied here).
Tooling installed/updated: none (no pacman, uv, npx or binary install was needed).

All commands ran with `GIT_OPTIONAL_LOCKS=0` and `TMPDIR=/fast/scratch/hyaku/souji-r54/S54executor03`,
from `/home/vgpnk/Projects/shokunin/souji-shokunin`. Every receipt file below is the verbatim
stdout+stderr of one run followed by its `rc=` line; each carries its own `## command:` header.

## Verdict table

| # | check | receipt | rc | verdict |
|---|---|---|---|---|
| 1a | r53 c1-counter at tip (v2-arm control, real lane) | `standing-r53-c1.txt` | 0 | GREEN filed=2 unfiled=0 |
| 1b | r53 c2-counter at tip (v2-arm control, real lane) | `standing-r53-c2.txt` | 0 | GREEN receipt=ok sorted=ok |
| 2a | r52 c1-counter at tip | `standing-r52-c1.txt` | 0 | GREEN filed=2 |
| 2b | r52 c2-counter at tip | `standing-r52-c2.txt` | 0 | GREEN |
| 3a | r51 c1-counter at tip | `standing-r51-c1.txt` | 0 | GREEN |
| 3b | r51 c2-counter at tip | `standing-r51-c2.txt` | 0 | GREEN |
| 4a | v3 c1 selftest, pinned | `selftest-c1-pinned.txt` | 0 | GREEN `SELFTEST pass cases=13` |
| 4b | v3 c2 selftest, pinned | `selftest-c2-pinned.txt` | 0 | GREEN `SELFTEST pass cases=10` |
| 5a | v3 c1 negative pin (all-zeros) | `negpin-c1.txt` | 2 | GREEN (refusal as specified) |
| 5b | v3 c2 negative pin (all-zeros) | `negpin-c2.txt` | 2 | GREEN (refusal as specified) |
| 6 | census v1 receipt verify | `census-receipt-verify.txt` | 0 | GREEN `VERIFY ok` |
| S1 | v3 c1 real lane at tip (prereg recompute command) | `v3-reallane-c1.txt` | 0 | GREEN, claim-state |
| S2 | v3 c2 real lane at tip (prereg recompute command) | `v3-reallane-c2.txt` | 0 | GREEN, claim-state |
| S3 | v2-arm acceptance on the NEW attack fixtures (independent re-take) | `v2arm-probe.txt` | 0 | GREEN 9/9 control rows reproduced |
| S4 | instrument/fixture/capture sha256 pin audit | `pins-sha256.txt` | 0 | GREEN, all pins equal prereg |

Assigned standing receipts: 11/11 green (items 1–6, with 5's two exits=2 being the specified
refusal). No assigned standing check is red.

## 1. r53 counters at the tip (before-state control arms)

`standing-r53-c1.txt`:
```
## command: python3 -B census/round-53/c1-counter.py --root . --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062 --base fe12daad2549f534650d406ebdbac9113d59313f --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 recomputed=79 rev=bfdbb336329e base=fe12daad2549
rc=0
```
`standing-r53-c2.txt`:
```
## command: python3 -B census/round-53/c2-counter.py --root . --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062 --capture census/round-53/records/fleet-root-census.tsv --receipt census/round-53/records/fleet-root-census-run.txt
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok rev=bfdbb336329e
rc=0
```

## 2. r52 counters at the tip

r52 c1 takes `--root --rev [--scratch]` (read from its argparse). r52 c2's frozen CLI is
`--root --rev [--scratch]` only — it has **no `--capture` flag** (the capture path is compiled in
as `census/round-52/records/fleet-root-census.tsv`). The prompt's suggested `--capture` form is
rejected: see `standing-r52-c2-promptflag.txt`
(`c2-counter.py: error: unrecognized arguments: --capture ...`, rc=2) — procedure/interface
mismatch, not a lane defect. Correct invocation:

`standing-r52-c1.txt`:
```
## command: python3 -B census/round-52/c1-counter.py --root . --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record=census/round-51/records/ws-drift-vs-r46.tsv recomputed=79 rev=bfdbb336329e
rc=0
```
`standing-r52-c2.txt`:
```
## command: python3 -B census/round-52/c2-counter.py --root . --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok rev=bfdbb336329e
rc=0
```

## 3. r51 counters at the tip

The r51 counters need `--base-rev` and `--scratch`; `census/round-51/c1-arms.tsv` pins the base
`d1b8734d835171c7329225fdaab249c5c6799de8` (the r50 spot-check commit; same value
`census/round-53/records/standing-tip.txt` used at the r53 tip). **Procedure note:** both r51
counters open `<scratch>/c1-last-run.txt` / `c2-last-run.txt` without creating the directory; my
first run passed a non-existent scratch dir and died post-SUMMARY with
`FileNotFoundError: .../r51c1/c1-last-run.txt` (rc=1) *after* printing the green SUMMARY. That is
my procedure (scratch dir not pre-created), not a standing-check failure — with `mkdir -p` both
are rc=0, as below (and as the r53 `standing-tip.txt` receipt records).

`standing-r51-c1.txt`:
```
## command: python3 -B census/round-51/c1-counter.py --root . --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062 --base-rev d1b8734d835171c7329225fdaab249c5c6799de8 --scratch /fast/scratch/hyaku/souji-r54/S54executor03/rt-r51c1
SUMMARY corr=ok dup=ok ntfs=ok listing=ok corr_lines=1 dup_base=2 dup_tip=2
rc=0
```
`standing-r51-c2.txt`:
```
## command: python3 -B census/round-51/c2-counter.py --root . --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062 --base-rev d1b8734d835171c7329225fdaab249c5c6799de8 --scratch /fast/scratch/hyaku/souji-r54/S54executor03/rt-r51c2
SUMMARY shape=ok drift=ok receipts=ok limit=ok rows=126 added=79 removed=2
rc=0
```
Both SUMMARY lines are byte-identical to `census/round-53/records/standing-tip.txt` (except the
revision is not printed by r51).

## 4. v3 selftests with pins (re-run by this seat)

`selftest-c1-pinned.txt` (tail; full 13 case lines in the receipt):
```
SELFTEST-CASE F1-HONEST-TIP pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE F2-MULTI-ANNOT pass rc=1 want_rc=1 finding=MULTIPLE-ANNOTATIONS ...
SELFTEST-CASE F3-INERT pass rc=1 want_rc=1 finding=INERT-CORRECTION ...
SELFTEST-CASE F4-FENCE pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE ...
SELFTEST-CASE F5-REWRITE pass rc=1 want_rc=1 finding=DELETED-LINES ...
SELFTEST-CASE F6-RECORD-DRIFT pass rc=1 want_rc=1 finding=RECORD-SHA-MISMATCH ...
SELFTEST-CASE F7-TILDE-FENCE pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE ...
SELFTEST-CASE F8-BT4-PARITY pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE ...
SELFTEST-CASE F9-HTML-COMMENT pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE ...
SELFTEST-CASE F10-STRADDLE pass rc=1 want_rc=1 finding=ZONE-TOKEN-STRADDLES-EDGE ...
SELFTEST-CASE F11-BOGUS-RECOMP pass rc=1 want_rc=1 finding=BOGUS-RECOMPUTED ...
SELFTEST-CASE F12-LOG-UNFILED pass rc=1 want_rc=1 finding=UNFILED-SOURCES-ANNOTATION ...
SELFTEST-CASE F12b-LOG-FILED pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST pass cases=13
rc=0
```
`selftest-c2-pinned.txt`:
```
SELFTEST-CASE FH-HONEST pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE FH2-SYMLINK-HONEST pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE FA1-UNSORTED pass rc=1 want_rc=1 finding=ROWS-UNSORTED ...
SELFTEST-CASE FA2-COMMENT pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME ...
SELFTEST-CASE FA3-TAMPER pass rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH ...
SELFTEST-CASE FA4-SPACE-NAME pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME ...
SELFTEST-CASE FA5-EXTRA-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY ...
SELFTEST-CASE FA6-CRLF pass rc=1 want_rc=1 finding=CAPTURE-CRLF ...
SELFTEST-CASE FA7-RECEIPT-ENTRIES pass rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH ...
SELFTEST-CASE FA8-SYMLINK-CLASS pass rc=1 want_rc=1 finding=class ...
SELFTEST pass cases=10
rc=0
```
Both runs were given `--builder-sha256 ae5881f8...b1ba` and their respective
`--expected-sha256` (`4e73c495...a1c7` / `e32f7934...c00d`); both pins match the prereg
(`pins-sha256.txt`), and the pin check runs before exec (item 5 shows it can refuse).

## 5. Negative pin control (both selftests, all-zeros expected pin)

`negpin-c1.txt`:
```
CANNOT-EVALUATE PIN-MISMATCH expected sha256 4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7 != pinned 0000000000000000000000000000000000000000000000000000000000000000
rc=2
```
`negpin-c2.txt`:
```
CANNOT-EVALUATE PIN-MISMATCH expected sha256 e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d != pinned 0000000000000000000000000000000000000000000000000000000000000000
rc=2
```
Both refuse **before** any fixture build (no fixture dirs created under the negpin work dirs),
which is the r53 sentinel-S4 fix behaving.

## 6. Census v1 receipt verify

`census-receipt-verify.txt`:
```
## command: python3 tools/souji-census-receipt.py verify --receipt census/round-54/records/census-before-receipt.txt
VERIFY ok receipt=census/round-54/records/census-before-receipt.txt lane=souji conf_rc=0 dir_rc=0 w04=61 result=ok checks=grammar,digest,raw-section,rc,w04,result,adapter-sha adapter=ok
rc=0
```

## Supplemental S1/S2 — the v3 counters at the real lane tip

Not assigned, but cheap and it is the claim state the L1 integrates; both exit 0 with the exact
flag sets the prereg's recompute commands name (`census/round-54/preregistration.txt` §§C1/C2).

`v3-reallane-c1.txt`:
```
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=bfdbb336329e base=fe12daad2549
rc=0
```
`v3-reallane-c2.txt`:
```
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=bfdbb336329e
rc=0
```
Both match the prereg's claimed SUMMARY token sets verbatim (`tool_pin=ok`, `straddle=0 bogus=0
logunfiled=0 logrecomp=0`).

## Supplemental S3 — independent re-take of the v2-arm before-state on the NEW attack fixtures

Not assigned; this is the "round's before-state" the goal names, measured independently rather
than by reading the control files. I rebuilt all fixtures with the frozen builder (pinned dates,
per-call hardened git) into fresh scratch and ran the **frozen r53 counters** against them.

`v2arm-probe.txt` (compact, all lines):
```
V2C1 F1-HONEST-TIP        tip=55b56e65f805 rc=0 findings=- SUMMARY ... filed=2 unfiled=0
V2C1 F7-TILDE-FENCE       tip=2daa874557c2 rc=0 findings=- SUMMARY ... fenced=0
V2C1 F8-BT4-PARITY        tip=5a0fafb73fe6 rc=0 findings=- SUMMARY ... fenced=0
V2C1 F9-HTML-COMMENT      tip=fafd3a2e582f rc=0 findings=- SUMMARY ... fenced=0
V2C1 F10-STRADDLE         tip=aa36dab9c2ca rc=0 findings=- SUMMARY ... (no straddle token in v2)
V2C1 F11-BOGUS-RECOMP     tip=7325d506da78 rc=0 findings=- SUMMARY sites=2 mismatches=1 filed=1 ...
V2C1 F12-LOG-UNFILED      tip=ea328890f5c1 rc=0 findings=- SUMMARY ... unfiled=0
V2C1 F12b-LOG-FILED       tip=2f6ce4b930a0 rc=0 findings=-
V2C2 FH-HONEST            tip=81c9f21461bf rc=0
V2C2 FH2-SYMLINK-HONEST   tip=6815d46eee0f rc=0
V2C2 FA1-UNSORTED         tip=0a1de12e2395 rc=1 findings=ROWS-UNSORTED
V2C2 FA2-COMMENT          tip=8b035bcf681f rc=1 findings=COMMENT-AMBIGUOUS-NAME
V2C2 FA4-SPACE-NAME       tip=e0aabc60013d rc=0 findings=-    <-- v2 accepts (new v3 kill)
V2C2 FA5-EXTRA-KEY        tip=2a6fdc6df02b rc=0 findings=-    <-- v2 accepts (new v3 kill)
V2C2 FA6-CRLF             tip=17c582af6c10 rc=1 findings=CAPTURE-RECEIPT-MISMATCH|... (first line spurious)
V2C2 FA7-RECEIPT-ENTRIES  tip=4fe9b56993d9 rc=1 findings=CAPTURE-RECEIPT-MISMATCH
V2C2 FA8-SYMLINK-CLASS    tip=e5900e5c5000 rc=1 findings=class
```
(Full SUMMARY strings are in the receipt; the elisions above are marker-trimmed only.)

Findings:
- **v2 accepts every NEW C1 attack** F7–F12 (rc=0, no finding) — the claimed work is not vacuous.
  F11 is the disclosed *silent* acceptance (`sites=2 mismatches=1 filed=1`, no finding: the site
  match masks the bogus recomputed) and matches the control's disclosure.
- **v2 accepts FA4 and FA5** (rc=0) — the two new-acceptance C2 attacks; v3 refuses both
  (`COMMENT-AMBIGUOUS-NAME`, `RECEIPT-UNKNOWN-KEY`, from the pinned selftest).
- v2 rejects FA6/FA7/FA8 and keeps FH/FH2 green — matches the control's branch-coverage disclosure.
- **Fixture-rev reproducibility:** rebuilt tips equal the revs embedded in
  `census/round-54/controls/{c1,c2}-control-donothing.txt` for all 9 fixture rows present there
  (F7 2daa874557c2, F8 5a0fafb73fe6, F9 fafd3a2e582f, F10 aa36dab9c2ca, F11 7325d506da78,
  F12 ea328890f5c1, F12b 2f6ce4b930a0, FA4 e0aabc60013d, FA5 2a6fdc6df02b) — 9/9 MATCH. This
  covers the prereg standing check "the fixture builder reproduces fixture revs (pinned dates)"
  for every fixture the controls pin.

## Supplemental S4 — pin integrity

`pins-sha256.txt` — every value equals the prereg's instrument pins:
```
f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e  census/round-54/c1-counter.py
84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09  census/round-54/c2-counter.py
ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba  census/round-54/fixtures/build-fixtures.py
4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7  census/round-54/records/c1-selftest-expected.tsv
e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d  census/round-54/records/c2-selftest-expected.tsv
2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30  census/round-51/records/ws-drift-vs-r46.tsv
e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b  tools/souji-fleet-root-census.py
0c3f42e000e00fd8165e99aee5d42908ccd63cdc3d7461ca840fb1f22f09e1f9  census/round-54/records/fleet-root-census.tsv
```
The last value equals the round-54 run receipt's `CAPTURE_SHA256=0c3f42e0...e1f9`, so the
committed capture bytes are the bytes the receipt binds.

## Fresh-capture facts checked (read-only)

- `census/round-54/records/fleet-root-census.tsv` and `fleet-root-census-run.txt` are tracked at
  `bfdbb336329e`; the tip subject is `round-54: C2 capture — fleet-root census re-taken at fleet
  HEAD 3b0d5329 (49 entries, tracked 22 / ignored 22 / untracked-stray 5 / symlink 0), RECEIPT_VERSION=1 ...`.
- Capture header carries `FLEET_HEAD=3b0d5329147d3b05d3aec5e908c75405ae3bc05a`, `ENTRIES=49`,
  `COUNT tracked=22 ignored=22 untracked-stray=5 symlink=0`, all four COUNT lines recomputed by
  the v3 counter as ok.
- `3b0d5329` is present in the fleet repo and is an ancestor of the fleet's current HEAD
  (`643cb2db` at probe time; the fleet moved forward during the wave — other seats' `.scratch/`
  state only, `git status --porcelain` shows 4 `.scratch/` entries, untouched by me). The capture
  is therefore at a real fleet HEAD that was current at take time, per the receipt.
- The capture's title line still says "souji round-52" because the tool bytes are pinned by the
  r52 capture's `TOOL_SHA256`; the round-54 run receipt discloses exactly this. Not a defect.

## Red lines / dead ends

None red among the assigned checks. Three non-green invocations were **procedure/interface**, all
recovered and documented above:
1. r51 c1/c2 first run with a non-existent `--scratch` dir → post-SUMMARY `FileNotFoundError`,
   rc=1; the counters do not `mkdir` their scratch (frozen behaviour; green when it exists).
2. r52 c2 invoked with the prompt's `--capture` flag → argparse exit 2 (the frozen r52 CLI has
   `--root/--rev/--scratch` only).
3. `--capture` probe receipt kept as `standing-r52-c2-promptflag.txt`.

## Risks / blockers

- The fleet root is read-only to this seat; the fleet HEAD advanced during the wave. The capture's
  `FLEET_HEAD` is a take-time value (ancestor of current HEAD) — the L1 should cite it as such.
- v3 C1's real-lane SUMMARY carries `inert=0` but the r53 counter printed `inert=0` too; no
  divergence. The C1 claim's numeric score is out of this seat's scope.
- No external state was modified; no lane tracked file was edited; no git/jj mutation anywhere.

## Scratch disposition

`/fast/scratch/hyaku/souji-r54/S54executor03/` deleted before yield (receipts were copied into
this seat directory first; the shared `/fast/scratch/hyaku/souji-r54/capture/` staging path named
in the round-54 receipt is not mine and was left untouched).
