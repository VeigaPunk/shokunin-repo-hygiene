# R13 w1 — ReviewEvidence (C1 manifest contract semantic review)

Seat: SoujiR13.ReviewEvidence (reviewer, leaf). Scope: review the C1 proposed manifest contract
for semantic holes. No implementation edited, no tests or builds run, no installs performed.
Tools installed/updated this seat: none. Certification remains OFF. This seat is NOT an
independent non-author verifier.

Contract under review (as dispatched, `.ufo/waves/round-13/w1-dispatch.json:399`, EvidenceGate):
`tools/souji-cert-evidence.py --root PATH --manifest PATH` with an explicit `fragments` array of
relative fragment JSON paths; each fragment requires `author`, artifact relative path, `sha256`,
`command`, `exit_code`, `verdict` (pass|fail), evidence relative path. Checks: contained regular
nonsymlink paths; duplicate authors/shared fragments; wrong installed digest; absent evidence;
pass with nonzero exit or fail with zero exit. Exit 0/1/2 = clean/failed/could-not-evaluate.

## Axes
- calibration: does the gate reject false certification, not only malformed input.
- coverage: does a pass mean the full required evidence set was checked, not just the listed subset.
- operability: is the gate runnable, deterministic, and its negative/positive cases checkable.

## Verdict on the proposal
The proposed checks are necessary but not sufficient. As written, the gate validates **evidence
consistency for whatever fragments are listed**. It does not validate (a) that the listed artifacts
are the installed set, (b) that the listed set is complete, (c) that the digest was measured on the
bytes the command ran against, or (d) that the verdict is derived from evidence rather than
self-declared. Each hole below has a documented r11/r12 precedent, so each is a real failure mode
for this lane, not a hypothetical.

## Findings (severity order)

### F1 — HIGH — candidate artifacts can be certified as if installed
Precedent:
- `census/round-11/cert-16.json:599-605`: `installed_r11_bytes_certified: false` and
  `c03_variant_certified: true` in the same verdict block.
- `census/round-11/cert-16.json:612-613`: `certification_ready: false`, but
  `certification_verdict` reads "CERTIFIED alternative exists: cand-census-03.sh (60aef4c0)"
  while installed is 462dabd2 (`cert-16.json:16`: `souji-census.sh (r11 installed, mid-round v2)` = 462dabd2; `:17`: cand-census-03 = 60aef4c0).
- `census/round-11/S08-fragment.md:5,50`: CERTIFIED on `tools/cand-census-08.sh` (7eb1b8d9); the
  installed census was 11bf9cdf / 462dabd2 at that time.
- `census/round-11/cert-13.json:366`: "CONDITIONAL CERTIFIED as a candidate set" while "on installed
  bytes ... the toolchain remains NOT-CERTIFIED".
Hole: the gate's "wrong installed digest" check is only meaningful if the artifact path is pinned.
A fragment naming `tools/cand-census-08.sh` with its own correct sha passes a naive
"sha(file at artifact path) == fragment.sha256" check.
Minimum invariant I1: the artifact set is a **gate-owned constant** (the four installed tools:
`tools/souji-verify.sh`, `tools/souji-vault-verify.sh`, `tools/souji-quarantine.sh`,
`tools/souji-census.sh`), not read from the manifest. Any other artifact path → finding
`artifact-not-installed` (exit 1). Candidate paths are never certifying.

### F2 — HIGH — coverage is whatever the manifest lists (complete coverage not checked)
Hole: a manifest with one fragment, or zero, can exit 0. "Pass" then means "listed evidence is
consistent", which is the r11 relay failure mode restated: the relay chose which evidence exists.
Precedent: `corpus/QUALITY.md:30` (Q6, one author per fragment) and `census/round-11/cert-13.json:412-417`
(`certification_flip_preconditions` requires all four installed tools re-certified on the installed path).
Minimum invariant I2: the required set is (installed artifact × required suite). Each required pair
has exactly one fragment. Missing pair → `coverage-missing` (exit 1). Zero fragments → exit 1
`coverage-missing`, never 0. Extra fragments outside the required set → `unexpected-fragment` (exit 1).

