STATUS: DONE — landed pointer code read at tip 5efb519; five proposed deletions/simplifications (≈18 lines, three inert predicates, one redundant `git cat-file` per run) proven output-inert against every pointer selftest and `r18-landing-pointers` case, plus one candidate withdrawn with its counterexample; five calibration findings recorded, nothing edited.

# Attacked claim

C2 calibration, pointer half: `tools/souji-landing-gate.py` emits `LG-DANGLING-PTR` / `LG-DANGLING-PTR-EXEMPT-STALE` at `--round ≥ 18`; exemptions are `corpus/pointer-exemptions.tsv`; `--fleet-root` classifies fleet-only citations; at b576341 round 18 → 10 findings (`census/round-18/gate-pointers-before-b576341.json`), at 5efb519 → 0; selftest 33 → 53; `tests/fixtures/r18-landing-pointers.py` 11/0; r17 pinned replays all match (`census/round-18/gate-replays-r18.json`).

Verdict on the claim's **structure**: holds, with caveats F1–F3 below. Verdict on the claim's **numbers** as far as a read-only seat can check: 10-finding record and 11 fixture cases verified directly; 33 → 53 selftest cases re-derived by static counting and matches on both bytes sets (below); tip 0 is fleet-root-conditional (F1). The gate itself was **not run** — this item carries no `ALLOWED-EXEC`, so every "no output change" below is a control-flow proof, not a measurement.

# Method and limits

- No `lsp` device/server is mounted in this seat (inventory: read/bash/edit/eval/glob/grep/task/wait/web_search/write + REA devices). Caller proofs are therefore **textual** (`grep -c` over the exact file plus the five named consumers), the literal fallback, not semantic references.
- Read-only only: `git show`/`cat-file`/`ls-tree` on named paths, `stat`, `sha256sum`, `grep` on exact named files. Scratch copy at `/var/tmp/souji-r18w2-SimplifyGatePointers/`; no lane file touched except this report (and its `w2/` directory).
- Scratch copy is byte-identical to the reviewed artifact: `sha256sum gate.py` = `f8a2ebe7695e600959ebfcd060ba99b6558a2f1149cbdcff8ad01a1467f2d27a` = `gate.sha256` in `census/round-18/gate-replays-r18.json`.
- Tooling: nothing installed or upgraded this seat.

# Landed anchors (5efb519:tools/souji-landing-gate.py, 1989 lines)

- `POINTER_ROOTS` 122, `POINTER_PATH_RE` 124–129, `FINDING_IDS` 133–143.
- `_round_log_lines` 651–666; `_expand_braces` 669–679; `_expand_round_ranges` 682–697; `_trim_pointer_token` 700–707; `_normalize_pointer_path` 710–715; `_pointer_paths` 718–749; `_safe_pointer_path` 752–756; `_path_exists_in_tree` 759–760; `load_pointer_exemptions` 763–789; `check_pointers` 792–876.
- Measured-commit path: pin validation 510/518, `record_bytes` read 529, `record_sha256` block 528–558, second read 560, measured branch 559–635 (round-18 finding 590–605, compare loop 607–635), exemption test 596, measured hash compare 621.
- `evaluate` 886–1030 (pointer branch 973–994); `emit` 1032–1087; `main` 1941–1989.

# Deletion proposals (ranked; all preserve selftest + fixture results)

## P1 — withdrawn during analysis: the pointer-root guard, 743–747

First pass called this guard dead. Counterexample: the regex's path rest is `[^\s`"'()\[\]]+` (128), which admits `..`, so a token like `../corpus/../x` from a source under `corpus/lessons/` normalizes to `x` — safe but not root-prefixed. The guard skips it (743–747); without the guard `x` reaches the fleet/exemption/finding cascade (844–876). Every source dirname is `""` or under `corpus/` (803–820), so such tokens are constructible; none exists in the tests or the tip/b576341 docs. Keep it, and add a comment naming the case — as written it reads like dead code, which is exactly how this seat misread it first.

## P2 — delete `FINDING_IDS`, 133–143 (11 lines)

`grep -c FINDING_IDS gate.py` = 1 (the definition). The five consumers (`tests/fixtures/r18-landing-pointers.py`, `r16-landing-gate.py`, `r15-preservation-evidence.py`, `census/round-17/gate-replays.py`, `census/round-18/run-matrix.py`) never import the module; `gate-replays.py:113–124` reads the file as bytes and executes it as a subprocess. The id list remains pinned in the module docstring (lines 63–64) and as literals in the selftest (e.g. 1254–1385, 1484, 1495). Expected delta: −11 lines, zero behavioral surface.

## P3 — hoist the duplicated `record_bytes` read, 529 + 560 (1 redundant process per run)

Line 529 computes the record blob when `record_sha256` is present; line 560 recomputes the identical expression:

```python
        if record_bytes := (blob_by_oid(root, tree[record_repo]) if record_repo and record_repo in tree else None):
