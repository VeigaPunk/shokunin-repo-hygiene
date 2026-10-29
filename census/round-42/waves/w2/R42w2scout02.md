# R42w2scout02 — adjacency and downstream check (souji round 42, wave 2, falsify)

Seat: R42w2scout02 (scout). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Base `bf618f6c5c09d302994871c94903abbea2deb60d`; freeze `afe17f416eec04dcf3f480b580a8f928de61d19d`; landed tip under attack `3105a63b23481fccf7df58e74d14a6681e0ea0c8`. Read-only sweep of `/home/vgpnk/Projects/shokunin` for consumers of the artifacts r42 changed. Milestone: r42 falsify — judged on adjacency.

## What r42 changed (the attack surface)

`git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat bf618f6c5c09d… 3105a63b2348… -- tools/souji-freeze-check.py` →
`tools/souji-freeze-check.py | 209 +++++++++++++++++++++++++++++++++++++-------` / `1 file changed, 179 insertions(+), 30 deletions(-)`.

New in the landed tool (from the diff, observed): finding classes `KEY-DUPLICATE` (first-wins reading gone, one finding per duplicated key), `HEADING-MALFORMED` (C0, the line opens no claim), `COUNTER-SYMLINK` / `POPULATION-SYMLINK` (no digest comparison), a widened `DISPATCH-BEFORE-FREEZE` (every file under `.ufo/waves/round-<N>/` at any depth whose basename contains `-dispatch` or `.ready`, or ends `-spec.json` / `-results.json`, first added at FREEZE-REV or an ancestor), and a `--selftest` mode printing `SELFTEST cases=<n> pass=<p> fail=<f>` (n ≥ 12). The tool remains read-only on `--root`. Per the frozen preregistration (§6 causally separable) the r42 landed set otherwise touches `tests/fixtures/r42-drift-conditions.py`, `census/round-42/*`, corpus/SCORECARD/LOG/SKILL bookkeeping — `tests/fixtures/r41-refusal-sites.py` and `census/round-41/*` are unchanged by r42.

## Consumer table

