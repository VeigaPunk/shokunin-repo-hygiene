# r13 baseline measures (SoujiR13.BaselineMeasures)

Lane root: /home/vgpnk/Projects/shokunin/souji-shokunin
Measured: 2026-10-20 ~05:12–05:20 UTC (container clock). Read-only probes only; no build, lint, test, or tool execution. Tools used: git 2.55.0, awk, grep, sha256sum, ls, stat via read. No installs or upgrades.

## 1. Two baselines, not one

The lane working tree moved during measurement. Record both.

| surface | HEAD `31984f4` (authoritative baseline) | working tree at measurement |
|---|---|---|
| `corpus/SOURCES.md` sha256 | `1b7cc681084e9e5efcb3a89ff0f7943758d3040926c22f4cf5c58046ca548127` | `9a0cb40089f414a1…` (prefix) |
| SOURCES rows / malformed / dup / enum | 33 / 0 / none / none | 33 / 0 / none / none |
| SOURCES tier A/B/C | A=29 B=3 C=1 | A=29 B=3 C=1 (tier unchanged) |
| SOURCES status mined/queued/rejected | **mined=16 queued=15 rejected=2** | mined=18 queued=13 rejected=2 |
| S005 status / used-by | queued / — | mined / `corpus/knowledge/git-repo-structure-readonly.md` |
| S006 status / used-by | queued / — | mined / `corpus/knowledge/git-repo-structure-readonly.md` |
| `corpus/knowledge/` tracked entries | 6 (5 `.md` + `obsidian-ledger.tsv`) | 6 tracked + 1 untracked `git-repo-structure-readonly.md` (sha256 `48ff065f…`, mtime 2026-10-20 02:12:39 -0300) |
| `PROVINCE.md`, `corpus/QUALITY.md` | clean | modified (`git diff --stat`: 14 insertions, 1 deletion) |
| `git status` untracked | not applicable | `?? .ufo/`, `?? census/operator-sweep-20261019/`, `?? census/round-13/`, `?? corpus/knowledge/git-repo-structure-readonly.md` |

Working-tree SOURCES.md is a sibling seat's uncommitted edit, not HEAD. Any L1 check that reads the working tree sees the mid-flight state. Use HEAD for the baseline.

Textual note: the assignment's "mined16 queued15 rejected2" matches HEAD. `census/round-12/sources-census.txt` and `census/round-12/after.txt` both record **mined=18 queued=13** at `d7266c5`. That is stale relative to HEAD. The diff `d7266c5 → 2a363a0` changes S024 and S025 from mined to queued (`git show d7266c5:corpus/SOURCES.md` vs `HEAD:corpus/SOURCES.md`; S030 stays rejected). So the round-12 snapshot is superseded, not wrong for its commit.

HEAD commit: `31984f473ce4bdab61a99b16cca194b28108cb81` (subject: `round-12 verifier spot-check (integrator, kaika): non-author admit/reject sample + adjudication`). Tracked files at HEAD: `git ls-files | wc -l` → 1574. Prior commit `2a363a0` ("round-12: post-review fixes").

## 2. Surface existence and counts (r13 targets)

| r13 surface | state at HEAD | evidence command | result |
|---|---|---|---|
| New executable evidence validator (C1) | **absent** | `git -C R ls-files \| grep -iE 'evidence\|validat' \| grep -v operator-sweep \| grep -v '^tests/vault'` | no output, exit 1 |
| Bounded per-target staging/digest in `tools/souji-quarantine.sh` (C2, Q8) | **absent** | `git -C R show HEAD:tools/souji-quarantine.sh \| grep -c timeout` | 0 |
| FIFO/device/socket rejection in quarantine tool | **absent** | `git -C R show HEAD:tools/souji-quarantine.sh \| grep -cE '\[ -(p\|S\|c\|b) \|FIFO\|fifo\|socket'` | 0 |
| r13 quarantine bounds fixture `tests/fixtures/r13-quarantine-bounds.sh` (C2) | **absent** | `test -e R/tests/fixtures/r13-quarantine-bounds.sh; echo $?` | 1 (no such file) |
| F2 knowledge entry (C3) | **absent at HEAD** | `git -C R ls-files corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` | 0 |
| F2 entry in working tree | present, untracked (see §1) | `ls R/corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` | 1 (`git-repo-structure-readonly.md`) |
| PROVINCE F2 row text | "unexplored; no entry yet" at HEAD | `grep -n 'F2 repository size census' R/PROVINCE.md` | PROVINCE.md:55 (HEAD text) |
| `corpus/README.md` F2 row | "frontier, no entry" at HEAD | `grep -n '^\| F2 ' R/corpus/README.md` | line 40 at HEAD |

