# R42w2reviewer07 — falsify S259 (Python `site`) and the round-42 sources census

Seat: reviewer, wave 2, round 42, lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Attack target: the S259 registry row (`corpus/SOURCES.md:213`) and its backing artefacts
(`census/round-42/sources/python-3-library-site.html`, `census/round-42/sources/SHA256SUMS`),
plus the round's claim that the C2 `patches=3/3` leg rests on S259.
Read-only: nothing under `census/`, `corpus/`, `tools/`, `tests/`, `SKILL.md` was written by this seat.
Scratch: `/fast/scratch/hyaku/souji-r42/R42w2reviewer07/` (removed before yield).
No tools installed or upgraded (none needed); `curl`, `python3`, `git` (read-only), `gawk`/`bash`
were the only binaries used, all pre-existing.

---

## 1. Verdict

**NARROW SCOPE** (not admit, not reject). S259 is byte-exact, correctly located, correctly quoted,
and genuinely load-bearing for C2 — but two of its scope statements reach past what the cited page
says, and the second half of the mechanism the C2 patch leg actually needs is not on this page at all.

Reason, in one line: the page grounds *that a `sitecustomize` import is attempted at interpreter
startup and that `-S` bounds it*; it does **not** ground *that `-S` suppresses the `sitecustomize`
import directly* (its `-S` sentence is about the `site` module), and it says **nothing** about
`PYTHONPATH` or `sys.path` search order — which is the channel the counter's patch leg uses.

Because `scope` is an immutable cell (CORPUS.md rule 2: only `status`, `recheck`, `used-by` change in
place; a correction is a new row whose `teaches` opens `supersedes S0NN —`), the narrowing **must be a
new row S260**, not an edit of S259. S259 stays as filed.

---

## 2. Evidence — the source bytes

### 2.1 Live fetch vs snapshot vs SHA256SUMS vs the committed blob

```
$ curl -sS -L --max-time 60 -o live-site.html https://docs.python.org/3/library/site.html ; echo "curl exit=$?"
curl exit=0
$ sha256sum live-site.html
620581fe5440952a9b62554526f6fe613b030b2c7a1521e1e57495f22e5d546a  live-site.html

$ sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/sources/python-3-library-site.html
620581fe5440952a9b62554526f6fe613b030b2c7a1521e1e57495f22e5d546a

$ cat census/round-42/sources/SHA256SUMS
620581fe5440952a9b62554526f6fe613b030b2c7a1521e1e57495f22e5d546a  python-3-library-site.html

$ git -C <lane> show 3105a63b23481fccf7df58e74d14a6681e0ea0c8:census/round-42/sources/python-3-library-site.html | sha256sum
620581fe5440952a9b62554526f6fe613b030b2c7a1521e1e57495f22e5d546a  -
```

**All four agree.** The live page fetched on 2026-10-28 is byte-identical to the L1's snapshot, to the
SHA256SUMS line, and to the blob committed at the tip. The row's anchor cell
("sha256 620581fe… (SHA256SUMS line matches)") is **true**.

### 2.2 Line numbers of the two quoted sentences in the snapshot

**Quoted sentence** ("an attempt is made to import a module named `sitecustomize`, …"), § `sitecustomize`:

```
$ sed -n '418p' …/python-3-library-site.html
<p>After these path manipulations, an attempt is made to import a module named
$ sed -n '419p' …/python-3-library-site.html
<code class="xref py py-mod docutils literal notranslate"><span class="pre">sitecustomize</span></code>, which can perform arbitrary site-specific customizations.
```

Section anchor `<section id="module-sitecustomize">` is at line 416, heading at 417.
→ the sentence spans **lines 418-419**. The row's anchor ("§ `sitecustomize`, snapshot lines 418-419")
and the lesson's Gate cell ("the sentence splits across two lines of the served HTML") are **true**.

**`-S` sentence** ("The automatic import can be suppressed using the interpreter's -S option."), § `site` introduction:

```
$ sed -n '227p' …/python-3-library-site.html
<p><strong>This module is automatically imported during initialization.</strong> The automatic
$ sed -n '228p' …/python-3-library-site.html
import can be suppressed using the interpreter’s <a …#cmdoption-S"><code …><span class="pre">-S</span></code></a> option.</p>
```

