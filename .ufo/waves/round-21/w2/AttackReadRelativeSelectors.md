# AttackReadRelativeSelectors — C1 boundary: raw-suffix-after-range read selectors

- Seat: SoujiR21.AttackReadRelativeSelectors (leaf, read-only; no ALLOWED-EXEC — nothing executed, no installs; pacman pause untouched).
- Target: pinned build `522dcd768ca90afe166532d37d306d3df70aeea5`, `tools/souji-seat-audit.py` (`implicit_root_read`, `audit_seat`), `tests/fixtures/r21-read-root.py`; oracle texts `.ufo/waves/round-21/preregistration.txt` (C1) and `.ufo/waves/round-21/clarification-before-measurement.txt`.
- No `lsp` device exists in this seat's tool inventory; no language server answered. Semantic checks below are pinned-rev `git grep -n` / `git show` text evidence (recorded unavailability; grep output is not semantic proof).
- All line quotes are from `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 522dcd768ca90afe166532d37d306d3df70aeea5:tools/souji-seat-audit.py` (and the fixture equivalent). Execution-requiring claims are labeled static.

## Findings (by severity)

### F1 — LOW (routed, adjacent class): a suffix past the lane root defeats the root-read check; both classes abstain
- Inputs: `read(souji-shokunin:17-33)`, `read(/home/vgpnk/Projects/shokunin/souji-shokunin:17-33)`, `glob(souji-shokunin/**)`.
- V-READ-ROOT correctly abstains per the C1 letter: the stripped component resolves to the lane root, and `souji-seat-audit.py:400-401`
  ```python
  if resolved != lane_root and not resolved.startswith(lane_root + "/"):
      return component
  ```
  treats `resolved == lane_root` as inside the lane.
- But the only other class that covers root-rooted read/glob calls is V-RECURSIVE, checked at `souji-seat-audit.py:459-461`:
  ```python
  a = args.rstrip("…").rstrip()
  if a.endswith(lane) or a.endswith(fleet) or a.endswith(lane + "/") or a.endswith(fleet + "/"):
      flag("V-RECURSIVE", "minor")
  ```
  Any argument text continuing past the root — a read selector (`…:17-33`) or a glob tail (`/**`) — breaks all four `endswith` alternatives, so a whole-lane-root directory read or whole-lane glob renders zero flags. Directory reads with paging selectors are real harness behavior (the read tool lists directories and pages listings with `:N-M`).
- Fleet-root equivalents are NOT affected: `read(.:2)` / `read(:50-)` strip to `.`/empty and resolve at `fleet`, outside the lane, so V-READ-ROOT flags them (line 400-401). The hole is exactly the lane-root-rooted, suffix-past-root forms.
- Attribution: class owner is V-RECURSIVE, which the prereg freezes ("existing V-RECURSIVE / V-SURFACE untouched"); V-READ-ROOT's contract only flags outside-lane resolutions. This is therefore a routed pre-existing observation for L1, not a C1 falsification.
- Fixture detection: NO. No fixture case asserts either form; `absolute-root-control` (tests/fixtures/r21-read-root.py:56, bare `LANE`, expected False) stays correct, and the r20 selftest's `recursive-read-lane-root` is bare-form only. Static expectation; not executed.

### F2 — LOW (fixture detection gap): no `./`-prefixed relative read case
- Assigned input `read(./tools/x:2,9:raw)` is flagged correctly today (proof in F4), but the fixture's comma+raw shape, `relative-comma` (tests/fixtures/r21-read-root.py:30, `corpus/x.md:2,9:raw`), never exercises a dot-leading component; the only dot cases are bare `.` (`dot-glob`, `dot-read`, lines 20-21 region). A regression that special-cased `.`-leading components (e.g. skipping them like the bare-`.` truncated form, or mis-normalizing `./`) would pass the fixture while breaking this exact boundary input. Current code is provably correct via `os.path.join` + `os.path.normpath` (line 398-399), so this is a detection-power gap, not a live defect. Suggested one-line case for L1: `('dot-slash-read', 'read', './tools/x.py:2,9:raw', True)`.

### F3 — LOW (prereg-letter deviation): `re.IGNORECASE` on the URI predicate
- Prereg C1 pins the URI form as `^[a-z][a-z0-9+.-]*://`. Implementation `souji-seat-audit.py:396`:
  ```python
  or re.match(r"^[a-z][a-z0-9+.-]*://", component, re.IGNORECASE)):
  ```
  An uppercase-scheme relative read (e.g. `X://y`) is skipped as a URI where the frozen oracle rule labels it a relative target → flag. Direction: suppressor (false-negative vs the letter).
- Bound, empirically: `git -C <lane> grep -nE '\([A-Z][A-Za-z0-9+.-]*://' 522dcd768ca90afe166532d37d306d3df70aeea5 -- census/round-20/transcripts` → exit 1, zero matches. No rendered r20 call shape is affected; the deviation can only bite synthetic input, so the C1 "after set == oracle" measurement is not endangered by any observed corpus shape.
- Fixture detection: NO — all URI cases (`skill`, `agent`, `artifact`, `https`, `uri-plus`) are lowercase-scheme.

