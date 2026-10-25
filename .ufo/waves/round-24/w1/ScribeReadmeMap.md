# ScribeReadmeMap — corpus/README.md append draft, round 24

## Status

STATUS: PASS — append drafted (below). Every path it names is tracked at lane tip `f9db2181647d91470a724a12d626bd6106805076` or is a round-24 delivery named in the preregistration or the w1 spec. A local simulation of the C2 predicate gives `mismatches=2` at base and `0` once the append and the C1 entry land together. The simulation is my own reading of the predicate, not the C2 tool (which is absent at tip).

## Delivery — append to `corpus/README.md` (after line 502; no older section edited)

~~~~markdown

## Round 24 — F2 write-safety census, coverage-map agreement, receipt verify symmetry

Appended; the sections above stand. For the entries column only, this table supersedes the F2
rows at :40 (r12 map) and :68 (Round 13); their status prose stays as history. F4's r12 row
(:42) already names both F4-grounded entries and is not repeated. Landing condition (the r17
convention at :205-211): the F2 row lands only in the same commit as
`knowledge/count-objects-linked-worktree-garbage.md` (carrying a `ground: F2` line),
`../tools/souji-size-census.py` and `../tests/fixtures/r24-size-census.py`; otherwise its cells
name only the files present at that commit.

| ground | status | entries / runnable evidence |
|---|---|---|
| F2 repository size census | frontier; read side (three entries, r13/r23) plus a write-safety debris census (r24 C1): `count-objects -v` read against the common git dir so a linked worktree's `garbage: 1` is not reported, `fsck` unreachable count without `--lost-found`, alternates counted; `--lost-found`, promisor/partialClone and non-repositories refused (exit 2). The 8 frozen fixture cases fence the no-write envelope; one lane-bound measurement, no fleet figure | `knowledge/git-repo-structure-readonly.md` (S035–S037); `knowledge/repo-size-census-readonly.md` (S115–S117); `knowledge/count-objects-garbage-readings-r25.md` (S118–S119); `knowledge/count-objects-linked-worktree-garbage.md` (r24, assimilated); `../tools/souji-size-census.py`; `../tests/fixtures/r24-size-census.py`; `../census/round-24/size-census-lane.txt` |
| Coverage-map agreement (calibration of this file; not a ground) | tool change, outside admission pending: `MISSING-FROM-MAP` and `DANGLING-MAP-PATH` over every table in this file whose header reads `ground` / … / `entries…` | `../tools/souji-coverage-agreement.py`; `../tests/fixtures/r24-coverage-agreement.py` |
| Receipt verify/run symmetry (r23 residuals) | runner change, outside admission pending: `verify` refuses a non-durable rev (`RECEIPT-REV-NOT-DURABLE`) and a `tool=` absent from `cmd=` argv (`RECEIPT-TOOL-NOT-IN-ARGV`); the five r23 receipts must still verify | `../tools/souji-receipt-run.py`; `../tests/fixtures/r24-receipt-verify.py` |

### Frontier (r24)

- F2 — next after the write-safety fixture: put `../tools/souji-repo-structure.sh` under the same
  `.git` manifest envelope the r24 fixture uses (its r13 no-change result is bounded, see
  `knowledge/git-repo-structure-readonly.md`), then the colocated/plain byte-comparison
  precondition (:233-234) before any `git repo structure` size baseline. Size attribution by
  object or path stays frontier; a fleet figure stays unclaimed.
- F1, F3, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.

