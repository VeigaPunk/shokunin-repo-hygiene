STATUS: PASS

The deliverable is the drafted `## Gate — attempt 2` block below plus the
evidence for every factual line in it. Nothing in `corpus/lessons/round-22.md`
was edited (rule: block in report only). One conflict must be resolved by L1
before the block is applied: the heading already exists at line 327 of the
committed lesson (finding F1).

# Deliverable — drafted block (verbatim, for `corpus/lessons/round-22.md`)

```markdown
## Gate — attempt 2

Drafted against base `4edb25d` and measured at tip `3216c19` (2026-10-25T06:47Z;
counter run with the working-tree `tools/souji-gate-check.py` at sha256
`f2d18e82…58fd4331`, drilled against the committed copy `d85c2696…12486b00`).
Receipts: `.ufo/waves/round-22/attempt2/w1/evidence/DraftGateLesson.md`.

**Candidates — one theme, two entries (§10: restorable-quarantine staging).**
- `corpus/knowledge/quarantine-staging-no-copy-r23.md` — **ADMITTED** (F4,
  the no-clobber staging primitive). Gate quotes S110 (§ DESCRIPTION flags,
  `RENAME_NOREPLACE`) and S111 (§ DESCRIPTION, option `--no-copy`) from
  committed snapshots. The five-device measurement is a *vendored*,
  byte-identical copy of `lanes/souji/round2/evidence/noreplace-probe.out`
  (sha256 `1634d206…8bb5` at both paths) and is labelled as not re-run here.
- `corpus/knowledge/quarantine-origin-record-fields-r24.md` — **ADMITTED**
  (F4 read side: the record field restore consumes). Gate quotes S112
  (`gio trash --list` / `--restore`), S113 (GIO `File.trash` Description),
  S022 (Trash Info `Path` / `DeletionDate`) and S114 (`struct statx`).
- staged `quarantine-staging-no-copy-r24.md` — **REFUSED** (not adopted, not
  appended). Reason: the two-entry budget is spent on the primitive and the
  record read side, and this entry repeats the same primitive. Its one real
  addition — 8 probed paths plus `RENAME_EXCHANGE` and `RENAME_WHITEOUT`
  (`lanes/souji/round3/evidence/r24-renameat2-probe.out`, sha256
  `a53f1e30…0809`, matching the entry's own frontmatter) — is *flag
  coverage*, not new refusal semantics, so it does not displace either seat
  at equal ground. Flip: a round whose frozen theme is staging flag coverage,
  or an operator staging-tool change that needs atomic exchange; then vendor
  the probe output under the snapshot directory and admit it with its own
  Gate and its campaign S133 row by document.
- staged `quarantine-origin-record-fields-r23.md` — **REFUSED** (not adopted).
  Reason: its field set is the admitted r24 entry's set minus the restore-side
  requirement; adopting both duplicates the record ground. Flip: the record
  format needs the unique mount id — then its campaign S125
  (`STATX_MNT_ID_UNIQUE`, Linux 6.8) is the row to append by document.
- staged `quarantine-staging-no-copy.md` (round-1 body) — **REFUSED**
  (superseded). Reason: same two documents, no committed fixture of its own
  (its own text: "no committed fixture; its `/dev/shm` device relied on
  QUALITY Q15, withdrawn by Q16"), which is exactly what the admitted r23
  body replaces with the vendored five-device measurement.
- staged `origin-record-{format-gvfs-r26, writer-r27, durability-r28,
  exclusivity-r28, mechanism-set-r33}.md` — **NOT ADOPTED this round**
  (adjacent F4 branches: format, writer, durability, exclusivity, mechanism
  set). They are not refuted; they are outside the frozen theme's two
  sub-claims and are not appended (CORPUS.md rule 4). Each carries its own
  campaign rows (S146, S152, S173, S158/S159, S210/S211).

**Admitted — the frozen gate-check criteria each must satisfy.** Every row is
per-entry; no row is satisfied by the other entry.

| # | frozen predicate | r23 staging | r24 origin-record |
|---|---|---|---|
| 1 | file at the lane root with a `## Gate` heading | pass | pass |
| 2 | Gate names >=1 https URL with `opened: YYYY-MM-DD` equal to the round date | `man7.org/…/rename.2.html`, `opened: 2026-10-25` | `man.archlinux.org/man/gio.1.en`, `opened: 2026-10-25` |
| 3 | >=1 located quote in double quotes, <=25 words, with a locator token (§, section, line, paragraph, DESCRIPTION) | 3 spans, longest 14 words, `§ DESCRIPTION flags` / `§ DESCRIPTION, option --no-copy` | 6 spans, longest 23 words, `§ COMMANDS trash --list`, `§ COMMANDS trash --restore`, `§ Description`, `§ 6 Contents of a trash directory` (x2), `§ DESCRIPTION struct statx` |
| 4 | every quoted span verbatim (whitespace-collapsed) in the committed snapshot the Gate names, under the snapshot directory | 3/3 spans over `man7-rename.2.txt`, `man7-mv.1.txt` | 6/6 spans over `arch-gio.1.txt`, `gtk-filetrash.txt`, `freedesktop-trash.txt`, `man7-statx.2.txt` |
| 5 | every `source: S<digits>` id in the frontmatter resolves to a `corpus/SOURCES.md` row | S109, S110, S111 | S112, S113, S114, S022 |
| 6 | >=1 ADMIT and >=1 REJECT, each with a reason string | 3 ADMIT, 1 REJECT | 6 ADMIT, 1 REJECT |

