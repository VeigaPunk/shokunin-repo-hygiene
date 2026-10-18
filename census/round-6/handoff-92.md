# S92 handoff — souji round 6

Seat S92, handoff drafter. Write scope: this file only. Observation window
2026-10-18T15:53:01-03:00 through 2026-10-18T16:11:40-03:00. Lane HEAD
`ce58c2b457c8ffb7886b36a509bf957f90d1f296` (round-5 close). The 128-seat
wave was still landing files at the end of the window. This note is a
snapshot, not a closed-wave integration.

Axes named: calibration (C1, docs/tools drift → 0), operability (O1,
`tools/souji-census.sh` repeatable), coverage (K1, kotodama `.scratch`
classified read-only). S92 improved none of them on disk. No axis was
harmed by this seat: no edits outside this file, no git mutators, no
ledger or vault writes, no kotodama writes, no deletes.

## Verdicts (this seat)

| claim | verdict | why |
|---|---|---|
| C1 calibration, drift → 0 | not met | `SKILL.md` still disagrees with the installed tools. Unapplied sibling diffs are not a reconciliation. |
| O1 operability, `tools/souji-census.sh` | not met | installed path absent. Three drafts, two contracts, one selftest failed 3/28. |
| K1 coverage, 16G `.scratch` fully classified | snapshot only, not a closed set | tree is live and larger than 16G. Full header walk exists. Removal is `NOT-SAFE`. |

Do not admit any of the three claims on this handoff alone.

## C1 — drift is not 0

Counting command, run from the lane repo at 15:54 and re-checked
`origin/main` at 16:11:40:

```
for t in metadata-prune pushed-unverifiable symlink-present secrets-refusal unreachable unpushed-branch; do
  rg -c -F "$t" SKILL.md || true
done
```

Observed: every token `SKILL=0`. Same tokens are present in
`tools/souji-verify.spec.md` (1–2 hits) and `tools/souji-verify.sh`
(2–7 hits).

Open contradictions S92 measured. Numerator = 12. Target was 0.

1. `SKILL.md:16` commands `git fetch -q` and `origin/main`. Spec lines
   39–42: no fetch; zero remote-tracking refs → `NOT-SAFE(pushed-unverifiable)`;
   a local `refs/heads/master` never establishes pushed.
   `git -C /home/vgpnk/Projects/shokunin rev-parse --abbrev-ref origin/HEAD`
   → `origin/master`. Still true at 16:11:40 (`rg -n origin/main SKILL.md`
   still hits line 16).
2. `SKILL.md:29` uses "last commit is an ancestor of `origin/<default>`".
   Spec uses the introducing commit (`git log --diff-filter=A`) and a
   remote-tracking ref only.
3. Six receipt/reason tokens above are absent from `SKILL.md` and present
   in the installed verifier. Counted as one taxonomy gap, six missing
   tokens, inside the numerator as item 3.
4. Stale procedure diverges. `SKILL.md:18` uses `*.tmp`, `out/`,
   last-admitted-round mtime, and `rg -l` with no D3 exclusions and no
   `--hidden`. Spec lines 49–54 use `.scratch/`, `*.out`, `*.log`,
   checkpoint json/png, `*-draft.*`, `--stale-days`, and census/tests/
   quarantine exclusions. Tool comment D-a (verify.sh:45) records that
   spec's `rg --basename` does not exist in ripgrep 15.2.0. That
   acknowledged deviation is still open text drift (item 4 includes it).
5. `SKILL.md:89` "lore-shokunin: 19 prunable worktrees".
   `git -C /home/vgpnk/Projects/shokunin/lore-shokunin worktree list | wc -l`
   → `1` (main only). The published relative form, run from this repo,
   does not reproduce that 1: `git -C lore-shokunin worktree list` →
   exit 128, `fatal: cannot change to 'lore-shokunin': No such file or
   directory`, stdout 0 lines (16:11:40).
6. `SKILL.md:90` "game-dev-2d-shokunin: 5 prunable worktrees".
   Absolute `worktree list | wc -l` → `4` (main + `wt-r98`/`wt-r99`/
   `wt-r100`, each `locked`). Relative `git -C game-dev-2d-shokunin`
   from this repo → exit 128, same fatal, stdout 0.
