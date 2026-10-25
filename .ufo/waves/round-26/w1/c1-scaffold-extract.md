# C1 scaffold extract — verbatim payloads (DRAFT, not applied)
Source: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 89e0fceeefcf28db313c94120be6d25e03c60094:SCORECARD.md`
(254 lines; byte-identical to lane base `0eca7c8` — `git diff 0eca7c8 89e0fce -- SCORECARD.md` empty).
Extract command used: `sed -n '172,229p'`. Every byte below was copied from the `git show` stream
this run, not retyped. Fence length chosen because the payloads contain no triple backtick.

## Payload 1 — Round 24 measurements block (base lines 175-207, 33 lines)
Appends as the new round block. Contains the heading, the 6-column table header, the 5 claim rows
(base 179-183) and the limits paragraph (base 185-207).

```markdown
### Round 24 measurements (2026-10-25, lane base a65fac98964b445758e94c805728c9a19d302ff8)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 F2 debris census (write-safety fixture) | coverage 8 | at base the fixture and tool are absent (`git cat-file -e a65fac9:tests/fixtures/r24-size-census.py` fails), so `cases=0 pass=0` by the frozen definition; skip-the-work control (the case-8 stub as `--tool`, fixture bytes of `1efe406`): `cases=8 pass=4 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 1 — the stub fails cases 2 dangling, 3 garbage, 5 alternates, 6 refusal (`census/round-24/records/c1-control-stub.tsv`, `rev=1efe406e7f39b8fe736be2a566053703a571ffc0`) | `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 0 (`census/round-24/records/c1-after.tsv`, `rev=778747eb671f8e85ef5387bc3d7023337b30467c`); case 3 reads `garbage=1 size_garbage=2` on the main and the linked path, case 4 reads `garbage=0` while raw `git -C <linked> count-objects -v` reads `garbage: 1`, case 7 sees `fsck --lost-found` change the manifest | `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` | fixture `tests/fixtures/r24-size-census.py` sha256 `373ef1f0a02f8ca11fccd4ff32d8511c1eaaf3ede672c37ed11ef2b10968084f` (bound by both receipts); tool `tools/souji-size-census.py` at 778747e sha256 `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d` (not bound by the receipt; `git show 778747e:tools/souji-size-census.py \| sha256sum`) |
| C2 coverage-map agreement | calibration 7 | `grounded=4 mapped=2 dangling=0 mismatches=2`, rc 1, at base `a65fac9` with the tool bytes of `1efe406`: `count-objects-garbage-readings-r25.md` and `repo-size-census-readonly.md` were MISSING-FROM-MAP (named only in a status cell) (`census/round-24/records/c2-control-base.tsv`) | `grounded=6 mapped=6 dangling=0 mismatches=0`, rc 0 (`census/round-24/records/c2-after.tsv`, `rev=778747eb671f8e85ef5387bc3d7023337b30467c`); fixture `cases=9 pass=9 control=FALSE-GREEN-REJECTED` (`census/round-24/records/c2-fixture-after.tsv`); per-entry kill rule (amendment 1): all 4 base-grounded entries present at the tip with the same F<k> (`git diff a65fac9 778747e -- corpus/knowledge/` adds two `ground:` lines and removes none) | `python3 -B tools/souji-coverage-agreement.py --root . --rev <full40>`; `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` | tool `tools/souji-coverage-agreement.py` sha256 `71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897`; fixture sha256 `42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44` |
| C3 receipt verify/run symmetry | operability 8 | base runner (`tools/souji-receipt-run.py` sha256 `e13d0c83…`, identical at `a65fac9` and `1efe406`): `cases=8 pass=6 refusals=0/2 regress=5/5`, rc 1 — case a (non-durable rev, no-ref and `refs/jj/keep`-only) and case b (`tool=` not in argv) both `verify=ok` (`census/round-24/records/c3-control-base-runner.tsv`) | `cases=8 pass=8 refusals=2/2 regress=5/5`, rc 0 (`census/round-24/records/c3-after.tsv`, `rev=778747eb671f8e85ef5387bc3d7023337b30467c`): `RECEIPT-REV-NOT-DURABLE` for both case-a instances, `RECEIPT-TOOL-NOT-IN-ARGV` for the absent and substring-only labels, the five r23 receipts still `verify=ok` | `python3 -B tests/fixtures/r24-receipt-verify.py --tool tools/souji-receipt-run.py --lane-root .` | fixture sha256 `f8c4c391097ee9745b72cbf5eef51aec235a89946c22831d10a1db7badc708b2`; runner at 778747e sha256 `9df0738c…` (not bound by the receipt) |
| assimilation (rides inside C1; no claim slot) | coverage 8 | F2 grounded entries 2 (`ground: F2` lines at `a65fac9`); quarantine slice not yet checked | gate `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0` (`census/round-24/records/gate-check-r24-entry.tsv`); entry `corpus/knowledge/count-objects-linked-worktree-garbage.md` (S120–S123), 2 staged packages admitted (r27 re-sourced, r25 matrix only), 4 rejected; slice 7 accepted + 1 unverifiable (S118) | `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/count-objects-linked-worktree-garbage.md --snapshot-dir census/round-24/sources --slice census/round-24/records/quarantine-slice --slice-verdicts census/round-24/records/slice-verdicts.tsv` | gate tool sha256 `d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d`; snapshots `census/round-24/sources/*` (`sha256sum -c SHA256SUMS` 6/6) |
| r13 structure entry recheck (freshness; not a claim) | — | `git-repo-structure-readonly.md` verified on git 2.55.0 only, r16 note "pending recheck" | `selftest=PASS ids=5/5` on git 2.56.0 (`census/round-24/records/r13-recheck-receipt.tsv`) | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | fixture sha256 `b6bf52056d037b2251632b409be3d31852588480c392ddc50ca8f8dbf101179f` |

