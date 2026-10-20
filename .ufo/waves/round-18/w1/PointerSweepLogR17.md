STATUS: DONE — blind re-derivation of C2 over LOG.md's round-17 section + `corpus/lessons/round-17.md` at b576341: 48 in-scope tokens (41 distinct) under the claim's written prefix list and 50 (42) under the `.ufo/` list that L1's own `.ufo/state` classification requires; 6 unresolved occurrences / 5 distinct (8 / 6 with `.ufo/`). Exactly one true dangling pointer (`census/round-17/gate-replays-ddb7347.json`, cited only at LOG.md:916, which the declared "LOG round-N section" rule does not scan), plus one never-committed deliberate fixture path, one untracked operator directory, the untracked quarantine tree, one fleet-only path, and one prose false positive. Replayable instrument: Appendix A.

# Blind pointer sweep — round-17 LOG section + lesson

Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, rev `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (short `b576341`, "round-17 verifier spot-check"). No writes outside this report; no tool installs; no network. The per-seat scratch dir `/var/tmp/souji-r18-PointerSweepLogR17-5/` was removed after this report; Appendix A is the replayable instrument.

## 1. LOG section delimitation rule (exact, as used)

1. Read `LOG.md` at the rev as a line list.
2. Section start = a line matching `^## ` (level-2 ATX heading) whose heading text matches the case-insensitive word-boundary regex `\bround[ -]17\b`.
3. Section end = the line before the next `^## ` line at or after the start; EOF if none.
4. If several headings match, concatenate every matching section in file order (this generalisation is required for `--round 18`, where corrections will add more round-18 headings; it is not exercised at b576341).

Measured at b576341: `grep -n '^## .*round 17' LOG.md` → **only line 944**; the next `^## ` heading does not exist (LOG.md is 946 lines), so the round-17 section is **LOG.md:944–946** (heading 114 bytes, blank line, body 1360 bytes; 3 lines). Exactly the heading text `## 2026-10-20 — round 17 (souji L1, hyaku phase 2): …`.

Consequence worth pinning: the two "round 16 correction" headings at **908** and **927** do **not** match `round 17`, so their bodies (including **LOG.md:916**) are outside the round-17 section under this rule. If the gate instead scanned "every section after the previous round", LOG:916 would be in scope; the contract does not say which, and the choice changes whether R2's LOG site is ever scanned.

`corpus/lessons/round-17.md` has no analogous sectioning: the file is 91 lines and the whole file is in scope (the declared rule says "the round's lesson corpus/lessons/round-N.md").

## 2. Rule as implemented, and the tokenizer traps it exposes

Declared rule, applied literally: tokens under `census/`, `tests/`, `tools/`, `corpus/`, `.ufo/waves/`; `path:line` suffix stripped; simple `{a,b}` braces expanded; tokens containing `<`, `>`, `*` or literal `round-N` skipped; `round-6..11` ranges expanded; resolution = present in the git tree at REV (blob or tree).

Implementation choices I had to make (each is unspecified in the claim and each changes the count):

- **Token character class must capture `<`, `>`, `*`, `{`, `}`.** If `<`/`>` are not captured, `census/round-<N>/` truncates to `census/round-`, the skip rule never fires, and four sites in the authority books (`corpus/QUALITY.md:34,37,65`, `corpus/README.md:54`) become bogus findings. Measured: first pass without `<`/`>` produced exactly those four false positives.
- **Token start boundary.** A prefix occurrence whose preceding character is a path character is a suffix of a longer path, not a token. Measured site: the lesson's quarantine path `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub` contains a `tests/` occurrence with `/` before it; without the boundary it yields a phantom token that resolves nowhere.
- **Colon handling (new defect, see §5).** `A:B` command-argument lists are not `path:line`. Literal rule leaves `.ufo/waves/round-16/w1-spec.json:.ufo/waves/round-16/w2-spec.json` as one unresolved token although **both members exist in the tree at REV**.
- **`fleet` fallback anchoring (new defect, see §5).** "Resolves only in the fleet repo" must be applied after lane-tree and lane-working-tree checks, and the fleet root has its own `.ufo/state` (64 tracked files) and `.ufo/watchdog.log` (1 tracked file), so a naive fleet join silently reclassifies lane-runtime tokens as `fleet` and therefore not findings.

