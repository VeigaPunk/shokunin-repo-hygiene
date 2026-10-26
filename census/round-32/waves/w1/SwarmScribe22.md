# SwarmScribe22 — C3 entry draft (r32 w1)

## Status

STATUS: PASS — `corpus/knowledge/jj-abandoned-object-mtime-clock.md` is drafted at the delivery path
with the r31 front-matter conventions, three tag-verified snapshots opened this run, 23 located Gate
quotes with exact line spans, one ADMIT and two REJECT lines, and eight Observed spans that are whole
lines of the fixture seat's record delivery. A simulated gate run prints
`entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0` (rc 0). The C3 counter itself was not run: its
fixture and record are still wave-1 deliveries, not installed at REV, and this seat executes no
fixture.

## Evidence

Scratch was `/fast/scratch/hyaku/souji-r32/SwarmScribe22` (`TMPDIR` set inside it) and is removed.
Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d` (branch master); preregistration read as a file at
`census/round-32/records/preregistration.txt` (commit `3ec84fc…`).

1. Sources fetched live from tag v2.56.0, hashed, and `cmp`-equal to the wave-1 fetch copies at
   `.ufo/waves/round-32/w1/sources/`:

```
curl -fsSL -o up-gitformat-pack.adoc https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc
curl -fsSL -o up-git-gc.adoc        https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc
curl -fsSL -o up-gc.adoc            https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc
ec285ba4f4e15a68ad83a570eaf74e8549b477496e49933126ef935d9291381b  27494 B  gitformat-pack.adoc
e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c   6744 B  git-gc.adoc
0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a   7753 B  config/gc.adoc
```

2. Gate verification over the final entry: 23 quote bullets, each quote verbatim in the snapshot named
   on its own line, each claimed line span equal to the span computed from the bytes, word counts 5–20,
   zero pipe characters, zero double-quoted spans in the Gate outside those bullets, `opened:
   2026-10-26` present, Gate URLs limited to `git-scm.com/docs/git-gc` and the raw gitformat-pack URL.
   Nine spans were off by one line in the first draft and were corrected (`gitformat-pack.adoc:638-640`,
   `:667-668`, `:682-683`, `:351-353`; `git-gc.adoc:63-64`, `:64-65`, `line 84`; `gc.adoc:line 97`,
   `lines 100-102`), as were four body anchors.

3. Gate checker pre-flight in a simulated root (three snapshots under `census/round-32/sources/`, a
   lane copy of `corpus/SOURCES.md` plus one **simulated** S223 row, the lane's empty slice/verdict
   files, the entry copied to `corpus/knowledge/`):

```
cd $R && python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-26 \
  --entries corpus/knowledge/jj-abandoned-object-mtime-clock.md --snapshot-dir census/round-32/sources \
  --slice census/round-32/records/empty-slice --slice-verdicts census/round-32/records/empty-verdicts
entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0
rc=0
```

   The S223 row exists only in that simulated root. Its shape, which L6 needs (`rows[i][2]` the URL
   cell, `rows[i][9]` the opened date), is
   `| S223 | <source cell with the raw URL> | docs | A | <scope> | <anchor> | <teaches> | mined | 2026-10-26 | on-release | corpus/knowledge/jj-abandoned-object-mtime-clock.md |`.

4. Record delivery cross-check (read-only), `.ufo/waves/round-32/w1/deliver-jj-mtime-clock-run.txt`
   (1887 B, sha256 `01cf6dc0011ae8f22d16922846b6834641df5dbce6e3a26cd0c267ede97e8254`): 24 lines, 22 of
   them `RESULT`, every one matching the frozen `census/round-32/c3-contract.txt` (keys in order,
   values in their sets) — 0 bad; five arms with a `gc-` step each; `mixed` has `gc-` lines for both
   B and C; three `object_present=no`, nineteen `yes`. All eight entry spans are whole lines of it.

5. Not run: `census/round-32/c3-counter.py`, `tests/fixtures/r32-jj-mtime-clock.sh`, any
   `sources-census.sh` call, any lane mutation. No tools installed, no pacman transaction, no network
   write beyond the three `curl` reads.

## Findings

1. **Gate URL binding is the integration point that can silently fail (L6).** Twelve Gate bullets and
   the S223 source line name
   `https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc`; L6 requires
   every Gate URL to be a substring of a cited row's `source` cell, so the new row must carry that exact
   raw URL, not a served alias. Location:
   `.ufo/waves/round-32/w1/deliver-entry-jj-abandoned-object-mtime-clock.md:1`, `:200-211`.

2. **The config-fragment quotes sit behind a page-scoped cell.** `gc.cruftPacks` (`gc.adoc:86-88`) and
   `gc.pruneExpire` (`:97`, `:98-99`, `:100-102`, `:102`) come from `Documentation/config/gc.adoc`,
   included into git-gc(1) by `git-gc.adoc:136`. S002's cell (`corpus/SOURCES.md`:23) scopes
   `§ CONFIGURATION gc.reflogExpire, gc.reflogExpireUnreachable, gc.rerereResolved, gc.rerereUnresolved,
   gc.worktreePruneExpire` and S063's (`:84`) scopes `§ NOTES first paragraph`; neither names the
   fragment. The Gate names the served URL both cells do carry (`https://git-scm.com/docs/git-gc`), so
   the check binds, but the anchor is a page that renders the fragment rather than the fragment itself —
   the shape the r31 wave-2 correction flagged. L1: extend one cell with `§ CONFIGURATION` and the raw
   `config/gc.adoc` URL, or record the served-URL anchor as a deliberate choice.