```

`blob_by_oid` is one `git cat-file blob` subprocess (`_git`, 177–190). Hoist one assignment before the `record_sha256` block and use `if record_bytes:` at 560 — same truthiness semantics (empty blob still skips the measured branch). Exactly one avoidable subprocess per gate run today: of the three `*-frozen/expected.json`, only `r15-preservation-frozen` contains `record_sha256` (grep counts 0/0/1). Tests that traverse the branch unchanged: selftest `clean-measured` (1523), `frozen-measured` (1668), `frozen-measured-absent` (1694), `measured-record-exemption` (1495); fixture has no record_sha256 case. Expected delta: net 0 lines, −1 `git cat-file` per evaluation, one fewer copy of a three-part expression.

## P4 — delete three provably inert predicates (0 lines, 3 dead tests)

- **674** `if len(choices) < 2 or any(...)`: reached only when `"," in match.group(1)` (671), and `str.split(",")` on a string containing a comma always yields ≥2 choices. Keep the empty-choice test. Covered by `brace-pointer-expansion` (1312) and fixture `brace-one-missing` (:231), neither of which can reach the dead conjunct.
- **721** `if not raw or ...`: `raw` is a `_trim_pointer_token` result of a token that begins with a root prefix; trimming removes only trailing punctuation, unbalanced `}`, and `:\d+` lists, so `raw` is never empty. Covered by every pointer case; nothing observes it.
- **776** `or not fields[0]`: an empty first field also fails `not fields[0].startswith(POINTER_ROOTS)` (779) and raises the same `EvalError` message. Covered by `pointer-bad-exemption-exit2` (1385) and fixture `malformed-exemption-exit2` (:272), both exit-2 only.

## P5 — single-pass `_round_log_lines`, 651–666 (16 → 11 lines)

Current: one pass finds the first heading whose round number equals `round_no`, a second pass finds the next heading **that carries any round number** (a heading without a round number does not close the section — `_round_heading_number` returns None for it). Equivalent single pass:

```python
def _round_log_lines(text, round_no):
    out = []
    inside = False
    for index, line in enumerate(text.splitlines(), 1):
        number = _round_heading_number(line)
        if inside and number is not None:
            break
        inside = inside or number == round_no
        if inside:
            out.append((index, line))
    return out
```

Same start (first matching heading, inclusive), same end (first subsequent round-numbered heading), same 1-based numbers, same behavior when the round is absent (`[]`) and when a round heading repeats (break). Covered by `pointer-log-round-section` (1353); live shape confirmed at `LOG.md:949` (`## 2026-10-20 — round 18 …`). Expected delta: −5 lines.

## P6 — inline the one-use wrapper `_path_exists_in_tree`, 759–760 + call 844 (−2 lines)

`_safe_pointer_path(path) and path.rstrip("/") in tree_paths` is used exactly once (844). Inlining is byte-equivalent for every pointer case (all of them call it). Low value; optional.

Total: ≈18 lines removed, 3 dead predicates, 1 redundant subprocess; no pinned assertion in the selftest or the fixture changes.

# Rejected deletions (would trade one axis for another)

- **Comma splitter, 727–741.** No fixture or selftest reaches a top-level comma list, and a grep of the tip and b576341 source docs finds none (`(census|tests|tools|corpus)/…,<alpha>`: no matches). Deleting it would keep tests green but turn a future `` `census/a.json,census/b.json` `` citation into one false dangling path — harms calibration for a 15-line win. Keep; budget a test instead.
- **Fleet fallback restriction to `../` paths, 849–864.** It is load-bearing and exercised: b576341's record lists `.ufo/waves/hyaku/jj-w1/reports/` as fleet with `source: corpus/knowledge/jj-colocation-receipts.md, line: 148` — a lane-relative citation. Selftest `pointer-fleet-only` (1425–1459) pins the same shape. Restricting would change the reproduced 10-finding record.
- **`_normalize_pointer_path` inline (710–715).** −5 lines but inlines a three-call expression at 742; readability loss with no behavioral gain.
- **`functools.lru_cache` on `blob_by_oid`.** Would save ~2 subprocesses/run (SKILL.md is read at 919 and again at 831; r15 record under P3) but is an addition, not a deletion, and caches across selftest repos are a new failure surface.

# Findings (calibration; not fixed — no edits)

## F1 — the tip zero is fleet-root-conditional; it is not reproducible from the lane alone

`corpus/knowledge/jj-colocation-receipts.md:148` cites `` `.ufo/waves/hyaku/jj-w1/reports/` ``. At 5efb519 that path is **absent** from the tree (`git cat-file -e 5efb519:.ufo/waves/hyaku/jj-w1/reports/` → ABSENT) and no exemption row matches it (tsv has 3 rows, none for it). The only code path that can keep the run at 0 is the fleet branch, gate.py:849–864, and `/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports` exists (`stat` → directory). So the claimed 0 requires `--fleet-root` plus that live directory; a lane-only invocation yields at least one `LG-DANGLING-PTR`. Smallest fix: record the exact argv (with fleet root) next to the 0 claim/record; no code change. The comment at 844–848 only justifies the `../` case, while the exercised entry is lane-relative — one sentence there would match the code and the b576341 record.

