# AttackNoHarm — round 13 W1 critic (causal separability + no-harm invariants)

Seat: `SoujiR13.AttackNoHarm` (critic, lane-dispatched; NOT an independent non-author). Read-only;
no tool executed except metadata (`sha256sum`, `git status/log/diff/grep`, `ls`, `git --version`).
Baseline HEAD `31984f4`. Observations are at 2026-10-20 ~02:10–02:20 -0300 against a working tree
that is moving mid-wave. `[F]` = fact observed at the cited path:line. `[I]` = inference.

Axes judged: calibration (C1, lowest = 7), operability (C2), coverage (C3).
Rules applied: AXES.md:30-36 (claims causally separable, distinct axes, admitted only if every
claim verifies **and no axis is harmed**); AXES.md:62-64 (a capability without a passing
demonstration is pre-claiming); PROTOCOL.md:375-411 (Gate standard); PROVINCE.md:26-36, :49-51;
QUALITY Q4/Q6/Q8/Q10/Q11/Q13/Q16; round-12-verifier-spotcheck.md:13 (K5 claimed a nonexistent fixture).

## 1. Separability verdict

Declared at `census/round-13/claims.json:10` [F]: "C1 isolated synthetic manifests do not depend on
C2 or C3; C2 fixture uses its own receipt fixture …; C3 isolated Git repo uses neither."
**As specified, it holds**, under three conditions that are easy to break:

| coupling | counterexample | evidence | fix |
|---|---|---|---|
| C1 ↔ C2 via real tool digests | If C1's "digest-pinned frozen input run" (`claims.json:5`) pins a fragment for the real `tools/souji-quarantine.sh` (`141c0fdc…`, `sha256sum` now), C2's edit changes those bytes. The frozen run then fails `artifact-digest`, or someone re-pins it after C2. Either way C1's after-state depends on whether C2 landed. | `tools/souji-cert-evidence.py:109-118` [F] (`--frozen` verifies sha256 of every listed file); quarantine hash 141c0fdc in 40+ r10/r11 receipts (`census/round-11/cert-16.json:14`) [F] | Pin only synthetic artifacts that the C1 fixture itself creates. No frozen input may reference `tools/souji-{quarantine,verify,vault-verify,census}.sh`. |
| C1 ↔ certification | A green C1 run read as "re-certification passed" ties C1 to the r11 carry (`SCORECARD.md:51-53`) and silently flips certification. | `round-11.md:12-18` [F]; `round-13.md:30` REJECT row [F] | Keep C1's after = discriminating fixtures only. Certification stays OFF in SCORECARD:76 and is not mentioned as a C1 delta. |
| C2 red-before ↔ harness layout | A baseline extracted to `/var/tmp/<x>/…/souji-quarantine.sh` recomputes `REPO_ROOT`/`LIVE_FLEET_ROOT` from its own path (`souji-quarantine.sh:127-130`) [F] and its engine as `$REPO_ROOT/tools/souji-verify.sh` unless a sibling `cand-merge-verify.sh` exists (`:134-138`) [F]. A bare copy fails "engine missing" (exit 1, `:610-611`) or hits the live-fleet guard (exit 4, `:616-624`). That is a red result for the **wrong reason**, and r11 already saw it: "bare-copy 65-fail figure is a layout artifact (engine missing + live-fleet guard scope)". | `census/round-11/rubric-score-22.json:119,122` [F]; `census/round-11/final-31.json:58` [F] | `r13-quarantine-bounds.sh --tool` must set `SOUJI_VERIFY_BIN` to the installed engine. It must put the fixture repo outside the copied tool's derived `LIVE_FLEET_ROOT`, and record per case the red *reason* (timeout or special-file id, never rc 1/4). |

Two more points, though neither breaks separability. C2 and C3 are on distinct axes. And no claim's
counting command reads another claim's artifact (`claims.json:5-7`) [F].

## 2. Per-axis potential harm list

### Calibration (C1 axis; lowest = 7)

