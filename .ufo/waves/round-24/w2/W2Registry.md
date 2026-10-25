# W2Registry — attack on corpus/SOURCES.md at ca7fc1cb (souji r24 w2, FALSIFY)

Seat: L1Souji24.W2Registry (scout, leaf, read-only). Target rev `ca7fc1cb6dd1333096c6f3bdbad304686691d126`.
Lane `master` read this run: `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface` (one commit past target, `c3ca7ad round-24: wave-1 seat reports, drafts and registry (38 seats)`).
`corpus/SOURCES.md` is byte-identical at target, master and the working tree (sha256 `f8b9b78f…a927a` for both the `git show` copy and the on-disk file; `git diff --stat` empty both ways).
Scratch `/var/tmp/souji-r24-W2Registry/` was used and has been removed. Tools installed or upgraded: none. Host git 2.56.0.

## Status

STATUS: PARTIAL. The mechanical checks all survive: validate exits 0 with no E lines, there are 123 rows, S120–S123 are well formed, every `used-by` path exists at the target and cites its id, and every anchor and sha256 matches the committed snapshots. Two contract-level attacks land, though. S115's `used-by` omits the new entry that cites it in `source:`. S120 and S122 list a tool in `used-by`, which is outside the contract's definition and has no precedent in 123 rows. Three lower-severity findings follow.

## Evidence

| check | command | result |
|---|---|---|
| validate (task command, live tree) | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | `EXIT=0`, `souji	ok	…/corpus/SOURCES.md`, 31 `W04`, 0 `E`, 0 other `W` |
| validate bound to target bytes | `git archive ca7fc1cb \| tar -x` into scratch, then `sources-census.sh validate --today 2026-10-25 <scratch lane>` | `VALIDATE@R EXIT=0`, `lane	ok`, 31 `W04`, no other lines. E11 checks the disk, not a rev (header line 29: `E11 used-by path missing on disk`), so this archive run is what binds E11 to ca7fc1cb |
| census at target | `sources-census.sh census <scratch lane>` | `rows 123`, tier A 117 / B 5 / C 1 / invalid 0, mined 100 / queued 15 / rejected 8 / invalid 0, exit 0 |
| CORPUS.md frozen census (CORPUS.md L135-148) at target | row grep, NF!=13, enum/tier-inflation awk, mined used-by existence loop | `123`, `malformed=0`, enum output empty, used-by `missing:` output empty |
| id integrity | python parse of the target bytes | 123 rows, 0 duplicate ids, no gaps S001–S123, one `## Registry` (L17) |
| S120–S123 shape | python split on `\|` | each `NF=13`, 11 cells, no escaped pipe, no `\|` inside any cell; lines 140–143 |
| snapshot sha256 | `git show ca7fc1cb:census/round-24/sources/<f> \| sha256sum` vs `SHA256SUMS` | all 4 cited snapshots match the SHA256SUMS lines and the row's `sha256 <8>…<4>` abbreviation |
| live probe of the S120 early-return claim | `/var/tmp` scratch: `git init`, `worktree add`, then `git -C lnk count-objects -v` vs `git --git-dir=<common> count-objects -v` | linked: `warning: garbage found: …/main/.git/worktrees/lnk/refs`, `garbage: 1`; common: `garbage: 0` |

### S120–S123 cell checks (target rev)

| id | kind | tier | status | opened | recheck | used-by (all exist at target; id grep count) |
|---|---|---|---|---|---|---|
| S120 | code | A | mined | 2026-10-25 | on-release | entry (13 hits), `tools/souji-size-census.py` (1 hit) |
| S121 | code | A | mined | 2026-10-25 | on-release | entry (6) |
| S122 | code | A | mined | 2026-10-25 | on-release | entry (5), `tools/souji-size-census.py` (1) |
| S123 | docs | A | mined | 2026-10-25 | on-release | entry (5) |

"entry" means `corpus/knowledge/count-objects-linked-worktree-garbage.md`, which is identical at target and in the working tree. Every value is in the contract vocabularies (kind enum CORPUS.md L145; tier A/B/C; status queued/mined/rejected). No row is community at tier A. `opened` 2026-10-25 is not a future date and matches the landing commit `778747e` (2026-10-25 06:29 -0300). `on-release` is a symbolic cadence that CORPUS.md L106 allows.

### Anchor spot-checks (all hold)

