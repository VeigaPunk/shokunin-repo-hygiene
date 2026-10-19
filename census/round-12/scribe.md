# r12 scribe — final summary

Author: W2RoundSouji-8.R12Scribe (L2, read-only); transcribed verbatim by the L1 from its final output (session-scoped `agent://W2RoundSouji-8.R12Scribe`; this committed copy is the durable form). 2026-10-19.

Deliverable written and verified in place: `census/round-12/mistakes.md` (35,081 B, lane worktree `…/kaika/souji-shokunin`, confirmed via `git -C <lane> rev-parse --show-toplevel`). No file was written outside the lane worktree; no sibling files touched.

**Behavior**
- Mined all 11 lessons, full LOG.md (incl. 2026-10-19 operator sweep) and `census/operator-sweep-20261018/`, starting from STATE §4.1–10 and ART §7 M1–M8, and added classes both missed (own debris committed, FIFO-blocked digests, shellcheck `-S error` gap, stale bookkeeping surfaces, evidence-layout drift, approve-list already-removed rows, unreachable-blob residue).
- Table 1: 52 classes with `kind`, evidence pointer, captured-by, fix. Table 2: 52 pasteable `bash -c "grep -n …"` evidence commands with observed output. Table 3: capture-pointer verification commands (SKILL/AGENTS/tool selftest ids/tests fixtures), all run this session.
- Counts by kind: **defect 22 · process 11 · honest-stop 8 · caught 11** (total 52).
- **captured-by = `none`: 24 of 52** (M04, M06, M07, M09, M10, M11, M13, M23, M25, M27, M28, M30, M37, M39, M40, M41, M42, M43, M44, M45, M49, M50, M51, M52); near-misses recorded as `partial:` but counted strict-none. 12 defect rows are captured (mostly tools-only: NUL gate, nested-repo gate, ledger pin, `GIT_OPTIONAL_LOCKS`, census compare refusal + selftest cases); 9 honest-stops captured by their round's lesson.

**STATE/ART claims found wrong or imprecise**
1. ART §7 M4 “Already captured? No” — wrong as stated: nested-repo class is captured in tools since r10 (`tools/souji-verify.sh:418` `nested-repo-or-unverifiable`, same in vault-verify; S17/S18 gate in quarantine). Only SKILL.md lacks it.
2. Tools-only capture has a gap: `souji-quarantine.sh` has **no** `command -v git` guard (verify:1308, census:818 do), so the “disappearing git” sub-class is half-closed in the flow that stages/deletes.
3. ART §8 D7 (gd2d lock ambiguity) resolved by measurement: 5 registrations, **3 locked** (wt-r98/99/100, reason text present), 2 unlocked = main + the kaika lane worktree. SKILL.md:100 current; LOG.md:134-136 is pre-r5 state.
4. STATE §5.6 “strays … reported, never touched” understates: `err4.nl2`, `err4.z2`, `.ufo-reports-placeholder`, `.scratch/s29-freeze-dir.txt`, `results/.s54-write-probe.txt` are all **tracked/committed** in `1ccf11b` — lane debris entered history (row M45).
5. Sweep provenance corroborated: fleet-root commits `9c220bf`, `99819ec`, `e20f4fa` exist with subjects matching LOG.md:381-383. ART §7 M6 pointer verified (`shellcheck -x -S error`, census/round-10/S02-cluster-A.md:19); no shellcheck anywhere under `tests/`.

**Out of scope / limits (stated in-file)**: M32 aggregates 23 r9 classes (fixes not re-derived beyond pointers); M44 FIFO reader provenance quoted from LOG; M51 consequence chain is `[INFERENCE]` source-derived (this round's C3 fixture). Barriers honored: read-only git with `GIT_OPTIONAL_LOCKS=0` on live repos; fixtures/scratch untouched; no commits, no `cd` reliance (cwd parameter + `git -C`/absolute paths after the orchestrator notice).