7. `SKILL.md:60` and `:91` say kotodama `.scratch` is 553M.
   `du -sh` at 15:53:01 → `18G`. `du -sb` at 15:53:01 → `18133369318`.
   `du -sb` at 15:57:41 → `18292985803`. The prompt's 16G figure and the
   sibling diff's "19G" string were not what `du -sh` printed here.
8. `SCORECARD.md:22` cites `tools/souji-verify.sh` sha256 `7efda63bd760…`.
   `sha256sum` at 15:54 → `53239fdfe5bcaaaf448e8525845ab962dd7ab6a4e7f75c0f4f051614f1c99200`.
9. `SCORECARD.md:24` cites `tools/souji-vault-verify.sh` sha256 `d312263a…`.
   `sha256sum` → `00d59b1b36d87db37518b5ef9fb98cd472888a075ed7b97bd5b8ff93bd559455`.
10. `SCORECARD.md` saturation paragraph says operability 7 and calibration
    6. The axis table says operability 8 and calibration 7. Internal doc
    contradiction, not a tool mismatch.
11. Installed script headers still name the CLI as
    `tools/souji-verify.impl-12.sh` (verify.sh:8) and
    `tools/souji-vault-verify.impl-20.sh` (vault-verify.sh:14). Those
    paths are not the installed entry points.
12. `tools/souji-vault-verify.sh` header says it supersedes
    `tools/souji-verify.sh`. Both files are installed. SCORECARD lists
    both as live capabilities.

Not in the numerator: `LOG.md` and `MINT.md` historical figures. Those
are append-only records. Rewriting them to match today's sizes would
violate the lane's correction discipline. `to-verify` only if the parent
expands C1 to historical prose.

Lane ledger, read-only hash, not the live vault:
`wc -l corpus/knowledge/obsidian-ledger.tsv` → `1`;
`sha256sum` → `3f7e9f2ab9e614464cb031d3f00a812a21f0e889f7666309a90d7784b75a9599`.
Header-only. No live moved-to-obsidian receipt in this file. S92 did not
open the vault at `/home/vgpnk/Documents/shokoknowledge`.

Sibling proposals existed and were not applied. `SKILL.md` still had
`origin/main` at 16:11:40, so none of these diffs had landed:

- `census/round-6/province-amend-26.diff` (read). It would retarget the
  receipt table at the installed tools and replace the 553M / 19 / 5
  surface figures. It also states three tool defects the amendment does
  not patch: stale sweep without `--hidden`, secret-shaped vault paths
  hashed instead of refused, `.ufo/state` not early-refused. S92 did not
  re-run those three probes. Treat that sentence as the sibling's claim,
  not as a re-proof.
- `census/round-6/scorecard-amend-29.diff` (read, first 40 lines). It
  would replace the stale sha prefixes with the HEAD hashes above and
  record that the relative `git -C lore-shokunin` form does not resolve
  from this repo. S92 independently reproduced that relative failure.
- Also present at 16:11:40, not read, not applied: `province-amend-25.diff`,
  `readme-amend-32.diff`, `skill-amend-20.diff`, `skill-amend-21.diff`,
  `skill-amend-23.diff`. Do not assume they agree with 26.

Parent close condition for C1: after one chosen patch is applied, re-run
the six-token loop (each `SKILL` count > 0, or the token is explicitly
retired), `rg -n 'origin/main|git fetch -q|553M|19 prunable|5 prunable'
SKILL.md` returns no operational hits, and `sha256sum` of both installed
verifiers matches the SCORECARD row. Until that re-run, drift is not 0.

## O1 — census entry point is not operable

```
ls -la tools/souji-census.sh
```

Observed at 15:53, 15:57, 16:04, and 16:11:40: `No such file or directory`.

Drafts present (not the installed path; contracts disagree):

| path | sha256 | contract (from its header) |
|---|---|---|
| `tools/souji-census.impl-33.sh` | `f4ab74df541ca93c0dececef6e2fbf003e9e900041c02bf17d025afbdb771bc0` | one row per git work tree: `repo worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags`. `--compare` exit 3 on diff. |
| `tools/souji-census.impl-39.sh` | `62315085a3ba676391010f7861432bb084f61d12df7b182e676a13fb89d6fd57` | same 7 columns, different `--compare` exit (1 on diff) and flag set. |
| `tools/souji-census.impl-34.sh` | `410c76eace7ce13f8f2bfb2c55b29bc3d68405845172eadc222b20108b396d65` | receipt census, `CENSUS` TSV, not the 7-column row. Not executed. |

Repeatability probe, fixture only:

