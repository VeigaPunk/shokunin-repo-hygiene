# handoff-91 — souji-shokunin round 6, seat S91

Role: handoff drafter. Wrote only this file. Did not install a tool, apply a
diff, edit SKILL.md / SCORECARD.md / PROVINCE.md / MINT.md / LOG.md, touch the
ledger, read a secret-shaped file, or run git fetch/push/commit/branch/prune/
remove.

Lane HEAD at every check this seat: `ce58c2b` (full
`ce58c2b457c8ffb7886b36a509bf957f90d1f296`). Docs named below were still the
committed bytes (SKILL.md mtime 2026-10-18 11:48:33 -0300; SCORECARD.md mtime
2026-10-18 15:48:07 -0300). Unapplied diffs under `census/round-6/*-amend-*.diff`
are other seats' drafts. They are not closure.

Axes this seat scored: calibration (drift count honest), operability (a
repeatable census at the installed path), coverage (every kotodama `.scratch`
entry classified), harm-none (read-only, secrets unread, no git writes).

## Verdict

| claim | status | why |
|---|---|---|
| C1 calibration, docs/tools drift → 0 | **NOT MET** | 9 live contradictions between committed docs and installed tools. Drift count = 9, not 0. |
| O1 operability, `tools/souji-census.sh` repeatable fleet census | **NOT MET** | Installed path absent at 2026-10-18T16:35:52-03:00. One draft selftest is green; the live kotodama row it emits is not trustworthy. |
| K1 coverage, kotodama 16G `.scratch` fully classified, read-only, plus this note | **SNAPSHOT ONLY, NOT CLOSED** | One walk classified every file it saw. Later commands disagree on size, file count, and top-level count. The 16G premise is already false. Receipt: none. Removal: not authorized. |

Nothing in this handoff is a removal list.

## C1 — drift is 9, not 0

Installed bytes this seat (`sha256sum`):

- `tools/souji-verify.sh` `53239fdfe5bcaaaf448e8525845ab962dd7ab6a4e7f75c0f4f051614f1c99200`
- `tools/souji-vault-verify.sh` `00d59b1b36d87db37518b5ef9fb98cd472888a075ed7b97bd5b8ff93bd559455`
- `SKILL.md` `422c0c3f71eeaae271c23226324da088e1516360ba46638361a93e42d35bdacf`
- `tools/souji-verify.spec.md` `f139efd6243020dacad4e3c7da00d597f15456b084118306e64643e6aa295144`

| id | where | installed behavior | command |
|---|---|---|---|
| D1 | `SKILL.md:16` requires `git fetch` and hardcodes `origin/main` | spec:38-42 and spec:61: no fetch; default ref is `refs/remotes/origin/HEAD` or the single remote-tracking ref; else `pushed-unverifiable`. Tool `resolve_default_ref` at `tools/souji-verify.sh:137-149` matches the spec, not the skill. r1 LOG already recorded the fleet default as `origin/master`. | `rg -n 'origin/main\|git fetch' SKILL.md tools/souji-verify.spec.md` |
| D2 | `SKILL.md:29` "last commit is an ancestor" | `try_pushed` uses the introducing commit: `git log --diff-filter=A` (`tools/souji-verify.sh:220`) | read those lines |
| D3 | `SKILL.md:18` stale sweep has no census/tests/quarantine exclusions | `count_live_refs` excludes them (`tools/souji-verify.sh:205-210`), matching spec D3 | read those lines |
| D4 | `SKILL.md` receipt table has only pushed / moved-to-obsidian / stale | tools and spec also emit `metadata-prune`, `secrets-refusal`, `pushed-unverifiable`, `symlink-present` (spec:31-33, spec:40, spec:47, spec:60; tool comments and `dir_digest` return 2 at `tools/souji-verify.sh:154-160`) | `rg -n 'pushed-unverifiable\|symlink-present\|metadata-prune' tools/souji-verify.spec.md tools/souji-verify.sh` |
| D5 | `SKILL.md:89-91` current surfaces: lore 19 prunable, gd2d 5 prunable, kotodama `.scratch` 553M | live: lore worktree lines = 1; gd2d = 4; scratch `du -sh` = 18G at 15:53, 19G / `du -sb` 18595798991 at 16:08, and impl-39 later reported 27689220554 | `git -C lore-shokunin worktree list \| wc -l` → 1; `git -C game-dev-2d-shokunin worktree list \| wc -l` → 4; `du -sh` / `du -sb` as above |
| D6 | `SCORECARD.md:22` cites souji-verify sha256 `7efda63bd760…`; `:24` cites vault-verify `d312263a…` | installed prefixes are `53239fdfe5bcaaaf` and `00d59b1b36d87db3` (r5 patched the tools; the capability rows were not) | `sha256sum tools/souji-verify.sh tools/souji-vault-verify.sh`; `rg -n '7efda63b\|d312263a' SCORECARD.md` |
| D7 | `SCORECARD.md:14-15` table: calibration 7, operability 8, coverage 8 | `SCORECARD.md:45` still says "operability 7, calibration 6" | `rg -n 'operability 7\|calibration 6' SCORECARD.md` |
| D8 | installed tool comment headers still name `tools/souji-verify.impl-12.sh` (`souji-verify.sh:8`) and `tools/souji-vault-verify.impl-20.sh` (`souji-vault-verify.sh:14`) | the files on disk are `tools/souji-verify.sh` and `tools/souji-vault-verify.sh`. Spec CLI matches the installed names. Comment-only; still a docs/tools mismatch an agent will copy. | read those headers |
| D9 | spec:3 allowlist is bash + coreutils + git + rg | `souji-verify.sh` calls `grep` at lines 144, 145, 159, 214, 342, 632. Header deviation D-a covers missing `rg --basename`, not `grep`. | `rg -n '\bgrep\b' tools/souji-verify.sh` |

