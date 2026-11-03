# S55sentinel01 — souji round 55 wave 1 — sentinel (write-scope + hardening review)

Seat: `S55sentinel01` · lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` · date 2026-11-03
Scratch: `/fast/scratch/hyaku/souji-r55/S55sentinel01/` (deleted at yield) · seat dir: `.ufo/waves/round-55/w1/S55sentinel01/`

## VERDICT: CONDITIONAL PASS

The r55 v4 counters are sound on every surface the preregistration claims to instrument, and the
lane/fleet are clean of seat-caused mutation. **CONDITIONAL** on the L1 routing the three
acceptance-escape classes below (S55-S1 … S55-S3) into the round's named-limit ledger and the
r56 instrument work. None of them is an edit of frozen bytes; each is a named limit with a
reproduction receipt. No finding invalidates either claim.

---

## 0. Pins, provenance, and cleanliness (task item 1)

### 0.1 Frozen pins — all six verified byte-identical, re-verified after peers' edits

| pinned file | sha256 (measured) | verdict |
|---|---|---|
| `census/round-55/c1-counter.py` | `944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2` | MATCH |
| `census/round-55/c2-counter.py` | `e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c` | MATCH |
| `census/round-55/fixtures/build-fixtures.py` | `e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62` | MATCH |
| `census/round-55/fixtures/run-matrix.sh` | `ce13d4fff4b66175071ccef2a808baf3b1f928c5ec9985343580524450ef8315` | MATCH |
| `census/round-55/records/c1-selftest-expected.tsv` | `ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e` | MATCH |
| `census/round-55/records/c2-selftest-expected.tsv` | `63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc` | MATCH |

`git diff --stat` over `preregistration.txt`, both counters, `fixtures/`, and both expected TSVs is
**empty** — no frozen byte was edited, by me or by a peer. The r54 v3 acceptance-control counters
also verify at their r54-published digests (`c1 f45d3d8f…fccf7e`, `c2 84b05295…735e09`), matching
the digest quoted in `corpus/knowledge/correction-filing-fence-grammar.md`.

### 0.2 Lane and fleet untouched by seat work

- Lane worktree: the only lane modifications are peers' in-flight lesson/knowledge edits
  (`SKILL.md`, `corpus/lessons/round-55.md`, `LOG.md`, `SCORECARD.md`, `census/round-55/wave/`) —
  **none is mine**; my seat writes only under `.ufo/waves/round-55/w1/S55sentinel01/`, which
  `.gitignore:1:.ufo/waves/` covers (`git check-ignore` confirms).
- Fleet root: `git status --porcelain` shows only `.scratch/goal-20261103-hyaku-run15.md` and
  `.scratch/run15-state.json` (orchestrator-owned run state, mtimes 16:26/18:46) plus one untracked
  `.ufo/reports/round-31/kagi.md` (mtime 18:50, a sibling lane's report — not mine). **No tracked
  fleet-root file (`LOG.md`, `SCORECARD.md`, `MANIFEST.json`) is content-modified**:
  `git diff --stat` on those paths is empty.
- Stray processes: `ps -u $(id -u) … | grep -E "c[12]-counter|build-fixtures|run-matrix"` → **0**.
  The seven live `python3` processes are all host shims/daemons (uwsm, printer applet, ds-flash,
  claude/oauth/glm shims), none souji-related. List-only observation; no signal was sent.
- Disk: `disk-guard.sh status` before the heavy pass — `/fast/scratch/hyaku` 409.2 G free (50 %),
  `/tmp` 95.6 G free. No ENOSPC.
- **No pacman invocation, no network call, no tool install** by this seat (task item 4). The tooling
  authorization in `/home/vgpnk/.omp/agent/RULES.md` was read; the task needed no new tool, so the
  pacman channel was not used and no `uv`/`npx`/binary install was performed. Nothing was written
  outside `/fast/scratch/hyaku/souji-r55/S55sentinel01/` and the seat dir.

### 0.3 Dispatch-tip scope confirmed

`git show --stat 3ce0ba03` = `census/round-55/records/c1-tip.txt`, `c2-tip.txt`,
`sources/s278-located-quote.txt`, `sources/s278-python-stdtypes.html` — **records and S278 sources
only**, as the dispatch states. The measured-revision legs reproduce independently:

- C1 at `4b10ddd1741a948c89d283358affd1da2ab3fd95` → exit 0, `unfiled=0 record_sha=ok
  appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0
  pairinert=0` — byte-identical to the committed `records/c1-tip.txt`.
- C2 at the same revision → exit 0, `receipt=ok sorted=ok tool_pin=ok` — byte-identical to
  `records/c2-tip.txt`.
- Both run from a scratch cwd with `--scratch` pointed at scratch: **the lane worktree was
  byte-identical before and after** (`git status --porcelain; git rev-parse HEAD` compared → IDENTICAL).

---

## 1. Write-scope and `--scratch` steering (task item 3)

### 1.1 No writes outside `--work` — confirmed, with one disclosed caveat

Grep of the committed tools for write primitives:

```
c1-counter.py:472   fdir.mkdir(parents=True, exist_ok=True)     # work/'c1-fixtures'
c2-counter.py:344   fdir.mkdir(parents=True, exist_ok=True)     # work/'c2-fixtures'
build-fixtures.py:232 path.parent.mkdir(parents=True, exist_ok=True)
build-fixtures.py:235 path.write_bytes(data)                     # fixture repo only
build-fixtures.py:250-252 shutil.rmtree(d); d.mkdir(...)         # fixture repo only
build-fixtures.py:724 Path(out).write_text(...)                  # --manifest path (explicit arg)
```

No `open(…,'w')`, no `write_text` outside the fixture/manifest paths, no `mkdir` outside `--work`,
no `unlink`/`rmtree` outside a fixture dir, no `os.system`/`shell=True`. All `subprocess.run` calls
are argument-list form (no shell) with `timeout=120`; every git call carries
`-c core.fsmonitor=false -c core.hooksPath=/dev/null` and a scrubbed env
(`GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_NO_REPLACE_OBJECTS=1`,
`GIT_OPTIONAL_LOCKS=0`, `GIT_NO_LAZY_FETCH=1`, `GIT_TERMINAL_PROMPT=0`).
No network surface: grep for `urllib|requests|socket|http|urlopen|curl` in all three files → **none**.

**Caveat (LOW, S55-S4).** The counters import the builder with
`importlib.util.spec_from_file_location(...).loader.exec_module(mod)`. Under plain `python3`
(no `-B`), CPython writes `census/round-55/fixtures/__pycache__/build-fixtures.cpython-314.pyc`
**inside the lane repo** — outside `--work`. Measured: running the C1 selftest in a *copy* of the
lane tree without `-B` produced
`…/lanesim/round-55/fixtures/__pycache__/build-fixtures.cpython-314.pyc`. The committed
`__pycache__/` in the lane (mtimes 18:27–18:30) is exactly this artifact, and `.gitignore:3`
(`__pycache__/`) keeps it out of `git status`. Every *committed* invocation form in the prereg and
in `run-matrix.sh` uses `python3 -B`, so the canonical path writes nothing outside `--work`; the
exposure is only a non-`-B` invocation. Named limit, not a defect in the frozen bytes.

### 1.2 `--scratch` steers — confirmed for both counters

Both selftests run with **only** `--scratch` set (no `--work`) succeed and place the whole work
tree under the `--scratch` path:

```
python3 -B census/round-55/c1-counter.py --selftest --scratch <scratch>
  → SELFTEST pass cases=27 ; exit 0 ; tree at <scratch>/c1-fixtures (27 fixture repos)
