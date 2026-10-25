## Status
STATUS: FAIL — C3 instrument and durable receipts are absent; ignore masks rather than resolves tracked wave residue.

## Evidence
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --short --untracked-files=all` → modified tracked `.ufo/waves/round-26/w1/*` paths (including reports and scripts), alongside untracked round-28 census work.
- `read /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-wave-evidence-capture.sh` → not found; fixture `tests/fixtures/r28-wave-evidence-capture.sh` → not found.
- `read .../census/round-26/waves` → not found.
- `.gitignore` lines 1-3: `.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/`.

## Findings
1. **Durable evidence: NO.** No capture tool, fixture, nor round-26 committable receipt observed. `.ufo/waves/` ignore does not unmodify tracked content: status lists modified tracked files. The unresolved tracked r26 changes falsify “revert after capture” as well as durable-capture completion. Location: lane status; absent `tools/souji-wave-evidence-capture.sh`, `tests/fixtures/r28-wave-evidence-capture.sh`, and `census/round-26/waves/`.
2. **Clean-worktree meaning: weakened.** The ignore rule suppresses *all* `.ufo/waves/` content, not only generated capture runtime/evidence paths; round-28 operator reports and any untracked round work stored there can disappear from ordinary status. Meanwhile census/operator-sweep and pycache are broad but declared runtime paths; no evidence here demonstrates they are exclusively runtime. Untracked census/round-28 files remain visible in `--untracked-files=all`, showing the check does not generally hide census work. Location: `.gitignore:1-3`; status output.
3. **Manifests tamper-evident: NO EVIDENCE.** No implementation or receipts to inspect/verify; cannot establish byte-exact copy, manifest verification, or resistance to manifest-and-payload co-tampering.
4. **Exit map/control: NO.** Required script and fixture are absent, so no declared exit mapping or failing tamper-negative control exists.

## Attack log
- Axes impacted: operability (C3) direct failure; calibration/coverage not assessed by this assigned attack. Smallest safe correction: deliver the specified bounded read-only capture tool and positive/tamper-negative fixture, produce and independently verify durable receipts for rounds 26/27, restore tracked r26 wave files to HEAD, and narrow ignore behavior so only explicitly declared runtime/evidence-capture directories are hidden while operator/untracked round work remains visible. Do not treat `.gitignore` as evidence capture or as a substitute for restoration.