**Rejected — the register's citation-class defect rows (campaign id space;
these ids are not lane registry ids).**
- **campaign:S123 → REFUSED.** Registered quote `git worktree prune [-n] [-v]
  [--expire <expire>]` against
  `lanes/souji/round2/evidence/r23-trigger-prune.out`. Reason: the cited bytes
  contain none of it (`grep` = 0 matches; the file opens
  `git_version=git version 2.56.0` and continues with PASS lines), and the `.sh`
  the verdict pointer names does not exist in that directory. The text is
  `git-worktree(1)` SYNOPSIS prose, so the row is a wrong-source citation, not
  a fact about the payload. Flip: re-cite the synopsis against
  `git-worktree(1)` as a URL row and keep the probe output for its own PASS
  lines; the row then becomes a citation row again.
- **campaign:S118 → UNVERIFIABLE** (not a rejection). The register's own cell
  records that the DOI `10.1109/SEQUEN.1997.666900` could not be fetched; that
  is the register's unchecked prose family, and unreachable is not fabrication.
  Flip: a resolvable copy, or a re-fetch that returns text.
- **5 accepted with corrected quotes:** campaign:S114 (`git-repack(1)` renders
  as `git-repack[1]` on the page), S124 (the payload carries an intervening
  `NOREPLACE_new=0(ok)` field the registered quote dropped; the second
  fragment is `rename(2)` prose), S131 (`git-worktree(1):218` prose; the
  payload's own dry-run lines carry the claim), S133 (`rename(2)` prose,
  supported by the payload's `SUMMARY:` line), S138 (`## gc.auto (6700)` is a
  markdown marker, the page heading is `gc.auto (6700)`).
- **1 present:** campaign:S126 — GIO `File.trash` Description, verbatim in the
  committed snapshot. Slice total 8/8, classes only
  `present|accepted|unverifiable|refused`.

