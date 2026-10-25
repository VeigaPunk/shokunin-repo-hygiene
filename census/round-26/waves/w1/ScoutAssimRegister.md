# ScoutAssimRegister — souji quarantine-register slice, round 26 (read-only census)

## Status

STATUS: PARTIAL — the full souji slice (8 rows, ids + class cells) is reported and its C2
contact is resolved, but the lane's own r26 slice-verdict artifact is not consumable by the
lane's gate tool (`accepted-carried` is outside the tool's class vocabulary), so the r26
re-check cannot currently be machine-validated. No predicate, target or case set is
challenged; the counters are untouched by this seat.

## Evidence

Lane revision `e78ac7c4837b81b634db4a927605a751a7f006ba` (master, ahead=0; C1/C2/C3 landed).
Register read at `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md`,
sha256 `5afe1810a6c3d62f37987b575a954f5b1197daa23005d4bb2f1d982f64bad833` (unchanged by this
seat; the file was never written).

### E1 — the full souji slice (awk from the addendum §10 form)

```
$ awk -F'|' '$2 ~ /souji/ && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ {id=$4; cl=$5;
    gsub(/^ +| +$/,"",id); gsub(/^ +| +$/,"",cl); printf "%s  %s  %s\n", id, $3, cl}' \
    /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
S114   round1   `payload-absent`
S123   round2   `payload-absent`
S124   round2   `payload-absent`
S126   round2   `payload-absent`
S131   round2   `payload-absent`
S133   round3   `payload-absent`
S138   round3   `payload-absent`
S118`  round1   the cited source could not be fetched, so no quote was checked
```

8 rows, matching the r24 gate's accepted 8 (`census/round-24/records/slice-verdicts.tsv:3-10`,
8/8 `accepted`). The register's own by-lane table counts souji = 7 (`absent-defect-register.md:247`)
because it counts only the seven `payload-absent` rows; the eighth (`S118`) lives in the
"Rows whose quotes were NEVER CHECKED" table (`:361`), whose class cell is the prose
"never checked" text rather than a class token — the register's class vocabulary at `:13-14`
names it `unreachable`.

### E2 — the C2 admit set's contact with the slice

C2's five staged rows are `S109, S110, S111, S123, S131`
(`/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:7,8,9,21,29`).
Overlap test against the souji slice (register ids are campaign ids, lane ids are renumbered):

```
$ for id in S109 S110 S111 S123 S131; do
    awk -F'|' -v I="$id" '$2 ~ /souji/ && $3 ~ /round[0-9]+/ && $4 ~ I"$" {f=1} END{exit !f}' \
      /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md \
      && echo "$id IS quarantined" || echo "$id not in slice"; done
