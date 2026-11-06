# S74ExecEvade — r74 w1: C1 gate byte-truth evasion (leaf seat, falsification)

Read census/round-74/preregistration.txt (frozen); lane HEAD 8fe48c86. Ran the gate+writer extracted from ec13ba7f,
byte-identical to the lane (sha256 3162de98… gate, 70bbf1c2… writer). No tool installs, no pacman.
Frozen C1(i) reproduced from my own bytes: python3 -B census/round-74/c1-gate-counter.py --gate $S/gate/souji-pre-report-gate.sh
--work $S/c1-cand → SUMMARY rows=9 mismatches=0 errors=0 / EXIT=0 (counter-candidate.txt); base gate 43cd74b →
mismatches=3 (GF1 GF2 GF3) / EXIT=1 (counter-base-gate.txt). The arithmetic holds; the coverage does not.
Probe: python3 -B .ufo/waves/round-74/w1/S74ExecEvade/probe.py --gate-copy $S/gate --work $S/work6 — 20 routes, 60 s
timeout, truth = sha256(worktree bytes) vs sha256(git cat-file blob HEAD:<path>) in a sanitised env.
SUMMARY rows=20 CAUGHT=13 FORGERY=5 FORGERY-MODE=1 HONEST-PASS=1 (every ROUTE line: probe-transcript.txt).
FORGERY — gate rc=0, check-clean=PASS, tracked bytes differ (wt=ac87f7fd vs head=0ce09c65):
  h-envconfig-filter — GIT_CONFIG_COUNT=2 injects core.attributesFile + filter.fix.clean; env only, no repo byte written
  h2-envconfig-filter-infoattrs — GIT_CONFIG_COUNT filter.fix.clean + .git/info/attributes
  h3-repo-filter — .git/config filter.fix.clean + .git/info/attributes (gate-output-h3-repo-filter.txt)
  f-info-exclude, f2-gitignore — untracked new.txt hidden from `status -uall` by .git/info/exclude / committed .gitignore
  n-filemode-config — core.fileMode=false + chmod 755: index 100644 vs worktree 755, bytes equal → FORGERY-MODE
CAUGHT (gate rc=1): a-v4-forge, b-split-forge, b2-split-linked, c-assume-unchanged, c2-skip-worktree, d-fsmonitor-empty,
  e-checkstat-minimal, g-fifo, g2-symlink-dev-zero, i-ident, k-gitlink-mode, l-core-worktree, ctl-gd1. HONEST-PASS ctl-honest.
  No HANG: g-fifo and g2-symlink-dev-zero both exited < 60 s with clean=FAIL.
HIGH — gate check 4 calls only _truth_refusal (tools/souji-pre-report-gate.sh:50); the r71 conversion guard _witness_refusal
(tools/souji-receipt-write.py:206, used by the receipt path at :597,:711) is never consulted. Measured on the h3 fixture:
_witness_refusal → "RECEIPT-FILTER-DRIVER-SET … (fix)"; _truth_refusal → None.
HIGH — tools/souji-pre-report-gate.sh:4 unsets no GIT_CONFIG_COUNT/GIT_CONFIG_KEY_n/GIT_CONFIG_VALUE_n: h1/h2 need nothing
on disk, the caller env supplies core.attributesFile and a clean driver that discards the edit.
MEDIUM — the byte check skips exactly the paths its own status lists (tools/souji-receipt-write.py:283): repo-local
core.fileMode=false makes the gate's status clean while the pinned inner status lists the path, so a mode change is never
hashed (n-filemode). MEDIUM — untracked payloads: .git/info/exclude is agent-writable and untracked, a committed
.gitignore hides new bytes; check-clean=PASS while the worktree holds bytes absent from HEAD (outside the frozen
tracked-path predicate, inside "No lane changes may remain", gate:37-38).
LOW — gate:43 folds status stderr into $status, so a warning counts as a change (d-fsmonitor-empty: detail-clean:
warning: Empty last update token.) — over-refusal, never a forgery. LOW — b-split-forge: rewriting sharedindex.<hash>
alone is rejected by git (fatal: broken index, expect <hash> …); after repairing the link extension (b2) git accepts
the file but still reports the entry modified.
Positive — e-checkstat-minimal (repo core.checkStat=minimal + trustctime=false) fooled BOTH status reads; the hash
comparison caught it (detail-clean: RECEIPT-WORKTREE-STAT-CONCEALED … (a.txt)): the frozen mechanism works while status
is the only concealment, and fails wherever check-in conversion is attacker-controlled.
Wrote under .ufo/waves/round-74/w1/: S74ExecEvade.md; S74ExecEvade/{probe.py, probe-transcript.txt, counter-candidate.txt,
counter-base-gate.txt, gate-output-h3-repo-filter.txt, repro-{h-envconfig-filter,h2-envconfig-filter-infoattrs,h3-repo-filter,
f-info-exclude,f2-gitignore,n-filemode-config}.sh}. Scratch /fast/scratch/hyaku/souji-r74/S74ExecEvade removed.