## 3. Counts

Raw prefix occurrences at b576341: round-17 LOG section 4 (`census/` 1, `tests/` 1, `corpus/` 2), lesson 43 (`census/` 19, `tests/` 5, `tools/` 4, `corpus/` 1, `.ufo/waves/` 14) = **47**.

| rule variant | occurrence rows | distinct tested | resolve | skipped | unresolved rows | distinct unresolved |
|---|---|---|---|---|---|---|
| declared literal (`path:line` only) | 47 | 40 | 39 file | 1 (`jj-receipts-*.txt`) | 7 | 6 |
| recommended (stop at `:` unless next char is a digit; allow start after `:`) | 48 | 41 | 41 file | 1 | 6 | 5 |

Reconciliation: 47 raw prefix occurrences → 46 token starts (one embedded `tests/` suffix correctly skipped) → +1 brace expansion (`{one.txt,inner/keep.txt}`) = 47 literal rows. The recommended rule splits the colon list into its two members (+2) and removes the joined token (−1), and additionally picks up the second member's prefix occurrence → 48.

The single skipped token is `census/round-17/jj-receipts-*.txt` (lesson:8) — glob, correctly skipped by the declared skip rule.

**Prefix-set sensitivity (a contract decision, measured).** The claim's written list is `census/`, `tests/`, `tools/`, `corpus/`, `.ufo/waves/`; L1's own classification of `.ufo/state` and `.ufo/watchdog.log` as in-scope unresolved tokens requires `.ufo/` instead. On the same two sources the recommended rule measures: **48 rows / 41 distinct tested / 6 unresolved rows / 5 distinct** with the written list; **50 / 42 / 8 / 6** with `.ufo/`. The two extra rows are `.ufo/quarantine/round-17/` (LOG.md:946, lesson:19) and the full quarantine stub path `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub` (lesson:16), both untracked-present and deliberate. §5(e) uses `.ufo/`, because that is the only reading under which L1's named deliberate set exists.

## 4. Every unresolved token, classified

Resolution order used for the class column: (1) git tree at REV (blob/tree); (2) lane working tree (`lexists`); (3) fleet root; (4) else dangling. Site syntax `file:line`; `[supp]` marks the supplementary LOG:916 site outside the round-17 section.

