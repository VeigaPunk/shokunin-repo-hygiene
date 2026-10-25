# ScoutCensusBefore — round-26 independent round-start census re-derivation

## Status
STATUS: PASS — fresh `sources-census.sh validate` is byte-identical to the frozen `census-before.txt` (sha256 `a699d0be…efa0c`, exit 0), and all six manual CORPUS.md census categories re-derive clean at rev `89e0fceeefcf28db313c94120be6d25e03c60094`; one witness-strength caveat recorded as Finding 3 (the frozen file carries no row count, so byte-identity alone cannot witness the C2 127→132 row-count literal — the C2 receipt counter does).

## Evidence

Revisions used
- Lane repo: `/home/vgpnk/Projects/shokunin/souji-shokunin`, branch `master`.
- Frozen prereg commit: `89e0fceeefcf28db313c94120be6d25e03c60094` (ancestor of HEAD `07f83e69979b1032f9de4fe876739a8dccc7242b`; verified with `git merge-base --is-ancestor`).
- Lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`.
- Fleet script `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` — worktree blob `3f314620b2395eeb70d8405410132027dfe608e4` == `git rev-parse HEAD:scripts/sources-census.sh` (fleet HEAD `8177d1e9334c21349fd20584e4f54d33466d9235`); `git status --porcelain -- scripts/sources-census.sh` empty (unmodified).
- Toolchain: bash 5.3.20, GNU Awk 5.4.1, git 2.56.0, grep 0.2.0 (pi-uu-grep). No installs performed this run.

### E1 — Fresh lane validate vs frozen `census-before.txt` (byte-identical)

Command (run from fleet root, lane dir = live worktree at tip):
```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
```
Output → `/var/tmp/souji-r26-ScoutCensusBefore/validate-fresh.txt` (stdout 2907 B, stderr 0 B), exit `0`.

```
$ cmp validate-fresh.txt /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/census-before.txt && echo BYTE-IDENTICAL
BYTE-IDENTICAL
$ sha256sum validate-fresh.txt .../round-26/census-before.txt
a699d0be3452bb74f662bbc07dc02f7cf9016ee26c26df72497fc366915efa0c  validate-fresh.txt
a699d0be3452bb74f662bbc07dc02f7cf9016ee26c26df72497fc366915efa0c  /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/census-before.txt
$ diff -u .../census-before.txt validate-fresh.txt   # no output
$ wc -l  → 35 both files
```
Second independent run reproduced run 1 byte-for-byte (`cmp` clean) — deterministic, no clock/`--today` dependence (both runs same UTC day `2026-10-25`).

Shape of the 35 lines: 34 × `souji W04 …` warning rows + 1 × `souji ok /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`. First and last W04 lines:
```
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S126 duplicate url git-scm.com/docs/git-worktree across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```
W04 semantics (fleet script, line 33, verbatim): `W04 same URL across scopes (warnings do not affect clean lanes)`.

### E2 — Independent reconstruction of the round-start census from the frozen tree

The frozen tree was materialised read-only with `git archive 89e0fceeefcf28db313c94120be6d25e03c60094 | tar -x -C /var/tmp/souji-r26-ScoutCensusBefore/tree` (lane repo contents only; no fleet `.scratch/`, no `.ufo/state/`, no `MANIFEST.json`, no `shokuknow` access). Byte check of the registry:
```
$ sha256sum tree/corpus/SOURCES.md
8252728f8fde08004b67492c1b9098d688c904149188248bb66cb7f2853d5859  tree/corpus/SOURCES.md
$ git cat-file -p 89e0fccc…:corpus/SOURCES.md | sha256sum
8252728f8fde08004b67492c1b9098d688c904149188248bb66cb7f2853d5859  -
```
Same blob at the lane base: `git rev-parse 89e0fccc…:corpus/SOURCES.md 0eca7c8…:corpus/SOURCES.md` → `f3cffccdb15be2b8ead6cf19fda8c8a8adc145d7` for both; `git diff --stat 0eca7c8… 89e0fccc… -- corpus/SOURCES.md` empty.

A scratch fleet root (`shokunin.conf` with one `souji|souji-shokunin` row) pointed at that tree reproduces the frozen artifact:
```
$ sources-census.sh validate --root /var/tmp/souji-r26-ScoutCensusBefore/fleetroot souji   # exit 0
$ diff -u .../census-before.txt val-frozen-lane.txt
-souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
+souji	ok	/var/tmp/souji-r26-ScoutCensusBefore/fleetroot/souji-shokunin/corpus/SOURCES.md
```
Only the path column of the trailing `ok` line differs (scratch path); the 34 W04 rows are identical, and the extracted W04 id set equals the frozen one (`diff` of sorted id columns empty). So `census-before.txt` is reproducible from the frozen commit, modulo the absolute-path field.

### E3 — Six manual CORPUS.md census categories at `89e0fccc…`

Command source: `/home/vgpnk/Projects/shokunin/CORPUS.md` lines 133–148 (the `### Census — run from the lane root` block). Contract anchor, verbatim, line 136: `malformed rows — 11 columns means NF=13; must print 0`. Run with cwd = the extracted lane root (so the relative `used-by` paths resolve against the frozen tree):

