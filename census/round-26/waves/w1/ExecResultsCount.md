## Status

STATUS: PASS — `w1/results-count.py` delivered and exercised over nine fixtures; the live `w1-results.json` does not exist yet (wave seats still settling), so its first real run is the L1's, after `WAVE-DONE`.

## Evidence

Lane master tip at write time: `166baa18f808071bc385187691713044a26bd663` (`git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse master`, 2026-10-25 14:37:35 -03). Deliverable: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/results-count.py`, mode `-rwxr-xr-x`, sha256 `a8c7227b225e09ba5150cab773c404395b3188537fa0fe119fc9d1e61a1d3fe0`.

Results-file contract (fleet, read-only): `/home/vgpnk/Projects/shokunin/scripts/hyaku/lane-addendum.md:34` — "when all seats settle writes `<wave>-results.json` beside the dispatch file (per seat: name, agent, id, status, final output)". Dispatcher implementation read from the orchestrator session cell (`/home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-25T16-43-09-760Z_01a173f1-d040-72cd-9542-6011673d5d9b.jsonl`), write call verbatim: `'seats':len(res),'dead':sum(r['status']=='dead' for r in res),'results':res}, open(outp,'w'), indent=1`; per-seat rows are `{'name','agent','id','status','output'}` on success and `{'name','agent','id','status':'dead','error':repr(e)[:2000]}` on failure.

Dispatch cross-check (`w1-dispatch.json`): `counts={"spawn": 87, "resume": 0, "total": 87}`; role mix executor 31, reviewer 15, scribe 11, scout 10, critic 9, mutation-tester 6, connector 2, simplifier 2, sentinel 1.

Fixture matrix, run in `/var/tmp/souji-r26-ExecResultsCount/` (now removed), `python3 -B <tool> --results <file>`:

```
realistic-done.json      exit=0  seats=87 dead=0 roles=executor:31 reviewer:15 scribe:11 scout:10 critic:9 mutation-tester:6 connector:2 simplifier:2 sentinel:1
realistic-dead-agree     exit=0  seats=87 dead=3 roles=... statuses=done:84 cancelled:1 dead:1 failed:1  agreement=ok
realistic-dead.json      exit=1  dead=3 recomputed vs declared-dead=2   agreement=mismatch
members-schema.json      exit=0  seats=3 dead=1 (ufo-swarm-results-v1, agentId/result)  agreement=undeclared
mismatch-seats.json      exit=1  seats=3 vs declared-seats=5           agreement=mismatch
dup-name.json            exit=1  warn=duplicate-name:A
bare-array.json          exit=0  seats=1 dead=0 (bare JSON array)
seat-string.json         exit=2  results=invalid ... error=seat-row-not-an-object
unreadable.json          exit=2  results=unreadable ... error=PermissionError
invalid.json             exit=2  results=invalid ... error=JSONDecodeError line=1 col=31
<directory>              exit=2  results=not-a-file
does-not-exist.json      exit=2  results=absent path=.../does-not-exist.json
```

Dead-seat extraction, real shape (multi-line `repr(e)` plus `failed`/`cancelled` variants):

```
dead name=ExecAxisTool agent=executor status=dead id=SoujiR26.ExecAxisTool
    error-last-line: RuntimeError: No active Python tool bridge session
    error-text:
        RuntimeError('No active Python tool bridge session: python:session:...')
          File "<cell>", line 1052, in agent
        RuntimeError: No active Python tool bridge session
```

Live invocation, default path, at 2026-10-25T17:38Z:

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/results-count.py
results=absent path=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1-results.json
exit=2
```

`ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1-results.json` → No such file or directory (dispatcher log `spawned 87/87` at 14:35 -03; file is written only after every seat settles). No `__pycache__`/`*.pyc` under `w1/` (`find` count 0).

## Findings

1. **Delivery** — `.ufo/waves/round-26/w1/results-count.py` prints, first line, exactly `seats=N dead=D roles=role:count...` (roles sorted by descending count, then name); then `results=<abs path>`, `lane=/round=/wave=`, `statuses=`, `agreement=`, one `seat name= agent= status= id=` line per seat, and one `dead …` block per dead seat. Default path is derived from the script's own location (`<round>/w1-results.json`, printed resolved and absolute) with `--results PATH` override.
2. **Dead rule is stricter than the dispatcher's own counter** — dead means any status outside `{done, completed, ok, success}` (so `failed`, `cancelled`, `error`, `timeout`, missing status all count), while the dispatcher declares `dead` as `status=='dead'` only. A late-failing seat therefore registers as `agreement=mismatch` instead of vanishing from the L1's "every seat that dies, with its last error text" obligation (`lane-addendum.md` §2 routing paragraph). Exit 1 on mismatch, never a silent pass.
3. **Error extraction** — `error` (the dispatcher's `repr(e)[:2000]`) then `lastError`/`errorText`, else the last non-empty line of `output`/`result`/`final`; prints a whitespace-collapsed `error-last-line` plus the verbatim text (8-space indent, capped at 4000 chars with an explicit `... [error-text truncated]` marker). Verified on a 5000-char traceback.
4. **No valid-looking zero** — an absent, unreadable, directory, non-JSON, or mixed-shape file exits 2 with a single `results=absent|not-a-file|unreadable|invalid …` line; `seats=0` can only print for a genuinely empty seat array.
5. **Schema tolerance** — accepts the dispatcher shape (`results`), the older `ufo-swarm-results-v1` shape (`members`, `agentId`, `result`), and a bare array; a member without `agent` counts under `?:n`; a document without `seats`/`dead` prints `agreement=undeclared` rather than inventing counts.
6. **Live numbers not reportable yet** — `w1-results.json` is absent at 17:38Z; the L1's wave numbers (seats, dead seats, role mix) must be read by running this tool after the dispatcher's `WAVE-DONE`. The fixture role mix reproducing the dispatch's own `counts` (87 seats; executor 31 … sentinel 1) is the cross-check that the role column maps to `agent` correctly.
7. **Cost** — stdlib only, single file, no lane writes outside this script and this report; no tool installs (nothing needed; `uv`/`npx` unused). Scratch `/var/tmp/souji-r26-ExecResultsCount/` removed.
8. **Committed snapshot vs working file** — the L1 already committed an earlier snapshot of this delivery in `166baa1` (blob `6568a99`); the working tree differs only in the two-line polish that prints `declared-seats=-`/`declared-dead=-` when a results file omits them (`git diff -- .ufo/waves/round-26/w1/results-count.py`, 4 lines changed). All evidence above was produced from the polished working file (sha256 `a8c7227b…`), so the L1 must land the working tree version, not the committed blob.

## Risks

- If the dispatcher renames its seat-array key or drops `agent`, the tool exits 2 (refusal) rather than mis-counting; the L1 should then report the schema drift, not hand-count.
- `agreement=mismatch` is expected only when the dispatcher's literal `dead` disagrees with the stricter rule; on such a run the recomputed `dead=` and the per-seat `status=` lines are the report's source, the declared field is not.
- Platform assumption: `status` values are lowercase as written by the dispatcher; a differently-cased status would count dead.
