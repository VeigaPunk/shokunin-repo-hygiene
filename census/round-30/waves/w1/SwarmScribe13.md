# SwarmScribe13 — R30 C3 SOURCES rows

STATUS: PASS — S220/S221 drafted against sources opened at tag and validate clean (exit 0, 36 pre-existing W04, 0 E11) in a scratch mirror; the two remaining requested slots resolve to existing rows S054 and S063 instead of duplicates.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, base revision `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` (read-only; no lane byte written, no git/jj mutation).

Sources fetched independently this run (2026-10-26), then sha256 compared to the staged C3 snapshots:

```
raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap   154561 B  b3306943…3554
raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs             102068 B  95147270…6c69
raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/operation-log.md                3334 B  2a48dab8…ce18
raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc              6744 B  e3dbc408…ba8c
```

`cd .ufo/waves/round-30/w1/sources && sha256sum -c SHA256SUMS` → `cli-reference@.md.snap: OK`,
`git_backend.rs: OK`, `operation-log.md: OK`, `git-gc.adoc: OK`, `cli-reference.md: OK`.

Registry validation (scratch mirror of the lane with S220/S221 spliced after `corpus/SOURCES.md:164`):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --file /fast/scratch/hyaku/souji-r30/SwarmScribe13/val/corpus/SOURCES.md --today 2026-10-26
…
file	W04	S063 duplicate url git-scm.com/docs/git-gc across scopes
…
file	W04	S216 duplicate url man7.org/linux/man-pages/man2/statx.2.html across scopes
file	ok	/fast/scratch/hyaku/souji-r30/SwarmScribe13/val/corpus/SOURCES.md
EXIT=0
```

36 W04 lines total, all pre-existing; no W04/E04/E11 from S220/S221. Without the placeholder for the
not-yet-landed entry the same tree printed exactly two extra lines (`E11 S220`, `E11 S221`, missing
`corpus/knowledge/jj-keep-ref-expiry.md`) and `EXIT=1`.

Full quotes, per-row word counts, the slot-substitution record and the complete validate output are in
`deliver-sources-rows.md`.

## Findings

1. **Slot 2 and slot 4 are already held; drafting them would duplicate evidence.** `corpus/SOURCES.md:75` (S054) is `lib/src/git_backend.rs` at tag v0.45.1 with scope "creation and removal of `refs/jj/keep/*`" and anchors `:900-953 recreate_no_gc_refs, :1558-1564 gc` — the requested gc/keep-ref row. `corpus/SOURCES.md:84` (S063) is git-gc reachability, and `corpus/knowledge/jj-colocation-receipts.md:86` already attributes `git-gc.adoc@v2.56.0:18, 81-83` to S063. Used-by appends implied: S054 `corpus/knowledge/jj-colocation-receipts.md` → `corpus/knowledge/jj-colocation-receipts.md, corpus/knowledge/jj-keep-ref-expiry.md`; S063 identical shape.

2. **The versioned CLI-reference page is really v0.45.1, but its canonical link says otherwise.** `https://docs.jj-vcs.dev/v0.45.1/cli-reference/` (`<link rel="canonical" href="https://docs.jj-vcs.dev/latest/cli-reference/">`) differs from `/latest/` only by 0.46-only headings (`jj file delete`, `jj file edit`, `jj util diff`, `jj workspace remove`), and its `jj util gc` text equals tag snapshot lines 3789-3803. S220 therefore cites the tag snapshot as the source of record and names the served page as the human-facing rendition.

3. **`docs/operation-log.md` at v0.45.1 does not document `jj op abandon`.** `grep -c abandon` → `0`; the only discard verbs are `jj undo`, `jj op revert`, `jj op restore` (`:15-18`). S221 is scoped to the operation-log model only, and its scope cell states the exclusion so the entry cannot cite it for abandon semantics.

4. **E11 for the new rows is gated on another seat's deliverable.** `corpus/knowledge/jj-keep-ref-expiry.md` does not exist in the lane yet (checked 2026-10-26); the exit-0 run used a scratch-only placeholder, disclosed in the delivery. The L1 must re-run the same validate command after the C3 entry lands — with no placeholder — and require E11 = 0.

5. **S054's anchor list omits the git-gc argument it teaches about.** `git_backend.rs@v0.45.1:975-977` is `.arg(format!("--prune=@{} +0000", keep_newer.as_secs()));` with the `run_git_gc(` call at `:1575-1578`; the anchor cell stops at `:1558-1564 gc`. Optional anchor addition, not a re-grounding — L1 decides.

6. **Pre-existing registry warnings surfaced, not introduced.** The 36 W04 lines include S002/S063 sharing `git-scm.com/docs/git-gc` across scopes (`corpus/SOURCES.md:23`, `:84`) and S210 at `:155` duplicating a `raw.githubusercontent.com` URL. They do not fail validation, and this item neither fixes nor worsens them.

## Deliveries

- `.ufo/waves/round-30/w1/deliver-sources-rows.md` — S220/S221 rows, grounding quotes with locations, slot-substitution record with used-by diffs, validation transcript.
- `.ufo/waves/round-30/w1/SwarmScribe13.md` — this report.

Scratch `/fast/scratch/hyaku/souji-r30/SwarmScribe13/` removed. No tool was installed or upgraded.
