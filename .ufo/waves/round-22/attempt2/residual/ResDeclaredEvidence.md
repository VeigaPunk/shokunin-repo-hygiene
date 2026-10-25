STATUS: PARTIAL

# ResDeclaredEvidence — residual attack on the landed C1 declared-evidence instrument

Scope: the landed bytes at the lane tip, read from commits only. Read-only; no writes outside
this report and `residual/evidence/ResDeclaredEvidence-*`. No tool installs were performed.

Claim under attack (frozen, `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/preregistration.txt`):
C1 — every machine-checkable assertion in `SCORECARD.md` (frozen classes A/B/C) resolves at the
measured revision. Counter: `python3 -B tools/souji-declared-evidence.py --root . --file
SCORECARD.md --rev <REV> --format counts` → `assertions=N resolved=R skipped=S mismatches=M`,
exit 0 iff M == 0.

## 1. Tip pinning (the tip moved during the attack)

`/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state
/home/vgpnk/Projects/shokunin/souji-shokunin` was sampled four times and reported four different
tips while sibling seats were landing:

```
1st: branch=master local=ee1aef2b87e35923859b3e1b84ae09ca56d1d289 remote=same head=detached
2nd: local=c9f1fe3caf642dfe3a9e00de94caf1d4bf86503f  (same)
3rd: local=7bc458c1e1dcf3396e9d65bc68aeae5de78609c4  (same)
4th: local=868075547dcd9b101e055481be89b2e97a38c5c9  (same)  <-- verdict measured here
5th: local=9fcc4f78fc5d01a4e405b58a21af6a7666a5613e  (same)  <-- post-write re-check
```

Post-write re-check at `9fcc4f78`: `assertions=62 resolved=62 skipped=39 mismatches=0`, exit 0 —
`M_after = 0` still holds, and the `62/62/39` literals are unchanged, so every number below
reproduces at the newest tip as well. The verdict is pinned to `8680755` because that is where the
full matrix (including the base run) was taken.

All verdicts below are against committed bytes at `868075547dcd9b101e055481be89b2e97a38c5c9`
(hereafter `8680755`), which is `master` = `origin/master` = detached `HEAD`, `ahead=0 behind=0`.
The worktree was dirty throughout (`tracked=5 untracked=5`, sibling edits); nothing in this report
was read from worktree bytes except the tool, which I re-extracted per revision and verified
byte-identical by sha256. `census/operator-sweep-20261019/` was present untracked and was NOT read
(contract exclusion).

The instrument is byte-stable across every revision sampled, and the digest pinned in the round
reproduces:

```
$ git show 8680755:census/round-22/attempt2/instrument-digests.txt
65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4  tools/souji-declared-evidence.py
5b8025a83f16957cb2ff6aca0adecfc3a6a1ff796c3eed1d70018ecc339b3062  tools/souji-gate-check.py
round=22 attempt=2 date=2026-10-25 lane_tip=f8f0b4a2c4ab3d16369413b6aa9f2d2c08590581
$ for R in 4a6ee90 8990ae4 c9f1fe3 7bc458c 8680755; do git show $R:tools/souji-declared-evidence.py | sha256sum; done
65817d0d…  (all five identical)
```
`inferred`: the "same instrument, both ends" claim in the calibration row is true; the digest pin
is honest. `lane_tip=f8f0b4a…` in that same receipt is stale (see finding L3).

## 2. The two canonical runs at the final tip

```
$ python3 -B tools/souji-declared-evidence.py --selftest          # tool@8680755
PASS fixture1 all-good -> 0 [assertions=2 resolved=2 skipped=0 mismatches=0]
PASS fixture2 absent path -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture3 dangling rev -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture4 wrong digest -> mismatch [assertions=3 resolved=2 skipped=0 mismatches=1]
PASS fixture5 path only at other rev -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture6 correct digest -> resolved [assertions=3 resolved=3 skipped=0 mismatches=0]
PASS control always-zero -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
PASS fixture7 command span -> skipped, not asserted [assertions=0 resolved=0 skipped=1 mismatches=0]
selftest=8/8
exit 0

$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev 8680755… --format counts
assertions=62 resolved=62 skipped=39 mismatches=0
exit 0
```

Base / named-tip / final-tip, tool@8680755 (`evidence/ResDeclaredEvidence-counts-matrix.txt`):

```
decl@4edb25d  exit=1 assertions=55 resolved=52 skipped=33 mismatches=3
decl@5fdd5d5  exit=0 assertions=60 resolved=60 skipped=38 mismatches=0
decl@8990ae4  exit=0 assertions=62 resolved=62 skipped=39 mismatches=0
decl@7bc458c  exit=0 assertions=62 resolved=62 skipped=39 mismatches=0
decl@8680755  exit=0 assertions=62 resolved=62 skipped=39 mismatches=0
```

