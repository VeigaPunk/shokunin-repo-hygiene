# corpus/README.md — round-25 patch draft (ScribeReadme-2, wave 1; independent second draft)

Base: `corpus/README.md` blob at lane HEAD de736c258e6df4c5999360daac749721ae06eff8 (unchanged
since 6e4737e; 536 lines). C3 sourcing per prereg amendment 2 item 4: S124/S125/S126. Draft only — `corpus/README.md` is not edited. The sibling draft
`readme-patch.md` (ScribeReadme) covers the same item; differences are listed in §5.

Integration rules (each was exercised in a scratch clone, see `ScribeReadme-2.md` § Evidence):

1. :40 is changed **in-cell** (no line added or removed) and the Round 25 block is appended
   after :536. Nothing is inserted between :1 and :536, so every line pointer already in the
   file (:40, :42, :68, :217, :233-234, :504, :517) stays true. Landing check:
   `awk 'NR==517' corpus/README.md | cut -c1-60` must print
   `| F2 repository size census | frontier; read side (three e`.
2. Q56 (`corpus/QUALITY.md` :135, "A new grounded entry and its map row land in the same
   commit"): the Round 25 F2 row names `knowledge/git-repo-structure-common-dir.md`; land it
   only in the commit that adds that entry. Without the entry the row is one
   `DANGLING-MAP-PATH` (measured).
3. No unescaped `|` inside any new cell; no `<digits> <accepted|present|unverifiable|refused>`
   span anywhere in the new text (record-agreement K3 `TALLY_RE` would count it).

---

## 1. :40 F2 status cell — append-only marker (D4 / R24-M2)

Old :40 (verbatim):

```text
| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19) | — |
```

New :40:

```text
| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19); superseded by Round 24 F2 row (:517) | — |
```

Old→new for the lesson log: appended span `; superseded by Round 24 F2 row (:517)` at the end of
the :40 status cell; ground cell and entries cell (`—`) byte-identical.

## 2. Round 24 section note (:506-508) — no change

The note reads "their status prose stays as history (:40's "frontier, no entry" is stale and
superseded here)". The :40 edit appends, does not delete, so the prose is still history and the
note is still true; the edit adds no line, so its :40/:68/:217/:42 pointers still resolve.
Editing r24 prose would violate the file's "sections above stand" rule — the fix is recorded in
the Round 25 section instead.

## 3. Round 25 section — append after :536 (Variant A: C3 verified)

