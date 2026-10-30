# R43 source gate — local committed snapshots only

Axes: byte provenance, quote fidelity, locator precision, registry shape, scope calibration.

Opened locally on 2026-10-30; no network requests. Snapshot bytes match the frozen commit f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 (both working-file and git-show SHA256 results agree). This is not evidence of a live-page recheck or the original fetch date.

## S260
- URL: https://man7.org/linux/man-pages/man2/symlink.2.html
- Snapshot: `census/round-43/sources/man2-symlink.html`
- SHA256: `c929903b2dec6c985e149ca27d509243e04fc80861d8b98c1f98e2325e857178` — matches requested hash.
- HTML section: `ERRORS` (heading line 143), `ELOOP` entry lines 163-164.
- Located quote (9 words, HTML tags removed, whitespace joined): “Too many symbolic links were encountered in resolving linkpath.”
- Version: `Linux man-pages 6.19`, footer line 239; `COLOPHON` line 229 names `man-pages-6.19.tar.gz`. Footer manual date 2026-02-08; colophon fetch date 2026-09-09 at line 232, neither is this seat's opening date.
- Finding attacking S260 requested grounding: the ERRORS quote concerns symlink(2) linkpath resolution. It does not document O_NOFOLLOW, a leaf-link open refusal, or Souji's --json policy. Requested wording: “a leaf symlink named by --json is refused, ELOOP is what an O_NOFOLLOW walk raises on a link”. The draft preserves the requested application scope but explicitly separates it from what these source bytes establish. No instrument or source was changed.

## S261
- URL: https://docs.python.org/3/library/subprocess.html
- Snapshot: `census/round-43/sources/python-3-library-subprocess.html`
- SHA256: `5935a4afd34ad560cc5b66f0ed6e90d4d63ba9047ad8f367d5081474650078b5` — matches requested hash.
- HTML section: `Using the subprocess Module` (section id `using-the-subprocess-module`, lines 264-265), `subprocess.run` entry (line 270), timeout paragraph lines 288-294.
- Located quote (25 words, HTML tags removed, whitespace joined), lines 289-291: “If the timeout expires, the child process will be killed and waited for. The TimeoutExpired exception will be re-raised after the child process has terminated.”
- Footer version marker, line 2037: `Last updated on Oct 30, 2026 (04:20 UTC).`
- Scope boundary: direct-child termination/waiting is documented; load-robust fixture classification is an application inference. Lines 291-294 warn that initial process creation cannot be interrupted on many platform APIs; no fixed wall-clock delivery guarantee or descendant-tree kill is established.

## Registry allocation and shape
Committed `corpus/SOURCES.md` at frozen commit: 183 registry rows, 183 unique ids, maximum S259; S260 count 0, S261 count 0. Existing ids are not contiguous: row count is not 259. Next append ids are S260 and S261, not a claim that historical gaps are available for reuse. Column order from header line 28: id, source, kind, tier, scope, anchor, teaches, status, opened, recheck, used-by. `rows.tsv` contains two headerless tab-separated rows in that order, with no pipe characters in cells. Both are draft tier-A docs, status mined; no registry admission or lesson integration was performed.
