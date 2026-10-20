STATUS: DONE — S071 quote is verbatim and 12 words at the pinned 2.56.0 page; version/anchor strings hold; row's anchor cell omits `-t` and its teaches cell names two commands the gate does not run.

# Reopen S071 — quote, anchor, version, row-cell overreach

Attacked claim: C2's source row `S071` (`corpus/SOURCES.md@5efb519`, row line 89) and the S071 provenance line in `corpus/lessons/round-18.md@5efb519:39` — that the recorded quote is verbatim at the located anchor and that the row's scope/anchor/teaches cells do not claim more than the served pages and the gate code support.

Probe discipline: no clone, no lane write, no execution of lane code; only `curl` reads of the two named pages, `git show`/`ls-tree` reads on the named lane repo, and `wc -w`. No tool installs or upgrades.

## 1. Quote — verbatim, at the located anchor

Served `https://git-scm.com/docs/git-cat-file` (HTTP 200; no redirect), raw HTML:

```
2244:<dt class="hdlist1" id="Documentation/git-cat-file.txt--e"><a class="anchor" href="#Documentation/git-cat-file.txt--e"></a>-e </dt>
2246:<p>Exit with zero status if <span class='synopsis'><em><span class="hover-term" data-term="object">&lt;object&gt;</span></em></span> exists and is a valid
```

The sentence continues on the next source line with `object.` — normalized to one space it is exactly `Exit with zero status if <object> exists and is a valid object.` The lesson's quote is byte-identical after whitespace normalization; it is the doc's first sentence (the second, "If <object> is of an invalid format, exit with non-zero status…", is not claimed).

- Located anchor: `#Documentation/git-cat-file.txt--e` (raw HTML line 2244), under the rendered `## OPTIONS` heading. The lesson's "§ OPTIONS -e" is an accurate human-readable form of that anchor.
- `wc -w` on the normalized sentence → `12` (lesson: "12 words" — correct).
- Pinned page `https://git-scm.com/docs/git-cat-file/2.56.0` carries the same `-e` term and sentence at the same raw lines 2244/2246.

## 2. Served version / last-updated lines

- cat-file: `<span class="light d-flex">git-cat-file last updated in 2.56.0</span>` (raw line 1324); version selector top entry `2.56.0 … 2026-09-28` (6/11 dots). Lesson's `("last updated in 2.56.0"` verified.
- Companion ls-tree `https://git-scm.com/docs/git-ls-tree`: `git-ls-tree last updated in 2.42.0` (line 1322), first version-list entry `2.42.1 → 2.56.0 no changes`. Both strings in the row's anchor cell are verbatim.

## 3. Row cells (`corpus/SOURCES.md:89` at 5efb519)

Commands: `git -C … show 5efb519:corpus/SOURCES.md | grep -n S071`; `… show 5efb519:tools/souji-landing-gate.py | sed -n '192,215p;798,802p'`; `git -C … ls-tree -r 5efb519 corpus` type census.

- **scope** — "existence of an object or rev:path at a revision; not a pointer grammar". `-e` grounds object existence directly. `rev:path` is shown on this page only for `--textconv/--filters`; for `-e` the argument is `<object>` and the page defers spellings to gitrevisions[7], so `rev:path` under `-e` is one small, standard inference. The negative clause matches house precedent (S035, S042, S045, S057, S059, S068 all carry "not …"). No overreach of substance.
- **anchor** — version strings and both anchors verified. Defect: the ls-tree half cites `§ OPTIONS -r, --name-only`, but the sentence that establishes the row's claim is `-t`: `Show tree entries even when going to recurse them. Has no effect if -r was not passed.` (`id="Documentation/git-ls-tree.txt--t"`, raw line 1666-1668). `--name-only`'s own text is only `List only filenames (instead of the "long" output), one per line.` The claim is therefore *under-anchored*, not false.
- **teaches** — "cat-file -e answers existence at a revision" is doc-true, but the pointer gate never calls it. Gate reads committed bytes via `git ls-tree -r -z --full-tree REV` (`tools/souji-landing-gate.py:195`), keeps only records whose type is `blob` (`:201-202`), cats blobs (`:209`), and tests existence with `git rev-parse --verify --quiet <rev>:<path>` (`blob_at_path`, `:211-224`). `grep 'rev-parse' corpus/SOURCES.md@5efb519` → no match, so the primitive the gate actually uses has no source row. Second half "ls-tree -r --name-only omits tree entries" is behaviorally true (below), but `--name-only` is not passed; the exercised flag set is `-r -z --full-tree`.
- The concluding clause "resolves against blobs plus their parent directories at REV, never the worktree" is code-accurate and correctly framed as a consequence: `list_tree(REV)` at `:195`; `check_pointers` folds every `os.path.dirname` prefix of every blob path into `tree_paths` (`:798-802`), so directories exist only via committed blob paths — never the worktree.

Behavioral check of the ls-tree claim at 5efb519 (read-only `git ls-tree` on the named repo):

```
git ls-tree -r 5efb519 corpus | cut -d' ' -f2 | sort | uniq -c
     36 blob
git ls-tree -r --name-only 5efb519 corpus | grep -c '/$'
0
git ls-tree -r -t 5efb519 corpus | cut -d' ' -f2 | sort | uniq -c
     36 blob
      3 tree
```

Tree entries appear only with `-t`; `-r` (without `-t`) plus `--name-only` emits no tree entries. The row's claim is right; its cited anchor is one option short.

## Verdict

**Agree** that the recorded quote is verbatim at the located anchor, is 12 words, and that both served version strings (`git-cat-file last updated in 2.56.0`; companion `git-ls-tree last updated in 2.42.0`, `2.42.1 → 2.56.0 no changes`) hold on today's served pages and on the pinned 2.56.0 page. **Disagree, partially**, with the row as calibrated: the anchor cell omits `-t` (the only option text that states tree entries are hidden by default) and cites `--name-only`, which the gate does not pass, while the teaches cell leads with `cat-file -e`, which the gate does not call; the gate's real existence predicate (`rev-parse --verify --quiet`) has no SOURCES row. This is an attribution gap, not a fabricated doc claim — every quoted string exists, and the gate's REV-vs-worktree behavior is exactly as taught.

Smallest fix (not applied — lane file): replace `ls-tree § OPTIONS -r, --name-only` with `ls-tree § OPTIONS -t ("Show tree entries even when going to recurse them"), -r; gate form -r -z --full-tree`; in teaches, replace `ls-tree -r --name-only omits tree entries` with `ls-tree -r lists blob entries only (tree entries need -t)` and either add `rev-parse --verify --quiet <rev>:<path>` as the gate's existence check or drop the `cat-file -e` lead. If the rev-parse primitive is to be sourced at all, it needs its own row (git-rev-parse(1)), since none exists.

Remaining unknowns: whether the wave-1 seat intended `--name-only` to describe the gate's command or only the doc form (report `SrcGitLsTree` not read); served HTML line numbers are reproducible today but not stable across re-renders — the fragment anchors (`#Documentation/git-cat-file.txt--e`, `#Documentation/git-ls-tree.txt--t`) are the stable locators.
