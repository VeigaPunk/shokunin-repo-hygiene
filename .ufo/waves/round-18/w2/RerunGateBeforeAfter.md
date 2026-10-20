STATUS: DONE — The specified findings-count transition reproduces: 10 at b576341 → 0 at 5efb519.

# Attacked claim

C2 calibration: `tools/souji-landing-gate.py`, round 18, baseline `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` versus landed `5efb519f00075d958c3d1109ef6fcb24c487eb87`; compare the baseline run with `census/round-18/gate-pointers-before-b576341.json`.

# Findings

No actionable calibration defect found. The rerun’s baseline JSON is byte-identical to the committed record (`cmp` below), including every finding and counter. The landed revision reports zero findings.

The ten baseline findings, in emitted order:

1. `LG-DANGLING-PTR` — `census/operator-sweep-20261019/`; source `corpus/README.md:81`.
2. `LG-DANGLING-PTR` — `census/round-17/gate-replays-ddb7347.json`; source `SKILL.md:163`.
3. `LG-DANGLING-PTR` — `census/round-17/gate-replays-ddb7347.json`; source `SKILL.md:165`.
4. `LG-DANGLING-PTR` — `census/round-17/jj-receipts-ddb7347.txt`; source `corpus/README.md:216`.
5. `LG-DANGLING-PTR` — `census/round-17/jj-receipts-ddb7347.txt`; source `corpus/knowledge/jj-colocation-receipts.md:126`.
6. `LG-DANGLING-PTR` — `census/round-17/jj-receipts-ddb7347.txt`; source `corpus/knowledge/jj-colocation-receipts.md:148`.
7. `LG-DANGLING-PTR` — `census/round-17/jj-receipts-ddb7347.txt`; source `corpus/knowledge/jj-colocation-receipts.md:2`.
8. `LG-DANGLING-PTR` — `census/round-17/jj-receipts-ddb7347.txt`; source `corpus/knowledge/jj-colocation-receipts.md:44`.
9. `LG-DANGLING-PTR` — `tests/vault/vadv54-run/p/p6repo/.git`; source `SKILL.md:110`.
10. `LG-FROZEN-MEASURED` — `tests/fixtures/r14-cache-frozen/expected.json`; `measured_commit` `0123456789abcdef0123456789abcdef01234567` does not resolve.

These are also recorded at `census/round-18/gate-pointers-before-b576341.json:4-54`. The landed revision’s three explicit exclusions are documented in `corpus/pointer-exemptions.tsv:1-3`: the operator-owned output pointer, the intentionally absent nested `.git`, and the synthetic invalid measured-commit record. `tools/souji-landing-gate.py:559-606` makes an unresolved measured commit a round-18+ finding unless exempted; `:763-789` validates exemption rows; `:841-876` counts pointer exemptions and emits unresolved-pointer findings; `:970-999` evaluates the pointers and flags unused/stale exemptions.

The remaining baseline-only references were corrected rather than exempted: current `SKILL.md:165-167` names the committed replay expectation path, current `corpus/README.md:216` names `jj-receipts-base5fa6017.txt` and `jj-receipts-4f48343.txt`, and current `corpus/knowledge/jj-colocation-receipts.md:148` names those receipt outputs. A tree query confirmed the three replacement targets are present at 5efb519. The current operator-owned and nested-`.git` citations remain, accounted for by the exemption rows.

# Exact reruns and outputs

Both commands ran from `/var/tmp/souji-r18w2-RerunGateBeforeAfter/lane`, the detached clone at 5efb519, and wrote JSON only under that `/var/tmp` directory. The root/revision arguments below are the exact authorized ones.

Baseline command:

```sh
python3 tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 --round 18 --fleet-root /home/vgpnk/Projects/shokunin --json /var/tmp/souji-r18w2-RerunGateBeforeAfter/f1.json
```

Combined emitted output:

