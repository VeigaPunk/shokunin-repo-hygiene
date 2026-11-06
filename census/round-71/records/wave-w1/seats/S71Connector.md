# S71Connector — r71 sibling-overlap + cross-claim scan (read-only; no lane edits)

## Reproduction from committed bytes (fresh runs, frozen invocations)
- C1 candidate: `SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=0` (23.9 s). Worktree instruments equal freeze blobs (counter 7e5a694a…, matrix e1a3c00b…, harness 6c7bf41d…, mutants 3e4945bf…); matrix = 70 rows = 19 accept + 51 refuse, and the run prints exactly 19 `new=accept` / 51 `new=refuse`.
- C1 do-nothing (`--new-tool census/round-71/controls/base-writer-8b9345b1.py`, sha 118597e0… = prereg): `new_forgeries=7 … class_mismatches=7` / `EXIT=1`; CASE FM1/FM2/FC1-3/AS1/AS2 `base=accept`, AS/FC/FM after rows refuse with the frozen classes.
- C2 after: `SUMMARY label=c2-after-r71 positive_selftest=PASS x_mutants=5 x_killed=5 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0` / `EXIT=0` (470.8 s); `POSITIVE … SELFTEST cases=39 pass=39 fail=0`. No mutant `apply=FAIL`.
- Direct counter selftest: `SELFTEST cases=39 pass=39 fail=0` / `EXIT=0`. All six claims reproduce; no numeric miss found.

## Separability: HOLDS for the frozen artifacts, NOT for arbitrary counter edits
Scratch copy with `selftest()` (section 8) and `verify_members()` stubbed (diff hunks `@@ -1259,73 +1259,8 @@`, `@@ -1357,257 +1292,8 @@`) run with the frozen C1 argv → byte-identical SUMMARY, `EXIT=0`. Code: `c1-counter.py:1661` `if ns.selftest: return selftest(...)`; `:1774` `evaluate(...)`; the only `verify_members` call is `:1714` under `if ns.battery_manifest:` (`:1695`); section (8) is `:1537-1584`; `selftest` reads only the base blob (`:1405`). Vice versa: `c2-harness.py:160` invokes the counter with only `--selftest --root --matrix --base-rev --work` (grep for `--rev|--tool|--new-tool` in the harness → 0), so C1's writer bytes are unreachable from C2. Caveat: both share the counter core — mutants X7 (`clean_env`, `:1542`) and X8 (`case_env`, `:1557`) mutate functions C1 executes; separable as measurements, not independent instruments.

## Ground sentence (corpus/README.md:1009): TRUE for the asked predicate
`git grep -n -i -E 'clean filter|filter driver|clean driver|filter\.[a-z]|status.witness|filter attribute' 8b9345b1… -- corpus/knowledge` → only `jj-colocation-receipts.md:93` (`filter.f.clean` NOT applied under jj) and `:94` (census filter checks do not cover jj). Broader: `filter` → 3 files (`diff-filter`, `--filter=tree:0`, jj); `GIT_ATTR_SOURCE` → `pathspec-env-scrub.md:33-35` (named as an unmeasured pathspec input, not a witness route). No earlier entry treats a clean filter as a status-witness route.
LOW: the same Ground sentence's second clause omits `caller-env-routes-receipt-writer.md:42`, which at base already records repo-local `core.fileMode=false` hiding a 755→644 flip ("routed to round 67"); `common-dir-route-receipt-writer.md:41` then contradicted it. Attribution/framing only, not a numeric miss.

## Sibling clean-tree tools: scrub GIT_ATTR_SOURCE / pin core.fileMode / check filter drivers
| tool:line | env handling | witness | scrub | pin | filter |
|---|---|---|---|---|---|
| kaidoku tools/round-29/prefile-check.sh:22 | unsets 3 GIT_* (:18) | status --porcelain | NO | NO | NO |
| kaidoku tools/round-42/prefile-gate.py:273 (cond :43-45) | inherit (_git :53 no env) | status | NO | NO | NO |
| kaidoku tools/round-45/frozen-path-preflight.py:137 | inherit (:47 no env) | status | NO | NO | NO |
| kaidoku tools/round-46/gate.py:134 (dirty :132) | inherit (:44 no env) | status | NO | NO | NO |
| kama tools/pre-report-gate.py:666-667 (arm 6) | os.environ copy (:443-448) | status | NO | NO | NO |
| kama tools/round72-round-scope.py:253,269 | inherit (:100 no env) | status | NO | NO | NO |
| kama tools/round73-round-scope-cases.py:165,276 | via mod._git | status | NO | NO | NO |
| mori tools/mori-index-clean.sh:71,77,101 | unsets 3 GIT_* (:26,41) | status | NO | NO | NO |
| mori tools/mori-unlanded-check.py:58 | os.environ copy (:38) | status | NO | NO | NO |
| mori tools/mori-misroot-sweep.py:119-123 | allowlist (:88-105) | status | YES* | NO | NO |
| mori tools/mori-census.sh:2389 | GIT_SCRUB (:580-590) | ls-files -mo | NO | NO | NO |
| tameshi tools/mutate-and-run.sh:2059,2071 | git_clean unsets all GIT_* (:289-300) | status | YES | NO | NO |
| audio corpus/live/r89-simplifier/proofs/run-all.sh:49 | inherit | diff --quiet | NO | NO | NO |

*Allowlist drops GIT_ATTR_SOURCE implicitly, but repo-local `core.fileMode` is still read. No sibling tool pins `core.fileMode` or enumerates filter drivers; the only attr mitigation is `core.attributesFile=/dev/null` in non-witness helpers (kaidoku round-25/ruler.py:31, instrument-custody.py:115; tsukuroi check-self-assessment.py:114; mori routed-check.py:235), which does not cover committed `.gitattributes`, `info/attributes`, or `GIT_ATTR_SOURCE`. No sibling carries `RECEIPT-FILTER-DRIVER-SET` (grep → 0).
HIGH: every gate above can certify a dirty tree through a caller-named attr source or repository-local `core.fileMode=false` / a repo-local clean filter — the routes r71 closes only in souji (writer :124 scrub, :132 `-c core.fileMode=true`, :139 `_filter_drivers`). Pre-existing, not introduced by r71. Counterexamples (no status witness): mado-verify.sh:3678,853 avoids `git status` by design; kotodama/chousa/tsukuroi tools have none (kotodama hits are frozen `freeze.txt` prose).

## Commands (cwd lane; scratch under /fast/scratch/hyaku/souji-r71/S71Connector)
`python3 -B census/round-71/c1-counter.py --root … --matrix census/round-71/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev a1db6c8514771c0a0321c29741831606d09cc2a5 --tool tools/souji-receipt-write.py --work <S>/c1frozen`
`… --new-tool census/round-71/controls/base-writer-8b9345b1.py --work <S>/dn`
`python3 -B census/round-71/c2-harness.py --label c2-after-r71 --counter census/round-71/c1-counter.py --matrix … --root … --base-rev 8b9345b1… --mutants census/round-71/c2-mutants.json --work <S>/c2`
`python3 -B <S>/c1rev/c1-counter-reverted.py <frozen C1 argv> --work <S>/c1rev`; `git grep -n -i … 8b9345b1 -- corpus/knowledge`; `diff -u` orig/copy.

Files written: `.ufo/waves/round-71/w1/S71Connector.md`; seat evidence `.ufo/waves/round-71/w1/S71Connector/{c1-frozen-run.txt,c1-donothing-run.txt,c1-reverted-counter-run.txt,c2-after-run.txt,counter-selftest-run.txt}`. Scratch removed before yield.
