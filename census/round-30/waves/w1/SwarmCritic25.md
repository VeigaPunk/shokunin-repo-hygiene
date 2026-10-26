# SwarmCritic25 — attack on C2 (operability), souji round 30 wave 1

## Status
STATUS: PASS — attack executed and scored in scratch; the frozen C2 instrument is falsified: a gate that reads nothing reproduces the frozen target SUMMARY byte-for-byte (`reports=86 cne=0 dangling=0 fixture=ok redarm=ok regress=same`, exit 0), so C2 as instrumented is not evidence for the claim. A stricter-only correction is listed; the target itself does not need to move.

## Evidence
Frozen contract opened: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/preregistration.txt:7` (C2 paragraph; target `reports=86 ...`), `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/c2-counter.py` (whole file), `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py` (discovery 326-540, pointers 738-1010, evaluate 1010-1140, CLI 2278-2326).

Lane base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` (branch master, HEAD at `df6afe8`), prereg `d4928ec`, controls `bae103c`. All scratch under `/fast/scratch/hyaku/souji-r30/AttackC2/`; clone `git clone -q --no-local` + `remote remove origin`, checked out at base, identity set with `git -C <scratch> config`. Receipt files copied to `.ufo/waves/round-30/w1/SwarmCritic25-*.txt`.

1. Cheat A — stub gate + byte-recognising fixture, commit `521cd5e3a275c916ffa870b12eae5b1e250638cd` (base + 4-line `--round 29` early return that prints a fixed SUMMARY; fixture reads the tool bytes and reports `CASE D1..D7 PASS` whenever the marker is present). Frozen counter, `--root <scratch clone> --base 9420341… --fleet-root /home/vgpnk/Projects/shokunin`:
   ```
   GATE rc=0 reports=86 cne=0 dangling=0 other=0
   FIXTURE rc=0 line='cases=7 pass=7 control=FALSE-GREEN-REJECTED' d1_d7_pass=True ok
   REDARM rc=1 line='cases=7 pass=0 control=FALSE-GREEN-REJECTED' ok
   REGRESS tools/souji-landing-gate.py base=(0, 'SELFTEST\tpass=65\tfail=0') rev=(0, 'SELFTEST\tpass=65\tfail=0') same
   REGRESS tests/fixtures/r16-landing-gate.py base=(0, 'SUMMARY\ttotal=15\tfailed=0') rev=(0, 'SUMMARY\ttotal=15\tfailed=0') same
   SUMMARY reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok regress=same rev=521cd5e3…
   EXIT=0
   ```
2. Cheat B — same commit, gate prints `checked_reports=1`, `68`, `999`: counter exit 0 each time (`reports=1|68|999`). The literal 86 is never bound.
3. Cheat C — commit `9fad74eadd702f2b51eb86645cb95bbcf6ef35ae` (same stub and fixture, **`census/round-29/waves` deleted**: `git ls-tree -r --name-only HEAD census/round-29/waves` = 0 rows). Counter exit 0 with the frozen target SUMMARY unchanged.
4. Narrowed-source gate (copy of `tools/souji-landing-gate.py@9420341`, pointer sources reduced to `corpus/QUALITY.md`): `--selftest` → `rc=1 SELFTEST pass=51 fail=14` (14 `CASE\tFAIL` lines, e.g. `dangling-skill-pointer`, `relative-pointer-normalization`, `relative-pointer-escape`). One cosmetic rewrite of the final print (`pass=passed+failed fail=0`, `return 0`) → `rc=0 SELFTEST pass=65 fail=0`, identical `(rc, last line)` to base.
5. Pointer mapping, synthetic repo `syn/repo` rev `4c71d8112ab0bf9f45e7117d4e809506b00d2abd`, `corpus/QUALITY.md:2` cites `.ufo/waves/round-29/w1/Ghost2.md`, never committed (`git ls-tree census` = 0 rows), present only in `--fleet-root`. Base gate: `LG-DANGLING-PTR .ufo/waves/round-29/w1/Ghost2.md`. Same gate with the two plausible C2 fixes (skip `%s`/`<N>` templates; resolve `.ufo/waves/round-N/` under `--fleet-root`): `findings=0`, rc 0.
6. Capture facts at base: `committed_md=86`, `committed_deliver_md=18`, `committed_seat_md=68`, `committed_entries=132`, `live_ufo_files=130`, `live_ufo_md=86`, `live_only_not_in_capture=0`, `capture_only=manifest.sha256 summary.tsv`; `census/round-29/waves` holds 0 `captured` paths (`census/round-26/waves` holds 131).
7. Control provenance: `git cat-file -t` fails for all five junk revisions in `records/controls.tsv` (`b148bf9b…`, `0067311…`, `84def39…`, `2adeb3c…`, `bfdeeea…`).
8. Scratch `/fast/scratch/hyaku/souji-r30/AttackC2/` (clone with `origin` removed, synthetic repo, patched gate copies) removed after the receipts above were copied out; no lane file was written (`git status --porcelain` shows only the pre-existing untracked `corpus/lessons/round-30.md`), no `git`/`jj` mutation in the lane.

