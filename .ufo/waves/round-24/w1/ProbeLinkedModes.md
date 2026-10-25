# ProbeLinkedModes — r25 `garbage` false-positive creation-mode matrix (souji r24 w1)

## Status
STATUS: PASS — the hypothesis holds in all 5 linked cells. Each one reads `garbage: 1` and `size-garbage: 0`, while the main worktree and every `--git-dir=<common>` read give 0. A causal check confirms that the empty private `refs/` directory is the only thing counted.

## Evidence
- Revision: lane HEAD `f9db2181647d91470a724a12d626bd6106805076` (the preregistration commit). Lane was read only; no lane files were written except this report.
- Tool: `git version 2.56.0` (host binary; nothing installed).
- Env: `LC_ALL=C GIT_CONFIG_NOSYSTEM=1 HOME=/var/tmp/souji-r24-ProbeLinkedModes/home`. Repo: `git init` + 1 commit on `main`, under `/var/tmp/souji-r24-ProbeLinkedModes/`.
- Script `matrix.sh` sha256 `bc1a82a8b0b7fe90e01f954db630a383fdd8e6ab7df1c96dc0231f4073e0092b`. Output `out.txt` sha256 `0d4036e0bcb3f4022d60c2b6c4bb4d3130b08e67cd504b8a4a3f155abe452c6e`. Both were removed with the scratch dir; the excerpts below are copied from that run.
- Flag spelling: `git worktree -h` gives `[--orphan] [(-b | -B) <new-branch>] <path> [<commit-ish>]`. `--orphan` is a bare flag. The task wording `git worktree add --orphan br-o1 <path>` gives `fatal: option '--orphan' and commit-ish cannot be used together` (exit 128). The working spelling is `--orphan -b br-o <path>` (exit 0), which matches the r25 entry's `--orphan -b <branch>`.

Per cell, with `P=/var/tmp/souji-r24-ProbeLinkedModes` and `C=$P/repo/.git`:

| cell | `-C <wt>` garbage / size-garbage | `--git-dir=$C` garbage / size-garbage | private gitdir `ls` |
|---|---|---|---|
| main | 0 / 0 (no stderr) | 0 / 0 | COMMIT_EDITMSG HEAD MERGE_RR config description hooks index info logs objects refs rr-cache |
| `--detach` | 1 / 0 | 0 / 0 (no stderr) | HEAD ORIG_HEAD commondir gitdir index logs refs |
| `-b br-b` | 1 / 0 | 0 / 0 (no stderr) | HEAD ORIG_HEAD commondir gitdir index logs refs |
| `--orphan -b br-o` | 1 / 0 | 0 / 0 (no stderr) | HEAD commondir gitdir index refs |
| `--detach` + commit | 1 / 0 | 0 / 0 (no stderr) | COMMIT_EDITMSG HEAD MERGE_RR ORIG_HEAD commondir gitdir index logs refs |
| `-b br-bc` + commit | 1 / 0 | 0 / 0 (no stderr) | COMMIT_EDITMSG HEAD MERGE_RR ORIG_HEAD commondir gitdir index logs refs |

Stderr from the `-C <wt>` read. There is exactly one line per linked cell:
```
warning: garbage found: /var/tmp/souji-r24-ProbeLinkedModes/repo/.git/worktrees/wt-detach/refs
warning: garbage found: /var/tmp/souji-r24-ProbeLinkedModes/repo/.git/worktrees/wt-b/refs
warning: garbage found: /var/tmp/souji-r24-ProbeLinkedModes/repo/.git/worktrees/wt-orphan/refs
warning: garbage found: /var/tmp/souji-r24-ProbeLinkedModes/repo/.git/worktrees/wt-detachc/refs
warning: garbage found: /var/tmp/souji-r24-ProbeLinkedModes/repo/.git/worktrees/wt-bc/refs
```
In every linked cell, `find <priv>/refs` printed only the directory itself, so the private `refs/` is empty. The main read was repeated after all 5 linked worktrees existed and still gave `garbage: 0`, `size-garbage: 0`.

Extra probes:
- Causal check: `rmdir repo/.git/worktrees/wt-detach/refs`, then `git -C wt-detach count-objects -v`, gives `garbage: 0`, `size-garbage: 0` with no warning. `git status` still works (`## HEAD (no branch)`) and does not recreate `refs/`.
- Reftable variant: `git init --ref-format=reftable` + `worktree add --detach`. The linked read gives `garbage: 1`, `size-garbage: 0` and `warning: garbage found: .../rt/.git/worktrees/rt-wt/refs`. The `--git-dir=<common>` read gives 0 / 0. The private gitdir contains HEAD, commondir, gitdir, index, `refs` (non-empty, size 10) and `reftable`. Only `refs` is reported.

## Findings
1. Hypothesis holds in all 5 cells: `garbage: 1` and `size-garbage: 0` for `--detach`, `-b`, `--orphan -b`, `--detach`+commit and `-b`+commit (table above).
2. Main worktree: holds. It reads 0, both before and after the linked worktrees were created.
3. `--git-dir=<common dir>`: reads `garbage: 0` in every cell. This is consistent with the frozen C1 tool contract (preregistration, C1 tool CLI section): "count-objects runs against the resolved COMMON git dir, so a linked worktree path reports the common-dir figure". It is also consistent with C1 case 4.
4. Spelling defect in the task wording: `--orphan <b>` is not a valid spelling on 2.56.0 (fatal, exit 128). The r25 entry's own `--orphan -b <branch>` is the correct form. Any fixture written from the task wording would fail in that cell for a reason unrelated to `garbage`.
5. Entry statements I could check against this run's bytes:
   - Correct: `COMMIT_EDITMSG` and `MERGE_RR` appear only after a commit; `--orphan` has no `logs` and no `ORIG_HEAD`; `refs` is present in every linked cell.
   - The entry's "the counted entries are **directories**" is confirmed. The counted `refs/` is in fact empty in the files backend, which is stronger than the entry's "not that the directories are empty" caveat.
6. Not established by this run (`[INFERENCE]` or out of scope):
   - The `path.c` / `common_list` source mechanism. No source was opened this run.
   - The fleet's "four linked worktrees have no `refs`" statement. The fleet was not probed (HARD BOUND).
   - Behavior under other git versions. Only 2.56.0 is installed.
7. Admission bearing: this run is lane-produced evidence for the r25 entry's measured claim (items 1–2 of its Claim), on git 2.56.0, with an added causal control. Its provenance line cites shokuknow S141 (`lanes/souji/round4/fixtures/r25-garbage-matrix.py`). Per the preregistration, those rows are "not appendable as-is", so the entry would need its `source:` and `verified-at:` lines rebased onto this lane's evidence.

## Attack log
- A1 (possible counter weakness, reported, not changed): frozen C1 case 4 expects raw `git -C <linked> count-objects -v` to read `garbage: 1`. This holds on 2.56.0 in both files and reftable backends. The witness depends on git creating the private `refs/`: if a future git stops creating it, or a seat `rmdir`s it, the raw read drops to 0 (shown by the causal check), and case 4's witness half fails even though the tool is correct. This is a version dependency, not a way to game the counter.
- A2: a stub that always prints `garbage=0` passes the tool half of case 4. Only the raw-read witness half of case 4 and the control cases 2–5 (case 8) reject it, so case 4 alone does not discriminate. Its discriminating power comes from the witness half.

Scratch `/var/tmp/souji-r24-ProbeLinkedModes/` removed after the run. No tools installed or updated. No labrat dispatched.
