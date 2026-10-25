# ConnectorSiblingSources — cross-lane overlap scan for C3's five URLs

## Status

STATUS: PASS — **no other lane holds a row for any of the five URLs**, at any id, in any scope cell.
The fleet's own `shared` mode returns no line for them, and no fleet-level corpus exists to hold one.
`souji`'s registry also holds **none of the three git-scm pages as a row** (git-count-objects appears
only as an unopened lead bullet), so **CORPUS rule 2's supersede/refuse branch is NOT triggered** for
S115–S117 — they are first rows, and a `supersedes S0NN —` prefix in their `teaches` would be false.
What *is* triggered is narrower and un-warnable: `S063` (git-gc reachability) and `S035` (git-repo
structure sizes) already hold adjacent in-lane ground, and the census cannot flag adjacency across
different URLs — so each new `scope` cell must name its delta. Nearest cross-lane holding is kama's
**S104, a rejected `code` row on `builtin/fsck.c`**, plus kama's unlanded evaluation of the very
git-fsck URL — an adjacency, not a duplicate.

Axes touched: **calibration** (a row that names its neighbour is falsifiable against it; a row that
does not is an unfalsifiable claim of new ground), **coverage** (the delta clause is what makes the
entry non-restating), **operability** (unchanged). No axis harmed.

## Evidence

Lane base for every lane read: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (souji). All commands
read-only; no `git add/commit`, no `jj`, no `rm`/`mv`, no signals, nothing written outside this file.

### E1 — per-lane registry grep (the brief's command shape)

```
for d in /home/vgpnk/Projects/shokunin/*-shokunin; do for p in "$d/corpus/SOURCES.md"; do [ -f "$p" ] || continue;
  n=$(grep -c -E 'git-scm\.com/docs/git-(count-objects|fsck|prune)' "$p"); echo "$n  ${d##*/}"; done; done
```
→ `0` for all 21 lanes except `1  souji-shokunin`, and that single hit is **not a row** (E5).

### E2 — authoritative cross-lane answer (fleet tool, `shared` mode)

```
bash scripts/sources-census.sh shared --root /home/vgpnk/Projects/shokunin
```
exit `0`, 56 lines (`wc -l`). **No line contains `git-count-objects`, `git-fsck`, `git-prune`, `qiita` or
`csdn`.** The git-scm.com lines that do exist are a pre-existing shared vocabulary souji↔kama:

```
git-scm.com/docs/git-cat-file	shared	kama,souji
git-scm.com/docs/git-config	shared	kama,souji
git-scm.com/docs/git-rev-list	shared	kama,mori,souji
git-scm.com/docs/git-worktree	shared	kumitate,souji
git-scm.com/docs/gitrepository-layout	shared	kumitate,kama,souji
git-scm.com/docs/git-rev-parse	shared	kumitate,tameshi,tabi,mori,souji
git-scm.com/docs/git	shared	kama,tameshi,souji
```

### E3 — fleet-level corpora

`ls /home/vgpnk/Projects/shokunin/corpus` → absent; `ls /home/vgpnk/Projects/shokunin/SOURCES.md`
→ absent. `/home/vgpnk/Projects/shokunin/research/` holds three campaign dirs and no registry.
Fleet-wide recursive byte grep for each URL (`grep -rl -F <url> /home/vgpnk/Projects/shokunin`)
returns, outside `souji-shokunin/` and `.git` indices, only:

- `https://git-scm.com/docs/git-count-objects` → `./.ufo/waves/kaika-w1/souji-art.md:146`
- `https://git-scm.com/docs/git-fsck` → `kama-shokunin/.ufo/waves/round-24/build/{spec.json,advice/SrcFsck.md,out/SrcFsck/*}`
- `https://git-scm.com/docs/git-prune` → nothing
- `https://qiita.com/koseki/items/f1af58f1ec1693f0536a` → nothing
- `https://bbs.csdn.net/weixin_33940469/article/details/100327798` → nothing

### E4 — nearest cross-lane holding (kama), with its scope cell

`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:116`

```
| S104 | Git fsck promisor exception — https://raw.githubusercontent.com/git/git/v2.56.0/builtin/fsck.c | code | A | rejection of fsck green as proof every promised object is locally present | `mark_object`, lines143–149, v2.56.0; opened2026-10-21 | REJECTED: … | rejected | 2026-10-21 | on-release | corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md, SKILL.md |
```

