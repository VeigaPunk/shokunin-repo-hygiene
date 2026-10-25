# Round 26 verifier spot-check

author: hyaku closure (non-author integrator, @m_kfc)

Round: souji 26 · lane HEAD before `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd` · after `166baa18f808071bc385187691713044a26bd663` · report `.ufo/reports/round-26/souji.md`

## Conformance (step 1)

- Report committed by lane identity: `git log --format='%an %H' -- .ufo/reports/round-26/souji.md` → `souji-shokunin 2c8fbc76373db009cfbbe05fa35c15c27e98d0b0`; report lands last, after the cited lane tip, and is on fleet `master` (pushed `ad8fc9f0e8e5bb65ea54d08ca4f5773e0f7aba0d`). Attribution OK.
- `SHONEN` heading: present, one line per box (4 boxes, all `[~]` with pointers). No `[x]` written; no non-author promotion check claimed. Boxes carry resolvable pointers; full promotion checkability is operator-owned.
- Cited lane commits: all 15 cited hashes exist (`git rev-parse --verify <h>^{commit}`) and each is an ancestor of `refs/heads/master` (`git merge-base --is-ancestor` → ok for all). Lane tip `166baa18…` sits on `master` and remote matches.
- Lane push state: `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state` → `branch=master local=166baa18… remote=166baa18… ahead=0 behind=0 head=detached`. Pushed, no round work uncommitted at the report's tip claim.
- Leftovers: `git status --porcelain` shows trailing wave-seat outputs in `.ufo/waves/round-26/w1/` (8 modified + 10 untracked, mtimes 14:36–14:39:37, past driver complete 14:39:08), plus untracked `census/operator-sweep-20261019/` and `__pycache__/` dirs. Status-neutral conformance defect (wave seats were still running at report time); routed to the lane to commit/sweep next round.
- Prompt fidelity: `.ufo/prompts/souji-round-26.md` carries the template contract verbatim (MISSION/AXES binding, 1–3 claims + admission rule, frontier step §2b, L2 floor §3, report contract §4 with `SHONEN` heading, commit-then-push §5) plus the hyaku addendum; L2 route map matches `MISSION.md` buckets and the run-7 role map. OK.
- Dispatch/completion digest (watchdog): `2026-10-25T13:52:04-03:00 launch souji round=26 pgid=15822 driver=hyaku-inline attempt=1`; `2026-10-25T14:39:08-03:00 complete souji round=26; hyaku-inline attempt=1`.

## Claims (step 2)

### C1 — calibration (7, lowest non-retired): markers 2→0, headings 17 175 231 → 17 44 78, 7 protected spans byte-equal
Re-measured over committed bytes (base `0eca7c8`, tip `166baa18`):
- `git show 0eca7c8:SCORECARD.md | grep -cE '^(Insert the table below directly above|Optional same-landing correction)'` → `2`; tip → `0`.
- `awk '/^### Round (23|24|25) measurements/…'` → base `17 175 231`, tip `17 44 78`.
- Seven amendment-2 protected spans (base spans 1–16, 231–254, 175–207 fenced r24 block, 17–62, `## Capabilities` 63–93 + two fenced r24 rows + R3 note, `## Planned` 95–137 + two fenced bullets, 138–169): each exact byte sequence found contiguous in tip. First pass flagged a construction error (R3 note placement / inclusive bound); corrected bound + row-end note → all seven OK.
Observed: `markers=2/0`, `headings=17 175 231 / 17 44 78`, spans 7/7 byte-equal. **Re-measured — verified.**

### C2 — coverage (8): F1 grounded 0→2, registry rows 127→132, K4 grounded 7→9
- `git show <rev>:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → base `127`, tip `132`.
- `ground:` scan over `corpus/knowledge/` per rev → base 7 grounded (F2×5, F4×2), tip 9 (adds F1×2: `git-auto-maintenance-trigger-set.md`, `-r23.md`); F1 coverage-map row `corpus/README.md:39` names both new entries.
- K4 re-executed: `python3 -B tools/souji-coverage-agreement.py --root . --rev 166baa18… --base-rev 0eca7c8…` → `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0` rc 0, byte-identical to committed `c2-k4-after.tsv` (rev 33e6807).
- K2 gate evidence-verified: committed `c2-gate.tsv` → `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0` rc 0; both entries carry `## Gate` sections; snapshots under `census/round-26/sources/` all pass `sha256sum -c SHA256SUMS`.
Observed: rows `127→132`, F1 `0→2`, K4 `7→9 mapped=9 dangling=0` (re-executed). **Re-measured + evidence-verified.**

