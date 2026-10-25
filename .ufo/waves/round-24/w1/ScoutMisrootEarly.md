# ScoutMisrootEarly — souji r24 w1, early misroot sweep (fleet root)

## Status
STATUS: PASS — all 6 untracked fleet-root entries classified; 0 name souji round 24; 1 is a
sibling-lane (tabi r24) misroot; nothing deleted, moved or copied.

## Evidence
Fleet HEAD `c249c01ed0e89404f6094fbfb0e3e81509ff32f0`; souji lane HEAD
`f9db2181647d91470a724a12d626bd6106805076`; 2026-10-25 ~09:20 UTC.

`git -C /home/vgpnk/Projects/shokunin status --porcelain` (no pathspec), untracked lines:
```
?? .omp/mcp.json
?? .scratch/goal-20261025-hyaku-12h.md
?? .ufo/state/kotoba.report-baseline
?? .ufo/state/kotodama.report-baseline
?? .ufo/state/revenger.report-baseline
?? .ufo/waves/round-24/
```
`--untracked-files=all` expands `.ufo/waves/round-24/` to one file:
`.ufo/waves/round-24/w2/RevUnlandedResolution.md`. No entry is gitignored (`git check-ignore -v` exit 1).
(Tracked `M` lines — 14 `.ufo/state/*.report-baseline`, `.ufo/watchdog.log`, `scripts/hyaku/*` — are
not untracked and out of scope.)

Content grep (`grep -c souji` / `grep -c round-24`), size, mtime (-0300):
```
.omp/mcp.json                                    souji=0 round24=0  285 B  2026-10-24 18:07
.ufo/state/kotoba.report-baseline                souji=0 round24=0   68 B  2026-10-24 22:45
.ufo/state/kotodama.report-baseline              souji=0 round24=0   68 B  2026-10-25 03:23
.ufo/state/revenger.report-baseline              souji=0 round24=0   68 B  2026-10-25 03:23
.ufo/waves/round-24/w2/RevUnlandedResolution.md  souji=0 round24=17 15891 B 2026-10-25 05:55
```
`.scratch/goal-20261025-hyaku-12h.md`: not read (orchestrator-owned, never a misroot).

Ownership probes:
- RevUnlandedResolution.md line 3: "Seat `L1Tabi24.RevUnlandedResolution`, round 24 wave 2, falsification pass."
  line 6: "Lane root `/home/vgpnk/Projects/shokunin/tabi-shokunin`. Read-only; no tracked file touched."
  sha256 `5f09b9b3b87b96cec62021ac3a605028765f9053b64f7b0b016ebfc6b3499aef`.
- `/home/vgpnk/Projects/shokunin/tabi-shokunin/.ufo/waves/round-24/w2-dispatch.json` contains
  "Report: write your scoped findings to .ufo/waves/round-24/w2/RevUnlandedResolution.md" (lane-relative).
- `tabi-shokunin/.ufo/waves/round-24/w2/RevUnlandedResolution.md`: absent ("No such file or directory");
  `git -C tabi-shokunin log --all -- '*RevUnlandedResolution*'`: empty. Tabi tip `8bc1d32`.
- `souji-shokunin/.ufo/waves/round-24/w1-dispatch.json`: 0 hits for `RevUnlandedResolution`;
  `souji-shokunin/.ufo/waves/round-24/w2`: absent.
- Baselines: content shape `<n> e3b0c442…b855` (sha256 of empty input), same shape as tracked
  `.ufo/state/souji.report-baseline` at HEAD (`22 e3b0…`). kotodama read `68 …` then `69 …` across two
  reads minutes apart — live, written by the running orchestrator.
- `.omp/mcp.json`: top-level keys `$schema`, `mcpServers` (one server); values not printed.

## Findings
| # | path (fleet-root relative) | owner | action |
|---|---|---|---|
| 1 | `.ufo/waves/round-24/w2/RevUnlandedResolution.md` | tabi lane, round 24 w2 (seat `L1Tabi24.RevUnlandedResolution`); MISROOT — the lane-relative report path resolved against the fleet root | souji: leave untouched. Route to tabi L1 (`L1Tabi24`) / orchestrator to land at `tabi-shokunin/.ufo/waves/round-24/w2/` (no copy exists there yet) |
| 2 | `.ufo/state/kotoba.report-baseline` | orchestrator run state (kotoba lane watchdog baseline) | leave; HARD BOUND (`.ufo/state/` never touched) |
| 3 | `.ufo/state/kotodama.report-baseline` | orchestrator run state (kotodama lane baseline; live-updated) | leave; HARD BOUND |
| 4 | `.ufo/state/revenger.report-baseline` | orchestrator run state (revenger baseline) | leave; HARD BOUND |
| 5 | `.omp/mcp.json` | operator/harness config (omp MCP server list), not a lane | leave; no action |
| 6 | `.scratch/goal-20261025-hyaku-12h.md` | orchestrator (`.scratch/`) | not read; never a misroot; leave |

1. No untracked fleet-root entry names souji or souji round 24: souji has 0 misroots at this sweep.
2. Finding 1 is the same misroot class souji's own `Report:` trailers guard against (relative path landing
   in the fleet repo); the `round-24` directory at fleet root is created by tabi, not souji.
   [INFERENCE] the seat's tool cwd was the fleet root and it wrote the lane-relative path verbatim.
3. Rows 2–4 have the same shape as tracked siblings in `.ufo/state/`; [INFERENCE] they are new lanes'
   baselines the orchestrator has not yet checkpointed (cf. commit `5b476c3d checkpoint: report baselines`).

## Remaining unknowns
- Whether tabi's L1 already knows of the misroot (not messaged; leaf seat, report-only).
- A later wave can produce new misroots; this sweep is a point-in-time census at fleet HEAD `c249c01e`.

No tools installed. No scratch created.
