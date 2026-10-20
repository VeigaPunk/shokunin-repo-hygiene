STATUS: DONE — C1 no-harm ledger holds on the measured universe (no r16-pass→changed-fail, no pre-harm-pass loss), but the D2 type probe (`stat %F`) contracts benign layouts the matrix cannot see: empty regular metadata and non-C message locales. D1 is a disclosed count-semantics change under `showUntrackedFiles=all`.

Seat: SoujiR17-3.CriticC1NoHarm-2 (critic, leaf). Rev under attack: ddb7347 (`tools/souji-census.sh` blob sha256 688ff8ad…4f59, identical to the lane worktree file).

## Axes
- operability: no whole-run refusal or row loss on benign layouts or environments.
- calibration: counts and flags mean what the doc says; degrade/refuse only where git would actually read the hostile file.

## 1. No-harm ledger (from L1 matrix aggregates + selftest diff)

| suite | pre-harm a31642d | r16 5fa6017 | changed ddb7347 | r16-pass → changed-fail | pre-harm-pass → changed-fail |
|---|---|---|---|---|---|
| r17-hygiene (26) | 20 fail | 13 fail = exactly the 13 `repair`-class ids (01–04,07–09,14–16,20,24,26 per CASE_CLASSES) | 0 fail | none (changed fails 0) | none |
| r15-config (20) | 8 fail | 0 | 0 | none | none |
| r14-namespace (12) | 10 fail | 0 | 0 | none | none |
| own --selftest | 36/0 | 38/0 | 49/0 | none removed | none removed |

Commands and output:
- `git diff 5fa6017 ddb7347 -- tools/souji-census.sh | grep -c -E '^-.*st_(ok|bad) '` → `0`
- `git diff a31642d ddb7347 -- tools/souji-census.sh | grep -c -E '^-.*st_(ok|bad) '` → `0`. So the r16 and pre-harm selftest checks are subsets of the changed checks. The 11 new checks are the hygiene-fleet block (diff hunk `@@ -1817,6 +1896,115`, additions only).
- `git show ddb7347:tools/souji-census.sh | sha256sum` = `sha256sum tools/souji-census.sh` = 688ff8ad684b…4f59. `git show ddb7347:tests/fixtures/r17-census-hygiene.py | sha256sum` = worktree 136b0e49…d693. L1's WORKTREE matrix run therefore applies to the landed bytes, assuming it ran on the final worktree. I could not check that assumption.
- `stat …/census/round-17/c1-matrix.json` → `No such file or directory`. The landed-rev per-case record is not on disk, so this ledger uses L1's aggregate numbers, not per-case JSON. **[INFERENCE]** Per-case no-harm follows from the totals (changed = 0 failures over the same case universes), but it is not re-measured here.

Verdict (measured universe): **holds**.

Blind spot: both matrix fixtures pin `LC_ALL=C` (`r17-census-hygiene.py:171,278`). No case puts an empty regular file at any guarded metadata name. The two counterexamples below lie entirely outside what the matrix can detect.

## 2. Counterexample A — empty regular metadata is now classified non-regular (operability contraction vs r16)

ddb7347 `tools/souji-census.sh:549-574`:
```
549  if ! kind=$(stat -L -c '%F %h' -- "$path" 2>/dev/null); then continue; fi
552  case "$kind" in
553    directory) continue ;;
554    'regular file') …
567    *) [info/attributes → meta_soft nonregular] ; protected_fail "git-metadata-nonregular"
```
GNU stat `%F` prints `regular empty file` for a zero-byte regular file:
```
$ /usr/bin/stat --version | head -1     → stat (GNU coreutils) 9.12
$ /usr/bin/stat -L -c '%F %h|%n' -- /proc/version /etc/hostname
regular empty file 1|/proc/version
regular file 1|/etc/hostname
```
`regular empty file` matches neither `directory` nor `'regular file'`, so it falls into `*)`.

r16 (`5fa6017:tools/souji-census.sh:523`) used `[ -f "$path" ]`, which is true for an empty file. The nlink was 1, so the file was accepted.

| empty regular file at | r16 | ddb7347 |
|---|---|---|
| `info/attributes` (`touch .git/info/attributes`) | normal row | per-repo `error` + `git-metadata-unsupported git-metadata-nonregular` |
| `info/exclude`, `config`, `packed-refs`, `objects/info/alternates` | accepted | **whole-run exit 2** `path-protected: git-metadata-nonregular`, for every repo in the fleet |
| `HEAD`, `index`, `commondir` | accepted by guard (git itself fails later) | whole-run exit 2 |