→ the `-S` sentence spans **lines 227-228**. The row's anchor is **true**.

### 2.3 Quote fidelity (rendered text vs raw HTML bytes)

The row's `teaches` cell is a bare quote of the rendered sentence:

> "an attempt is made to import a module named sitecustomize, which can perform arbitrary site-specific customizations."

De-markup test on the snapshot: **FOUND** verbatim (including the trailing period, which the page
has at line 419). In *raw HTML bytes* the string is **not** contiguous (the module name sits inside a
`<code>` tag), which is the same convention the neighbouring HTML rows already use (S255 `inspect.html`,
S256 `codecs.html`). Word count 16 ≤ 25 (contract rule 1). **No defect.**

---

## 3. Evidence — every S259 cell against CORPUS.md and the census rules

Row: `corpus/SOURCES.md:213`. Parsed cells (NF=13 ⇒ 11 columns, correct):

| cell | value | check | result |
|---|---|---|---|
| id | `S259` | `S` + 3 digits; next unused (S258 exists, S259 new, no reuse) | pass |
| source | `Python `site` — Site-specific configuration hook — https://docs.python.org/3/library/site.html` | title + canonical URL | pass |
| kind | `docs` | in enum | pass |
| tier | `A` | official upstream documentation, primary for this scope; not `community` | pass |
| scope | see §4 | must state the claim **and** its limits | **narrow — see §4** |
| anchor | § `site` intro lines 227-228; § `sitecustomize` lines 418-419; "Python 3.15.2 documentation"; sha256 | exact section/line + revision + digest; never a bare homepage | pass |
| teaches | the 16-word quote | one grounded learner benefit (bare quote; S255/S256 are the same shape) | pass (consistency note, F3) |
| status | `mined` | cited by ≥1 path in `used-by` — the lesson cites S259 at `corpus/lessons/round-42.md:27,30,165` | pass |
| opened | `2026-10-28` | ISO; equals this round's own access date (the L1 opened it 2026-10-28) | pass |
| recheck | `on-release` | valid symbolic cadence; matches the rolling `docs.python.org/3/` URL's cadence | pass (residual risk R1) |
| used-by | `corpus/lessons/round-42.md` | repo-relative, exists on disk → E11 clean | pass |

No `|` inside any cell; no bare homepage; nothing rewritten in an older row (see §5).

---

## 4. Findings

### F1 (medium) — the scope cell overstates what the `-S` sentence says

S259's scope: *"the automatic `sitecustomize` import attempted during interpreter startup, **and the
`-S` option that suppresses the automatic import**"*.

The page's `-S` sentence is about the **`site` module**, not about `sitecustomize`:

> "**This module** is automatically imported during initialization. The automatic import can be
> suppressed using the interpreter's -S option." (lines 227-228, `This module` = `site`)

The chain to `sitecustomize` is real but is **one step**: the page states the `sitecustomize` import
happens "**After these path manipulations**" (line 418) — i.e. inside `site`'s own processing — so
suppressing `site` suppresses the `sitecustomize` attempt. The row reads as if the page states the
suppression of the `sitecustomize` import directly. It does not.

**Fix (append-only):** a superseding row S260 whose scope reads, e.g., *"the automatic `sitecustomize`
import attempted during interpreter startup (lines 418-419), and the `-S` option that suppresses the
automatic import of the `site` module — and with it the `sitecustomize` attempt (lines 227-228, 418,
506)"*; `teaches` opens `supersedes S259 —`.

### F2 (medium) — the C2 patch leg's discovery channel is not on this page

S259's scope excludes "the contents of any particular `sitecustomize` module" and "the effect of `-I`
(not stated on this page)". Both exclusions are **true** — the page contains:

```
$ grep -c 'pre">-I<' … ; grep -ci 'isolated' … ; grep -ci 'pythonpath' …
0
0
0
```

(the page never mentions `-I`, isolated mode, or `PYTHONPATH`; it does mention `-s` 6× and `-S` 7×).

