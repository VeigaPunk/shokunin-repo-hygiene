# SwarmReviewer36 — C3 capture-tool review (round 28 w1)

## Status
STATUS: PASS — tool+fixture reviewed, selftest passes (cases=6 pass=6 control=TAMPER-REJECTED rc 0), all break attempts refused or bounded-conformant; findings below are non-blocking (1 contract-adjacent note + consistency/info items). No tooling installed (RULES.md consulted; nothing needed).

## Evidence
- `bash -n tools/souji-wave-evidence-capture.sh` and `bash -n tests/fixtures/r28-wave-evidence-capture.sh` → SYNTAX-OK (no error).
- Selftest (isolated): `TMPDIR=/var/tmp/souji-r28-SwarmReviewer36 bash tests/fixtures/r28-wave-evidence-capture.sh` →
  `case-1: PASS (happy path rc=0) … case-6: PASS (empty dir captured rc=0)`; `cases=6 pass=6 control=TAMPER-REJECTED`; `FIXTURE-RC=0`. All six cases + tamper control green; scratch removed by trap (verified: no residue under `$base`).
- Break attempts (all in /var/tmp/souji-r28-SwarmReviewer36 probe lanes, never the real lane):
  - FIFO inside snapshot → rc=3 (refused). Absolute symlink escape → rc=3. Relative `../` escape → rc=3. Dangling symlink → rc=3. Symlink→FIFO → rc=3 (target entry itself refused). Internal symlink (fixture supplementary) → accepted.
  - Traversal in lane argument (`.../lane-5/../..`) → rc=1 (per fixture case 5).
  - Huge dense file: 128 MiB `/dev/urandom` copied+hashed rc=0 in ~1 s, receipt 129 MiB — no size/quota guard exists (finding F1).
  - Tamper control: byte-flip `manifest.sha256` → `--verify` rc=4; append to `summary.tsv` → rc=4. Newline-in-filename round-trips (NUL-safe `mapfile -d ''`/`xargs -0`, `LC_ALL=C sort -z` symmetric gen/verify).
  - Source dir deleted after capture → `--verify` still rc=0 (receipt self-check only; source not consulted).
  - Pre-existing `census/round-N/waves` symlink to foreign dir: `rm -rf` removes only the link; foreign untouched (0 entries); real receipt dir created.
- No `git`/`jj`/network constructs in tool (grep for git/jj/curl/wget/ssh/fetch/commit/clone/eval → only comment text). Writes limited to `$dst` (`rm -rf`/`mkdir -p`/`cp -a`/python3 summary/manifest); source reads only.
- Lane state: `tools/souji-wave-evidence-capture.sh`, `tests/fixtures/r28-wave-evidence-capture.sh`, `.gitignore` untracked (not yet committed); `git check-ignore -v .ufo/waves/round-26/w1/x` → `.gitignore:1:.ufo/waves/` — ignore rule active. `SKILL.md` has no `wave-evidence` registry row yet.

## Findings
1. (MEDIUM — contract) No size/time bound on capture: "bounded, read-only over the source" (prereg C3) is not enforced. `cp -a` (tools/souji-wave-evidence-capture.sh:104-111) and manifest hashing have no quota, per-file cap, or timeout; a huge/growing snapshot is copied unbounded (128 MiB accepted rc=0), and a mid-copy special-file swap could block `cp` indefinitely. Recommend a documented byte cap + `timeout` wrapper with a mapped exit class.
2. (LOW — exit-map consistency) Declared map vs behavior mismatch: header ("Exit codes" tools/…:25-31) assigns "path escape" to rc=3, but lane-argument `..` traversal exits 1 (usage; codified by fixture case 5 expecting 1). Align by moving the lane-segment check to rc=3 or rewording the map. Else 0/1/2/3/4/5 map matches exercise shape (0 clean; 1 failed/usage per class; 2 could-not-evaluate; explicit others).
3. (INFO) `--verify` never consults the source: it certifies receipt self-consistency only (matches docstring); source↔receipt identity is checked only in capture mode, and then as hash-value-set equality (`awk '{print $1}'`), i.e. filename-blind (tautological over a fresh copy; low risk).
4. (INFO) Symlink policy verified: absolute/relative/dangling escapes refused rc=3; internal links accepted; special files refused transitively (any real FIFO/device/socket entry fails the `! -f && ! -d` branch). Claim "refuses symlinks/special files/escaping" holds.

## Attack log
Not an attack item; no counter/predicate/target proposed for change.

## Residual risk / verification gaps
- Source-tamper-after-capture detection requires rerunning capture; `--verify` will be green even if the source tree was altered post-capture (finding 3).
- No `--max-bytes`/timeout coverage in fixture; if a bound is added, the fixture must gain a refusal case.
- SKILL.md registry row for the new tool is not yet present (executor/L1 integration task; gate on registry row + manifest tests at tip per C3 counters).
- Read-only seat: tool/fixture not modified by me; untracked state owned by executor.
