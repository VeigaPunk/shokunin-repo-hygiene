STATUS: PASS

# DraftGates — `## Gate` blocks for the two adopted entries (C2, restorable-quarantine staging)

Round 22, attempt 2 (hyaku) · lane `souji` · item L1Souji22.DraftGates · leaf seat, no subagent dispatch.
Report locations: this report; evidence at `.ufo/waves/round-22/attempt2/w1/evidence/DraftGates.md`.
No corpus file was created or edited by this seat.

## Axes (named before the work)

- **calibration** — every quoted span is measured against the committed snapshot bytes with the
  checker's own whitespace-collapsing predicate; no quote is reconstructed from memory or from an
  entry body.
- **operability** — both blocks are in the exact frozen shape the round's counter parses (top-level
  `url:`/`snapshot:`/`opened:`, per-row quote + locator + `snapshot:`, ADMIT/REJECT with reasons), so
  an adopting seat can paste them without re-deriving the predicate.
- **coverage** — both theme entries are covered (no-clobber primitive; origin-record restore side),
  and a slice row (S123) is discharged as an explicit REJECT instead of being silently dropped.

## Behavior delivered

Two insertion-ready Gate blocks, drafted in the report and in the evidence file only:

| entry | top-level snapshot | ADMIT rows | REJECT row |
|---|---|---|---|
| `corpus/knowledge/quarantine-staging-no-copy-r23.md` | `census/round-22/attempt2/sources/man7-rename.2.txt` | 3 | 1 (register S123) |
| `corpus/knowledge/quarantine-origin-record-fields-r24.md` | `census/round-22/attempt2/sources/arch-gio.1.txt` | 6 | 1 (register S123) |

## Evidence (executed)

1. **Contract read before any verdict**: `.ufo/waves/round-22/attempt2/preregistration.txt` — frozen
   per-entry predicate 1–6, snapshot dir, round date `2026-10-25`, slice/verdicts paths, base
   revision `4edb25dfe262515d0da63224bbba71e02e36cba5`.
2. **Quote provenance**: quotes taken only from the snapshot-seat artifacts in
   `.ufo/waves/round-22/attempt2/w1/evidence/` (`snap-rename2.txt`, `snap-mv1.txt`, `snap-gio1.txt`,
   `snap-trashspec.txt`, `snap-statx2.txt`, `snap-filetrash.txt`). Each candidate was tested with the
   checker's `squash()` against **both** the evidence `.txt` and the census `.txt` it is copied to.
   Result for all nine spans: present in BOTH. Word counts: 14, 7, 6, 9, 17, 10, 13, 23, 6 — all ≤25.
3. **Raw captures** are byte-identical between `w1/evidence/snap-*.raw` and
   `census/round-22/attempt2/sources/*.raw` (`sha256sum`, six of six).
4. **Frozen parser validation (read-only, real code, not a reimplementation)**: imported
   `tools/souji-gate-check.py` via `importlib` and called its `check_entry()` on each draft block
   with fixture frontmatter, `round_date=2026-10-25`,
   `snapshot_dir=census/round-22/attempt2/sources`:
   - `draftgate-r23.md -> (True, [])`
   - `draftgate-r24b.md -> (True, [])`
   (Draft texts were staged in `/var/tmp` — outside the lane tree — so the lane gained no extra
   file; those two files are scratch and are not evidence.)
5. **Current landed state (read-only, for contrast, not an acceptance act of mine)**:
   `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries … --snapshot-dir
   census/round-22/attempt2/sources --slice census/round-22/attempt2/quarantine-slice
   --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv`
   → `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, `exit=0`. Re-measured at 03:49 against
   the live entry bytes (`quarantine-staging-no-copy-r23.md` mtime 03:46:44, 4908 B;
   `quarantine-origin-record-fields-r24.md` mtime 03:48:19, 5462 B); the identical line came out of
   the 03:44 bytes.
6. **REJECT grounding**:
   - register row `absent-defect-register.md:172` (lane `souji`, round2, S123, class `payload-absent`,
     cited source `lanes/souji/round2/evidence/r23-trigger-prune.out`, claimed span
     `git worktree prune [-n] [-v] [--expire <expire>]`).
   - payload is 1043 B of `id=SOUJI-R23-TRIGGER-… verdict=PASS` lines; the claimed span occurs **0**
     times (`grep -c -F` → `0`).
   - the span is genuine man-page text: `MANWIDTH=80 man -P cat git-worktree | sed -n '12p'` →
     `git worktree prune [-n] [-v] [--expire <expire>]` under `SYNOPSIS`.
   - lane verdict already on record: `S123 refused … synopsis is git-worktree(1):12`.
   The defect is a **wrong-source citation**: a man-page sentence offered as evidence of what a local
   probe printed. That is why it is rejected rather than admitted; the flip is to re-cite it against
   `git-worktree(1)` and use the probe only for its own PASS lines.

## Drafted blocks (deliverable)

### A — `corpus/knowledge/quarantine-staging-no-copy-r23.md`

```markdown
## Gate

