# round-13 — final checks for L1 (verify suite draft)

Seat: SoujiR13.VerifySuiteDraft (executor, leaf). Owns only this file and its report.
No test, build, lint, formatter or tool selftest was executed by this seat; every command below is
for L1 to run after integration. Certification remains OFF. This seat is NOT an independent
non-author verifier.

Lane root `R` is always the absolute `/home/vgpnk/Projects/shokunin/souji-shokunin`. Baseline read:
`git -C "$R" rev-parse HEAD` → `31984f473ce4bdab61a99b16cca194b28108cb81` (2026-10-20).

Artifacts read while drafting. The hashes are the bytes these line references describe; if a hash
differs at run time, re-read the region and re-derive the expected literal before trusting a check.

| artifact | sha256 at drafting | lines | state |
|---|---|---|---|
| `tools/souji-quarantine.sh` (HEAD `31984f4`) | `141c0fdc4eaf9d0a3d628b381cc5386f6d4be71565ddfb98aa10f6eb3c9573c9` | 1569 | baseline for red-before; HEAD blob `201c3c46…` |
| `tools/souji-quarantine.sh` (working) | `e7e1fae2d8ae6fae3c285519654b770126d7f388ef75996d43b0a1a2f57fbeb5` | 1683 | C2 fix landed in the working tree |
| `tools/souji-cert-evidence.py` | `9a2ed8aa438d5f00878bf157f1e143d9b24305e4f4d681d224bb13556b96db5b` | 1525 | C1 gate landed; frozen fixture present |
| `tests/fixtures/r13-cert-evidence.py` | `3a3535da8b46ccc177b459609b6dfcca4e46362d1fe0c56dd727ecbe70891b7c` | 196 | external CLI harness; `fixture: 5/5 checks passed` |
| `tools/souji-repo-structure.sh` | `80025137b20d5a6143db0120057552bd239fb60de1a504ede69896baade5aec2` | 312 | C3 probe landed |
| `tests/fixtures/r13-repo-structure.sh` | `b6bf52056d037b2251632b409be3d31852588480c392ddc50ca8f8dbf101179f` | 659 | C3 fixture landed |
| `tests/fixtures/r13-cert-frozen/` | `expected.json` 743 B, 7 files pinned | — | landed; `--selftest` can run |
| `tests/fixtures/r13-quarantine-bounds.sh` | `e8e7e9a13b2c9f76798ff4f5f0978b5df2abfd7a183d2b0b554bd32d38f08035` | 279 | C2 red/green fixture landed |

## Axes

- **calibration** — every check either fails on baseline bytes (red-before) or asserts a literal
  finding id/exit code read from the landed code, never a prose claim.
- **operability** — one bounded `env` preamble, fixed timeouts, `/var/tmp` scratch only, no `cd`,
  no network, no credentials, no live mutation.
- **coverage** — the four installed tools, the two new tools, the two new fixtures, the r12 gate,
  the SOURCES census and the live-fleet guard each have an explicit check; omissions are named.

## 1. Inventory — installed tool selftest modes and isolated controls

All four installed shell tools are `--selftest`-only entry points; none takes a target. They refuse
nesting, build fixtures under `mktemp`, and remove them on `EXIT`. The new Python gate and the size
probe are separate contracts.

