# ProbeAlternates — souji r24 w1

## Status
STATUS: PARTIAL — clause 1 (`alternate:` line, absolutized) CONFIRMED; clause 2 (fsck ignores alternate-only objects) FALSIFIED; clause 3 (comment/blank lines appear) FALSIFIED (they do not appear). The partial verdict reflects the mixed hypothesis, not unfinished work.

## Evidence
Environment: git 2.56.0, `LC_ALL=C GIT_CONFIG_NOSYSTEM=1 HOME=<scratch>/home`, scratch `/var/tmp/souji-r24-ProbeAlternates/` (removed at end). Lane HEAD read: f9db2181647d91470a724a12d626bd6106805076. Setup: `src` repo with one commit plus one dangling blob `b6f6913…` (`echo only-in-alt | hash-object -w`); `dst` is an independent repo with its own commit.

P1, absolute path in `dst/.git/objects/info/alternates`:
```
garbage: 0
size-garbage: 0
alternate: /var/tmp/souji-r24-ProbeAlternates/src/.git/objects
-- fsck --unreachable --no-reflogs
unreachable commit 80022feaff8bd27550fb900b37d75a5cf040be40
unreachable tree f36e32b1bc59ac7e94aab71c4c02ca3df038a8d4
unreachable blob b4785957bc986dc39c629de9fac9df46972c00fc
unreachable blob b6f6913882aca174e0e4f003aaed67468e8a97f3
rc=0
```
P1b, same `dst` with an empty alternates file: `fsck --unreachable --no-reflogs` printed nothing, `rc=0`. All four lines above come from the alternate.

P2, relative line `../../../src/.git/objects`, run with `-C dst` and also as `--git-dir=… ` from `/`: both printed `alternate: /var/tmp/souji-r24-ProbeAlternates/src/.git/objects` (absolutized).

P3, file contents (`cat -A`) `# a comment$`, `$`, `/var/…/src/.git/objects$`: the output had exactly one `alternate:` line, the path. Neither the comment nor the blank line appears.

Other probes. Each row shows the file lines (non-blank, non-`#`) and then the number of `alternate:` lines output:

| probe | file lines | `alternate:` lines | note |
|---|---|---|---|
| P4 same path twice | 2 | 1 | deduplicated |
| P5 nonexistent path | 1 | 0 | stderr `error: unable to normalize alternate object path: …/nope/objects`, rc=0 |
| P6 `…/.git/./objects/` | 1 | 1 | normalized to `…/src/.git/objects` |
| P7 no trailing newline | 1 | 1 | |
| P8 symlinked dir `srclink` | 1 | 1 | printed realpath `…/src/.git/objects` |
| P9 path with space | 1 | 1 | unquoted `…/sp ace/src/.git/objects` |
| P10 CRLF line | 1 | 0 | stderr `error: object directory …/src/.git/objects? does not exist; check .git/objects/info/alternates` |
| P11 empty file + `GIT_ALTERNATE_OBJECT_DIRECTORIES` | 0 | 1 | environment alternates are listed |
| P12 chained (src→third) | 1 | 2 | transitive alternates are listed |
| P13 self-reference | 1 | 0 | silently dropped, no stderr |
| P14 linked worktree of `dst` | 1 | 1 | plus `garbage: 1` false positive and `warning: garbage found: …/worktrees/wt/refs` |
| P20 tab / non-ASCII path | 2 | 2 | C-quoted: `alternate: "…/t\tab/…"`, `alternate: "…/\303\274ml/…"`; with `core.quotePath=false` the non-ASCII path is not quoted, but the tab path still is |

P15–P19, `git clone --shared src shared` (the realistic case):
```
count: 0
alternate: /var/tmp/souji-r24-ProbeAlternates/src/.git/objects
-- fsck --unreachable --no-reflogs in shared
unreachable blob b6f6913882aca174e0e4f003aaed67468e8a97f3
```
After a new commit in `src` that `shared` does not reference, the default fsck also listed `unreachable commit cbd4d07…`, `tree 95bfdf4…` and `blob 5e28b27…`, all of which live only in `src`.