url: https://man7.org/linux/man-pages/man2/rename.2.html
snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
opened: 2026-10-25

- ADMIT: "RENAME_NOREPLACE Don't overwrite newpath of the rename. Return an error if newpath already exists." — § DESCRIPTION flags — reason: verbatim in the named snapshot and it states the refusal (error instead of overwrite) that the staging step needs — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "RENAME_NOREPLACE requires support from the underlying filesystem." — § DESCRIPTION flags — reason: verbatim in the named snapshot and it makes per-device support a precondition, not an assumption — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "do not copy if renaming fails" — § OPTIONS --no-copy — reason: verbatim in the named snapshot; without it mv may fall back to copy+remove across devices — snapshot: census/round-22/attempt2/sources/man7-mv.1.txt
- REJECT: register-slice row S123 (souji round2, class payload-absent) — the row offers a man-page SYNOPSIS sentence as evidence of what a local trigger probe printed; reason: the payload r23-trigger-prune.out contains 0 occurrences of the span and its own bytes are only id=... verdict=PASS lines, while the span sits in git-worktree(1) SYNOPSIS line 12, so the citation names the wrong source class and cannot support a claim about probe output — flip: re-cite the span against git-worktree(1) and cite the probe only for its PASS lines.
```

### B — `corpus/knowledge/quarantine-origin-record-fields-r24.md`

```markdown
## Gate

url: https://man.archlinux.org/man/gio.1.en
snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
opened: 2026-10-25

- ADMIT: "List files in the trash with their original locations." — § COMMANDS trash --list — reason: verbatim in the named snapshot; the listing field is the original location the restore consumes — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
- ADMIT: "Restore a file from trash to its original location. A URI beginning with trash:// is expected here." — § COMMANDS trash --restore — reason: verbatim in the named snapshot; restore is defined by the original location, so the record cannot omit it — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
- ADMIT: "The key “Path” contains the original location of the file/directory" — § 6 Contents of a trash directory, key/value list — reason: verbatim in the named snapshot; the spec makes the original path a required record key — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "The key “DeletionDate” contains the date and time when the file/directory was trashed." — § 6 Contents of a trash directory, key/value list — reason: verbatim in the named snapshot; it is the second required key and it is a timestamp, not a retention policy — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "Sends file to the “Trashcan”, if possible. This is similar to deleting it, but the user can recover it before emptying the trashcan." — § Description — reason: verbatim in the named snapshot; it is the documented recoverability the receipt-gated quarantine relies on — snapshot: census/round-22/attempt2/sources/gtk-filetrash.txt
- ADMIT: "__u64 stx_ino; /* Inode number */" — § DESCRIPTION struct statx — reason: verbatim in the named snapshot; identity fields are exposed directly, not parsed from text — snapshot: census/round-22/attempt2/sources/man7-statx.2.txt
- REJECT: register-slice row S123 (souji round2, class payload-absent) — the row offers a man-page SYNOPSIS sentence as evidence of what a local trigger probe printed; reason: the payload r23-trigger-prune.out contains 0 occurrences of the span and its own bytes are only id=... verdict=PASS lines, while the span sits in git-worktree(1) SYNOPSIS line 12, so the citation names the wrong source class and cannot support a claim about probe output — flip: re-cite the span against git-worktree(1) and cite the probe only for its PASS lines.
```

## Gates

Frozen per-entry predicate, mapped to the draft (each check can fail on its own):

1. `## Gate` heading present — yes, as the first line of each block.
2. https URL with `opened: 2026-10-25` equal to `--round-date` — yes (`man7.org` rename(2); `man.archlinux.org` gio(1)).
3. ≥1 located quote of ≤25 words with a locator token — yes: `§`, `§ OPTIONS`, `§ COMMANDS`, `paragraph`, `§ DESCRIPTION` on every quote row.
4. Each span verbatim (whitespace-collapsed) in the named committed snapshot under
   `census/round-22/attempt2/sources` — measured BOTH-sides before drafting; re-confirmed by the real
   `check_entry()` returning `(True, [])` for each block.
