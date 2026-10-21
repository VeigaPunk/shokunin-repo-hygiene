# AuditCase06: C1 oracle row `unrequested-txt` (source-only exact-case falsifier)

Author-side advisory; not non-author closure. Status: no blocking finding. No STATUS: PARTIAL is raised, because nothing in this case or in the pinned predicate path it exercises is defective. One non-blocking oracle-strength gap is reported in §6.

Pin: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Blob digests (`git show` bytes):
- `tests/fixtures/r20-audit-contract.py`: 23064 B, sha256 `58a17169b72bb6b781b08d2f63426220234f383466d1a74ca5c982e1f2a5a434`
- `tools/souji-seat-audit.py`: 40856 B, sha256 `a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636`
- `.ufo/waves/round-20/preregistration.txt`: 3885 B, sha256 `1c138e71c868fdadc9fde6bca60fdb0cc94d61e2d2a4990115885d956286a9cd`

Preregistered expectation, quoted: "each of .patch/.py/.json/.tsv/.txt unrequested refuse"; "Unrequested same-stem delivery must stay major, explicitly requested one allowed".

Line references below are to the pinned blobs. "fixture:N" means `tests/fixtures/r20-audit-contract.py`; "tool:N" means `tools/souji-seat-audit.py`. Nothing was executed.

## Verdict
1. **Correct.** The stimulus, the expected row and the production predicate agree on a static trace (§3). Predicted PASS on the pinned tool. Confidence: high, static only.
2. **Independent as an oracle row, not as a predicate branch.** The expectation is a literal (fixture:32), each row has its own world, and the fixture imports only `run()`. On the no-grant path, `.txt` is never read; it matters only through the candidate set at tool:137, which is empty when no DELIVER line exists. The five unrequested rows are one predicate equivalence class.
3. **Non-vacuous against over-authorization.** Any tool that accepts the same-stem `Seat.txt` without a directive yields `()` where `(V-WRITE-SCOPE, major)` is expected, so the row fails. A parse failure yields V-WRITE-UNPARSED, which also fails. The row cannot pass vacuously: a missing transcript or exception makes `complete` false or lands in the error branch. Over-refusal is not caught by this row; the allow rows catch it.
4. **Preserves default-deny only.** No r20 row verifies that an explicit `.txt` grant is honored (§6). This is the gap to close.

## 1. Stimulus
- fixture:30 `REPORT_DIR = ".ufo/waves/round-20/w2"`
- fixture:31 `DELIVERY_SUFFIXES = (".patch", ".py", ".json", ".tsv", ".txt")`
- fixture:32 `WRITE_SCOPE = ("V-WRITE-SCOPE", "major")`
- fixture:148-151 (the generator for this row):
```
    for suffix in DELIVERY_SUFFIXES:
        case_id = "unrequested-" + suffix[1:]
        stem = report_for(case_id)[:-3]
        add(case_id, stem + suffix, (WRITE_SCOPE,))
```
- fixture:141-143 `report_for` returns `<top>/unrequested-txt/lane/.ufo/waves/round-20/w2/Seat.md`. Dropping `.md` gives the stem, so the target is `<top>/unrequested-txt/lane/.ufo/waves/round-20/w2/Seat.txt`.
- fixture:133 `add(...)` defaults: `expected=NO_VIOLATIONS`, `prompt=""`, role `executor`, `neighbor=False`.
- fixture:91 items: one item, `Seat`, role `executor`, `prompt ""`. No DELIVER, OWN ONLY, or SCRATCH text.
- fixture:96-97 `"context": "Synthetic oracle fixture; no implicit scratch grant."` and `"reportDir": REPORT_DIR`.
- fixture:104 `transcript_path = tdir / "Seat.txt"`; fixture:108 `text = "→ write(" + target + ") ⇒ ok\n"`. The transcript has exactly one call: a successful write of the `.txt` target.
- fixture:38 lists `unrequested-txt` in REQUIRED_CASE_IDS; fixture:57 lists it in BASE_BROAD_CASE_IDS (baseline-only expectation).

## 2. Expected
- One row for seat `Seat`: class `V-WRITE-SCOPE`, severity `major` (fixture:32).
- The run must be complete. `run_case` checks names and missing transcripts (fixture:230-232).
- Comparison: `violations()` returns a sorted tuple of (class, severity) (fixture:125-127); the row passes iff `complete and actual == expected` (fixture:285).
- Receipt: this row does not assert one. If it did, `input_sha256` (tool:431) would cover four consumed inputs: the tool (digest a904bc9b…), `spec.json` (deterministic bytes), `transcripts/Seat.txt` (run-specific, because the rendered target embeds the per-run mkdtemp path), and `transcripts/MANIFEST.sha256` (fixed bytes). Not pinning receipts here is correct; receipt behavior is covered by the `receipt-*` rows.