Each round-24 counter scored the amended (amendment 1, stricter-only, written before any control
or after receipt) bytes pinned above. Controls were committed in `ce5971c` before any after-data. A
disclosed deviation: the L1 ran sanity executions of the C2 tool and C3 fixture before the
amendment; those runs are not claim evidence. Named limits:

- **C1.** The no-write envelope is a `/var/tmp` fixture claim over 8 frozen cases on git 2.56.0.
  The manifest excludes atime/ctime, so a tool that restores directory mtimes after a write is
  invisible to it. The stderr contract (`census.warning=` lines, exit 1 on other stderr) and the
  not-a-repository exit 2 have no case. No case plants hostile config or environment: the tool
  carries `-c core.fsmonitor=false -c core.hooksPath=/dev/null` and a scrubbed env, but no counter
  exercises them. Cases 7 and 8 pass for any `--tool`.
- **C2.** C2 covers the 6 grounded entries out of 13 `.md` entries. The per-entry kill rule was
  checked by `git diff`, not by the tool. `mismatches=0` does not retire the stale
  "frontier, no entry" F2 row at `corpus/README.md:40`.
- **C3.** Argv membership binds the label to recorded text, not to the executed program. A tool
  named as an operand while another program runs still verifies. Of the 20 r23 residuals, C3
  closes 1 and narrows 6.

The lane-bound figure `census/round-24/size-census-lane.txt` (`garbage=0 size_garbage=0
unreachable=1093 alternates=0`, tool sha256 `09bb8e0d…`) describes this repository at the moment of
the run (jj keep refs plus a cruft pack). It is not a fleet figure and not a plain-clone figure. It
is a measurement file, not a v1 receipt: `verify` returns `RECEIPT-MALFORMED`. Registry 119 → 123
(S120–S123) is a grep count over committed bytes, not a receipt.
```

## Payload 2 — capability rows (base lines 213-214, 2 lines)
Appends at the END of `## Capabilities`, after the `record agreement audit (r23)` row (base 93).