**The row's literals reproduce exactly at the final tip.** Calibration row at `8680755` says
`base 4edb25d… assertions=55 resolved=52 skipped=33 mismatches=3; tip 8990ae4… assertions=62
resolved=62 skipped=39 mismatches=0` — both match, and `M_after = 0` also holds at the actual final
tip `8680755` (the row names `8990ae4`, three commits earlier; identical counts). The do-nothing
control required by the kill rule scores `M = 3` at base, not 0. Target met.

## 3. Forced-false-green attacks (throwaway repo `/var/tmp/sde-fx`, git-init'd and removed after the run; tool copies byte-identical to the committed tool; full transcript in `evidence/ResDeclaredEvidence-attacks.txt`)

| # | attack | observed counts line | exit | verdict |
|---|---|---|---|---|
| a | repo-relative declaration absent at `--rev`, worktree copy present (`--file decl.md --rev 91cb9e4`) | `declaration is not present at 91cb9e4efaac…: decl.md` | 1 | **killed** — no worktree fallback |
| b | uppercase 64-hex **wrong** digest on `tools/present.sh` | `assertions=3 resolved=2 skipped=1 mismatches=1` | 1 | **killed** |
| b2 | uppercase 64-hex **correct** digest (control) | `assertions=3 resolved=3 skipped=1 mismatches=0` | 0 | correct — lowercase normalisation works |
| c | path token with a trailing period, `` `tools/absent.sh.` `` | `assertions=1 resolved=1 skipped=1 mismatches=0` | 0 | **survives (green)** — out of the frozen enum, see L4 |
| d | glob whose `*` would cross `/`: `` `census/*/foo.md` `` with only `census/round-22/a/foo.md` | `assertions=2 resolved=1 skipped=0 mismatches=1` | 1 | **killed** — `_segmatch` is per-segment |
| d2 | control: `` `census/*/*/foo.md` `` (real depth) | `assertions=2 resolved=2 skipped=0 mismatches=0` | 0 | correct positive |
| e1 | `` `ac71bfc:later.md` `` (valid rev, path present) | `assertions=2 resolved=2 skipped=0 mismatches=0` | 0 | correct positive |
| e2 | `` `91cb9e4:later.md` `` (path only at the other rev) | `assertions=2 resolved=1 skipped=0 mismatches=1` | 1 | **killed** |
| e3 | `` `deadbeefdeadbeef:tools/present.sh` `` (unresolved rev) | `assertions=2 resolved=1 skipped=0 mismatches=1` | 1 | **killed** |
| f | EXTRA: dangling rev `deadbeef…` inside a compound backticked command, cell also names `census/round-22` | `assertions=1 resolved=1 skipped=1 mismatches=0` | 0 | **survives (FALSE GREEN, in-enum)** — H1 |
| h | EXTRA: sha256 in a cell with two backticked paths | `assertions=3 resolved=3 skipped=1 mismatches=0` | 0 | out of enum (class C requires exactly one path) — named limit, correct |
| l | EXTRA: uppercase 7-hex inside a context-carrying span, `` measured commit `AC71BFC` `` | `assertions=1 resolved=1 skipped=1 mismatches=0` | 0 | correct resolution, but same token is also counted in `skipped` — L2 |

## 4. Findings

### H1 — HIGH, still open: class-B tokens inside a compound backticked span are never measured (in-enum false green)

`classify()` blanks every backticked span that is not *pure* hex before the class-B/C cell scan
(`tools/souji-declared-evidence.py`, `scan = SPAN_RE.sub(... else " ", cell)`). A revision named
inside a compound span — the normal shape for a quoted command, `git show <sha>:<path>` — is
therefore erased before `HEX_B_RE` sees it. The frozen class B does not exclude that shape: it
names "a bare hex token of length 7..40 inside a table cell that also names a revision context …
or a `census/round-<N>/` path in the same cell".

Proof (executed, fixture f): a cell containing
`` `git show deadbeefdeadbeefdeadbeefdeadbeefdeadbeef:census/round-22/a/foo.md \| python3 -B x.py`; see census/round-22 at ac71bfc ``
prints `assertions=1 resolved=1 skipped=1 mismatches=0`, **exit 0**, with a non-existent revision.
The frozen enum requires that token to be asserted (and it would be a mismatch).