| tool | selftest entry | exit map | final line (literal form) | fixture base and cleanup | nesting guard |
|---|---|---|---|---|---|
| `tools/souji-verify.sh` | `bash tools/souji-verify.sh --selftest` | 0 pass / 1 fail (usage 2) | `selftest: N checks, M failed` (`:1281`) | `mktemp -d "${TMPDIR:-/tmp}/souji-verify-selftest.XXXXXX"` `:1105`, trap `:1229` | `SOUJI_SELFTEST_ACTIVE=1` → refuse `:1224-1227` |
| `tools/souji-vault-verify.sh` | `bash tools/souji-vault-verify.sh --selftest` | 0 / 1 | `selftest: N checks, M failed` (`:1587`) | mktemp `:1308`, trap `:1447`; each child run `timeout 120` `:1221` | `SOUJI_SELFTEST_ACTIVE=1` → refuse `:1442-1445` |
| `tools/souji-quarantine.sh` | `bash tools/souji-quarantine.sh --selftest` | 0 / 1 | `selftest: N checks, M failed` (`:1627`) | `ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-quarantine-selftest.XXXXXX")` `:1361`, trap `:1425`; G1 `:1441-1448`; H2 base assertion `:1600`; H3 live sentinels `:1607-1613` | `SOUJI_Q_SELFTEST_ACTIVE=1` → refuse `:1420` |
| `tools/souji-census.sh` | `bash tools/souji-census.sh --selftest` | 0 / 1 | `selftest: N checks, M failed` (`:790`) | `mktemp -d "${TMPDIR:-/tmp}/souji-census-selftest.XXXXXX"` `:516`, trap `:517` | `SOUJI_CENSUS_SELFTEST_ACTIVE=1` → refuse `:512-515` |
| `tests/fixtures/r12-maintenance-guard.sh` | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` | 0 pass / 1 fail / 2 could-not-evaluate (unknown arg 2) | `selftest=PASS ids=6/6` (`:229`) | hard-coded `mktemp -d /var/tmp/souji-r12-maintenance.XXXXXX` `:68`, trap `:71`; TMPDIR deliberately ignored | `SELFTEST_EXPECTED_IDS` `:130` |
| `tools/souji-cert-evidence.py` | `python3 tools/souji-cert-evidence.py --selftest` | 0 pass / 1 assertion fail / 2 fixture unavailable or could-not-evaluate | `selftest: N/N passed` (`:1478`) | `tempfile.mkdtemp(prefix="souji-r13-cert-selftest.", dir="/var/tmp")` `:1155`; child env pins `TMPDIR=/var/tmp`, `PYTHONDONTWRITEBYTECODE=1` (`_selftest_env` `:989`); `rmtree` in `finally` | argparse: `--selftest` accepts no other args (`:1494-1496`) |
| `tools/souji-repo-structure.sh` | probe only, no selftest | 0 ok / 2 usage-or-not-a-repo / 3 git lacks `--format=lines` / 4 structure run failed | `probe.status=ok` + 28 structure keys | `mktemp -d /var/tmp/souji-repo-structure.XXXXXX` `:263`, EXIT trap `:164`; captured stderr ≤20 lines | n/a |
| `tests/fixtures/r13-repo-structure.sh` | `bash tests/fixtures/r13-repo-structure.sh --selftest [--probe PATH]` | 0 pass / 1 fail / 2 setup error | `selftest=PASS ids=4/4` baseline mode, `ids=5/5` with `--probe` | `mktemp -d /var/tmp/souji-r13-repo-structure.XXXXXX` `:159`, trap `:162`; `env -i` allowlist; `HOME` under WORK | n/a |
| `tests/fixtures/r13-quarantine-bounds.sh` | `bash tests/fixtures/r13-quarantine-bounds.sh [--tool PATH] [--verify PATH] [--case ID ...]` | 0 all PASS / 1 any FAIL or HANG / 2 usage or environment | `CASE<TAB><id><TAB>PASS|FAIL|HANG<TAB><detail>`, ids `R13Q8-01..05`; then `SUMMARY<TAB>total=N<TAB>failed=M` | `mktemp -d /var/tmp/r13-qbounds.XXXXXX` `:84`, trap `:86`; always `SOUJI_QUARANTINE_ALLOW_LIVE=1` for disposable repos; pins `SOUJI_VERIFY_BIN` | n/a |

Case counts that must not silently shrink (re-derive if the hash differs): gate `--selftest` has
31 `case(...)` + 1 inline `root-not-directory` + 4 `frozen_case(...)` = **36 cases** at `9a2ed8aa`;
the size fixture pins **4** ids baseline / **5** with `--probe`; the bounds fixture pins **5** ids;
the r12 gate pins **6** ids. CertProtocol's static derivation of the older suites (for reference, not
a substitute for the run): verify 40 checks (floor 38 with a locale SKIP), vault 51 (49), census 36
(36), quarantine 77 at baseline (75). The C2-preflight edits may change quarantine's N; record the
printed N and require 0 failed plus the G1/H2/H3 lines.

### 1.1 Whole-tool selftest TMPDIR override (exact mechanism)

`tools/souji-verify.sh:490`, `tools/souji-vault-verify.sh:680` and `tools/souji-quarantine.sh:672`
each execute, at file load and therefore for **every** invocation (not just `--selftest`):

```bash
export TMPDIR="${TMPDIR:-/var/tmp}"
```

This is the appended S18 hardening block running at top level. Consequences:

1. The selftest fixture lines still read `${TMPDIR:-/tmp}` (`verify:1105`, `vault:1308`,
   `quarantine:1360`), but the exported value wins, so with `TMPDIR` unset the fixtures land in
   `/var/tmp` and the tools' own base assertions (`verify` H5, `vault` H3, `quarantine` H2) pass.
2. The override **defers to an inherited value**: if the caller exports `TMPDIR=/tmp` (or a
   short-quota dir), fixtures go there and Q4 is violated while every selftest still reports 0
   failed. The suite must not rely on the override; it pins `TMPDIR=/var/tmp` itself.
3. `tools/souji-census.sh` has **no** override: `:418` (`--compare` temp file) and `:516`
   (selftest base) are `${TMPDIR:-/tmp}`, so an unset `TMPDIR` means `/tmp`. This is a real
   calibration gap in an installed tool; pinning `TMPDIR=/var/tmp` is mandatory for census.
4. The gate ignores `TMPDIR` for its base (`dir="/var/tmp"` hard-coded at `:1155`) and pins its
   child env to `/var/tmp`; `PYTHONDONTWRITEBYTECODE=1` prevents `__pycache__` writes beside the
   tool. The size and bounds fixtures hard-code `/var/tmp` and do not consult `TMPDIR`.

### 1.2 Live-fleet guard (quarantine only) and what it means for checks

Quarantine derives its guard root from its own location, not from an argument:

```
SCRIPT_DIR=<dir of the running tool>; REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd -P)   # :147-149
LIVE_FLEET_ROOT=$(dirname -- "$REPO_ROOT")                                          # :149
```

For the installed tool this is the real fleet root `/home/vgpnk/Projects/shokunin`. Any **non**
dry-run invocation whose `<repo>` equals or lies under that root is refused with `exit 4` and
`GUARD refusal live-fleet-mutation-forbidden …` unless `SOUJI_QUARANTINE_ALLOW_LIVE=1` is set
(`:603-614`). `--dry-run` is always allowed and emits `live-fleet-dry-run` only (`:616-621`).

Three consequences the checks depend on:

- **The guard is location-derived.** A baseline copy placed at `/var/tmp/<x>/souji-quarantine.sh`
  computes `LIVE_FLEET_ROOT=/var/tmp`, so any `/var/tmp` fixture repo would be refused with exit 4.
  The bounds fixture sets `SOUJI_QUARANTINE_ALLOW_LIVE=1` for its disposable `mktemp` repos and
  passes `--hold 0`, so the red/green comparison isolates the bounds behavior. The fixture must
  never receive a live path; FC-1 checks that statically.
- **The guard is not a hang guard.** It runs after argument/engine checks and only for mutation.
  `--dry-run` is not a baseline safety net either: the stage-1 pin digest runs before the dry-run
  branch, and on baseline a non-regular target exits silently under `set -e`.
- **The selftest owns the live-guard proof.** G1 (`:1440-1447`) invokes the real tool against the
  real lane root, expects exit 4 + the token, and separately asserts `LOG.md` sha, porcelain count
  and `.ufo-quarantine` presence are unchanged (`:1600-1612`). FC-7 repeats those sentinels
  externally around the whole suite.

## 2. Suite preamble (run once, in one shell; every path absolute)

```bash
set -u
R=/home/vgpnk/Projects/shokunin/souji-shokunin
BASE=31984f473ce4bdab61a99b16cca194b28108cb81
SCRATCH=$(mktemp -d /var/tmp/r13-final.XXXXXX) || exit 2
cleanup() { rm -rf -- "$SCRATCH"; }
trap cleanup EXIT

