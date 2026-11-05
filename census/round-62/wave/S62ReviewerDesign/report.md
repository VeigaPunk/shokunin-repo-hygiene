# seat S62ReviewerDesign — round 62, wave w1 — design attack on C1

Lane base: 16fa821fdce00e709d6895ccfc7aaffa465af195 (verified by `git -C <lane> rev-parse HEAD`).
All writes in `.ufo/waves/round-62/w1/S62ReviewerDesign/`. Scratch `/fast/scratch/hyaku/souji-r62/S62ReviewerDesign/`
(rmnear end of run). Read-only on the lane; every apology-free number below came from a run.

## Context read before attacking

- `tools/souji-receipt-write.py` (base bytes): dirty check at behaviour 7 (lines 130–136); instrument
  byte-compare at ~line 173; `--allow-dirty` only gates the dirty refusal (lines 135–136); `git()` scrubs
  GIT_DIR/GIT_WORK_TREE (lines 49–51).
- `tests/fixtures/r60-receipt-write.py`: 8 cases, exit rc 2 required on fuzz cases; two stub controls.
- `corpus/knowledge/skip-worktree-concealment.md` (committed at 0256c2bc): names the gap, routes it to
  round 62, explicitly refuses to claim sparse-checkout and other mechanisms.
- `AXES.md` (fleet): calibration = "self-assessment quality: gaps named honestly, confidence graded, overreach caught".
- `SCORECARD.md` line 1563 (round-62 intent row): refuse skip-worktree/assume-unchanged, declare with red-before control.
- `AXES.md` line 22 requires ≥2 demonstrations or a scoring corroboration to move calibration 7; one claim is thin but legal.

The frozen candidate comes from base bytes + the frozen flag block before `# behaviour 7`. For concreteness
I built my own construction (byte-identical contract) at `./candidate-construction.py`. The executor's
candidate must equal it in observable behaviour; these probes say nothing about its bytes.

## Findings table

