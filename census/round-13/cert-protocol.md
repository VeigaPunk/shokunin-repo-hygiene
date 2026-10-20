# r13 cert protocol — no-relay, installed-byte re-certification

Seat: `SoujiR13.CertProtocol` (executor, leaf). Round 13, wave 1.
Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Baseline HEAD: `31984f4`
(`31984f473ce4bdab61a99b16cca194b28108cb81`).

**Status: proposal only. No suite, gate, fixture, build, lint, formatter, or install was run by this
seat.** Every command below is specified for L1 to execute after integration. Certification remains
**OFF**. This seat is **not** an independent non-author verifier and does not claim to be one.

Facts are cited by path and line at the baseline named above; anything derived by static reading
rather than execution is marked `[derived]`; anything that would need a run to settle is marked
`[to-verify]`.

---

## 1. What this protocol replaces

r11 did not fail because the tests were weak. It failed because the **evidence path** was writable by
everyone and the verdict was attached to whatever bytes happened to be on disk:

- `census/round-11/cert-16.json` was used as a shared relay and overwritten repeatedly
  (`corpus/lessons/round-11.md:14`; `census/round-11/dissent-32.md:49`, "cert-16.json as a shared
  relay is a process defect worth naming precisely").
- A sibling's fix landed mid-run and rewrote `tools/souji-census.sh`; the same seat re-ran
  `cert-16.json` in place (`census/round-11/S08-fragment.md:86-88`, observed new digest
  `462dabd281e417c80266ba4d3ffd2cd8ebca0aa84147e1c45c9832ee638b52ca`).
- One certifier's own harness auto-wrote `cert-16.json` before the relays did
  (`census/round-11/dissent-32.md:62-69`). The write path, not the person, was the defect.
- The selection rule ranked census candidates by selftest count and picked `impl-46` (67 checks),
  which fails the class under test; `cand-census-08` (35 checks) closed it
  (`census/round-11/dissent-32.md:74-80`).

The replacement is structural, not documentary: **one author, one installed artifact, one suite, one
fragment, one digest, one raw output file — and an executable gate that rejects every other shape.**
The gate is `tools/souji-cert-evidence.py` (C1 seat `EvidenceGate`, in flight; untracked at this
baseline). This protocol binds to that gate's documented CLI, not to its transient line numbers.

## 2. Certification unit and definitions

**Installed set (protocol-owned constant for this round; the gate has no allowlist, §7).** These four
paths are the only certifiable artifacts, matching the "four installed tools" named in
`SCORECARD.md:55` and QUALITY Q6:

| tool id | installed path |
|---|---|
| `souji-verify` | `tools/souji-verify.sh` |
| `souji-vault-verify` | `tools/souji-vault-verify.sh` |
| `souji-census` | `tools/souji-census.sh` |
| `souji-quarantine` | `tools/souji-quarantine.sh` |

**Installed bytes** means both of these are byte-identical:

1. the worktree file at the installed path;
2. `git -C <lane> show HEAD:<installed path>` (the committed blob).

If they differ, no fragment may be written; the run is `installed-bytes-unstable`. This matters
because `tests/results/INSTALL.json:4` still pins `7efda63bd7607009f98604356baf2fabeff1e3d8ca2b946be47bf22cd32c6820`
for `tools/souji-verify.sh`, while the HEAD blob hashes to
`9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd`. Any verdict that cites
`INSTALL.json` today certifies bytes that are not installed.

**Candidate paths never certify.** The gate rejects any artifact whose basename starts with `cand-`
(`tools/souji-cert-evidence.py`, finding `artifact-candidate`). A candidate becomes certifiable only
after it is installed at one of the four paths above — bytes first, then measurement.

**A fragment is one author × one tool × one suite.** The manifest for a complete pass lists exactly
four fragments with four distinct `author` values (the gate's `author-duplicate` check enforces the
distinctness; this protocol requires one tool per author so one measurement cannot stand in for
another).

## 3. Baseline anchors (HEAD `31984f4`)

Full sha256 of the committed blob, so a later run can prove which bytes it measured:

| path | git blob oid | sha256 of blob | lines / bytes |
|---|---|---|---|
| `tools/souji-verify.sh` | `c0f3377e8812224529073035960e9f0a141517c6` | `9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd` | 1316 / 50864 |
| `tools/souji-vault-verify.sh` | `f83997a7166aecbbdab642eede833488d29b8afd` | `f9e778ca478c7aa8b33234ee793030df631c1b9fcebc942b1ff41d0008ed9c5b` | 1632 / 65047 |
| `tools/souji-census.sh` | `8f114996ce7658693a326bcad6c1da5690c46033` | `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026` | 827 / 30197 |
| `tools/souji-quarantine.sh` | `201c3c462d59ee882d498543acfb5634a2fff2d7` | `141c0fdc4eaf9d0a3d628b381cc5386f6d4be71565ddfb98aa10f6eb3c9573c9` | 1569 / 63162 |
| `tools/souji-round9-selftest.sh` | `61bae1aeb546fd2957a02a4c21b389cfb3ddff17` | `dd7c636ebe39e70c489516500440a311167b5280d18c3a5e9db1399d2f62e5c2` | 269 / 9775 |

`tools/souji-quarantine.sh` is expected to change under C2 (`BoundQuarantine`); its row above is the
red-before anchor, not a prediction. Re-measure before writing any fragment.

Host facts relevant to suite shape (read-only probes, not suite runs): bash `5.3.15(1)`,
git `2.55.0`, rg `15.1.0`, shellcheck `0.11.0`, python3 `3.14.7`, GNU `timeout` present,
`localedef` present, `/usr/share/i18n/locales/tr_TR` and the UTF-8 charmaps present. The last point
means the shared runner's Turkish-locale block is expected to execute rather than print `SKIP`
(`tools/souji-round9-selftest.sh:162,176`).

## 4. Fragment contract

### 4.1 Required by the gate

The gate's documented fragment schema requires every key:
`author`, `class`, `artifact`, `sha256`, `command`, `exit_code`, `verdict`, `evidence`,
`evidence_sha256`. Extra keys are tolerated. `verdict` is `pass|fail`; `exit_code` is an integer
compared only against zero; `sha256` must equal the artifact digest at gate time; `evidence_sha256`
must equal the evidence file so an overwrite is rejected.

### 4.2 Required by this protocol (extra keys)

| key | value |
|---|---|
| `run_id` | `"<author>/<tool>/<UTC timestamp>"`, also written as evidence line 1 |
| `suite` | `"--selftest"` |
| `checks` | observed summary count (integer, or `null` on a timeout) |
| `failed` | observed failure count (0 for a pass) |
| `expected_checks` | the certifier's pre-run static count for the integrated bytes |
| `count_command` | the exact grep/awk used to derive `expected_checks` (re-runnable by L1) |
| `host_bash`, `host_git`, `host_rg` | version strings observed in the certifier's shell |
| `tmpdir` | `/var/tmp` (must match the invocation) |
| `timeout_s` | the integer passed to `timeout` |
| `started_utc`, `finished_utc` | `date -u +%s` values |

### 4.3 Paths, ownership, and write-once

```
census/round-13/cert/manifest.json
census/round-13/cert/fragments/<author>--<tool>.json
census/round-13/cert/evidence/<author>--<tool>.txt
census/round-13/cert/frozen/            # L1-only snapshot, section 8
```

- `<author>` is the seat's exact roster id; the fragment filename must begin with it.
- Every path is created write-once: shell `set -o noclobber`, Python `open(..., "x")`. A mistaken or
  superseded run gets a **new** `run_id` at a **new** path; no fragment or evidence file is ever
  edited, appended to, or re-run in place. This is the difference between a fragment and a relay.
- Evidence is raw combined stdout+stderr with exactly one prepended line
  `# run_id <run_id>`; its last line must be the suite summary. The prepended line makes an
  overwrite visible even before the digest check.
- The parent/L1 aggregates by **listing** fragment paths in `manifest.json`. It never writes into a
  fragment, never rewrites evidence, and never adds a verdict of its own to a fragment.

## 5. Certifier procedure — one author, one tool

Each author does all four steps itself: computes the installed digest, runs the bounded suite,
captures the raw output, and writes the fragment. A parent, sibling, or aggregator that performs any
of those on the author's behalf turns the fragment back into a relay and voids it — even if every
digest matches.

### 5.1 Preconditions (per certifier)

1. The integration commit exists; `git -C "$ROOT" status --porcelain -- tools/` prints nothing.
2. The four installed blobs still match section 3, except any tool whose binding fragment was
   written after a reviewed change (re-measure, do not reuse).
3. `command -v bash git rg timeout sha256sum python3 localedef` all resolve.
4. The environment does not carry another selftest's guard:
   `SOUJI_SELFTEST_ACTIVE`, `SOUJI_Q_SELFTEST_ACTIVE`, `SOUJI_CENSUS_SELFTEST_ACTIVE` must be unset
   (each tool refuses nested selftests: `souji-verify.sh:1224-1226`,
   `souji-vault-verify.sh:1442-1444`, `souji-census.sh:512-514`,
   `souji-quarantine.sh:1305-1308`).

### 5.2 Bounded invocation (template; run once per tool)

Timeouts are finite and recorded. Sizes are chosen from observed suite work, not from old claims:
`quarantine` runs an internal ≥77-check battery including git plumbing, `vault` includes a 30-second
hung-CLI fixture bounded internally, `verify`/`census` are lighter.

| `TOOL` | `LIMIT` (s) |
|---|---|
| `souji-verify` | 300 |
| `souji-vault-verify` | 300 |
| `souji-census` | 300 |
| `souji-quarantine` | 600 |

```bash
ROOT=/home/vgpnk/Projects/shokunin/souji-shokunin
AUTHOR='<roster-id>'        # distinct per tool; never a shared/parent id
TOOL=souji-verify           # one of the four installed ids
LIMIT=300
EXPECTED=40                 # static count for these bytes; §6 table (re-derive after C2)
RUN_ID="$AUTHOR/$TOOL/$(date -u +%Y%m%dT%H%M%SZ)"
EV="census/round-13/cert/evidence/$AUTHOR--$TOOL.txt"
FR="census/round-13/cert/fragments/$AUTHOR--$TOOL.json"

mkdir -p -- "$ROOT/census/round-13/cert/evidence" "$ROOT/census/round-13/cert/fragments" || exit 3
umask 077
set -o noclobber
[ ! -e "$ROOT/$EV" ] && [ ! -e "$ROOT/$FR" ] || { printf 'cert: write-once path exists\n' >&2; exit 3; }

H=$(mktemp -d /var/tmp/cert-home.XXXXXX) || exit 3
trap 'rm -rf -- "$H"' EXIT
start=$(date -u +%s)
{
  printf '# run_id %s\n' "$RUN_ID"
  env -u SOUJI_SELFTEST_ACTIVE -u SOUJI_Q_SELFTEST_ACTIVE -u SOUJI_CENSUS_SELFTEST_ACTIVE \
      -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u SOUJI_VERIFY_BIN \
      -u SOUJI_LEDGER -u SOUJI_Q_LEDGER \
      TMPDIR=/var/tmp LC_ALL=C HOME="$H" \
      timeout --signal=TERM --kill-after=15 "$LIMIT" \
      bash "$ROOT/tools/$TOOL.sh" --selftest
} >"$ROOT/$EV" 2>&1
rc=$?
end=$(date -u +%s)
```

Notes that are part of the contract:

- The redirection is a single writer. No pipeline, no `tee`, so the recorded bytes are the suite's
  bytes.
- `TMPDIR=/var/tmp` is forced even though each tool defaults to `"${TMPDIR:-/var/tmp}"` except
  `souji-census.sh`, which has no `/var/tmp` default at all (`souji-census.sh:418,516` use
  `"${TMPDIR:-/tmp}"`). See §12.
- `rc=124` (TERM) or `rc=137` (KILL) is a bounded timeout, never a pass. The partial evidence stays
  on disk; the fragment records `verdict: "fail"` and the gate returns `failed` (exit 1), not
  `clean`.

### 5.3 Parse and classify

```bash
tail_line=$(tail -n 1 -- "$ROOT/$EV")
checks=$(printf '%s\n' "$tail_line" | sed -nE 's/^selftest: ([0-9]+) checks, ([0-9]+) failed$/\1/p')
failed=$(printf '%s\n' "$tail_line" | sed -nE 's/^selftest: ([0-9]+) checks, ([0-9]+) failed$/\2/p')
```

- Missing summary (timeout, crash, usage error) → `checks=null`, `verdict=fail`.
- `checks != expected_checks` → `verdict=fail` with the observed values recorded. This is the
  anti-false-success check: a suite that silently skipped cases cannot be declared a pass.
- `failed != 0` → `verdict=fail`.
- `rc != 0` → `verdict=fail`.

### 5.4 Write the fragment (write-once)

```bash
python3 - "$ROOT" "$AUTHOR" "$TOOL" "$RUN_ID" "$rc" "$checks" "$failed" "$EXPECTED" "$LIMIT" "$start" "$end" <<'PY'
import hashlib, json, os, sys
root, author, tool, run_id, rc, checks, failed, expected, limit, start, end = sys.argv[1:12]
art  = "tools/%s.sh" % tool
ev   = "census/round-13/cert/evidence/%s--%s.txt" % (author, tool)
frag = "census/round-13/cert/fragments/%s--%s.json" % (author, tool)
sha  = lambda p: hashlib.sha256(open(os.path.join(root, p), "rb").read()).hexdigest()
checks = None if checks in ("", "null") else int(checks)
failed = None if failed in ("", "null") else int(failed)
ok = int(rc) == 0 and failed == 0 and checks == int(expected)
obj = {
    "author": author,
    "class": "installed-byte-selftest",
    "artifact": art,
    "sha256": sha(art),
    "command": "bash tools/%s.sh --selftest" % tool,
    "exit_code": int(rc),
    "verdict": "pass" if ok else "fail",
    "evidence": ev,
    "evidence_sha256": sha(ev),
    "run_id": run_id,
    "suite": "--selftest",
    "checks": checks,
    "failed": failed,
    "expected_checks": int(expected),
    "count_command": "<paste the static-count command used for expected_checks>",
    "host_bash": "5.3.15(1)-release",
    "host_git": "2.55.0",
    "host_rg": "15.1.0",
    "tmpdir": "/var/tmp",
    "timeout_s": int(limit),
    "started_utc": int(start),
    "finished_utc": int(end),
}
with open(os.path.join(root, frag), "x", encoding="utf-8") as handle:
    json.dump(obj, handle, indent=1, sort_keys=True)
    handle.write("\n")
PY
```

`EXPECTED` is the static count for the integrated bytes (`40` for `souji-verify` at baseline; see
§6), set beside `LIMIT` before the run. The `count_command` is mandatory for L1's spot-check; the
gate cannot verify execution, so the count derivation is where a silent skip is caught.

## 6. Suite inventory and expected outputs — derived from the code

All counts below are `[derived]` by enumerating emission sites and loop multiplicities in the
baseline blobs, not read from any results file. "Summary" means the last line of combined output;
"exit" means the process status.

### 6.1 `tools/souji-verify.sh --selftest`

- Code: `run_selftest` 1223-1284; `st_case` 1026-1055; `st_status` 1062-1071; `st_audit_source`
  1205-1221; fixture builder 1105-1204; R9 hook 1272-1280.
- Inventory: 18 `st_case` (F1-F10, E1-E8, one `PASS <id> <SAFE|NOT-SAFE>(<receipt>)` each);
  3 `st_status` (H2-H4, `PASS <id> exit=2`); H6 json shape; H1 and H5 audits (2); the shared R9
  runner contributes 16 on this host (2 nested-stale + 2 nested-pushed + 1 nested-gitfile +
  2×2 worktree-discovery failures + 1 readonly-index + 2 Turkish-locale + 2×2 ledger revocation).
- Expected: `selftest: 40 checks, 0 failed`, exit 0. Floor when R9 prints its SKIP: 38.

### 6.2 `tools/souji-vault-verify.sh --selftest`

- Code: `run_selftest` 1441-1590; `st_case` 1226-1258; `st_status` 1262-1269;
  `st_audit_source` 1416-1438; fixture builder 1308-1414; R9 hook 1576-1585.
- Inventory: 21 `st_case` (F1-F5, F7-F10, V1-V6, V9, V12, V15, V17, V18, V20); 2 `st_status`
  (H4, H5); 9 explicit checks (V10b, V11b, V13, V14, V16, V19, V21, V22, V23); 3 audits
  (H1 no forbidden git, H2 no GUI-launcher literal, H3 fixtures under mktemp); R9 16.
- Expected: `selftest: 51 checks, 0 failed`, exit 0. Floor with R9 SKIP: 49.

### 6.3 `tools/souji-census.sh --selftest`

- Code: `run_selftest` 511-793; fixture builder 511-601; checks 601-788.
- Inventory: 33 `st_ok` success sites in the range; lines 767-768 are one check inside the
  4-iteration loop at 761-769, so 32 + 4 = 36 checks. No shared R9 runner, no `--json` case.
  Named groups: repeat/header/row-count/skip-rules (6), clean row (4), dirty row (3),
  unpushed/wt flags (5), no-remote (2), secret/forbidden-surface absence (2), mtime shape and
  future-sentinel (2), compare clean/blank/mutation/field deltas (5), four malformed baselines
  (4), unknown flag (1), source audit (2).
- Expected: `selftest: 36 checks, 0 failed`, exit 0. This arithmetic independently reproduces the
  r11 "36/36" number — which is why a matching number is not evidence that the same bytes were run.

### 6.4 `tools/souji-quarantine.sh --selftest`

- Code: `run_selftest` 1304-1514; `st_check` 1219-1221; fixture builder 1246-1302; R9 hook
  1502-1511.
- Inventory: 50 `st_check` sites + 1 `st_ok` (H2) = 51 internal. Labels: G1 (3), D1 (4), D2 (1),
  D3 (3), N1 (3), N2 (1), N3 (2), N4 (2), P1 (7), P2 (3), P3 (4), SKIP1 (1), L1 (2), A1 (5),
  U1-U5 (5), H1 (1), H2 (1), H3 (3). R9 quarantine contributes 28 on this host: 18 base
  (2×2 nested, 1 gitfile, 2×2 git-failure, 1 readonly, 2 locale, 3×2 ledger) +
  3×2 NUL-list cases + 2×2 default-ref cases.
- Expected: `selftest: 79 checks, 0 failed`, exit 0. Floor with R9 SKIP: 77.
- **Structural bound:** 51 internal + at most 28 R9 = 79. The r9/r11 figure "quarantine 91/0"
  (`SCORECARD.md:65`, `census/round-11/S08-fragment.md:50`) cannot describe these bytes; it was
  measured on a different build. C2 will add FIFO/timeout checks, so the post-integration count is
  `79 + added`; `expected_checks` must be re-derived, and this table is the floor, not the target.

### 6.5 Shared runner `tools/souji-round9-selftest.sh <kind> <tool>`

- Code: 1-269. Kind gate at line 6 (`verify|vault|quarantine`, else exit 2). Fixtures are
  `mktemp -d -p /var/tmp` (line 8) and it exports `TMPDIR=/var/tmp` (line 15).
- Output: `PASS R9 <case>` / `FAIL R9 <case>: ...`, one optional
  `SKIP R9 Turkish locale (localedef or locale source unavailable)` (line 176), and a final
  `ROUND9\t<PASS>\t<FAIL>` (line 268). The tools parse only that last line and add a FAIL if it is
  missing (`souji-verify.sh:1272-1279` and the equivalent blocks in the other two).
- `N` is host-dependent by design: the Turkish-locale block contributes 2 checks when `localedef`
  compiles the fixture and 0 when it prints SKIP. This is exactly why a fragment records `checks`
  and `expected_checks` instead of a hard-coded total.

### 6.6 Gate `tools/souji-cert-evidence.py --selftest`

- The in-flight worktree file changed twice during this seat's work (1377 → 1442 → 1509 lines), and
  `selftest()` and the frozen-fixture path move with it. **Do not cite line numbers for this file**;
  certify only the committed blob and re-derive everything below from it.
- Case call sites moved with the file: 31 when first observed (`27 case(...)` + `4 frozen_case(...)`),
  38 at the last observation (`34 + 4`). Expected output shape is `case <name>: ok ...` lines and a
  final `selftest: <N>/<N> passed`, exit 0; `N` must be re-derived from the committed file. **This
  number is deliberately not pinned in this protocol.**
- Dependency: `tests/fixtures/r13-cert-frozen/expected.json` was **absent at observation**, so the
  gate selftest exits 2 with `finding selftest-unavailable: ...` until C1 commits the fixture. A
  committed fixture is a precondition for the gate's own green row.

### 6.7 Old claims are not admissible evidence

| claim | location | why it cannot be relayed |
|---|---|---|
| `sha256 7efda63b...` for `tools/souji-verify.sh` | `tests/results/INSTALL.json:4` | r2 bytes; HEAD blob is `9adb1764...` |
| `selftest: 24 checks, 0 failed` | `census/round-3/seat-34.json:58` | measured on the r2 installed bytes |
| `verify 40/0, vault 51/0, quarantine 91/0, census 35/0` | `census/round-11/S08-fragment.md:50` | candidate/older bytes; quarantine 91 exceeds the 79 structural bound for HEAD bytes |
| r9 `40/51/91` | `SCORECARD.md:65` | same historical build; already corrected as stale at `SCORECARD.md:72-77` |
| `census selftest 36/36` | `corpus/lessons/round-11.md:9` | a real number for those bytes; the arithmetic in §6.3 reproduces 36, but the claim is not a measurement of the current blob |

A fragment that quotes any of these numbers without its own `evidence` file and `run_id` is
malformed for this protocol, even if the gate's schema accepts its keys.

## 7. Manifest completeness preflight (compensates the gate's deliberate gap)

The gate does **not** maintain an installed-tool allowlist and does **not** check that the manifest
covers the required set; its docstring says so explicitly ("The gate does not maintain a fixed
installed-tool allowlist; the caller-chosen --root and the explicit manifest define the measured
set", lines 97-99). A one-fragment manifest would therefore be `clean`. This preflight closes that
hole and is the part L1 must run before reading a gate result as coverage. It also re-checks every
evidence summary and the live-vs-HEAD digest equality.

Save as `census/round-13/cert/cert-manifest-check.sh` (L1 write; **not** written by this seat):

```bash
#!/usr/bin/env bash
# Complete-coverage preflight for the r13 certification manifest.
# Usage: bash cert-manifest-check.sh <lane-root>
set -u -o pipefail
root=${1:?lane root}
exec python3 - "$root" <<'PY'
import hashlib, json, os, re, subprocess, sys

root = os.path.realpath(sys.argv[1])
tools = {
    "souji-verify": "tools/souji-verify.sh",
    "souji-vault-verify": "tools/souji-vault-verify.sh",
    "souji-census": "tools/souji-census.sh",
    "souji-quarantine": "tools/souji-quarantine.sh",
}
floors = {
    "souji-verify": 38,          # 40 when the R9 locale block runs
    "souji-vault-verify": 49,    # 51
    "souji-census": 36,
    "souji-quarantine": 77,      # 79 at baseline; C2 additions only raise it
}
fail = []

def sha(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()

manifest_path = os.path.join(root, "census/round-13/cert/manifest.json")
try:
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    fragments = manifest["fragments"]
except Exception as exc:
    sys.exit("CERT-MANIFEST: INCOMPLETE manifest-unreadable %s" % exc)
if not isinstance(fragments, list) or len(fragments) != 4:
    fail.append("fragment-count=%r want 4" % (len(fragments) if isinstance(fragments, list) else fragments))

seen_art, seen_author, seen_ev = set(), set(), set()
for rel in fragments:
    try:
        frag = json.load(open(os.path.join(root, rel), encoding="utf-8"))
    except Exception as exc:
        fail.append("%s fragment-unreadable %s" % (rel, exc))
        continue
    art = frag.get("artifact", "")
    author = frag.get("author", "")
    ev = frag.get("evidence", "")
    if art not in tools.values():
        fail.append("%s artifact-not-installed %r" % (rel, art))
    if art in seen_art:
        fail.append("%s artifact-shared %r" % (rel, art))
    seen_art.add(art)
    if author in seen_author:
        fail.append("%s author-duplicate %r" % (rel, author))
    seen_author.add(author)
    if ev in seen_ev:
        fail.append("%s evidence-shared %r" % (rel, ev))
    seen_ev.add(ev)
    try:
        art_sha = sha(os.path.join(root, art))
        if frag.get("sha256") != art_sha:
            fail.append("%s sha-mismatch declared=%s installed=%s" % (rel, frag.get("sha256"), art_sha))
        head = subprocess.run(
            ["git", "-C", root, "show", "HEAD:%s" % art],
            capture_output=True, check=True,
        ).stdout
        head_sha = hashlib.sha256(head).hexdigest()
        if head_sha != art_sha:
            fail.append("%s worktree!=HEAD %s!=%s" % (art, art_sha, head_sha))
    except Exception as exc:
        fail.append("%s artifact-read %s" % (rel, exc))
    try:
        ev_path = os.path.join(root, ev)
        ev_sha = sha(ev_path)
        if frag.get("evidence_sha256") != ev_sha:
            fail.append("%s evidence-sha-mismatch" % rel)
        text = open(ev_path, encoding="utf-8", errors="replace").read()
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            fail.append("%s evidence-empty" % rel)
        else:
            summary = lines[-1]
            match = re.match(r"^selftest: (\d+) checks, (\d+) failed$", summary)
            if not match:
                fail.append("%s evidence-summary %r" % (rel, summary))
            else:
                checks, failed = int(match.group(1)), int(match.group(2))
                tool_id = os.path.basename(art)[:-3]
                if failed != 0:
                    fail.append("%s summary-failed=%d" % (rel, failed))
                if checks < floors.get(tool_id, 0):
                    fail.append("%s checks=%d below-floor=%d" % (rel, checks, floors.get(tool_id, 0)))
                if frag.get("checks") != checks:
                    fail.append("%s checks-field %r != summary %d" % (rel, frag.get("checks"), checks))
                if not isinstance(frag.get("expected_checks"), int) or frag["expected_checks"] != checks:
                    fail.append("%s expected_checks %r != summary %d" % (rel, frag.get("expected_checks"), checks))
        if re.search(r"(?m)^FAIL\b", text):
            fail.append("%s evidence-has-FAIL" % rel)
        skips = [line for line in text.splitlines() if line.startswith("SKIP")]
        if any(not line.startswith("SKIP R9 Turkish locale") for line in skips):
            fail.append("%s unexpected-SKIP %r" % (rel, skips))
        if frag.get("exit_code") != 0 or frag.get("verdict") != "pass":
            fail.append("%s not-pass exit=%r verdict=%r" % (rel, frag.get("exit_code"), frag.get("verdict")))
        if ("tools/%s.sh --selftest" % os.path.basename(art)[:-3]) not in str(frag.get("command", "")):
            fail.append("%s command-does-not-name-installed-suite" % rel)
        if not frag.get("run_id"):
            fail.append("%s run-id-missing" % rel)
    except Exception as exc:
        fail.append("%s evidence-check %s" % (rel, exc))

for art in sorted(set(tools.values()) - seen_art):
    fail.append("coverage-missing %s" % art)

if fail:
    for line in fail:
        print("CERT-MANIFEST: INCOMPLETE " + line)
    sys.exit(1)
print("CERT-MANIFEST: COMPLETE tools=4 fragments=4")
PY
```

`CERT-MANIFEST: COMPLETE tools=4 fragments=4` (exit 0) is the only preflight output that may sit
next to a gate `clean`. This script is new this round and is itself unproven until L1 runs it against
one deliberately broken manifest (e.g. three fragments) and sees `INCOMPLETE`.

### 7.1 L1 assembles the manifest by listing, not writing

The parent lists the four fragment paths it received; it does not edit them. Write-once:

```bash
python3 - /home/vgpnk/Projects/shokunin/souji-shokunin <<'PY'
import json, os, sys
root = sys.argv[1]
frag_dir = os.path.join(root, "census/round-13/cert/fragments")
names = sorted("census/round-13/cert/fragments/" + name
               for name in os.listdir(frag_dir) if name.endswith(".json"))
if len(names) != 4:
    sys.exit("refusing manifest: found %d fragments, want 4" % len(names))
target = os.path.join(root, "census/round-13/cert/manifest.json")
with open(target, "x", encoding="utf-8") as handle:   # O_EXCL: never rewrite a manifest
    json.dump({"fragments": names}, handle, indent=1, sort_keys=True)
    handle.write("\n")
print("manifest: %d fragments" % len(names))
PY
```

A fifth fragment is not "more evidence": this protocol's required set is the four installed
artifacts, and the §7 preflight rejects a manifest whose count or artifact set differs
(`fragment-count` / `coverage-missing`). The gate alone would not catch this — it has no allowlist
(docstring lines 97-99), which is why the preflight is mandatory.

If an author must redo a run, L1 removes the superseded fragment from the listing only after
recording why in the round's report; the superseded bytes stay on disk for inspection, never
silently replaced.

## 8. Gate invocation and frozen snapshot

After the preflight is COMPLETE:

```bash
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-cert-evidence.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --manifest /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/cert/manifest.json
```

Expected, exactly:

```
souji-cert-evidence: clean
scope: evidence_valid/NOT_CERTIFICATION (declared-fragment consistency/integrity only; not tool safety certification; class coverage and command execution are not established)
summary fragments=4 assessed=4 pass=4 fail=0 findings=0
```

Exit 0. A `failed` (exit 1) with `fragment-reported-fail` is honest evidence of a failing suite and
is **not** certification. `could-not-evaluate` (exit 2) means the evidence package itself is
untrustworthy; fix the package, never the verdict text.

### 8.1 Frozen snapshot (tamper-evident record)

One manifest, two roots: the live run above resolves `tools/<tool>.sh` to the worktree; the frozen
run resolves the same relative paths to copied bytes. L1 creates the snapshot once, after the live
gate is clean:

```bash
python3 - /home/vgpnk/Projects/shokunin/souji-shokunin <<'PY'
import hashlib, json, os, shutil, sys
root = sys.argv[1]
src = os.path.join(root, "census/round-13/cert")
dst = os.path.join(src, "frozen")
os.makedirs(dst, exist_ok=False)                      # refuse to overwrite a snapshot
manifest = json.load(open(os.path.join(src, "manifest.json"), encoding="utf-8"))
rels = ["manifest.json"] + manifest["fragments"]
for rel in manifest["fragments"]:
    frag = json.load(open(os.path.join(root, rel), encoding="utf-8"))
    rels += [frag["artifact"], frag["evidence"]]
files = {}
for rel in rels:
    target = os.path.join(dst, rel)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copyfile(os.path.join(root, rel), target)  # byte copy, never a symlink
    files[rel] = hashlib.sha256(open(target, "rb").read()).hexdigest()
with open(os.path.join(dst, "expected.json"), "x", encoding="utf-8") as handle:
    json.dump({"manifest": "manifest.json", "verdict": "clean", "files": files},
              handle, indent=1, sort_keys=True)
    handle.write("\n")
PY
```

Then:

```bash
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-cert-evidence.py \
  --frozen /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/cert/frozen
```

Expected: `souji-cert-evidence: clean`, and
`summary fragments=4 assessed=4 pass=4 fail=0 findings=0 frozen_files=13` (manifest + 4 fragments +
4 evidence + 4 tool copies), exit 0. `expected.json` is the caller's trust anchor and is not
self-authenticated; the frozen run proves the record did not change after this point, not that the
live tools still match it. Re-running the live gate catches drift.

## 9. Candidate selection: class probes, never check count

The r11 selection rule ranked candidates by selftest size and chose a candidate that fails the class
under test (`census/round-11/dissent-32.md:74-80`: `impl-46`, 67 checks, failed the empty-prior
class; `cand-census-08`, 35 checks, closed it). QUALITY Q6 encodes the result
(`corpus/QUALITY.md:30`; lesson `corpus/lessons/round-11.md:16`). The rule for this round:

1. **Installed paths only.** Candidates (`cand-*`) are never certifiable; promotion means install
   the bytes at `tools/souji-<name>.sh`, commit, then measure. The gate enforces the basename rule.
2. **Pre-register the class table before the run.** Each row is
   `class-id | positive probe | negative probe | expected finding/exit`. A candidate is eligible
   only if every row passes on the candidate bytes and the same rows fail (red-before) on the
   baseline bytes.
3. **Check count is recorded, never a ranking key.** It is useful as a regression tripwire
   (`expected_checks`), not as a quality score. More checks can mean more irrelevant assertions;
   fewer checks can mean better-targeted ones.
4. **No hidden promotion.** A verdict on a candidate may be recorded as a candidate result, but the
   manifest's `artifact` must be the installed path. A `clean` gate result over a candidate path is
   rejected by construction.

For C2 specifically, the class rows are: bounded `mv`/`git mv`, bounded `sha256sum`, FIFO target
refusal, FIFO descendant refusal, delayed-`mv` timeout, delayed-digest timeout, no deletion after a
timeout, and staged-byte preservation. The fixture must run those before and after the change
(`--tool <path>` red-before mode is the executor's contract); suite size is not part of the
selection.

## 10. Decision: broad certification cannot be granted this round

Default answer: **NO.** The state at this baseline and the reason for each blocker:

| # | blocker | observed fact | consequence |
|---|---|---|---|
| B1 | Q8 is open in the installed quarantine tool | `grep -c timeout` on the HEAD blob is **0**; stage-2 calls `git -C "$crepo" mv` at `souji-quarantine.sh:529` and `mv --` at `:536` with no wrapper; pin/digest calls reach `content_digest` (`:196`), whose `file_sha` call resolves to the **last** definition at `:722` (the `:184` definition is dead), and `dir_digest` at `:186` is likewise shadowed by `:727`; none is bounded; no `mkfifo`/FIFO/socket case exists in `run_selftest` (`:1304-1514`) | the tool cannot yet satisfy QUALITY Q8's test; C2 must land and be measured post-integration |
| B2 | no admissible evidence set exists | `census/round-13/cert/` did not exist at the baseline; the gate is untracked and still changing (`tools/souji-cert-evidence.py`, 1377→1442→1509 lines observed during the wave); `tests/results/INSTALL.json:4` pins non-installed bytes | there is nothing to certify *from* until the four fragments are produced after integration |
| B3 | the gate deliberately does not enforce coverage | docstring lines 97-99: no fixed installed-tool allowlist; a zero- or one-fragment manifest can be `clean` | a gate `clean` alone is not coverage; §7 preflight is mandatory and itself new |
| B4 | the harnesses do not satisfy Q4 literally | `souji-census.sh:418,516` default to `${TMPDIR:-/tmp}` and contain no `/var/tmp`; the other three each contain one `${TMPDIR:-/tmp}` selftest line (`souji-verify.sh:1105`, `souji-vault-verify.sh:1308`, `souji-quarantine.sh:1247`) and only default to `/var/tmp` through a top-level export | the *invocation* can force `/var/tmp`, but a claim that the tests themselves satisfy Q4 is false; scope Q4 to knowledge fixtures or change the tools |
| B5 | no Q5 blind re-derivation, no Q9 result, no Q7 commit yet | QUALITY Q5 (`corpus/QUALITY.md:29`), Q9 (`:33`), Q7 (`:31`) | even a four-green set stays self-verdict until a named blind seat re-derives it and L1 commits under the guarded form |

What is admissible this round, if and only if the conditions are met after integration:

- **per-tool row:** `suite-green, evidence-consistent` — the fragment passes §5, the preflight is
  COMPLETE, the live and frozen gates are `clean`, and the tool's own Q8/Q9 conditions hold. This is
  a statement about measured bytes, not a deletion authority.
- **not admissible:** "broad certification", "CERTIFIED toolchain", any wording that implies
  receipts are safe to act on. Deletion authorization stays **OFF** per the round contract and C2's
  explicit "without granting deletion certification", independent of any suite result.
- **flip condition (future round, not this one):** all four rows valid + preflight COMPLETE +
  frozen clean + a named Q5 blind re-derivation + Q9 green + an operator decision on deletion
  authority. Any one missing keeps certification OFF.

## 11. Final checks for L1 (exact commands, expected results)

1. **HEAD identity and clean tool paths**
   `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → the integration commit;
   `git -C ... status --porcelain -- tools/` → empty.
2. **Gate selftest**
   `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-cert-evidence.py --selftest` → `selftest: <N>/<N> passed`, exit 0, with `N` re-derived from the committed file (31 at first observation, 38 at the last; requires `tests/fixtures/r13-cert-frozen/`).
3. **Preflight**
   `bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/cert/cert-manifest-check.sh /home/vgpnk/Projects/shokunin/souji-shokunin` → `CERT-MANIFEST: COMPLETE tools=4 fragments=4`,
   exit 0; and one negative control with three fragments → `INCOMPLETE`, exit 1.
4. **Live gate** → `souji-cert-evidence: clean`, `summary fragments=4 assessed=4 pass=4 fail=0 findings=0`,
   exit 0.
5. **Frozen gate** → `clean`, `frozen_files=13`, exit 0.
6. **Byte table** — re-hash the four tools:
   `sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-{verify,vault-verify,census,quarantine}.sh`.
   `verify`, `vault-verify`, and `census` should still equal §3; if one changed under a reviewed
   r13 edit, §3 is superseded and the new digest must be the one in that tool's fragment (an
   unrecorded change invalidates the fragment). `quarantine` must equal its C2-measured digest, and
   that digest must be the one in its fragment.
7. **Q8 evidence** — `grep -c timeout /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh` > 0; the literal QUALITY test
   `grep -nE 'timeout [0-9]+[smh]? .*(mv|sha256sum)' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh` must match, or a
   wrapper must exist **and** the fixture must show bounded stagger/FIFO refusal; the fixture run on
   the §3 baseline copy must fail (red-before) and on the installed bytes must exit 0. A timeout
   (124/137) in any case is a failure, never a pass.
8. **Duplicate definitions** — `grep -c '^file_sha()' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh` = 1 and
   `grep -c '^dir_digest()' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh` = 1 (five definition lines exist at baseline; the later definition
   silently wins, `baseline-measures.md` §2).
9. **Q9** — `shellcheck -S warning /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-quarantine-bounds.sh`
   → exit 0. (`-S error` is not the gate; `corpus/QUALITY.md:33`.) The Python gate is not a
   shellcheck target.
10. **Q7 commit** — the integration commit was made with
    `git -C <repo> -c maintenance.auto=false commit -- <paths>` and
    `git -C <repo> show --stat --format= <hash>` lists only approved paths.
11. **No relay** — `git -C <repo> diff --stat -- census/round-10/cert-16.json census/round-11/cert-16.json`
    empty; their sha256 remain `662294df4291c16fb0fe8c9a0b6dd58b72ada9476b45113fa7c44d383952c3c1`
    and `718409192fd82f7a9fff70965d24d4161713792bb7afd04e04de55cc595598fc`
    (`baseline-measures.md` §2).
12. **State text** — `SCORECARD.md`'s certification note still says OFF unless all of the above
    passes and L1 decides otherwise. This protocol's recommendation is: keep it OFF this round.

## 12. Limitations and calibration notes

- **No runs by this seat.** Every count in §6 is static enumeration of emission sites and loop
  multiplicities, not an observed summary. The conditional counts (R9 locale on/off) are the one
  place `[to-verify]` remains until a certifier runs on this host: with the locale sources present,
  the expected totals are 40 / 51 / 36 / 79; with `SKIP R9 Turkish locale` they are 38 / 49 / 36 / 77.
- **The quarantine bytes are moving.** C2 will add checks and `timeout` call sites. §6.4's 79 is a
  red-before figure and a floor; the post-integration `expected_checks` must be re-derived, and a
  fragment that hard-codes 79 after C2 adds cases is a false-success risk (it will fail the
  `expected_checks` equality, which is the intended behavior).
- **The gate is in flight.** It is untracked at this baseline; its schema and case count can change.
  The protocol binds to the CLI and the documented finding ids, not to line numbers. No fragment
  may cite an uncommitted gate as its harness.
- **Coverage is caller-enforced.** The gate explicitly disclaims an installed-tool allowlist and
  command execution; §7's preflight is the only completeness check, and it cannot prove a command
  ran. The gate's own limitation text says a co-conspiring author can report a false exit code whose
  digests all match (docstring lines 136-139). This protocol narrows but does not close that hole;
  a blind Q5 seat is the remaining check.
- **Author identity is an unauthenticated string.** The gate rejects duplicate labels and shared
  inodes/paths, but it cannot prove the author is not the parent or a sibling model. Gate output
  must be read as "evidence-consistent", never "independent".
- **Q4 is not satisfied by the harnesses themselves.** The invocations here force
  `TMPDIR=/var/tmp`, but `souji-census.sh` has no `/var/tmp` path at all and the other three carry
  a `${TMPDIR:-/tmp}` fallback. A certification claim about the *tests* satisfying Q4 would be
  false; the claim this protocol supports is only "the executed run used `/var/tmp`".
- **Q8's literal test is a grep proxy.** A correct wrapper can still fail the literal
  `timeout ... mv|sha256sum` regex if it hides behind a function. Record both the literal grep and
  the behavioral fixture; the fixture outranks the proxy, and the proxy's failure is a criterion
  defect to report, not a reason to call a bounded tool unbounded.
- **No deletion authority.** Nothing in this document, and no `clean` gate result, authorizes a
  deletion, a quarantine purge, or a certification flip. Those remain operator/L1 decisions with
  their own receipts and holds.
