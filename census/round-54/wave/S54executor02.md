# S54executor02 — C2 v3 matrix + acceptance arms, independent reproduction

Seat: **S54executor02** (executor, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Read first: `census/round-54/preregistration.txt` (freeze commit `3c394cab0cd406bbab72b8d365e0f3deed4ef98a`).
Lane HEAD at run: `bfdbb336329e6afba3ab1ca83cbd6d9759271062`.
Scratch: `/fast/scratch/hyaku/souji-r54/S54executor02/` (deleted before yield; every receipt below was copied into `results/` first).
No file outside this seat directory was written; no lane file, index, jj state, or fleet path was modified. Read-only git only (`rev-parse`, `show`, `log`, `merge-base`, `ls-files`), `GIT_OPTIONAL_LOCKS=0` on every call against a repo I do not own. No tool install or upgrade this seat (python3 stdlib + git only).

## Verdict

**PASS.** 10/10 C2 matrix cells **AGREE** with `census/round-54/records/c2-selftest-expected.tsv`; **0 DISAGREE**. Every acceptance arm behaves exactly as preregistration C2 states: v2 accepts FA4/FA5 (rc 0), FA6 shows the named-class pair (v2 first line spurious `CAPTURE-RECEIPT-MISMATCH`, v3 `FINDING CAPTURE-CRLF` first), the `--tool-sha256` pin refuses on wrong bytes and passes on the fixture's stub digest, and the real-lane run at `bfdbb336` exits 0 with `receipt=ok sorted=ok tool_pin=ok`. No defect was found; nothing was edited (the counters are byte-frozen by rule).

## 1. Instrument pins (observed — all equal the frozen pins)

`results/pins.txt`:

```
84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09  census/round-54/c2-counter.py
e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d  census/round-54/records/c2-selftest-expected.tsv
ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba  census/round-54/fixtures/build-fixtures.py
f9d277636d6642de7b287678a145e8916f84f0c9cba00f4768aa16feaca80799  census/round-54/fixtures/run-matrix.sh
6515b97553dd6f6d207d638de2520c4367a56a1a37ff7329b9d914c329a349b7  census/round-53/c2-counter.py
```

v3 counter `84b05295…` = prereg C2 pin. Expected TSV `e32f79…` = prereg population pin. Builder `ae5881…` and run-matrix `f9d277…` = prereg instrument pins. The v2 acceptance control `6515b975…` = the pin frozen in `census/round-53/preregistration.txt:158` (so the v2 arm I ran is the frozen r53 bytes).

```
$ GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
bfdbb336329e6afba3ab1ca83cbd6d9759271062
```

## 2. Fixtures built (own scratch, pinned-date builder)

```
$ S=/fast/scratch/hyaku/souji-r54/S54executor02; mkdir -p "$S/work"
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && TMPDIR="$S" python3 -B \
    census/round-54/fixtures/build-fixtures.py --work "$S/work" --manifest "$S/fixture-manifest.tsv"
BUILT F1-HONEST-TIP tip=55b56e65f805f850dc6e2d966b3f3131da33697b
…
BUILT FH-HONEST tip=81c9f21461bf315dcbd062ee47c30ee94d4f7a27
BUILT FH2-SYMLINK-HONEST tip=6815d46eee0f29c663fdaaf6c55b14ab934db13e
BUILT FA1-UNSORTED tip=0a1de12e2395e120ba8190b503f69042aff8c222
BUILT FA2-COMMENT tip=8b035bcf681f0f98dd3eee55639e6e55cd4541f7
BUILT FA3-TAMPER tip=9be703f0c77cccb1c4841a2c06c0f79ae31d44c5
BUILT FA4-SPACE-NAME tip=e0aabc60013d3b7b435a55db03b191937989b916
BUILT FA5-EXTRA-KEY tip=2a6fdc6df02bd026e67adc267f17ddeeb8a5d8ac
BUILT FA6-CRLF tip=17c582af6c10aa2815b7524253e698ca12fbb375
BUILT FA7-RECEIPT-ENTRIES tip=4fe9b56993d97ce6f3a2027f458ab9d45737748b
BUILT FA8-SYMLINK-CLASS tip=e5900e5c500019ffdc022b616c278ef62a99f093
MANIFEST /fast/scratch/hyaku/souji-r54/S54executor02/fixture-manifest.tsv
rc=0
```

(23 fixtures total: the 13 C1 fixtures and the 10 C2 fixtures; full manifest in `results/fixture-manifest.tsv`. The builder asserts `git rev-parse --show-toplevel == <fixture dir>` before committing and pins `GIT_AUTHOR_DATE/GIT_COMMITTER_DATE`, so the C2 tips reproduce.)

**Rev determinism reproduced independently:** my 10 C2 tips are byte-identical to the L1's `census/round-54/records/fixture-manifest.tsv` C2 rows — the only diff is the absolute scratch dir (`…/matrix-final/selftest/…` vs `…/S54executor02/work/…`). Base = tip for every C2 fixture (single-commit fixtures).

## 3. v3 counter over every C2 fixture — rc + first FINDING

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ TMPDIR="$S" python3 -B census/round-54/c2-counter.py --root "$S/work/<n>" --rev <tip> \
    --capture census/round-52/records/fleet-root-census.tsv \
    --receipt census/round-53/records/fleet-root-census-run.txt --scratch "$S"
```

| fixture | rev (12) | exit | first FINDING |
|---|---|---|---|
| FH-HONEST | 81c9f21461bf | 0 | – |
| FH2-SYMLINK-HONEST | 6815d46eee0f | 0 | – |
| FA1-UNSORTED | 0a1de12e2395 | 1 | ROWS-UNSORTED |
| FA2-COMMENT | 8b035bcf681f | 1 | COMMENT-AMBIGUOUS-NAME |
| FA3-TAMPER | 9be703f0c77c | 1 | CAPTURE-RECEIPT-MISMATCH |
| FA4-SPACE-NAME | e0aabc60013d | 1 | COMMENT-AMBIGUOUS-NAME |
| FA5-EXTRA-KEY | 2a6fdc6df02b | 1 | RECEIPT-UNKNOWN-KEY |
| FA6-CRLF | 17c582af6c10 | 1 | CAPTURE-CRLF |
| FA7-RECEIPT-ENTRIES | 4fe9b56993d9 | 1 | CAPTURE-RECEIPT-MISMATCH |
| FA8-SYMLINK-CLASS | e5900e5c5000 | 1 | – (class_mismatch=1; expected-file wildcard) |

Raw outputs: `results/v3-<fixture>.txt`; matrix: `results/v3-matrix.tsv`.

## 4. Cell-by-cell comparison (expected TSV vs observed)

`results/c2-compare.tsv`:

```
name                 expect_exit  expect_finding            got_exit  got_finding               verdict
FH-HONEST            0            -                         0         -                         AGREE
FH2-SYMLINK-HONEST   0            -                         0         -                         AGREE
FA1-UNSORTED         1            ROWS-UNSORTED             1         ROWS-UNSORTED             AGREE
FA2-COMMENT          1            COMMENT-AMBIGUOUS-NAME    1         COMMENT-AMBIGUOUS-NAME    AGREE
FA3-TAMPER           1            CAPTURE-RECEIPT-MISMATCH  1         CAPTURE-RECEIPT-MISMATCH  AGREE
FA4-SPACE-NAME       1            COMMENT-AMBIGUOUS-NAME    1         COMMENT-AMBIGUOUS-NAME    AGREE
FA5-EXTRA-KEY        1            RECEIPT-UNKNOWN-KEY       1         RECEIPT-UNKNOWN-KEY       AGREE
FA6-CRLF             1            CAPTURE-CRLF              1         CAPTURE-CRLF              AGREE
FA7-RECEIPT-ENTRIES  1            CAPTURE-RECEIPT-MISMATCH  1         CAPTURE-RECEIPT-MISMATCH  AGREE
FA8-SYMLINK-CLASS    1            -                         1         -                         AGREE
---
AGREE=10 DISAGREE=0
```

Beyond the two expected columns, my 10 observed `SUMMARY` lines are **byte-identical** to the SUMMARY column of the L1's `census/round-54/records/c2-matrix-v3.tsv` (`diff` empty over 10 lines: `results/my-summaries.txt` vs `results/l1-summaries.txt`).

## 5. Acceptance arms with the FROZEN v2 counter (before-state)

```
$ TMPDIR="$S" python3 -B census/round-53/c2-counter.py --root "$S/work/FA4-SPACE-NAME" --rev e0aabc60013d3b7b435a55db03b191937989b916 \
    --capture census/round-52/records/fleet-root-census.tsv \
    --receipt census/round-53/records/fleet-root-census-run.txt --scratch "$S"
SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok rev=e0aabc60013d
rc=0
```

```
$ … --root "$S/work/FA5-EXTRA-KEY" --rev 2a6fdc6df02bd026e67adc267f17ddeeb8a5d8ac …
SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok rev=2a6fdc6df02b
rc=0
```

Both match the control file rows (3) and the L1's `c2-matrix-v2.tsv` FA4/FA5 rows.

### The FA6 named-class pair

**v2 (frozen r53 counter) — full finding list, exit 1** (`results/v2-FA6-CRLF.txt`; 18 `FINDING` lines, first line spurious):

```
FINDING CAPTURE-RECEIPT-MISMATCH TOOL_SHA256 receipt=f509d0cb0d6d tool=f509d0cb0d6d capture=-
FINDING CAPTURE-RECEIPT-MISMATCH FLEET_HEAD receipt=0123456789ab capture=-
FINDING CAPTURE-RECEIPT-MISMATCH ENTRIES receipt=3 capture=- rows=3
FINDING column header mismatch
FINDING disposition 'none\r' for 'a.txt'
FINDING disposition 'none\r' for 'b.md'
FINDING disposition 'none\r' for 'zz'
FINDING missing header TOOL_SHA256
FINDING missing header FLEET_HEAD
FINDING missing header ENTRIES
FINDING TOOL_SHA256 None != tool bytes f509d0cb0d6d505cfb3a2358534ce90425d8de8fc7d75e1aa024346c0fbfe0fc
FINDING FLEET_HEAD not 40-hex
FINDING TOOL_SHA256 not 64-hex
FINDING COUNT tracked declared None recomputed 2
FINDING COUNT ignored declared None recomputed 1
FINDING COUNT untracked-stray declared None recomputed 0
FINDING COUNT symlink declared None recomputed 0
FINDING COUNT class set [] != ['ignored', 'symlink', 'tracked', 'untracked-stray']
SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=FAIL tool_sha=FAIL removal_proposed=3 receipt=FAIL sorted=ok rev=17c582af6c10
```

**v3 on the same fixture — exit 1, `CAPTURE-CRLF` first** (`results/v3-FA6-CRLF.txt`; 19 `FINDING` lines = the named class + the same 18 cascade lines):

```
FINDING CAPTURE-CRLF capture bytes carry CR (carriage return)
FINDING CAPTURE-RECEIPT-MISMATCH TOOL_SHA256 receipt=f509d0cb0d6d tool=f509d0cb0d6d capture=-
…
FINDING COUNT class set [] != ['ignored', 'symlink', 'tracked', 'untracked-stray']
SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=FAIL tool_sha=FAIL removal_proposed=3 receipt=FAIL sorted=ok tool_pin=n/a rev=17c582af6c10
```

The operative pair holds: v2's first line is a spurious `CAPTURE-RECEIPT-MISMATCH` (header keys unreadable because of CR), v3 names `CAPTURE-CRLF` first.

## 6. `--tool-sha256` argument pin

Fixture stub tool digest in FH-HONEST: `f509d0cb0d6d505cfb3a2358534ce90425d8de8fc7d75e1aa024346c0fbfe0fc` (`git show <tip>:tools/souji-fleet-root-census.py | sha256sum`).

Wrong pin, all zeros (`results/pin-wrong.txt`):

```
FINDING TOOL-SHA-ARG-MISMATCH pinned=000000000000 observed=f509d0cb0d6d
SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=FAIL rev=81c9f21461bf
rc=1
```

Correct pin (`results/pin-correct.txt`):

```
SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=81c9f21461bf
rc=0
```

Extra robustness probe (non-64-hex pin): `--tool-sha256 zz` → `CANNOT-EVALUATE --tool-sha256 must be 64-hex`, **rc=2** (refuses rather than crashing).

## 7. Real-lane run at the capture commit

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-54/c2-counter.py --root . \
    --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062 \
    --capture census/round-54/records/fleet-root-census.tsv \
    --receipt census/round-54/records/fleet-root-census-run.txt \
    --tool-sha256 e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b \
    --scratch /fast/scratch/hyaku/souji-r54/S54executor02
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=bfdbb336329e
rc=0
```

Matches `census/round-54/records/c2-tip.txt` (`EXIT=0`) line for line. Independent digest re-derivation at the same rev (`results/real-lane-digests.txt`):

```
e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b  -   (tools/souji-fleet-root-census.py at bfdbb336)
45e1cf0c28cf713424c10c503404d63378591aa69e762c3802af98f34a40f143  -   (fleet-root-census-run.txt at bfdbb336)
0c3f42e000e00fd8165e99aee5d42908ccd63cdc3d7461ca840fb1f22f09e1f9  -   (fleet-root-census.tsv at bfdbb336)
```

The receipt's `CAPTURE_SHA256=0c3f42e0…` equals the committed capture's digest, and `FLEET_HEAD=3b0d5329147d3b05d3aec5e908c75405ae3bc05a` is the captured fleet HEAD stated in the dispatch.

## 8. Observations — reported, not fixed (counters are byte-frozen)

- **O1 (freshness, disclosed limit).** At my run the fleet root HEAD is `643cb2db74dcefbf9a5350199d660897d4762286`; the captured `3b0d5329…` is an ancestor (`git merge-base --is-ancestor` rc 0; `3b0d5329 round-70: hyaku closure dispatch for kake`, `643cb2db round-65: hyaku closure dispatch for kengaku`). The counter format-checks `FLEET_HEAD` only, so this is inside the prereg's named limits — but integration should say plainly that the round-54 capture is a point-in-time take at `3b0d5329`, not the fleet tip at claim time.
- **O2 (cascade volume / wording).** v3 does not suppress the v2 cascade; it prepends the named class. Measured: 18 `FINDING` lines on FA6 under v2, 19 under v3. The prereg/control prose "six misleading findings" matches the misleading *classes*, not the emitted line count — an observation about wording precision, not a claim failure (the operative test holds).
- **O3 (branch coverage gap).** The counter implements `RECEIPT-CRLF` alongside `CAPTURE-CRLF`, but no committed fixture exercises the receipt-side class. A seat-scratch probe (fresh fixture I created this seat: FH-HONEST bytes with only the run receipt converted to CRLF, committed in my own scratch repo `RC-r38I`, rev `bd770a6223eb0c2dd874f472a47bf6b824f66f75`) gives `FINDING RECEIPT-CRLF receipt bytes carry CR (carriage return)` first, `receipt=ok`, rc 1 — the branch works, it is simply uncovered. Candidate next-round branch-coverage fixture, parallel to the r53 M-F1/M-F2 rationale. Evidence: `results/receipt-crlf-probe.txt`.
- **O4 (FA8 expectation is a wildcard).** `FA8-SYMLINK-CLASS`'s expected finding is `-`, i.e. exit 1 with the finding id unconstrained (the selftest's `want_find in ('', '-')` branch). Observed failure is `class_mismatch=1` with no named id. The row pins the kill but not a class name.
- **O5 (builder double-`#`).** The FA2/FA4 hidden row is emitted as `##odd name\t…` because the builder prepends `#` to a name that already starts with `#`. The v3 kill comes from the `>=5 tabs` data-shaped rule (`FINDING COMMENT-AMBIGUOUS-NAME comment shaped like a data row (>=5 tabs): '##odd name\tfile\tno\tno\tuntracked-stray\treport-only'`), not from the counter's separate `name.startswith('#')` bad-name rule. No claim impact; noted so a future builder does not mistake the double `#` for the name grammar.
- **O6 (tooling).** None installed or upgraded; `python3` (stdlib only) and `git` used as found.