3. **The record settled two draft predictions and refuted a third.** The first draft's placeholders
   predicted `arm=nocruft step=gc-cruft-disabled obj=B … object_present=yes` and treated
   `--prune=never` as a loose-only lever. The delivered record shows
   `RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=absent object_present=no` (the old
   object is dropped from the loose set; the recent C stays loose) and
   `RESULT arm=mixed step=gc-prune-never obj=B mtime=old where=cruft object_present=yes` (the flag puts
   the old object into a cruft pack and keeps it). Claim 7 was rewritten from "narrower lever" to the
   measured reach, and claim 5 now states the two removal paths separately. Locations: entry `:67-93`,
   `:112-122`.

4. **`where=cruft` is decided by the `.mtimes` file's existence, not by reading it.** The fixture's
   `where()` reports `cruft` only when the pack holding the object has a `.mtimes` sibling
   (`tests/fixtures/r32-jj-mtime-clock.sh:107-120`, delivery copy
   `.ufo/waves/round-32/w1/deliver-r32-jj-mtime-clock.sh`). The entry therefore claims the per-object
   clock as document (claim 4) plus outcome (claim 5) and says in `## What this does NOT establish` that
   no individual date from the table is reported.

5. **The old arms remove the descendant keeper deliberately.** `seal()` drops every keep ref naming the
   tracked commit or a descendant and expires every reflog before the first `RESULT` line (`:197-202`),
   and `backdate_island` backdates the whole unreachable island (`:231-236`) so a recent rewritten
   descendant cannot hold B through reachability — which is why the record isolates the mtime and says
   nothing about precedence against a live ref.

6. **`git-gc.adoc` at tag v2.56.0 is the round-30 capture byte for byte** (sha256 `e3dbc408…`,
   6744 B). The r32 snapshot can be that blob, but L4 still needs a blob at
   `census/round-32/sources/git-gc.adoc` with a `SHA256SUMS` line and a `fetch-receipts.tsv` row whose
   http field is `200`; the wave-1 copies are those bytes.

7. **Two quotes are truncated to avoid the adoc's own double quotes.** `gc.adoc:100-101` contains
   `"now"` and `:102` contains `"never"`; L5 counts every double-quoted span in the Gate, so a one-word
   span would fail. The Gate quotes start at `may be used to disable …` and `may be used to suppress
   pruning.`; any later edit that spans the value word re-breaks L5. Entry `:221-222`.

8. **Five Observed spans became eight, all record lines.** The entry now quotes whole lines for
   recent/gc-default, old/gc-default, mixed at `gc-prune-never` and at `gc-default` (B and C), never at
   `gc-pruneexpire-never`, and nocruft at `gc-cruft-disabled` (B and C). L10's condition — every
   backticked `RESULT` span is a whole line of the run record — holds against the delivered record and
   will hold at landing provided the record is installed unchanged (`cmp`).

9. **Remaining L1 work on this entry**: install it as
   `corpus/knowledge/jj-abandoned-object-mtime-clock.md`; install the three snapshots with `SHA256SUMS`
   and `fetch-receipts.tsv` rows; install the fixture and the record byte-identical (the record's 22
   lines are the ones the entry quotes); open and number the gitformat-pack row (placeholder S223,
   renumber by document) with the raw URL in its `source` cell; update the F1 map row, the frontier
   line and `PROVINCE.md` in the same commit.

## Attack log

No attack filed: no predicate, target, counter or item set was contested and none was changed. Two
draft predictions were replaced by record bytes after the fixture seat's delivery appeared; that is
evidence being corrected to the measured state, not a change to the frozen contract.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-entry-jj-abandoned-object-mtime-clock.md` — the entry draft, 227
  lines, 24692 B, sha256 `d7901ad3997d441b607104797a5fc73a932086ba870e4be8a09c657165561197`: front
  matter (`source:` x3, `verified-at:`, `recheck:`, `ground: F1`), the claim in seven numbered steps,
  Observed with eight whole record lines and the field definitions, the receipt consequence, what it
  does not establish, the lane link, and the Gate (23 located quotes, `opened: 2026-10-26`, 1 ADMIT, 2
  REJECT).
- `.ufo/waves/round-32/w1/SwarmScribe22.md` — this report.