**[INFERENCE]** git accepts empty files at `info/attributes` and `info/exclude` (no patterns), at `objects/info/alternates` (no alternates), at `packed-refs` (the packed backend returns early on size 0) and at `config` (format version defaults to 0). Under that inference these are benign layouts. I did not execute git on them; my item grants no ALLOWED-EXEC.

Live exposure today: nil.
```
$ cd /home/vgpnk/Projects/shokunin && /usr/bin/stat -L -c '%s|%F|%h|%n' -- */.git/{config,HEAD,index,packed-refs,commondir,info/exclude,info/attributes,objects/info/alternates} */.git/worktrees/*/{info/attributes,info/exclude,commondir,HEAD,index} 2>/dev/null | awk -F'|' '$2!="regular file"{print} END{print NR" entries checked"}'
110 entries checked        (no non-"regular file" line)
```
(The command was run as written out per name, without brace expansion.)

Impacted axes: operability (benign layout → whole-run refusal) and calibration (the diagnostic says `nonregular` for a regular file). This is a **fixable defect, not a tradeoff**.

## 3. Counterexample B — `%F` is a translated string (operability contraction vs r16, environment-dependent)

The census does not set `LC_ALL`/`LC_MESSAGES`/`LANGUAGE` for its own process. The only `LC_ALL=C` uses are on `sort` (lines 1384 and 1519). By contrast, souji-verify exports `LC_ALL=C` at :79 and :528.
```
$ LANGUAGE=de /usr/bin/stat -L -c '%F %h|%n' -- /proc/version /etc/hostname
reguläre leere Datei 1|/proc/version
reguläre Datei 1|/etc/hostname
$ LANGUAGE=fr /usr/bin/stat -L -c '%F %h|%n' -- /etc/hostname
fichier 1|/etc/hostname
```
Host: `LANG=en_US.UTF-8`, `LANGUAGE` unset, and `/etc/locale.conf` contains only `LANG=en_US.UTF-8`. The de/fr coreutils catalogs are installed. An operator with `LANGUAGE=de` (or any LC_MESSAGES whose catalog translates "regular file") would get `.git/config` classified as `*)` → `protected_fail git-metadata-nonregular` → **whole-run exit 2 on every fleet, every repo**.

r16's `[ -f ]` test is locale-independent. Live exposure today: nil. The matrix cannot see this because its fixtures force `LC_ALL=C`.

Impacted axes: operability. This is a fixable defect.

## 4. Minor — the probe now fails open on a stat failure (calibration)

r16: `[ -f ]` true + `stat %h` failing → `protected_fail git-metadata-unavailable`, which fails closed.
ddb7347:549: any `stat` failure → `continue`, treating the entry as absent, which fails open. This differs only when the `stat` binary itself fails or rejects `-c`. A path-level failure is the same stat(2) that makes `[ -e ]` false, so r16 also accepted it. Low reach, but the direction is fail-open.

## 5. D1 — does `--untracked-files=normal` change dirty COUNTS under `status.showUntrackedFiles=all`?

Yes. It is a semantics change for that config, not only a repair:
- r16 status followed config. Under `all`, a wholly untracked 3-file directory counted 3. At ddb7347:1117-1118 it counts 1.
- The fixture pins this change: `R17-04` (class `repair`) requires `dirty(all) == dirty(normal)`, and r16 fails it.

Flags are unchanged under `all`: with any untracked content, dirty > 0 both before and after, so `dirty`/`clean`/`wt-dirty` and the count-vs-zero comparisons in `worktree_extra_flags` do not move. Only the numeric field changes. Under `no|false|0|off`, 0 → >0 is the intended repair (no false clean).

Consequences to disclose:
1. **`--compare` discontinuity.** Comparing an r16-era TSV with an r17 TSV for any repo with `all` (repo-local, include, config.worktree, or global/system) emits a `dirty` field row and exit 3 with no tree change. LOG/README should state this one-time break.
2. **Duplicate authority / doc drift.** census:37-38 still says the count matches souji-verify. souji-verify still follows config: ddb7347 `tools/souji-verify.sh:361` (`evaluate_repo_root`: `git -C … status --porcelain | wc -l`) and `:865` (worktree receipt). The two now diverge on any repo carrying the key. Under `no`, verify's repo-root/worktree dirty is 0 while census reports dirty, and verify is the unsafe side. This was pre-existing in verify, but the census doc claim is now false.
3. **Live exposure:** none. L1 found 0/22 repos with the key. I checked user/system scope: `/home/vgpnk/.gitconfig` absent, `/etc/gitconfig` absent, and `/home/vgpnk/.config/git/config` has no `status.*`, `include.*` or `includeIf.*` line.