## Findings
1. `reports` is self-reported, never anchored, never bound to 86. `census/round-30/c2-counter.py:86` is `m = re.search(r"checked_reports=(\d+)", out)` over the merged stdout+stderr, and `:118` is `return 0 if reports > 0 and cnef == 0 and dangling == 0 and fok and rok and same else 1`. Any value >0 passes; the 86 literal is only a text comparison a human makes. A gate printing no parseable count falls back to `reports=-1` and exit 1 (`SwarmCritic25-cheat-D-negone.txt`), so the defect is the unbound positive rule, not the fallback. Evidence: cheats A/B/C.
2. The two discriminating legs are lane-authored artifacts. `census/round-30/c2-counter.py:95-102` runs `tests/fixtures/r30-landing-gate-discovery.py@REV` given `--tool`, and accepts a last line plus 7 `CASE` lines the fixture itself prints. A fixture that recognises the base tool by its bytes passes FIXTURE and REDARM simultaneously (cheat A). Neither leg creates a repo the REV gate must evaluate.
3. REGRESS is a count, not a suite. `census/round-30/c2-counter.py:110-115` compares `(rc, last digit-bearing line)` only — `same = same and s1 == s2` (`:115`). The compared line is printed by `tools/souji-landing-gate.py:2269` — `print("SELFTEST\tpass=%d\tfail=%d" % (passed, failed))`. Narrowing pointer sources to `corpus/QUALITY.md` does break the run (51/14), but a one-line cosmetic rewrite restores the compared pair while 14 pointer cases fail — so a fix that stops checking SKILL.md/SHONEN.md/lessons/knowledge pointers is not detectable by the frozen leg (evidence 4).
4. The target literal `86` counts delivery artifacts as reports. At base, `census/round-29/waves` holds 86 `.md`: 68 seat-id reports and 18 `deliver-*.md`. A stricter discovery that counts seat reports only prints 68, exits 0, and is a kill-rule miss even though it is the more honest reading of "reports". Conversely a discovery that counts `deliver-*.md` (or any `.md`) is the one the target rewards. `.captured` paths do not exist under `round-29/waves` (0), so that sub-variant is inert for r29 only.
5. Capture-mapped resolution by live disk hides uncommitted evidence. `tools/souji-landing-gate.py:967` already resolves `.ufo/waves/hyaku/` pointers from `--fleet-root` on the filesystem — `elif path.startswith(".ufo/waves/hyaku/"):` — and the counter always passes the live fleet root. Extending that branch to `.ufo/waves/round-N/` (the obvious "capture-mapped pointer" fix) resolves every pointer from the gitignored live tree and never reads the capture; a pointer to a file the capture omitted is then `findings=0` (evidence 5). For round 29 the capture is currently complete (`live_only_not_in_capture=0`), so this is latent, not yet instantiated; Q61's `excluded.tsv` would be the file that makes it real, and a fleet-mapped gate would silently absolve it.
6. The counter's premise is false. Its docstring (`census/round-30/c2-counter.py:5-7`) claims execution from committed bytes — "the lane working tree is never read or written" (`:7`) — but `:84` runs the gate with `--root root` (the live lane), not the export `tr`. A gate that keeps reading `.ufo/waves/round-29/` on disk prints `reports=86` — the live `.md` count is also 86 (evidence 6) — so the target number cannot distinguish capture-reading from live-reading, and the C2 claim's own defect (r28 routed defect 3) survives the target unnoticed (cheat C).
7. Unreproducible controls. Every junk control revision is absent from the object store (`git cat-file -t` fatal), so `C2-junk(stub gate + fake fixture)` cannot be re-run; its recorded `redarm=fail regress=differs` is text, and cheat A shows the strongest cheat was not tried (same stub passes once the fixture recognises bytes and the selftest path is untouched).
8. `census/round-30/c2-counter.py:89` counts `LG-DANGLING-PTR-EXEMPT-STALE` as dangling (prefix match) and `:90` therefore drops it from `other`; the SUMMARY calls a stale exemption a dangling pointer.
9. Scratch discipline of the instrument: `census/round-30/c2-counter.py:70` defaults `--scratch` to the shared `…/souji-r30/c2-counter` rather than a per-seat dir, and `tools/souji-landing-gate.py:1022` and `:1339` hardcode `dir="/var/tmp"` for gate snapshots and the selftest, ignoring the `TMPDIR` the counter exports. No leftovers after my runs (`/var/tmp/souji-landing-gate*` = 0), but the frozen run writes outside `/fast/scratch`.

