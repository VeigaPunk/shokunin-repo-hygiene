# RevSHONEN — SHONEN.md evidence audit (round 23, w1)

## Status

STATUS: PASS — all four evidence pointers resolve at lane base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` and all four support their box wording; no `[x]` claimed (promotion is operator-owned). Four residual precision/staleness findings, none of which falsifies a box.

Scope: `SHONEN.md` at base rev (blob `b5ec7115cd04277f1c5d5b17b8115ab61e2e8578`, byte-identical to the worktree file). Box wording is verbatim the canonical seed (`/home/vgpnk/Projects/shokunin/PROTOCOL.md:439-451` and `/home/vgpnk/Projects/kimi-shokunin/templates/mint/SHONEN.md`). Marks: 4 x `[~]`, 0 x `[x]`.

## Evidence

Read-only throughout. Shell scratch `/var/tmp/souji-r23-RevSHONEN/` removed before finish. No tool installed or upgraded.

**Base identity and pointer existence** — `git rev-parse HEAD` = `1208bfb…` (ahead=0 behind=0); `git cat-file -e 1208bfb:<path>` for all ten named paths returned OK (SHONEN.md, SKILL.md, corpus/SOURCES.md, corpus/lessons/round-21.md, LOG.md, census/round-21/{run-acceptance.py,accepted-matrix.json,remote-source-after.json}, PROVINCE.md, .ufo/waves/round-21/w1/ConnSiblingOverlap.md). `git hash-object SHONEN.md` = `b5ec7115…` = `git rev-parse 1208bfb:SHONEN.md`.

**Lane's own pointer gate, run at base rev** — `python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd --round 22` → rc=1, `SUMMARY findings=6 checked_reg=50 … checked_reports=248`. SHONEN.md is in the gate's pointer-source set (`tools/souji-landing-gate.py:918`); zero of the 6 findings name SHONEN.md (they are `corpus/README.md:217` and `corpus/lessons/round-22-verifier-spotcheck.md:32,89`).

## Findings

### Box 1 — `SHONEN.md:5-6` — verdict: **supported**

Wording: `SKILL.md contains real decision tables, error patterns, checklists, cited sources`. Pointer line: `SKILL.md Decision tables/Error patterns/Checklists/Gate registry; corpus/SOURCES.md S100-S103; corpus/lessons/round-21.md Gate`.

- `git show 1208bfb:SKILL.md | grep -nE '^#{1,4} '` → `42:## Decision tables`, `78:## Error patterns (false-SAFE signatures)`, `147:## Checklists`, `167:## Gate registry`. All four named sections exist.
- Substance checked, not just headings: :44-61 is a five-row Observation/Verdict table plus a six-step removal flow; :78-100 lists five false-SAFE signatures each with a live instance; :147-155 is a pre-removal checklist with the command per line; :167-226 is a 30-row gate registry carrying entry command, verdict map, self-test command and pinned-value path.
- `git show 1208bfb:corpus/SOURCES.md | grep -cE '^\| S10[0-3] '` → `4` (rows S100-S103 at :120-123, each with URL, tier, decision).
- `git show 1208bfb:corpus/lessons/round-21.md | grep -n '^## Gate'` → `25:## Gate`; :27-37 carries the four opened-source decisions with located quotes.
- Gate-registry path resolution: 81 unique `tools|tests|corpus|census` paths extracted from :167-226, `git cat-file -e` each → `missing=0`.

Residual (R1): `git show 1208bfb:SKILL.md | grep -c 'https\?://'` → `0`. "Cited sources" is satisfied only through the SOURCES.md pointer, never inside SKILL.md itself; the box reads as if SKILL.md carries them.

### Box 2 — `SHONEN.md:7-8` — verdict: **supported**

Wording: `At least one end-to-end domain task executed and logged in LOG.md`. Pointer: `LOG.md:362 (2026-10-19 operator sweep: 96 pushed-receipt artifacts quarantined, second-checked, removed)`.

