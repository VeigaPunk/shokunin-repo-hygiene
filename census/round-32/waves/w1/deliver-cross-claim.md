# r32 w1 cross-claim connector deliverable (SwarmConnector42)

Read-only seat. Bytes opened this run: lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`, prereg `3ec84fc81b3243429c834a051880b0bcde06291c`, controls `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1` (worktree clean). No counter was executed; all findings are source-byte comparisons.

## F1 — C2→C1 coupling via C1 `run:` bindings (separability claim only partially holds)

C1's `run()` checks out REV, then overwrites **only the script blob** with `--base` bytes; every sibling file stays REV (`c1-counter.py:221-231`; docstring line 23 "The script is taken from the --base blob and run (no shell) in a private git clone --no-local at REV"). So a base-blob script that **consumes sibling tools/fixtures from disk** executes the C2-patched versions, and C2's edits can move C1's `S`.

Pairs where an enumerated C1 cell line names a script whose stem is also a C2 item:

| C1 item(s) | base line | script (stem on line) | C2 overlap |
|---|---|---|---|
| N35–N42 | 423 | `tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py` | exactly T30's argv; T30's file list includes **both** files, so C2 may change bytes C1 runs as "base" |
| N12 | 161 | `tests/fixtures/r17-jj-receipts.sh --tool-dir tools` (executes `$TOOL_DIR/souji-verify.sh`, `r17-jj-receipts.sh:128`) | T15 = `souji-verify.sh --selftest` (only selftest output is pinned) |
| N22–N24 | 314 | `tests/fixtures/r28-wave-evidence-capture.sh` | T27 (same argv) |

Note T30's own invariant (`s1==s0`) protects the **REV fixture + REV tool** combo; C1 runs **base fixture + REV tool**, a combo C2 never tests. If C2's patch touches the fixture, C1's run result is unconstrained by C2's gates.

Recommendation: bind N35–N42 via the cited records (`census/round-31/records/c2-after-v1.txt` etc., which A0(a) admits) rather than run; if run bindings are used, the L1 should re-run C1 against the final tip after C2 lands (a second-order check), or C2 should leave shared fixtures/tools byte-identical.

## F2 — C1 rows are unnamespaced: cross-round duplicate hazard, no last-row-wins, no post-landing repair

- The counter treats **any** row in the post-base tail matching `^\|\s*(?:N|L)\d{2}...` with the item's line as a binding; two rows ⇒ `BAD-ROW(duplicate)` (`c1-counter.py:262-263`; docstring line 12 "an item with two or more such rows is BAD-ROW(duplicate) (no last-row-wins)").
- r31's supersession block proves the same row shape recurs across rounds (`SCORECARD.md:361-363`; r31 residual: "The C1 supersession block is last-row-wins and unanchored: any later row-shaped line reusing an item id and base line silently replaces this round's binding."). If a later round reuses r32 ids N01–N43/L29 on the same lines, the final-tip re-measurement of C1 breaks.
- Within the round: appending a `withdrawn:` row over an existing binding also produces a duplicate, so there is **no honest in-round repair path** once C1 lands — the block must land complete. Wave 2 must not append "replacement" rows.

## F3 — C2 T03 / landing-gate family vs C1's appended SCORECARD rows: verified immune

`souji-declared-evidence.py` reads the declaration at `--rev` from git blobs (`read_declaration` → `tracked(rev)`/`blob(rev, relfile)` = `git show rev:path`; lines 64-87), never the worktree. The landing gate reads only committed bytes (`ls-tree`/`cat-file`; docstring "Files that need a real path for bash -n are written under a private tempfile.mkdtemp(dir='/var/tmp') snapshot removed in finally"). C1's appended rows at REV therefore cannot perturb T03 or T01/T02/T29/T30. The C1→C2 channel is closed; the open channel is only F1 (C2→C1).

## F4 — C3 fixture vs C2 sandbox rule

The r31 fixture already obeys scratch discipline: refuses unset/non-dir/inside-fleet `TMPDIR`, `mktemp -d "$TMPDIR/r31-jj-object-clock.XXXXXX"` (`r31-jj-object-clock.sh:64-80`). The new r32 fixture must mirror this guard. Enforcement gap: the r32 fixture is outside C2's frozen enumeration (new file, not at base), and C3's replays (L9/L12) run **without bwrap** with TMPDIR set — a hardcoded `/tmp`/`/var/tmp` write would fail no leg while violating the operator directive. Grep gate at delivery: no literal `/tmp`/`/var/tmp` in the fixture.

## F5 — M1 tool vs C3 leg L14: two independent parsers, equivalent today, drift-prone

`contract_bad()` (`c3-counter.py:83-104`) and `souji-record-contract.py:41-59` both require: every `RESULT` line carries exactly the contract keys in order, each value in its set (prefix matched by `startswith(prefix+" ")`). They are functionally equivalent for the frozen `c3-contract.txt`. Divergences:
- the tool admits `*` (any non-empty) / `#` (non-negative int) set members; the counter treats them as literal values — a future contract using wildcards behaves differently in the two guards;
- malformed contract: tool exits 2; counter flags all lines bad;
- L14 does not invoke the tool (no single source of truth; M1's red-before `m1-red-before.txt` already shows `lines=17 bad=4`, exit 1, matching the prereg claim).

The D1 class (value-outside-set) is caught identically by both; the **dangling-citation** variant (r30's D1: report citing a path absent at landing) is covered by neither M1 nor L14.

## F6 — Recurring mistake classes r28–r31 and r32 analogues

1. **vacuous / met-at-frozen-price** (r29 no-work composite; r30 stub gate + banner; r31 A1–A5): C2's creation floor `w1*2 >= w0` permits a patch to drop up to half the file operations; rc/S equality can be met by a catch-and-suppress symptom patch. Wave 2 should review diffs, not trust the counter. C1 v1 alone was reachable by cheap bindings — A0 (v2) is the guard; v1+v2 must both hold, so v2 is the effective bar.
2. **record-outside-contract / number-drift** (r29, r30 D1, r31 D1): M1+L14 fix only value-set violations. The r30 "scope" class — entry prose stronger than its record (five sentences) — has **no leg**: C3 L10 only checks backticked `RESULT` spans are whole RUN lines. Wave-2 falsifiers should compare ENTRY claim sentences against RUN lines byte-wise.
3. **landing/carry** (r29–r31): C1's `record:`/`field:` payload paths are blob-checked equal at base and REV, so no dangling pointers are introduced; SCORECARD.md remains append-only.
4. **stale-premise / instrument self-measurement** (r30 A1 regex): v1 and v2 duplicate the full parse; low risk, but any change must keep both summaries in agreement.

## F7 — C1 binding-channel map (planning aid; feasibility of unverified record lines marked [INFERENCE])

Items whose base line has **no cited `census/round-K/` path and no script stem** — under A0(a) only `withdrawn` remains:
- N15, N16, N17 (line 168: only prose counts, no path);
- N20, N21 (line 313: only `r29-registry-agreement.py` script + prose);
- N22, N23, N24 (line 314: only `census/round-26/waves` — `waves` component is forbidden by `record_path_ok` — plus script).

That is 8 items whose only v2 channel is `withdrawn`, saturating the cap `withdrawn<=8` exactly. Every additional stranded item overflows; N19 (line 175, unitless `0`), N43 (line 424 — the run's last digit-bearing line is a version line, not a RESULT line, since the r32 contract fields carry no digits), and N06–N11 (depend on `oracle-acceptance.json` having dotted-int keys with a unit word: [INFERENCE]) are borderline. The C1 plan should be validated against this budget before binding. (The L1's A0 control already shows a citation-restricted binder matches only 13/44: `controls-a0.tsv` summary in amendments.txt.)

## Attack log

No ATTACK filed (connector seat; counters are frozen and A0 already closed the cheapest-skip gap for C1). Structural advisories: F2 (duplicate outcome is untameable post-landing) and F1 (C2 can move C1 run outputs) are raised above as design notes, not counter defects.
