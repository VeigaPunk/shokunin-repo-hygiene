# S84ScoutDirs — lane directory-shape reconnaissance (souji r84, w1 seat)

Seat: scout (read-only on the lane). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Lane base: `35d87842efd966bfc326eff92fb534ab3e56b79e` (r83 closed admitted).
Receipt (every claim is a command output there): `.ufo/waves/round-84/w1/S84ScoutDirs/dirs-receipt.txt`.
Seat artifacts: `branch-histogram.py`, `census-in-tree-probe.py`, `shape-existence.py`,
`mutants-census-in-tree.json` (all under the seat dir, all read-only on the lane).

**Scope note.** The lane's working tree at receipt time carried one modified tracked file,
`tools/souji-vault-verify.sh` (56 insertions, 34 deletions) plus untracked `census/round-84/records/*`,
`census/round-84/srcs/` and `plans/round-84.md`. Those are **another seat's** C2 candidate bytes;
this seat did not create, edit or touch them, and this seat's own writes are confined to its seat
directory. `git diff --stat HEAD` shows no other tracked file changed.

---

## 1. The census command and its output

The command is the one `census/round-83/records/wave-dirs.txt` itself names:

```sh
for d in .ufo/waves/round-*/*/; do printf "%s\n" "${d#.ufo/waves/round-*}"; done \
  | sed -E "s#^[0-9]+/##" | sort | uniq -c | sort -rn
```

Run at the lane base, in the lane working tree:

```
     67 w1/     19 w2/      4 assimilation/   3 records/    2 residual/
      1 w3/      1 transcripts/  1 recovery/   1 l1/         1 final/
      1 build/   1 attempt2/   1 a2w1/       1 __pycache__/
```

`diff` against the r83 record's counts differs on **one line only**: `w1/ 67` vs `w1/ 65`.
Excluding the two rounds created since that census gives exactly 65:

```sh
for d in .ufo/waves/round-*/*/; do n=$(basename "$d"); [ "$n" = "w1" ] && echo "$d"; done \
  | grep -v -E 'round-(83|84)/' | wc -l      # -> 65
```

So the delta is precisely `.ufo/waves/round-83/w1/` and `.ufo/waves/round-84/w1/`. The r83 record
is reproduced exactly on every other shape.

**The census/round-<N> capture shapes** (the census-side tree):

```sh
ls -d census/round-*/waves/          | wc -l   # -> 16
ls -d census/round-*/wave/           | wc -l   # -> 12
ls -d census/round-*/records/wave-*/ | wc -l   # -> 21   (wave-w1/ 14, wave-repair/ 6, wave-responses/ 1)
ls -d census/round-*/w[0-9]/ census/round-*/a2w1/ 2>/dev/null   # -> (none)
```

Under `census/` the capture shapes are exactly the three the counter's `CAPTURE` regex names
(`waves/`, `wave/`, `records/wave-<w>/`). There is **no** `census/round-N/wN/` and **no**
`census/round-N/a2w1/`; `census/round-N/assimilation/` exists for rounds 27, 40, 46.

---

## 2. Do the population's TRUE and REFUSED shapes exist in the real tree?

**Every shape the r84 population uses as TRUE exists, with a non-zero count.** No TRUE row names a
shape absent from the lane's real tree.

| shape class | real-tree count | used by |
|---|---|---|
| `w1/` | 67 | TF7 |
| `w2/` | 19 | TF6, TF8 |
| `w3/` | 1 | (NF-L, a false row) |
| `a2w1/` | 1 | TF9 |
| `assimilation/` | 4 | TF10 |
| `records/` (own-tree) | 3 | (NF-M, a false row) |
| `waves/` (census-side) | 16 | TF1, TF3, TF4 |
| `wave/` (census-side) | 12 | PF-1 |
| `records/wave-*/` (census-side) | 21 | TF2, TF5 |

The deep two-component suffix shape TF8 depends on occurs **599** times in the real own tree
(`find .ufo/waves -mindepth 3 -maxdepth 3 -type d | grep -E '/(w[0-9]+|a2w1|assimilation)/[^/]+$' | wc -l`).

Both population tokens are the real lane bytes at their real paths — the sha256s equal the
harness pins exactly:

```
5212878dc0e8156e5cf27bd639a732a51d33473547b7e03ddf1a17ad6baddaaa  .ufo/waves/round-61/w1/S61ExecRealRecord/erratum-evidence.txt   (P07_PIN)
d0693448c0895860ebe7ece2549d3f70f694247ddb717d1fa2c66a4518d5aa89  .ufo/waves/round-32/a2w1/SwarmExecutor08.md                      (P04_PIN)
```

**Every shape the population REFUSES as a real shape also exists:** own-tree `records/` ×3
(`.ufo/waves/round-{23,27,60}/records/`, holding receipt files such as
`round-27/records/c1-before.tsv`, `round-60/records/sources-before.txt`) — the NF-M class; a real
`wN/` prefix that drops the token's suffix — `w2/` ×19, `w1/` ×67, `w3/` ×1 — the NF-Q class; and
another round's tree — 67 round dirs under `.ufo/waves`, each carrying exactly one `w1/` — the NF-L2 class.