This is not hypothetical on the real file: at base `4edb25d` the token
`41553adb139d06511dc386bb3ce4326aebfba675` (a real commit, `round-21: final zero-finding gate and
scoped cleanup receipts`, named as `base: git show 41553adb…:census/round-21/run-acceptance.py \|
python3 …`) sits in a cell whose context is `CENSUS=True` and inside a compound span. Under the
scanner that shipped before `4a6ee90` it was asserted; the landed scanner drops it. It resolves,
so `M_before=3` is unaffected, but the enumeration is short:

```
pinned tool      base 55 / 52 / 33 / 3      tip 62 / 62 / 39 / 0
hex-retained     base 60 / 57 / 35 / 3      tip 66 / 66 / 40 / 0
tokens only the pinned tool drops (evidence/ResDeclaredEvidence-dropped-tokens.txt):
  base 14 41553adb139d…  B       <- command form, no class-A fallback, unmeasured
  base 58 4f48343 B, 61 4800fd7 B, 62 4800fd7 B, 101 63bb887 B
  tip  63 4f48343 B, 66 4800fd7 B, 67 4800fd7 B, 110 63bb887 B
```
`inferred`: the four `tip` tokens are revision stamps embedded in census *filenames*
(`census/round-17/c1-matrix-4f48343.json`, …). Those files are still asserted as class-A paths and
resolve at the tip, so their evidence role is checked even though the class-B reading is not
enumerated; whether a stamp inside a filename is a "bare hex token" is genuinely ambiguous and the
round should say which reading it intends. The command-form token (`41553adb…`, and fixture f) has
no such fallback and is simply unmeasured.

Consequence for the claim: `M_after = 0` is true at the tip even over the wider enumeration (I
checked all four dropped tokens resolve), so the conclusion survives; what does not survive is the
instrument's ability to falsify — a future stale revision written in command form prints green.

### H2 — HIGH, fixed mid-flight (recorded, not a round-1 restatement): stale base literal and an impossible set delta

At the revisions I first sampled (`ee1aef2`, `c9f1fe3`) the row quoted
`Base 4edb25dfe…: assertions=56 resolved=53 skipped=33 mismatches=3` and
"5 base tokens retired, 6 added". Measured then:

```
tool@ee1aef2 x 4edb25d -> assertions=56 resolved=53 skipped=33 mismatches=3   (the literal)
tool@4a6ee90 x 4edb25d -> assertions=55 resolved=52 skipped=33 mismatches=3   (the landed scanner)
delta base->5fdd5d54 and base->c9f1fe3 with tool@ee1aef2: 7 retired / 8 added distinct tokens
                                                         7 retired / 11 added assertions
```
So the base literal was reproducible only with the superseded scanner that was replaced by
`4a6ee90` four commits before the final tip, and "5 retired / 6 added" matched no convention at
any revision (net +4 requires 11 added assertions − 7 retired). **Both are fixed at `8680755`**:
the row now quotes `55/52/33/3` (verified exact) and says the multiset delta "is not claimed".
Nit: with the instrument pinned the delta is *revision*-dependent, not instrument-dependent, and it
is determinate; declining to claim it is fine, the stated reason is not.

### M1 — MEDIUM, still open: declaration provenance is bypassable, so the green line does not certify `SCORECARD.md` at the rev

`read_declaration()` falls back to reading an **absolute** `--file` from disk (`if
os.path.isabs(relfile)`), against any `--root`. Attack (a) proves the repo-relative guard works;
the absolute form defeats it:

```
$ ... --root . --file /var/tmp/doctored.md --rev 8680755…      # 2-line file naming `SCORECARD.md`
assertions=2 resolved=2 skipped=0 mismatches=0   exit 0
$ ... --root . --file SCORECARD.md --rev 8680755…
assertions=62 resolved=62 skipped=39 mismatches=0   exit 0
$ ... --root . --file /dev/null --rev 8680755…
assertions=0 resolved=0 skipped=0 mismatches=0   exit 0
```
The third line is the always-zero control's exact output, emitted by the real tool with exit 0. The
kill rule tests only whether the *control script* fails the fixtures, so this is not a violation of
the frozen kill rule — but no selftest fixture covers it, and exit 0 with `assertions=0` is
indistinguishable at the exit-code level from a calibrated run. A guard (refuse `assertions=0`, or
require `--file` to be repo-relative when `--selftest` is not set) would close it. `evidence/ResDeclaredEvidence-provenance-bypass.txt`.

### L2 — LOW, still open: uppercase hex is counted twice, so `N+S` does not enumerate tokens

