# S44executor28 — C2 frozen counter findings

**Axis:** operability. **Freeze:** `d314fd6e85d62565344fa6c4b102f52f62297884`.

## Run evidence

Executed from the lane root:

```sh
python3 -B census/round-44/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor28
```

Captured full stdout, stderr, and exit status in `c2-counter.stdout`, `c2-counter.stderr`, and `c2-counter.rc`. Observed exit status `0`; stdout exactly:

```text
SUMMARY tool=present population=ok retention=ok hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED controls_ran=ok selftest=ok tmpdir=ok
```

stderr was empty. This satisfies the registered C2 target. No tools were installed or updated.

## Retention and negative-control crash review

Counter source `census/round-44/c2-counter.py` lines 114–124 invokes retained r43 counter and requires its process return code exactly 1, a `SUMMARY` line, and every configured field equal to the retained historical values (`newtable=9/9`, `r42table=ok`, `hidden=RED`, `hidden_ctrl=REJECTED`, `real=ok`, `selftest=ok`, `tmpdir=ok`, and both controls rejected). Consequently an r43 crash/no-summary cannot satisfy `retention=ok` merely by being nonzero.

For v2 stubs, lines 153–165 require an audit verdict (a parseable `SUMMARY`), at least one failed scenario, and fewer passes than total. A crash/no-summary yields no verdict and is labeled `CRASH`, not `REJECTED`. Independently, lines 167–175 run each generated stub directly and require a summary line (`controls_ran=ok`). The captured green result thus establishes the intended two stub rejections plus direct controls ran.

The historical r43 counter has weaker hidden memorizer control logic: lines 341–350 mark it rejected on any nonzero return code, without requiring a summary or distinguishing a crash. Its target nevertheless separately requires `hidden=RED` and `hidden_ctrl=REJECTED`; r44 retention requires the historical summary fields exactly. This counter run proves historical red retained, but not that the r43 memorizer's nonzero result represented a substantive audit rejection rather than a crash. That is a limitation of the retained historical oracle, not a counter failure; the v2 controls' summary requirement avoids that crash-based false discrimination for the current controls.

The v2 audit source lines 92–99 converts timeout to no verdict; lines 101–107 derive classes from findings, and lines 160–166 compare exit and exact expected classes. Each scenario requires a parseable process result, so crashes cannot count as matching a scenario. Scenario h10 additionally checks exit 2 and `REFUSAL` in stderr.

## Limitations and handoff

The frozen counter reports aggregate legs only; it does not emit per-leg child streams in this run. No external state or frozen source was modified. Parent owns post-integration verification.
