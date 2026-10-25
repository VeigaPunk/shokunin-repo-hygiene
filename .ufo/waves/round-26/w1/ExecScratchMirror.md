## Status

STATUS: PASS — delivered `.ufo/waves/round-26/w1/mirror-build.py` (417 lines, mode 0755, sha256 `15b9d9d47f6cd3d3a9866c0f65f57bb6d1964d816f0c18dd3b6c0ecda175f3e4`), a runnable C2 scratch-mirror builder taking `--entries-dir` and `--rows-file`. Exercised end-to-end on a synthetic corpus in `/var/tmp` (1 positive build + 13 refusals + 1 usage refusal + 1 warning-only build, all as specified), plus a probe of the real scribe draft bytes against a synthetic registry carrying the five target ids. It was never run against the real lane corpus, per instruction; no lane bytes were written.

## Evidence

Lane revision during the work: HEAD `ea0bbe66c974`, base `0eca7c8a5d10…`. Read-only `git` only; no `git add/commit/push/checkout/reset`, no `jj`, no signals, no writes outside my two deliverable paths, no tool installs (host `python3` 3.14.8, `bash` 5.3.20, existing `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`).

Base row literal the builder binds to (default `--expect-rows-before 127`):

```
$ git show 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd:corpus/SOURCES.md \
    | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
127
$ grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md   # worktree, after the append landed
132
```

Positive self-test (synthetic corpus with 1 existing mined row; the `SOURCES.md` header copied verbatim from `corpus/SOURCES.md:20`; rows file = 5 synthetic rows on the frozen id set):

```
$ python3 -B .ufo/waves/round-26/w1/mirror-build.py \
    --corpus /var/tmp/souji-r26-ExecScratchMirror/synth/corpus \
    --entries-dir /var/tmp/souji-r26-ExecScratchMirror/entries \
    --rows-file /var/tmp/souji-r26-ExecScratchMirror/rows.good \
    --dest /var/tmp/souji-r26-ExecScratchMirror/mirror --expect-rows-before 1
mirror=/var/tmp/souji-r26-ExecScratchMirror/mirror
source_corpus=/var/tmp/souji-r26-ExecScratchMirror/synth/corpus
rows_before=1
rows_appended=5
rows_after=6
ids_appended=S128,S129,S130,S131,S132
rows_sha256=db44b43cc52c5be54e47054186175c64cb0f088cf94cdd29a1c956c9d5f7d5c6
source_registry_sha256=5694d10a4d8771718f2d861b34632e65a6a8817f7ca7e791309312ab2c8d29fc
mirror_registry_sha256=bb944de7b43a0fa04d91f9b0532be0dfeb11a6b76772d893e311c70777b5e1b8
entries=2
entry corpus/knowledge/git-auto-maintenance-trigger-set-r23.md
entry_sha256 corpus/knowledge/git-auto-maintenance-trigger-set-r23.md 30b54f40bd4478466410369372466c7832ddf157ca84e42989d8e972d6dcf7d9
entry corpus/knowledge/git-auto-maintenance-trigger-set.md
entry_sha256 corpus/knowledge/git-auto-maintenance-trigger-set.md ad4d1f05576fc041cbecf0cf6d0cd06258732bcbb41d29d3ec4b0abb5c976130
file	ok	/var/tmp/souji-r26-ExecScratchMirror/mirror/corpus/SOURCES.md
validate_exit=0
```

The last two lines are `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file <mirror>/corpus/SOURCES.md` itself (exit 0); the script prints that exit code as `validate_exit=<n>` and propagates it. Mirror shape after insertion — rows land inside `## Registry`, not after `## Paths`:

```
$ sed -n '3,14p' mirror/corpus/SOURCES.md | cut -c1-50
## Registry

| id | source | kind | tier | scope | anchor | tea
|---|---|---|---|---|---|---|---|---|---|---|
| S001 | Existing doc — https://example.test/exi
| S128 | Synthetic fetch doc — https://example.t
| S129 | Synthetic builtins — https://example.te
| S130 | Synthetic pull — https://example.test/p
| S131 | Synthetic fixture — https://example.tes
| S132 | Synthetic census — https://example.test

## Paths
```

