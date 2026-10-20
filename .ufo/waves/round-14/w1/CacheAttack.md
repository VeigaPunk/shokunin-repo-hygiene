# CacheAttack — round 14, wave w1 (critic, C1 stale-green eligibility)

Seat: `SoujiR14.CacheAttack`, a leaf critic. It is read-only apart from this report.
Axes: calibration, operability.
Target inspected: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-evidence-cache.py`. It was absent at seat start and present (44997 B, 03:51) after a bounded existence wait.
Consumer context: `census/round-14/cache-demonstration.py`, `census/round-14/run-verification.py`, `tests/fixtures/r14-cache-frozen/`, and `corpus/QUALITY.md` Q20.
`tests/fixtures/r14-evidence-cache.py` was still absent at report time (`to-verify`).
I opened RULES.md first. No tools were installed or upgraded because none were needed. I made no edits outside this report. I did not open `census/operator-sweep-*` or `~/.omp/agent` beyond RULES.md and skills.
I messaged `SoujiR14.CacheGate` twice: once with the design attacks before the gate existed, and once with the concrete findings B1–B3 below.

## Evidence classes

**Code inspection (not executed).** The gate source lines cited below, the r13 runner `census/round-13/run-verification.py:49-54`, the r14 runner, and the r14 demonstration. The gate's CLI and `--selftest` were not run. No fixture was run.

**Exercised read-only observations (commands I ran; none of them are tests):**
- `jq` over `census/round-13/verification.json` and `verification-attempt-1.json`:
  - In attempt-1, all 14 results lack a per-result `measured_commit` (`ABSENT`).
  - In the final file, 5 retained results carry `measured_commit=6ed10a7…` with `retained_from=…attempt-1.json`: evidence-frozen, structure-selftest, and both historical replays.
  - `sources-contract` carries `23014d4…`, a descendant of the top-level `6f8ee0f`. This shows per-result revisions really do diverge from the top-level value.
- `git rev-parse <c>:tools/souji-cert-evidence.py` gives `ad9dacf…` at `6ed10a7` and `91e1a7d…` at `6f8ee0f`. The `git diff` between them is the 1-line regex in `_finding_ids` (l.1018-1021), which is used only by the selftest via `_record` (l.1031).
- `git show <c>:<path> | sha256sum` against `verification.json` `installed_sha256`:
  - cert-evidence: json `943d664c…` = blob@6f8ee0f; blob@6ed10a7 is `a029aaa0…`.
  - quarantine: json `df407511…` = blob@6f8ee0f; blob@6ed10a7 is `a94621bf…`.
- `sha256sum` of `tests/fixtures/r14-cache-frozen/{record.json,dependency.txt}` matches the `expected.json` pins (`67221a33…`, `875598b6…`). All three files are regular with nlink 1.
- `/var/log/pacman.log`:
  - python upgraded 3.14.6→3.14.7 on 2026-10-11.
  - shellcheck installed 0.11.0 on 2026-10-18.
  - git 2.55.0 installed 2026-10-03.
  - There was no toolchain drift inside the r13 window. The log shows that drift happens between rounds.
- `git status --porcelain` (lane): `tools/souji-evidence-cache.py`, `census/round-14/`, and `tests/fixtures/r14-cache-frozen/` are untracked; HEAD is `a31642d` (= r14 `BASE`).
- `git ls-files` secret-shaped names: `tests/fixtures/case-F10/app.env` and `creds.pem` would be refused as `path-protected`. This is conservative and documented.

## Attacks, verdicts and smallest corrections

### A1 Measured-revision laundering — holds in the gate; precedent confirmed; one consumer risk
- **Precedent (exercised):** r13 `run-verification.py:51` sets `retained.get("measured_commit", PREVIOUS["measured_commit"])`. Attempt-1 had no per-result revisions, so all 5 retained results inherited the run-level `6ed10a7`. It is inferred, not measured.
- **Gate (inspection):** `measured_commit` must match `COMMIT_RE` `[0-9a-f]{40}\Z` (l.182, l.517-522). An absent, short or symbolic value gives `measured_commit-invalid` (exit 2). The value is echoed verbatim only when valid (l.755-756). There is no defaulting from HEAD or top level. The selftest has `measured-commit` and `per-result-commit` cases (l.987-1045). **Not a bug.**
- **Consumer (inspection):** `cache-demonstration.py:313-314` retains `record["measured_commit"]` with `measured_commit_source="record"`. Its producer captures `measured_commit` and `dependencies` in the same execution (l.271-284). That is correct.
- **Residual calibration risk — r14 runner (owner: L1, not CacheGate):** `census/round-14/run-verification.py:46,51,75` stamps every result with `git rev-parse HEAD`. All r14 artifacts are untracked and HEAD is `a31642d` (= `BASE`, where the gate does not exist). A pre-commit run would therefore label fresh results with a revision that does not contain the measured bytes. `installed_sha256` (l.76) is the real byte binding.
  - Smallest correction: also record `git status --porcelain -- <paths>` (or a dirty boolean) in `data`, or run only after commit.
  - The same caveat applies to `cache-demonstration.py`: its `measured_commit` is the lane HEAD, but its dependencies are synthetic `/var/tmp` files, so the value is a label.

### A2 Stale green (r13 precedent) — correctly refused; false-stale is intended
- Retained evidence-frozen and historical-replay-* were measured at `6ed10a7` against cert-evidence `ad9dacf`; the installed bytes are `91e1a7d`.
- A whole-file digest yields `dependency-digest-mismatch` (exit 1). My inspection inference is that the change was selftest-only, so these specific greens were probably still valid. Refusing them anyway is conservative false-stale, which Q20 accepts. **Not a bug.**

### A3 Dependency omission / transitive dependencies — intentionally bounded, documented
- Inspection: only declared keys are measured (l.543-615). The selftest `unrelated-change` case (l.864-871) *is* the omission case: an undeclared file changes and the result is exit 0.
- Real transitive edges a hand-written record could miss:
  - `tests/fixtures/r13-quarantine-bounds.sh:50` implicitly runs `tools/souji-verify.sh` and honors env `SOUJI_QUARANTINE_BIN` (l.49).
  - The cert-evidence selftest reads `tests/fixtures/r13-cert-frozen/expected.json` (l.1150-1153).
- The bound is stated in the docstring (l.142-144) and Q20 ("does not infer complete dependencies"). **Bounded, not a bug.**
- Optional teeth for the judge's tradeoff, not required by the contract: a repeatable `--require REL` would let the *caller* fix a minimum set, giving a `dependency-undeclared` finding.

### A4 Same content, changed runtime — bounded but under-documented
- Absolute paths are refused (`path-absolute`, l.256-257 and l.588-590), so toolchain and out-of-root inputs can **never** be declared. Examples: `git repo structure` (structure-selftest), shellcheck, python, env, `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (sources-contract).
- A record for such a result is reusable after any upgrade. RULES.md *mandates* upgrades, and pacman.log shows they happen between rounds.
- Smallest correction (docs only): add a Limitations bullet. Interpreter, toolchain, environment and out-of-root inputs are outside eligibility, so results that depend on them must not be retained. The demonstration and runner already re-execute everything, so nothing breaks.

