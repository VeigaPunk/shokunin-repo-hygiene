# SwarmCritic48 — r29 w1, attack on claim C2 (operability)

STATUS: PASS — 17 cheat-state runs in scratch against the frozen counter (plus the base
reproduction); the counter faithfully implements its frozen predicate (base `152/14` reproduced
byte-for-byte) but **13 runs reach `failed=0 uncovered=0 floor_violations=0` while wave evidence
was destroyed, dropped, fabricated or never captured**, and 4 runs are held. C2's numeric target
is not falsified; the kill rule's sufficiency inference is, and it is the round's own
`symlinks.tsv` that turns the prereg's own F2 junk control green.

## Evidence

Counter identity (attacked bytes == committed bytes at the lane tip):

    $ sha256sum <scratch>/counter.py
    5ab641c41459ca72529baa57268eef99bb16b849f92e8bc2b0dd6fd7df3b1b3f
    $ git -C <lane> show b8cb4b31ce80e2e3314b88e85d40ea9873180804:census/round-29/c2-counter.py | sha256sum
    5ab641c41459ca72529baa57268eef99bb16b849f92e8bc2b0dd6fd7df3b1b3f

Base reproduction, scratch clone of the lane, base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`:

    $ python3 -B <scratch>/counter.py --root <scratch>/c --rev 691dd292...92e ; rc=1
    r26 records=1382 failed=152 uncovered=14 floor_violation=0
    r27 records=124 failed=0 uncovered=0 floor_violation=0
    r28 records=75 failed=0 uncovered=0 floor_violation=0
    SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0

Setup per contract: `D=$(mktemp -d /var/tmp/souji-r29-SwarmCritic48.XXXXXX)` then
`git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin "$D/c"`;
`git -C "$D/c" rev-parse --show-toplevel` printed `$D/c` before the first commit; identity only
via `git -C "$D/c" config`. All commits are in that clone (branches `s1`, `atk1`..`atk11`); the
lane was never written except this report. No tool was installed.

## Findings

F1 (ATK-1) **The counter is content-blind.** A capture that truncates every wave file to zero
bytes and re-hashes the manifest to `sha256("")` scores a clean floor: `s1` runs
`failed=0 uncovered=0 floor_violations=0`, rc 0, with `1252` of `1253` r26 regular files, all
`124` r27 and all `75` r28 files zero-byte (`git diff --stat base..s1` = `1466 insertions(+),
312536 deletions(-)`). Location: `census/round-29/c2-counter.py:67-71` compares only
`sha256(committed blob)` against the record; nothing checks size, content or a non-empty
invariant. Smallest safe correction: not a blanket size floor (base already holds 6 zero-byte
r26 files, 2 r27, 1 r28 — a size floor would fail the honest state); require a committed
`counts.tsv` and an `excluded.tsv` digest reconciliation instead (A4/A5 below).

F2 (ATK-2) **The round's own instrument defeats the prereg's F2 junk control.** Prereg line 7
states the control as "drop the failing records only -> uncovered 14 (fails)". Reproduced
exactly: `atk10` (r26 receipt minus the 152 absent records) gives `records=1230 failed=0
uncovered=14`, rc 1. Adding only `symlinks.tsv` — the file C2 introduces — gives `atk11`:
`records=1231 failed=0 uncovered=0 floor_violations=0`, rc 0, with base evidence untouched
(`git diff --stat base..atk11` = 2 files, receipt plus 14-row `symlinks.tsv`). The frozen junk
control therefore no longer bounds the attack it was written for. Location:
`c2-counter.py:73-88` (exemption) and the F2 row of `census/round-29/records/preregistration.txt:7`.
Correction: A4/A5 (count reconciliation), plus re-state the control as "drop records and supply
symlinks.tsv" in the L1's log.

F3 (ATK-3) **`manifest.sha256` need not be a file.** A waves receipt committed as a mode
`120000` symlink whose *target text* is one valid record line verifies: `atk1` prints `r29
records=1 failed=0 uncovered=0 floor_violation=0`, global zeros. Location: `c2-counter.py:42`
matches the path from `ls-tree` without inspecting the mode. Correction: reject unless
`ents[m][0] == '100644'` (the delivered tool writes a regular file, so this is stricter-only).

F4 (ATK-4) **Symlink exemptions need no resolution.** Three r29 evidence entries replaced by
symlinks to `missing/gone1.png`, `missing/gone2.log`, `/nonexistent/e3.tsv` score zeros; all
three targets fail `git cat-file -e` (rc 128). Location: `c2-counter.py:87` compares only the
link blob to the declared target. Correction: do **not** demand resolution — the honest r26 set
contains deliberately dangling links (`vadv54-run/q/led-dangling.tsv -> missing.tsv`,
`led-devnull.tsv -> /dev/null`), so a resolution requirement is not stricter-safe. Demand
instead that each row be accounted in the committed count reconciliation (A4).

F5 (ATK-6) **Duplicate records are last-wins.** A false record line followed by the true one for
the same path scores zeros (`atk4a`); reversed order scores `failed=1` (`atk4b`). So a receipt
may carry false lines undetected and the verdict depends on line order. Location:
`c2-counter.py:63` (`recs[name] = ...` overwrites). Held: 75 duplicate lines for one path yield
`records=1`, so duplicates cannot inflate a floor (`atk4c`) — dedup is strict, only the silent
overwrite is a defect. Correction: a repeated path is a failure, whatever the hashes.

F6 (ATK-8) **A second receipt name is never evaluated.** `manifest2.sha256` holding a
non-verifying receipt for three absent files is recorded in the real manifest as an ordinary
file, so the counter reads it as evidence, not as a receipt: zeros. Location:
`c2-counter.py:42` regex accepts only `manifest.sha256`. Correction: any `*manifest*.sha256` or
any file matching the record-line grammar under a waves dir that is not the manifest is a
failure.

F7 (ATK-9) **A waves directory with no manifest is wholly unexamined.** `atk9` (r29 waves dir
with four files, no manifest) prints no r29 line at all and exits 0 with `manifests=3`. The
prereg's final-tip `manifests=4` is therefore a manual check, not a counter verdict. Location:
`c2-counter.py:42,95` (only `FLOORS` rounds must exist). Correction: every
`census/round-<N>/waves/` directory present at REV must contain `manifest.sha256`. Strict-safety:
base and tip hold exactly rounds 26, 27, 28, each with a manifest (`git ls-tree -r -d` sweep).

F8 (ATK-10) **Rounds past 28 have no floor.** A one-record r29 manifest gives
`floor_violation=0` (`atk8`). Location: `c2-counter.py:23` (`FLOORS` = 26/27/28) and `:90`
(`FLOORS.get(rn, 1)`). Correction: a `--min-records <round>=<n>` option measured at the final
tip only, so the C2 landing measurement (prereg: `manifests=3` there) is unchanged.

F9 (ATK-11) **`excluded.tsv` is opaque.** Dropping three source files and listing them in
`excluded.tsv` scores zeros (`atk7`); rows with fabricated digests (`0` x 64 for a file that
never existed, `sha256("")` for a file claimed `too-large`) and rows with malformed columns also
score zeros (`atk7b`). The counter never opens the file: `grep -nE 'ufo|excluded|summary|SOURCE'
census/round-29/c2-counter.py` returns nothing. Location: `c2-counter.py` reads only
`manifest.sha256` and `symlinks.tsv`. Correction: the delivered tool already writes `# path`,
`sha256`, `reason` rows (`deliver-souji-wave-evidence-capture.sh:523`); require the counter to
parse them, insist on a 64-hex digest and non-empty reason, insist that each excluded path is
absent from the tree, and insist `excluded.tsv` carries its own manifest record (the tool
records it at `:524-525`, so stricter-only).

