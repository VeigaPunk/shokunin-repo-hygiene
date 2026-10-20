# RevRegenerate — `tests/fixtures/r15-preservation-frozen/regenerate.py`

Seat SoujiR16.RevRegenerate-4 (wave 2, FALSIFY). Target at lane HEAD `a6ec7810e9b5`.
Source-only review: nothing under the lane was executed (no ALLOWED-EXEC on this item).

## Verdicts

**1. Does it record only real run output? — partial.**
The load-bearing fields are real: `stdout` is the complete captured stream
(regenerate.py:54, 75) and `cases`/`summary` are re-derived from exactly that stream
(59-66). The checker independently re-parses the recorded `stdout` and rejects a
declared case set or summary that differs from it
(tools/souji-preservation-evidence.py:1350-1362, 1383-1410), so a hand-shaped `cases`
list cannot survive. Three fields are literals instead of measurements: `stderr`
(79), `timed_out` (74), `stdout_truncated` (78). The latter two are provably true for
every written record (see "What holds"); `stderr` is not — F2. The stdout digest is
also taken over a lossy decode — F5.

**2. Can it pin uncommitted bytes? — holds for the normal flow; one narrow exception.**
The guard at 89-95 runs before any payload is measured and compares
`git show <rev>:<path>` against the worktree bytes for exactly the three paths that are
later pinned; every arm's tool comes from a commit blob (104-106), never the worktree,
and the record's tool digest (71) is cross-bound to the transcript `TOOL` line by the
gate (checker:1360-1362). With a single writer, an uncommitted tool or fixture cannot be
pinned. The exception is F1: the two fixture pins are re-read from the worktree after all
four arms have run, and no fixture digest is bound to a transcript, so a concurrent edit
inside the run window is pinned without having been measured.

## Findings (severity order)

### F1 — fixture pins are measured after the runs, with no transcript binding (medium)

`record.json`'s `fixture.sha256` / `namespace_fixture.sha256` (regenerate.py:118-119)
and `expected.json["files"]` (126-127) are computed from `(LANE / rel).read_bytes()`,
i.e. from the worktree at *write* time — not from the blobs the guard already read at
90-92. The four arms themselves execute the worktree fixtures (`run_arm(CONFIG_FIXTURE,
…)` at 109, `run_arm(NS_FIXTURE, …)` at 111, cwd=LANE), so the guard is a one-shot check
at T0 while the pins are taken at T1, up to 4 × `timeout 300` later (53).

Counterexample path (no exploit, just a concurrent writer): edit
`tests/fixtures/r15-census-config.py` in the window. The record and `expected.json` then
pin the edited bytes, while the transcripts were produced by the `rev` bytes. The frozen
evaluator cannot see it: fixture pins are checked only against that same live worktree
(checker:1700-1718) and `record.fixture.sha256` the same way (1235-1250); only the *tool*
has a transcript cross-binding (1360-1362). A non-semantic edit (message/comment text)
keeps the independent status oracle green (checker:1302-1320), so the gate reports clean
while pinning bytes that produced no transcript. The tool is safe from this race because
`changed.tool.sha256` is bound to both the observed worktree tool (1275-1279) and the
transcript `TOOL` digest (1360-1362).

Minimal patch — keep the verified blobs, re-verify after the runs, pin from the blobs:

```python
    verified = {}
    for rel in (TOOL, CONFIG_FIXTURE, NS_FIXTURE):
        committed = subprocess.run([...], check=True, capture_output=True).stdout
        if committed != (LANE / rel).read_bytes():
            ...
            return 2
        verified[rel] = committed
    ...
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    for rel, blob in verified.items():
        if (LANE / rel).read_bytes() != blob:
            print(f"regenerate: {rel} changed while the arms were measured", file=sys.stderr)
            return 2
```

then substitute `sha_bytes(verified[rel])` for `sha_bytes((LANE / rel).read_bytes())` at
118-119 and 126-127. Stronger variant, optional: run each fixture from a scratch copy of
its verified blob; both fixtures reach `__file__` only for a default tool
(r15-census-config.py:1467-1470, r14-census-boundary.py:681), and `--tool` is always
passed, so a relocated copy is behaviour-identical.

