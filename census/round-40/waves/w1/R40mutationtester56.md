# R40mutationtester56 — attack on the frozen r40 C2 operability claim

Seat: `R40mutationtester56` (role mutation-tester, axis **operability**).
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Target claim: `census/round-40/preregistration.txt` §C2 (sha256 of the C2 paragraph:
`3ae6b4a973e6b5fcf06d3bd4e2a72fad34f4221ada1aae92a5f7adf27cdd0bd5`, 527 bytes).

Verdict in one line: **the frozen C2 predicate is not yet falsifiable, because the r40 leg's
*observation channel* — how it learns which refusal class the tool actually raises — is
path-contaminable, and a contaminating path turns a genuine docstring/runtime disagreement
into a PASS. The r40 leg must pin the observation channel before it can claim it "verifies
all observed class/trigger pairs".**

---

## 0. Named edge case (item 56's distinct scope)

Every other seat in this wave attacks the C2 leg's **analyzer** (how the docstring is parsed
or joined). This seat attacks the leg's **observation channel** — the step that decides
*which class the tool actually raised at runtime*, which is the input the analyzer's output
is compared against.

**The edge case, named: `classify()` is a priority-ordered substring scan over
`stdout+stderr`, and the tool echoes the record path into that text. The observed class is
therefore a function of the probe path string, not only of the audited bytes.**

Concrete consequence, measured below: with a probe path containing the literal token
`RECORD-MISSING`, the missing-path probe (which the tool really answers `RECORD-MALFORMED`)
is classified as `RECORD-MISSING`; the *observed class set collapses from two pairs to one*,
and the "missing" conjunct becomes a tautology because the stored docstring line begins with
the class token itself. A mutant that removes the `RECORD-MALFORMED` entry's `missing (ENOENT)`
trigger — a real docstring/runtime disagreement — then reads `LEG L4 PASS` instead of
`LEG L4 FAIL`.

This is the falsifier the frozen predicate does not currently exclude.

---

## 1. The frozen claim, quoted exactly

From `census/round-40/preregistration.txt` §C2:

> Predicate: r40 L4 docstring analyzer joins wrapped continuation lines into one class entry
> and verifies all observed class/trigger pairs in the frozen list; a synthetic wrapped-trigger
> probe is detected while the r39 one-line analyzer misses it. Control: r39 `docstring_classes`
> extracts only the first class line. Kill if wrapped trigger is missed, or if any observed
> class mapping disagrees with runtime behavior. Measurement: r40 counter receipt comparing base
> and candidate bytes.

Three load-bearing words are **not** pinned by the text: *joins* (where does a class entry
end?), *observed* (how is the runtime class learned?), *frozen list* (which pairs, and where
does the list live?). Sections 3–5 below measure each.

---

## 2. Committed r39 artifacts used (all at base rev `0242085909fb6a4ee041c5443d76316ac6d59d4b`)

| artifact | sha256 |
|---|---|
| `census/round-39/c2-counter.py` | `732b1e425a6ddc37a9632431269c9c679b32cbe18a22cb35b5b4f4cec151ee11` |
| `tools/souji-worktree-drift.py` | `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76` |
| `census/round-39/preregistration.txt` | `25b430a41201607877fd376d9da62780792a79f1d376074dae41071cffcc777a` |
| `census/round-39/records/c2-after.txt` | `bf5b5ec0a599b136a9ebbbebe293e639175f7dac83152b1688a66700be9ab1c7` |
| `census/round-39/waves/w1/W1SimpC2.md` (the committed frozen pair list) | `b40a398d78d9c16d4e466238d52ea14ece118e5f234afa7cd31ee3e5952da288` |

The frozen class/trigger list is **committed**, in `census/round-39/waves/w1/W1SimpC2.md:193-199`:

```
RECORD_CLASSES = ("RECORD-MISSING", "RECORD-MALFORMED", "RECORD-EMPTY", "RECORD-OUTSIDE-ROOT")
DOC_CLASSES = ("RECORD-MISSING", "RECORD-MALFORMED")
```
with the grounding "the drift tool's docstring maps `RECORD-MISSING` to EACCES/ELOOP,
`RECORD-MALFORMED` to ENOENT/non-regular/schema/TOTAL violations, `RECORD-EMPTY` to 'no REPO
rows' and `RECORD-OUTSIDE-ROOT` to a row escaping root". This file is listed in
`census/round-39/waves/manifest.sha256` (same hash), so the pair list is verifiable committed
bytes, not wave-local hearsay.