python3 -B census/round-55/c2-counter.py --selftest --scratch <scratch>
  → SELFTEST pass cases=15 ; exit 0 ; tree at <scratch>/c2-fixtures (15 fixture repos)
```

The r54 sentinel-S6 routed fix holds in v4 (`work = ns.work or ns.scratch`, both counters).
Pin refusal is fail-closed **before exec**: a wrong `--builder-sha256` (C1) and a wrong
`--expected-sha256` (C2) each print `CANNOT-EVALUATE PIN-MISMATCH …` and exit **rc 2** (measured
rc=2 for both, not 0).

### 1.3 Committed matrices name every kill row

`c1-matrix-v4.tsv` (27 rows) and `c2-matrix-v4.tsv` (13 rows): every row with `exit=1` carries a
non-empty finding token — `awk '$5==1 && $6=="-"'` → **no unnamed kill row** in either arm. The
r54 §5.2 unnamed-kill-row defect class is repaired in the C1/C2 matrices, and the v3 acceptance
control (`c1-matrix-v3.tsv`) does **not** kill any of the eight acceptance attacks (F7-FF, F13,
F14, F15, F16, F20, F21, F22 all exit 0 under v3), so the v4 work is non-vacuous.

---

## 2. One-line-model re-attack — the four surfaces the fixtures do not cover (task item 2)

All four probes were built by **importing the frozen builder module** in scratch
(`importlib.util.spec_from_file_location('bf', 'census/round-55/fixtures/build-fixtures.py')`) and
using its `init_repo`/`write`/`commit_all` helpers — no frozen byte was edited, and nothing was
committed anywhere but in scratch fixture repos. Each probe was run under **both** arms (v4-r55
and the v3-r54 acceptance control) so that a "regression vs v3" claim is evidenced, not asserted.

### S55-S1 — NUL byte in a correction file (HIGH)

**Exploit.** A `\x00` appended to a correction line makes the whole correction file *binary* to git.
Two distinct consequences, both measured:

1. **The deletion check mis-fires and masks the real verdict.** If the correction file changed
   between base and rev, `git diff --numstat` emits the binary marker `-\t-\tSCORECARD.md`
   (measured raw: `'-\t-\tSCORECARD.md\n'`). The counter's `numstat_deletions` maps `dels == '-'`
   to `-1` and reports it as a **deletion**:

   ```
   FINDING DELETED-LINES SCORECARD.md deletions=-1 between faf39fbc5fcd..79db092bc945
   SUMMARY … appended=DELETED … bogus=0
   ```
   Note `deletions=-1`: the file was not deleted, and the **bogus corrections in it were never
   judged** (`bogus=0`). The exit is 1 for the wrong reason — the counter accuses a deletion that
   did not happen and silently drops the `BOGUS-RECOMPUTED` verdict the same bytes earn without the
   NUL.
2. **The bogus correction escapes entirely when the file is unchanged base→rev.** Same bogus
   corrections (`recomputed=83` against a record of 79), one build with a trailing `\x00`, one
   without, both with an *unchanged* correction file so the deletion check has nothing to say:

   | probe | arm | exit | first FINDING |
   |---|---|---|---|
   | D-CONTROL-UNCHANGED (no NUL) | v4-r55 | **1** | `BOGUS-RECOMPUTED` (×2) |
   | A-NUL-UNCHANGED (trailing NUL) | v4-r55 | **0** | – (none) |

   The identical bytes minus one `\x00` flip the verdict from 1 to 0. The v3 arm behaves the same
   way on both, so this is not a v4 regression — it is a **carried, undisclosed acceptance escape**
   on a surface the prereg's "one line model" narrative claims to have closed. Reproducible: two
   independent builds (`NUL-REPRO-1`, `NUL-REPRO-2`) and two independent harnesses
   (`attacks2.py`, `attacks5.py`) give the same verdict.

**Classification: routed proposal (HIGH), disclosed as a named limit.** The prereg's named-limit
list covers "CR-only line endings (no LF) are one line to this counter" but says nothing about NUL.
Impact: a single NUL byte in `SCORECARD.md` silently converts a `BOGUS-RECOMPUTED` refusal into
either a wrong-reason `DELETED-LINES` (exit 1) or a silent pass (exit 0). Smallest remediation
(r56, not now): treat a numstat `-` (binary) entry as **"cannot evaluate deletions"** rather than
`-1` deletions — refuse by name (e.g. `DELETIONS-UNREADABLE-BINARY`) instead of reporting a
fabricated deletion count, and keep the bogus-correction verdict visible. Do not edit the frozen
bytes.

### S55-S2 — an HTML-comment region opener that is not at column 0 hides a SOURCES overstatement (MEDIUM)

**Exploit.** The v4 `hidden_lines()` HTML-comment branch fires on `'<!--' in ln` for *any*
indentation, and the LOG/README pair scan skips lines the same grammar hides. So an opener that is
indented by four spaces — which CommonMark 0.31.2 reads as an **indented code block**, not an
HTML block — silently hides the next line from the pair scan:

| probe | arm | exit | first FINDING |
|---|---|---|---|
| G-PAIR-CONTROL (plain overstating pair) | v4-r55 | 1 | `UNFILED-SOURCES-ANNOTATION` |
| F-INDENT4-PAIR-HIDE (`    <!--` then the pair) | v4-r55 | **0** | – (none) |
| H-NESTED-PAIR-HIDE (`<!-- <!--` then the pair) | v4-r55 | **0** | – (none) |
| F-INDENT4-PAIR-HIDE | v3-r54 | **1** | `UNFILED-SOURCES-ANNOTATION` |

The last row is the important one: **v4 regresses against the v3 arm on this surface.** v3 fired
the refusal; v4 does not. The same nested-opener shape also swallows a bogus correction on an
agreeing site (`P-NESTED-COMMENT`, v4 exit 0), and a 4-space-indented one-line wrapper is outside
the `{0,3}` lexing tolerance and does not lex (`P-INDENT4-WRAPPER`, v4 exit 0) — both are the
expected "must not lex" behaviour named in the task, and both are consistent with v3.

**Classification: routed proposal (MEDIUM) + named limit.** The r54 lesson already discloses "the
counter recognises a `<!--` anywhere on a line, while the CommonMark type-2 start condition is a
line that **begins** with `<!--`" as a conservative-for-refusal divergence. That disclosure covers
the *fence* side but not this pair-scan side: here the divergence is **not** conservative — it
**hides a live overstatement** that v3 still caught. The r56 remediation is narrow: apply the
CommonMark start condition (≤3 spaces of indent) to the HTML-comment branch, or make the pair scan
consult only the *fence* grammar. Not an edit of frozen bytes.

### S55-S3 — the correction lexer's tolerance boundary (MEDIUM)

**Exploit.** `CORR_RE`/`CORR2_RE` accept `{0,3}` leading spaces and an optional one-line
`<!-- … -->` wrapper, so a correction that is **not** lexed is invisible to the whole instrument
(it never reaches the hidden-set audit, the bogus check, or the filedness computation):

| probe (bogus `recomputed=83` on an agreeing site) | v4 exit | first FINDING |
|---|---|---|
| CTL-INDENT2 (`  R52-CORRECTION …`) | 1 | `BOGUS-RECOMPUTED` |
| CTL-INDENT3 (`   R52-CORRECTION …`) | 1 | `BOGUS-RECOMPUTED` |
| CTL-WRAPPER (`<!-- R52-CORRECTION … -->`) | 1 | `BOGUS-RECOMPUTED` (+`CORRECTION-IN-FENCE`) |
| P-INDENT4-WRAPPER (`    <!-- … -->`, 4 spaces) | **0** | – |
| P-NESTED-COMMENT (`<!-- <!-- … --> -->`) | **0** | – |
| P-TAB-WRAPPER (tab-indented wrapper) | **0** | – |

The controls confirm the fixtures' own claim (F20/F21 lex and are judged). The escapes are at the
tolerance boundary — 4 spaces, a tab, and a nested `<!--` all fall outside the v4 lexing grammar
and therefore outside the audit. The task's expectation is met exactly: the 4-space-indented
`<!-- … -->` line **must not lex**, and it does not.

**Classification: named limit (disclosed, MEDIUM), routed to the r56 ledger.** The prereg already
carries the "0-3 spaces / one-line wrapper" lexing boundary as its R1 repair; what is *not* written
down is that a non-lexing correction is therefore **unjudged** (never counted as a bogus filing).
The r56 wording should say so explicitly and pin the boundary with a committed fixture (e.g. a
4-space-indented bogus correction expected to stay green), so the tolerance edge is a measured
property rather than an accident.

### S55-S4 — `__pycache__` written into the lane when the counters are run without `-B` (LOW)

See §1.1. Named limit; canonical `python3 -B` invocations are unaffected; `.gitignore` keeps the
lane's `git status` clean.

---

## 3. C2 capture-counter re-attack (supplementary)

The C2 surfaces are sound on the claims the prereg makes. One uncovered shape, routed as a named
limit:

### S55-S5 — an empty-valued unknown receipt key is not refused (LOW)

The receipt grammar `RECEIPT_KV = r'\s*#\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\S+?)\s*'` requires a
**non-empty** value (`\S+?`). An unknown key written with an empty value therefore does not match
the grammar at all and is silently ignored:

| probe (receipt extra line) | v4 exit | first FINDING |
|---|---|---|
| C2-CONTROL-NONEMPTY (`# BUILDHOST=fixture`) | 1 | `RECEIPT-UNKNOWN-KEY` |
| C2-EMPTY-VALUE-KEY (`# BUILDHOST=`) | **0** | – |
| C2-EMPTY-VALUE-KEY-SPACE (`# BUILDHOST = `) | **0** | – |

