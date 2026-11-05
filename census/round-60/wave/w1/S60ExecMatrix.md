# S60ExecMatrix — round-60 wave-1 seat report (C1 frozen matrix + runner)

Seat: S60ExecMatrix (leaf executor). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Assigned move: build the frozen C1 8-case fixture matrix (3 honest accept / 5 forgery refuse)
and its runner `c1-counter.py`, plus receipts `base-run.txt` and `new-run.txt`.
No production files were edited; no git/jj mutation anywhere except inside scratch fixture
repositories; no tool installs (python3 + git present; nothing installed, nothing upgraded).

## Delivered (absolute paths)

- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecMatrix/build-matrix.py
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecMatrix/c1-counter.py
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecMatrix/c1-matrix.tsv
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecMatrix/matrix/&lt;case&gt;/{pre.txt,counter.py,pop.tsv,ctl*.txt,expected.txt} for the 8 cases (honest-2 carries two control receipts ctl-c1.txt/ctl-c2.txt and a two-block preregistration; every case dir ≤6 files)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecMatrix/matrix/stubs/{stub-accept.py,stub-refuse.py}
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecMatrix/base-run.txt
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecMatrix/new-run.txt

## What the matrix encodes

TSV header `case<TAB>expect<TAB>control_receipt<TAB>class`, exactly 8 data rows
(honest-1/2/3 accept, forgery-{kind-only,digest,rev-at-freeze,rev-missing,command-other} refuse).
Each case is a deterministic synthetic git repository: ancestor commit(s) carrying counter.py +
pop.tsv, then the freeze commit adding pre.txt + the control receipt(s). Honest receipts carry
`instrument=counter.py`, `instrument_sha256=<sha256 of the counter blob at freeze>`, `rev=<full40
strict ancestor>`, `command=python3 -B counter.py --selfcheck` (names the counter), one output
line, `EXIT=1`. Forgeries deviate in exactly one dimension each: kind-only has only `EXIT=1`;
digest states pop.tsv's digest; rev-at-freeze names the freeze commit itself (see limits);
rev-missing omits `rev=`; command-other names tools/souji-verify.sh. The base tool accepts all 8
(no substance checks); the substance arm must refuse the 5 forgeries and accept the 3 honest.

## Commands run and observed outputs (exit codes exact)

1. Builder (determinism self-verify rebuilds every case from the delivered bytes and compares
   pinned hashes; any mismatch aborts):
   `python3 -B .../S60ExecMatrix/build-matrix.py --out .../S60ExecMatrix --scratch /fast/scratch/hyaku/souji-r60/S60ExecMatrix/build`
   → exit 0; printed sha256 pins for all 43 fixture files (list below); rebuild checks passed.
2. base-run receipt (argv verbatim in base-run.txt):
   `python3 -B .../c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --matrix .../c1-matrix.tsv --base-tool-rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 --rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 --work /fast/scratch/hyaku/souji-r60/S60ExecMatrix/base-run-work --new-arm plain`
   → exit **1**; stdout: 8 `CASE` lines, every `base=accept new=accept`, then
   `SUMMARY matrix=8 forgeries_accepted=5 honest_accepted=3 stubs=REJECTED`. Matches the
   expected before-state: the base bytes accept all 5 forgery controls (EXIT=1 because the
   plain-arm verdicts mismatch the five refuse expectations). Lane HEAD at run time was exactly
   1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4, so base bytes == current tool bytes.
