STATUS: DONE — C2 precision attacked with 3 synthetic-lane probes and a validated minimal patch; every pinned count reproduces, but 12 realistic citation grammars produce false LG-DANGLING-PTR.

# Attacked claim

C2 calibration, precision half: `tools/souji-landing-gate.py` at `5efb519f00075d958c3d1109ef6fcb24c487eb87` reports **0 findings** at round 18, **10** at `b576341`, selftest **53/0**, `tests/fixtures/r18-landing-pointers.py` **11/0**, r17 pinned replays match — i.e. the gate is calibrated enough to be the r18 admission oracle. Ticket-named grammar: URLs containing `/tools/`, `path:12-14,20`, one-level `{a,b}`, `round-{6..11}`, trailing `…`, quoted shell `--spec a.json:b.json`.

# Method (clone `/var/tmp/souji-r18w2-ScoutGrammarFalsePos/lane`, detached 5efb519)

Three disposable git repos shaped exactly like `tests/fixtures/r18-landing-pointers.py` `Repo` (same `BASE_DOCS`, synthetic round 77, lesson + `.ufo/waves/round-77/w1` so the carry check evaluates), invoked as the fixture does:

    python3 <gate> --root <repo> --rev <rev> --round 77

Every target I call "present" was verified with `git cat-file -e <rev>:<path>`. Probe 2 cites **only files that exist at the rev**; its findings are unambiguously false. Probe 3 mirrors the lane author's own `LOG.md:145` brace style in the scanned round section.

# Findings — false LG-DANGLING-PTR (pre-fix, 5efb519 bytes)

Probe 2: `exit 1`, **19 dangling**, **1 true** (`census/round-18/absent.json`), **13 false findings on existing or mangled targets** (12 grammar classes), plus scope/output classes; probes 1 and 3 add F3 (elision, probe 1), F14 (probe 1), F15 (probe 3).

