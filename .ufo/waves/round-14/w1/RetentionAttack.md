# RetentionAttack — round 14, wave w1 (critic, leaf)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Axes: calibration, operability.
Write set: this report only. No edits to runners, evidence, tools, or bookkeeping. No installs or upgrades (none needed).
Status of the C1 gate at the time of writing: `tools/souji-evidence-cache.py` and `tests/fixtures/r14-evidence-cache.py` were **absent**. A glob returned "Skipped missing paths". The integration findings below are therefore design findings against the shared interface in `w1-spec.json`. They are not inspections of gate code.

## Verdict

**No.** A standalone gate does not fix the recurrence if no runner calls it. The defect from round 13 sits in the runner's retain branch (`census/round-13/run-verification.py:49-54`). That branch reuses every previously `matched` result without comparing digests. Adding a separate CLI leaves that callsite unchanged. Suppose the gate exists and round-14 evidence is produced by a runner copied from r13 (or by any `--retry-failed`-style rerun). A stale green would then be retained exactly as before, and `census/round-14/claims.json` C1 `after` ("eligible only matching declared dependency bytes…") would describe a capability that the evidence path never exercises. That would be false provenance on the calibration axis.

C1's counting command (`r14-evidence-cache.py; cache-demonstration.py`) can prove only that the gate discriminates. It cannot prove that retained evidence passes through the gate. Either the callsite migrates (§4, option A), or the claim is narrowed and retention is disabled (§4, option B).

## 1. Code inspection: r13 retained-green behaviour (no execution)

`census/round-13/run-verification.py`:

| Line(s) | Behaviour | Defect |
|---|---|---|
| 31-33 | `--retry-failed` loads `OUTPUT` (= `census/round-13/verification.json`). `RETRY_NAMES` = names whose prior `matched` is false. | The only test for whether a result is eligible is its *prior verdict*. No dependency or digest input is checked. |
| 34-36 | Hand-coded pairing: if `quarantine-bounds` failed, `quarantine-red-before` is also rerun. | This encodes one dependency edge by hand (the fixture is shared). No other edge is encoded, which shows that dependency tracking was known to be needed. |
| 49-50 | `if PREVIOUS and name not in RETRY_NAMES: retained = dict(PREVIOUS_RESULTS[name])` | This is the stale-green callsite: every prior pass is reused whatever the current bytes are. A name that is new this run (absent from `PREVIOUS`) raises `KeyError` and crashes instead of running. That fails closed, but it is an operability defect. |
| 51 | `retained.get("measured_commit", PREVIOUS["measured_commit"])` | A legacy result with no per-result revision inherits the file's top-level revision. If the previous file had itself been a retry output, its top-level `measured_commit` would be *that retry's* HEAD, so the old observation would be relabelled as newer. That is revision laundering. |
| 52 | `retained_from = "census/round-13/verification-attempt-1.json"` (constant) | The bytes actually read come from `verification.json`. The label is correct only if a human copied the file to `attempt-1` beforehand. No digest of the source file is recorded. |
| 104-107 | Top-level `installed_sha256`/`artifacts_unchanged_during_run` hash the *current* run's tool bytes. | Retained results were measured against different bytes, but the record reports only current digests. A reader of `installed_sha256` would wrongly think every result was measured against those bytes. |

## 2. Counterexamples from committed evidence (read-only git/sha256sum; not tests)

Exercised commands (read-only object and file reads only): `git log`, `git diff --stat 6ed10a7 6f8ee0f`, `git diff 6ed10a7 6f8ee0f -- tools/souji-cert-evidence.py`, `git show <rev>:<path> | sha256sum`, `sha256sum` on committed lane files, and `git show 23014d4/15d95e3 -- census/round-13/verification.json`.

**CE-1: a stale green was actually retained across a tool change (round 13).**
- In `verification.json` (HEAD), `evidence-frozen`, `historical-replay-wrong-bytes` and `historical-replay-candidate` carry `measured_commit 6ed10a7…` and `retained_from attempt-1`. All three invoke `tools/souji-cert-evidence.py`.
- `tools/souji-cert-evidence.py` changed between 6ed10a7 and 6f8ee0f. Its sha256 went from `a029aaa0…` to `943d664c…`. The diff is the `_finding_ids` regex at line 1021 (`[a-z0-9-]` → `[a-z0-9_-]`).
- The record's top-level `installed_sha256` lists only `943d664c…`. Under the shared interface, a gate given `dependencies:{"tools/souji-cert-evidence.py": "a029aaa0…"}` would return exit 1 (digest mismatch) and force a rerun. The r13 runner retained the results instead.
- The r13 spot-check (`corpus/lessons/round-13-verifier-spotcheck.md:80,132`) accepted this only after a *human* found the delta production-irrelevant: the delta is used only by `selftest()`, while `--frozen`/`--manifest` go through `main()`, at lines 1500-1522. That is a manual exemption, not a mechanism. The next delta could touch `evaluate_frozen`, and no human or tool would check it.

