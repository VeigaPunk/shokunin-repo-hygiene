# Round 65 — corpus paperwork draft for the L1 to finalize (SEAT DRAFT, not the landed lesson)

Base `4a43a4d919c5b51ae9be859a1266ce4b11337b0b` (lane master at round start, clean, pushed). Instruments
`2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8`; do-nothing controls + SHA256SUMS pin `3c5bfdc0db50785cb7b2ec60e509facf2d7e9f25`;
FREEZE `d2850b3eb160ae65c1c65b93753dfec7f4153b45`; writer+SKILL landing `022cf9791ec83ca6c854733c66c84705016f4d67`;
S2 literal wrap fix `40a371d8232e89e4f50d3ece4ff8779f44c0ee4c`; chronology arm landing
`16da2445088ccca15aa32c66841d878ee57a8706` (post-freeze — see M1 below).

This file is a DRAFT delivered by seat `S65ScribeEntry` under
`.ufo/waves/round-65/w1/S65ScribeEntry/`. The L1 (planner + integration owner) owns the final text, the
landed paths (`corpus/lessons/round-65.md`, `corpus/knowledge/untracked-visibility-concealment.md`, the
S297 row in `corpus/SOURCES.md`), and every commit. No lane file was edited by this seat.

## Claim

Two frozen claims, both declared and frozen at `d2850b3e…`. The predicates are frozen; this wave attacks or
reproduces them and never amends them.

### C1 — operability (axis: runnable fixture matrix on an input edge class, per QUALITY Q59)

- Base: `4a43a4d919c5b51ae9be859a1266ce4b11337b0b`
- Counter: `census/round-65/c1-counter.py`, sha256 `6401b35db7ff67883ff17af90e3415057017edc324aeecc053b1843fae1b8d2f`
- Population: `census/round-65/c1-matrix.tsv`, sha256 `a521170cd13eee52a3ad671388f84b84b4ebdd55ec1bc682f4324c1839d0f133`
  (19 rows: A, B, C, D, T1–T5, N1–N4, V1, V2, MOD, SY1, SY2, P13)
- Candidate: `tools/souji-receipt-write.py` at the measured revision `40a371d8232e89e4f50d3ece4ff8779f44c0ee4c`
- Frozen target: `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5
  class_mismatches=0 regress=PASS`, `EXIT=0`
- Kill: any of `new_forgeries>0`, `new_honest<5`, `class_mismatches>0`, `regress=FAIL`, or a nonzero exit
- Do-nothing control: `census/round-65/controls/c1-do-nothing.txt` — the same counter with the base bytes in
  the new slot prints `new_forgeries=12` and exits 1
- After receipt: `census/round-65/records/c1-after.txt` (binds `40a371d8…`)
- Realizability probes (committed pre-freeze): `census/round-65/probes/` —
  `c1-probe-writer-be344a7d.txt` (the full 19-row probe) and `n4-n2-dispute-*` (the r64 M1/M5 dispute shapes)

### C2 — calibration (the lowest owned axis, score 7)

- Base: `4a43a4d919c5b51ae9be859a1266ce4b11337b0b`
- Counter: `census/round-65/c2-counter.py`, sha256 `afd4cb54e5f58e10acc0a42dda1525ba4bd2f2a5753debee32cb2949cc02fabb`
- Population: `census/round-65/c2-statements.tsv`, pinned at `2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8`,
  sha256 `0291e1d3f2d7e9364e3a9b812814f4058722e03ee31cf1df86ca117535735be7` (4 statements, s1–s4)
- Candidate: the corrected `SKILL.md` statements and the landed writer at `40a371d8…`
- Frozen target: `SUMMARY rows=4 findings=0 verdict=PASS`, `EXIT=0`
- Kill: `findings>0` or a nonzero exit
- Live-marker rule: a needle counts only on an UNCOMMENTED line carrying `refuse(` or `return`
- Do-nothing control: `census/round-65/controls/c2-do-nothing.txt` — the same counter at the base revision
  prints `findings=2` (s2 `SCOPE-OVERREACH` + s4 `UNRESOLVED`), exits 1
- After receipt: `census/round-65/records/c2-after.txt` (binds `40a371d8…`)

### This seat's independent reproductions (wave evidence, never replacements)

Run from this seat's scratch `/fast/scratch/hyaku/souji-r65/S65ScribeEntry/`, writer bytes at `40a371d8…`,
base bytes at `4a43a4d9…`, counters and matrix read from the lane, `--work` under the seat's scratch:

