# CritRoutings — role/route assignment review (souji r27 w1, hyaku run 7)

## Status
STATUS: PASS — all 79 seat roles exist in the run-7 route map; config.yml `task.agentModelOverrides` matches the run-7 table exactly; no seat passes a model; this wave has zero resumed seats (route-on-resume rule documented and vacuous here); L1 (m_kfc) is the only integrator and no seat is a coordinator.

## Evidence
- Run-7 route map (global role map), `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-27.md:155-162`:
  `Run-7 routing (global role map; never pass `model`): task/main/planner `@m_kfc``;
  `reviewer/mutation-tester/security-reviewer `@m_zfl``; `connector `@m_antigravity``;
  `scout/distiller/seance `@m_mim``; `executor/labrat/scribe/sonic/simplifier/critic/revenger/sentinel `@m_flash``
  (m_glm53 dropped by operator).
- `~/.omp/agent/config.yml` `modelRoles` (lines 317-345): m_kfc=`kimi-code/kimi-for-coding:max` (329), m_zfl=`zai/glm-5.3-flash:max` (334), m_antigravity=`google-antigravity/gemini-3.8-flash:high` (324), m_mim=`minimax-code/MiniMax-M3.1-Flash:high` (343), m_flash=`commandcode/deepseek/deepseek-v4.1-flash:high` (336).
- `~/.omp/agent/config.yml` `task.agentModelOverrides` (lines 349-367): task/main/planner `@m_kfc`; reviewer/mutation-tester/security-reviewer `@m_zfl`; connector `@m_antigravity`; scout/distiller/seance `@m_mim`; executor/labrat/scribe/sonic/simplifier/critic/revenger/sentinel `@m_flash`. Identical to the run-7 table.
- `souji-shokunin/.ufo/waves/round-27/w1-dispatch.json`: `counts={spawn:79, resume:0, total:79}`, `resumeSends=[]`; `taskCall.tasks` 79 entries. Each task object's key set is exactly `{'agent','name','task'}` — no `model` key anywhere.
- `souji-shokunin/.ufo/waves/round-27/w1/swarm-registry.json`: 79 members (matches tasks).
- `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-27.md:273-274`: `A seat keeps the route chain it captured at spawn, also when resumed.`
- `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-27.md:264-267`: validator rejects `planner` as a frozen-topology seat, never a swarm role; the L1 holds the canonical planner seat.

## Mapping table (role → run-7 bucket → expected answering model from config.yml)

| Role | Run-7 bucket | Expected answering model (config.yml modelRoles) | Seats this wave |
|---|---|---|---|
| executor | @m_flash | commandcode/deepseek/deepseek-v4.1-flash:high | 25 |
| labrat | @m_flash | commandcode/deepseek/deepseek-v4.1-flash:high | 0 (unused) |
| scribe | @m_flash | commandcode/deepseek/deepseek-v4.1-flash:high | 8 |
| simplifier | @m_flash | commandcode/deepseek/deepseek-v4.1-flash:high | 3 |
| critic | @m_flash | commandcode/deepseek/deepseek-v4.1-flash:high | 10 |
| revenger | @m_flash | commandcode/deepseek/deepseek-v4.1-flash:high | 1 |
| sentinel | @m_flash | commandcode/deepseek/deepseek-v4.1-flash:high | 0 (unused) |
| sonic | @m_flash | commandcode/deepseek/deepseek-v4.1-flash:high | 0 (unused) |
| reviewer | @m_zfl | zai/glm-5.3-flash:max | 12 |
| mutation-tester | @m_zfl | zai/glm-5.3-flash:max | 6 |
| security-reviewer | @m_zfl | zai/glm-5.3-flash:max | 0 (unused) |
| connector | @m_antigravity | google-antigravity/gemini-3.8-flash:high | 3 |
| scout | @m_mim | minimax-code/MiniMax-M3.1-Flash:high | 11 |
| distiller | @m_mim | minimax-code/MiniMax-M3.1-Flash:high | 0 (unused) |
| seance | @m_mim | minimax-code/MiniMax-M3.1-Flash:high | 0 (unused) |
| planner | (frozen-topology; held by L1, never dispatched) | @m_kfc → kimi-code/kimi-for-coding:max | 0 |
| task/main (L1) | @m_kfc | kimi-code/kimi-for-coding:max | 0 (L1 outside wave) |

Total seats: 79 (connector 3, scout 11, executor 25, reviewer 12, critic 10, mutation-tester 6, simplifier 3, revenger 1, scribe 8). No duplicates; all names unique.

## Findings
1. Every used role (executor, scribe, simplifier, critic, revenger, reviewer, mutation-tester, connector, scout) exists in the run-7 route map; no role used by a seat is missing from the table.
2. `task.agentModelOverrides` in `~/.omp/agent/config.yml` matches the run-7 routing line for line. No divergence between the prompt's route map and the live config.
3. No seat passes a model: dispatch task objects carry only `name`/`agent`/`task`; no `model` key. Routing is role-based via config, per the run-7 "never pass `model`" rule.
4. Route-on-resume: documented (`souji-round-27.md:273-274`); this dispatch has `resume=0` and empty `resumeSends`, so no seat resumes in this wave — the assumption holds vacuously.
5. L1 is the only integrator: config routes task/main/planner to `@m_kfc`; the wave contains no planner/integrator/coordinator role (validator rejects planner as frozen-topology, and the L1 holds it). No seat is a coordinator.
6. v2 attack share is met: reviewer (12) + critic (10) + mutation-tester (6) = 28/79 = 35.4% ≥ 25%. m_flash roles (executor 25 + scribe 8 + simplifier 3 + critic 10 + revenger 1 = 47) = 59.5% ≥ 50% ("use more m_flash" majority rule).
7. Observation (not a defect): items named `Lab*` (`LabKinsProbe`, `LabF4Probe`, `LabCensusProbe`, `LabSliceFetch`, `LabGitIgnoreProbe`) carry role `executor`, not `labrat`. Both roles route to `@m_flash` in run-7, and runnable checks are executor work per the routing doc, so this is consistent with the route map and role semantics. `[INFERENCE]` intended-role naming.

## Attack log
No attack item; this seat performs the assigned routing review only.
