STATUS: DONE — the r16/r17 auditor predates r18 patch delivery and clone contracts; its allow model was stale by r18.

# Findings

- **Patch delivery was introduced after the auditor was written.** The auditor was first added in `7a79dc2` (r16, 2026-10-20 11:55:35 -03); `a6ec781` amended it four minutes later. The r17 revisions were `ddb7347` and `4f48343` (latest 14:24:42 -03). The r18 wave-1 spec, which first requires executor patch delivery, appears in `3f822e8` (16:24:03 -03), after all those auditor commits. The r18 audit review also records that no r18 commit changed the auditor (`.ufo/waves/round-18/w2/RevSeatAuditContract.md:7,69`).
- **R16/r17 did not declare clone work or patch delivery.** R16 required seats to write only their report; commands specifically marked `ALLOWED-EXEC` could write in `/var/tmp/souji-r16-<SeatName>/` (`.ufo/waves/round-16/w2-spec.json:3`). R17 allowed a report plus files named in `OWN ONLY`, with test-command scratch in `/var/tmp/souji-r17-<SeatName>/` (`.ufo/waves/round-17/w1-spec.json:3`). Those were private temporary workspaces, not a declared clone-and-patch delivery workflow.
- **Clone work was declared in r18, in two distinct forms.** W1 instructs executors to use `/var/tmp/souji-r18-<SeatName>/lane`, edit their `OWN ONLY` file in that clone, and deliver a patch into the lane (`.ufo/waves/round-18/w1-spec.json:5,13`; e.g. `CensusWatchdog.patch`). W2 separately declares clones for items that execute lane code, at `/var/tmp/souji-r18w2-<SeatName>/lane` (`.ufo/waves/round-18/w2-spec.json:5`). Thus: clone writes were not declared in r16/r17; **yes, they were expressly declared in r18**.
- **Why the old auditor missed the new shapes:** r16/r17 auditor history models write authorization as the report plus parsed `OWN ONLY` targets, with scratch handled separately. R16 source review says the implementation's `/var/tmp` exception was actually too broad for the r16 contract, while the contract itself only authorized the seat's scoped scratch (`.ufo/waves/round-16/w2/RevSeatAuditCode.md:63-94`, especially `:77-94`). R17 then calibrated scratch to a context-derived prefix plus item name; its documented path semantics remain report/owned targets plus that scratch (`.ufo/waves/round-17/w1/SeatAuditPrecision.md:25,31-34`). It did not add a delivery-path field.
- **Patch false major:** the r18 W1 item says `OWN ONLY tools/souji-census.sh (in your clone)` and separately names the absolute `.patch` delivery destination (`.ufo/waves/round-18/w1-spec.json:13`). At the r18 auditor bytes, `OWN_RE` stopped at the parenthetical, `owned` therefore did not include that destination, and `allowed = [report, *owned]` omitted it. Consequently `write`/`edit` to the contract-ordered patch was `V-WRITE-SCOPE` major; the reported shell-redirection route was invisible (`.ufo/waves/round-18/w2/RevSeatAuditContract.md:15-17,75`).
- **Clone false majors are path-specific, not universal.** The r17 auditor derived scratch by matching `souji-r<N>-` in wave/context and appending the item name. That happened to align with an ordinary r18 W1 clone path, but not with W2's `souji-r18w2-` namespace: the regex instead derives `/var/tmp/souji-r18-`, so W2 clone writes fall outside scratch and become `V-WRITE-SCOPE` majors. A W1 retry/variant path also diverges: `MatrixR18b` worked under `/var/tmp/souji-r18-MatrixR18b/lane`, not the derived `.../MatrixR18/` (`.ufo/waves/round-18/w2/RevSeatAuditContract.md:11-13,27-30`). The review marks exact-name W1 clone writes clean (`.ufo/waves/round-18/w1/ScoutSeatAuditR18.md:25-32,84-87`).
- **Provenance verdict — [INFERENCE]:** this is primarily contract evolution, not evidence that the auditor deliberately rejected a declared r16/r17 workflow. The old report/OWN ONLY and scratch model followed those rounds' narrower rules; r18 added separate patch output and clone namespaces without corresponding auditor inputs. The model then misclassified compliant r18 outputs.

## Smallest faithful fix

Make the authorization inputs explicit per item rather than infer them from prose or the wave name:

1. Add exact patch destinations as `items[].writeAllow` and include them in the write allowlist (`allowed = [report, *item.get("writeAllow", []), *owned]`). This is the r18 reviewer’s one-line code change plus per-item declarations (`.ufo/waves/round-18/w2/RevSeatAuditContract.md:49-50,77`).
2. Add the exact clone scratch root as `items[].scratch` (or a list for explicitly authorized retry variants); use it for the existing containment check and remove the generic `/var/tmp/` fallback. This handles the r18 W1/W2 naming difference without granting all `/var/tmp` paths (`.ufo/waves/round-18/w2/RevSeatAuditContract.md:13,29,49,77`).

Keep patch permissions file-exact and clone permissions prefix-bounded; test each declared shape against an unauthorized lane `tools/` write. Prompt-only alternative for the patch is to place its absolute path inside `OWN ONLY` before the parenthetical, but explicit `writeAllow` preserves the distinction between the in-clone source file and the delivered patch. Git-mutation auditing is a separate detection gap, not fixed by these write-target allow entries (`.ufo/waves/round-16/w2/RevSeatAuditCode.md:68-76`; `.ufo/waves/round-18/w1/ScoutSeatAuditR18.md:89-105`).

# Evidence