| # | Citation (style) | Reported path | Gate evidence |
|---|---|---|---|
| F1 | `` `census/round-18/live-fleet-pairs/…` `` | `census/round-18/live-fleet-pairs/…` | skip set at gate:721 has no `…`; directory exists |
| F2 | `` `census/round-18/live-fleet-pairs/pair1-….tsv` `` | same with `…` | same; elision mid-basename |
| F3 | `` `tools/souji-…` `` (probe 1) | `tools/souji-…` | same |
| F4 | `` `census/round-18/{kept.json, kept2.json}` `` | `census/round-18/{kept.json` | token stops at the brace-internal space (regex 124-129); both files exist |
| F5 | `` `census/round-18/{kept.json:1,kept2.json:1}` `` | `…kept.json:1`, `…kept2.json:1` | `_trim_pointer_token` runs before brace expansion (700-707 vs 747-748); both exist |
| F6 | `census/…/pair{1..2}-base-b576341.tsv` | unexpanded token | `ROUND_RANGE_RE` 130 + `_expand_round_ranges` 682 only expand `round-N..N`; both pair files exist |
| F7 | `` `tools/souji-census.sh --spec census/round-18/kept.json:kept2.json` `` | `…kept.json:kept2.json` | trim only strips numeric `:line` (706); both exist |
| F8 | `` `--pair census/round-18/kept.json:census/round-18/kept2.json` `` | both paths colon-joined | same; both exist |
| F9 | `` `census/round-18/kept.json#L1` `` | `…kept.json#L1` | no `#L` handling in trim; file exists |
| F10 | `` `census/round-18/source.md:12–14` `` | `…source.md:12–14` | line regex accepts ASCII `-` only; file exists |
| F11 | `` `census/round-18/kept.json\` `` (markdown hard break) | trailing `\` kept | `rstrip(".,;:!?")` 701; file exists |
| F12 | `\|census/round-18/kept.json\|` (table, no spaces) | trailing `\|` kept | same; file exists |
| F13 | `` `tools/souji-census.sh;census/round-18/kept.json` `` | one compound token | top-level splitter accepts only `,` (728); both exist |
| F14 | `` `census/round-18/kept{,.json}` `` | whole token | `_expand_braces` bails on empty alternative (675); `kept.json` exists |
| F15 | `**Artifacts.** census/round-18/{seat-01..64.json, approvals-*.tsv,` (probe 3; exact `LOG.md:145` shape) | `census/round-18/{seat-01..64.json` | unbalanced brace is **not** skipped; `*` is on the next line, so the `<>*` skip does not fire |

Non-citation claims also reported:

| # | Citation | Reported | Note |
|---|---|---|---|
| F16 | `<!-- census/round-18/removed.json -->` | `census/round-18/removed.json` | `HTML_COMMENT_RE` exists (112) but is unused in `check_pointers` (827-840) |
| F17 | `git show <rev1>:census/round-18/removed.json` | `census/round-18/removed.json` | rev-qualified; blob exists at rev1 |
| F18 | `-census/round-18/removed.json` (unified-diff quote) | same | lookbehind 125 admits `-` |
| F19 | `https://host/find?path=tools/absent-file.sh` (probe 3) | `tools/absent-file.sh` | query/fragment form; absent local target. Plain `https://github.com/…/tools/absent-file.sh` is correctly **not** flagged |
| F20 | `… --out census/round-18/proc.tsv` / `> …` | `census/round-18/proc.tsv` | output target, not a citation. **Not scored as a defect**: the lane commits records produced this way (`census/round-18/*.json`), so the path is an evidence claim |

Exact probe-2 pre-fix output (target set verified present at `63d72a6ba8d9`):

    exit 1 dangling: 19
    plain-missing  'census/round-18/absent.json'  <- SKILL.md:29
    anchor         'census/round-18/kept.json#L1' <- SKILL.md:12
    brace-lineref  'census/round-18/kept.json:1'  <- SKILL.md:6
    pair-alias     'census/round-18/kept.json:census/round-18/kept2.json' <- SKILL.md:11
    spec-pair      'census/round-18/kept.json:kept2.json' <- SKILL.md:10
    hardbreak      'census/round-18/kept.json\'  <- SKILL.md:14
    table-nospace  'census/round-18/kept.json|'  <- SKILL.md:15
    brace-lineref  'census/round-18/kept2.json:1' <- SKILL.md:6
    ellipsis-name  'census/round-18/live-fleet-pairs/pair1-….tsv' <- SKILL.md:9
    shell-range    'census/round-18/live-fleet-pairs/pair{1..2}-base-b576341.tsv' <- SKILL.md:7
    brace-space    'census/round-18/live-fleet-pairs/{pair1-base-b576341.tsv' <- SKILL.md:5
    ellipsis-dir   'census/round-18/live-fleet-pairs/…' <- SKILL.md:8
    out-flag       'census/round-18/proc.json'   <- SKILL.md:20
    redirect-space 'census/round-18/proc.tsv'    <- SKILL.md:19
    fenced-rev-qualified 'census/round-18/removed.json' <- SKILL.md:16
    fenced-diff    'census/round-18/removed.json' <- SKILL.md:17
    html-comment   'census/round-18/removed.json' <- SKILL.md:18
    endash-lines   'census/round-18/source.md:12–14' <- SKILL.md:13
    semicolon      'tools/souji-census.sh;census/round-18/kept.json' <- SKILL.md:21

Probe 3 (author's `LOG.md:145` shape in the scanned round section):

    pre-fix  exit 1 findings 1: 'census/round-18/{seat-01..64.json' | LOG.md:5
    post-fix exit 0 findings 0

# What holds (no false positive)

`path:12-14,20`, `path:12,14-20`, `path:12`; simple one-level `{a,b}`; `round-{6..11}` and unbraced `round-16..18`; multi-group `{17,19}`; `tools/<script>.py`, `census/round-N/…`, `tests/fixtures/*.sh` (skipped, FN not FP); plain GitHub/raw URLs containing `/tools/` and `/census/` (lookbehind 125 blocks them even when the local target is absent — probe 3); `./tools/…`, `<tools/…>`, `**tools/…**` (skipped, FN); a missing path still fires correctly.

# Calibration facts about the claim itself

All claimed numbers reproduce from the clone, but the after-number is fleet-root-dependent and unrecorded:

    $ python3 tools/souji-landing-gate.py --root . --rev b576341… --round 18 --fleet-root <synthetic fleet>
    exit 2, findings=10 (9 LG-DANGLING-PTR + 1 LG-FROZEN-MEASURED)      # claim 10 holds
    $ … --rev 5efb519f… --round 18 --fleet-root <synthetic fleet>
    exit 0, findings=0 (ptr_exempt=3, ptr_fleet=3)                      # claim 0 holds
    $ … --rev 5efb519f… --round 18            # no fleet root
    exit 1, findings=3 (the three fleet citations at corpus/README.md:217, jj-colocation-receipts.md:148)

`census/round-18/` commits no after-run record: `gate-pointers-before-b576341.json` (10 findings) is the only pointer record, and `gate-replays-r18.json` binds `lane_head 42d9ff39` with rounds 13-16 only; its `match:true` and the selftest 53 / fixture 11/0 are reproducible (base gate: selftest 33/0, fixture 11/**4**), but none of those cases exercises F1-F15.

Fleet laundering (calibration, not FP): the classifier at 849-853 applies to **any** unresolved path, not only `../` escapes. A lane-relative `census/round-18/owned.json` absent from the lane but present under `--fleet-root` is classified `fleet` and silenced:

    no-fleet exit 1 ['LG-DANGLING-PTR\tcensus/round-18/owned.json']
    fleet    exit 0 []

`corpus/lessons/round-18.md:27` says "an elided token … [is] not [a] token"; F1-F3 show attached elisions **are** tokens and **do** fire. `CriticC2Calibration.md:35` says unbalanced braces are skipped; F15 shows they are not (probe 3 pre-fix).

# Verdict

**Fails** on the precision axis for the two ticket-named styles `…` and `--spec a.json:b.json`, and for brace lists with a space, per-member line refs, or a shell range; **holds** for the other named styles (URLs with `/tools/`, `path:12-14,20`, simple `{a,b}`, `round-{6..11}`) and for every pinned count. The gaps are 12 target-existing grammar classes (F1-F15; F1-F3 are one elision class) plus 3 scope classes (F16-F18) and one URL-query class (F19), none covered by selftest/fixture.

# Smallest fix (validated in a `/var/tmp` copy, sha256 73456712c7da9b98b20332c6165b0e665a153231d3ca7b51291b1090f50cabc1, 93 insertions / 14 deletions, no lane file touched; the copy was removed with the clone, reproduce from the hunks listed)

Per class, minimal edits: (F1-F3) skip a token containing `…`; (F4) strip whitespace inside `{…}` before `finditer`; (F5) apply `_trim_pointer_token` to expanded members; (F6) add a numeric `{N..M}` brace-range expander; (F7-F8) split a colon-joined pair when both sides end in a filename, resolving the tail against dirname(head); (F9) strip `#L<d>(-L<d>)?`; (F10) accept `–` in the line-range regex; (F11-F12) extend `rstrip` to `\` and `|`; (F13) split at top-level `;`; (F15) skip unbalanced-brace tokens; (F16) blank `<!--…-->` per source (newline-preserving); (F17) skip matches preceded by a 7-40 hex `rev:`.

Validation of that patch:

    py_compile rc 0
    --selftest                          SELFTEST pass=53 fail=0        (unchanged)
    r18-landing-pointers --tool fix     SUMMARY total=11 failed=0      (unchanged)
    --root lane --rev 5efb519 --round 18 --fleet-root …   findings=0  (unchanged)
    --root lane --rev b576341 --round 18 --fleet-root …   findings=10 (unchanged)
    probe 1 dangling  20 -> 7   (true: missing-a, absent; residual: 3 output paths, 1 diff quote, ../ escape, empty-brace alt)
    probe 2 dangling  19 -> 4   (true: absent; residual: 2 output paths, 1 diff quote)
    probe 3 LOG-style  1 -> 0   ; probe 3 dangling 3 -> 1 (query-URL residual)

Residual after the patch: output-target paths (F20, deliberately kept — they are committed evidence claims), unified-diff quotes (F18; fix = add `-` to the lookbehind), URL query/fragment forms (F19; low realism), `{,.json}` empty-alternative mangling (F14; expanding empty alternatives would yield the correct `census/round-18/kept` finding), and the fleet-laundering suppression above.

No tools installed or updated. Clone and `/var/tmp` probes removed after this report; no lane file was modified.
