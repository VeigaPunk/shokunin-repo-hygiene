# R42w2sentinel01 — hostile-input safety review of `tools/souji-freeze-check.py`

Seat: R42w2sentinel01 (role sentinel, round 42 wave 2, falsify). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Subject: landed tool at tip `3105a63b23481fccf7df58e74d14a6681e0ea0c8`; the working tree equals it. The tool sha256 is
`9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6` (`git show 3105a63…:tools/souji-freeze-check.py | sha256sum`).
Judged on: operability. Milestone: r42 falsify the landed artifacts.

Nothing in the lane was written by this seat. The frozen tool, counters, populations and fixtures were not edited. Every
attack fixture lived under `/fast/scratch/hyaku/souji-r42/R42w2sentinel01` (deleted before yield). Receipts copied into this seat
directory are the evidence. Scratch paths are shown only to say where a result was produced.

Receipts (committed-tree paths under this seat directory):
- `.ufo/waves/round-42/w2/R42w2sentinel01/receipts/commands-and-outputs.txt`: every command run and its observed output.
- `.ufo/waves/round-42/w2/R42w2sentinel01/receipts/driver.py`: the attack driver (sections A–H, I1, K1, G1–G3).
- `.ufo/waves/round-42/w2/R42w2sentinel01/receipts/final.py`: N1, I2, H4, K1, K2 probes.
- `.ufo/waves/round-42/w2/R42w2sentinel01/receipts/batch1.out` … `batch5.out`, `final.out`: raw captured output of those runs.
  `batch3.out` ends at the 900 s ceiling of its batch because one of my own harness calls (`manifest` on a FIFO fixture)
  blocked; that section was re-run after the harness fix (`batch4.out`). `batch3.out`'s F2 lane diff is a sibling seat's live file.
- `.ufo/waves/round-42/w2/R42w2sentinel01/probe/probe-patched-freeze-check.py` and `probe/probe-patched.diff`: a **scratch-only
  remediation probe** (not landed, not a candidate for `tools/`). It adds `--no-show-signature` to both `git log` calls,
  `GIT_NO_LAZY_FETCH=1` to `Repo.env`, a Control `is_symlink` check, and a SIGTERM handler in `--selftest`. 47 diff lines.

## Attacks, observed outcome, severity, handling

Severity: **High** = breaks a stated invariant (never executes repository-controlled code) or a fail-open verdict;
**Medium** = integrity of a verdict or a repository-writing/fetching side effect; **Low** = operability (time, memory, cleanup).
"Handling" states what the landed tool does today; the frozen tool is not edited here.

