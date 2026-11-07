# S77Scribe — round-77 knowledge drafts

Two sections. (a) is an append block for `corpus/knowledge/filter-filemode-witness.md` (after its r76
section). (b) is the new entry `corpus/knowledge/self-assessment-pointer-resolution.md`. Numbers below
were re-derived this seat: pointer-check `missing=35` at d4f51563 and `missing=31` at ef04ca6c (own runs,
2.5 s each), C2 `resolved=0/35` at base and `35/35` at ef04ca6c (own runs, EXIT=1/0), class counts from
`census/round-77/c2-pointer-ledger.tsv` (31 rows: MOVED 10, FLEET 8, TOKEN 6, LOCAL-POLICY 3, ABSENT 3,
QUARANTINED 1) plus four CAPTURED items; C1 numbers read from the committed receipts/controls.

## (a) appends to corpus/knowledge/filter-filemode-witness.md

## r77: an exclude or attribute source that is not a regular file (appended 2026-11-06)

**Rule.** Before check 4 runs any git call that reads an exclude or attribute source, the gate requires
every such source that exists to be a regular file: `$GIT_DIR/info/exclude`, `$GIT_DIR/info/attributes`,
`core.excludesFile` and `core.attributesFile` — or, when a variable is unset, their
`$XDG_CONFIG_HOME/git/ignore` and `…/attributes` defaults — and every `.gitignore`/`.gitattributes` in the
work tree outside `.git`. A symlink counts by its target only where the gate's test follows the link
(`[[ -e && ! -f ]]`, for the repository-local and configured sources); the work-tree scan uses
`find … ! -type f`, which does not follow, so a symlinked `.gitignore` is refused there — consistent with
git, which opens per-directory sources with O_NOFOLLOW (S321, `dir.c:1778`) and so never reads the link.
Any other kind fails `clean` with
`RECEIPT-NONREGULAR-SOURCE` and a count, never a path. Check 4's `git status` and python block also run
under `timeout -k 5 300` (backstop; expiry fails `clean`).

**Why.** git opens an exclude source with a plain blocking open(2) and calls fstat only after it returns
(S321, `dir.c` add_patterns lines 1164-1169; attr.c opens the attribute sources the same way, S064), and
opening a FIFO blocks until a writer appears (fifo(7), S062). add_patterns uses the fstat only for
`st_size` — the file's two `S_ISREG` tests (`:2361`, `:2385`) map `d_type`, not the exclude source — so a
FIFO source never reaches a type decision. On the lane-base gate eight of the 16 frozen rows read `HANG`
at the 30 s bound (`census/round-77/controls/c1-K-a-do-nothing.txt`: `mismatches=9 hangs=8`, EXIT=1; n1-n7
and n10 hang, n8 is a policy row that git never opens and that passes there). The W gate reads
`SUMMARY rows=16 mismatches=0 errors=0 hangs=0`, each n-row refused in 0.1 s
(`census/round-77/records/c1-after.txt`); r76's 30 rows, r36 21/21 and r27 4/4 hold
(`records/c1-regress-r76.txt`, `-r36.txt`, `-r27.txt`).

**Rulings and controls.** n8 (a FIFO `.gitignore` inside a directory a tracked rule ignores) is refused
although git never opens it: the gate fails closed and does not model git's descent — a policy row, not a
hang row. The one-path rows o1-o3 kill the r76 survivor M09 (`census/round-77/controls/c1-K-c-m09-one-path.txt`,
`mismatches=11`); a refuse-all gate fails the four positive controls (`c1-K-b-refuse-all.txt`, 7) and a
blanket refusal of every non-regular entry or of any configured `core.excludesFile` fails p2/p3
(`c1-K-d-blanket-nonregular.txt`, `mismatches=7 hangs=4`).

**Stated limits.** A FIFO `$GIT_DIR/config` or `~/.gitconfig` blocks git in checks 1-3, before this
surface; the timeout bounds check 4 only; a caller's `XDG_CONFIG_HOME`/`HOME` decides which default file
is examined; a source swapped for a FIFO between the pre-check and `git status` is caught only by the
backstop. No frozen row carries a symlink-to-regular work-tree `.gitignore`; that refusal is read from
the `find` expression, not measured.

## (b) new corpus/knowledge/self-assessment-pointer-resolution.md

source: S322 — git-add(1) at tag v2.56.0 § OPTIONS `--force` (https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-add.adoc; accessed 2026-11-06), cited where the capture rule is named
verified-at: ef04ca6c66af02b98bc061290b8028c6c0654a4b (round 77 after-arms; capture `6690cb5ad96d11a7b528a62a98ba42fad7783d35`, ledger `8bf42fc6233cc4fee28c170d57e5d38a80f6d2bc`)
recheck: `python3 -B census/round-77/c2-pointer-counter.py --root LANE --rev <rev> --fleet-root FLEET --ledger census/round-77/c2-pointer-ledger.tsv` must print `SUMMARY items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0` and `EXIT=0`, run from the lane checkout on the host that froze the population

