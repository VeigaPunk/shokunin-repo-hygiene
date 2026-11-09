# R93MutC2 — C2 r93-fixture forgery attack: 9 one-edit forgeries vs the r93 fixture

Seat: R93MutC2 (mutation-tester). Filed tool `tools/souji-record-agreement.py`
(sha256 `fc0e35c208331de8ce568de3543b330c470e0a80336652f94d575dc242137a75`).
Fixture `tests/fixtures/r93-k4-flagfail.py` (sha256 `ed15094e…`); before-tool
`census/round-92/controls/c2-before-tool.py` (sha256 `21e5c740…`). Post-run hashes
re-verified: all three unchanged; the lane was never edited and no git mutation ran.

Each forgery is ONE contiguous text edit (anchor count asserted == 1) applied to a
scratch copy. Each was run through the r93 fixture with the before-tool as `--before`:
`python3 -B tests/fixtures/r93-k4-flagfail.py --tool <forgery> --before
census/round-92/controls/c2-before-tool.py --work <empty>`.

Positive control (filed tool): rc=0, `SUMMARY cases=22 tool_pass=22 before_pass=16`.
Negative control (before-tool): rc=1 (tool_pass 16/22 — per fixture receipts).

Method and receipts, all in this seat dir: `gen_forgeries.py` (writes the nine
forgeries; sha256s reproduce across runs), `run_forgeries.py` (runs the fixture,
writes `forgery_table.tsv`), `fixture_<name>.txt` (full fixture stdout per
forgery), `forgery_table.tsv`, `differ.py` and `differ.txt` (sweep counts),
`celllevel.txt` (the M and Q cell pairs), `window3cells.txt` (window-3 straddle
proof), `q-and-deadloop.txt` (Q head/tail diff and the dead-iteration check).
Tool installs: none.

## Forgery table

| name | edit | rc | tool_pass | failing cases | verdict |
|---|---|---|---|---|---|
| a_window3 | search window 3 back instead of 4 (`cut - 4` → `cut - 3`) | 0 | 22/22 | — | EQUIVALENT (proof below) |
| b1_len230_nomove | `if len(raw) == 230:` raw cuts (no boundary move); else filed rule | 1 | 21/22 | KFF19 | REJECTED |
| b2_len230_correct | `if len(raw) != 230:` limit 201 (wrong off the sweep length); else filed | 1 | 20/22 | KFF3, KFF11 | REJECTED |
| c_reprokey | R92MutC2 H verbatim: `if seq and b"fatal: inv" in raw: return t` (tail branch) | 0 | 22/22 | — | SURVIVES — covered by limit (iii) |
| d_headback1 | head cut `seq[0] - 1` when a sequence straddles | 1 | 20/22 | KFF18, KFF19 | REJECTED |
| e_tail4byte | tail cut `seq[1] - 1` for 4-byte sequences only | 1 | 20/22 | KFF18, KFF19 | REJECTED |
| f_table_noF4cap | range-table decoder, F4 second-byte 8F cap dropped; every other row exact | 1 | 21/22 | KFF19 | REJECTED |
| g_table_noEDcap | range-table decoder, ED second-byte 9F cap dropped; every other row exact | 1 | 21/22 | KFF19 | REJECTED |
| h_filler_a | `if b"a" not in raw: limit = 199` (filed rule only when filler `a` present) | 0 | 22/22 | — | SURVIVES — covered by limit (i) |

Per-forgery sha256 (scratch copies, reproduced on regeneration): `a_window3 59a9a116…`,
`b1_len230_nomove f06b0f7b…`, `b2_len230_correct d0ffa41f…`, `c_reprokey b7bf720f…`,
`d_headback1 818fd7a8…`, `e_tail4byte 2c41cb80…`, `f_table_noF4cap 9e76c249…`,
`g_table_noEDcap 72450407…`, `h_filler_a 7fa92905…`.

Notes on the required edits. (b) is the length-keyed special case with the filed rule
as fallback; both polarities (special at 230 = no move, and special off 230 = wrong
limit) are rejected. (c) is R92MutC2's H anchor verbatim; it keys on the raw payload
bytes (`b"fatal: inv"`), which is the same payload-identity key as keying on the cell
text. (f) and (g) each drop exactly one second-byte cap and are otherwise the filed
table.

## Survivors: distinguishing payloads and verdicts