# Isolation pins (inherited by every child).
export TMPDIR=/var/tmp
export LC_ALL=C
export GIT_OPTIONAL_LOCKS=0
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_NOSYSTEM=1
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE GIT_OBJECT_DIRECTORY \
      GIT_ALTERNATE_OBJECT_DIRECTORIES SOUJI_QUARANTINE_ALLOW_LIVE
mkdir -p "$SCRATCH/home"
export HOME="$SCRATCH/home"

# Deterministic executables: rg 15.2.0, git 2.55.0, shellcheck 0.11.0, python 3.14.7 are in /usr/bin.
export PATH=/usr/local/bin:/usr/bin:/bin

# Sentinels: the suite mutates nothing in the lane and nothing in /tmp.
BEFORE_HEAD=$(git -C "$R" rev-parse HEAD)
BEFORE_PORCELAIN=$(git -C "$R" status --porcelain | wc -l)
BEFORE_LOG=$(sha256sum "$R/LOG.md" | cut -d' ' -f1)
BEFORE_Q=absent; [ -e "$R/.ufo-quarantine" ] && BEFORE_Q=present
BEFORE_TMP=$(find /tmp -maxdepth 1 -name 'souji-*' -printf '.' | wc -c)
```

`HOME` is a temp dir so `tools/souji-vault-verify.sh` cannot discover an operator
`~/.local/bin/obsidian` shim; its selftest pins `SOUJI_CLI_BIN` fixtures. `PATH` excludes
`~/.local/bin` wrappers (the same `rg` 15.2.0 exists at `/usr/bin/rg`).

Postamble after all checks:

```bash
git -C "$R" rev-parse HEAD | grep -qx "$BEFORE_HEAD"            # no commit during the gates
test "$(git -C "$R" status --porcelain | wc -l)" = "$BEFORE_PORCELAIN"
test "$(sha256sum "$R/LOG.md" | cut -d' ' -f1)" = "$BEFORE_LOG"
test "$BEFORE_Q" = absent && test ! -e "$R/.ufo-quarantine"
test "$(find /tmp -maxdepth 1 -name 'souji-*' -printf '.' | wc -c)" = "$BEFORE_TMP"
```

Failure of any sentinel is a suite failure regardless of individual case verdicts.

## 3. Checks

### FC-1 (red-before) — bounds fixture fails on baseline bytes extracted to `/var/tmp`

Premise, measured statically on HEAD bytes (read-only): the baseline has **no** `timeout` token
anywhere (`grep -c timeout` → 0), **no** special-file preflight (`grep -cE '\[ -(p|S|c|b) '` → 0),
duplicate digest helpers (`file_sha` at `:184` and `:722`, `dir_digest` at `:186` and `:727`; the
later definitions win), unbounded engine/staging calls (`bash "$VERIFY_BIN"` `:215`, `git … mv`
`:529`, `mv --` `:536`), and a stage-1 pin digest before the dry-run branch (`:498`). On a FIFO the
effective S18 `file_sha` (`[ -f ]` guard at `:723`) makes `content_digest` return 1, so under
`set -e` the baseline exits silently rc 1 with no `RESULT`/`SUMMARY`; it does not hang. The delayed
`mv`/`sha256sum` cases are the timeout reds: the fixture's outer bound kills the baseline at 20 s
and the case records the missing bound (`rc=124` plus the missing `mv-timeout`/`digest-timeout`
token), not a PASS.

```bash
RED="$SCRATCH/red"; mkdir -p "$RED"
git -C "$R" show "$BASE:tools/souji-quarantine.sh" > "$RED/souji-quarantine.sh"
chmod 700 "$RED/souji-quarantine.sh"
test "$(sha256sum "$RED/souji-quarantine.sh" | cut -d' ' -f1)" \
     = 141c0fdc4eaf9d0a3d628b381cc5386f6d4be71565ddfb98aa10f6eb3c9573c9
