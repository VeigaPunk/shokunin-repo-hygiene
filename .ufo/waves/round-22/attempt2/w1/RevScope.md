STATUS: PASS

# RevScope — working-tree state inherited by souji round 22 / attempt 2

Seat: L1Souji22.RevScope (leaf, no subagent dispatch). Read-only census.
Evidence table: `.ufo/waves/round-22/attempt2/w1/evidence/RevScope.tsv` (27 data rows + header; 5 tab fields on every row, verified with `awk -F'\t' 'NF!=5'` → no output).
Nothing was modified, staged, deleted, committed, or signalled by this seat; no tool installs were
needed (no package manager transaction was run).

Snapshot anchors (the tree is LIVE — see Residual risk):

| plane | revision | snapshot time |
|---|---|---|
| lane `/home/vgpnk/Projects/shokunin/souji-shokunin` | `3216c19` (`round-22: record the measured declared-evidence counts`) | 2026-10-25T03:46:29 and 03:47:09 -03:00 |
| fleet `/home/vgpnk/Projects/shokunin` | `fed29568` | 2026-10-25T03:46:09 -03:00 |

Lane HEAD moved **during** this census (`2a130b4` -> `3216c19`, then a 5th modified path appeared at
03:47:09), so every statement below is a timestamped snapshot, not a final state.

Prereg base revision `4edb25dfe262515d0da63224bbba71e02e36cba5` is present and an ancestor of HEAD;
base..HEAD counts 4 commits: `a211e4d`, `70af563`, `2a130b4`, `3216c19`.

---

## 1. Lane working tree

### Commands and observed output (executed)

```
$ git -C .../souji-shokunin status --porcelain          # @03:47:09
 M corpus/knowledge/quarantine-staging-no-copy-r23.md
 M tests/vault/vadv-51/fixture/src/x2-note.txt
 M tests/vault/vadv54-run/elsewhere/led-outside.tsv
 M tests/vault/vadv54-run/p/p2.md
 M tests/vault/vadv54-run/p/p3.md
?? .ufo/waves/round-22/attempt2/assimilation/
?? .ufo/waves/round-22/attempt2/w1/{MutPath,MutQuote,ScoutCollision,Slice118,Slice123,Slice124,Slice126,Slice131,Slice133,Slice138,SnapFileTrash,SnapGio1,SnapMv1,SnapRename2,SnapStatx2,SnapTrashSpec}.md
?? .ufo/waves/round-22/attempt2/w1/evidence/
?? census/operator-sweep-20261019/
?? census/round-21/__pycache__/
?? tools/__pycache__/

$ git diff --stat
 4 files changed, 0 insertions(+), 0 deletions(-)          # @03:44 — the mode-only signature
```

### The four lane modifications are content-free mode flips (executed)

```
$ git diff --summary -- tests/vault/
 mode change 100644 => 100755 tests/vault/vadv-51/fixture/src/x2-note.txt
 mode change 100644 => 100755 tests/vault/vadv54-run/elsewhere/led-outside.tsv
 mode change 100644 => 100755 tests/vault/vadv54-run/p/p2.md
 mode change 100644 => 100755 tests/vault/vadv54-run/p/p3.md

$ stat -c '%n mode=%a mtime=%y' <the four>
 x2-note.txt              744  2026-10-18 13:59:49
 led-outside.tsv          744  2026-10-18 14:51:47
 p2.md                    744  2026-10-18 14:51:47
 p3.md                    744  2026-10-18 14:51:47
$ git log -1 --format='%h %ci %s' 48a64d8   # the commit that added these fixtures
 48a64d8 2026-10-18 15:09:36 -0300 round-4 (amended): ...
$ for f in <the four>; do sha256sum "$f"; git cat-file blob HEAD:"$f" | sha256sum; done
 e.g. x2-note.txt worktree=957fd5572f34…6a70c head=957fd5572f34…6a70c
      led-outside.tsv efc1c7dd…52fb5 == HEAD ; p2.md e66b973b…72dc1 == HEAD ; p3.md 22454e36…24ba1 == HEAD
$ git config --get core.fileMode
 true
$ find tests/vault/vadv54-run -type f -printf '%m %p\n'
 644 p/ctrl.md / p1.md / p4.md / p5.md …   744 p/p2.md, p/p3.md    # inconsistent siblings
```