Not counted as drift: `MINT.md` 553M / 24 worktrees. That file is a mint-time
measurement (2026-10-18), not a current-state contract. Do not rewrite it to
today's numbers.

Ledger check, header only, not a data-row read: `wc -c corpus/knowledge/obsidian-ledger.tsv` → 67. First line is the header `source_path source_sha256 vault_path vault_sha256 exported_at note`. Data rows: 0. Unchanged by this seat.

Parent: do not mark C1 closed until a re-count of D1–D9 against the committed files is 0. Unapplied `skill-amend-*.diff` / `scorecard-amend-29.diff` are not that re-count. This seat did not apply them and did not verify they zero the list.

## O1 — installed census does not exist

```
ls tools/souji-census.sh
# ls: cannot access '.../tools/souji-census.sh': No such file or directory
```

Observed at 15:53, 16:08, and 16:35:52-03:00. Drafts seen, all untracked, none installed by S91:

| draft | mode | what S91 ran | result |
|---|---|---|---|
| `tools/souji-census.impl-33.sh` | 755 | `timeout 90 bash tools/souji-census.impl-33.sh --selftest` | exit 1. `selftest: 28 checks, 3 failed`. Repeat check passed (`PASS repeat: two runs byte-identical`). Failures: clean fixture verdict `dirty` because status contained `?? .ufo/state/live.json` and `?? .ufo/watchdog.log`; `dirty=2` not 0; dirty-count 3 not 2. |
| `tools/souji-census.impl-34.sh` | 644 | `timeout 120 bash tools/souji-census.impl-34.sh --selftest` | exit 126. Selftest re-exec hit `Permission denied`. S91 did not chmod another seat's file. |
| `tools/souji-census.impl-36.sh` | 644 at 16:08:53 | not run | to-verify |
| `tools/souji-census.impl-39.sh` | 755 | `--selftest`, then one live census | selftest exit 0, `15 checks, 0 failed`, including `S15 repeat census byte-identical`. Live census exit 0 (below). |
| `tools/impl-38.sh`, `tools/impl-43.sh` | 644 | not run | other seats' reconciler/census drafts; not the installed path |

Live census command (read-only, existing refs, no fetch):

```
timeout 180 bash tools/souji-census.impl-39.sh --root /home/vgpnk/Projects/shokunin
# exit 0, header + 21 rows, ~15s, 2026-10-18 ~16:23 -0300
```