- S120 / `git-v2.56.0-path.c`: `struct common_dir` L89–96, `common_list[]` L98–124, info L102, info/sparse-checkout L103, logs L104, logs/HEAD L105, refs L111, gc.pid L120, `report_linked_checkout_garbage` L365–385. L371 quote: "if (!r->different_commondir)".
- S121 / `git-v2.30.0-path.c`: L101–108, L110–136 (refs L123), L376–396. Running `diff` on the tables (v2.30 101–136 against v2.56 89–124) prints `TABLE-IDENTICAL`. The function diff shows exactly 3 lines: signature, `different_commondir` source and gitdir source, which matches the row's teaches.
- S122 / `git-v2.56.0-builtin-count-objects.c`: L41–53, L55–82, verbose gate L116–119, loose walk L121–122, KiB L151–152, garbage lines L161–162. L117–118 quote: "report_garbage = real_report_garbage; report_linked_checkout_garbage(the_repository);".
- S123 / `git-worktree.1.txt`: § REFS L137–146. L140 quote: "There are exceptions, however: refs inside refs/bisect, refs/worktree and refs/rewritten are not shared."

### Tool question: does `tools/souji-size-census.py` cite S120 and S122?

Yes. Each is cited once, in the module docstring at ca7fc1cb L30–33: "Sources: S120 (path.c@v2.56.0 report_linked_checkout_garbage returns early without a separate common dir, …), S122 (builtin/count-objects.c@v2.56.0 -v path and KiB floor)". Both citations are substantively true: the early return is at path.c L371–372 and was reproduced live above, and the `-v` path and KiB floor are at count-objects.c L116–119 and L151–152. The tool cites no other source id. In particular it does not cite S115 or S116, even though its only two commands are `count-objects -v` and `fsck --unreachable` (docstring L27).

## Findings

1. **ATTACK, lands. S115 `used-by` omits a citing entry** (`corpus/SOURCES.md` L135, S115). The new entry cites S115 in front matter, at L5: "source: S115 — https://git-scm.com/docs/git-count-objects — § OPTIONS -v/--verbose — git 2.56.0". It cites S115 again in the body at L58. Yet the S115 `used-by` at ca7fc1cb is only `corpus/knowledge/repo-size-census-readonly.md`. The contract (`/home/vgpnk/Projects/shokunin/CORPUS.md` L107) says: "`used-by` — repo-relative paths of the knowledge entries or lessons citing the row,". The wave-1 draft prescribed this exact in-place change (`.ufo/waves/round-24/w1/ScribeSourcesRows.md`, "In-place change to log"): "S115 `used-by`: `corpus/knowledge/repo-size-census-readonly.md` → …, corpus/knowledge/count-objects-linked-worktree-garbage.md". It was not applied at 778747e or ca7fc1cb. The validator cannot see this, because it only checks forward existence (E11), never reverse citation. S116 and S117 also appear in the entry, but only in REJECT flip clauses (L143–144) and a range mention (L121 "S115–S117"), so they are weaker cases. Confidence: high.

2. **ATTACK, lands. A tool path in `used-by` falls outside the contract definition** (S120 L140, S122 L142). `tools/souji-size-census.py` is neither a knowledge entry nor a lesson (CORPUS.md L107, quoted above). In the 123-row registry at target, S120 and S122 are the only rows whose `used-by` contains a `tools/`, `tests/` or `census/` path (awk scan over cell 12). It is a new convention with no contract amendment. The status rule (CORPUS.md L103) "`mined` (cited by ≥1 path in `used-by`)" still holds through the entry, so no status depends on the tool path. The substance survives: the tool really does cite both ids (see the tool question above). Severity: low to moderate (a contract-form deviation, not a false citation). Confidence: high.

3. **Gate record for S120–S123 is absent at target** (`corpus/lessons/` at ca7fc1cb). `git ls-tree` lists `round-23.md` and `round-23-verifier-spotcheck.md` but no `round-24.md`. CORPUS.md L112–113 says: "The round lesson's `## Gate` records, for every new row, the URL, the access date, and a ≤25-word quote". The Gate lines exist only as a wave-1 draft (`ScribeSourcesRows.md` "Lesson Gate lines"). So at the target, rule 1 is satisfied only by the anchor cells and snapshots, not by the required lesson record. [INFERENCE] This is pending, not violated, if the round-24 lesson (W2LessonDraft) lands the Gate plus the S115 old→new log that rule 2 (L116) requires. Confidence: high on absence.

