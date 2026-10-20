STATUS: DONE — frontier-step plan attacked; 16 concrete pitfalls with file:line evidence and smallest fixes; the timeout-URL recheck trap and the `|`/E04/E11 mechanics are the sharpest.

Axis attacked: calibration (the registry and lesson are the lane's self-assessment; every pitfall below is a way the frontier step writes evidence that does not match observed state).

# Plan under attack (from `.ufo/waves/round-18/w1-spec.json`)

~9 planned rows S064+: bash Job-Control-Basics, kill.2, subprocess.html, proc_pid_cwd.5, proc_pid_stat.5, open.2 (ENXIO), timeout-invocation `--foreground`, git-cat-file(1), attr.c@v2.56.0. Drafted by 4 ScribeRows* seats + 7 "Source item" seats; knowledge `census-bounded-repo-reads.md` uses "S0xx placeholders"; ScribeLessonDraft seeds R18-M1 (dangling pointers) and R18-M2 (fixture orphans). Contract: CORPUS.md:64-148; validator `scripts/sources-census.sh`.

## P1 — timeout URL: "new row" is the trap, not the warning

The planned `timeout-invocation.html --foreground` opening reuses S034/S038's exact URL (`SOURCES.md:50,54`). The Goal is right that this is a recheck. Three legal outcomes, ranked:

- **(a) Recheck S038, no new row.** If the `--foreground` fact only needs grounding in the lesson/claim, cite S038 with the new sentence and log `used-by`/`recheck` old→new in the Gate (r17 precedent for S042, `SOURCES.md:9`). Zero validator cost.
- **(b) New row, disjoint scope** (e.g. "timeout --foreground leaves COMMAND's children untimed") → exactly one new **W04** (validator `:643-645`). Legal, advisory, must be disclosed: expected W04 set goes 4→5, not "stays 4".
- **(c) ILLEGAL: new row, overlapping scope, no `supersedes S038`** → **E04, exit 1** (`:646-649`; regex needs literally `supersedes S0NN` in teaches, `:648`). Also note W04 fires even on `rejected` rows (`:644` has no status test) — a rejected timeout row still adds a warning.

Smallest fix: prefer (a); if (b), the provenance paragraph and Gate census line must name the fifth W04. Any "validator must still show exactly 4 W04" expectation is already wrong.

## P2 — every installed/versioned anchor drifted today

Host now: `git 2.56.0-1, coreutils 9.12-2, bash 5.3.20-1, man-pages 6.19-1, python 3.14.8-1` (`pacman -Q`). S034/S038's installed anchors say **coreutils 9.11-2** and cite info lines 15316-15320 — copying those coordinates into a new row is a stale anchor. attr.c must be pinned at **v2.56.0** (the plan does), but its line numbers must be re-derived at that tag, not recalled from r16-era v2.55.0 reading (S037/S009 pin v2.55.0 lines — different file generation). Every git-scm.com "last updated" line and every man7 version line must be re-read as served 2026-10-20.

## P3 — subprocess row: two different timeout semantics, plus a moving URL

`Popen.communicate(timeout=)` does not kill on expiry; `subprocess.run(timeout=)` does kill then wait. The ScribeRowsPy prompt recalls one wording; a teaches that conflates them miscalibrates the fixture fix (r15/r14 fixtures use `run`, r17 uses Popen+killpg). Also S061's precedent: `docs.python.org/3/library/…` 301s (`/3/builtins/`); record the URL actually fetched, the served version (3.15.0) and its last-updated line — `/3/` is a moving target, so the anchor needs the served version.

## P4 — used-by ordering: E11 and LG-DANGLING-PTR check different trees

`mined` requires ≥1 used-by path that exists **in the working tree** at validation (E11, `sources-census.sh:566-567`); LG-DANGLING-PTR resolves tokens **at REV**. A row pointed at `corpus/knowledge/census-bounded-repo-reads.md` breaks if the knowledge entry is narrowed or dropped in wave 2; a row pointed at the lesson breaks if the lesson is renamed. r17 precedent: used-by `corpus/lessons/round-NN.md` (always lands) or a committed knowledge entry. Smallest fix: default every new row's used-by to `corpus/lessons/round-18.md`; add the knowledge path only when it lands; a `mined` row whose only cite is planned is a status lie — and C1 "rests on new rows" needs them mined, not queued.

## P5 — id collisions and `S0xx` placeholders

Four ScribeRows* seats plus seven Source-item seats draft rows concurrently; `S0xx` placeholders sit in the knowledge draft. Two rows landing with one id = **E03**; a placeholder reaching a committed file = an unresolvable pointer. Rule for L1 (round-17 did this, `round-17.md:46`): ids assigned only at integration, ascending from **S064** (registry ends S063, `SOURCES.md:79`), Gate list and provenance paragraph renumbered to match.

## P6 — literal `|` inside cells → E01

A row is exactly 11 cells (NF=13, `:635-638`). The **attr.c code row** is the exposed one: C source quotes/anchors containing `||` split a cell. Keep `|` out of every cell — put the code quote (which may contain `|`) in the lesson Gate's quote slot, and choose an anchor line range without pipes. Related: `url_of` takes the **first** http(s) token in the source cell (`:600-605`) — a "canonical — (raw mirror: URL)" ordering decides which URL dedups; S051 led with the docs URL deliberately.

## P7 — quotes: opened not recalled, located, ≤25 words, grounding teaches

No script enforces the limit (r17 ScribeSourcesRows §7.4) — hand-count. Each Gate entry needs URL · access date · quote · location + which seat opened it (round-17.md:32-44 shape). Precedents for fetch failure: gnu.org bash page unreachable in r16 (Wayback fallback, `SOURCES.md:59`), gnu.org timeout fetch timed out in r13 (installed info fallback, `SOURCES.md:50`). If a planned page fails today, the row must name the fallback actually opened with ITS location — never a recalled quote. teaches must not exceed what the located quote+scope states (scope-bounded tier A; S036's "suppression only, not…" shape).

## P8 — provenance paragraph must not lie about untouched rows

The new "Round-18 provenance" paragraph mirrors r17 (`SOURCES.md:11`): name the new id range, access date, where the quotes live. If S038 gets a recheck or used-by gain (P1a), or S062's used-by gains the r18 lesson, "no existing row changed" is false — record `S0NN used-by: <old> → <new>` exactly as the contract rule 2 requires and r17 did for S042.

## P9 — non-author re-open and the census line are both required

Contract rule 1: "Non-author verification re-opens a sample." R17 reopened all 13 rows via wave-2 seats (`round-17.md:46`, `SOURCES.md:11`). If wave 2 skips re-opens, the Gate must say so — implying a re-open that never happened is a fabrication. The `Source census` line must record start+end verbatim: exit codes, sha256, and the full W04 list (round-17.md:48) — a count mismatch vs the declared set signals a row bug.

## P10 — row placement: inside `## Registry` only

E12 flags any `| S0NN` row outside the Registry section (`:618-622`). The provenance paragraphs are prose — never start a line there with `| S`.

## P11 — the mined mistakes: captured-by honesty and red arms that can fail

Class vocabulary is fixed (`mistakes.md:447-449`: vacuous, survivor, stale-premise, reference-drift, number-drift, scope, attribution, landing, provider). Draft rows:

- **R18-M1 (dangling pointers)** — class `landing` or `reference-drift`. captured-by `none` is arguable but weaker than honest: **Q17 existed** (`QUALITY.md:41`) and covers claimed-fixture existence at the measured rev — it simply never swept authority-file prose. The honest cell is "Q17 (partial — fixture claims only) → LG-DANGLING-PTR/Q31". Red-arm trap (**M027-class**: fix that cannot fire): running the NEW gate on the ALREADY-FIXED tree and reporting "0 findings → works" is vacuous — the pointers were already repaired by R2. Valid red arm: new gate + pre-fix authority bytes (SKILL.md:163,165 and jj-colocation-receipts.md:2,44,126,148 citing `ddb7347` records) → named LG-DANGLING-PTR ids; green: same gate + fixed bytes → 0, gate the only delta, failure text committed under `census/round-18/` (Q13).
- **R18-M2 (fixture orphans)** — class `scope` (Q4's cleanup is files, not children). **M029-trap**: the red arm must actually spawn the FIFO-blocked git and count ≥1 (leak-count.py before-arm), not just assert it. **M030-trap**: a "0 leaks after fix" against a run that never launched the blocking arm is an empty prior — pair before/after on identical runs. captured-by should say Q4 partially (trap removes files, not blocked children) → new Q30.

## P12 — the lesson's own `.ufo/waves/` citations are inside LG-DANGLING-PTR's sweep

`.ufo` IS tracked in this lane (419 `git ls-files` entries; `.ufo/waves/round-*/w*/<Seat>.md` committed each round). C2's token grammar scans `.ufo/waves/` — so every wave-report path the round-18 lesson cites (Gate reopen seats, Mistakes pointers like `.ufo/waves/round-18/w2/ReopenS0NN.md`) must be **committed at or before the measured REV**, or the lane's own new finding fires on its own lesson. Landing order: cite only reports already committed at the measured rev; the r17 lesson's `.ufo/waves/round-17/w2/…` tokens resolve because those reports were committed.

## P13 — search log and excluded candidates

Contract rule 5 requires a bounded search-log note for this opening (identified/screened/included/excluded, stop rationale — the r13 `:95` counting note is the model). Any planned source opened but not rowed is an exclusion to record; unusable candidates get `REJECTED: <reason>; flip: <what would change it>` rows (S044/S048 precedent), never silent drops. The 9 planned URLs do not appear in `## Leads` (`SOURCES.md:103-113`), so no lead-removal is needed — but a row added for a lead must also delete the lead bullet.

## P14 — kind/tier/scope honesty per row

- `attr.c` = kind `code`, tier A, pinned `file@tag:line` at v2.56.0. A "opens without O_NONBLOCK/S_ISREG guard" teaches is a **negative claim — it carries its sweep** (name the functions read or the grep), and must not claim "status always blocks" (S045's defensive-scope precedent, `SOURCES.md:61`).
- `open.2 ENXIO` grounds only the **writer-side** no-reader probe (`O_WRONLY|O_NONBLOCK` → ENXIO); `O_RDONLY|O_NONBLOCK` succeeds with no writer — scope must not claim both.
- `kill.2` negative-pid fact must be bounded: caller ownership/EPERM, `pid=-1` ≠ `pid=-pgid`, `kill(0)` = own group — the row grounds `killpg`-equivalence, not "signal all processes".
- `Job-Control-Basics` grounds pgid-per-pipeline **under job control** — the teaches needs the `set -m` precondition, not job control as default. NB: a row anchored instead at `The-Set-Builtin.html` collides with **S043's URL** (`SOURCES.md:59`) — a second new W04; Job-Control-Basics is a fresh URL, so the plan's choice is correct.
- `proc_pid_stat` quote should cover the `comm`-in-parens parse hazard (fields after `)`) — it is what makes C3's `wchan`/state extraction honest, and it is the likely quote.
- man7 rows re-derive the served version line (6.19 printed, matching `man-pages 6.19-1` installed — verify today, don't copy S062's text).

## P15 — `supersedes` must match the validator's exact regex

If any r18 row supersedes, teaches must contain literally `supersedes S<3+ digits>` (`:648`); "replaces S038" or `supersedes S34` still E04s. Contract rule 2 wants it as the teaches opening anyway (`supersedes S0NN —`).

## P16 — `opened` date is the open date, not the landing date

E08 (`:660-662`) only requires ≤ today; all r18 rows opened 2026-10-20. If integration lands a later day, `opened` stays 2026-10-20 — bumping it to match the landing commit rewrites an immutable cell (append-only rule 2).

# Impacted axes

Calibration primarily (P1–P16 all); operability indirectly (P11 red arms are C1's falsifier); coverage indirectly (P4/P12 decide whether C3's new surface is actually governed at landing).

# Verdict

Plan is **sound in shape** (fresh URLs for 8 of 9 sources; distinct scopes; S0xx→S064 renumber planned) but carries three live wires: (1) the timeout item must land as a S038 recheck or a disclosed-W04 disjoint-scope row — anything else is E04 exit 1; (2) every anchor must be re-derived against today's host (coreutils 9.11→9.12, git 2.55→2.56 already bit r16); (3) R18-M1's red arm is vacuous unless it runs the new gate against the pre-fix pointer bytes, with failure text committed.

# Checks run

- `read` corpus/SOURCES.md (whole, S001–S063), CORPUS.md SOURCES section, corpus/lessons/round-17.md (whole), corpus/QUALITY.md, `.ufo/waves/kaika-w1/mistakes.md` §5 lines.
- `read` scripts/sources-census.sh:538-695 (E01–E12/W01–W04 mechanics, url_of, E11 filesystem check).
- `python3` walk of w1-spec.json seat prompts (all source-item and scribe items enumerated).
- `pacman -Q git coreutils bash man-pages python` → 2.56.0-1 / 9.12-2 / 5.3.20-1 / 6.19-1 / 3.14.8-1.
- `git ls-files .ufo` → 419 tracked entries (`.ufo/waves/round-13/w1/AttackBounds.md` etc.).
- Not run: sources-census.sh validate (probe rule — not an ALLOWED-EXEC for this seat); no source was fetched (frontier items belong to the named seats).

# Tool installs

None.