**CE-2: a dependency changed after the run, and the record was then edited by hand.**
- `sources-contract` was retained from 6ed10a7. `corpus/SOURCES.md` had the same bytes at 6ed10a7 and 6f8ee0f (`4772663b…`), so the gate would have allowed reuse at retry time.
- Commit 23014d4 then changed `corpus/SOURCES.md` (`a405cdd4…`). After that, commit 15d95e3 hand-edited `verification.json`: `measured_commit` became 23014d4, `source_sha256` was added, and `seconds` and `retained_from` were removed. The runner never produces a result without `seconds`, so this result has no runner provenance.
- Lesson: a gate check run at retry time can still go stale before the closing commit. Retained or fresh results need one final dependency check against the closing tree. Hand-edited result rows defeat any gate, because the gate trusts the record (spec: "No proof of actual historical execution").

**CE-3: round-14 recurrence path (inference from the planned write set; not observed).**
C2 edits `tools/souji-census.sh` this round. Its `-selftest` row and `shellcheck-warning` depend on those bytes. Suppose a first attempt passes `souji-census.sh-selftest` at bytes X, then a C2 review fix changes the file to Y, and a retrying runner with r13 semantics runs. The C2 operability evidence would then be a green measured on X, while `installed_sha256` reports Y. Today `git diff --stat a31642d -- tools tests corpus/SOURCES.md` is empty, so the C2 edit has not landed yet. `[INFERENCE]`

**CE-4: the dependency list is self-declared, so omitted transitive dependencies pass the gate (bounded guarantee, not a gate bug).**
Selftests invoke other repo files: `souji-verify.sh:1270`, `souji-vault-verify.sh:1576` and `souji-quarantine.sh:1610` all call `tools/souji-round9-selftest.sh`, which sets `SOUJI_VERIFY_BIN=…/souji-verify.sh` (line 64). If the caller declares only the tool file, a change to `souji-round9-selftest.sh` or `souji-verify.sh` would still leave the `souji-quarantine.sh-selftest` green eligible. Runtime binaries (bash, python3, git, shellcheck) and the out-of-root `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` cannot be expressed as contained dependencies at all. Such checks must be non-cacheable, or the claim must state the runtime omission.

**CE-5: the gate can be laundered at the callsite (design).**
Suppose a runner computes `dependencies` at *retain* time from current bytes, rather than storing the digests captured when the command ran. The gate would then always return 0. Nothing in `{name, matched, measured_commit, dependencies}` lets the gate tell the two cases apart. I sent this precondition to `SoujiR14.CacheGate`.

## 3. Axes impacted

- **calibration**: CE-1 and CE-2 are real instances of stale or hand-edited evidence in committed history. If no runner uses the gate, the C1 `after` wording overstates what was achieved. CE-5 would make even an integrated gate vacuous.
- **operability**: the `KeyError` on new check names (line 50) and the hand-coded pairing (lines 34-36) make retries brittle. CE-3 would let C2's census evidence go stale within this round.
- Neither the r13 runner nor its outputs should be rewritten. They are historical evidence and the spot-check already disclosed them. The correction applies only to round-14 evidence.

## 4. Smallest safe correction (round-14 evidence only; no historical rewrite)

Do **not** edit `census/round-13/run-verification.py`, `verification.json`, or `verification-attempt-1.json`. Round-13 rows lack `dependencies`, so they are legacy records and the gate refuses them anyway. They must never become retention sources for round 14.

