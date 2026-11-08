# S82Connector — round-82 cross-claim separation, sibling-overlap, carried-list scan

Seat: S82Connector (connector). Read-only. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Scratch: `/fast/scratch/hyaku/souji-r82/S82Connector` (removed at end).

## 0. Frozen claims re-derived from committed bytes (all reproduce)

| frozen predicate | my re-run | verdict |
|---|---|---|
| C1 harness 32 rows, candidate `census/round-82/c1-pointer-counter.py` | `SUMMARY rows=32 mismatches=0 accepted=0 refused_true=0 errors=0` EXIT=0 | HOLDS |
| C1 r78 regression | `items=22 resolved=22` + `forged=12 matched=12 accepted=0` | HOLDS |
| C1 r77 regression | `items=35 resolved=35` + `forged=7 matched=7 accepted=0` | HOLDS |
| C2 16 rows, default launch | `SUMMARY rows=16 mismatches=0 errors=0 orphans=0` EXIT=0 | HOLDS |
| C2 16 rows, `env SHELLOPTS=monitor` | `SUMMARY rows=16 mismatches=0 errors=0 orphans=0` EXIT=0 | HOLDS |
| C2 selftest (committed lane file) | `selftest: 57 checks, 0 failed` EXIT=0 | HOLDS |
| probe D successor | `SUMMARY arms=6 failed=0` EXIT=0 | HOLDS |
| controls C1 K-a/K-b/K-c red 2/2/2; C2 K-a 4/4, K-b 12/12, K-c 1 | receipts re-read, red | HOLDS |

