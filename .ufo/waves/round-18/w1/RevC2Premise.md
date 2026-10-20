STATUS: DONE — Of the 18 listed instances, six are genuine dangling evidence references; the rest are fleet paths, ranges resolving to real files, or deliberate absent paths needing explicit exemption.

# C2 premise falsification

Axes: **calibration** (judged), **coverage** (all 18 listed instances checked), **operability** (read-only, exact-path inspection).

## Findings — MEDIUM, calibration

1. **`census/round-17/gate-replays-ddb7347.json` is a genuine dangling evidence pointer** — `SKILL.md:163,165`. It is absent from the lane tree at `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`, from fleet `HEAD`, from the working tree, and even from commit `ddb7347` itself. `git log --all` has no entry for that path. The expected replay file is tracked, but the round-17 tree instead contains `gate-replays-4f48343.json`; the cited `*-ddb7347.json` record does not exist. This substantiates the listed R2 issue.

2. **`census/round-17/jj-receipts-ddb7347.txt` is a genuine dangling evidence pointer** — `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148`. It is absent at the base, fleet `HEAD`, current lane working tree, and `ddb7347`; `git log --all` has no entry for it. The base receipt `jj-receipts-base5fa6017.txt` and a separately named `jj-receipts-4f48343.txt` are tracked. The cited `*-ddb7347.txt` output is not. This is an independent calibration defect not covered by the gate-replay R2 pointer.

   **Smallest fix:** point each citation at the actually committed output only if it is the intended evidence; otherwise generate and commit the missing, correctly identified artifact, then update all affected citations.

   **Additional occurrence noticed in the same in-scope file:** `corpus/README.md:216` also cites `../census/round-17/jj-receipts-ddb7347.txt`. Resolved from `corpus/README.md`, that is the same missing lane-root artifact. It was not among the 18 supplied occurrences. If the gate is intended to recognize file-relative `../` references, include this occurrence in the finding/fix; otherwise the path-token scope should say so explicitly.

## Classified non-findings among the 18

### Fleet-relative — seven instances

- `.ufo/state`: `SKILL.md:69`, `corpus/QUALITY.md:38`, `PROVINCE.md:39`.
- `.ufo/watchdog.log`: `SKILL.md:70`, `PROVINCE.md:39`.
- `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`: `SCORECARD.md:60`.
- `.ufo/waves/hyaku/jj-w1/reports`: `corpus/knowledge/jj-colocation-receipts.md:148`.

All four unique paths are absent from the lane tree at the base and **present in fleet `HEAD`**. Fleet working-tree `stat` also showed their targets (state directory, watchdog file, probe file, reports directory). These resolve as fleet-only, not dangling lane evidence.

### Range notation — two instances

- `SCORECARD.md:70` uses `corpus/lessons/round-{6..11}.md`.
- `corpus/README.md:55` uses `corpus/lessons/round-{1..11}.md`.

The literal range strings are not tree paths, but every expanded `corpus/lessons/round-1.md` through `round-11.md` exists at the lane base. None of those expanded files exists in fleet `HEAD`. These are valid range references, not calibration defects.

### Deliberate absent paths — three instances; explicit exemption required

- `SKILL.md:110` names `tests/vault/vadv54-run/p/p6repo/.git` as the old r16 fixture location and explicitly says it was quarantined. It is absent from the lane base, fleet `HEAD`, lane working tree, and commit history; its parent `tests/vault/vadv54-run` is a tree at the base. Treat this as a historical source-path description, not a current evidence artifact.
- `SKILL.md:110` names `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub`. It is absent from both committed trees but `stat` finds a directory at that exact lane working-tree path.
- `corpus/README.md:81` names `census/operator-sweep-20261019`. It is absent from both committed trees but `stat` finds a lane working-tree directory; the text explicitly calls it untracked and operator-owned. I inspected only its metadata, not its contents.

These three are deliberate, not evidence artifacts. However, `corpus/pointer-exemptions.tsv` is absent at the base. Under the stated C2 contract, the round-18 tree must commit exemptions with reasons for these exact non-tree paths, or the checker will mechanically flag them. Their deliberate nature alone is not an exemption.

