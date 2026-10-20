STATUS: DONE — blind C2 re-derivation at b576341 over the five authority files: 272 path-token occurrences (132 distinct); 23 lane-unresolved occurrences (16 distinct) = 2 dangling evidence pointers, 3 deliberate non-files, 5 fleet-relative, 6 grammar artefacts; one dangling citation (corpus/README.md:216) is outside the routed R2 list.

# PointerSweepAuthority — C2 (QUALITY Q5) blind pointer re-derivation

Seat `SoujiR18.PointerSweepAuthority-5`. Read-only except this report: no lane/fleet writes, no jj, no tool runs, no signals, no other seat's output read.
Revision: `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (short `b576341`), lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Fleet tree for fleet-relative checks: `git -C /home/vgpnk/Projects/shokunin ls-tree -r --name-only HEAD`.

## 1. Method — pinned so the count is falsifiable

Files (content read only via `git show REV:<file>`): `SKILL.md`, `SCORECARD.md`, `PROVINCE.md`, `corpus/QUALITY.md`, `corpus/README.md`.

Tokenizer (regex, left-to-right, non-overlapping):
- an *anchored* token starts at start-of-line or after one of `space \t \` ' " ( [ { ; : , |` and matches `(?:census|tests|tools|corpus|\.ufo)/` followed by `(?:[^\s\`'")\],;{] | \{[^{}]*\})+`;
- a *relative* token starts at the same boundary and matches `(?:\.\./)+(?:census|tests|tools|corpus|\.ufo)/…` (so `../tools/x` and `../../.ufo/x` are both counted);
- trailing `.` `:` `,` `;` `` ` `` `'` `"` stripped; a `:\d+(-\d+)?` suffix is stripped before resolution (11 distinct tokens carried one).
- Deliberately not tokenised: `souji-shokunin/census/**` and `souji-shokunin/tests/**` (SKILL.md:37) — tokens rooted at the fleet repo *name*, part of a `find` expression, not lane-relative; and `^\.tower/\|\.ufo/state/\|watchdog\.log` (corpus/QUALITY.md:38) — a grep alternation with escaped dots, not a path token.

Resolution:
- lane: exact blob in `git ls-tree -r REV`, else directory if any tree entry lies beneath the token (`…/` or bare dir names);
- braces: `{a,b}` and `{N..M}` expanded, every candidate must resolve;
- fleet: same test against the fleet HEAD tree; a token (or its `../`-normalised form) that fails in the lane but passes in the fleet is class `fleet`;
- wildcards (`*`) are checked with `fnmatch` against the tree for reporting, but a wildcard token that matches ≥1 blob is **not** dangling.

Counting unit: a path-token *occurrence* per line (a token repeated on two lines is two occurrences); distinct-token counts are also given. No occurrence was double-counted as a substring of a longer token (the inner `tests/` of `.ufo/quarantine/…/tests/…` is skipped because `/` is not a boundary).

## 2. Counts

| file | token occurrences | lane-unresolved occurrences |
|---|---|---|
| SKILL.md | 87 | 7 |
| SCORECARD.md | 69 | 4 |
| PROVINCE.md | 14 | 2 |
| corpus/QUALITY.md | 61 | 5 |
| corpus/README.md | 41 | 5 |
| **total** | **272** (109 anchored + 23 relative distinct; **132 distinct**) | **23** (**16 distinct**) |

Resolved: 249 occurrences / 116 distinct (246 plain + 3 brace/wildcard forms that resolve after expansion).

Unresolved by class:

| class | distinct | occurrences |
|---|---|---|
| dangling evidence pointer | 2 | 3 |
| deliberate non-file | 3 | 3 |
| fleet-relative | 5 | 8 |
| grammar artefact | 6 | 9 |
| **total** | **16** | **23** |

Forms that must **not** be treated as unresolved (prerequisite for a zero-finding gate tip):
- brace forms, all candidates present at REV: `census/round-17/seat-audit-r16-replay-{base5fa6017,4f48343}.json` (SCORECARD.md:14; both files exist), `corpus/lessons/round-{6..11}.md` (SCORECARD.md:70), `corpus/lessons/round-{1..11}.md` (corpus/README.md:55);
- wildcard forms, non-empty matches at REV: `census/round-14/verification*.json` (SCORECARD.md:45 → 3 matches: `verification.json`, `verification-attempt-1.json`, `verification-plan.json`), `census/round-17/jj-receipts-*.txt` (SCORECARD.md:50 → 2 matches: `jj-receipts-4f48343.txt`, `jj-receipts-base5fa6017.txt`);
- all 11 `path:line` tokens resolve after suffix strip.

## 3. Full lane-unresolved list (file:line, class)

### 3.1 Dangling evidence pointer — 2 distinct / 3 occ

| token | locations | note |
|---|---|---|
| `census/round-17/gate-replays-ddb7347.json` | SKILL.md:163, SKILL.md:165 | routed as closure R2 |
| `../census/round-17/jj-receipts-ddb7347.txt` → `census/round-17/jj-receipts-ddb7347.txt` | corpus/README.md:216 | **not named in the routed R2 text**; same missing artifact family |