- `git show 1208bfb:LOG.md | sed -n '362p'` → `## 2026-10-19 — operator sweep (execution): root-wide receipts + home-wide cache/tmp cleanup`. LOG.md is 1522 lines at rev, so the pointer is in range.
- The 96 figure is at `LOG.md:368`: `**Removed — fleet root, receipt pushed (96 artifacts).**`, then :371 `96/96 SAFE(pushed)`, :372-373 the two receipt paths, :373-378 the quarantine/second-check/delete flow (`93 staged via git mv`, `second check as hash-vs-origin`, `restored from origin`).
- Named receipts resolve at rev and agree: `census/operator-sweep-20261018/approval-list.tsv` = 97 lines = header + `96` rows whose receipt column is `pushed`; `resume-verdicts.tsv` = 93 rows, `grep -c SAFE` = 93. 93 staged by script+manual `git mv` plus 3 script-staged = 96, consistent with the narrative.

Residual (R2): the pointer lands on the section heading; the number it is cited for is six lines later (:368). A line-number pointer into an append-only 1522-line file is durable only while nothing is inserted above :362.

### Box 3 — `SHONEN.md:9-10` — verdict: **supported** (re-derived at base this run)

Wording: `Instructions executable by an agent without oral context`. Pointer: `census/round-21/run-acceptance.py; census/round-21/accepted-matrix.json (3/3 sources, each18/18); census/round-21/remote-source-after.json`.

- Matrix counting command, `jq` over the rev blob: `scenarios=3 replayed=3 summaries_equal=true records=3 counts=18,18,18 all_matched=true,true,true`.
- Denominator is the tool's own constant: `git show 1208bfb:census/round-21/run-acceptance.py | grep -n 'EXPECTED_COMMANDS ='` → `25:EXPECTED_COMMANDS = 18`.
- Self-description without oral context: extracted the rev blob to scratch, `sha256` matched the blob (`00d0e9c2…`), `python3 -B -m py_compile` → OK, `--help` → rc=0 with `usage: run-acceptance.py [-h] --root ROOT --rev REV --output OUTPUT`.
- Executability re-derived at the named revision: `TMPDIR=/var/tmp python3 -B <scratch>/run-acceptance.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd --output /var/tmp/…/out-base.json` → `RC=0` in 11.4s; record: `expected=18 observed=18 matched=18 all_matched=true measured=1208bfb… inputs_unchanged=true source_sample_unchanged=true schema=souji-round21-replay-acceptance-v1`. Lane `git status --porcelain` unchanged by the run.

Residual (R3): the committed matrix is a historical receipt, not bound to current tool bytes. Its own command records rev `1957154…`, whose `run-acceptance.py` blob is `1ecbad09…`, while the base-rev blob is `a62d67d5…` (`git diff --stat 1957154 1208bfb -- census/round-21/run-acceptance.py` → `73 insertions(+), 17 deletions(-)`, the r22 cache-check additions). This is the D3 class the r22 spot-check routed to this lane: 18/18 reproduces, but the lane holds no committed receipt binding it to the tool blob a verifier will read. Minor: the JSON's own key is `scenarios`/`replayed`, not `sources`; "3/3 sources" maps to the three recorded source roots (S1 subtree extract, S2 clone, S3 lane) only by inspection of each record's `source_before`/`source_after`.

### Box 4 — `SHONEN.md:11-12` — verdict: **supported**

Wording: `No cross-domain bleed (PROVINCE.md still accurate)`. Pointer: `PROVINCE.md Round21 privacy boundary; .ufo/waves/round-21/w1/ConnSiblingOverlap.md; corpus/lessons/round-21.md Boundaries`.