**Every worktree byte equals the HEAD blob**; only the owner-exec bit differs, and the mtime is
~1 h *before* the round-4 commit that recorded these paths as 644. Reverting is therefore lossless.

Cause is **not** the in-repo harness: `tests/vault/vadv-51/run-vadv-51.sh` only ever chmods
`fixture/vault/h-note.txt` and `fixture/src/h-note.txt` and restores them to 644 (lines 37, 62, 155,
157, 273, 275, 281); nothing in the lane sets 744 on these four paths. The flip is a pre-commit
worktree event of 2026-10-18.

### Classification (full table in RevScope.tsv)

| path | class | action for L1 |
|---|---|---|
| `tests/vault/vadv-51/fixture/src/x2-note.txt` | lane-authored leftover → **REVERT** (mode-only) | `git checkout --` or `chmod 644`; **do not stage** |
| `tests/vault/vadv54-run/elsewhere/led-outside.tsv` | same | same |
| `tests/vault/vadv54-run/p/p2.md` | same | same |
| `tests/vault/vadv54-run/p/p3.md` | same | same |
| `corpus/knowledge/quarantine-staging-no-copy-r23.md` | lane-authored, in flight → **COMMIT with C2** | commit once it stops moving |
| `.ufo/waves/round-22/attempt2/assimilation/` (3 files) | lane-authored → **COMMIT with C2** (id-map receipt) | populate or drop the 0-byte `collisions` first |
| `.ufo/waves/round-22/attempt2/w1/*.md` (16 seat reports) | lane-authored, in flight → **COMMIT at landing** | commit by explicit path |
| `.ufo/waves/round-22/attempt2/w1/evidence/` (87 files @03:47) | lane-authored, in flight → **COMMIT at landing** | commit by explicit path |
| `census/operator-sweep-20261019/` (152 files) | **operator-owned → never touch** | never add/move/delete; needs an ignore rule |
| `census/round-21/__pycache__/`, `tools/__pycache__/` | inherited/generated → **not committable** | ignore-rule or delete (not my authority) |

Contents of `census/operator-sweep-20261019/` were **not read** (contract); the class rests on the
path name, the sibling `census/operator-sweep-20261018`, and the file count only.

---

## 2. Fleet root `/home/vgpnk/Projects/shokunin`

17 untracked paths, all files (no collapsed untracked dirs, so the enumeration is complete):

```
$ git -C .../shokunin status --porcelain | grep -c '^??'
17
?? .omp/mcp.json                       ?? .scratch/goal-20261025-hyaku-12h.md
?? .ufo/state/{kotoba,kotodama,revenger}.report-baseline   ?? .ufo/reports/round-35/mado.md
?? bm.json  ?? live.html  ?? live_s228.html  ?? nama.html  ?? s395.txt
?? scripts/hyaku/append-closure.py.bak-20261023T040735Z
?? scripts/hyaku/fleet-commit.sh.bak-20261023T040735Z
?? tf_bavelas.html  ?? unblob.log  ?? wb2.html  ?? write  ?? xc.xml
```

Seat-misroot test (executed): each of the 17 was grepped for `souji` **and** `round-22`.

```
### HIT <none>        --- every file: (souji=0 round-22=0)
```

**No untracked fleet file mentions `souji` and `round-22` together — no seat misroot in this census.**
No first-line quote is owed because there is no hit. The one file that looks like a misdirected agent
payload is `write` (25 B), whose entire content is `agent://U100N079H334f935b` — an agent-message
idiom, but for an unrelated id and with no `souji`/`round-22` text; it lands in the operator scratch
batch below, not as a seat artifact.

Scratch cluster, all one batch mtime `2026-10-24 18:07:20 -0300`:

| file | size | observed content |
|---|---|---|
| `xc.xml` | 237 B | `<!DOCTYPE html> … <title>Too many requests</title>` |
| `wb2.html` | 620 B | "blocked because our system has flagged it as suspected abusive bot traffic … Wayback Machine" |
| `unblob.log` | 1510 B | `[info] Creating extraction directory` — unblob extraction log |
| `write` | 25 B | `agent://U100N079H334f935b` |
| `s395.txt` | 0 B | empty |
| `bm.json` `live.html` `live_s228.html` `nama.html` `tf_bavelas.html` | 5–69 KB | same batch; **not read** (no `souji`/`round-22` hit, so no need) |

---

## 3. Protected holds

```
$ git status --porcelain -- .ufo/state .ufo/watchdog.log MANIFEST.json   # LANE root
 (no output; exit 0)
$ ls -d .ufo/state .ufo/watchdog.log MANIFEST.json                      # LANE root
 ls: cannot access '.ufo/state': No such file or directory
 ls: cannot access '.ufo/watchdog.log': No such file or directory
 ls: cannot access 'MANIFEST.json': No such file or directory
```

Lane-relative holds are **absent by construction** (lane `.ufo/` contains only `quarantine/` and
`waves/`) → vacuous pass: there is no lane hold to have been touched. The holds named in the item
exist only at the fleet root, and there they are **modified**:

| fleet hold | state | evidence |
|---|---|---|
| `.ufo/state/` | **MODIFIED (15 entries)** | 12 ` M` (`chousa kagi kaidoku kake kama kengaku kumitate mado mori souji tameshi tsukuroi`) + 3 `??` (`kotoba kotodama revenger`); sample `souji.report-baseline`: `22 e3b0c442…b855` -> `22 7573fed9…269f` |
| `.ufo/watchdog.log` | **MODIFIED** | `git diff --numstat` → `655 0` (655 appended lines) |
| `MANIFEST.json` | **clean** | `git status --porcelain -- MANIFEST.json` → 0 lines |
| `templates/` | **clean** | `git status --porcelain -- templates/` → 0 lines |
| `scripts/` | **MODIFIED (4 entries)** | ` M scripts/hyaku/hyaku.env`, ` M scripts/hyaku/lane-addendum.md`, `?? scripts/hyaku/append-closure.py.bak-20261023T040735Z`, `?? scripts/hyaku/fleet-commit.sh.bak-20261023T040735Z` |

Fleet `scripts/` change is operator-owned content, not corruption: `hyaku.env` moves
`L1_MODEL`/`JUDGE_MODEL` from `@m_swe` to `@m_flash` (comment cites the 2026-10-25 12 h directive and
a config backup), and `lane-addendum.md` (+19/−16) extends the addendum to phase 6 with the run-6
directives quoted verbatim and retargets the goal-file pointer to `20261025`. None of those paths was
written by this seat.

---

## Findings (severity order)

**F1 — HIGH (operability): four tracked lane files carry phantom dirt that has ridden 18 rounds.**
Content-empty `100644→100755` flips on two `.md`, one `.tsv`, one `.txt` vault fixture, byte-identical
to HEAD, mtime 2026-10-18, i.e. **before** round-4's commit `48a64d8` recorded the same paths as 644.
Any `git add -A` bakes exec bits into text fixtures; any round that reasons from `git status` inherits
a false "uncommitted work" signal. Reverting is provably lossless (sha256 worktree == HEAD blob).
Action: `chmod 644` the four paths, never stage them.

**F2 — HIGH (coverage/operability): the lane has no `.gitignore` at all.**
`ls .gitignore` → `No such file or directory`; `git check-ignore -v` returns NOT-IGNORED for every
untracked lane path, including a `.pyc`. Consequence: `census/operator-sweep-20261019/` — 152
operator-owned files, **0 tracked at HEAD** — is a single `git add -A` away from entering lane history,
and `census/round-21/__pycache__/` and `tools/__pycache__/` are committable bytecode. This is the
sharpest hygiene defect in the census: the destructive move is one careless command away and no rule
blocks it.

**F3 — MEDIUM (coverage): the round's own output is entirely untracked and still growing.**
Observed growth inside 3.5 minutes: w1 seat reports 0 → 4 → 16; `w1/evidence/` 19 → 50 → 87 files;
`assimilation/` 3 files. Landing therefore has to commit by explicit path, and cannot use a blanket
add without tripping F2. No content was lost during the census; this is a landing-discipline risk, not
damage.