Verdict D1: **holds as a repair, partial on calibration** (semantics change and verify divergence undisclosed).

## 6. Is the per-repo degrade a contraction for any benign layout?

| layout at info/attributes (or other guarded name) | r16 | ddb7347 | contraction? |
|---|---|---|---|
| directory | accepted (`-e && ! -d` false) | `directory) continue` | no |
| in-gitdir dangling symlink / ELOOP / EACCES | accepted (`-e` false) | stat fails → continue | no |
| symlink → single-link regular non-empty | accepted | `regular file`, nlink 1 | no |
| hardlink / FIFO / socket / device at info/attributes (main or common dir) | whole-run exit 2 | per-repo error row | no (expansion) |
| same, in a **linked-worktree admin dir** (callsite :864) | whole-run exit 2 | the **main repo's whole row** = `error` | no vs r16, but over-degrade: **[INFERENCE]** git resolves `$GIT_DIR/info/*` (except `info/sparse-checkout`) to the common dir, so an admin-dir info/attributes is never opened by git |
| **empty regular file** at info/attributes | normal row | error row | **YES** (§2) |
| **empty regular file** at config/packed-refs/info/exclude/alternates | accepted | whole-run exit 2 | **YES** (§2) |
| any regular metadata under a translating message locale | accepted | whole-run exit 2 | **YES** (§3) |

## Verdict per axis
- **operability: partial.** No regression on the measured matrix, and the r14/r16 harm repairs are real. Two benign classes now refuse the whole run where r16 did not: zero-byte regular metadata (§2) and a translated stat locale (§3). Neither is live today. Both are fixable defects that the canonical judge should require fixed (or at least pinned) before saturation. They are not tradeoffs.
- **calibration: partial.** The diagnostic misclassifies an empty regular file as `nonregular`. The probe fails open on stat failure (§4). The D1 count semantics change under `all` and the census↔verify divergence are undisclosed (§5). Admin-dir info/attributes degrades a file git never reads (§6), but that is an improvement over r16 and should be recorded as debt, not harm.

## Smallest safe correction
1. `tools/souji-census.sh:549`: run the probe under the C locale and accept both regular spellings:
   `if ! kind=$(LC_ALL=C stat -L -c '%F %h' -- "$path" 2>/dev/null); then …`
   and at :554 use `'regular file'|'regular empty file')`.
   An alternative is to classify by raw mode (`%f` hex & 0xF000 == 0x8000 / 0x4000), which avoids translated strings entirely.
2. `tools/souji-census.sh:549` (fail-closed): on stat failure, `continue` only when `[ ! -e "$path" ]`. Otherwise `protected_fail git-metadata-unavailable`, as r16 did.
3. Fixture `tests/fixtures/r17-census-hygiene.py`: add two preserve cases.
   - Empty `info/attributes` + empty `info/exclude` + empty `packed-refs` → three normal rows, exit 0.
   - One `run_tool` arm with `LANGUAGE=de` and `LANG=en_US.UTF-8` (no `LC_ALL`) on a benign fleet → exit 0 and clean rows. Skip only if the de catalog is absent, and report it as SKIP, never PASS.
   Both cases fail on ddb7347 and pass on r16. This is what the matrix needs to catch the contraction.
4. Docs:
   - census:37-38: drop or qualify "matching souji-verify".
   - LOG/README C1 entry: note the `all`-config count change and the resulting one-time `--compare` break.
   - Route verify:361/865 config-following status to a later round as a separate finding (out of C1 scope).

## Probe discipline
- All commands were read-only (git show/diff/ls-tree/log, `git config --file <f> --list` filtered to status/include keys, stat, sha256sum, cat /etc/locale.conf). I ran no census, verify, vault or quarantine script, and no jj.
- **Self-report:** my first batch wrote `git show ddb7347:tools/souji-census.sh` to `/var/tmp/souji-r17-CriticC1NoHarm.census.sh`. That is outside the report-only write allowance, since my item has no ALLOWED-EXEC. I never executed it and deleted it with `rm -f` in the next batch.
- Tool installs/updates: none.