### A5 Attacker-edited record — bounded; one cheap laundering vector open
- Inspection: the record is unauthenticated. An editor who recomputes digests gets exit 0. This is documented in l.139-141 and l.11-13, and in Q20 ("does not … authenticate execution").
- Frozen mode pins inputs, but `expected.json` is the unpinned trust anchor (l.135). **Bounded.**
- **Digest-provenance laundering (exercised data):** take r13's retained `evidence-frozen` (`matched=true`, `mc=6ed10a7`) and backfill `dependencies` from the run-level `installed_sha256` (`943d664c…`, which is 6f8ee0f bytes). The record then exits 0 even though `6ed10a7`'s bytes were `a029aaa0…`. This is the same pattern as r13 l.51, applied to digests.
  - The gate cannot detect it without executing git, so it is bounded.
  - Correction (docs/Q20): dependency digests must be captured by the same execution as `matched`/`measured_commit` and are never backfilled from run-level fields. Every historical r13 record must stay legacy (exit 2).
- **Unknown keys tolerated (l.50):** a record that keeps `exit_code: 1, expected_exit: 0` (r13 attempt-1 `quarantine-bounds`) but flips `matched` to `true` exits 0.
  - Optional, cheap teeth: when both are non-bool ints, `matched is True` requires `exit_code == expected_exit`. Emit a level-2 finding otherwise. `matched=false` with equal codes stays allowed, because r13 replays use a stricter `matched`.