test "$(git -C "$R" show "$BASE:tools/souji-quarantine.sh" | grep -c timeout)" = 0

# Fixture preconditions (read the landed fixture; do not assume).
test -f "$R/tests/fixtures/r13-quarantine-bounds.sh"
grep -q 'mktemp -d /var/tmp/' "$R/tests/fixtures/r13-quarantine-bounds.sh"
! grep -qE '/home/vgpnk|Projects/shokunin' "$R/tests/fixtures/r13-quarantine-bounds.sh"

# RED: expected exit 1; 01 PASS (honest control), 02-05 non-PASS with the baseline cause.
timeout --kill-after=10 180 bash "$R/tests/fixtures/r13-quarantine-bounds.sh" \
  --tool "$RED/souji-quarantine.sh" --verify "$R/tools/souji-verify.sh" \
  >"$SCRATCH/red.out" 2>&1; red_rc=$?
test "$red_rc" = 1
grep -q $'^TOOL\t'"$RED/souji-quarantine.sh"$'\tsha256=141c0fdc' "$SCRATCH/red.out"
grep -q $'^CASE\tR13Q8-01\tPASS\t' "$SCRATCH/red.out"
grep -qE $'^CASE\tR13Q8-02\tFAIL\t' "$SCRATCH/red.out"
grep -qE $'^CASE\tR13Q8-03\tFAIL\t' "$SCRATCH/red.out"
grep -qE $'^CASE\tR13Q8-0[45]\tHANG\trc=1(24|37)' "$SCRATCH/red.out"
grep -q $'^SUMMARY\ttotal=5\tfailed=4\thung=2' "$SCRATCH/red.out"
! grep -q 'live-fleet-mutation-forbidden' "$SCRATCH/red.out"   # not a guard refusal

# GREEN: expected exit 0, 5/5 PASS, failed=0.
timeout --kill-after=10 180 bash "$R/tests/fixtures/r13-quarantine-bounds.sh" \
  --tool "$R/tools/souji-quarantine.sh" --verify "$R/tools/souji-verify.sh" \
  >"$SCRATCH/green.out" 2>&1; green_rc=$?
