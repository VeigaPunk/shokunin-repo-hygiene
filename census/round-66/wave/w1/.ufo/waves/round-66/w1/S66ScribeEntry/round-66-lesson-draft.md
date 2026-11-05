# Round 66 — one post-freeze wave, two frozen claims

Base `045e103478fa4a7eff77db2cab5b9e2f26959a0a` (lane master at round start, clean, pushed; carries the
round-65 landed writer `tools/souji-receipt-write.py` and the round-65 SKILL.md). Attempt 2 — the operative
preregistration is `census/round-66/preregistration-attempt2.txt` (freeze commit
`02cc660965e027c6c6390604e50702bb06377b2e`); `census/round-66/preregistration.txt` (attempt 1) is SUPERSEDED
and is not amended. Instruments `4576f101a9200206de00ef00923dd38a7b2dbc7d` (C1 counter, 28-row matrix, C2
counter, C2 population, M-ENV recipe `census/round-66/c2-mutate.py`); an earlier instruments commit
`8410a97ef14683b4e65d0f29bf4ff15ccbb1b42e` carried the E6 fault (see M-c). Do-nothing control receipts
`4864c01f112c9f423def430d9b6e01bdc0e21f36`, strictly before the freeze.

## Gate

Two pages opened this round by the scout seat (`S66ScoutSources`): `https://git-scm.com/docs/git` (HTTP 200,
244227 bytes, sha256 `534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1`) and
`https://git-scm.com/docs/git-config` (HTTP 200, 830605 bytes, sha256
`37aa8407b12e377a38f523d5012835d0515cc82f2249c942b9e5cff656019226`); accessed 2026-11-05. Captures and the
located-quote proof: `.ufo/waves/round-66/w1/S66ScoutSources/` (`git-environment.html`,
`git-environment.txt` sha256 `624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035`,
`git-config.html`, `git-config.txt` sha256 `dfc44574996cdf9023e9b61ea37a4aab0fe0c79058b34743d08d5bc788d46054`,
`recipe.py`, `quotes.tsv`, `upstream-evidence.txt`, `verify.sh`); the L1 copies them to
`census/round-66/sources/`. S66ScribeEntry independently re-sliced ALL 34 rows of `quotes.tsv` against the
delivered `.txt` bytes: 34/34 byte-identical at the stated offset, 34/34 sha256 match, every quote ≤25 words.

- ADMIT (git(1) § ENVIRONMENT VARIABLES) — `GIT_OBJECT_DIRECTORY` (locator 30732; quote at 30753, 9 words)
  and `GIT_ALTERNATE_OBJECT_DIRECTORIES` (locator 30937; quote at 31092, 9 words); `GIT_CONFIG_GLOBAL`/
  `GIT_CONFIG_SYSTEM` (locator 40065; quote at 40302, 10 words) with the page's `/dev/null` skip sentence;
  `GIT_NO_REPLACE_OBJECTS` (locator 46311; quote at 46334, 9 words). Reason: each states the variable's own
  effect — the object-database and object-search directories, the global config file, and the switch that
  makes git ignore replacement refs. Flip: the page stops documenting the variable or its `/dev/null`
  behaviour.
- ADMIT (git-config(1) § ENVIRONMENT and § CONFIGURATION) — `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_<n>`/
  `GIT_CONFIG_VALUE_<n>` (locator 20861; quote at 20918, 11 words) with the `-c` precedence sentence (quote
  at 21340, 11 words; "passed via git -c ." at 21411, 5 words); `core.excludesFile` (locator 102897; quotes at
  102915, 10 words and 103037, 6 words). Reason: the pairs are "added to the process's runtime configuration"
  and are "overridden by any explicit options passed via git -c" — the injection C1 rows E1/E2 exercise and
  the reason the writer's `-c core.excludesFile=<null device>` pin beats an injected pair (measured on git
  2.56.0). Flip: the page stops documenting the variable or the `-c` precedence.
