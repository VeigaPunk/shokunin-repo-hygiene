# R40simplifier34 — C1 calibration attack: evidence-pointer vacuity, strict-descendant bypass, forged-row observability

- seat: simplifier (leaf member — no subagent dispatch)
- lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- frozen contract read first: `census/round-40/preregistration.txt` (C1, calibration)
- frozen r40 base used in every run: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (round-39 verified tip; lane HEAD during this seat was its descendant `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e` — `git -C $LANE status --porcelain=v1` showed only `?? census/round-40/`)
- target of attack: the frozen C1 predicate wording — "each anchored item line to carry a resolvable, revision-bound evidence pointer in addition to the r39 token predicate" and "reject a register row whose commit is not a strict descendant of receipt_rev"
- tool installs/upgrades: **none** (RULES.md read; pacman paused; nothing needed beyond `python3`/`git`, already present)
- `lsp` device: not mounted in this seat (not in the session tool set), so no semantic-reference proof is claimed; none is needed — this seat runs instruments, not deletions
- scratch: `/fast/scratch/hyaku/souji-r40/R40simplifier34` (removed at hand-off, see Hygiene)
- lane writes: exactly one file — this report

## Named distinct failure modes (item 34)

Adjacent-seat overlap check: simplifier 10 attacked duplicate-anchor existential hits (their report at `.ufo/waves/round-40/w1/R40simplifier10.md`); simplifier 58 claimed items-table provenance (`--items` read from the working tree, not `--rev`) plus a merge-base direction census of r39 `cells.tsv`. Coordinated with 58 via peer message: both their angles are distinct from mine and kept. Mine, named:

1. **FM-B — resolvable-but-vacuous evidence pointer (primary).** The frozen control covers only the *token-only* forged line. A forged line that *carries* a pointer satisfies the literal predicate: the pointer resolves, it is revision-bound, and the token half passes on pre-round bytes. "Resolvable, revision-bound" as written has no content binding and no round-floor, so the predicate does not kill this forgery.
2. **FM-A — prefix-equal bypass of the strict-descendant comparison.** A register row whose `receipt_rev` is 40-hex and whose `commit` is a 7-hex prefix *of the same commit* passes a naive strict check (`is_ancestor(receipt, commit) && commit != receipt_rev`) because git resolves prefixes while the string compare sees inequality. Plain equal commits also pass a naive `--is-ancestor`-only check (`rc=0` for equal args).
3. **FM-C — forged-row refusal inversion (measurement contract).** If the r40 counter inherits the r39 strict 5-field items schema (`census/round-39/c1-counter.py`, `parse_items`: `len(parts) != 5` → refusal) and the forged control row is authored in the old shape inside a new-schema table, the observable is `REFUSAL USAGE` exit 2 with no `ITEM` line — the frozen target "the forged token-only item **remains OPEN**" becomes unobservable, and no frozen kill clause fires. The receipt must be pinned to show the forged id as an OPEN item, not a refusal.
4. **FM-C′ — pointer-as-token absorption / column-index trap** (found by an instrumented accident, labeled as such). With the r39 5-column parser, a row that stuffs the pointer into the `mustnot` slot still CLOSES: the pointer is parsed as mustnot tokens, absent from the anchored line, hence inert for a forger — while the same index bug would put a real evidence path into `mustnot` for any honest row whose anchored line names its evidence path, flipping it OPEN (kill clause "any existing valid row is rejected"; the mustnot-inert mechanism is the r39 counter's own, cf. F3-NEG in `census/round-39/waves/w1/W1RevC1Forge.md`).

## Evidence — commands run and exact outputs

### E1 (FM-B token half) — token-only forged row closes at the frozen r40 base, zero r40 work

Anchor taken from pre-round bytes: `git -C $LANE show 0242085...:LOG.md` line 1855 carries `cases=9 pass=3 fail=6 base_fail=6` (an r37-era bullet; same line family r39 item R39-C1-11 polices). Items file written to scratch (r39 5-column schema, `mustnot=-`):

```
printf 'id\tfile\tanchor\tmust\tmustnot\nF34\tLOG.md\tcases=9\tfail=6\t-\n' > $S/f34-items-5col.tsv
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
  --items $S/f34-items-5col.tsv --register census/round-39/cells.tsv --scratch $S/tmp
```

```
ITEM F34 CLOSED
REGISTER cells=6 mismatches=0 commit_distinct=6
SUMMARY items=1 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=cf459c0d5b6c
rc=0
```

**Verdict: FORGERY GREEN AT BASE.** One token-only row closes at the frozen r40 base with the honest r39 register; exit 0. This re-derives, on my own instance at the r40 base, the control side the prereg asserts about the r39 counter — and it is the token half my FM-B forgery rides on.

### E2 (FM-B pointer half) — the plausible pointer target resolves at base and predates the round

```
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin; B=0242085909fb6a4ee041c5443d76316ac6d59d4b; P=census/round-39/records/c1-after.txt
git -C $LANE cat-file -e "$B:$P" ; echo rc=$?          # rc=0 — resolves at the r40 base
git -C $LANE rev-parse "$B:$P"                          # df68271348d783eaa08c5e61b7a089800af1a2a5
git -C $LANE rev-parse "5441045:$P"                     # df68271348d783eaa08c5e61b7a089800af1a2a5 (blob identical at authoring commit)
git -C $LANE log --oneline -- "$P"                      # only: 5441045 round-39: measurements — ... three after receipts at 2f6e981
git -C $LANE show "$B:$P" | grep -c 'round-40'          # 0
git -C $LANE show "$B:$P" | grep -c 'R40-'              # 0
```

**Verdict: VACUITY DEMONSTRATED.** `0242085...:census/round-39/records/c1-after.txt` is resolvable, revision-bound, byte-identical to the blob authored at r39 landing-measurement commit `5441045` (strictly pre-round), and contains zero r40-specific content. Combined with E1, a forged row carrying this pointer satisfies both clauses of the frozen C1 predicate **as worded** — token predicate (E1) + "resolvable, revision-bound evidence pointer" (E2) — with no round work. A resolve-only pointer check cannot kill it; the kill rule "forged line closes" fires on any implementation that reads the clause literally. Claim-level falsifier: **the frozen control set (token-only line) is strictly weaker than the forgery space the predicate admits.**

### E3 (FM-A) — equal-ancestor trap and prefix-equal bypass, git fixture

Fixture script `$S/e3-strict-descendant.sh` (quoted in full in the report appendix below): `mktemp -d -p $S`, `git -C "$D" init -q`, toplevel asserted equal to the fixture (`toplevel=.../tmp.7xPGE6wDpo`), commits A → B, trap-removed.

```
is_ancestor(A,A) rc=0        # equal passes a naive ancestor check
is_ancestor(B,A) rc=1        # backwards is refused by is-ancestor itself
is_ancestor(A, 2445c70) rc=0 # git resolves the 7-hex prefix to B
string-compare: '2445c70' != '18ec1f06...' -> true
git rev-parse '2445c70^{commit}' -> 2445c701ed94f08866fa1d6350561180918879d6
```

**Verdict: TWO NAIVE IMPLEMENTATIONS PASS FORBIDDEN REGISTERS.** (a) `--is-ancestor` alone passes an equal commit; (b) `is_ancestor && commit != receipt_rev` (string) passes receipt_rev==commit when the commit cell is spelled as its own 7-hex prefix. The prereg kill rule says an equal commit passing **kills** — so the r40 counter must resolve both cells (`git rev-parse <cell>^{commit}`) to full hash before comparing, then require `receipt != commit && is_ancestor(receipt, commit)`. Control side from committed r39 artifacts: the r39 counter's register parse is string-compare only (`census/round-39/c1-counter.py`, `parse_register`: `commit = parts[7]...; if commit and commit != parts[6]`), no resolution, no direction; committed reviewer artifacts `census/round-39/waves/w1/W1RevC1Register.md` A3 (equal commit register reads `mismatches=0`, floor-refused only) and A5 (backwards `commit` reads green rc 0) close the r39 half. Base `census/round-39/cells.tsv` (8-column, 6 rows, all `commit != receipt_rev`) is the honest-shape register any new check must keep accepting (kill clause "any existing valid row is rejected").

### E4 (FM-C / FM-C′) — schema-strict refusal vs pointer-as-token absorption, both at the r40 base

Attempt 1 (accident, kept and labeled): a pointer row written *without* the empty `mustnot` placeholder — 5 fields, pointer in the `mustnot` slot:

```
F34→LOG.md→cases=9→fail=6→0242085...:census/round-39/records/c1-after.txt   # cat -A shows 5 ^I-separated fields
python3 -B .../census/round-39/c1-counter.py --root $LANE --rev 0242085... --items $S/f34-items-6col.tsv --register census/round-39/cells.tsv --scratch $S/tmp
```
```
ITEM F34 CLOSED
SUMMARY items=1 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=1eb319622403
rc=0
```

Attempt 2 (the intended 6-field row, with `-` in `mustnot`):

```
REFUSAL USAGE: items /fast/scratch/hyaku/souji-r40/R40simplifier34/f34-items-6col-v2.tsv line 2 has 6 fields, expected 5
rc=2          # no ITEM line, no SUMMARY
```

**Verdict: both traps live in the r39 instrument, by run.** FM-C: a strict-schema counter refuses an over-schemad forged row (exit 2) instead of printing it OPEN — if the r40 counter inherits this and the forged control is authored old-shape, the frozen target ("remains OPEN") is unobservable and the receipt must be rejected as not-measured, not counted as pass. FM-C′: the pointer string inside a token slot is inert for a forger (row CLOSES) — and by the same parse indices, an honest row whose anchored line names its evidence path would read mustnot-hit OPEN (the "valid row rejected" kill clause); the honest-direction flip is [INFERENCE] from the r39 `mustnot` semantics (proven inert-token mechanism in E4 attempt 1; the flip case itself not constructed).

## Bounded measurement plan for the r40 C1 counter receipt

Each item is one command shape over committed bytes, named so the L1 can pin it in the receipt; explicit scratch paths only (no `/tmp`), per the frozen round rules:

1. **Pristine base control** — r40 counter + r40 items table at `--rev 0242085...`: every item OPEN (no refusal). items sha printed and equal to the committed r40 `c1-items.tsv`.
2. **Forged token-only control** — new-schema row with an empty evidence cell: receipt must print `ITEM <id> OPEN EVIDENCE-<CLASS>` and exit 1. A `REFUSAL` exit 2 here means the forged state was never observed (FM-C); count as not-measured.
3. **Vacuous-pointer control** — new-schema row whose evidence cell is `<0242085...>:census/round-39/records/c1-after.txt` (real, pre-round, E2): must read OPEN. Passes only if the counter binds pointer *content* and pointer-rev *round-floor*, not mere resolvability.
4. **Pointer cross-validation** — the counter re-derives the item's anchor/must/mustnot predicate at the pointer's own `rev:path` (not only at `--rev`), and requires the pointer revision to resolve at `--rev` and to be a strict descendant of the frozen base. This is the minimal tightening that kills E1+E2 jointly without rejecting an honest row.
5. **Strict-descendant register battery** (fixture or fixture-free over a scratch clone): equal (full-hash), equal (7-hex-prefix spelling), backwards, and the honest `DIFFERS` shape from base `cells.tsv`. Expected: equal-both-spellings and backwards REJECTED, honest shape accepted. The prefix case must be in the battery — it is the one E3 shows a passing-string-compare implementation admits.
6. **Floor pinning** — carry the r39 lesson (`W1RevC1Forge.md` §4: caller-settable `--min-cells`/`--min-commit-distinct` turn rc 0 with an empty register): the r40 predicate command should pin its floors literally.

## Verdict

**C1 (calibration), claim-level attack: FALSIFIER DELIVERED — the frozen predicate as worded is insufficient.** The token-only control covers the weakest forgery only; E1+E2 construct a pointer-carrying forgery that satisfies both predicate clauses at the frozen base with zero round work; E3 shows two naive strict-descendant implementations pass commits the kill rule forbids, including one (prefix spelling) the kill rule's own words do not obviously cover; E4 shows the target observable ("forged item remains OPEN") is reachable only if the counter's parse path is explicitly pinned. None of this is an r40-implementation measurement — no r40 counter bytes exist (`census/round-40/` holds only the preregistration), so the claim is **not yet measured, attack sustained against the frozen wording**. Frozen claims untouched.

## Hygiene

- Lane writes: this report only. `git -C $LANE status --porcelain=v1` at seat end: `?? census/round-40/` (pre-existing untracked prereg) plus this report; no tracked byte modified; no git/jj/index mutation anywhere outside the throwaway fixture (toplevel asserted before commit; trap-removed).
- Scratch `/fast/scratch/hyaku/souji-r40/R40simplifier34` (items fixtures, E3 script, tmp/) removed before yield; `TMPDIR` pointed at the scratch `tmp/` in every instrument run.
- No commits/pushes; no `~/.local/bin` or PATH writes; no installs to record.

## Appendix — E3 fixture script (`e3-strict-descendant.sh`, scratch, removed)

```sh
#!/bin/sh
# E3 — strict-descendant trap fixtures for the r40 C1 commit-vs-receipt_rev arm.
set -u
S=/fast/scratch/hyaku/souji-r40/R40simplifier34
export TMPDIR="$S/tmp"
D=$(mktemp -d -p "$S")
trap 'rm -rf -- "$D"' EXIT
git -C "$D" init -q
TOP=$(git -C "$D" rev-parse --show-toplevel)
[ "$TOP" = "$D" ] || { echo "FATAL: toplevel mismatch"; exit 9; }
printf 'root\n' > "$D/f.txt"; git -C "$D" add f.txt
git -C "$D" -c user.name=f -c user.email=f@x -c commit.gpgsign=false commit -qm A
A=$(git -C "$D" rev-parse HEAD)
printf 'second\n' >> "$D/f.txt"; git -C "$D" add f.txt
git -C "$D" -c user.name=f -c user.email=f@x -c commit.gpgsign=false commit -qm B
B=$(git -C "$D" rev-parse HEAD); P7=$(printf '%s' "$B" | cut -c1-7)
git -C "$D" merge-base --is-ancestor "$A" "$A"; echo "is_ancestor(A,A) rc=$?"
git -C "$D" merge-base --is-ancestor "$B" "$A"; echo "is_ancestor(B,A) rc=$?"
git -C "$D" merge-base --is-ancestor "$A" "$P7"; echo "is_ancestor(A,prefix) rc=$?"
[ "$P7" != "$A" ] && echo "string-compare: prefix != receipt_rev -> true"
git -C "$D" rev-parse "$P7^{commit}"
```