- `git show 1208bfb:PROVINCE.md | grep -n '### Round21 privacy boundary'` → `161`, body :163-172 (`it still reads raw eligible same-uid argv/fd paths`, `Historical exposure … remain unproved`, `Operator/Kagi retains exposure assessment`). The section states the limit of the lane's own scanner and routes exposure to Kagi/operator rather than absorbing it.
- `git show 1208bfb:corpus/lessons/round-21.md | grep -n '^### Boundaries'` → `38:### Boundaries and teaching`, which records the same routing (credential handling Kagi, reusable fixture method Tameshi, host/fleet health Mori, no sibling code changed).
- `.ufo/waves/round-21/w1/ConnSiblingOverlap.md` (127 lines) opens: `No sibling contests Souji's lane-internal ownership of these three surfaces` and names the adjacent ground per claim.
- PROVINCE internal citations resolve at rev: 17 unique repo paths, `missing=2` = `.ufo/state/` and `.ufo/watchdog.log`, both named in `## Refuses` as operator-owned, so absence is the stated contract, not a dangling pointer. Its cross-reference `the r21 section of corpus/knowledge/process-residue-observations.md` resolves (`174:## Round-21 reason output repair — synthetic only`), as does QUALITY `113:| Q49`.
- Sibling side re-read now, read-only: `kotoba-shokunin/PROVINCE.md:64` row `souji … none`; `mori-shokunin/PROVINCE.md:69` cites `souji-shokunin@fe7590b…:PROVINCE.md:8-17,50-52`, and `git diff fe7590b… 1208bfb -- PROVINCE.md` is empty, so that citation is still current.

Residual (R4): `PROVINCE.md:25` says `seven colocated lanes at r17`; `ls -d /home/vgpnk/Projects/shokunin/*-shokunin/.jj` now returns 19 (souji included). The count is explicitly dated and the paragraph says re-resolve per round, so it is stale rather than false — but a non-author reading PROVINCE.md as current guidance will flag it. `[INFERENCE]` the r17 figure was accurate when written; I did not reconstruct r17 sibling state. ConnSiblingOverlap's sibling reads are r21 HEAD, not re-resolved at base.

### Cheapest change to earn `[x]` from a non-author verifier, per box

One change per box; each is a single edit to the evidence line in `SHONEN.md` unless noted.

- **B1** — append the revision and one counting command: `@1208bfb; git show 1208bfb:SKILL.md | grep -cE '^## (Decision tables|Error patterns|Checklists|Gate registry)'` → 4. (If R1 matters, also state that sources live in SOURCES.md, not SKILL.md.)
- **B2** — replace the bare line number with the heading plus the receipts: `LOG.md "## 2026-10-19 — operator sweep (execution)" :368-378; census/operator-sweep-20261018/approval-list.tsv 96 pushed rows`. Cheapest durable form, since the section heading is unique in LOG.md.
- **B3** — commit one base-rev replay receipt and cite it instead of the 1957154-bound matrix: `census/round-23/records/acceptance-base-<sha>.json` with `tool_sha256=a62d67d5…`, `matched=18/18`, `measured_commit=1208bfb…`. The run already succeeds; only the committed receipt is missing. (This is exactly C2's runner scope, so it is cheap for this round.)
- **B4** — cite `PROVINCE.md "### Round21 privacy boundary"` by heading rather than by round label, and either drop the `seven colocated lanes at r17` count or append the re-resolved count with its date.

Global cheapest single move, if only one edit is allowed: add `@1208bfb` plus one re-runnable command to each of the four evidence lines. That converts all four from assertion to re-derivable claim without touching any pointer target.

## Notes

- Peer work appeared in the lane worktree during this audit (`tools/souji-record-agreement.py`, `tools/souji-receipt-run.py`, `census/round-23/`, `tools/__pycache__/` at 05:11-05:15); none of it is mine, and my replay reported `inputs_unchanged=true` / `source_sample_unchanged=true` for the tree it measured.
- No deletion, move, quarantine or VCS mutation anywhere; no sibling file written; no `.scratch/`, `.ufo/state/`, `watchdog.log`, MANIFEST or fleet script read beyond what is quoted above.
- Tooling: no installs or upgrades. `python3` (system), `jq` (system), `git` (system) only.
