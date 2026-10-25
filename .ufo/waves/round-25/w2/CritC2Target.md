# CritC2Target (seat L1Souji25.CritC2Target) — falsify the do-nothing target for C2

Report: .ufo/waves/round-25/w2/CritC2Target.md

## Status
STATUS: PASS. Attack executed against the integrated fixture (`tests/fixtures/r24-size-census.py`, sha256 `9c8a512f…bd528`, byte-identical to the W1 draft hash). A canned emitter that hard-codes only the four refusal cases 9–12 scores **6/12** with `control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 1: all four refusal cases PASS with zero census/refusal implementation. The built-in stub control still checks only cases 2–5 (`CASES[1:5]`), not 9–12.

## Evidence
Environment: git 2.56.0; lane HEAD `6deb53561aace9aa14a399f88cf8150da4d4f4bd` (W1 draft in working tree); fixture sha256 `9c8a512f94d5682efee725dc7ed7519c127fde6a775a038ec3292374970bd528`; tool sha256 `c5690681b4e86afd4a2a019847c8d18315cea51c2d58d67b3cbc1260143a6eb3`; scratch `/var/tmp/souji-r25-CritC2Target/` (removed on finish).

- Hard-coder run: `python3 -B tests/fixtures/r24-size-census.py --tool /var/tmp/souji-r25-CritC2Target/hardcode-emitter.py` → rc 1:
  - `CASE 1 clean FAIL exit=3 …`, `CASE 2 dangling FAIL exit=3 …`, `CASE 3 garbage FAIL …`, `CASE 4 linked FAIL exit=3 …`, `CASE 5 alternates FAIL exit=3 …`, `CASE 6 refusal FAIL lost_found_argv[exit=3 …] partial_clone[exit=2 …] promisor_unset[exit=2 …]`
  - `CASE 7 detector PASS …`, `CASE 8 control PASS stub_failed=dangling,garbage,alternates`
  - `CASE 9 bare-nonempty PASS exit=0 counts=0,0,0,0 manifest_changed=0 invoked_from_bare=True`
  - `CASE 10 bare-empty PASS exit=1 counts=none manifest_changed=0 stderr_git_failure=True stderr_no_default_references=True stdout_counts_line=False`
  - `CASE 11 subdir PASS exit=2 counts=none manifest_changed=0 stderr_must_name_repo=True`
  - `CASE 12 partialClone-only PASS exit=2 counts=none manifest_changed=0 stderr_partial_clone=True`
  - `cases=12 pass=6 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`
- Green arm on same integrated fixture: `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` → rc 0, `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` (matches W1 `c2-green.tsv`).
- Stub vs full fixture (W1 receipt `w1/ExecC2-2/receipts/c2-stub.tsv`, same fixture hash): stub fails 8/12 including **all four** of 9–12 (9, 10, 11, 12 FAIL), passes only 1, 4, 7, 8; `cases=12 pass=4`.
- Control case source (`tests/fixtures/r24-size-census.py:275-280,341-345`): `case_control` runs `STUB` against `CASES[1:5]` = cases 2–5 (dangling, garbage, linked, alternates). Cases 9–12 are not exercised by the control. `case_control` and `case_detector` ignore the `tool` argument entirely — both are tool-invariant self-checks, so the two final flags are constant for any tool.
- Base receipt `census/round-25/records/c2-control-base.tsv`: pre-extension fixture (sha `373ef1f0…84f`) `cases=8 pass=8` at `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`.

### Emitter under test (self-contained; reproduced verbatim)
```python
#!/usr/bin/env python3
import os, subprocess, sys
GIT = ["git", "--no-pager", "--no-optional-locks"]
def git(*args):
    p = subprocess.run(GIT + [str(a) for a in args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr
def argv_repo(argv):
    for i, a in enumerate(argv):
        if a == "--repo" and i + 1 < len(argv):
            return argv[i + 1]
    return None
def promisor_any(path, common):
    rc, _, _ = git("-C", path, "config", "--get", "extensions.partialClone")
    if rc == 0: return True
    rc, out, _ = git("-C", path, "config", "--type=bool", "--get-regexp", r"^remote\..*\.promisor$")
    if rc == 0 and any(line.rsplit(" ", 1)[-1] == "true" for line in out.splitlines()): return True
    packs = os.path.join(common, "objects", "pack")
    if os.path.isdir(packs) and any(n.endswith(".promisor") for n in os.listdir(packs)): return True
    return False
def classify(path):
    rc, out, _ = git("-C", path, "rev-parse", "--path-format=absolute",
                     "--git-common-dir", "--git-dir", "--is-bare-repository")
    if rc != 0: return None
    lines = out.splitlines()
    if len(lines) < 3: return None
    common, _, bare = lines[0], lines[1], lines[2]
    if bare == "true":
        rc2, _, _ = git("-C", path, "rev-parse", "--verify", "--quiet", "refs/heads/main")
        return "bare-empty" if rc2 != 0 else "bare-nonempty"
    rc2, top, _ = git("-C", path, "rev-parse", "--show-toplevel")
    if rc2 != 0 or not top.strip(): return None
    if os.path.realpath(path) != os.path.realpath(top.strip()): return "subdir"
    if promisor_any(path, common): return "partialclone"
    return None
def emit(kind):
    if kind == "bare-nonempty":
        print("census.status=ok"); print("census.invoked_from=bare")
        print("garbage=0 size_garbage=0 unreachable=0 alternates=0"); return 0
    if kind == "bare-empty":
        print("git failure: /usr/bin/git --no-pager fsck --unreachable "
              "--no-reflogs --no-progress exited 0: notice: No default references", file=sys.stderr)
        return 1
    if kind == "subdir":
        print("refused: --repo must name the repository itself, not a directory "
              "inside or below it", file=sys.stderr)
        return 2
    if kind == "partialclone":
        print("refused: partial-clone repository (extensions.partialClone=origin)", file=sys.stderr)
        return 2
    return None
def main(argv):
    path = argv_repo(argv)
    if not path: return 3
    kind = classify(path)
    code = emit(kind) if kind else None
    if code is None:
        print("broken: unhandled non-refusal case", file=sys.stderr); return 3
    return code
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

## Findings
1. **The four refusal cases 9–12 are satisfiable by canned special-casing with zero census work.** The emitter above performs no census (no count-objects, no fsck, no unreachable/alternate accounting) and no write-safety logic; it classifies the invocation by three read-only git probes and prints the exact expected bytes. Cases 9, 10, 11, 12 all PASS. The fixture is a black-box contract test: it cannot distinguish a genuine implementation from a scenario-hard-coded emitter on the new surface.
2. **The built-in stub control still covers only cases 2–5, not 9–12.** `case_control` runs the always-zero STUB against `CASES[1:5]` (dangling, garbage, linked, alternates). It never runs the stub against 9–12. Because `case_control` ignores the tool under test, `control=FALSE-GREEN-REJECTED` holds identically for the real tool, the stub, and my fully-broken-across-1–8 emitter — the control flag carries no information about the new surface.
3. **The new cases themselves are not vacuous — they reject the always-zero emitter.** The W1 `c2-stub.tsv` receipt shows the stub fails all of 9–12 (plus 2, 3, 5, 6), so the new assertions (rc + stderr/stdout literals) have teeth. The gap is that the *control* — the fixture's self-sensitivity guard — does not extend to them; only the per-case assertions stand between a regression and a false green.
4. **C2's target is not reachable by a do-nothing (always-zero) emitter, but is per-case reachable by hard-coding.** The stub scores 4/12 (passes only 1, 4, 7, 8). A full 12/12 requires genuinely satisfying cases 1–6 as well (unreachable counting, garbage/alternates detection, `--lost-found`/promisor refusals, manifest write-safety), which a canned emitter cannot fake without inspecting repo state — i.e., without doing the census. So C2 is not a vacuous claim; its green arm is real behavioral conformance on 12 enumerated scenarios, and the red arms (1efe406 fails 11; 778747e fails 9/10 — W1 receipts) prove the fixture discriminates the two historical regressions.
5. **What C2 proves, precisely:** (a) at the landing tip the tool emits the specified observable contract on the 12 enumerated scenarios, including the four refusal surfaces; (b) the fixture rejects an always-zero emitter on cases 2–5 (control) and the detector self-check works; (c) the two named regressions are discriminated by the extended fixture. It does **not** prove: general refusal logic, anything about refusal configurations beyond the four enumerated (bare-empty/nonempty, subdir, partialClone-only), or any implementation property — the refusal surface's verification is contract-level and hard-code-satisfiable. The disclosed limits (atime/ctime excluded, mtime-restoring writes invisible, no hostile config/env cases) are unchanged.

## Attack log
- A1 (this seat): canned emitter for 9–12, broken elsewhere → 6/12, rc 1, all four refusal cases PASS. Demonstrates the refusal surface pins output contracts, not implementation, and that the control does not cover it.
- A2 (retry within A1): first emitter build used `git rev-parse HEAD` as the bare-emptiness probe — on an empty bare repo git resolves HEAD to the unborn-symref name and exits 0, so case 10 was misclassified as bare-nonempty (exit=0 + counts line → FAIL). Fixed with `rev-parse --verify --quiet refs/heads/main`. Also: git 2.56.0 partial clones set `remote.origin.promisor=true` and do **not** set `extensions.partialClone`; the classifier mirrors the real tool's three promisor paths (extensions, promisor-remote regexp, promisor pack). After both fixes: 6/12 exactly as predicted.
- A3 (observation): under the current fixture, case 6's `promisor_unset` invocation still refuses via `extensions.partialClone` (only `remote.origin.promisor` is unset by the fixture), consistent with the real tool's behavior.

## Housekeeping
- Tools installed: none.
- Scratch `/var/tmp/souji-r25-CritC2Target/` removed before finish.