## F2 — measured exemption key ≠ the path the gate prints

`check_frozen_pins` suppresses on `record_repo` (record path) at 596–597, but the finding it suppresses is emitted with `exp_path` (599–603). Observed pair: `corpus/pointer-exemptions.tsv` row 3 names `tests/fixtures/r14-cache-frozen/record.json`; `census/round-18/gate-pointers-before-b576341.json` prints `"path": "tests/fixtures/r14-cache-frozen/expected.json"`. An operator exempting the printed path gets no suppression and a stale-exemption finding. Smallest fix (1 line): accept either key (`record_repo in exemptions or exp_path in exemptions`), or emit the record path in the detail.

## F3 — a malformed pin can be counted twice (latent)

An invalid pin value is reported `LG-FROZEN-PIN` at 510–517, but the measured loop then compares `sha256(blob) != pinned` unconditionally at 621, so a resolving `measured_commit` plus differing bytes emits `LG-FROZEN-PIN` **and** `LG-FROZEN-MEASURED` for one shape defect. No current fixture triggers it (all pins in r13/r14/r15 `expected.json` are 64-hex; r17 pinned replays therefore match). Smallest fix: `elif isinstance(pinned, str) and SHA256_RE.match(pinned) and sha256(blob) != pinned:` at 621.

## F4 — a trailing slash makes any existing file resolve (latent)

`_path_exists_in_tree` (760) strips `/` before the lookup, so `tools/souji-census.sh/` passes if the file exists. No test and no current citation; fixing it needs a dir/file distinction that `tree_paths` does not carry — report only.

## F5 — reading caution on "r17 pinned replays all match"

`census/round-17/gate-replays.py:292–320` computes `record["match"]` from per-replay `(id, path)` multisets and exit codes only; `expected.gate_sha256_match` is recorded separately and `false` in `census/round-18/gate-replays-r18.json` (the gate changed by design). The claim is true in that scope; it does not assert the r17-pinned gate bytes.

# Evidence commands (abridged; all run in the scratch seat)

```
$ sha256sum /var/tmp/souji-r18w2-SimplifyGatePointers/gate.py
f8a2ebe7695e600959ebfcd060ba99b6558a2f1149cbdcff8ad01a1467f2d27a
$ git show 5efb519:census/round-18/gate-replays-r18.json | grep sha256   # gate.sha256 == above

$ git cat-file -e 5efb519:census/round-17/gate-replays-ddb7347.json   -> ABSENT
$ git cat-file -e 5efb519:census/round-17/jj-receipts-ddb7347.txt    -> ABSENT
$ git cat-file -e 5efb519:tests/vault/vadv54-run/p/p6repo/.git       -> ABSENT
$ git cat-file -e 5efb519:census/operator-sweep-20261019            -> ABSENT
$ git cat-file -e 5efb519:.ufo/waves/hyaku/jj-w1/reports/           -> ABSENT
$ stat -c %F /home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports
directory
$ stat -c %F /home/vgpnk/Projects/shokunin/corpus -> No such file or directory

$ git show 5efb519:corpus/pointer-exemptions.tsv | wc -l   -> 3
$ for f in tests/fixtures/*-frozen/expected.json: grep -c record_sha256 -> 0, 0, 1 (r15)
$ git show b576341:census/round-18/... record: 10 findings, exit 2,
  fleet = [{.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md, corpus/README.md:217},
           {…JjAuditSouji.md, :217}, {.ufo/waves/hyaku/jj-w1/reports/, knowledge…:148}]

Selftest counts (static): tip 44 check() sites − 2 loop bodies + 3 + 2 = 47, plus
6 explicit increments (1412 ×2, 1461, 1546, 1891, 1921) = 53;
b576341: 27 sites − 2 + 3 + 2 = 30, plus 3 explicit (953, 1298, 1328) = 33.
Fixture: 10 `emit_case` (202/213/223/231/244/251/261/272/279/305) + `vacuity-stub` = 11.
```

# Verdict

- Claim holds structurally: ids, round gate, exemption file, fleet classification, measured exemption, and the 33→53 / 11-case numbers all reconcile with the landed bytes. The P2–P6 proposals are output-inert by control-flow proof; none was executed, so they remain proposals until the gate selftest (53/0) and `tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py` (11/0) are run once on the patched file.
- Claim should be tightened in three places: F1 (record the fleet-root argv behind the 0), F2 (exemption key must be the record path, not the printed expected.json), F3 (guard the measured compare against malformed pins). F4/F5 are review notes.
- Preserved contract: exact TSV rows/order, SUMMARY counters (including `checked_ptrs`/`ptr_exempt`/`ptr_fleet`), exit codes 0/1/2, exemption staleness, and the `--fleet-root` JSON `fleet` list.
- Smallest fix overall: P2 + P4 (≈11 lines, three dead predicates, zero behavioral risk), then P5 and P3; P6 optional. P1 stays with a comment naming the `..`-traversal case.
