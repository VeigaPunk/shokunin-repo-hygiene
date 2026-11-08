# DRAFT for the L1 — two `corpus/QUALITY.md` rows (Q158, Q159), round-85 style

Seat: `S86Scribe`. Lane: `souji`. Draft only: the L1 integrates. Nothing here is filed.

**These two rows are NEW.** They do not replace or amend any landed row: Q158 extends Q157 (the audit instrument
re-derives the fact it reports), and Q159 is a new criterion about record fields. They land as a new `## Round 86
criteria` section after the landed `## Round 85 criteria` section (`corpus/QUALITY.md:382-388`).

Style, taken from the landed round-84 and round-85 rows: five columns — `id | criterion | applies to | test | lesson` —
one long prose cell, a pointer cell that names the receipts and the command, and a lesson cell that names the round's
lesson and the evidence that produced it.

Evidence this draft cites (all opened and measured this round):

- `tools/souji-record-agreement.py` — `truth_refusal` (`:171`), the writer's `_truth_refusal` call (`:196`), the
  index-flag sweep added inside the same bootstrap (`:199-211`), the C-escape of the refusal message (`:224-226`), the
  K4 key (`:411`), the class split (`:440-441`), the record emitter (`:445`).
- `tools/souji-receipt-write.py` — `_truth_refusal` (`:262`), the skip condition (`:283`), `_flag_refusal` (`:338`) and
  its three classes (`:344-357`), the writer's own flag sweep (`:587-595`), `_cquote` (`:227-241`).
- `census/round-86/c2-k4-counter.py` — the frozen 9-row instrument (`:48`, `:50-51`, `:53`, `:201-215`).
- `census/round-86/controls/c2-before-base-tool.py:199` — the lane-base bytes' space-join.
- `census/round-86/c1-pointer-counter.py` — the census-in-tree branch (`:417-425`), the own-tree belt (`:405-409`),
  `_owntree_ok`'s short-shape guard (`:366-367`).
- `census/round-86/c1-false-rows.tsv:49-50` — NF-W and NF-Y.
- `census/round-86/c1-mutants.json` — members `c7-census-in-tree` and `m14-short-shape`.
- `census/round-86/records/c1-after.txt`, `census/round-86/controls/c1-before-r85-population.txt`,
  `census/round-86/records/c2-after.txt`, `census/round-86/controls/c2-before-base-tool.txt` — the four arms.

---

## Round 86 criteria

