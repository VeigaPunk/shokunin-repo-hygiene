# S61ExecC2Fixture — C2 receipt-fixture mutant kill-power (souji r61 w1)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin @ rev `c7228424c3919ecf142bab1aec8181722d86467b`
(lane HEAD == the declared base-tool-rev; worktree `tests/fixtures/r60-receipt-write.py`
sha256 `d5291501e8ce828e26aabaea69853fe3223297f2d5ac249aee62f73bb294c114` ==
`git show c7228424…:tests/fixtures/r60-receipt-write.py` — verified byte-identical).
No tools installed or upgraded (system python3 + git sufficed); no pacman transactions.

## Delivered (absolute paths; full bytes, production paths untouched)

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-61/w1/S61ExecC2Fixture/r61-receipt-write.py`
  sha256 `fc4b48d35b45a1fd7251df4fc408f30905a72e414465e74f9cd311ad7e25161d` — r60 fixture bytes + cases 9/10 (10-case matrix; all 8 r60 case bodies, both stub controls and their expected failsets byte-compatible).
- `…/S61ExecC2Fixture/mutant-worktree-hash.py` sha256 `ff69329e1952a146237588ed74c7a084020d69b3f1e50df5ba1a13cc2c33c57d`
- `…/S61ExecC2Fixture/mutant-direct-write.py` sha256 `cc5d71ab1ed3aab2c2eb312914a7f61b4561db8afc8c38d187c9c2f44992f514`
- `…/S61ExecC2Fixture/c2-counter.py` sha256 `49e8ae8102070b1b456fbdd78acf0ad024e3a2d6974374f58331f97abac00660`
- `…/S61ExecC2Fixture/{r61-receipt-write,mutant-worktree-hash,mutant-direct-write}.diff` — exact line-level diffs vs the r60 bytes
- `…/S61ExecC2Fixture/receipts/{honest-r61,mutant-worktree-hash-r61,mutant-direct-write-r61,mutant-worktree-hash-r60,mutant-direct-write-r60,base-arm}.txt` — each `rev= / instrument= / instrument_sha256= / command= / output-begin…output-end / EXIT=`

## r61 fixture deltas (all scaffolding; case bodies 1–8 and stubs untouched)

Diff hunks (see `r61-receipt-write.diff`): docstring 8→10 case header + usage line + case list + exit doc; `import json`; constants `CONCEALED_BODY` (`#!/bin/sh\necho instrument-concealed\n` — different bytes AND length vs `INSTRUMENT_BODY`), `CASE_10_MAX_BYTES="2097152"`, `CASE_10_CMD` (5×`head -c 200000 /dev/zero; sleep 0.4` ≈ 2.05 s), `READER_SRC`; `CASE_NAMES` + 9/10; `case_9`/`case_10` inserted before `CASE_FUNCS`; `CASE_FUNCS` + 9/10; `range(1, 9)`→`range(1, 11)` (3 sites); run_matrix docstring; main banner/description/`f=10-p`/`SUMMARY cases=10`/`p == 10`.

- case_9 `concealed-divergence`: `git update-index --skip-worktree tools/instrument.sh`, overwrite worktree bytes, assert `git status --porcelain` prints NOTHING, run tool → EXPECT rc=2, OUT absent, no temp siblings.
- case_10 `partial-visibility`: reader subprocess (20 ms `os.stat` polls; ready-file handshake so sampling starts BEFORE the tool; stop-file after tool exit; JSON samples). EXPECT rc=0, OUT last line `EXIT=0`, every sample nonexistent-or-exactly-final-size; zero samples → one re-run on a fresh repo, persistent zero-sample = FAIL with reason (never a silent pass).

## Mutant deltas (full r60 writer byte copies; docstrings left describing honest behavior)