### F3 — HIGH — digest is self-reported; freshness is only checked at gate time, not at run time
Hole: the gate compares `fragment.sha256` to the *current* file. It cannot tell which bytes the
command actually ran against. A fragment measured on bytes X, with the file later changed to Y and
the author writing Y, passes if the author lies; a fragment with the honest X fails only by luck of
timing.
Precedent: `census/round-11/cert-13.json:18-27`: `tools/souji-census.sh` was rewritten mid-run
(11bf9cdf → 462dabd2) after freeze; the run's own J14/V07 probes were on new bytes, and the
frozen-copy verdicts were on old bytes. `cert-16.json:19`: "changed bytes twice during this seat".
Minimum invariants:
- I3a: fragment records `artifact_sha256_before` and `artifact_sha256_after` (hash of the **executed**
  copy, and of the installed path before/after). Both must equal the gate-time installed sha (exit 1
  `mid-run-drift` otherwise).
- I3b: `evidence_sha256` pinned in the fragment and recomputed by the gate (`evidence-digest-mismatch`).
- I3c: the gate re-hashes the installed artifact before and after reading fragments (TOCTOU bound);
  a change during gate execution → exit 2 `could-not-evaluate`.
- I3d: fragment records `round` and the gate takes `--round N`; fragments from another round →
  `stale-fragment` (exit 1). Replay of an old r11 fragment is otherwise indistinguishable.

### F4 — HIGH — false pass via self-declared verdict; narrative fields not ignored
Hole: the gate's check is "verdict agrees with exit_code". A suite can exit 0 and still report
`unsafe_outcomes: 3`. The proposal never reads evidence content, so such a fragment passes.
Precedent: `census/round-11/cert-13.json:362-363`: run1 frozen baseline "3 unsafe" recorded as an
honest OPEN result; the fragment-level verdict is a free-text string. `cert-16.json:612-613` shows
a narrative `certification_verdict` string that contradicts `certification_ready: false`.
Minimum invariants:
- I4a: pass requires the gate to **derive** pass from evidence content using a fixed per-suite result
  rule (e.g., suite selftest final line `selftest: N checks, 0 failed` with exit 0; cert JSON with
  `certification_ready == true`, `unsafe_outcomes == 0`, `test_failure_count == 0`, `errors == []`).
  Fragment `verdict` must equal the derived verdict (`verdict-disagrees-with-evidence`, exit 1).
- I4b: the gate never reads narrative fields (`certification_verdict`, `verdicts.*` prose, notes).
  Only the structured keys named in I4a under the artifact's own path count. Keys for other
  artifacts in the same JSON (e.g., `c03_variant_certified`) are ignored.
- I4c: the gate's output is its own verdict; it never echoes a fragment's "certified" claim.

### F5 — HIGH (limitation, must be stated) — author identity is an unauthenticated string
Hole: `author` is free text. "S16" / "s16" / "S16 " pass a naive uniqueness check; one seat can
emit several authors; two certifiers can share the same harness and still be "unique authors".
Precedent: `census/round-11/cert-13.json:30-34` and `cert-16.json:622` both run the same frozen
harness (`cand-s16-cert.py`, sha 4130502c); `cert-13.json:33` says candidates "were selected to
satisfy" the frozen judge. The two certifiers are correlated, not independent.
Minimum invariants:
- I5a: normalize author (strip + casefold) and require uniqueness on the normalized value; require a
  roster-shaped id (the dispatch seat id) — otherwise `author-malformed` (exit 2).
- I5b: fragment path must be bound to author (fragment file name or parent dir equals the author id).
- I5c: fragment records `harness_sha256` of the **executed** harness copy; the gate requires it equal
  the tracked harness bytes; a `harness_modified: true` flag or sha mismatch → exit 1
  `harness-not-tracked` (cert-13 ran a modified scratch copy, `cert-13.json:31-32`).
- Limitation (not gate-checkable): the gate cannot prove the author is not the parent, a sibling, or
  the same model/harness. The gate output must say "evidence-consistent", never "independent".
  Independence stays a Q5 blind re-derivation claim, not a gate result.