1. **Pre-claimed shared-doc edits (K5 class repeating).** In the working tree at 02:12–02:13 [F]:
   - `corpus/knowledge/git-repo-structure-readonly.md:2-3` cites `census/round-13/verification.json` and `recheck: bash tests/fixtures/r13-repo-structure.sh --selftest`. Neither file existed at read time (`ls` → No such file). `tools/souji-repo-structure.sh` was also absent.
   - `PROVINCE.md` diff: "bounded structure probe and isolated write-safety fixture acquired r13" and "Core now includes … `tools/souji-repo-structure.sh`".
   - `corpus/SOURCES.md` S005/S006 `queued→mined` with `used-by` pointing at the not-yet-admitted entry.
   - `corpus/lessons/round-13.md:68` asserts "No live artifact removal … was performed" before the round closes.
   L1 replied that it will commit only complete, tested files (accepted). The **harm exists only if
   any of these lands before its pointed-to file exists and runs green**. The new Q17 is written to
   catch exactly this, so committing these first would make the round's own bar self-refuting.
2. **Stale hash receipts that C1 does not touch.** `SCORECARD.md:27` cites souji-verify `7efda63bd760…` and `:29` vault `d312263a…`. Installed bytes are `9adb1764…` and `f9e778ca…` [F, `sha256sum`]. `results/cross-95.json:142` already confirmed this drift [F] and it was never fixed. If C1 claims "installed-byte integrity" while SCORECARD still carries non-installed digests, the calibration signal ("SCORECARD matches observed repo state", AXES.md:15) is contradicted in the same file. Fix: append a dated correction to those capability rows. That is a bookkeeping correction, not a C1 delta.
3. **SCORECARD count drift (Q10).** `SCORECARD.md:30` reads "mined=18 queued=13". `SCORECARD.md:18`, `round-13.md:52` and `before.json` use 16/15 [F]. After S005/S006 flip, the true count becomes 18/13 again. **A reader can mistake the coincidence for "no change".** The r13 row must show 16/15 → 18/13 with the command, and the `:30` cell must be corrected, not left as is.
4. **Author-label uniqueness ≠ independent identity.** `author` is a self-declared string in the fragment schema (EvidenceGate target). A "duplicate author rejected" pass proves only distinct labels. Report wording must not say "independent certifiers" (contract: no non-author claims).
5. **Q17/Q18 test = the claim's own tool.** QUALITY diff Q17/Q18 `test` column is `python3 tools/souji-cert-evidence.py --selftest` [F]. The lessons are real (r11:14, r12 post-review item 2), so this is not Q15-style circularity. But the criterion is only as strong as a fixture written in the same round. The round Gate must also show one **independent** falsifier: a historical r11 `cert-16.json` shape or a missing-path case that the gate rejects.
6. **Textual counts as proof.** `before.json:6` `bounded_staging_calls` and the Q8 grep test (`QUALITY.md:32`) are textual. A `timeout 30 mv` inside a dry-run `emit CMD` string (`souji-quarantine.sh:505-516` pattern) or a comment would raise the count without bounding anything. Only the behavioural fixture counts (Q11).

### Operability (C2 axis)

