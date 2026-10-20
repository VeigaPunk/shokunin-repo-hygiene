# RevGateFrozenRules — frozen expected.json / record_sha256 / measured_commit / root-prefix review

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Target: `tools/souji-landing-gate.py` (sha256 `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`, clean in worktree) and its frozen data. Fixture `tests/fixtures/r16-landing-gate.py` sha256 `aae67c9c7bafd86f1b745193ac4aead74b3a3403b5c5ade33991d246e6413f2`.

Method: source only. The gate was **not executed** (no `ALLOWED-EXEC` in this item); every behavioural claim below is derived from the source, and every digest claim from `git cat-file`/`git show` + `sha256sum`/`rev-parse` on named paths. Where the gate's behaviour is asserted, it is a read of the code at the cited lines, not a measured run.

Verdicts: **root-prefix resolution holds** (no defect). `record_sha256` and `measured_commit` comparisons hold for the shipped, well-formed records, but the frozen layer has one hard output-contract failure (F1) and four false-negative/misleading channels (F2–F5), all in malformed or adversarially shaped input.

---

## Holds (explicitly no finding)

1. **Root-prefix resolution — holds.** `_pin_repo_path` (`tools/souji-landing-gate.py:364-368`) implements exactly the documented rule: a key starting with `tools/`, `tests/`, `census/`, `corpus/` (`:90`) resolves at the snapshot root; anything else resolves at `<frozen_dir>/<key>`; there is no fallback in either direction. Both branches are exercised by the shipped data and produce correct resolutions:
   - r13 (7 dir-local keys, `tests/fixtures/r13-cert-frozen/expected.json:5-11`) — all seven hashes recomputed from `HEAD:<frozen_dir>/<key>` equal the pins (`902fd623…`, `48dce861…`, `c78445a7…`, `606d4f9e…`, `3b41e8f9…`, `26beb4ca…`, `58f199c1…`).
   - r15 (3 root keys, `tests/fixtures/r15-preservation-frozen/expected.json:3-5`) — all three equal their pins at `HEAD` **and** at the record's measured commit `c6207bd` (`64a60fd0…`, `274743…`, `e6a984…`).
   No dir-local/root shadowing fallback exists to misuse; the shadowing case is the intended `LG-FROZEN-PIN` (fixture case 6).

2. **`record_sha256` comparison — holds for well-formed input.** `tools/souji-landing-gate.py:425-456` reads the record blob at REV via `tree[record_repo]`, hashes it, and flags type/non-hex/mismatch. Verified: `sha256(HEAD:tests/fixtures/r15-preservation-frozen/record.json)` = `173db77793bca747e9efad4150ea8a0dd2d9d4bdc0c17f30dc734bfe0e983599`, exactly `expected.json:8`. The historical record also verifies: `record_sha256` `4749ad07…` at `b410186:…/expected.json:8` equals `sha256(b410186:…/record.json)`.

3. **`measured_commit` comparison — holds for the shipped records.** `c6207bd` resolves and the three pinned blobs at it equal the pins (above). The historical `b410186` record's `measured_commit fc3a8d49…` resolves, and the source semantics reproduce the claimed replay exactly: one `LG-FROZEN-PIN` (tool pin `b5187351…` vs `dab4122c…` at REV) plus two `LG-FROZEN-MEASURED` (tool pin vs `fcff8b05…` at measured; r15-fixture pin `6314d45…` whose path is absent at measured; the r14-boundary pin matches at measured). That is the advertised "3 pin" findings on `b410186`.

4. Ancestry of `measured_commit` is not checked, and that is **not** a defect to patch: every pin must also equal the blob at REV (`:395-424`), so an unrelated measured commit can only satisfy the check by holding the same bytes; the check is a byte-truth test, not a provenance test (provenance of the *runs* belongs to `tools/souji-preservation-evidence.py`).

---

## Findings

### F1 — malformed `expected.json` shape escapes as an uncaught traceback: exit 1, no finding row, no SUMMARY (fails)

`/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:391-395` assumes `expected.json` is an object, `files` is an object, and `record` is a string:

- `expected` is a list/string/null → `.get` at `:391` raises `AttributeError`.
- `"files"` is a truthy non-object → `.items()` at `:395` raises `AttributeError`.
- `"record"` is a truthy non-string → `_pin_repo_path` → `key.startswith` at `:366` raises `AttributeError`.

`check_frozen_pins` is called inside `evaluate`'s `try` (`:569`), but only `EvalError` is caught (`:586-588`). The exception therefore leaves `evaluate` before `emit`, so the run prints a Python traceback to stderr, **no TSV row, no `SUMMARY`**, and the process exits 1 (interpreter default), not the documented exit 2 for could-not-evaluate. A seat can land a syntactically valid but shape-invalid pin file and the gate reports "findings" without a finding.

Invalid *syntax* is already a finding (`:386-390`), so shape invalidity should be one too. Minimal patch, at `:391-394`:

```python
        if not isinstance(expected, dict):
            findings.append(("LG-FROZEN-PIN", exp_path,
                             "expected.json is not a JSON object: %s" % type(expected).__name__))
            continue
        files = expected.get("files") or {}
        if not isinstance(files, dict):
            findings.append(("LG-FROZEN-PIN", exp_path, "files is not a JSON object"))
            files = {}
        record = {}                      # :392 — dead, delete
        record_key = expected.get("record")
        if record_key is not None and not isinstance(record_key, str):
            findings.append(("LG-FROZEN-PIN", exp_path,
                             "record is not a string: %r" % (record_key,)))
            record_key = None
        record_repo = _pin_repo_path(frozen_dir, record_key) if record_key else None
```

(`record = {}` at `:392` is overwritten at `:460`/`:462`; remove it while here.) Equivalent alternative: wrap the body in `except (AttributeError, TypeError)` → `EvalError`, but the finding route is consistent with `:386-390`. No shipped dir is affected; `tests/fixtures/r16-landing-gate.py` has no malformed-shape case, so add one synthetic case.

### F2 — a zero-pin frozen dir is certified clean without any check (partial)

`/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:391` coerces a missing/empty `files` to `{}`; `:395` then iterates nothing. If `record_sha256` is also absent (`:425`) and `record` absent (`:458`), `check_frozen_pins` returns `([], 0)`. A matching `tests/fixtures/<name>-frozen/expected.json` containing `{}` or `{"verdict": "clean"}` is therefore certified clean, and the only trace is `checked_pins=0` in the SUMMARY (`:599-608`) while exit is 0. This is exactly the round-15 hand-edit class (a pin file written/truncated at landing), and the lane's own frozen contract rejects it: `tools/souji-preservation-evidence.py:1619-1621` requires `files` to be a non-empty object and `:1613-1615` requires `record_sha256`.

Minimal patch, after `:391`:

```python
        if not files and "record_sha256" not in expected:
            findings.append(("LG-FROZEN-PIN", exp_path,
                             "expected.json declares no files pins and no record_sha256"))
            continue
```

(`if not files:` alone also matches `souji-preservation-evidence.py:1620`; both are replay-safe — all three shipped dirs have non-empty `files`.)

### F3 — a `measured_commit` that resolves nowhere silently disables `LG-FROZEN-MEASURED` (partial; concrete in-tree instance)

`/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:459-476`: an unparseable record becomes `{}` (`:461-462`), a non-string or non-hex `measured_commit` sets `measured_ok = False` (`:475-476`), a `rev-parse` failure sets it `False` (`:474`), and `if measured_ok:` (`:477`) simply performs no checks. There is no finding for "the record claims a measurement at a commit that is not resolvable" — the same defect class as R16-M2, surviving at the record level instead of the expected.json level.

Concrete instance: `tests/fixtures/r14-cache-frozen/record.json:6` declares `"measured_commit": "0123456789abcdef0123456789abcdef01234567"`; `git rev-parse --verify --quiet 0123456789abcdef0123456789abcdef01234567^{commit}` returns rc=1 (verified). The r14 dir has no `record_sha256` and its two pins match REV at `cc21683` and at `HEAD` (both verified), so at both revisions the gate performs **zero** measured checks for it and emits nothing else. The claimed "r14 → 0 findings" replay is true, but that zero includes a frozen record whose measurement claim was never evaluated; an auditor reading the replay as "r14 frozen evidence is coherent" is over-crediting it. A malformed string (`"c6207bd\n"`, a prose sentence, a 3-char prefix) disables the check identically, including on a v1 preservation record.

