STATUS: DONE — C2 pointer calibration has a local-relative false-fleet path and is not reproducible against a pinned fleet revision.

Axes: calibration (primary), path ownership, replay reproducibility.

# Attacked claim

`tools/souji-landing-gate.py@5efb519`: missing citation paths are distinguished from fleet-only paths; `../` references that escape the lane map to the fleet root.

# Findings

## HIGH — A `../` citation that resolves inside the lane can be hidden as fleet-only

Evidence: `tools/souji-landing-gate.py:710-715` normalizes a leading `../` relative to the citing document's directory. `corpus/README.md` is among the scanned sources (`:803-820`). Then `check_pointers` first tests the selected lane revision (`:841-845`), but after a miss it checks `fleet_root` for the normalized path regardless of whether normalization actually escaped the lane (`:846-864`). `fleet_root` hits are recorded as fleet data and skip `LG-DANGLING-PTR` (`:855-864`); the gate's documented fleet list is not a finding (`:38-42`), and its exit is based on findings (`:1019-1023`).

Concrete static trace (no fixture was executed): if `corpus/README.md` contains `../census/round-18/x`, `_normalize_pointer_path` computes `normpath(join("corpus", "../census/round-18/x")) == "census/round-18/x"`. That path points inside the lane, not outside it. If it is absent from the selected lane `--rev` tree but the same path exists under `--fleet-root`, lines 849-853 keep `fleet_path == "census/round-18/x"`, find the fleet copy, and classify the citation as `fleet` instead of reporting the missing lane target. Thus the lane path and fleet path can be different files with the same relative name, and the local missing reference is suppressed.

Important distinction: for a genuinely escaping reference—for example `../../census/round-18/x` from `corpus/README.md`, which normalizes to `../census/round-18/x`—`path[3:]` maps to `census/round-18/x` under the parent fleet root as intended; a same-named file inside the lane is not the citation's resolved target. The defect is that the fallback also treats normalized in-lane paths as fleet references. The existing selftest covers only a bare `corpus/fleet-only.md` fallback (`tools/souji-landing-gate.py:1419-1428`), not this distinction.

Smallest fix: retain whether normalization actually crossed above the lane root and permit the `../` fleet mapping only for a path that resolves outside the lane by exactly one level. An in-lane normalized path absent at `--rev` should remain dangling. If bare/root-relative fleet citations are also a requirement, give them an unambiguous fleet syntax and update the current `pointer-fleet-only` selftest rather than using same-name existence as disambiguation.

## MEDIUM — Fleet classification is based on mutable filesystem state, not a revision

Evidence: the CLI accepts only `--fleet-root PATH` (`tools/souji-landing-gate.py:1946-1951`); `check_pointers` asks `os.path.exists(os.path.join(fleet_root, fleet_path))` (`:849-853`). In contrast, lane presence is evaluated from `tree = list_tree(root, resolved)` for the explicitly selected `--rev` (`:908-912`, `:844`). There is no fleet revision or immutable fleet-tree identity in the call.

Concrete calibration example: keep the lane `--rev` fixed with a reference to `../census/round-18/x`; when `--fleet-root/census/round-18/x` is absent the pointer is dangling, but adding that file as an untracked file (or checking out a later fleet state that contains it) changes the result to `fleet` without changing the lane revision. A historical replay therefore depends on the current fleet working tree, including untracked content, and cannot establish that the fleet target existed for the measured state.

Smallest fix: pin fleet lookup to an explicit `--fleet-rev` and inspect that commit's tree (or otherwise record and validate an immutable fleet-tree identity); require it whenever fleet classification is enabled.

# Verdict

**C2 pointer calibration fails** for the cases above. `path[3:]` is correct for a path already normalized to exactly one level above the lane, but the classifier does not require that condition before the fleet fallback, and its presence check is not revision-pinned. The two issues are independently actionable.

# Verification and residual risk

- LSP status/references/definition/diagnostics were unavailable: the `read` request for `xd://lsp` returned `No such tool: xd://lsp` and listed mounted devices without an LSP device. Literal grep was used only as a locator, not semantic proof.
- Read-only diff command: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --unified=12 b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- tools/souji-landing-gate.py` → `tools/souji-landing-gate.py | 653 +++++++++++++++++++++++-`; `1 file changed, 625 insertions(+), 28 deletions(-)`.
- Source inspection: `tools/souji-landing-gate.py:710-715, 803-820, 841-876, 908-912, 1019-1023, 1419-1458, 1946-1967`; fixture source inspected at `tests/fixtures/r18-landing-pointers.py:112-131, 282-306`.
- No gate, selftest, or fixture was run: this assignment supplied no `ALLOWED-EXEC` authorization. Findings are static traces of the implementation; a runtime reproducer remains unverified.