test "$green_rc" = 0
test "$(grep -cE $'^CASE\tR13Q8-0[1-5]\tPASS\t' "$SCRATCH/green.out")" = 5
grep -q $'^SUMMARY\ttotal=5\tfailed=0\thung=0' "$SCRATCH/green.out"
```

Reading the red: `R13Q8-01` passing on baseline is expected (the honest path already worked);
`02/03` are silent-exit reds (baseline refuses nothing and names nothing; the patched tool must
emit `special-file-refused` / `special-descendant`, exit 3, and leave no `.ufo-quarantine`);
`04/05` are timeout reds (`mv`/`sha256sum` shim sleeps 30, fixture outer bound 20 s) and are
reported `HANG` with `rc=124` in the detail. The fixture increments both `failed` and `hung` for a
HANG, so the red summary is `total=5 failed=4 hung=2`. A red that instead reports
`live-fleet-mutation-forbidden` failed for the wrong reason.

The fixture's shims rewrite the tool's literal `timeout --kill-after=N <secs> <cmd>` to 2 s/1 s
(option order is `--kill-after` before `DURATION`; GNU coreutils 9.11 rejects an option after the
duration with 127). Baseline never calls `timeout`, so only the fixture's 20 s bound stops 04/05.
If the fixture's CLI (`--tool`/`--verify`) is absent, record FC-1 as NOT-RUN (C2 unproven); never
copy baseline bytes over the lane tool to fake it.

Supplemental static check on the fixed tool (Q8's behavioral intent; see limitation 2):

```bash
grep -nE 'timeout --kill-after=[0-9]+ +[0-9]+[smh]? .*(mv|sha256sum)' "$R/tools/souji-quarantine.sh"
# expect matches at the file digest (:712-720), dir digest (:722-731), staging (:497/:499) and
# rm (:506); a zero count fails the Q8 shape even if the fixture passes.
```

### FC-2 — new evidence gate selftest and frozen CLI (C1)

Precondition (present; the tool exits 2 `selftest-unavailable` without it):

```bash
test -f "$R/tests/fixtures/r13-cert-frozen/expected.json"
```

Selftest:

```bash
timeout 180 python3 "$R/tools/souji-cert-evidence.py" --selftest >"$SCRATCH/gate.out" 2>&1; gate_rc=$?
test "$gate_rc" = 0
grep -qE '^selftest: 36/36 passed$' "$SCRATCH/gate.out"   # N at 9a2ed8aa: 31 case + 1 root + 4 frozen
for id in digest-mismatch duplicate-author duplicate-fragment shared-artifact shared-evidence \
          hardlinked-artifact missing-class evidence-digest-mismatch missing-evidence \
          missing-artifact false-pass false-fail honest-fail path-symlink parent-symlink \
          candidate-artifact protected-path protected-env-local control-char-path evidence-fifo \
          manifest-empty; do
  grep -qE "^case $id: ok" "$SCRATCH/gate.out" || { echo "gate case not ok: $id"; false; }
done
```

Expected: exit 0 and every named case `ok`. Exit 2 with `finding selftest-unavailable` is a FAIL of
the deliverable, not a skip; exit 1 is a failed assertion. The 36 cases include the four required
rejects — mismatched installed digest (`artifact-digest-mismatch`), shared ownership
(`author-duplicate`, `fragment-shared`, `path-hardlink`), absent evidence (`evidence-missing`,
`fragment-missing`), false success (`verdict-false-pass`) — plus the review-driven additions
(`candidate-artifact` refuses a `cand-*` path, `missing-class`, `evidence-digest-mismatch`,
`control-char-path`, `protected-path`, `parent-symlink`). Re-derive N from the file if it changed:

```bash
grep -cE '^        case\("' "$R/tools/souji-cert-evidence.py"
grep -cE '^        frozen_case\("' "$R/tools/souji-cert-evidence.py"
grep -c '_record(results, "root-not-directory"' "$R/tools/souji-cert-evidence.py"
```

External black-box harness (CLI-facing, five checks; does not certify):

```bash
timeout 300 python3 "$R/tests/fixtures/r13-cert-evidence.py" >"$SCRATCH/gate-ext.out" 2>&1; ext_rc=$?
test "$ext_rc" = 0
grep -qE '^fixture: 5/5 checks passed$' "$SCRATCH/gate-ext.out"
for name in selftest external-clean external-digest-mismatch frozen-clean frozen-tampered; do
  grep -qE "^ok $name$" "$SCRATCH/gate-ext.out"
done
```

Exit 2 means the tool or frozen snapshot is missing; exit 1 is an assertion failure on the CLI
contract, distinct from the in-tool selftest.

Frozen CLI (pins every snapshot input before evaluating; mismatch is could-not-evaluate):

```bash
timeout 60 python3 "$R/tools/souji-cert-evidence.py" --frozen "$R/tests/fixtures/r13-cert-frozen" \
  >"$SCRATCH/frozen.out" 2>&1; fro_rc=$?
test "$fro_rc" = 0
head -1 "$SCRATCH/frozen.out" | grep -qx 'souji-cert-evidence: clean'
grep -qE '^summary fragments=2 assessed=2 pass=2 fail=0 findings=0 frozen_files=7$' "$SCRATCH/frozen.out"

cp -a "$R/tests/fixtures/r13-cert-frozen" "$SCRATCH/frozen-tamper"
printf 'tampered\n' >> "$SCRATCH/frozen-tamper/evidence/alpha.txt"
timeout 60 python3 "$R/tools/souji-cert-evidence.py" --frozen "$SCRATCH/frozen-tamper" \
  >"$SCRATCH/tamper.out" 2>&1; tam_rc=$?
