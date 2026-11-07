# S76ExecC1 — C1 reproduction (round 76, seat S76ExecC1)

Commands (lane root /home/vgpnk/Projects/shokunin/souji-shokunin; S=/fast/scratch/hyaku/souji-r76/S76ExecC1):
- Gate dirs: `git show e827d2bf:tools/souji-pre-report-gate.sh > $S/gw/...` (+writer from same rev); similarly ee59aa4d→$S/gb, K-b variant→$S/gkb, K-c variant→$S/gkc, gate-only→$S/gfc2.
- `python3 -B census/round-76/c1-evade-counter.py --gate-dir $S/gw --work $S/c1w2` via `tools/souji-receipt-write.py --rev e827d2bf --instrument census/round-76/c1-evade-counter.py --out .ufo/waves/round-76/w1/S76ExecC1/r/rep-c1w.txt --allow-dirty -- ...` (base/K-b/K-c arms at --rev 6c9c2a8e since counter absent at ee59aa4d; writer refuses otherwise).
- r36: `python3 -B tests/fixtures/r36-report-gate.py --work $S/r36 --gate $S/gw/souji-pre-report-gate.sh` (receipt-wrapped same rev); r27: `bash tests/fixtures/r27-pre-report-gate.sh` (TMPDIR=$S/r27).
- Domain trial: `bash tools/souji-pre-report-gate.sh --lane <abs> --branch master --report <abs prereg> --prereg <abs prereg>` (also rec.sh-wrapped); attribution via `git ls-files -o -i --exclude-standard -z | git -c core.excludesFile=/dev/null check-ignore -v -z --stdin`.
- Fail-closed: gate-only $S/gfc2, counter run direct.

Verdicts:
1. W gate REPRODUCED — `SUMMARY rows=30 mismatches=0 errors=0`, rc=0, EXIT=0 (rep-c1w.txt); ROW lines identical to records/c1-after.txt:44-45. Wall 4.32s. sha256 gate=18587bd2ff103f8ee136a3b6e59e96039f3202e06c688a8ecb7c8f4bf76623ad, writer=70bbf1c2..., counter=618e4f9a..., pop=937e4a9b... all match frozen binds.
2. Lane-base gate REPRODUCED — `SUMMARY rows=30 mismatches=4 errors=0` EXIT=1 (rep-c1b.txt); mismatches = f7,f9,f10,f14 (expect=FAIL clean=PASS), identical ROW lines to controls/c1-K-a-do-nothing.txt:48-49.
3. K-b REPRODUCED — mismatches=4 [f2 f6 f11 f12] EXIT=1; variant sha256 36f06903... = `# gate` line in c1-K-b-blanket-ignored.txt:9.
4. K-c REPRODUCED — mismatches=1 [f11] EXIT=1; variant sha256 43ebc213... = `# gate` line in c1-K-c-naive-untracked-gitignore.txt:9.
5. Regressions REPRODUCED — r36 `SUMMARY cases=21 pass=21 fail=0`, r27 `cases=4 pass=4`, both EXIT=0 (rep-r36.txt, rep-r27.txt); rows match records/c1-regress-r36.txt:31, c1-regress-r27.txt:17.
6. Domain trial MISMATCH (environmental, not C1) — check-tip=PASS, check-report=PASS, check-shonen=FAIL (found 0 `## SHONEN` headings in preregistration.txt — prereg has no SHONEN heading; gate expects one in --report), check-clean=PASS, check-prereg=PASS, EXIT=1 (domain-trial.txt). check-clean=PASS is the C1-relevant line: no RECEIPT-UNTRACKED-UNDECLARED-IGNORE. Wall 5.07s, RSS 50872 kB.
7. Ignored attribution: 26349 paths (`ls-files -o -i`); via check-ignore -v: 26338 via tracked `.gitignore` (covers .jj/, .ruff_cache/, .ufo/waves/), 9 via tests/vault/vadv-49/.gitignore, 6 via tests/vault/case-V6/.gitignore, 2 via fixture .scratch/.gitignore — all tracked. Zero untracked-source. Seat files (9 paths incl. this report) correctly ignored via tracked .gitignore:4-5 `.jj/`/`.ruff_cache/` and `.ufo/waves/` rule.
8. Fail-closed REPRODUCED — gate-only dir: `C1-COUNTER-FATAL: gate dir incomplete: .../gfc2` rc=2 (check-fc3.txt). Expected-PASS rows never reach a PASS verdict without the writer.

Findings: LOW — receipt-writer `--rev` must be a rev containing the instrument; base-rev base-gate arms need --rev 6c9c2a8e (P) though gate bytes are ee59aa4d's (verified sha256 ef3b04e4...). LOW — `git status --porcelain` empty this run (all seat files ignored), so clean-PASS not confounded. No HIGH/MEDIUM found; no mismatch on any frozen C1 number.

Files written: .ufo/waves/round-76/w1/S76ExecC1.md (this file), .ufo/waves/round-76/w1/S76ExecC1/r/{rep-c1w,rep-c1b,rep-c1kb,rep-c1kc,rep-r36,rep-r27,domain-trial,check-c1w,check-r36,check-r27,check-fc3}.txt. Tools: none installed (python3 3.14, git 2.56.0, /usr/bin/time present).
