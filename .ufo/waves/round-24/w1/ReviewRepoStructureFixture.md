# ReviewRepoStructureFixture — r13 F2 write-safety fixture as C1 precedent

## Status
STATUS: PASS — the questions are answered from committed bytes plus a /var/tmp-only rerun. The r13 fixture has exactly one committed PASS (r13, git 2.55.0). It was retained into the final record, not rerun, and r14 refused it as non-reusable. It passes again today on git 2.56.0, but that run is not committed. Thirteen weaknesses are listed below for C1 to avoid, plus one ATTACK on the frozen case set.

## Evidence
Lane revision: `f9db2181647d91470a724a12d626bd6106805076`. Fixture last touched at `6ed10a7`. Fixture sha256 `b6bf5205…179f` (659 lines, 23499 B), probe `tools/souji-repo-structure.sh` sha256 `80025137…aec2`. Both match `census/round-13/final-checks.md:20-21`.

**Committed executions.**
- `census/round-13/verification-attempt-1.json` (measured `6ed10a7`) holds the only execution of `structure-selftest`. The command was `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh`, with `exit_code: 0`, `seconds: 0.084`, and stdout `git_version=git version 2.55.0` … `selftest=PASS ids=5/5`.
- `census/round-13/verification.json` (measured_commit `6f8ee0f`) carries the same result with `"measured_commit": "6ed10a7…"` and `"retained_from": "census/round-13/verification-attempt-1.json"`. It is retained, not rerun.
- `census/round-14/verification.json` `historical_legacy` lists `"source_result": "structure-selftest"` with `"findings": ["dependencies-legacy"]`, `"gate_exit": 2`, `"reusable": false`.
- `grep -rn 'selftest=PASS ids=' census --include=*.json` shows only the two round-13 files. There has been no committed rerun in r14–r23.
- `tests/results/`: `git ls-files tests/results | grep -ci r13` returns `0`. The proposed `tests/results/r13-repo-structure.txt` (`census/round-13/registry-draft.md:270,410`) never landed.

**Rerun this seat (git 2.56.0, scratch `/var/tmp/souji-r24-ReviewRepoStructureFixture/`, now removed).** The fixture's own mktemp is hard-coded `/var/tmp/souji-r13-repo-structure.XXXXXX` (`:159`), HOME is under WORK (`:171`), and the EXIT trap does `rm -rf` (`:162`). The probe's only write is `mktemp -d /var/tmp/souji-repo-structure.XXXXXX` (`tools/souji-repo-structure.sh:265`). Lane `git status --porcelain --untracked-files=all` had the same sha256 before and after, and no new `/var/tmp/souji-r13-repo-structure.*` or `souji-repo-structure.*` directories were left behind.
```
== baseline   (bash .../r13-repo-structure.sh --selftest)
id=SOUJI-R13-STRUCT-write-free case=write-free rc=0 manifest_entries=41 verdict=PASS
id=SOUJI-R13-STRUCT-object-metrics case=object-metrics checks=18 verdict=PASS
id=SOUJI-R13-STRUCT-bogus-repo case=bogus-repo plain_dir_rc=128 missing_rc=128 verdict=PASS
selftest=PASS ids=4/4                                   exit=0
== probe      (--selftest --probe .../tools/souji-repo-structure.sh)
id=SOUJI-R13-STRUCT-object-metrics case=object-metrics checks=29 verdict=PASS
id=SOUJI-R13-STRUCT-promisor-refusal case=promisor-refusal promisor_rc=2 partial_rc=2 verdict=PASS
selftest=PASS ids=5/5                                   exit=0
== shellcheck -S warning (0.11.0)                       sc_exit=0
```

**Falsifier probes (scratch only).**
```
stub-noop (exit 0, no output, never runs git) as --probe:
  write-free rc=0 manifest_entries=41 verdict=PASS
  object-metrics/bogus-repo/promisor-refusal verdict=FAIL
  selftest=FAIL ids=5/5 missing=[] extra=[] failed_verdicts=1      exit=1
stub-rc3 (exit 3) as --probe:
  write-free rc=3 verdict=FAIL ... selftest=FAIL ... failed_verdicts=1  exit=1
linked worktree (main + `worktree add ../linked`):
  r13 manifest root (rev-parse --absolute-git-dir) = <S>/main/.git/worktrees/linked
  common dir = <S>/main/.git
  raw count-objects -v from linked: warning: garbage found: <S>/main/.git/worktrees/linked/refs ; garbage: 1
  hash-object -w via linked -> r13-root manifest: write NOT detected; common-dir manifest: write detected
fsck --lost-found on the repo holding that dangling blob, r13 manifest_all over .git:
  detected: new d .git/lost-found, d .git/lost-found/other, f .git/lost-found/other/4ba8ea60…, d .git (mtime)
```
Tooling: no installs. The harness Read tool refused the 23 KB fixture and records with a spurious ">100000 characters" error, so the bytes were read with `nl -ba`.

## Findings
These are weaknesses in the r13 fixture that C1's `tests/fixtures/r24-size-census.py` must not repeat.