test "$tam_rc" = 2
grep -q '^finding snapshot_tampered:' "$SCRATCH/tamper.out"
```

Real-bytes run (only when the round's manifest exists; never fabricate it):

```bash
MAN="$R/census/round-13/cert-manifest.json"
if test -f "$MAN"; then
  timeout 120 python3 "$R/tools/souji-cert-evidence.py" --root "$R" --manifest "$MAN" \
    >"$SCRATCH/cert.out" 2>&1; echo "gate_real_rc=$?"
  grep -qE '^summary fragments=4 assessed=4 pass=4 fail=0 findings=0' "$SCRATCH/cert.out"
  # independent digest re-derivation (no relay text trusted):
  for t in souji-verify.sh souji-vault-verify.sh souji-quarantine.sh souji-census.sh; do
    printf '%s %s\n' "$(sha256sum "$R/tools/$t" | cut -d' ' -f1)" "tools/$t"
  done >"$SCRATCH/installed.txt"
  python3 - "$R" "$MAN" "$SCRATCH/installed.txt" <<'PY'
import json,os,sys
root,man,inst=sys.argv[1:]
installed=dict(reversed(l.split()) for l in open(inst))
m=json.load(open(man))
frags=[json.load(open(os.path.join(root,f))) for f in m["fragments"]]
authors=[f["author"].strip().casefold() for f in frags]
assert len(set(authors))==len(authors), "shared author"
assert all(os.path.isfile(os.path.join(root,f["evidence"])) for f in frags), "missing evidence"
for f in frags:
    assert installed[f["artifact"]]==f["sha256"], ("digest mismatch",f["artifact"])
print("cert-manifest independent checks: ok")
PY
else
  echo "FC-2b NOT-RUN: no census/round-13/cert-manifest.json; do not report C1 as installed-byte certified"
fi
```

`--root "$R"` reads the lane's installed bytes through relative paths; the manifest and fragments
must therefore live under the lane root and be committed. An absent manifest is NOT-RUN, never
green. The gate's own limits (docstring `:139-154`) still apply: a co-conspiring author can
self-report a matching digest, the recorded command is never executed, hardlinked installs are
refused rather than followed, and a clean result is evidence consistency — not safety, not
independent authorship. CertProtocol's expected `frozen_files=13` refers to a future round
certification snapshot, not this 7-file test fixture; do not substitute one for the other.

### FC-3 — size probe selftest (C3)

```bash
timeout 180 bash "$R/tests/fixtures/r13-repo-structure.sh" --selftest \
  --probe "$R/tools/souji-repo-structure.sh" >"$SCRATCH/size.out" 2>&1; size_rc=$?
test "$size_rc" = 0
grep -qE '^selftest=PASS ids=5/5$' "$SCRATCH/size.out"
timeout 30 "$R/tools/souji-repo-structure.sh" --help >/dev/null 2>&1   # usage exits 0
```

Expected with `--probe`: exit 0 and `selftest=PASS ids=5/5`. Baseline mode (`--selftest` without
`--probe`) pins 4 ids (`4/4`): `manifest-control`, `write-free`, `object-metrics`, `bogus-repo`.
`--probe` adds `promisor-refusal`: config-marked promisor and partialClone repos must exit 2 with
`probe.error=promisor-remote-unsupported` / `partial-clone-unsupported`, emit no structure key, and
leave the fixture manifest unchanged; the baseline never runs the raw command there. The write-free
case's detector control first proves the manifest sees an appended byte (content) and a `touch`
(mtime-only), then measures one `git repo structure --format=lines` run with before/after manifests
equal. Exit 3 from the probe means the installed git lacks `repo structure --format=lines` (host git
2.55.0 has it) — a capability finding, not a pass.

Stated bound: one normal non-bare, non-linked `/var/tmp` repo; names+bytes+type/mode/size/mtime; no
atime/ctime; no syscall trace; no link/bare/worktree/corrupt/alternates coverage. C3 must not be
widened past that, and a size census authorizes no deletion.

### FC-4 — ShellCheck warning (Q9)

```bash
shellcheck --version | sed -n '2p'      # expect: version: 0.11.0
shellcheck -S warning \
  "$R/tools/souji-quarantine.sh" \
  "$R/tests/fixtures/r13-quarantine-bounds.sh" \
  "$R/tools/souji-repo-structure.sh" \
  "$R/tests/fixtures/r13-repo-structure.sh" \
  >"$SCRATCH/sc.out" 2>&1; sc_rc=$?
