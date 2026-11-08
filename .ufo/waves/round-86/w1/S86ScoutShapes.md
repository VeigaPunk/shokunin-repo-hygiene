# S86ScoutShapes — reconnaissance: are NF-W's and NF-Y's shapes real in the lane, and what do the r85-routed shapes still lack?

Seat: S86ScoutShapes (scout, leaf member — no subagent dispatch).
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (lane id souji). Round 86, wave 1.
Lane base (read for the shape census): `2acbbfc80ac91e1b65cf5dae7287209fed9c7c86` (the working tree's HEAD).
Items' base revision: `705fa1385c4ccec23811cfa57104046ec6587258` (the `r85`/`r86` item-population base, as the filed
counter's `POPS` table records it).

Counter under test: `census/round-86/c1-pointer-counter.py`, sha256
`8278ea4d41d0975b748419ba79de44d3eefc924d8f415071660def83f9fba1f3`.
Population: `census/round-86/c1-false-rows.tsv` sha256 `79db70f6740de41a326dc4193bf80c5394fe126d636cc98d4e26e4b5e140f561` (49 rows, matches the preregistration pin).
Items: `census/round-86/c1-items.tsv` sha256 `5abf3b01d8cfe50b9b64d465a4602bd5a9d8f6915ad257e02fb4ee5a9c9dade2` (matches the preregistration pin).
Ledger: `census/round-86/c1-ledger.tsv` sha256 `7cbb28c9805c959925805b9e06dfdf5d9f8d01e57b1ad2645269e06cf782abce` (2 rows: I85R, I85T).
Mutants: `census/round-86/c1-mutants.json` sha256 `6f055edea73e5b22d870cb1e85100251cf7ba47486519ed448582b1b9c6471a6` (8 members).
Harness: `census/round-86/c1-false-row-harness.py` sha256 `2dac2e818c65bb9cd8a8361899b78cc33ddb91b9ba216d27e5b0f821804bc9d9`.
Battery: `census/round-86/c1-clause-battery.py` sha256 `d7e299c247066b3022fe19378af3ff16c076326ddbc86c289d9ca8a459cba9e5`.

**Scope note.** This is reconnaissance. Nothing here is a claim about C1 or C2; every verdict below is a statement about
*shape reality* and *row expressibility*, each backed by a command and its output. I did not run the C1 battery, did not
score the eight mutants, and did not touch any lane file other than this report.

---

## 0. Headline

1. **NF-W's shape is NOT real in the lane.** The census-in-tree clause's shape (a census-rooted token landing in a
   wave directory under its own round) has **0 instances** in the committed tree and **0** in the working tree. The
   lane's only `census/round-<N>/<wdir>/` children are `assimilation/` in rounds 27, 40, 46 — and every
   byte-equal sibling of those files sits under `waves/`, a *capture* shape, so `_capture_ok` accepts them and the
   census-in-tree clause is never the refuser. The r86 row NF-W is therefore **synthetic**: it is exactly the
   R9 fixture plant `census/round-84/w1/c1-after.txt` that the harness builds (`c1-false-row-harness.py`, R9 block).
   *This is consistent with the preregistration's own stated limit* ("NF-W and NF-Y are synthetic fixture rows") and
   with r85's S85ScoutShapes §1b, which measured the same 0 and said a future binding row "must plant the copy in a
   fixture revision". Nothing here contradicts the filed claim; it pins the shape's reality precisely.
2. **NF-Y's shape is NOT real in the lane either, but it is one step closer.** The short-shape shape (a token ONE
   component below its round, landing in a wave capture under the same round) has **0 exact instances** in both trees
   — because the lane's one-component census tokens (`census/round-42/c1-register.tsv`, `census/round-58/c1-counter.py`,
   …) have **no** copy at `census/round-<N>/<capture>/<same name>`. There are **61 near-misses**: the same
   one-component token with a same-basename copy **deeper** under a capture subtree
   (`census/round-42/waves/w1/R42critic01/h0/c1-register.tsv`). The near-miss is *not* the NF-Y shape: `_capture_ok`
   compares the whole suffix (`have[-len(want):] == want`), so a deep copy with a short token's tail does **not**
   satisfy it, and the m14 guard is not what decides those pairs.