1. **Timeout-killed `git mv` leaves `.git/index.lock`** [I, from git lock semantics; not run]. Wrapping `git -C "$crepo" mv` (`:529`) in `timeout --kill-after` can SIGKILL git while it holds the index lock. The owning lane repo then refuses every later commit or `git mv`, which harms a live repo. Fail closed: on rc 124/137, report `STAGE2-TIMEOUT` plus a lock-present probe (`test -e "$gitdir/index.lock"`). **Never remove the lock** (souji never removes a lock it did not provably set, PROVINCE.md:62-63).
2. **Timeout-killed plain `mv` across a device boundary** [I]. `mv` falls back to copy-then-unlink on EXDEV, which can happen between btrfs subvolumes inside one repo. A kill mid-way leaves a partial copy in quarantine and possibly a partially unlinked source. That is deletion without a receipt (AGENTS.md:5-8). Required: after a timeout, no stage 5. Emit residue on both sides (`test -e "$ct"`, `test -e "$qpath"`). Never `rm` the partial quarantine copy automatically; RESULT `STAGE2-FAILED`, RC 3 (`:536-541` pattern).
3. **False provenance on the FIFO class** [I, static read]. The installed tool already redefines `file_sha`/`dir_digest` after the hardening block (`:722-734` override `:184-194`). `file_sha` requires `[ -f ]` and no symlink component. `s18_scope_ok` returns 1 on any non-regular descendant (`:714-715`). The engine has the same guard (`cand-merge-verify.sh:528`) [F]. So the baseline digest path **may already refuse** a FIFO without hanging. The documented hangs were (a) the staging loop (`LOG.md:373-374`) and (b) **judge fixtures** of `souji-vault-verify.impl-17.sh` (`LOG.md:402-403`), not this tool. Claiming "closes FIFO hang in quarantine" needs a baseline FIFO case observed red. If it is green on baseline, record it as a regression guard, not a closure.
4. **Selftest contaminated by the concurrent wave.** Selftest checks G1/H3 compare live-lane `git status --porcelain` count and `LOG.md` sha before vs after (`:1316-1331`, `:1490-1494`) [F]. Any seat or L1 write during the run flips them. Run only after all seats land and before L1's integration edits, or record the flip as environmental.
5. **Q4 text vs behaviour.** `:1247`, `:1486`, `:1519` contain `${TMPDIR:-/tmp}` [F], so the Q4 grep (`QUALITY.md:28`) returns ≥3. Effective behaviour is `/var/tmp` only because `:685` exports `TMPDIR="${TMPDIR:-/var/tmp}"` first [F]. An inherited `TMPDIR=/tmp` (host default is unset now [F]) would put fixtures in `/tmp`. Final checks must run with explicit `TMPDIR=/var/tmp`. C2 should replace the three literals; behaviour stays the same.
6. **Dry-run must stay inert.** Dry-run emits `CMD` lines and returns before stage 2 (`:504-519`) [F]. The patch must not add a pre-flight `timeout … sha256sum` or `mkdir` above `:504` that touches the target in dry-run. Check: the existing D1 assertions (`:1334-1342`) still pass, plus one new dry-run FIFO case that creates nothing.
7. **Live guard bypass in the fixture.** If the bounds fixture exports `SOUJI_QUARANTINE_ALLOW_LIVE=1` to get past a derived guard, it must first assert the repo arg is under its own `mktemp -d /var/tmp/...` root.

### Coverage (C3 axis)

1. **Duplicate or renamed authority.** SourceRepo recommends `knowledge/git-repo-structure-size-census.md` (`SourceRepo.md:121`) [F]. The tree holds `git-repo-structure-readonly.md` [F]. Exactly one entry may land, and SOURCES `used-by` must name it.
2. **Coverage-map contradiction.** `corpus/README.md:40` still says F2 "no entry … `ls corpus/knowledge | grep -ciE 'size|structure|sizer'` → 0" [F]. The new filename matches `structure`. That needs an appended correction, or the index row (a claim) becomes false.
3. **Frontier→Core needs an admitted entry *and* a SKILL rule** (PROVINCE.md:50-51) [F]. The PROVINCE diff moves the probe to Core with no SKILL rule or registry row yet. Either land the SKILL row (RegistryDraft) or keep the PROVINCE text at "frontier, entry admitted".
4. **Scope overreach.** One isolated fixture proves only that the observed `.git` file set and contents did not change, for one non-bare repo on git 2.55.0 with the fixture's config. The entry text (`:11`) already says this [F]; keep the PROVINCE text equally narrow. "Reachable object size" ≠ recoverable disk (`round-13.md:32`) [F].
5. **The probe has no live-path guard** (SizeProbe target: `--repo PATH`). It is read-only by design, but no live repo run is evidenced this round. Final checks must exercise only `/var/tmp` repos. The fixture should isolate global config (`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`) so user hooks or fsmonitor settings can't make the write-safety result depend on the host config. I did not read the operator's git config.

## 3. Invariants checked

| invariant | status | evidence |
|---|---|---|
| Certification OFF | holds in text | `SCORECARD.md:72-77`, `claims.json:11`, `round-13.md:30,62`, `souji-cert-evidence.py:9,29,134` [F] |
| Operator sweep untouched | holds | `git status --porcelain -- census/operator-sweep-20261019` → 1 line, untracked; no seat diff touches it; `before.json:13` [F]. Contents not read. |
| No live mutation required | holds as designed | all three fixtures specified under `/var/tmp` (spec targets) [F]. Quarantine live guard `:614-626` stays intact. |
| No commits by seats | holds | HEAD still `31984f4`. Working-tree edits to shared docs (PROVINCE/QUALITY/SOURCES/SHONEN) are L1's integration seat, per L1. |
| Q16 / no `/dev/shm` | holds | `round-13.md:31` REJECT row [F] |

