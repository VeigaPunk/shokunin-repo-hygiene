# SwarmScout09 — S221 re-open (round 30 wave 2)

## Status
STATUS: PASS — S221 re-fetched live and hashed; both Gate quotes and every S221 row cell checked against the bytes. Both quotes FOUND; one line-range defect and one scope/wording finding.
Tooling: curl (host), python3 -B; nothing installed.

## Evidence
- Live fetch of https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/operation-log.md: sha256 2a48dab85483f8bed666ccc1aebd458d70f4ff57ece1a122aee8889b3209ce18 == /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/sources/SHA256SUMS line 3 (operation-log.md) == committed snapshot; `cmp` identical; `wc -l` = 65 (row says 65).
- `grep -c abandon` on the live bytes = 0 (case-insensitive `grep -ci` also 0). Row's negative claim HOLDS.
- Line text (live bytes): L6 "Jujutsu records ... You can see the log with `jj op log`. Each operation object contains a snapshot"; L7 "of how the repo looked at the end of the operation. We call this snapshot a"; L9 "Git ref (in Git-backed repos) pointed, as well as the set of heads in the repo,"; L10 "and the current working-copy commit in each workspace."

## Findings
1. Quote 1 — FOUND, spans a line wrap: "Each operation object contains a snapshot of how the repo looked at the end of the operation." is on L6-L7 (17 words, no pipe). Matches only after whitespace normalisation, not as one source line.
2. Quote 2 — FOUND: "as well as the set of heads in the repo" is on L9 (10 words, no pipe), single line.
3. DEFECT-NOT-FATAL (location): the Gate bullet (corpus/knowledge/jj-keep-ref-expiry.md `## Gate`, S221 line), the header `source: S221` line (line 3) and claim 4 (line 41, "[S221, lines 5-8]") all say lines 5-8. Quote 2 is on L9, outside 5-8. Correct span is 5-9. The SOURCES.md anchor cell says `:5-12`, which does cover it, so the entry and the row disagree. L5 of the C3 gate (`quotes=14 bad=[]`) passed without catching this, i.e. it does not bind the quoted text to the cited line range [INFERENCE from c3-after-v1.txt L5 PASS; counter source not read].
4. SOURCES.md S221 row (line 166), cell by cell: kind docs / tier A — consistent with S220 (docs, A). scope "bookmark, tag and Git ref positions, the head set and each workspace's working-copy commit" — FOUND L8-L10. anchor "65 lines; :5-12 § Introduction; :47-56 § Loading an old version of the repo" — FOUND (L47-56 is the `--at-op` text; the section runs L45-65, 47-56 is a sub-range, ok). teaches "each operation object carries a view recording where every bookmark, tag and Git ref pointed at the end of that operation, plus the set of heads and the working-copy commit of each workspace" — FOUND; it drops the doc's "(in Git-backed repos)" qualifier, harmless here. Negative claim `grep -c abandon` = 0 — FOUND/true. "not GC thresholds" — true, no gc/expire/prune text in the file.
5. Tier/scope judgement: the row's scope cell is honest — it disclaims `op abandon` and GC and points to S220. The entry also keeps the `op abandon` content on S220 (line 2419 re-read: "The abandoned operations, commits, and other unreachable objects can later be garbage collected by using `jj util gc` command."). So a page that never says `op abandon` is NOT the citation for the abandon claim; it is cited only for one sub-fact (views hold the head set). Tier A is right for an official docs page at a pinned tag. What is overstated is claim 4's clause "which is the state a later `gc` reads": S221 says nothing about gc, and the source (git_backend.rs:1561) reads `index.all_heads_for_gc()`, not the op view (wave-1 SwarmScout09 found it returns heads among all indexed commits). Likewise "Abandoning is therefore the precondition that lets a keep ref fail the current-heads test" is an unlabelled inference; its real support is the measured steps 4 vs 5 (6 -> 2 keep refs), not S221. Recommended wording (for the L1, not applied): mark the last two sentences `[INFERENCE]` or cite S054 :1561 plus the record, and keep S221 as vocabulary-only; or drop S221 from claim 4.
6. Entry text line 17 says "two new rows, S220 and S221": consistent with the SOURCES rows, no issue.

## Attack log
- Re-fetch + hash of S221 vs SHA256SUMS — HOLDS.
- Quote 1 verbatim and <=25 words, no pipe — HOLDS (wrapped across L6-7).
- Quote 2 verbatim — HOLDS; its cited line range 5-8 — DEFECT-NOT-FATAL (L9).
- Row cells scope/anchor/teaches — HOLDS.
- Negative claim `grep -c abandon` = 0 — HOLDS.
- Citation fitness for claim 4 — DEFECT-NOT-FATAL: acceptable as a vocabulary source for the view/heads sentence only; the "state a later gc reads" and "precondition" clauses are not supported by S221.

## Deliveries
None beyond this report. Scratch /fast/scratch/hyaku/souji-r30/SwarmScout09 removed.
