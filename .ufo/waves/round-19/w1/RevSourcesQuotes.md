STATUS: DONE — source-row review complete; findings and residual risks recorded.

# Findings

- **MEDIUM — S079–S081 mix documentation with implementation-specific claims in `teaches`.** The cited Git passages support the stated command semantics, but S079 additionally says the helper adds durability/tree checks and that the 20-byte text predates SHA-256; S080 applies the helper's namespace arguments to `refs/jj`; and S081 describes the helper's treatment of non-1 nonzero statuses. Those are code/context claims, not claims established by the cited quoted passages. The assertions are explicitly attributed to the helper rather than silently presented as Git guarantees, and the local helper confirms the behavior (`tools/souji-rev-pin.py:69–83, 104–147`), but the task's quote-bounded teaches criterion still calls for separating them from these documentation rows or narrowing the cells. See `corpus/SOURCES.md:99–101` and the corresponding quote/context at `corpus/lessons/round-19.md:63–73`.
- **LOW — S079's reported quote count is wrong and remains uncorrected.** `wc -w` counts the located quote as 18 words, not the 20 claimed at `corpus/lessons/round-19.md:63–65`. It is still within the 25-word maximum. The appended correction acknowledges the S082/S083/S085 count errors but does not mention S079 (`corpus/lessons/round-19.md:148–154`).

# Residual risk

- All seven S079–S085 source URLs are public canonical Git or man7 documentation URLs, and each opened to the cited section on 2026-10-21. The quoted spans are located in the named anchors. `wc -w` counts: **S079 18; S080 19; S081 8; S082 13; S083 13; S084 15; S085 18** — all are ≤25. S082/S083/S085's stale initial counts are explicitly corrected by the appended note at `corpus/lessons/round-19.md:148–153`.
- The literal registry scan found no earlier use of these seven URLs. S086–S088 intentionally reuse S083–S085's exact URLs as append-only teaches-scope corrections (`corpus/SOURCES.md:103–108`); these are the only new same-URL pairs and should be disclosed as W04 correction duplicates, not treated as unrelated new sources. Their superseding purpose is also stated in `corpus/lessons/round-19.md:148–153`. Prior corpus guidance identifies W04 as advisory for append-only correction duplicates (`corpus/lessons/round-13-verifier-spotcheck.md:105–111`). I did not run the source-census command, so no runtime W04 output/count is claimed.
- The original over-attribution in S083–S085 is correctly called out and superseded by S086–S088: the disappearance/path-shaped-target inference, “never proof” and liveness-proof policy are explicitly identified as lane inference/policy, not page text (`corpus/SOURCES.md:103–108`; `corpus/lessons/round-19.md:148–153`). S082's suffix boundary is appropriately assigned to fixture behavior, not the cwd page (`corpus/SOURCES.md:102`; `corpus/lessons/round-19.md:74–76`).

# Verification gaps

- The `lsp` device is unavailable in this session (`read xd://lsp` returned “No such tool”); therefore no LSP status, references, definition or diagnostics were obtainable. The literal registry search below is only evidence of exact URL occurrences, not semantic proof.
- I opened all seven cited pages, but did not run a separate HTTP-status checker or the source-census validator. Their text was returned by the static reader; no status-code assertion is made.

# Evidence

- Worktree diff against `3ab2c81` shows the SOURCES provenance and S079–S088 additions; current rows are `corpus/SOURCES.md:15, 99–108`. The registry's named anchors resolve to: Git `git-rev-parse` OPTIONS `--verify` (https://git-scm.com/docs/git-rev-parse, accessed 2026-10-21); Git `git-for-each-ref` OPTIONS `<pattern>...` and `--format` (https://git-scm.com/docs/git-for-each-ref, accessed 2026-10-21); Git `git-diff` OPTIONS `--quiet`/`--exit-code` (https://git-scm.com/docs/git-diff, accessed 2026-10-21); proc cwd, fd, wchan and status DESCRIPTION (https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html, https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html, https://man7.org/linux/man-pages/man5/proc_pid_wchan.5.html, https://man7.org/linux/man-pages/man5/proc_pid_status.5.html; all accessed 2026-10-21).
- Quote text and Gate locators are at `corpus/lessons/round-19.md:63–90`; the F5 entry's sourced claims are at `corpus/knowledge/process-residue-observations.md:13–31`. The public pages support the cited description/access facts and do not document a cwd/fd deleted-suffix rule.

# Commands run

- Read-only `git diff -- corpus/SOURCES.md`, `git diff 3ab2c81 -- corpus/SOURCES.md`, and `git status --short` for worktree/diff context.
- Literal `grep` searches of `corpus/SOURCES.md`, round-19 lesson, corpus history and the local helper to locate rows, URLs, corrections and relevant behavior; no LSP server was available.
- Seven `wc -w` invocations over the exact Gate quote spans; results recorded above.
- Static reads of the seven exact public URLs named by S079–S085, plus the referenced local rows, lesson, knowledge entry and helper.
- No test, fixture, source-census, live census, install, or mutation was run.

# Contract compliance

- Wrote only this scoped report; did not edit source rows, implementation, tests, or any other lane file. No subagents were dispatched, no git/jj mutations or signals were issued, and no operator-owned path was opened. No tool was installed or updated; no scratch files were created.