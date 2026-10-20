STATUS: DONE — `*-ddb7347.*` evidence was never committed under those names; L1 re-measured at the wave-2 landed rev and committed the records as `*-4f48343.*` at `95519a7`, while the authority texts (committed later at `d98065d`) still cite the untracked wave-1 names. Fix = re-point, not commit.

Seat: SoujiR18.RevengeDdb7347Pointers-5 · 2026-10-20 · lane `/home/vgpnk/Projects/shokunin/souji-shokunin` · axis: **calibration** (C2 provenance for LG-DANGLING-PTR / closure R2). Leaf; read-only throughout (git read-only verbs only, no `jj` invocation, no installs, no writes outside this report).

## The answer

**What was renamed to what, at which commit:**

| never-committed name (cited in authority files) | committed as | at commit |
|---|---|---|
| `census/round-17/gate-replays-ddb7347.json` | `census/round-17/gate-replays-4f48343.json` | `95519a7` (15:57:26 -0300) |
| `census/round-17/jj-receipts-ddb7347.txt` | `census/round-17/jj-receipts-4f48343.txt` | `95519a7` |
| `census/round-17/seat-audit-r16-replay-ddb7347.json` | `census/round-17/seat-audit-r16-replay-4f48343.json` | `95519a7` |

It is **not a git rename and not a re-suffixing of the same bytes**: the `-ddb7347` files existed only as untracked L1 measurement outputs from the wave-1 landed rev `ddb7347` (ddb73474433977ff54b015ac3e77669ff2537353, 12:42:34). After the wave-2 fixes landed as `4f48343` (4f4834390ad4845b76804e94cc04d8f867ef9b54), L1 **re-measured everything at 4f48343** and committed the fresh records under the new suffix at `95519a7` ("round-17: wave specs/dispatch/registries and seat reports (w1 78, w2 71), landed-rev evidence (matrix, replays, jj fixture, live fleet), stub quarantine receipt"). The old-named files were superseded and removed from the worktree; no commit ever tracked them.

