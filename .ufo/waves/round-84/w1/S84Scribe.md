# S84Scribe — souji r84 draft seat (knowledge sections + QUALITY rows)

Seat: S84Scribe (scribe, w1). Lane: `souji-shokunin`. Scratch: `/fast/scratch/hyaku/souji-r84/S84Scribe/`.
Scope: **drafts only**. No corpus file was edited, no commit, no push, no git/jj mutation, no MANIFEST /
`.ufo/state/*` / `.scratch/*` / `.ufo/watchdog.log` touch. The L1 integrates.

> **Landed state (checked 2026-11-08, after my drafts were written).** The L1 landed its own versions of both
> knowledge sections and both QUALITY rows while this seat was measuring: `4557fc71` (sections, QUALITY rows,
> S334–S336, lesson, plans, SCORECARD) and `1f49b3a7` (the C2 repair and its receipts). My drafts are therefore
> **superseded as integration inputs** — the landed text is the lane's. What this seat still contributes:
> (a) an **independent re-verification** of the landed claims (below), (b) the **read-guard defect and its
> minimal reproducer**, which the L1 recorded as lesson M2 and credited to this seat
> (`corpus/lessons/round-84.md` M2 and the wave table's `S84Scribe` row), and (c) the drafts, kept as the
> **paste-ready text and the grounding maps** for anything the L1 wants to re-check or extend. Nothing here
> contradicts the landed text.

## Deliverables (drafts, for the L1)

| file | what it is |
|---|---|
| `.ufo/waves/round-84/w1/S84Scribe/draft-gate-signal-handling-r84.md` | paste-ready section **"A re-walk after the TERM pass (r84, `tools/souji-vault-verify.sh`)"** for `corpus/knowledge/gate-signal-handling.md` + a grounding map |
| `.ufo/waves/round-84/w1/S84Scribe/draft-own-tree-pointer-binding-r84.md` | paste-ready section **"Bounding a population, not just a rule (r84)"** for `corpus/knowledge/own-tree-pointer-binding.md` + a grounding map |
| `.ufo/waves/round-84/w1/S84Scribe/draft-QUALITY-r84-rows.md` | the two QUALITY rows (**Q154**, **Q155**) under a new `## Round 84 criteria` heading, in the file's `\| id \| criterion \| applies to \| test \| lesson \|` shape + a grounding map |
| `.ufo/waves/round-84/w1/S84Scribe/receipts/` | the receipts every draft sentence cites (below) |

## Behavior (what the round does, as measured by me)

### C1 — the population binds five pointer-counter clauses (calibration)

- The r84 population `census/round-84/c1-false-rows.tsv` is the r83 36 rows **byte-for-byte in the same order**
  (verified: `diff` of the first 36 data rows is empty) plus eight rows at fixture revision R7 — TF8, TF9, TF10
  (TRUE) and NF-P, NF-L, NF-L2, NF-M, NF-Q (FALSE).
- Re-measured with the frozen battery:
  - after arm — `python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py
    --work <empty dir outside /tmp> --only r84 --expect-killed 5` →
    `ARM pristine pop=r84 rows=44 mismatches=0 errors=0`, five `MUTANT … killed=yes`,
    `SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5`, **EXIT 0**.
    Receipt: `.ufo/waves/round-84/w1/S84Scribe/receipts/c1-battery-r84.txt`.
  - before arm — the same battery `--only r83` → `ARM pristine pop=r83 rows=36 mismatches=0 errors=0`, five
    `MUTANT … killed=no`, `SUMMARY … killed_r83=0 killed_total=0`, **EXIT 0**.
    Receipt: `.ufo/waves/round-84/w1/S84Scribe/receipts/c1-before-r83.txt`.
  - The committed before receipt says the same (`census/round-84/controls/c1-before-r83-population.txt`).
- **Which row kills which mutant** (re-measured row by row through the frozen harness, not inferred):
  `m6-digest-blind` → **NF-L**; `m7-round-blind` → **NF-L2**; `m8-w-only-shapes` → **TF9, TF10**;
  `m9-basename-only` → **TF8, TF9, TF10, NF-P**; `m10-records-as-wave` → **NF-M**.
  Receipt: `.ufo/waves/round-84/w1/S84Scribe/receipts/c1-per-mutant-rows.txt`.

### C2 — the vault CLI's signal path freezes the tree before terminating it (operability)

- The escape: a CLI that traps the caller's signal and forks from its trap, after the map pass, and `setsid`s the
  child out of `timeout`'s group. The r83 walk read `/proc` once and TERMed each descendant it had found, so the
  child was in neither the map nor the group. The frozen `latefork` stub is that shape.
- The r83 bytes are red exactly on l1/l2: `SUMMARY rows=22 mismatches=2 errors=0 orphans=2`, EXIT 1, one
  survivor each (`census/round-84/controls/c2-before-r83-tool.txt`).
- The repair (executor candidate, `.ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh`, sha256
  `a33038e9099e31052a16201d3e23b84b0b228558ab10188679f60efde6c26b15`): two fork-free `/proc` map passes, every
  discovered descendant SIGSTOPped **before any trappable signal reaches it**, then SIGKILL of the frozen set with
  a starttime re-read. I re-ran the frozen counter on those bytes independently:
  `SUMMARY rows=22 mismatches=0 errors=0 orphans=0`, EXIT 0, `l1` 0.9 s / `l2` 0.8 s, both
  `survivors=0 tmpleft=0`. Receipt: `.ufo/waves/round-84/w1/S84Scribe/receipts/c2-exec-candidate-receipt.txt`.
- **The landed bytes, re-verified independently.** The L1 landed `tools/souji-vault-verify.sh` sha256
  `030fa10d5b7d312c4bc2ef759495c124616b9130f6cd0a52da7be2bdbb6ef41d` (`1f49b3a7`). I copied those exact bytes to
  scratch and re-ran the frozen counter: `SUMMARY rows=22 mismatches=0 errors=0 orphans=0`, EXIT 0, `l1` 0.8 s /
  `l2` 0.6 s, both `survivors=0 tmpleft=0` — the same summary and the same per-row verdicts as the L1's own
  `census/round-84/records/c2-after.txt` (which reads `l1` 0.7 s / `l2` 0.6 s; the seconds differ by run, the
  verdicts do not). Receipt: `.ufo/waves/round-84/w1/S84Scribe/receipts/c2-landed-tool-receipt.txt`. The landed
  bytes use the whole-file stat read with a **content** guard (`[ -n "$now" ] || continue`, no `||` on the read
  itself), which is the shape that avoids F1 below.

## Gates

- C1 before arm: **green as specified** (`killed_r83=0`, EXIT 0) — my run matches the committed receipt.
- C1 after arm: **green as specified** (`killed_r84=5`, EXIT 0).
- C2 after arm on the executor's candidate: **green as specified** (22/0/0/0, EXIT 0, l1/l2 survivors 0).
- C2 after arm on the **landed** bytes (`030fa10d…`): **green as specified** (22/0/0/0, EXIT 0) — my independent
  re-run reproduces the L1's receipt.
- C2 after arm on the **reference** bytes currently in the wave directory: **RED** — see finding F1.

## Findings

### F1 — HIGH (found by me; now the lane's lesson M2, and the landed bytes avoid it). The whole-file read's exit status is not a guard

`.ufo/waves/round-84/w1/RefC2/souji-vault-verify.sh` (sha256
`a810acaf438cd6deee83a98f0db5b9697a5b5029f3126c207929c391f1130b25`) measured
`SUMMARY rows=22 mismatches=5 errors=0 orphans=5`, **EXIT 1** through the frozen counter — the two late rows
(`l1`, `l2`), the two job-control fork rows (`m1`, `m2`) and the 24-descendant job-control row (`d24-monitor-group`)
red. Receipt: `.ufo/waves/round-84/w1/S84Scribe/receipts/c2-refc2-current-bytes-FAILING.txt`.

**Cause.** The bytes use the whole-file stat read for the identity re-reads and guard it on the read's **exit
status**:

```bash
{ IFS= read -r -d '' now < "/proc/$k/stat"; } 2>/dev/null || continue
```

`IFS= read -r -d ''` reads the whole file and then hits EOF, and the bash manual's `read` node says "The exit
status is zero, unless end-of-file is encountered" — so the read **always** returns 1 and the `|| continue` skips
**every** descendant. The freeze therefore never reaches a descendant: nothing is SIGSTOPped, nothing is SIGKILLed
by the tree walk, and only the group kill remains. That is exactly the failing row set.

**Reproducer (minimal).** `.ufo/waves/round-84/w1/S84Scribe/receipts/repro-read-d-status.sh` — one `read` and one
exit status; output `repro-read-d-status.out` ("SKIPPED: read -d '' returned non-zero (content was read: 337
bytes)").

**Fix, measured.** Guard on the *content* instead of the status (`|| true` plus `[ -n "$now" ] || continue`): the
same bytes then read `rows=22 mismatches=0 errors=0 orphans=0`, EXIT 0 — receipt
`.ufo/waves/round-84/w1/S84Scribe/receipts/c2-fix-candidate.txt`.

**Status: the L1 landed the fix, and recorded this as lesson M2.** `tools/souji-vault-verify.sh` (sha256
`030fa10d…`) reads the stat file whole and tests the **content** (`[ -n "$now" ] || continue`), with no `||` on the
read itself; my independent run of those bytes reads 22/0/0/0 (receipt
`c2-landed-tool-receipt.txt`). `corpus/lessons/round-84.md` M2 names the defect and its fix, and the wave table
credits this seat with "an independent reproducer for the `read -d ''` guard defect".

**Why the committed pre-freeze receipt did not catch it.** `census/round-84/records/c2-reference-prefreeze.txt`
measures sha256 `66f535273bc1523175c11cdace36a7de189c98dc50ac016a3e591c04fbbf5e73`, which is the same file **before**
the whole-file-read edit; I re-ran those bytes and they read `rows=22 0/0/0`, EXIT 0
(`receipts/c2-prefreeze-bytes-rerun.txt`). The wave's `RefC2` file changed under the receipt. The lesson's M5
records the same chronology hazard from the other side: two seats scored `RefC2` sha256 `a810acaf…` while the L1
was rewriting the reference, so their numbers describe bytes no one filed. **A receipt names the digest it
measured; a wave-directory file can move under it.**

### F2 — MEDIUM. The two read shapes fail in opposite directions, and both are silent

Measured on this host (`receipts/d5-read-shapes.txt`, `receipts/d5-read-shapes-measure.sh`):

| shape | newline-comm pid | normal pid |
|---|---|---|
| first-line read | status 0, 10 bytes, **2 fields** after the strip → the `>= 20` guard fails → the pid is skipped | status 0, 321 bytes, 50 fields → fine |
| whole-file read | status **1**, 319 bytes, 50 fields → the strip works, the status says failure | status **1**, 322 bytes, 50 fields → the status still says failure |

So the r83 spot-check's routed defect **D5** ("read each stat whole" was true of the map pass only) and F1 are the
same guard read two ways. A first-line read skips exactly one hostile descendant (one whose `comm` carries a
newline — r83 spot-check §2 measured that such a descendant is still reached by the group kill, which is why no
frozen row fails today). A whole-file read guarded on the status skips **every** descendant and disables the freeze
entirely.

**Status.** The landed bytes use the whole-file read with a content guard, so D5's hazard is closed in the landed
tool — but the lesson records it as **M4**: "the whole-file stat re-check (the r83 D5 fix) carries no row — its
first-line variant scores 22/22 green because no frozen row has a comm with a newline"
(`census/round-84/records/c2-mutants-on-filed.txt`, M4 survives), and routes a comm-newline row to the next round.
So the D5 fix is real but unrowed, and the round says so rather than claiming it.

### F3 — informational (now the lane's lesson M1). The `latefork` stub's own history is part of the claim's evidence

`plans/round-84.md` A0.1 records that the first stub deferred its own trap (a foreground `sleep` inside the
busy-loop), so the tool's 0.1 s KILL sweep killed the CLI before the trap ran and the row measured the stub — the
before receipt read `survivors=0` on both late rows, a **false green**. The corrected stub busy-loops on the `:`
builtin. My before-arm re-measurement of the r83 bytes is consistent with the committed control
(`survivors=1` on each late row), so the frozen before is sound. The lesson records this as M1. The drafts therefore
describe the stub's bytes rather than assuming the stub is inert.

### F4 — informational (integrated by the L1 as amendment A7). The `NF-Q` row has no mutant of its own

`NF-Q` (a real `w2/` prefix that drops the token's suffix) is a false row the r84 population adds, but none of the
five frozen single-edit mutants is killed by it — the five killing rows are NF-L, NF-L2, TF9/TF10, TF8/TF9/TF10/NF-P
and NF-M. `NF-Q` is carried as a shape decoy, not as a clause binder. The landed section
(`corpus/knowledge/own-tree-pointer-binding.md`, "Bounding a population, not just a rule (r84)") lists the criterion
as "one FALSE row per clause the rule enforces (digest, round, shape set, suffix depth, non-wave dir)" — five
clauses, five binders — and does not claim `NF-Q` as a binder, so the landed text is consistent with this
measurement. **The L1 integrated this finding as `plans/round-84.md` A7 ("C1: NF-Q carries no kill
attribution"), citing `S84Scribe.md` F4 by name** and stating the five named kills as m6↔NF-L, m7↔NF-L2,
m8↔TF9/TF10, m9↔TF8/TF9/TF10/NF-P, m10↔NF-M — the same attribution this seat measured independently, row by row.

### F5 — informational. The r84 population's `w2/`-shape rows and the "no recorded move" limit

TF9/TF10 use `a2w1/` and `assimilation/`, directories the lane really has (`census/round-83/records/wave-dirs.txt`:
`w1/` 65, `w2/` 19, `assimilation/` 4, `w3/` 1, `a2w1/` 1 — S331, with S333 correcting the provenance to a
working-tree count), but **no recorded ledger move has used those layouts** (r83 A4). The drafts therefore call
them shape rows, not move rows, and say so explicitly. The landed text states the limit in the round's own frozen
wording (`census/round-84/preregistration.txt` C1 "Stated limits (frozen)"), so this is covered there too.

## Touched surfaces

- **Written** (all under my seat directory): `.ufo/waves/round-84/w1/S84Scribe/` — three draft files, this report,
  and `receipts/`.
- **Read-only**: the lane's corpus, `census/round-84/*`, `plans/round-84.md`, `corpus/QUALITY.md`,
  `corpus/SOURCES.md`, `corpus/lessons/round-83*.md`, and the sibling seats' wave directories (read only; no
  sibling file was edited).
- **Not touched**: `corpus/knowledge/*.md`, `corpus/QUALITY.md`, `census/round-84/*`, `tools/*`, `MANIFEST.json`,
  `.ufo/state/*`, `.scratch/*`, `.ufo/watchdog.log`, any fleet-root file. No git/jj command that mutates state was
  run; the only git calls were read-only (`log`, `show --stat`, `status --short`, `ls-files`, `diff` of two files).
- **Scratch**: `/fast/scratch/hyaku/souji-r84/S84Scribe/` — removed before yielding (see below).

## Out of scope (noted, not done)

- Landing any file (the L1 integrates; it has since landed `4557fc71` and `1f49b3a7`).
- Choosing which candidate bytes the L1 lands, and re-running the after arm on them (the L1's measurement).
- The r84 **source rows**: the round's source seat (S84ScoutSources) landed **S334** (signal(7): SIGSTOP cannot be
  caught, blocked or ignored), **S335** (the own-work clause-kill receipt row) and a rejected **S336**, per the
  lesson's wave table and `corpus/SOURCES.md`. The drafts as written cite only the committed rows **S331, S332,
  S333** and carry an explicit placeholder line for the L1 to add the new r84 ids; the landed sections name S334
  and S335. **No source id was invented by this seat.**
- The bash `read` exit-status quote the drafts lean on comes from the capture S325/S329 already cite
  (`census/round-79/srcs/bash.info.gz-5.3`, sha256 `cde1a336…0588f`); the located quote is in
  `receipts/bash-read-exit-status-quote.txt`.
- The r83 routed items that remain open after this round (the census-in-tree branch; the C2 pid-reuse,
  parent-before-child, `termign-fork`, `p5-late-term` and `strace`-settle rows; the comm-newline hostile-CLI row —
  the last is F2 above, recorded by the L1 as lesson M4 with the row routed on). The drafts state the limits; they
  do not claim those rows.

## Method notes

- Every measurement used the frozen instruments only: `census/round-84/c1-clause-battery.py`,
  `census/round-84/c1-false-row-harness.py`, `census/round-84/c2-late-fork-counter.py`, the two pinned
  populations and the pinned mutants file. No population row was edited; no instrument was modified.
- All `--work` directories were empty, created outside `/tmp`, and the battery's own output file was written
  **outside** the `--work` directory (a shell redirect into `--work` makes it non-empty and the battery refuses it —
  `BATTERY-FATAL: --work … is not empty`; that is a harness guard, worth knowing).
- The tool-under-test copies were made into scratch and given mode 0755; the lane's `tools/souji-vault-verify.sh`
  was never modified.
- **No tool was installed or upgraded for this seat** (none was needed): bash 5.3.20, coreutils 9.12, git 2.56.0
  and Python 3.14 as installed on this host were sufficient.
- Cleanup: `rm -rf -- /fast/scratch/hyaku/souji-r84/S84Scribe` after the receipts were copied into
  `.ufo/waves/round-84/w1/S84Scribe/receipts/` (16 files, verified present after the removal).

## Reproduce

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin
D=/fast/scratch/hyaku/souji-r84/recheck; mkdir -p "$D"
# C1 after (expect: rows=44 mismatches=0, killed_r84=5, EXIT 0)
python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py \
          --work "$D/c1a" --only r84 --expect-killed 5
# C1 before (expect: rows=36 mismatches=0, killed_r83=0, EXIT 0)
python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py \
          --work "$D/c1b" --only r83
# C2 on the LANDED tool (expect: rows=22 mismatches=0 errors=0 orphans=0, EXIT 0)
cp tools/souji-vault-verify.sh "$D/tool.sh"; chmod +x "$D/tool.sh"
python3 -B census/round-84/c2-late-fork-counter.py --tool "$D/tool.sh" --work "$D/c2"
# C2 on the wave's RefC2 bytes (expect: rows=22 mismatches=5 errors=0 orphans=5, EXIT 1)  <- finding F1
cp .ufo/waves/round-84/w1/RefC2/souji-vault-verify.sh "$D/ref.sh"; chmod +x "$D/ref.sh"
python3 -B census/round-84/c2-late-fork-counter.py --tool "$D/ref.sh" --work "$D/c2ref"
# the read guard, minimally (<expect: SKIPPED, exit 3>)
.ufo/waves/round-84/w1/S84Scribe/receipts/repro-read-d-status.sh
```
(The battery refuses a non-empty `--work`, so redirect its output **outside** `--work`.)