| # | attack | observed | severity | handling |
|---|---|---|---|---|
| S1 | repo-local `.git/config`: `gpg.program` + `log.showSignature=true`, a prereg history with a `gpgsig` commit | **Repo-controlled program executed.** `freeze_rev()`'s `git log --diff-filter=A … -- <prereg>` ran the configured program (marker `EXEC gpg …`). Other tool git calls (`rev-parse`, `cat-file`, `ls-tree`, `merge-base`, dispatch log) did not. Receipt A1, A2. Patched (`--no-show-signature` on both logs): `exec_fired=no` (A1-patched). Precondition: write access to the target's `.git/config`; `.git/config` is not transported by `git clone`. | **High** (invariant); exploitability medium | Unhandled in landed tool. Verified fix in the probe. |
| S2 | partial clone (`blob:none`) + repo-local `remote.origin.uploadpack` **or** `core.sshCommand` with a remote URL: the tool's blob read lazily fetches the prereg blob | **Repo-controlled program executed during the tool run.** I1 (fresh clone): `EXEC uploadpack …` marker. I2: `EXEC sshCommand -G … attacker.invalid` and `… git-upload-pack '/x'`. The fetch also **writes a new pack into the target's object store** (F3: `.git/objects/pack/pack-ae92….pack`, `cat-file -e` rc=0 after the run). Probe with `GIT_NO_LAZY_FETCH=1`: I1 and I2 `executed: False`, `rc=2 REFUSAL … pre.txt is absent`. | **High** (invariant + object-store write); precondition: write access to `.git/config` of a partial clone | Unhandled. Verified fail-closed fix in the probe. |
| S3 | `Control:` path that is a git **symlink** whose link text is `EXIT=1` (spoofed red control) | **Accepted.** `SUMMARY claims=1 findings=0`, rc=0 (D3 `symlink-EXIT1`). A real green file is correctly `CONTROL-NOT-RED` (D3 `real-green`). Cause: the `Control` branch reads the blob of the symlink object (the target string) and has no `is_symlink` check, though `COUNTER-/POPULATION-SYMLINK` exist. Not among the 37 frozen C2 cases. | **Medium** (fail-open for the control-red leg) | Unhandled. Probe adds `CONTROL-SYMLINK`: `rc=1 FINDING C1 CONTROL-SYMLINK census/link.txt …`. |
| S4 | the **prereg itself** committed as a symlink | Plain link text (`real.txt`): fails closed, `NO-CLAIMS` rc=1 (N1). A link text that *is* a complete clean prereg (target absent): **`SUMMARY claims=1 findings=0` rc=0**, while `test -e pre.txt` shows the link target ENOENT. The tool validates the blob text of the link, not the file a reader follows. The tool has no `PREREG-SYMLINK` check. | **Medium** (fail-open verdict for an unreadable prereg) | Unhandled. Not probed; recommended fix: `repo.is_symlink(rev, prereg)` → finding. |
| S5 | `--selftest` killed by SIGTERM mid-run | **Repositories left under `$TMPDIR`**: 19 files in `freeze-selftest-…` after rc=-15 (H-SIGTERM). SIGINT: cleaned up, no residue (H-SIGINT), because `KeyboardInterrupt` runs `finally`. Scratch probe with `SIGTERM → sys.exit(143)` in `selftest()`: rc=143, residue 0 entries; unpatched same method: 1 entries. SIGKILL is not handleable in-process: [INFERENCE] unrecoverable residue, not tested. | **Low** (cleanup) | Unhandled. Probe fixes SIGTERM. |
| S6 | no internal time budget; claim fan-out | Zero `timeout` references in the tool (G3). ~11 ms per claim: `claims=100 1.5 s`, `300 4.0 s`, `900 10.5 s` (G2). A 20 000-claim prereg is ~3.7 min, each claim spawning ~7 git processes. Termination is the caller's timeout only. | **Low** (operability) | Unhandled; the caller must impose a deadline. |
| S7 | huge population blob | No size cap; the whole blob is read into memory and split. **400 MB population: maxrss 2.0 GB** (≈5×), 6.0 s (G1b). 200 MB: 1.35 s (G1). | **Low–Medium** (operability/memory) | Unhandled. |
| S8 | hostile `.git/config` surface, otherwise: `core.pager`, `core.fsmonitor`, `diff.external`, `diff.c.textconv`, `alias.log`, `core.sshCommand` (no remote, so not reached), `core.gitProxy`, `credential.helper`, `uploadpack.packObjectsHook`, `core.hooksPath`, `log.showSignature`, `.gitattributes diff=c` on a plain non-signed, non-partial repo | **No execution** (B: `any repo-controlled program executed: False`). The tool's subcommands never invoke pager, fsmonitor, diff drivers or hooks. `includeIf`/`include.path`, `info/grafts` and an ssh-variant `gpg.ssh.program` were **not tested** (same class as S1/S2 by reading, [INFERENCE]). | (contained) | Holds for the tested keys. |
| S9 | environment: GIT_DIR, GIT_WORK_TREE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_INDEX_FILE, GIT_CONFIG_COUNT, GIT_EXTERNAL_DIFF, PAGER, GIT_PAGER, GIT_TRACE, GIT_CEILING_DIRECTORIES, GIT_NAMESPACE | **No effect**: every run `rc=0 SUMMARY claims=1 findings=0` (E). `Repo.env` is a whitelist (only `PATH`, `LC_ALL`, `GIT_*` safety switches) and the decoy repo is not read. | (contained) | Holds. |
| S10 | `PYTHONPATH` with a `sitecustomize.py` | Runs inside the tool process (E2: `sitecustomize-in-tool-process=True`). The variable is operator-supplied, not repository-controlled. `PATH` is inherited, so `git` is resolved from the caller's `PATH`. | **Low** (operator environment; known as the C2 `patches` mechanism, S259) | Documented limit (N-C2b). Not a repo-controlled path. |
| S11 | `--rev` as ref name, `HEAD~1`, `main`, `refs/…`, option-looking (`--help`, `-p`, `-x`, `--root`, `--prereg=…`, `--root=/tmp`) | Refusal `rc=2 REFUSAL COULD-NOT-EVALUATE: --rev must be a full 40-hex commit id` or argparse `rc=2` (C1). Full-40-hex gate before any git call; `--` before every path argument. | (contained) | Holds. |
| S12 | `--root` as symlink-to-repo, bare repo, linked worktree, subdir, plain file, nonexistent, `/tmp` | Symlink, bare and worktree read normally (rc=1 on fixture, read-only); subdir/file/nonexistent/`/tmp` refused `rc=2` (C2). Lane write manifest: see S14. | (contained) | Holds. |
| S13 | `--prereg`: `../../etc/passwd`, `/etc/passwd`, newline, `--help`, `-p`, empty, `.`, `pre.txt/`, globs `:(glob)**`, `*`, `:(exclude)…`, and a worktree **FIFO** at the path | Object-store read only: all refused `rc=2 … absent at <rev>`; the FIFO is never opened and there is no hang (D1). Newline in argv is echoed unescaped into the refusal line (`…b.txt is absent` on its own line): **Low**, operator-supplied argv only. | (contained; cosmetic) | Holds. |
| S14 | writes to the repo, cwd or fixture | Fixture repo + cwd: **no change** (F1). Lane copy via `cp -a` (mtimes preserved), 45 142 entries before/after: **NONE** (F2b). The live-lane diff (F2) showed a sibling seat's live `grid.jsonl` and loose-object mtime churn with unchanged sha256; attributed to siblings, not the tool. Exception: S2 partial-clone lazy fetch **writes objects**. | (contained except S2) | Holds for non-partial repos. |
| S15 | `--selftest` write scope (HOME, cwd, TMPDIR, `/tmp`) | Normal run: `SELFTEST cases=31 pass=31 fail=0`, rc=0, **no change** in HOME, cwd, TMPDIR, and no new `/tmp` entry (H1, H4). SIGINT cleans up (H-SIGINT). SIGTERM: S5. | (contained except S5) | Holds except SIGTERM. |
| S16 | Counter/Population/Control paths: traversal, absolute, newline, option-like, `..` inside, trailing slash, empty, 70 KB path, NUL byte | No path escapes the object store. Missing paths → `COUNTER-MISSING`/`CONTROL-MISSING`, rc=1. 70 KB path and NUL: no traceback (K1). Empty value parses the digest as a path (cosmetic). | (contained) | Holds. |
| S17 | the frozen C2 counter as the safety net | **Green on the defective tool**: `SUMMARY cases=37 pass=37 fail=0 … selftest=ok patches=3/3 tool_sha=9ddd596b98fb` on the unmodified tip (control, receipt end). **Also green on the probe** (scratch commit `470f63f6` on top of the tip): `… patches=3/3 tool_sha=bcc752e86bc7`. The counter has no leg for S1–S5 or S3/S4. So the operability target does not measure safety. | **Medium** (measurement gap, a named limit for L1) | Named limit: not editable under the freeze. The L1 decides the round lesson and any future counter. |