## 4. Smallest safe corrections (for L1)

1. Commit no pointer before its file: `test -f` on `tools/souji-repo-structure.sh`, `tests/fixtures/r13-repo-structure.sh`, `tests/fixtures/r13-quarantine-bounds.sh`, `tests/fixtures/r13-cert-evidence.py`, `census/round-13/verification.json` at the commit.
2. C1 frozen inputs: synthetic artifacts only. `grep -cE 'souji-(quarantine|verify|vault-verify|census)\.sh' <frozen>/expected.json` → 0.
3. C2: report the red reason per case and handle the timeout residue (index.lock probe; no rm after a timeout). Run the baseline via `--tool` with `SOUJI_VERIFY_BIN` set and the fixture repo outside the derived fleet root.
4. Append-only corrections: SCORECARD:27/29 digests, SCORECARD:30 counts, README:40 F2 sweep.
5. PROVINCE: no "Core" wording unless a SKILL row lands in the same commit.

## 5. Proposed final checks (L1; not run by me)

```bash
L=/home/vgpnk/Projects/shokunin/souji-shokunin
git -C $L status --porcelain -- census/operator-sweep-20261019        # exactly '?? census/operator-sweep-20261019/'
for f in tools/souji-repo-structure.sh tests/fixtures/r13-repo-structure.sh tests/fixtures/r13-quarantine-bounds.sh tests/fixtures/r13-cert-evidence.py census/round-13/verification.json; do test -f "$L/$f" -a ! -L "$L/$f" || echo "MISSING $f"; done
grep -c 'TMPDIR:-/tmp' $L/tools/souji-quarantine.sh $L/tests/fixtures/r13-*        # target 0
grep -nE 'souji-(quarantine|verify|vault-verify|census)\.sh' <C1 frozen dir>/expected.json   # target: no output
TMPDIR=/var/tmp bash $L/tests/fixtures/r13-quarantine-bounds.sh --tool <baseline-copy>   # red; reasons = timeout/special-file ids, not rc 1/4
TMPDIR=/var/tmp bash $L/tests/fixtures/r13-quarantine-bounds.sh --tool $L/tools/souji-quarantine.sh  # green
TMPDIR=/var/tmp bash $L/tools/souji-quarantine.sh --selftest   # after all seats land (G1/H3 sensitivity)
grep -c '^\- \[x\]' $L/SHONEN.md   # 0
grep -nE 'CERTIFIED|certification (granted|ON)' $L/SCORECARD.md $L/corpus/lessons/round-13.md   # no grant
ls /var/tmp | grep -cE 'souji-r13|srepo-write-test'   # 0 residue after runs
```

## 6. Correction (appended after L1 challenge, 2026-10-20)

My message to L1 claimed that deleting the SHONEN.md `Marks:` paragraph was a canonical-seed
regression. **That was wrong.** PROTOCOL.md:432 defines the seed as the *indented* block (:441-448).
The `Marks:` lines (:450-451) are unindented prose outside it. The canonical mint template
`/home/vgpnk/Projects/kimi-shokunin/templates/mint/SHONEN.md` (read here) ends at the four boxes,
with no Marks paragraph. ReviewSHONEN.md §8 records the same erratum. Removing those lines brings
SHONEN.md *toward* byte-canonical form, so there is no calibration harm. The `[x]`-needs-non-author
rule still lives in PROTOCOL.md:59-73. The finding is withdrawn and is not part of §2.

## Limitations

- Static read only. Every timeout, lock and EXDEV behaviour above is `[I]` until a fixture shows it.
- The working tree moved during the review. Line numbers refer to the files as read at ~02:13–02:20.
- I did not read the in-flight `souji-cert-evidence.py` beyond grepping its header and frozen sections.
- No tools installed or updated.
