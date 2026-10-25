# ConnSiblings — souji r25 w1 sibling-overlap scan (seat L1Souji25.ConnSiblings-2)

## Status
STATUS: PASS — every sibling PROVINCE.md/SKILL.md was scanned read-only. No sibling claims `git repo structure` or common-git-dir manifest ground (C3 is clear). One real Q57 overlap: chousa keeps its own quarantine-slice verdicts over the same campaign register, and bare register ids collide across lanes. R3 has parallel wording in three lanes and no ownership conflict. Nothing absorbed, no sibling file touched, no scratch created.

## Evidence
Revision: souji `refs/heads/master` = HEAD = `6e4737eab43d8fde1b85eb9f57023d29046705b4` (`git rev-parse HEAD refs/heads/master`). Siblings were read from the live tree (read-only), with no pins.

1. C3 keyword count over `<lane>/PROVINCE.md` and `<lane>/SKILL.md` for 20 sibling dirs (mori tsukuroi kagi kumitate chousa revenger kotodama tabi mado kasegi kengaku kotoba kake kama tameshi kaidoku lore game-dev-3d game-dev-2d audio):
   `rg -n -i -c 'repo structure|repo-structure|common.?git.?dir|git-common-dir|commondir|common-dir'` → **0 hits in every sibling** (no `C3core` line printed for any lane).
2. The same pattern plus `git.common.dir|common_dir|refs/jj/keep` over every sibling `corpus/knowledge/` → 2 hits: `kumitate-shokunin/corpus/knowledge/agent-isolation-substrates.md:98` and `mado-shokunin/corpus/knowledge/tripwire-precision-r20.md:70`.
3. Fleet main-repo lanes (`protocol`, `aggregator`, per `PROTOCOL.md:147` "`protocol` and `aggregator` for the two main-repo lanes"): the C3/Q57/R3 pattern over `PROTOCOL.md PROTOCOL-APPENDIX.md AGENTS.md README.md` → only `PROTOCOL.md:394` (worktree comparability), `PROTOCOL-APPENDIX.md:36`, `AGENTS.md:74` (jj convention).
4. Q57 collision: `comm -12` of the chousa `corpus/evidence/round42/quarantine-verdicts.tsv` ids against the souji `HEAD:census/round-24/records/slice-verdicts.tsv` ids → `S114`. The register (`/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md`, read only) has `:53` `` `chousa` `` round4 S114 (sinomed), `:171` `` `souji` `` round1 S114 (git-scm git-prune), and `:183` `` `tabi` `` round1 S114.
5. souji's own lane registry `HEAD:corpus/SOURCES.md:134` S114 is statx(2), not git-prune. The TSV header "campaign register ids … NOT lane registry ids" is therefore correct. The register key is (lane, id), not id.

## Findings — overlap table