3. **Of the four r85-routed shapes the r85 seat still names, exactly ONE is expressible as a row against the current
   harness population/ledger model: m14 (already bound by NF-Y in r86).** The other three are **not expressible as a
   row**:
   - **m12** (R0's token-on-base-line half) needs an *item* whose token is off its line; the item set is sha-pinned
     and every one of its 64 items across the four pinned sets has its token **on** its line. A row cannot change an
     item's `(file, line, token)` — the harness's forge replaces only `(class, target)`.
   - **m16** (the sentence-end punctuation disjunct in `_whole`) is reachable only through `_declared()`, which is
     called only for `cls == QUARANTINED`, and only matters on a line that must **resolve** a quarantine. The
     r86 population has **7 QUARANTINED rows, all expecting REFUSED** and **zero** positive ones; a stricter rule
     cannot be seen by a REFUSED row.
   - **m17** (duplicate-id refusal in `_ledger`) is a property of the ledger *file*, not of a row. The harness passes
     `--ledger` once per run; the forge never replaces the ledger. A duplicate id in a pinned ledger makes the
     counter print `LEDGER-REFUSED` and exit 1 for **every** row of the arm at once.
   - **the basename clause** (r85 S85Scribe F4's `p1-no-basename`) is **reachable but not outcome-differentiating**:
     dropping it changes only the *message* on 74 119 real byte-equal lane pairs and the *outcome* on **zero** of
     them (measured; see §3.4). A row that only changes the message cannot kill the mutant, because the harness
     compares `got=<status>`, not `why`.
4. **A new census-round child name appeared since r85**: `census/round-86/` (this round) plus `results/` and
   `chunks/` in the working tree only. Neither affects the C1 shapes.

---

## 1. Shape census — one command per claim, with its output

### 1.1 NF-W's shape: "a `census/round-<N>/` token landing in a wave directory under the same round"

Command (one; read-only; run from the lane root):

```
python3 -B /fast/scratch/hyaku/souji-r86/S86ScoutShapes/final_census.py <receipt>
```

Output (verbatim, receipt `final-census.txt`):

```
=== WORKTREE (34687 files under census/ + .ufo/waves/) ===
  NF-W shape instances (census token -> same-round wave-dir landing, identical tail): 0
  NF-Y shape instances (one-component census token -> same-round wave-capture landing): 0
  NEAR-MISS shape instances (one-component census token -> same-basename file under a capture subtree, DEEPER landing): 61
=== COMMITTED HEAD (19741 files under census/ + .ufo/waves/) ===
  NF-W shape instances (census token -> same-round wave-dir landing, identical tail): 0
  NF-Y shape instances (one-component census token -> same-round wave-capture landing): 0
  NEAR-MISS shape instances (one-component census token -> same-basename file under a capture subtree, DEEPER landing): 61
  byte-equal pairs census/round-N/assimilation/X <-> census/round-N/waves/assimilation/X: 4
    census/round-27/assimilation/collisions == census/round-27/waves/assimilation/collisions
    census/round-27/assimilation/quarantine-slice == census/round-27/waves/assimilation/quarantine-slice
    census/round-27/assimilation/reg-ids == census/round-27/waves/assimilation/reg-ids
    census/round-27/assimilation/staged-ids == census/round-27/waves/assimilation/staged-ids
```

**NF-W shape: 0 instances (committed), 0 instances (worktree).** The shape is *synthetic*.

Why 0 — the lane's `census/round-<N>/` immediate children that are wave-shaped:

```
$ git ls-tree -r -d --name-only HEAD -- census/ | awk -F/ 'NF==3' | awk -F/ '{print $3}' \
    | grep -E '^(w[0-9]+|a2w1|assimilation)$' | sort | uniq -c
      3 assimilation
```

i.e. **only `assimilation/`, in 3 rounds** (27, 40, 46 — 6, 3, 5 files). There is **no** `census/round-<N>/w1/`,
`w2/`, `a2w1/` anywhere in the lane, in either tree. And the 4 byte-equal `assimilation/` pairs are the *wrong
direction* for the census-in-tree clause: the copy sits under `waves/`, which the counter's `CAPTURE` regex
(`^(?:waves/|wave/|records/wave-[^/]+/)(.+)$`) accepts, so `_capture_ok` resolves them as MOVED rather than letting
the census-in-tree clause refuse.

The row NF-W therefore binds a clause on a **planted** copy. That plant is in the filed harness, R9:

```
# census/round-86/c1-false-row-harness.py, R9 block
put("census/round-84/w1/c1-after.txt", c1b)
...
git(fx, "add", "-f", "--", "census/round-84/w1/c1-after.txt", "census/round-83/waves/c1-pointer-counter.py")
git(fx, "commit", "-q", "--no-verify", "-m", "r86 C1 fixture R9 (census-in-tree + short-shape targets)")
```

and the row itself (`census/round-86/c1-false-rows.tsv`, last two lines):

```
NF-W	fixture	R9	r85	I85R	MOVED	census/round-84/w1/c1-after.txt	REFUSED	-	r86 C1 decoy: the census-in-tree clause is the ONLY refusal ...
NF-Y	fixture	R9	r86	I86S	MOVED	census/round-83/waves/c1-pointer-counter.py	REFUSED	-	r86 C1 decoy: a token ONE component below its round ...
```

**Clause-level confirmation that c7 is the first refuser for NF-W** (the filed counter's own functions, imported
read-only; `reach-probe.txt`):

```
NF-W row  : token census/round-84/records/c1-after.txt -> census/round-84/w1/c1-after.txt
    _capture_ok = False
    _owntree_ok = True
    -> own-tree belt ACCEPTS (w1/ is OWNTREE_WAVE and the tails match) so the census-in-tree clause is the first refuser
```

So the clause attribution in the row text is right; the *shape* is synthetic.

### 1.2 NF-Y's shape: "a token ONE component below its round landing in a wave capture under it"

Command (one; from the lane root):

```
$ git ls-tree -r --name-only HEAD -- census/ > cm-all.txt        # 16191 paths
$ awk -F/ 'NF==3 && $2 ~ /^round-[0-9]+$/' cm-all.txt | sort > onecomp-rounds.txt    # 1163 one-component census tokens
```

Output:

```
### NF-Y exact shape, committed: token census/round-N/<f> AND landing census/round-N/<capture>/<f> ###
NF-Y exact-shape pairs (committed): 0
NF-W exact-shape pairs (committed): 0
```

**NF-Y shape: 0 exact instances (committed), 0 (worktree).**

The 61 near-misses (from §1.1) are the closest real thing. A sample, with byte-equality:

```
TOKEN census/round-42/c1-register.tsv -> LANDING census/round-42/waves/w1/R42critic01/h0/c1-register.tsv byte_equal=True
TOKEN census/round-43/c1-counter.py    -> LANDING census/round-43/waves/w1/R43reviewer01/c1-counter.py    byte_equal=True
TOKEN census/round-58/c1-counter.py    -> LANDING census/round-58/wave/w1/S58Mutationtester10/c1-counter.py byte_equal=True
TOKEN census/round-60/c1-matrix.tsv    -> LANDING census/round-60/wave/w1/S60ExecMatrix/c1-matrix.tsv    byte_equal=True
TOKEN census/round-62/c1-counter.py    -> LANDING census/round-62/wave/S62ExecCounter/c1-counter.py           byte_equal=True
```

Why a near-miss is *not* NF-Y's shape: `_capture_ok` compares the token's whole below-round suffix against the
target's suffix (`have[-len(want):] == want`), so `census/round-42/waves/w1/R42critic01/h0/c1-register.tsv` does not
carry the token's tail (`c1-register.tsv`); and the m14 guard (`len(want) < 2 or len(got) < 2`) fires only when the
*token* is one component below its round **and** the target is at the same depth — the near-misses have a *deep*
target, so `len(got) >= 2` and the pair is decided elsewhere.

Clause-level confirmation (filed counter's own functions):

```
NF-Y row  : token census/round-83/c1-pointer-counter.py -> census/round-83/waves/c1-pointer-counter.py
    _capture_ok = True
    _owntree_ok = False
    want(got) component counts: token below round = 1, target below round = 2 -> the len(want)<2 guard fires
    with the m14 guard dropped: _capture_ok would accept (last component equal) -> resolves MOVED
```

Note the asymmetry that makes NF-Y work and the near-misses not: NF-Y's target is at
`census/round-83/waves/<file>` — **directly** under the capture root, so `_capture_ok`'s suffix comparison is
`["c1-pointer-counter.py"] == ["c1-pointer-counter.py"]`, while the own-tree branch is refused *only* by the
short-shape guard. The lane holds no such pair.

### 1.3 The census-round / wave-round child census (both trees), by kind

Command (one; from the lane root):

```
$ git ls-tree HEAD "census/" | awk '$2=="tree" && $4 ~ /^census\/round-[0-9]+$/ {print $4}' \
    | while read -r d; do git ls-tree HEAD "$d/" | awk -v d="$d" '{k=($1=="040000")?"DIR":"FILE"; print k"\t"$4}'; done \
    | awk -F'\t' '{c[$1]++} END{for(k in c) print k"="c[k]}'
```

Output (committed HEAD):

```
DIR=227
FILE=1163
```

The 227 **DIR** children of `census/round-<N>/` (committed), by name and by how many rounds hold them:

| dir child | rounds holding it |
|---|---|
| `records/` | 60 (r23…r57, r60…r86) |
| `controls/` | 44 (r24, r41…r57, r60…r86) |
| `sources/` | 37 (r23…r63) |
| `probes/` | 19 (r64…r84, r86) |
| `srcs/` | 16 (r69…r86) |
| `waves/` | 16 (r26…r34, r39…r45) |
| `wave/` | 12 (r54…r62, r65…r67) |
| `fixtures/` | 5 (r53…r57) |
| `assimilation/` | **3 (r27, r40, r46)** |
| `battery/` | 3 (r68, r69, r72) |
| `transcripts/` | 3 (r16, r18, r20) |
| `matrix/` | 2 (r60, r61) |
| `manifests/` | 1 (r57) |
| `live-fleet-pairs/` | 1 (r18) |
| `jj-w1-reports/` | 1 (r42) |
| `replay-fragments/` | 1 (r13) |
| `attempt2/` | 1 (r22) |
| `c2-cases/` | 1 (r76) |
| `__pycache__/` | 1 (r10) |

**Not one of the 227 is a `w[0-9]+/`, `w2/`, `a2w1/` directory.** The `OWNTREE_WAVE` set
(`^(?:w[0-9]+|a2w1|assimilation)/`) has exactly **3** hits under a census round, all `assimilation/`
(rounds 27, 40, 46 — 6, 3, 5 files). The worktree adds `results/` (1) and `chunks/` (1) and 10 `__pycache__/`
entries, and round-86's own `controls/`.

The `census/round-<N>/` tree's **1163 FILE** children are the one-component-below-round tokens (round-1 … round-86,
plus `census/operator-sweep-*`).

`.ufo/waves/round-<N>/` immediate children (worktree): **DIR 106, FILE 587**; the dominant wave-dir child names are
`w1` (69 rounds), `w2` (19), `a2w1` (8), `assimilation` (4). Committed `.ufo/waves/` holds **3550 files** across
**35 round dirs** (round-13 … round-86). The `.ufo/waves/round-<N>/` shape is *the lane's real* wave shape — it is the
`census/round-<N>/` tree that lacks it.

---

## 2. Authority-line list: every real `census/round-<N>/` and `.ufo/waves/round-<N>/` path on a committed authority line

Command (one; from the lane root; the authority set is the counter's own `AUTHORITY = ("SKILL.md", "LOG.md",
"SCORECARD.md", "corpus")`):

```
python3 -B /fast/scratch/hyaku/souji-r86/S86ScoutShapes/auth_candidates.py <receipt>
```

Output (receipt `auth-candidates.txt`):

```
authority lines scanned at BASE: 34163
distinct real paths named on a committed authority line (whole-path match): 1772
distinct (file:line) sites: 3125

by shape class:
  census:1-below-round (NF-Y item shape)	473
  census:2+below-round (NF-W item shape)	1044
  ufo-waves	255

== ROW-CARRIABLE candidates: census-rooted paths named on a committed authority line ==
  census-rooted candidates total: 1517   of which ONE component below their round: 473
```

(The same census without the base-rev restriction gives 1642 distinct paths over 4219 `(file:line, path)` hits —
receipt `auth-lines.txt` — because the base-rev scan only counts lines that exist at the items' base revision.)

**Which of these could carry a population row without fabricating a line?** A row needs an **item**, and an item is
`(id, file, line, token, frozen-digest)` where the token is a real path that appears **on that line** of that
authority file. So the row-carriable candidates are exactly the census-rooted paths in the list above:

* **NF-Y's item shape — 473 candidates** (a census path ONE component below its round, named on a committed
  authority line). First 12 by file:line:

  ```
  SCORECARD.md:147            census/round-1/census-summary.json
  SCORECARD.md:147            census/round-1/census.tsv
  corpus/README.md:53         census/round-1/census.tsv
  corpus/QUALITY.md:33        census/round-10/S02-cluster-A.md
  corpus/lessons/round-12.md:112   census/round-10/S02-cluster-A.md
  corpus/knowledge/trash-spec-restorable-quarantine.md:28   census/round-10/S06-cluster-C-member2.md
  corpus/lessons/round-12.md:97     census/round-10/S13-fragment.md
  LOG.md:527                  census/round-10/cert-16.json
  SCORECARD.md:443            census/round-10/cert-16.json
  corpus/lessons/round-13.md:20     census/round-10/cert-16.json
  LOG.md:497                  census/round-12/after.txt
  corpus/lessons/round-12.md:8      census/round-12/critic.md
  ```

  Any one of these is a legal **item token** for a future NF-Y-shaped row — provided the row also plants the
  same-round capture copy (see §1.2: no such copy exists, so the plant is unavoidable).

* **NF-W's item shape — 1044 candidates** (a census path two or more components below its round). The filed row
  uses `census/round-84/records/c1-after.txt` at `LOG.md:3165`; the other 1043 are equally legal item tokens.

* **`.ufo/waves/round-<N>/` — 255 candidates** (e.g. `corpus/QUALITY.md:43` → `.ufo/waves/round-13/w1/AttackBounds.md`,
  `LOG.md:825` → `.ufo/waves/round-15/w1/ConfigRepair.md`). These are **not** usable for the census-in-tree or
  short-shape clauses: those clauses need a census-rooted token (the census-in-tree clause's condition is
  `target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census"`). They are usable only for the *own-tree*
  belt and the `no-round` guard.

* **The full per-path `file:line` index** (all 1772 candidates, 3125 sites) is in `auth-candidates.txt` under
  `== full per-path file:line index (all candidates) ==`, and the un-restricted version in `auth-lines.txt`.

---

## 3. The r85-routed shape gap: expressibility per shape

The r85 routed list (`.ufo/waves/round-85/w1/S85MutCounter.md` §3, and `plans/round-85.md` §A4) names **six** new
single-edit mutants, of which one was already bound (`m13-no-round-guard`, killed by NF3) and five were unbound:
`m12-r0-line`, `m14-short-shape`, `m15-empty-want` (measured **dead**), `m16-nf6b-punct`, `m17-dup-id`. The r85
verifier spot-check (§5 R86-3) carries them to r86 together with **NF-L3** (the token-on-line row) and, from
`.ufo/waves/round-85/w1/S85Scribe.md` §F4, the **basename clause** (`p1-no-basename`).

Verdict key — *expressible as a row against the current harness population/ledger model* means: there exists a row
in `census/round-86/c1-false-rows.tsv` that, on the current pinned items/ledger/harness, changes the counter's
**outcome** (not just its message) when the clause is dropped.

| shape | clause (filed counter line) | reachable? | expressible as a row today? | why |
|---|---|---|---|---|
| **m12** token-on-line | `judge` line 378: `and token in blob[int(line) - 1]` | yes (r85 seat measured: fabricated item → pristine `ERROR`, mutant `UNRESOLVED`) | **NO** | needs an **item** whose token is off its line; the item set is sha-pinned in the counter's `POPS` and **every** item in all four pinned sets has its token **on** its line (§3.1); a row replaces only `(class, target)` |
| **m14** short-shape | `_owntree_ok` line 366: `if len(want) < 2 or len(got) < 2` | yes | **YES — already bound by NF-Y in r86** | NF-Y is exactly this shape; the r86 population kills `m14-short-shape` on the 49 rows and the r85 control leaves it alive |
| **m15** empty-want | `_capture_ok` line 348: `bool(want) and` | **no — dead code** | **NO (and not needed)** | `CAPTURE` is matched against a non-empty `group(1)`, so `want` is never empty; r85 measured 0 of 32 inputs flip. Routed decision was "delete or state as dead", not "a row" |
| **m16** punctuation | `_whole` lines 256-257: the `.`/`,`/`;`/`:` sentence-end disjunct | yes (251 decisive sites on committed authority lines at BASE — but see below) | **NO** | reachable only via `_declared()`, which is called **only** for `cls == QUARANTINED`; the disjunct only matters on a line that must **resolve** a quarantine; the r86 population has **7 QUARANTINED rows, all `REFUSED`**, and **0** positive ones (§3.2) |
| **m17** duplicate-id | `_ledger` line 479: `or r[0] in ledger` | yes (r85: silent overwrite) | **NO** | a property of the **ledger file**, not of a row; the harness passes `--ledger` once per run and the forge replaces only `(class,target)`. A duplicate id makes the counter print `LEDGER-REFUSED` and exit 1 for **every** row of the arm at once (§3.3) |
| **basename** clause | `judge` line 401: `os.path.basename(target) != os.path.basename(token)` | yes | **NO** | reachable but **not outcome-differentiating**: measured on the real lane's byte-equal pairs, dropping it changes the *message* on 74 119 pairs and the *outcome* on **zero** (§3.4) |

### 3.1 m12 — every pinned item's token is ON its cited base line

Command (one; read-only; from the lane root):

```
python3 -B /fast/scratch/hyaku/souji-r86/S86ScoutShapes/m12_scan.py <receipt>
```

Output (receipt `m12-scan.txt`):

```
=== item set r77: census/round-77/c2-population.tsv (base d4f5156) : 35 items ===
  items whose token IS on its cited base line : 35  (P01,...,P35)
  items whose token is NOT on its cited line  : 0
=== item set r78: census/round-78/c2-population.tsv (base a8558d4) : 22 items ===
  items whose token IS on its cited base line : 22  (L01,...,L22)
  items whose token is NOT on its cited line  : 0
=== item set r85: census/round-85/c1-items.tsv (base 705fa13) : 3 items ===
  items whose token IS on its cited base line : 3  (I85R,I85C,I85T)
  items whose token is NOT on its cited line  : 0
=== item set r86: census/round-86/c1-items.tsv (base 705fa13) : 4 items ===
  items whose token IS on its cited base line : 4  (I85R,I85C,I85T,I86S)
  items whose token is NOT on its cited line  : 0
```

**64 of 64 items across the four pinned sets are on-line.** The clause's negative arm is unreachable from any row:
the harness's forge file carries `(rid, item, class, target, expected)` and the counter's `judge` receives the item
from the **population's pinned item set** — a row cannot move a token off its line. Binding m12 needs a **new pinned
item set** (an instrument change: a new `POPS` entry in the counter plus a new items TSV), not a row. The r85 seat
reached the same conclusion ("it needs an item whose token is *not* on its line — i.e. a new pinned item set, not a
row") and it is unchanged by r86.

### 3.2 m16 — needs a positive QUARANTINED row, and there is none

Commands (two; from the lane root):

```
$ grep -n "QUARANTINED" census/round-86/c1-false-rows.tsv | cut -f1,5,7,8
$ awk -F'\t' '!/^#/{print $8}' census/round-86/c1-false-rows.tsv | sort | uniq -c
```

Output:

```
NF4   L06   .ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/NOT-THE-STUB   REFUSED
FP8   L16   .ufo/quarantine/round-17/.ufo/NOT-THE-L0                                REFUSED
LP3   P01   .ufo/quarantine/round-17/tests                                          REFUSED
NF6b  L06   .ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/other-stub       REFUSED
NF6c  L06   .ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/ghost-stub       REFUSED
NF6d  L06   .ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/readme-stub      REFUSED
NF6e  L06   .ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/late-stub        REFUSED

     12 MOVED
     37 REFUSED
```

**7 QUARANTINED rows, all expecting `REFUSED`; 0 positive QUARANTINED rows; the population's expected-status
vocabulary is `{MOVED, REFUSED}` only.** Dropping the punctuation allowance makes the rule **stricter**, and a
stricter rule cannot change a `REFUSED` row's outcome — it can only change a row that *resolves*. So m16 needs a
**positive QUARANTINED row** (`expect=QUARANTINED`), i.e. a new expected-status in the population vocabulary plus a
quarantine leaf on the lane disk plus a committed declaration line whose path is followed by sentence punctuation.

The punctuation site itself exists in the lane — 251 decisive sites at BASE (receipt `m16-scan.txt`), e.g.

```
LOG.md:963   path=census/round-18/seat-audit-adjudication.json   followed_by='. '
SKILL.md:159 path=/souji-census-now                             followed_by='.*'
```

— but **not one** of the 251 is a `.ufo/quarantine/…` path or a `tests/vault/…` path, i.e. **not one** is a
declaration line the `_declared()` check could consume for a QUARANTINED row.

The filed function's behaviour, for the record:

```
_whole(b'other-stub', b'...p/p6repo/other-stub.') = False     <- the '.' is preceded by a path byte
_whole(b'p6repo/other-stub', b'a `p6repo/other-stub.` b') = True
_whole(b'p6repo/other-stub', b'a `p6repo/other-stub` b')  = True
```

(the disjunct only matters when the byte *before* the path is not a path byte and the byte *after* the path is
`.`/`,`/`;`/`:` followed by a non-path byte).

### 3.3 m17 — a ledger-file property, unreachable from a row

Commands (two; from the lane root):

```
$ cat census/round-86/c1-ledger.tsv
$ python3 -B /fast/scratch/hyaku/souji-r86/S86ScoutShapes/reach_probe.py <receipt>   # _ledger() on a duplicated-id file
```

Output:

```
I85R	MOVED	census/round-84/waves/c1-after.txt	a capture-shaped move under the token own census round
I85T	TOKEN	census/round-49/sources/s272-python-open-located-quote.txt	path wrapped onto the next LOG line

_ledger on a duplicated-id file -> {'I85R': ('MOVED', 'census/round-84/records/c1-after.txt')} bad= ['I85R']
```

The duplicate is refused by `_ledger` (it lands in `bad`), and `main()` then prints `LEDGER-REFUSED id=…` and
returns 1. That is a **whole-arm** red, not a row-level one: the harness runs one counter invocation per row but
passes the **same** `--ledger` to all of them, so a duplicate id turns every row of the arm red at once and cannot
isolate a clause. The r85 seat said the same ("this clause is not merely unbound — it is unmeasurable by the current
harness. Binding needs a duplicate id in a pinned ledger (instrument change)"), and the r86 ledger is byte-identical
to r85's (`census/round-86/c1-ledger.tsv` sha256 `7cbb28c9…`, 2 rows), so nothing has changed.

### 3.4 The basename clause — reachable, but no row can kill it

This is the one routed shape whose status the r85 seat and I measure **differently in emphasis**. S85Scribe §F4
corrected an earlier claim and reported the basename clause as *"a live, reachable, discriminating clause that no
pinned row exercises — unbound, and therefore groundable, exactly like the census-in-tree clause"*. The reachability
half is right. The **groundable** half does not hold for the current harness: a population row is killed by a change
in the counter's **outcome**, and the harness compares `got=<status>` — the `why=` message is not compared.

Command (one; from the lane root):

```
python3 -B /fast/scratch/hyaku/souji-r86/S86ScoutShapes/real_pair_diff.py
```

Output (receipt `real-pair-diff.txt`), over the **201 209** byte-equal file pairs in the lane's committed tree:

```
clause histogram (pristine / mutant) over the real byte-equal lane pairs:
  pristine:
     D:round	120922
     C:basename	74119
     E:owntree-belt	3385
     None	1352
     G:capture-cross-root	1011
     I:no-round	418
     F:location-belt	2
  p1:
     D:round	120922
     E:owntree-belt	71122
     G:capture-cross-root	5015
     I:no-round	2796
     None	1352
     F:location-belt	2

OUTCOME-DIFFERING real lane pairs under c7: 0
OUTCOME-DIFFERING real lane pairs under m14: 0
OUTCOME-DIFFERING real lane pairs under p1: 74119
```

Read that last line carefully: under `p1` the 74 119 pairs move from `C:basename` to a *different refusing clause*
(`E`/`G`/`I`) — the **message** changes, the **outcome** (`REFUSED`) does not. The `None` count is **1352 in both
arms** and **the accepted set is identical**: dropping the basename clause never turns a refusal into a resolution.

A second, independent check through the counter's **real `judge()`** (30 000 synthetic shape pairs, digest and
disk checks stubbed so the path clauses are reached, receipt `judge_diff2` output):

```
pairs with differing basenames driven through the REAL judge(): 30000
status pairs (pristine, p1):
   ('REFUSED', 'REFUSED')	30000
OUTCOME-DIFFERING pairs (rows that would kill p1-no-basename): 0
```

**Conclusion.** The basename clause is *reachable* — it decides 74 119 real lane pairs as the **first** refuser —
but it is **not outcome-differentiating**: every pair it refuses is refused by a later clause too, because the
downstream `_capture_ok` / `_owntree_ok` suffix comparisons already force the last component to match. A population
row therefore **cannot** kill `p1-no-basename` under this harness. It would take either (a) an instrument change that
compares the `why` message, or (b) a *clause reordering* (moving the basename check after the suffix comparisons,
where it would become outcome-differentiating), or (c) a decision to state the clause as **redundant** and delete it
— the r85 verdict "ground it" is not reachable by a row on the current model.

Note this does **not** contradict the r86 claim: `m9-basename-only` (a *different* clause — the own-tree comparison's
`got[1:] == want[1]` vs a basename-only form, `_owntree_ok` line 375) is a different edit and **is** killed by rows
(TF8/NF-P, per r85's receipts). The basename clause at `judge` line 401 is the one measured here.

### 3.5 Side-by-side with the r86 claim's own scope

The preregistration's stated limit is *"NF-W and NF-Y bind exactly one clause each and prove nothing about the other
four r85-measured guards (m12, m14's neighbours, m16, m17) that stay unrowed."* My measurement **confirms** that limit
and sharpens it: of those four, **m14 is now bound** (by NF-Y) and **m12, m16, m17 are not expressible as rows at
all** against the current harness population/ledger model — they need an instrument change (new pinned item set for
m12; a positive QUARANTINED row + a lane-disk quarantine leaf + a punctuated declaration line for m16; a pinned
ledger with a duplicate id for m17). The fifth routed guard, **m15**, is dead code by the r85 measurement and has no
row either.

---

## 4. What this means for the L1 (findings, not claims)

1. **NF-W and NF-Y are synthetic fixture rows.** The preregistration says so; the census pins it down: the
   census-in-tree shape has **0** real instances and the short-shape shape has **0** exact instances in either tree.
   The lane's *nearest* real relations are the 4 byte-equal `census/round-27/assimilation/X ≡
   census/round-27/waves/assimilation/X` pairs (which resolve as MOVED, so they never reach the census-in-tree clause)
   and the 61 deeper same-basename capture copies (which `_capture_ok` rejects on the suffix, so they never reach the
   short-shape guard). **The claim wording need not change** — the limit is already stated — but a reviewer should
   read "the lane really holds the shapes" as **the shape is real in the counter's rule and in the fixture, not in
   the lane's bytes**.
2. **The r85 routed list has shrunk to two live items, and neither is a row.** m12 / m16 / m17 each need an
   instrument change, not a population row. If r87 wants to close them, the cheap route is an instrument change
   (new pinned item set for m12; a positive QUARANTINED row + a lane-disk quarantine leaf for m16; a pinned ledger
   with a duplicate id for m17) — and the lane should say so explicitly, because "a row each" (r85 §A4 disposition)
   is not available on this model.
3. **The basename clause needs a different disposition than "ground it".** It is reachable but outcome-redundant;
   r85's S85Scribe §F4 corrected one reading of it but kept "groundable". On this harness, no row can kill it. The
   honest options are: reorder it after the suffix comparisons (then it becomes outcome-differentiating), or delete
   it as redundant, or change the instrument to score the refusal message. **This is a re-routing recommendation,
   not a claim against C1** — C1's claim is about the eight frozen mutants, none of which is `p1`.
4. **If r87 wants a *real* (non-synthetic) NF-W/NF-Y-shaped row, the lane must first grow the shape.** There are
   **1044** census-rooted two-or-more-below-round paths and **473** one-below-round paths already named on committed
   authority lines (§2) — i.e. the *item* side is abundant and needs no fabrication; only the *target* side (a
   same-round wave-dir / wave-capture copy with matching bytes) has to be planted, and the lane has no such copy.

---

## 5. Reproducers (all read-only; receipts copied into this seat's directory `.ufo/waves/round-86/w1/S86ScoutShapes/`)

| receipt (in `.ufo/waves/round-86/w1/S86ScoutShapes/`) | what it measures |
|---|---|
| `final-census.txt` | census/.ufo-waves child census by kind (both trees); NF-W / NF-Y / near-miss instance lists with byte-equality; the 4 `assimilation` byte-equal pairs |
| `reach-probe.txt` | the filed counter's `_capture_ok` / `_owntree_ok` on NF-W's and NF-Y's own pairs; m12/m16/m17 requirement analysis; `_ledger` on a duplicated-id file |
| `m12-scan.txt` | on-line / off-line token census over all four pinned item sets |
| `m16-scan.txt` | 251 decisive sentence-end punctuation sites in the committed authority lines at BASE |
| `judge_diff2` output | real-`judge()` differential for the basename clause over 30 000 shape pairs |
| `real-pair-diff.txt` | clause-chain differential over the lane's 201 209 real byte-equal pairs (c7 / m14 / p1) |
| `auth-candidates.txt` | the authority-line list with file:line at BASE, by shape class (1772 paths / 3125 sites) |
| `auth-lines.txt` | the same census without the base-rev restriction (1642 paths / 4219 sites) |
| `shapes-receipt.txt` | full census child-kind tables, both trees |
| `census-child-kinds.txt` | the `census/round-<N>/` child census split DIR/FILE, with the per-name round roster |
| `judge_diff2.txt` | the real-`judge()` basename differential (30 000 shape pairs) |

Scripts: `final_census.py`, `reach_probe.py`, `m12_scan.py`, `m16_scan.py`, `judge_diff.py`, `judge_diff2.py`,
`real_pair_diff.py`, `auth_census.py`, `auth_candidates.py`, `shape_census.py`.

**No mutating git/jj command was run in the lane.** Every git call was read-only (`rev-parse`, `ls-tree`,
`cat-file`, `show`, `log`). No fixture repository was created (the differential probes drive the counter's own
functions in-process, over the lane's committed bytes). No lane file was modified except this report.

**Tooling.** No installs or upgrades were needed; no pacman transaction was attempted. The `pacman` guard was
respected (nothing was installed at all).

## 6. Confidence

* **High** (measured, reproducible): NF-W shape 0/0, NF-Y shape 0/0, 61 near-misses, 4 `assimilation` byte-equal
  pairs, 473/1044/255 authority-line candidates, m12's 64/64 on-line items, m16's 7-all-REFUSED QUARANTINED rows,
  m17's ledger-file mechanism, the basename clause's 74 119 message-changes vs **0** outcome-changes over 201 209 real
  pairs, and the same zero on 30 000 real-`judge()` shape pairs.
* **Medium** (structural inference, stated as such): that the census-in-tree and short-shape clauses can only ever
  be reached via a planted copy, given the lane holds 0 instances of both shapes.
* **Not claimed**: any verdict on the C1/C2 claims, on the eight mutants' kill counts, or on the battery's exit
  code. Those are the L1's and the executors' to measure.