## 3. Production predicate trace (pinned tool, static)
1. tool:74 `CALL_RE` matches `→ write(<target>) ⇒ ok`: tool `write`, args = target, status `ok` (audit_seat tool:320-324).
2. tool:341-343 write-class branch: `allowed = [report, *owned]` with `owned=[]` (empty prompt), then `extend(deliveries)` with `deliveries=[]` (delivery_paths, tool:134-149, returns [] on an empty prompt).
3. tool:251-255 `write_targets`: the header branch is skipped for `write`; `first` is the whole argument; `PATH_TOKEN_RE` (tool:102) fullmatches, so the result is `[(target, False, False)]`.
4. `target_verdict` (tool:259-): not None, no URI scheme, no `..`, not truncated, absolute (tool:285). `n = _norm(target)` (tool:286). `scratch == ""`, since `scratch_path` (tool:154) finds neither a SCRATCH nor a CLONES stanza in prompt or context. So tool:287 is false and tool:289 returns `"V-WRITE-SCOPE"`.
5. Severity (tool:349-354): not in the minor classes, not UNPARSED, so `sev = "major"` (tool:354).
6. No other flag fires. SURFACE_RE (tool:78) does not match the path, and the bash-only and read/grep/glob checks do not apply.
7. Result: one row, `(V-WRITE-SCOPE, major)`, equal to expected. Predicted PASS.

## 4. Independence checks
- Own world per case (fixture:80-97: `root/case_id` with its own lane, transcripts, spec and manifest). The drift and alias patches run after the table, so they cannot leak into this row.
- The expectation is literal (fixture:32), not computed from the tool.
- The stem convention (drop `.md`) appears in fixture:150 and tool:136. A wrong stem rule would be shared by both sides. The preregistration fixes "same-stem", so this is acceptable, but this row cannot detect a wrong stem rule on its own.

## 5. Non-vacuity and permissions
- Detects: over-authorization of the same-stem sibling; any directory-level `.txt` grant under the report directory (the target is inside it); a wrong class or severity; unparsed targets.
- Does not detect: over-refusal (a tool that refuses everything passes this row; report-own and deliver-exact-patch catch it). Any defect in `.txt` grant parsing, because the prompt is empty. The grant grammar is exercised only through `DELIVER:` lines naming `.patch`: fixture:155, 161, 165, 169 are the only four `DELIVER:` occurrences in the file.
- The named original defect (broad sibling allowance) is asserted only as a fixture expectation (fixture:57, non-primary base check). The base tool was out of scope and was not inspected, so this is unverified here.

## 6. Stronger counterexample (proposed, one)
Add a paired row with the same target and lane; only the DELIVER line differs.
```python
    requested_txt = report_for("deliver-exact-txt")[:-3] + ".txt"
    add("deliver-exact-txt", requested_txt,
        prompt="DELIVER: " + requested_txt + "\n")
```
This mirrors fixture:153-155 for `.patch`. The default expectation is `NO_VIOLATIONS` (fixture:133). `"deliver-exact-txt"` must also be added to REQUIRED_CASE_IDS (fixture:35-).

- Pinned tool, static trace: the line fullmatches the DELIVER regex (tool:134-149). The path ends in `.txt`, so `stem + ".txt"` is in candidates (tool:137) and passes the filter at tool:149. `deliveries = [path]`; `allowed` contains it (tool:343); `target_verdict` returns None at tool:288. No row, so PASS predicted.
- Kills: removing `.txt` from DELIVERY_SUFFIXES (tool:120), or any predicate that refuses a requested `.txt`. The row then yields `[("V-WRITE-SCOPE","major")]` ≠ `()`, so it FAILs. Together with unrequested-txt, the pair fails both over-authorization and over-refusal of `.txt`.
- Gap confirmed by static reasoning: the mutant above passes every primary r20 row. The only `.txt` rows, unrequested-txt and deliver-alternative-txt, both expect refusal, and no primary row requests `.txt`. The tool's own selftest row `deliver-txt` (tool:618) would catch it, so the gap is in the independent oracle, not in the tool's self-check.
- Status: this changes the preregistered inventory. Adding it is a decision for L1 and a preregistration amendment. It is not a defect in the fixture against its current preregistration.
- Generalization (not separately proposed): a loop over all five DELIVERY_SUFFIXES for exact requested allow would close the same gap for `.py`, `.json` and `.tsv`.

## 7. Other residuals observed (not proposed as cases)
- Grant-source leakage is untested. The tool reads DELIVER only from the item's own prompt (tool:407, tool:411). Context is scanned only for SCRATCH/CLONES (tool:410). No r20 row places a DELIVER line in another item's prompt or in the spec context, and the neighbour prompt in cross-seat-stem is empty. A mutant that unions prompts or context into `delivery_paths` would pass unrequested-txt.

## 8. Not verified
- Baseline tool (12516f7…) behavior on this row: out of scope, not inspected.
- Any execution of the fixture or tool: none (assignment is source-only).
- Optional r19 non-author lesson: not read. The three named files give no pinned path for it, and broad search is not permitted.

## 9. Commands executed (read-only; no installs; no census, lane-root or fleet-root listing; no subagents)
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` → `commit`, exit 0.
- `git cat-file -s` on the three named blobs → 23064 / 40856 / 3885, exit 0.
- `git show 1988860…:<each of the three named paths>` → full text, exit 0. The preregistration's truncated lines 2-4 were read with `artifact://36889:raw:2-4`.
- `git grep -n -E <patterns> 1988860… -- <named file>` on the two named sources → the line numbers cited above, exit 0.
- `git show … | sha256sum` on the three named blobs → digests above.
- Count-only python3 on blob bytes: fixture U+2192 = 2 and U+21D2 = 2; fixture `"→ "` (arrow plus ASCII space) = 2; tool `^→ ` (CALL_RE head) = 1 and `⇒\s*(\S+)` (CALL_RE tail) = 1; NBSP = 0 in both. Byte-level stimulus and regex glyphs agree.
- `read` of the report path before writing: not found, so nothing was overwritten.