**Spot-check — `G1 RevSliceVerif`** (wave seat, roster
`L1Souji22.RevSliceVerif`; the gate's independent second seat). It re-derives,
from primary bytes and not from this block:
1. all 8 slice verdicts — open each cited source or committed snapshot, locate
   the exact quote or fail to, and assign one of the four frozen classes;
   note that campaign:S114 (git-scm) and S138 (qiita) have **no committed
   snapshot**, so those two require a fetch, while campaign:S118 requires a
   reachability check;
2. the slice itself — re-run the frozen awk over the read-only register and
   compare byte-for-byte with `census/round-22/attempt2/quarantine-slice`;
3. predicates 4 and 5 of both admitted entries against the committed
   snapshots at the final revision (whitespace-collapsed span test, id
   resolution in `corpus/SOURCES.md`);
4. the campaign→lane id map by **document** (URL or bytes decide the row),
   never by number;
5. the one frozen counter command's single output line and its exit code.
   Boundary: G1 is a lane seat, so its result is lane evidence — no
   outside/non-author spot-check is claimed by it.

**Campaign → lane id map slot.** One slot per adopted document; the final-id
column is L1's to fill and confirm. Only rows the admitted entries cite have a
slot — no staged row enters the registry wholesale (CORPUS.md rule 4).

| slot | campaign id | final lane id (L1) | cited by |
|---|---|---|---|
| `S-NEW-noreplace-probe-vendored` | campaign:S124 | ☐ S109 | r23 |
| `S-NEW-rename2-noreplace` | campaign:S116 | ☐ S110 | r23 |
| `S-NEW-mv1-no-copy` | campaign:S115 | ☐ S111 | r23 |
| `S-NEW-gio1-trash` | campaign:S137 | ☐ S112 | r24 |
| `S-NEW-gtk-file-trash` | campaign:S126 | ☐ S113 | r24 |
| `S-NEW-statx2-identity` | campaign:S117 | ☐ S114 | r24 |
| (no slot — existing lane row) | — | ☐ S022 cited, not duplicated | r24 |

As measured at `3216c19`, `corpus/SOURCES.md` already holds S109–S114 with
exactly these `used-by` cells (114 rows, no duplicate id, S022 unchanged), so
L1's fill is a confirmation of a landed mapping, not a new assignment. The
`S-NEW-<slug>` labels are minted in this Gate — no earlier slot registry
exists in the round prompt or the frozen contract — so a label may be renamed;
the pairing that carries meaning is document → slot. Not
mapped and not appended: campaign S125 (cited only by the refused r23
origin-record entry), S133 (refused r24 staging entry), and every other staged
id.

**§10 assimilation parameters (as run).**
- Theme: **one** — restorable-quarantine staging.
- Entries: **2** adopted, each re-grounded this round: snapshots committed
  under `census/round-22/attempt2/sources/`, spans re-located verbatim, source
  ids re-resolved, Gate ADMIT/REJECT rows present.
- Package: `/home/vgpnk/Projects/shokuknow/merge/souji/` (read-only; 68
  proposed entries, 134 proposed rows, 108 lane ids at staging time, 0
  collisions). Nothing copied wholesale; the campaign→lane re-pointing above
  is by document.
- Register slice: 8 rows, reproduced byte-exact from the read-only register
  with the frozen awk; verdict table
  `census/round-22/attempt2/slice-verdicts.tsv` carries one row per id.
- Counter (one command): `entries=2 ok=2 slice_verdicts=8 slice_total=8
  fail=0`, exit 0. Tool selftest `selftest=9/9` exit 0, including
  `FALSE-GREEN-REJECTED` on the always-green control; an entry-absent run of
  the same command exits 1.
- No-harm: read-only throughout; no staging tool changed; no deletion
  authority created; `shokuknow` never written; certification OFF and K5 HELD
  untouched. The C1 calibration counter and its receipts are the SCORECARD
  seat's axis and are not restated here.
```

# Evidence (executed commands and observed output)

1. Frozen C2 counter, after state:
   `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/quarantine-staging-no-copy-r23.md corpus/knowledge/quarantine-origin-record-fields-r24.md --snapshot-dir census/round-22/attempt2/sources --slice census/round-22/attempt2/quarantine-slice --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv`
   → `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, exit 0.
2. Kill rule: `python3 -B tools/souji-gate-check.py --selftest` →
   `selftest=9/9`, exit 0, with `PASS control always-green ->
   FALSE-GREEN-REJECTED` and `PASS fixture partial-verdicts -> fail on V!=T
   with fail=0 [slice_verdicts=1 slice_total=2 fail=0]`. Instrument pinned:
   working tree `f2d18e8273d56467a1af29499241348bcfcf90ccac7729bbd424b90d58fd4331`,
   HEAD `d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00`; the
   sha was identical before and after both counter runs, so no measurement
   straddled a tool edit.
3. Before-state substitute (the frozen before line needs the entries deleted,
   which is a mutating cleanup this lane may not run): same command with
   `quarantine-staging-no-copy-r24.md` as the first entry →
   `FAIL … entry-missing`, `entries=2 ok=1 slice_verdicts=8 slice_total=8
   fail=1`, exit 1, re-run at the same pinned instrument sha. So one good
   entry cannot satisfy the counter.
4. Slice reproduction: frozen awk over
   `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md`
   piped to `diff - census/round-22/attempt2/quarantine-slice` → empty diff,
   8 rows, every line carrying an S-id.
5. Span test (my own, not the tool's): every double-quoted Gate span,
   whitespace-collapsed, found in the snapshot its line names — r23 3/3 over
   2 snapshots, r24 6/6 over 4 snapshots; longest span 23 words; frontmatter
   ids S109–S111 and S112–S114 + S022 resolve to `corpus/SOURCES.md` rows.
6. Vendored measurement: `sha256sum` of
   `<shokuknow>/lanes/souji/round2/evidence/noreplace-probe.out` and of
   `census/round-22/attempt2/sources/vendor-noreplace-probe.out` →
   `1634d206…8bb5` at both, `diff -q` byte-identical; `git show
   HEAD:…vendor-noreplace-probe.out | sha256sum` identical, so it is the
   committed copy.
7. Registry state: 114 rows, S001–S114, 0 duplicate ids; S109–S114 `used-by`
   are exactly the two admitted entries; S022 already present (cited, not
   duplicated); `assimilation/collisions` 0 bytes with `reg-ids` 108 and
   `staged-ids` 134.
8. Row re-derivations executed by me: campaign:S123 quote absent from the
   cited payload (0 matches) and the named `.sh` absent; S126 quote present
   (1 match) in `gtk-filetrash.txt`; S131 quote absent from the payload while
   the payload's own dry-run lines exist; S133 `SUMMARY:` line present, payload
   sha256 `a53f1e30…0809`; S124 intervening `NOREPLACE_new=0(ok)` field
   present. Carried, not re-derived: S114 and S138 (no committed snapshot),
   S118 (not re-fetched).
9. Locator truth: `man7-mv.1.txt:60` is `DESCRIPTION top` and the page has no
   `OPTIONS` heading; `freedesktop-trash.txt:54` is `6 Contents of a trash
   directory`. Both working-tree locator corrections are therefore true.
10. Host claim: `/usr/bin/mv --version` → `mv (GNU coreutils) 9.12`;
    `/usr/bin/mv --help` lists `--no-copy`. (The session shell's `mv` is a
    wrapper reporting `0.8.0`; it must not be used for host-version claims.)
11. Measured bytes: HEAD `3216c1998fe04d7e23793ffd4e135bd37c3a11f4`; working
    tree dirty with the two entries' locator corrections (5 lines) and the
    gate tool's 4-line conformance fix (the earlier run's 5 test-vault fixture
    modifications were gone by the final status check). Working-tree shas r23
    `80a6a895…d22762de`, r24 `8a21704d…8fdea3d0`, tool `f2d18e82…58fd4331`;
    HEAD shas r23 `0081e830…ae45f394`, r24 `b92f8118…d801eac`, tool
    `d85c2696…12486b00`. No quote span or source id is among the uncommitted
    entry edits (diff read in full).

# Bounded findings

- **F1 (blocking for application, not for the draft): heading collision.**
  `corpus/lessons/round-22.md` at `3216c199` is 370 lines and already has
  `327:## Gate — attempt 2`, committed by `70af563`. Appending the block as
  drafted duplicates the heading. The committed block lacks the per-entry
  frozen criteria, a register-row rejection with a flip, the `G1
  RevSliceVerif` name, the `S-NEW-<slug>` slot and the §10 parameter record.
  L1 must choose: replace the committed attempt-2 Gate with this block, or
  append under a distinct heading. This seat takes no such decision.
- **F2 (executed) predicate 3 checks a locator token, not locator truth.** The
  committed Gate located `(mv 1)` text under `§ OPTIONS`, a heading the
  snapshot does not have; the uncommitted correction to `§ DESCRIPTION` is
  true. A Gate can therefore pass predicate 3 while naming a section that does
  not exist.
- **F3 (executed) two slice verdicts have no committed bytes.** campaign:S114
  (git-scm) and S138 (qiita) cite public URLs with no snapshot under
  `census/round-22/attempt2/sources/` (13 files, none of them either page), so
  their verdicts cannot be re-derived offline; `G1 RevSliceVerif` must fetch.
  This is a reproducibility limit, not a fabrication finding.
- **F4 (executed) the committed refusal reason for staged
  `quarantine-staging-no-copy-r24.md` is contradicted by its bytes.** The
  committed Gate says "no new refusal semantics or field, so no new
  consequence"; the staged entry in fact adds `RENAME_EXCHANGE` and
  `RENAME_WHITEOUT` coverage on 8 paths, with an evidence file whose sha256
  matches its own frontmatter. The draft therefore refuses it on budget and
  ground duplication and names the flag-coverage flip, instead of asserting
  no new consequence.
- **F5 (executed) dangling path reference inside an admitted entry.** The r24
  origin-record entry states that
  `corpus/knowledge/quarantine-origin-record-fields-r23.md` "is not replaced";
  that file does not exist in the lane (it is a package-only candidate, and
  `ls corpus/knowledge/` shows only the r24 variant). The frozen predicates
  check `source: S<digits>` ids, not other path references, so the gate passes
  while the sentence points at nothing. Reword it, drop it, or adopt the r23
  entry — L1's call.
- **F6 (executed) TSV evidence pointers paraphrase payload text.** The S131
  pointer renders an em-dash payload line with ASCII hyphens and a different
  label than the payload carries; a verifier that reads pointers instead of
  bytes would mis-report. `G1` must read the artifacts.
- **F7 (executed) measurement environment caveat.** The session shell resolves
  `mv` to a wrapper reporting `0.8.0`; the real host binary is
  `/usr/bin/mv` (GNU coreutils 9.12). Any host-version claim in a Gate must be
  taken from the absolute path.
- **F8 (executed) the counter's instrument was uncommitted and mid-repair.**
  `tools/souji-gate-check.py` carried a 4-line working-tree fix at measurement
  time: `check_slice` no longer appends `verdict-missing` to `fail`, and the
  `partial-verdicts` selftest fixture now asserts `slice_verdicts=1
  slice_total=2 fail=0` with exit 1, which matches the frozen rule that a
  missing verdict row is counted in neither V nor F. Under the committed tool
  the same fixture reported `fail=1`, i.e. the pre-fix instrument counted a
  missing row as a failure and thus over-counted F. The after-state line is
  identical under both copies, executed by piping the committed copy from
  `git show HEAD:tools/souji-gate-check.py` into `python3 -B -` with the same
  arguments: `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, exit 0.
  The fix matters for a partial-verdicts round, and it is not yet committed.

# Out of scope / not executed

- C1 (declared-evidence calibration): its counter, receipts and repairs are
  another seat's axis; not restated, not measured, not judged here.
- The frozen C2 before line: not re-derived (would require deleting the
  admitted entries); only the entry-absent control was run.
- Any registry append, knowledge-file edit, lesson edit, git/jj write, commit,
  fetch or push; any write into `shokuknow`, `.ufo/state`,
  `.ufo/watchdog.log`, `MANIFEST.json`, the fleet root's `templates/` or
  `scripts/`, or a sibling repo; any signal, deletion or quarantine action.
- No tool was installed or updated this run.

# Artifact paths

- Report: `.ufo/waves/round-22/attempt2/w1/DraftGateLesson.md`
- Evidence: `.ufo/waves/round-22/attempt2/w1/evidence/DraftGateLesson.md`

Report: .ufo/waves/round-22/attempt2/w1/DraftGateLesson.md