Proof the committed records are fresh measurements, not renamed stale output:
- `jj-receipts-4f48343.txt` is the **wave-2 35-case fixture run** (J10–J12 rows present, `SUMMARY total=35 failed=0 skipped=0` at `:54`), with wave-2 tool digests (verify `f88fed23…`, vault `5cb0fb13…`, quarantine `83cc3ce1…`) — not the wave-1 20-case run (`SUMMARY total=20` at `:33`) that the `ddb7347` name refers to.
- `gate-replays-4f48343.json` header: `"gate_rev_arg": "4f4834390ad4845b…"` = `"resolved_rev"` = `"lane_head"`; gate sha256 `f619518a…` (≠ ddb7347's `c7e8eea5…`, ≠ expected pin `e7d2439d…`).

Base-arm records kept the `base5fa6017` suffix (committed at `95519a7` too: `jj-receipts-base5fa6017.txt`, `seat-audit-r16-replay-base5fa6017.json`) — the base rev `5fa6017` never changed, which is exactly why **only changed-arm citations dangle**.

## Timeline (master first-parent, all at 2026-10-20 -0300)

1. `5fa6017` 12:42 — r16 tip, r17 base.
2. `ddb7347` 12:42 — wave-1 landing: code + `census/round-17/{gate-replays-expected.json,gate-replays.py,run-matrix.py,seat-audit-replay.py,transcript-manifest.py}` (5 files; `git ls-tree ddb7347 census/round-17/`, also reported by w2 `RevReplayBinding.md` F1). L1's measurement runs at ddb7347 write **untracked** worktree files with the `ddb7347` suffix.
3. `d7e648d` — r15 frozen record regenerated at ddb7347 (only those two fixture files differ from ddb7347; w2 `ScribeReportSections.md:10`).
4. `4f48343` — wave-2 fixes; also adds `census/round-17/c1-matrix.json` + mutates `seat-audit-replay.py` (`git log --name-status`).
5. `95519a7` 15:57 — **the commit**: adds `c1-matrix-4f48343.json`, `gate-replays-4f48343.json`, `jj-receipts-4f48343.txt`, `jj-receipts-base5fa6017.txt`, `live-fleet.json`, `seat-audit-r16-replay-{4f48343,base5fa6017}.json` (name-status `A` ×7). The `ddb7347`-named predecessors are nowhere in it.
6. `d98065d` 16:12 — commits the authority texts (SKILL/LOG/lesson/knowledge/README/SOURCES/QUALITY/SCORECARD) **citing the old `ddb7347`-suffixed names** — drafts written against the untracked wave-1 outputs (w2 seats read them and marked them "(L1)" = L1-pending), never re-pointed when the commit used the new names. w2 `ScribeReportSections.md:8,79` explicitly measured all six artifacts ABSENT at ddb7347 and d7e648d and flagged "commit them or cite as worktree-only"; the citation half of that advice was not executed.
7. `2cfc6c0` 16:12 — gate-landing.json; `b576341` 16:24 — r17 spot-check closure routing R1–R5 (`corpus/lessons/round-17-verifier-spotcheck.md:150` = R2).

## Evidence commands (run in this seat)

```
git -C LANE log --all -S 'ddb7347.json' --oneline            → 15 commits, incl. b576341 95519a7 d98065d
git -C LANE log --all -S 'jj-receipts-ddb7347' --oneline     → 11 commits, incl. 95519a7 d98065d (not b576341)
git -C LANE log --all --oneline -- census/round-17/gate-replays-ddb7347.json
                                 census/round-17/jj-receipts-ddb7347.txt
                                 census/round-17/seat-audit-r16-replay-ddb7347.json
                                                             → EMPTY (never tracked, any ref)
git -C LANE log --all --name-status -- census/round-17/      → A×7 at 95519a7 (4f48343 names); A×5 runners at ddb7347
git -C LANE ls-tree b5763415 census/round-17/                → only -4f48343/base5fa6017 names + tools + expected + gate-landing + live-fleet + c1-matrix.json
git -C LANE rev-parse ddb7347^{commit} 4f48343^{commit}      → full hashes above; both resolvable (ddb7347 held by refs/jj/keep/*)
glob census/round-17/* (worktree)                            → no *ddb7347* file remains on disk
read census/round-17/jj-receipts-4f48343.txt:1-43,:54        → 35-case run, all PASS, tool digests as above
read census/round-17/gate-replays-4f48343.json:1-33          → gate_rev_arg/lane_head = 4f48343, expected.gate_sha256_match=false, match=true
grep ^CASE\t(J1|J3|J9)\t on both committed records           → changed: J1:18 J1-vault:19 J3:22 J3-vault:23 J3-quarantine:24 J9-file:31 J9-worktree:32, SUMMARY:54
                                                               base:    J1:15 J1-vault:16 J3:19 J3-vault:20 J3-quarantine:21 J9-file:28 J9-worktree:29, SUMMARY:51 (total=33 failed=13 skipped=2)
git for-each-ref                                             → master=origin=origin/master=b576341; 0e78075/9411e47/67c0f4d exist only as refs/jj/keep/* (jj-side duplicates of the landing, not on master)
```

## Citation inventory at b576341 (master)

`gate-replays-ddb7347.json` (routed by closure R2 at `corpus/lessons/round-17-verifier-spotcheck.md:150`):
- `SKILL.md:163` (r15-preservation-evidence row, pinned-value column, "(L1)")
- `SKILL.md:165` (r17-gate-replays row, "(committed at ddb7347) and record … (L1)")
- `LOG.md:916` (D3 correction entry, replay `r16-precarry`)

`jj-receipts-ddb7347.txt` (**not** routed by the closure; caught by r18 LG-DANGLING-PTR):
- `corpus/knowledge/jj-colocation-receipts.md:2` (verified-at), `:44` (§4 failure case, "at ddb7347"), `:126` (F-1, cites `:18-19, 22-24, 31-32` changed / `:15-16, :19-21, :28-29` base), `:148` (Source-rows footer, `{base5fa6017,ddb7347}` brace expansion)
- `corpus/README.md:216` (F1-jj row, "(changed arm 0 failed)")

## Verdict and fix

**Re-point; do not (re)commit.** The `ddb7347`-named bytes exist nowhere (never tracked on any ref, gone from the worktree); recreating them would mean re-measuring at a rev that is not the landed tip. The committed `-4f48343` records already fulfill the evidential role, are the tip's own measurements, and — measured, not assumed — **every line citation survives the re-point unchanged** (both changed- and base-arm cites in knowledge F-1 land on identical row numbers in the committed records). LG-DANGLING-PTR strips `:line`, so the gate only needs the path tokens fixed:

1. `SKILL.md:163,165` + `LOG.md:916` → `census/round-17/gate-replays-4f48343.json` (as R2 already prescribes: appended LOG correction + registry pointer fix).
2. `corpus/knowledge/jj-colocation-receipts.md:2,:44,:126,:148` and `corpus/README.md:216` → `census/round-17/jj-receipts-4f48343.txt`; adjust the prose label "at ddb7347" (`:44`) / "run at landed revision ddb7347" (`:2`) to the revision actually recorded (4f48343) — the claims' substance (J1/J3/J9 NOT-SAFE at the landed rev) is byte-present in the committed record. `:148`'s brace expansion becomes `{base5fa6017,4f48343}`.
3. Keep `ddb7347` as a rev mention where it is history, not a pointer: `LOG.md:946` ("Code landed `ddb7347` … wave-2 fixes `4f48343`") resolves as a rev, not a path, and is correct.

Residuals, same root cause, advisory (beyond the pointer sweep):
- `corpus/knowledge/jj-colocation-receipts.md:3` recheck line expects `SUMMARY total=20 failed=0 skipped=0` — that is the wave-1 20-case fixture shape; the committed fixture yields `total=35 failed=0 skipped=0` (and base `total=33 failed=13 skipped=2`). Update the expectation with the re-point.
- `census/round-17/gate-replays-expected.json` still pins the `5fa6017` gate sha `e7d2439d…`, so `gate-replays-4f48343.json` reports `expected.gate_sha256_match: false` with top-level `match: true` (verdict-only match) — already surfaced in the r17 lesson residuals; outside the pointer fix.

Note for C1/C2 design: `ddb7347` remains resolvable today only via jj keep refs (`refs/jj/keep/ddb734744…`); once the authority files are re-pointed, nothing cites a keep-ref-only rev, removing that GC dependency from the lane's calibration surface.

Provenance: no tools installed or upgraded; no pacman transactions; all git invocations read-only (`log/ls-tree/show/grep <rev>/rev-parse/for-each-ref/merge-base`); no `jj` executed; no processes started; the only file written is this report.