The `decoy/` class used by NF-F, NF-G, NF12, NF12b, NF10, DM07 does **not** exist anywhere in the
real tree (`find .ufo/waves -type d -name decoy | wc -l` → 0). That is expected — a decoy is by
construction a shape the lane never had — and it is not among the three shapes the round's wording
claims to refuse from the real tree.

**Which real own-tree names the counter accepts.** The lane has 14 real own-tree wave-dir names;
the counter's `OWNTREE_WAVE` accepts exactly the 5 wave shapes and refuses the other 9:

- accepted: `w1/` 67, `w2/` 19, `w3/` 1, `a2w1/` 1, `assimilation/` 4
- refused: `records/` 3, `residual/` 2, `transcripts/` 1, `recovery/` 1, `l1/` 1, `final/` 1,
  `build/` 1, `attempt2/` 1, `__pycache__/` 1

NF-M is the only population row exercising the refusal of a non-wave own-tree directory, and it uses
`records/` — the class with the most files (3).

---

## 3. The r83 routed item: "ground or delete the census-in-tree branch"

Routed item (`corpus/lessons/round-83.md:138`, "## Routed to round 84", item 1): *"… true rows for
`a2w1/` and `assimilation/`; ground or delete the census-in-tree branch."*

The branch is `census/round-84/c1-pointer-counter.py` lines 387–395 (byte-identical to the r83
counter; both sha256 `052c4f3f…`):

```python
elif kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census" \
        and not _capture_ok(token, kr, target, tr):
    ...
    why = "census-in-tree target is not a wave capture keeping the token's full path suffix"
```

Its preconditions: the **token** begins `census/round-<N>/`; the item has a non-`-` frozen digest
(else `no frozen bytes to move` fires first); the **target** begins `census/round-<same N>/`; and
the target is not a census-side wave capture keeping the token's suffix.

### 3a. Zero rows of either population reach it

`branch-histogram.py` calls the counter's own `judge()` per population row against the R7 fixture
and buckets rows by the counter's own `why` string. On the 44-row r84 population the census-side
rows that fire (NF12, NF12c, NF12d, NF-H, NF-I) all fire the **neighbouring** branch at line 383
(`token[:kr.start(0)] != "census"` — their tokens are under `.ufo/waves/`, not `census/`). No row
reaches line 387. The same probe on the 36-row r83 population: also zero.

### 3b. The decisive measurement: deleting the branch is not killed by either population

Mutant `m11-no-census-in-tree` deletes the 902-byte block verbatim (it occurs exactly once, as the
battery requires):

```
ARM pristine pop=r83 rows=36 mismatches=0 errors=0 exit=0
ARM pristine pop=r84 rows=44 mismatches=0 errors=0 exit=0
MUTANT m11-no-census-in-tree pop=r83 killed=no mismatches=0 errors=0 exit=0
MUTANT m11-no-census-in-tree pop=r84 killed=no mismatches=0 errors=0 exit=0
SUMMARY mutants=1 sets=r83,r84 pristine_r83=ok pristine_r84=ok killed_r83=0 killed_r84=0 killed_total=0
```

**The census-in-tree branch is a sixth unbound clause, exactly as m6–m10 were before r84.** The
r84 population does not discriminate it: deleting it leaves both populations green.

### 3c. No existing population item can reach it

The only `census/round-<N>/` tokens in the whole lane are P19, P27 (r77) and L05, L13, L17 (r78),
and **all of them carry `frozen='-'`** — no item in the lane has a `census/round-<N>/` token *and*
a non-`-` frozen digest. The only census-token item *with* a frozen digest (L02/L03/P28,
`census/operator-sweep-20261019`) has no `round-<N>` in its token at all. An exhaustive sweep over
every census-token item × 16 candidate census targets: **0 reach branch 387, 96 blocked earlier**
(by `no frozen bytes to move` or `target absent at rev or digest differs`).

### 3d. No real ledger row or real layout makes it load-bearing

- **0** ledger rows in the whole lane are `MOVED` with a population token under `census/round-N/`.
  Every `MOVED` row in both pinned ledgers has an own-tree token (`.ufo/waves/round-N/…`) and a
  census-side target — e.g. P04 `.ufo/waves/round-32/a2w1/SwarmExecutor08.md` →
  `census/round-32/waves/a2w1/SwarmExecutor08.md`; P07 `.ufo/waves/round-61/w1/S61ExecRealRecord/erratum-evidence.txt`
  → `census/round-61/wave/w1/S61ExecRealRecord/erratum-evidence.txt`.
- The only `census/round-N/` dirs with a wave-dir-shaped child are rounds 27, 40, 46
  (`assimilation/`).