The source corpus is never written: its digest is re-checked after the build (`source_registry_sha256` before == after, `5694d10a…`).

Refusal and warning cases (each on its own `--dest`; observed exits):

| case | exit | message |
|---|---|---|
| rerun over an existing mirror, no `--force` | 1 | `REFUSED: dest … holds a previous mirror; pass --force to replace` |
| default row-count binding (1 row vs 127) | 1 | `REFUSED: registry holds 1 rows, not the frozen base literal 127` |
| escaped pipe in a cell | 1 | `REFUSED: …rows.escpipe:3: escaped pipe inside a cell (C2 kill rule)` |
| NF != 13 | 1 | `REFUSED: …rows.nf:3: NF=12 (want 13)` |
| kind off-enum (`slides`) | 1 | `REFUSED: S129: kind='slides' not in the census enum` |
| status not mined (`queued`) | 1 | `REFUSED: S129: status='queued' (frozen contract: mined)` |
| id outside the frozen renumber set | 1 | `REFUSED: ids ['S127','S129',…] != frozen renumber target ['S128',…]` |
| duplicate id in the block | 1 | `REFUSED: …:10: duplicate id S131 in the append block` |
| row already in the registry | 1 | `REFUSED: append block repeats registry ids: ['S132']` |
| entry cites an unappended row | 1 | `REFUSED: …/git-auto-maintenance-trigger-set.md: cites rows not in the post-append registry: ['S999']` |
| used-by names a non-admitted entry | 1 | `REFUSED: S128: used-by 'corpus/knowledge/other.md' is not one of the admitted entries […]` |
| entries-dir without the drafts | 1 | `REFUSED: admitted entry missing from --entries-dir: git-auto-maintenance-trigger-set.md` |
| dest outside `/var/tmp` and the lane | 1 | `REFUSED: dest /home/vgpnk/Projects/shokuknow/mirror-x is outside /var/tmp and the lane repo (hard bound)` |
| only one `--entry` mapping | 2 | `exactly 2 admitted entries are required, got 1` |
| entry without `ground: F1` | 0 | `WARN …: no 'ground: F1' line (C2 K1 will score 0)` (build and validate still exit 0) |

Static refusals create no dest directory (`ls -d m-bad7` → `none`); the `shokuknow` refusal wrote nothing (`mirror-x` absent). Real-byte parser check, read-only (the 5 landed rows extracted with `sed -n '149,153p'`; no corpus copy, no validate run):

```
parsed_rows=5 ids=S128,S129,S130,S131,S132
cells_per_row=[11]
pipes_in_cells=0
```

