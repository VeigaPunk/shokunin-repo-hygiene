# S66CriticClaims — round 66 critic report (summary)

Full evidence and per-item tables: `.ufo/waves/round-66/w1/S66CriticClaims/critic.md`. Read-only seat; no lane file, no git mutation, no install.

## Numeric results measured

- Matrix rows: 28. Base forgeries 8 (E1–E6, MOD2, MOD3). Base honest accepts 5 (A, B, T4, V2, SY1). SY3 refused by base.
- C1 do-nothing: new_forgeries=8, class_mismatches=8, EXIT=1. C2 do-nothing: rows=5 findings=1 (s5), EXIT=1.
- M-ENV (base writer, 3 lines removed): r66 env=0 → SCOPE-OVERREACH s2 (findings=1); r65 env=1 → findings=0. Kill reproduced conditional on S2_AFTER in candidate SKILL.md.
- Writer probes, base writer, clean scratch lane (no --allow-dirty): W0 clean rc 0; W1 tracked mode-only change rc 2; W2 same + GIT_COMMON_DIR (common config core.fileMode=false) rc 0, receipt written; W3 GIT_CONFIG_PARAMETERS via git -c child rc 0; W4 benign GIT_CONFIG_GLOBAL rc 0.
- Pre-run setuid-only tracked change (committed 644, chmod 4644): `git status --porcelain` 0 lines.
- Byte checks: attempt-1 and attempt-2 Target/Kill lines identical; controls' blobs unchanged between their commit and freeze 02cc6609 (C1 7c0fd032…, C2 e8b1fd1b…).

## Findings (severity order)

1. **C1 "routes" universal is false at base (HIGH).** GIT_COMMON_DIR carrying core.fileMode=false makes the base writer accept a tracked mode change (W2). No matrix row, not in the candidate design text. C1 claim unprovable as worded.
2. **C2 is not separable from C1 (HIGH; AXES.md line 31).** s5 and the M-ENV target read the candidate writer's needles. Not named in the prereg's L1–L5.
3. **Frozen-text contradiction on E3 (HIGH).** L3 says presence of GIT_CONFIG_GLOBAL is refused; the frozen E3 class is `lane worktree is dirty`. A presence refusal would fail C1 (class_mismatches=1 by findings_for).
4. **setgid unmeasured (MEDIUM).** Claim says "setuid, setgid and sticky included"; matrix has MOD2 and MOD3 only. Q59 R4 does not scan "full".
5. **C2 cannot falsify s5 breadth (MEDIUM; M9 class, not named).** A writer with E1–E6 refused and W2 open scores findings=0.
6. **Honest-row set incomplete (MEDIUM).** git -c propagates GIT_CONFIG_PARAMETERS (W3 accepted at base; refused by candidate design); benign GIT_CONFIG_GLOBAL (W4) unexercised; L2 host-excludes cost unobservable on this host; pre-run setuid (P-B) accepted and unnamed.
7. **M10 repair tested on one witness; changed clause's other side untested (MEDIUM).** Q53 not met; a `return <name>` or multi-line refuse shape would read dead.
8. **Frozen-file in-place edit in history (LOW-MEDIUM).** Commit 01bc1e16 edited the attempt-1 prereg (+8/−1); restored by a81280e1 (blob = 5d17a5de). Disclosed only as restoration.
9. **Stale note in frozen c2-statements.tsv (LOW).** s4 note says absent at base; base SKILL.md contains it (grep count 1).
10. **Control reproducibility (LOW).** C1 control new slot cites a scratch file removed by trap; sha matches base blob.

## Round-65 routed items

Covered: E4–E6 (env redirects); M10 (repaired, single witness); M11 partly (SY3 row, base already refuses; control cannot fail); M12 partly (setuid, sticky; no setgid).
Partly: ignore/config route fix (E1–E3 only; ignore routes and GIT_COMMON_DIR open); if-False dead-token (L4 named).
Routed again: F4 env-value redaction (no reason); F6 clean_env isolation (no reason; host ~/.config/git/config present); N4 dual-seed (no reason); TSV anti-launder (no reason); F5 excerpt bound; operator L0 (`:(top)`).

## Verdicts

- **C1 operability:** unprovable as worded. Would-admit if narrowed to E1–E6 and setuid/sticky, E3 reconciled, and W2, P-B and honest-row gaps named. Single falsifier: W2.
- **C2 calibration:** would-reject (separability; s5 breadth). Single falsifier: E1–E6 refused + W2 open → findings=0 with s5 false. M-ENV kill: would-admit conditionally.

## Recommended for L1 before candidate scoring

Name items 1–10 above in the round report and lesson. Do not edit frozen files. Run the Q59 instrument on this prereg rather than relying on the source reading.

No tool installed. Scratch removed.
