STATUS: DONE — git-ls-tree/git-cat-file opened and located; draft S064 row plus measured pointer-resolution semantics for LG-DANGLING-PTR.

Seat: SoujiR18.SrcGitLsTree-5. Lane: /home/vgpnk/Projects/shokunin/souji-shokunin @ b576341. No process, clone or lane file touched; report is the only write.

## 1. Sources opened

| # | URL fetched (exact) | Method | Revision line served | Access |
|---|---|---|---|---|
| a | https://git-scm.com/docs/git-ls-tree | native web fetch | "git-ls-tree last updated in 2.42.0"; "2.42.1 → 2.56.0 no changes" | 2026-10-20 |
| b | https://git-scm.com/docs/git-cat-file | native web fetch | "git-cat-file last updated in 2.56.0"; version entry 2.56.0 dated 2026-09-28 | 2026-10-20 |

Host `git --version` → `git version 2.56.0`. Both pages are the live vendor manuals; no tag-pinned copy was needed (the ls-tree page itself states no changes 2.42.1→2.56.0, and cat-file is at 2.56.0).

## 2. Draft registry row (candidate S064; L1 renumbers)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S064 | git-ls-tree(1) — https://git-scm.com/docs/git-ls-tree; companion git-cat-file(1) — https://git-scm.com/docs/git-cat-file | docs | A | `ls-tree -r --name-only` pathname emission and `cat-file -e <object>` existence on Git 2.56.0; not a dangling-pointer policy and not a token grammar | web manual "git-ls-tree last updated in 2.42.0", "2.42.1 → 2.56.0 no changes": § OPTIONS -r, -t, -z, --name-only, [\<path\>…]; § Output Format (core.quotePath paragraph); companion "git-cat-file last updated in 2.56.0" (2.56.0 dated 2026-09-28): § OPTIONS -e, § BATCH OUTPUT ("missing"); host git 2.56.0 | `-r` recurses into sub-trees and `--name-only` prints one filename per line, but tree entries appear only with `-t`, so a directory path is absent from a `-r --name-only` list; without `-z` pathnames with unusual characters are quoted per `core.quotePath`; `<path>` arguments are patterns, not literal paths; `cat-file -e <object>` exits zero iff the object exists and is valid and non-zero otherwise — the literal existence test, stated without a specific non-zero code | mined | 2026-10-20 | on-release | corpus/lessons/round-18.md |

Notes for L1: `used-by` points at the round lesson that does not exist at b576341 (`test -e corpus/lessons/round-18.md` → rc 1), matching the r17 convention of naming the round lesson that lands with the row. If L1 prefers a single quoted source in the row, use the 19-word ls-tree quote below; the cat-file quote is a companion on the same row.

## 3. Quote ledger (verbatim, located, `wc -w` measured)

Primary (row quote), git-ls-tree § Output Format, final paragraph, exact URL a:

```
Without the `-z` option, pathnames with "unusual" characters are quoted as explained for the configuration variable `core.quotePath` (see git-config[1]).
```

`printf '%s' 'Without the `-z` option, pathnames with "unusual" characters are quoted as explained for the configuration variable `core.quotePath` (see git-config[1]).' | wc -w` → **19**.

Companion (same row), git-cat-file § OPTIONS `-e`, exact URL b. The page renders the placeholder in italics; plain text is `<object>`:

```
Exit with zero status if <object> exists and is a valid object.
```

`printf '%s' 'Exit with zero status if <object> exists and is a valid object.' | wc -w` → **12**.

Plane-listing sentence available if L1 wants the listing statement instead (git-ls-tree § OPTIONS `--name-only`):
"List only filenames (instead of the "long" output), one per line." — `wc -w` → **11**.

All three are contiguous sentences from the fetched pages; no paraphrase inside a quote. Round-17 lesson style keeps the quote in the Gate section and a paraphrase in the row's `teaches` cell; either assignment of the two quotes is faithful.

## 4. What it teaches for souji r18 (LG-DANGLING-PTR)

Doc-grounded (sections named above):