| consumer path (fleet root `/home/vgpnk/Projects/shokunin` unless lane-prefixed) | what it uses | can r42 change it? | evidence |
|---|---|---|---|
| `MANIFEST.json:31879-31885` (fleet closure entry, souji round 41, written by the closure integrator per `scripts/hyaku/closure-prompt.md` step 5) | capability strings `freeze check (tools/souji-freeze-check.py)`, `refusal-site battery (tests/fixtures/r41-refusal-sites.py)`, `record-order fixture (tests/fixtures/r41-drift-record-order.py)`, `corrections counter (census/round-41/c1-counter.py)`; `report: .ufo/reports/round-41/souji.md` | **No.** Descriptive name strings for landed r41 capabilities; paths unchanged; the r41 capability re-verifies green at the tip (run 2 below). Closure duty 2 binds gates to committed evidence and says "never execute a sibling's gate" (`closure-prompt.md` step 2), so the stricter tool never runs inside a closure. | grep sweep 1/7 below; `closure-prompt.md:22-24` ("Where the claim rests on a lane-owned gate or selftest … verify its committed evidence … — never execute a sibling's gate") |
| `.ufo/reports/round-41/souji.md:5,52` (closed round-41 fleet report) | names the tool as the landed C2 capability; cites "SKILL.md Gate registry rows `souji-freeze-check`…`r41-c1-corrections`" | **No.** Both statements remain true at the tip: the tool still reads the r41 prereg clean (`SUMMARY claims=3 findings=0`, run 2), and the cited row range still exists (r42 rows were appended after `r41-c1-corrections`, SKILL.md:287-292). | grep sweep 1/7; run 2 |
| `souji-shokunin/SKILL.md:282` — gate row `souji-freeze-check` (r41). Consumers: the fleet closure integrator (evidence-verifies, never runs it), every future souji closure, and any souji prereg author writing to the grammar it documents | the r41 verdict map (14 finding classes), the pinned command, and the named-limits cell | **Verdict for its pinned invocation: no** (re-measured exit 0 at tip, run 2). **Row text: yes — now stale in three cells (finding F1).** The exit-1 class list omits `KEY-DUPLICATE`, `HEADING-MALFORMED`, `COUNTER-SYMLINK`, `POPULATION-SYMLINK`; the named-limits cell reads "duplicate keys read first-wins, a malformed `## C` heading is dropped, an unlisted dispatch file name is not checked" — all three abolished by r42. Any future prereg with a duplicated key that the r41 tool read green now reads exit 1 (the intended stricter grammar; the r42 prereg itself passes, `real ok`). Tracked file — not edited by this seat; a finding for the L1. | verbatim row read (`:raw:282`); tool diff; run 1/2 |
| `souji-shokunin/SKILL.md:283-286` — r41 counter rows `r41-freeze-check-cases`, `r41-refusal-sites`, `r41-drift-record-order`, `r41-c1-corrections` (commands `census/round-41/c2-counter.py`, `c3-counter.py`, `r1-counter.py`, `c1-counter.py`) | evidence-verification targets at closure; the r41 c2-counter scores `tools/souji-freeze-check.py` **at `--rev`** | **No.** r42 changed none of the four counters or their fixtures. The r41 C2 case table (21 cases) is embedded verbatim in the r42 counter's 37 and all 21 r41 case lines read PASS at the tip (run 1: `case-clean` … `case-dup-target` PASS), so re-scoring the tip tool with the r41 table stays green. [INFERENCE for the r41 counter binary as a whole — its cases are a subset of the 37 I ran; I did not invoke the r41 counter.] | SKILL.md:283-286 read; run 1 case list |
| External invokers of `tools/souji-freeze-check.py` | — | **None exist.** Fleet-wide grep excluding souji's lane and `.jj/` finds the string only in `MANIFEST.json:31880` and `.ufo/reports/round-41/souji.md:5` (citation strings). No sibling script, fleet `scripts/`, closure prompt, or template invokes it. | grep sweeps 1, 6, 7 |
| External consumers of `tests/fixtures/r41-refusal-sites.py` | — | **None** (`MANIFEST.json:31881` string only). r42 did not touch the fixture. | grep sweep 2 |
| External consumers of `census/round-41/c*-counter.py` | — | **None.** All non-souji hits of `round-41/c…-counter` are kaidoku's own `kaidoku-shokunin/tools/round-41/{c1,c2}-counter.py` (same naming convention, own lane, squashfs-carrier surface) — a name-pattern collision, zero invocation of souji's counters. | grep sweep 4 |
| External readers of the `CORRECTION-DE` marker | — | **None.** Fleet-wide grep excluding souji: zero matches. The marker is read only by souji's `census/round-42/c1-counter.py`. | grep sweep 3 |
| External citers of the new row ids (`r42-c1-counter`, `r42-c2-counter`, `r42-freeze-check-selftest`, `r42-c3-counter`, `r42-drift-conditions`, `r42-r1-counter`) | — | **None** (one coincidental string hit, see observations). | grep sweep 5 |

## Name-collision family (adjacency record; verdicts cannot change — different CLIs, different inputs, no invocation in either direction)

- `chousa-shokunin/tools/freeze-check.py` — own wave-payload checker (`--claims/--dispatch/--spec/--ready`; checks `CLAIMS_NONEMPTY`, `CONTEXT_DIGEST`, `BODY_RENDER`, …) with its **own `--selftest`** (10 selftest mentions in the file; evidence `chousa-shokunin/corpus/evidence/round61/freeze-check-selftest.txt`, cited at `.ufo/reports/round-61/chousa.md:65`). r42 gives souji's tool a `--selftest` too, so the generic name now carries a self-test mode in two lanes. No code, input, or finding-class overlap (souji's classes are prereg-grammar classes). Collision surface widened; verdicts unaffected. The r41 connector's discipline holds: souji's tool is the souji-prefixed one.
- `kasegi-shokunin/corpus/instruments/freeze-check.py` — own claims-v2 replay at a frozen base, own `--selftest`. The kasegi round-42 report (`.ufo/reports/round-42/kasegi.md:101-103`) describes its own `corpus/instruments/r42-closure.sh --selftest` — same round number, zero souji coupling.
- `kengaku-shokunin/plans/attrib_probe.py` subcommand `freeze-check --double-read` (evidence `kengaku-shokunin/corpus/evidence/attrib-r22-opencode-trials.log:8,46,71`, `attrib-r22-legs-hyper.log:147`, `attrib-r23-stream-trials.log:429`) — name collision only.
- `mori-shokunin/tools/mori-freeze-order.py` and `mado-shokunin/quality/check-freeze-order.py` — name family, no coupling (existence verified by glob).
- `kumitate-shokunin/scripts/plan-before-ready.sh` (header lines 12-13) — independently re-derives the "oldest commit that adds a top-level `.ufo/waves/round-R/*.ready` (fallback `*-dispatch.json`)" marker rule for kumitate's own rounds. souji's widened `DISPATCH-BEFORE-FREEZE` now uses the same artifact-name family (`-dispatch`, `.ready`, `-spec.json`, `-results.json`) inside prereg checking. No invocation in either direction; verdicts independent. Documented divergence risk: if kumitate renames its markers, souji's widened list does not follow. Matches r41 `R41connector01.md:47-49` ("cite, don't fork").