## Attack log
Counterexamples (scored, receipts in Deliveries):
- No-op gate + byte-recognising fixture ⇒ frozen target SUMMARY, exit 0 (A).
- Frozen target SUMMARY with `census/round-29/waves` deleted at REV (C).
- `reports` unbound: 1, 68, 999 all exit 0 (B).
- Pointer-source narrowing + one-line count rewrite ⇒ REGRESS identical while 14 selftest cases fail (4).
- Capture-mapped pointer to a never-committed file resolved via `--fleet-root` ⇒ `dangling=0` (5).
- Control revisions unreachable ⇒ junk control unreproducible (7).

Impacted axes: **operability (8)** only — C2 is the operability claim; the counter does not touch calibration or coverage, and I ran nothing against C1/C3 (`C2` is frozen not to move `--selftest`/r16 literals; the cosmetic experiment stayed in scratch and no lane file was edited). Impact: operability would be admitted and saturate at 8 on a test a no-op passes — premature saturation.

Verdict: fixable defect, not a tradeoff — the target literals stay, only the checks tighten. Smallest safe correction (stricter-only, L1-logged in `census/round-30/records/amendments.txt`):
1. `c2-counter.py:86`: anchor to the SUMMARY line (`^SUMMARY\t` … `checked_reports=(\d+)`, last match) and compute `expected` from committed bytes (`git ls-tree -r --name-only <rev> census/round-29/waves | grep -c '\.md$'`); fail unless `reports == expected`.
2. `c2-counter.py:84`: run the REV gate with `--root <export tr>`, and add one arm the counter owns: the same gate against a tree with `census/round-29/waves` removed must print `COULD-NOT-EVALUATE`. That single arm rejects stubs (cheat A/C), live-dir discovery (finding 6) and a fixture that self-declares.
3. `c2-counter.py:110-115`: compare full normalized `--selftest` / r16 stdout (scrub `<TMP>`, `/var/tmp`, hex) instead of `(rc, last line)`.
4. Optional accuracy: exclude `LG-DANGLING-PTR-EXEMPT-STALE` from `dangling` at `:89`.

Do not admit C2 on an unamended run of the frozen counter; do not relax the target.

## Deliveries
- `.ufo/waves/round-30/w1/SwarmCritic25.md`
- `.ufo/waves/round-30/w1/SwarmCritic25-cheat-A.txt`
- `.ufo/waves/round-30/w1/SwarmCritic25-cheat-B-reports-unbound.txt`
- `.ufo/waves/round-30/w1/SwarmCritic25-cheat-C-nocapture.txt`
- `.ufo/waves/round-30/w1/SwarmCritic25-cheat-D-negone.txt`
- `.ufo/waves/round-30/w1/SwarmCritic25-selftest-compare.txt`
- `.ufo/waves/round-30/w1/SwarmCritic25-pointer-hiding.txt`
- `.ufo/waves/round-30/w1/SwarmCritic25-capture-facts.txt`