test "$sc_rc" = 0
test ! -s "$SCRATCH/sc.out"
```

`-S warning` (not `-S error`) is the gate; SC2114/SC2115 are warnings and must be fixed, not
downgraded. For the modified installed tool, distinguish pre-existing warnings against HEAD:

```bash
git -C "$R" show "$BASE:tools/souji-quarantine.sh" >"$SCRATCH/base-quarantine.sh"
shellcheck -S warning "$SCRATCH/base-quarantine.sh" >"$SCRATCH/sc-base.out" 2>&1; echo "base_rc=$?"
```

If `base_rc` is 0, the post file must be clean. If `base_rc` is nonzero, the pass condition is: the
post warning set has no line absent from the baseline set (compare `-f gcc` outputs after stripping
the path); record both counts. Never report a nonzero baseline as a pass for new code. Python is not
shellchecked; the gate selftest parses and exercises it.

### FC-5 — source census

Run from the lane root without `cd`:

```bash
env -C "$R" TMPDIR=/var/tmp bash census/round-12/sources-census.sh >"$SCRATCH/census.out" 2>&1; cen_rc=$?
test "$cen_rc" = 0
```

Expected (both observed 2026-10-20; the stored r12 output is not the baseline):

| line | HEAD `31984f4` | post-C3 target | notes |
|---|---|---|---|
| rows | 33 | 34 if S034 is admitted, else 33 | `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` |
| malformed | 0 | 0 | `awk … NF!=13` |
| tier | `A=29 B=3 C=1` | `A=30 B=3 C=1` with S034 | A can only grow by a tier-A row |
| status | `mined=16 queued=15 rejected=2` | `mined=18 queued=13 rejected=2` (S005/S006 mined); `queued=14` if S034 queued | working tree already shows 18/13 |
| duplicate ids | empty | empty | `uniq -d` |
| enum/tier inflation | empty | empty | tier A+community forbidden |
| mined used-by paths | empty | empty | script line 16, run from lane root |

Do **not** copy `census/round-12/sources-census.txt` or `after.txt`: both record
`mined=18 queued=13` at `d7266c5`, and `2a363a0` moved S024/S025 back to `queued`, so HEAD is
16/15/2. The counts above were measured with the script's own commands.

Tracked-existence gate (catches an untracked F2 entry satisfying `[ -e ]`):

```bash
grep -c PENDING "$R/corpus/SOURCES.md"      # must be 0
git -C "$R" ls-files --error-unmatch -- corpus/knowledge/git-repo-structure-readonly.md
grep -oE 'corpus/knowledge/[A-Za-z0-9._/-]+' "$R/corpus/SOURCES.md" | sort -u | while read -r p; do
  git -C "$R" ls-files --error-unmatch -- "$p" >/dev/null 2>&1 || echo "not-tracked: $p"
done
```

Expected: the `not-tracked:` list empty after the integration commit. If S034 lands, its row must
have zero PENDING cells and a used-by path that exists (or `—` for queued), and the census must show
the matching delta.

### FC-6 — installed tool regression suite

Each command is bounded; any nonzero exit or `M>0` fails the suite.

```bash
timeout 300 bash "$R/tools/souji-verify.sh" --selftest >"$SCRATCH/verify.out" 2>&1; echo "verify_rc=$?"
timeout 300 bash "$R/tools/souji-vault-verify.sh" --selftest >"$SCRATCH/vault.out" 2>&1; echo "vault_rc=$?"
timeout 600 bash "$R/tools/souji-quarantine.sh" --selftest >"$SCRATCH/quarantine.out" 2>&1; echo "quarantine_rc=$?"
timeout 120 bash "$R/tools/souji-census.sh" --selftest >"$SCRATCH/census-st.out" 2>&1; echo "census_rc=$?"
timeout 180 bash "$R/tests/fixtures/r12-maintenance-guard.sh" --selftest >"$SCRATCH/maint.out" 2>&1; echo "maint_rc=$?"
```

Required:

- each rc = 0;
- each of verify/vault/quarantine/census prints `selftest: N checks, 0 failed` (final line) and its
  fixture-base PASS line names a `/var/tmp` path (`verify` H5, `vault` H3, `census` base line,
  `quarantine` H2). A base under `/tmp` fails Q4 even when all checks pass;
- the printed N is not below CertProtocol's static floor (verify 38, vault 49, census 36,
  quarantine 75); record N in the round evidence. A lower N means a case disappeared;
- quarantine also prints `PASS G1 guard rc=4`, `PASS G1 guard token`, `PASS G1 live lane untouched`,
  `PASS H3 live lane porcelain unchanged`, `PASS H3 live LOG.md unchanged`, `PASS H3 no live
  .ufo-quarantine`;
- maintenance guard prints `selftest=PASS ids=6/6`;
- nested refusal: `env SOUJI_Q_SELFTEST_ACTIVE=1 bash tools/souji-quarantine.sh --selftest` → exit 1
  with `refusing nested --selftest` (same pattern for the other three env markers).

### FC-7 — live-fleet guard proof (no mutation)

```bash
QSHA_BEFORE=$(sha256sum "$R/LOG.md" | cut -d' ' -f1)
timeout 60 env -u SOUJI_QUARANTINE_ALLOW_LIVE bash "$R/tools/souji-quarantine.sh" \
  --hold 0 "$R" no-such-live-target.txt >"$SCRATCH/guard.out" 2>&1; guard_rc=$?