```
bash tools/souji-census.impl-33.sh --selftest; echo EXIT:$?
```

Observed 16:04: `PASS repeat: two runs byte-identical`, then
`FAIL clean-shokunin verdict='dirty' want clean`. Debug row:
`dirty=2` because `git status` listed `?? .ufo/state/live.json` and
`?? .ufo/watchdog.log`. `selftest: 28 checks, 3 failed`. `EXIT:1`.
The mktemp tree `/tmp/souji-census-selftest.pIU5Rr` was gone at 16:11:40
(the script's own trap; S92 did not delete it).

So a draft can emit two identical runs on a frozen fixture, and still
fails its own clean-verdict contract by counting the two surfaces souji
must not touch as dirty. That is not an installed, repeatable fleet
census. impl-34 and impl-39 were not executed. A live-fleet run was not
attempted: kotodama `.scratch` was growing during the window, and a
census that opens lane trees would not be a stable repeat.

Parent close condition for O1: one contract chosen, installed as
`tools/souji-census.sh`, `--selftest` exit 0, then two consecutive runs
against a frozen `--root` byte-identical. Drafts under `impl-*` do not
satisfy the claim path.

## K1 — classified snapshot, not a closed 16G set

Subject: `/home/vgpnk/Projects/shokunin/kotodama-shokunin/.scratch`.
Read-only. No file there was modified. Secret-shaped paths were not
opened. Content reads were `read(200)` equivalent, regular files only.
Symlinks were `readlink`'d, not followed.

Owning lane at 15:53 and again at 15:57:

```
git -C kotodama-shokunin rev-parse HEAD
→ 1ad491a1a4b0aef9ebdc1861dfb8237727503825
git status --porcelain=v1 | wc -l → 29
git log --branches --not --remotes --oneline | wc -l → 47
```

Receipt: none. Verdict: `NOT-SAFE`. Not a removal authorization. The
tree was being written during the walk (`r26-run` mtime 15:52; scratch
dir mtime 15:52; `du -sb` rose 159616485 bytes between 15:53:01 and
15:57:41).

Size is not 16G.

| command | when | observed |
|---|---|---|
| `du -sh .scratch` | 15:53:01 | `18G` |
| `du -sb .scratch` | 15:53:01 | `18133369318` |
| `du -sb .scratch` | 15:57:41 | `18292985803` |
| python `st_size` sum of regular files | walk 15:55:20–15:55:57 | `19230117970` |

The `st_size` sum is not `du -sb`. A second walk counted 535526 regular
directory entries and 527219 unique `(st_dev, st_ino)` pairs; 11163
entries had `st_nlink>1` (hist top: nlink 2 × 5346, 31 × 3420, 44 × 2322,
6 × 75). `du -sb` counts an inode once. The name-sum double-counts
hardlinks. Both numbers are real; they are different quantities.

Walk coverage, 15:55:20–15:55:57, `os.walk(followlinks=False)`:

| class | count |
|---|---|
| directories | 87912 |
| regular files | 535526 |
| symlinks | 80 |
| header reads (200 bytes, non-secret) | 535466 |
| secret-shaped skipped, unread | 60 |
| header read errors | 0 |

Earlier `find -mindepth 1 | wc -l` at 15:53:01 was 615587
(d 86689 + f 528819 + l 80). The walk two minutes later saw ~7k more
files. A single walk cannot be "the" closed classification of a live tree.

Secret-shaped skip: all 60 basenames were `outside-secret.txt` (8 bytes
each, name match on `*secret*`). No `*.env`, `*credential*`, `id_*`,
`*.pem`, or `*.key` basename in that find. Contents not read.

Symlinks: 80, all absolute. 64 targets under
`/home/vgpnk/Projects/shokunin/kotodama-shokunin/`. 16 targets under
`/tmp/` (sample: `/tmp/d3-outside-probe.json`). Not followed.

Header classes (non-secret regular files + 60 skipped):

| magic | n |
|---|---|
| text-hash (`#` in first bytes; mostly markdown) | 295818 |
| json-like | 121155 |
| text-other | 58071 |
| text-yaml-or-shebang | 30526 |
| binary-other | 15002 |
| empty | 9414 |
| binary-nul | 2177 |
| text-markup | 2160 |
| pdf (`%PDF`) | 780 |
| git-pack (`PACK`) | 223 |
| jpeg | 80 |
| utf16-bom | 40 |
| gzip | 20 |
| skipped-secret-shaped | 60 |

Extension ≠ magic residual, not unclassified: ext `pdf` 800 vs magic 780;
ext `jpg` 140 vs magic 80; ext `gz` 40 vs magic 20. Those residuals were
still header-read and landed in another magic class. Top extensions:
md 274049, json 119029, yml 34983, txt 29559, py 26763, (none) 19022,
out 16663. Size buckets of regular files: 0 → 9414; 1B–1KiB → 45869;
1KiB–1MiB → 479433; 1MiB–100MiB → 790; 100MiB–1GiB → 20; ≥1GiB → 0.

Top-level at end of walk: 219 entries (138 dirs, 81 files). Largest
apparent-size families (name-sum, hardlinks included): `x*` 123124 files /
6399747946 bytes; `r25` 89976 / 3136141756; `r26` 90858 / 2924854674;
`r58` 86846 / 1747470533; `r23` 51664 / 1471413534; loose-or-other 10188 /
1363243159; `r22` 52343 / 1112057418. Biggest single names were repeated
copies of `b35683971-Gamble_R.pdf` at 135327186 bytes. Headers only;
bodies not read.

Machine-readable walk: `/tmp/s92-scratch-class.json` (scratch, not a lane
artifact). It will not survive a reboot. The tables above are the record.

Sibling K1 fragments are a different index. `census/round-6/seat-76.json`
(3.2MB at 16:06, first line read) is residue `i % 16 == 11` of a sorted
filename list, `pinned_n` 535606, slice 33475, its own `NOT-SAFE`. That
`pinned_n` is not this seat's 535526 regular files (it indexes filenames
including symlinks, on a later listing). Do not add the slice to this
walk, and do not treat either number as confirmation of the other.
`seat-72.json` (6.5MB) and `scratch-judge-82.json` were present at
16:11:40 and were not read.