Nothing was edited in `census/`, `tools/`, `tests/`, `corpus/`, `SCORECARD.md`, `LOG.md`, `SKILL.md`, `PROVINCE.md`; no commit/add/stash/checkout/reset/pull/push and no jj mutation ran anywhere. All fixture commits happened inside repos created this seat under `/fast/scratch/hyaku/souji-r54/S54executor02/` with the toplevel asserted and in-fixture identity.

## 9. Receipts (all under `results/`)

```
c2-compare.tsv            the 10 AGREE rows
v3-matrix.tsv             fixture -> exit -> first finding
v3-<10 fixtures>.txt      full v3 outputs
v2-FA4-SPACE-NAME.txt     v2 acceptance arm rc 0
v2-FA5-EXTRA-KEY.txt      v2 acceptance arm rc 0
v2-FA6-CRLF.txt           v2 cascade (18 FINDING lines)
pin-wrong.txt             TOOL-SHA-ARG-MISMATCH rc 1
pin-correct.txt           tool_pin=ok rc 0
real-lane.txt             real-lane command + SUMMARY + rc 0
real-lane-digests.txt     independent sha256 of tool/receipt/capture at bfdbb336
receipt-crlf-probe.txt    RECEIPT-CRLF branch probe (uncovered branch)
pins.txt                  counter/builder/expected hashes + HEADs + capture header
fixture-manifest.tsv      my 23 built fixtures (C2 tips identical to L1 manifest)
my-summaries.txt / l1-summaries.txt   the two SUMMARY columns that diff empty
```