The r54 reviewer02 NL-3/NL-4 routing ("an unknown key in any of those shapes is refused") is
satisfied for populated values and missed for the empty-value spelling. Classification: named
limit (LOW), routed to r56 — the smallest remediation is to let the value be empty
(`(?:\S*)`) so an unknown key is still *named*, not silently dropped.

Everything else the prereg claims for C2 reproduces: the receipt binds capture↔receipt bytes, the
tool digest pin is honoured (`TOOL-SHA-ARG-MISMATCH` rc 1 / `TOOL-SHA-ARG-MALFORMED` rc 2 both
reachable), `TOOL_SHA256`/`FLEET_HEAD`/`ENTRIES`/`COUNT` recount all hold, and the `#`-leading
tab-bearing row is refused.

---

## 4. Named limits carried (not new, listed for the L1's ledger)

- Zone frozen at 32 chars; a token wholly beyond it is not an annotation.
- SOURCES scan is line-based; a path-like `path.ext:line` pointer exempts the line.
- Annotations whose pair does not exceed the registry count are historical notes.
- Pair annotations outside `LOG.md` / `corpus/README.md` are invisible to the instrument.
- CR-only line endings are one line to this counter — **measured (P-CR-ONLY): exit 0, no finding**,
  consistent with the disclosure; a CR-only correction file is one `re.M`-less line, so the
  correction does not lex and the bogus filing is not judged. This is the same class as S55-S1/S55-S3
  and is the disclosed half of it.