```markdown
| debris census (r24) | read `count-objects -v` garbage / size-garbage / alternates against the resolved common git dir (so a linked worktree's private-gitdir `garbage: 1` is not reported) and count `fsck --unreachable --no-reflogs` lines, under a scrubbed environment with `core.fsmonitor=false` and `core.hooksPath=/dev/null`; refuse `--lost-found`, promisor/partialClone repositories (including a leftover `objects/pack/*.promisor`) and non-repositories with exit 2. The no-write envelope is a `/var/tmp` fixture claim over 8 frozen cases (manifest excludes atime/ctime); unreachable includes alternates when alternates>0; one lane-bound figure, no fleet figure, no deletion authority | `tools/souji-size-census.py`; `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` 8/8 `control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` (`census/round-24/records/c1-after.tsv`); stub control 4/8 (`c1-control-stub.tsv`); `corpus/knowledge/count-objects-linked-worktree-garbage.md`, S120–S123 | r24 |
| coverage-map agreement (r24) | at a full 40-hex revision, from committed bytes only, flag every `ground: F<k>` knowledge entry not named by a backticked `knowledge/<name>` in the entries column of a coverage-map row whose ground cell starts with F<k> (status-column mentions never map), and every backticked entries-column `knowledge/` path absent at that revision; its fixture fails the always-zero emitter on all nine cases. Scope: grounded entries only (6 of 13 at 778747e); the per-entry kill rule is not mechanized | `python3 -B tools/souji-coverage-agreement.py --root . --rev <full40>`; `census/round-24/records/c2-control-base.tsv` (2 at base), `c2-after.tsv` (0); `tests/fixtures/r24-coverage-agreement.py` 9/9 (`c2-fixture-after.tsv`) | r24 |
```

## Payload 3 — planned bullets (base lines 225-226, 2 lines)
Appends after base line 137 (the blank that closes `## Planned`), keeping the existing
`- **r24 — planned:**` line at base 134 intact.

```markdown
- **r24 (planned r23) — done, see `corpus/lessons/round-24.md`:** C1 F2 debris census with a `/var/tmp` write-safety fixture that refuses `--lost-found` (8/8), C2 coverage-map agreement (2 → 0 mismatches), C3 receipt verify/run symmetry (refusals 0/2 → 2/2, regress 5/5), as measured in the Round 24 table; one assimilated F2 entry (S120–S123), `git-repo-structure-readonly.md` re-verified on git 2.56.0. Of the planned "re-run the r23 counters": C3 case d re-verifies the five r23 receipts at the tip; the r23 record-agreement counter has no r24 receipt. Of "close the residual C1/C2 limits": 1 of 20 closed (verify durability), 6 narrowed, 12 open, 1 open by design (`.ufo/waves/round-24/w1/RevR23Residuals.md`). Certification OFF, K5 HELD.
- **r25 (planned r24):** (a) calibration: make C2's per-entry kill rule (base-grounded entry absent or re-grounded at tip) a tool row instead of a hand `git diff`; retire or mark superseded the stale F2 "frontier, no entry" row at `corpus/README.md:40`; turn `census/round-24/size-census-lane.txt` into a v1 receipt or relabel it; replace the r23 `tool_sha256=` grep counter with a count of `verify=ok` receipts; receipt the r23 record-agreement counter at the tip; carry the open r23 residuals R3, R7 (counts read from stderr), R15 (K1 decoy) and R17 (K1 trailing shadow). (b) coverage: put `tools/souji-repo-structure.sh` under the r24 common-dir manifest envelope, then the colocated/plain byte-comparison precondition (README `### Frontier (r24)`); add the untested C1 contract parts — `census.warning=` and exit 1 on other stderr, not-a-repository exit 2, hostile `core.fsmonitor`/env cases, and a ctime or read-only-`.git` arm against mtime-restore writes; re-verify the two remaining git-2.55.0 entries (`git-auto-maintenance-prunes-worktrees.md`, `git-grace-periods-and-expire-to.md`) on 2.56.0. (c) operability: bind the receipt label to the program position (interpreter's first script argument), not just argv membership. Fleet route: the LEARNING.md expansion predicate (capability vs entry-on-uncovered-ground) is unresolved. Certification stays OFF, K5 HELD; F5 reap and NAMESPACE holds unchanged.
```

## Deleted scaffold machinery (base lines 170-230 minus payloads 1-3)
| base lines | content | note |
|---|---|---|
| 170-171 | blank, blank | separator after `None.` (base 169) |
| 172 | `Insert the table below directly above ...` | K1 marker 1 |
| 173 | blank | |
| 174 | opening fence | |
| 208-212 | closing fence, blank, capability instruction, blank, opening fence | instruction consumed |
| 215-216 | closing fence, blank | |
| 217-220 | `Optional same-landing correction (calibration, RevR23Residuals R3): ...` | K1 marker 2; discharged by the R3 dated note appended to base line 92 |
| 221-224 | blank, planned instruction, blank, opening fence | instruction consumed |
| 227-230 | closing fence, blank, `---`, blank | separator |