## Commands run (exact; outputs in `receipts/commands-and-outputs.txt`)

```
git --version                                   -> git version 2.56.0
python3 -V                                      -> Python 3.14.8
sha256sum tools/souji-freeze-check.py           -> 9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6
python3 -B driver.py  (SECTIONS=…)              -> batch1..batch5.out
python3 -B final.py                             -> final.out
python3 -B tools/souji-freeze-check.py --root <attack repo> --prereg pre.txt --rev <40hex>   (A1, B, C, D, E, I1, I2, N1 …)
python3 -B tools/souji-freeze-check.py --selftest   (TMPDIR=…; normal, SIGTERM, SIGINT, HOME/cwd/tmp manifest)
cp -a /home/vgpnk/Projects/shokunin/souji-shokunin/. lane_snap/ ; python3 -B snapwrite.py
   -> tool rc=0 out=SUMMARY claims=3 findings=0 time=3.45s ; entries before=45142 after=45142 ; changes: NONE
git clone --no-hardlinks <lane> clone ; git -C clone commit (patched probe, scratch only)
python3 -B census/round-42/c2-counter.py --root <clone> --rev <rev> --scratch <dir>
   -> control (tip)   : SUMMARY cases=37 pass=37 fail=0 … patches=3/3 tool_sha=9ddd596b98fb
   -> probe           : SUMMARY cases=37 pass=37 fail=0 … patches=3/3 tool_sha=bcc752e86bc7
GNUPGHOME=<scratch>/gnupg gpg --batch --quick-generate-key …   -> timed out (agent_genkey); not needed for the findings.
GNUPGHOME=<scratch>/gnupg gpgconf --kill all    -> rc=0 (stopped the gpg-agent this seat started)
```