- `corpus/lessons/round-16.md:101-102` records the r16 transcript audit and its `V-WRITE-*` observations; `.ufo/waves/round-16/w2/RevSeatAuditCode.md:63-94` reviews the auditor against the r16 contract.
- `.ufo/waves/round-17/w1/SeatAuditPrecision.md:1-3,23-25,31-37,89` records the r17 calibration, scratch derivation, and replay binding. `corpus/lessons/round-17.md:89` still reports fresh-transcript precision unmeasured.
- `.ufo/waves/round-18/w1-spec.json:5,13` and `w2-spec.json:5` are the changed contract shapes; `.ufo/waves/round-18/w2/RevSeatAuditContract.md:11-17,27-30,67-77` gives their observed auditor divergence and the smallest proposed fields.
- LSP unavailable: `read xd://lsp` returned “No such tool: xd://lsp”; the mounted-tool list contained no LSP device. I used direct reads of the named specs/reports and read-only Git history; no grep result is treated as semantic proof.
- Confidence: high for chronology, contract contents, and the documented classification paths; no auditor, fixture, or runtime check was executed in this seat.

# Commands run

Read-only Git history commands and observed output:

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --reverse --format='%h %ad %s' --date=iso-strict -- tools/souji-seat-audit.py
7a79dc2 2026-10-20T11:55:35-03:00 round-16: landing gate, its held-out fixture, seat transcript audit, regenerated r15 frozen record, wave-1 evidence (C2, R4, R5)
a6ec781 2026-10-20T11:59:22-03:00 round-16: narrow the gate's failure channel to contract STATUS vocabulary; audit honors ALLOWED-EXEC (C2, R5)
ddb7347 2026-10-20T12:42:34-03:00 round-17: C1 census D1/D2, C2 seat-audit precision + r16 transcripts bundle, C3 jj-aware receipt roots/novelty, D6 gate exact ids + replays, vadv54 stub, regenerate verdict
4f48343 2026-10-20T14:24:42-03:00 round-17: wave-2 fixes — census empty/locale/dot-admin + both soft diagnostics, jj_keep_novel leaf-blob/SIGPIPE-safe/fail-closed, gate exit-2 totality + mutant killers, seat-audit survivors, fixtures R17-27..29 and J10..J12
005f3d3 2026-10-20T21:11:54-03:00 round-19: wrap-aware carry gate, truthful audit shapes, durable revision stamps, F5 process-residue entry, D2/D5 repairs
```

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %ad %s' --date=iso-strict -- .ufo/waves/round-18/w1-spec.json .ufo/waves/round-18/w2-spec.json
4800fd7 2026-10-20T19:42:07-03:00 round-18: falsifier fixes — interruption-safe watchdog, gitfile timeout rows, proc precision/redaction, pointer scope and exemptions, local recipe identity, complete matrix provenance
3f822e8 2026-10-20T16:24:03-03:00 round-18: build — C1 bounded census + fixture session kill, C2 LG-DANGLING-PTR, C3 proc census, R1 recipe owner, R2 pointer repairs; wave-1 evidence
```

The other read-only Git history probes (outputs as observed):

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %ad %s' --date=short -- tools/souji-seat-audit.py
005f3d3 2026-10-20 round-19: wrap-aware carry gate, truthful audit shapes, durable revision stamps, F5 process-residue entry, D2/D5 repairs
4f48343 2026-10-20 round-17: wave-2 fixes — census empty/locale/dot-admin + both soft diagnostics, jj_keep_novel leaf-blob/SIGPIPE-safe/fail-closed, gate exit-2 totality + mutant killers, seat-audit survivors, fixtures R17-27..29 and J10..J12
ddb7347 2026-10-20 round-17: C1 census D1/D2, C2 seat-audit precision + r16 transcripts bundle, C3 jj-aware receipt roots/novelty, D6 gate exact ids + replays, vadv54 stub, regenerate verdict
a6ec781 2026-10-20 round-16: narrow the gate's failure channel to contract STATUS vocabulary; audit honors ALLOWED-EXEC (C2, R5)
7a79dc2 2026-10-20 round-16: landing gate, its held-out fixture, seat transcript audit, regenerated r15 frozen record, wave-1 evidence (C2, R4, R5)
```

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat --oneline 7a79dc2 -- tools/souji-seat-audit.py
7a79dc2 round-16: landing gate, its held-out fixture, seat transcript audit, regenerated r15 frozen record, wave-1 evidence (C2, R4, R5)
 tools/souji-seat-audit.py | 233 ++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 233 insertions(+)
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat --oneline a6ec781 -- tools/souji-seat-audit.py
a6ec781 round-16: narrow the gate's failure channel to contract STATUS vocabulary; audit honors ALLOWED-EXEC (C2, R5)
 tools/souji-seat-audit.py | 6 +++++-
 1 file changed, 5 insertions(+), 1 deletion(-)
```

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %ad %s' --date=iso-strict -- .ufo/waves/round-18/w1-spec.json
3f822e8 2026-10-20T16:24:03-03:00 round-18: build — C1 bounded census + fixture session kill, C2 LG-DANGLING-PTR, C3 proc census, R1 recipe owner, R2 pointer repairs; wave-1 evidence
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %ad %s' --date=iso-strict -- .ufo/waves/round-18/w2-spec.json
4800fd7 2026-10-20T19:42:07-03:00 round-18: falsifier fixes — interruption-safe watchdog, gitfile timeout rows, proc precision/redaction, pointer scope and exemptions, local recipe identity, complete matrix provenance
```

Also read the preregistration, r16/r17 contracts and auditor reports, r18 W1/W2 specs and auditor reviews, and current auditor excerpts. No selftest, fixture, build, or runtime command was run. No tools were installed or updated.

# Contract compliance

Only this assigned report was written. No subagents, `jj`, git mutations, signals, installs, or `/var/tmp` scratch were used. `census/operator-sweep-20261019/`, credentials, and secret contents were not opened.