- `mutant-worktree-hash` (diff vs r60 writer, 20 diff lines): dropped `digest = hashlib.sha256(blob.stdout).hexdigest()` after the `cat-file blob` absence check; dropped `if wt_bytes != blob.stdout: refuse(...)` and replaced with `digest = hashlib.sha256(wt_bytes).hexdigest()` after the worktree read.
- `mutant-direct-write` (111 diff lines): header bytes assembled before `Popen`; OUT opened on the FIRST captured chunk and every chunk written+flushed straight to OUT (no temp, no `os.link`); overflow path closes+unlinks its own OUT before refusing (keeps case_5's no-residue contract); receipt construction + entire temp/`os.link`/dirfsync publish block deleted; final `body` + `EXIT=` appended to OUT directly.

## Exact commands (run in scratch `/fast/scratch/hyaku/souji-r61/S61ExecC2Fixture/`)

```
python3 -B build/c2-counter.py --root $LANE --rev c7228424c3919ecf142bab1aec8181722d86467b --work work
python3 -B build/c2-counter.py --root $LANE --rev c7228424c3919ecf142bab1aec8181722d86467b --work work-base --base-arm
```
Counter internally: extracts r60 fixture via `git show <base-tool-rev>:tests/fixtures/r60-receipt-write.py` (read-only), runs each fixture×tool pair (`python3 -B <fixture> --tool <tool> --work <arm-dir>`), parses `CASE`/`SUMMARY` lines, writes receipts. Lane git usage strictly read-only (`rev-parse`, `show`, `cat-file`, `status`); `update-index --skip-worktree` ran only inside throwaway fixture repos created under `--work` (toplevel equality asserted by the fixture before first commit; throwaway repo-local identity).

## Observed outputs (final counter bytes, sha 49e8ae81…)

Normal run — **EXIT=0**:
```
ARM honest                 fixture=r61-receipt-write.py tool=souji-receipt-write.py cases=10 pass=10 fail=0 failed=[] stubs=REJECTED,REJECTED rc=0
ARM mutant-worktree-hash-r61 … cases=10 pass=9 fail=1 failed=[9] … rc=1
ARM mutant-direct-write-r61  … cases=10 pass=9 fail=1 failed=[10] … rc=1
ARM mutant-worktree-hash-r60 … cases=8 pass=8 fail=0 failed=[] … rc=0
ARM mutant-direct-write-r60  … cases=8 pass=8 fail=0 failed=[] … rc=0
killed_old=0 killed_new=2 killer-cases={'mutant-worktree-hash': True, 'mutant-direct-write': True}
SUMMARY honest-pass=10 honest-fail=0 killed_old=0 killed_new=2 stub-always-write=REJECTED stub-always-refuse=REJECTED EXIT=0
```
Base-arm (do-nothing) run — **EXIT=1 red as designed**: honest 10/10 unchanged; both mutant arms on the extracted r60 fixture pass=8; `killed_new=0` printed; summary `…killed_old=0 killed_new=0 stub-always-write=REJECTED stub-always-refuse=REJECTED EXIT=1`.

Receipt evidence: honest r61 run shows `CASE 1..10 pass`, control always-write failed [1..10] → REJECTED, always-refuse failed [1,3,10] → REJECTED (assertions are the r60 supersets {2,4,5,6,7,8}⊆failed and 1∈failed). Mutant r61 receipts show exactly the designated killer case failing (9 / 10); mutant r60 receipts show 8/8 pass on the committed base bytes — the named r60 gap, demonstrated.

## Named limits

- partial-visibility timing: mutant kill relies on chunk cadence (partial OUT states persist ≥0.4 s vs 20 ms polls) — robust, not racy; honest pass relies on the writer's `os.link` atomic publish, not timing. No flake observed across the four counter invocations run (two normal, two base-arm; each runs honest case_10 once). Zero-sample risk handled by readiness handshake + single re-run; persistent zero-sample fails loudly with reason.
- Disclosed run history: the first base-arm invocation crashed with `KeyError: 'mutant-worktree-hash-r61'` (counter bug: base-arm has no `-r61` arms). Fixed in `c2-counter.py` (killed_new computed from the r60 arms in base-arm mode); the delivered counter sha 49e8ae81… is the fixed bytes, and all outputs above come from the final counter.
- Counter rc: 0 iff honest pass=10 fail=0 ∧ killed_old=0 ∧ killed_new=2 ∧ both stubs REJECTED ∧ killer-case attribution holds; `--base-arm` is red by construction (EXIT=1).
- Mutant docstrings still describe honest behavior (bytes-only delta policy); the .diff files are the authoritative behavior description.
- case_10 passes `--max-bytes 2097152` (5×200000 body must not trip the bound; the bound remains case_5's subject).
- The counter dies (rc 64) if a fixture emits no SUMMARY line or revs are not full-40 commits — loud, not silent.

Blockers: none.