```
### rows
127
### malformed
0
### tier
A=120 B=5 C=2
### status
mined=103 queued=15 rejected=9
### dup-ids
(none above)
### enum
(none above)
### mined-missing
(none above)
```
Supporting counts at the same rev: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` = 127; NF distribution = `NF=13 127` (all 127 rows are 13-field, so malformed = 0 by construction); 103 mined rows carry 112 `used-by` path tokens, all present on disk; no escaped `\|` sequence anywhere in the file; `grep -n '\\|' corpus/SOURCES.md` returns nothing.

Same six categories re-run against the live worktree at tip (post-C2-append), for comparison:
```
rows: 132   malformed: 0   tier: A=125 B=5 C=2   status: mined=108 queued=15 rejected=9
dupids: []   enum: []   mined-missing: []
```
and the maintained parser agrees (`sources-census.sh census --root /home/vgpnk/Projects/shokunin souji`, exit 0): `souji rows 132`, `tier.A 125 / tier.B 5 / tier.C 2`, `status.mined 108 / queued 15 / rejected 9`.

### E4 — Fleet-wide validate (read-only, no-harm datum)

```
$ sources-census.sh validate --root /home/vgpnk/Projects/shokunin   # exit 0
```
356 output lines, 331 × `W04`, **0** lines matching `^E[0-9]{2}`; every lane ends with an `ok` line. No E-code anywhere in the fleet at this moment.

### E5 — C2 receipt cross-check (row-count witness)

```
census/round-26/records/c2-before.tsv   rev=89e0fceeefcf28db313c94120be6d25e03c60094  registry_rows=127  grounded_f1=0  rc=0
census/round-26/records/c2-after.tsv    rev=e0f8dcd12b1df1c53f213dc3a71def77d8ddf3f3  registry_rows=132  grounded_f1=2  rc=0
```
Independently re-derived: 127 rows at `89e0fccc…` and at base `0eca7c8…` (both via `git show … | grep -c`), 132 rows at tip. The receipt's `registry_rows` literal is corroborated.

### E6 — Mutation control on the frozen artifact

A copy of the frozen tree with one registry row (`| S100 |`) deleted (127 → 126 rows) still validates with exit 0 and produces the **same** validate output as the frozen artifact after normalising the trailing path column (`diff` of normalised outputs empty). This is the basis of Finding 3.

## Findings

1. **Fresh lane census is byte-identical to the frozen round-start census.** `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/census-before.txt` (committed at `12fd90bcd9cdfab495e178023eeaa838a977fcbe`, the prereg-freeze commit; blob `d6c62e5d7a9bc7b641c6fdfa3d5792ee99e37376`, unchanged at `89e0fccc…` and in the worktree — `git rev-parse` and `git hash-object` agree) equals the fresh run's stdout exactly, sha256 `a699d0be3452bb74f662bbc07dc02f7cf9016ee26c26df72497fc366915efa0c`, exit 0, 35 lines, 34 W04 + 1 `ok`. **No divergence.**
2. **The frozen artifact is reproducible from the frozen commit.** `git archive` of `89e0fceeefcf28db313c94120be6d25e03c60094` into a scratch fleet root yields the identical 34 W04 rows (identical id set) and an `ok` line; only the absolute path in the `ok` row differs because the tree lived under `/var/tmp`. The registry blob at `89e0fccc…` is byte-identical to the lane base `0eca7c8…` (`f3cffccdb15be2b8ead6cf19fda8c8a8adc145d7`), so the round-start registry is provably the base registry.
3. **Witness-strength caveat (not a counter defect): `census-before.txt` cannot witness the C2 row-count literal.** `validate` mode prints findings/warnings only; it emits no row count. Evidence: the E6 mutant (126 rows) reproduces the frozen artifact's output exactly. Consequently the C2 K3 sub-literal "registry row count 127 → 132" is witnessed by `census/round-26/records/c2-before.tsv` (`registry_rows=127`) and `c2-after.tsv` (`registry_rows=132`) — not by `census-before.txt`. Both receipts are correct and independently corroborated (Finding 5). Recommendation for the L1 (integrator seat, no prereg change implied): when the round's "census before/after" pair is cited, cite the counter receipt for the count and `census-before.txt` only for the finding set. **[INFERENCE]** — the frozen file's 35 lines are what `validate` emits; nothing in it was ever intended to encode a count (the file was produced by the same CLI at the freeze commit), so this is a gap in the witness, not a defect in a frozen counter. No kill rule of C1/C2/C3 is affected by it.
4. **All six manual CORPUS.md census categories re-derive clean at the frozen rev** (`89e0fceeefcf28db313c94120be6d25e03c60094`): rows 127; malformed 0; tier `A=120 B=5 C=2`; status `mined=103 queued=15 rejected=9`; duplicate ids none; enum/tier-inflation violations none; mined `used-by` paths missing none (112 path tokens over 103 mined rows, all resolving on disk). NF distribution is uniformly 13 for all 127 rows and no escaped `\|` appears in the file, so the C2 kill-rule clauses "malformed 0 / duplicate ids none / enum violations none / mined used-by missing 0" hold at the round-start state. [CORPUS.md:136, verbatim: `malformed rows — 11 columns means NF=13; must print 0`]
5. **C2 base literals are corroborated.** Rows at the frozen rev and at the lane base = 127 (both `git show`-derived); rows at tip = 132; `grounded_f1` 0 → 2 per `c2-before.tsv`/`c2-after.tsv`. At the frozen rev `corpus/knowledge/` holds 15 entries including `git-auto-maintenance-prunes-worktrees.md`, which does **not** carry `ground: F1` — consistent with `grounded_f1=0` at base and with C2's K1 base literal of 0.
6. **The C2 append introduced no new validate findings.** The tip's lane validate output is byte-identical to the round-start one, so rows S128–S132 (added between `89e0fccc…` and tip) raised neither an E-code nor a new W04 duplicate-URL-across-scope warning. Independently: tip malformed 0, dup ids none, enum violations none, mined used-by missing none.
7. **Fleet is clean at census level.** Fleet-wide `validate` exit 0 with zero `E##` lines and 331 W04 warnings; every lane ends `ok`. No-harm datum for the round.
8. **Bounded-scope compliance.** Only read operations outside the lane's own report directory: `git log/show/diff/rev-parse/cat-file/ls-tree/hash-object/merge-base/status` (read-only) on `/home/vgpnk/Projects/shokunin/souji-shokunin`, and read-only executions of `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`. No `git add/commit/push/stash/checkout/reset`, no `jj` mutation, no `rm`/`mv` outside `/var/tmp/souji-r26-ScoutCensusBefore/`, no signal sent, no write to `/home/vgpnk/Projects/shokuknow`, no access to the fleet `.scratch/`, `.ufo/state/`, `watchdog.log`, `MANIFEST.json`, `census/operator-sweep-*`, or any sibling lane repo. All scratch removed at the end of the run.

## Attack log
Not an attack item — read-only census re-derivation (scout seat). Findings 1–2 are clean confirmations; Finding 3 is a witness-strength observation reported upward to the L1 integrator without any predicate, target, case-set or axis change. No counter is proposed for change.
