## Status

Adversarial falsification review of the W1 finding for C1 item E26, **with bounded execution**
(gate-leg-only probes; read-only on the lane; per-rev gate bytes extracted to scratch).
**Corrected status (post-dispatch challenge by `SoujiR34a2`, verified against frozen bytes):**
the W1 *mismatch* finding is confirmed — E26 is a genuine, deterministic value-drift mismatch,
not a measurement artifact. However, the honest-correction route I first reported (Q76 `same`
restatement, cause `aea0525…`) is **engine-rejected**, and the correction route is in fact
**closed under the frozen bytes by two independent blockades**; the only engine-accepted route
requires stripping the instrument's rev provenance stamp and is dishonest. Net: E26 is honestly
unrestateable, so the frozen C1 target `items=60 agree=60` is unreachable through E26 by honest
means. One cross-item structural hazard and one engine hole are reported for the canonical judge.

## Evidence

- Frozen E26 row, `census/round-34/c1-items.tsv:71` (list revision
  `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`): exit `0`; statement
  `reports=86 cne=0 dangling=1 other=7 fixture=ok redarm=ok regress=same`; cell `SCORECARD.md:345`;
  `files` = `census/round-30/c2-counter.py` **only**; argv
  `python3 -B census/round-30/c2-counter.py --root . --rev {REV} --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --fleet-root /home/vgpnk/Projects/shokunin`.
  E26 is the only item binding that cell; `SCORECARD.md` is byte-identical between base
  `9c76c72…` and list rev (`git diff` empty), so the frozen `where` line is the Round-30
  "C2 committed-capture report discovery" row's *after* cell, qualified "at the C2 landing commit".
- Mismatch reproduction (three agreeing readings): committed control
  `census/round-34/records/controls-c1-do-nothing.txt:55` (load 10.36), W1
  `w1/deliver-c1-do-nothing-check.txt:60` (35.17), W1 `deliver-q76-honoring.txt` (52.05) — last
  line `SUMMARY reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok regress=same rev=9c76c72…`,
  `rc=0`, predicate fails. Deterministic; not load-sensitive.
- Historical value: committed `census/round-30/records/c2-after-v1.txt` at the C2 landing commit
  `68447afef62e4761249af55a2467657f04046537` — `dangling=1 other=7`, `rc=1`.
- Executed probes (read-only on lane; `/fast/scratch/hyaku/souji-r34/E26/out-*.txt`): per-rev gate
  bisect of `68447af..52ebd48` (13 commits). `68447af` → findings=8 (`dangling=1`, `other=7`,
  `reports=86`; reproduces the committed record today → no fleet-root live-state artifact);
  `aea0525305167b8765ce36a3f20e68b1996274b8` → findings=7 (`dangling=0`, `other=7`; capture
  `census/round-30/waves/w1/deliver-c1-literal-history.tsv` committed, resolving the one dangling
  pointer); `936efc8a0f5a6a0d38a7d6ddb7d28f7a96273265` → findings=0 (the 7 LG-SEAT-UNCARRIED
  carried); `8024b54…` (r31 gate-precision) and its parent `52ebd48…` → findings=0 (gate-binary
  change is NOT the drift cause); `98e5203…` (r32) → transient 1×LG-FROZEN-PIN, fixed before base;
  `9c76c72…` (base) → findings=0. `8024b54`/`98e5203` are ancestors of list rev (YES/YES).
- **Blockade 1 (peer-identified, verified): the judge's `same` branch requires the cause to touch
  an item file.** Frozen `census/round-34/c1-counter.py` at list rev, `judge()`:
  `if rrun == "same": names = git(root,"show","--name-only","--format=",cause); if not set(names)
  & set(item["files"]): return … "BAD-ROW(cause touches none of the item files)"`, followed by
  `held=holds(…parent…); stops=holds(…cause…); need held is True and stops is False`. On the
  list-rev ancestry the ONLY commit touching `census/round-30/c2-counter.py` is `d4928ec`
  (creation; `git log --oneline 2b0171e -- census/round-30/c2-counter.py` → d4928ec alone;
  `git show d4928ec^:…` → "path exists on disk, but not in d4928ec^"; the `--all` hits `12b3439`/
  `14f93e7` are duplicate orphan commits, NOT ancestors of list rev). At `d4928ec^` the counter
  does not exist → `holds` returns None → `held is not True` → BAD-CAUSE. So no `same`
  restatement for E26 can be engine-accepted; my earlier `aea0525` proposal fails the file-touch
  check (aea0525 touches only `census/round-30/{records,waves}` files).
- **Blockade 2 (new): A1(c) exact binding + the counter's self-rev print makes any
  unmodified-argv restatement self-referentially impossible.** Amendment A1(c) (`preregistration`
  amendment log): "a restated `statement` must equal the run's collapsed LAST digit-bearing output
  line". Frozen judge: `ok = … collapse(last_digit_line(lines)) == target`. But
  `census/round-30/c2-counter.py:116-117` prints `… regress=… rev={a.rev}` — the measured rev's
  own hash — in that last line. A restatement row is committed *inside* the landing commit L, and
  at the landing reading the run's last line carries `rev=L`; the row cannot contain L's own hash.
  Impossible at the landing reading (and at the tip reading whenever tip ≠ landing). The
  `RESULTS:` binding cannot substitute: the c2-counter emits no `RESULT ` lines, and `RESULTS:…:0`
  is refused.
