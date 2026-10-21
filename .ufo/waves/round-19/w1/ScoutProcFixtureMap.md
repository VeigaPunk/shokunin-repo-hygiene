STATUS: DONE — mapped all P1–P19 cases against the committed F5 entry.

# Findings

Compared `tests/fixtures/r18-proc-census.sh` and `corpus/knowledge/process-residue-observations.md` at committed HEAD `7d199d2b2446cac1a0c6d08c53e1e950e99bec35`; both paths were clean versus HEAD. Fixture source was read, not executed. The map below distinguishes a general entry claim from the specific edge case named by a fixture.

| Case | Entry claim / coverage |
|---|---|
| P1 | Positive deleted-cwd detection and a nonempty FIFO-like `wchan`: supports the cwd row rule and measured `wchan` output. It does not test the kernel documentation's meaning or permission rule. Entry: `corpus/knowledge/process-residue-observations.md:21-22,38`; fixture: `tests/fixtures/r18-proc-census.sh:5,506-531`. |
| P2 | Positive argv path whose top-level directory is gone. Entry: `corpus/knowledge/process-residue-observations.md:39`; fixture: `tests/fixtures/r18-proc-census.sh:6,533-545`. |
| P3 | Live clean control absent. No explicit control-case claim; absence is implied by the entry's row-inclusion predicates. Entry: `corpus/knowledge/process-residue-observations.md:35-40`; fixture: `tests/fixtures/r18-proc-census.sh:7,547-548`. |
| P4 | `--prefix` selects P2 and excludes P6, supporting the argv side of the prefix claim. It does not exercise cwd selection or a positive fd match under a prefix. Entry: `corpus/knowledge/process-residue-observations.md:44`; fixture: `tests/fixtures/r18-proc-census.sh:8,550-567`. |
| P5 | Fresh residue excluded under `--min-age`. The entry names the option and `age_s`, but does not state the filtering behavior. Fixture: `tests/fixtures/r18-proc-census.sh:9,569-587`; entry: `corpus/knowledge/process-residue-observations.md:35,42`. |
| P6 | Password-shaped argv redaction supports the broad redaction claim; password is not one of the entry's named examples. Entry: `corpus/knowledge/process-residue-observations.md:58-59`; fixture: `tests/fixtures/r18-proc-census.sh:10,589-595`. |
| P7 | Census invocation emits no observed signal syscalls while fixture workers remain alive, directly supporting the census-mode no-signal claim. It does not test the separate selftest worker/session rule or reap authority. Entry: `corpus/knowledge/process-residue-observations.md:52-54`; fixture: `tests/fixtures/r18-proc-census.sh:11,597-618`. |
| P8 | Invalid usage exits 2. No entry claim describes invalid-usage behavior. Fixture: `tests/fixtures/r18-proc-census.sh:12,620-622`. |
| P9 | Positive deleted-fd-path report. Entry: `corpus/knowledge/process-residue-observations.md:40`; fixture: `tests/fixtures/r18-proc-census.sh:13,624-633`. |
| P10 | Deleted nested argv path is omitted while its top-level directory remains; this bounds the entry's top-level-directory criterion. The exact child-deleted boundary is not spelled out. Entry: `corpus/knowledge/process-residue-observations.md:39`; fixture: `tests/fixtures/r18-proc-census.sh:14,635-636`. |
| P11 | Reported starttime matches `/proc/<pid>/stat` field 22. The parser also checks the boot-id comment against the fixture's expected boot ID, but no reboot/identity comparison is exercised. Entry: `corpus/knowledge/process-residue-observations.md:46-48`; fixture: `tests/fixtures/r18-proc-census.sh:15,257-260,638-654`. |
| P12 | Live cwd whose literal path ends in ` (deleted)` is omitted. Entry: `corpus/knowledge/process-residue-observations.md:60-63`; fixture: `tests/fixtures/r18-proc-census.sh:16,657-662`. |
| P13 | Live fd whose literal path ends in ` (deleted)` is omitted, including a custom-prefix invocation. Entry: `corpus/knowledge/process-residue-observations.md:44,60-63`; fixture: `tests/fixtures/r18-proc-census.sh:17,664-681`. |
| P14 | Authorization/Bearer header value redaction; covered by the entry's headers example. Entry: `corpus/knowledge/process-residue-observations.md:58-59`; fixture: `tests/fixtures/r18-proc-census.sh:18,683-685`. |
| P15 | AWS-shaped argv redaction; covered by the entry's AWS example. Entry: `corpus/knowledge/process-residue-observations.md:58-59`; fixture: `tests/fixtures/r18-proc-census.sh:18,687-689`. |
| P16 | Slack-shaped argv redaction; covered by the entry's Slack example. Entry: `corpus/knowledge/process-residue-observations.md:58-59`; fixture: `tests/fixtures/r18-proc-census.sh:18,691-693`. |
| P17 | A similarly prefixed sibling is excluded, supporting prefix matching boundaries. The exact sibling-root edge is not named in the entry. Entry: `corpus/knowledge/process-residue-observations.md:44`; fixture: `tests/fixtures/r18-proc-census.sh:19,695-711`. |
| P18 | Where cwd, argv, and fd residue coexist, cwd wins. Entry: `corpus/knowledge/process-residue-observations.md:42-43`; fixture: `tests/fixtures/r18-proc-census.sh:20,713-732`. |
| P19 | Where argv and fd residue coexist with a live cwd, argv wins over fd. Entry: `corpus/knowledge/process-residue-observations.md:42-43`; fixture: `tests/fixtures/r18-proc-census.sh:21,734-751`. |