`shared2` (fresh `clone --shared`, plus one local dangling blob `587be6b…`):
```
--no-full: rc=2
missing blob 5e28b27ad652e6f72ac4b68f912f147de7332a24
missing blob b4785957bc986dc39c629de9fac9df46972c00fc
missing commit cbd4d078db427e6949a88e289045de493917c5d7
missing tree 95bfdf4a492620d8822cbe8c6ed6a6e2d3154fe2
unreachable blob 587be6b4c3f93f93c489c0111bba5596147a26cb
--connectivity-only: rc=0  -> unreachable 587be6b… (local) + b6f6913… (alternate-only)
full (default):      rc=0  -> unreachable 587be6b… (local) + b6f6913… (alternate-only)
loose-path test: b6f6913… not-local ; 587be6b… local-loose
```
Local-pack membership: `git show-index < objects/pack/*.idx` on the repacked `shared` listed only the local pack OIDs. `cat-file --batch-all-objects --batch-check` counted 8 objects in `shared2`, while its `count:` was 1, so it includes alternates and cannot be used as a local filter.

Write-safety: the manifest of both `shared/.git` and the alternate `src/.git` (find path/type/mode/size/mtime, sha256) was unchanged across `fsck --unreachable --no-reflogs`.

Lane (read-only): `git -C …/souji-shokunin count-objects -v` reports `garbage: 0` and `size-garbage: 0`, with 0 `alternate:` lines. `objects/info/` contains only `commit-graphs` and `packs`, with no alternates file.

## Findings
1. **Clause 1 — CONFIRMED.** The spelling is `alternate: <path>`, one line per resolved object directory. The path is absolutized, normalized, and symlink-resolved (P2, P6, P8). Paths with non-printable characters are C-quoted. Source: `git help -m count-objects`, ALTERNATE section. Quote: "alternate: absolute path of alternate object databases; may appear multiple times, one line per path."
2. **Clause 2 — FALSIFIED.** `fsck --unreachable --no-reflogs` reports alternate-only objects that the local refs do not reach as `unreachable` (P1: 4 lines from the alternate; P15: `b6f6913…`). Cause: the fsck manual says full checking is now the default. Source: `git help -m fsck`, `--full`. Quote: "also the ones found in alternate object pools listed in GIT_ALTERNATE_OBJECT_DIRECTORIES or $GIT_DIR/objects/info/alternates".
3. **`--no-full` is not a fix.** It prints `missing <type> <oid>` for alternate-backed objects that refs point to, and exits 2 (shared2). Under the frozen contract, the tool would report that as a git failure (exit 1).
4. **Clause 3 — FALSIFIED (they do not appear).** `#` comment lines and blank lines in the alternates file produce no `alternate:` output (P3).
5. **File line counts and output line counts diverge.** They differ for duplicates (2→1), nonexistent paths (1→0, with `error:` on stderr), CRLF lines (1→0, with `error:`), self-reference (1→0, silent), the environment variable (0→1) and chained alternates (1→2). Only the output lines reflect what git actually resolved.
6. **Linked worktree plus alternates (P14).** Both the garbage false positive and the `alternate:` line appear through `-C <linked>`. Resolving the common directory, as the contract already requires, does not change the alternates figure.

## Recommendation (tool counting)
- `alternates=A`: count the `^alternate: ` lines from `count-objects -v`, run against the common git dir. Do not count file lines. Also:
  - Unset `GIT_ALTERNATE_OBJECT_DIRECTORIES` and `GIT_OBJECT_DIRECTORY` in the child environment so ambient state cannot inflate A.
  - The `error: …alternate…` stderr from P5 and P10 is "other stderr", so it already maps to exit 1 under the contract. Keep that, because a broken alternate is a real repository fault, not a count of 0.
  - Count lines rather than parsing paths, because quoted paths (P20) make naive path parsing fragile.
- `unreachable=U`: keep the default fsck (`--unreachable --no-reflogs`, without `--no-full`), then count only OIDs stored locally. That means OIDs with a loose file at `<common>/objects/xx/<38>`, or OIDs listed by `git show-index` over `<common>/objects/pack/*.idx`. Without this filter, U on any `clone --shared` or `--reference` repo counts the donor's debris.

## Attack log
- A1 (C1 case 5 is non-discriminating). The frozen case "objects/info/alternates with one path: alternates=1" passes under both counting methods. It does not check U, so an implementation that counts the donor's unreachable objects (Finding 2) passes case 5. Within the frozen counter, nothing detects the U inflation. I am not proposing a change; this is reported as a residual coverage gap for C1.
- A2. The lane measurement has 0 alternates (Evidence, last paragraph), so the lane-bound figure is not exposed to A1. The exposure is limited to repositories that use alternates.

Tools installed or updated: none. Scratch `/var/tmp/souji-r24-ProbeAlternates/` was removed after the run.