| sibling | surface | overlap? | evidence pointer (path:line, quote) | adjudication |
|---|---|---|---|---|
| mori | C3 jj colocation | no: own revision-provenance reads | `mori-shokunin/PROVINCE.md:108` "jj-colocated history reads use the resolved" | report only; this is mori's branch-anchor rule, not structure measurement |
| tsukuroi | C3 jj/HEAD | no: revision pin | `tsukuroi-shokunin/SKILL.md:1913` "Under jj, git `HEAD` is the working-copy parent: measure the branch tip" | report only |
| tsukuroi | R3 receipt digest | adjacent (prior art) | `tsukuroi-shokunin/SKILL.md:2670` "the receipt header (revision, tool revision, tool sha256) is the evidence" and "runs a tracked tool from a sandbox clone at the tool revision" | report, don't absorb. tsukuroi binds the executed program by construction (it runs from a clone at the tool revision); souji R3 says souji's digest "does not bind the executed program" (`souji-shokunin/SCORECARD.md:218`). This contrasts with souji's wording and does not conflict with it |
| kagi | C3 git admin paths | no | `kagi-shokunin/SKILL.md:733` "Revision data paths exclude Git/JJ administrative components and" | report only; kagi's own input guard |
| kumitate | C3 linked worktrees / common dir | adjacent (knowledge, not ground) | `kumitate-shokunin/PROVINCE.md:21` "Isolation substrates for parallel agents (git worktrees, harness isolation backends)"; `corpus/knowledge/agent-isolation-substrates.md:98` "`$GIT_COMMON_DIR` (S027: `.git/info/exclude` is shared across linked worktrees)" | report only. kumitate's frontier is seat containment, not size/structure, and it says "jj workspaces are not demonstrated" (`:21`). Possible source overlap: kumitate S063/S027 vs souji S124/S125. Each lane keeps its own registry rows; do not cross-cite ids |
| kumitate | Q57 verdict vocab | no | `kumitate-shokunin/SKILL.md:355` "**Verdict vocabulary.** `GateDecision` (`gate.rs:15`): admit iff ≥1" | report only; this is a gate-admission vocabulary, not slice verdicts |
| kumitate | R3 receipt digest | adjacent | `kumitate-shokunin/SKILL.md:618` "contract `kumitate-receipt-attest-v3`" | report only; a different instrument (receipt tamper/replay), with no claim on souji wording |
| chousa | C3 | no | 0 C3/worktree/jj hits (Evidence 1) | — |
| **chousa** | **Q57 slice verdicts** | **YES: same external register, parallel verdict table** | `chousa-shokunin/SKILL.md:107` "`python3 tools/quarantine-check.py {slice,examine,verdict,digests}`"; `tools/quarantine-check.py:2` "re-derive chousa's absent-defect-register quarantine slice"; `:291-294` vocabulary `present`/`absent`/`mixed`/`unverifiable`; `corpus/evidence/round42/quarantine-verdicts.tsv:18` "S114	absent" | report, don't absorb. Both lanes classify rows of `absent-defect-register.md` with different vocabularies (souji: accepted/unverifiable/refused/present, `census/round-24/records/slice-verdicts.tsv:1`). Bare `S114` names chousa `absent`, souji `accepted` and a tabi row. No verdict contradicts another (they are different rows), but any id-only join conflates them. See the proposed move |
| revenger | C3 | no | `revenger-shokunin/SKILL.md:368` "none runs `git`/`jj` mutations, none installs software." | — |
| kotodama | C3 worktree | no | `kotodama-shokunin/SKILL.md:628` "isolated repo export — a history-retaining copy (clone or worktree; the" | — |
| tabi | C3 jj colocation | no: own pin rule | `tabi-shokunin/SKILL.md:1902` "The lane is jj-colocated: git `HEAD` is jj-owned, normally detached, and may name an empty or" | report only |
| mado | C3 `refs/jj/keep` | adjacent (write-detection, not structure) | `mado-shokunin/corpus/knowledge/tripwire-precision-r20.md:70` "the working copy is snapshotted before the dry-run return"; `SKILL.md:1938` "`vcs_write` (jj mutating verbs, jj reads without `--ignore-working-copy`, git write" | report only. mado treats a keep-ref write as a VCS write. souji C3 case `colocated-vs-plain` simulates keep refs in /var/tmp without jj, which is consistent with that |
| kasegi | C3/Q57/R3 | no | `kasegi-shokunin/SKILL.md:989` "append-only mission state machine + dispatcher heartbeat + hunter intake" (bounty ledger) | — |
| kengaku | R3 receipt digest | no | `kengaku-shokunin/PROVINCE.md:116` "P1 receipts sha256-pinned" | report only; this pins receipts, not tool-to-argv binding |
| kotoba | all | no | 0 C3/worktree/jj hits; Q57/R3 hits are unrelated (`slice(0, _8n-1)`, `SKILL.md:28`) | — |
| kake | R3 receipt digest | no | `kake-shokunin/SKILL.md:538` "disposable clone commits only; never lane Git/jj writes" (receipt-replay-matrix row) | report only; kake's own replay gate makes no tool-digest wording claim |
| kama | Q57 vocab | no | `kama-shokunin/SKILL.md:11` "Verdict vocabulary is shared with" `tools/kama-probe.sh` | — |
| kama | C3 jj | no | `kama-shokunin/SKILL.md:581` "Order of operations under jj: commit through the lane helper first, then run the" | — |
| tameshi | C3 git discovery | adjacent (source) | `tameshi-shokunin/SKILL.md:1818` "repository discovery and `GIT_*` environment), S061 (jj leaves Git `HEAD`" | report only |
| tameshi | R3 receipt digest | adjacent (parallel limit wording) | `tameshi-shokunin/SKILL.md:1695` "digest binding verifies the bytes read, not filesystem-origin authenticity"; `:1685` "never a re-execution of stored argv and" | report, don't absorb. This matches souji R3's direction (a digest is not execution). Wording is independent, and no ownership conflict exists |
| kaidoku (not in task list) | C3 jj | no | `kaidoku-shokunin/SKILL.md:570` "The lane is a colocated jj workspace (jj 0.45.1). jj usually leaves Git HEAD" | — |
| protocol (main repo) | C3 | no | `PROTOCOL.md:394` "run over a moving worktree is not comparable to one over the cited commit"; `AGENTS.md:74` "Lane repos are Jujutsu-colocated (`HYAKU_VCS=jj`)" | report only |
| protocol (main repo) | Q57 registry tally | adjacent (instrument owner) | `AGENTS.md:15` "Source-registry census: `scripts/sources-census.sh {census,validate,overdue,shared,selftest}`" | report only. souji's registry tally uses the fleet tool (`souji-shokunin/SCORECARD.md:23`). Q57 must not claim that instrument as lane-owned |
| aggregator (main repo) | Q57 surface (corpus/) | adjacent (write authority) | `PROTOCOL.md:329-330` "it may create or repair `corpus/` inside any child repo, and nothing else"; ledger `.ufo/reports/AGGREGATE.md:2177` souji row | report only. Q57 lands in souji `corpus/QUALITY.md`, which is aggregator-writable. souji must not commit any `corpus/lessons/round-*-aggregator-*` file (`PROTOCOL.md:188`). No aggregator ledger row tallies slice verdicts (`rg -i 'slice.verdict` over AGGREGATE.md → 0) |

