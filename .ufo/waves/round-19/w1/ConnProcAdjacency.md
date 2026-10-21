STATUS: DONE — C3 process-residue adjacency review complete; report only.

# Findings

- The F5 scope transition is otherwise consistent: r18 records own-uid residue and no signaling; r19 promotes only the observation surface, retains list-only/no-reap limits, and leaves the reap protocol pending. The entry also distinguishes census mode (no signal) from fixture workers it spawned. See `corpus/README.md:242,274,281`, `PROVINCE.md:43-46,73-78`, and `corpus/knowledge/process-residue-observations.md:52-54,79-81`.
- Boundary drift in the entry: `corpus/knowledge/process-residue-observations.md:82-83` assigns “other uids” to mori along with host-wide liveness. PROVINCE says mori observes/reports fleet and host health, while souji lists only its own uid's residue and routes liveness/resource findings to mori (`PROVINCE.md:50-52`); it does not say all other-uid process residue belongs to mori. State that other-uid process residue is outside this census, rather than expanding mori's stated surface. The r18 row and r19 README row stay scoped (`corpus/README.md:242,274`); the SKILL rule likewise says own-uid (`SKILL.md:129-134`).
- Kagi boundary / explicit contradiction: the entry's redaction sentence (`corpus/knowledge/process-residue-observations.md:58-59`) and the repeated SKILL wording (`SKILL.md:131-133`) describe identifying secret-shaped argv, without saying credential-hygiene evidence remains kagi's or findings route there. This could read as taking part of kagi's credential surface. More importantly, PROVINCE says credentials/tokens are kagi's and souji never reads secret content (`PROVINCE.md:36-37`), but the current census reads raw `/proc/<pid>/cmdline` into `CMD_RAW` and applies credential-pattern redaction before output (`tools/souji-proc-census.sh:192-227,230-256,364-365`). This is a direct wording/implementation tension if secret-bearing argv is secret content; redaction-before-print does not make the raw read disappear. The README F5 rows make no credential claim (`corpus/README.md:242,274`).
- Tsukuroi's host-repair surface is not claimed by the C3 entry, README row, or SKILL rule; adding the boundary sentence below makes that separation explicit. PROVINCE assigns host-operability repair to tsukuroi and credential-hygiene evidence to kagi (`PROVINCE.md:53-56`).

Exact adjacency sentence proposed for the entry (replace the overbroad Mori clause and make all three boundaries explicit):

> Souji lists only its own uid's residue, routes fleet/host liveness and resource findings to mori for observation and reporting, leaves host-operability repairs to tsukuroi, and routes credential-shaped findings to kagi, which owns credential hygiene.

This fixes the ownership wording but does not resolve the raw-argv/province contradiction; that needs an explicit scope decision rather than an implication that redaction makes the read credential-free.

# Evidence

- `PROVINCE.md:36-37,50-56,73-78` — credential refusal and kagi routing; Mori observation/reporting and own-uid boundary; Tsukuroi repairs host operability; r18 F5 remains list-only with other-uid and host-wide scope outside it.
- `corpus/lessons/round-18-verifier-spotcheck.md` is preregistered as the r18 closure source; the C3 claim is recorded in `.ufo/waves/round-19/preregistration.txt:51-61` as first knowledge entry, list-only, no reap authority.
- `corpus/README.md:236-248,270-282` — r18 F5 own-uid/no-signal row and pending operator reap protocol; r19 observation-surface row and continued no-reap boundary.
- `corpus/knowledge/process-residue-observations.md:5-11,50-63,77-91` — current entry scope, argv redaction, reap limit, Mori wording, and limits.
- `SKILL.md:129-141` — current process-residue rule and inherited-process signal boundary.
- `tools/souji-proc-census.sh:192-227,230-256,344-365` — raw argv read, secret-pattern redaction, and emitted command field.

# Commands run

None. Used read/grep inspection only; no tests, fixtures, census, or other executable checks were run.

# Contract compliance

Read-only review. Wrote only `.ufo/waves/round-19/w1/ConnProcAdjacency.md`; no subagents, tool installs, network access, process signaling, or forbidden-path reads/writes. Affected declared axis: coverage. No calibration or operability effect is evidenced by this wording review.
