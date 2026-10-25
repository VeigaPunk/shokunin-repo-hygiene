STATUS: PASS

# Sibling-overlap scan — souji r22 attempt2, seat L1Souji22.Connector

Read-only. Wrote only this report and
`.ufo/waves/round-22/attempt2/w1/evidence/Connector.md`. No cleanup executed,
no process signalled, no git/jj write, no deletion authority created. Base lane
revision `4edb25dfe262515d0da63224bbba71e02e36cba5`.

Axes in play: **calibration**, **operability**, **coverage**. This seat proposes
one move at the end that improves two of them and harms none.

## 1. Executed evidence (command → observed output)

**Fleet census.** `ls -d /home/vgpnk/Projects/shokunin/*-shokunin/ | wc -l` → `21`
(audio, chousa, game-dev-2d, game-dev-3d, kagi, kaidoku, kake, kama, kasegi,
kengaku, kotoba, kotodama, kumitate, lore, mado, mori, revenger, souji, tabi,
tameshi, tsukuroi).

**Exact-URL search**, scope exactly as assigned — every lane's
`corpus/SOURCES.md` + `corpus/knowledge/`, then repeated over all of
`*/corpus/`:

```
$ grep -rln 'man1/mv\.1\.html'        */corpus/   -> souji only
$ grep -rln 'method\.File\.trash\.html' */corpus/ -> souji only
$ grep -rln 'freedesktop\.org/trash'  */corpus/   -> souji only
$ grep -rln 'man2/rename\.2\.html'    */corpus/   -> souji only
$ grep -rln 'man2/statx\.2'           */corpus/   -> souji only
$ grep -rln 'man/gio\.1\.en'          */corpus/   -> souji only
$ grep -rln 'git-prune'               */corpus/   -> NONE
```

No sibling lane holds any of the seven URLs. Sibling near-misses are different
documents (`man.archlinux.org/man/{pacman.8,systemd.exec.5,access.2,...}` across
tsukuroi/mori/kumitate/chousa/kama;
`git-scm.com/docs/{git-gc,git-fsck,git-fetch}`, none git-prune).

**Staged package.** `SOURCES.append.md` holds 134 rows, ids **S109–S242**;
`knowledge/corpus/knowledge/` holds 68 entries including ten F4-candidate files.
The two adopted lane entries are **not** copies of their staged namesakes:

| file | lane sha256/bytes | staged sha256/bytes |
|---|---|---|
| `quarantine-staging-no-copy-r23.md` | `0081e83045a9…` / 4848 | `f13fb769c418…` / 3490 |
| `quarantine-origin-record-fields-r24.md` | `b92f8118ab9c…` / 5299 | `0fb78aef7929…` / 3665 |

Lane files add their own frontmatter (`source:`, `verified-at`, `recheck`,
`ground:`) and their own `## Gate`; staged files carry campaign ids
(`S124/S116/S115`; `S137/S126/S117/S022`).

## 2. Verdict table

Overlap classes, fixed here: **duplicate** = the same URL already exists as a
row somewhere other than the row this round minted; **adjacent** = a different
document covering the same decision surface; **none** = no other holder.

| lane | row id | URL | overlap-class |
|---|---|---|---|
| souji | S110 | https://man7.org/linux/man-pages/man2/rename.2.html | duplicate — campaign registry only (staged `S116`); no sibling lane |
| souji | S111 | https://man7.org/linux/man-pages/man1/mv.1.html | duplicate — campaign `S115`; **plus** in-lane claim duplication with HELD `S025` (see F7) |
| souji | S112 | https://man.archlinux.org/man/gio.1.en | duplicate — campaign `S137`; no sibling lane |
| souji | S113 | https://docs.gtk.org/gio/method.File.trash.html | duplicate — campaign `S126`; no sibling lane |
| souji | S114 | https://man7.org/linux/man-pages/man2/statx.2.html | duplicate — campaign `S117`; no sibling lane |
| souji | S022 (pre-existing, mined 2026-10-19) | https://specifications.freedesktop.org/trash/latest/ | duplicate — **same lane, pre-existing row cited not re-minted** (adopted-row rule satisfied); no sibling lane |
| — | none minted | https://git-scm.com/docs/git-prune | none — no row in any lane registry; appears only as register-slice evidence `S114` (see F4) |
| souji | S109 (own-work, no URL) | vendored five-device `RENAME_NOREPLACE` probe | none — lane-owned measurement, no external holder |