Confirmation: **no sibling claims `git repo structure` or common-dir manifest ground.** Evidence 1 shows 0 hits across 20 sibling PROVINCE/SKILL files. Evidence 2 shows the only two knowledge hits are kumitate seat isolation and mado write detection. souji holds this ground alone (`souji-shokunin/PROVINCE.md:66` "F2 repository size census (`git repo structure`, `count-objects`)").

Side finding: `MANIFEST.json` `roster` lists 13 ids and omits mori, tsukuroi, chousa, kotodama, tabi, mado, tameshi and souji. I scanned by lane directory, so the task's "rostered" list and the manifest roster do not match. Report only; MANIFEST was not touched.

## Proposed move (one, bounded)
**Q57 / D6: key slice verdicts on the register's (lane, id) pair.** The Q57 criterion text and the D6 lesson vocabulary mapping should state that a slice-verdict row is identified by the register's lane column plus id (`souji`, S114), never by a bare id. They should also record the cross-lane vocabulary correspondence: chousa `present`, `absent`, `mixed` and `unverifiable` against souji `accepted`, `refused` and `unverifiable`, as report-only prose. This goes in the lesson and Q57 text only, not in r24 bytes, which stand unchanged per prereg §Assimilation.
- Axes: calibration + (removes a latent F6-class id conflation; same family as the D5 "bare S123" note). Operability/coverage are unaffected. No predicate, target or case set changes.
- Risks: Q57 wording could drift into owning chousa's vocabulary. Keep it report-only. A "lane registry id" vs "campaign register id" mix-up recurs if the mapping omits the lane column.
- Verification: `rg -n '^\| `(chousa|souji|tabi)` \| round[0-9]+ \| S114 \|' /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md` should return 3 rows, which shows the collision. After landing, the Q57 row in `corpus/QUALITY.md` should name the lane key: `rg -n 'Q57' corpus/QUALITY.md` must show the (lane, id) wording.

## Attack log
- ATTACK (Q57 counter scope, report only): any Q57 or D6 check that joins slice verdicts by bare id across `census/round-22/attempt2/`, `census/round-24/records/` and a sibling table would accept a chousa row as souji evidence. The collision is witnessed for S114.
- No predicate, target or case set in `preregistration.txt` is touched by any sibling surface. C1/C2/C3 tool and fixture paths are souji-only.

Tooling installs: none. Scratch: none created (`/var/tmp/souji-r25-ConnSiblings` never made).
