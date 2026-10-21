STATUS: DONE — counter exclusion, selftest, D2 digests, and agreement-record gap are grounded in the requested source and records.

# Findings

- `census/round-18/leak-count.py:141-175` excludes exactly its own PID (`{os.getpid()}`), not its ancestors; it scans same-UID `/proc` entries and counts qualifying residue classifications. The accompanying repair record explains that ancestor exclusion hid a compositor residue and states the counter spawns no scan children (`census/round-18/counter-exclusion-repair.json:4-6`).
- The selftest first exercises dangling-path/argv recognition, path-component boundaries, literal ` (deleted)` cwd/fd suffixes, and a genuinely deleted open fd (`census/round-18/leak-count.py:207-306`). It then starts a blocked `cat` FIFO reader under `/var/tmp`, removes its FIFO directory, and requires exactly one new count for that PID and one additional `argv-path-gone` classification; it cleans up its worker (`:324-364`). The committed repair record reports `--selftest` exit 0 and `before=66`, `after=67`, `added_pid=1873890`, `pass` (`counter-exclusion-repair.json:7-9`). This report did not rerun the selftest.
- Exact D2 byte facts:
  - At `2d4c7f84b969ee0485d657b86f7860af01bbf3cf` (`2d4c7f8`), `census/round-18/leak-count.py` SHA-256 is `a26530199434ecddf4b36d2513730765bb0ae7487fa3c007f9c04d33244ebb3b`.
  - `tools/souji-proc-census.sh` SHA-256 is `37c3316a1fd8cdda18cbefdc7692d3d3f388e5783e8fe19085f5d932a8ceba64` at both `2d4c7f8` and `4800fd7`. The `4800fd7` final-verification record has this tool digest and the pre-fix counter digest `f1d1f9b482cdde5ea12114de234b0f0701dcb4ceb9fd62fd9a4119ee85fd5972` (`census/round-18/final-verification-4800fd7.json:3-9`).
- The two agreement snapshots are:
  1. `census/round-18/proc-agreement-final.json`: measured at `4800fd79488e5f2c11a18117958f104171d85dc8`; both pairs are tool 66 vs counter 65, with stable tool-only PID 1659 and `pass: false` (`:2-8,143-152,153-157,292-308`). Current working-tree JSON SHA-256: `a43039e37959553fee095bd0e7a5a22199c443906585e204feeff4b93485dc01`.
  2. `census/round-18/proc-agreement-counterfix.json`: names `4800fd7` as `base_code_commit`; both pairs are 66/66 with no differing PIDs and `pass: true` (`:2-8,145-151,153-157,293-304`). Current working-tree JSON SHA-256: `a162f5409ae0e4ca36fb2abc087bc652ce1cbbd5d5d850660f193c9379654d87`.
- The post-fix agreement whose counter digest D2 specifically requires is `proc-agreement-counterfix.json`: its complete top-level key list has no counter commit or digest field, and it records only the tool base plus the textual fix. The pre-fix `proc-agreement-final.json` also has no counter digest field. `counter-exclusion-repair.json` points to `2d4c7f8` as `measured_commit` and to the counterfix agreement, but supplies no digest (`:2-12`). This matches the routed D2 finding (`corpus/lessons/round-18-verifier-spotcheck.md:146`).

# Evidence

- Source behavior and selftest: `census/round-18/leak-count.py:141-175,207-306,324-364`.
- Repair provenance and recorded selftest outcome: `census/round-18/counter-exclusion-repair.json:2-12`.
- Agreement results: `census/round-18/proc-agreement-final.json:2-8,143-152,153-157,292-308`; `census/round-18/proc-agreement-counterfix.json:2-8,145-151,153-157,293-304`.
- Historical digest record and routed D2: `census/round-18/final-verification-4800fd7.json:3-9`; `corpus/lessons/round-18-verifier-spotcheck.md:145-146`. Round-19 preregistration labels D2 as the counter digest pin (`.ufo/waves/round-19/preregistration.txt:66-70`).

# Commands run

- Targeted `grep` searches located the relevant counter, D2, and digest references; they were used only for discovery, not as semantic proof.
- Read-only digest calculations: `git show 2d4c7f8:<path> | sha256sum` for the counter and proc-census tool, and `git show 4800fd7:<path> | sha256sum` for the tool and pre-fix counter. Results are recorded above.
- `sha256sum` over the two agreement JSONs and repair JSON; the two agreement snapshot hashes above identify current working-tree bytes. Repair JSON SHA-256: `faed4ceb433b3aa1b096c47b765f25b9038215e58e7d2193b362b92f38cddad3`.
- No selftest, census, fixture, or other runtime check was run.

# Contract compliance

- Wrote only this scoped report; no subagents, installs, git/jj mutations, live census, process signals, or network access. Did not open the operator-owned sweep directory.
- The `lsp` device is not mounted (`xd://lsp` returned “No such tool”); targeted search was followed by direct reads of the relevant source and JSON sections. No grep result is presented as semantic proof.