## Sibling open reports vs souji capabilities r42 changed

- `.ufo/reports/round-42/` holds 13 sibling reports (tabi, kasegi, kaidoku, tsukuroi, kengaku, mado, kama, tameshi, mori, chousa, kake, kumitate, kotodama) — no souji.md yet (souji r42 closure not filed). Grep for `souji` in that directory: the only hit is `tabi.md:175` — "`w1/ConnSiblingProc` refreshed the kama/souji overlap (nothing new to absorb)". **No sibling round-42 report claims a souji capability that r42 changed.**
- All-rounds grep of `.ufo/reports` for souji-capability wording (`souji.freez|souji SKILL|souji gate|souji tool|souji lane|souji's`): hits only in souji's own reports (rounds 12/16/17/19/23/41), mori misroot notes about souji report files (rounds 20/22 — file hygiene, not capabilities), chousa r61 (its own freeze-check selftest line), kumitate r64 (cites souji's colocation ground, not a tool). Nothing open claims the freeze-check, refusal battery, r41 counters, gate rows, or the CORRECTION-DE marker.
- `.ufo/l0-questions.md` souji rows (r16, r17 ×2, r18 ×2, r20, r40 ×2, r41): none concerns the r42 artifacts.

## Sibling interference events relevant to souji r42 verdicts (downstream findings)