`skipped += 1` fires in the span pass for a token that `re.fullmatch(r"[0-9a-f]{7,40}")` rejects
for being uppercase, and the cell pass then asserts the same token. Fixture l: one token
(`AC71BFC`), `assertions=1 resolved=1 skipped=1`. Fixture b2: the uppercase digest appears as the
class-C assertion *and* in `skipped=1`. The prereg states "skipped counts tokens excluded by these
rules (so N+S enumerates every candidate token the scanner saw)"; for uppercase tokens it
over-counts by one. No uppercase hex exists in `SCORECARD.md` at the final tip (`grep -cE '[A-F]'
over 7..64-hex runs = 0`), so the shipped `62/39` figures are unaffected.

### L3 — LOW, still open: two stale "tip" pointers

The row names `tip 8990ae4…`; the final tip is `8680755` (three commits later). Counts are
identical (`62/62/39/0`), so the claim holds, but the row cannot name the tip it ships in — the
literal will always lag. Separately `instrument-digests.txt` still says
`lane_tip=f8f0b4a2c4ab3d16369413b6aa9f2d2c08590581` (four commits behind the final tip and three
behind the row's own named tip), so a strict reader sees three different "lane tip" values across
two receipts.

### L4 — LOW, out of the frozen enum, still open as an undisclosed limit: sentence-final punctuation on a path token

`` `tools/absent.sh.` `` → `assertions=1 resolved=1 skipped=1 mismatches=0` (fixture c). Because
class A requires the token to *end* `.py/.sh/…`, a comma or period after a dead path silently
removes it from the audit. This is enum-conformant — I am not calling it a false green of the
frozen predicate — but the row's list of named enum limits ("command-embedded paths are skipped,
class C is structurally empty, skips are not itemised, class B proves existence not measurement")
does not include it, and it is the shape a human writer produces most often.

### Verified-correct behaviours (attacked, held)

`*` never crosses `/` (`_segmatch` per segment, and a segment-count mismatch fails); `rev:path`
spans resolve against the named rev and mismatch on absent path *or* unresolved rev; globs are
expanded over `tracked(--rev)`; sha256 is compared against the blob at `--rev`, case-normalised;
a repo-relative declaration absent at `--rev` raises instead of reading the worktree; class C truly
is structurally empty on this file (0 class-C assertions at base and tip; class histogram at tip
`8680755` = 53 A + 9 B, base `4edb25d` = 50 A + 5 B); `skipped` is not itemised, as the row admits. The three base mismatches (`AXES.md`,
`reason-after.txt`, `.ufo/scopes/…/obsidian-cli-probe.md`) are truth-preserving at the tip:
`AXES.md` is now an absolute host path (bare `` `AXES.md` `` occurrences = 0), `reason-after.txt` is
`census/round-21/reason-after.txt` and exists at the tip, and the `.ufo/scopes/…` pointer is now
prose, not a backticked repo-relative path.

## 5. Round-1 cross-check

This attempt's round-1 residual reports (`ResGateCheck.md`, `ResScopeNoHarm.md`, `ResSources.md`,
`ResSliceVerdicts.md`) contain no C1-instrument findings — `grep -i 'declared-evidence\|calibration'`
matches only incidental mentions of the tool path. Nothing in section 4 restates them; H2 was
observed *during* this attack at `ee1aef2`/`c9f1fe3` and is recorded as fixed at `8680755`, not as
a prior finding. Attempt 1's C1 (strict full-adequacy of the r22 result oracle) is not re-claimed
by this round and was not tested here — out of scope.

## 6. Residual risk and verification gaps

- The landing is still in flight (`master` moved four times during this attack, worktree dirty).
  The verdict is pinned to `8680755`; any later commit to `SCORECARD.md` invalidates the `62/62/39`
  literals while `M=0` may still hold.
- The C1 conclusion (`M=0` at the final tip) is verified for the instrument's enumeration and, by
  manual check, for the four tokens the wider enumeration adds. I did not exhaustively re-derive
  every one of the 39 skipped tokens by hand; only the skipped tokens that a hex-retaining scanner
  and the round's own receipts surface were examined. "Skips are not itemised" means an in-enum
  token could hide in the 39 without this report seeing it.
- No verification of `souji-gate-check.py` (C2) or of the registry — other seats own those.

## Evidence

`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/residual/evidence/`:
`ResDeclaredEvidence-selftest.txt`, `-counts-matrix.txt`, `-attacks.txt`,
`-dropped-tokens.txt`, `-provenance-bypass.txt`, `-tip-identity.txt`. Throwaway fixtures
(`/var/tmp/sde-fx`, `/var/tmp/sde-tools`, `/var/tmp/doctored.md`) were removed after the run; the
tool copies used were byte-identical to the committed tool
(`sha256 65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4`).