But the counter's patch leg does **not** use `site-packages`. `census/round-42/c2-counter.py`
(`run_selftest`, lines 337-340) writes `sitecustomize.py` into a temp dir and puts that dir on
`PYTHONPATH`:

```
337:        with open(os.path.join(pdir, "sitecustomize.py"), "w", encoding="utf-8") as handle:
338:            handle.write(SITECUSTOMIZE)
339:        e["PYTHONPATH"] = pdir
340:        e["SOUJI_R42_PATCH"] = patch
```

The page grounds the *startup import attempt*; the **`PYTHONPATH` → `sys.path` discovery** it relies on
is documented on a *different* page (`using/cmdline` / `sys.path` initialisation), and the souji
registry has **no row** for it:

```
$ grep -in 'using/cmdline\|PYTHONPATH\|sys\.path' corpus/SOURCES.md
(no row)
```

So the lesson's admitted-for cell — *"C2's `patches=3/3` leg: runtime patches are injected through a
`sitecustomize` module **on PYTHONPATH**"* — asserts a mechanism S259 does not carry. S259's own scope
cell is silent about the channel, which is the honest shape; the *lesson* is where the overreach sits.

**Fix (append-only):** either (a) S260's scope adds the discovery channel explicitly and a companion
row is opened for the `PYTHONPATH` / `sys.path` documentation, or (b) the lesson's admitted-for cell
is re-worded to say the patches leg rests on S259 **plus** the un-opened `using/cmdline` page (and the
un-opened page is filed as a lead, not a row — CORPUS rule 4/5: a lead is not evidence).

### F3 (low) — the lesson's `-S` quote is not in the snapshot (apostrophe drift)

`corpus/lessons/round-42.md:27` quotes: `"The automatic import can be suppressed using the interpreter's -S option."`
with a **straight** apostrophe. The snapshot carries U+2019 (’):

```
$ grep -o "interpreter.\{1,3\}s" corpus/lessons/round-42.md | head -1 | od -c
0000000   i n t e r p r e t e r   '   s       - S   o p t i o n
$ grep -o "interpreter.\{1,3\}s" census/round-42/sources/python-3-library-site.html | head -1 | od -c
0000000   i n t e r p r e t e r 342 200 231   s
```

