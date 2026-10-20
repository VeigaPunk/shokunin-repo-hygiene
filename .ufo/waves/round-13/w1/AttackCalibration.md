# R13 w1: AttackCalibration (critic, C1 falsification)

Seat: SoujiR13.AttackCalibration (critic, leaf). Read-only. I edited nothing in the lane except this report. I ran no tests, builds or lane tools. I ran some read-only probes (`git show`, `sha256sum`, `jq`, `grep`) and one Python-semantics probe, listed below. I installed or updated no tools. Certification remains OFF. This seat is **not** an independent non-author verifier.

The gate under attack is the C1 contract in `.ufo/waves/round-13/w1-spec.json` (item `EvidenceGate`) and `census/round-13/claims.json:5`. At the time of this review, neither `tools/souji-cert-evidence.py` nor `tests/fixtures/r13-cert-evidence.py` existed (`ls` → "No such file or directory"). Every point below is therefore against the contract, not against code.

Peer overlap: `ReviewEvidence.md` already gives invariants I1–I9 (gate-owned artifact set, coverage, before/after digests, verdict derived from the evidence, author normalisation, inode uniqueness). I do not repeat them. I add:
- live counterexamples taken from committed repo bytes;
- holes that ReviewEvidence does not cover;
- admit/reject cases at the level of the **C1 claim**, not only the gate.

## Axes
- **Calibration.** Does C1 change how well the lane's claims match reality, or does it only add a new report that nobody checks?
- **Operability.** Can the gate be run deterministically, and can it visibly fail?
- **Coverage.** Does the gate see the real evidence population, or only the synthetic fixtures it was written for?

## Verdict
C1 as worded can be **falsified as a calibration claim**. These are observed facts:
- The "before" metric is an existence count: `census/round-13/before.json:5` reads `"cert_evidence_gate": 0`, measured by "existence of tools/souji-cert-evidence.py" (`:4`).
- The "after" claim names "synthetic manifests" and a "digest-pinned frozen input run" (`claims.json:5,10`).

A gate that exists and passes its own synthetic selftest is the same shape as r12's C1. r12's count was restated afterwards as "a rule-coverage count, not calibration proof" (`SCORECARD.md:18-19`; `corpus/lessons/round-12-verifier-spotcheck.md:17`).

The lane's own repo holds a false certification claim at HEAD today (CX1). That is the strongest test available. C1 improves calibration only if the gate is shown to reject that real record.

## Observed facts (commands are read-only)

| # | fact | command / location |
|---|---|---|
| F1 | `HEAD:census/round-10/cert-16.json` sha256 = `662294df4291c16f…`, label `s16-r11-cert-c03b`, `certification_ready: true`, verdict `CERTIFIED`, census lane sha `60aef4c0…`, `installed_tool_sha256.souji-census.sh` = `462dabd2…` | `git -C <lane> show HEAD:census/round-10/cert-16.json \| sha256sum`; `… \| jq -c '{seat,label,round,…}'`; `grep -n` lines 10, 20, 26 |
| F2 | The r10 receipt the judges ordered restored is `6293283e…` and is present only at `e879ba0`. The overwritten state was **committed** in `1ccf11b` ("pre-reboot sweep: remaining r11 fragments + results") | `git -C <lane> log -- census/round-10/cert-16.json` → `1ccf11b`, `e879ba0`; `git show e879ba0:… \| sha256sum` → `6293283e…` |
| F3 | The restore was a closure precondition: "1. Restore census/round-10/cert-16.json from HEAD" | `census/round-11/final-27.json:228`; `final-31.json:111`; `final-32.json:118` |
| F4 | Neither LOG nor the r12 mistakes ledger records that the relay state is committed. M40 records only the overwrites | `LOG.md:351-357`; `corpus/lessons/round-12.md:102` |
| F5 | The installed census is `6a000c59…` (= `cand-census-02.sh`). Nothing in r11 certified the installed bytes. `census/round-11/cert-16.json` freezes `462dabd2` and `60aef4c0` and sets `c03_variant_certified: true` (`:604`) next to `installed_r11_bytes_certified: false` (`:602`) | `sha256sum tools/souji-census.sh tools/cand-census-0*.sh`; `census/round-11/cert-16.json:10-18,599-605` |
| F6 | The r11 harness hard-codes both author and destination: `"seat": "S16"` (`tools/cand-s16-cert.py:1772`) and an unconditional write to `census/round-10/cert-16.json` (`:1856-1860`). Every seat that ran it produced a file that self-declares as S16 | `grep -n` on the harness |
| F7 | `verify` / `vault-verify` / `quarantine` installed digests still equal r11's frozen digests (`9adb1764`, `f9e778ca`, `141c0fdc`) | `sha256sum tools/souji-{verify,vault-verify,quarantine}.sh` vs `census/round-11/cert-16.json:12-14` |
| F8 | Python 3.14.7 behaviour: `json.loads('{"verdict":"fail","verdict":"pass"}')` → `{'verdict':'pass'}`; `isinstance(True,int)` and `True==1` are both True; `json.loads` accepts `NaN`; with TMPDIR unset, `tempfile.gettempdir()` → `/tmp` | eval probe (language semantics, not lane verification) |