### C3 — operability (8): tool absent→present, claims=3 flags=0, 12-case fixture FALSE-GREEN-REJECTED
- Base: `git cat-file -e 0eca7c8:tools/souji-axis-check.py` fails (absent); fixture absent.
- Re-executed at tip: `bash census/round-26/c3-counter.sh` → `axis_check_tool=present`, `claims=3 flags=0`, `axis_check_exit=0`, `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, `fixture_exit=0`, rc 0 — byte-identical to committed `c3-after.tsv` (rev c5949013).
- Static collateral: prereg `MACHINE BLOCK` holds exactly 3 `CLAIM` blocks each with `axis:`/`surface-class:`/`enumerate:` (no universal word without `enumerate:`); fixture sources 12 cases including case 12 always-green stub control.
Observed: identical to frozen receipt; **re-measured + evidence-verified.**

Axis verdicts: `calibration improved` · `coverage improved` · `operability improved`. No owned axis harmed: `git diff 0eca7c8 166baa18 -- SCORECARD.md` shows scaffold removal, heading reorder, r26 measurements/corrections/planned adds; axes scores unchanged (calibration 7, operability 8, coverage 8).

## Discernment spot-check (step 3)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S128 admit (git-fetch(1) § OPTIONS) | admit A/mined | committed snapshot `census/round-26/sources/git-fetch.1.txt` (sha256 OK) | **agree** | `--auto-maintenance`/`--no-auto-maintenance`/`--auto-gc`/`--no-auto-gc` present in OPTIONS (lines 3190–3192); teaches 24 words ≤25; scope honest |
| S130 admit (builtin/pull.c) | admit A/mined | committed snapshot `git-builtin-pull.c` (sha256 OK) | **agree** | line 392 `strvec_pushl(&cmd.args, "fetch", "--update-head-ok", NULL);` verbatim; child-spawn claim grounded |
| S119 reject (zh-Hans git-fetch edition) | reject (staged corroboration) | live https://git-scm.com/docs/git-fetch/zh_HANS-CN (fetched 2026-10-25) | **disagree (qualified)** | page now carries "git-fetch last updated in 2.56.0" and the `--auto-maintenance` switch — the recorded reason ("version alignment unprovable, build stamps ambiguous") does not reproduce today; decision-time mirror state is unrecoverable. The reject OUTCOME (non-load-bearing corroboration refused; claim surface kept) stays sound; routed to r27 to re-evaluate S119-style rows with a pinned snapshot + sha256 if re-adoption is wanted |
| S120/S121 rejects (Pro Git ja; Atlassian ja) | reject | source rows in `merge/souji/SOURCES.append.md` (S120 book chapter: no release version pin; S121 vendor behavior outside git semantics) | **agree** | refusal bases hold: book has no version stamp to align; vendor page quotes hosted-service workflow, not git's own semantics |

New SOURCES row quote check (S128, newly written): `teaches` 24 words ≤25, located (`§ OPTIONS`), `used-by` resolves to both admitted entries. Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0 (W04 warning-only class, unchanged).

## Trend verdicts

- **expansion — improved.** Two admitted entries on F1 frontier ground not previously held (README coverage-map row :39 updated; S128–S132); rows 127→132; entries cite `mined` rows. Bound (report): `gc.worktreePruneExpire`/maintenance strategy still unmeasured — accepted as stated.
- **quality — improved.** Both entries source-pinned by sha256-verified snapshots with `verified-at: 2026-10-25`; no pre-existing admitted entry found false; C1 counter blind spot disclosed and carried (calibration debt named). S131/S132 own-work re-verified by sha256.
- **discernment — improved.** Spot-check agrees with sampled admits and with reject outcomes; Q59 criterion added grounded in R26-M1; the C3 instrument makes the axis-of-surface check mechanical with a FALSE-GREEN discriminator. The S119 rationale caveat is routed (not left unlearned silently).

## Routed defects (lane to fix next round)

1. Trailing wave-seat outputs under `.ufo/waves/round-26/w1/` were still being written past driver completion and remain uncommitted in the lane repo — commit under a next-round entry or sweep, and record the sweep.
2. S-language edition rows: the current zh-Hans manual aligns with 2.56.0; if the staged S119-style corroboration is ever re-adopted, pin the snapshot + sha256 and record the fetch date/quote at decision time (the round's "unprovable" reason is time-fragile).
3. `__pycache__/` dirs (`tools/`, `tests/fixtures/`) are untracked; add to `.gitignore` or never stage.
