# AttackCorpus10 — full-code C1 classifier falsification

## Result

No disagreement was found between the independent labels and the pinned `implicit_root_read` predicate for the classifiable calls in the eight assigned transcripts. This is a bounded static comparison, not a claim that C1 passes on the full corpus: 19 calls have cut/ambiguous target text and are explicitly `UNSEEN`.

## Independent labels

I read the frozen C1 contract, `clarification-before-measurement.txt`, and `full-corpus-restoration.txt` before creating the oracle, and wrote the 113-row TSV before reading the classifier. The TSV includes every read/grep/glob tool invocation on the eight named transcripts, including failed reads; it does not import earlier oracle labels.

`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-21/w2/AttackCorpus10.tsv`

Counts: 113 total = 79 `read` + 34 `grep` + 0 `glob`; 94 `OK`, 0 `FLAG`, 19 `UNSEEN`.

| Transcript | Calls | UNSEEN |
|---|---:|---:|
| `final/AuditCase07.txt` | 3 | 0 |
| `final/AuditCase24.txt` | 3 | 0 |
| `final/InputCase05.txt` | 1 | 0 |
| `recovery-final/InputRegular.txt` | 18 | 6 |
| `recovery-final/SourceDiff.txt` | 21 | 2 |
| `recovery/ContainmentLimit.txt` | 39 | 9 |
| `recovery/FixtureOracle.txt` | 12 | 0 |
| `recovery/SourceRefs.txt` | 16 | 2 |

The 19 `UNSEEN` rows are visible truncations in a target component or selector, or a truncated grep argument with no complete target/separator. Rows with a visible `@` and a cut pattern remain classifiable only if their complete target is visible; a cut target component is `UNSEEN`. The `SourceRefs.txt:40` grep has a semicolon-separated target list with a visible absolute first component and a cut later component, so the whole call is `UNSEEN`. Failed attempts (`AuditCase07.txt:49-50`, `FixtureOracle.txt:67`, and `SourceRefs.txt:57`) are still counted and classified from their rendered targets.

## Pinned source comparison

After writing the TSV, I read `tools/souji-seat-audit.py` from pinned commit `522dcd768ca90afe166532d37d306d3df70aeea5` with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 522dcd768ca90afe166532d37d306d3df70aeea5:tools/souji-seat-audit.py`. The attacked symbol is `implicit_root_read`; no code or tests were executed.

- **Target extraction / precedence:** for `grep`, the source checks the last `" @ "` first, then the legacy `" in "` form, then treats a complete pathless call as `.`. This matches the frozen/clarified contract. The assigned visible grep calls use `@`; no complete legacy `grep(PATTERN in PATH)` example occurs in this subset. Two cut grep arguments without a visible separator are `UNSEEN`, not evidence of a pathless call.
- **Multi-path targets:** the source splits targets on `;`, strips each component, and skips an incomplete component containing `…`. That agrees with the oracle treatment of `SourceRefs.txt:40`; the visible first absolute component is not enough to classify its cut later component.
- **Read selectors:** the source strips supported trailing selector sequences (`raw`, `img`, `conflicts`, and documented numeric/range/time forms) before testing a read component. The visible selector-bearing reads in this set resolve to absolute or URI targets after stripping. No disagreement found.
- **Truncation:** incomplete components are skipped; pathless grep arguments containing `…` do not fall through to the implicit `.` target. This matches the lower-bound rule and all 19 `UNSEEN` labels. No truncated target was mislabeled `OK` or `FLAG` in the TSV.
- **Absolute, tilde, and URI exclusions:** absolute (`/…`), tilde (`~…`), and URI targets are exempt from `V-READ-ROOT`; URI detection is case-insensitive. All 94 classifiable targets in this subset are explicit absolute paths or URIs, so each is `OK`. Mixed-case URI spelling is not present in the subset; the case-insensitive behavior is established only by source inspection.
- **Relative resolution and implicit-root flag:** a complete relative target is joined to the supplied fleet root, normalized, and flagged only if outside the lane; a complete grep without an explicit target resolves to `.` and is flagged. No complete relative target or complete pathless grep occurs here. Therefore the lexical containment/escape branch has no in-sample positive case; this is the bounded reason the attack cannot establish its precision/recall on that branch.

**Disagreements:** none observed in the classifiable portion. **Static prediction only:** the pinned function would produce no `V-READ-ROOT` for the 94 `OK` calls and would emit no root finding for the 19 incomplete calls, consistent with the lower-bound oracle labels. This was not verified by running the classifier.

No LSP device is exposed in the mounted tool inventory; this report relies on direct pinned-source inspection, not grep output as semantic proof. No tools were installed or updated. No earlier oracle-label files were read.