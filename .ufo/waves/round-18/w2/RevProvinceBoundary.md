STATUS: DONE — Scoped falsification found two boundary contradictions and two documentation drifts.

Axes reviewed: signal/ownership boundary; mori adjacency and routing; Core-versus-Frontier admission.

## Findings

### MEDIUM — F5 is both Core and Frontier

`PROVINCE.md:31-37` adds F5 process residue under `## Work surfaces`. But `PROVINCE.md:67` defines Core as the surfaces under both `## Owns` and `## Work surfaces`; `PROVINCE.md:68-69` says a Frontier row moves to Core only with an admitted `corpus/knowledge/` entry and a SKILL rule. F5 at `PROVINCE.md:80-82` explicitly has no knowledge entry and “stays frontier.” `corpus/README.md:242,246-248` independently labels F5 frontier and says the knowledge entry is next; SKILL has the tool/gate rows at `SKILL.md:172-173`, so the missing knowledge entry is the remaining stated admission condition. Thus the new Work surfaces bullet classifies the same unadmitted surface as Core through the existing Core definition.

Smallest fix: keep F5 frontier until admitted, by moving the observed process-residue bullet out of `## Work surfaces` or changing the Core definition to exclude unadmitted observed surfaces. Do not silently treat the existing SKILL rows as replacing the missing knowledge entry; PROVINCE and corpus/README explicitly require that entry.

### MEDIUM — The blanket signal prohibition conflicts with required test cleanup

`PROVINCE.md:50-53` says “Signalling any process except” the per-repository process group forked by the census watchdog. There is no fixture/selftest exception. Taken literally, this prohibits the test harnesses from signalling their own private sessions, even though `corpus/QUALITY.md:79` requires FIFO-case fixtures to kill the whole census session on timeout, and `SKILL.md:173` says the proc-census fixture kills exactly processes it started. This is not hypothetical: `tests/fixtures/r15-census-config.py:287-294` kills session members and the session process group; `tests/fixtures/r17-census-hygiene.py:155-169` does likewise; `tests/fixtures/r18-census-bounded.py:445-469,545-550,582-584` kills groups within its verified private session. Those fixtures start their census run in a new session (`r15-census-config.py:297-310`; `r17-census-hygiene.py:170-207`; `r18-census-bounded.py:515-540`). Also, `QUALITY.md:81` and the SKILL registry row at `SKILL.md:172` say the proc-census tool “never signals,” while `tools/souji-proc-census.sh:355-377` kills its own `--selftest` worker groups; its source comment at line 3 correctly narrows that to “outside its selftest.”

Answer to the boundary question: as written, “any process” covers test harnesses too; the intended distinction (operational action versus cleanup of processes created in an isolated test) is not expressed. The current fixture code scopes cleanup to its own sessions/groups, so this is a policy/documentation contradiction, not evidence that a fixture targets unrelated processes.

Smallest fix: state that operational Souji tools may signal only the census watchdog’s per-repository group, while fixture/selftest harnesses may signal only verified process groups/sessions they created for isolated `/var/tmp` cases; qualify Q32 and the SKILL row as “normal inventory path never signals; selftest cleans up only its own workers.” Keep listed-residue reaping operator-owned and identity-checked.

### LOW — Mori’s existing evidence pointer and quoted boundary are stale

The new Souji adjacency is at `PROVINCE.md:55-59`, and now says Mori observes fleet/host health while Souji lists its own residue and routes liveness/resource findings to Mori. The current `mori-shokunin/PROVINCE.md:69` still quotes the removed wording (“mori-shokunin observes fleet health and reports; souji acts on artifacts”) and points to `../souji-shokunin/PROVINCE.md:40-41`. At the reviewed Souji revision, lines 40-41 instead describe the history-rewrite refusal; the adjacency section is now lines 55-59. Mori’s own ownership declaration (`mori-shokunin/PROVINCE.md:3-16`) supports the new liveness, kill/OOM, and runway routing, so the changed boundary direction itself is sound; the stale quote and line reference are the defect.

Smallest fix: update the Mori sibling row and its evidence pointer to the current Souji adjacency (lines 55-59), with the new list-only residue boundary. This seat made no cross-lane edits.

### LOW — “Scratch residue” abbreviates a broader deleted-cwd predicate

The rewritten adjacency says Souji lists “only its own uid's scratch residue” (`PROVINCE.md:57-59`), and F5 summarizes “own-uid scratch residue” (`PROVINCE.md:80-82`). But the exact predicate in `PROVINCE.md:31-34` and `QUALITY.md:81` includes every current-uid process whose cwd link is deleted, without requiring that cwd to be under `/var/tmp`, `/tmp`, or `/dev/shm`; only the argv/fd alternatives are constrained to those scratch roots. The implementation confirms this: `tools/souji-proc-census.sh:326-337` sets `cwd-deleted` unconditionally, then checks argv/fd path conditions only if no cwd reason was found. The summary could therefore imply a narrower Souji observation surface than the tool actually lists.

Smallest fix: use “own-uid process residue” in the adjacency/F5 summaries, or state the deleted-cwd alternative explicitly. This does not undermine the routing to Mori; it makes the Souji side precise.

## Verification and residual risk

- The scoped diff was read with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --unified=3 b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- PROVINCE.md`. Output: `PROVINCE.md | 19 +++++++++++++++++--`, `1 file changed, 17 insertions(+), 2 deletions(-)`; it shows the old Mori adjacency text removed and the new list/routing text added.
- LSP status/references/definition/diagnostics were unavailable: `read xd://lsp` returned “No such tool: xd://lsp” and the mounted-device list contained no LSP device. Source locations above come from exact file reads; grep was used only to locate text, not as semantic proof.
- The retained proc census record has a boot-id header and PID/starttime columns (`census/round-18/proc-census-live-1721.tsv:1-2`) with 65 process rows (`:3-67`); the independent count record says `total: 65` (`census/round-18/leak-count-live-1721.json:80`). This supports the recorded cardinality, but I did not independently compare the complete PID sets or rerun a live census. No test/runtime commands were run.
- Identity handling is preserved in the written contract: the list carries PID, starttime, and boot_id (`PROVINCE.md:52-53`; `QUALITY.md:81`), and Q32 requires re-verification of the tuple before an operator kill. No handoff implementation is part of this documentation diff, so same-identity transfer to Mori was not dynamically exercised.
- The diff contains no alternate process-census runtime: SKILL names `tools/souji-proc-census.sh` as the list-only probe and describes `leak-count.py` separately as an independent counter. No host-wide process-liveness or complete-host saturation claim is made by F5; that scope is explicitly routed to Mori.

## Verdict

The Souji-to-Mori ownership direction and process identity wording hold. The reviewed documentation set fails internal consistency on test/selftest signal authority and F5 Core/Frontier status; it also leaves one stale Mori cross-reference and an imprecise “scratch residue” summary. No lane files were edited.