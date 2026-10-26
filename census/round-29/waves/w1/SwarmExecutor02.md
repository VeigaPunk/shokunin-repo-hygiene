# SwarmExecutor02 — Souji round 29, C1 K1 cell repairs (exact derivation)

## Status

STATUS: PASS — all six K1 mismatches at base are reduced to one lawful in-place cell edit each (nine cells over six rows: S022, S024, S025, S075, S076, S215), the delivery TSV matches base bytes and rehearsal bytes cell-for-cell, and the C1 counter over a scratch clone commit reads `k1=0` (was 6). The lane file was never edited.

## Evidence

Base measurement, lane `691dd29211c53d0ef94fa072394cb9c8a69fe92e`, list revision `b8cb4b31ce80e2e3314b88e85d40ea9873180804`:

```
$ python3 -B tools/souji-registry-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
K1 used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md
K1 cited-not-in-used-by S075 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S076 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S022 corpus/knowledge/quarantine-origin-record-fields-r24.md
K1 cited-not-in-used-by S024 corpus/knowledge/quarantine-same-filesystem-rename.md
K1 cited-not-in-used-by S025 corpus/knowledge/quarantine-same-filesystem-rename.md
K2 uncorrected LOG.md:1758
K2 uncorrected SCORECARD.md:23
K2 uncorrected corpus/lessons/round-28.md:22
K2 uncorrected corpus/lessons/round-28.md:40
SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e
rc=1
```

Scratch rehearsal — clone of the lane at the prereg commit, edits applied to `corpus/SOURCES.md` only, commit in scratch only:

```
$ D=$(mktemp -d /var/tmp/souji-r29-C1UsedByRepair.XXXXXX)   → /var/tmp/souji-r29-C1UsedByRepair.6ubdj27t
$ git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin "$D/c"
$ git -C "$D/c" rev-parse --show-toplevel
/var/tmp/souji-r29-C1UsedByRepair.6ubdj27t/c
$ git -C "$D/c" config user.name/user.email   (scratch-only identity)
$ git -C "$D/c" commit -m "round-29 C1 K1 rehearsal: six cell repairs (status/used-by only)"
$ git -C "$D/c" rev-parse HEAD
5b588d72a6029b5835ab10dcafb020050ddbb4bf
$ git -C "$D/c" diff --stat b8cb4b31ce80e2e3314b88e85d40ea9873180804 5b588d7
 corpus/SOURCES.md | 12 ++++++------
 1 file changed, 6 insertions(+), 6 deletions(-)
```

Counter over the scratch commit (the stale list is present in the clone at that commit, so `--list-rev` names it; no copy was needed):

```
$ python3 -B tools/souji-registry-agreement.py --root /var/tmp/souji-r29-C1UsedByRepair.6ubdj27t/c \
    --rev 5b588d72a6029b5835ab10dcafb020050ddbb4bf --list-rev 5b588d72a6029b5835ab10dcafb020050ddbb4bf
K2 uncorrected LOG.md:1758
K2 uncorrected SCORECARD.md:23
K2 uncorrected corpus/lessons/round-28.md:22
K2 uncorrected corpus/lessons/round-28.md:40
SUMMARY k1=0 k2=4 mismatches=4 rev=5b588d72a6029b5835ab10dcafb020050ddbb4bf
rc=1
```