F10 (ATK-12) **`failed=0` is not a claim about the source.** The counter has no source input
(`--root`, `--rev` only, `:30-31`). Concretely: the r28 receipt holds 75 records against 74
files in `.ufo/waves/round-28` (the receipt adds `summary.tsv`), and `.ufo/waves/round-29` holds
90 files today with no receipt and no comparison. The count line exists only on the tool's
stdout (`deliver-souji-wave-evidence-capture.sh:531`), never in the receipt. `.ufo/waves/` is
gitignored in this lane (`git check-ignore -v` -> `.gitignore:1:.ufo/waves/`), so a
committed-bytes predicate can never read the source directly: only a tool-written, committed
accounting file can carry the source's digests. The stronger check
is computable — the tool's own `check_manifest_and_set` compares names and digests against a set
derived from the source (`:544`) — but the frozen counter deliberately does not, so C2 measures
self-consistency, not capture completeness. This is the tradeoff the canonical judge must accept
or amend; it cannot be fixed without changing the predicate's input surface.

## Attack log

All rows: scratch clone of the lane at `691dd292...92e`, counter bytes `5ab641c4...`; `rc` is the
counter exit code. "zeros" = `failed=0 uncovered=0 floor_violations=0`.

1. ATK-1 `s1` `55758f25c7271f5fe32f588ffb9a7449dae7d3d4` — all r26/r27/r28 wave files truncated
   to zero bytes, receipts re-hashed: rc 0, zeros, `manifests=3`. **Cheat succeeded.**
2. ATK-2 `atk10` `48993e76c6cac2d1b90980a86cb6706112e54475` — drop the 152 absent r26 records
   only: `records=1230 failed=0 uncovered=14`, rc 1 (prereg F2 reproduced; control holds today).