Scope cell, verbatim: "rejection of fsck green as proof every promised object is locally present".
Note the URL: **`builtin/fsck.c` at v2.56.0, not the documentation page.** kama's round-24 seat
`SrcFsck` did open `https://git-scm.com/docs/git-fsck` (2026-10-21, HTTP 200, 95083 B, sha256
`ba958ce1…`) and concluded, at
`kama-shokunin/.ufo/waves/round-24/build/advice/SrcFsck.md:9`: "The page cannot be cited for
promisor validity." That verdict is a **wave artifact, not a registry row** — kama landed the code
row instead.

### E5 — souji's own registry: no row under another id

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
grep -nE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md | grep -cE 'git-scm\.com/docs/git-(count-objects|fsck|prune)'   → 0
grep -n -F 'git-count-objects' corpus/SOURCES.md                                                                                    → 176
awk 'NR>=140 && NR<=183 && /^#/{print NR": "$0}' corpus/SOURCES.md
  → 143: ## Search log
  → 171: ## Leads (unopened)
```
Line 176 is `- git-rev-list(1) --disk-usage; git-count-objects(1) -vH — https://git-scm.com/docs/git-rev-list, https://git-scm.com/docs/git-count-objects`,
i.e. a bullet **inside the `## Leads (unopened)` section**. It is the transcription of the campaign
dossier line `./.ufo/waves/kaika-w1/souji-art.md:146` (E3). `git-fsck` and `git-prune` have **zero**
occurrences anywhere in `corpus/`.

### E6 — in-lane census warnings at base (`validate`)

```
bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
```
exit `0`, 31 lines = **30 `W04` + 1 `ok`**, zero `E01`–`E12`. **No `W04` line names
git-count-objects, git-fsck or git-prune.** The 30 existing warnings are S035…S108 registry content
(e.g. `S058 duplicate url git-scm.com/docs/git-worktree across scopes`), unchanged from the round's
own baseline receipt (`.ufo/waves/round-23/w1/ScoutRegistryCensus.md` E1).

### E7 — why that absence is necessary-but-not-sufficient (tool mechanics)

`scripts/sources-census.sh:641-653`:

```
scope_key=u SUBSEP scope
if (u!="" && (u in url_seen) && !(scope_key in url_scopes))
  printf "%s\tW04\t%s duplicate url %s across scopes\n",lane,id,u
if (u!="" && (scope_key in url_scopes) && status!="rejected" && url_scope_nonrejected[scope_key] && teaches !~ /supersedes S[0-9]{3}/)
  printf "%s\tE04\t%s duplicate url %s within scope %s\n",lane,id,u
```
So `W04`/`E04` key on the **normalized URL**, and normalization (fixture at `:357-363`, where
`https://DUP.example/source` and `https://dup.example/source/` collapse to `dup.example/source`)
strips scheme/host case and a trailing slash only — a version segment is **not** stripped. Souji
already carries `git-scm.com/docs/git-worktree` (S003) *and* `…/git-worktree/2.56.0` (S230) with no
warning between them, which confirms it. Adjacency across **different pages** (`git-gc` vs
`git-prune`) can therefore never warn at all.

### E8 — in-lane history: the ground was already opened once, under campaign ids