# A dangling evidence pointer is a census item: locate its bytes, then say where they live

ground: F4 — preserved-artifact census applied to the lane's own self-assessment: every path SCORECARD.md,
SKILL.md, corpus/QUALITY.md, corpus/README.md and PROVINCE.md cite as evidence either resolves to bytes
someone can check, or the lane is overstating what it holds.

## Claim

A self-assessment row that cites a path the pushed tree does not hold is a calibration defect even when the
row was true on the day it was written: the evidence existed on one host, under an ignored directory
(`.ufo/waves/` is ignored by the lane's committed `.gitignore`), and a reader of the pushed repository
cannot open it. At the r77 base the lane's own pointer check (`tools/souji-pointer-check.py`) reported
`missing=35` over those files; the stale items were not one class: four captures plus six ledger classes.

## Rule (round 77, C2)

Freeze the MISSING findings first, with the digest of whatever bytes this host's lane disk holds at each
path (`census/round-77/c2-population.tsv`). The counter then applies, per item, the first rule that
applies: R0 integrity (the base blob of the citing file carries the token on the frozen line, else ERROR);
R1 CAPTURED; then the item's single ledger class. An item already CAPTURED ignores its ledger row; an
unknown id or class, a duplicate id, or a ledger rule that fails is a REFUSED item.

| class | when | what the counter checks |
|---|---|---|
| CAPTURED | local-only evidence with no committed copy | the path now exists at the measured revision with the frozen digest (file sha256, or the sorted per-file listing for a directory) |
| MOVED | the bytes were already committed under another path (wave captures under `census/round-N/wave[s]/`) | the named target at the revision has the frozen digest |
| LOCAL-POLICY | bytes deliberately kept local (quarantine root, operator sweeps) | the path sits under a frozen policy prefix (`.ufo/quarantine`, `census/operator-sweep-`) and the lane disk still holds equal bytes |
| QUARANTINED | the cited path was moved into quarantine | absent at the revision and on disk; the named quarantine target exists on the lane disk |
| FLEET | the path is fleet runtime the lane never owns (`.ufo/state`, `watchdog.log`, `l0-questions.md`, operator scopes) | absent from the lane; present under the fleet root |
| TOKEN | the extracted string is a parse artefact (`path>` inside `<git show …>`, a regex `\|`, `"census/round-"+rd`, a `D1..D5` range) | the artefact is present; every named target exists and continues the token |
| ABSENT | the sentence cites the path as an example of something absent | absent at the revision, on disk, under the fleet root and in every lane ref's history; no parse artefact |

Capture the local-only items at the exact path the row cites, not at a new path: the rows are append-only,
so a new path would leave the old pointer dangling. An ignore rule does not stop a named file from being
tracked — git-add(1) `--force`: "Allow adding otherwise ignored files." (S322) — and the lane helper records
named files this way (`jj file track --include-ignored`; a named directory is tracked like `git add <dir>`,
so ignored content under it stays out).

## Evidence

- Before (no ledger, base `d4f51563`): `census/round-77/controls/c2-K-a-no-ledger.txt` →
  `SUMMARY items=35 resolved=0 unresolved=35`, EXIT=1.
- After: `census/round-77/records/c2-after.txt` → `resolved=35 unresolved=0 refused=0 mismatched=0`,
  EXIT=0 (4 CAPTURED — P09 P10 P11 P18, commit `6690cb5a` — plus 10 MOVED, 8 FLEET, 6 TOKEN,
  3 LOCAL-POLICY, 3 ABSENT, 1 QUARANTINED).
- The lane's pointer check drops from `missing=35` (base; command frozen in
  `census/round-77/c2-population.tsv`'s header and preregistration §C2) to `missing=31`
  (`census/round-77/records/c2-pointer-check-after.txt`): only the four captured items become git objects,
  so the other 31 remain MISSING to that tool and are accounted for by the ledger, not by a path.
- Forgeries the counter refuses (all at the base): every item declared ABSENT (`c2-K-b`, 31 refused);
  local-only evidence declared LOCAL-POLICY instead of captured (`c2-K-c`, 4 refused); empty stubs
  committed at the capture paths (`c2-K-d`, 4 mismatched); MOVED to a same-named file with other bytes
  (`c2-K-e`, 3 refused).

## Stated limits

- CAPTURED and MOVED prove byte identity with what this host held when the population was frozen, not
  that those bytes are what the seat first wrote.
- FLEET proves the path exists under the fleet root, not what it contains.
- P14 (the r16 `.git` stub, quarantined under `round-17`) is truthfully both ABSENT and QUARANTINED; the
  counter does not discriminate.
- The population is host-bound: LOCAL-POLICY and QUARANTINED read this host's lane disk, so the recheck
  only reproduces on the host that froze it.
- A ledger row is a claim the tool verifies, not evidence a reader can check without the tool; the four
  captured items are the only ones that resolve for every reader.