3. new-run receipt: measured against the S60ExecFreezeArm candidate
   `.ufo/waves/round-60/w1/S60ExecFreezeArm/souji-freeze-check.py`
   (sha256 928745cd7f294320e6a37551334f32f43eb409728169bb5d8606c8b7054cb24e, matching the
   sibling seat's landing claim), invoked with `--substance`:
   `python3 -B .../c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --matrix .../c1-matrix.tsv --base-tool-rev 1e8bfd87… --rev 1e8bfd87… --work /fast/scratch/hyaku/souji-r60/S60ExecMatrix/new-run-work --new-tool .../S60ExecFreezeArm/souji-freeze-check.py`
   → exit **0**; stdout: 3 honest cases `new=accept`, 5 forgery cases `new=refuse` (all equal
   expect), then `SUMMARY matrix=8 forgeries_accepted=5 honest_accepted=3 stubs=REJECTED`.
   Before the candidate landed, an interim fallback run against the current lane tool (which has
   no `--substance` arm) produced EXIT=2 could-not-evaluate with `new=error` rows; that interim
   receipt was superseded in place by the post-landing run above.
4. Direct tool-level evidence on a rebuilt fixture:
   `python3 -B base-run-work/base-tool.py --root base-run-work/honest-1 --prereg pre.txt --rev 3659929681203a7d0e7346ca13db8aae01d6e4e6`
   → `SUMMARY claims=1 findings=0`, exit 0 (the fixture passes the real tool's full grammar).
   `git -C base-run-work/forgery-rev-at-freeze rev-parse freezemark^{commit}` →
   dc1f00d9a098e2cb424f7baeb3a456afb3284977 = the case's pinned freeze hash.

## Runner contract (as delivered)

`python3 -B c1-counter.py --root LANE --matrix c1-matrix.tsv --base-tool-rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 --rev FULL40 --work DIR [--new-tool PATH] [--new-arm substance|plain]`
prints one `CASE <name> expect= base= new=` per case in matrix order, then
`SUMMARY matrix=8 forgeries_accepted=<n> honest_accepted=<m> stubs=REJECTED|ACCEPTED`.
forgeries_accepted / honest_accepted count BASE-arm accepts over forgery / honest classes.
Verdicts: tool exit 0 = accept, 1 = refuse. Exit 0 iff every NEW verdict equals expect AND both
stubs fail the expectation check; 1 otherwise; 2 on could-not-evaluate: unresolved
--rev/--base-tool-rev, missing/malformed matrix (must be exactly 8 valid rows), missing or
volatile --work (must exist, be writable, and not resolve under /tmp or TMPDIR/TEMP/TMP),
fixture hash mismatch against expected.txt, missing fixture part (control receipt, stubs,
builder), or a BASE/NEW run exiting with neither 0 nor 1. `--new-arm plain` runs the new tool
without --substance (used by base-run because the base bytes predate the arm). Read-only on
--root (git object store only); writes only under --work. The runner imports build-matrix.py at
run time as the single source of the rebuild recipe — the two files ship together.

## Named limits and disclosures

1. **rev-at-freeze construction**: a commit tree cannot contain its own hash, so no fixture can
   literally bake `rev=<its own freeze commit hash>` at freeze. The case names the freeze commit
   through the lightweight tag `freezemark` on the freeze commit; the receipt carries
   `rev=freezemark`. The landed arm's semantics (confirmed by S60ExecFreezeArm): a non-full40
   `rev=` refuses CONTROL-REV-INVALID, and a resolvable non-strict-ancestor (including the
   freeze commit itself) refuses CONTROL-REV-NOT-BEFORE-FREEZE — measured refuse on this case
   either way; the runner binds the verdict, not the code.
2. **Substance binds bytes, not execution** (round-57 recorder doctrine): instrument_sha256 pins
   blob bytes; the counter is never run by the matrix or the runner.
3. **Stub semantics**: a stub exiting with something other than 0/1 counts as failing the
   expectation check (REJECTED), not could-not-evaluate; only BASE/NEW arm errors escalate to 2.
4. **Stability**: commit hashes are pinned by fixed identity (S60ExecMatrix Fixture), fixed date
   (2026-11-04T00:00:00+00:00), fixed message "fixture", mode 0644, gpgsign off, sanitized
   GIT_* environment. The runner re-verifies rebuilt ancestor/freeze hashes against each case's
   expected.txt before measuring and exits 2 on any drift (tamper evidence).
5. **new-run identity**: the receipt measures the sibling's candidate bytes at
   `.ufo/waves/round-60/w1/S60ExecFreezeArm/souji-freeze-check.py` (sha256
   928745cd7f294320e6a37551334f32f43eb409728169bb5d8606c8b7054cb24e), NOT the landed lane tool.
   After integrating the arm into tools/, the L1 can reproduce with the lane tool (from the lane
   root, persistent scratch):
   `python3 -B .ufo/waves/round-60/w1/S60ExecMatrix/c1-counter.py --root . --matrix .ufo/waves/round-60/w1/S60ExecMatrix/c1-matrix.tsv --base-tool-rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 --rev <landed full40> --work <persistent-scratch>/new-run-work --new-tool tools/souji-freeze-check.py`
   Expected: all 8 new= verdicts equal expect, `stubs=REJECTED`, exit 0.
6. Coordination: S60ExecFreezeArm confirmed the arm's receipt semantics (column-0 key lines,
   first occurrence wins; instrument= must equal the declared Counter path; instrument_sha256=
   must equal the Counter blob's sha256 at freeze; command= must contain the Counter path;
   rev= full40-or-refuse) — all satisfied by the frozen matrix as built; the measurement above
   is the joint result.

## sha256 pins (frozen fixture bytes as delivered)

- pin build-matrix.py 7ea29c3b004b6c03a2e867f70e2eeca5cd211899321085762e0aabe36fc576e2
- pin c1-counter.py 96ec711aa48359248c0ee4e7b9392e0e10f39a232fb526191635834b7e54b715
- pin c1-matrix.tsv 7973d52030f9bf7d34867c2a46527708556cf82765c1e5b4a5f087bcb310132d
- pin matrix/forgery-command-other/counter.py ec07e0ce4345532c8635ed6074aecf4f93633a381e6aaf72deac8d35572d4f58
- pin matrix/forgery-command-other/ctl.txt 9cc719fef80015c3d67aa1b487cddf5a3521d29a1e5a52cdf3af6634dbf74a74
- pin matrix/forgery-command-other/expected.txt 3898d31d7de2f256cdbb07373bff5bea47053b9310b43c010b47618df014aed3
- pin matrix/forgery-command-other/pop.tsv 514c822bda6672916458f0147c1f2b428cfe7f1347de4ba7769d82e8dbd2626e
- pin matrix/forgery-command-other/pre.txt 034a4ba6cd4fe003d8c59529fae160c000d4625b77b0de0f9a209cd3d7c2c78e
- pin matrix/forgery-digest/counter.py ec07e0ce4345532c8635ed6074aecf4f93633a381e6aaf72deac8d35572d4f58
- pin matrix/forgery-digest/ctl.txt 5cf1dd10d4f6ffe9bcd928cb58ca51c06b27a0edd6482e95b20ae6b896e6b69f
- pin matrix/forgery-digest/expected.txt 98e64b33a44115ea4ae77e6c2e4872ad34b7b9da08c2cb9a43f12f5a549fa7d5
- pin matrix/forgery-digest/pop.tsv 514c822bda6672916458f0147c1f2b428cfe7f1347de4ba7769d82e8dbd2626e
- pin matrix/forgery-digest/pre.txt 034a4ba6cd4fe003d8c59529fae160c000d4625b77b0de0f9a209cd3d7c2c78e
- pin matrix/forgery-kind-only/counter.py ec07e0ce4345532c8635ed6074aecf4f93633a381e6aaf72deac8d35572d4f58
- pin matrix/forgery-kind-only/ctl.txt 4bf4fca02e6eeaf7f1c510b82c756e7f8a3c567a230bae1094b254adc774f38b
- pin matrix/forgery-kind-only/expected.txt d3dcc858903b55130c015c4e03129fc6dcea57b4888074805a2b85013cfadad9
- pin matrix/forgery-kind-only/pop.tsv 514c822bda6672916458f0147c1f2b428cfe7f1347de4ba7769d82e8dbd2626e
- pin matrix/forgery-kind-only/pre.txt 034a4ba6cd4fe003d8c59529fae160c000d4625b77b0de0f9a209cd3d7c2c78e
- pin matrix/forgery-rev-at-freeze/counter.py ec07e0ce4345532c8635ed6074aecf4f93633a381e6aaf72deac8d35572d4f58
- pin matrix/forgery-rev-at-freeze/ctl.txt 6f2c981a47328b18d0c8b3275f1e22ba0b516dc7f741e7889b5e8c3c4757025c
- pin matrix/forgery-rev-at-freeze/expected.txt deae7a6efd4795c850951c8a9bd7f8057c145884012357cbec3a0e4effa980fa
- pin matrix/forgery-rev-at-freeze/pop.tsv 514c822bda6672916458f0147c1f2b428cfe7f1347de4ba7769d82e8dbd2626e
- pin matrix/forgery-rev-at-freeze/pre.txt 034a4ba6cd4fe003d8c59529fae160c000d4625b77b0de0f9a209cd3d7c2c78e
- pin matrix/forgery-rev-missing/counter.py ec07e0ce4345532c8635ed6074aecf4f93633a381e6aaf72deac8d35572d4f58
- pin matrix/forgery-rev-missing/ctl.txt 70df2f86c0f9ddbb17fc242f75fa9eef6c20eb62684b7ec38f667214f4b5c17f
- pin matrix/forgery-rev-missing/expected.txt ca29496197e980864ec675bf97d4db98fa7d64b4a0556613fe548d7971c733d4
- pin matrix/forgery-rev-missing/pop.tsv 514c822bda6672916458f0147c1f2b428cfe7f1347de4ba7769d82e8dbd2626e
- pin matrix/forgery-rev-missing/pre.txt 034a4ba6cd4fe003d8c59529fae160c000d4625b77b0de0f9a209cd3d7c2c78e
- pin matrix/honest-1/counter.py ec07e0ce4345532c8635ed6074aecf4f93633a381e6aaf72deac8d35572d4f58
- pin matrix/honest-1/ctl.txt c0bdee5c509bf58f04e496b78ec9612b1bdcad4eb67135ab385fad12da16f1fd
- pin matrix/honest-1/expected.txt 2d6c3d0bcb656ed69026ddea2d10c310b59eedec03fda746167345532f875d26
- pin matrix/honest-1/pop.tsv 514c822bda6672916458f0147c1f2b428cfe7f1347de4ba7769d82e8dbd2626e
- pin matrix/honest-1/pre.txt 034a4ba6cd4fe003d8c59529fae160c000d4625b77b0de0f9a209cd3d7c2c78e
- pin matrix/honest-2/counter.py ec07e0ce4345532c8635ed6074aecf4f93633a381e6aaf72deac8d35572d4f58
- pin matrix/honest-2/ctl-c1.txt c0bdee5c509bf58f04e496b78ec9612b1bdcad4eb67135ab385fad12da16f1fd
- pin matrix/honest-2/ctl-c2.txt 78cc626293af90791ddf572529b3d3ba1eddf7713c2afd26fedb84c6b7f3423e
- pin matrix/honest-2/expected.txt bda637c413cc675cb783185422103582f65d621a8d8e52e54e3b491aa8b8b895
- pin matrix/honest-2/pop.tsv 514c822bda6672916458f0147c1f2b428cfe7f1347de4ba7769d82e8dbd2626e
- pin matrix/honest-2/pre.txt 601bf8f8e48757f7774d4af75d01c401e80abb5d116c12a20fb6b56e3b1b4a2e
- pin matrix/honest-3/counter.py ec07e0ce4345532c8635ed6074aecf4f93633a381e6aaf72deac8d35572d4f58
- pin matrix/honest-3/ctl.txt c012bc5305b033b5de612bc86ecfaaa8b80c4b5a4c96fb6437465c7d654731e1
- pin matrix/honest-3/expected.txt f453befa1a8644a9d93dedd0c53dd9a619ed20d16108bb801217455fbdb6cfb7
- pin matrix/honest-3/pop.tsv 514c822bda6672916458f0147c1f2b428cfe7f1347de4ba7769d82e8dbd2626e
- pin matrix/honest-3/pre.txt 6f3754aff819919b5bee65dd53da01edaa6baa2d18c869cd10a0ed2893fb25de
- pin matrix/stubs/stub-accept.py 9e21b46d4af8af2fde1de7374fe9f21e55c7fcd329dee78c5ebe1e8312eff23a
- pin matrix/stubs/stub-refuse.py 5852d5201d880efa67eb648e4e7fe2236b3ea3e2776afb5a298f13afcf1901b7

(base-run.txt / new-run.txt are receipts, not pinned inputs. Pinned case commit hashes live in
each case's expected.txt: honest-1 ancestor 14ab27ee557cddce1c2735a7ed1e5a960d6ec342, freeze
3659929681203a7d0e7346ca13db8aae01d6e4e6; forgery-rev-at-freeze freeze
dc1f00d9a098e2cb424f7baeb3a456afb3284977, tagged freezemark.)
