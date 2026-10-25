# corpus/README.md — round-25 patch draft (ScribeReadme, wave 1)

Base: `corpus/README.md` at lane HEAD 6e4737eab43d8fde1b85eb9f57023d29046705b4 (blob last
changed in 315422ba9970f03c27f8a9184446783b7fcdf0a7; 536 lines). This is a draft. The L1 integrates it; nothing
here edits `corpus/README.md`.

Integration constraints:

1. **Change :40 in place and append the Round 25 section after :536. Insert no lines between
   :1 and :536.** The new :40 marker points at `:517`, and the r24 note (:506-508) and r24
   frontier (:523-527) give line numbers too. Inserting any line above :517 makes those
   pointers stale.
2. **Same commit (Q56, `corpus/QUALITY.md` :135):** the Round 25 F2 row names
   `knowledge/git-repo-structure-common-dir.md`. It lands only in the commit that adds that
   entry (ground: F2). Without the entry, the row is a `DANGLING-MAP-PATH` (measured below).
   If C3 is not verified, use Variant B (§3 below).
3. Every cell is free of unescaped `|`, so `tools/souji-coverage-agreement.py` `CELL_SPLIT`
   keeps the three-column shape.

---

## 1. :40 status cell — append-only marker (D4 / R24-M2)

Old (:40, verbatim):

```text
| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19) | — |
```

New (:40; the only change is the text appended before the status cell's closing ` | — |`):

```text
| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19) — superseded by Round 24 F2 row (:517) | — |
```

Appended span (log this verbatim as old→new in the round-25 lesson): ` — superseded by Round 24 F2 row (:517)`.
The ground cell and entries cell (`—`) are unchanged, so the coverage-map counts stay the same.

## 2. Round 24 section note (:506-508) — no change

Current text: "their status prose stays as history (:40's "frontier, no entry" is stale and
superseded here)". After §1 this is still true. :40's prose stays as history, and the marker
now says the same thing at :40 itself. Editing r24 prose would break the append-only rule, so
the Round 25 section records the fix instead (first paragraph of §3).

## 3. Round 25 section — append after :536 (Variant A: C3 verified)

Append the block between the fences after the blank line that follows :536.

```markdown

## Round 25 — kill-rule tool row, size-census refusal coverage, structure probe under the common-dir envelope

Appended; the sections above stand. For the entries column only, this table supersedes the r24
F2 row (:517); its status prose stays as history. :40's status cell now carries an append-only
"superseded by Round 24 F2 row (:517)" marker (r25 D4, R24-M2; old→new logged in
`lessons/round-25.md`); the r24 note at :506-508 is unchanged. Landing condition (Q56): this
row lands in the same commit as `knowledge/git-repo-structure-common-dir.md`.

| ground | status | entries / runnable evidence |
|---|---|---|
| F2 repository size census | frontier; read side (three entries, r13/r23), write-safety debris census (r24 C1), and now the structure probe under the common-git-dir envelope (r25 C3): with `--repo` naming a linked worktree, `probe.git_common_dir` equals the main repository's git dir, and the no-write manifest over the common dir and the private gitdir is unchanged across the run; a clone carrying `refs/jj/keep/*` reports a larger `references.others.count` than the plain clone, so a colocated figure is not interchangeable with a plain baseline (precondition from :233-234, measured in a sandbox, not on the lane). Size-census fixture cases 9-12 now cover bare non-empty, bare empty, subdirectory and `extensions.partialClone`-only inputs (r25 C2); the r24 limit "does not cover … bare/subdirectory inputs" (:517) is answered by them. Still disclosed: a tool that restores mtimes after writing is invisible to the manifest (atime/ctime excluded); hostile config/env has no case; no size baseline; no fleet figure | `knowledge/git-repo-structure-readonly.md` (S035–S037); `knowledge/repo-size-census-readonly.md` (S115–S117); `knowledge/count-objects-garbage-readings-r25.md` (S118–S119); `knowledge/count-objects-linked-worktree-garbage.md` (r24, assimilated); `knowledge/git-repo-structure-common-dir.md` (S124/S125, r25); `../tools/souji-repo-structure.sh`; `../tests/fixtures/r13-repo-structure.sh`; `../tools/souji-size-census.py`; `../tests/fixtures/r24-size-census.py` |
| Coverage-map kill rule (calibration of this file; not a ground) | tool change, outside admission pending: with `--base-rev`, every entry grounded `F<k>` at the base must still exist at `--rev` with the same `F<k>` ground line, otherwise `MISMATCH KILL-RULE`; the counts line gains `kill_tested` / `kill_violations`. This replaces the hand `git diff` check of Q56's last clause | `../tools/souji-coverage-agreement.py`; `../tests/fixtures/r25-coverage-agreement.py` |

### Frontier (r25)

- F2 — the common-git-dir envelope for `../tools/souji-repo-structure.sh` and the colocated/plain
  precondition (r24 frontier :523-527) are now measured in the sandbox (r25 C3, `selftest=PASS
  ids=7/7`; see `knowledge/git-repo-structure-common-dir.md`). Next: a `git repo structure` size
  baseline taken on a plain (non-colocated) clone, with the Git version recorded and the
  common-dir manifest asserted around the run. Size attribution by object or path stays
  frontier; a fleet figure stays unclaimed.
- F1, F3, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.
```

Row scoping, for the L1 to keep or cut:

- **F2 row, required parts:** the entries column, which lists the four r24 F2 entries plus
  the new one, so this row names every F2 entry (the r23 prose/table drift class; see the r24
  note :531-536), and the C3 status clause.
- **F2 row, C2 clause** ("Size-census fixture cases 9-12 …"): keep only if C2 is verified
  (`cases=12 pass=12`). If C2 fails, delete that sentence and the `answered by them` clause.
  The r24 limit at :517 then stands.
- **Coverage-map kill rule row:** keep only if C1 is verified. If C1 fails, delete the row.
  Its ground cell does not start with `F<k>`, so it adds no F mapping either way.
- **After-receipt paths:** add the C2/C3 after-receipt `census/round-25/records/…` paths to
  the evidence columns once they exist at the landing tip (none exist in this draft).

### Variant B — C3 not verified (kill rule fires)

Do not append the F2 row and do not land the entry. Append the section without the F2 row and
use this F2 frontier line. The F1/F3/F4/F5 bullet stays as in Variant A:

```markdown
- F2 — unchanged from the r24 frontier (:523-527): the common-git-dir envelope for
  `../tools/souji-repo-structure.sh` and the colocated/plain precondition stay unmeasured
  (r25 C3 not verified). Size attribution by object or path stays frontier; a fleet figure
  stays unclaimed.
```

If only C2 holds, add a non-F row (ground cell not starting with `F<k>`, entries cell with no
`knowledge/` path) carrying the C2 clause. This keeps F2's entries column unchanged.