S109 not in slice ; S110 not in slice ; S111 not in slice ; S123 not in slice ; S131 not in slice
```

**Contact is by payload, not by id.** The staged rows `S123` and `S131` are exactly the two
campaign rows the register quarantined:

- register `:172` — souji round2 `S123`, class `payload-absent`, cited source
  `lanes/souji/round2/evidence/r23-trigger-prune.out`, quote `git worktree prune [-n] [-v] [--expire <expire>]`
- register `:175` — souji round2 `S131`, class `payload-absent`, cited source
  `lanes/souji/round2/evidence/r23-worktree-census.out`, quote `-n, --dry-run With prune, do not remove anything; just report what it would remove.`

Both staged rows are the *own-work* rows whose payloads those two register rows cite; the
lane appends them as lane ids **S131** (fixture) and **S132** (census) per the frozen renumber
map (`preregistration.txt:94`: `staged S109->S128, S110->S129, S111->S130, S123->S131, S131->S132.`).
The lane's own r26 slice file names the same two: `slice-verdicts-r26.tsv:3-4`
(`r26 re-checks only` / `the two rows whose payloads the C2 claim actually appends (staged S123 -> lane`).

### E3 — the quarantined quotes were NOT carried into the append

```
$ git grep -c -F -e 'git worktree prune [-n] [-v] [--expire <expire>]' \
    -e 'With prune, do not remove anything' HEAD -- corpus/        # (no output = 0 hits)
$ git show HEAD:corpus/SOURCES.md | awk 'NR>=149&&NR<=153' | grep -c '\\|'   # 0
$ git show HEAD:corpus/SOURCES.md | awk -F'|' '/^\| S[0-9]{3} \|/{c[NF]++} END{for(k in c) print "NF="k, c[k]}'
NF=13 132
```

Neither ABSENT quote string appears anywhere in the committed `corpus/`; the five appended rows
are 11-column (NF=13) with zero escaped pipes. The lane re-grounded the two payloads by digest
instead of re-importing the mis-bound man-page span. Digests re-verified by me this run against
the campaign bytes: fixture `11c136aa71066733d50d226d344df9125401780aa81836f8ca9ca68a9997e65a`,
evidence `510722c11a97f6bca8f93e49b8a279f1f109d0222e40f675d001058768e069b4`,
census `1ac71c4f7199a134c204b45f339aadfc7e90c84b2d640cbed181b3577b9392fd` — all three match the
r26 verdict file cells and the appended registry rows (`corpus/SOURCES.md:152-153`).

### E4 — the lane's r26 slice artifacts against the gate tool

```
$ cmp census/round-24/records/quarantine-slice .ufo/waves/round-26/assimilation/quarantine-slice
IDENTICAL
$ cmp <(register-derived slice, same formatting) .ufo/waves/round-26/assimilation/quarantine-slice
BYTE-IDENTICAL to register-derived   (sha256 12d3c325649ca6026bdb9b98 for both)
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/git-auto-maintenance-trigger-set.md \
    --entries corpus/knowledge/git-auto-maintenance-trigger-set-r23.md \
    --snapshot-dir census/round-26/sources \
    --slice .ufo/waves/round-26/assimilation/quarantine-slice \
    --slice-verdicts .ufo/waves/round-26/assimilation/slice-verdicts-r26.tsv
FAIL slice verdict-bad-class-line-8:accepted-carried
FAIL slice verdict-bad-class-line-9:accepted-carried
... (6 lines)
entries=2 ok=2 slice_verdicts=2 slice_total=8 fail=6     rc=1
$ python3 -B tools/souji-gate-check.py ... --slice census/round-24/records/quarantine-slice \
    --slice-verdicts census/round-24/records/slice-verdicts.tsv
entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0     rc=0
$ grep -n "CLASSES" tools/souji-gate-check.py
48:CLASSES = {"present", "accepted", "unverifiable", "refused"}
```

The r26 slice file is byte-identical to the register-derived slice (so the slice itself is
correct and current), but the r26 verdict file's six carried rows use the class
`accepted-carried`, which is outside the tool's class vocabulary, so the tool drops them and the
pair fails with `slice_verdicts=2 slice_total=8`.

The frozen C2 K2 is unaffected: it runs with the inert empty arms
(`preregistration.txt:108` `Slice arms inert this round`; receipt
`census/round-26/records/c2-gate.tsv`, `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`, rc=0).

## Findings

1. **The souji quarantine slice is 8 rows, and the C2 admit set touches exactly two of them
   (by payload, not by id).** Register `:171-177` (class `payload-absent`) plus `:361`
   (S118, never-checked class cell). The two C2-touching rows are campaign `S123` (register
   `:172`, payload `r23-trigger-prune.out`) and campaign `S131` (register `:175`, payload
   `r23-worktree-census.out`), appended as lane S131/S132 per `preregistration.txt:94`.
   The remaining six (S114, S118, S124, S126, S133, S138) are untouched by C2. The lane's
   r26 verdicts file scopes its re-check to the same two rows
   (`.ufo/waves/round-26/assimilation/slice-verdicts-r26.tsv:3-4`), so the coverage is
   correct.

2. **Neither quarantined ABSENT quote reached the registry.** `git grep` over HEAD `corpus/`
   returns 0 hits for `git worktree prune [-n] [-v] [--expire <expire>]` and for
   `With prune, do not remove anything`; the five appended rows are NF=13 with 0 escaped
   pipes (`corpus/SOURCES.md:149-153`). The two own-work payloads were re-grounded by sha256
   (E3), so the register's `payload-absent` verdict (wrong-source citation) is not
   propagated. Location: `corpus/SOURCES.md:152-153`,
   `.ufo/waves/round-26/assimilation/slice-verdicts-r26.tsv:6-7`.

3. **DEFECT (operability, not a claim failure): the r26 slice-verdict artifact cannot be
   machine-validated by the lane's own gate tool.** `slice-verdicts-r26.tsv:8-13` use the
   class `accepted-carried`; `tools/souji-gate-check.py:48` admits only
   `{"present","accepted","unverifiable","refused"}`, so the six carried rows are dropped and
   the pair exits 1 with `slice_verdicts=2 slice_total=8 fail=6` (E4). The r24 authoritative
   pair passes 8/8 (`census/round-24/records/slice-verdicts.tsv`, all `accepted`). The
   vocabulary is the r24 one, per `corpus/lessons/round-25.md:44`
   (`The r24 vocabulary collapses round 22's `present` and `accepted` pass classes into one r24 `accepted`.`).
   No frozen counter depends on this artifact, so C1/C2/C3 stand; the r26 re-check is
   currently prose-only. **[INFERENCE]** a vocabulary-legal rendering of the same eight
   verdicts (e.g. class `accepted` plus a separate provenance column) would restore 8/8.

4. **Naming hazard, already recognised by the lane: bare `S131`/`S132` now denote different
   documents in different tables.** Campaign `S131` = the worktree census; lane `S131` = the
   trigger-prune fixture and lane `S132` = the census (`corpus/SOURCES.md:152-153`), and
   `corpus/lessons/round-24.md:236` uses bare `S131` for the campaign census row
   (`fleet census, never appended`). The r26 verdict file states the disambiguation
   (`slice-verdicts-r26.tsv:2` — `ids are campaign register ids, NOT lane registry ids.`) and
   the r25 lesson writes ids as `SOURCES S1xx` (`corpus/lessons/round-25.md:33-36`), but the
   r26 lesson body writes bare ids (`corpus/lessons/round-26.md:24-26`). Q57 requires the
   join to use `(lane, campaign-id)`, never a bare id (`corpus/QUALITY.md:141`).

5. **Stale cell that the r26 append invalidates, no supersession note yet.** The r24
   authoritative cell for the census row reads `never appended by this lane`
   (`census/round-24/records/slice-verdicts.tsv:8`; same wording at
   `corpus/lessons/round-24.md:236`). At the r26 tip the census payload **is** appended by
   this lane (`corpus/SOURCES.md:153`, used-by `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`),
   so that clause is now false and needs the Q57 appended note naming the exact
   `file:line`, the authority file and the recomputed value. `git grep "never appended"` at
   HEAD returns only the two r24-era occurrences — no correction is recorded yet.

6. **The r26 verdict file's S123 cell over-claims one digest.** It reads
   `fixture sha256 11c136aa… matches staged row` (`slice-verdicts-r26.tsv:6`), but the staged
   row (`merge/souji/SOURCES.append.md:21`) carries only the evidence digest `510722c1…`
   (`grep -c 11c136aa` over the whole staged package = 0); `11c136aa…` is the lane's own
   re-grounding digest and appears only in the appended lane row and the entry's
   `verified-at:` line. The digest value itself is correct (E3); the provenance wording is not.
   Same cell: `7/7 PASS ids present in bytes` — the payload carries 7 case ids plus a
   `SOUJI-R23-TRIGGER-SUMMARY` id (8 `verdict=PASS` lines), so "7/7" undercounts the ids by
   one unless SUMMARY is excluded on purpose.

7. **Cross-lane position, for the L1's routing only.** The other lanes' quarantined rows
   (197 non-souji rows) are outside this seat's scope and were not enumerated. The lane's own
   quarantine vocabulary is documented in `corpus/lessons/round-25.md:40-46` and the
   authoritative table is `census/round-24/records/slice-verdicts.tsv` (per D6,
   `corpus/README.md:555`); no r26 authoritative counterpart exists at
   `census/round-26/records/` (that directory holds only the inert `empty-slice` /
   `empty-verdicts` arms), so the r26 re-check currently has no authority-table slot.

## Attack log

Not an attack seat; no predicate, target, case set or axis is challenged, and no counter was
re-run under a modified condition. Findings 3, 5 and 6 are defects in the lane's own r26
artifacts and its stale-cell bookkeeping, reported for the L1 to route; none of them changes a
frozen counter's outcome (C1/C2/C3 receipts stand as committed). Per the round's amendment
rules, any fix would be append-only and logged; this seat proposes no predicate change.

Scratch: none needed beyond read-only greps; `/var/tmp/souji-r26-ScoutAssimRegister/` was
created for the slice comparison and removed before this report was written. No tooling was
installed or upgraded (no package manager invoked; `pacman` untouched). The register file was
opened read-only and is byte-unchanged (sha256 `5afe1810…` before and after).