1. `git ls-tree -r --name-only <rev>` prints one path per line with no mode/type field, and **omits tree entries unless `-t` is given**. Therefore the listing is a blob path set, not the set of all objects: a directory-valued token can never be found in it.
2. `<path>…` arguments to `ls-tree` are "a list of patterns to match", not raw pathnames, and path arguments are taken relative to the current working directory unless `--full-tree`. So a token must not be appended as an `ls-tree` path argument to test it.
3. `-z` makes the filename "output verbatim and the line … terminated by a NUL byte"; without `-z` unusual pathnames are quoted per `core.quotePath`.
4. `git cat-file -e <object>` exits zero iff the object exists and is a valid object, non-zero otherwise; it emits no stdout on success. The page states no specific non-zero code. `-e` is the literal existence test; it does not filter by object type (measured: `b576341:corpus/knowledge`, a directory, exits 0) — unlike rule 1.

Measured on the lane (git 2.56.0; §5 row 9): the b576341 tree has 2018 `100644`, 214 `100755`, 14 `120000` and 181 `040000` entries; 2 of the 2246 blob/symlink pathnames are emitted C-quoted without `-z`.

Consequence for the finding as specified (repo-relative token, `path:line` suffix stripped, braces expanded, `<`/`>`/`*`/`round-N` skipped, fleet-only tokens classified `fleet`):

- Use `cat-file -e "<REV>:<path>"` per token with `<REV>` already resolved by the gate's `resolve_commit`, or one `cat-file --batch-check` over all specs. Do **not** use `list_tree()` as the dangling set: it is blob-only by design (`tools/souji-landing-gate.py:182` filters `parts[1] != b"blob"`), and widening it to `-t` would mix tree oids into every SHA-256/pin caller.
- If an enumerated listing is preferred, pass `-z --full-tree` (as `list_tree` already does at `:175`) and compare raw bytes; a line-split set built from non-`-z` output produces false danglings for the 2 quoted paths in this very tree.
- Never pass a token as an `ls-tree` `<path>`: wildcards silently match nothing and `:(glob)` magic is rejected (§5, rows 4–5).

