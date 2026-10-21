# AttackCorpus13 — C1 classifier calibration

**Axes:** (1) independent per-call label fidelity; (2) agreement with the pinned classifier predicates; (3) whether this corpus slice exercises the positive FLAG boundary.

**Result:** Labeled all **113** read/grep/glob call lines from the nine named transcripts before opening the classifier. The DELIVER TSV contains **100 OK, 13 UNSEEN, 0 FLAG**. I found **no disagreement** between these labels and a source-only comparison with the pinned C1 implementation. This is not an executed classifier run or a census-wide precision/recall claim.

## Independent labels

The TSV is `AttackCorpus13.tsv`; it uses transcript-relative paths and 1-based physical line numbers. Counts by transcript:

| Transcript | OK | UNSEEN | FLAG |
|---|---:|---:|---:|
| `final/AuditCase17.txt` | 1 | 0 | 0 |
| `final/InputCase09.txt` | 1 | 0 | 0 |
| `final/MutateProtectedAncestor.txt` | 3 | 0 | 0 |
| `recovery-final/ErrataCarry.txt` | 9 | 1 | 0 |
| `recovery-final/ErrataFinal.txt` | 19 | 7 | 0 |
| `recovery-final/GrantScratchForeign.txt` | 14 | 0 | 0 |
| `recovery/F5ReadSet.txt` | 20 | 2 | 0 |
| `recovery/GrantPatch.txt` | 14 | 3 | 0 |
| `recovery/OutputRecordedScope.txt` | 19 | 0 | 0 |
| **Total** | **100** | **13** | **0** |

Complete visible targets in this slice are absolute paths or URIs, so none is a V-READ-ROOT case under the frozen rule. The 13 UNSEEN rows have literal `…` cuts in the recorded target, or a cut grep argument with no visible target; they are not silently treated as OK. Error-status calls remain included (including `ErrataCarry.txt:65`, `GrantPatch.txt:61`, and `OutputRecordedScope.txt:71`); status does not remove a recorded call from the classification pass.

## Pinned-source comparison

`tools/souji-seat-audit.py` on the working tree has the same blob ID as `522dcd768ca90afe166532d37d306d3df70aeea5`: `6cf3a85b01b6ca883a1e6ea226cdec65278da0f4` (observed from `git rev-parse <rev>:tools/souji-seat-audit.py` and `git hash-object <absolute file>`). No classifier or target code was executed.

Direct source read, `tools/souji-seat-audit.py`:

- `CALL_RE` at L81 recognizes the rendered `→ tool(args) ⇒ status` form; `audit_seat` increments its call count at L409–L415 without filtering on status. It invokes the C1 check for `read`, `grep`, and `glob` at L455–L458.
- `implicit_root_read` at L377–L402 implements the frozen target rules: grep uses the last ` @ ` first, then legacy ` in ` (L379–L386); a no-separator grep is implicit fleet root only when its args are complete (L385–L386). Targets are split on `;`, whitespace-trimmed, and components containing `…` are skipped (L389–L392). Read selectors including `raw`, `img`, `conflicts`, and numeric/comma ranges are removed (L393–L394). Absolute and `~` paths and case-insensitive URI schemes are excluded (L395–L397). Other targets are normalized against `fleet` and flagged only when the lexical result lies outside `lane` (L398–L401).
- Thus each of the 100 complete absolute/URI rows returns no root target, and each of the 13 cut rows is unclassifiable/no-flag in the implementation, matching the required independent UNSEEN treatment. No row enters the implicit-cwd grep branch or relative-path normalization branch; the slice does not test positive FLAG recall, legacy ` in ` behavior, or multi-component relative paths.

The LSP device is unavailable in this session: `read xd://lsp` returned `No such tool: xd://lsp`. Grep was used only to locate source lines; the predicate comparison above is grounded in the direct source read, not grep output.

No earlier oracle-label files were read. No tests, builds, or target programs were run; no tools were installed.

DELIVER: `.ufo/waves/round-21/w2/AttackCorpus13.tsv`
Report: `.ufo/waves/round-21/w2/AttackCorpus13.md`