`census/round-22/attempt2/slice-verdicts.tsv` (its own header: "ids below are campaign register ids
… NOT lane registry ids"):

```
S114	accepted	snapshot git-scm git-prune 2026-10-25: sentence present, only reference renders as git-repack[1] not git-repack(1)
S138	present	qiita page and its API markdown both carry "## gc.auto (6700)" at markdown line 11 / h2 anchor #gcauto-6700, access 2026-10-25; register class was a fold false positive (seat Slice138)
```

The eight slice ids are `S114 S118 S123 S124 S126 S131 S133 S138` — **the CSDN article is not among
them**, and `grep -rn -F '100327798' .ufo/waves/round-22` returns **nothing**. The ZH item has never
been opened by a souji seat.

## Findings

1. **No cross-lane row exists for any of the five URLs.** Location: E1 (21 lanes, 0 hits) and E2
   (fleet `shared` mode, no line). The `git-scm.com/docs/git-fsck` string outside souji exists only
   in kama's round-24 *wave* tree (E3), never in a `corpus/SOURCES.md`. There is no fleet-level
   registry that could hold one (E3).
2. **Cross-lane duplication verdict: none, on any of the five.** Discernment consequence: nil for
   this round's rows. The one real cross-lane fact is that souji and kama already share seven
   git-scm.com pages (E2), so a reader diffing the two registries will see the new rows sitting in
   that shared vocabulary — the same *host*, different *commands*. That is not duplication, and it
   should not be reported as such.
3. **Nearest holder is kama S104, and it is a different claim on a different URL.** Location: E4.
   Its scope is the *promisor* exception in `builtin/fsck.c`, status `rejected`. Souji's S116 scope
   ("reachability classes … and the `--lost-found` write side effect") does not touch promisor
   remotes. Two consequences the scribe must respect: (a) S116 is the **fleet's first row for that
   page** — no `supersedes` prefix, no claim of having displaced anyone; (b) S116 must **not** drift
   into promisor language, because kama's own seat established the page carries none (E4) — citing
   it for that would be a mis-citation kama has already documented.
4. **None of the three git-scm pages sits in souji's registry under another id, so CORPUS rule 2's
   supersede/refuse branch does not fire.** Location: E5. The one prior appearance —
   `corpus/SOURCES.md:176` — is a bullet in `## Leads (unopened)` (heading at line 171), and the
   contract settles its status at `CORPUS.md:83`: "## Leads (unopened)   bullets; a lead is not
   evidence and never a row". A lead is not an id, so S115 does not supersede anything. Writing
   `supersedes S0NN —` into S115's `teaches` would be a false statement in an append-only registry
   (`CORPUS.md:119-120`: "A correction is a new row whose `teaches` opens `supersedes S0NN —`.") —
   it applies only when a row is being displaced.
5. **The unwarnable adjacency is in-lane, and it is real.** Location: E6 + E7 + the registry cells.
   `S063` (git-gc reachability) already teaches that "once a ref is gone its objects become prunable
   after the prune date", and `S005` (git-repo structure; scope narrowed by `S035`) already teaches
   that `structure` reports "reachable object counts, inflated and disk sizes and largest objects by
   type". S117 and
   S115 therefore sit on *partly held* ground on *different URLs*, where neither `W04` (different
   normalized URL) nor `E04` (different URL) can fire. The delta each must carry, in its own `scope`
   cell, is exactly what the held rows lack: S117 — prune removes unreachable **unpacked** objects
   only, plus `-n` and `--expire`; S115 — the **loose vs in-pack** split, `prune-packable`,
   `garbage`/`size-garbage`, and alternate object databases, which the structure sizes do not
   separate.
6. **The community pair splits cleanly, and only one half is new.** Location: E8. The JA Qiita item
   was hand-checked in r22 attempt 2 (`S138`, verdict **`present`**, class recorded as a fold false
   positive); the ZH CSDN article has **no** prior souji opening. So: S119 is genuinely new and its
   tier-B call rests entirely on this round's ScoutCommunity fetch; S118's evidence chain starts at
   a *prior* round's hand-check, which `CORPUS.md` rule 1 does not accept as this round's opening —
   it needs this round's own fetch, quote and access date, and the r22 `present` verdict may be
   cited as corroboration only, never as the opening.
7. **No sibling lane's frontier owns this ground better.** `souji-shokunin/SKILL.md:5` — "fleet
   repository & workspace hygiene"; `mori-shokunin/SKILL.md:6` — "fleet & host observability";
   `kama-shokunin/corpus/README.md:3` — "local model serving & endpoint health". The only adjacent
   assignment anywhere is host **disk**, not the git object store:
   `tsukuroi-shokunin/corpus/README.md:243` — "Disk-space runway stays with mori". No lane's coverage
   map names git repository size; souji's `F2` (`corpus/README.md:40`) is the fleet's only such
   frontier row. Ground correctly owned here.
8. **Residual hygiene note, not a defect:** after the append, `corpus/SOURCES.md:176` will name a URL
   that is now also a row. The Leads section is not append-only (only the registry is,
   `CORPUS.md:118-120`), so the L1 may mark that bullet opened — but it must not be silently
   rewritten, because it records the r12 campaign's origin (E5) and the round-22 verifier already
   treats filed bytes as append-only evidence.

## Affected axes

- **calibration (7)** — improved, cheaply: a `scope` cell that names the held neighbour (S063/S035,
  kama S104) makes the row's novelty falsifiable from committed bytes instead of asserted.
- **coverage (8)** — improved in kind, not in count: the delta clause is what separates "3 new rows"
  from "3 rows restating S063/S035 with a new URL". No extra row, no extra id, no target change.
- **operability (8)** — untouched. Nothing in this item runs, writes or binds a receipt.

## Proposed move

Write S115–S117 as **complements with a named delta**, not as rows on a blank page:

1. **S117 (git-prune)** — put the unpacked-vs-packed distinction and `-n`/`--expire` in the `scope`
   cell *and* point at the neighbour by id, e.g. "…unpacked objects only, `--dry-run`, `--expire`;
   the gc reachability rule itself is S063's". This is the one row that would otherwise restate
   S063's teach ("become prunable after the prune date") under a fresh id, undetected by `W04`/`E04`.
2. **S115 (git-count-objects)** — scope the delta against `S035`/`S005`: the loose/in-pack split,
   `prune-packable`, `garbage`/`size-garbage`, alternates — the fields `git repo structure` does not
   separate.
3. **S116 (git-fsck)** — no in-lane neighbour, so no delta clause; instead an explicit boundary:
   reachability classes + the single writing option, **not** promisor validity (kama S104 and kama's
   `SrcFsck` already own and refuted that reading).
4. **S118/S119** — keep the `opened` date at this round's `2026-10-25` with this round's own fetch.
   For S118 the r22 `present` verdict is corroboration in `used-by`/lesson prose, not the opening.

Cost: three cell rewrites in a drafted block that has not been appended yet. No predicate, target,
key set or id assignment changes.

## Risks

- **Scope-cell drift into restatement.** Adding "not X (S0NN holds that)" text to a `scope` cell is
  safe for `E04` (which keys on URL+scope identity, E7), but if the same phrasing migrates into
  `teaches`, S117 starts to read as a correction of S063 — which it is not, and `supersedes` must
  stay out (Finding 4).
- **Versioned-URL blind spot.** If a later round adds `…/git-prune/2.56.0` while S117 holds the bare
  URL, no warning fires (E7, and the live S003/S230 pair). The delta clause does not fix that; it
  only makes the *current* adjacency visible. Do not treat the 30-warning `W04` set as a completeness
  check for same-page coverage.
- **Prior-round verdict reuse.** S118's strongest in-lane evidence is an r22 hand-check that returned
  `present`, not `accepted`. If ScoutCommunity's 2026-10-25 fetch disagrees, the r22 verdict does not
  outrank it — the newer opening wins, and the disagreement should be recorded rather than smoothed.
- **kama adjacency mis-read.** A future reader comparing registries may see kama's rejected `fsck`
  row and souji's admitted `git-fsck` row and call it a contradiction. It is not: different URLs,
  different claims, one rejected. Worth one sentence in the lesson's Gate so the pair is not
  re-litigated.

## Verification

Run by the L1 after the append (none of these were run by this item, which is read-only):

1. `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit `0`,
   `E01..E12` count `0`, and the **`W04` set unchanged at 30** (none of the three URLs collides;
   a 31st `W04` would mean a URL was already present and the scan in E5/E6 was wrong).
2. `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|.*git-scm\.com/docs/git-(count-objects|fsck|prune)' corpus/SOURCES.md`
   → `3` (currently `0`; E5).
3. `bash scripts/sources-census.sh shared --root /home/vgpnk/Projects/shokunin | grep -cE 'git-count-objects|git-fsck|git-prune'`
   → `0`, i.e. the new rows introduce **no** new cross-lane shared URL.
4. `python3 tools/souji-gate-check.py --entries corpus/knowledge/repo-size-census-readonly.md corpus/knowledge/count-objects-garbage-semantics-r24.md --snapshot-dir <dir> --expect-slice 0`
   → entries=2 ok=2 fail=0 (the frozen C3 counter; unchanged by this item).
5. Row/id arithmetic unchanged from the round baseline: `rows 114 → >=117`, `0` malformed, `0`
   duplicate ids (`.ufo/waves/round-23/w1/ScoutRegistryCensus.md` E2/E3/E6/E7).

No installs or upgrades were performed; no `pacman` transaction attempted. No scratch directory was
created — every read was direct. The only write of this run is this report.