Smallest concrete helper (fits the gate's existing `GIT_ENV`, no new dependency):

```python
def path_resolves(root, rev, path):
    # rev already resolved; absent path exits 128, not 1
    proc = subprocess.run(["git", "-C", root, "cat-file", "-e", "%s:%s" % (rev, path)],
                          stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=GIT_ENV)
    if proc.returncode == 0:
        return True
    if b" does not exist in '" in proc.stderr:
        return False
    raise EvalError("git cat-file -e failed (rc=%d): %s"
                    % (proc.returncode, proc.stderr.decode("utf-8", "replace").strip()[:300]))
```

Optional batched variant (measured, §5 row 8): `git cat-file --batch-check='%(objectmode) %(objecttype)' -Z` over NUL-separated `rev:path` specs returns one process, `040000 tree` / `100644 blob` / `<spec> missing`, and exit 0 even when records are missing. Caveat: § BATCH OUTPUT documents the missing record as `<object> SP missing LF`; under `-Z` I measured a NUL terminator. Verify the terminator before adopting. Not needed for ~281 tokens.

## 5. Exact commands run and observed output

All in `/home/vgpnk/Projects/shokunin/souji-shokunin`, read-only, `set +e`.

| # | command | observed |
|---|---|---|
| 1 | `git ls-tree -r --name-only b576341 \| wc -l` | `2246` |
| 2 | `git ls-tree -r --name-only b576341 \| grep -cx 'corpus/knowledge'` ; same with `-t` | `0` ; `1` |
| 3 | `git cat-file -e b576341:corpus/knowledge; echo $?` | rc `0` (a directory resolves) |
| 3b | `git cat-file -e b576341:corpus/knowledge/dupe; echo $?` | rc `128`, `fatal: path 'corpus/knowledge/dupe' does not exist in 'b576341'` (a path prefix is not existence) |
| 4 | `git ls-tree -r --name-only b576341 -- 'corpus/knowledge/*.md' \| wc -l` | `0` (wildcard pattern matched nothing) |
| 4b | `git ls-tree -r --name-only b576341 -- corpus/knowledge \| wc -l` | `8` |
| 4c | `git ls-tree -r --name-only b576341 -- ':(glob)corpus/*.md'` | `fatal: :(glob)corpus/*.md: pathspec magic not supported by this command: 'glob'`; 0 lines |
| 5 | `git -C corpus ls-tree -r --name-only b576341 -- SKILL.md \| wc -l` ; `git -C corpus cat-file -e b576341:SKILL.md; echo $?` | `0` ; rc `0` (ls-tree path args are cwd-relative, `<rev>:<path>` is not) |
| 6 | `git ls-tree -r --name-only b576341 \| grep '^"'` ; same after `-z` + `tr '\0' '\n'` | 2 quoted records: `"tests/vault/vadv54-run/r/nl/first\nsecond.md"`, `"tests/vault/vadv54-run/r/scratch/.scratch/old\nname.log"` ; `0` (verbatim under `-z`) |
| 7 | `git cat-file -e 0000000:SKILL.md; echo $?` ; `git cat-file -e 'b576341:'; echo $?` | rc `128`, `fatal: invalid object name '0000000'.` ; rc `0` (empty path resolves the root tree) |
| 7b | `git rev-parse --verify --quiet b576341:census/round-17/gate-replays-ddb7347.json; echo $?` | rc `1` (contrast: `rev-parse` uses 1, `cat-file -e` uses 128 for absence) |
| 8 | `printf 'b576341:corpus/knowledge\n…gate-replays-ddb7347.json\nb576341:SKILL.md\n' \| git cat-file --batch-check='%(objectmode) %(objecttype)'` | `040000 tree` ; `b576341:census/round-17/gate-replays-ddb7347.json missing` ; `100644 blob`; rc `0` |
| 8b | `printf '…gate-replays-ddb7347.json\0' \| git cat-file --batch-check -Z \| od -c` | record ends `m i s s i n g \0` |
| 9 | `git ls-tree -r -t -z --format='%(objectmode) %(path)' b576341 \| tr '\0' '\n' \| awk '{print $1}' \| sort \| uniq -c` | `181 040000`, `2018 100644`, `214 100755`, `14 120000` |
| 10 | `oid=$(git rev-parse b576341:corpus/knowledge); git cat-file blob "$oid"` | `fatal: git cat-file 9f88d0d5…: bad file`, rc `128` (the trap in §6) |
| 11 | `git cat-file -e $'b576341:tests/vault/vadv54-run/r/nl/first\nsecond.md'; echo $?` | rc `0` (newline in pathname survives as one argv; not doc-stated) |

## 6. Existing gate surface this lands on (b576341)

- `tools/souji-landing-gate.py:157-171` `_git()` raises `EvalError` on any non-zero rc — so `_git(..., ["cat-file", "-e", spec])` would turn absence into gate exit 2.
- `:173-186` `list_tree()` uses `ls-tree -r -z --full-tree` and keeps only `parts[1] == b"blob"`: a blob path→oid map, not an object existence set.
- `:192-211` `blob_at_path()` special-cases `rev-parse --verify --quiet` rc `1` as "absent" and then returns `blob_by_oid(...)`.
- `:214-222` `resolve_commit()` pins `<rev>^{commit}` before anything else.
- `:115-123` `FINDING_IDS` — `LG-DANGLING-PTR` is absent today (`grep -n 'LG-DANGLING-PTR' tools/souji-landing-gate.py` → no matches), consistent with the r18 goal.

Two reuse traps, both measured:

1. **Directory token through `blob_at_path`** → `rev-parse` succeeds (tree oid), `cat-file blob <tree-oid>` fails 128, `_git`/`blob_by_oid` raise `EvalError` → the whole gate exits 2 instead of emitting a finding. This is why `cat-file -e` (or `--batch-check`) must be used, not the blob helper.
2. **Copying the `rc == 1` idiom** from `blob_at_path` onto `cat-file -e` → absence is 128 on this git, so every dangling pointer becomes exit 2. The `128` is measured, not documented; the pages only say "non-zero".

A cheaper alternative for L1: stderr is diagnostic — absent prints `fatal: path '<p>' does not exist in '<rev>'`, invalid rev prints `fatal: invalid object name '<rev>'`; both rc 128, so a pre-resolved REV plus the message split keeps absent-vs-error honest.

## 7. What it does NOT establish

- **No token grammar or policy.** Which prose text counts as a path pointer, how `path:line` is stripped, brace/range expansion, the fleet-vs-lane split and `corpus/pointer-exemptions.tsv` are the gate's own rules; neither page says anything about them.
- **No absence exit code.** `-e` says "non-zero"; both "path does not exist" and "invalid object name" measured rc 128. Exit status alone cannot distinguish a dangling pointer from a malformed object name.
- **No `<rev>:<path>` grammar.** Splitting at the first colon, `:<path>` index forms and `./`-relative forms are gitrevisions(7) material; that page was not opened here.
- **No file-vs-directory or tracking claim.** `-e` is true for a valid object of any type; it does not say the path is a blob, is tracked at a branch tip, or exists in the working tree.
- **No network guarantee.** Neither page states whether a missing promisor object is lazily fetched during object lookup; the gate's own `GIT_ENV` sets `GIT_NO_LAZY_FETCH=1` (S049) and must keep doing so.
- **No config/hook immunity.** The pages do not promise these plumbing reads ignore repository-local config or hooks; no hook is documented to run, but absence of a statement is not immunity.
- **No cross-version behavior.** The ls-tree manual claims no changes 2.42.1→2.56.0; that is a documentation-stability statement, not an output-byte guarantee on other git versions.
- **No cross-version parsing guarantee.** The default line format is stated compatible with `git update-index --index-info --stdin`, but the page makes no output-stability promise across versions, and non-`-z` output is quoted; `-z` is the documented verbatim form.

## 8. Mined mistake (one, for the round's Frontier step)

**"Absence from a tree is exit 1."** `git rev-parse --verify --quiet <rev>:<path>` exits 1 when the path is absent, but `git cat-file -e <rev>:<path>` exits **128** (measured; stderr `fatal: path '<p>' does not exist in '<rev>'`). A helper that copies the existing `blob_at_path` special-case (`returncode == 1` → absent, everything else → `EvalError`) would convert every dangling pointer into a whole-gate exit 2 — the finding would never print, and the run would look like "could not evaluate". Fix: split on rc 0 vs rc 128-with-the-absence-message, or resolve once and treat any post-resolution `cat-file -e` failure whose stderr names the path as absent.

Second, non-mined hazard: treating `ls-tree -r --name-only` lines as raw repo paths (false for the 2 C-quoted pathnames in this tree).

## 9. Draft Search-log entry for SOURCES.md

**Round-18 pointer-resolution primitive (2026-10-20).** Question: which primary text grounds a dangling-pointer check over a fixed revision? Seat SrcGitLsTree-5 opened the git-ls-tree and git-cat-file web manuals (access 2026-10-20; ls-tree served "last updated in 2.42.0", "2.42.1 → 2.56.0 no changes"; cat-file "last updated in 2.56.0"). Identified 2 documents, screened 2, included both in one new A row (S064), excluded 0. Stop: listing shape, tree omission, quoting and the literal existence test are located; the token grammar, fleet split and exemption policy are the gate's own and were not sourced here.

## 10. Remaining unknowns

- Policy: does "resolve in the tree at REV" admit directory tokens, or must `corpus/pointer-exemptions.tsv` name them? The docs support both readings; the gate's rule decides.
- `core.quotePath`'s exact quoting rules were not opened (only the sentence that points at it); the 2 quoted paths were observed, not decoded back to raw names.
- Whether `cat-file -e` fetches a missing promisor object: not stated by the page; not tested (would require a partial clone, outside this seat's write scope).
- The gate's own `--round ≥ 18` pinning and `census/round-17/gate-replays-expected.json` replay invariance are executor scope (GatePointers / CensusWatchdog seats), not measured here.

## 11. Compliance and tooling

- Probe rule: only exact named-file reads (`corpus/SOURCES.md`, `corpus/lessons/round-17.md`, `tools/souji-landing-gate.py` ranges), `grep` on that one file, and read-only git (`ls-tree`, `cat-file`, `rev-parse`, `--version`) inside the lane plus the two vendor URLs. No recursive search, no clone, no `jj`, no git write, no process signalled, no `souji-*` tool run.
- Tooling: nothing installed or upgraded; no pacman/uv/npm action.
- Write set: this report only.