### F4 — PROOF (primary deliverable): no FP/FN on the exact assigned inputs
1. `read(corpus/x:raw:2-4)` → **flagged, correctly** (V-READ-ROOT, minor, target `corpus/x`).
   - `CALL_RE` captures args `corpus/x:raw:2-4`; read branch (no ` @ `/` in ` logic applies); single `;`-component, no `…`.
   - Strip regex at `souji-seat-audit.py:394`
     ```python
     component = re.sub(r":(?:(?:raw|img|conflicts)|[-\d,+hms]+)(?::(?:raw|img|conflicts|[-\d,+hms]+))*$", "", component)
     ```
     matches the tail `:raw:2-4` anchored at end: first segment `raw` (keyword alternative), second segment `2-4` (class `{-,digit,,,+,h,m,s}`), `$`. Component becomes `corpus/x`; fails the `/`/`~`/URI skips (line 396 is `^`-anchored); `os.path.normpath(os.path.join(FLEET, "corpus/x"))` = `/home/vgpnk/Projects/shokunin/corpus/x` → outside `souji-shokunin` → line 400-401 returns it → flag at lines 455-458. Exactly what C1 requires (complete relative target resolving outside the lane).
2. `read(./tools/x:2,9:raw)` → **flagged, correctly** (target `./tools/x`).
   - Line 394: first segment `2,9` (class includes `,`), second segment `raw` → component `./tools/x`. `component.strip()` (line 391) keeps `./`; the URI skip cannot fire (`.` first char); `normpath(FLEET + "/./tools/x")` = `/home/vgpnk/Projects/shokunin/tools/x` → outside the lane → flag. Correct: only the `<lane-basename>/…` fleet-relative form legitimately passes; a bare lane-internal subpath typed at fleet cwd must flag.
3. Family closure — every documented selector form is handled by line 394: `:N`, `:N-M`, `:N-`, `:-N`, `:N+M`, comma lists (`:5-16,960-973`, `:19,59`, `:2,9`), `:raw`, `:img`, `:conflicts`, time forms (`:1h5m42s`, `:90s`, `:01:23`), and combos `:2-4:raw`, `:raw:2-4`, `:17-:raw`, `:raw:2-4:raw` (keyword or class per `:`-segment).
4. Invariance theorem (bounded): for `tool == "read"`, any strip mismatch preserves the verdict. Premise: the harness parses a greedy trailing selector, so the true path is exactly the pre-colon prefix — what the regex extracts. A stripped component is a prefix of the original ending before a `:`; the matched suffix contains no `/` (neither the keyword alternatives nor the class include one), so it only extends the final path segment. The three verdict predicates — final-segment containment under `lane_root` (line 400-401), the `startswith(("/", "~"))` prefix checks (line 395), and the `^`-anchored URI match (line 396) — are all invariant under appending characters to the final segment (no `..` can be created or destroyed; a welded `..:2` is a regular segment name, and in that case the unstripped reading contradicts the harness's own greedy selector parsing, so the stripped reading is the true one). Consequence: raw-suffix-after-range stripping errors can never create a missed or spurious flag; worst case is a wrong `target` string in the JSON row (e.g. a literal-colon filename `data:raw` reported as `data`), severity unchanged.
5. Fixture detection: the selector shapes of both inputs are covered — `relative-range` (l.28), `relative-raw` (l.29, raw-first: `.ufo/x.md:raw:2-4`), `relative-comma` (l.30, comma+raw), with negatives `lane-relative-range` (l.41) and `absolute-root-control` (l.56). Both exact inputs pass the current implementation and a regression of raw-first or comma-raw handling would be caught — except the `./` prefix dimension (see F2). Statically, the new class adds zero flags over the 118 selftest cases (every selftest read/grep/glob arg is absolute or in-lane), so the harm guard `SELFTEST pass=118 fail=0` is expected to hold — static expectation, not an observed run.

## Residual risk
- F1 leaves whole-lane-root read/glob enumeration unflagged under both classes (minor severity if ever classed); exploiting it requires a seat to page a directory listing past the root name — unusual but legal harness usage.
- Strip-suffix over-greed (line 394 also strips non-selector tails like a literal `:raw` filename component) is verdict-invariant per F4.4 but corrupts the reported `target` text in auditor JSON — cosmetic only.
- `grep` patterns containing " in " + an in-lane token resolve to that token and abstain where the implicit-cwd reading would flag; the clarification pins the historical-renderer treatment explicitly, so this is accepted ambiguity, noted only.

## Verification gaps
- Read-only seat: the fixture run, `--selftest`, and the 128-transcript (final + recovery-final) oracle comparison are runtime evidence owned by executor/reviewer seats; all "expected" statements above are static traces, not observed passes.
- Corpus inspected only via the single uppercase-scheme grep (F3); the per-call 1347-call oracle equality is not re-derived here.
- No installs performed (nothing needed); no pacman transaction touched.