Commands (all from lane root, scratch `<S>` = `/fast/scratch/hyaku/souji-r82/S82Connector`):
`python3 -B census/round-82/c1-false-row-harness.py --counter census/round-82/c1-pointer-counter.py --lane <lane> --fleet-root /home/vgpnk/Projects/shokunin --work <S>/c1`
`python3 -B census/round-82/c1-pointer-counter.py --root <lane> --rev e65538e73c7f1a8f7570bc24a2215da8a90043f3 --fleet-root /home/vgpnk/Projects/shokunin --population census/round-{77,78}/c2-population.tsv --ledger census/round-{77,78}/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r7{7,8}.tsv`
`git show 73110f6f…:tools/souji-vault-verify.sh > <S>/souji-vault-verify.sh` (sha256 `556ad94abc7341107716e30295e41c0981f980ef83263afe46ca60ba9010c032` = the receipt's bind digest) then
`python3 -B census/round-82/c2-vault-signal-counter.py --tool <S>/souji-vault-verify.sh --work <S>/c2` and the same under `env SHELLOPTS=monitor`.
`TMPDIR=<S>/st bash tools/souji-vault-verify.sh --selftest`; `python3 -B census/round-82/probes/tmpdir-in-vault.py --tool <S>/souji-vault-verify.sh --work <S>/pd3`.

## 1. Causal separation — verdict **SEPARABLE**

Byte-level, from the receipts' own `# bind` / `instrument=` lines and `strace -f -e trace=openat`:

| check | evidence | verdict |
|---|---|---|
| does a C1 receipt bind/read a vault-tool byte? | `records/c1-after.txt:7-8` binds only `c1-false-row-harness.py` + `c1-pointer-counter.py`; `c1-regress-r*.txt` bind only `c1-pointer-counter.py` | NO |
| does a C2 receipt bind/read a C1 counter byte? | `records/c2-after.txt:7-8` binds only `c2-vault-signal-counter.py` + `tools/souji-vault-verify.sh`; `c2-regress-r17.txt` binds `tests/fixtures/r17-jj-receipts.sh` | NO |
| runtime: does the C1 counter open any vault-tool file? | `strace` of `c1-pointer-counter.py --rev e65538e…`: `grep -c souji-vault-verify` → **0** | NO |
| runtime: does the C2 counter open any C1 instrument? | `strace` of `c2-vault-signal-counter.py`: `grep -c c1-pointer-counter` → **0**, `c1-false-row` → **0**; the only lane opens are `census/round-82/c2-population.tsv` + `c2-vault-signal-counter.py` | NO |
| source-level cross-reference? | `grep -n 'souji-vault-verify\|round-82' census/round-82/c1-pointer-counter.py census/round-82/c1-false-row-harness.py` → none; `grep -n 'c1-' census/round-82/c2-vault-signal-counter.py` → none; `grep -n 'round-82' tools/souji-vault-verify.sh` → none | NO |
| **would C1 verify with W2 absent?** | lane clone at W1 `f5bc4197` (tool blob = pre-W2 `51847933…`): harness → `rows=32 mismatches=0 accepted=0 refused_true=0 errors=0` EXIT=0. Ref-free variant (all refs deleted) → same, EXIT=0 | YES |
| **would C2 verify with W1 absent?** | lane clone at F3 `1ec433c6` (no `census/round-82/c1-pointer-counter.py` present): counter under `env SHELLOPTS=monitor` → `rows=16 mismatches=0 errors=0 orphans=0` EXIT=0 | YES |

The only residual coupling is the lane's **git history**, not its bytes: the C1 counter's ABSENT rule runs `git log --all -- <token>` (counter `:411`), so a lane commit that creates an ABSENT-class token path flips that item to REFUSED. Reproducer (read-only probe clone): committing `corpus/knowledge/absentdir` → `ITEM P02 … status=REFUSED … why=present in lane history`, r77 drops to `resolved=30 refused=5`; committing `.ufo/waves/round-16/build` → `ITEM L04 … REFUSED`, r78 drops to `resolved=18 refused=4`. **No r82 commit touches any of the 9 ABSENT-class token paths** (checked against P/F/F2/F3/W1/W2/A/w1-spec), so this channel is inert for round 82 — but it is a live coupling of the C1 regression conjuncts to *future* lane commits, and it is what the r80/r81 counters inherited.

## 2. Sibling overlap — documented, 8 rows (tools/ scope, ≤15 cap)

Scan: `$(` … `timeout` … `)` in `*/tools/**` of every other `*-shokunin` lane; exposure = does the file install a TERM/INT/HUP trap that could reap the CLI subtree.

| lane | file:line | exposed |
|---|---|---|
| kaidoku | `tools/round-39/c1-run.sh:258` | yes |
| kaidoku | `tools/round-40/c1-run.sh:449` | yes |
| kaidoku | `tools/round-41/c1-run.sh:450` | yes |
| kaidoku | `tools/round-42/c1-run.sh:716` | yes |
| kaidoku | `tools/round-50/c1-run.sh:699` | yes |
| kaidoku | `tools/round-67/c1-run.sh:699` | yes |
| tameshi | `tools/mutate-and-run.sh:923-924` | no (inside a quoted `<<'EOT'` mutation-spec heredoc, not executed shell) |

Shape is identical to the C2 defect: `rea_ver=$(timeout 120 npx -y "$rea_pin" --version …)` — an external CLI under `timeout` inside `$( )` with **no** signal trap (the only trap in each kaidoku file is `EXIT` for scratch cleanup). Reproducer of the mechanism (`<S>/expo/probe2.sh`): host runs `out=$(timeout 300 cli.sh)`; `cli.sh` starts `sleep 600 &` then `exec sleep 600`. After `kill -TERM <host pid>`: **survivors=1** (the grandchild stays alive in the CLI's own group). The r82 fix (`tools/souji-vault-verify.sh:229-241 cli_kill_tree`) is exactly what closes this shape in souji. Documented only — no sibling file was modified.

## 3. Carried list (V1) — which are touchable read-only

Preregistration `census/round-82/preregistration.txt:115-118` names 9 carried items. Re-measurable read-only now (pointer + status):

| carried item | file:line | touchable r82? |
|---|---|---|
| `_regular` pathspec framing | `census/round-82/c1-pointer-counter.py:223-235` (byte-identical to r81 `:223`); used at `:251` | yes — read-only |
| quarantine intro-blob digest site | `tools/souji-quarantine.sh:459` (`git log --diff-filter=A` → intro commit), `:487` (`cat-file blob "$intro:$REL" \| timeout --kill-after=10 120 sha256sum`) | yes — read-only site; no frozen row |
| fork-tail row | `census/round-80/records/wave-w1/seats/S80MutTool.md:28`; lesson `corpus/lessons/round-80.md:163` | left to r83 (needs a new probe) |
| r79 gate re-measurement | `corpus/lessons/round-79-verifier-spotcheck.md:73,103` | left to r83 |
| check-4 300 s backstop row | `tools/souji-pre-report-gate.sh:227` (`gate_timeout=300`), comment `:35`; `corpus/QUALITY.md:354` | yes — site located; still no frozen row |
| r76 K03/K04 | `corpus/lessons/round-76.md:93,111` | left to r83 |
| status-trusting lane tools | `tools/souji-verify.sh:550,594` (prereg's own pointers), `tools/souji-census.sh` | yes — read-only |
| r17 240 s runners | `tests/fixtures/r17-jj-receipts.sh:257,266,277,966-967,986-987,1031` | yes — read-only |
| r82's own C2 `$(timeout …)` fallback (no trap) | `tools/souji-vault-verify.sh:300` — the no-private-file branch runs the CLI in the foreground with **no** trap armed | see finding F4 |

## Findings

**F1 — MEDIUM — the K-b control is not a distinct mutant; it is the r81 counter byte-for-byte.**
`census/round-82/controls/variants/c1-K-b-owntree-dropped.py` vs `census/round-81/c1-pointer-counter.py`: `diff` → **2 lines, both the module docstring**; code identical. Re-running both against the 32 rows gives byte-identical ROW output (`diff` of the two receipts' ROW lines → empty) and identical `SUMMARY rows=32 mismatches=2 accepted=2 refused_true=0 errors=0` EXIT=1. So K-b is a re-run of K-a under a new filename: the round has **two** distinct C1 controls (K-a, K-c), not three, and the mutant that would isolate the round's *own* new rule (owntree dropped, PF-1 kept) is absent. Its own docstring also claims "red by accepted=3" while its receipt says `accepted=2` (`census/round-82/controls/c1-K-b-owntree-dropped.txt` last lines).
*Reproducer:* `python3 -B census/round-82/c1-false-row-harness.py --counter <K-b> --lane <lane> --fleet-root /home/vgpnk/Projects/shokunin --work <fresh>` vs the same with `--counter census/round-81/c1-pointer-counter.py`.

**F2 — MEDIUM — the r82 counter's PF-1 branch is dead code: it changes no verdict on any frozen row or regression.**
The counter carries a second new branch (census/round-82/c1-pointer-counter.py:365-371, `census`-token + `census`-target → `_capture_ok`). Mutant with that branch replaced by `elif False:` → harness `SUMMARY rows=32 mismatches=0 accepted=0 refused_true=0 errors=0` **EXIT=0** (fully green) and r77/r78 regressions unchanged (`items=35 resolved=35 forged=7 matched=7`; `items=22 resolved=22 forged=12 matched=12`). So the "PF-1 full-suffix" rule the prereg names at `:37` (`preregistration.txt` C1 paragraph, "the suffix binding is the token's FULL path below its round-<N>") is **not** what keeps PF-1 (a *true* row, expect MOVED) or NF-I/NF-H (already refused by the r81 `_capture_ok` last-component-vs-full-path test). Only the **owntree** branch (`:353-357`) is load-bearing: mutant with the owntree branch disabled → `mismatches=2 accepted=2` on exactly NF-F and NF-G. Per-row diff of candidate vs r81 counter over all 32 rows: the two counters disagree on **NF-F and NF-G only**.
*Consequence:* the C1 claim "the successor counter refuses NF-F/NF-G and the M8-class NF-H" is true, but the *second* named rule (PF-1 full-suffix) buys nothing measurable, and the round's stated kill-list does not contain a mutant that would catch its removal. The `PF-1` population row (expect MOVED) is decided by the pre-existing `_capture_ok`, so the "shape-true" label does not discriminate either.

**F3 — LOW — the r81-counter K-a receipt is not what the prereg names, and the r82 K-a is a different instrument with a different population.**
`preregistration.txt` (C2 paragraph) says: "the frozen r81-counter K-a receipt `census/round-81/controls/c2-K-a-do-nothing.txt` is the earlier do-nothing red baseline (mismatches=8 orphans=8)". That file exists and does read `mismatches=8 orphans=8` — but it was produced by the **r81** counter over the **r81** 12-row population (`command=… census/round-81/c2-vault-signal-counter.py`, `instrument_sha256=075606340…`), not by the r82 instrument. The r82 receipt at `census/round-82/controls/c2-K-a-do-nothing.txt` is a *different* receipt (r82 counter, `d1a43e08…`, 16 rows, `mismatches=4 orphans=4`). Both numbers in the prereg are individually accurate; the sentence cross-references one receipt while the sentence's own numbers come from the other. Non-blocking, but the prereg's Control path for C2 was edited at F3 (`28fd32c0`→`1ec433c6`, dropping the trailing "(recorded under `env SHELLOPTS=monitor`…)" parenthetical) — the only prereg change after the freeze.

**F4 — LOW — the shipped tool keeps an un-trapped `$(timeout …)` CLI path (disclosed as a limit, but it is the same shape the sibling scan exposes).**
`tools/souji-vault-verify.sh:300`: `out=$(timeout "$CLI_TIMEOUT" "$bin" vault:hash "$vp" 2>/dev/null)` — the branch taken when `cli_tmp_ok` fails, i.e. exactly the "refused configuration" the prereg's C2 stated-limits paragraph *does* mention ("a signal in the refused configuration (cli_tmp_ok fails, TMPDIR under the vault) runs the foreground call as before, so a signal there leaves the CLI running"). The limit is disclosed; but it is the same `$(timeout …)`-with-no-trap shape the round's own sibling scan exposes (section 2), so it is a live residual of the C2 class rather than a closed surface. The prereg covers it as a limit, so this is documentation-grade, not a claim defect.

**F5 — LOW — M1 chronology: the prereg's own freeze-check re-run is `findings=3`, and one of the three is the disclosed slip.**
`census/round-82/records/freeze-check-at-P.txt` (run at rev `1ec433c6`, F3): `FINDING C0 FROZEN-EDITED … preregistration.txt differs between freeze and revision` + `C1/C2 CONTROL-ADDED-NOT-BEFORE-FREEZE` for both K-a receipts, `SUMMARY claims=2 findings=3`, EXIT=1. Re-running the checker at the real P (`1cb7c7d1`) gives `findings=2` with `C2 CONTROL-MISSING … (recorded under env SHELLOPTS=monitor, the launch that reproduces the leak) not present at freeze` — i.e. the parenthetical that F3 deleted was what made the C2 Control line unparseable as a path. That is the disclosed M1 (prereg landed in P alongside the controls). Not a claim defect; recorded so the round's own chronology numbers are not read as clean.

**F6 — LOW — the C2 counter's rows are strace-fragile; the A-receipt's 16/0/0 does not survive tracing.**
Running the frozen C2 command under `strace -f -e trace=openat` yields `mismatches=12 orphans=11` (default launch) — the tracing overhead pushes the tool past the counter's 5 s `SETTLE` (`census/round-82/c2-vault-signal-counter.py:55`). The untraced runs reproduce 16/0/0. So the C2 receipt is only reproducible untraced; a non-author who verifies with `strace` will see red and may misread it as a defect.

### Files written (this seat only)
`.ufo/waves/round-82/w1/S82Connector.md` (this file) and `.ufo/waves/round-82/w1/S82Connector/` (empty scratch dir created; removed at end of run).
No lane tracked file was created, edited, or deleted; no git mutation was performed in the lane or the fleet repo (read-only `show/log/diff/ls-files/rev-parse/cat-file` only); no commit, push, stash, reset, checkout, switch or pull. Fixture clones were made under my scratch with `git clone --shared --no-checkout` + `git checkout --detach` inside the clone only, with the toplevel asserted before use.