Parent close condition for K1: kotodama idle (dirty and unpushed still
force `NOT-SAFE` even then), two walks with equal entry counts and equal
header-class totals, secret-shaped names still unread, and an explicit
statement that classification is not a removal list. The prompt's 16G
figure should be corrected to the `du` pair actually observed, with the
hardlink caveat, not rounded to 19G unless a new `du -sh` prints `19G`.

## Sibling inventory at 16:11:40 (not a closed wave)

`census/round-6/` then held: `province-amend-25.diff`,
`province-amend-26.diff`, `readme-amend-32.diff`,
`scorecard-amend-29.diff`, `scratch-judge-82.json`, `seat-01.json`,
`seat-05.json`, `seat-10.json`, `seat-11.json`, `seat-29.json`,
`seat-72.json`, `seat-76.json`, `seat-78.json`, `skill-amend-20.diff`,
`skill-amend-21.diff`, `skill-amend-23.diff`, plus this file once written.

Read by S92: `province-amend-26.diff`, the first 40 lines of
`scorecard-amend-29.diff`, `seat-11.json` (SHONEN seed trailer, not a
box edit; its verdict is that seat's, not re-derived here), and the
first line of `seat-76.json`. Everything else in that directory is
unreviewed.

`seat-11.json` is out of S92's claim set. Cited only so the parent does
not miss a SHONEN finding already on disk.

## What the parent should do

- Do not mark C1, O1, or K1 improved from this seat.
- Pick one docs patch and re-run the drift commands above. Unapplied
  diffs leave drift at 12.
- Do not install a census draft until one contract wins and its selftest
  exits 0. impl-33's clean-fixture failure is a real blocker for that
  draft: it counts `.ufo/state` and `.ufo/watchdog.log` as dirty.
- Do not prune, quarantine, or otherwise touch kotodama `.scratch`.
  47 unpushed, 29 dirty, live writes during the census.
- Do not hash or open the 60 `outside-secret.txt` paths, and do not open
  the live vault. Lane ledger hash above is the in-repo TSV only.
- Integrate sibling fragments after the wave stops. This listing is
  already incomplete relative to seats still writing.

## Non-interference

S92 wrote only `census/round-6/handoff-92.md` and
`/tmp/s92-scratch-class.json` plus two tiny `/tmp/s92-rel-*.{out,err}`
captures. No git fetch, push, commit, branch, prune, reset, or delete.
No write to kotodama, the lane ledger, the vault, `.ufo/state`, or
`.ufo/watchdog.log`. Secret-shaped file contents were not read.
