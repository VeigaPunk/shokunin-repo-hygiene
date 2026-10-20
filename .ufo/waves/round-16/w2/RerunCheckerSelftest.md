# R4 attack — rerun `souji-preservation-evidence.py --selftest`, negative-control inventory

Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`
Assignment HEAD: `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae` (lane advanced to `163158a` mid-review;
`git diff a6ec781 163158a -- tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-frozen/ tests/fixtures/r15-preservation-evidence.py tests/fixtures/r15-census-config.py` is empty — reviewed bytes unchanged).
Checker under test: `tools/souji-preservation-evidence.py`, 2653 lines, sha256
`5942f689a61a25884e52a8f1e377e4b41696bf1b920334a60a989beae1034b2a`.

## Verdict on the assigned claim

**Holds.** `--selftest` prints `selftest: 47/47 passed` and exits 0 (1.87 s). The r16 edits
(CASE regex, detail rendering, class tables, `CONFIG_TOKEN_IDS`) removed **no** negative control,
and the r16 tables are byte-for-byte consistent with the observed matrices and the committed
frozen record. Five calibration defects in the surrounding documentation/metadata are reported
below (one moderate); none changes what the checker actually enforces.

## 1. 47/47 — confirmed

```
$ python3 .../tools/souji-preservation-evidence.py --selftest
selftest: 47/47 passed
EXIT=0
```

`python3 -m py_compile` on the same bytes is clean.

## 2. No deleted negative control — evidence

Full diff `b410186..HEAD -- tools/souji-preservation-evidence.py` is 185 lines, 6 hunks, +54/−39.
No `cases.append((` tuple is removed and no case name changes:

- `cases.append((` count: 47 at `b410186`, 47 at HEAD.
- Extracted case-name literals (sorted, 47 vs 47): `diff` empty.
- Only two selftest hunks exist; both change expectations, not coverage:
  - `duplicate-id` (2134-2140): `["case-duplicate","case-finding-mismatch","run-inconsistent","summary-mismatch"]`
    → `["case-duplicate","run-inconsistent","run-inconsistent","summary-mismatch"]`.
  - `finding-mismatch` (2533-2543): count scales `len(CONFIG_REFUSAL_IDS)`=3 → `len(CONFIG_TOKEN_IDS)`=6;
    the control itself is unchanged and **wider**.

Why the `duplicate-id` change is correct, not a lost control: `_eval_arm` builds both
`declared_set` and `parsed_set` with `setdefault` (first row wins, 1374-1382), and the test appends
the injected `CASE\tR15CFG-01\tPASS\tok` row *after* the real row, immediately before `SUMMARY`
(2141-2143). The token rule therefore reads the original, token-bearing row; the old
`case-finding-mismatch` expectation was unreachable under this code (part of the 24/47 as-authored
failure set). The two `run-inconsistent` findings are the post-hoc `stdout` mutation breaking
`stdout_sha256` and `stdout_bytes_total` (1341-1350), and `summary-mismatch` is `total=20` vs 21
CASE rows. Duplicate detection itself survives via `case-duplicate` + that summary check.

`case-finding-mismatch` retains a dedicated negative control (`finding-mismatch`) that asserts one
finding per token id when every token-row is rendered `observed_finding=none`.

## 3. Class tables and `CONFIG_TOKEN_IDS` — verified against three independent artifacts

HEAD tables (323-363): benign `01,04,06,07,09,10,12,13,15,16,20`; refusal `02,11,17`;
safety `03,08,14,18,19`; preserve `05`; `CONFIG_HARM_FAILS` = benign ∪ safety (16 ids).
`CONFIG_TOKEN_IDS` = `02,03,11,14,17,19`.

- `census/round-16/c1-matrix-final.json` and `c1-matrix-landing.json`: a jq predicate encoding the
  HEAD `_expected_status` oracle over `changed`/`pre-harm`/`r14-harm` returns **zero mismatches**
  in both files (20 ids × 3 arms each). Both were also checked against the observed verdict maps
  directly (pre-harm FAIL set = `02,03,08,11,14,17,18,19`; harm FAIL set = 16 ids as above).
- Committed frozen record (`tests/fixtures/r15-preservation-frozen/record.json`): declared statuses
  over `baseline_preharm`/`baseline`/`changed` (20 each) + `namespace_controls` (12) match the HEAD
  oracle with **zero mismatches**; the changed arm's non-`none` token set is exactly
  `["R15CFG-02","R15CFG-03","R15CFG-11","R15CFG-14","R15CFG-17","R15CFG-19"]`.
- `tests/fixtures/r15-preservation-evidence.py:30-38` duplicates the same four tables plus `TOKEN`
  independently; its `external-clean` check (expects exit 0) would fail on any single-id membership
  drift in either direction, because `detail()` (104-110) gives only `TOKEN` ids a non-`none` token.

Supporting frozen-state facts I re-measured: record has 0 literal TABs (space-rendered details);
`expected.json` pins `record.json` sha256 `173db7…`, fixture `2747439…`, tool `64a60fd0…`, all equal
to live bytes (`sha256sum`); tool pins in the record equal `PREHARM_SHA256`/`BASELINE_SHA256`/
changed `64a60fd0…`; `measured_commit = changed.tool.commit = c6207bd`. Every baseline FAIL detail
carries `observed_exit=` (so `baseline-reason-weak` cannot fire) and is ≤ 471 chars
(< `MAX_DETAIL_CHARS` 512). Static reading therefore supports a clean `--frozen` verdict, but I did
not run it (see gaps).

## Findings

### F1 — MODERATE — the file's own oracle table is stale and contradicts the code
`tools/souji-preservation-evidence.py:113-116` (and the token prose at 119-120) still states the
pre-r16 taxonomy:

```
benign   (01,04,06,09,10,12,13,15,16): preharm pass, baseline FAIL, changed pass
refusal  (02,03,07,11,14,17,19):       preharm fail, baseline pass, changed pass
safety   (08):                         preharm fail, baseline FAIL, changed pass
preserve (05 pass / 18,20 fail preharm; all pass baseline + changed)
```

Implemented (323-357): benign adds `07,20`; refusal is only `02,11,17`; safety is
`03,08,14,18,19`; preserve is only `05`. Concretely the header says `03,07,14,19,20` PASS on the
harm baseline; the code requires them to FAIL (matrix `r14-harm` agrees with the code), and says
`20` fails preharm where the matrix records PASS. The token sentence is wrong the same way: `03`
and `14` are safety/degrade PASS rows that **must** carry a non-`none` token under
`CONFIG_TOKEN_IDS`, while the header files them under "every other PASS must carry
observed_finding=none". A reviewer or integrator trusting the header applies the wrong oracle.
Fix: replace 113-120 with the r16 tables and name `CONFIG_TOKEN_IDS` as the token set.

### F2 — MINOR — record-schema contract says "exactly", code normalizes one side only
`tools/souji-preservation-evidence.py:95-97` documents `cases[].detail`: "The declared multiset must
equal the parsed CASE multiset exactly." The implementation compares
`parsed_detail.replace("\t", " ") == declared_detail` (1388-1391) and normalizes only the **parsed**
side; writers normalize on write (`_arm`, 1849; `regenerate.py`; the external harness). Consequence:
a record whose `detail` is byte-identical to the transcript (`ok\tobserved_exit=0\tobserved_finding=none`)
is rejected `run-inconsistent`, while the space-rendered form passes. That is a faithful record by
the documented contract, and it is the shape the frozen README tells a human integrator to refresh
by hand. Fix: normalize the declared side too, or state the canonical single-space rendering in
95-97.

### F3 — MINOR (latent) — fixture metadata contradicts the observed harm arm for `R15CFG-19`
`tests/fixtures/r15-census-config.py:161-165` (`HARM_CASES`, described as "expected to FAIL under
the r14 harm tool from OBSERVED behavior") omits `R15CFG-19`, and `CASE_CLASSES` (168-176) labels it
`"refusal"` (which implies a harm PASS). Observed: `r14-harm` fails `19` with
`store: contract: synthetic store path in output … path-protected:credential-store` (the r14 refusal
echoes the store), which is why the checker's safety class is correct. `run-matrix.py` does not read
`harm_cases`/`case_classes` (grep empty), so nothing consumes the wrong table today; the fixture only
emits it in `--json` (1529, 1554-1555). Fix: add `19` to `HARM_CASES` and relabel or mark
`CASE_CLASSES` display-only.

### F4 — MINOR — frozen README describes a state that no longer exists
`tests/fixtures/r15-preservation-frozen/README.md:7-10` says the pins were authored pre-integration
and that evaluating the directory "correctly yields `snapshot_tampered` (exit 2) until the integrator
refreshes". At HEAD `expected.json` pins the live bytes exactly (verified above) and the record was
measured at `c6207bd`; the README was last touched in `b410186`, i.e. r16 regenerated
`record.json`/`expected.json` without updating the hand-off text. Fix: rewrite 7-10 to the r16
regenerated state (`regenerate.py --rev`, verdict `clean`).

### F5 — NIT — `duplicate-id` comment names the wrong mechanism
`tools/souji-preservation-evidence.py:2136-2138` says the duplicate "shows as declared/parsed
disagreement". With first-wins on both sets there is no declared/parsed disagreement; the two
`run-inconsistent` entries are the `stdout_sha256` and `stdout_bytes_total` mutations. Fix the
comment (or make it true by adding a real detail-disagreement control, below).

## Residual risk and verification gaps

- I did **not** run `--frozen` or the 8-check external fixture (`tests/fixtures/r15-preservation-evidence.py`);
  they are outside this item's ALLOWED-EXEC. The "8/8" and "frozen clean" claims in the handoff are
  therefore unverified by me. Static re-derivation says the frozen record satisfies `_eval_arm`
  (statuses, normalized details, summaries, token set, reason tokens, length bound, exit codes),
  `_check_bindings` (pins equal live bytes, `changed.tool.commit == measured_commit`), and the
  pinned literals; only the runtime byte re-measure path is unexercised.
- No selftest mutates only a declared `detail` to a non-whitespace value, so `details_equal`'s
  mismatch branch has **no negative control** (pre-existing, not deleted). Smallest addition: flip
  one changed row's declared detail and expect exactly one `run-inconsistent`.
- `case-finding-mismatch` checks token *presence*, not token identity. A consistent swap of the
  token text in both `stdout` and `cases` still evaluates clean. That is inherent to
  declared-consistency admission, but the token strings are not semantically pinned.
- Process note: four text scratch files were written under `/tmp` (not
  `/var/tmp/souji-r16-RerunCheckerSelftest-4/`) during name extraction; they were removed. No lane
  file other than this report was written.

## Commands

```bash
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-preservation-evidence.py --selftest; echo "EXIT=$?"
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff b410186 HEAD --stat -- tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-frozen/ ; echo ---; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff b410186 HEAD -- tools/souji-preservation-evidence.py
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-preservation-evidence.py; wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "CONFIG_\(BENIGN\|REFUSAL\|SAFETY\|PRESERVE\|HARM_FAILS\|TOKEN\)\w*\|CONFIG_IDS\|NAMESPACE_IDS" tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "CASE_LINE_RE\|def _parse_transcript\|RECORD_PREFIXES\|unparseable\|malformed" tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -m py_compile tools/souji-preservation-evidence.py && echo COMPILE-OK; git show b410186:tools/souji-preservation-evidence.py | grep -n "CASE_LINE_RE\|TOOL_LINE_RE\|SUMMARY_LINE_RE"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -A1 'cases\.append(($' tools/souji-preservation-evidence.py | grep -o '"[a-z0-9-]*",$' | sort > /tmp/h.txt; grep -c . /tmp/h.txt; git show b410186:tools/souji-preservation-evidence.py | grep -n -A1 'cases\.append(($' | grep -o '"[a-z0-9-]*",$' | sort > /tmp/b.txt; grep -c . /tmp/b.txt; diff /tmp/b.txt /tmp/h.txt && echo IDENTICAL-NAMES
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'cases.append(("' tools/souji-preservation-evidence.py | wc -l; git show b410186:tools/souji-preservation-evidence.py | grep -c 'cases.append(("'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'cases.append\|CASES\b\|SELFTEST_CASES' tools/souji-preservation-evidence.py | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1960,1990p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "HEAD: $(grep -c 'cases\.append(($' tools/souji-preservation-evidence.py)"; echo "b410186: $(git show b410186:tools/souji-preservation-evidence.py | grep -c 'cases\.append(($')"; echo ---; grep -n -A1 'cases\.append(($' tools/souji-preservation-evidence.py | sed -n '1,24p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la census/round-16/ 2>/dev/null | head -30; echo ---; ls tests/fixtures/r15-preservation-frozen/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'run-inconsistent\|case-duplicate\|case-finding-mismatch\|known record shape\|transcript-' tools/souji-preservation-evidence.py | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '/# duplicate CASE row in the transcript/,/structured-disagree/p' <(git show b410186:tools/souji-preservation-evidence.py) | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '\bdetail\b' tools/souji-preservation-evidence.py | sed -n '/^19[0-9][0-9]:\|^2[0-5][0-9][0-9]:/p' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'observed_finding\|R15CFG-0[0-9]\|R15CFG-1[0-9]' tests/fixtures/r15-census-config.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '\bREFUSAL\b\|\bBENIGN\b\|\bNS_IDS\b' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'frozen' tools/souji-preservation-evidence.py | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '\["detail"\]\|detail.*=.*record\|detail_map' tools/souji-preservation-evidence.py | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c $'\t' tests/fixtures/r15-preservation-frozen/record.json; grep -o 'observed_finding=[a-z:-]*' tests/fixtures/r15-preservation-frozen/record.json | sort | uniq -c; echo ---; git show b410186:tests/fixtures/r15-preservation-frozen/expected.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && cat tests/fixtures/r15-preservation-frozen/expected.json; echo ---; sha256sum tests/fixtures/r15-preservation-frozen/record.json tests/fixtures/r15-census-config.py tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && cat tests/fixtures/r15-preservation-frozen/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'refusal\|benign\|preserve\|safety' tools/souji-preservation-evidence.py | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'HARM_CASES\|CASE_CLASSES' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'harm_cases\|case_classes\|"class"\|\[.class.\]' census/round-16/run-matrix.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -A10 'def _good_statuses\|def _bad_statuses' tools/souji-preservation-evidence.py; echo ---; git log --oneline -2 -- tests/fixtures/r15-preservation-frozen/README.md; echo ---; git log --oneline -2 -- tools/souji-preservation-evidence.py; echo ---; git diff HEAD --stat -- tests/fixtures/r15-preservation-frozen/ tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -B2 -A6 'must equal the parsed CASE multiset exactly' tools/souji-preservation-evidence.py; echo ---; grep -n 'details_equal\|details\b' tools/souji-preservation-evidence.py | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'replace("\\\\t"\|replace("\\t"\|must equal the parsed CASE multiset exactly\|declared multiset' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "b410186 record tabs: $(git show b410186:tests/fixtures/r15-preservation-frozen/record.json | grep -c $'\t')"; echo "HEAD record measured_commit: $(grep -o '"measured_commit": "[0-9a-f]*"' tests/fixtures/r15-preservation-frozen/record.json)"; echo "HEAD rev: $(git rev-parse HEAD)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-preservation-evidence.py; git diff a6ec7810 163158a7 --stat -- tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-frozen/ tests/fixtures/r15-preservation-evidence.py tests/fixtures/r15-census-config.py; echo "RC=$?"; git log --oneline -3
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff a6ec781 163158a --stat -- census/round-16/ .ufo/waves/round-16/w2/ | tail -8
rm -f /tmp/h.txt /tmp/b.txt /tmp/bn.txt /tmp/hn.txt; ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2/ 2>&1 | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'snapshot_tampered\|pre-integration\|authored before' tests/fixtures/r15-preservation-frozen/README.md; echo ---; grep -n 'r16: with TAB\|first (token-bearing)' tools/souji-preservation-evidence.py; echo ---; grep -n 'A refusal PASS' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -A6 'REASON_TOKENS' tools/souji-preservation-evidence.py | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'def _check_bindings' -A40 tools/souji-preservation-evidence.py | grep -n 'PREHARM_SHA256\|BASELINE_SHA256\|measured_commit\|tool' | head -20
```

Read-only JSON queries against `c1-matrix-final.json`, `c1-matrix-landing.json`,
`tests/fixtures/r15-preservation-frozen/record.json`, and `expected.json` were issued through the
`read` tool (`?q=<jq>`), not the shell.

STATUS: ok