Answer to question 1: **no sibling lane holds this round's knowledge.** The only
same-URL rows are the staged campaign registry (not a lane) and souji's own
pre-existing `S022`, which the round correctly cites rather than duplicates.

## 3. F4 delta — staged package vs the lane's current F4

The lane holds four F4 files (the frontier table row still lists two; see F2):

| F4 entry | status | rows |
|---|---|---|
| `corpus/knowledge/trash-spec-restorable-quarantine.md` | pre-existing, admitted | S022 |
| `corpus/knowledge/quarantine-same-filesystem-rename.md` | pre-existing, **HELD** | S024, S025 |
| `corpus/knowledge/quarantine-staging-no-copy-r23.md` | adopted r22 | S109, S110, S111 |
| `corpus/knowledge/quarantine-origin-record-fields-r24.md` | adopted r22 | S112, S113, S114, S022 |

Ten staged files are F4-relevant. Two were assimilated (re-grounded); eight were not:

| staged entry | what it adds | held by lane? |
|---|---|---|
| `quarantine-staging-no-copy.md` (951dbddd) | base claim: staging can refuse copy *and* refuse overwrite | superseded by the adopted r23 |
| `quarantine-staging-no-copy-r23.md` (f13fb769) | rename(2) support schedule + vendored probe | **yes** — re-grounded |
| `quarantine-staging-no-copy-r24.md` (109a2a6b) | **"Every writable mount implements the no-clobber rename"** — a universal quantifier | no — and the lane's evidence (5 devices) cannot carry it; see F8 |
| `quarantine-origin-record-fields-r23.md` (a2b46cf8) | three-part record: layout + refusal + identity | no — broader than the adopted r24 |
| `quarantine-origin-record-fields-r24.md` (0fb78aef) | read side: original path is what restore consumes | **yes** — re-grounded |
| `origin-record-format-gvfs-r26.md` | the record is a two-key key-file; the brief's named path did not exist | no — **additive** |
| `origin-record-writer-r27.md` | GLib writer's guarantees as a receipt contract | no — **additive** |
| `origin-record-durability-r28.md` | atomicity ≠ durability; durability is the platform's | no — **additive** |
| `origin-record-exclusivity-r28.md` | O_EXCL + rename, not rollback | no — **additive** |
| `origin-record-mechanism-set-r33.md` | three mechanisms complementary; GLib uses all three | no — **additive** |

F4 delta in one line: **+2 admitted entries (staging primitive, record read
side), 0 byte-copied; 5 genuinely new staged entries remain unadopted (record
format, writer, durability, exclusivity, mechanism set) and 3 are variants the
lane should not adopt as-is.**

## 4. Adjacency worth reporting out

- **Staging entry (`quarantine-staging-no-copy-r23.md`, S109/S110/S111) →
  `tsukuroi-shokunin`.** Its province is host operability and system repair —
  package state, `.pkg.tar.zst` receipt discipline, boot health — where a
  staging move that silently overwrote an existing initramfs or kernel file is
  exactly the failure its update-safety gate exists to prevent.
- **Origin-record entry (`quarantine-origin-record-fields-r24.md`,
  S112/S113/S114/S022) → `mado-shokunin`.** Its province owns the desktop plane
  (`~/.config/hypr`, `~/.config/waybar`, themes/wallpapers) — real files that an
  operator trashes and must restore, and the entry's whole content is which
  field makes that restore possible.
- Register-row adjacency (not adopted, offered once): the git-prune row is
  directly useful to `kumitate-shokunin`, whose province is `ufo-fsd` scripts
  and runtime that create the worktrees whose registrations a prune/expire
  policy silently affects.

## 5. Bounded findings

- **F1 — id collision, six-fold, post-mint (calibration, operability).** The
  lane registry now ends at S114; the staged registry holds S109–S242. They
  name different documents:
  `S109` probe vs git-fetch; `S110` rename(2) vs `builtin/fetch.c`;
  `S111` mv(1) vs `builtin/pull.c`; `S112` gio(1) vs git-count-objects;
  `S113` File.trash vs git-fsck; `S114` statx(2) vs git-prune.
  `corpus/lessons/round-22.md:318-321` records the collision step as
  "reg 108 ids, staged 134 ids, 0 collisions" — true for the **pre-mint**
  range only; after minting S109–S114 it is not true of the tree as it now
  stands. In-lane proof needs no campaign read: `slice-verdicts.tsv:1` carries
  `S114 … snapshot git-scm git-prune` beside `SOURCES.md` S114 = `statx(2)`,
  same round, same directory tree.