| run | result |
|---|---|
| C1 counter, candidate slot | `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0` |
| C1 counter, do-nothing slot (base bytes as new) | `SUMMARY … new_forgeries=12 … class_mismatches=12 regress=PASS`, `EXIT=1` |
| C2 counter at `40a371d8…` | `MARKERS flag=1 inrun=1 env=1 unmerged=1`, `SUMMARY rows=4 findings=0 verdict=PASS`, `EXIT=0` |
| C2 counter at the base revision | `FINDING SCOPE-OVERREACH s2`, `FINDING GOVERNED-STATEMENT-UNRESOLVED s4`, `SUMMARY rows=4 findings=2 verdict=FAIL`, `EXIT=1` |

Both frozen targets are met and both do-nothing controls are red, reproduced independently.

## Gate

- **S297 admit candidate** — git-config(5) `status.showUntrackedFiles`,
  https://git-scm.com/docs/git-config, § `status.showUntrackedFiles` (HTML anchor
  `Documentation/git-config.txt-statusshowUntrackedFiles`, raw HTML byte offset 761837); accessed 2026-11-05;
  HTTP 200; 830605 bytes; sha256 `37aa8407b12e377a38f523d5012835d0515cc82f2249c942b9e5cff656019226`.
  Located quote — **verified-by-scout**, and independently re-verified by this seat against the scout's
  DELIVERED bytes (slice assertions re-run, all PASSED): the 11-word primary
  `So, this variable controls how the commands display the untracked files.`, byte-contiguous in the
  tag-stripped text capture at offset 299266 (`assert text[299266:299338] == quote_bytes` PASSED; NOT
  byte-contiguous in the raw HTML — the page wraps the sentence over one source newline; HTML first-word
  offset 762393). The three documented VALUES are byte-contiguous in TWO independent carriers (tag-stripped
  text and the rendered man page, git 2.56.0-1, MANWIDTH=200): `no - Show no untracked files.` (text 299360 /
  man 330781), `normal - Show untracked files and directories.` (text 299390 / man 330827),
  `all - Show also individual files in untracked directories.` (text 299437 / man 330890). Default `normal` at
  text 299496; the `-u|--untracked-files` command-line override at text 299634.
  Scope: what the variable controls and what each of its three values displays — the concealment the round's
  C1 V1 row exercises. The row draft is delivered separately as
  `.ufo/waves/round-65/w1/S65ScribeEntry/sources-row-s297.md`; the captures and the located-quote proof are
  the scout seat's (`.ufo/waves/round-65/w1/S65ScoutSources/`, to be copied by the L1 to
  `census/round-65/sources/`).
  **Offset discipline (the scout's correction to this seat, recorded so it is not repeated).** Offsets are
  meaningful only against the exact capture bytes AND the tag-strip recipe they were measured from; the
  recipe must travel with them. This seat initially quoted a raw-HTML offset of 762518 for
  `Show no untracked files.` — that was a CHARACTER offset in the decoded string, not a BYTE offset; the byte
  offset in the same capture is 762618 (762616 for `- Show no untracked files.`), because the capture holds
  100 multi-byte characters before that point. The HTML capture's sha256 is identical between this seat's
  fetch and the scout's (`37aa8407…9226`, confirmed by a third client in the scout's seat), so the mismatch
  was in the measuring, not in the bytes.
- **One reject candidate (routed, not adopted)** — the code-kind registry row for `:(top)`: the pathspec
  long-form spelling is composed by the reader, not printed on the git-scm.com page (r64's S296 named limit;
  the binding is code — `pathspec.c` v2.56.0 line 106 `{PATHSPEC_FROMTOP,'/',"top"}` and `parse_long_magic()`
  line 333). **This row is ROUTED, NOT ADOPTED, pending the operator L0**: whether the registry admits
  code-kind rows at all is an open operator question (r64 route 7), and no operator answer is recorded in
  this lane. Do not append it under round 65 without that answer.
- **Frontier step satisfied.** S297 is opened this round and cited by this round's evidence (the knowledge
  entry `corpus/knowledge/untracked-visibility-concealment.md` cites it in its `source:` line and in its
  `## Gate` ADMIT line). The registry tail stands at 219 rows; S297 is the next id (S291/S295/S296 already
  exist).
