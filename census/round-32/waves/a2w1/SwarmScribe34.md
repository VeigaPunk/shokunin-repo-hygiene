# SwarmScribe34 — round-32 report draft (attempt 2, wave a2w1)

## Status

STATUS: PASS — the round report is drafted at `.ufo/waves/round-32/a2w1/deliver-report-draft.md` in
the house style of `/home/vgpnk/Projects/shokunin/.ufo/reports/round-31/souji.md`, with every required
section, the attempt-2 framing (attempt 1's crash, the salvage commit, what was reused after
re-verification and what was discarded, and the ABANDONED `w2` marker), and every value I could not read
from committed bytes marked `<L1>`. No counter of my own was run; no lane file was modified.

## Evidence

All paths relative to `/home/vgpnk/Projects/shokunin/souji-shokunin` unless absolute. Draft-time lane
HEAD `4e56c48b8fc828f9aba2746e324dc46aa538bdbf` (`git rev-parse master`), equal to
`git ls-remote origin refs/heads/master`.

1. **Frozen contract and amendments** — `census/round-32/records/preregistration.txt` (32 lines, targets
   `unbound=0 mismatches=0 withdrawn<=8` / `fail=0` / `legs=14 fail=0 f1_entries=5`),
   `census/round-32/records/amendments.txt` (A0 at `7a6667c`, A1 at `a92e1aa`), `controls.tsv:2-4`,
   `controls-a0.tsv:2-5`.
2. **Landing readings, from bytes committed by the salvage commit** (line numbers verified with
   `grep -n '^SUMMARY'`):

```
c1-after-v1.txt lines=46 summary=46   items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6 rev=9e8982b7
c1-after-v2.txt lines=46 summary=46   same rev, same reading
c2-after-v1.txt lines=29 summary=29   items=27 pass=26 fail=1 rev=98e5203d
c3-after-v1.txt lines=16 summary=16   legs=14 fail=0 f1_entries=5 rev=a92e1aae
c3-after-v2.txt lines=19 summary=19   legs=17 fail=0 f1_entries=5 rev=a92e1aae
```

3. **Frontier counts** —

```
git show <rev>:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
85b61a1 -> 146 ; a92e1aa -> 147 ; 4e56c48 -> 147
git grep -l 'ground: F1' <rev> -- corpus/knowledge | wc -l     85b61a1 -> 4 ; 4e56c48 -> 5
```

   S223 sits at `corpus/SOURCES.md:168` (tier A, raw tag URL, `mined`); touched cells diffed old->new:
   S002 `used-by`, S051 `used-by` (+`jj-dropped-keep-object-lifetime.md`), S063 `anchor` (+`§ CONFIGURATION
   gc.pruneExpire, gc.reflogExpire and gc.reflogExpireUnreachable`) and `used-by`.
   `census/round-32/records/census-start.txt:37` = `souji ok`, exit 0, 36 `W04`; no `census-end.txt` exists.
4. **Wave shape** — `w1/swarm-registry.json` 44 members / 41 report files (missing `SwarmReviewer30`,
   `SwarmReviewer31`, `SwarmMutationTester40`); `a2w1/swarm-registry.json` 38 members / 15 report files at
   draft time; `w2/swarm-registry.json` empty. Flash/attack per `make-spec-a2w1.py:115-116`
   (`flash = executor+scribe+critic+sentinel+revenger+simplifier`, `attack = reviewer+critic+mutation-tester`):
   w1 34/44 and 11/44, a2w1 19/38 and 23/38 (the w1 figures agree with `w1/SwarmSimplifier44.md` E1).
   `w2.ready.dispatched` = `2026-10-26T09:04:54 ABANDONED by hyaku run-8 orchestrator cleanup: no seat was spawned`.
5. **Salvage commit content** — `git show --stat 4e56c48` = the five after-records only (+156); six lane
   commits in `85b61a1..4e56c48`.
6. **Reproduction of the scratch fallback** (my own, scratch `/fast/scratch/hyaku/souji-r32/SwarmScribe34`
   with `TMPDIR` set inside it; each probe removed its own directory):

```
with TMPDIR:    /fast/scratch/hyaku/souji-r32/SwarmScribe34/tmp/souji-r27-pre-report.8fUpLe
without TMPDIR: /tmp/souji-r27-pre-report.P9YJhV
r9 without TMPDIR: /var/tmp/souji-round9-selftest.L3ElRV
tests/fixtures/r20-input-binding.py:31  TMP_ROOT = Path("/var/tmp")
tests/fixtures/r20-input-binding.py:47-49  "HOME": "/var/tmp", "TMPDIR": "/var/tmp"
```

7. **Fleet state** — `git -C /home/vgpnk/Projects/shokunin status --porcelain`: 152 staged `.tower/`
   entries, 19 `.ufo/` driver entries, one transient untracked `s8-colon.txt` at the fleet root (absent on
   a second read). `considerthese` absent. No seat report under either wave mentions a tool install.