Rows that matter for this handoff (full TSV was the command's stdout):

- `kotodama-shokunin` — worktrees 1, unpushed 49, dirty 93, scratch_bytes **27689220554**, mtime_iso **1970-01-01T00:00:00Z**, flags `unpushed,dirty,scratch`
- `souji-shokunin` — unpushed 11, dirty 38, scratch_bytes 0, flags `unpushed,dirty,no-remote`
- `lore-shokunin` — worktrees 1, unpushed 3, dirty 26, scratch_bytes 218489
- `game-dev-2d-shokunin` — worktrees 4, unpushed 6, dirty 83, flags include `multi-worktree`
- 11 rows flagged `clean` (chousa, kagi, kake, kasegi, kengaku, kumitate, mado, mori, revenger, tameshi, tsukuroi). S91 did not re-derive each clean flag.

Two defects, so this draft is not install-ready even though its fixture selftest is green:

1. Kotodama `mtime_iso=1970-01-01T00:00:00Z` while `scratch_bytes=27689220554`. The tool's own comment (`souji-census.impl-39.sh:169-170`) says that epoch means an empty tree. The tree is not empty. `newest_mtime_iso` prints the epoch when `find|awk` yields an empty epoch (`:191-193`), including when `find` fails. A green exit with a false empty-tree mtime on the largest lane is a false measurement.
2. Live output is not a stable census. Same afternoon, different commands: `du -sh` 18G (15:53), classification apparent sum 19230125122, `du -sb` 18595798991 (16:08, `du -sh` 19G), impl-39 scratch_bytes 27689220554 (~16:23). Unpushed `git rev-list --count --branches --not --remotes` was 47 at 15:53 and 49 at 16:35. Porcelain line count was 29, then 31, then 26 at 16:35. Fixture repeatability (S15) does not transfer to this live tree.

Independent check of the souji `no-remote` flag: `git -C souji-shokunin for-each-ref --format='%(refname)' refs/remotes | wc -l` → 0. That flag is real. The dirty=38 count includes this round's untracked seat files; it is not a pre-round baseline.

`/tmp` note: `find .scratch -printf '%y\n' | sort | uniq -c` failed with `sort: write failed: /tmp/sort…: Disk quota exceeded` at 16:08, while `df -h /tmp` showed 3.6G free (77% of a 16G tmpfs). Quota, not a full filesystem. A census that spills a full-tree listing through `sort` can fail here. impl-39's live run did not hit that failure.

Parent: do not copy a draft onto `tools/souji-census.sh` until one draft is the chosen contract, its selftest is green, and a live kotodama row does not report the epoch. S91 did not install.

## K1 — classified once, not frozen, not safe

Owning lane is live, so the surface is NOT-SAFE before any file class is considered.

- `git -C kotodama-shokunin rev-parse --short HEAD` → `1ad491a` (full `1ad491a1a4b0aef9ebdc1861dfb8237727503825` at 15:53)
- unpushed: 47 at 15:53 (`git log --branches --not --remotes --oneline | wc -l`); 49 at 16:23 (impl-39) and at 16:35 (`git rev-list --count --branches --not --remotes`)
- porcelain: 29 lines at 15:53 (22 `??`, 7 `M`); 26 lines at 16:35
- round-5 report called this tree 16G. 16GiB = 17179869184. Every measurement this seat was above that. The "16G" premise does not hold.

### Per-file snapshot (the classification)

One `os.walk` (followlinks false), 35.4s, 0 read errors. Secret-shaped path components (`credential`, `secret`, `.env`, `.pem`, `id_rsa`, `id_ed25519`, `id_ecdsa`, `passwd`, `.netrc`) were counted and not opened. Every other regular file: at most 200 bytes. `.git` components classed by path, not read. Symlinks not followed.

| class | count | apparent bytes |
|---|---:|---:|
| content:text-markup | 295136 | 5135655204 |
| content:json-like | 120942 | 2478029721 |
| content:text-utf8 | 56994 | 2329139875 |
| content:shebang | 27300 | 1160831380 |
| git-metadata (path contains `.git`) | 22646 | 1154672765 |
| content:empty | 9410 | 0 |
| content:html | 1900 | 164425840 |
| content:pdf | 780 | 6557905000 |
| content:pyc-or-binary-header | 118 | 7023685 |
| content:xml | 80 | 166130540 |
| content:jpeg | 80 | 71012420 |
| symlink | 80 | 7152 |
| secret-shaped-unread | 60 | 480 |
| content:binary-other | 40 | 5020700 |
| content:gzip | 20 | 269820 |
| content:binary-nul | 20 | 540 |
| **sum** | **535606** | **19230125122** |

Reads: 512820. Secret skips: 60. Directory symlinks: 0. Top-level entries in that walk: 201.

Extension-vs-header mismatches in the same walk (not a second census):

| mismatch | count | cited header (≤200 bytes, non-secret) |
|---|---:|---|
| json→html | 200 | — |
| html→text-utf8 | 180 | — |
| pdf→html | 80 | `r23-run/reports/supplement-opencode-1/scratch/round5-13/evans2003b.pdf` starts `<!DOCTYPE html>` |
| html→empty | 60 | — |
| jpg→text-utf8 | 60 | `…/round5-07/leaf_try_684.jpg` starts `Error serving request:` |
| json→text-utf8 | 44 | — |
| gz→html | 20 | `…/src-09-slavs/ivanits_hocr.txt.gz` starts `<html>` / `401 Authorization Required` (not gzip magic) |
| json→binary-other | 20 | — |
| pdf→json-like | 20 | — |
| pdf→empty | 20 | — |
| json→binary-nul | 20 | — |
| json→empty | 1 | — |

A real PDF header was also seen (`%PDF-1.4` on `…/source-recheck-turkic/kincses2019.pdf`). Largest apparent file in the walk: 135327186 bytes, PDF magic, same basename under at least 8 clone prefixes (`x46/tree`, `x46/tree2`, `r25-o04/vclone`, `r24-run`, `r23-run`, `cold-run-4/tree`, `cold-run-4/tree2`, `audit4/export2`). Byte dominance is duplicated clone payload, not 780 unique PDFs.

Symlink targets in that walk: 64 absolute under kotodama-shokunin, 16 absolute under `/tmp`. Not followed. A removal of `.scratch` would not remove the `/tmp` targets, and following them leaves the tree.

Secret-shaped: 60 files, 480 bytes total (8 bytes each), every basename `outside-secret.txt` in the earlier name pass. Unread. Treat as fixture sentinels by name only. Content is to-verify, and must stay unread by souji.

### Why this is not "fully classified" as a closed claim

The tree moved during the seat.

| when | command | observed |
|---|---|---|
| 15:53 | `du -sh .scratch` | 18G |
| 15:53 | `find -mindepth 1 -maxdepth 1` | 219 top-level names, including 18 empty `r26-o33-*` dirs |
| classification walk | `os.walk` | 535606 file+symlink entries, 201 tops, apparent 19230125122 |
| 16:08 | `du -sb` | 18595798991 (`du -sh` 19G) |
| 16:09 | `os.walk` type count, no content | dirs 88133, files 536421, symlinks 85, tops 226 |
| ~16:23 | impl-39 `du -sb` | 27689220554 |

S82 (`census/round-6/scratch-judge-82.json`, read by S91, not written by S91) independently judged NOT-SAFE, receipt none, `sixteen_g_holds: false`, top-level classification of 219 entries, and explicitly `fully_classified_per_file_rows: false`. Apparent bytes there (19230117970) differ from this seat's per-file sum by 7152, which is this seat's symlink apparent-size total. Same window, different grain. Agreement on verdict. Not a freeze.

Coverage this seat actually delivered: a per-file header classification of one walk, plus this note. It did not deliver a stable inventory of a live 16G tree, because that tree is neither 16G nor stable.

Parent: do not prune `kotodama-shokunin/.scratch` from this note. Re-census only after that lane is quiet, then require per-path reference checks, secret-name refusal, and symlink fail-closed. Nested `.git` dirs under `.scratch` are clone fixtures; pruning them is still a write to a dirty unpushed lane.

## What S91 did not integrate

`census/round-6/` already held other seats' files at 2026-10-18T16:08:57-03:00 (listing, not a closed roster): `province-amend-25.diff`, `province-amend-26.diff`, `readme-amend-32.diff`, `scorecard-amend-29.diff`, `scratch-judge-82.json`, `seat-01.json`, `seat-05.json`, `seat-10.json`, `seat-11.json`, `seat-29.json`, `seat-72.json` (6519520 bytes, not read), `seat-76.json` (3213369 bytes, not read), `seat-78.json`, `skill-amend-20.diff`, `skill-amend-21.diff`, `skill-amend-23.diff`. More may have landed after that listing. Parent integrates. S91 did not.

## Parent stop list

- Do not claim drift → 0 while D1–D9 are true of the committed files.
- Do not install `tools/souji-census.sh` from impl-33 (selftest red) or from an untested draft. impl-39 is the only green selftest S91 ran, and its live kotodama mtime is false.
- Do not remove or quarantine kotodama `.scratch`.
- Do not rewrite `MINT.md` mint measurements.
- Do not read `outside-secret.txt` to "finish" classification.
- Ledger, `.ufo/state`, `.ufo/watchdog.log`: untouched, and should stay that way.