5. Every `source: S…` id resolves in `corpus/SOURCES.md` — S109, S110, S111, S112, S113, S114, S022
   all have registry rows (grep confirmed).
6. ≥1 ADMIT and ≥1 REJECT, each with a reason string — yes; the ADMIT rows carry explicit `reason:`
   clauses as well, which the parser does not require but the preregistration's wording ("with a
   reason string each") does.

No `PENDING-SNAPSHOT` slot remains: all six snapshot `.txt` files were present when the blocks were
finalised (`snap-gio1.txt` was missing at the 03:45 listing and landed at 03:46; quotes were
re-verified after it appeared).

## Touched surfaces

- `…/attempt2/w1/evidence/DraftGates.md` (new, named evidence file).
- `…/attempt2/w1/DraftGates.md` (new, this report).
- Nothing else in the lane. No corpus file, no registry row, no `census/` write, no index, no
  `.ufo/state`, no `MANIFEST.json`, no git/jj write, no cleanup, no process signal, no
  deletion authority. `/home/vgpnk/Projects/shokuknow` was read only (payload, register).
- Tool installs/updates: none. No package manager, `uv`, `npx` or binary added.

## Findings (bounded)

1. **The corpus entries already carry Gate blocks, and sibling seats edited them while this draft was
   being written** (`quarantine-staging-no-copy-r23.md` mtime 03:46:44, 4908 B;
   `quarantine-origin-record-fields-r24.md` mtime 03:48:19, 5462 B). My drafts are report-only and
   were not applied. The live bytes pass the counter (`entries=2 ok=2 slice_verdicts=8
   slice_total=8 fail=0`, re-measured after both edits), so this item's value is the divergence
   below, not a repair of a red gate.
2. **The landed `r24` Gate's REJECT is still a different rejection.** As of 03:48 it rejects a
   duplicate staged entry (`quarantine-staging-no-copy-r24`, duplicate ground), not the
   register-slice citation-class defect. My assignment requires S123 as the rejected candidate in
   both blocks; if the adopting seat keeps the landed REJECT, the item's stated reject is not executed.
3. **Landed ADMIT rows carry no reason string.** Preregistration predicate 6 reads ">=1 ADMIT and
   >=1 REJECT with a reason string each"; the parser enforces a reason only on REJECT. My draft adds
   `reason:` to every ADMIT, which is parser-neutral (validated) and closes the prose/predicate gap.
4. **Evidence `.txt` and census `.txt` are not byte-identical** for any of the six sources: the
   snapshot seats and the census mirror use different strippers (lengths differ, ordering of site
   chrome differs). The `.raw` captures are byte-identical, and every quoted span survives
   whitespace collapse in both `.txt` files — so the Gate quotes are sound against the file the
   checker actually opens, but a reader comparing the evidence sha to the census sha will see a
   mismatch. The Gate names the census path deliberately for that reason.
5. **S123 is a wrong-source citation, not fabrication.** The span is verbatim `git-worktree(1):12`,
   so the honest verdict is "refused: cited against the wrong artifact", with a flip, not "false
   quote". The block says exactly that.
6. **Quotes that the entry bodies use are all genuinely in the snapshots.** The earlier `grep -F`
   misses on `rename(2)` and `gio(1)` were line-wrap artifacts of the raw text (the checker collapses
   whitespace); no entry quote is absent.
7. **The landed `r23` REJECT is the citation-class defect but is mislabelled.** Its 03:46 edit names
   the row `campaign-S123` and omits the register provenance (lane, class `payload-absent`, cited
   payload path). My draft names register-slice row S123 (`souji` round2), states the measured 0
   matches in the named payload and the `git-worktree(1):12` origin — same verdict, sharper receipt.

## Not done / out of scope

- Did not write the blocks into `corpus/knowledge/` (explicitly forbidden for this item; an adopting
  seat must apply them).
- Did not run the round counter as an acceptance act on my drafts inside the lane (no entry file
  exists to point it at); validation was the real `check_entry()` on the exact draft text.
- Did not re-derive the base revision `4edb25d`, adopt registry rows, edit the slice, or touch
  `slice-verdicts.tsv`.
- Did not verify or claim anything about the round's C1 calibration claim (other lane, other seats).

## Artifact paths

- Evidence: `.ufo/waves/round-22/attempt2/w1/evidence/DraftGates.md`
- Report: `.ufo/waves/round-22/attempt2/w1/DraftGates.md`