3. ATK-2 `atk11` `8611daf8894554919642b5a50192821ddb77c868` — same drop plus `symlinks.tsv`:
   rc 0, zeros, `records=1231`. **Cheat succeeded; the round's fix disables the control.**
4. ATK-3 `atk1` `3d79b32b54f9b01f1c1730cba8a0e1fa065b4ebe` — `manifest.sha256` is a mode 120000
   symlink whose target text is the record: `r29 records=1 failed=0 uncovered=0`. **Succeeded.**
5. ATK-4 `atk2` `8d62a66e40ba2d26935347ab50e2c09b1a087174` — `symlinks.tsv` row naming a regular
   file: `r29 records=2 uncovered=1`, rc 1. **Held: mode 120000 is required.**
6. ATK-4 `atk2b` `12bcfbf8980f99479dc955122f9c6eef346a25c9` — same row after the path became a
   self-dangling symlink: rc 0, zeros. **Succeeded.**
7. ATK-4 `atk3` `5037159118028b31acab1a8a9f8c3346eda7cefb` — three evidence entries are
   dangling symlinks (`cat-file -e` rc 128 for every target): rc 0, zeros. **Succeeded.**
8. ATK-6 `atk4a` `79875d6a61f238b1ed714a3dde2cb6fdff716f8a` — false hash line first, true line
   second: rc 0, zeros. **Succeeded.** `atk4b` `f8b5ea88...` reversed order: `failed=1`, held.
9. ATK-6 `atk4c` `66d589f60532cc2c4fb1e112aaf10435c011220e` — 75 identical record lines:
   `records=1`, zeros. **No floor inflation; held.**
10. ATK-7 `atk5` `ab12b08f62e3ae258db4d1442affc689b5cb8fe3` — record name
    `../round-28/waves/summary.tsv` with its true sha256: `failed=1`, rc 1. **Held: traversal
    rejected.**
11. ATK-8 `atk6` `460fafdbdaa97343a888b6b35b5b6a3cd90f2dc9` — non-verifying receipt parked as
    `manifest2.sha256`, recorded as a file: rc 0, zeros. **Succeeded.**
12. ATK-11 `atk7` `36446faae80b249df1fd74e17c51b10bb66f579c` — three source files absent, listed
    in `excluded.tsv` with no digest: rc 0, zeros. `atk7b` `a3878734...` fabricated digests and
    `28b5b311...` malformed rows: rc 0, zeros. **Succeeded.**
13. ATK-10 `atk8` `2afbc2b9b59e3a3601ef6869480c44712225e5d0` — one-record r29 manifest:
    `r29 records=1 floor_violation=0`. **Succeeded.**
14. ATK-9 `atk9` `92a90d5e2c4e9f8cd3b6e66f53c455b6af5c4b43` — r29 waves dir with four files and
    no manifest: rc 0, zeros, `manifests=3`, no r29 line. **Succeeded.**

Stricter-only amendment set (all must be logged by the L1 before the C2 landing is scored; none
may retro-fail the honest recapture, so no blanket non-empty rule and no symlink-resolution
rule):

- A1 reject a manifest whose tree mode is not `100644`.
- A2 a path appearing twice in a manifest is a failure.
- A3 `excluded.tsv` and `symlinks.tsv`, when present, must be recorded in the manifest; every
  `excluded.tsv` row must carry a 64-hex digest and a non-empty reason and name a path absent
  from the tree.
- A4 require a committed `counts.tsv` with `records=`, `symlinks=`, `excluded=`, `source_files=`
  and require the three to sum to `source_files`; the delivered tool already prints these four
  numbers (`:531`), so committing them is inside the same instrument-acquisition surface.
- A5 every `census/round-<N>/waves/` directory at REV must hold `manifest.sha256`.
- A6 at the final tip only, a `--min-records` floor for the measured round (r29 = the source
  count recorded in `counts.tsv`), leaving the landing-commit measurement at `manifests=3`.

Impacted axes: operability 8 (the instrument cannot distinguish a real capture from a fabricated
one; the claim is still reachable honestly, so the axis is not harmed by the fixes above);
calibration 7 (only if the r29 scorecard records "receipts verify over committed bytes" as
evidence that the capture happened — it must be worded as self-consistency plus the tool's
source check); coverage 8 (untouched: no C1 or C3 byte was written, read or inferred here).
Verdict: fixable defects, not a tradeoff to reject — every one has a stricter-only form that the
honest state satisfies, except F10, which is a predicate-input choice the canonical judge must
accept explicitly.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmCritic48.md` (this report)

Scratch `/var/tmp/souji-r29-SwarmCritic48.sgm1nq` was removed after the run; no lane file, index,
jj state or sibling repo was touched. No credentials, no live `/proc` census, no
`census/operator-sweep-*` content, no `.scratch/` content was read.
