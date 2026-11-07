# S79Scribe — r79 corpus drafts (SOURCES S325/S326, gate-signal knowledge, QUALITY Q142/Q143)

Verdicts — all PASS unless stated
1. S325 row: verified from installed bytes. `/usr/share/info/bash.info.gz` sha256 `cde1a336…` equals capture `census/round-79/srcs/bash.info.gz-5.3`; the node capture is byte-identical to `gunzip -c … | sed -n '3243,3290p'` (diff -q clean); quote "it will not execute the trap until the / command completes. If Bash is waiting for an asynchronous command via / the ‘wait’ builtin" at decompressed 3281-3283 (22 words), async-ignore clause at 3262; bash 5.3.20-1; 11 cells, no `|` in any cell.
2. S326 row: re-fetched `https://raw.githubusercontent.com/coreutils/coreutils/v9.12/src/timeout.c` → http=200 bytes=21183, sha256 `bf1f0d99…`, `cmp` identical to the capture; line 567 "/* Ensure we're in our own group so all subprocesses can be killed." with setpgid at 572 and cleanup() at 204 (send_sig(0, sig) at 246); host `pacman -Q coreutils` = 9.12-2.
3. Knowledge draft: 54 lines (≤60), cites S325/S326 only, no `.ufo/waves` path.
4. Q142/Q143 drafts: 5 columns each, as Q140/Q141; every count in the test cells re-read from receipts (K-a 10/10, K-b 10/10, K-c 10/10; harness 9/9, ablations 2/1/1/1).
5. sources-census validate: EXIT=0; last line `file ok /fast/…/val/corpus/SOURCES.md`; only pre-existing W04 warnings, none for S325/S326.

Falsification — own runs from committed bytes
- C1 at W1 (gate+writer via `git show c8c3fbca:…`, gate blob `ae5022c5…`): `SUMMARY rows=11 mismatches=0 errors=0 orphans=0`, all 11 match=yes incl. `s4-int-ls-remote … rc=130`; launched without `&` (setsid for session isolation) with dispositions reset by `env --default-signal=INT,QUIT,HUP`; reproduces the L1's foreground claim.
- C2 harness with `census/round-79/c2-pointer-counter.py` (sha `f597909b…`): `SUMMARY rows=9 mismatches=0 accepted=0 errors=0`, EXIT=0.
- C2 regressions: r78 `items=22 resolved=22` + `forged=12 matched=12 accepted=0`; r77 `items=35 resolved=35` + `forged=7 matched=7 accepted=0`; both EXIT=0.
- C1 regressions at the same gate: r78 17/17, r77 16/16, r76 30/30, r36 `cases=21 pass=21 fail=0`, r27 `cases=4 pass=4`; all EXIT=0.
- Frozen digests at P: c1 counter `0d0ec67c…`, c1 population `8a34f772…` (11 rows), c2 harness `5d5bd236…`, c2 false rows `7c108820…` (9 rows); base gate blob `5f5cb865…`.

Commands
- `sha256sum /usr/share/info/bash.info.gz census/round-79/srcs/bash.info.gz-5.3 census/round-79/srcs/coreutils-timeout.c-v9.12`
- `gunzip -c census/round-79/srcs/bash.info.gz-5.3 | sed -n '3243,3290p' | diff - census/round-79/srcs/bash.info-5.3-Signals.txt`
- `curl -sS -o timeout-refetch.c -w 'http=%{http_code} bytes=%{size_download}\n' <S326 url>`
- `setsid -w /usr/bin/timeout -k 5 300 /usr/bin/python3 -B census/round-79/c1-signal-counter.py --gate-dir $S/c1-gate --work $S/c1`
- `setsid -w /usr/bin/timeout -k 5 240 /usr/bin/python3 -B census/round-79/c2-false-row-harness.py --counter census/round-79/c2-pointer-counter.py --lane /home/vgpnk/Projects/shokunin/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin --work $S/c2`
- `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file $S/val/corpus/SOURCES.md --today 2026-11-07` (EXIT=0)

Findings
- MEDIUM (confirmed, inherited instrument defect): rows s3/s4 are labelled `ls-remote` but block at check 0's `git … config … --file <rowdir>/…` (`tools/souji-pre-report-gate.sh`:120-122) because the shim matches the pattern anywhere in argv (`census/round-79/c1-signal-counter.py`:62-64) and the row dir names contain `ls-remote`; in my run s3/s4 `gate.out` carry no `check-gitsource` line while s2's does. The kill rule is still exercised on a git child; label and surface are wrong (routed r80 M1).
- LOW (method): `tests/fixtures/r36-report-gate.py` mkdtemps under `--work`, so that parent must already exist; a missing dir is a FileNotFoundError, not a row result (my first r36 run; the receipt was replaced by the passing rerun). No tool installed or upgraded this seat; disk-guard showed /fast/scratch 49% used, 412.7G free.

Files written under `.ufo/waves/round-79/w1/S79Scribe/`: skeleton.md, sources-rows.md, knowledge-gate-signal-handling.md, quality-rows.md, census-validate.txt, c1-run.txt, c2-run.txt, c2-regress-r78.txt, c2-regress-r77.txt, c1-regress-r78.txt, c1-regress-r77.txt, c1-regress-r76.txt, c1-regress-r36.txt, c1-regress-r27.txt.
