# SwarmMutationTester39 — C2 counter mutation test (souji r32 w1)

## Status
STATUS: PASS — all 8 assigned mutants of `census/round-32/c2-counter.py` killed (2 by the committed do-nothing control row, 2 by a scratch reconstruction of the committed C2-junk control, 4 by built scratch states); **no survivors**. Pristine baseline reproduced the frozen `C2-do-nothing` row exactly; lane counter bytes untouched (sha256 identical before/after). One provenance finding on the committed C2-junk control (F3).

## Evidence

Harness baseline — pristine counter, full set, do-nothing rev (lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`, `--rev` = prereg `3ec84fc81b3243429c834a051880b0bcde06291c`):

```
python3 -B c2-pristine.py --root <scratch-clone> --rev 3ec84fc8… --base 85b61a1… --list-rev 3ec84fc8…
SUMMARY items=27 pass=1 fail=26 rev=3ec84fc81b3243429c834a051880b0bcde06291c
```
Byte-identical to the frozen row `SUMMARY items=27 pass=1 fail=26 rev=3ec84fc8…` (census/round-32/records/controls.tsv:2). Per-item: T03 is the lone passer (base `rc1:W0`, read-only invocation — work rule vacuous); 23 items fail `regress work-dropped`, T15/T29/T30 fail `regress` only. All 26 failing items have `rc1 != rc0` and `s1 != s0`.

Detector runs: each mutant = one-point edit of a scratch copy of the counter (`ff03f9ad61d88261b349abb91c801fd481109c74b8c3522e955fea478db3512b`), run with the same argv on an exposing state; pristine verdict on the same state from the runs above.

| # | Mutant (edit @ census/round-32/c2-counter.py) | sha256 (mutant copy) | Exposing state (`--rev`, `--only`) | Pristine | Mutant | Verdict |
|---|---|---|---|---|---|---|
| M1 | :173 `run("rev", argv, False)` — sandbox dropped | `89d54f23…18683def` | committed do-nothing rev `3ec84fc8…`, full set | `items=27 pass=1 fail=26` | `items=27 pass=27 fail=0` | KILLED — committed do-nothing row |
| M2 | :154-155 keep only `--ro-bind /var/tmp` | `478c2cff…efeba475` | committed row does **not** kill (T15/T29/T30 still `fail=3`); built P2 `3a0b03ed…`, `--only T05` | `FAIL` (sbox `rc1`, `OSError … Read-only file system`) | `items=1 pass=1 fail=0` (sbox `rc0:W2`) | KILLED — built state |
| M3 | :174-175 `ok_a = rc1 == rc0`, `ok_b = True` | `772c2300…00ceb026` | committed row does **not** kill (all 26 have rc mismatch); built junk `987280a9…`, `--only T01,T05` | `items=2 pass=0 fail=2 partial=1` | `items=2 pass=2 fail=0 partial=1` | KILLED — junk-row reconstruction |
| M4 | :174-175 `ok_a = s1 == s0 and s0 != "NONE"`, `ok_b = True` | `c5a3c3ca…d0dd1adf` | committed row: no item has `s1==s0` with rc mismatch; built P4 `a3c719b4…`, `--only T05` | `FAIL` (base `rc0` → sbox `rc1`, same anchor `selftest=9/9`) | `items=1 pass=1 fail=0` | KILLED — built state |
| M5 | :175 `ok_b = True` — work rule dropped | `10ef1db3…51034e18379be4` | committed row: no `work-dropped`-only item; built junk `987280a9…`, `--only T01,T05` | `items=2 pass=0 fail=2 partial=1` | `items=2 pass=2 fail=0 partial=1` | KILLED — junk-row reconstruction |
| M6 | :84 drop `int(m.group(3)) < 0` filter — failed syscalls counted | `2420d7d8…d6806b2` | committed row: no flip; built P6 `1b85ae8f…`, `--only T05` | `FAIL` (base `W1`, sbox `W0`, `work-dropped`) | `items=1 pass=1 fail=0` (sbox `W1` = 1 failed mkdir) | KILLED — built state |
| M7 | :173 `run("base", argv, True)` — SBOX at `--base` | `42731b97…b33633e2b` | committed row: no flip (item files identical in base and rev trees); built fix `01f1b260…`, `--only T05` | `PASS` (base `rc0:W20`, sbox `rc0:W21`) | `items=1 pass=0 fail=1` (sbox `rc1`, EROFS) | KILLED — built state (rejects a good state; `fail=0` unreachable under it) |
| M8 | :64 insert `text = re.sub(r"\d", "", text)` | `e8c60d65…9bf55e0b` | committed do-nothing rev `3ec84fc8…`, full set | `items=27 pass=1 fail=26` | `items=27 pass=0 fail=27` (every `S=NONE`) | KILLED — committed do-nothing row |

**Survivors: none.**

Built scratch states (commits on branches of the scratch clone of the lane, origin removed; stub sources for replay):

- **J (junk, `987280a9bc40f98416987e6c9a98389bc570966f`, at base + stubs):** `tools/souji-landing-gate.py` → `print("SELFTEST pass=65 fail=0")`; `tools/souji-gate-check.py` → `print("selftest=9/9")` — the anchors are T01/T05's base `S` from the baseline run; stubs exit 0, zero creations. Pristine run reproduces the frozen C2-junk shape: `ITEM T01 FAIL … work-dropped`, `ITEM T05 FAIL … work-dropped`, `SUMMARY items=2 pass=0 fail=2 partial=1` (controls.tsv:6 reads `SUMMARY items=2 pass=0 fail=2 partial=1`).
- **P2 (`3a0b03ed…`):** `tools/souji-gate-check.py` → `tempfile.mkdtemp(prefix="souji-gate-check-", dir="/tmp")` + one `open(...,"w")`, then `print("selftest=9/9")` — a /tmp-writer the committed set lacks.
- **P4 (`a3c719b4…`):** prints `selftest=9/9`, then `mkdtemp(dir="/var/tmp")`; on `OSError` prints digit-less `scratch blocked` to stderr and `exit(1)`.
- **P6 (`1b85ae8f…`):** `mkdtemp(dir="/var/tmp")` inside `try/except OSError: pass`, then `print("selftest=9/9")` — swallows the blocked write, keeps rc and anchor.
- **F (fix, `01f1b260…`):** real `tools/souji-gate-check.py:231` `dir="/var/tmp"` → `tempfile.mkdtemp(prefix="souji-gate-check-")` (TMPDIR honoured); pristine certifies it (`items=1 pass=1 fail=0`).

Restoration: mutants were separate copies; the pristine copy and the lane file were never edited. After all runs, pristine spot-check at the do-nothing rev reproduced the baseline verdicts exactly (`ITEM T01 FAIL … regress work-dropped`, `ITEM T05 FAIL …`, `SUMMARY items=2 pass=0 fail=2 partial=1`), and `sha256sum` of the lane counter still prints `ff03f9ad61d88261b349abb91c801fd481109c74b8c3522e955fea478db3512b` (same as before the experiments). Lane HEAD untouched at `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`.

## Findings
1. **No counter hole found.** Every pass-rule component is load-bearing: sandbox bind set (M1, M2), exit-code equality (M4), last-line equality (M3), successful-creation ratio (M5, M6), and digit-bearing normalization (M8). Killing M6 required a tool that swallows `EROFS` and keeps its anchor — the `result >= 0` filter is what makes "did the work" meaningful under the sandbox.
2. **The two committed C2 controls are necessary but not sufficient:** the do-nothing row alone kills only M1 and M8; M2/M3/M4/M5/M6/M7 reproduce the frozen rows on both committed control states and are exposed only by targeted states (built here). The counter's real strength is the per-item base-vs-sbox comparison, which the SUMMARY-level frozen rows do not pin down.
3. **Control provenance gap:** the C2-junk control rev `bf984f0cef06b18884450a97ad0a8a7b6728f65d` is not an object in the lane repo (`git cat-file -t` → `could not get object info`; `rev-parse --verify …^{commit}` → `Needed a single revision`), so the committed row `SUMMARY items=2 pass=0 fail=2 partial=1 rev=bf984f0c…` (census/round-32/records/controls.tsv:6) cannot be re-verified from the lane. A reconstruction at `987280a9…` reproduces its exact shape, so the row's reading is credible — but the frozen junk state itself is unreplayable. Not a counter-gameability issue; the do-nothing control (the one that pins the C2 base reading) is replayable and reproduces exactly.
4. **M7 is invisible to both committed controls by construction:** at the do-nothing rev the enumerated item files are byte-identical in the base and rev trees (the prereg commit adds only `census/round-32/*`), so SBOX-at-base and SBOX-at-rev cannot differ there. Any future amendment that wants the controls to catch a rev/rev-mix-up needs a control state whose rev changes an item file.
5. **M2 is invisible to the committed do-nothing control because no enumerated item writes a literal `/tmp` scratch root:** every enumerated file hard-codes `/var/tmp` (e.g. `tools/souji-gate-check.py:231` `base = tempfile.mkdtemp(prefix="souji-gate-check-", dir="/var/tmp")`) or honours TMPDIR (`tools/souji-verify.sh:1164` `ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-verify-selftest.XXXXXX")` — TMPDIR is always set by the counter). The `/tmp` and `/dev/shm` ro-binds are therefore untested by the committed controls; built state P2 covers `/tmp` (nothing covers `/dev/shm` — no item touches it).
6. T03's base run creates nothing (`W0=0`), so the work rule is vacuous for it; its pass is rc+last-line only. Harmless (the tool is read-only in that mode) but worth knowing when reading `pass=1` in the do-nothing row.
7. No tool installs or upgrades were needed (bwrap 0.13.1, strace, git, python3 3.14.8 already present; pacman untouched).

## Attack log
Attacks on the C2 counter (this seat's item): 8 one-point mutants + 5 cheat/fix states, all reproduced above. Every mutant either (a) certified a state the pristine counter rejects — M1 (`pass=27 fail=0` on the do-nothing rev), M2/M4/M6 (PASS on built cheats), M3/M5 (PASS on no-work stubs) — or (b) rejected a state the pristine counter certifies — M7 (FAIL on the TMPDIR fix), M8 (FAIL on everything). All 8 killed; no gameable path found. The one weakness surfaced is controls-provenance (Finding 3), not counter logic.

## Deliveries
- `.ufo/waves/round-32/w1/SwarmMutationTester39.md` — this report.
- Scratch `/fast/scratch/hyaku/souji-r32/MutateC2Counter/` (clone, mutants, cheat branches, run dirs) removed after this report was written; cheat-state stub sources and commit shas are embedded above for replay.
