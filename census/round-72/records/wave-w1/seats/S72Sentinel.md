# S72Sentinel — fail-closed / security review of the lane-base writer (souji r72 w1)

VERDICT: 1 forging route survives (HIGH: .git/index stat cache); 13 attribute/config routes are refused; C2's five FW shapes independently reproduce (lane-base refuse 5/5, pre-r71 base accept 5/5).

Commands (from the lane root; <S>=/fast/scratch/hyaku/souji-r72/S72Sentinel; lane writer sha b7790001…244d at 0bf098dd; base writer sha 118597e0…e71f from `git show 8b9345b1:tools/souji-receipt-write.py`):
1 `python3 -B .ufo/waves/round-72/w1/S72Sentinel/s72-probe.py --work <S>/w4` (17 routes; every line in S72Sentinel/probe-transcript.txt)
2 `python3 -B census/round-72/probes/fw-shapes-probe.py --work <S>/fw4 tools/souji-receipt-write.py`, then `--work <S>/fwb4 <S>/writer-base.py`
3 `S72_WRITER=census/round-72/battery/{WM3,WM8}.py python3 -B .ufo/waves/round-72/w1/S72Sentinel/s72-probe.py --work <S>/w4w{3,8} nested-fww-prerun`

HIGH — index stat-cache forge (deterministic; no --allow-dirty, no driver, no timing race). Decisive lines:
`PROBE route=index-stat-inrun pre_status=<clean> rc=0 wrote=1 truth_mismatch=tools/counter.py post_status=<clean> verdict=FORGERY`
`… route=index-stat-prerun … verdict=FORGERY`; `… route=index-stat-instrument-inrun … truth_mismatch=tools/instr.sh verdict=FORGERY`
Receipt: instrument_sha256=8f513b9f… while worktree tools/instr.sh sha=fbc4b960…; counter.py worktree "counter v2" vs HEAD blob "counter v1"; index OID still the HEAD blob; status empty.
Exploit: the wrapped command rewrites .git/index per-entry stat (dev/ino/mode/uid/gid/size/ctime/mtime, blob OID kept, SHA-1 recomputed, index mtime moved past the entry) after writing the forged bytes; git status/diff then report clean.
Writer evidence: tools/souji-receipt-write.py:482 (flags), :492/:602 (witness), :605-606 (post reads) never hash worktree content; the content snapshot is built only under --allow-dirty (:510); the instrument is compared pre-run only (:549-552). This falsifies the bound of the declared named limit :95-97 (same whole second).
Matrix: no row — CASE_SPECS/inrun_argv have no index-stat kind, so the r72 matrix cannot catch it. Proposed rows FX1 in-run, FX2 pre-run index, FX3 in-run instrument: expect refuse (new class, e.g. RECEIPT-INDEX-STAT-FORGED), base_expect=accept (measured: the base writer accepts FX1/FX3).
Smallest remediation: post-run, hash every tracked worktree file and compare with rev:path (or with the index OID, which also catches an OID swap), and re-check the instrument bytes after the command.

Fail-closed (all rc=2, wrote=0, verdict=refused; class RECEIPT-FILTER-DRIVER-SET unless noted; forged same-size tracked file, driver configured):
(a) nested untracked tools/.gitattributes pre-run and in-run; nested committed-empty + self-erasing worktree attr: refused (drivers e,t) [nested-wt-prerun, nested-wt-inrun, nested-empty-committed-inrun, nested-fww-prerun]
(b) macro `[attr]m filter=t` + `tools/counter.py m`: refused. (c) filter.t.required with no command: refused at the status read — "cannot read worktree status … fatal: tools/counter.py: clean filter 't' failed".
(d) driver via include.path (repo config and config.worktree+extensions.worktreeConfig): refused. (e) drivers UP and foo.bar: refused.
(f) core.attributesFile=<file outside the repo> and attr.tree=<commit>: refused — the r71 named limits (S71CriticDiscern:14, S71ScoutSources:108-115) are closed, but no row binds either.
(g) in-run .git/config replaced by a symlink to a driver config: refused (the config read follows the link).
(h) also refused: regular→symlink typechange (status " T"); core.autocrlf=input + in-run CRLF rewrite (RECEIPT-STATE-CHANGED-DURING-RUN); core.ignoreStat (h bit caught by ls-files -v).

LOW — coverage: no row exercises (a)-(g) except the (a) FWw class, and all are refused only by the witness code :159-205 that WM3/WM4 delete. Nested FWw under mutants: lane base refuse, WM3 refuse (post-witness), WM8 FORGERY (check-attr --cached) — a nested row adds no kill over FWw but binds the subdirectory-relative pattern. Proposed FX4-FX7 (nested attr, macro, include/worktree config, attributesFile/attr.tree), base_expect=accept.
LOW — declared ignore limit confirmed: info-exclude-inrun rc=0 wrote=1 over an in-run untracked file matched by .git/info/exclude (declared :56-60; no row).
LOW — WM7 needs a non-repository route: 14 repo-state attempts all gave check-attr rc=0 (.gitattributes/info/attributes as a directory, chmod 000, dangling symlink, attr.tree missing/blob/subtree/HEAD, self/mutual/empty macros, NUL, bad UTF-8, CRLF lines, /proc/self/mem); /dev/zero and /dev/full hang the unbounded read (no subprocess timeout). S72ExecFailOpen's ../ev path-escape trigger is outside my probe set; not double-counted.

Files written: .ufo/waves/round-72/w1/S72Sentinel.md; .ufo/waves/round-72/w1/S72Sentinel/{s72-probe.py, idxcraft-run.py, idxcraft-instr.py, probe-transcript.txt}. No lane tracked file touched (the ` M SCORECARD.md` in `git status` is another seat's, written during the wave — not mine), no commits, no tool installs; scratch /fast/scratch/hyaku/souji-r72/S72Sentinel removed.