**c_reprokey (rc 0, 22/22).** Distinguishing payload M, 214 bytes (sha256 `ec115573…`):
`b"fatal: inv " + b"a"*103 + b"\xc2\x85" + b"b"*98`. The tail cut is at 115, inside
U+0085 (bytes 114..116).
- filed tail: `…aaaa…bbbb`, U+0085 elided whole, cut moved to 116.
- forgery tail: `…aaaa…\x85bbbb`, cut held at 115, the orphan 0x85 spelled as a raw
  byte. This is the r91 spelling defect class (S354) reintroduced on this payload.

The key never fires on the fixture's own pairs: at KFF14/KFF15's tail cut (111) no
well-formed sequence straddles, so the forgery branch returns the filed result. So the
fixture cannot see it. Verdict: **within limit (iii)** — "a tool that hardcodes cells
per payload can pass any finite fixture." Not a falsification.

**h_filler_a (rc 0, 22/22).** Distinguishing payload Q, 214 bytes (sha256 `69e720a5…`):
`b"f" + b"q"*113 + b"\xc2\x85" + b"w"*98`, with no `a` byte.
- filed head ends at 100 bytes (ellipsis at index 100).
- forgery head ends at 99 bytes (limit 199). Tails are identical.

With `a` in place of the first filler byte (`QA`, same length) the forgery matches
the filed tool exactly (`q-and-deadloop.txt`: "h on QA identical: True"). Verdict:
**within limit (i)** — "KFF19 is a finite sweep (one payload length 230, filler `a`,
33 tokens pairwise); exact agreement is measured there, not proven for every payload."
Q is length 214 and filler `q`, outside the sweep's domain by the prereg's own
description. Not a falsification.

## (a) A_window3 — equivalent, proved by construction and measured

Filed loop: `range(cut - 1, max(cut - 4, 0) - 1, -1)` yields starts `cut-1 … cut-4`.
Its end loop is `range(cut + 1, min(start + 4, len(raw)) + 1)`. For `start = cut-4`
that is `range(cut+1, cut+1)`, which is empty (`q-and-deadloop.txt`: `[]`). So the
`start = cut-4` iteration never produces a candidate. Window 3 (starts `cut-1 … cut-3`)
removes only that dead iteration; every candidate the filed tool can produce is still
produced. Measured: 192 four-byte straddle payloads at both cuts, lengths 214/230,
fillers `a` and `7F`, starts `cut-3 … cut-1`: 0 differ (`window3cells.txt`). Together
with the fixture sweeps (KFF18 29,700 and KFF19 14,586 payloads): 0 differ. Verdict:
EQUIVALENT mutant; prereg limit (v) covers it. Not a gap.

## KFF19 and KFF20 coverage of the non-survivors

- KFF19 (exact cut position) is what rejects b1, d, e, f and g. Each of d and e moves a
  cut one byte off and is caught on the exact-position sweep (KFF18 also fires for d,
  e). f and g each drop one second-byte cap and are caught on KFF19 alone at 21/22.
- b2 fails KFF3 and KFF11 on payloads off length 230, before the sweep is reached.
- KFF20 (overlong `E0 80 80` across the head cut) is not exercised by any survivor:
  c's key is absent from the `fatal: hil` payload, and h's filler is `a` in KFF20's
  payload, so h matches the filed tool there. The survivors are caught by limits, not
  by KFF20.

## FALSIFIES-WORDING / FALSIFIES-NUMBER

NO-FALSIFICATION. Neither survivor breaks a sentence of the C2 claim. The claim's
predicate is the eight-edit probe (all rejected by the probe; the probe itself is
outside this seat's scope) and the fixture's 22/22 on the filed tool. Prereg limit (ii)
says the forgery set is eight named edits and "others are the wave's to try"; this seat
tried nine plus the survivors' distinguishing payloads. The survivors fall inside the
stated limits: c under (iii), h under (i). Limit (i)'s clause "exact agreement is
measured there, not proven for every payload" is the statement the h survivor
exercises, and it is in the prereg before any run.

One wording note for the L1, not a falsification: limit (i) calls the sweep's filler
"`a`". That is accurate for KFF19 (its payloads are `a`-filled). KFF18's sweep is
`x`/`y`/`z`-filled, so "filler `a`" describes KFF19 only. The C2 claim sentence names
KFF19 and nothing else, so it stays accurate.

## Corrections to this seat's earlier drafts

The first draft of this report contained three errors, fixed here: (1) the window-3
proof said window 3 "never proposes `start = cut-3`" — wrong; it is the dead
`start = cut-4` iteration that is removed. (2) The Q description attributed the
difference to a filler byte; the difference is the head window (99 vs 100 bytes), and
the filler matters only in that `a` restores the filed window. (3) The KFF18 filler
was described as `x`-only in the head; the sweep uses `x`, `y` and `z`.

Report: .ufo/waves/round-93/w1/R93MutC2.md