**Note on scope of "observed":** L4's two probes (absent path → ENOENT; mode-0 path → EACCES)
observe exactly `RECORD-MALFORMED` and `RECORD-MISSING`. Measured directly:

```
probe absent  -> RECORD-MALFORMED
probe locked  -> RECORD-MISSING
```
`RECORD-EMPTY` and `RECORD-OUTSIDE-ROOT` are **not** reachable by these probes (they need a
parsed record). So "all observed class/trigger pairs" is, for the r39 probe pair, **two** of
the four frozen pairs. The r40 text must say which probes it runs; if it keeps the two r39
probes it can only ever verify two pairs, and the other two frozen pairs are unverifiable
by the leg as specified. This is a *scoping* limit, not yet a defect — but it means the r40
leg's claim scope is not derivable from the frozen text.

---

## 3. Baseline: the r39 counter reproduces its own receipts, exactly

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ python3 -B census/round-39/c2-counter.py --root . \
    --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --scratch /fast/scratch/hyaku/souji-r40/R40mutationtester56/scratch1
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
rc=0
```

Byte-identical to `census/round-39/records/c2-after.txt`. Control at the r39 base revision
reproduces `pass=2 fail=4` byte-identically to `census/round-39/records/c2-before.txt`:

```
LEG L1 FAIL ... LEG L2 FAIL ... LEG L3 PASS ... LEG L4 FAIL ... LEG L5 FAIL ... LEG L6 PASS
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=e555d8281484
rc=1
```

**The instrument is sound at its own bytes.** Every mutant below is therefore a true kill/survive
measurement, not a baseline failure.

---

## 4. THE FALSIFIER — the observation channel is path-contaminable

### 4.1 Mechanism

`census/round-39/c2-counter.py:125-131`:

```python
def classify(proc):
    out = (proc.stdout + proc.stderr).replace("\n", " ")
    for cls in ("RECORD-MISSING", "RECORD-MALFORMED", "RECORD-EMPTY", "RECORD-OUTSIDE-ROOT"):
        if cls in out:
            return cls
    return "NO-CLASS"
```

First-match substring scan, `RECORD-MISSING` **first** in the priority order. The tool's
refusal message embeds the record path:

`tools/souji-worktree-drift.py:135` — `raise Refusal("RECORD-MALFORMED: %s is not a regular file" % path)`

So if the record path itself contains the literal string `RECORD-MISSING`, the scan matches
`RECORD-MISSING` *before* the true `RECORD-MALFORMED`. Measured directly against the
committed tool blob:

```
plain                classify=RECORD-MALFORMED   true_class=RECORD-MALFORMED
RECORD-MISSING       classify=RECORD-MISSING     true_class=RECORD-MALFORMED   <-- FLIP
xRECORD-MISSINGy     classify=RECORD-MISSING     true_class=RECORD-MALFORMED   <-- FLIP
RECORD-MALFORMED     classify=RECORD-MALFORMED   true_class=RECORD-MALFORMED
```

Raw output for the flipped case (the path is echoed verbatim):

```
REFUSAL RECORD-MALFORMED: .../RECORD-MISSING/absent.tsv is not a regular file
```

The observed class set then **collapses**:

```
== clean    observed class set : ['RECORD-MALFORMED', 'RECORD-MISSING']  (size 2)
== contam   observed class set : ['RECORD-MISSING']                     (size 1)
```

And the `"missing"` conjunct becomes a **tautology**: the stored docstring line for
`RECORD-MISSING` begins with the class token, so `"missing" in line.lower()` is True for a
reason that has nothing to do with the missing-path trigger.

### 4.2 The consequence, through the committed counter

`--scratch` is the *only* thing that varies between the two arms. The audited bytes are
identical.

```
$ python3 -B census/round-39/c2-counter.py --root . --rev <rev> \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <clean>
$ ... --scratch <.../RECORD-MISSING>
```

### 4.3 The mutant battery (git fixture, toplevel asserted before every commit)

Fixture: `mktemp`-style scratch clone at
`/fast/scratch/hyaku/souji-r40/R40mutationtester56/fixture/repo`, every `git` call `-C` that
exact root, `git rev-parse --show-toplevel` asserted to equal it before each commit.
Script: `final_verify.sh` (scratch). Mutants are committed on detached HEADs off the base rev.

| mutant | what it changes | tool sha256 |
|---|---|---|
| **PRISTINE** | none (base rev `0242085`) | `e48ed08e672824e2` |
| **M4** | `RECORD-MALFORMED` entry drops `a missing (ENOENT)` — the tool still raises `RECORD-MALFORMED` for ENOENT, so the docstring now disagrees with runtime | `5c06737566d0ae93` |
| **M2** | `EACCES` moved out of the `RECORD-MISSING` entry and into the `RECORD-MALFORMED` entry (mis-attribution) | `a0435b601b001a43` |
| **W1** | `EACCES` moved onto the *continuation* line of `RECORD-MISSING` (the synthetic wrapped-trigger probe the r40 predicate names) | `73dbe4b0c38b8bb3` |

### 4.4 Result table — committed r39 counter, base-rev `ed30b7f` (so `old_maps=False` is live)

```
rev      | sha256           | CLEAN scratch                                       | CONTAMINATED scratch
---------|------------------|-----------------------------------------------------|-------------------------------------------------
PRISTINE | e48ed08e672824e2 | PASS missing=RECORD-MALFORMED locked=RECORD-MISSING   | PASS missing=RECORD-MISSING locked=RECORD-MISSING
         |                  |      new_maps=True old_maps=False                    |      new_maps=True old_maps=False