## Verdict

**RED for the stated safety invariants; GREEN for the argument, path and environment surface.**

- **Repository-controlled code execution: FAIL.** The landed tool executes a program named in the target repository's own
  `.git/config`, in two ways: `gpg.program` on a signed commit in the prereg's history (S1), and `remote.<n>.uploadpack`
  or `core.sshCommand` through a lazy fetch in a partial clone (S2). Both were observed with marker files, not inferred.
  The precondition is write access to that repository's `.git/config`. The clone does not transport it, but a candidate or
  sibling that can write a lane's `.git/config` can drive the tool, and the tool's own docstring says it "never" executes
  repository-controlled code.
- **Writes: partial FAIL.** Non-partial repositories are untouched (F1, F2b, H4). A partial-clone run writes a pack and
  fetches blobs from the promisor remote (S2, F3).
- **Fail-open verdicts: FAIL (two).** A spoofed red control via a symlink (S3) and a symlinked prereg validated by its link
  text (S4) both pass clean.
- **Termination and budget: partial.** No internal deadline (S6). Memory is ~5× the population blob (S7). `--selftest`
  leaves repositories on SIGTERM (S5).
- **Holds:** `--rev`/`--root`/`--prereg` argument hostility (S11–S13), the environment whitelist (S9), the hostile-config
  keys tested in S8 (no pager, fsmonitor, diff driver, hook run), the Counter/Population/Control path traversal and oversize
  inputs (S16), and the selftest scope on normal exit (S15).
- **Measurement:** the frozen C2 counter reads the defective tool and the probe identically, `cases=37 pass=37`, so C2's
  green status is not evidence of safety (S17).

## Routed to L1 (findings, not edits; no frozen file changed)

1. **S1 and S2 (High).** Add `--no-show-signature` to both `git log` calls in `freeze_rev` and `dispatch_findings`, and
   `GIT_NO_LAZY_FETCH=1` to `Repo.env`. Scratch probe verified: S1 `exec_fired=no`; S2 `rc=2`, `executed: False`; C2 counter
   still `37/37` on the probe (receipt end). Changing the tool needs the L1's own landing and a re-score.
2. **S3 (Medium).** Add `is_symlink` to the `Control` branch (probe `CONTROL-SYMLINK`).
3. **S4 (Medium).** Add a prereg symlink check (not probed).
4. **S5 (Low).** A SIGTERM handler in `--selftest` (probe: residue 0).
5. **S6/S7 (Low).** A caller deadline and a population size cap are needed; neither is in the tool.
6. **S17 (named limit).** The frozen C2 target has no leg for S1–S5 and should say so in the round lesson; a future counter
   needs an exec-marker leg (fixture with a `gpg.program` marker) and a symlink-control leg.

## Limits of this review

- Not tested: `includeIf`/`include.path`, `info/grafts`, `gpg.ssh.program`, `core.askPass`, SIGKILL, Windows, and hooks
  firing by trigger (none is invoked by the tool's subcommands per the code, not per a fixture).
- The gpg signed-commit fixture is hand-written (`gpgsig` with a dummy signature). The execution is `git`'s own verification
  call, which is the point.
- The probe is a scratch copy with four small edits, scored once by the frozen counter; it is advice, not a landing.

## Tooling

No tool installed or upgraded. `git` 2.56.0 and `gpg` were used read-only through `git`. Nothing was written to `~/.local/bin`
or any PATH directory. No pacman transaction. Scratch dir deleted before yield (after copying receipts here).
