# deliver-docs-f1 — r32 w1 documentation edits that land with C3

Seat `SwarmScribe24` (item `C3Docs`), wave `souji-r32-w1`. Read-only seat: this file is the
draft; the L1 applies the four edits. Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`,
preregistration `3ec84fc81b3243429c834a051880b0bcde06291c`.

Targets (lane-relative):

1. `corpus/README.md:39` — in-place replacement of the F1 coverage-map row.
2. `corpus/README.md` EOF — appended `## Round 32 — F1 the abandoned object's own mtime clock`.
3. `PROVINCE.md` EOF — appended `## Round 32 boundary note (F1 mtime clock)`.
4. `SKILL.md` — one bullet at the end of `## Error patterns (false-SAFE signatures)` (after the
   `Process residue is a nomination, not a receipt` bullet, before the `The repository-content
   bound is not a kernel/filesystem sandbox` paragraph) and three rows appended after the last
   `## Gate registry` row (`r31-jj-object-clock`).

Placeholders: `<RESULT ...>` stands for a whole measured line of
`census/round-32/records/jj-mtime-clock-run.txt`; `<N>` for its `RESULT`-line count. The entry,
record and fixture are produced by other seats of this wave, so no measured value is written
here. Filling rule for the L1: copy each `RESULT` line byte-for-byte from the record (contract
`census/round-32/c3-contract.txt`, keys `arm step obj mtime where object_present`), and drop any
sentence of the drafts below that the record contradicts — the record is the measurement, this
prose is not.

Constraints already checked against the instruments that read these files:

- `census/round-32/c3-counter.py` L1 counts files in `corpus/knowledge/` whose front matter has
  `ground: F1` (target 5); L2 runs `tools/souji-coverage-agreement.py@REV`, whose map parser needs
  the new entry named as a backticked `knowledge/<name>` span in an `F1` row's entries cell and
  whose `DANGLING-MAP-PATH` class needs the file to exist at REV. Edit 1 is what makes L2 read
  `mapped=18 dangling=0`.
- `tools/souji-landing-gate.py` cites registry scripts through
  `(tools|tests/fixtures|census/round-<n>)/<name>.(sh|py)`: all three new paths match that shape
  and must exist at REV (`LG-MISSING-REG`) and parse (`LG-PARSE-REG`).
- Map rows are edited in place and the history goes in the round section (r28 F4, r29 F3, r30 and
  r31 F1 precedent). The F1 status cell stays `frontier, entries held`: a measured edge class
  does not promote a frontier ground to Core.

## Edit 1 — `corpus/README.md:39`, in place

Old line (exact, one line):

```text
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md`, `knowledge/jj-keep-ref-expiry.md`, `knowledge/jj-dropped-keep-object-lifetime.md` |
```

New line (exact, one line; only the entries cell changes, one name appended):

```text
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md`, `knowledge/jj-keep-ref-expiry.md`, `knowledge/jj-dropped-keep-object-lifetime.md`, `knowledge/jj-abandoned-object-mtime-clock.md` |
```

## Edit 2 — `corpus/README.md`, append at EOF (after `### Round 31 corrections`'s last bullet, one blank line between)