## Evidence: commands and outputs

All commands were read-only. `LANE=/home/vgpnk/Projects/shokunin/souji-shokunin`, `FLEET=/home/vgpnk/Projects/shokunin`, `R=b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`, and `D=ddb73474433977ff54b015ac3e77669ff2537353` below.

- `git -C "$LANE" rev-parse HEAD` → `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`; authority files compared with `git diff --quiet "$R" -- SKILL.md SCORECARD.md PROVINCE.md corpus/QUALITY.md corpus/README.md corpus/knowledge/jj-colocation-receipts.md` → `IDENTICAL`.
- For each unique literal token path, `git -C "$LANE" cat-file -e "$R:<path>"` → `ABSENT`: `.ufo/state`, `.ufo/watchdog.log`, `tests/vault/vadv54-run/p/p6repo/.git`, `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub`, `census/round-17/gate-replays-ddb7347.json`, `census/round-17/jj-receipts-ddb7347.txt`, `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`, `census/operator-sweep-20261019`, `.ufo/waves/hyaku/jj-w1/reports`, and the two literal range spellings `corpus/lessons/round-1..11.md` / `round-6..11.md`.
- `git -C "$FLEET" cat-file -e "HEAD:<path>"` → `PRESENT` for `.ufo/state`, `.ufo/watchdog.log`, `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`, `.ufo/waves/hyaku/jj-w1/reports`; `ABSENT` for the other unique paths above, including both literal range spellings. A second loop checked fleet `corpus/lessons/round-1.md` through `round-11.md`: all `ABSENT`.
- A lane `cat-file -e` loop for `R:corpus/lessons/round-N.md`, `N=1..11`, returned `PRESENT` for all eleven.
- `git -C "$LANE" ls-tree --name-only "$R" -- census/round-17/` listed `gate-replays-expected.json`, `gate-replays-4f48343.json`, `jj-receipts-base5fa6017.txt`, `jj-receipts-4f48343.txt`, and other round-17 files; neither ddb7347-named artifact was listed. `cat-file -e "$R:census/round-17/gate-replays-expected.json"` and `...jj-receipts-base5fa6017.txt` both returned `PRESENT`.
- `git -C "$LANE" cat-file -e "$D:census/round-17/gate-replays-ddb7347.json"` and the corresponding `jj-receipts-ddb7347.txt` check both returned `ABSENT`. `git -C "$LANE" log --all --oneline -- census/round-17/gate-replays-ddb7347.json census/round-17/jj-receipts-ddb7347.txt` returned no rows (exit 0).
- `git -C "$LANE" cat-file -e "$R:corpus/pointer-exemptions.tsv"` → `ABSENT`. `git -C "$LANE" ls-tree "$R" -- tests/vault/vadv54-run` → `040000 tree ... tests/vault/vadv54-run`; `stat` on the old `.git` path → no such file, and `git log --all --oneline -- tests/vault/vadv54-run/p/p6repo/.git` returned no rows.
- `stat -c '%n|%F'` → lane quarantine stub `|directory`, lane operator sweep `|directory`, fleet `.ufo/state|directory`, fleet `.ufo/watchdog.log|regular file`, fleet probe `|regular file`, fleet reports `|directory`; lane state/watchdog and lane ddb7347 artifact paths returned no such file.
- `git -C "$LANE" grep -n -E ... "$R" -- SKILL.md SCORECARD.md PROVINCE.md corpus/QUALITY.md corpus/README.md corpus/knowledge/jj-colocation-receipts.md` located the cited lines. Targeted `git show "$R:SCORECARD.md" | sed -n '55,75p'` and `git show "$R:corpus/README.md" | sed -n '50,60p'` confirmed the brace ranges; `git show "$R:corpus/README.md"` also showed the additional `../census/...ddb7347.txt` citation at line 216.

## Residual risk / verification gap

This was a premise/path review, not an execution of the round-18 landing gate. The base lacks `corpus/pointer-exemptions.tsv`; round-18 exemption coverage and whether the gate recognizes `../` references remain unverified. No tools were installed and no tests or runtime commands were run.