4. **Id-number reuse with staged and quarantine ids grew from 11 to 15** (S120–S123). `.ufo/waves/round-24/assimilation/collisions` (frozen at f9db218) lists S109–S119 only. `staged-ids` L12–15 also hold S120–S123, which name different documents in `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` L18–21: Pro Git ja, Atlassian ja, link(2), and the own-work `r23-trigger-prune.sh`. Lane S123 also shares its number with quarantine-slice S123 (`quarantine-slice` L2), which round-22 lessons cite. For example, `corpus/lessons/round-22.md` L298: "Rows S123/S131/S133 quote man-page prose (`git worktree prune [-n] …`". The `r23-record-agreement.py` fixture L171 and `souji-gate-check.py` L236 also cite it. A reader resolving that round-22 "S123" through the lane registry now lands on git-worktree(1) § REFS, a superficially plausible but wrong match. `corpus/SOURCES.md` has no provenance paragraph that discloses the reuse. The wave-1 draft states it (`ScribeSourcesRows.md` Finding 1: "staged S120–S123 name other documents"), but the registry itself does not. Severity: low (ambiguity hazard, no wrong row). Confidence: high.

5. **The entry cites S123 for § DETAILS, which is outside S123's anchor** (entry L4 and L35, against S123 L143). Entry L4 reads "source: S123 — https://git-scm.com/docs/git-worktree — § REFS, § DETAILS", and L35 reads "(S123 § DETAILS, § REFS)". S123's scope and anchor are § REFS only ("§ REFS paras 2 and 4"). § DETAILS is anchored by S003 ("§ DETAILS; § LIST OUTPUT FORMAT; installed man page git 2.55.0-1"). The `$GIT_DIR`-is-private sentence the entry grounds (L138 ADMIT, "— § DETAILS —") is therefore cited to a row whose declared scope excludes it. Severity: low. Confidence: high.

6. **Survives: the W04 on S123 is a disclosed, scoped URL share** (live-run and archive-run validate output). The warning reads `S123 duplicate url git-scm.com/docs/git-worktree across scopes`. S123's scope explicitly excludes S003 and S058 ("not lock or prune behaviour (S003), not config.worktree read order (S058)"). It is a warning only, and there is no E04.

7. **Minor teaches precision** (S122 L142, S123 L143); neither is a falsification:
   - S122's "each reported path adds 1 to garbage and its stat size to size_garbage" omits two conditions. First, `real_report_garbage` returns early when `bits_to_msg` yields NULL (L46–47). Second, size is added only when `stat` succeeds (L49–50).
   - S123's "a linked worktree's copies live at $GIT_COMMON_DIR/worktrees/<id>/refs" generalises from para 4's single `refs/bisect/bad` example (L144). [INFERENCE] The generalisation is consistent with para 2 and with the live probe (`main/.git/worktrees/lnk/` holds `refs`).

## Attack log

| # | attack | result |
|---|---|---|
| A1 | the validator exits non-zero or prints E lines at the target | survives (exit 0 live and on archived target bytes) |
| A2 | row count is not 123, or ids are duplicated or gapped | survives (123, 0 duplicates, 0 gaps) |
| A3 | an S120–S123 row has NF≠13 or a pipe inside a cell | survives |
| A4 | tier, kind or status is outside the vocabulary, or community is at A | survives |
| A5 | a `used-by` path is missing at the target | survives (git cat-file -e on both paths; E11 clean on the archive) |
| A6 | a `used-by` file does not cite the id | survives (counts 13/6/5/5 in the entry; 1/1 in the tool for S120/S122) |
| A7 | the opened date is future or malformed, or recheck is invalid | survives |
| A8 | an anchor line or sha256 does not match the snapshot | survives (all spot lines and 4/4 digests) |
| A9 | the S120 early-return claim cited by the tool is false | survives (live probe: linked `garbage: 1`, common dir `garbage: 0`) |
| A10 | reverse binding: an entry cites a row whose `used-by` omits it | **lands** on S115 (Finding 1) |
| A11 | a `used-by` value is outside the contract's entries-or-lessons definition | **lands** on S120 and S122 (Finding 2) |
| A12 | rule-1 Gate record present at the target | **absent** (Finding 3) |
| A13 | id-number reuse disclosed in the registry | not disclosed; reuse grew to 15 (Finding 4) |
| A14 | entry citations stay within the cited row's anchor | **lands** on S123 § DETAILS (Finding 5) |
