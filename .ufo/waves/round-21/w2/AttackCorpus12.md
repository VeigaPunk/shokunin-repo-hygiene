# AttackCorpus12 — C1 classifier comparison

**Result:** no disagreement found in this bounded corpus. I independently labelled all 113 read/grep/glob tool-call rows before inspecting the classifier; the TSV is `./.ufo/waves/round-21/w2/AttackCorpus12.tsv` (actual tab-separated header and rows): 95 `OK`, 18 `UNSEEN`, 0 `FLAG`.

## Inventory

| Transcript export path | Calls | OK | UNSEEN | FLAG |
|---|---:|---:|---:|---:|
| `final/AuditCase16.txt` | 1 | 1 | 0 | 0 |
| `final/InputCase07.txt` | 1 | 1 | 0 | 0 |
| `final/InputCase18.txt` | 3 | 3 | 0 | 0 |
| `final/ReopenRefs.txt` | 14 | 14 | 0 | 0 |
| `recovery-final/ConsumerReadme.txt` | 10 | 8 | 2 | 0 |
| `recovery-final/F5Authority.txt` | 21 | 18 | 3 | 0 |
| `recovery-final/GrantPatch.txt` | 17 | 14 | 3 | 0 |
| `recovery/GrantTraversal.txt` | 19 | 17 | 2 | 0 |
| `recovery/InputR13Fixtures.txt` | 27 | 19 | 8 | 0 |
| **Total** | **113** | **95** | **18** | **0** |

`UNSEEN` rows have a clipped target component/selector, or a clipped grep pattern with no complete explicit target visible. The two `ConsumerReadme.txt` semicolon-separated greps each have an absolute first path and a clipped second path; no visible component is a relative outside-lane target. Error-result calls were retained as attempts (including `ConsumerReadme.txt:48` and `F5Authority.txt:59`).

## Pinned classifier trace

I inspected the pinned base `522dcd768ca90afe166532d37d306d3df70aeea5` source, not an executed classifier:

- `tools/souji-seat-audit.py:377–402`, `implicit_root_read`, implements path selection and normalization. For grep it takes the last ` @ ` target first, then the last legacy ` in ` target; without either it returns no target for clipped args and `.` for complete args. It splits `;` components, skips empty/clipped components, strips read selectors, exempts `/`, `~`, and URI targets, then lexically normalizes relative paths at `fleet` and returns an outside-lane component.
- `tools/souji-seat-audit.py:455–461` invokes that predicate for read/grep/glob and emits `V-READ-ROOT` as minor.
- `tools/souji-seat-audit.py:81`, `:409–421` identifies rendered calls, strips read-export line-number prefixes, counts attempts, and records tool arguments/status. The read-root branch is not conditioned on success status.

This matches the frozen rules I applied: `@` precedence over legacy `in`, path omission as implicit fleet-root grep when complete, component-wise semicolon handling, lexical containment, and conservative handling of visible truncation. The read-selector expression at `:394` includes `:conflicts` (and `:raw`, `:img`, numeric/range/comma/time suffix forms); URI matching at `:396` uses `re.IGNORECASE`.

On the 113 labelled calls, every complete explicit target is absolute or a URI. The classifier therefore predicts no `V-READ-ROOT` finding here; its no-finding result on the 18 clipped rows agrees with `UNSEEN`, not with a clean `OK` claim. There are no oracle `FLAG` rows to test positive recall in this sample, and the corpus contains no direct positive test of relative lexical resolution, a legacy `grep(PATTERN in PATH)` call, a mixed-case URI, or a `:conflicts` selector. Those branches agree by source inspection but remain unexercised by these transcript examples. This is not a precision/recall certification.

## Evidence and limits

The source searches were read-only `git grep` queries against the pinned file for `implicit_root_read`/`V-READ-ROOT` and for `CALL_RE`/line-prefix/status handling; they returned the cited source lines. No classifier, tests, or other target code were executed, and no tools were installed. No LSP device is exposed in this session; this is a bounded textual source comparison, not a claim of LSP-backed semantic proof.