Routed defect from `lessons/round-23-verifier-spotcheck.md` :41 (map table versus the "read side
now holds three" prose): answered by the F2 row above, which names every F2 entry in its entries
column, and C2's `MISSING-FROM-MAP` now counts any recurrence as a mismatch.
~~~~

## Evidence

All commands were run read-only against the lane at rev `f9db2181647d91470a724a12d626bd6106805076`, with git 2.56.0. Scratch lived in `/var/tmp/souji-r24-ScribeReadmeMap/` and has been removed.

1. **Path existence** (`git cat-file -e f9db218…:<p>`):
   - TRACKED at tip: `corpus/knowledge/{git-repo-structure-readonly,repo-size-census-readonly,count-objects-garbage-readings-r25}.md`, `corpus/knowledge/obsidian-ledger.tsv`, `tools/souji-repo-structure.sh`, `tools/souji-receipt-run.py`, `corpus/lessons/round-23-verifier-spotcheck.md`.
   - ABSENT at tip, each a named round-24 delivery:
     - `corpus/knowledge/count-objects-linked-worktree-garbage.md` (w1-spec ScribeEntry: "proposed lane path `corpus/knowledge/count-objects-linked-worktree-garbage.md`").
     - `tools/souji-size-census.py` and `tests/fixtures/r24-size-census.py` (prereg C1).
     - `census/round-24/size-census-lane.txt` (prereg line 66: "committed as census/round-24/size-census-lane.txt").
     - `tools/souji-coverage-agreement.py` and `tests/fixtures/r24-coverage-agreement.py` (prereg C2).
     - `tests/fixtures/r24-receipt-verify.py` (prereg C3).
2. **Ground lines** (`grep -n '^ground:' corpus/knowledge/*.md`): two files are `ground: F2` (repo-size-census-readonly, count-objects-garbage-readings-r25) and two are `ground: F4` (quarantine-staging-no-copy-r23, quarantine-origin-record-fields-r24). `grep -c '^ground:' corpus/knowledge/git-repo-structure-readonly.md` → `0`.
3. **F4 check** (README :42 entries cell): it contains `knowledge/quarantine-staging-no-copy-r23.md` and `knowledge/quarantine-origin-record-fields-r24.md`, which are both F4-grounded files, so no F4 row is needed.
4. **C2 predicate simulation** (`python3 -B sim.py <lane> <rev> <append|-> [simulated-present]`), implementing prereg lines 81–88 as written:
   - Base `f9db218` (and `a65fac9`; `git diff --stat a65fac9 f9db218 -- corpus/ tools/ tests/` is empty):
     ```
     MISMATCH	MISSING-FROM-MAP	corpus/knowledge/count-objects-garbage-readings-r25.md	F2
     MISMATCH	MISSING-FROM-MAP	corpus/knowledge/repo-size-census-readonly.md	F2
     grounded=4 mapped=17 mismatches=2
     ```
   - Base + append, with the C1 entry absent:
     ```
     MISMATCH	DANGLING-MAP-PATH	knowledge/count-objects-linked-worktree-garbage.md	F2 repository size c
     grounded=4 mapped=20 mismatches=1
     ```
   - Base + append, with the C1 entry present (simulated `ground: F2`): `grounded=5 mapped=20 mismatches=0`.
5. **Pipe check**: the append contains exactly 5 lines with `|`, which are the table's 5 lines. No escaped pipe appears inside any cell.

## Findings

1. **Routed defect confirmed.** The r23 spot-check line 41 says "the frozen coverage map was not changed to add an explicit entry row for the two new titles". README :68 names the two new titles only in its status cell, and :40 has `—` as its entries cell. The C2 predicate, as I simulated it, counts exactly these two as `MISSING-FROM-MAP` at base. The append closes both.
2. **Landing-order hazard (C2).** The append names `knowledge/count-objects-linked-worktree-garbage.md`. If the append lands before that entry, or if the entry lands under another name, C2 reads `DANGLING-MAP-PATH=1`; if the entry lacks a `ground: F2` line, C2 does not count it as grounded at all. The append's landing-condition paragraph makes this a same-commit rule. If the L1 renames the entry, edit both the entries cell and the landing paragraph.
3. **ATTACK (C2 calibration blind spot, no counter change proposed).** `corpus/knowledge/git-repo-structure-readonly.md` has no `ground:` front-matter line; it states its ground in prose instead ("Coverage-map ground: F2 repository size census.", line 7). As a result, C2's `grounded` misses it, and `MISSING-FROM-MAP` could never fire for it: deleting it from every map row would leave `mismatches=0`. This is reported, not fixed: adding a `ground:` line is a knowledge-entry edit outside this item.
4. **ATTACK (C2 gameability).** The prereg's "basename appears in … entries-column cell" is satisfied by any mention, including prose like "not `x.md`" or a non-`knowledge/` path. My simulation used substring match. Whether the real tool requires a backticked `knowledge/<basename>` token is for the C2 fixture to fence.
5. **Status-cell wording.** The append's F2 status cell describes the C1 contract (prereg lines 34–41 and 46–61). It is true only if C1 lands with `cases=8 pass=8`. Under the C1 kill rule (prereg :69), the L1 must reword the cell to "not verified" rather than ship it as drafted.
6. **Line references** in the append (:40, :42, :68, :205-211, :233-234, spot-check :41) were read this run against the 502-line README at tip. Prepending anything would shift them, but an append does not.

## Out of scope / not done

- The README itself was not edited (draft only). No C1/C2/C3 tool was run; those tools are absent at tip. No commits, no jj, no shokuknow writes.
- No tools were installed or upgraded.