1. **The committed status prose contradicts the record.** `tests/fixtures/r13-repo-structure.sh:4-7`: "STATUS: authored, NOT EXECUTED by this seat … not an observed PASS." This sits beside a recorded `selftest=PASS ids=5/5`. C1 must not ship status claims inside fixture bytes that a later record contradicts. Run status belongs only in the receipt.
2. **The header and code disagree on the exit class.** `:21-22`: "treats nonzero exit OR any stderr as could-not-evaluate". The code adds `rc=` / `stderr-nonempty` to `WF_REASONS`, which yields `verdict=FAIL` and exit 1 (`:387-392`, `:423`, `:659`). Observed: stub-rc3 gave `exit=1`, not 2. C1 must pin each tool exit (0/1/2 per the frozen CLI) to an expected value per case, and keep fixture exit 2 for setup failure only.
3. **The summary count is a boolean.** The header promises `failed_verdicts=<n>` (`:72`), but `FAILED=1` is a flag (`:304`, `:658`). Observed: four failing verdicts printed `failed_verdicts=1`. C1's `cases=C pass=P` must be computed counts, with P derived from per-case verdict lines.
4. **The case set depends on the mode, and a reduced PASS line exists.** Baseline `--selftest` prints `selftest=PASS ids=4/4` and silently omits the refusal case (`:618-626`). `SKILL.md:253` cites the reduced form "(`bash tests/fixtures/r13-repo-structure.sh --selftest`)". The entry recheck (`corpus/knowledge/git-repo-structure-readonly.md:3`) and the registry row (`SKILL.md:186`) use `--probe`. C1 must expose one invocation with a fixed C=8. No flag may produce a passing last line over fewer cases.
5. **The manifest root is the per-worktree git dir, not the common dir.** `:297` uses `rev-parse --path-format=absolute --absolute-git-dir`. From a linked worktree that resolves to `<common>/worktrees/<id>`, and a write to common `objects/` was NOT detected (probe above). C1's manifest must cover the resolved common dir, plus the per-worktree dir for case 4.
6. **The detector control is synthetic only.** `:326-357` appends to and touches a pre-existing `description`. It never shows new-path creation or a real Git write. An r13-style manifest does detect `fsck --lost-found` (new `lost-found/other/<oid>` plus the `.git` mtime; probe above), so C1 case 7 is the missing real-world positive. C1 should keep the synthetic control as well, so that detector blindness and absence of writes stay distinguishable.
7. **The write-free verdict is vacuous on its own.** A no-op stub got `write-free … verdict=PASS`. No-write evidence binds only through discriminating output from the same invocation. In C1, case 1 (clean, all-zero) has the same property: the case-8 stub passes it, which is why the control uses cases 2–5. Per-case write-safety claims should be read only for cases 2, 3 and 6, where nonzero or refusal output proves the tool ran.
8. **There is no skip-the-work control.** r13 has no stub or false-green case; only the id-set equality is checked (`:628-653`). C1 has case 8 and a pre-data stub receipt. Both must be committed before any after-data, as `preregistration.txt:61-63` requires.
9. **There was a single run, never re-measured, and it is now non-reusable.** One execution at `6ed10a7` on 2.55.0 was retained into `verification.json` and refused by r14 (`dependencies-legacy`, `reusable: false`). Host git is now 2.56.0. The knowledge entry still says "host Git 2.55.0" (`git-repo-structure-readonly.md:2`). C1's receipt should bind the git version, the tool and fixture digests, and the measured commit in the same record.
10. **The PASS is stored only as an embedded JSON stdout string.** There is no standalone results artifact (the proposed `tests/results/r13-repo-structure.txt` was never committed). C1 should commit the counter output as its own receipt file, matching the prereg's `census/round-24/` pattern.
11. **The coverage limits are self-declared.** `:111-113`: "does not exercise packs, tags, remotes, linked worktrees, bare repos, alternates…". C1 covers pack junk, linked worktrees and alternates. For case 5, the alternate target directory lives outside `.git`, and C1 should state whether it is manifested. [INFERENCE: neither count-objects nor fsck writes there, but this is unmeasured.]
12. **The manifest has gaps by design.** It records type, mode, size, mtime, path, link target and sha256 (`:205-213`), but not uid/gid or xattrs, and it records persistent state only, so transient lock files go unseen. The prereg's C1 manifest has the same scope (`preregistration.txt:48`). C1 must disclose this rather than claim "no write".
13. **The verifier certified bounded scope correctly — keep that.** `corpus/lessons/round-13-verifier-spotcheck.md:78` admitted F2 as "bounded F2 slice only". C1's entry must equally avoid generalizing to "count-objects/fsck never write" beyond the 8 cases on this host.

## Attack log
- **A1 (frozen counter, reported only, not proposed for change): cases 4 and 5 have no manifest-unchanged predicate.** `preregistration.txt:52-55` checks only figures for `linked` and `alternates`, while cases 1, 2, 3 and 6 assert manifest equality. A tool that writes while answering a linked-worktree path (for example, cleaning `worktrees/<id>/refs`) would still pass case 4. Combined with finding 5, an r13-style `--absolute-git-dir` manifest would also be blind to common-dir writes there. This is the exact assimilation theme, and it is unguarded by the counter. The L1 should record it as a disclosed residual: C1 does not show write-safety on linked or alternates paths.
- **A2 (gaming surface carried over from r13):** if the C1 fixture kept a reduced mode (finding 4) or a boolean failure flag (finding 3), a passing-looking last line could be produced over fewer than 8 cases. The prereg's fixed `cases=8 pass=8` closes this only if P is counted from emitted per-case verdicts, and C is the frozen constant 8, not `len(emitted)`.

Checks for the main agent: `bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-repo-structure.sh --selftest --probe /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-repo-structure.sh` should return `selftest=PASS ids=5/5`, exit 0, on git 2.56.0. Review the C1 fixture's manifest root (it must be the common dir) and its last-line arithmetic against findings 3–5.
