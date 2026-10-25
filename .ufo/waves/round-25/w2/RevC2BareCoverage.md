# RevC2BareCoverage — bare cross-product coverage

STATUS: FAIL — the requested additional bare shapes expose untested behavior. The current 12-case counter still reports 12/12 for a bare-alternates mutant that drops the alternates count.

## Evidence

- Frozen C2 cases are explicitly 9 bare-nonempty, 10 bare-empty, 11 worktree subdir, 12 partialClone-only (`.ufo/waves/round-25/preregistration.txt:64-74`). Case 9’s bare repo is created with an optional single commit (`w1/r24-size-census.py:95-107`); its oracle checks only rc, final counts line, `invoked_from=bare`, and unchanged manifest (`w1/r24-size-census.py:297-305`). The other predicates are located at `w1/r24-size-census.py:308-336`.
- Bare-alternates reproduction, Git 2.56.0: built two bare repos, wrote the alternate object-dir path into `bare-alt.git/objects/info/alternates`, and added a dangling blob to the alternate. Tool tip output ended `garbage=0 size_garbage=0 unreachable=4 alternates=1`, rc 0. Mutant replaced the `a` computation at `tools/souji-size-census.py:210` with `a = 0 if invoked_from == "bare" else ...`; same repo output ended `garbage=0 size_garbage=0 unreachable=4 alternates=0`, rc 0. Running the frozen extended fixture against that mutant produced `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 0; case 9 passed.
- This mutant is a single-expression regression and is the simplest directly relevant broken tool demonstrated here. Separately, W1 RevC2 already gives an even smaller general survivor: M3 changes `resolve()` to return `common, "bare"` universally; it scores 12/12 while mislabeling ordinary repositories (`w1/RevC2.md:26-41,73`).
- Bare promisor-pack reproduction: created a bare repo and a `.promisor` marker under `objects/pack/`; tip refused with rc 2 and `promisor pack (objects/pack/pack-deadbeef.promisor)`. W1 RevC2 reports M9 (bare pack lookup missed) survives all 12; witness is bare promisor clone with `extensions.partialClone` unset (`w1/RevC2.md:35-39,49`). The frozen fixture has no bare promisor-pack or bare remote-promisor case (case list and setup above). A bare remote-promisor config probe likewise tip refused rc 2 with `promisor remote (remote.origin.promisor true)`.
- Tool implementation confirms it has distinct mechanisms: alternates is derived from `count-objects` fields at `tools/souji-size-census.py:208-220`; promisor remote config and `.promisor` pack checks are at `:159-178` and use `common` for pack lookup.

## Findings

1. **[Medium — coverage]** Bare-repo alternates accounting is not exercised by C2’s 12-case fixture: the minimal bare-alternates mutant above passes all 12 while returning an incorrect `alternates=0` on a constructed bare repo. Case 9 does not include alternates or assert census values beyond a syntactically valid counts line. This is direct evidence that the counter does not validate the generality of bare census behavior.
2. **[Medium — coverage]** Bare `.promisor` pack and bare `remote.*.promisor=true` refusal shapes are absent from the frozen cases. Tip behaves correctly on both probes, but the W1 M9 survivor demonstrates the bare pack-path blind spot can survive 12/12; no current fixture predicate falsifies it.
3. **Claim boundary:** C2 is **bounded to the four named surfaces**, not a general claim that every bare-repository census/refusal shape is correct. The preregistration calls these “Size-census refusal surfaces covered by the frozen fixture” and names the four exact cases (`preregistration.txt:58-74`); the target is explicitly `cases=12 pass=12` (`:82-85`). Read as a universal bare-support claim it would be over-general. The cross-product shapes are attack evidence, not permission to expand the frozen case set.

## Attack log

- Constructed isolated `/var/tmp/souji-r25-RevC2BareCoverage-*` repositories; no lane production files changed.
- Bare-alternates tip vs mutant: outputs and fixture result above; mutant passes 12/12.
- Bare `.promisor` pack and remote-promisor config: tip rc 2 on each with matching refusal reason.
- Scratch removed after probes. No tools installed or upgraded.
