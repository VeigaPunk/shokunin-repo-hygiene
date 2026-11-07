# S75Reviewer — round-75 falsification review (52d3f07..5d10e09)

## Verdicts
- Change 1 (gate diff be599cbb..1ad737b, tools/souji-pre-report-gate.sh): SOUND (see F1, O1).
- Change 2 (census/round-75/c1-evade-counter.py): SOUND.
- Change 3 (census/round-75/c2-kill-counter.py): SOUND (see O2).
- Change 4 (prereg vs every receipt; freeze-check): all 17 receipts in census/round-75/{controls,records} consistent with preregistration.txt; freeze-check re-run `SUMMARY claims=2 findings=0` rc=0, no lane writes. One evidence-trail finding (F1).
- Frozen C1 claim: REPRODUCED (mismatches 2→0 on 25 rows, K-b stays red, domain trial check-clean=PASS).
- Frozen C2 claim: REPRODUCED (killed 4/6→6/6: X09 and P1=X15∘M17 killed, M08/M14/M15/M17 stay killed, pristine 64/64 PASS).

## Reproduced numbers (all re-derived by me; scratch /fast/scratch/hyaku/souji-r75/S75Reviewer, receipts preserved under .ufo/waves/round-75/w1/S75Reviewer/rec/)
- Instrument sha256 = prereg, exact: c1-evade-counter=9ed4a97b…, c1-population=85257260…, c2-kill-counter=fdb75c09…, c2-mutants=612e89e2….
- Probe evade-probe.py sha256=09e18d8a…; ROUTES=20 (probe :408-427) + 5 r75 builders = 25 rows; counter prints `# probe path=… sha256=09e18d8a…` in every receipt.
- Gate blobs: base=062b6d39…, candidate 1ad737b4=620ed97e… (same blob at A tip 5d10e09e — no amendment needed), K-b variant=e0d2e149….
- C1 K-a, base gate (mine): `SUMMARY rows=25 mismatches=2 errors=0`, mismatches exactly f-info-exclude + f5-info-exclude-dir, rc=1 — equals controls/c1-K-a-do-nothing.txt.
- C1 W, candidate gate (mine): `SUMMARY rows=25 mismatches=0 errors=0`, rc=0 — equals records/c1-after.txt.
- C1 K-b, blanket gate (mine): `SUMMARY rows=25 mismatches=3 errors=0` (f2, f6, f7), rc=1 — equals controls/c1-K-b-blanket-ignored.txt.
- C1 domain trial: lane HEAD=5d10e09e; standard-ignored=26032 paths, per-directory-ignored=26032, hidden_only=0, listings 0.07–0.09 s; faithful tip replica (clone at 5d10e09e + lane's real 26032 ignored files overlaid; replica hidden_only=0) → W gate prints check-tip/report/shonen/clean/prereg=PASS, rc=0, 8.27 s, 42 MB RSS. (Direct gate run on the live lane worktree FAILs check-clean on concurrent wave dirt — `M corpus/SOURCES.md`, `M corpus/knowledge/filter-filemode-witness.md`, `?? corpus/lessons/round-75.md` — environmental, fires before the new block.)
- C2 mutants rebuilt from source: all 8 apply-edit products byte-identical to committed variants (X09=0890321d…, X15=54573344…, P1=fc91b5b3… proving the X15→M17 order, M08=6ae083b8…, M14=f92429d2…, M15=0c355f3b…, M17=bdc86901…, r74-X09=a2e45c55…); sources match committed instruments (r75 counter=90a3c7b2…, r74 counter=e3fc47c2…).
- C2 my 9 selftest arms ≡ committed receipts: pristine 64/64 fail=0 EXIT=0; X09/P1/M08/M14 fail=1 EXIT=1; M15/M17 fail=2 EXIT=1; X15 64/64 EXIT=0 (survives, as the prereg predicts informationally); r74-X09 62/62 EXIT=0 (X09 independently confirmed alive on the r74 counter).
- C2 tallies (mine / committed re-run / do-nothing control re-run): `SUMMARY mutants=6 killed=6 survived=0 unread=0 pristine=PASS` rc=0, identical; do-nothing `killed=4 … survived=2` rc=1 with X09 and P1 SURVIVED — equals controls/c2-K-do-nothing-r74.txt; blanket control reads pristine=FAIL EXIT=1 — equals controls/c2-K-blanket-pristine-red.txt.
- Counter r74→r75 diff: docstring + two `r75 C2` selftest checks only (32 lines added, 1 docstring line replaced); no evaluate()/verdict change.
- EXPECT cross-checks enforced in code (population dict+length compare, route-set compare → rc=2 FATAL); probe build() commits the .gitignore before seeding, so f2/f6 "committed rule = declared policy" rulings stand on real bytes; fixture toplevel assertion present (probe build()).

## Findings
- F1 MEDIUM: the frozen C1 domain-trial predicate has no committed receipt in census/round-75/records/ (r74 kept census/round-74/records/c1-domain-trial.txt; r75 records/ has none at tip 5d10e09e). The claim itself reproduces (above); the evidence trail is missing at review time — L1 should commit census/round-75/records/c1-domain-trial.txt with the report.
- O1 LOW (attribution nuance, not a defect): f3-repo-excludesfile is refused at BASE already — the writer pins `-c core.excludesFile=<devnull>` on every git call (tools/souji-receipt-write.py:159-161), so its pinned status lists the file before the new block runs. The new ls-files block's marginal catch is the info/exclude surface (f-info-exclude, f5-info-exclude-dir). The prereg is honest about this (K-a lists exactly those 2 mismatches); observable verdicts unchanged.
- O2 LOW: c2-kill-counter.py never binds a --mutant receipt to the named mutant (no instrument=/instrument_sha256= cross-check); the mapping is caller-trusted. Round use is correct (each receipt's instrument= matches its variant blob); a swapped receipt is caught only if its SELFTEST/EXIT shape differs.

## Change-1 review detail (all verified)
- `lane` scope: argv-derived (`path, lane = sys.argv[1], sys.argv[2]`), absolute enforced by `[[ $lane = /* …]]`.
- `-I` isolation: block lives in the existing `python3 -I -B -` heredoc; `import subprocess` valid under -I.
- Env: run inherits the gate's scrubbed env (GIT_* unset at gate :5-12, LC_ALL=C, GIT_OPTIONAL_LOCKS=0) plus explicit `--no-optional-locks` and `-c core.fsmonitor=false` (deterministic listing; consistent with the writer's pinned status).
- PATH lookup of git: `["git", …]`; missing git → FileNotFoundError → heredoc nonzero → check clean FAIL (fail-closed).
- stderr=DEVNULL: only diagnostics lost; rc≠0 still fails closed (`ignored-file listing failed`).
- Raw-bytes `-z` set difference, `{b""}` stripped; count-only echo (D30 no-echo respected).
- 26k ignored files: 2×~0.1 s listings; honest lane unaffected (hidden_only=0); full gate 8.27 s on the replica (dominated by the pre-existing 19k-file truth hash).
- Exit wiring: `sys.exit(1)` inside the heredoc → `truth=$(…)` fails → `check clean FAIL` with 400-byte sanitized detail.

## Change-3 review detail (all verified)
- Two EXIT lines per receipt (counter's own + rec.sh's): parser reads the LAST line (rec.sh's), matching the frozen grammar "the receipt's last line is EXIT=1"; counter's own EXIT line is ignored but both agree in every receipt I checked (13 of mine + 17 committed).
- `fail` taken only when exactly one `^SELFTEST cases=…$` line exists; 0 or ≥2 → UNREAD (never a kill); trailing blanks stripped; non-EXIT last line → UNREAD. All paths conservative (fail-closed for the kill claim).

## Receipts audited (prereg vs bytes)
controls/c1-K-a-do-nothing.txt, c1-K-b-blanket-ignored.txt, c2-before-r74-{pristine,X09,X15,P1}-selftest.txt (rev=52d3f07 ✓, Q99 column-0 headers ✓), c2-K-do-nothing-r74.txt, c2-K-blanket-pristine-red.txt; records/c1-after.txt (rev=1ad737b, gate 620ed97e), c2-after.txt, c2-after-{pristine,X09,X15,P1,M08,M14,M15,M17}-selftest.txt (rev=1ad737b, instruments = committed variant blobs), census-before.txt (EXIT=0), freeze-check.txt. Zero prereg mismatches besides F1.

## Files written under my seat dir
- .ufo/waves/round-75/w1/S75Reviewer.md (this report)
- .ufo/waves/round-75/w1/S75Reviewer/base-gate.txt (base gate blob used for diffs)
- .ufo/waves/round-75/w1/S75Reviewer/rec/ (13 small receipts: myKa, myW, myKb, my-domain-trial, pristine, X09, X15, P1, M08, M14, M15, M17, r74X09)
Scratch /fast/scratch/hyaku/souji-r75/S75Reviewer removed. No tools installed (none needed).

## Verification gaps
- Live-lane gate run impossible while the wave holds worktree dirt; substituted with the byte-faithful tip replica plus a direct listing-difference proof on the real worktree.
- X15 informational survival verified from both committed receipt and my own run; not part of the frozen target.