| id | criterion | applies to | test | lesson |
|---|---|---|---|---|
| Q158 | Extends Q157 (the rest of Q157 stands): a tool that INHERITS a check inherits only the code path it calls, so the classes the callee skips are unmeasured until the caller names them — and the caller must name them by running the callee's OWN implementation, not by re-implementing the rule. A check is not a rule and not a function: it is a set of classes, and each class is bound to the code that refuses it. The r85 repair gave record-agreement's K4 the receipt writer's byte-truth re-hash (`tools/souji-record-agreement.py:171`, running the writer's `_truth_refusal`, `tools/souji-receipt-write.py:262`), which SKIPS non-zero-stage entries and gitlinks (`tools/souji-receipt-write.py:283`); the implementation that names a concealed gitlink — `_flag_refusal` (`tools/souji-receipt-write.py:338`, `RECEIPT-GITLINK-CONCEALED` at `:349-351`) — lived in the writer's own `write_receipt` path (`tools/souji-receipt-write.py:587-595`), which K4 never called. Measured by r85's own probe (`.ufo/waves/round-85/w1/S85ExecK4/out-probe2.txt`, §2d `probe-d2b`): a nested repository's commit moved under `skip-worktree` on its gitlink entry leaves porcelain EMPTY and K4 emits ZERO rows. The r86 repair runs the writer's index-flag sweep in the same isolated subprocess (`tools/souji-record-agreement.py:199-211`) and reports that class as `index-flag-concealed` (`:440-441`). The general form: when a tool delegates a check, the delegation carries the callee's SKIPS as silently as its coverage, and a skip is indistinguishable from a clean verdict at the call site — so an inheriting tool states which classes it inherits and which it does not, and the un-inherited ones are named as routed defects until they are carried. A caller that reaches into the callee's internals to copy the rule has a second implementation and inherits nothing; the correct inheritance is to CALL the callee for the class in question, and the frozen counter measures both the class that was missing and the classes that were already covered (the seven r85 rows unchanged). | any lane tool that answers a fact by calling another tool's check — an audit key, a gate, a receipt writer, a counter that delegates its verdict; and any counter that measures such a tool | `python3 -B census/round-86/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <an empty dir outside /tmp>` must print `SUMMARY rows=9 mismatches=0 errors=0` and `EXIT=0`, with KG1 `k4=1 named=yes` (`k4rows=['.|index-flag-concealed']`) and KG2 `k4=1 named=yes`; the same counter on the lane-base tool bytes `census/round-86/controls/c2-before-base-tool.py` must print `mismatches=2` with KG1 `k4=0 named=no` (no row at all) and KG2 `k4=1 named=no`, and the seven r85 rows (KH1, KH2, KU1, KU2, KF1, KF2, KF3) must be identical in both arms | corpus/lessons/round-86.md (C2; r85 A2 and S85ExecK4 §2d `probe-d2b` are the measurement this row generalises) |
| Q159 | A record field that carries a FILESYSTEM NAME must be escaped, never space-joined, and the escape must be reversible enough to name the path: a reader must be able to tell `bad\nname.txt` from `bad name.txt`, because those are two different paths and only one of them exists. A record is one physical line of delimited fields (`tools/souji-record-agreement.py:445`); a raw newline in a name splits the record into a truncated first line and an orphan tail that a line-oriented reader cannot reassemble, a space-join keeps the line intact while making the name unrecoverable, and a raw TAB — which the lane-base bytes never replaced at all — splits the record's FIELD structure, so a reader parsing on the tab boundary reads the detail as two fields and the path as a fragment (measured: the base bytes emit SIX tab-separated fields for a tab-named path where the filed tool emits FIVE; `tools/souji-record-agreement.py:226` escapes `\t` as well as `\n` and `\r`). The lane already has the convention — the receipt writer's `_cquote` (`tools/souji-receipt-write.py:227-241`) C-quotes a path for `git hash-object --stdin-paths` so a newline, CR, quote or backslash path hashes correctly — and the escape belongs at the RECORD boundary, where the name becomes text. The r86 repair applies it to the refusal message before it becomes a record (`tools/souji-record-agreement.py:224-226`); the lane-base bytes space-joined the newline (`census/round-86/controls/c2-before-base-tool.py:199`), which is the worse of the two failures because it is invisible in the record's shape. The general form: an escaping defect is measured by whether the record still NAMES the path a reader must act on and still holds its field structure, not by whether the record still parses; a name that no longer round-trips to a path is a lost finding, and a lost finding is a fail-open surface. | every lane tool that emits a line-oriented record naming a filesystem path — the receipt writer's refusals, record-agreement's `MISMATCH` rows, a counter's per-row verdicts, a receipt's path list | the frozen 9-row counter `census/round-86/c2-k4-counter.py` scores KG2 by requiring the record to NAME the escaped path (`FORGED["KG2"] = "bad\\nname.txt"`, `:51`, matched against the whole record at `:269`); the filed tool must read `k4=1 named=yes` and the base bytes `k4=1 named=no`; the raw record text is in `.ufo/waves/round-86/w1/S86Scribe/probe-k4-record-text.py`'s output — the filed record reads `... (bad\\nname.txt); ...`, the base record reads `... (bad name.txt); ...`; the TAB variant is measured by `.ufo/waves/round-86/w1/S86Scribe/probe-tab-name-field-split.py` (the base bytes emit six fields where the filed tool emits five) | corpus/lessons/round-86.md (C2; r85 S85ExecK4 §2e measured the raw-newline split, and the tab-named variant is this seat's r87 candidate, not this round's coverage) |

## Gate

- Destination: `corpus/QUALITY.md`, a NEW `## Round 86 criteria` section appended after the landed `## Round 85
  criteria` section (which ends at `corpus/QUALITY.md:388`). Neither row replaces an existing one: Q158 extends Q157
  and says so in its first clause; Q159 is new. The round-85 rows Q156 and Q157 stand as written.
- Q158 states the general rule as "a tool that inherits a check inherits only the code path it calls", and names the
  r86 measurement that grounds it (the writer's `_truth_refusal` skip at `tools/souji-receipt-write.py:283`, the
  writer's own flag sweep at `:587-595`, K4's new sweep at `tools/souji-record-agreement.py:199-211`, and r85's
  `probe-d2b` receipt with zero K4 rows).
- Q159 states the general rule as "a record field that carries a filesystem name must be escaped, never space-joined",
  names the lane's existing convention (`_cquote`), and measures by whether the record still NAMES the path.
- The `lesson` cells name `corpus/lessons/round-86.md`, which the L1 writes at integration; that file does not exist
  yet at lane base `2acbbfc8`, and the row is not self-contained without it. The L1's dependencies are therefore:
  (i) author `corpus/lessons/round-86.md` with the C1 and C2 findings these rows cite; (ii) if the L1 prefers a
  pointer that resolves today, the substitute is `.ufo/waves/round-86/w1/S86Scribe.md` (this seat's report) together
  with `census/round-86/preregistration.txt` and the four receipts named in the `test` cells.
- Every pointer in these rows resolves to a committed path and line number at lane base `2acbbfc8`, except the two
  files under this seat's own directory (`.ufo/waves/round-86/w1/S86Scribe/`).
- No claim in these rows exceeds what the round's own receipts carry. The `test` cells name the four committed
  receipts and the two committed instruments; the raw `MISMATCH\tK4\t…` record text quoted in Q159 is not in any
  receipt and is supplied by this seat's own re-derivation, with the reproducer named in the row.
- Nothing outside the seat's own directory was written. The lane's `corpus/QUALITY.md` is unchanged.
