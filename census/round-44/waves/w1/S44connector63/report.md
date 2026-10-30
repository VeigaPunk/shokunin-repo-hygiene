# S44connector63 — cross-claim separability

Axes: calibration / operability / coverage. This is evidence and one bounded proposal, not admission, judgment, integration, or a score change. Admission remains outside non-author closure; certification OFF, K5 HELD.

## Observed evidence

Frozen revision: `d314fd6e85d62565344fa6c4b102f52f62297884`; base: `55d7af6f5a22340f7a3de1c386e514ababfaa75f`.

Executed command (cwd was this seat's explicitly created scratch):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44connector63/probe.py
```

Exit 0. Exact subprocess argv, stdout, stderr, exit codes, and nine-path SHA256 matrix are preserved in `probe-output.txt`; reproducible driver is `probe.py`, with the frozen C1 instrument preserved separately. Only read-only Git commands and two bounded C1 measurements ran. No tools installed or upgraded.

### 1. Inherited work precedes formal freeze; causal attribution differs by claim

Read-only committed history reports:

* `4641e14671e60bf6cdc62ba8045c02a387a0d72c`, 2026-10-30 03:30:45 -03:00: instruments and leaf-symlink cutover.
* `6538a1538102b8b2e82311044681de005441c53b`, 07:51:48 -03:00: scenario population/control receipts/counter fixes.
* `d314fd6e85d62565344fa6c4b102f52f62297884`, 08:12:56 -03:00: freeze inherited claims before dispatch.

These are commit metadata, not independent wall-clock or dispatch certification. `preregistration.txt:4` explicitly discloses inherited attempts and zero numerical deltas; this is not an undisclosed timing repair.

The repaired C2 audit, C3 tool, updated r38 consumer, and r44 battery have identical SHA256 at `4641e...` and freeze. The C2 production tool is identical at base, inherited revision, and freeze (`f7f54e8f0a71aa952a66f53abb12dcd96f2805d8a8ef141c4b741a7865d87999`). Thus C2 measures an oracle repair, not new production behavior. C3's behavioral cutover is inherited before formal freeze. C1's lesson is absent at both inherited revision and freeze: its registration work is separable from those already-present implementations.

### 2. The three do-nothing controls are not interchangeable

Exact anchors: `controls/c1-donothing.txt:2-9`, `controls/c2-donothing.txt:1-18`, `controls/c3-donothing.txt:2-10` (all under `census/round-44/`).

* C1 uses revision `4641e...`, not the declared base. Running the **freeze-pinned** counter at both `4641e...` and `d314fd...` produced the same output and exit 1:

```
SUMMARY population=70 corrections=0 registered=0 missing=70 junk=0 fenced=0 duplicate=0 retracted=0 rederive=0 rederive_failed=70 new_mismatches=0 instrument_mismatches=66 lesson=absent
```

  This confirms its absence-of-register comparison. However, the receipt's phrase “instruments are unchanged” (`c1-donothing.txt:6-7`) is literally too broad: C1 counter SHA changed from `d3974b38...` at `4641e...` to frozen `dde1ae29...`. The receipt explicitly runs worktree instrument bytes; equal outputs do not establish equal historical instruments.
* C2's control is the **old r43 audit**, not a full run of the repaired r44 counter at base. Its recorded 8/10 is an old oracle disagreement. AST-only comparisons observed identical `build`, `classes`, `run`, and `git` functions between the base r43 audit and frozen r44 audit. This supports unchanged scenario construction, not correctness of the repaired expectations. Those expectations explicitly change at `c2-hidden-audit.py:116-120`.
* C3's base control runs the base fixture against the base tool: `legacy=ok` is compatible with `legacy_case=RED`; it does not validate the new refusal contract. The frozen counter separately supplies a discriminating old-tool/new-fixture arm (`c3-counter.py:205-224`). That arm, not old-old green, is the appropriate contract attribution surface.

Contradiction to avoid: presenting these three controls as a uniform pre-freeze/post-freeze experiment would conflate register absence, oracle replacement, and tool/consumer contract migration. There is no observed evidence supporting that uniform interpretation.

### 3. Shared substrate weakens independence, not necessarily behavior

* C1 calls **live** `tools/souji-declared-evidence.py` (`c1-counter.py:94-101`) for base and tip, despite using committed data; its return codes are captured but not enforced (`179-188`). It derives referents at base, but tip mismatch detection spans all SCORECARD appends (`249-283`). Therefore C2/C3 reporting additions can affect C1's `new_mismatches` gate even when their runtime implementations are independent. Registration of 70 occurrences covers 66 unique keys (`245-247`), not 70 newly corrected facts. This distinction is also explicit in preregistration line 4 and the current worktree lesson lines 21-23; the latter is context, not frozen evidence.
* C2 invokes the live r43 counter (`c2-counter.py:114-117`), while extracting tool/audit blobs at the measured revision (`108-113`, `125-131`). Its module claim that worktree is never read (`4-5`) is broader than this implementation. Its population check tests ID and exit-text presence/count, not per-row class multiset equality (`132-145`). Do not count population alignment as independent oracle validation.
* C3 intentionally executes live prior fixtures after verifying each fixture's SHA against the measured blob (`c3-counter.py:225-252`). This protects the entry file; the comment explicitly notes sibling resource loading (`226-228`). It does not itself bind those transitive resources. Therefore `prior=5/5` is partly dependent on the surrounding checkout, unlike the extracted tool/battery pair. No transitive-resource exploit was executed here.

These are runtime/verification substrate dependencies, not proof that C1, C2, or C3 has failed its target. C2 and C3 production tools are distinct; no direct C2-to-C3 production dependency was established.

## One bounded proposed move: attribution ledger attached to the integration report

Keep frozen counters, targets, controls, and scores unchanged. Add one evidence-only three-row ledger identifying, for each claim: declared base; actual control revision and instrument hash; implementation-origin revision; formal freeze; measured candidate revision; measurement dependency closure; and the precise inference supported. Classify C1 as token registration, C2 as oracle repair over unchanged tool behavior, C3 as inherited joint tool/consumer cutover. Cite the distinct controls rather than summing their reds/greens as independent gains.

Affected axes: calibration improves by preventing double-credit and mismatched baselines. Operability and coverage behavior are unchanged because this move changes only attribution evidence, not runtime contracts or gate requirements. This is a proposed nondominating-harm-free move, not a claimed measured score increase.

Risk: extra ledger fields may be misread as new acceptance gates or replace required checks. Label them diagnostic only; retain preregistered targets and outside admission. Missing transitive pin evidence must remain unknown, not silently “hermetic.”

Verification for the integration owner: reproduce the preserved bounded probe; compare each ledger cell to the frozen blobs and receipts; ensure C2 explicitly retains historical red; ensure C3 old-old green is not substituted for its old-tool/new-fixture discriminator. If claiming fully frozen provenance, separately bind the live C1 instrument, C2 r43 counter, and C3 transitive fixture resources before making that claim. No counter changes are proposed.

## Limits and self-check

No C2/C3 fixture suites rerun: they construct and mutate fixture repositories; this seat selected read-only provenance/AST checks and the non-mutating C1 instrument instead. Their runtime target outcomes are not newly verified here. No candidate, production, sibling, Git index, shared LOG, or fleet edits occurred. Scratch removed before return; receipts preserved in this seat directory. Self-check: accuracy 4 (runtime C2/C3 not exercised); completeness 4 (transitive closure identified, not fully enumerated); clarity 4 (different control semantics require detail); actionability 4 (ledger proposal requires integration-owner action); conciseness 4 (full reproducibility details kept in receipts). No scalar judgment of proposals or admission is made.