- **Registry ordering, for the L1.** The S297 row and the knowledge entry must land TOGETHER: the entry
  `corpus/knowledge/untracked-visibility-concealment.md` does not exist at the tip, and the registry-agreement
  check (`tools/souji-registry-agreement.py`, K1) fires `K1 used-by-missing` / `K1 used-by-no-cite` until it
  lands and cites `S297`. The K1 `cited-not-in-used-by` direction also requires the new entry path to appear
  in S291's `used-by` cell (today only `corpus/knowledge/skip-worktree-concealment.md`), because the drafted
  entry's `source:` line cites S291 as well as S297; `used-by` may change in place under contract rule 2 and
  the old→new pair must be logged in this lesson.
- **Assimilation.** `considerthese/` does not exist in this lane (recorded). The knowledge-repo read is the
  connector seat's duty; this seat did not read
  `/home/vgpnk/Projects/shokunin/shokuknow/merge/souji/MERGE-REPORT.md`.
- **Non-author closure** (the round's non-author spot-check samples from here): the S297 quote's byte-offset
  assertion in the committed capture; the two REJECT flips recorded in the knowledge entry's `## Gate`
  (duty-to-tools; ignored-files-surfaced); and the knowledge entry's own rule sentence — it must be stated at
  the KEY's scope (`status.showUntrackedFiles`), not at the CLASS's scope (operator config in general).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | chronology-arm landing miss. The commit chain says the `--chronology` arm landed pre-freeze; the bytes say otherwise. `2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8` (instruments, 2026-11-05 09:57) carries the message "round-65: instruments (c1/c2 counters, matrix, population, probes) + freeze-check chronology arm" but its diffstat touches only `census/round-65/**` (8 files) — `tools/souji-freeze-check.py` is NOT in it. A grep for `chronology` in that commit's `tools/souji-freeze-check.py` returns 4 hits, all belonging to the PRE-EXISTING r61 control-chronology arm (`control_chronology()` at line 295, called at 379); the file is byte-identical at the freeze `d2850b3e…` (same 4 hits). The actual arm — the `--chronology` CLI flag, `r64 --chronology` docs, `evaluate(..., chronology=)`, the receipt-rev-after-freeze check — landed at `16da2445088ccca15aa32c66841d878ee57a8706` (2026-11-05 10:43), i.e. AFTER the freeze commit, and only there does the grep count reach 24. The freeze commit's own summary (`census/round-65/records/freeze-check-substance-at-freeze.txt`: `SUMMARY claims=2 findings=0`) and the chronology selftest record (`census/round-65/records/freeze-check-selftest-chronology.txt`: `SELFTEST cases=52 pass=52 fail=0`) are therefore evidence about the PRE- or POST-freeze bytes, not about the bytes that existed at the freeze. The preregistration's sentence "`tools/souji-freeze-check.py --chronology` landed pre-freeze" is contradicted by the tree. Disclosed; the closure judge rules. | commit chain `2761f0aa…` → `3c5bfdc0…` → `d2850b3e…` → `40a371d8…` → `16da2445…`; `git show 2761f0aa:tools/souji-freeze-check.py` (4 `chronology` hits) vs `git show 16da2445:tools/souji-freeze-check.py` (24 hits); `census/round-65/records/freeze-check-substance-at-freeze.txt`; `census/round-65/records/freeze-check-selftest-chronology.txt`; `census/round-65/preregistration.txt` ("`tools/souji-freeze-check.py --chronology` landed pre-freeze") | "the pre-freeze landing checklist had no working-tree copy step" — the checklist verified the CANDIDATE's bytes and the instruments commit's census files, but never verified that the modified working-tree file `tools/souji-freeze-check.py` was actually STAGED into that commit. A commit message asserting "…+ freeze-check chronology arm" is not evidence that the arm is in the commit. | the landing checklist gains a working-tree copy step: for every file the round intends to land, assert `git show <commit>:<path>` equals the working-tree bytes AND that `<path>` appears in `git show --stat <commit>`. The chronology arm's own selftest record must also name the revision it ran against. Until then, a claim about a tool's presence at a revision must be read out of `git show <rev>:<path>`, never out of a commit message or a preregistration sentence. |
| M2 | claim-scope overreach in the LANDED WRITER'S OWN DOCSTRING (post-freeze finding; the frozen predicate is NOT affected). `tools/souji-receipt-write.py`'s round-65 C1 paragraph reads "every status read overrides status.showUntrackedFiles to `all`, so an operator-injected config cannot hide untracked entries from the dirty check or the content snapshot". The first clause is measured true; the second is broader than the bytes support. Measured, per-slot FRESH fixture repos, one untracked file `untracked.txt` in each, writer blob `be344a7d` (`40a371d8…`), base blob `9fb55f35` (`4a43a4d9…`): arm A (repo-local `status.showUntrackedFiles=no`, the frozen V1 shape) → new REFUSES rc=2 `lane worktree is dirty`, base accepts; arm B (`core.excludesFile` injected via `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0`) → new ACCEPTS rc=0, receipt written, base accepts; arm C (repo-local `core.excludesFile`) → new accepts rc=0, base accepts; arm D (tracked `.gitignore` naming the file) → new accepts rc=0, base accepts; arm E (repo-local `.git/info/exclude` naming it) → new accepts rc=0, base accepts; arm F (control, no concealment) → new refuses rc=2, base refuses; V2 (repo-local `showUntrackedFiles=no`, CLEAN tree) → new accepts rc=0 (the honest polarity holds). The reason is mechanical: a path matched by an exclude rule is IGNORED, not untracked, so `showUntrackedFiles=all` does not surface it. Independently reproduced by the sentinel seat (`S65SentinelScope`, HIGH; `.ufo/waves/round-65/w1/S65SentinelScope/probe-env-output.txt`). NOT a C1 forgery: the frozen V1 row's shape is specifically `status.showUntrackedFiles=no` and it PASSES (`new_forgeries=0`, exit 0). NOT a C2 finding: `SKILL.md`'s own writer-delta sentence is already key-scoped ("every status read overrides `status.showUntrackedFiles=all` (V1/V2)") and IS in the C2 population; the overreach is in the writer docstring, which is not. | `tools/souji-receipt-write.py` at `40a371d8…`, docstring round-65 (C1) paragraph; `.ufo/waves/round-65/w1/S65ScribeEntry/excl_probe3.py` + `excl-probe-results.txt`; `.ufo/waves/round-65/w1/S65ScribeEntry/v2_probe.py` + `v2-probe-results.txt`; `.ufo/waves/round-65/w1/S65SentinelScope/probe-env-output.txt` | the sentinel seat, independently; cross-verified by this seat (both directions agreed; this seat's own earlier D-arm reading was a probe artifact — a leftover out file inside the shared repo — and was corrected to per-slot fresh repos before being reported) | reword the writer docstring to the key-only claim (proposed wording in `knowledge-untracked-visibility-concealment.md`): "…overrides `status.showUntrackedFiles` to `all`, so THAT CONFIG KEY cannot hide untracked entries from the dirty check; other operator-config routes that make a path IGNORED rather than untracked (`core.excludesFile`, `.git/info/exclude`, `.gitignore`) are not closed by this override." The alternative fix (scrubbing `GIT_CONFIG_*`, pinning `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM`) changes what the writer reads and is an operator/design decision, NOT a scribe's or a wave's call. |
| M3 | SOURCE-ROW PROVENANCE (this seat's own draft hygiene, recorded because the row is being appended to the registry). The S297 row's quote was located by this seat in its OWN scratch capture, fetched independently of the scout seat's committed capture. Two captures of the same URL taken minutes apart are not the same bytes, so an offset quoted from one cannot be pasted into a row whose anchor cell names the other's path and digest. | `.ufo/waves/round-65/w1/S65ScribeEntry/sources-row-s297.md` (offsets and the digests they belong to); `.ufo/waves/round-65/w1/S65ScribeEntry/knowledge-untracked-visibility-concealment.md` `## Gate` | this seat | the L1 takes the offset, the sha256 and the capture path from the COMMITTED capture (`census/round-65/sources/`, the scout's), and re-verifies the slice assertion against those bytes before appending. If the committed capture's digest differs from this seat's, the row's anchor cell MUST carry the committed capture's digest, and the located-quote cell must carry the offset in THAT capture. |

## Named limits

(carried as observed; none claimed)

- **Env redirects beyond `GIT_INDEX_FILE` are unread.** `GIT_OBJECT_DIRECTORY`,
  `GIT_ALTERNATE_OBJECT_DIRECTORIES` and `GIT_REPLACE_REF_BASE` are neither scrubbed nor checked by the
  writer. Frozen with the r65 preregistration (`census/round-65/preregistration.txt`), and carried into
  `SKILL.md`'s writer-delta sentence.
- **The C2 live read is lexical; it does not prove reachability.** A refusal behind `if False:` keeps its
  live line. That is the C1 matrix's kill, not a C2 finding. Frozen with the preregistration.
- **N4 depends on the dual-seed fixture shape.** The frozen realizability probe resolution is
  `census/round-65/probes/n4-n2-dispute-results.txt`: a fixture WITHOUT the root-level dual copies makes even
  the BASE writer fail at `cat-file` ("absent at") — the r64 reviewer's H1 shape, not this row.
- **`GIT_CONFIG_*` reaches child git; the `-c` override outranks it for ONE key only.** Measured on host git
  2.56.0: a command-line `-c status.showUntrackedFiles=all` beats a repository-local `=no` AND a
  `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0` injection of the same key (`git config --get
  status.showUntrackedFiles` → `all` in both cases). So no bypass exists for that key; for other keys the
  passthrough is live (M2 arms B and C).
- **Ignored files are not untracked.** A path covered by `.gitignore`, `.git/info/exclude` or
  `core.excludesFile` is invisible to `git status --porcelain` by design, with or without the override. The
  dirty check is a status check; it says nothing about ignored content.
- **The wrapped command inherits the caller's environment.** The writer's own `git()` calls scrub
  `GIT_DIR`/`GIT_WORK_TREE`; the wrapped command's `Popen` inherits them, so a child that calls git may read
  a different view than the writer measured.
- **refs/replace substitutes the object git resolves** — a DIFFERENT route from the ignore routes, and the
  sentinel seat's finding, not this seat's measurement: with a replacement ref on the instrument blob and
  `--allow-dirty`, the writer accepts and the receipt's `instrument_sha256` is the REPLACEMENT's bytes
  (`aea35bbef2e7f0c0…`) against committed blob `8f513b9f361acb7e…`. Evidence:
  `.ufo/waves/round-65/w1/S65SentinelScope/probe-replace-excludes.sh` (case p6b),
  `.ufo/waves/round-65/w1/S65SentinelScope/probe-env-output.txt` (p6b lines), final report
  `.ufo/waves/round-65/w1/S65SentinelScope.md`. Cited as that seat's measurement; this seat did not re-run it
  and does not state the base-slot outcome for that arm.
- **The C2 population is four `SKILL.md` sentences** (s1–s4). A kind-only forger editing only
  `corpus/knowledge/` is outside it by design (r63 M3 rationale).
- **Axis tie-break and MACHINE BLOCK (operator L0 open).** `.ufo/l0-questions.md` lines 324–325 and 335–336.
  Routed around; not answered.
- **Planner seat (round-63 spot-check D3).** The validator refuses a planner role; the L1 holds it. Recorded
  again this round.

## Routed to round 66

<!-- L1: fill. The candidates this seat can see are listed below as suggestions, not decisions. -->

1. **Reword the writer docstring to the key-only claim** (M2). Proposed wording is in the drafted knowledge
   entry. The alternative — scrubbing `GIT_CONFIG_*` or pinning `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM` — is
   an operator/design decision and must not be taken by a wave.
2. **A matrix row for the ignore routes** — one untracked file made IGNORED by `core.excludesFile` /
   `.git/info/exclude` / `.gitignore`, so the "operator config cannot hide untracked entries" claim gets its own
   frozen predicate instead of living as a defect in a docstring. If the L1 prefers to keep the r65 claim
   scoped to the one key, say so explicitly and record it.
3. **The pre-freeze landing checklist needs a working-tree copy step** (M1): assert `git show <commit>:<path>`
   equals the working-tree bytes and that `<path>` is in `git show --stat <commit>` for every file the round
   intends to land. A commit message asserting a file is not evidence that the file is in the commit.
4. **The `:(top)` code-kind registry row** stays ROUTED pending the operator L0 on code-kind rows.
5. **The `refs/replace` route** (sentinel seat's finding) needs its own predicate: the receipt's
   `instrument_sha256` should bind the COMMITTED blob, not the replacement's bytes.
6. Carried from rounds 62–64: R1 (SKILL.md:830 overreach — re-checked this round, the sentence is now
   key-scoped and the C2 population's s2/s3 afters are the pinned literals), the operator L0 lines, and the
   round-63 spot-check D3 (planner seat).

## Integrated verification

<!-- L1: fill after integration. -->

- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` at round end: exit 0 required;
  the before/after row counts are in the report. This seat's read of the pre-append state: 219 rows
  (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`).
- Registry shape checks for the S297 row: 11 columns (NF=13), tier `A`, kind `docs`, status in
  `{queued,mined,rejected}`, no `|` inside any cell, and `used-by` paths that exist.
- Freeze checker: not re-run by this seat (no preregistration is this seat's to freeze).