```markdown
## Round 32 — F1 the abandoned object's own mtime clock

Appended; the sections above stand. One knowledge entry is admitted for F1, measured this round
with real jj 0.45.1 and git 2.56.0 in scratch repositories under the round's scratch root, never
against a lane:

- `knowledge/jj-abandoned-object-mtime-clock.md` — how an abandoned commit's object dies by its
  own modification time once neither a keep ref nor a reflog entry names it. Five arms of one
  fixture, each in its own colocated repository, with the `refs/jj/keep/*` refs and the reflog
  entries naming the object already gone: `recent` (a just-created object), `old` (backdated by
  `touch -d` on the object's loose files), `mixed` (an old object and a recent one in one
  repository), `never` (`gc.pruneExpire=never`) and `nocruft` (`gc.cruftPacks=false`). The
  record's `where` field is what separates an object kept loose from one kept inside a cruft
  pack, whose `.mtimes` file carries the clock per object — sourced in the entry's Gate, not
  measured by any arm. The measured lines are
  `<RESULT arm=recent step=gc-default obj=B mtime=recent where=<loose|cruft|pack|absent> object_present=<yes|no>>`,
  `<RESULT arm=old step=gc-default obj=B mtime=old where=<loose|cruft|pack|absent> object_present=<yes|no>>`,
  `<RESULT arm=mixed step=gc-default obj=B mtime=old where=<loose|cruft|pack|absent> object_present=<yes|no>>`
  and `obj=C` in the same step, `<RESULT arm=never step=gc-pruneexpire-never obj=B mtime=old where=<loose|cruft|pack|absent> object_present=<yes|no>>`
  and `<RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=<loose|cruft|pack|absent> object_present=<yes|no>>`.
  Fixture `../tests/fixtures/r32-jj-mtime-clock.sh`; measured record
  `../census/round-32/records/jj-mtime-clock-run.txt` (`jj-version: jj 0.45.1`,
  `git-version: git version 2.56.0`, `<N>` `RESULT` lines, deterministic across runs and held to
  `../census/round-32/c3-contract.txt` by the C3 counter's L14).

Coverage-map effect: the F1 row at `:39` now names a seventh entry with its status cell unchanged
(`frontier, entries held`); the six entries it already carried are unchanged. F1 stays frontier —
a measured edge class does not promote a frontier ground to Core (PROVINCE
`## Round 32 boundary note (F1 mtime clock)`).

### Frontier (r32)

- F1 — the object's own mtime clock is now measured (the entry above;
  `../census/round-32/records/jj-mtime-clock-run.txt`), including the question the r31 section
  left open: whether git's cruft-pack handling changes that keeper's reach. Remaining: the fleet
  exposure numerator re-census named at `:46`, and the classes the entry's own limits section leaves
  open — no lane or fleet repository gc'd, the mtime keeper not isolated against a live keep ref or
  a reflog entry, the `never` asymmetry read from the docs rather than implemented, and the two-week
  window sourced rather than waited out.
- F2, F3, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.

### Round 32 corrections

- The r12 F1 row at `:39` was replaced in place rather than superseded by a later table: its
  entries cell gained `knowledge/jj-abandoned-object-mtime-clock.md` and its status cell, already
  `frontier, entries held`, was not reworded. Map rows are edited in place (r28 the F4 row, r29
  the F3 row, r30 and r31 this row); the append-only record is this section.
- The r31 section's `### Frontier (r31)` disclosed "whether git's cruft-pack handling changes the
  mtime keeper's reach" as unmeasured, and its wave-2 correction said the object's own mtime clock
  (`gc.pruneExpire`) "is sourced, not measured". Both stand as history and are not rewritten; the
  r32 entry is that clock's measurement, and `PROVINCE.md` `## Round 32 boundary note (F1 mtime
  clock)` records the closure.
- The r31 C3 record printed `arm=reflog-only`, which is outside its frozen contract's two arm
  values (`solo`, `descendant`), and the deviation was disclosed only after landing (r31 closure
  routed defect 3, class D1). The record is not rewritten: it stands as landed, and the r31 section
  above stands with it. What changes is instrumentation — `tools/souji-record-contract.py` now
  fails that shape over the r31 record and the reconstructed r31 contract (four `BAD` lines 16-19
  naming `arm=reflog-only`, then `lines=17 bad=4`, exit 1;
  `../census/round-32/records/m1-red-before.txt`), and the r32 C3 counter's L14 holds this round's
  record to `../census/round-32/c3-contract.txt` as frozen at the preregistration.
```

## Edit 3 — `PROVINCE.md`, append at EOF (one blank line after the r31 note)

```markdown
## Round 32 boundary note (F1 mtime clock)

F1 now holds a measured entry — `corpus/knowledge/jj-abandoned-object-mtime-clock.md` — beside the
six entries its map row at `corpus/README.md:39` already named, and it measures the one holder the
r30 and r31 notes called sourced rather than measured: the abandoned commit's own modification
time. With the keep refs and the reflog entries naming the object gone, the fixture's five arms
isolate that clock — a recent object and an old one in separate repositories and in one, under a
default `git gc`, under `gc.pruneExpire=never` and under `gc.cruftPacks=false` — and the record's
`where` field separates an object kept loose from one kept inside a cruft pack, whose `.mtimes`
file carries the clock per object (sourced in the entry's Gate). Two boundary consequences follow,
and they are the r31 ones restated: an object that survives a prune is not evidence that a deletion
completed, because the prune date may simply be older than the object's mtime or `gc.pruneExpire`
may reach it; and absence is not proved by an object count the lane did not run. What this does not
record: which reflog file carries the naming entries, the real 90/30-day windows (sourced from
git-reflog(1) and the `gc.*` config, not waited out), the fleet exposure numerator, and jj's own
store GC, which stays outside this lane — no `jj op abandon` and no `jj util gc` runs on a lane
repository and the operator's store is left alone. One entry does not promote F1 to Core: Core stays
the `## Owns` and `## Work surfaces` list above (`:60`), the F1 row keeps the status
`frontier, entries held`, and this round adds nothing to either list. The round's one tool change is
`tools/souji-record-contract.py`, a record-versus-contract check that creates no receipt class, no
receipt and no deletion verdict; the r17 receipt-root rule is untouched. Certification OFF, K5 HELD.
Sources: `census/round-32/records/preregistration.txt` claim C3; the entry and its Gate; the run
record `census/round-32/records/jj-mtime-clock-run.txt`.
```

## Edit 4 — `SKILL.md`

### 4a — error-pattern bullet, inserted after the `Process residue is a nomination, not a receipt` bullet

```markdown
- **jj: an unreferenced object dies by its own mtime, so presence is not a receipt** (r32, F1):
  after the `refs/jj/keep/*` refs naming an abandoned commit and the reflog entries naming it are
  gone, the object's own modification time is what decides its fate under `git gc` — a recent
  object survives the `gc.pruneExpire` window and an old one is dropped, the clock is carried per
  object where a cruft pack holds it (its `.mtimes` file, sourced in the entry's Gate),
  `gc.pruneExpire=never` keeps the old object, and
  `gc.cruftPacks=false` leaves the recent object loose instead of in a cruft pack. The five arms
  and their measured lines are in `corpus/knowledge/jj-abandoned-object-mtime-clock.md`:
  `<RESULT arm=recent step=gc-default obj=B mtime=recent where=<loose|cruft|pack|absent> object_present=<yes|no>>`,
  `<RESULT arm=old step=gc-default obj=B mtime=old where=<loose|cruft|pack|absent> object_present=<yes|no>>`,
  `<RESULT arm=mixed step=gc-default obj=B mtime=old where=<loose|cruft|pack|absent> object_present=<yes|no>>`,
  `<RESULT arm=never step=gc-pruneexpire-never obj=B mtime=old where=<loose|cruft|pack|absent> object_present=<yes|no>>`,
  `<RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=<loose|cruft|pack|absent> object_present=<yes|no>>`;
  record `../census/round-32/records/jj-mtime-clock-run.txt`, fixture
  `../tests/fixtures/r32-jj-mtime-clock.sh`. A `git cat-file -e` that succeeds therefore says only
  that no prune reaching the object has completed — never that a deletion was proved absent.
```

### 4b — `## Gate registry` rows, appended after the `r31-jj-object-clock` row

```markdown
| r32-jj-mtime-clock | probe | `TMPDIR=<scratch> bash tests/fixtures/r32-jj-mtime-clock.sh` | 0 prints a `jj-version:` line, a `git-version:` line and `<N>` `RESULT arm=… step=… obj=… mtime=… where=… object_present=…` lines per `census/round-32/c3-contract.txt`, every arm of that contract carrying a `gc-` step and `mixed` carrying one for `obj=B` and one for `obj=C`; 2 refused (TMPDIR unset, empty, not a directory, or resolving inside the souji lane or the fleet root; `jj`, `git` or `touch` absent from PATH; an `mktemp` base resolving into either root) or interrupted | no self-test; the judging instrument is the r32 C3 counter's legs L8 (record shape and arm coverage), L9 (two replays equal the record), L12 (jj, git and touch argv through a shim) and L13 (M2 gc/prune/repack and M3 touch subtraction mutants) | `census/round-32/records/jj-mtime-clock-run.txt`; field contract `census/round-32/c3-contract.txt` | jj-colocated scratch repos under `$TMPDIR`, backdating only by `touch -d` on loose object files, every jj call `-R`, every git call `-C`; never a lane | souji |
| souji-record-contract | gate | `python3 -B tools/souji-record-contract.py --record PATH --contract PATH` | 0 `lines=<n> bad=0` with n ≥ 1 (every record line carrying the contract prefix has exactly the frozen keys in order, each value in its set); 1 any `BAD <line> <reason>` line, or a record with no prefixed line; 2 could-not-evaluate (unreadable record or contract, malformed contract line, no prefix line, no key line) | red arm from committed bytes: the r31 object-clock record against the r31 contract prints `BAD 16` to `BAD 19` and `lines=17 bad=4`, rc 1 (`census/round-32/records/m1-red-before.txt`); green arm: the r32 run record against `census/round-32/c3-contract.txt` prints `lines=<n> bad=0`, rc 0, which is the r32 C3 counter's L14 | reconstructed r31 contract `census/round-32/m1-r31-contract.txt`; r32 contract `census/round-32/c3-contract.txt` | read-only; writes nothing | souji |
| r32-c2-counter | gate | `python3 -B census/round-32/c2-counter.py --root LANE --rev REV --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev PREREG` | 0 `SUMMARY items=27 pass=27 fail=0`; 1 any `ITEM` line without `PASS` (the sandboxed run's exit code or normalized last digit-bearing line differs from the base run's, or its successful file-creating syscalls are below half of the base run's, so a tool that stops working to dodge the sandbox fails); 2 could-not-evaluate (usage, non-40-hex or unresolvable revision, items file absent at `--list-rev`, `bwrap` or `strace` absent, git failure). `--only` prints `partial=1` and is diagnostic, never a pass | red arm reproducible from committed bytes: the same command with `--rev 85b61a151923986e7e6b48f7084b9122561b5f3d` prints `SUMMARY items=27 pass=1 fail=26`, rc 1 (`census/round-32/records/controls.tsv`, control `C2-do-nothing(prereg)`); the round's landing tip must print `fail=0`, rc 0 | item set `census/round-32/c2-items.tsv` read at `--list-rev`; base commit 85b61a151923986e7e6b48f7084b9122561b5f3d | private `git clone --no-local` per run under `--scratch` (origin removed), one fresh `$TMPDIR` per run, `bwrap` read-only /tmp, /var/tmp and /dev/shm; read-only on `--root` | souji |
```

## Fill notes for the L1 (not part of any target file)

1. `<N>`: the `RESULT`-line count of `census/round-32/records/jj-mtime-clock-run.txt` (L8 needs
   at least 8; the fixture contract's five arms each need a `gc-` step).
2. `<RESULT ...>`: copy byte-for-byte from the record. The drafts assert two rules in prose that
   the placeholders must not contradict: a fresh object surviving the default prune and an
   old one dropped, and `gc.pruneExpire=never` keeping the old object. If either arm prints
   otherwise, delete that clause and say what the record says — do not reword the record.
3. Edit 2's `:46` reference is the r12 `## Frontier` bullet, unchanged by this round (as r30 and
   r31 also left it); the r32 `### Frontier (r32)` bullet is its supersession.
4. The r31 record line quoted in Edit 2's third correction bullet carries four `BAD` lines; the
   receipt `census/round-32/records/m1-red-before.txt` shows numbers 16 to 19, which are the
   record's 16th to 19th lines, not RESULT indices.
5. If the wave-2 oracles change the fixture's `RESULT` key order or step names, the contract
   `census/round-32/c3-contract.txt` is the authority; adjust the sketched `<RESULT ...>` lines to
   it rather than to this draft.
6. Peer-reported fixture shape (SwarmExecutor18, item `C3Fixture`, message of this wave; the
   committed fixture path is still absent and the wave directory holds only the uncommitted draft
   `deliver-r32-jj-mtime-clock.sh`, so this is not a record): arms in the declared order, exactly 22
   `RESULT` lines — recent 2, old 3, mixed 8 (four steps for each of `obj=B` and `obj=C`), never 3,
   nocruft 6 — plus the two version lines and nothing else on stdout; step tokens are exactly the
   contract's six; `where` values seen are `loose`, `cruft` and `absent`, with `pack` in the set but
   produced by no arm. On that report `<N>` fills as 22, and no draft sentence should claim a `pack`
   outcome. Re-count both from the landed fixture and record before the landing commit. The
   gate-registry row carries that wider refusal set as the author's run-reported one; re-check it
   against the landed fixture and drop any condition the bytes do not implement.
7. Forward-promise check at the landing commit: the `### Frontier (r32)` bullet names the remaining
   F1 classes as "the classes the entry's own limits section leaves open", and names no entry
   heading (only `## Gate` is instrument-constrained). That sentence is checkable only against the
   entry's final bytes, so read them at the landing commit: if the entry's limits list still carries
   the four classes quoted there, the bullet stands; if it does not, rewrite the clause to the
   classes the entry does state, or drop it. The same landing-time test applies to every "measured"
   claim in Edit 2's entry bullet, Edit 3 and Edit 4a: they hold only once the record's lines,
   copied into the `<RESULT ...>` placeholders, show those outcomes.
8. Drafts in this wave directory, used only to align wording, never as evidence: `SwarmScribe22.md`
   and `deliver-entry-jj-abandoned-object-mtime-clock.md` carry the entry draft, whose H1, `ground:
   F1` line, five claims, `## Consequence for souji receipts`, `## What this does NOT establish`,
   `## Lane link` and `## Gate` are uncommitted; `deliver-jj-mtime-clock-run.txt` carries 22
   `RESULT` lines with the shape in note 6. Three draft sentences were aligned to those bytes: the
   `nocruft` outcome is stated as the recent object staying loose (the draft record shows no cruft
   pack in that arm), the backdating is "the object's loose files" (the entry names commit, tree and
   blob), and `### Frontier (r32)` lists the classes the entry's own limits section leaves open
   rather than the round-31 ones. If the landed entry or record differs from those drafts, the rule
   in note 7 applies: the record and the entry's own text win, and the sentence is rewritten or
   dropped.