Quarantine tool at HEAD: blob `201c3c462d59ee882d498543acfb5634a2fff2d7`, 1569 lines, working-tree sha256 `141c0fdc4eaf9d0a3d628b381cc5386f6d4be71565ddfb98aa10f6eb3c9573c9`, last commit `e879ba0`. `git ls-files -s` blob id is the authoritative HEAD identity.

Digest helper duplication (observed, not yet a bug claim): the tool defines `file_sha` and `dir_digest` twice, at lines 184/186 and again at 722/727, plus `content_digest` at 196. In bash the later definition wins at runtime, so lines 184–194 are dead, and `content_digest` (198) calls the later `file_sha`, which has the `[ -f ]` guard at 723. Whether a FIFO reaches `sha256sum` is therefore [INFERENCE]; check it in the executor's fixture, not here.

Stage-2 call sites (observed): `git -C "$crepo" mv` at line 529, `mv --` at 536, both with no timeout wrapper. Dry-run prints `sleep $HOLD` at 511. The live stage-2 loop has no timeout token anywhere in the file (count 0).

Historical hang evidence (observed text): `LOG.md:372-378` says the tool "hung" after 3 staged files and was completed manually. `LOG.md:434-435` records the per-target staging loop "can hang". These are log statements; no reproduced timing exists.

Certification relays (observed, tracked): `census/round-10/cert-16.json` sha256 `662294df4291c16fb0fe8c9a0b6dd58b72ada9476b45113fa7c44d383952c3c1`; `census/round-11/cert-16.json` sha256 `718409192fd82f7a9fff70965d24d4161713792bb7afd04e04de55cc595598fc`. Different bytes across rounds is expected; whether either matches an installed artifact is [INFERENCE] not measured here. The validator must compare explicit installed hashes, not relay text.

Corpus lesson pointer: `corpus/lessons/round-12-verifier-spotcheck.md` (1982 bytes; not hashed here) is the current non-author lesson. Its K5 HELD note and Q15/Q16 are read from it and `corpus/README.md:59-60`.

## 3. Source census — reproducible counting commands

