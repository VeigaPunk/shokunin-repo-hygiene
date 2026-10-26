# SwarmCritic47 — attack on C1 (calibration) of round 29

## Status

STATUS: PASS — assignment executed: C1 was attacked with 12 executed cheating states in scratch repos (all read-only against the lane); `mismatches=0` was reached at `k1=0 k2=0 rc=0` with no true fact recorded, and the r28 routed defect 2 is relabelled, not closed.

## Evidence

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`; base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; prereg commit = lane HEAD `b8cb4b31ce80e2e3314b88e85d40ea9873180804`; scratch clone `/var/tmp/souji-r29-SwarmCritic47/fix.ssqOWm/c` (`git -C "$D/c" rev-parse --show-toplevel` printed that path; identity configured only with `git -C` inside it; removed at end).

Frozen counter, executed at both revs with the prereg list pinned:

```
python3 -B tools/souji-registry-agreement.py --root . --rev 691dd29… --list-rev b8cb4b31…
SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e   (rc 1)
python3 -B tools/souji-registry-agreement.py --root . --rev b8cb4b31… --list-rev b8cb4b31…
SUMMARY k1=6 k2=4 mismatches=10 rev=b8cb4b31ce80e2e3314b88e85d40ea9873180804   (rc 1)
```

Do-nothing control at the prereg rev (same invocation) reproduces `k1=6 k2=4 mismatches=10` — the target is not vacuous.

Truth state at the prereg rev, independent of C1:

```
python3 -B census/round-29/c2-counter.py --root . --rev b8cb4b31…
r26 records=1382 failed=152 uncovered=14 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0
python3 -B tools/souji-declared-evidence.py --root . --rev b8cb4b31…    (rc 1)
assertions=164 resolved=145 skipped=223 mismatches=19
```

Tool under attack: `tools/souji-registry-agreement.py` (`ROW` regex line 17; `k1` lines 49-73; `k2` lines 75-98; `main` lines 101-120). All attack commits below are in the scratch clone only; the edits are landable as-is in the lane (they touch `corpus/SOURCES.md`, three `corpus/knowledge/*.md`, `LOG.md`, `SCORECARD.md`, `corpus/lessons/round-28.md`).

Attack totalling run (each attack = one scratch commit, counter run with `--list-rev b8cb4b31…`):

| # | cheat | rev | tool result | accepted? |
|---|---|---|---|---|
| A1 | four `R29-CORRECTION` lines reading “acknowledged; no claim made.” | `6d5d93ec…` | `k1=6 k2=0` | yes (k2→0) |
| A2 | one marker per file naming a *nonexistent* line (`LOG.md:17580`, `SCORECARD.md:2300`, `round-28.md:220`, `:400`) | `e540da04…` | `k1=6 k2=0` | yes |
| A3 | one blanket marker line per file listing every tag | `0c577c13…` | `k1=6 k2=0` | yes |
| A3b | one identical marker line copied verbatim into the tail of all three files | `45044759…` | `k1=6 k2=0` | yes |
| B5 | in-place rewrite of `LOG.md:1758` ending “The r26 receipt verifies fully; all 1382 records are present and complete.”, phrase retained, + A1 markers | `8f469da4…` | `k1=6 k2=0` | yes (append-only not enforced) |
| A5 | every `source:` line deleted from the three cited entries | `cd59a0d2…` | `k1=2 k2=4` | partial (deletion creates `used-by-no-cite` masks) |
| A6c | `source:` lines moved below the first `# ` heading (text preserved) | `e5c6be61…` | `k1=4 k2=4` | yes (S024/S025 checks vanish) |
| C2 | S024 demoted to `rejected`, used-by set to `—`, entry citation moved below heading | `84e3858f…` | `k1=4 k2=4` | yes |
| row-delete | S025 row deleted (registry 139→138), entry citation moved below heading | `a04ba0ec…` | `k1=4 k2=4` | yes, no row-count complaint |
| A7 | S215 row indented four spaces | `3d447045…` | `k1=5 k2=4` | yes (row invisible to parser) |
| B4 | entry moved to `corpus/knowledge/sub/`, cites S001; depth-2 control entry with the same citation | `30494e5f…` | nested citation not flagged; control flagged `cited-not-in-used-by S001 corpus/knowledge/zz-control.md` | yes (depth-2-only scan) |
| B1 | S215 used-by repointed at `corpus/SOURCES.md` (self-reference) | `1a447b64…` | `k1=5` | yes |
| B2 | S215 used-by repointed at `corpus/lessons/round-28-verifier-spotcheck.md` (a lesson that merely mentions S215) | `98db0185…` | `k1=5` | yes |
| A8 | `stale-statements.tsv` emptied, counter run without `--list-rev` (default = `--rev`) | `124be868…` | `k2=0` without the flag; `k2=4` with `--list-rev` pinned | yes, invocation-controlled |
| A9b | `--stale-list census/round-29/empty-list.tsv` (no `--list-rev`) | `f04a9fce…` | `k1=6 k2=0` | yes |
| D1 | A1 markers + all `source:` lines below headings + S215 used-by `corpus/SOURCES.md` | `af7fe69b…` | `SUMMARY k1=0 k2=0 mismatches=0 rev=af7fe69b…` **rc=0** | yes |

D1 is the existence proof: `k1=0 k2=0 mismatches=0` while nothing true was recorded. Residue measured inside the same commit: `git show af7fe69b:corpus/knowledge/git-auto-maintenance-trigger-set.md | grep -c S215` → `0` (the routed defect 5 is untouched, merely hidden behind a false used-by cell); the four stale statements are byte-unchanged; the appended markers assert “no claim made”; and the registry now claims `S215` is used by `corpus/SOURCES.md` (`sed -n '160p'` field 12). `git merge-base --is-ancestor af7fe69b… master` (lane) → non-ancestor only because the cheat lives in scratch; the same file edits are landable in the lane.

## Findings

1. **K1 used-by is a mention test, not a provenance test** — `tools/souji-registry-agreement.py:61-66` accepts any blob that contains the id anywhere (`re.search(r'\b' + i + r'\b', t)`). Consequence: used-by may point at `corpus/SOURCES.md` itself (every id occurs in the table) or at a lesson that discusses the id (B1, B2). Location: `corpus/SOURCES.md` row S215.
2. **K1 forward direction is suppressible** — the citation scan at lines 59-70 reads only lines matching the case-sensitive `^(- )?source:` before the first `^#\s` heading, and only entries at depth exactly 2 (`p.count('/') == 2`). Moving a `source:` line below the title (A6c), deleting it (A5), or nesting the entry (B4) removes the check without removing the declaration. Location: `corpus/knowledge/process-residue-observations.md:1`, `quarantine-origin-record-fields-r24.md:1-4`, `quarantine-same-filesystem-rename.md:1`.
3. **Registry enumeration is indentation- and count-unguarded** — `ROW` (line 17) matches only 0-3 leading spaces, and nothing compares the parsed row set with the table's row lines. A four-space indent makes a row invisible (A7, `k1` 6→5); deleting the row (S025) plus suppressing its citation is fully accepted, registry 139→138.
4. **Status demotion is inert, so the cheat is cell erasure, not demotion** — `status` is never read by `k1`. Demoting S024 to `rejected` with its used-by emptied still reports `cited-not-in-used-by S024` (C1 rev `52bb3c48…`); only when the entry's citation is also moved out of front matter does the finding disappear (C2). `S030/S032/S044/S048` already carry `status=rejected` with used-by `—`, so an empty used-by on a demoted row is indistinguishable from convention.
5. **K2's marker test is a bare substring** — line 96 accepts any line starting `R29-CORRECTION ` that contains the tag, so a tag for `LOG.md:1758` is satisfied by `LOG.md:17580`, and one marker line can satisfy several statements (A2, A3, A3b). Nonexistent line numbers are accepted.
6. **K2 does not check what the correction says** — A1/B5 markers reading “acknowledged; no claim made.” yield `k2=0`. The tool cannot distinguish a correction from an acknowledgement. This is also the honest answer to the routed-defect question below.
7. **K2's documented append-only property is not implemented** — the docstring (line 9) says “an in-place edit is a mismatch”, but line 92 checks only `phrase in lines[ln-1]`. Rewriting `LOG.md:1758` to “The r26 receipt verifies fully; all 1382 records are present and complete.” while keeping the phrase yields `k2=0` (B5). The phrase is 9 words of the sentence; the rest of the line is unconstrained.
8. **The instrument is invocation-controlled** — `--list-rev` is optional (`main`, line 104) and defaults to `--rev`; `--stale-list` can be overridden; and `--rev` is only checked with `cat-file -e`, so any full-40 commit is accepted, including one never landed. A8/A9b print `k2=0` with the statements untouched; D1 prints a clean `rc=0` for a scratch-only commit.
9. **C1 does not measure calibration as the axis defines it** — no predicate reads the self-assessment. The in-tree instrument that does (`tools/souji-declared-evidence.py`, SCORECARD declarations vs bytes) reports `mismatches=19` at the prereg rev (executed, rc 1). `mismatches=0` from C1 is consistent with a self-assessment that is still wrong; K2 touches self-assessment text only as a phrase-presence check on one SCORECARD table row.
10. **No truthful-correction cross-check** — the real r26 fact (`failed=152`, GNU-escaped records valid) is measurable only by `census/round-29/c2-counter.py`. C1's K2 never re-derives it, so a marker can claim the opposite of what C2 measures (B5 does exactly that) and still pass.

## Answers to the two judgement questions

- **Does `mismatches=0` measure calibration or only bookkeeping consistency?** Only bookkeeping consistency of two declaration families (registry used-by cells, entry front-matter citations, four phrase markers). It measures neither the SCORECARD axis numbers nor the observed state the axis claims to describe. Base 10 → 0 is a real, non-vacuous delta, but the target is gameable by amnesia: erasing or relocating declarations lowers the count exactly as repair does (A5, A6c, C2, row-delete, B1, B2).
- **Is r28 routed defect 2 closed by K2 or relabelled?** Relabelled. Defect 2 owed an append-only correction saying the r26 records are valid GNU escapes and the real defect is 152 absent records. K2 enforces the retained phrase and the existence of a marker naming `file:line`; it never enforces the corrected content, and its “append-only” promise fails on an in-place rewrite (B5). The substance of defect 2 is closed, if at all, by C2's `failed 152 → 0`; C1's K2 only adds a tombstone.

## Smallest safe corrections (stricter-only, for the L1 to log)

1. **Pairing, not mention (kills B1/B2, and makes S215's used-by honest).** For every `(id, path)` in a used-by cell, require `path` to be a committed blob under `corpus/knowledge/` whose front-matter `source:` lines cite `id`. One added condition; the existing mention test becomes redundant.
2. **Citation floor and scan repair (kills A5/A6c/B4/C2/D1).** Every `corpus/knowledge/**.md` (any depth) must carry ≥1 front-matter `source:` line, matched case-insensitively; a `source:` line occurring after the first heading is a mismatch, not an ignored line; drop the depth-2 restriction.
3. **Enumeration floor (kills A7 and row deletion).** Parse rows with `^\s*\|\s*S\d{3,}\s*\|`, fail if a row is non-canonical, and require the parsed id count to equal a count recorded in the stale/registry freeze (139 at the prereg rev).
4. **Exact marker (kills A2/A3/A3b).** Tag must match with a digit boundary (`(?!\d)`), and one marker line may name exactly one tag.
5. **Byte-level append-only + content (kills A1/B5).** Record the exact stale line's sha256 in the frozen TSV and require equality at REV; require the marker to carry `corrected: <text>` plus a `verified-by:` command whose expected number the counter re-derives (e.g. `failed=152`, `escaped-records=2`) so “acknowledged” and inverted text fail.
6. **Invocation pinning (kills A8/A9b and D1's rev pick).** Make `--list-rev` mandatory and hash-pin the stale list to the prereg blob; hash-pin `--stale-list` or remove it; require REV to be the tip of `refs/heads/master` (or an explicitly recorded commit range) and print the resolved tip in `SUMMARY`.

## Attack log

- A1 content-free markers → accepted, `k2` 4→0 (`6d5d93ec…`). Rejected by correction 5.
- A2 marker naming a nonexistent line (`:17580`, `:2300`, `:220`, `:400`) → accepted (`e540da04…`). Rejected by correction 4.
- A3/A3b blanket and verbatim-copied markers → accepted (`0c577c13…`, `45044759…`). Rejected by correction 4.
- A5 deleting `source:` lines → `k1` 6→2, but the deletion surfaces `used-by-no-cite S087` and `S215`, so deletion alone is not the cheapest route; moving the lines (A6c) is (`cd59a0d2…`, `e5c6be61…`). Rejected by correction 2.
- A6c source lines moved below the heading → S024/S025 checks gone, `k1` 6→4 (`e5c6be61…`). Rejected by correction 2.
- C1/C2 demote S024 to `rejected` → rejected status alone changes nothing; emptied used-by plus moved citation is accepted (`52bb3c48…`, `84e3858f…`). Rejected by corrections 1+2; status must not be the mechanism.
- Row deletion S025 + moved citation → accepted, 139→138 rows (`a04ba0ec…`). Rejected by correction 3.
- A7 four-space indent on S215 → row dropped, `k1` 6→5 (`3d447045…`). Rejected by correction 3.
- B4 nested entry cites S001 unchecked while the depth-2 control is flagged (`30494e5f…`). Rejected by correction 2.
- B1/B2 used-by → registry self-reference / lesson mention → accepted (`1a447b64…`, `98db0185…`). Rejected by correction 1.
- A8/A9b stale list emptied or redirected, `--list-rev` omitted → `k2=0` with statements untouched (`124be868…`, `f04a9fce…`). Rejected by correction 6.
- B5 in-place inversion of `LOG.md:1758` + free markers → `k2=0` (`8f469da4…`). Rejected by corrections 4+5.
- D1 composed cheat → `k1=0 k2=0 rc=0` with no true fact (`af7fe69b…`); residual truth: S215 absent from the entry, 152 r26 records still missing under C2, declared-evidence still 19. Rejected only by a combination of 1+2+4+5 (correction 1 alone also blocks the S215 used-by cell).

[INFERENCE] The same edits compose with the C3 rows S216-S219 at the final tip (the counters' parsing is independent of which ids exist); D1 was built on the prereg tree, where those rows do not exist yet.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmCritic47.md` (this report). No delivery file was named for this seat.