```markdown

## Round 25 — kill-rule tool row, size-census refusal coverage, structure probe common-dir envelope

Appended; the sections above stand. The r12 map's F2 status cell (:40) now ends with an
append-only "superseded by Round 24 F2 row (:517)" marker (routed D4, R24-M2; old→new logged in
`lessons/round-25.md`); no line was added, so the line pointers in the sections above still
resolve. For the entries column only, the F2 row below supersedes the Round 24 F2 row (:517) and
names every F2-grounded entry; :517's status prose stays as history. Landing condition (Q56):
the row landed in the same commit as `knowledge/git-repo-structure-common-dir.md`.

| ground | status | entries / runnable evidence |
|---|---|---|
| F2 repository size census | frontier; read side (three entries, r13/r23), write-safety debris census (r24 C1), and the structure probe under the common-git-dir envelope (r25 C3): probing a linked worktree (`--repo B`) reports `probe.git_common_dir` equal to the main repository's git dir, and the no-write manifest over the common dir and the private gitdir is unchanged across the run; the colocated/plain precondition (:217, :233-234) is measured on a sandbox clone carrying `refs/jj/keep/*` refs, whose `references.others.count` exceeds the plain clone's, so a colocated figure is not interchangeable with a plain baseline. Structure fixture `selftest=PASS ids=7/7` (was 5/5). Limits: the keep-ref case simulates jj without the jj binary; atime/ctime are excluded and a write that restores mtimes stays invisible to the manifest; no `git repo structure` size baseline and no fleet figure | `knowledge/git-repo-structure-readonly.md` (S035–S037); `knowledge/repo-size-census-readonly.md` (S115–S117); `knowledge/count-objects-garbage-readings-r25.md` (S118–S119); `knowledge/count-objects-linked-worktree-garbage.md` (r24, assimilated); `knowledge/git-repo-structure-common-dir.md` (S124–S126); `../tools/souji-repo-structure.sh`; `../tests/fixtures/r13-repo-structure.sh`; `../tools/souji-size-census.py`; `../tests/fixtures/r24-size-census.py`; `../census/round-24/size-census-lane.txt` |

### Frontier (r25)

- F2 — the r24 next step is measured: `../tools/souji-repo-structure.sh` runs under the
  common-git-dir manifest and the colocated/plain precondition holds in the sandbox (r25 C3).
  Next: one lane-bound `git repo structure` baseline of this repository, taken from a plain
  `--no-local` clone (the lane is jj-colocated, so its own git dir carries `refs/jj/keep/*` and
  is not a plain baseline), with alternates read (S115) and the manifest asserted around the
  run. Size attribution by object or path stays frontier; a fleet figure stays unclaimed.
- F1, F3, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.
```

Optional clauses (L1 keeps or cuts; neither changes any F mapping):

- **C2 clause** — keep only if C2 is verified (`cases=12 pass=12`); insert into the F2 status
  cell before "Limits:": `Size-census refusal surfaces are now fixture cases 9-12 (bare
  non-empty, bare empty, subdirectory, extensions.partialClone-only; r25 C2), closing the r24
  "does not cover" limit at :517.`
- **C1 row** — keep only if C1 is verified; append to the table (its ground cell does not
  start with `F<k>`; its entries cell has no `knowledge/` path):

```text
| Coverage-map kill rule (calibration of this file; not a ground) | tool change, outside admission pending: with `--base-rev`, every entry carrying a front-matter `ground: F<k>` line at the base must still exist at `--rev` with that same `F<k>` line, else `MISMATCH KILL-RULE`; the counts line gains `kill_tested` / `kill_violations` (r25 C1), replacing the hand `git diff` check of Q56's last clause | `../tools/souji-coverage-agreement.py`; `../tests/fixtures/r25-coverage-agreement.py` |
```

- **Receipts** — append the C3 (and C2) after-receipt `../census/round-25/records/…` paths to
  the F2 entries cell once they exist at the landing tip; none exist at de736c2.
- **Sources** — S124–S126 are absent from `corpus/SOURCES.md` at de736c2 (`grep -c` → 0); they
  must land no later than the commit carrying this row.

## 4. Variant B — C3 not verified (C3 kill rule fires)

Do not append the F2 row; do not land the entry (Q56 pairs them). Keep the Round 25 heading and
first paragraph minus its last two sentences, and use this F2 frontier line (F1/F3/F4/F5 bullet
as in Variant A):

```markdown
- F2 — unchanged from the r24 frontier (:523-527): the common-git-dir envelope for
  `../tools/souji-repo-structure.sh` and the colocated/plain precondition stay unmeasured
  (r25 C3 not verified). Size attribution by object or path stays frontier; a fleet figure
  stays unclaimed.
```

## 5. Differences from the sibling draft `readme-patch.md`

- :40 separator: this draft uses `; superseded by …` (matches the cell's existing `;`-joined
  clauses); the sibling uses ` — superseded by …`. Either passes both counters.
- F2 frontier next-line: this draft names the measurement source (plain `--no-local` clone,
  because the lane is jj-colocated) and keeps the alternates requirement (S115) from Frontier
  (r23); the sibling says "a plain (non-colocated) clone, with the Git version recorded".
- Entries cell: this draft keeps `../census/round-24/size-census-lane.txt` (named at :517) so the
  superseding row drops no r24 evidence path.