```text
LG-DANGLING-PTR	census/operator-sweep-20261019/	corpus/README.md:81 cites path absent at b5763415cc67
LG-DANGLING-PTR	census/round-17/gate-replays-ddb7347.json	SKILL.md:163 cites path absent at b5763415cc67
LG-DANGLING-PTR	census/round-17/gate-replays-ddb7347.json	SKILL.md:165 cites path absent at b5763415cc67
LG-DANGLING-PTR	census/round-17/jj-receipts-ddb7347.txt	corpus/README.md:216 cites path absent at b5763415cc67
LG-DANGLING-PTR	census/round-17/jj-receipts-ddb7347.txt	corpus/knowledge/jj-colocation-receipts.md:126 cites path absent at b5763415cc67
LG-DANGLING-PTR	census/round-17/jj-receipts-ddb7347.txt	corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at b5763415cc67
LG-DANGLING-PTR	census/round-17/jj-receipts-ddb7347.txt	corpus/knowledge/jj-colocation-receipts.md:2 cites path absent at b5763415cc67
LG-DANGLING-PTR	census/round-17/jj-receipts-ddb7347.txt	corpus/knowledge/jj-colocation-receipts.md:44 cites path absent at b5763415cc67
LG-DANGLING-PTR	tests/vault/vadv54-run/p/p6repo/.git	SKILL.md:110 cites path absent at b5763415cc67
LG-FROZEN-MEASURED	tests/fixtures/r14-cache-frozen/expected.json	measured_commit '0123456789abcdef0123456789abcdef01234567' does not resolve to a commit
SUMMARY	findings=10	checked_reg=27	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-18/ at b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
Exit status: 2
```

Landed command:

```sh
python3 tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 5efb519f00075d958c3d1109ef6fcb24c487eb87 --round 18 --fleet-root /home/vgpnk/Projects/shokunin --json /var/tmp/souji-r18w2-RerunGateBeforeAfter/f2.json
```

Output:

```text
SUMMARY	findings=0	checked_reg=33	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=4	status_lines=90	carry_heading=1	checked_reports=91
Exit status: 0
```

The baseline error is material context, not a count mismatch: the pre-wave revision has no round-18 reports. `tools/souji-landing-gate.py:970-973` explicitly preserves pointer findings when that carry check cannot evaluate; `:1001-1017` records the error and zero carry counters, and `:1019-1026` gives an errored evaluation exit 2. Thus the baseline has ten independently computed findings but does not have a clean gate exit. The stored baseline JSON is honest about both facts (`error` and `exit` at lines 1-3; summary at 78-90).

All JSON summary counters (baseline → landed):

| Counter | b576341 | 5efb519 |
|---|---:|---:|
| findings | 10 | 0 |
| checked_reg | 27 | 33 |
| checked_changed | 0 | 0 |
| checked_pins | 13 | 13 |
| checked_measured | 3 | 3 |
| checked_markers | 0 | 4 |
| status_lines | 0 | 90 |
| carry_heading | 0 | 1 |
| checked_reports | 0 | 91 |
| checked_ptrs | 319 | 445 |
| ptr_exempt | 0 | 3 |
| ptr_fleet | 3 | 3 |

Both runs classify the same three citations as fleet-only, not findings: `JjTrialSouji.md` and `JjAuditSouji.md` from `corpus/README.md:217`, and `.ufo/waves/hyaku/jj-w1/reports/` from `corpus/knowledge/jj-colocation-receipts.md:148`. Both have `resolved_base: null`; baseline `error` is the missing-round-reports message and landed `error` is null.

Comparison command/output:

```sh
cmp /var/tmp/souji-r18w2-RerunGateBeforeAfter/f1.json /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-18/gate-pointers-before-b576341.json && printf 'cmp: identical\n'
cmp: identical
```

Replacement-target tree query/output:

```sh
git -C /var/tmp/souji-r18w2-RerunGateBeforeAfter/lane ls-tree -r --name-only 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- census/round-17/gate-replays-expected.json census/round-17/jj-receipts-base5fa6017.txt census/round-17/jj-receipts-4f48343.txt
census/round-17/gate-replays-expected.json
census/round-17/jj-receipts-4f48343.txt
census/round-17/jj-receipts-base5fa6017.txt
```

# Verdict, fix, and gaps

**Verdict: HOLDS** for the scoped findings-count claim, 10 → 0. No gate change is indicated. Smallest fix: none; retain the qualification that the baseline run is `exit:2` because the round-18 carry/report set does not exist at that pre-wave revision, rather than describing it as a clean failing evaluation.

**Residual risk / verification gaps:** this assignment authorized only the two revision reruns; it does not validate other round-18+ revisions or the broader replay/selftest suite. LSP status/references/definition/diagnostics could not be queried: `read xd://lsp` returned “No such tool” and listed no LSP device. The literal grep was used only to locate candidate source sections; semantics above are based on direct reads, diff/tree evidence, and the executed gate output. No tools were installed or updated.