## Counterexamples

**CX1. A real false-success record is committed and nothing gates it (calibration, coverage).**
- **Counterexample.** C1 ships with synthetic fixtures only. At the same time, `HEAD:census/round-10/cert-16.json` keeps asserting `certification_ready: true` for census bytes `60aef4c0`, which are not installed (F1, F2, F5).
- **Effect.** The round would add a validator while the lane's most-cited certification artifact stays false. That is new reporting, not a calibration gain.
- **Smallest correction.**
  - Add a real-replay case: a fragment derived from F1 claims `{artifact: tools/souji-census.sh, sha256: 60aef4c0…, exit_code: 0, verdict: pass}`, against a /var/tmp root holding a copy of the installed census pinned to `6a000c59…`. Expect exit 1 with `digest-mismatch`.
  - Record F2 as a mistake row with its disposition. Restoring the file is a bookkeeping write that belongs to L1, not to any seat.
- **Status.** Fact (F1–F4). That L1 has not already planned this is an inference.

**CX2. A candidate path that matches its own digest gives exit 0 without an allowlist (calibration).**
- **Counterexample.** `census/round-11/cert-16.json:604` certifies `cand-census-03`. A fragment `{artifact: tools/cand-census-03.sh, sha256: 60aef4c0…}` passes "wrong installed digest", because that file's own digest is `60aef4c0` (F5).
- **Effect.** The contract's "installed" check reduces to "the digest of whatever path the fragment names".
- **Smallest correction.** Hold the installed artifact set as a constant inside the gate (ReviewEvidence I1). Add this exact replay as a selftest case expecting exit 1 `artifact-not-installed`. If the case returns 0, C1 is rejected.

**CX3. The author field is a harness constant, not provenance (calibration; no independence claim may be made).**
- **Counterexample.** Seats S15, S30, S32 and others ran `cand-s16-cert.py`, and every output says `seat: S16` (F6; `rubric-score-19.json:30` names an `s15-CERT-R11-FULL` state of the same file). A "unique author" check therefore passes strings, not seats.
- **Smallest correction.**
  - The gate reports `declared_author` only.
  - The lane text never counts distinct authors as independent seats.
  - Fragment paths are round-scoped, e.g. `census/round-13/cert-<author>.json`, which makes overwriting a sibling's file visible as a path collision.
- **Limitation.** The gate cannot authenticate identity; independence stays a Q5 blind re-derivation (`corpus/QUALITY.md:29`).

**CX4. Dropping a fragment hides an honest fail (calibration).**
- **Counterexample.** The manifest is one mutable file listing fragments, so it is the new relay. Author A writes `cert-A.json` with an honest `verdict: fail`. Anyone edits the manifest to list only `cert-B.json` (pass). Required-set coverage (ReviewEvidence I2) is still met by B.
- **Smallest correction.** The gate requires that the manifest's fragment list equals the set of fragment files under the declared round dir (`census/round-<N>/cert-*.json`). An unlisted file gives `fragment-unlisted` (exit 1). Conflicting verdicts for one (artifact, suite) give `verdict-conflict` (exit 1), never "the pass wins".

**CX5. Old-round evidence on unchanged bytes passes (calibration, coverage).**
- **Counterexample.** By F7, a fragment that recycles r11 evidence for `souji-verify.sh` (`9adb1764`) matches the installed digest today. Yet that evidence came from the compromised relay round.
- **Smallest correction.** Evidence and fragment paths must sit under `census/round-<N>/` for the gate's declared round. The fragment carries `round` and must equal it; anything else gives `stale-round`.