## Findings

1. **C2's landed fix keeps literal scratch fallbacks the frozen instrument cannot see.**
   With `TMPDIR` unset, ten of the 27 files the C2 commit touched still resolve scratch to a literal
   `/tmp` or `/var/tmp`: `tools/souji-round9-selftest.sh:7,14` (`mktemp -d "${TMPDIR:-/var/tmp}/…"` and
   `export TMPDIR="${TMPDIR:-/var/tmp}"`), `tools/souji-census.sh:309,1879,2009`,
   `tools/souji-repo-structure.sh:266`, `tools/souji-receipt-run.py:71`,
   `tests/fixtures/r13-repo-structure.sh:189,232`, `tests/fixtures/r23-receipt-run.py:50`,
   `tests/fixtures/r24-receipt-verify.py:47`, `tests/fixtures/r25-receipt-stderr.py:20`,
   `tests/fixtures/r27-pre-report-gate.sh:7`, `tests/fixtures/r28-wave-evidence-capture.sh:51`
   (reproduced, evidence 6). The counter always sets `TMPDIR` in SBOX, so a fallback is unobservable by it;
   the drafted Q71 text asks for the `${TMPDIR:?}` / `mktemp -d -t` idiom
   (`.ufo/waves/round-32/w1/deliver-quality-q70-q72.md`, Q71 row). Location: the files above plus
   `census/round-32/c2-counter.py` SBOX construction.
2. **The two r20 fixtures meet C2's sandbox by re-binding `/var/tmp` writable, not by honouring `TMPDIR`.**
   `tests/fixtures/r20-input-binding.py` and `tests/fixtures/r20-audit-contract.py` keep `TMP_ROOT =
   Path("/var/tmp")` (input-binding `:31`) and re-exec themselves under a nested
   `bwrap … --bind <private> /var/tmp`, while the child env still pins `"TMPDIR": "/var/tmp"`
   (`:47-49`) — the exact child-env form the C2 fix text forbids ("child environments that pass the
   caller's `TMPDIR` and never a literal `/var/tmp` or `/tmp`", `deliver-quality-q70-q72.md` Q71).
   Location: the two fixture files, added `_private_var_tmp()`.
3. **C2's landing reading is contested and the draft carries both.** The salvaged record says 26/27 with
   T18 failing (`c2-after-v1.txt:29`); two independent full re-runs at the same commit say 25/27 with T12
   and T18 failing (`.ufo/waves/round-32/a2w1/SwarmExecutor08.md`), and the tip reads 25/27. The draft
   states the conflict and leaves the final-tip cell `<L1>`, so the L1 does not inherit a single
   unverified number.
4. **Attempt 1 lost three of its 44 seat reports.** `SwarmReviewer30`, `SwarmReviewer31`,
   `SwarmMutationTester40` have no file under `w1/`; the draft states 41/44 instead of the r31 formula
   "every seat wrote its report". Location: `.ufo/waves/round-32/w1/swarm-registry.json` vs the directory.
5. **Every wave-shaped number in the draft is uncommitted.** The registries, dispatches and ready markers
   live under the gitignored `.ufo/waves/`, so the draft names them as provenance and leaves the committed
   capture `census/round-32/waves/*-results.json` as `<L1>`; `census-end.txt` is likewise absent.
   Location: the draft's round-shape table and Sources & frontier bullet.
6. **C1's withdrawal prose is invisible to the frozen counter**, which reads only the reason's word count;
   the falsify wave already reproduces one wrong withdrawal (N25 binds as `k13`) and one decoy-row bypass
   (`.ufo/waves/round-32/a2w1/SwarmCritic04.md` A1, `SwarmCritic06.md` A2). The draft records both under the
   C1 measurement and in the discernment verdict, without changing a predicate. Location: `SCORECARD.md:459`
   at `9e8982b`, `census/round-32/c1-counter-v2.py:224`.
7. **The draft's `<L1>` set is complete for what has not landed**: final HEAD, `jj-lane.sh state`, QUALITY
   Q70-Q72, the C1/C3 Gate-registry rows, SCORECARD round-32 measurements/capability/planned rows, the
   lesson, the LOG entry, the end census, the wave capture, the final-tip receipt, the no-harm numbers and
   scratch removal. No value outside that set is unbacked. Location: the draft itself.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/a2w1/deliver-report-draft.md` — the round report draft (sections: Work performed, Landed changes, Before -> after measurements incl. No harm, Sources & frontier, Trend verdicts, SHONEN, Other report lines).
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/a2w1/SwarmScribe34.md` — this report.

Not an attack seat: no counter predicate, item set or target was challenged; findings 1 and 2 are
predicate-coverage observations with a reproduced state, offered as input for the lesson's residuals, not
as amendments. Scratch `/fast/scratch/hyaku/souji-r32/SwarmScribe34` removed after the probes; no tool
installed, no pacman transaction, no `git`/`jj` mutation in the lane.