### F2 — `stderr` is pinned as a literal empty string (medium-low)

`capture_output=True` (54) captures the child's stderr, but line 79 writes `"stderr": ""`
unconditionally and `proc.stderr` is never read. `r15-census-config.py` has exactly one
stderr write today (`die()`, 263-265), and every `die()` aborts the arm before a record is
written, so the false value is currently unreachable for the fixture's own paths — the
defect is structural, not yet observable. It becomes a false record the first time
anything emits a warning or a non-fatal diagnostic, and the docstring's "records only what
the runs printed" (regenerate.py:7-8) is already untrue of the code. The checker only
type-checks the field (1121) and never compares it to anything, so nothing downstream would
catch the first occurrence.

Minimal patch: `"stderr": proc.stderr,` (optionally with `stderr_sha256` /
`stderr_bytes_total`, both already accepted by the checker's generic stream loop,
1095-1119). Otherwise drop the key; a literal `""` is the one value it must not be.

### F3 — `expected.json["verdict"] = "clean"` is authored; the script exits 0 either way (low)

Line 130 hardcodes `"verdict": "clean"` and line 137 returns 0 regardless of what the arms
recorded. Concrete case: regenerate at a `rev` whose `changed` arm carries a FAIL (a
regression) or whose namespace arm is not 12/12. It writes a "clean" pin, prints
`changed=1/20 fail`, and returns 0. This is not a silent admission — the gate recomputes
the verdict and refuses on mismatch (checker:1750-1760) — but the generator's own success
signal is wrong, and the committed snapshot is born failing.

Minimal patch: after both writes, run the authoritative check and propagate its status:

```python
    check = subprocess.run(
        [sys.executable, str(LANE / "tools/souji-preservation-evidence.py"),
         "--frozen", str(HERE), "--root", str(LANE)],
        capture_output=True, text=True)
    sys.stdout.write(check.stdout)
    sys.stderr.write(check.stderr)
    return check.returncode
```

`--frozen DIR --root DIR` is the supported invocation (checker:2606-2616), and frozen
mode only re-measures a pinned snapshot: no tool execution (checker:31, 1772).

### F4 — the could-not-evaluate path discards the reason and uses exit 1 (low)

Lines 67-69 raise `SystemExit(f"... could not evaluate (rc={proc.returncode})")`. The
fixture's actual cause is on `proc.stderr` (e.g. `die()` at r15-census-config.py:264,
strace-probe failure at 749/751) and is captured but never printed; `SystemExit(str)` exits 1,
while the other refusal path (95) returns 2, so the two refusals are not distinguishable
by code.

Minimal patch:

```python
        raise SystemExit(f"regenerate: {fixture} on {commit} could not evaluate "
                         f"(rc={proc.returncode}): {proc.stderr.strip()[-400:]}")
```

(or return a sentinel from `run_arm` and `return 2` from `main`, matching line 95).

### F5 — digests describe the decoded text, not the bytes the run printed (low)

`subprocess.run(..., text=True, errors="replace")` (54-55) replaces any non-UTF-8 byte
with U+FFFD and decodes with the locale encoding before `stdout_sha256` and
`stdout_bytes_total` are computed (76-77). The checker's digest test re-encodes the
*recorded* text (1338, `_sha_text` 1811-1812), so the rewrite is undetectable by
construction: the record cannot prove its stdout is byte-identical to the process output.

Minimal patch: `encoding="utf-8", errors="strict"` at 54-55. A non-UTF-8 transcript then
aborts loudly instead of being rewritten, and the pin stops depending on the caller's
locale.

### F6 — README still prescribes the manual digest-only re-pin (doc, low)

`tests/fixtures/r15-preservation-frozen/README.md:12-18` tells the integrator to hand-edit
`measured_commit`, the tool digests, `fixture.sha256`, `record_sha256` and the `files`
pins. That is exactly the "authored transcript with new digests" the script exists to
replace (regenerate.py:3-5). An integrator who follows the README instead of the script
recreates the R4 defect.

