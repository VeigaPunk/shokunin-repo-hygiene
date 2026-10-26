# Souji round 30 w1 — sibling-overlap scan (connector seat SwarmConnector31)

Scope: read-only scan of sibling lane surfaces for overlap with souji round 30's three claim surfaces.
Scan reference: fleet working tree at fleet HEAD `a7c6d0f1828099828a6ca0e01c2f6eb2b3f8c59c`; lane HEAD observed `df6afe817d096e4ad71ba2b9cc21a83f126eb658` (wave-1 landings in progress; this scan is lane-state independent). Souji's own files were excluded from corpus globs per the seat brief.

## Sweep inventory (negative claims carry their sweep)

- Files scanned: 21 `*/PROVINCE.md`, 19 `*/SKILL.md`, 21 `*/corpus/README.md`, 890 `*/corpus/knowledge/*.md`, plus `scripts/hyaku/jj-lane.sh` (952 files total).
- Command shape: `grep -rnF '<pattern>' */PROVINCE.md */SKILL.md */corpus/README.md */corpus/knowledge/*.md scripts/hyaku/jj-lane.sh` from `/home/vgpnk/Projects/shokunin`, souji lines filtered out; supplemental regex pass for `landing|\.ufo/waves/round-`, `keep[- ]ref`, and `souji-landing-gate|souji-capability|SHONEN`.

## Surface 1 — jj keep refs / `jj util gc` / `jj op abandon` / keep-ref expiry

Sibling hits: 2 files, 3 lines. None claims keep-ref *expiry* ground (what removes a `refs/jj/keep/*` ref and when).

| Lane | File:line | Subject | Contests souji C3? |
| --- | --- | --- | --- |
| kumitate | corpus/knowledge/jj-workspace-seat-containment.md:102 | workspace-seat cleanup; storage lifecycle of *abandoned commits* | No — adjacent mechanism citation |
| kumitate | corpus/knowledge/agent-isolation-substrates.md:57,59 | jj snapshot behavior (M1); keep-ref *creation* counts per op | No — creation-side measurement |
| mado | corpus/knowledge/tripwire-precision-r20.md:70 | write-tripwire classification; `jj git push --dry-run` writes | No — creation-side observation |

- kumitate jj-workspace-seat-containment.md:102 (verbatim, 16 words): "only `jj op abandon` + `jj util gc` or a separate clone excludes them from storage" — this names the op-log GC mechanism but asserts it for abandoned *commits'* object/op-log storage, not for `refs/jj/keep/*` refs. It is the nearest sibling citation to souji C3 and is complementary, not overlapping.
- kumitate agent-isolation-substrates.md:57 (verbatim): "one keep-ref, rewrites `.git/index`" — keep refs counted as a snapshot side effect (9→9 under `--ignore-working-copy` control, :59). Creation side only.
- mado tripwire-precision-r20.md:70 (verbatim): "measured: +1 op, `refs/jj/keep`" — a keep ref created by `jj git push --dry-run`. Creation side only.

Verdict: souji's C3 frontier (keep-ref expiry, `ground: F1`) is uncontested this round. No sibling entry states when jj drops `refs/jj/keep/*`.

## Surface 2 — landing gates / report discovery over committed wave captures

Sibling hits on the `census/round-` assigned pattern: 1 file, 2 lines — both *consumption* of souji's committed census reports, not claims over souji's gate surface.

| Lane | File:line | Subject | Contests souji C2? |
| --- | --- | --- | --- |
| tsukuroi | corpus/knowledge/adjacency-anchors-r19.md:185 (IN-090) | operative adjacency anchor citing `souji:census/round-12/connector.md:29` | No — cites souji's committed report as evidence |
| tsukuroi | corpus/knowledge/adjacency-anchors-r19.md:186 (IN-091) | operative adjacency anchor citing `souji:census/round-16/transcripts/w1/SiblingOverlap.txt:52` | No — cites souji's committed report as evidence |

Supplemental pass: no sibling file references `souji-landing-gate` or `souji-capability` (zero hits). The nearest sibling instrument family is kumitate-internal: `report-receipt-diff` (kumitate-shokunin/SKILL.md:636, diffs one round report against receipts that round committed) and the round-close gate (kumitate-shokunin/corpus/knowledge/round-close-gate.md) — both operate inside kumitate over its own reports/receipts; neither discovers reports from committed census captures of a gitignored `.ufo/waves/` tree.

Verdict: souji's C2 surface (committed-capture discovery + template/pointer mapping in `tools/souji-landing-gate.py`) is uncontested. Tsukuroi's IN-090/IN-091 are demand-side evidence that sibling lanes read souji's committed census paths.

## Surface 3 — capability-table literal agreement

Sibling `capability` hits are generic domain vocabulary (e.g. kaidoku's `error:capability_unavailable` tool-error strings; kengaku/kotoba "measured capability effects of prompt format", a kengaku↔kotoba routing boundary). None binds a bookkeeping capability table's stated runnable counts to committed command output.

The same *calibration idiom* as souji C1 is practiced lane-internally by three siblings — each over its own SCORECARD/SHONEN, none over souji's:

| Lane | File:line | Instrument | Contests souji C1? |
| --- | --- | --- | --- |
| kaidoku | SKILL.md:1263 | `tools/round-36/c2-counter.py`, R36-C2 calibration gate, guard baseline `cab59f22…` | No — kaidoku-internal (`--root <LANE>` = kaidoku) |
| kama | corpus/knowledge/self-assessment-at-writing.md:7 + corpus/README.md:440 | statement-form checks vs `SCORECARD.md`/`SHONEN.md` at frozen base via `git blame --line-porcelain`; frozen counter `.ufo/waves/round-29/count-c1.py` | No — kama-internal |
| revenger | SKILL.md:295 | `corpus/self_assessment_check.py --root <tree>` over its own corpus/SHONEN/SCORECARD | No — revenger-internal |

- kaidoku SKILL.md:1263 (verbatim, 11 words): "gate — R36-C2 calibration, self-assessment surfaces vs observed repo state".
- kama self-assessment-at-writing.md:7 (verbatim, 16 words): "Round 29 C1 checks only the statement forms extracted from lines of `SCORECARD.md` and `SHONEN.md`".

Verdict: souji's C1 surface (binding souji's SCORECARD table rows R01–R18 + SHONEN pointer tokens at souji's base `9420341d…` to committed command output) is uncontested; siblings own the same idiom for their own tables.

## Does scripts/hyaku/jj-lane.sh ever run `jj util gc` or `jj op abandon`?

No. `grep -nE 'util gc|op abandon' scripts/hyaku/jj-lane.sh` → exit 1, zero matches (empty sweep over all 841 lines). The helper's actual `"$JJ_BIN"` invocations are read/config/bookmark/workspace-free surface only: `config get` (:95,:111), `log --no-graph` (:148), `bookmark list --conflicted` (:203,:300), `git fetch` (:286), `bookmark set` (:310,:332,:340), `git push --bookmark` (:357), `status` (:394), `git init --colocate` (:431), `config set/list --repo` (:437-443). No GC, no op-log mutation anywhere in the fleet helper.

## Notes

- Tool defect observed: the harness `grep` tool returned "No matches found" for absolute-path globs (e.g. `/home/vgpnk/Projects/shokunin/*/corpus/README.md`) while a literal path over the same bytes matched; the scan above was run with `grep -F`/`-E` over shell globs instead. Reported at `xd://report_issue`.
- Tool installs this seat: none.
- No files outside the seat's write scope were touched; all writes are the two delivery files in `.ufo/waves/round-30/w1/`.