Forensics (all observed):
- `git cat-file -e b576341:census/round-17/gate-replays-ddb7347.json` → rc 128; same for `…/jj-receipts-ddb7347.txt`.
- `git rev-list --all --objects | grep ddb7347` → exactly one line, the **commit** `ddb73474433977ff54b015ac3e77669ff2537353` ("round-17: C1 census D1/D2, …"), no path object. The ddb7347 run's outputs were never committed anywhere in lane history.
- Neither file exists on disk (`os.path.lexists` false for both) and neither appears in `git ls-files --others` (no untracked copy).
- The committed counterparts exist at REV: `census/round-17/gate-replays-4f48343.json` (`gate_rev_arg: 4f48343…`), `census/round-17/gate-replays-expected.json`, `census/round-17/jj-receipts-base5fa6017.txt`, `census/round-17/jj-receipts-4f48343.txt`.

Smallest fix (R2): do not silently substitute. Either regenerate/commit the ddb7347 record and receipt, or reword the three citing sites (SKILL.md:163, SKILL.md:165, corpus/README.md:216, plus the four citations in `corpus/knowledge/jj-colocation-receipts.md` handled by R2) to cite only the committed artifacts and drop the claim that a `ddb7347` record exists. `corpus/README.md:216` must be in the same edit or the gate will find it.

### 3.2 Deliberate non-file — 3 distinct / 3 occ

| token | location | why it is not a committed file | smallest fix |
|---|---|---|---|
| `tests/vault/vadv54-run/p/p6repo/.git` | SKILL.md:110 | the r16 nested-`.git` stub was removed and quarantined in r17 (a `.git` directory cannot be tracked; the tracked siblings `p6repo/one.txt`, `p6repo/inner/keep.txt` exist) | one row in `corpus/pointer-exemptions.tsv` |
| `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub` | SKILL.md:110 | present on disk as an **empty directory** (verified: `os.listdir` → `[]`); git does not track empty directories; quarantine is runtime state | one row in `corpus/pointer-exemptions.tsv` |
| `census/operator-sweep-20261019/` | corpus/README.md:81 | present on disk, 152 untracked non-ignored files; corpus/README.md:81 itself says "untracked … remains operator-owned and is excluded from round staging"; never staged by contract | one row in `corpus/pointer-exemptions.tsv` |

If the gate's scan scope is the literal `.ufo/waves/` from the C2 text (not `.ufo/` as assigned to this seat), the quarantine-stub row is not scanned and only **2** rows are needed; `tests/vault/…/.git` and `census/operator-sweep…` are in scope either way.

### 3.3 Fleet-relative — 5 distinct / 8 occ (not findings)

| token | locations | fleet evidence |
|---|---|---|
| `.ufo/state/` | SKILL.md:69, PROVINCE.md:39, corpus/QUALITY.md:38 | fleet HEAD tracks 64 entries under `.ufo/state/` (e.g. `.ufo/state/.gitkeep`, `.ufo/state/aggregator.mission`) |
| `.ufo/watchdog.log` | SKILL.md:70, PROVINCE.md:39 | tracked in fleet HEAD |
| `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` | SCORECARD.md:60 | tracked in fleet HEAD |
| `../../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` | corpus/README.md:217 | normalises to fleet `.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md`; tracked in fleet HEAD |
| `../../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` | corpus/README.md:217 | same; tracked in fleet HEAD |

Caveat for the gate: all five resolve **only** against the fleet repo (the lane worktree has no `.ufo/state`, `.ufo/watchdog.log`, `.ufo/scopes`, and no `../.ufo/waves/hyaku`). If the gate cannot locate the fleet tree it will emit 5 false findings; it needs an explicit fleet root (the parent directory works only in this layout) and, in a hermetic clone, either 5 exemption rows or a documented `fleet-unchecked` outcome.

### 3.4 Grammar artefact — 6 distinct / 9 occ (skip rule covers them)

| token | locations | form |
|---|---|---|
| `census/round-N/<new>.json` | SKILL.md:231, SCORECARD.md:26 | placeholder template |
| `census/round-<N>/` | corpus/QUALITY.md:34, corpus/QUALITY.md:37, corpus/README.md:54 | placeholder |
| `census/round-<N>/seat-audit-<wave>.json` | corpus/QUALITY.md:65 | placeholder |
| `tools/<tool>.sh` | corpus/QUALITY.md:30 | placeholder |
| `census/round-14/verification*.json` | SCORECARD.md:45 | wildcard, **resolves** (3 blobs) |
| `census/round-17/jj-receipts-*.txt` | SCORECARD.md:50 | wildcard, **resolves** (2 blobs) |

## 4. Consequences for the C2 gate (smallest set that reaches 0 findings at the tip)

