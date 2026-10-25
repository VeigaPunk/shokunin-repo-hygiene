STATUS: PARTIAL

Critic seat `L1Souji22.CritC1Predicate`. Attacked C1's frozen predicate, not the
task owner. Read-only; wrote only this report and
`.ufo/waves/round-22/attempt2/w1/evidence/CritC1Predicate.md`. No installs, no
tool changes; instrument digest `58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2`
(14845 B) matches the digest peers MutPath/MutDigest pinned.

Headline: the arithmetic target is reached (`mismatches=0` at the tip) but
**three of the four questions fail**. The instrument cannot distinguish a
truth-preserving repair from a dodge, and one of the three landed repairs
satisfies none of the preregistration's own three permitted branches.

Tip movement to note: the lane advanced three times during this review —
`2a130b4` → `3216c19` (fills the placeholders `BODYCOUNT/RESN/SKN` that `2a130b4`
left in SCORECARD L14) → `5ff5041` → `d6a75ba`. Results are reported at
`4edb25d` (base) and `3216c19`; E10 re-measures at `d6a75ba`, where the counter
now reads **58**, not the 56 the artifact quotes. Every finding below still holds
at `d6a75ba`: L14 still says "the same 56 assertions", L3 still absolutises
`AXES.md`, L83 still names the absent obsidian probe, and both non-table class-B
tokens are still counted. A report that cites `2a130b4` as the final tip also
cites a revision whose calibration cell carried unfilled template text.

---

## Q1 — reachable by a do-nothing control? **holds**

No passthrough. Measured, not inferred:

```
--rev 4edb25d --format counts  -> assertions=56 resolved=53 skipped=33 mismatches=3   rc=1
```

and all three mismatches are genuine absent targets at base
(`git cat-file -e 4edb25d:<p>` → ABSENT for `AXES.md`, `reason-after.txt`,
`.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`; `git log --all -- AXES.md`
is empty, so `AXES.md` was never tracked in this lane). The frozen do-nothing
control therefore scores M>0 and the claim is **not** void.

Bounded caveat (not a failure of Q1 as frozen, but an uncontrolled second axis):
the do-nothing control freezes *SCORECARD bytes only*. The instrument is a
mutable file **inside the measured repo** and the counter contract does not pin
its digest; and `read_declaration` silently falls back to the worktree when the
named file is not tracked at `--rev`:

```
--rev 4edb25d --file census/round-22/attempt2/declared-evidence-before.tsv
  -> assertions=56 resolved=56 skipped=0 mismatches=0
```
That file is ABSENT at `4edb25d` (`git cat-file -e` fails) — the tool read
worktree bytes and reported them as the named revision. So the do-nothing
control covers SCORECARD, not the instrument, and not the provenance of the file
it is told to read.

## Q2 — does the enum enumerate the set it claims? **fails**

**A real assertion it provably misses** — base SCORECARD L14, final cell:

```
changed runner4f83fd222ffbd8825340221a8c426550ef891191 (unchanged bytes); ...
final oracle258 at473e98a498dbdb7315604251ab5a19a0823e7818
```

`HEX_B_RE`'s lookbehind `(?<![A-Za-z0-9_.-])` blocks both 40-hex revision tokens
because they are glued to `runner` and `at`. Neither enters N; neither even
enters S. Falsification (probe 01): replacing `473e98a…` with a dangling
`deadbeefdeadbeefdeadbeefdeadbeefdeadbeef` leaves the counter **byte-identical**
(`N=56 R=53 S=33 M=3`). Today both tokens resolve, so the miss is latent, not
live — but the scan is unreported either way.

Second miss, structural: class C requires digest and path **in the same cell**,
while SCORECARD puts evidence paths in the left column and measurements in the
right. Class C contributes **zero** assertions at both ends
(`Counter({'A':50,'B':6})` base, `Counter({'A':51,'B':5})` head; no 64-hex token
exists in the file). The claim's third kind — "sha256 digests" — is vacuously
satisfied: a wrong digest in a second cell is skipped and the run exits 0
(probe 12).

Third miss (latent): `corpus/lessons/round-{6..11}.md` is skipped because brace
ranges are outside `GLOB_RE`; six path assertions are invisible. All six exist,
so no live mismatch — the hole is open, not tripped.

**A real assertion it provably over-counts** — class B on non-table lines:

```
HEAD L38  pipes=0  (base L33) `... reproduced at its named measured revision `6f8ee0f``
HEAD L114 pipes=0  `Preregistration `29c1f7e8df849be8ee1b2d62d2351e17ec9d21a8``
```

`cells_of()` returns `[line]` when `line.count("|") < 2`, so every prose
paragraph and bullet becomes a "cell". The frozen enum says class B is a token
"inside a table cell". L114 has no revision-context word at all and matches only
on the word "measured" in running prose. Two of the 56 are outside the enum,
while the preregistration states "the enum, nothing else counts" — so
`assertions=56` is not the enum's set.

Related and worse for the claim's wording: class B tests only
`git cat-file -e <tok>^{commit}`. Rewriting `base60/214` → `base999/999`, or
`positive20/20` → `positive0/0`, leaves all counters identical (probes 21/22). A
false measurement attributed to a real commit is not an assertion this enum can
see, although the claim says revision tokens are "re-derived from committed
bytes".

## Q3 — can the repair game the counter? **fails** (demonstrated, and used)

Four rewrites, all information-preserving in the document, all measured on the
real base bytes:

| rewrite | counter | what it proves |
|---|---|---|
| `` `reason-after.txt` `` → `reason-after.txt` | N 56→55, M 3→2, S 33 | de-backtick: assertion vanishes, token still present |
| `` `AXES.md` `` → `` `/home/vgpnk/Projects/shokunin/AXES.md` `` | N 55, S 34, M 2 | mismatch converted into a **skip** |
| `b912328d…` → `rev-b912328d…` | N 55, R 52 | prefix makes a token stop being "bare" |
| `base60/214` → `base999/999` | unchanged | false measurement with a valid commit |

The landed repair used two of these. Multiset diff base→head:

```
REMOVED: AXES.md | 41553adb… | b912328d… | reason-after.txt | .ufo/scopes/…/obsidian-cli-probe.md
ADDED:   declared-evidence-before.tsv x2 | 4edb25dfe… | round-22-verifier-spotcheck.md | census/round-21/reason-after.txt
```

N is 56 at both ends, so **"repaired to 0 mismatches over the same 56
assertions" (head SCORECARD L14) is false**: five base tokens were retired and
six added, and the counter prints only the total, so the sentence is
self-certifying. Of the three base mismatches:

* `reason-after.txt` → `census/round-21/reason-after.txt` — **genuine repair**.
* `.ufo/…/obsidian-cli-probe.md` — still named at head L83, unbackticked; target
  still absent from disk and tree. Letter-conforming ("drops the evidence role")
  but the drop is unreceipted (`ls` claim with no committed bytes).
* `AXES.md` — head L3 `` `/home/vgpnk/Projects/shokunin/AXES.md` `` **still
  presents a path as the axes authority**, names no revision, supplies no
  receipt. It satisfies **none** of the three branches the preregistration
  itself allows (names a revision holding the path / drops the evidence role /
  supplies the missing committed receipt). This repair is non-conforming to its
  own target text, not merely unproven.

**Falsifiable boundary the report must carry** (smallest sufficient set):

1. **Pin the instrument**: the counter line must carry
   `sha256(tools/souji-declared-evidence.py)` (here `58ddbfef…`) and the report
   must state it. Unpinned, the measured file is inside the measured repo.
2. **Pin the set, not N**: before and after receipts in `--format tsv`, with
   `set_after(token,cls) ⊇ set_before(token,cls)`; every removed token listed in
   the report with its replacement and a reason. Without this, equal N is a
   coin-flip of additions and deletions — and at head it is exactly that.
3. **Close the evasion list** as tool verdicts, never `skipped`: `de-backticked`,
   `absolutised`, `prefixed`/`suffixed so no longer bare`, `shortened below 7`,
   `moved out of the table`. Each must appear as `mismatch:evaded`.
4. **Downgrade measurements**: any cell whose prose carries a measured number
   plus a revision token is `unverifiable` unless re-derived — existence of a
   commit is not evidence of the number attributed to it.
5. **Repair the false sentence** in SCORECARD L14: 56 assertions at each end,
   five retired and six added; of three base mismatches, one resolved and two
   converted to non-assertions.

**Fifth dodge, live and self-evident — the counter's own output is unscanned.**
The quoted receipt `` `assertions=56 resolved=56 skipped=36 mismatches=0` `` in
L14 is neither a path nor a bare hex, so it lands in `skipped` and is never
checked. At `d6a75ba` the same command on the same file returns **58**. So the
C1 row's headline number drifted by 2 at the tip and the instrument that exists
to catch exactly that reports `mismatches=0`. It was accurate at `2a130b4` and
`3216c19`, so this is drift rather than a false commit; but the row is keyed to
"`--rev <final tip>`" and the tip moved three times in twenty minutes. Either
commit the counts receipt as a digest-pinned file, or add:

6. **class D**: a backticked
   `assertions=N resolved=R skipped=S mismatches=M` in a cell must equal the
   tool's output at the cell's named revision. Without it, the audit's own
   headline is a declared evidence the audit cannot falsify.

## Q4 — does `skipped` let a mismatch escape? **fails**

Yes, and the escape is unauditable: `run()` emits TSV rows for classified
assertions only, so `skipped` is a bare integer with no per-token ledger — the
receipt cannot show *what* was skipped or *why*, and "N+S enumerates every
candidate token" is therefore not falsifiable from the output.

Wrong-reason skips, executed:

* **Two paths → wrong digest skipped**: `assertions=2 resolved=2 skipped=1
  mismatches=0`, exit 0, with a 64-hex of all zeros in the cell. A wrong digest
  escapes precisely because the cell is ambiguous.
* **Path and digest in different cells**: `assertions=1 resolved=1 skipped=1
  mismatches=0`, exit 0. This is SCORECARD's actual layout.
* **Command span swallows a real path**: `` `git show 41553adb…:census/round-21/run-acceptance.py` ``
  is skipped as a whole; the path inside is never asserted (it happens to exist).
  Its revision token resolved only incidentally, via `census/round-21/` in the
  same cell — a different cell layout and it would have vanished.
* **The audit's own receipt is skipped**: `` `assertions=56 resolved=56 skipped=36 mismatches=0` ``
  is skipped as a non-path, non-hex span, which is how it stayed at 56 while the
  file reached 58 (E10). The skip reason is shape-based, but the token is a
  declared-evidence assertion about the very file being audited.
* `skipped:unknown-class` is unreachable, so no assertion can ever be reported
  as skipped-with-reason in the TSV.

## Impacted axes

* **calibration** (primary, the claimed axis): the M=0 reading is arithmetically
  true and evidentially weak. One of three repairs is non-conforming (AXES), the
  conservation sentence is false, and 5 of the 56 base assertions were retired
  without a receipt (the tip now enumerates 58, so even the two totals no longer
  agree). If closure takes `mismatches=0` as the axis move 7→8, it
  credits a dodge. My verdict: the move is **not** supported; C1 holds only as a
  bounded demonstration that the instrument discriminates its own five fixtures.
* **coverage**: class C is empty and structurally unreachable on this file's
  layout; brace-range and command-embedded paths are invisible. Three of the
  claim's stated assertion kinds are under-enumerated, and the class-B
  over-count means N is not the frozen enum's count either way.
* **operability**: unpinned instrument, worktree fallback that reports a foreign
  revision, no itemised skip ledger. The receipt is not reproducible from the
  document alone, and the quoted receipt itself has already drifted by 2.

## Smallest safe correction

1. `--format tsv` before/after with a set-conservation gate (boundary 2 above);
   a removed token is `mismatch:evaded` unless the report lists it as retired.
2. A pre-pass that finds path/hex **shapes in raw text regardless of backticks**,
   and pairs a digest with a path **per row** when exactly one of each exists.
   That single change closes the de-backtick dodge, the class-C blind spot, the
   `git show <rev>:<path>` miss and the boundary-blocked token miss.
3. Emit skipped rows `line \t token \t reason` from a closed reason set.
4. Pin the tool digest in the counter line and in SCORECARD L14's evidence cell.
5. Rewrite L14's conservation clause and re-state AXES.md as `unverifiable`
   (host path, no lane revision) rather than resolved-by-relocation.

Nothing here requires a new claim, a new revision, or deletion authority; items
1–3 are edits to the instrument the round already added, item 5 is one sentence.

## Executed vs inferred

Executed: E1–E10 in the evidence file (counters at base/`2a130b4`/`3216c19`/`d6a75ba`,
`--selftest` 8/8, multiset diff, twelve synthetic probes against real base bytes,
class-B line audit, class-C probes, provenance fallback, `git cat-file` absence
checks, `ls` of the AXES host file, tip ancestry and drift). Inferred (marked in
place): that a wrong revision token inside `git show <rev>:<path>` *would* vanish
if its cell lacked a census path — the mechanism is shown, the instance is latent.