M4       | 5c06737566d0ae93 | FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING   | PASS missing=RECORD-MISSING locked=RECORD-MISSING
         |                  |      new_maps=False old_maps=False                   |      new_maps=True old_maps=False      <-- SURVIVES
M2       | a0435b601b001a43 | FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING   | FAIL missing=RECORD-MISSING locked=RECORD-MISSING
         |                  |      new_maps=False old_maps=False                   |      new_maps=False old_maps=False
W1       | 73dbe4b0c38b8bb3 | FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING   | FAIL missing=RECORD-MISSING locked=RECORD-MISSING
         |                  |      new_maps=False old_maps=False                   |      new_maps=False old_maps=False
```

Full receipts (`legs=6 pass=6` vs `legs=6 pass=5 fail=1`):
- M4 clean: `SUMMARY legs=6 pass=5 fail=1 harm=0 tool_sha=59f1e57d7af0/5c06737566d0`
- M4 contaminated: `SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/5c06737566d0`

### 4.5 What this falsifies, precisely

**M4 is killed under a clean scratch and survives under a contaminated scratch, with the
audited bytes held byte-identical (`5c06737566d0ae93` in both arms).**

M4 is exactly the defect class the r40 C2 claim exists to police: the docstring's
`RECORD-MALFORMED` entry no longer names the ENOENT/missing trigger that the code raises
(`tools/souji-worktree-drift.py:135`). Under the r39 L4 rule this is caught
(`new_maps=False`). Under a contaminating probe path it is not.

So the r40 predicate's kill clause — "Kill if … any observed class mapping disagrees with
runtime behavior" — **cannot be reached** whenever the observation channel is contaminated,
because the r40 leg inherits the same `classify()`-shaped observation. The r40 text says
"verifies all observed class/trigger pairs"; it does not say *how* the pairs are observed,
and the inherited method is not sound.

Note the direction of the failure is safe-ish for the base receipt (pristine bytes still PASS
either way) but **unsafe for mutant discrimination**, which is precisely what the round needs
in order to claim the join actually buys something.

### 4.6 Is this reachable in practice?

Yes, and the r40 text makes it *more* reachable, not less. Two facts:

1. `census/round-39/preregistration.txt` (r39) §"Scratch root" and the r40 prereg's closing
   line — "All counters must accept explicit scratch paths and avoid hardcoded `/tmp`" —
   **require** the r40 counter to take an explicit `--scratch` from the caller. The r39 counter
   already does (`--scratch`, `census/round-39/c2-counter.py:162`), and it creates its
   `base_scratch` under it (`census/round-39/c2-counter.py:172`) and uses that directory as the
   probe path, so the *probe path* is inside the caller-chosen scratch root.
   A caller who names a scratch root containing a class token flips the observation.
2. The tool's own message text is caller-influenced for any path the tool is pointed at: the
   `--record` argument is echoed into the refusal. A record path under a directory named after
   a class token is enough.

This is not a hypothetical: the whole lane's scratch convention is
`/fast/scratch/hyaku/souji-r40/<seat-name>`, and seat names are free-form.

### 4.7 The bounded fix the r40 leg should adopt (for the L1 to consider)

Pin the observation to the tool's *refusal class token at the start of the refusal line*,
not to a substring of the whole output. Concretely, the class is always the literal after
`"REFUSAL "` in the tool's stderr (`REFUSAL RECORD-MALFORMED: …`, `REFUSAL RECORD-MISSING: …`),
so an anchored match on that prefix removes the path echo from the class signal entirely.
A second, independent belt: strip the class token from the docstring entry before testing
the trigger word, so `"missing"` is not satisfied by the entry's own leading
`RECORD-MISSING`. My scratch prototype does both (§5) and passes both mutants.

---

## 5. A joined analyzer is *not* sufficient on its own — the join boundary is load-bearing

The r40 predicate names "joins wrapped continuation lines into one class entry". The word
*joins* does not say **where a class entry ends**, and the two natural readings disagree on a
mutant.

Scratch prototype `r40_leg.py` (NOT a lane file) implements the r40 design as written:
a joined docstring map, a frozen pair list, and the trigger search performed on the entry
body **with the class tokens stripped** (so the `"missing"` tautology of §4.1 cannot fire).

```
=== bounded join (entry ends at the next class line) ===
PRISTINE | CLEAN: VERDICT joined-leg PASS   | CONTAMINATED: VERDICT joined-leg PASS
M4       | CLEAN: VERDICT joined-leg FAIL   | CONTAMINATED: VERDICT joined-leg FAIL
M2       | CLEAN: VERDICT joined-leg FAIL   | CONTAMINATED: VERDICT joined-leg FAIL
W1       | CLEAN: VERDICT joined-leg PASS   | CONTAMINATED: VERDICT joined-leg PASS
```

Reading the table:

- **W1 (wrapped trigger) — the r40 predicate's own named probe — is detected by the bounded
  join and missed by the r39 one-line analyzer.** This part of the claim is *sound*. The r39
  one-line analyzer on W1 returns `False` for the rule (measured directly against the
  committed `docstring_classes`), while the committed r39 counter reads `LEG L4 FAIL
  new_maps=False` on W1, exactly as the predicate's control describes.
- **M2 (mis-attribution) — killed by the bounded join.** The bounded join stops the
  `RECORD-MISSING` entry at the next class line, so the `EACCES` word sitting under
  `RECORD-MALFORMED` cannot be credited to `RECORD-MISSING`.

Now the alternative reading of the same words:

```
=== unbounded join (each class entry absorbs every following docstring line) ===
M2       | CLEAN: VERDICT joined-leg PASS     <-- M2 SURVIVES
PRISTINE | CLEAN: VERDICT joined-leg PASS
```

**Under the unbounded reading, M2 survives.** The `RECORD-MISSING` entry absorbs the
`RECORD-MALFORMED` entry's text, so the `EACCES` word under `RECORD-MALFORMED` is credited to
`RECORD-MISSING` and the mis-attribution passes.

So the frozen text "joins wrapped continuation lines into one class entry" admits **both** a
join that kills M2 and one that lets M2 live, and the r40 predicate does not say which. If
the r40 implementation picks the unbounded reading, its "verifies all observed class/trigger
pairs" is vacuous for exactly the class of defect (a trigger named under the *wrong* class)
that the round's own r39 wave seat `W1RevC2Doc` already flagged as uncaught
(`.ufo/waves/round-39/w1/W1RevC2Doc.md:21-24`, "L4 vs mutant B (both class lines name both
triggers, contradictory) — **NOT CAUGHT**").

**This is the second, independent falsifier: the frozen C2 predicate does not pin the join
boundary, and one reading of its own words makes the leg blind to mis-attribution.**

---

## 6. Coverage note on the frozen pair list

`RECORD-EMPTY` ("no REPO rows") and `RECORD-OUTSIDE-ROOT` ("a record row … escapes --root")
are in the frozen list but are **not observable** by L4's two probes (measured, §2). They
*are* observable in principle by different probes:

- `RECORD-EMPTY`: a record file whose only non-comment line is `TOTAL` → the tool raises
  `RECORD-EMPTY` (`tools/souji-worktree-drift.py:168`).
- `RECORD-OUTSIDE-ROOT`: a record row resolving outside `--root` → raised at `:293` (name) and
  `:310` (gitdir).

If the r40 leg wants to claim "all observed class/trigger pairs in the frozen list" over all
four frozen pairs, it needs two more probes, and each probe is a *new* path that must also be
kept clear of class tokens — which the §4 fix (anchored `REFUSAL ` match) makes automatic.
The r39 wave seat `W1SimpC2` already named this asymmetry (`census/round-39/waves/w1/W1SimpC2.md:193-199`,
`:201-205`).

---

## 7. Bounded measurement plan for the r40 C2 leg (offered to the L1; nothing here is written to the lane)

Nothing in this section is implemented in the lane. It is the plan the evidence above implies.

1. **Pin the observation channel.** Match the class token on the refusal *prefix*
   (`REFUSAL <CLASS>:`) rather than a substring of `stdout+stderr`. Add a fixture case that
   names a probe path containing `RECORD-MISSING` and asserts the observed class is still
   `RECORD-MALFORMED`.
2. **Strip class tokens from the entry body** before searching for the trigger word, so the
   `"missing"` conjunct cannot be satisfied by the entry's own leading token.
3. **Pin the join boundary** in the prereg text: "a class entry ends at the next line whose
   stripped form starts with a known class token". Add the M2 mutant (trigger named under the
   wrong class) to the r40 battery and require it killed.
4. **Keep the W1 probe** (wrapped trigger): it is the r40 claim's own discriminator and it
   works — the r39 one-line analyzer misses it, the bounded join detects it.
5. **Add M4** (the trigger word removed from a class's own entry): it is the mutant the
   current r39 rule catches and a contaminating path silently un-catches.
6. **State the pair scope** in the receipt: which of the four frozen pairs the leg's probes
   actually observe, and that `RECORD-EMPTY` / `RECORD-OUTSIDE-ROOT` need their own probes if
   they are to be claimed.
7. **Require the receipt to print the scratch path** and the per-probe observed class, so a
   contaminating path is visible in the receipt rather than silently changing the verdict.

---

## 8. Commands actually run (all evidence above is reproducible from these)

```bash
# baseline + control (r39 counter, committed bytes)
cd /home/vgpnk/Projects/shokunin/souji-shokunin
python3 -B census/round-39/c2-counter.py --root . \
  --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <scratch1>