test "$guard_rc" = 4
grep -q 'live-fleet-mutation-forbidden' "$SCRATCH/guard.out"
test "$(sha256sum "$R/LOG.md" | cut -d' ' -f1)" = "$QSHA_BEFORE"
test ! -e "$R/.ufo-quarantine"
```

This is G1's case repeated externally against the real lane path. Do not set
`SOUJI_QUARANTINE_ALLOW_LIVE=1` for this check. Even if the guard failed, the target name is
nonexistent, so stage 1 cannot authorize a move; the sentinels prove nothing was mutated.

## 4. Order, bounds, abort rules

1. Preamble + FC-7 (guard) — fail fast if the lane is unsafe.
2. FC-1 red → green (C2 calibration); abort the C2 claim if red is not observed.
3. FC-2 (C1), FC-3 (C3), FC-5 (census), FC-4 (ShellCheck).
4. FC-6 full regression last (most CPU/time heavy), then the postamble.
5. Any HANG is a failure. Any exit 2 from a gate is a failure unless the check explicitly expects
   could-not-evaluate. No check may be skipped because a tool "seemed fine"; an absent artifact is
   recorded NOT-RUN with the claim it blocks (C1 manifest, C3 entry tracking).

Total outer bound: ~20 min with the timeouts above; the bounds fixture internally bounds each run
at 20 s (`--kill-after=5`), so its 180 s outer bound is slack, not the gate.

## 5. Limitations and open defects observed while drafting

1. **Bounds fixture verdict vocabulary**: at `e8e7e9a1` `finish_case` emits `HANG` when the outer
   20 s bound kills the tool (`rc=124/137`) and counts it in both `failed` and `hung`; `02/03`
   silent exits are `FAIL` with rc 1/2. An earlier snapshot (`ba97bfaa`) had no HANG code path and
   surfaced the timeout as `FAIL` — the drift rule below is why FC-1 pins `HANG` for the current
   bytes.
2. **QUALITY Q8's literal grep is not satisfiable** with GNU `timeout` option order: the criterion
   `timeout [0-9]+[smh]? .*(mv|sha256sum)` puts the duration before `--kill-after`, which coreutils
   9.11 parses as the command (exit 127, probed by BoundQuarantine). Use FC-1 as the behavioral
   gate and the corrected static regex in FC-1 as the shape check; do not report the literal Q8
   regex as passing when it cannot match.
3. **Census TMPDIR gap**: `tools/souji-census.sh` has no whole-tool override and defaults to
   `/tmp`; the suite pins `TMPDIR=/var/tmp`, but the tool itself remains non-compliant with Q4 when
   invoked bare. Record it as an operability debt, not a passing check.
4. **Baseline silent exits**: the baseline's stage-1 pin runs before the dry-run branch and under
   `set -e`; a FIFO target exits rc 1 and a directory containing one exits rc 2 with no `RESULT`/
   `SUMMARY`. This is the baseline red, not a hang; only the delayed-shim cases hit the outer
   bound. The fixed tool dedupes the digest helpers (single `file_sha` `:712`, `dir_digest` `:722`)
   and refuses special files before any read (`:1191-1222`).
5. **Author identity is unauthenticated** in the gate: distinct `author` strings and distinct
   fragment/evidence paths are checkable; independence is not. A clean result is evidence
   consistency; Q5 blind re-derivation remains separate.
6. **Size probe proof bound**: one normal repo; before/after manifests cover names+bytes and
   type/mode/size/mtime, not atime/ctime, syscall transients, link/bare/worktree/corrupt shapes or
   concurrent writers. The promisor/partialClone refusals are config-detection only (the
   `example.invalid` URL is never contacted). C3 must not be widened beyond this.
7. **Hashes drift as executors finish**: every line reference is tied to the sha256 in the table.
   If a hash changed, re-read the cited region and re-derive the expected literal (case count, ids,
   exit map) before running; never accept an old literal on new bytes.

## Tools installed or upgraded by this seat

None. Versions observed (not installed): ShellCheck 0.11.0, git 2.55.0, Python 3.14.7, ripgrep
15.2.0, GNU coreutils 9.11 (`timeout`, `mktemp` 0.8.0), bash 5.3.15. Kernel 7.2.3-arch1-3.