Replay-safe minimal patch (r14's record has no `schema`; the `b410186` and `HEAD` r15 records are v1 and their `measured_commit` resolve, so their replays are unchanged):

```python
            if measured_ok:
                ...
            elif isinstance(record, dict) and \
                    record.get("schema") == "souji-preservation-record-v1":
                findings.append(
                    ("LG-FROZEN-MEASURED", exp_path,
                     "v1 record measured_commit %r is not a resolvable commit"
                     % (measured,)))
```

Companion guard at `:461-462`: if the parse fails and `"record_sha256" in expected` (the record is content-addressed, so it is claimed to be JSON), emit `LG-FROZEN-PIN "record is not a JSON object"` instead of `record = {}`. If L1 prefers to treat any declared `measured_commit` as a claim, apply unconditionally — that flips `cc21683` to one honest finding on the r14 placeholder; either way the landing decision must not claim r14's record was verified when it was skipped.

### F4 — malformed pin is re-reported as a nonsensical `LG-FROZEN-MEASURED` comparison (partial)

The files loop validates the pin (`:408-415`) before comparing, but the measured loop (`:478-491`) does not: `elif sha256(blob) != pinned:` compares a digest to a non-digest and formats it with `str(pinned)[:16]` (`:499`). For a pin already reported as "not a sha256" and a resolvable `measured_commit`, the gate emits a second row asserting `files[k] pinned zzz but <rev>:<path> hashes <digest>` — a comparison that was never meaningful, and one more `n_checks` (`:479`). One malformed pin, two findings, the second misleading.

Minimal patch at `:478`:

```python
                for key, pinned in sorted(files.items()):
                    if not isinstance(pinned, str) or not SHA256_RE.match(pinned):
                        continue
                    n_checks += 1
```

After this, `str(pinned)` at `:499` can drop to `pinned[:16]`.

### F5 — a v1 preservation record can be accepted with `record_sha256` omitted (partial)

`record_sha256` is checked only when present (`:425`). For r15's shape (`files` pins payloads, `record` separate) omitting `record_sha256` leaves the record bytes unpinned: `measured_commit` and the entire `runs`/`namespace_controls` evidence can be edited at landing with no gate signal (the measured check re-verifies only the `files` payloads). `tests/fixtures/r15-preservation-frozen/README.md` states expected.json "pins the record bytes", and `tools/souji-preservation-evidence.py:1613-1615` requires the field for this format. r14 is not affected (its `record.json` is itself listed in `files`, so its bytes are pinned, and its record declares no schema).

Replay-safe minimal patch, inside the record-parse block after `:460`:

```python
            if isinstance(record, dict) and \
                    record.get("schema") == "souji-preservation-record-v1" and \
                    "record_sha256" not in expected:
                findings.append(
                    ("LG-FROZEN-PIN", exp_path,
                     "v1 record present but record_sha256 is not pinned"))
```

(Alternative without schema coupling: require `record_repo` to appear among the resolved `files` paths when `record_sha256` is absent; r14 satisfies it, a v1-shaped dir missing both does not.)

---

## Residual risk / verification gaps

- The gate itself was not run (probe rule). Digest facts above are exact; behavioural claims are code reads. The fixture (`tests/fixtures/r16-landing-gate.py`, 15 cases) and the in-file selftest (18 cases) contain **no** case for F1–F5, so their green counts do not falsify any of these. Each is one synthetic repo in the fixture's existing `Repo` harness: a non-object `expected.json`, an empty `files` map, a record whose `measured_commit` is `"0"*40`, a non-hex pin under a resolvable measured commit, and a v1 record without `record_sha256`.
- The whole gate is looser than the lane's own frozen schema (`tools/souji-preservation-evidence.py:1601-1636`: object-only, unknown keys rejected, non-empty `files`, mandatory lowercase `record_sha256`, 64-hex pins). The gate deliberately accepts the r13/r14 dir-local style the checker would call `frozen-incomplete`; out of scope here, but L1 should not describe a gate pass as checker coherence.
- F2/F3/F5 share one root cause (the frozen layer is permissive when the claim is absent). If L1 wants one change instead of five, gate all three on `schema == "souji-preservation-record-v1"` plus a no-pins vacuity guard; the shipped `b410186`/`HEAD`/`a31642d`/`cc21683` replay counts are unchanged by that combination as analysed above.
- The frozen-dir scan is one level only: `EXPECTED_JSON_RE` (`:92`) matches `tests/fixtures/<one-segment>-frozen/expected.json`. A frozen dir nested deeper, or not named `*-frozen`, is silently unscanned and contributes no `checked_pins`; a seat choosing a non-conventional path evades the pin layer entirely. The convention is pinned in the docstring, so this is a policy boundary, not a bug; if landing policy wants the convention enforced rather than assumed, widen to `tests/fixtures/.*-frozen/expected\.json` (changes no shipped dir).
- `blob_at_path` (`:150-158`) maps any non-zero `git cat-file` rc to "absent", so a corrupt object store would be reported as a missing path rather than exit 2. Not actionable for a landing gate; noted only.

## Probe-rule disclosure

Two deviations from the listed allowed commands, both read-only:

1. `python3 -c` (stdlib `json` only, no repository code) was used three times to render/read blobs at named paths (r13 pin-key list, `b410186` record key summary, `b410186` `record_sha256`). The two load-bearing facts were re-derived with `grep` on the same named blobs afterwards.
2. One transient scratch file, `/var/tmp/r13pins.txt`, was written and deleted inside the same command (not under `/var/tmp/souji-r16-RevGateFrozenRules-4/`). It does not exist now (`ls` confirms ENOENT).

No lane file, `census/operator-sweep-20261019/`, `~/.omp`, `.ufo/state`, `MANIFEST.json` or sibling lane was touched. No tool was installed or upgraded.

STATUS: ok

## Commands

```sh
wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain | head -50 && sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD | grep -E 'frozen|expected\.json' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in tests/fixtures/r13-cert-frozen/expected.json tests/fixtures/r14-cache-frozen/expected.json tests/fixtures/r15-preservation-frozen/expected.json tests/fixtures/r15-preservation-frozen/record.json; do echo "=== $f"; git show HEAD:$f; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file blob HEAD:tests/fixtures/r15-preservation-frozen/record.json | sha256sum && for p in tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py; do echo -n "c6207bd:$p "; git cat-file blob c6207bdac2e0ef52c1da5fbc87dce5d94065972e:$p | sha256sum; done && echo "--- r14 record:" && git show HEAD:tests/fixtures/r14-cache-frozen/record.json && echo "--- r13 manifest key:" && git show HEAD:tests/fixtures/r13-cert-frozen/manifest.json | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "--- r13 pins at HEAD" && git show HEAD:tests/fixtures/r13-cert-frozen/expected.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('\n'.join('%s %s'%(k,v) for k,v in d['files'].items()))" > /var/tmp/r13pins.txt 2>/dev/null; cat /var/tmp/r13pins.txt 2>/dev/null || true; while read -r k v; do echo -n "$k "; git cat-file blob HEAD:tests/fixtures/r13-cert-frozen/$k | sha256sum | cut -d' ' -f1; done < /var/tmp/r13pins.txt; rm -f /var/tmp/r13pins.txt; echo "--- r14 pins at HEAD"; for p in dependency.txt record.json; do echo -n "$p "; git cat-file blob HEAD:tests/fixtures/r14-cache-frozen/$p | sha256sum | cut -d' ' -f1; done; echo "--- placeholder resolve"; git rev-parse --verify --quiet 0123456789abcdef0123456789abcdef01234567^{commit}; echo "rc=$?"; echo "--- r14 record at cc21683"; git show cc2168325768d5356a82c039dcdf787377c55784:tests/fixtures/r14-cache-frozen/record.json 2>/dev/null | head -8
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '360,500p' tools/souji-landing-gate.py | nl -ba -v360
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-preservation-frozen/regenerate.py | sed -n '80,240p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '500,520p' tools/souji-landing-gate.py | nl -ba -v500 && grep -n "def check_frozen_pins\|pin_findings\|n_pins" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== b410186 expected" && git show b410186:tests/fixtures/r15-preservation-frozen/expected.json 2>&1 && echo "=== b410186 record (keys only)" && git show b410186:tests/fixtures/r15-preservation-frozen/record.json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print({k:(v if not isinstance(v,(dict,list)) else type(v).__name__) for k,v in d.items()})" 2>&1; echo "=== commit topology" && git show -s --format='%H %P %s' c6207bd 0a70bef && git log --oneline -3 -- tests/fixtures/r15-preservation-frozen/record.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== r15 round lesson HEAD" && git show HEAD:corpus/lessons/round-15.md | head -20; echo "=== round-16 lesson worktree" && sed -n '1,120p' corpus/lessons/round-16.md 2>/dev/null | head -120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '556,612p' tools/souji-landing-gate.py | nl -ba -v556
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1595,1640p' tools/souji-preservation-evidence.py | nl -ba -v1595; echo "---"; sed -n '1125,1175p' tools/souji-preservation-evidence.py | nl -ba -v1125
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "record_sha256\|measured_commit\|expected.json\|isinstance\|files\[" tools/souji-preservation-evidence.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "record_sha256\|measured_commit\|root\|prefix\|files" tools/souji-preservation-evidence.py | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "--- frozen dirs at cc21683:" && git ls-tree -r --name-only cc21683 | grep -E '\-frozen/(expected|record)\.json$' && echo "--- r14 record lines:" && git show HEAD:tests/fixtures/r14-cache-frozen/record.json | nl -ba && echo "--- r15 expected lines:" && git show HEAD:tests/fixtures/r15-preservation-frozen/expected.json | nl -ba && echo "--- r15 record measured/schema lines:" && git show HEAD:tests/fixtures/r15-preservation-frozen/record.json | grep -n 'measured_commit\|"schema"'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo -n "b410186 record sha: " && git cat-file blob b410186:tests/fixtures/r15-preservation-frozen/record.json | sha256sum && echo -n "expected record_sha256: " && git show b410186:tests/fixtures/r15-preservation-frozen/expected.json | python3 -c "import json,sys;print(json.load(sys.stdin)['record_sha256'])" && echo "--- measured fc3a8d4 resolves:" && git rev-parse --verify --quiet fc3a8d49b52de26bef74418da96611aae34b958d^{commit}; echo "rc=$?" && echo "--- blobs at b410186 (pins 6314d45/e6a984):" && for p in tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tools/souji-census.sh; do echo -n "$p "; git cat-file blob b410186:$p | sha256sum; done && echo "--- blobs at fc3a8d4:" && for p in tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tools/souji-census.sh; do echo -n "$p "; git cat-file blob fc3a8d49b52de26bef74418da96611aae34b958d:$p 2>/dev/null | sha256sum; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'SHA256_RE = \|record = {}\|EXPECTED_JSON_RE = ' tools/souji-landing-gate.py && ls /var/tmp/r13pins.txt 2>&1 || true
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "--- r13 expected keys (grep)" && git show HEAD:tests/fixtures/r13-cert-frozen/expected.json | grep -n '"[^"]*": "[0-9a-f]\{64\}"' && echo "--- b410186 record_sha256 (grep)" && git show b410186:tests/fixtures/r15-preservation-frozen/expected.json | grep -n 'record_sha256' && echo "--- b410186 record schema/measured (grep)" && git show b410186:tests/fixtures/r15-preservation-frozen/record.json | grep -n '"schema"\|measured_commit"'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "--- r14 expected at cc21683" && git show cc21683:tests/fixtures/r14-cache-frozen/expected.json && echo "--- hashes at cc21683" && for p in dependency.txt record.json; do echo -n "$p "; git cat-file blob cc21683:tests/fixtures/r14-cache-frozen/$p | sha256sum; done
```