**F4 — MEDIUM (evidence integrity, informational): a C2-gated file changed mid-census.**
`corpus/knowledge/quarantine-staging-no-copy-r23.md` was clean at 03:46:29 and ` M` at 03:47:09, diff
`2 +/2 -`, rewriting two Gate locators from `§ OPTIONS --no-copy` to
`§ DESCRIPTION, option --no-copy` ("the page has no OPTIONS heading"). That is precisely C2 predicate
3 (locator token) being repaired in flight: any C2 counting command run before the file settles
measures different bytes than the ones that will land. Not my verdict to give; flagging the window.

**F5 — MEDIUM (fleet durability): the round's binding contract file is uncommitted.**
`.scratch/goal-20261025-hyaku-12h.md` is untracked, while all three predecessors
(`goal-20261018-game-dev-2d-training`, `goal-20261022-hyaku-12h`, `goal-20261023-hyaku-24h`) are
tracked, and the modified fleet `scripts/hyaku/lane-addendum.md` cites it at lines 14 and 23 as the
lane-order/holds authority. A worktree reset or `git clean` on the fleet root destroys the contract
every lane is currently bound by. Operator/fleet owns the fix.

**F6 — LOW (hygiene): leftovers inside the protected fleet `scripts/` directory.**
Two dated backups (`append-closure.py.bak-20261023T040735Z`, `fleet-commit.sh.bak-20261023T040735Z`)
are untracked there; plus `.ufo/reports/round-35/mado.md` untracked at the fleet root (another lane's
report). Deletion is a fleet/operator decision; no lane may act, and this seat created no deletion
authority.

**F7 — INFO: no seat misroot, and the lane's cross-lane citation is clean.**
All 17 untracked fleet paths: 0 hits for `souji`+`round-22`. Within this lane, the only `round-35`
mention is `.ufo/waves/round-22/attempt2/w1/SnapTrashSpec.md:214-217`, which *documents* the
`scratch/` → `scratch-evidence/` relocation and states it cites no such path — confirmed, it does not.
Read-only cross-check in `mado-shokunin`: `git ls-files .ufo/waves/round-35/scratch-evidence | wc -l`
→ `261`; `4efaf63` present ("checkpoint the 235 seat evidence files and drop the 3.2 GB mutant
trees"); `scratch/` gone; `scratch-evidence/RevQuoteS210/{rederive.sh,rederive.out}` = 3727 B / 2714 B.
The peer reports' citations resolve there, and nothing in *this* lane dangles. (Fleet root has no
`.ufo/waves/round-35` at all — round waves are lane-local, so a fleet-root check of those paths is
the wrong root.)

---

## Residual risk and verification gaps

- **Live tree.** Lane and fleet both changed while I measured (HEAD `2a130b4`→`3216c19`; new
  `corpus/knowledge/...` edit at 03:47:09; seat reports and evidence files appearing). The census is a
  snapshot at 03:46:29–03:47:28, not an end state. A final post-landing `git status` is still owed.
- **Operator-sweep contents unread** (contract). Its class is a name/count inference, not a content
  check — deliberate.
- **Mode-flip mechanism is inference.** The observation (mode-only, sha-identical, mtime pre-committing
  round-4) is exact; *what* chmod'ed them on 2026-10-18 is `[INFERENCE]` — no in-repo code at HEAD sets
  744 on those paths.
- **`MANIFEST.json` cleanliness is worktree-vs-HEAD only**; its 1.6 MB of content was not audited (out
  of scope for this item).
- **Concurrent ownership.** Fleet `.ufo/state/`, `.ufo/watchdog.log` and `scripts/` are live machinery
  paths; an external sweep (round-35 case, ~03:45) was active on the fleet during this census, so any
  "stale artifact" judgement here is provisional by construction. This seat created no deletion
  authority and ran no mutating cleanup.
- **Written by this seat:** exactly two files —
  `.ufo/waves/round-22/attempt2/w1/RevScope.md` and
  `.ufo/waves/round-22/attempt2/w1/evidence/RevScope.tsv` (7473 B, 28 TSV lines = header + 27 rows,
  5 tab fields/row).
  No git write, no stage, no delete, no signal, no tool install.