**Option A — migrate the one callsite (this is what closes the recurrence).** Apply this only in a round-14 runner, if L1 creates one (for example `census/round-14/run-verification.py`, owned by L1):
1. Declare `DEPS[name]` as contained, repo-relative paths for each check, including transitive repo files (CE-4; RetentionIntent supplies the list). Mark `cacheable=False` for `quarantine-red-before` (temp baseline outside the root), `sources-contract` (out-of-root script), and `shellcheck-warning` (binary version).
2. At measurement time, compute `before = {rel: sha256}` before `Popen` and `after` after `communicate`. Store `item["dependencies"] = before if before == after else {}`. An empty map is refused by the gate as "empty deps", so a dependency that changed during the run can never be reused. Set `item["measured_commit"] = CURRENT_REV`.
3. Retain branch: replace lines 49-54 with the following. If `cacheable` is set and the prior row exists, write the prior row's `{name, matched, measured_commit, dependencies}` *as stored* to a `/var/tmp` temp file. Run `python3 <ROOT>/tools/souji-evidence-cache.py --root <ROOT> --record <tmp>` and remove the temp file. Retain only on exit 0. On exit 1 or 2, rerun, and record `cache_gate_exit` plus finding ids on the new row. Never use `PREVIOUS["measured_commit"]` as a default (delete the line-51 fallback). A missing prior row means the check runs; it must not raise `KeyError`.
4. Provenance on retained rows: `retained_from` = the path actually read, plus its `retained_from_sha256`, plus `cache_gate_sha256` (= sha256 of the installed gate). The runner writes `verification-attempt-N.json` itself before overwriting. Sources must be round-14 files that this runner produced, never files from round 13 or earlier.
5. Closing check: immediately before commit, re-gate every row that has `dependencies` against the closing tree (CE-2). A failing row is rerun, not edited by hand. Per-row `measured_commit` stays explicit. Top-level `installed_sha256` is described as the closing-tree bytes only.

**Option B — no retention at all (smaller and also safe, but narrows C1).** Round-14's final evidence is one full run at the closing commit, with no `--retry-failed`. At r13 the whole suite summed to about 55 s (`seconds` total: 55.06 in `verification.json`, 50.01 in attempt-1), so retention saves almost nothing. With no retained rows, stale green cannot occur in round-14 evidence. In that case, `claims.json` C1 `after` must say: the gate exists and is demonstrated; no runner consumes it this round; round-14 evidence contains zero retained results. Claiming that retained greens are now gated would be unsupported.

Distinguishing the two: option B is a tradeoff the judge should accept only with the narrowed claim. Option A is the fix for the defect class. Either way, the gate is a precondition, not the fix.

## 5. Final L1 commands (not run by this seat)

Run these after the C1 and C2 artifacts land, on a committed tree (`git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- tools tests census/round-14` must be empty):

```
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-evidence-cache.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-evidence-cache.py
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-14/cache-demonstration.py
# Legacy refusal on real r13 rows, read-only; copy one row to /var/tmp, never modify census/round-13:
python3 -c 'import json,sys; d=json.load(open("/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/verification.json")); r=[x for x in d["results"] if x["name"]=="evidence-frozen"][0]; json.dump({k:r.get(k) for k in ("name","matched","measured_commit","dependencies")}, open(sys.argv[1],"w"))' /var/tmp/souji-r14-legacy-row.json
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-evidence-cache.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --record /var/tmp/souji-r14-legacy-row.json   # expect non-zero, legacy/no-dependencies finding
rm -f /var/tmp/souji-r14-legacy-row.json
# If option A: the round-14 runner must show at least one retained row with cache_gate_exit 0 and one rerun row with cache_gate_exit 1 after a dependency edit, run in an isolated /var/tmp clone, not the live lane.
# Option B, or the closing run: a full run with no retry flag, then confirm that no row carries retained_from:
python3 -c 'import json; d=json.load(open("/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-14/verification.json")); print([r["name"] for r in d["results"] if "retained_from" in r])'   # expect [] under option B
```

## Separation of evidence

- **Code inspection only**: §1 line analysis; CE-4 call sites (`grep` on `tools/*.sh`); `souji-cert-evidence.py:999-1031,1149,1485-1522` routing; the CE-5 design argument; and the absence of gate and fixture files.
- **Exercised (read-only)**: git object reads and sha256 values quoted in CE-1 and CE-2 (`a029aaa0…`→`943d664c…`; SOURCES.md `4772663b…`→`a405cdd4…`; attempt-1 = `6f8ee0f:verification.json` = `aa7a0e77…`), the commit sequence 6ed10a7→6f8ee0f→23014d4→15d95e3, the 15d95e3 hand-edit hunk, and the seconds totals.
- **Not exercised**: no gate, selftest, fixture, runner, or linter was run. CE-3 is `[INFERENCE]`.
- **Peer coordination**: I messaged `SoujiR14.CacheGate` about the measurement-time digest precondition (CE-5) and `SoujiR14.FinalEvidencePlan` about not retaining without the gate, the clean-tree precondition, and the ~55 s full-run cost.