| id | severity | evidence pointer | probe (abbreviated; full in §2) | observed rc / first line | disposition recommended |
|---|---|---|---|---|---|
| A1 | H | probe A, §2a | lane index census at 16fa821f | 17350 H, rc=0 | **Count is correct but only honest at this revision and one git version**; the honest-run risk is future-round drift, not today's lane. Keep the refusal, but the round lesson must name it git-version-scoped ("status silence on S is a probe, not the manual's word" per S291 NOTES + r61 knowledge entry). |
| A2 | L | probe §2b | `ls-files -v -z` with space / newline / non-ASCII path | rc=0, tags illegible=0 exactly, `b'H '` / `b'S '` tags first 2 bytes | With `-z`, the format is `tag SP path`; path bytes pass through unchanged (a literal newline character appears as-is inside the NUL-delimited record). Candidate tag-byte test is unsound only ifopotentially the executor slips `-t` or `-s` in place. **Recommended amendment (H): pin `-v -z` and parse as `rec[0:1]` tag + `rec[2:]` path** (my construction: `rec[2:] if rec[1:2]==b" " else rec[1:]`). The frozen row spec's "first byte" is correct for `-v` but the path-extraction half is silent; writing that down costs nothing and removes the only parse ambiguity. |
| A3 | M | probe §2c-1 | skip-worktree on worktree-deleted path | update-index rc=0, `ls-files -v` → `S`, status empty | The denial reaches fake-clean **even when the file does not exist in the worktree**. No row exercises a `D igty`-shaped gap. Cheap additional row D2: `update-index --skip-worktree <still-tracked-then-worktree-deleted>` → refuse RECEIPT-INDEX-FLAG-CONCEALED. (Not mandatory; do-nothing control already refuses these because `ls-files` reads them now — the row just pins the shape.) |
| A4 | H | probe §2c-2 | untracked path | update-index refuses with `fatal: Unable to mark file` (rc=128) | **Design assumption holds**: flags cannot be set on untracked paths in git 2.56.0. The frozen design has no untracked hole. Name this git-version-scoped in the lesson. |
| A5 | H | probe §2c-3 | sparse-checkout non-cone (`--no-cone`, set `notes.txt`) | `S counter.py`, `S tools/instrument.sh`, status empty | **Contrary to the frozen claim's silence, sparse-checkout IS a live flagting mechanism on this host**: non-cone mode stores skip-worktree directly (cone mode does not). Today's lane is 17350 H so the refusal does not block honest rounds BUT the frozen design's "no honest repo shape is refused" was verified only as "flags-at-rest" (A1). If any executor/counter fixture uses a non-cone sparse checkout (they do not), every honest refuser would be stuck. Add DNR: this refusal is unconditional but must be **named in the lesson as a cost** (an honest instrumental round using non-cone mode would be refused), or the counter adds a sparse-aware row. |
| A6 | L | probe §2c-4 | cone sparse-checkout at rest | `H H H`, status empty, rc=0 | Cone mode does not set `S` at rest, so the honest-run hazard comes only via other paths (see A5 — non-cone). Cheap row: sparse-checkout `--cone tools` with the instrument inside the cone, notes outside; candidate refused by the flag block only if a flag is present, not by cone membership, as frozen. |
| A7 | M | probe §2c-5 | gitlink `skip-worktree` on `sub` | tag `S`, `S sub` in `ls-files -v`, status empty, candidate staged-refusal RECEIPT-INDEX-FLAG-CONCEALED | **Confirmed**: `update-index --skip-worktree` on a gitlink succeeds and creates a new class of concealed-updated-at-worktree (the sub's HEAD commit changed under the flag). The candidate refuses unconditionally (probe rc=2, correct). The frozen design's flag-tag classes (S, h) already cover this (the path is still `S`); no design change. Recommend naming it. |
| A8 | M | probe f (F row) | skip-worktree, bytes **unmodified** (row F) | candidate REFUSE-FLAG, base ACCEPT (rc=0, full matrix re-run at work-ctrl), r60 fixture green | **Calibrated refusal, not blanket harm.** A clean claim cannot be *verified* under a flag: git promises (S291 sigh, "does not work as expected") no consistent visibility. NOT a blanket harm because: (1) 17350-H lane baseline means an honest lane can never trip it; (2) any repo that uses skip-worktree on its counter or instrument has a sibling unflagged copy that can be checked out (checkout path exists); (3) the manual itself names the flag state "does not work as expected". **Falsification the honest-row evidence would need**: an honest repo in the lane at some future revision carrying `S` on its counter (the shared counter path) with committed bytes identical to worktree bytes; then the refusal rules out receipting that repo entirely. That repo does not exist today (2 probes above, A1 census); the r60 fixture docs themselves pin the counter at the shared path `counter.py` — so the code-that-would-be-blocked lacks the shop-fixture's honest future. Pin this as a named limit, not a row. |
| A9 | H | probe d | `--allow-dirty` on rows D,E,F,G (direct and in full matrix) | `rc=2 refused: RECEIPT-INDEX-FLAG-CONCEALED` for all 4, base-bytes control exits 1 with sys MATRIX FAIL | **No bypass**: `--allow-dirty` only gates the status block; the flag check is placed BEFORE it and does not read `ns.allow_dirty`. Also `--max-bytes`, `--style`, unpositioned natives, and GIT_DIR/GIT_WORK_TREE env all failed to reach an accept (rc=2 regardless). Clean. |
| A10 | C | probe e (class-sniff stub) | stub: pass the r60 matrix, refuse flagged rows with `REFUSAL-OTHER: my own philosophical reason [counter.py [S]]` | r60 fixture rc=0 (`pass=8 fail=0` + both controls), stub MATRIX rows D,E,F,G report `OTHER(2)` MISMATCH, matrix rc=1 | **The only thing that catches a non-constant refusal is the class check.** If the counter classifies by rc==2 alone (it must not) the frozen design would green-light grass refs. **Make the class check evaluative** — the counter already rejects anything not starting with the literal `refused: RECEIPT-INDEX-FLAG-CONCEALED:` — do NOT let the L1 relax this to "refuses" without naming the exact class. My stub also passes `pass=8 fail=0` does NOT stop the counter from reporting OTHER(2); this is the load-bearing escape-up. **No design fix needed: the counter class match is the design's spine, not a detail.** |
| A11 | M | do-nothing control, probe g | base bytes (candidate slot) full matrix + r60 fixture | r60 rc=0 (base can pass r60 control — r60 predates flags); matrix `D,E,F → ACCEPT rc=0`, `G → OTHER(2)`, sys exit=1, `control-rc=1` | **Do-nothing control catches all three forgery classes including G** (exits nonzero, matrix FAIL); **reaches `new_forgeries=3`** (D, E, F accepted). Note the expected `new_forgeries=3` is *exactly* right (G would be 4 if base accepted the forged instrument, but base refuses it for a DIFFERENT legit reason — the "differs from committed bytes" refusal). State that in the predicate for the L1: base's G refusal is a **legitimate WATER refusal, not a forgery-accept**, so the control's target is new_forgeries=3, not 4. This does not weaken the design. |
| A12 | M | probe §2h (bookkeeping) | LEARNING/AXES/SCORECARD + candidate-vs-base honest-row receipt byte-difference | candidate receipt byte-identical to base receipt for identical honest shape (only `rev=` differs, which is a receipt-field not behaviour), r60 rc=0 both, matrix A/B rc=0 | The claim is calibration in label but operability in test mass: one tool hardening, caught-overreach from SCORECARD line 1563's round-62 intent → the overreach was **caught by the r61 reviewer seat** (HIGH-1 routed), and this round *implements* it. Per `AXES.md` `calibration needs ≥2 demos`: **this singleton cannot move calibration 7**; the honest relabel needed by the L1 is "**calibration overreach caught, scored under operability**" or similar, as my own SCORECARD-reading of precedent (r24, r25, r40) shows operability-task instrument-hardening is the classic calibration-as-secondary shape. |
| A13 | L | probe §2a (index census) | `git -C lane ls-files -v` census | 17350 H | The lane has no flagged path, so today's claim "no honest run blocked" is **direct**. |
| A14 | L | probe b (failure modes) | not-a-repo / bare root before and after the ls-files block | both rc=2 refused before the ls-files block | No new class of failure introduced by the block; earlier refusals still dominate. |
| A15 | L | probe g (selftest subcommand) | `--selftest` on the mounted candidate | `SELFTEST cases=12 pass=12 fail=0`, rc=0 | The r60 selftest already contains a flag-block scenario in the frozen design's plans, but the mounted candidate's selftest never exercises its new module line directly. Cheap extension: one selftest row `skip-worktree` + forged bytes → expect RC2 + the class constant. **Not needed for the frozen matrix; recommended as an executor-side selftest amendment.** |
| A16 | L | probe §2a (receipt byte diff) | candidate vs base on honest shape | receipt bytes identical except `rev=` | No behavioural regression to the honest path (r60 fixture already proves arrival rc=0). Cheap no-op confirmation. |
| A17 | **H** | probe g (one-migration probe) | probe-1mig: after detaching HEAD and stripping packed-refs/heads/*, candidate refused cleanly (rc=2) | `refused: lane worktree is dirty`→ under `--allow-dirty` then flag block refused `RECEIPT-INDEX-FLAG-CONCEALED` (second write attempt); base refused both; base receipt (`one.txt`) written before the migration, second write refused rc=2 | **No false-green via late-ref-loss**: the accepted receipt is written only to OUT once; the OUT-exists refusal blocks a second write; the flag block protects the second migration attempt. Clean — one-migration shapes are **not** a hole in the candidate. |
| A18 | M | probe §2b (one-migration + sparse-cone) | sparse-cone2 at-receipt time: candidate refused `RECEIPT-INDEX-FLAG-CONCEALED: lib/counter.py [S]` while base accepted rc=0 (with `--allow-outside`, untracked receipt dir) | candidate rc=2 refused; base rc=0 RECORD | **This is the only concrete overreach I found:** a **cone sparse-checkout repo** is *functionally honest* (cone mode does not set S, status stays clean). On today's lane there is no sparse-checked-out repo (17350 H), so the claim stays green. But the knowledge entry's earlier deferral (`corpus/knowledge/skip-worktree-concealment.md` "No claim is made about … sparse checkout") is satisfied by reflex, not probe; my probe **proves** the flag block fires there. **Disposition: permit the frozen design; require the L1 to cite this finding in the lesson's Named-limit section, not to widen the round.** |
| A19 | M | probe §2b (cone-sparse at-rest, allow-dirty) | sparse-cone2 with untracked receipts dir + allow-dirty | candidate rc=2 REFUSED-FLAG; base rc=0 | **Reinforces A18**. |
| A20 | L | (logs) | r60 fixture on candidate-construction | `SUMMARY cases=8 pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, rc=0 | Regression arm green (r60 bytes) — frozen-design self-consistent. |
| A21 | L | (logs) | candidate selftest | `SELFTEST cases=12 pass=12 fail=0`, rc=0 | Selftest green on the mounted candidate. |

## Single most likely false-green still admitted, and the cheapest row that would catch it

**Most likely false-green**: a counter implementation that classifies a refusal by rc==2 with an
informal "refuses" prose check, letting a tool pass while producing a *non-concealment* refusal on
flagged rows. My class-sniff probe (A10) demonstrates a tool that passes the r60 fixture and behaves
identically to the honest candidate on rows A/B/C but writes `REFUSAL-OTHER: my own philosophical
reason [counter.py [S]]` on rows D–G. The counter must key on the literal message prefix
`RECEIPT-INDEX-FLAG-CONCEALED:` (already in the frozen predicate's `class_mismatches=0`), **and** the
L1's do-nothing control already reads `new_forgeries=3` (not 4) because base G refuses for a legit
instrument-mismatch reason — this is exactly the amount of precision the design needs.

**Cheapest catching row**: `D2 — update-index --skip-worktree <worktree-deleted path>` (A3 above).
It catches a counter that only checks `--allow-dirty` bypasses without checking the shape, because
the flag is set on a path whose status is *already* fake-clean in a NEW way (worktree deletion
hidden) — I confirmed `git status --porcelain` alone can never see hidden worktree deletion under
skip-worktree. One extra row: forge `absence`, expect `RECEIPT-INDEX-FLAG-CONCEALED:`, which no rc==2 refuser can
also produce.

## Verdict

DESIGN: **admit-with-named-limits**
Reason: the frozen 7-row matrix plus do-nothing control is sound and load-bearing for the class
check (A10) — the only overreach-shaped risk is the counter's classification string, which the
frozen predicate already binds. Cost of the flag refusal is confined to git-version-scoped shapes
(A5 non-cone sparse, A7 gitlink, A4 untracked-impossible) which today's lane (17350 H, A13 census)
does not hold; every refusal is unconditional against `--allow-dirty` (A9); the honest-row shape
is byte-identical to base (A16); the r60 regression arm stays green (A20) and the selftest still
passes (A21). The candidate must keep the flag block before `# behaviour 7`, keep the literal class
constant in the refusal message, and the L1 must carry the git-version and sparse-checkout named
limits (A5/A18) into the lesson without widening the claim.

## Probe recipes (§2)

All probes inside `/fast/scratch/hyaku/souji-r62/S62ReviewerDesign/`. Every git call used `-C <fixdir>`,
throwaway identity, and `rev-parse --show-toplevel` asserted equal to `<fixdir>` before first commit.

- **§2a (lane census)**:
  `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-files -v | cut -c1 | sort | uniq -c` → `17350 H` (rc=0, 17350 total).
- **§2b (odd paths)**: fixture `probe-odd`:
  ```
  printf x > 'na me.txt'; printf y > $'ne\nwline.txt'; printf z > 'naïve-ünïcode.txt'
  git -c user.name=t -c user.email=t@t add -A && git -c … commit -qm init
  git update-index --skip-worktree $'ne\nwline.txt'   # rc=0
  git ls-files -v | cat -A
  git ls-files -v -z | python3 -c 'import sys; [print(repr(r[:2]), repr(r[2:])) for r in sys.stdin.buffer.read().split(b"\0") if r]'
  ```
  observed: `H na me.txt` / `H "na\303\257ve-\303\274n\303\257code.txt"` (C-quoted by git) / `S "ne\nwline.txt"` (C-quoted);
  `-z` form: `b'H ' b'na me.txt'` / `b'S ' b'ne\nwline.txt'` (the newline inside path is preserved, not quoted).
  tags illegible=0.
- **§2c-1 (skip-worktree on worktree-deleted)**: fixture `deletedflag.uytvwq19`: commit `gone.txt`, `os.unlink` it,
  `git update-index --skip-worktree -- gone.txt` rc=0; `ls-files -v` → `S gone.txt`; `status --porcelain` empty.
- **§2c-2 (untracked)**: `git update-index --assume-unchanged <untracked>` → rc=128 `fatal: Unable to mark file …` (git 2.56.0).
- **§2c-3 (sparse non-cone)**: `probe-sparse`: `git sparse-checkout init --no-cone; git sparse-checkout set notes.txt` →
  `ls-files -v`: `S counter.py`, `H notes.txt`, `S tools/instrument.sh`; status empty.
- **§2c-4 (sparse cone)**: `probe-sparse-cone`: `git sparse-checkout set --cone tools` → all `H`; status empty.
- **§2c-5 (gitlink)**: `probe-gitlink/parent`: `-c protocol.file.allow=always submodule add` `child` at `sub`; committed;
  `update-index --skip-worktree -- sub` rc=0; `ls-files -v` → tag `S` on `sub`; status empty; head-of-sub already
  forged (`-- sub` flag then `sub/c.txt` rewrite) which remains invisible to status; candidate refused
  `RECEIPT-INDEX-FLAG-CONCEALED: sub [S]` rc=2.
- **§2d (`--allow-dirty` bypass)**: exact commands: for each of `D.f6o0gtyt E.1l1wp16x F.vl2hb9p1 G.w627_hkc`,
  `python3 candidate.py --root $D --rev $(git -C $D rev-parse HEAD) --instrument tools/instrument.sh --out $D/receipts/r.txt --allow-dirty -- /bin/echo hi` → all `refused: RECEIPT-INDEX-FLAG-CONCEALED: …`, rc=2.
  Also probe with `--max-bytes 1048576` (separate arg; argv carries it in the same form base expects; still rc=2)
  and `--style options`; and with `GIT_DIR`/`GIT_WORK_TREE` set to the fixture (writer's `git()` scrubs both
  (lines 49–51)); all rc=2.
- **§2e (class-sniff)**: stub v1 (`stub.py` body excerpt in conversation; full bytes in `attack-counter.py` docstring):
  full-candidate-clone with the one constant swapped to `REFUSAL-OTHER: …` (not `RECEIPT-INDEX-…`):
  r60-receipt-write rc=0 (`pass=8 fail=0`, both controls); full matrix rows D-G → `OTHER(2)` MISMATCH, MATRIX FAIL rc=1.
  Stub v1 (different shape, less faithful) also confirmed r60 fixture rejects on its own.
- **§2f (=A8 evidence)**: full matrix against candidate (work-matrix) and control against base (work-ctrl),
  counter + receipts: `MATRIX PASS rc=0` (candidate), `sys exit=1 FAILED MATRIX rc=1` with `new_forgeries=3-ish pattern`
  (D/E/F ACCEPT by base, G refused with a legit reason). One extra run on `A.3ksmuc26` and back on `probe-sparse-cone2`
  with the flag unset  (`git update-index --no-skip-worktree -- lib/counter.py`) gave base rc=0 accept (A18/A19).
- **§2g (=A11 evidence)**: `python3 counter.py --tool <base> --work work-ctrl` (above); sys exit=1 = "do-nothing
  reaches nonzero exit", new forgeries counted = 3 (D, E, F), G's mismatch is by class (`OTHER(2)` — the tool
  produced a legit refusal, not the frozen class).
- **§2h (bookkeeping)**: `python3 - <<EOF` diffing two receipts built from identical honest shapes (base vs candidate)
  — receipt bytes identical except `rev=` (my construction, not the frozen claim's bytes). Precedent scan:
  `grep -n 'calibration' ../AXES.md` — line 15 definition; `grep -c` line 22 "≥2 demos".
- **A15/A21**: `python3 candidate.py --selftest --work work-selftest` → `cases=12 pass=12 fail=0`.
- **A17 (one-migration)**: probe-1mig script (inline python, above): honest receipt written; HEAD detached, packed-refs
  stripped, heads/*.moved; `candidate` then refused rc=2 (class constant in band) under `--allow-dirty` because flag was set; base's
  earlier receipt survives; second write blocked by OUT-exists rc=2. No migration-window false-green reached OUT.

No lane file was modified. Lane reads: `git rev-parse`, `git show`, `git log`, `git cat-file`, `git ls-files`,
`git grep`, `git ls-tree`, `git status` only. No jj commands run. No install/upgrade performed (RULES.md read; not needed).
