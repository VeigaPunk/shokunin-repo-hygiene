# SwarmSimplifier68 — dry-run hygiene census of the souji lane's own top level

STATUS: PASS — every tracked and untracked top-level entry (167 artifact rows) is classified with a git-derived receipt and a NOT-SAFE default; nothing was moved, deleted or quarantined, and no artifact qualifies for removal under the lane's own rules this round.

Base: `b8cb4b3` (branch master, `refs/remotes/origin/master` = `b8cb4b31ce80e2e3314b88e85d40ea9873180804`; `git log --branches --not --remotes --oneline | wc -l` = 0).

## Evidence

Enumeration (NUL-safe; the tasking's `git ls-files | cut -d/ -f1` variant is unsafe, see Finding 1):

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-files -z | tr '\0' '\n' | ... top-level tally
18 top-level names / 7097 tracked files  -> .ufo 3016, census 2911, tests 920, tools 138, corpus 68,
results 32, .gitignore, .scratch, .ufo-reports-placeholder, AGENTS.md, LOG.md, MINT.md,
PROVINCE.md, SCORECARD.md, SHONEN.md, SKILL.md, err4.nl2, err4.z2
$ git -C ... status --porcelain --ignored | wc -l
69   (1 modified tracked file: .ufo/waves/round-26/w1/ScribeGateDraft.md; 68 ignored entries)
```

Receipts, installed tool (`tools/souji-verify.sh`, read-only; ledger `corpus/knowledge/obsidian-ledger.tsv` has 1 line = header, so no `moved-to-obsidian` row can qualify):

```
VERDICT  err4.nl2                       SAFE      pushed  intro=1ccf11ba3711 ref=refs/remotes/origin/master ancestor=yes
VERDICT  err4.z2                        SAFE      pushed  intro=1ccf11ba3711
VERDICT  .ufo-reports-placeholder       SAFE      pushed  intro=1ccf11ba3711
VERDICT  .scratch                       SAFE      pushed  intro=1ccf11ba3711
VERDICT  results                        SAFE      pushed  intro=1ccf11ba3711
VERDICT  tests/results                  SAFE      pushed  intro=d7266c5e9493
VERDICT  tools/impl-21.sh               NOT-SAFE  secrets-refusal  secret-shaped-or-protected-symlink-or-control-path-refused
VERDICT  tools/impl-40.sh               SAFE      pushed  intro=b5db5cf27b5c
VERDICT  tools/cand-a1-verify.sh        SAFE      pushed  intro=e879ba03a2d7
VERDICT  tools/souji-census.impl-34.sh  SAFE      pushed  intro=b5db5cf27b5c
VERDICT  tools/souji-verify.impl-12.sh  SAFE      pushed  intro=9435e464a2dc
VERDICT  tests/fixtures/__pycache__  tools/__pycache__  NOT-SAFE none  pushed=dirty-or-untracked-content; obsidian=no-matching-ledger-row; stale=not-scratch-type
VERDICT  tools  census  tests  .ufo      NOT-SAFE secrets-refusal  protected-or-unsupported-descendant-refused
VERDICT  corpus                         NOT-SAFE none  pushed=unpushed-commits-touching intro=691dd29211c5 jj-keep-novel
VERDICT  .jj                            NOT-SAFE none  pushed=dirty-or-untracked-content; stale=not-scratch-type
```

Per-path git receipt (same rule the tool implements, `SKILL.md:35`): `git log --diff-filter=A --format=%H -1 -- <path>` + `git merge-base --is-ancestor <intro> refs/remotes/origin/master` + `git log --branches --not --remotes --oneline -- <path>` (0 for all 152 pushed rows).

Sizes: `du -sb` per artifact; lane total 190,200 KiB (`du -sk . --exclude=.git`). Census per round from `du -sk`, largest first: round-6 44,916 KiB, round-26 20,084, round-21 9,388, round-20 3,500, round-18 2,768.

## Findings

1. **The tasking's suggested top-level command misreports phantom entries.** `git ls-files | cut -d/ -f1 | sort -u` prints `second.md` and `name.log` three times each. Cause: two tracked fixture paths contain a literal newline — `tests/vault/vadv54-run/r/nl/first`+newline+`second.md` and `tests/vault/vadv54-run/r/scratch/.scratch/old`+newline+`name.log` (and their mirrors under `census/round-26/waves/` and `.ufo/waves/round-26/`, 6 tracked records). Verified by `git ls-files -s -z | tr '\0' '\n' | grep -B2 -E '^second\.md$'`: the path is on the record line that contains the tab, the tail of the name lands on the next line. Correct enumeration is NUL-safe (`ls-files -z`); any census that cuts paths line-wise under-counts here.

2. **The lane-root strays are four files, all with `pushed` receipts, all pinned as evidence — retain.** `err4.nl2` and `err4.z2` are 67 B each and byte-identical (`sha256sum` = `2f4106c97935d41145984144b73c631e6e3f6bf32ca15f4eb6f39b014446d94d`); `.ufo-reports-placeholder` is 0 B; `.scratch/s29-freeze-dir.txt` is 38 B and names `FREEZE_DIR=/var/tmp/s29-freeze.fe7LLx`, which no longer exists (`stat`: ENOENT). All four entered in `1ccf11b`. Zero references in live authority, but `census/round-12/mistakes.md:139` (row M45) and `:219` plus `corpus/lessons/round-12.md:107` cite them, and `LOG.md:423` records them as live/too-young. Removing the pair would leave the r12 defect row's path:line citation unresolvable — the calibration cost exceeds the 134 B recovered.

3. **The 112 `cand-*` / `impl-*` / `*.impl-*` / `*.r9-s18.sh` files are historical fixtures, not strays.** `git grep -E 'cand-|impl-|r9-s18' HEAD -- SKILL.md AGENTS.md SCORECARD.md PROVINCE.md SHONEN.md MINT.md` returns nothing — SKILL.md cites none of them. Of the 112: **34 are executed** by committed gates via glob (`tests/vault/judge-60-vault.sh:63,67`; `runner-25.sh:93-94`; `runner-28.sh:55`; `runner-31.sh:103`; `runner-34.sh:91`; `vadv52-harness.sh:287`); **all 112 are name-cited** in committed census (3385 `git grep` lines under `census`); the 61 `cand-*` are **byte-identical triple copies** (`tools/`, `.ufo/waves/round-26/assimilation/validate/tools/`, `census/round-26/waves/assimilation/validate/tools/` — 61/61 equal by sha256) and hash-pinned, e.g. `census/round-10/seat-01.json:77`.

4. **Two naming conventions are bridged by three tracked symlinks, and that is what blocks whole-directory receipts.** `tools/impl-21.sh -> souji-vault-verify.impl-21.sh`, `tools/impl-39.sh -> souji-census.impl-39.sh`, `tools/souji-census.impl-40.sh -> impl-40.sh` (mode 120000 in `git ls-files -s`). `tests/vault/runner-34.sh:87-89` documents the convention: "Two naming conventions are in flight this round" and dedupes by realpath. Consequence measured above: `tools/`, `tests/`, `census/` and `.ufo/` cannot receive a tree-level verdict (`protected-or-unsupported-descendant-refused`) — driven by those three aliases for `tools/`, by the tracked `tests/fixtures/case-F10/creds.pem` at three paths for `tests/`/`census/`/`.ufo/`, and by 14 tracked symlinks under `tests/`. Cleanup of this lane is per-file only.

5. **Ignore rule and tracked state disagree for `census/operator-sweep-20261018/`.** `.gitignore:2` says `census/operator-sweep-*/`, yet all 15 files (5,488,672 B) under `census/operator-sweep-20261018/` are tracked (introduced `2f303dc`, older than the ignore rule's `765fe8b`), while `census/operator-sweep-20261019/` has 0 tracked files and 4,131,107 B apparent. Contents were not opened (seat contract). C1's declared case set does not include ignore-rule drift, so this is a visible hygiene surface no counter reads — reported, not amended.

6. **`results/` is a dead-end chain next to the live `tests/results/`.** `results/` = 32 files, 462,904 B, last touched `1ccf11b`; only files with a consumer are `results/.write-probe` (read by `tools/souji-quarantine.impl-S12.sh`), `results/qrun-11.json` and `results/cross-100.json` (read by `tools/qrun-11.sh`), `results/qrun-23.json` (`tools/impl-07.sh`). `tools/qrun-11.sh` is referenced only by itself (`git grep -c -F 'qrun-11.sh'` → 7 hits, all inside it). `tests/results/` is the live output dir of `tests/runner-*.sh`, `tests/judge-60.sh`, `tests/vault/*.sh`; 35 of its 137 basenames are cited outside it (`SCORECARD.md:148-152`, `SKILL.md:183`, `tests/fixtures/case-F6/make-fixture.sh:16`), 102 are not — but bulk cleanup would break the cited subset and the case-F6 ledger-inject input.

7. **Wave evidence has no receipt at its own path, by design.** `.gitignore:1` (`.ufo/waves/`, added `765fe8b`) makes rounds 27–29 untracked: 123 / 74 / 101 files. Their committed receipt is the census mirror `census/round-27/waves` (125 files), `round-28/waves` (76), `round-29/waves` (0 at base). Deleting a wave directory would destroy live work; the mirror is the retention mechanism.

8. **Census size concentration.** `census/` = 100 MB apparent over 2911 files; round-6 alone is 45,813,161 B (98 files, `seat-73.json` 11.4 MB, `seat-71.json` 9.3 MB). Rounds 11 and 15 have zero live references; all 28 rounds hold `pushed` receipts. No round is reclaimable without destroying historical evidence, and no counter in this round scores the disk axis.

9. **`corpus/` refuses `pushed` right now.** `tools/souji-verify.sh` returns `pushed=unpushed-commits-touching intro=691dd29211c5 jj-keep-novel` — a `refs/jj/keep/*` commit introduces a blob under `corpus/` that is not on origin (616 keep refs present). Consistent with the C3 registry landing being in flight; recorded as NOT-SAFE, no action.

10. **The `stale` taxonomy word is unreachable for this artifact set.** `__pycache__/` is not in the tool's scratch-type set (`stale=not-scratch-type`), `err4.*` has no scratch extension, and `.scratch/s29-freeze-dir.txt` is scratch-type but `pushed` is tried first (`SKILL.md:38-40`). So the receipt column is 152 `pushed` / 15 `none` / 0 `moved-to-obsidian` / 0 `stale`; the two `__pycache__/` dirs (126,664 B and 9,615 B, 4 .pyc total) are regenerable but hold no receipt, and `SKILL.md:40` "No receipt → no removal." keeps them in place.

## Attack log

None filed. No frozen predicate was found gameable: C1's case set, C2's manifest/uncovered pair and C3's row counts were inspected only as consumers of this census; Finding 5 (ignore-rule drift) lies outside C1's declared cases and is a coverage observation, not a defect in the predicate.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-lane-stray-census.tsv` — 167 artifact rows plus header: `path, bytes, tracked, referenced-by, last-commit, receipt, proposed-action, reason, class`. `class` is the assignment's classification word (live 76 / duplicate 66 / stale 21 / unknown 4) and is independent of `receipt`, which is the lane's receipt taxonomy (pushed 152 / none 15 / moved-to-obsidian 0 / stale 0). Directory rows are aggregates and are not additive (lane total 190,200 KiB). Nothing was moved or deleted; every `proposed-action` is `retain` (four rows say `retain, quarantine only after operator approval`; two `__pycache__` rows say `report only, delete on operator approval (regenerable)`).

Tooling: no installs or upgrades this run (no package needed; `git`, `du`, `sha256sum`, `python3 -B` sufficed).