- **F2 — F4 coverage-map row is stale (coverage).** `corpus/README.md:42` still
  says "frontier, entries held" and lists two files, while the round's own
  prose claims F4 "moves from 'frontier, entries held' to 'frontier, entries
  admitted'". The two new entries appear only at lines 429 and 432.
- **F3 — entry attributes pre-existing knowledge to a same-round row
  (calibration, outside C1's frozen enum).**
  `quarantine-origin-record-fields-r24.md:12-14` says the lane "already holds …
  the *write contract* (S113)", but S113 was mined `2026-10-25` in this round
  (`SOURCES.md:133`). C1's enum reads SCORECARD.md only, so this is **not**
  reported as a C1 mismatch and must not be folded into it.
- **F4 — git-prune evidence pointer does not resolve inside the lane
  (operability).** `slice-verdicts.tsv` row `S114` cites "snapshot git-scm
  git-prune", but `census/round-22/attempt2/sources/` holds 13 files and none
  is git-prune. The lane-alone reader cannot re-check that verdict. Not a
  fabrication finding: the campaign snapshot tree was not read (out of scope).
- **F5 — slice row S118 carries prose into the id field (operability, low).**
  `quarantine-slice` line 8 reads `` S118`   the cited source could not be
  fetched, …``. Coverage is unaffected — `SLICE_ID_RE = r"S\d{3,}"`
  (`tools/souji-gate-check.py:45`) is unanchored and still yields `S118`;
  reproduced extraction gives T=8, verdict rows=8, missing=[], extra=[].
  Residual risk: the same unanchored regex would accept any `S<digits>` in free
  prose as a required id.
- **F6 — S131 class divergence, recorded not adjudicated.** Committed
  `slice-verdicts.tsv` says `S131 accepted`; peer `L1Souji22.Slice131` reports
  `refused` (citation-class defect, span belongs to git-worktree(1)). Either
  way it is one frozen class and V=T. Flagged so the final tip and the report
  do not disagree silently.
- **F7 — in-lane claim duplication (coverage, calibration).** The HELD K5 entry
  `quarantine-same-filesystem-rename.md` already asserts "GNU `mv` first tries
  `renameat2(…, RENAME_NOREPLACE)`" and "`mv --no-copy` turns the cross-device
  case into a hard failure", citing S025. The new staging entry presents
  "`mv --no-copy` is the portable fallback" as newly supplied. Genuinely new:
  the rename(2) per-filesystem schedule (S110) and the vendored probe (S109).
- **F8 — staged r24's universal quantifier is unsupported by this lane
  (calibration risk if adopted later).** Its claim is "every writable mount
  implements the no-clobber rename"; the lane's committed evidence is five
  probed devices. If a future round adopts that variant unchanged it will import
  a claim wider than the receipt.

## 6. One bounded proposal

**Evidence.** F1 above: the collision receipt is scoped "reg 108 ids" but the
tree now has 114 lane ids whose S109–S114 overlap the staged S109–S114 on
different documents, and the overlap is already visible inside one round's
census directory.

**Affected axes.** Improves **calibration** (a declared zero must be true of the
tree it is declared in, not of an earlier snapshot of it) and **operability**
(a reader resolving `S114` across lane and campaign currently gets two
documents). **Coverage** unchanged; no entry added or removed.

**Proposed move.** Make the id-space disjointness a *post-mint*, machine-checked
receipt rather than a pre-mint prose clause: re-run the collision step at the
final tip over id→document maps of `corpus/SOURCES.md` and the staged
`SOURCES.append.md` restricted to the lane's minted range, and state the
namespace once where ids are defined — one line saying a lane id and a campaign
id are distinct namespaces whose numeric overlap is expected and disambiguated
by registry, not by number.

**Risks.** CORPUS.md rule 2 is append-only, so renaming or renumbering S109–S114
is not available — a "fix" that renumbers would itself violate the rule and
re-point six citations (S109→S109, S110→…, per the document map). The checker
must ship with its own failing fixtures (divergent id, missing id, identical id)
or it becomes the same kind of unverified assertion it replaces. A prose-only
namespace note without the checker changes nothing measurable.

**Verification.** One command from the lane root that exits non-zero on any id
in the lane's minted range mapping to a different document than the campaign
row of that number, plus the fixtures above; read the exit status at the final
tip, not at the pre-mint base where it necessarily passes.

## 7. Tooling

No install or update was required or performed; no pacman transaction was
attempted (host-wide pause respected). Nothing outside the two permitted files
was written.
