# S44executor37 — C3 independent output-envelope probe

Axes: calibration / operability / coverage. Finding: the parent-symlink output envelope is unchanged by the leaf-symlink refusal cutover; it still resolves the parent and writes the resolved target. The cutover changes the separate final-component symlink case. This is bounded behavioral evidence only, not admission or deletion authorization.

## Basis and exact artifacts

Read the R44 preregistration, C3 counter, frozen tool JSON refusal docstring/logic, and `tests/fixtures/r38-drift-write-envelope.py`. The documented contract rejects a final `--json` symlink with `JSON-TARGET-SYMLINK`, while parent components are still resolved; the r38 fixture labels its final-component case `json-symlink-refused` (replacing the prior resolved-and-written expectation). Relevant frozen candidate is `d314fd6e85d62565344fa6c4b102f52f62297884`; its tool SHA-256 is `4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d`, identical to the tested lane tool bytes. The requested comparison base `55d7af6f5a22340f7a3de1c386e514ababfaa75f` tool SHA-256 is `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`.

Exact successful command (base extracted by `git show` into the seat scratch; fixture created isolated fake repositories and output targets under its `--work`):

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-write-envelope.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --base-tool /fast/scratch/hyaku/souji-r44/S44executor37/base-tool.py --work /fast/scratch/hyaku/souji-r44/S44executor37/work
```

Exact saved stdout/stderr receipt: `r38-envelope.txt`. Observed exit 0, all 12 candidate cases pass, including `case-json-symlink-refused=PASS`; base arm reports `base-json-symlink-refused=FAIL rc=0 resolved_written=True exists=True`, and `BASE-BEHAVIORAL failed=1 cases=json-symlink-refused`; summary: `cases=12 pass=12 fail=0 base_cases=12 base_fail=1 behavioral_fail=1`. Thus base55d7af6 does not refuse a final symlink and writes through it, while frozen candidate does. The separate parent-symlink path is explicitly still resolved according to the tool contract, so this leaf-only cutover does not alter behavior for a symlinked parent; the fixture does not exercise that parent variant directly.

The first attempted invocation exited 2 because the fixture requires `--work` to name an existing directory; created that directory under the allowed seat scratch and reran successfully. Scratch was removed before handoff. No tools installed. No production, shared bookkeeping, or frozen counter files changed.

## Limits

This executes the r38 output-envelope fixture with a base55d7af6 behavioral comparison, not the entire frozen C3 counter or C3 registered r37-base thresholds. It validates the final-component symlink behavior and existing fixture battery; a parent-component symlink-specific assertion was not present in this fixture and was not added. No claim is made about other output paths or races.