python3 -B census/round-39/c2-counter.py --root . \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <scratch2>

# the falsifier: identical audited bytes, only --scratch differs
python3 -B census/round-39/c2-counter.py --root . --rev <rev> \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <clean>
python3 -B census/round-39/c2-counter.py --root . --rev <rev> \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <.../RECORD-MISSING>

# git fixture (toplevel asserted before every commit)
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/souji-shokunin <fixture>/repo
git -C <fixture>/repo checkout --detach 0242085909fb6a4ee041c5443d76316ac6d59d4b
[ "$(git -C <fixture>/repo rev-parse --show-toplevel)" = "<fixture>/repo" ] || exit 1

# consolidated battery (scratch)
bash /fast/scratch/hyaku/souji-r40/R40mutationtester56/final_verify.sh
```

Scratch artifacts (all under `/fast/scratch/hyaku/souji-r40/R40mutationtester56/`, removed
before yield): `final_verify.sh`, `mutants.sh`, `mutants2.sh`, `mutants3.sh`, `mutants4.sh`,
`mutants5.sh`, `exp_c2.py`, `r40_leg.py`, `patch_*.py`, `fixture/repo`.

---

## 9. Restoration and scope evidence

- **Fixture restored byte-exactly.** `git -C <fixture>/repo status --porcelain=v1` → empty;
  fixture `HEAD` = `0242085909fb6a4ee041c5443d76316ac6d59d4b`; tool blob sha256 after
  restore = `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76`, identical to the
  pre-mutation value.
- **Lane repo untouched.** `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain=v1`
  → `?? census/round-40/` only (the round-40 prereg, which is the L1's own untracked file and
  was already present when this seat started — verified at 16:33 before any command of mine).
  `git rev-parse HEAD` → `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e` (unchanged).
- **No commits, no pushes, no `jj`/index mutation in the lane.** All commits were made in the
  scratch clone under `/fast/scratch/...`, on detached HEADs, with the toplevel asserted.
- **This seat wrote exactly one file in the lane**: this report
  (`.ufo/waves/round-40/w1/R40mutationtester56.md`). No production file, no counter, no
  fixture, no census byte was created or modified. Note `.ufo/waves/` is git-ignored
  (`.gitignore:1`), so this report is a wave artifact, not a tracked lane file — consistent
  with the r39 wave reports being captured under `census/round-39/waves/` by the L1 instead.
- **No tools installed.** No `pacman`, no `uv tool install`, no `~/.local/bin` writes.
  `sudo` was checked for availability only (`sudo -n true`) and never used.

---

## 10. Verdicts

| # | item | verdict |
|---|---|---|
| V1 | r39 C2 instrument at its own bytes | **SOUND** — reproduces `census/round-39/records/c2-after.txt` byte-identically (`legs=6 pass=6 fail=0 harm=0`, rc 0); control reproduces `c2-before.txt` (`pass=2 fail=4`, rc 1) |
| V2 | r40 C2 "joins wrapped continuation lines" — does a join detect the wrapped trigger? | **SUPPORTED** — W1 (EACCES on the continuation line) is missed by the committed r39 one-line analyzer and detected by a bounded join (`joined-leg PASS` vs r39 `LEG L4 FAIL new_maps=False`) |
| V3 | r40 C2 "verifies all observed class/trigger pairs" — is the observation channel sound? | **FALSIFIED as written** — the observed class is path-contaminable (§4). M4 (a real docstring/runtime disagreement) is killed under a clean scratch and **survives** under a scratch path containing the token `RECORD-MISSING`, with audited bytes held identical (`5c06737566d0ae93`). The observed pair set collapses 2 → 1 and the `"missing"` conjunct becomes a tautology |
| V4 | r40 C2 — is the join boundary pinned? | **NOT PINNED** — "joins wrapped continuation lines into one class entry" admits a bounded reading (M2 killed) and an unbounded reading (M2 **survives**). The r40 text must say where a class entry ends |
| V5 | r40 C2 — scope of "the frozen list" | **AMBIGUOUS** — the frozen list is committed (`census/round-39/waves/w1/W1SimpC2.md:193-199`), but L4's two probes observe only 2 of its 4 pairs; `RECORD-EMPTY` and `RECORD-OUTSIDE-ROOT` need their own probes to be claimable |
| V6 | Do the five consumer fixtures / the r39 record fixture detect the contamination? | **NO** — `r38-drift-record` 10/10, `r36-worktree-drift` 12/12, `r38-drift-write-envelope` 12/12 under both a clean and a contaminated work dir. The fixture arm cannot see this defect; only the counter's `classify()`-based observation can |

**Bottom line for the L1.** The r40 C2 claim is *directionally* right — a join really does buy
the wrapped-trigger detection the r39 one-line analyzer misses (V2, measured). But as frozen,
it is **not yet falsifiable**: it does not pin the join boundary (V4), it does not pin the
observation channel, and the inherited observation channel is path-contaminable so that a
genuine docstring/runtime disagreement can be made to read as a PASS (V3). Before the r40
counter receipt can carry this claim, the leg must (a) observe the class from the refusal
*prefix* rather than a substring of the whole output, (b) strip class tokens before testing
the trigger word, and (c) name the join boundary in the frozen text. With (a)–(c) the joined
leg kills M2 and M4, detects W1, and passes the pristine bytes — measured, in scratch, with
the fixture restored byte-exactly.

**Honest limits of this seat's own work.** (1) The r40 counter does not exist yet, so §5's
"r40-style joined leg" is a scratch prototype implementing the frozen words as written, not
the L1's implementation; a different (correctly pinned) implementation would not share these
defects. (2) The contamination is demonstrated for the *r39* counter and for one natural
r40 reading; whether the L1's r40 leg inherits it depends on code not yet written, which is
exactly why the prereg must pin it now, before the after-data. (3) No conclusion is offered
about whether the lane's *current* docstring is correct — that is the r39 C2 receipt's
already-closed business, and this seat does not reopen it.