`k1=0` at revision `5b588d72a6029b5835ab10dcafb020050ddbb4bf`; `rc 1` comes only from the four K2 rows (out of this item's scope) — no K1 line is emitted.

Registry tallies, same counter the lane already trusts (`python3 -B census/round-13/count-claims.py <rev>`):

```
base 691dd29211c53d0ef94fa072394cb9c8a69fe92e: admitted_entries=9 sources=139 statuses mined=115 queued=15 rejected=9
rehearsal 5b588d72a6029b5835ab10dcafb020050ddbb4bf: admitted_entries=9 sources=139 statuses mined=116 queued=14 rejected=9
```

Cell-level cross-check (script over `git show <rev>:corpus/SOURCES.md`, columns `status`=cell 8, `used-by`=cell 11, cells stripped): all nine delivery rows match the base cell as `old_cell` and the rehearsal cell as `new_cell` — `TSV matches base and rehearsal bytes: True` (9/9). `git diff --quiet 691dd29 b8cb4b3 -- corpus/SOURCES.md` also holds, so base row bytes and the prereg revision agree (`True`).

Isolation runs in the same scratch clone, each variant branched from `b8cb4b31ce80e2e3314b88e85d40ea9873180804` and measured with `--list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804`:

```
status cells only  → rev 5c1a13c57aee0f838fb46cbe82c79c5924e999f6: SUMMARY k1=6 k2=4 mismatches=10  rc 1
used-by cells only → rev a52be700d08d872c6e02e3d0e67c9231b61cc60f: SUMMARY k1=0 k2=4 mismatches=4   rc 1
```

So the counter reads only `used-by`; the `status` flips are registry-contract compliance measured to be counter-neutral, not counter chasing.

`used-by`-import surface at base, distinct from my edits: `grep -c S215 corpus/knowledge/git-auto-maintenance-trigger-set.md` → `0`; the same entry's front matter is S128/S129/S130 only (`…git-auto-maintenance-trigger-set.md:1-3`).

## Findings

1. **S215 is a forward reference the entry never made.** Row `corpus/SOURCES.md:160` declares `used-by corpus/knowledge/git-auto-maintenance-trigger-set.md`, but that entry's `source:` lines cite S128, S129 and S130 and the token S215 occurs zero times in the file (`git-auto-maintenance-trigger-set.md:1-3`; the r28 closure already recorded it, `corpus/lessons/round-28-verifier-spotcheck.md:60-61` and routed it as defect 5 at `:123`). Rule 2 of the registry contract (`../CORPUS.md:116`) permits only `status`, `recheck` and `used-by` to change in place and never an entry's `source:` lines, and this seat's contract repeats the entry-side prohibition, so the repair must land on the row: `used-by` → `—` and `status mined` → `queued` (a `mined` row needs ≥1 used-by path, `../CORPUS.md:103`). No other path can cite S215 without editing an entry.

2. **S075/S076 name only the lesson that predates the knowledge entry.** Rows `corpus/SOURCES.md:96` and `:97` list `corpus/lessons/round-18.md` (which does name both ids, so those rows raised no `used-by-no-cite`), while the admitted F5 entry `corpus/knowledge/process-residue-observations.md` cites them on its own front matter (`:1`) and applies them in the body (`:47` starttime for PID identity; `:28` and `:62` exe-suffix scope). The entry is admitted, not HELD (`corpus/README.md:274`; the only HELD marker in that file is `:218` about the K5 reap hold). Repair: append the entry after the existing lesson path; `status` stays `mined`.

3. **S022 has the same shape with an admitted successor entry.** Row `corpus/SOURCES.md:43` lists only `corpus/knowledge/trash-spec-restorable-quarantine.md`, while `corpus/knowledge/quarantine-origin-record-fields-r24.md:4` cites S022 on its front matter and uses it in the body (`:29`, `:51`). That entry is admitted — the F4 coverage-map row records "read-side fields admitted r24" (`corpus/README.md:42`). Repair: append it; `status` stays `mined`.

4. **S024/S025 are cited by the lane's single HELD entry — adding them is honest, and it is the only lawful lever.** Rows `corpus/SOURCES.md:45` and `:46` are `queued` with `used-by —`; `corpus/knowledge/quarantine-same-filesystem-rename.md:1` cites both ids and quotes the manuals verbatim in its Evidence (`:15-:17` mv, `:18-:20` rm). The entry's HELD status is an admission judgement about its `/dev/shm` device claim, not about those citations (`corpus/knowledge/quarantine-same-filesystem-rename.md:51`; `corpus/README.md:59` and `:90`). The registry defines `used-by` as the paths of the knowledge entries or lessons citing the row (`../CORPUS.md:107`) and defines `mined` as "cited by ≥1 path in `used-by`" (`../CORPUS.md:103`) — neither mentions admission, so the honest state is `used-by corpus/knowledge/quarantine-same-filesystem-rename.md` with `status mined`. Two consequences the L1 must carry, both recorded in the delivery reasons: the mined flag on these two rows now rests on a HELD entry, and the expansion metric is unaffected because it counts admitted entries, not row status (`../CORPUS.md:123`) — `count-claims.py` reports `admitted_entries=9` at both revisions. The two rejected alternatives: leaving `queued` beside a non-empty `used-by` would contradict the status definition and introduce the lane's first `queued`+`used-by` row (sweep at base: zero such rows, and zero `mined`+`—` rows, `awk -F'|' 'NF==13'` over `corpus/SOURCES.md`), and removing the citations would require editing an entry, which rule 2 forbids.

5. **The counter is status-blind, so the status flips are contract compliance rather than counter chasing — measured, not inferred.** `tools/souji-registry-agreement.py` builds its row map from the id and the 12th cell only (`registry()`, `:36-47`; the `used-by` parse is `:46`) — `status` is never read by K1. Measured in the scratch clone: the status-cells-only variant keeps `k1=6` (rev `5c1a13c…`), the used-by-cells-only variant reaches `k1=0` (rev `a52be70…`). Applying only the `used-by` half would therefore pass the counter while leaving S215 `mined` with `used-by —` and S024/S025 `queued` with a path — both contradicting the registry's own status definition; both cells change together, and the kill rule about in-place phrase edits is untouched (no stale-list file and no lesson text is written by this seat).

6. **No row, entry or census file is added, removed or renumbered, and the three pre-existing `rejected`-with-`used-by` rows are unchanged.** Invariant sweep `(status == mined) != (used-by non-empty)` over all rows: base and rehearsal both report exactly `S090` (`corpus/SOURCES.md:111`), `S097` (`:118`) and `S127` (`:148`), `same: True`. Row count stays 139 at both revisions. The three axes other than calibration are untouched: no instrument, fixture, entry, snapshot or census byte is modified.

7. **Forward risk for the final tip (not a defect at base).** C3's two new entries will cite existing rows as well as S216–S219, and K1 compares entry front matter against every row's `used-by`. The rows most exposed are S114 (`corpus/SOURCES.md:135`, `mined`, `used-by` = `corpus/knowledge/quarantine-origin-record-fields-r24.md` only — the statx identity fields the new identity entry needs) and S118 (`:139`); if either new entry cites them without a matching `used-by` append, `k1` returns ≥1 at the C3 landing commit and at the final tip even though this repair holds. The C3 integration must append those paths in the same commit as the entries; S216–S219 are safe by construction only if their `used-by` is exactly the citing new entries.

8. **Required companion edit (integration, not mine to write): the old→new log.** Rule 2 requires each in-place cell change to be logged in the round lesson. Proposed append for `corpus/lessons/round-29.md`, naming all nine changes and the HELD caveat:

```
## C1 K1 registry repairs (append-only log, CORPUS.md rule 2)

- corpus/SOURCES.md:43 S022 used-by `corpus/knowledge/trash-spec-restorable-quarantine.md` → `corpus/knowledge/trash-spec-restorable-quarantine.md, corpus/knowledge/quarantine-origin-record-fields-r24.md`.
- corpus/SOURCES.md:45 S024 status `queued` → `mined`; used-by `—` → `corpus/knowledge/quarantine-same-filesystem-rename.md`. The citing entry is HELD (`quarantine-same-filesystem-rename.md:51`), so this marks citation, not admission; no expansion credit.
- corpus/SOURCES.md:46 S025 status `queued` → `mined`; used-by `—` → `corpus/knowledge/quarantine-same-filesystem-rename.md`. Same HELD caveat.
- corpus/SOURCES.md:96 S075 used-by `corpus/lessons/round-18.md` → `corpus/lessons/round-18.md, corpus/knowledge/process-residue-observations.md`.
- corpus/SOURCES.md:97 S076 used-by `corpus/lessons/round-18.md` → `corpus/lessons/round-18.md, corpus/knowledge/process-residue-observations.md`.
- corpus/SOURCES.md:160 S215 status `mined` → `queued`; used-by `corpus/knowledge/git-auto-maintenance-trigger-set.md` → `—`. That entry never cites S215 (`grep -c S215` = 0); the r28 defect is repaired on the row because an entry's `source:` lines are not editable.
```

## Deliveries

- `.ufo/waves/round-29/w1/deliver-c1-usedby-changes.tsv` — nine rows, six columns (`row_id`, `column`, `old_cell`, `new_cell`, `evidence`, `reason`), header included; every `old_cell`/`new_cell` verified against base and rehearsal bytes.
- `.ufo/waves/round-29/w1/SwarmExecutor02.md` — this report.

Scratch `/var/tmp/souji-r29-C1UsedByRepair.6ubdj27t` removed after the measurements above; no lane file, index, ref or jj state was written.
