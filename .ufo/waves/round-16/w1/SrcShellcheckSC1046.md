# SrcShellcheckSC1046 — SC1046 page: admissibility and proposed registry row

Scope: open `https://www.shellcheck.net/wiki/SC1046`, extract its text, decide whether it
may source the r15 "script did not parse" classification, and draft the SOURCES row or
rejection. Read-only; SOURCES.md was not edited.

## Opened (access date 2026-10-20)

- Served page: `https://www.shellcheck.net/wiki/SC1046` (render and raw HTML both read).
  **No version and no last-updated line is served.** The full raw HTML is 40 lines and its
  only provenance line is the footer: "ShellCheck is a static analysis tool for shell
  scripts. This page is part of its documentation." The page links itself to the GitHub
  wiki ("See this page on GitHub").
- Raw wiki markdown: `https://raw.githubusercontent.com/wiki/koalaman/shellcheck/SC1046.md`,
  fetched 2026-10-20. Text is identical to the served render; only link markup differs
  (raw carries `[[SC1047]]` where the render carries an `SC1047` link).
- Wiki revision: the history endpoint `…/wiki/SC1046/_history` (and its `.atom` form)
  returned no commit list to the text reader (HTTP 406 / JS shell), so **no wiki HEAD sha is
  recorded**; the anchor is date-based, as S015 already does for unstamped pages.
- Host tool for the severity recheck: `shellcheck 0.11.0`.

## Extracted text (exact, from the served raw HTML)

> **Couldn't find `fi` for this `if`.**
>
> Problematic code: `if true / then / echo "True" / done`; Correct code: same block ending
> `fi`.
>
> **Rationale:** ShellCheck has found an `if` statement that does not appear to have a
> matching terminating `fi`. This could be because it's missing entirely, or because the
> `if` statement was incorrectly terminated by a mismatched `done`, `esac`, `)` or similar.
> A companion warning SC1047 is emitted at the point where ShellCheck expected the `fi`.
> Check that the `if` statement is completely and correctly terminated.
>
> **Exceptions:** None

## Verdict: reject as the source for the r15 failure classification

The page is a version-agnostic definition of one diagnostic. It observes nothing about
r15, about `tools/souji-census.sh`, or about shellcheck 0.11.0 behaviour, so it cannot
carry a measured claim about those bytes. The classification's admissible basis is
own-work tool output at named revisions:

- `b410186cea626a67c92396ac58fbd57fb86876ac`, `tools/souji-census.sh` blob
  `86490d0dfb9b58a41bb4c4440d98df36686ab196`, 75,656 bytes:
  - `bash -n` → exit 2, `line 1368: syntax error near unexpected token '}'`.
  - `shellcheck 0.11.0` → SC1009 `:1320:14`, **SC1046 `:1324:3`**, SC1073 `:1324:3`,
    SC1047 `:1368:1`, SC1072 `:1368:2`, exit 1.
  - `shellcheck -S error` → SC1046, SC1073, SC1047, SC1072 survive, exit 1: a parse
    failure is not demoted by severity filtering.
  - Site: `list_repos()` opens at `:1320`, is called at `:1376`, and the `if` at `:1324`
    (`if [ "$INCLUDE_ROOT" = 1 ] && …; then`) has no `fi` before the function's closing
    `}` at `:1368`.