1. Strip `:\d+(-\d+)?` before resolution (11 tokens depend on it).
2. Expand `{a,b}` **and** `{N..M}` before the skip test (3 tokens depend on it, e.g. SCORECARD.md:14 — a naive tokenizer stops at the comma and would flag it).
3. Treat `*` tokens as resolved when `fnmatch` matches ≥1 blob, or skip them (2 tokens).
4. Skip tokens containing `<`, `>`, or the literal `round-N` (6 tokens above; `round-<N>` also contains `<`).
5. Normalise `../` **and** `../../` prefixes relative to the citing file and test the result against the lane tree; without this the README:216 dangling pointer is invisible to the gate (it has no leading prefix), and the two `../../.ufo/waves/hyaku/…` links would be misclassified.
6. Resolve directories (trailing `/` and bare dir names such as `corpus/knowledge`, `census/round-13/`, `tests/results/`, `.ufo/waves/round-13/`) as present when any tree entry lies beneath — 16 distinct tokens end in `/`.
7. Fleet check required, with the 5 fleet tokens above reported as `fleet`, not findings.
8. Exactly 3 exemption rows (2 if `.ufo/quarantine` is out of scope): `tests/vault/vadv54-run/p/p6repo/.git`, `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub`, `census/operator-sweep-20261019/`. `corpus/pointer-exemptions.tsv` does **not** exist at REV (`cat-file -e` rc 128), so it must be created by this round.
9. `census/round-17/gate-replays-ddb7347.json` (SKILL.md:163,165) and `census/round-17/jj-receipts-ddb7347.txt` (README:216) must be fixed in prose or committed as artifacts; no exemption row can honestly cover a missing evidence file.

## 5. Calibration note on the C2 counting claim

C2 states "281 tokens, 18 unresolved" from L1's sweep. That number is not reproducible without the unit (occurrence vs distinct) and the tokenizer/boundary rules; my independent measure over a **subset** of the cited files is 272 occurrences / 132 distinct / 23 lane-unresolved occurrences / 16 distinct. These are not in conflict — they are an underdetermined comparison. To make "findings before → 0 at the round tip" falsifiable, the round should pin the four counting rules in §1 (unit, boundaries, `../` normalisation, brace/wildcard handling) next to the count; otherwise a re-derivation cannot agree or disagree.

## 6. Verdict

- C2's core claim **holds in substance**: after fixing the two ddb7347 pointer families and recording 2–3 exemption rows, a correctly implemented gate has zero findings over these five files at the tip; the remaining 13 lane-unresolved distinct tokens are fleet (5, not findings) or grammar (6, skipped) or deliberate (3, exempted).
- The routed fix list is **incomplete by one citation**: `corpus/README.md:216` cites the missing `jj-receipts-ddb7347.txt` through a `../` link, which the routed R2 prose does not name; fixing only SKILL.md and the knowledge file leaves a dangling pointer.
- `partial` on gate readiness as specified: without brace/range expansion, `../` normalisation, folder resolution, fleet resolution and the exemptions file, the gate cannot reach 0 findings honestly.

## 7. Commands run (exact; outputs quoted above or in §3)

```
git -C <lane> show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:<SKILL.md|SCORECARD.md|PROVINCE.md|corpus/QUALITY.md|corpus/README.md>
git -C <lane> ls-tree -r --name-only b5763415cc67ecff1e8fe56c58c39a6fb106d7a3        # 2246 entries
git -C /home/vgpnk/Projects/shokunin ls-tree -r --name-only HEAD
git -C <lane> cat-file -e b576341:census/round-17/gate-replays-ddb7347.json            # rc 128
git -C <lane> cat-file -e b576341:census/round-17/jj-receipts-ddb7347.txt              # rc 128
git -C <lane> cat-file -e b576341:census/round-17/gate-replays-4f48343.json            # rc 0
git -C <lane> cat-file -e b576341:census/round-17/jj-receipts-4f48343.txt              # rc 0
git -C <lane> cat-file -e b576341:corpus/pointer-exemptions.tsv                        # rc 128
git -C <lane> rev-list --all --objects | grep ddb7347                                  # 1 line: commit ddb73474433977ff54b015ac3e77669ff2537353
git -C <lane> log -1 --format=%H\ %s ddb73474433977ff54b015ac3e77669ff2537353
git -C <lane> ls-files --others --exclude-standard census/round-17                     # none
git -C <lane> ls-files --others --exclude-standard census/operator-sweep-20261019      # 152 files
git -C <lane> ls-files --others --exclude-standard --directory .ufo/                   # .ufo/quarantine/, .ufo/waves/round-18/
```
Tokenisation/classification ran in this session's Python kernel over the five `git show` blobs; no files were written outside this report and no processes were started.

Probe-rule disclosure: one `git -C <lane> status --porcelain --untracked-files=all .ufo/quarantine` was issued while checking whether quarantine is ignored (read-only, empty output); it is outside the enumerated read-only allowlist. All other git calls are in the allowlist (`show`, `ls-tree`, `cat-file`, `ls-files`, `rev-list`, `log`). No jj invocation, no signals, no writes except this report.
