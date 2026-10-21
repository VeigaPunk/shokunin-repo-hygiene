STATUS: DONE — S038’s timeout claims remain supported by the dated Coreutils 9.12 capture, but its installed-info line anchors are stale.

# Findings

- **Re-opened source:** The canonical GNU manual URL timed out on a live fetch. The dated Wayback capture `20260919212856` opened successfully and identifies the page as `timeout invocation (GNU Coreutils 9.12)`. The `--kill-after` section still says “Ensure the monitored command is killed by also sending a ‘KILL’ signal.” The Exit status block still says “124 if command times out, and --preserve-status is not specified.” Both are under §23.6 of the archived page (GNU manual URL, accessed 2026-10-21; anchor: Wayback capture 20260919212856, `--kill-after` and `Exit status`). The claims therefore still match. The literal presentation is not byte-for-byte identical to the older quote: the 9.12 page renders the metavariable as italic lower-case `command`, while the 9.11 quotation used upper-case `COMMAND`.
- **Observed anchor drift:** S038 records Coreutils 9.11-2 info locations `--kill-after` KILL sentence 15319–15320 and exit 124 at 15365 (`corpus/SOURCES.md:58`). Round 18 records the 9.11-2 → 9.12-2 upgrade and the replacement info file: node starts at 15710, `--kill-after` header at 15744, and exit 124 at 15791 (`.ufo/waves/round-18/w1/SrcCoreutilsTimeout.md:13-18,107-111`; `corpus/lessons/round-18.md:65-67`). These are version-specific line locators, not a uniform offset. The report does not record the exact new 9.12 info line for the KILL sentence; do not infer one from the option header.
- **Append-only recommendation:** Append a new row, provisionally **S089** (S088 is the last row in the inspected registry, `corpus/SOURCES.md:105-108`), anchored to the dated capture and its content identity rather than info line numbers. Suggested row:

  `| S089 | GNU Coreutils timeout invocation manual — https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html | docs | A | GNU Coreutils 9.12 timeout: --kill-after sends KILL; timeout exit 124 without --preserve-status | Wayback capture 20260919212856 (memento 2026-09-19 21:28:56 GMT), page title “timeout invocation (GNU Coreutils 9.12)”, §23.6; archived HTML SHA-256 8e0c74666b842b0f745455f9e853ba65f82776f379d57640d26291555e85259c | supersedes S038 only as the current 9.12 locator/version; S038 remains the historical 9.11-2 correction; --kill-after sends KILL and timeout returns 124 without --preserve-status; no residue/deletion guarantee | mined | 2026-10-21 | on-release | corpus/lessons/round-18.md |`

  The capture digest above is the uncompressed HTML digest recorded by the round-18 source report, not recalculated here; the capture itself was reopened in this check. Its report also records the 9.12-2 installed info digest `a2478c0f130ea61db02efefdf675e311a16ea16149bd0d309841d58bf77df494` (`.ufo/waves/round-18/w1/SrcCoreutilsTimeout.md:13-16,107-111`).
- **Supersession decision:** Yes, append a row to supersede S038 **for the current 9.12 source anchor/version only**. Do not alter or discard S038: its 9.11-2 correction remains historically accurate. The shared canonical URL should be disclosed as a duplicate-URL advisory if the row is integrated. Confidence: high for the capture’s page/version and the two claims; medium for the new installed-info line map because the exact KILL sentence line was not recorded. The live page remained unreachable, and the installed man-page roff locations were not rechecked in this run.

# Evidence

- `corpus/SOURCES.md:58` — S038’s version-specific 9.11-2 info locators and narrow teaches claim.
- `.ufo/waves/round-14/w1/SourceTimeout.md:89-104,115-126` — originally located quotations and their 9.11 info/man anchors.
- `.ufo/waves/round-18/w1/SrcCoreutilsTimeout.md:13-18,32-38,104-111` — live-fetch failure; capture timestamp, version, recorded HTML digest, and 9.12-2 info digest/locations.
- `corpus/lessons/round-18.md:65-67` — records that S038’s prior anchor was routed for recheck after the upgrade.
- Reopened page: https://web.archive.org/web/20260919212856id_/https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html (accessed 2026-10-21; §23.6 `--kill-after` and `Exit status`). The page states the same KILL and exit-124 conditions quoted above.

# Commands run

- `read https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html` — failed with a fetch timeout.
- `read https://web.archive.org/web/20260919212856id_/https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html` — succeeded; verified the page title, §23.6, and both claims.
- Read the cited SOURCES, round-14/18 lesson, and round-18 scout-report sections; searched for S038/S085 and located the latest source-row IDs.
- No shell commands, installs, or scratch files.

# Contract compliance

Only this scoped report was written. No lane source, registry, tests, census, or corpus files were changed. No subagents, git/jj mutations, pacman transactions, or prohibited reads were used.