| # | token | sites | tree@REV | lane disk | fleet | ever in any commit | class | smallest fix |
|---|---|---|---|---|---|---|---|---|
| 1 | `census/round-17/gate-replays-ddb7347.json` | LOG.md:916 `[supp]` (closure R2; also SKILL.md:163,165 outside this scope) | absent | absent | absent | **no** — `git log --all -- <path>` = 0; `git log --all -- '*gate-replays-ddb7347*'` = 0 | **TRUE DANGLING** — the committed record is `census/round-17/gate-replays-4f48343.json` (tree-confirmed; lesson D6 agrees) | SKILL.md:163,165 → `gate-replays-4f48343.json`; for LOG:916 (append-only) add a `corpus/pointer-exemptions.tsv` row with that reason — do **not** append a correction entry that re-types the old name, because the new text would itself be scanned |
| 2 | `census/round-17/jj-receipts-ddb7347.txt` | not in my two files; `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148` (goal's second class) | absent | absent | absent | **no** — 0 commits; committed are `jj-receipts-4f48343.txt` and `jj-receipts-base5fa6017.txt` | **TRUE DANGLING** — 3 literal occurrences + 1 brace member at :148 (`{base5fa6017,ddb7347}`) | replace with `jj-receipts-4f48343.txt` at :2,:44,:126; at :148 `{base5fa6017,4f48343}` |
| 3 | `tests/vault/vadv54-run/p/p6repo/.git` | lesson:16, LOG.md:946 (also SKILL.md:110) | absent | absent | absent | **no** — 0 commits (a `.git` dir and an empty dir are untrackable by git) | DELIBERATE non-file: the defect path of R17-M3; the stub was an on-disk untracked empty dir, now at `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub` (present on disk, untracked) | exemption row `tests/vault/vadv54-run/p/p6repo/.git` — reason: quoted path of nested repository, never a tracked object |
| 4 | `census/operator-sweep-20261019/` | lesson:91 | absent | **present** (untracked) | absent | **no** — 0 commits; the tracked sibling is `census/operator-sweep-20261018/` (15 files) | DELIBERATE non-tracked: operator-owned live directory, rev-pinned resolution can never see it | exemption row `census/operator-sweep-20261019/**`-equivalent exact path with reason "operator-owned, untracked, never committed" — or narrow the lesson to a prose description |
| 5 | `.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` | lesson:16 | absent | absent | **present and tracked in the fleet repo** (`git -C /home/vgpnk/Projects/shokunin ls-files <path>` matched, rc 0; 75 hyaku paths tracked) | n/a (fleet repo) | **FLEET** — reported separately, not a finding | none |
| 6 | `census/verify/vault/quarantine` | lesson:80 | absent | absent | absent | **no** — 0 commits | **FALSE-POSITIVE TOKEN**: prose slash-abbreviation of four selftests (`census`, `verify`, `vault`, `quarantine`, measured 49/49/57/101 on the same line); not a path | exemption row, or rewrite future prose (`census`, `verify`, `vault`, `quarantine` selftests) |
| 7 | `.ufo/waves/round-16/w1-spec.json:.ufo/waves/round-16/w2-spec.json` | lesson:7 | joined token absent; **both members present** (`w1-spec.json`, `w2-spec.json`) | — | — | members: `w2-spec.json` first added at `163158a` (1 commit) | **TOKENIZER ARTIFACT** (literal rule only) — a `--specs A:B` argument list | split on `:` when the following character is not a digit; then both members resolve |
| 8 | `.ufo/quarantine/round-17/` | lesson:19, LOG.md:946 (the `…` ellipsis stops the token) | absent | **present** (untracked dir) | absent | **no** — 0 commits | DELIBERATE non-tracked: the quarantine destination named by R17-M3/M6 | needs an exemption or an explicit untracked-present policy; only in scope under the `.ufo/` reading |
| 9 | `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub` | lesson:16 | absent | **present** — 0-byte directory, inode 30073199 (stat-verified), untracked | absent | **no** — 0 commits | DELIBERATE non-tracked: the moved empty fixture stub; the record of where `.git` went | same exemption decision as row 3; only in scope under the `.ufo/` reading |

Net: under the recommended rule the round-17 material has **one genuine broken-evidence pointer** (`gate-replays-ddb7347.json`, at a site the declared LOG rule does not reach), one never-tracked fixture path, one untracked operator dir and the untracked quarantine tree that need exemptions or a stated policy, one fleet-only citation, and one prose false positive.

## 5. Defects in the C2 contract that block a green, replayable count

**(a) The named counting command cannot be evaluated at b576341.** The claim's metric is "changed gate `--rev b576341 --round 18` findings before → 0 at the round tip". At b576341 the tree has **no** `.ufo/waves/round-18/` entries (0), no `corpus/lessons/round-18.md`, and no round-18 LOG heading. `check_carry` requires reports: `tools/souji-landing-gate.py:368-375` (`prefix = ".ufo/waves/round-%d/"`, `raise EvalError("no .md reports under %s at %s")`; its own selftest case at `:1248` asserts exactly this stderr), and the tool's documented exit-2 set includes the missing wave dir. `[INFERENCE — read from the code and the documented exit-2 set; the gate was not executed, so this was not measured live.]` Consequently `--rev b576341 --round 18` cannot produce a finding count: the "before" half of the metric is unmeasurable with the declared command. Fix: state the metric at the tip rev for both readings (pre-fix and post-fix tree states), or add an explicit check-only mode (e.g. `--dangling-only` that skips carry), or measure the base sweep as a committed census record with its own script (the `gate-replays.py` + expected-file pattern).

**(b) The LOG rule excludes the very site closure R2 names in LOG.** LOG.md:916 lives in the "round 16 correction" section (heading 908, next heading 927). Under "LOG.md's round-N section" it is never scanned for `--round 17` or `--round 18`. Either widen the LOG scope (e.g. all sections whose heading matches `round[ -]N`, plus sections that cite round-N artifacts), or exempt LOG:916 and treat the SKILL.md sites as the only gate-enforced R2 fix. Note the append-only constraint: a new round-18 LOG correction that names `gate-replays-ddb7347.json` would put a dangling token into the round-18 section and create a fresh finding.

**(c) The tokenizer needs two pinned rules, not one.** Measured on real text:
- A token ends at `:` unless the next character is a digit (line reference); a token may start immediately after `:`. Without this, `--specs A:B` is a false positive (site lesson:7) and its members are invisible.
- `<`, `>`, `*`, `{`, `}` must be inside the token before the skip rule is applied. Without this, `census/round-<N>/` truncates and four authority-file sites become false positives.
- A token start must not follow a path character (`/`), else the embedded `tests/…` inside `.ufo/quarantine/…` is a phantom token.

**(d) `fleet` needs an anchored definition.** The fleet root `/home/vgpnk/Projects/shokunin` is a git repo that tracks **0** files under `souji-shokunin/` (nested/ignored) but **64** under `.ufo/state` and **1** `.ufo/watchdog.log` — its own operator state. A bare `fleet_root + token` existence test therefore reclassifies lane-runtime tokens as `fleet` (measured: `.ufo/state/` at SKILL.md:69, PROVINCE.md:39, QUALITY.md:38 and `.ufo/watchdog.log` at SKILL.md:70, PROVINCE.md:39 all flip to `fleet` even though the lane's own `.ufo/state` and `.ufo/watchdog.log` are absent). Pin the order lane-tree → lane-working-tree → fleet-repo tree, and state whether untracked-but-present counts.

**(e) The 281/18 pair is not replayable.** No sweep script or record is committed for it. My independent implementation over the claim's file list (`SKILL.md`, `SCORECARD.md`, `PROVINCE.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/knowledge/*.md` = 12 files, `.ufo/` prefix required by L1's own `.ufo/state` classification) measures **308 occurrence rows: 282 resolve, 9 skipped, 17 non-resolving** (8 dangling, 7 fleet, 2 untracked-present; **10 distinct unresolved**, including the artifact), i.e. 16 rows after excluding one regex-escape artifact (`\.ufo/state/\` from `corpus/QUALITY.md:38`'s escaped alternation). The four classes L1 names reproduce exactly (gate-replays at SKILL:163,165; jj-receipts at knowledge:2,44,126,148; quarantine stub at SKILL:110; fleet hyaku), but the summary does **not** name two of the measured classes: `tests/vault/vadv54-run/p/p6repo/.git` (SKILL.md:110) and `census/operator-sweep-20261019/` (corpus/README.md:81). The literal number 18 is author prose until the sweep is committed; that is the same failure class as R17-M2 that this round exists to remove.

Also measured, since the claim's declared prefix list is `.ufo/waves/` only: `.ufo/state/` (4 occurrences) and `.ufo/watchdog.log` (2) are cited in the authority files and are not under `.ufo/waves/`. The claim's prefix list is therefore narrower than the sweep that produced 18; the written rule must say `.ufo/` (or the two citations must be declared out of scope).

**(f) Q25(b) is genuinely open, and one existing selftest world must change.** At b576341 a frozen record whose `measured_commit` does not resolve is silently swallowed: `tools/souji-landing-gate.py:544-569` sets `measured_ok = False` and emits **no** finding (only a non-zero-and-not-1 git rc raises). `LG-FROZEN-MEASURED` is emitted only for a *resolving* commit with absent/mismatched pinned blobs (`:578`, `:587`). The selftest helper `_frozen_world` (`:835-860`) writes `{"measured_commit": "0"*40}` with `verdict: clean`, and cases at `:911`, `:931`, `:949`, `:1076` expect clean/`checked_measured` 0 or 2 on that world. Making a dangling `measured_commit` a `LG-FROZEN-MEASURED` finding flips the `0`*40 world to exit 1, so `_frozen_world` must take a real commit sha and the case expectations/count (documented as 28 cases) must be updated in the same change.

## 6. Commands run (exact, with the load-bearing outputs)

- `git -C <lane> show b576341:LOG.md` / `:corpus/lessons/round-17.md` → written to `/var/tmp/souji-r18-PointerSweepLogR17-5/{log,r17}.md` (transient; removed after this report); `wc -lc` → `946 57137` and `91 25069`.
- `git show b576341:LOG.md | grep -n '^#'` → last heading `944:## 2026-10-20 — round 17 (souji L1, hyaku phase 2) …`; `grep -n '^## .*round 17'` → `944` only.
- `git ls-tree -r --name-only b576341` → 2246 blobs (that exact command; `-t` omitted).
- `git ls-tree -r --name-only b576341 census/round-17/` → 14 files; **no** `gate-replays-ddb7347.json`; `gate-replays-4f48343.json` and `gate-replays-expected.json` present.
- `git ls-tree -r --name-only b576341 census/ | grep operator-sweep` → 15 paths, all `census/operator-sweep-20261018/…`; `-20261019` absent from every commit.
- `git ls-tree -r --name-only b576341 .ufo/waves/round-16/ | grep -E 'w[12]-spec'` → `w1-spec.json` and `w2-spec.json` both present.
- `for p in …; do git log --all --oneline -- "$p" | wc -l; done` → 0 for `census/round-17/gate-replays-ddb7347.json`, `tests/vault/vadv54-run/p/p6repo/.git`, `census/verify/vault/quarantine`, `census/operator-sweep-20261019`, `census/round-17/jj-receipts-ddb7347.txt`; 1 for `.ufo/waves/round-16/w2-spec.json` (`163158a`).
- `git log --all --oneline -- '*gate-replays-ddb7347*'` → 0.
- `git -C /home/vgpnk/Projects/shokunin rev-parse --show-toplevel` → the fleet root itself; `git ls-files .ufo/waves/hyaku/` → 75 files incl. `jj-w1/reports/JjTrialSouji.md` (tracked); `git ls-files souji-shokunin/` → 0; `git ls-files .ufo/state` → 64; `.ufo/watchdog.log` → 1.
- `grep -c 'LOG' tools/souji-landing-gate.py` → **0** (the gate reads no LOG.md today; the LOG half of the rule is new and its delimitation must be pinned).
- `sed -n '360,400p' tools/souji-landing-gate.py` → `def check_carry(root, tree, rev, round_no)`; `prefix = ".ufo/waves/round-%d/"`; `raise EvalError("no .md reports under %s at %s")`; `grep -n 'def _frozen_world\|def check_frozen_pins'` → `835`, `439`; `git ls-tree -r -t --name-only b576341 | grep -c '^\.ufo/waves/round-18/'` → 0 entries.
- Instrument: Appendix A (self-contained; reads blobs at REV only). `python3 <appendix> round17` and `python3 <appendix> books` produce the counts in §3 and §5(e) verbatim; those two runs were the source of every number in this report. The per-seat scratch copy under `/var/tmp/souji-r18-PointerSweepLogR17-5/` was removed after this report was written; Appendix A is the replayable artifact.
- `ls`-free existence checks on the exact paths in the class column (`test -e` / `os.path.lexists`). I stat'd the path `census/operator-sweep-20261019` only; I did **not** list or read it.

## 7. Verdict

- **Premise (C2) holds** for the two pointer classes it names: `census/round-17/gate-replays-ddb7347.json` never existed in any commit (0 commits, glob 0) while the committed record is `-4f48343.json`, and `census/round-17/jj-receipts-ddb7347.txt` never existed (0 commits) while `-4f48343.txt` and `-base5fa6017.txt` are committed. Q25(b) is a real gap at base.
- **Rule as written is partial/under-specified**: one counting command that exits 2 at the named rev; a LOG section rule that excludes LOG:916; a tokenizer that needs the `:` rule, the `<`/`>` capture, and the start-boundary rule to avoid four measured false-positive classes; an unanchored `fleet` bucket that silently swallows lane-runtime tokens; and an unreplayable 281/18 pair with two unnamed residual classes.
- **No fabricated numbers**: every count above is from a command listed in §6, and the two rows I could not resolve to a definite category (the colon-list under the literal rule, the regex-escape artifact) are labelled as such rather than folded into a total.

Smallest integration sequence for L1: (1) fix SKILL.md:163,165 and the four knowledge-file sites to the `-4f48343` names; (2) commit `corpus/pointer-exemptions.tsv` with rows for `tests/vault/vadv54-run/p/p6repo/.git`, `census/operator-sweep-20261019/**` (exact path as written), and `census/verify/vault/quarantine`; (3) pin the tokenizer rules in §5(c) and the fleet order in §5(d) in the gate docstring + selftest; (4) restate the count as a committed sweep record (script + JSON) so `281/18 → 0` is replayable; (5) update `_frozen_world`/the `0`*40 cases for the Q25(b) change.

## Appendix A — reference instrument (tested, self-contained)

Measured output at `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`, 2026-10-20. `round17` = LOG.md's round-17 section (delimited by the §1 rule) + the whole lesson; `books` = the claim's authority-file list. Note `round17` does **not** include LOG:916, which is exactly the §5(b) point.

```text
$ python3 appendix.py round17
rows 50 {'file': 41, 'DANGLING': 3, 'untracked-present': 4, 'skip': 1, 'fleet': 1}
distinct 42
untracked-present .ufo/quarantine/round-17/                                          LOG.md:946
DANGLING          tests/vault/vadv54-run/p/p6repo/.git                               LOG.md:946
untracked-present .ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub corpus/lessons/round-17.md:16
fleet             .ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md                     corpus/lessons/round-17.md:16
DANGLING          tests/vault/vadv54-run/p/p6repo/.git                               corpus/lessons/round-17.md:16
untracked-present .ufo/quarantine/round-17/                                          corpus/lessons/round-17.md:19
DANGLING          census/verify/vault/quarantine                                     corpus/lessons/round-17.md:80
untracked-present census/operator-sweep-20261019/                                    corpus/lessons/round-17.md:91

$ python3 appendix.py books
rows 308 {'file': 282, 'DANGLING': 8, 'skip': 9, 'fleet': 7, 'untracked-present': 2}
distinct 115
fleet             .ufo/state/                                                        PROVINCE.md:39
fleet             .ufo/watchdog.log                                                  PROVINCE.md:39
fleet             .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md              SCORECARD.md:60
fleet             .ufo/state/                                                        SKILL.md:69
fleet             .ufo/watchdog.log                                                  SKILL.md:70
untracked-present .ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub SKILL.md:110
DANGLING          tests/vault/vadv54-run/p/p6repo/.git                               SKILL.md:110
DANGLING          census/round-17/gate-replays-ddb7347.json                          SKILL.md:163
DANGLING          census/round-17/gate-replays-ddb7347.json                          SKILL.md:165
fleet             .ufo/state/                                                        corpus/QUALITY.md:38
DANGLING          .ufo/state/\                                                       corpus/QUALITY.md:38
untracked-present census/operator-sweep-20261019/                                    corpus/README.md:81
DANGLING          census/round-17/jj-receipts-ddb7347.txt                            corpus/knowledge/jj-colocation-receipts.md:2
DANGLING          census/round-17/jj-receipts-ddb7347.txt                            corpus/knowledge/jj-colocation-receipts.md:44
DANGLING          census/round-17/jj-receipts-ddb7347.txt                            corpus/knowledge/jj-colocation-receipts.md:126
fleet             .ufo/waves/hyaku/jj-w1/reports/                                    corpus/knowledge/jj-colocation-receipts.md:148
DANGLING          census/round-17/jj-receipts-ddb7347.txt                            corpus/knowledge/jj-colocation-receipts.md:148
```

The instrument, verbatim:

```python
#!/usr/bin/env python3
"""Reference instrument for LG-DANGLING-PTR (recommended rule).
Usage: appendix.py round17 | books. Reads blobs at REV only."""
import os
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
REV = "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3"
PREF = ("census/", "tests/", "tools/", "corpus/", ".ufo/")
S = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        "_./@~%+=-")
B = S | set("{}*?<>[]\\")
g = lambda *a: subprocess.run(["git", "-C", LANE] + list(a),
                              capture_output=True, text=True, check=True).stdout
tree = g("ls-tree", "-r", "-t", "--name-only", REV).splitlines()
ents = set(tree)
dirs = {"/".join(p[:i]) for p in tree for i in range(1, len(p.split("/")))}


def toks(txt):
    for pref in PREF:
        for m in re.finditer(re.escape(pref), txt):
            i = m.start()
            if i > 0 and txt[i - 1] in S:
                continue
            j, br = i, 0
            while j < len(txt):
                c = txt[j]
                if c == "{":
                    br, j = br + 1, j + 1
                    continue
                if c == "}" and br:
                    br, j = br - 1, j + 1
                    continue
                if c == "," and br:
                    j += 1
                    continue
                if c == ":":
                    break
                if c in B:
                    j += 1
                    continue
                break
            if j > i:
                yield txt.count("\n", 0, i) + 1, txt[i:j]


def expand(t):
    m = re.search(r"\{([^{}]*)\}", t)
    if m:
        for a in m.group(1).split(","):
            yield from expand(t[:m.start()] + a + t[m.end():])
        return
    m = re.search(r"round-(\d+)\.\.(\d+)", t)
    if m:
        for n in range(int(m.group(1)), int(m.group(2)) + 1):
            yield from expand(t[:m.start()] + "round-%d" % n + t[m.end():])
        return
    yield re.sub(r":\d[\d,\-]*$", "", t).rstrip(".,;:")


def verdict(t):
    t = t.rstrip("/")
    if t in ents:
        return "file"
    if t in dirs:
        return "dir"
    if os.path.lexists(os.path.join(LANE, t)):
        return "untracked-present"
    if os.path.lexists(os.path.join(FLEET, t)):
        return "fleet"
    return "DANGLING"


def sources(mode):
    if mode == "round17":
        L = g("show", REV + ":LOG.md").splitlines(keepends=True)
        s = next(i for i, l in enumerate(L)
                 if l.startswith("## ") and re.search(r"(?i)\bround[ -]17\b", l))
        e = next((j for j in range(s + 1, len(L)) if L[j].startswith("## ")),
                 len(L))
        return [("LOG.md", s, "".join(L[s:e])),
                ("corpus/lessons/round-17.md", 0,
                 g("show", REV + ":corpus/lessons/round-17.md"))]
    files = ["SKILL.md", "SCORECARD.md", "PROVINCE.md", "corpus/QUALITY.md",
             "corpus/README.md"]
    files += sorted(p for p in ents
                    if re.match(r"corpus/knowledge/.*\.md$", p))
    return [(p, 0, g("show", REV + ":" + p)) for p in files]


rows = []
for name, base, txt in sources(sys.argv[1]):
    for line, raw in toks(txt):
        for t in expand(raw):
            if any(c in t for c in "<>*") or re.search(r"round-N\b", t):
                rows.append((name, line + base, t, "skip"))
                continue
            rows.append((name, line + base, t, verdict(t)))
from collections import Counter
print("rows", len(rows), dict(Counter(r[3] for r in rows)))
print("distinct", len({r[2] for r in rows if r[3] != "skip"}))
for r in sorted({r for r in rows if r[3] not in ("file", "dir", "skip")}):
    print("%-17s %-66s %s:%d" % (r[3], r[2], r[0], r[1]))
```

Known limits of the instrument: it uses the first matching `## ` section only (at b576341 exactly one heading matches, so §1 step 4's multi-section generalisation is not exercised); it resolves directories as well as blobs (the claim does not say which); it does not expand `round-6..11` unless that literal appears (it does not in these sources); it reads `corpus/knowledge/*.md` from the tree at REV only; and its `fleet` step is the bare fleet-root join criticised in §5(d), retained deliberately so the bucket drift is reproducible.