### Actual defects (fixable, sent to CacheGate)
- **B1 (calibration, doc):** docstring l.40-42 lists "a false or non-boolean `matched`" under exit 2. The code (l.630-631, l.176-180), l.37-39 and l.101-103 make `matched=false` exit 1 `failed`. Correction: delete "a false or".
- **B2 (operability/safety):** `_record_text` (l.469-488) reads `--record` paths via `_read_regular_text` with no `_protected_reason` check, lexical or realpath. `--record @$HOME/.ssh/x.json` is opened and read, and for valid JSON its `name` is echoed (l.753-754).
  - This conflicts with the contract "never allow protected credential paths".
  - Correction: check both `Path(value).parts` and `realpath` parts before opening, then emit `path-protected`/`record-unreadable`. Add a synthetic `/var/tmp/<base>/.ssh/rec.json` selftest case.
- **B3 (calibration, operability):** `_emit` (l.751-763) does not print the evaluated root. `--root /var/tmp/old-copy` (an old tree with old bytes) gives exit 0, and the transcript cannot be told apart from a lane evaluation. Correction: print `root: <realpath>`; `meta["root"]` already exists (l.539).
- Low: `_resolve_root` runs `os.stat` on the lexical path before the realpath protection check (l.450-462), so a symlink located inside `~/.ssh` would be stat'ed (metadata only). The lexical-first rule mirrors Q21.

## Axis impact
- calibration: A1 runner dirty-HEAD labeling, A5 digest provenance, B1 and B3 affect what a "reusable" or measured-at claim means.
- operability: B2 (protected read), B3 (transcript identifies the tree), A4 (unstated runtime bound).

No finding invalidates the core claim. Within declared dependencies, legacy, empty, stale, failed and malformed records are refused, and per-result `measured_commit` is preserved verbatim. The claim must stay scoped to "declared bytes unchanged", not "result still true".

## Final L1 commands (not run by this seat)
Run from `/home/vgpnk/Projects/shokunin/souji-shokunin`:
```
git status --porcelain -- tools/souji-evidence-cache.py census/round-14 tests/fixtures/r14-cache-frozen tests/fixtures/r14-evidence-cache.py
python3 -B tools/souji-evidence-cache.py --selftest; echo "exit=$?"
python3 -B tools/souji-evidence-cache.py --frozen tests/fixtures/r14-cache-frozen; echo "exit=$?"
python3 -B tests/fixtures/r14-evidence-cache.py; echo "exit=$?"
python3 -B census/round-14/cache-demonstration.py; echo "exit=$?"
```
Historical digest-provenance check (read-only):
```
git show 6ed10a7:tools/souji-cert-evidence.py | sha256sum
jq -r '.installed_sha256["tools/souji-cert-evidence.py"]' census/round-13/verification.json
```

Attack probes, all isolated under `/var/tmp`. Each line gives the current expectation from code inspection:
```
B=$(mktemp -d /var/tmp/souji-r14-cacheattack.XXXXXX); mkdir -p "$B/r/src" "$B/p/.ssh"; printf a >"$B/r/src/a"; printf b >"$B/r/src/b"
A=$(sha256sum <"$B/r/src/a" | cut -d' ' -f1); C=0123456789abcdef0123456789abcdef01234567
# omission: declare only a, mutate b -> 0 (documented bound)
printf x >>"$B/r/src/b"; python3 -B tools/souji-evidence-cache.py --root "$B/r" --record "{\"name\":\"o\",\"matched\":true,\"measured_commit\":\"$C\",\"dependencies\":{\"src/a\":\"$A\"}}"; echo "omission=$?"
# laundering: absent measured_commit -> 2 measured_commit-invalid
python3 -B tools/souji-evidence-cache.py --root "$B/r" --record "{\"name\":\"l\",\"matched\":true,\"dependencies\":{\"src/a\":\"$A\"}}"; echo "no-commit=$?"
# inconsistent exit fields -> currently 0 (optional teeth T1)
python3 -B tools/souji-evidence-cache.py --root "$B/r" --record "{\"name\":\"f\",\"matched\":true,\"exit_code\":1,\"expected_exit\":0,\"measured_commit\":\"$C\",\"dependencies\":{\"src/a\":\"$A\"}}"; echo "flip=$?"
# protected record path (synthetic) -> currently read (B2); after fix expect 2
printf '{"name":"synthetic"}' >"$B/p/.ssh/rec.json"; python3 -B tools/souji-evidence-cache.py --root "$B/r" --record "$B/p/.ssh/rec.json"; echo "record-protected=$?"
rm -rf -- "$B"
```