- A real-layout sweep over every `census/round-N/records/*` file × every wave-dir-shaped child,
  with the digest and basename checks satisfied: **0 pairs reach the branch.** `census/round-27`
  has `records/` and `assimilation/` but **no shared basename** (`OVERLAP: []`), so the counter's
  basename test kills the rest first.

### 3e. But the branch is live code, not redundant

A hand-built pair satisfying all four preconditions does reach it, and deleting the branch flips
that verdict from REFUSED to MOVED:

```
PRISTINE : ('REFUSED', "class=MOVED why=census-in-tree target is not a wave capture keeping the token's full path suffix")
DELETED  : ('MOVED', '')
```

So the branch is the **only** thing refusing a census-tree move whose target is not a wave capture
keeping the token's full path suffix. **It is not safe to delete silently** — the population would
stay green while the rule changes for a whole class of census-tree moves.

### Routing

**ROUTE TO r85** (this is the one routed item r84 does not discharge). The branch is a sixth
unbound clause, and the r84 population cannot bind it: grounding it requires a population item with
a `census/round-<N>/` token **and** a non-`-` frozen digest **and** a `MOVED` class — no such item
exists in the lane today, and the r77/r78 population files are sha256-pinned inside the counter
(`bbc19ac6…`, `7c04cdaf…`), so adding one means a new population + a new pin. Alternatively ground
it in a real census-tree layout — Section 3d finds none — or delete the branch **and** state its
effect explicitly (3e). Do not delete it on the strength of the green battery: the battery cannot
see it.

---

## 4. Disclosure: the calibration is against an on-disk tree, not a committed one

`census/round-83/records/wave-dirs.txt` heads itself *"at branch tip `1e870403…`"*, but the counts
it records (65 `w1`, 19 `w2`) are **working-tree** counts. The **tracked** tree at that commit has
20 `w1` and 8 `w2`:

```sh
git ls-tree -d -r --name-only 1e870403... -- .ufo/waves/ | grep -E '^\.ufo/waves/round-[0-9]+/[^/]+$' \
  | sed -E 's#^\.ufo/waves/round-[0-9]+/##' | sort | uniq -c | sort -rn
#  20 w1 / 8 w2 / 3 assimilation / 2 residual / 2 records / 1 transcripts / 1 recovery / 1 final / 1 attempt2
```

`.ufo/waves/` is gitignored (`.gitignore` line 1), so most of the "real" wave shapes the counter's
rule is calibrated against are **untracked directories that no commit carries**. Per shape at the
lane base: `w1` tracked 20 / on-disk 67; `w2` 8 / 19; `w3` **0 / 1**; `a2w1` **0 / 1**;
`assimilation` 3 / 4; `records` 2 / 3. `w3/` and `a2w1/` — two of the three shapes the r84
population newly binds clauses on — are **entirely untracked**.

The r84 population reproduces the r83 record exactly (the `w1` 67-vs-65 delta is precisely
`round-83/w1` + `round-84/w1`), so the record is sound *as a working-tree census*. The r84 report
should say so explicitly, so the calibration is not read as a claim about committed bytes.

---

## 5. Scope note on "exact path" vs "shape class"

The population's rows are judged at fixture revision **R7 inside the harness's own fixture repo**
(`build_fixture`, `census/round-84/c1-false-row-harness.py`), which copies the token bytes into
synthetic paths. The receipt's "exact parent directory PRESENT/ABSENT" column is therefore about
the **lane disk**, not about where a row is judged, and no row's verdict depends on the lane disk's
directory contents — the fixture carries the bytes. The **shape-class** column is the load-bearing
one, and it is what Section 2 reports.

---

## 6. Remaining unknowns

- Whether the L1 wants a new census-token population item built for r85 (this requires new sha256
  pins inside the counter and the harness — an L1/council decision, not a seat's).
- Whether the `w3/` and `a2w1/` shapes being untracked is intentional lane policy or drift. The
  r83 record's header suggests the lane treats the working tree as the shape source of truth; this
  seat does not adjudicate that, it reports it.
- `census/round-27|40|46/assimilation/` is a real census-side wave-dir-shaped directory, but the
  lane has no `MOVED` row pointing into any of them; whether those three directories were ever
  intended as capture targets is not answerable from the tree.

## 7. Tooling

No tool was installed, upgraded or removed; no pacman/uv/npm/cargo transaction was run. The seat
needed only coreutils, read-only git and stdlib python3. Per the host guard, pacman transactions
are paused host-wide; nothing was needed from an install channel.

## 8. Checks the main agent should run

The receipt's Section 5 lists the reproductions. The seat ran its own measurements; per the seat
contract the integration owner re-measures once after integration:

```sh
python3 -B census/round-84/c1-clause-battery.py --counter <candidate> \
  --work <empty dir outside /tmp> --only r84 --expect-killed 5
```

and, for the routed branch specifically, the m11 mutant run reproduced in receipt Section 3b.