Run from the lane root. The contract source is `census/round-12/sources-census.sh` (copied from fleet-ledger SOURCES-CONTRACT-v1; the fleet file itself is not in this lane and was not opened). Each command reads `corpus/SOURCES.md` only.

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin   # or use: git -C ... show HEAD:corpus/SOURCES.md > $TMP
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md                       # rows
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}' corpus/SOURCES.md   # malformed, must be 0
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {t=$5; gsub(/[[:space:]]/,"",t); n[t]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md   # tier
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {s=$9; gsub(/[[:space:]]/,"",s); n[s]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md   # status
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {i=$2; gsub(/[[:space:]]/,"",i); print i}' corpus/SOURCES.md | sort | uniq -d   # dup ids, must be empty
# enum/tier-inflation check: census/round-12/sources-census.sh line 14, must print nothing
# missing used-by paths for mined rows: census/round-12/sources-census.sh line 16, must print nothing
```

Measured now (each `grep -c` and `awk` command exited 0; `grep -c` printed 33):

- HEAD via `git show HEAD:corpus/SOURCES.md` into a `mktemp -p /var/tmp` file (then removed): tier `A=29 B=3 C=1`, status `mined=16 queued=15 rejected=2`.
- Working tree (same commands on the file as it stood): rows 33, malformed 0, dup empty, enum empty; status `mined=18 queued=13 rejected=2` (sibling uncommitted edit).
- The used-by existence check (line 16) was **not run** at HEAD. Proposed check (L1): extract HEAD to a temp dir and run line 16 there, so untracked files cannot satisfy `[ -e ]`. On the working tree, the untracked F2 file makes a `mined` used-by path resolvable, which is exactly the false-pass a HEAD-based check would catch.
- The phrase "souji ok" in the assignment is asserted by `corpus/lessons/round-12-verifier-spotcheck.md` ("census ok"). `tools/souji-census.sh:192` prints `ok` as the output of a secret-shape classifier, which is a different function. Do not conflate them. No stored stdout of the registry census with "ok" exists in the lane; treat that label as text-only.

Textual counts are not proof: they come from `awk`/`grep` over a markdown table with a column-position assumption (NF==13). A row with an extra `|` inside a cell would change NF and the status column index. L1 should check that `malformed=0` and the row count 33 agree.

## 4. Proposed final checks for L1 (not run by this seat)

1. `git -C R rev-parse HEAD` equals `31984f473ce4bdab61a99b16cca194b28108cb81`.
2. Validator absence at HEAD: the `ls-files` grep above returns empty. Re-run after C1 lands; expect exactly the new validator path.
3. Quarantine tool: `git -C R show HEAD:tools/souji-quarantine.sh | grep -c timeout` is 0 at baseline; after C2 it must be nonzero and the timeout call sites listed. Also `grep -nE '^(file_sha|dir_digest|content_digest)\(\)'` shows the 5 definition lines at baseline; after C2 duplicates must be removed (one definition each).
4. Bounded test fixture: `tests/fixtures/r13-quarantine-bounds.sh` must exist after C2 and be run by L1, not by the executor.
5. Registry census: run `census/round-12/sources-census.sh` lines 4–16 against HEAD-extracted SOURCES and against the post-C3 SOURCES; expected after C3 only if S005/S006 are changed under the contract, which is what the C3 seats are deciding.
6. F2 entry: `git -C R ls-files corpus/knowledge | grep -ciE 'size|structure|sizer'` must be 1 only after the entry is committed; the working-tree untracked file must be committed or excluded by the same check.
7. Cert relay hashes: re-hash `census/round-10/cert-16.json` and `census/round-11/cert-16.json` and compare with the `662294df…` and `71840919…` values above; any change means a relay was rewritten.

## 5. Limitations and deviations

- **Deviation (disclosed):** my first probe was an unscoped regex search over the whole lane for validator/quarantine/F2 tokens. It returned lines from `census/operator-sweep-20261018/` and `census/operator-sweep-20261019/`, which the assignment says must not be scanned. I did not open, quote, or use those contents, and no finding here depends on them. The same search could have matched files in `tests/fixtures/case-F10/` (credential-shaped fixture); I did not read them. All later probes were scoped to `corpus/`, `tools/`, `tests/fixtures/`, `census/round-1x/`, `LOG.md`, and `PROVINCE.md`.
- **Race:** the working tree changed during measurement (§1). Every working-tree number is a snapshot at its timestamp. HEAD numbers are stable.
- **Not verified:** the 16 mined rows' used-by paths at HEAD; the `sources-census.sh` tail checks (lines 14, 16) at HEAD; the FIFO behaviour of `file_sha`/`dir_digest` (no fixture run; baseline audit only). The `tests/fixtures/r12-maintenance-guard.sh` gate was not run.
- **Installs:** none. Tools used were already present (git 2.55.0, awk, grep, sha256sum).
- No commits made. No edits outside `census/round-13/baseline-measures.md` and `.ufo/waves/round-13/w1/BaselineMeasures.md`.