- ADMIT (upstream SOURCE, not a manual page) — `GIT_REPLACE_REF_BASE` and `GIT_CONFIG_PARAMETERS` appear in
  NO manual page at 2.56.0: 0 hits in the captured git(1)/git-config(1) pages, 0 in the installed
  `git(1)`/`git-config(1)`/`git-replace(1)` man pages, and 0 in upstream `Documentation/git.txt`,
  `git-config.txt` and `git-replace.txt` at tag v2.56.0. Their only upstream prose is `refs.c`
  (`NAMESPACE_REPLACE`: "this one can be changed by the GIT_REPLACE_REF_BASE environment variable"),
  `environment.h` (`#define GIT_REPLACE_REF_BASE_ENVIRONMENT "GIT_REPLACE_REF_BASE"`,
  `#define CONFIG_DATA_ENVIRONMENT "GIT_CONFIG_PARAMETERS"`), `config.h` (the `GIT_CONFIG_PARAMETERS` value
  format) and `Documentation/RelNotes/2.6.0.adoc` ("An environment variable GIT_REPLACE_REF_BASE tells Git
  to look into refs hierarchy other than refs/replace/ for the object replacement data."). Reason: rows E2
  and E6 can only be grounded on upstream source. Flip: the variables appear in a shipped manual page.
- REJECT — "a receipt writer must refuse these environment variables": the pages assign no duty to any
  consumer; the refusal is this lane's design. Flip: a git(1)/git-config(1) sentence assigning that duty.
- REJECT — "`GIT_CONFIG_GLOBAL` to the null device skips every config level": the page scopes the skip to the
  global level; the system and local levels are separate routes. Flip: a sentence stating all levels are
  skipped.
- REJECT — "`GIT_NO_REPLACE_OBJECTS=1` also disables the `GIT_REPLACE_REF_BASE` namespace shift": the page
  documents the variable's own effect; the namespace base is a separate variable with separate upstream
  prose. Flip: a sentence stating the two are equivalent.
- **Registry.** Three new rows drafted (ids assigned by the L1): git(1) object-store redirects, git(1)
  global-config file + replace-ref read switch, git-config(1) runtime-config injection + `core.excludesFile`.
  `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` = **220 before**, **223 after** the
  three rows. A fourth `code` row for the two undocumented variables is the L1's call (223 or 224). Draft:
  `.ufo/waves/round-66/w1/S66ScribeEntry/sources-rows-draft.md`.
- **Knowledge entry.** Draft: `.ufo/waves/round-66/w1/S66ScribeEntry/knowledge-caller-env-routes.md`
  (target path `corpus/knowledge/caller-env-routes-receipt-writer.md`). It and the registry rows must land in
  ONE commit (the `used-by` cell and the entry's `source:` line are one binding, both directions — the
  round-65 M6 lesson).
- **SKILL.md statement (population row s5).** The L1 landed it with the writer in commit `c13fbb4e…`:
  "- Env routes, round 66: the writer's `GIT_*` env-route surface is closed for the caller-injected config
  and object-redirect routes by the `tools/souji-receipt-write.py` refusals `RECEIPT-ENV-CONFIG-SET` and
  `RECEIPT-ENV-REDIRECT-SET`." The s5 `after_pattern` (167 bytes) occurs exactly ONCE in the SKILL.md blob
  at that revision, and each of s1–s5 resolves to exactly one wording (s1 base 1/after 1, s2 base 0/after 1,
  s3 base 0/after 1, s4 base 1/after 1, s5 base 1/after 1) — no `DUPLICATE-LIVE-WORDING` on any row. This
  seat's own pre-landing draft sentence and its collision check are kept for the audit trail in
  `.ufo/waves/round-66/w1/S66ScribeEntry/skill-writer-rule-s5.md`; it is SUPERSEDED by the landed bullet and
  must NOT be pasted a second time.
- **Non-author closure:** sample the ADMIT offsets against the committed capture, sample the two upstream
  quotes against the pinned tag, and sample one REJECT flip against the page bytes.

## Claims

Frozen at `census/round-66/preregistration-attempt2.txt`; the predicates are the sentences in that file and
are not amended here.

- **C1, operability.** The receipt writer refuses the caller-injected config and object-redirect
  environment routes (`GIT_CONFIG_COUNT`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_GLOBAL`,
  `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE`), records the full
  permission bits (setuid, setgid and sticky included) in the in-run snapshot, and refuses a same-content
  symlink retarget, on the frozen 28-row matrix. Target: `SUMMARY matrix=28 base_forgeries=8 base_honest=5
  new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0`. Do-nothing (base bytes in the new
  slot): `new_forgeries=8 … class_mismatches=8`, `EXIT=1` (`census/round-66/controls/c1-do-nothing.txt`).
  After receipt: `census/round-66/records/c1-after.txt`.
- **C2, calibration (lowest owned axis, score 7).** The SKILL.md statement population (`s1`–`s5`) agrees with
  the writer bytes under the live-marker (anchored) read, including the new env-refusal statement `s5`; and
  the round-66 counter scores the M-ENV kill mutant that the round-65 counter scores as live (round-65 M10)
  as a kill. Target: `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0`. Do-nothing (base revision):
  `SUMMARY rows=5 findings=1 verdict=FAIL`, `EXIT=1`
  (`census/round-66/controls/c2-do-nothing.txt`; the finding is
  `GOVERNED-STATEMENT-UNRESOLVED s5: stable wording absent at this revision`).
  After receipt: `census/round-66/records/c2-after.txt`.

Named limits, frozen with the preregistration and NOT counted as passes: (L1) the ignore routes
(`.git/info/exclude`, a tracked `.gitignore`, a repository-local `core.excludesFile`) stay outside C1 and
still hide untracked content on both slots; (L2) C1's pins change behaviour for honest lanes whose
host-global excludes hid untracked files — those files now count as dirty, and the frozen honest rows A, B,
T4, V2 and SY1 do not exercise that route; (L3) C1 refuses the PRESENCE of the six named variables, not the
content of a harmless value (an empty string is still refused); (L4) C2 is lexical — a needle on a
refusal-emitting line that is itself dead stays live, and a one-line docstring carrying a needle and a
`refuse(` call stays live; (L5) the M-ENV kill is one mutant recipe, one number, not a kill rate.

Measured revision for both after receipts: **`c13fbb4e1b563a78278ddc14316c20252e9a6d8d`** (the L1's landing
commit: "round-66: writer rejects caller-injected GIT_CONFIG_* and object-redirect env routes; full mode
bits; SKILL/QUALITY r66 rows"; the base `045e1034…` is NOT it).

Measured results at that revision, from the committed receipts:

- **C1** (`census/round-66/records/c1-after.txt`): `SUMMARY matrix=28 base_forgeries=8 base_honest=5
  new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0`. Frozen target met.
- **C2** (`census/round-66/records/c2-after.txt`): `MARKERS flag=1 inrun=1 env=1 unmerged=1 envcfg=1
  envred=1`, `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0`. Frozen target met.
- **C2 kill-power** (`census/round-66/records/c2-mutant-m-env.txt`): on the M-ENV mutant of the writer at
  `c13fbb4e…` (mutant bytes sha256 `7afafa0c141efdd2db3b0b3ca19d58a72539a941774394d2a2c571bc97c0569e`,
  committed in a scratch clone as `0c8c5f4bfe02d2c7ca19d8da719edf59bfaabf22`), the round-66 counter prints
  `FINDING SCOPE-OVERREACH s2: after wording: claim closed_full needs writer markers env; writer blob lacks
  them`, `SUMMARY rows=5 findings=1 verdict=FAIL`, `EXIT=1`; the round-65 counter (instrument sha256
  `afd4cb54e5f58e10acc0a42dda1525ba4bd2f2a5753debee32cb2949cc02fabb`, tsv-rev
  `2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8`) on the SAME mutant at the same SKILL.md prints
  `SUMMARY rows=4 findings=0 verdict=PASS`, `EXIT=0`. The round-65 M10 repair is demonstrated: the mutant
  the round-65 counter scored as LIVE is scored as a kill by the round-66 counter.
- The SKILL.md statement s5 landed with the writer in the same commit; the s5 literal occurs exactly once
  in the SKILL.md blob at `c13fbb4e…` and each of s1–s5 resolves to exactly one wording (no
  `DUPLICATE-LIVE-WORDING`).
- The knowledge entry and the three SOURCES.md registry rows are NOT yet landed; they are the drafts in this
  seat's directory (see `## Gate`).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M-a | Pre-freeze control receipt without the required header lines. The C2 do-nothing capture `10d175a5edac242c9fc11324faa6c35d78b3ee6c` was the counter's four output lines only (`FINDING …`/`MARKERS …`/`SUMMARY …`/`EXIT=1`); it carried no `rev=`, `instrument=`, `instrument_sha256=` or `command=` line. The attempt-1 freeze commit `5d17a5deaf75328439fe66ae19b06d4b0151391e` landed and pushed that capture as its `Control:` receipt, and `tools/souji-freeze-check.py --substance` reported `CONTROL-REV-MISSING`, `CONTROL-INSTRUMENT-MISSING` (two) and `CONTROL-COMMAND-MISSING` for it — 4 findings, rc 1. The freeze-check tool caught it; no candidate writer, after receipt or data existed at either freeze, so no measurement was corrupted. | `git show 10d175a5:census/round-66/controls/c2-do-nothing.txt` (4 lines, no `rev=`/`instrument=`/`instrument_sha256=`/`command=`); `git show 5d17a5de:census/round-66/preregistration.txt` (the attempt-1 freeze); the finding classes and rc 1 are recorded verbatim in the attempt-2 preregistration's freeze-history paragraph (`census/round-66/preregistration-attempt2.txt`); the receipt grammar is `tools/souji-freeze-check.py`'s `--substance` arm (its docstring names `CONTROL-INSTRUMENT-MISSING`, `CONTROL-REV-MISSING`, `CONTROL-COMMAND-MISSING`) | the freeze-check `--substance` arm (the L1's freeze validation), not a QUALITY criterion — no criterion in `corpus/QUALITY.md` names the control receipt's HEADER lines, only Q99's `Control:` key line and Q122's content binding | re-issued the freeze at a NEW path (`census/round-66/preregistration-attempt2.txt`, commit `02cc660965e027c6c6390604e50702bb06377b2e`) with the header-complete control receipt `4864c01f112c9f423def430d9b6e01bdc0e21f36` committed strictly before it; the attempt-1 file is superseded, not deleted, and its bytes are restored |
| M-b | A frozen file was edited IN PLACE after the freeze. The attempt-1 preregistration was amended by an append (commit `01bc1e1601dba200a3f9e7b1b131b6505cde553a`, "re-issued freeze (attempt 2; header-complete C2 control; predicates unchanged)") — 8 insertions, 1 deletion in `census/round-66/preregistration.txt` — which changed a file the freeze had already claimed. A predicate change after data is not this round's rule, and the file's own bytes must not move under a freeze that has already been read. Restored by commit `a81280e18c98483d8d163b21bde2d3756eb198ce` ("restore attempt-1 preregistration to its frozen bytes (superseded, not edited)"); the attempt-1 blob at `5d17a5de` and at HEAD are byte-identical (sha256 `becb21ba78b5688c6fb0869be0a681e12336d24a418b6fa0f54431d5e61298bc`), and the attempt-2 blob is byte-identical between `02cc6609` and HEAD (sha256 `400d3dfe9078c65163aaefd8acbef1ccb18ffb2361352bab71b5d8f8e68fd90e`). | `git show 01bc1e16 --stat` (+8/−1 on `census/round-66/preregistration.txt`); `git show a81280e1 --stat` (+1/−8, the restore); the byte-identity digests above, read with `git show <rev>:census/round-66/preregistration.txt \| sha256sum`; the superseded file is retained at `census/round-66/preregistration.txt` | none — no QUALITY criterion names "a frozen file may not be edited in place"; the freeze-check's own `FROZEN-EDITED` finding class (which compares the preregistration blob at the freeze commit with the blob at the revision) would have refused it had the check been run against the attempt-1 path, but no criterion requires the check to be run on the OLD path | re-issued the freeze at a NEW path (`census/round-66/preregistration-attempt2.txt`), so the freeze tool's "oldest commit adding a path" rule binds the attempt-2 bytes; the attempt-1 file was restored to its frozen bytes rather than left edited |
| M-c | An instrument fixture value that made git ABORT, so a matrix row measured a tool crash instead of the writer's behaviour. The earlier instruments commit `8410a97ef14683b4e65d0f29bf4ff15ccbb1b42e` set the E6 fixture's `GIT_REPLACE_REF_BASE` to `refs/replace-forged-r66` — no trailing slash. On git 2.56.0 that value makes git die with `BUG: refs.c:1908: ref pattern must end in a trailing slash when trimming` (exit 134) on `git status --porcelain` and `git for-each-ref`, so the E6 row would have measured the crash, not the writer's refusal. Repaired before any control was taken and before any candidate existed: the frozen instrument at `4576f101a9200206de00ef00923dd38a7b2dbc7d` uses `refs/replace-forged-r66/`. S66ScribeEntry reproduced the crash independently on host git 2.56.0 (both `git status --porcelain` and `git for-each-ref` exit 134 with the same message) and confirmed the trailing-slash form works and that the route really forges a read: with `refs/replace-forged-r66/<real-oid>` pointing at another blob, `git cat-file -p HEAD:a.txt` prints the forged content, and `GIT_NO_REPLACE_OBJECTS=1` restores the real content. | `git diff 8410a97e 4576f101 -- census/round-66/c1-counter.py` (one line: `refs/replace-forged-r66` → `refs/replace-forged-r66/`); the frozen instrument's digest equals the preregistration's pin (`sha256=273d6fc9ad1f8b1f8091e58439be9e5a8d844e8e0812ddd5c9b50b58585f1490`, re-measured at HEAD and at `4576f101`); S66ScribeEntry's host probes under `/fast/scratch/hyaku/souji-r66/S66ScribeEntry/probe/` (`rp2`, `rp3`, `rp4`) | the L1's pre-freeze instrument re-run — no QUALITY criterion names a fixture value that makes the tool under test crash; the adjacent criterion Q85 ("a crashing fixture is a battery defect, not a kill") is about mutant batteries, not about a frozen matrix row's env fixture | repaired the fixture value in the frozen instrument before the control receipts were taken; no control, candidate or after receipt was taken against the crashing value, so no round-66 measurement is affected. The lesson recorded for round 67: an env fixture value must be validated against the HOST git before the freeze, not after |

## Named limits carried into the report (draft; the L1 owns the final text)

- **Ignore routes stay outside C1 (L1).** Measured on git 2.56.0 by S66ScribeEntry: under
  `.git/info/exclude`, a tracked `.gitignore` and a repository-local `core.excludesFile`, the excluded path
  is absent from `git status --porcelain`; `-c core.excludesFile=/dev/null` restores it ONLY for the
  repository-local `core.excludesFile` route — the `.git/info/exclude` and tracked-`.gitignore` routes survive
  the `-c` pin, because neither is the `core.excludesFile` key.
- **C1's pins change honest-lane behaviour (L2).** `GIT_CONFIG_GLOBAL` → null device,
  `GIT_CONFIG_NOSYSTEM=1` and `-c core.excludesFile=<null device>` make a host-global or repository-local
  excludes file ineffective, so a previously hidden file becomes untracked and counts as dirty. The frozen
  honest rows A, B, T4, V2 and SY1 do not exercise that route.
- **Presence, not content (L3).** C1 refuses the PRESENCE of the six named variables; an empty-string value
  is still refused.
- **C2 is lexical (L4).** A needle on a dead line, or in a one-line docstring that also carries a `refuse(`
  call, still reads live. Reachability is C1's job.
- **One mutant, not a battery (L5).** The M-ENV kill is one number from one recipe.
- **Two of the six refused variables have no manual anchor.** `GIT_REPLACE_REF_BASE` and
  `GIT_CONFIG_PARAMETERS` appear in no manual page at 2.56.0 (0 hits in the captured git(1)/git-config(1)
  pages, in the installed man pages, and in upstream `Documentation/git.txt`, `git-config.txt` and
  `git-replace.txt` at tag v2.56.0). Their grounding is upstream SOURCE (`refs.c`, `environment.h`,
  `config.h`, `Documentation/RelNotes/2.6.0.adoc`).

## Wave evidence (w1, 10 seats) — draft

Seat list, evidence pointers and the C1/C2 after receipts are the L1's to assemble from the wave directories
under `.ufo/waves/round-66/w1/`; the durable mirror is `census/round-66/wave/w1/`. Scribe seat
(`S66ScribeEntry`) deliverables: `knowledge-caller-env-routes.md`, `skill-writer-rule-s5.md`,
`sources-rows-draft.md`, `round-66-lesson-draft.md` in this seat's directory.