**CX6. Same-round tool mutation (operability, calibration).**
- **Counterexample.** C2 edits `tools/souji-quarantine.sh` this round (`claims.json:6`). Any fragment produced before C2 lands then mismatches. Conversely, a gate run before C2 lands can report "clean" for bytes that are about to be replaced. This is the r11 mid-round drift class (`final-27.json:31`).
- **Smallest correction.** L1 runs the gate last: after every tool write, at the commit point. The gate prints the digests it measured. L1 records those printed digests in the round evidence and checks that they equal the committed blob, `git -C <lane> rev-parse HEAD:tools/<tool>` hashed via `git show … | sha256sum`.

**CX7. JSON and type confusion turns a fail into a pass (calibration).**
- **Counterexample (F8).**
  - Duplicate keys: a reviewer reads the first `verdict` (`fail`) while the gate parses the last (`pass`).
  - `"exit_code": true` equals 1, and passes as an integer.
  - An 8-char digest prefix (the r11 convention throughout) could slip past a `startswith` comparison.
  - `NaN` is accepted.
- **Smallest correction.**
  - Parse with `object_pairs_hook` and reject duplicate keys.
  - `type(x) is int` for `exit_code`.
  - Digests must match `^[0-9a-f]{64}$` exactly.
  - Pass `parse_constant` to reject NaN/Infinity.
  - Each failure gives exit 2 `malformed`.

**CX8. Evidence text does not bind to the bytes (calibration).** This is the S31 incident: 462dabd2 was certified using cand-census-08's selftest tail (`final-27.json:122`; `final-32.json:105`).
- **Counterexample.** A fragment with a correct `sha256` and an evidence file copied from another tool's run passes the existence check.
- **Smallest correction.** The evidence is produced by a fixed wrapper whose first line is `sha256=<hex of the executed path>` and last line is `exit=<n>`. The gate requires both to equal the fragment's fields (`evidence-digest-mismatch`, `evidence-exit-mismatch`).
- **Limitation.** This catches substitution, not a consistent lie.

**CX9. Fixtures may not prove the gate can fail (operability).**
- **Counterexample (inference about likely fixture design).** Fixture A ("digest mismatch") may also lack evidence. It then returns exit 1 even if the digest check is deleted. A selftest that asserts only "rc != 0", or only "id ∈ findings", stays green after a check is removed.
- **Smallest correction.**
  - Each negative fixture is the clean fixture plus exactly **one** mutation.
  - The selftest asserts the **exact** finding-id set and rc.
  - Each finding id is emitted on exactly one source line, so L1 can mutation-test a /var/tmp copy of the gate (final check K6).

**CX10. Q4 can break silently (operability).**
- **Counterexample (F8).** `tempfile.mkdtemp()` without `dir=` lands in `/tmp` when TMPDIR is unset, and in an arbitrary place when TMPDIR is set. Q4's grep test (`corpus/QUALITY.md:28`) misses Python.
- **Smallest correction.** Every `mkdtemp` passes `dir="/var/tmp"`, and cleanup sits in `try/finally`.

**CX11. Wording leakage (calibration).**
- **Counterexample.** A clean exit 0 that prints "certified" or "independent" restates the r11 overclaim (`cert-16.json:613`).
- **Smallest correction.** Clean output says `evidence-consistent`. The words `CERTIFIED` and `independent` appear in no positive message (final check K5).

## Admit / reject cases for the C1 *claim*