- `cc2168325768d5356a82c039dcdf787377c55784` (blob `3f037a2f…`, 55,730 B) and
  `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (blob `ea05ba72…`, 65,991 B): `bash -n`
  exit 0. The restore target and the restored commit parse; only b410186 does not.

This matches the r15 spot-check's independently recorded row
(`corpus/lessons/round-15-verifier-spotcheck.md:41-42`: b410186 `bash-n=2 sc=1`, "SC1046 at
1324 … has no `fi`"). Two independent readings of the same bytes agree; the wiki page adds
neither reading.

Two calibration facts fall out of the same comparison:

1. **Docs prose loses to host output on severity.** The page calls SC1047 a "companion
   *warning*"; shellcheck 0.11.0 emits it as `error`. Transcribing the page's word as the
   severity would be a Q1/Q2 failure, and it is why the page cannot be the severity
   authority even for its own diagnostic.
2. **A gate must not key on the SC1046 spelling** (Q11). Parse status is a behaviour:
   `bash -n` exit and shellcheck parse diagnostics. Keying on one code would miss any other
   truncation; the page itself lists `done`, `esac` and `)` as alternate terminator
   mistakes, not alternate codes.

Cross-domain line (R6): the classification uses *host tool output* (bash parser, shellcheck
0.11.0) over *lane git objects* at three revisions; the web page is *vendor documentation*
for the name only. It is corroboration, not a source for the observation.

## Proposed SOURCES row (S043; last row is S042 — L1 renumbers)

Following the R7 convention (opened-and-excluded sources are curated in the registry, not
left in search-log prose), the primary draft is a `rejected` row:

| S043 | ShellCheck wiki SC1046 — https://www.shellcheck.net/wiki/SC1046 | docs | A | SC1046's definition, its SC1047 pairing and its stated exceptions; not evidence that any named script failed to parse | SC1046.md § Rationale and § Exceptions, page as served 2026-10-20 (no version or last-updated line; footer reads "This page is part of its documentation"); raw wiki markdown at raw.githubusercontent.com/wiki/koalaman/shellcheck/SC1046.md fetched 2026-10-20, text identical; host shellcheck 0.11.0 | an `if` with no matching terminating `fi` (missing, or ended by a mismatched `done`, `esac`, `)`) gives SC1046 at the `if` plus a companion SC1047 where `fi` was expected, Exceptions: None. REJECTED as the source for the r15 failure classification: that is own-work tool output at named revisions (`bash -n` exit 2 at b410186:1368; SC1046 :1324 and SC1047 :1368, both still emitted under `-S error`), and the page labels SC1047 a "warning" while 0.11.0 emits it as error. flip: a lesson or gate cites the SC1046/SC1047 pairing as a definition and records the host severity — then open the queued row below | rejected | 2026-10-20 | 365d | — |

Flip target, if L1 instead decides to curate the definition (same number, either/or):

| S043 | ShellCheck wiki SC1046 — https://www.shellcheck.net/wiki/SC1046 | docs | A | what SC1046 means, its SC1047 pairing and its no-exception scope; not proof of any script's parse status | SC1046.md § Rationale and § Exceptions, page as served 2026-10-20 (no version or last-updated line); raw wiki markdown at raw.githubusercontent.com/wiki/koalaman/shellcheck/SC1046.md fetched 2026-10-20, text identical; host shellcheck 0.11.0 | an unclosed `if` yields SC1046 at the `if` and companion SC1047 where `fi` was expected; on shellcheck 0.11.0 both are error severity, so a parse failure is never demoted by `-S error` | queued | 2026-10-20 | 365d | — |

Recheck `365d` mirrors S027 (the only other ShellCheck-wiki row), since the page carries no
release stamp to key `on-release` to. Used-by stays `—`: C2's declared source is GNU Bash
`set -n`; this page is not the landing gate's source and must not be folded into that
claim.

## Remaining unknowns

- Wiki HEAD sha not resolved (history endpoint gave no revision list); HTTP `Last-Modified`
  headers were not read (probe rule). The row's anchor is therefore date-based.
- The page is version-agnostic: it cannot distinguish shellcheck 0.11.0 from other releases,
  and the host severity was taken only from the installed binary.
- Bash version under `bash -n` was not recorded (not queried).

STATUS: no lane-blocking failure; the only gap is that the SC1046 page has no revision
stamp, so the proposed row pins by access date (S015 precedent) rather than by sha.

## Commands

```sh
shellcheck --version; echo ---; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify b410186^{commit} cc21683^{commit} cbf688ab2ab28e38103e5a9417ca525b5f2ed423^{commit}; echo ---; git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only b410186 | grep -c . ; git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree b410186 tools/
L=/home/vgpnk/Projects/shokunin/souji-shokunin; for r in b410186 cc21683 cbf688ab2ab28e38103e5a9417ca525b5f2ed423; do echo "== $r"; git -C "$L" rev-parse --verify "$r^{commit}" 2>&1; done; echo ---; for r in b410186 cc21683 cbf688ab; do echo "== $r"; git -C "$L" ls-tree "$r" -- tools/souji-census.sh 2>&1; git -C "$L" cat-file -s "$r:tools/souji-census.sh" 2>&1; done
L=/home/vgpnk/Projects/shokunin/souji-shokunin; echo "== b410186 bash -n"; git -C "$L" show b410186:tools/souji-census.sh | bash -n; echo "exit=$?"; echo "== b410186 shellcheck"; git -C "$L" show b410186:tools/souji-census.sh | shellcheck -f gcc - ; echo "exit=$?"; echo "== cc21683 bash -n"; git -C "$L" show cc21683:tools/souji-census.sh | bash -n; echo "exit=$?"; echo "== cbf688ab bash -n"; git -C "$L" show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | bash -n; echo "exit=$?"
L=/home/vgpnk/Projects/shokunin/souji-shokunin; echo "== shellcheck -S error on b410186 bytes"; git -C "$L" show b410186:tools/souji-census.sh | shellcheck -S error -f gcc -; echo "exit=$?"; echo "== defect window at b410186"; git -C "$L" grep -n -B2 -A8 'if \[ "\$INCLUDE_ROOT"' b410186 -- tools/souji-census.sh
L=/home/vgpnk/Projects/shokunin/souji-shokunin; git -C "$L" grep -n 'list_repos' b410186 -- tools/souji-census.sh
L=/home/vgpnk/Projects/shokunin/souji-shokunin; for r in b410186 cc21683 cbf688ab2ab28e38103e5a9417ca525b5f2ed423; do git -C "$L" rev-parse --verify "$r^{commit}"; done
```

Probe disclosures:

- The first command's `rev-parse --verify` with three revisions fails (`--verify` takes one
  revision); it produced no hash. It was re-run correctly in the last command.
- The first command's `ls-tree -r --name-only b410186 | grep -c .` enumerates the whole
  tree at that revision but printed only the count (1787): no paths, no file contents.
  The same command's `ls-tree b410186 tools/` printed the `tools/` directory listing
  (names, modes, blob ids, no contents). Both are disclosed as unnecessary breadth even
  though neither read file content.
- Non-shell probes were `read`/`grep`/`glob` on exact named files and URLs only:
  `corpus/SOURCES.md`, `corpus/QUALITY.md`, `corpus/lessons/round-15.md`,
  `corpus/lessons/round-15-verifier-spotcheck.md`, `census/round-12/sources-gate.md`,
  `.ufo/waves/round-16/w1-spec.json`, and the SC1046 URLs above.
- Tool installs/updates: none.