Rendered-text containment test: the straight-apostrophe string is **ABSENT** from the snapshot; the
curly one is **FOUND**. The wave-1 scribe draft
(`.ufo/waves/round-42/w1/R42scribe06/S259-gate.md`) carried the **correct** curly form; the landed
lesson changed it. The registry row itself does not quote the `-S` sentence (it only names "the `-S`
option"), so the drift is confined to the lesson's Gate cell.

**Fix (append-only):** the lesson's Gate cell is corrected to the U+2019 form. The row needs nothing.

### F4 (low) — "census exit 0 at both ends" has only a *before* receipt

`LOG.md:1932` and `SCORECARD.md:852` both say "census exit 0 **at both ends**
(`census/round-42/records/census-before.txt`)". `census/round-42/records/` contains **only**
`census-before.txt` — there is no `census-after.txt`:

```
$ ls census/round-42/records/ | grep -i census
census-before.txt
$ cat census/round-42/records/census-before.txt
# round 42 start census … lane base bf618f6c5c09d302994871c94903abbea2deb60d
rows=182
W04=52
…
EXIT=0
```

The end-of-round figure (183 rows) has no committed receipt. The claim is **true** (I measured it, §5),
but the pointer is one-sided — a Q101/Q103-shaped gap in the same bookkeeping that adds S259.

**Fix:** commit the end-of-round census receipt as `census/round-42/records/census-after.txt`
(rows=183, W04=52, EXIT=0) and cite it alongside `census-before.txt`.

### F5 (informational) — `teaches` is a bare quote, not a stated benefit

CORPUS.md: "`teaches` — one grounded learner benefit." S259's `teaches` is the quoted sentence with no
benefit clause. S255/S256 are the same shape; S257/S258 add a benefit clause. Consistency note only,
**not** a defect against the frozen contract.

---

## 5. Evidence — the census, and the E11 experiment

### 5.1 The mandated command

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
… (52 W04 lines) …
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
EXIT=0
```

- **exit code 0** ✓ (expected)
- **rows 183** ✓ (expected) — measured two ways:
  `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `183`, and
  `sources-census.sh census --root … souji` → `souji rows 183` / `FLEET rows 183`.
- **W04 count 52** ✓ (expected) — `grep -c W04` over the validate output = `52`.
- S259 itself raises **no** W04: its URL `docs.python.org/3/library/site.html` is unique in souji
  (`grep -c 'W04.*site.html'` → `0`), and `shared` mode lists no `site.html` across the fleet.
  The W04 count is therefore unchanged from the base (52 → 52), matching `LOG.md:1932`.
- Census mode at the tip: `tier.A 174 / tier.B 6 / tier.C 3`, `status.mined 153 / queued 14 / rejected 16`,
  `FLEET.missing 0`, `FLEET.tier.invalid 0`, `FLEET.status.invalid 0`.

### 5.2 E11 experiment — "is E11 the only dependency?"

Three scratch copies of the lane were made under `/fast/scratch/hyaku/souji-r42/R42w2reviewer07/`
(full copy = the whole lane minus `.git`; partial copy = `corpus/` only).

**A. S259 row removed, full lane copy** — the row's own line is deleted from `corpus/SOURCES.md`:

```
$ sources-census.sh validate --root <fullA> <fullA>/souji-shokunin
EXIT_fullA(S259 row removed)=0
rows_A=182  W04_A=52
souji-shokunin	ok	…/corpus/SOURCES.md
```

**Clean.** Removing S259 leaves the census at 182 rows / 52 W04 / exit 0 — no finding is raised against
the row's *absence*.

**B. Lesson file removed, S259 kept, full lane copy** — `corpus/lessons/round-42.md` deleted:

```
$ sources-census.sh validate --root <fullB> <fullB>/souji-shokunin
EXIT_fullB(lesson removed, S259 kept)=1
W04_B=52
souji-shokunin	E11	S259 missing used-by corpus/lessons/round-42.md
```

**Exactly one** non-W04 line, and it is S259's own E11. This is the only census-visible coupling of S259
to anything on disk.

**C. S259 row removed, corpus-only copy** (a *partial* copy, kept for honesty about the difference):

```
EXIT_nos259=1
nos259	E11	S120 missing used-by tools/souji-size-census.py
nos259	E11	S122 missing used-by tools/souji-size-census.py
nos259	E11	S224 missing used-by SKILL.md
nos259	E11	S225 missing used-by SKILL.md
nos259	E11	S226 missing used-by SKILL.md
```

These five are an **artefact of the corpus-only copy** (it has no `tools/` and no `SKILL.md`), not of
S259 — the full-lane copy A shows the same corpus with exit 0. Recording it so the L1 does not read the
partial-copy output as an S259 finding.

**Conclusion on the E11 question:** confirmed. The **only** dependency the census makes on S259 is the
E11 "used-by path must exist on disk" rule, and it is discharged by `corpus/lessons/round-42.md`, which
is committed at the tip. No other row, code path, or lesson cell is coupled to S259 by any census rule.
Note the census has **no** rule that would notice a lesson citing a registry id that no longer exists
(codes are E01-E12 / W01-W04 only) — so if S259 were ever removed, the lesson's four S259 mentions would
become dangling and the census would stay green. That is a census coverage limit, not an S259 defect.

---

## 6. Evidence — does the C2 claim really rest on S259?

The mechanism the counter depends on, and whether the page carries it:

| what the counter needs | documented on the S259 page? | evidence |
|---|---|---|
| a `sitecustomize` import is **attempted** at interpreter startup | **yes** | lines 418-419 (verbatim quote, §4 F1) |
| `-S` bounds that attempt | **yes, indirectly** — `-S` suppresses the `site` module; the `sitecustomize` attempt follows from it | lines 227-228 ("This module" = `site`), 506 (`site.main()` "is called automatically when this module is imported, unless the Python interpreter was started with the `-S` flag") |
| the module is found via **`sys.path` / `PYTHONPATH`** | **no** — the page never says `PYTHONPATH`, `sys.path` search order, or `site-packages` discovery for a user-supplied module | `grep -ci pythonpath` → 0; `grep -in 'using/cmdline\|PYTHONPATH\|sys\.path' corpus/SOURCES.md` → no row |
| the module's *contents* / what it may do | **out of scope by the row's own exclusion** | scope cell: "not the contents of any particular `sitecustomize` module" |

### 6.1 The dependency is real and measurable (patch reach), and the `-S`/`-I` bound is exact

`SITECUSTOMIZE` was extracted **verbatim** from `census/round-42/c2-counter.py` (its `SITECUSTOMIZE`
literal, lines 298-336) into a scratch dir and placed on `PYTHONPATH`, then the landed tool was run:

```
$ python3 -B tools/souji-freeze-check.py --selftest                      # no PYTHONPATH
rc=0   SELFTEST cases=31 pass=31 fail=0

$ PYTHONPATH=<pdir> SOUJI_R42_PATCH=P1 python3 -B tools/souji-freeze-check.py --selftest
rc=1   SELFTEST cases=31 pass=3 fail=28
        selftest FAIL counter-symlink
        selftest FAIL population-symlink
```

So the patch leg genuinely turns the tool red **only** because `sitecustomize` is imported at startup —
the mechanism S259 documents. The C2 claim does rest on the page's content.

Reach of the same patch under interpreter flags (host Python 3.14.8), confirming the lesson's Q105
caveat exactly:

```
PYTHONPATH=<probe> python3 -B        → SITECUSTOMIZE-REACHED
PYTHONPATH=<probe> python3 -B -s     → SITECUSTOMIZE-REACHED
PYTHONPATH=<probe> python3 -B -P     → SITECUSTOMIZE-REACHED
PYTHONPATH=<probe> python3 -B -E     → (not reached)
PYTHONPATH=<probe> python3 -B -I     → (not reached)
PYTHONPATH=<probe> python3 -B -S     → (not reached)
```

and with the patch module present but `PYTHONPATH` dropped from the child environment:
`rc=0 SELFTEST cases=31 pass=31 fail=0` (the patch does not reach).

This matches the lesson's caveat verbatim — *"the injection does not reach a child started with `-I`,
`-E` or `-S`"* — and the counter never passes `-I`/`-E`/`-S` to the child
(`grep -n '"-I"\|"-E"\|"-S"\|isolated' census/round-42/c2-counter.py` → no match).

**So: the dependency is real, and it is bounded exactly as the lesson states. The gap is not in the
dependency — it is in what the page is credited with carrying** (F2: the `PYTHONPATH` discovery channel).

---

## 7. Residual risk

- **R1 — the URL is rolling.** `https://docs.python.org/3/library/site.html` always serves the newest
  3.x; the snapshot is 3.15.2 while the host interpreter is 3.14.8 (`python3 -VV` → `3.14.8`). The row
  pins the digest and the version stamp, so drift is detectable, but `recheck on-release` means the
  live bytes will change at the next Python release and the snapshot will no longer match the URL.
  Consistent with S255/S256 handling of the same `docs.python.org/3/` hazard.
- **R2 — the documented page is one minor version ahead of the interpreter the counter runs.** The
  behaviour asserted (startup `sitecustomize` import, `-S` bound) is present on both 3.14.8 (measured)
  and 3.15.2 (documented); the counter's `patches=3/3` was measured on the host 3.14.8.
- **R3 — the census has no rule that binds a lesson's cited id to a registry row** (§5.2). A future
  removal of S259 would leave `corpus/lessons/round-42.md` citing a nonexistent id with the census
  green.
- **R4 — `SITECUSTOMIZE` reachability is environmental.** The patch reaches because `site` is imported
  at startup and `PYTHONPATH` is on `sys.path`; a host with `PYTHONPATH` scrubbed, or a `python3`
  resolved through a wrapper, changes the counter's behaviour. The counter builds a minimal `env`
  (`env(scratch)` keeps only `PATH`, `TMPDIR` and `GIT_ENV`), so it controls this; but the *child's*
  `python3` is still resolved through the caller's `PATH` (already named as N-C2b).

---

## 8. Commands actually run (verbatim), for reproduction

```sh
# 1. bytes
curl -sS -L --max-time 60 -o live-site.html https://docs.python.org/3/library/site.html
sha256sum live-site.html census/round-42/sources/python-3-library-site.html
cat census/round-42/sources/SHA256SUMS
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3105a63b23481fccf7df58e74d14a6681e0ea0c8:census/round-42/sources/python-3-library-site.html | sha256sum

# 2. line numbers
sed -n '416,419p;227,228p;506p' census/round-42/sources/python-3-library-site.html
grep -n 'sitecustomize' census/round-42/sources/python-3-library-site.html

# 3. census (the mandated command)
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census  --root /home/vgpnk/Projects/shokunin souji
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh shared  --root /home/vgpnk/Projects/shokunin

# 4. row shape / cells
awk -F'|' '/^\|[[:space:]]*S259[[:space:]]*\|/ {print NF; for(i=1;i<=NF;i++) print i, $i}' corpus/SOURCES.md
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md

# 5. E11 experiments (scratch copies under the seat's scratch dir)
cp -a <lane> $S/full ; rm -rf $S/full/.git
cp -a $S/full $S/fullA ; grep -vE '^\|[[:space:]]*S259[[:space:]]*\|' $S/fullA/souji-shokunin/corpus/SOURCES.md > tmp && mv tmp $S/fullA/souji-shokunin/corpus/SOURCES.md
cp -a $S/full $S/fullB ; rm $S/fullB/souji-shokunin/corpus/lessons/round-42.md
sources-census.sh validate --root $S/fullA $S/fullA/souji-shokunin   # exit 0
sources-census.sh validate --root $S/fullB $S/fullB/souji-shokunin   # exit 1, E11 S259 only

# 6. counter dependency
python3 -c "<extract SITECUSTOMIZE literal from census/round-42/c2-counter.py> > $S/pdir/sitecustomize.py"
env -i PATH=/usr/bin:/bin HOME=/tmp                      python3 -B tools/souji-freeze-check.py --selftest
env -i PATH=/usr/bin:/bin HOME=/tmp PYTHONPATH=$S/pdir SOUJI_R42_PATCH=P1 python3 -B tools/souji-freeze-check.py --selftest
env -i … PYTHONPATH=$S/pdir SOUJI_R42_PATCH=P1 python3 -B -I tools/souji-freeze-check.py --selftest
env -i … PYTHONPATH=$S/pdir SOUJI_R42_PATCH=P1 python3 -B -S tools/souji-freeze-check.py --selftest

# 7. page reach probe (sitecustomize on PYTHONPATH under -s/-P/-E/-I/-S)
```

Scratch directory `/fast/scratch/hyaku/souji-r42/R42w2reviewer07/` was removed after this report was
written. No file outside `.ufo/waves/round-42/w2/` in the lane was created or modified by this seat.

---

## 9. Summary of findings by severity

| id | severity | finding | what it attacks |
|---|---|---|---|
| F1 | medium | scope says "`-S` suppresses the automatic import"; the page's `-S` sentence is about the `site` module, one step from `sitecustomize` | S259 scope cell |
| F2 | medium | the C2 patch leg's `PYTHONPATH` discovery channel is not on this page and has no registry row; the lesson's admitted-for cell asserts it | S259 as C2's sole ground |
| F3 | low | the lesson's `-S` quote uses a straight apostrophe; the snapshot has U+2019 (the w1 draft had the correct form) | `corpus/lessons/round-42.md:27` |
| F4 | low | "census exit 0 at both ends" cites only the *before* receipt; no `census-after.txt` exists | LOG.md:1932 / SCORECARD.md:852 |
| F5 | info | `teaches` is a bare quote, not a stated benefit (S255/S256 same shape) | S259 teaches cell |

**Verdict on S259: NARROW SCOPE.** All bytes, digests, line numbers and quotes check out and the row is
genuinely load-bearing for C2; land a superseding row S260 (CORPUS rule 2 — `scope` is immutable in
place) that (a) attributes the `-S` bound to the `site` module's import rather than directly to the
`sitecustomize` attempt, and (b) states the `PYTHONPATH`/`sys.path` discovery channel as outside this
page, with the `using/cmdline` page filed as an un-opened lead or opened as its own row.