Minimal patch: replace README steps 1-2 with "run
`python3 tests/fixtures/r15-preservation-frozen/regenerate.py --rev <commit>`; it refuses
a worktree that differs from `<commit>` and refuses to write when any arm cannot
evaluate."

## What holds (checked)

- Guard order and coverage: 88-95 completes before scratch creation (96); the three
  checked paths are the record's `fixture`/`namespace_fixture` plus all three
  `expected.json["files"]` entries (126-127); arm tools are written from
  `git show <full>:TOOL` (104-106), never copied from the worktree.
- Real-output core: 54/75 capture the whole stream (no truncation branch), 59-66 derive
  `cases`/`summary`; the checker re-parses and compares both, including detail text
  (1383-1410).
- The `timed_out` / `stdout_truncated` literals are safe: `timeout 300` in argv (53)
  makes a real timeout exit 124/137, which 67 rejects before any record is written, and
  `capture_output=True` cannot truncate.
- No partial snapshot: both files are written only after all four arms return (114-133);
  an abort during the runs leaves the previously committed pins untouched (and 95 refuses
  before any scratch is created).
- The committed frozen directory is internally consistent at HEAD: `sha256sum` gives
  `record.json` = `173db77793bca747e9efad4150ea8a0dd2d9d4bdc0c17f30dc734bfe0e983599`,
  equal to `expected.json.record_sha256`, and all three `files` pins equal the live bytes;
  `git status --porcelain` over those four paths is empty. The record's
  `measured_commit` is `c6207bdac2e0…`, not lane HEAD `a6ec7810e9b5…`; the gate still
  passes because the pinned tool (`64a60fd0…`) and both fixtures are byte-identical
  between the two commits.

## Residual risk

- The record is a one-shot pin, not a reproducible one. `argv` and transcripts embed
  `/var/tmp/souji-r16-repin.<rand>/…` (record.json:16, 82, 365, 471), the fixture's own
  `/var/tmp/r15-census-config.<rand>/…` appears in FAIL details (record.json:246, 291,
  331) together with traced PIDs, so regenerating identical inputs yields a different
  `record_sha256`. "Re-run and diff the digest" is not a verification path. This is
  consistent with `declared_consistency_only: true` (regenerate.py:116); it is honest only
  as long as `expected.json` is not read as reproducible provenance.
- Frozen verification is digests plus internal consistency and never re-executes
  (checker:31, 1772, 2606-2616), so "regenerated from real runs" is not machine-checkable; the
  gate proves the pins match the committed bytes and that the transcript is
  self-consistent with an independent status oracle.

## Verification gaps

- I did not execute `regenerate.py`, either fixture, `tools/souji-census.sh`, or
  `tools/souji-preservation-evidence.py` (no ALLOWED-EXEC). Every statement above is from
  source reading plus `sha256sum` / `git` byte comparisons.
- F1's race is a code-path argument, not an exercised counterexample; exercising it would
  require running the tool suite, which this item forbids.

STATUS: ok