### F6 — HIGH — unique fragment ownership is under-specified
Hole: uniqueness of fragment *paths* and *authors* does not stop:
- hardlinks: two fragment paths sharing one inode (same bytes, two owners);
- the same `evidence` path referenced by two fragments;
- overwrite: a fragment rewritten after its author wrote it (the r11 relay failure, `round-11.md:14`,
  `corpus/QUALITY.md:30`).
- symlinked parent directories: "nonsymlink" on the leaf only lets `census/round-13/` → elsewhere pass.
Minimum invariants:
- I6a: for every fragment and evidence file: `realpath` of every component is under `--root`; regular
  file; `st_nlink == 1`; `(st_dev, st_ino)` unique across all fragments and evidence (else
  `shared-inode`, exit 1). Path escape or symlink in any component → exit 2 `path-not-contained`.
- I6b: evidence path unique across fragments; evidence path ≠ artifact path, ≠ fragment path, and not
  inside `tools/` (a tool cannot be its own evidence).
- I6c: fragment must carry a `run_id` unique in the manifest; the evidence file's first line or key must
  embed the same `run_id`. Overwrite then changes the run_id and is detected at gate time.
- I6d: fragments are written O_EXCL by their author and never rewritten (operator procedure; gate
  cannot prove it, record as a limitation).

### F7 — MEDIUM — "absent evidence" is weaker than "evidence is the measured output"
Hole: the existence check accepts an empty or unrelated file. The r12 K5 defect (`round-12-verifier-spotcheck.md`,
reject row: Gate claimed a committed fixture that does not exist) is the same class for the `command`
field: a fragment can name a script that does not exist.
Minimum invariants:
- I7a: evidence file is non-empty and parseable under its declared format (JSON or text); empty → exit 1
  `evidence-empty`.
- I7b: the script named in `command` (first path token) must exist, be regular, and its sha256 must
  equal the sha recorded in the fragment (`command-script-missing` / `-digest-mismatch`, exit 1).

### F8 — MEDIUM — "complete coverage" and "evidence validity" must be separate outputs
Hole: one aggregate pass hides that coverage can be complete while evidence is invalid, or the
reverse. Output must report `evidence_valid` (I3–I7), `coverage_complete` (I2), and `honest_failures`
(count of derived fail) separately. Certification requires all three to be true; the gate itself never
sets certification ON (certification stays OFF per round contract).

### F9 — MEDIUM — exit-code ordering not pinned
Spec gives 0/1/2 but not precedence. Pin: 2 (could-not-evaluate: malformed JSON, path escape,
unreadable file, author-malformed, concurrent change) overrides 1 (any finding) overrides 0. A manifest
with a fail fragment and a malformed fragment must exit 2. Honest fail (fragment verdict fail, derived
fail, consistent) exits 1 and is recorded as evidence, not as an error.

### F10 — MEDIUM — candidate-selection bias is not detectable from hashes
Precedent: `census/round-11/cert-13.json:33,364` and `round-12.md:102-103` (M40/M41: selection rule
picked a candidate that fails the class). The gate cannot see the candidate universe.
Minimum invariant (partial): fragment declares `candidates_considered` count and the selection rule
id; the gate requires the certified artifact to be an installed path (I1), so any promotion must happen
by installing the bytes first, then certifying them. Full detection needs a pre-registered candidate
list committed before runs. Limitation; not closable inside the gate.

### F11 — LOW — positive control required
A gate that exits 1 on every input passes every negative case. Selftest must include one fully
consistent clean manifest (all four installed artifacts, correct digests, derived pass, unique
owners/inodes/evidence) asserting exit 0, plus the negative cases below.

## Minimum invariant set (for L1 integration)
I1 gate-owned artifact set; I2 complete coverage, zero fragments = fail; I3 before/after/evidence/round
digests with live re-hash; I4 verdict derived from evidence, narrative ignored; I5 normalized unique
author, bound fragment path, executed-harness sha; I6 contained regular nlink=1 unique inode, unique
evidence, no self-evidence, run_id embedded; I7 non-empty evidence, command script exists and pinned;
I8 separate evidence_valid / coverage_complete / honest_failures; I9 exit precedence 2>1>0 and
positive control.