- **The only engine-accepted route is dishonest.** An argv-correction whose corrected argv pipes
  the counter through `sed -E 's/ rev=[0-9a-f]{40}$//'` names the row's own file
  (`c2-counter.py` — passes the basename check), needs cause `393b011a8221259abe6825fc3b637fcdc1b0e1eb`
  (verified: the exact current line 345 text is absent at its parent `f732978506f3fa8ef32d4af1b4ee5bc962603aaf`
  and present at `393b011`; the original argv fails at `393b011` — gate findings=0 probed;
  `393b011` is an ancestor of list rev), and then the stripped last line equals the quoted
  statement at both landing and tip. Engine-accepted — but it deletes the rev provenance stamp
  from measured output, i.e. it makes the row quote a line that never existed in raw output,
  violating the preregistration's verbatim-quote clause in spirit (cf. r30 A3 "banners refused";
  the provenance stamp exists precisely to prove which revision was measured). A canonical judge
  must reject it; it is reported as an attack surface, not a route.

## Findings

1. **W1's mismatch finding stands** (real, deterministic, correctly classified value drift).
   What W1 did not state — and what this seat first got wrong — is that the correction route is
   not merely unexecuted but **unexecutable by honest means under frozen bytes**:
   Blockade 1 (same-branch file-touch rule; structurally dead — the sole ancestry-touching commit
   is the counter's own creation, whose parent yields `held=None`), and Blockade 2 (A1(c)
   exact-binding vs the counter's `rev={a.rev}` self-print: the quoted line would have to embed
   the measured commit's own hash). Both verified against the frozen judge/counter bytes and by
   probe.
2. **Peer challenge upheld.** `SoujiR34a2`'s objection (aea0525 → BAD-ROW, cause touches none of
   the item files) is confirmed; the correction generalizes it: no same-cause exists at all.
3. **Cross-item structural hazard (for the integrator).** Blockade 2 is not E26-specific: it
   blocks honest restatements of EVERY item whose counter prints `rev=` in its last digit-bearing
   line. Per W1's q76 receipt that includes E23a, E23b, E24, E27, E29, E31, E32, E33 (E28's r31
   counter prints no `rev=`). Any of those that turn out to need restatement is likewise honestly
   unrestateable.
4. **Engine hole (for the canonical judge / a stricter future freeze).** The frozen judge's
   argv-correction branch never re-runs the corrected argv at the cause (it checks the ORIGINAL
   argv there) and does not refuse shell pipes/metacharacters in the corrected argv, so a
   corrected argv can alter measured output (strip provenance, banners, reorder) and still be
   engine-accepted. `tests/fixtures/r34-c1-junk.py` (A4/A5) tests foreign-script corrections and
   vacuous RESULTS, not output manipulation. A fixable defect: refuse corrected argv containing
   shell metacharacters outside the frozen template, or require the quoted statement to match a
   line the unmodified row script can print.
5. **Process note.** The r34 freeze already forbids amendments after counter data exists, so the
   honest disposition of E26 is a judgment-level ruling (record the mismatch as a frozen
   instrument/statement-binding defect, as with E25's seat), not a stricter amendment.
6. Forward-hazard and enumeration-hypothesis findings from the first pass remain valid and are
   retained in the Attack log below (SCORECARD citation pointers; "at the C2 landing commit"
   historical pinning).

## Attack log

- Read frozen row (`c1-items.tsv:71`), preregistration incl. amendment log A1(c)
  (`census/round-34/preregistration.txt`), W1 receipts, committed controls and r30 record,
  counter/gate source, and the frozen judge (`git show 2b0171e:census/round-34/c1-counter.py`,
  `judge()` restatement block, `run_item`/`holds`/`last_digit_line`).
- Executed read-only per-rev gate probes (13-commit bisect of `68447af..52ebd48`; commands and
  raw outputs in `/fast/scratch/hyaku/souji-r34/E26/`).
- Verified Blockade 1: `git log --oneline 2b0171e -- census/round-30/c2-counter.py` (→ d4928ec
  only); `git merge-base --is-ancestor` for `12b3439`/`14f93e7` (NO — orphan duplicates);
  `git show d4928ec^:census/round-30/c2-counter.py` (absent → `holds`=None at parent).
- Verified Blockade 2: `c2-counter.py:116-117` `rev={a.rev}` print; judge statement check
  `collapse(last_digit_line(lines)) == target` (exact equality; `collapse` is whitespace-only).
- Verified the dishonest route's mechanics: line authorship (`f732978` lacks the exact line,
  `393b011` has it, `2726c3d` has it; `393b011^` = `f732978`); original-argv failure at
  `393b011` (gate findings=0, probed).
- No lane or fleet-root file modified; no commits; scratch < 2 MB.

## Deliveries

- This report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/AttackE26.md`
  (corrected after peer challenge; supersedes the route-open claim of the first pass).
- Seat report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/SwarmCritic21.md`.
- Probe artifacts: `/fast/scratch/hyaku/souji-r34/E26/` (`out-*.txt`, `gate-*.py`).
- Revisions referenced: base `9c76c7222a8abff027af42e37f0d160d52526bba`; list/counter re-pin
  `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; landing `68447afef62e4761249af55a2467657f04046537`;
  semantic drift `aea0525305167b8765ce36a3f20e68b1996274b8`; carry `936efc8a0f5a6a0d38a7d6ddb7d28f7a96273265`;
  row author `393b011a8221259abe6825fc3b637fcdc1b0e1eb` (parent `f732978506f3fa8ef32d4af1b4ee5bc962603aaf`);
  counter creation `d4928ec`.