**Fixture cases with no corresponding entry behavior claim:** P8 (invalid-usage exit) and P5's substantive expectation (fresh rows are excluded by `--min-age`). P3's clean-control result is not stated as a case, though it follows from the entry's listed inclusion predicates. Details not named even though a broader rule corresponds: P6's password form, P10's deleted child with surviving top-level directory, and P17's similarly prefixed sibling. In particular, the entry's mention of `--min-age` is syntax only, not a claim about its effect.

**Entry claims not directly exercised by P1–P19, or only partly covered:**

- The source/documentation claims in `corpus/knowledge/process-residue-observations.md:15-31`: `cwd`/`fd` symlink and ptrace-permission facts; pipe/socket `type:[inode]` representation; `wchan` definition and permission; the `status`/`stat`/`statm` relationship and enumerated states; and the boundary that man-page documentation for `(deleted)` is about `exe`, not `cwd`/`fd`. P1 checks a FIFO-like `wchan` value, and P12/P13 exercise literal suffix paths, but no P case verifies those documentation or permission claims.
- Prefix semantics at `:44` are partial: P4 and P17 concern argv evidence; P13 is a negative literal-fd case. No case tests a positive fd match selected by `--prefix`, or that a cwd match remains selected with a prefix that excludes its path.
- Identity wording at `:46-48` is partial: P11 checks starttime and the common parser checks the current boot-id comment (`tests/fixtures/r18-proc-census.sh:257-260`). No P case compares snapshots across boots or demonstrates why a PID alone is insufficient.
- The exact mechanism stated at `:61-63`—classification by comparing held-link and target inodes—is not independently asserted by a P case. P12/P13 establish that the fixture's live named targets have matching inodes and must be omitted; P1/P9 provide deleted-path positives. These exercise the boundary outcomes, not an instrumentation of the implementation's comparison mechanism.
- The no-`environ` read boundary (`:55-57`), argv truncation (`:59`), own-uid exclusion of other UIDs (`:7-8,82-83`), and the selftest-only worker/session signal rule (`:52-54`) have no dedicated P case. P7 covers signal syscalls during census mode only.
- P7 is not a test of the full no-reap-authority policy (`:79-81`): it observes signal syscalls during one census run, not operator approval, fresh identity verification, a LOG record, or any broader action boundary. Likewise, the nomination-not-removal statement (`:8-9`) is a policy boundary, not a P-case result.
- The reported r18 counter disagreement, its cause, the two-window measurements, and their retained evidence (`:67-75`) have no corresponding P case.
- The stated limits at `:82-91`—other-UID/host-wide scope routing, non-atomic `/proc` observation, no proof of data unrecoverability or safe deletion, and PID-namespace/NSpid behavior—are not exercised by P1–P19.
- Provenance and environment metadata (`:1-3`) are not fixture assertions. The fixture cannot establish source-page access dates, the stated man-pages/host versions, or the historical verification commit.

The fixture parser validates the boot-id line, exact ten-column header, row shape and duplicate-PID exclusion (`tests/fixtures/r18-proc-census.sh:94-102,257-277`), so the entry's output-field inventory at `corpus/knowledge/process-residue-observations.md:42-43` has structural coverage. That does not make the parser a check of every field's full semantic accuracy.

# Evidence

- `corpus/knowledge/process-residue-observations.md:1-91` — committed entry claims and limits.
- `tests/fixtures/r18-proc-census.sh:4-27,94-103,257-315,502-751` — case inventory, common parser/helpers, and P1–P19 assertions.
- `.ufo/waves/round-19/preregistration.txt:51-64` — C3 intended scope (first F5 knowledge entry, source/metadata, list-only and no-reap boundary).
- HEAD observed as `7d199d2b2446cac1a0c6d08c53e1e950e99bec35`; `git diff --quiet HEAD -- tests/fixtures/r18-proc-census.sh corpus/knowledge/process-residue-observations.md` succeeded, confirming those inspected files matched committed HEAD.
- No LSP device is mounted (`read xd://lsp` returned “No such tool”); the mapping is based on source text and fixture assertions, not LSP semantic results.

# Commands run

- `git rev-parse HEAD && git status --short` (read-only); HEAD was `7d199d2b2446cac1a0c6d08c53e1e950e99bec35`.
- `git diff --quiet HEAD -- tests/fixtures/r18-proc-census.sh corpus/knowledge/process-residue-observations.md` (read-only; success, no output).
- Used source search/read tools for the cited sections. Did not execute `tests/fixtures/r18-proc-census.sh` or any census command.

# Contract compliance

Only this scoped report was written. No subagents, installs, network access, git/jj mutations, fixture execution, or other file edits. No restricted source or operator-owned path was opened.