## Selftest cases to demand (each names the finding id it must produce)
- clean consistent manifest over the four installed tools → exit 0 (positive control).
- candidate path `tools/cand-census-08.sh` with correct own sha → exit 1 `artifact-not-installed`.
- fragment sha ≠ installed sha → exit 1 `digest-mismatch`.
- sha_before ≠ installed (mid-run drift, reproducing cert-13 11bf9cdf→462dabd2 shape) → exit 1 `mid-run-drift`.
- evidence file edited after fragment written → exit 1 `evidence-digest-mismatch`.
- one of four required pairs missing → exit 1 `coverage-missing`; zero fragments → exit 1 `coverage-missing`.
- two fragments with authors "S16" and "s16" → exit 1 `duplicate-author`.
- two fragments hardlinked to one inode → exit 1 `shared-inode`.
- two fragments sharing one evidence path → exit 1 `evidence-shared`.
- verdict pass, exit 0, evidence `unsafe_outcomes: 3` → exit 1 `verdict-disagrees-with-evidence` (false pass).
- verdict fail, exit 0, evidence consistent with fail → exit 1 honest failure, `honest-fail` recorded (not 2).
- `harness_modified: true` or harness sha ≠ tracked → exit 1 `harness-not-tracked`.
- fragment with stale `round` → exit 1 `stale-fragment`.
- narrative string says CERTIFIED while structured `certification_ready: false` → exit 1 (structured wins; narrative ignored).
- symlinked parent dir or `../` escape → exit 2 `path-not-contained`.
- malformed JSON → exit 2 `could-not-evaluate`.
- command script missing → exit 1 `command-script-missing`.
- fail fragment plus malformed fragment → exit 2 (precedence).

## Limitations (stated, not closable by the gate)
- The gate proves consistency between declared fragments and current bytes; it does not prove the
  command was executed. Re-execution in a /var/tmp copy would close that but is out of scope for this
  design and would be execution in the gate.
- Author identity is unauthenticated. Independence is not a gate output.
- Correlated certifiers (shared harness, shared model, same lane) are undetectable from hashes.
- Candidate-selection bias is undetectable without a pre-registered candidate list (F10).
- A passing gate is not tool safety, not deletion authorization, not operational clearance
  (`cert-16.json:629` scope note). Certification stays OFF.

## Final checks for L1 (after all seats land; not run by this seat)
- `python3 -m py_compile /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-cert-evidence.py`
- `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-cert-evidence.py --selftest; echo rc=$?`
  expect rc=0 and every case in the list above reporting its exact finding id.
- Confirm the gate's artifact set is a literal constant:
  `grep -nE 'souji-(verify|vault-verify|quarantine|census)\.sh' .../tools/souji-cert-evidence.py` ≥ 4 and no
  manifest-derived artifact list.
- Confirm no narrative-field reads: `grep -nE 'certification_verdict|certification_ready' .../tools/souji-cert-evidence.py`
  shows only the structured key comparisons in I4a.
- Confirm installed digests at check time: `sha256sum tools/souji-{verify,vault-verify,quarantine,census}.sh`
  compared to the manifest fragments, not to this report.
- Confirm certification flag is untouched: no edit to SCORECARD certification note by this round's gate.

## Evidence index
- `.ufo/waves/round-13/w1-dispatch.json:399` (EvidenceGate contract), `:454` (this seat's task).
- `corpus/lessons/round-11.md:13-18`, `:22-25`; `corpus/lessons/round-12-verifier-spotcheck.md` (K5 reject row).
- `corpus/QUALITY.md:30` (Q6), `:32` (Q8).
- `census/round-11/cert-16.json:7-17, 599-613, 619-629`.
- `census/round-11/cert-13.json:11-34, 362-369, 412-417`.
- `census/round-11/S08-fragment.md:5-7, 50-53, 75-81`.
- `corpus/lessons/round-12.md`: M40, M41 (rows at lines 102-103 of the round-12 table in `corpus/lessons/round-12.md`).
- `LOG.md:351-359` (r11 non-grant: relay overwrites, verdicts on non-installed bytes).
Facts are cited from files read in this seat. Items marked as limitations are inference about what a
hash-consistency gate cannot observe, not observed behaviour.
