source: S322 — git-add(1) at v2.56.0 § OPTIONS `--force` (https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-add.adoc; accessed 2026-11-07), cited where the capture rule is named
verified-at: ef04ca6c66af02b98bc061290b8028c6c0654a4b (round 77 after-arms; capture `6690cb5ad96d11a7b528a62a98ba42fad7783d35`, ledger `8bf42fc6233cc4fee28c170d57e5d38a80f6d2bc`)
recheck: `python3 -B census/round-77/c2-pointer-counter.py --root LANE --rev <rev> --fleet-root FLEET --ledger census/round-77/c2-pointer-ledger.tsv` must print `SUMMARY items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0` and `EXIT=0`, run from the lane checkout on the host that froze the population

# A dangling evidence pointer is a census item: locate its bytes, then say where they live

ground: F4 — preserved-artifact census applied to the lane's own self-assessment: every path SCORECARD.md,
SKILL.md, corpus/QUALITY.md, corpus/README.md and PROVINCE.md cite as evidence either resolves to bytes
someone can check, or the lane is overstating what it holds

## Claim

A self-assessment row that cites a path the pushed tree does not hold is a calibration defect even when
the row was true on the day it was written: the evidence existed on one host, under an ignored directory
(`.ufo/waves/` is ignored by the lane's committed `.gitignore`), and a reader of the pushed repository
cannot open it. At the r77 base the lane's own pointer check
(`tools/souji-pointer-check.py`) reported `missing=35` over those files; the stale items were not one
class but six.

## Rule (round 77, C2)

Freeze the MISSING findings first, with the digest of whatever bytes this host's lane disk holds at each
path (`census/round-77/c2-population.tsv`). Then resolve each finding to exactly one class the counter
can verify on its own:

| class | when | what the counter checks |
|---|---|---|
| CAPTURED | local-only evidence with no committed copy | the path now exists at the measured revision with the frozen digest (file sha256, or the sorted per-file listing for a directory) |
| MOVED | the bytes were already committed under another path (wave captures under `census/round-N/wave[s]/`) | the named target at the revision has the frozen digest |
| LOCAL-POLICY | bytes deliberately kept local (quarantine, operator sweeps) | the path sits under a frozen policy prefix and the lane disk still holds equal bytes |
| QUARANTINED | the cited path was moved into quarantine | absent at the revision and on disk; the quarantine target exists on the lane disk |
| FLEET | the path is fleet runtime the lane never owns (the orchestrator state directory and watchdog log, the L0 question file, operator scope files) | absent from the lane; present under the fleet root |
| TOKEN | the extracted string is a parse artefact (a path followed by `>` inside a `git show` placeholder, a regex alternation, a Python string concatenation that builds a round path, a `D1..D5` range) | the artefact is present; every named target exists and continues the token |
| ABSENT | the sentence cites the path as an example of something absent | absent at the revision, on disk, under the fleet root and in every lane ref's history; no parse artefact |

Capture the local-only items at the exact path the row cites, not at a new path: the rows are
append-only, so a new path would leave the old pointer dangling. An ignore rule does not stop a named file
from being tracked — git-add(1) `--force`: "Allow adding otherwise ignored files." (S322); the lane helper
tracks explicitly named ignored files the same way.

## Evidence

- Before (no ledger, base `d4f51563`): `census/round-77/controls/c2-K-a-no-ledger.txt` →
  `SUMMARY items=35 resolved=0 unresolved=35`, EXIT=1.
- After: `census/round-77/records/c2-after.txt` → `resolved=35 unresolved=0 refused=0 mismatched=0`,
  EXIT=0 (4 CAPTURED, 10 MOVED, 8 FLEET, 6 TOKEN, 3 LOCAL-POLICY, 3 ABSENT, 1 QUARANTINED); the lane's pointer
  check now reads `missing=31` (`records/c2-pointer-check-after.txt`): the four captured items resolve
  for every reader, the other 31 resolve through the ledger.
- Forgeries the counter refuses (all at the base): every item declared ABSENT (`c2-K-b`, 31 refused);
  local-only evidence declared LOCAL-POLICY instead of captured (`c2-K-c`, 4 refused); empty stubs
  committed at the capture paths (`c2-K-d`, 4 mismatched); MOVED to a same-named file with other bytes
  (`c2-K-e`, 3 refused).

## Stated limits

- CAPTURED and MOVED prove byte identity with what this host held when the population was frozen, not
  that those bytes are what the seat first wrote.
- FLEET proves the path exists under the fleet root, not what it contains.
- P14 (the r16 `.git` stub) is truthfully both ABSENT and QUARANTINED; the counter does not discriminate.
- The population is host-bound: LOCAL-POLICY and QUARANTINED read this host's lane disk.