- The registry's append-only monotonicity is assumed.
- HTML comment class is line-level `<!--`/`-->`, not full CommonMark HTML blocks — **measured
  (S55-S2): the divergence hides a SOURCES overstatement, so it is not conservative on the pair-scan
  side.**
- Finding-id precedence inside one correction is INERT → BOGUS → IN-FENCE.
- Only the first unknown receipt key is reported; capture-header unknown `# KEY=VALUE` lines are
  ignored.
- Free-form comments without tabs are accepted.
- ENTRIES is the tool's own count; the receipt binds bytes, not execution; FLEET_HEAD is
  format-checked, not resolved.
- At most one ZONE-TOKEN-STRADDLES-EDGE registers per line.
- The deletion check reads `git diff --numstat` — **measured (S55-S1): a binary file yields the
  marker `-\t-`, which the counter currently reports as `deletions=-1`.**

---

## 5. What I did not do

- No edit of any frozen byte; no commit, push, or mutating git/jj command anywhere; no write
  outside my scratch and my seat dir; no pacman; no network; no subagent dispatch (leaf).
- No new SOURCES row opened (this seat is a hardening seat, not a frontier seat; the round's
  planned source is the L1's `str.splitlines()` documentation capture, S278, already landed).
- No change to the counters, the expected TSVs, the matrices, or the preregistration — every
  defect above is a named limit with a reproduction receipt, per the r54/r55 discipline.

## 6. Receipts index (all under the seat dir)

| file | content |
|---|---|
| `S55sentinel01-report.md` | this report (also at `.ufo/waves/round-55/w1/S55sentinel01.md`) |
| `receipts/pins.txt` | the six frozen sha256 measurements + r54 v3 control digests |
| `receipts/cleanliness.txt` | lane/fleet porcelain, tracked-file diff emptiness, stray-process list, disk-guard status |
| `receipts/writescope.txt` | write-primitive grep, `--scratch`-only selftest runs (rc 0, 27/15 cases), pin-mismatch rc 2, real-lane legs, lane-unchanged check, pycache experiment |
| `receipts/attacks-nul.txt` | S55-S1 verbatim: A/D controls, B numstat raw `-\t-\tSCORECARD.md`, NUL repro ×2 |
| `receipts/attacks-hidden.txt` | S55-S2/S55-S3 verbatim: F/G/H pair-hide, CTL-INDENT2/3, CTL-WRAPPER, P-INDENT4-*, P-NESTED-*, P-TAB-*, P-CR-ONLY |
| `receipts/c2-emptykey.txt` | S55-S5 verbatim: C2 empty-value receipt probes |
| `receipts/harness/` | the four scratch harnesses (`attacks2.py`, `attacks3.py`, `attacks4.py`, `attacks5.py`) + raw JSON results, kept as the reproduction scripts |

Scratch tree `/fast/scratch/hyaku/souji-r55/S55sentinel01/` deleted at yield; receipts copied into
the seat dir first.