Reject C1 as a calibration improvement if **any** of these holds:
- **R1.** The after-metric is gate existence, or a synthetic selftest only (`before.json:5`-style 0→1).
- **R2.** The CX2 replay (`tools/cand-census-03.sh`, own digest) returns 0, **or** the non-`cand-` replay (`tools/souji-census.impl-46.sh` with its own digest; see Addendum CX12) returns 0 while the lane text claims "installed hash" checking.
- **R3.** The CX1 replay (F1's claim against the installed `6a000c59`) does not exit 2 with exactly `artifact-digest-mismatch`. In the landed gate this finding is level 2, not level 1 (Addendum).
- **R4.** Any lane text calls the fragment authors independent, or calls a clean gate run certification.
- **R5.** A negative fixture fails for more than one reason, or the selftest asserts only rc.
- **R6.** The gate run that is cited predates the last tool write of the round (CX6).
- **R7.** F2 (committed relay at HEAD) goes unrecorded while C1 claims the relay class is handled.

Admit C1 as a narrow integrity improvement, not certification, only if **all** of these hold:
- **A1.** The metric is "documented evidence-integrity failure classes rejected by single-mutation fixtures plus real replays: 0 → k". The k classes are listed: M40 relay/wrong bytes, the CX2 candidate path, the S31 evidence substitution, K5 missing evidence, false pass, honest fail, and unlisted fragment.
- **A2.** R2 and R3 replays are red, with exact finding ids.
- **A3.** The K6 mutation check shows every finding id is load-bearing.
- **A4.** Certification is stated as OFF, and author identity is stated as declared-only.

## Final checks for L1 (not run by this seat; exact)

```
L=/home/vgpnk/Projects/shokunin/souji-shokunin
# K1 fact behind CX1/F2 (expect 662294df…; e879ba0 gives 6293283e…)
git -C $L show HEAD:census/round-10/cert-16.json | sha256sum
git -C $L show e879ba0:census/round-10/cert-16.json | sha256sum
# K2 installed census digest used by the replay pin (expect 6a000c59…)
sha256sum $L/tools/souji-census.sh
# K3 gate selftest; expect rc=0. Landed gate: digest mismatch = rc 2 `artifact-digest-mismatch`, cand-* = rc 2 `artifact-candidate`.
#    R2/R3 real replays are NOT in the landed selftest (Addendum); L1 runs them by hand under mktemp -d /var/tmp (K8).
python3 $L/tools/souji-cert-evidence.py --selftest; echo rc=$?
# K4 hardening greps (each ≥1, last =0)
grep -c 'object_pairs_hook' $L/tools/souji-cert-evidence.py
grep -nE 'mkdtemp\(' $L/tools/souji-cert-evidence.py $L/tests/fixtures/r13-cert-evidence.py   # every hit has dir="/var/tmp"
grep -c 'TMPDIR:-/tmp' $L/tools/souji-cert-evidence.py $L/tests/fixtures/r13-cert-evidence.py
# K5 clean-path wording: no positive CERTIFIED/independent in the gate's messages
grep -niE 'certified|independen' $L/tools/souji-cert-evidence.py   # inspect: only negations/limitations allowed
# K6 load-bearing check (if each id is emitted on one line): in a mktemp -d /var/tmp copy, neuter one
#     emit line per finding id; --selftest of that copy must exit nonzero for every id.
# K7 ordering: re-run K3 after C2's quarantine write and immediately before the commit; record printed digests.
# K8 non-cand replay (CX12): in R=$(mktemp -d /var/tmp/r13-cx12.XXXXXX) with trap 'rm -rf "$R"' EXIT, copy
#    $L/tools/souji-census.impl-46.sh to $R/tools/, write a fragment {artifact: tools/souji-census.impl-46.sh,
#    sha256: <its own sha>, exit_code: 0, verdict: pass, evidence + evidence_sha256} and a manifest; run
#    --root $R --manifest $R/manifest.json. Expected on the landed gate: rc 0 (clean). That is the residual, not a gate bug
#    under its declared scope; it bars any lane text saying the gate checks *installed* bytes.
```

## Addendum: landed gate (`tools/souji-cert-evidence.py`, mtime 02:24; read-only grep)

EvidenceGate reported which hardening items it applied. I checked each against the code:

| item | landed? | code |
|---|---|---|
| duplicate JSON keys rejected | yes | `:390` `object_pairs_hook=_reject_duplicate_keys` |
| `exit_code` bool/str rejected | yes | `:438` `isinstance(exit_code, bool) or not isinstance(exit_code, int)` |
| full 64-hex digests | yes | `:196` `SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")` |
| mkdtemp under /var/tmp | yes | `:1151` `tempfile.mkdtemp(prefix=…, dir="/var/tmp")` inside `try/finally` rmtree `:1452-1453` |
| exact finding-id set in selftest | claimed | `:131-133` header; I did not audit every case |
| evidence pinned by `evidence_sha256` | yes | finding `evidence-digest-mismatch` `:83` (partly closes CX8: substitution of the evidence file is caught, but evidence content is not tied to the artifact) |
| clean wording | yes | `:953` `scope: evidence_valid/NOT_CERTIFICATION …` (closes CX11) |
| CX4 `fragment-unlisted` | **declined** (scope: declared fragments only) | none |
| CX2 installed allowlist | **replaced by denylist** | `:664` `.name.startswith("cand-")` → `artifact-candidate` |
| exit levels | changed from my assumption | `:81-88`: digest mismatch, false pass and candidate are level 2 (could-not-evaluate); only `fragment-reported-fail` is level 1 |

**CX12. The `cand-` denylist is bypassed by committed files, including the r11 wrong-selection candidate (calibration). Fact.**
- `git ls-files tools` lists 54 `.sh`/`.py` files that are neither the four installed tools nor `cand-*`. They include `tools/souji-census.impl-46.sh`, the candidate that r11's "most selftest passes" rule wrongly picked (`census/round-11/cert-09.json:74`; `dissent-32.md:74-79`), plus `souji-verify.impl-16.sh` and the `*.r9-s18.sh` lineage.
- A fragment naming any of these with its own digest passes `:664` and the digest check at `:679`.
- In addition, `--root` is caller-chosen. A root whose `tools/souji-census.sh` is a copy of any candidate passes even with an allowlist. "Installed" therefore holds only when `--root` is the lane worktree and that worktree equals HEAD.
- **Smallest correction.** No gate change is required under its declared scope (`:953`). The C1 claim text must not say "rejecting mismatched installed hashes" unqualified. It should say "rejects a declared digest that differs from the bytes at the declared path under `--root`, and `cand-*` names".
  - If "installed" is wanted, the gate needs a fixed set of the four tool paths, and L1 runs it with `--root $L`, recording `git -C $L status --porcelain -- tools/` empty.
  - That fixed path set is a 4-line constant. It is a fixable defect, not a tradeoff.

**CX4 residual (declined).** In frozen mode the reachable inputs are pinned (`:921-929`). An honest-fail fragment that the manifest never lists is invisible to the gate, so r11's relay pattern (pick which evidence exists) survives one level up, at the manifest.
- This is a tradeoff L1 must state, not a gate bug.
- C1 may claim "declared-fragment consistency", **not** "rejects false success" at the round level, unless L1 adds the cheap check: `ls census/round-13/cert-*.json` equals the manifest list.

**Frozen mode calibration note (fact from `:109-129`).** `--frozen` evaluates with root = the snapshot dir, and `expected.json` "is not self-authenticated" (`:128-129`).
- A green frozen run proves the snapshot is internally consistent and unchanged since it was pinned. It says nothing about lane-installed bytes.
- `claims.json:5`'s "digest-pinned frozen input run" must not be read as an installed-hash check.

**Updated claim-level verdict.** The landed gate closes CX7, CX10 and CX11 and partly closes CX8. CX2/CX12 (installed identity) and CX4 (completeness) remain open as stated scope limits.
- C1 is admissible only as a narrow integrity improvement under A1–A4.
- The metric must not count "installed" or "unlisted-fragment" as rejected classes until K8 and the CX4 list check are red.

**CX12 disposition (re-checked by grep after EvidenceGate's correction).** The wording fix landed:
- `:50-51` the artifact is "the bytes measured (the gate cannot prove this path is the installed tool location)".
- `:100-104` "`.impl-*` are not detected; the gate has no installed-tool allowlist and --root is caller-chosen … grants no certification".
- `:687` the mismatch detail reads `declared=%s measured=%s`.

This closes CX12 as a **wording** defect: the gate no longer overclaims. The installed-identity gap remains a stated limitation; the denylist still matches only basenames starting `cand-`. C1's claim text in `census/round-13/claims.json:5` ("Installed-byte evidence gate") was not edited by EvidenceGate. L1 must align it to "declared-artifact digest gate" or R2 applies.

## Limitations
- CX1–CX11 were written against the contract text, before any gate code existed. The Addendum checks the landed gate by read-only grep only: I did not run its selftest or K8. K8's expected rc 0 is an inference from `:664`/`:679`.
- None of these corrections authenticate authors or prove a command was executed. They detect inconsistency and substitution, not a consistent fabrication.
- I neither restored nor edited `census/round-10/cert-16.json`. That is L1's decision.
- I did not read the operator sweep contents.

## Peer messages sent
- `SoujiR13.EvidenceGate`: CX2, CX4, CX7, CX9, CX10 hardening items.
- `SoujiR13.MistakeLedger`: F1/F2 committed-relay fact, as a candidate mistake row.
