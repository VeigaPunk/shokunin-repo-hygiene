# SwarmExecutor07 — C3Snapshots (wave souji-r30-w1)

## Status

STATUS: PASS — five source snapshots pinned byte-exact (the four named URLs plus the docs include page), `sources/SHA256SUMS` and a 5-row fetch receipt written, every requested anchor line located from those exact bytes, scratch removed. No lane bytes touched; no installs (nothing needed).

## Evidence

Fetch (scratch `TMPDIR` `/fast/scratch/hyaku/souji-r30/C3Snapshots`, now removed), into `.ufo/waves/round-30/w1/sources/`:

```
$ curl -fsSL -m 60 -o <basename> <url>      # 2026-10-26T04:43:49Z (4 files), 04:44:49Z (cli-reference.md)
$ curl -s -o /dev/null -w '%{http_code}' <url>   # all five: 200
```

Tag pins (`git ls-remote`, full ids):

```
jj-vcs/jj refs/tags/v0.45.1 -> 7c41cdeb16b6b321c64e789a966b6adf723816a5      (lightweight)
git/git   refs/tags/v2.56.0 -> 2478544319491bbd2a42cc57a83e3d2f4730a280      (tag object)
                             -> a018953688f1b10bddf91bff8747068f5f4746a4     (commit)
```

Digests and sizes (`sha256sum`, `stat`; `sha256sum -c SHA256SUMS` with cwd `sources/` → 5 × `OK`):

```
b330694348c2a6fb21b637425c711d48ac9fa41d0b3596b4ca2955f7a9333554  cli-reference@.md.snap  154561 B  4038 lines
95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69  git_backend.rs          102068 B  2610 lines
2a48dab85483f8bed666ccc1aebd458d70f4ff57ece1a122aee8889b3209ce18  operation-log.md          3334 B    65 lines
e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c  git-gc.adoc               6744 B   187 lines
5832fd949ae8b876fde7dc97cd5a92a3c26055de136eb76c53f7d1ade1487dbb  cli-reference.md           674 B    20 lines
```

Byte-identity of each snapshot against the tag archives (`codeload.github.com/.../tar.gz/refs/tags/v0.45.1`, `.../git/git/.../v2.56.0`, compared with `cmp`): `CLI-REF-SNAP-IDENTICAL`, `GIT_BACKEND-IDENTICAL`, `OPLOG-IDENTICAL`, `CLIREF-DOC-IDENTICAL`, `GIT-GC-ADOC-IDENTICAL`.

Anchor sweep for the item (3) choice (`grep -rn "op abandon"` over all 53 `*.md` under `docs/` at the tag): exactly one hit, `docs/working-copy.md:114`; `grep -c abandon docs/operation-log.md` → `0`.

`git gc` argv probe, scratch repo, installed `git version 2.56.0`:

```
$ git --git-dir=. gc --prune=@1792903642 +0000      -> usage: git gc [<options>]; rc=129
$ git --git-dir=. gc "--prune=@1792903646 +0000"    -> rc=0
$ # unreferenced loose blob: cat-file -e rc 0 before, rc 1 after gc --prune=@<now+3600> +0000
```

## Findings

1. `jj op abandon` is documented in the generated CLI reference, not in `docs/operation-log.md`. `sources/cli-reference@.md.snap:2411` is the section heading, `:2413` "Abandon operation history", `:2415` "To discard old operation history, use `jj op abandon ..<operation ID>`." The operation-log doc at the tag never uses the word (0 matches in 65 lines). `sources/cli-reference.md:16` is the include (`include-markdown "../cli/tests/cli-reference@.md.snap"`) that makes the snapshot the docs page — that is the recorded choice for item (3).

2. `jj util gc` and its `--expire` text: `sources/cli-reference@.md.snap:3789` heading, `:3795` usage, `:3799` the `--expire <EXPIRE>` option line with description "Time threshold" (em dash U+2014, byte-verified), `:3801` "By default, only obsolete objects and operations older than 2 weeks are pruned.", `:3803` `Only the string "now" can be passed to this parameter.`. `:3793` states the order: abandon before gc.

3. Keep-ref namespace and survival rule: `sources/git_backend.rs:100` `const NO_GC_REF_NAMESPACE: &str = "refs/jj/keep/";` (comment `:99`). `recreate_no_gc_refs` exists under that name at this tag (`:902`); a keep ref survives iff `:925` `if new_heads.contains(&id) && name_good {` or its loose-ref mtime is newer than the cut-off, `:941` `if mtime > keep_newer {`; otherwise `:948-949` traces and queues it in `no_gc_refs_to_delete`; deletions plus new keep refs are applied in one transaction at `:964` `.edit_references(ref_edits)`.

4. The `--prune` argument jj passes to git is a single raw date argv element: `sources/git_backend.rs:977` `.arg(format!("--prune=@{} +0000", keep_newer.as_secs()));`, invoked from `run_git_gc` (`:970`) with `--git-dir=.` and `gc` (`:975-976`), called by the backend `gc` (`:1558`, keep refs first at `:1564`, git at `:1575`). Measured: git 2.56.0 rejects the same date split into two argv words (`rc=129`) and accepts/honours it as one word, pruning an unreferenced loose blob older than the cut-off.

5. `git-gc.adoc` `--prune` default: `:81` `--prune=<date>::`, `:82` "Prune loose objects older than date (default is 2 weeks ago," continuing `:83` "overridable by the config variable `gc.pruneExpire`)."; `:86-87` says it is on by default; `:160-161` is why a keep ref protects objects.

6. Integration requirement for the L1 (counter-enforced): `census/round-30/c3-counter.py:92` reads `census/round-30/sources/SHA256SUMS` keyed by basename and `:97` reads `census/round-30/records/fetch-receipts.tsv`, matching column 1 = http (`200`), 4 = sha256, 5 = snapshot path (`:14`), and `:70` resolves `snapshot:` paths against `census/round-30/sources`. So `sources/` (5 files + `SHA256SUMS`) and `deliver-fetch-receipts.tsv` → `census/round-30/records/fetch-receipts.tsv` are exactly where they must land; the extra `cli-reference.md` row is inert for L4 (L4 only scans `snapshot:` lines of the entry) and every snapshot must be ≥ 512 B (smallest is 674 B). Related entry-side constraints the sources must satisfy: L5 caps each double-quoted Gate span at 4..25 words (`:109`) and L6 binds every Gate https URL to the exact string in a cited row's cell (`:115-116`).

7. Negative claim sweep: no other at-tag docs file documents `jj op abandon` — 53 markdown files under `docs/`, one incidental mention (`docs/working-copy.md:114`, "the operation has then been lost").

## Deliveries

Written under `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/` (nothing else, no lane mutation):

- `sources/cli-reference@.md.snap`
- `sources/git_backend.rs`
- `sources/operation-log.md`
- `sources/git-gc.adoc`
- `sources/cli-reference.md`
- `sources/SHA256SUMS`
- `deliver-fetch-receipts.tsv` (header `url	http	fetched_at	bytes	sha256	snapshot`; 5 rows, all http 200)
- `deliver-c3-anchor-lines.md` (anchor lines emitted from the snapshot bytes; tag pins; selection record; corroboration)
- `SwarmExecutor07.md` (this report)

Scratch `/fast/scratch/hyaku/souji-r30/C3Snapshots` removed (`rm -rf`, verified absent).