Real scribe draft probe — the two w1 drafts copied under their final basenames and run against the *synthetic* registry that carries the five target ids (so entry-side checks and the mirror validate are exercised on the drafts' real bytes, without touching the lane corpus):

```
$ sha256sum …/entries-real/*.md
53144e1d…  git-auto-maintenance-trigger-set.md        (copy of .ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md)
449eccab…  git-auto-maintenance-trigger-set-r23.md    (copy of …/entry-git-auto-maintenance-trigger-set-r23.md)
$ python3 -B …/mirror-build.py --corpus synth/corpus --entries-dir entries-real \
    --rows-file rows.good --dest m-real-drafts --expect-rows-before 1
entry_sha256 corpus/knowledge/git-auto-maintenance-trigger-set-r23.md 449eccab4ba37e792da386837c1c0841c374741bca2b55326307f36786d7f865
entry_sha256 corpus/knowledge/git-auto-maintenance-trigger-set.md 53144e1d237c4dac09f47a1db041342af15598831655d3347fa2f0a922ca7014
file	ok	/var/tmp/souji-r26-ExecScratchMirror/m-real-drafts/corpus/SOURCES.md
validate_exit=0        (exit=0; no WARN lines — both drafts carry 'ground: F1' and only S128-S132 citations)
```

`--help` exits 0; all runs used `python3 -B` (`find …/w1 -name __pycache__` → `0`); `git status --porcelain` shows my two files as the only additions from this seat.

## Findings

1. **The rows file must be the pure 5-row block; the draft beside it is a grep trap.** Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/sources-append-block.md:27-31` holds the 5 normalized rows, while `:39-51` keeps the 5 staged pre-renumber rows (S109/S110/S111/S123/S131) for the mapping table and `:1-24` is prose. Passing the whole file is refused (`…:3: row must start and end with '|'`); passing `grep -E '^\| S[0-9]{3,} \|'` on it is refused at its 10th line (`duplicate id S131`). The builder never guesses: the L1 should hand it a 5-line file (`sed -n '27,31p'` of that draft).

2. **The draft-entry filenames are not the final basenames, so the default mapping will not fire on `.ufo/waves/round-26/w1`.** Location: `.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md` and `entry-git-auto-maintenance-trigger-set-r23.md`, versus `mirror-build.py`'s default map `corpus/knowledge/<basename>`. Supply `--entry` for both (supplying any `--entry` replaces the default pair — verified, and a single `--entry` is a usage refusal), e.g.
   `--entry entry-git-auto-maintenance-trigger-set.md=corpus/knowledge/git-auto-maintenance-trigger-set.md`.

3. **`/var/tmp/souji-r26-mirror` is already occupied by another seat's build and is not mine to touch.** Location: `/var/tmp/souji-r26-mirror/` (mtime 14:22, `corpus/ tools/ tests/ validate.out`, no `.souji-mirror-build` marker). The default `--dest` therefore refuses there (`non-empty and carries no .souji-mirror-build marker`) and leaves the directory byte- and mtime-identical (`before=14:22:29.191726460`, `after=14:22:29.191726460`). The L1 must pass an explicit fresh `--dest`; the prereg-verbatim choice is `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/assimilation/validate` (permitted; built and validated to exit 0 in a throwaway child of my report directory, then removed).

4. **The mirror must be built from the base registry bytes, not from today's worktree.** Location: `preregistration.txt` C2 SCRATCH MIRROR GATE ("must exit 0 BEFORE the first real append") versus lane state: `0eca7c8:corpus/SOURCES.md` has 127 rows, the worktree has 132 (append landed at `d6c13b0`/`ea0bbe6`). A worktree build refuses twice over (`registry holds 132 rows, not … 127`; `repeats registry ids: ['S128',…]`). Reproduce the gate by copying the corpus and overwriting `<copy>/corpus/SOURCES.md` with `git show 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd:corpus/SOURCES.md`, then point `--corpus` at that copy; `--expect-rows-before` (default 127) makes any drift loud instead of silent.

5. **Entries must be dropped inside the mirror because `used-by` resolves against the mirror root.** Location: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:500-501` (`dir_abs=$(realpath -- "$(dirname -- "$file_abs")/..")`) and `:567` (`[ ! -e "$dir/$path" ]` → E11). A mirror carrying only `SOURCES.md` would report E11 for every mined row; the builder copies the two entries to `corpus/knowledge/<basename>` inside the copy and pre-checks each row's `used-by` against the actual entry set.

6. **`ground: F1` is deliberately a WARN, not a refusal.** Location: `mirror-build.py` `main()`, ground check. K1 (`git grep -l '^ground: F1'`) is the frozen counter for that property; making the mirror builder a second gate for it would let a mirror refusal masquerade as a C2 result. The warning is visible in the receipt and the validate arm still decides the exit code.

7. **The receipt binds bytes, not just structure.** Location: `mirror-build.py` output block. `rows_sha256`, `source_registry_sha256`, `mirror_registry_sha256` and per-entry `entry_sha256` let the L1 tie the validated mirror to the landed bytes; copy those lines into `c2-gate.tsv` and compare against the committed files.

## Attack log

My item is a builder, not a claim; these are adjacent contract attacks reported, not performed:

- **A1 — stale-gate swap.** The C2 gate validates the mirror's bytes, not the committed bytes, so a seat could validate placeholder entries/rows and land edited ones afterwards. `sources-census.sh` never compares the mirror with the lane (`--file` mode only parses and checks paths under the mirror root), and the `--root … souji` arm checks only the row count. Mitigation available now: compare landed files against the receipt's `rows_sha256`/`entry_sha256`; a mismatch voids the gate receipt.
- **A2 — count-blind mirror.** The mirror arm exits 0 on 131 or 133 rows, so a mirror built from a drifted registry could "pass". `--expect-rows-before` (default 127) binds the before-count and the receipt prints `rows_after`, which must be 132.