## Commands

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --long a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae -- tests/fixtures/r15-preservation-frozen/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "open(\|read_text\|read_bytes\|Path(\|subprocess\|argv\|--tool\|sys.argv" tests/fixtures/r15-census-config.py | head -60; echo ===; grep -n "open(\|read_text\|read_bytes\|Path(\|subprocess\|sys.argv" tests/fixtures/r14-census-boundary.py | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "var/tmp\|stderr\|timed_out\|stdout_bytes_total" tests/fixtures/r15-preservation-frozen/record.json | head -40; echo ---; cat tests/fixtures/r15-preservation-frozen/expected.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "stderr\|timed_out\|stdout_truncated\|record_sha256\|expected\|verdict\|summary\|cases" tools/souji-preservation-evidence.py | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "" tests/fixtures/r15-preservation-frozen/regenerate.py | sed -n '54,140p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1180,1280p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1280,1330p;1330,1460p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1086,1160p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== fixture stderr writes =="; grep -n "sys.stderr" tests/fixtures/r15-census-config.py; echo "== ns fixture =="; grep -n "sys.stderr" tests/fixtures/r14-census-boundary.py; echo "== checker re-exec? =="; grep -n "subprocess\|Popen\|run(" tools/souji-preservation-evidence.py | head; echo "== census self-location deps =="; grep -n "BASH_SOURCE\|dirname\|^source\|^\. \|source " tools/souji-census.sh | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '250,285p' tests/fixtures/r15-census-config.py; echo "=== warn callers ==="; grep -n "^def warn\|warn(" tests/fixtures/r15-census-config.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "SCRIPT_DIR\|REPO_ROOT\|\bROOT\b" tools/souji-census.sh | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1460,1560p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^INSTALLED_TOOL_PATH\|^PREHARM_COMMIT\|^BASELINE_COMMIT\|^PREHARM_SHA256\|^BASELINE_SHA256\|^SCHEMA_ID\|^CONFIG_FIXTURE_PATH\|^NAMESPACE_FIXTURE_PATH\|^MAX_BIND_BYTES" tools/souji-preservation-evidence.py; echo ---; python3 - <<'EOF'
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
for arm,v in r['runs'].items():
    print(arm, v['exit_code'], v['summary'], len(v['cases']), v['tool']['sha256'][:12], v['tool']['commit'][:12])
print('ns', r['namespace_controls']['exit_code'], r['namespace_controls']['summary'], r['namespace_controls']['tool']['sha256'][:12], r['namespace_controls']['tool']['commit'][:12])
print('measured', r['measured_commit'][:12], 'argv0', r['runs']['changed']['argv'])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1560,1700p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1700,1790p' tools/souji-preservation-evidence.py; echo "=== CLI ==="; grep -n "add_argument\|--frozen\|--selftest\|--root" tools/souji-preservation-evidence.py | sed -n '1,30p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "_status_for\|def _sha_text" -A12 tools/souji-preservation-evidence.py | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tests/fixtures/r15-preservation-frozen/record.json tests/fixtures/r14-census-boundary.py tests/fixtures/r15-census-config.py tools/souji-census.sh; echo "== HEAD blob ids =="; git -C . rev-parse HEAD:tests/fixtures/r15-preservation-frozen/record.json HEAD:tests/fixtures/r15-preservation-frozen/expected.json; echo "== worktree dirty check on these paths =="; git -C . status --porcelain -- tests/fixtures/r15-preservation-frozen tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "__file__\|parents\[" tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '725,800p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "run_tool(" tests/fixtures/r15-census-config.py | wc -l; grep -n "run_tool(\[" -A3 tests/fixtures/r15-census-config.py | grep -c "\-\-root"; echo "== invocations lacking --root in first 6 lines =="; python3 - <<'EOF'
import re
src=open('tests/fixtures/r15-census-config.py').read().splitlines()
idx=[i for i,l in enumerate(src) if 'run_tool(' in l]
bad=[]
for i in idx:
    window='\n'.join(src[i:i+10])
    if '"--root"' not in window and "'--root'" not in window and '--root=' not in window:
        bad.append((i+1, src[i].strip()))
print(len(idx), 'call sites;', len(bad), 'without visible --root')
for b in bad[:10]: print(b)
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "" tests/fixtures/r15-preservation-frozen/README.md | sed -n '1,30p'; echo "=== ARM_IDS / stdout digest check lines ==="; grep -n "^ARM_IDS\|_sha_text(stdout)\|stderr must be a string" tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '40,60p' tests/fixtures/r15-preservation-frozen/regenerate.py; echo "=== die context in fixture ==="; sed -n '255,270p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "snapshot-verdict-mismatch\|transcript TOOL sha256\|binding-digest-mismatch" tools/souji-preservation-evidence.py | head; echo ===; grep -n "def _check_bindings" tools/souji-preservation-evidence.py; grep -n "observed_tool" tools/souji-preservation-evidence.py | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1955,2010p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "def main\|add_argument" tools/souji-preservation-evidence.py; echo ===; sed -n "$(grep -n 'def main' tools/souji-preservation-evidence.py | tail -1 | cut -d: -f1),+45p" tools/souji-preservation-evidence.py
mkdir -p /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2 && ls -d /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2
```