- **F2 — kama round-64 `pkill` incident** (`.ufo/l0-questions.md:208`, kama r64): the kama L1 ran `pkill -f mut-.*\.py` to stop its own scratch mutant job; the pattern also matched souji-r42 wave-1 seat mutant processes (`R42w2critic07`, `R42w2reviewer05`, `R42mutationtester03`) under `/fast/scratch/hyaku/souji-r42/` and sent SIGTERM; "some souji r42 mutant runs may have died and been scored as dead mutants … flagged so the souji r42 closure can discount a spurious de[ath]". Can change a souji r42 verdict: yes, potentially — a SIGTERMed process is not a mutant kill; any wave-1 kill claim from those three seats whose run overlapped the pkill window is unreliable and should be discounted or re-run at closure. Whether the L1's landed C3 measurement (`census/round-42/records/c3-after.txt`) overlapped the window is not determinable from this seat.
- **Observation — souji w2 scratch visible to sibling crawls**: `mado-shokunin/.ufo/waves/round-56/w2/R56W2CritC2Cheat/receipts/crumbs-e-crawl-nobwrap.txt:11,49,81,…` lists `/fast/scratch/hyaku/souji-r42/R42w2critic04/work/base-r42-drift-conditions` and `R42w2reviewer10/c3b/souji-r42-c3…` among crawled process roots (a mado seat's read-only runtime census). No verdict coupling; recorded because it shows souji w2 scratch paths were observable fleet-wide while this wave ran.

## Commands run (verbatim) and observed output

Greps (grep tool over `/home/vgpnk/Projects/shokunin`, `!**/.jj/**;!**/souji-shokunin/**` exclusions where stated, hidden+gitignore off):

1. `souji-freeze-check` → 2 files: `MANIFEST.json:31880`; `.ufo/reports/round-41/souji.md:5`.
2. `r41-refusal-sites` → 1 file: `MANIFEST.json:31881`.
3. `CORRECTION-DE` → no matches.
4. `round-41/c[0-9a-z]*-counter` → `MANIFEST.json:31883` + kaidoku's own `tools/round-41/{c1,c2}-counter.py` tree (own lane, no souji path).
5. `r42-c[0-9]-counter|r42-freeze-check-selftest|r42-drift-conditions|r42-r1-counter` → 1 file: `mado-shokunin/.ufo/waves/round-56/w2/R56W2CritC2Cheat/receipts/crumbs-e-crawl-nobwrap.txt` (coincidental scratch-dir strings).
6. `r41-c1-corrections|r41-freeze-check-cases|r41-drift-record-order|r41-c2-counter|r41-c3-counter` → `MANIFEST.json:31882-31883`; `.ufo/reports/round-41/souji.md:52`.
7. `souji` in `templates/` → no matches. `SKILL` in `templates/`+`scripts/` → generic load-order and closure references only (`scripts/hyaku/closure-prompt.md:93` "Never edit lane-authored files (report, SCORECARD, LOG, lessons, SKILL, PROVINCE)"; `lane-addendum.md:190-194` per-lane SKILL load order).
8. `souji` in `.ufo/reports/round-42/` → `tabi.md:175` only.

Git/read-only:

9. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat bf618f6c5c09d302994871c94903abbea2deb60d 3105a63b23481fccf7df58e74d14a6681e0ea0c8 -- tools/souji-freeze-check.py` → `1 file changed, 179 insertions(+), 30 deletions(-)`; the class-grep of the diff is quoted under "What r42 changed".

Re-measurement at the tip (this seat, uid 1000, scratch `/fast/scratch/hyaku/souji-r42/R42w2scout02`, `TMPDIR` set explicitly):

10. `TMPDIR=/fast/scratch/hyaku/souji-r42/R42w2scout02 python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --scratch /fast/scratch/hyaku/souji-r42/R42w2scout02/c2` → 37 case lines all `PASS` (`case-clean` … `case-unresolved-rev`, `case-absent-prereg`); then verbatim:
    ```
    real ok rc=0 findings=0 summary=(3, 0)
    retro red rc=1 findings=19 summary=(3, 19)
    retro_clean ok rc=0 findings=0 summary=(3, 0)
    selftest ok rc=0 summary=(31, 31, 0)
    SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb
    ```
    exit 0, wall 10.96 s — matches the frozen target and `census/round-42/records/c2-after.txt`. (First attempt without creating the scratch dir read `REFUSAL COULD-NOT-EVALUATE: --scratch (or TMPDIR) must name a directory`, exit 2 — the counter's refusal contract, not a defect.)
11. r41 SKILL gate-row command at the tip: `TMPDIR=… python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --prereg census/round-41/preregistration.txt --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8` → `SUMMARY claims=3 findings=0`, exit 0.

## Verdict

**Adjacency: clean.** No sibling lane, fleet script, closure prompt, template, or open sibling report invokes — or reads verdict-relevant output of — souji's changed tool, the r41 refusal fixture, the r41 counters, the souji SKILL gate rows as commands, or the `CORRECTION-DE` marker. The only fleet-level consumers are closed citation strings (`MANIFEST.json` r41 entry, `.ufo/reports/round-41/souji.md`), and both stay true at the tip (re-measured, run 11). The r42 stricter grammar cannot flip any external verdict because no external invoker exists, and it demonstrably keeps every prior internal verdict green (`retro_clean=ok`; r41 gate row exit 0 at tip; all 21 retained r41 cases PASS).

Findings for the L1 (all report-only; nothing outside my seat dir and this report was written):
- **F1** `souji-shokunin/SKILL.md:282` r41 row `souji-freeze-check` is stale against the landed tool: its exit-1 class list omits the four new classes and its named-limits cell asserts three behaviours r42 abolished ("duplicate keys read first-wins", "a malformed `## C` heading is dropped", "an unlisted dispatch file name is not checked"). Pinned invocation still green; documentation drift only.
- **F2** kama r64 `pkill -f mut-.*\.py` SIGTERMed souji r42 w1 mutant runs of `R42w2critic07`/`R42w2reviewer05`/`R42mutationtester03` (`.ufo/l0-questions.md:208`); discount or re-run their kill claims at closure.
- **F3** the `freeze-check` name collision now includes a `--selftest` mode in both souji and chousa (kasegi's instrument too); no coupling; keep the souji-prefixed discipline.
- **F4** kumitate's marker vocabulary and souji's widened DISPATCH list are independent implementations of the same name family; divergence risk documented, no fork.

Tooling installs: none (system `python3` and `git` only; no tool added or upgraded). Scratch `/fast/scratch/hyaku/souji-r42/R42w2scout02` removed before yield. Report trailer: `.ufo/waves/round-42/w2/R42w2scout02.md`.
