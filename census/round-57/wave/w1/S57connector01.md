# S57connector01 — sibling-overlap scan (souji r57, w1)

Scope: the round's two surfaces — (a) the inline HTML-comment / hidden-span rule in a
markdown visibility check, (b) receipt `rev=` binding and instrument-digest pinning.
Read-only over `/home/vgpnk/Projects/shokunin/*-shokunin/{tools,census}`. No sibling file
was edited, executed, or imported. No subagent, no background job.

Freeze under test: `d749f7ee081ec1b382b2f92577eb22bfba1c7761` (base
`b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd`). Our instruments read this session:
`census/round-57/c1-counter.py:235-330` (v6 `hidden_lines`), `census/round-57/c2-counter.py:1-83,84-150`
(gate + `check_receipt`), fixtures `census/round-57/fixtures/build-fixtures.py:625-665`.

## Scan commands (run this session, fleet root cwd)

```
for lane in *-shokunin; do case "$lane" in souji-shokunin) continue;; esac
  grep -rIl --exclude-dir=.git -e 'hidden_lines' -e 'in_fence' -e 'splitlines' "$lane/tools" "$lane/census"; done
```
Observed: only `souji-shokunin` has a `census/` directory (21 sibling dirs checked, incl.
`kumitate-shokinin`; `kumitate-shokinin` has neither `tools/` nor `census/`). Results:

| token | sibling hits |
|---|---|
| `hidden_lines` | **0** (the name is lane-local to souji) |
| `in_fence` | **1** — `tameshi-shokunin/tools/cold-read-forecast.py:183,186,188` |
| `splitlines` | **366 files** (idiomatic Python; only the line-model choices below matter) |

Because the literal tokens under-report the class, the class scan used the HTML-comment and
fence openers themselves (`-e '<!--'`, `-e 'fence'` over the same `tools/ census/` scope), which
is what produced the rows in table A. Receipt scan:
`grep -rIl -e 'instrument_sha256' -e 'tool_sha256' -e 'is-ancestor' -e 'cat-file -e' -e 'blob' */tools */census`
(produced table B).

## Table A — comment / fenced-span models

Shapes are the r57 fixtures (`build-fixtures.py:625-665`): **B4** NBSP-prefixed mid-line opener,
closer two lines later; **C4** mid-line opener, closer on a later line; **C6** complete one-line
inline comment; **F29** mid-line opener with **no** closer. `refuse` = the filings inside the span
are hidden (a filing counter refuses them); `keep` = they stay visible. Cells are source-derived
traces of the cited code, not executions of sibling gates.

| # | sibling path:line | grammar / variant | B4 | C4 | C6 | F29 | our v6 variant (`c1-counter.py`) | verdict |
|---|---|---|---|---|---|---|---|---|
| A1 | `tsukuroi-shokunin/tools/check-btrfs-space-r30.py:174-198` (`comment_state`; caller `visible_table_lines` :200-240) | **any occurrence**, cross-line state, FIRST `-->` closes, `<!-->` / `<!--->` close immediately, **no closer → open to EOF**; code spans stripped first; no indent gate for comments (only fences) | refuse | refuse | keep | refuse | same opener/closer scan, but indent ≤3 and **no closer → literal** (`:299-325`) | SHARED (closest owner of the inline class) |
| A2 | `kaidoku-shokunin/tools/round-50/c2-record.py:282-320` (`vis`) | fence + **line-start** block (≤3 sp, unclosed → EOF) + same-line closed inline → NUL; **unclosed inline opener → truncate + open to EOF**; LF-only split, documented | refuse | refuse | keep | refuse | same for B4/C4/C6; diverges on F29 and on the ≤3-space gate | SHARED |
| A3 | `chousa-shokunin/tools/research-gate.sh:818-850` (`load_sections`) | two-pass fence pairing (0-3 sp, same char, closer ≥ opener, unclosed = fail-closed); comment: any `<!--` with no `-->` **on the same line** opens, any later line containing `-->` closes; no `<!-->` handling | not hidden | not hidden | not hidden | not hidden | span model exists but is **heading-only**: body lines inside a comment are still appended (`:835-840`) | SHARED (different use) |
| A4 | `tsukuroi-shokunin/tools/check-owed-statements-r29.py:211-235` (`live_lines`) | fence paired; 4-space/tab indented code skipped; `EMPTY_COMMENT`/`CLOSED_COMMENT` stripped; any residual `<!--` → **open to EOF**; `text.splitlines()` at `:214` | refuse | refuse | keep | refuse | LF-only line model, literal fallback | SHARED |
| A5 | `tsukuroi-shokunin/tools/check-selector-contract.py:149-176` (`_visible_lines`) | one regex `<!--.*?(?:-->|\Z)` with `DOTALL` (any occurrence, first closer, **`\Z` fallback**); fence `^\s*` = any indent; `splitlines()` | refuse | refuse | keep | refuse | — | SHARED |
| A6 | `chousa-shokunin/tools/capture-fetch.py:80` (`html_to_text`) | `re.sub(r"(?s)<!--.*?-->")` — closed-only: first closer after the opener, spanning lines, **no closer → no match = literal**; no indent rule; not a filing gate | refuse | refuse | keep | keep | **identical verdicts on all four shapes**; v6 adds indent ≤3 and `<!-->`/`<!--->` | SHARED (grammar precedent outside the gate class) |
| A7 | `tameshi-shokunin/tools/cold-read-forecast.py:179-188` (`sectionize`) | naive toggle on `line.strip().startswith('```')`; no tilde, no length rule, **no comment model** | keep | keep | keep | keep | — | comment-blind (the v5 over-acceptance class) |

Read of the table: the fleet has **four** cross-line inline-comment implementations used as
visibility gates (A1, A2, A4, A5 — A3 is a fifth tracker but heading-only), and **all four**
answer F29 the opposite way from v6 — "unclosed opener hides to EOF".
Only A6 (a regex with no `\Z` alternative, used for HTML→text extraction) reproduces v6's
"no closer = literal text" on all four shapes. So v6's inline class is **not lane-first as a
grammar**; what is lane-first is the *gate combination*: indent ≤3 **and** literal-on-no-closer
**and** `<!-->`/`<!--->` **and** the `hidden_by=` label **and** the full-ordered-finding selftest.
None of A1–A5 would reproduce the 36-row r57 population: each fails F29 (and A1/A2/A4/A5 also
diverge on the 4-space shapes F17/F26, where their comment/fence scans are looser than v6's
`indent <= 3`).

## Table B — receipt revision binding and instrument-digest pinning

| # | sibling path:line | mechanism | binds a revision to a receipt? | binds the instrument's **committed blob at that revision**? | our C2 variant (`c2-counter.py`) | verdict |
|---|---|---|---|---|---|---|
| B1 | `chousa-shokunin/tools/receipt-pin.py:1-20,36-94` | frozen 4-line header: `REVISION=<40 lower hex>` must equal `--revision`; `EXIT=` decimal 0..255; `SHA256=<64hex> <canonical rel path>`; digest compared to `git cat-file blob REVISION:PATH` (committed bytes, never the worktree) | YES (exact, full-40, lowercase) | **YES — path-bound and revision-bound** | `rev=` + `instrument_sha256=` + `EXIT=` in a free-form receipt; manifest over N receipts | **SIBLING-OWNED (chousa)** |
| B2 | `tameshi-shokunin/tools/receipt-revision-gate.py:43-44,97-165` | `\brev=([0-9a-f]{7,40})\b` (+ JSON `"rev"`); resolve, roles `positive`/`verdict` (one distinct rev, must equal certified or be byte-identical on `--paths`) / `control` (every rev ancestor-or-equal via `merge-base --is-ancestor`); codes `RECEIPT_REV_ABSENT/AMBIGUOUS/UNRESOLVABLE/MISMATCH/CONTENT_DRIFT/CONTROL_NOT_ANCESTOR/DIGEST_MISMATCH` | YES | **NO** — `RECEIPT_DIGEST_MISMATCH` hashes a `.sha256` sidecar of the *receipt* (`:114-121`); 7-40 hex accepted, so no full-40 durability | full-40 durability incl. jj keep-only refusal (`:86-101`), instrument-name cross-check | SHARED (owns the rev=-gate-with-roles shape) |
| B3 | `tsukuroi-shokunin/tools/run-receipt.py:73-120` | recorder: clones the lane at TOOL-REV, requires the tool tracked, sha256 of the checked-out tool file = committed blob bytes at TOOL-REV, recorded as `tool_sha256` with `revision`/`tool_revision`; never re-gates | records | YES at record time (no verification arm) | `record-receipt.sh` is the recorder analogue; the gate verifies | SHARED (recorder-side) |
| B4 | `tameshi-shokunin/tools/receipt-window.py:152-182` | `instrument_sha256` must be 64-hex and classified against a contract (`frozen_sha256`/`installed_sha256`, historical map) plus measurement-interval windows | NO (no rev in the check) | NO (contract constants + installed worktree digest) | — | different axis (time windows) |
| B5 | `kaidoku-shokunin/tools/round-62/base-binding-sweep.py:26-40,121-178` | `--expect-sha256` pins the **worktree** copy of the audit tool; base binding read from the receipt's own **committed** bytes (`git show REV:RECEIPT`) with a 40-hex name-binding grammar | YES (base name binding) | NO for the instrument (worktree hash); YES for the receipt's own bytes | — | SHARED (variant contrast) |
| B6 | `chousa-shokunin/tools/digest-in-tree.py:1-25,33,55-63` | every 64-hex pin in a receipt must re-derive from sha256 of committed blob bytes reachable at `--revision`; no digest → exit 2 (fail-closed) | YES (a revision) | YES but **path-unbound** (any committed blob satisfies) | path-bound via the manifest's instrument column | SHARED |
| B7 | `tsukuroi-shokunin/tools/check-revision-binding.py:18-26` | `--revision` binding contract: `HEAD`/`@`/branch rejected, must be landed on `refs/heads/<branch>` and pushed to `refs/remotes/origin/<branch>`; no receipt, no digest | YES (stronger durability than full-40) | NO | — | SHARED (durability grammar) |

Read of the table: the exact C2 predicate — *`instrument_sha256=` must equal the committed blob of
the named instrument at the receipt's revision* — already exists in the fleet at
`chousa-shokunin/tools/receipt-pin.py` (r65 frozen receipt format), path-bound and
revision-bound, with `EXIT=` in the same header. `tameshi` owns the `rev=` **gate** shape
(roles, ancestry, named refusal codes); `tsukuroi` owns the recorder that derives `tool_sha256`
from a committed checkout. C2 is therefore a re-derivation in a different receipt format, not a
fleet-new capability. No sibling models a jj keep-only ref (`refs/jj/keep`) — that class is
lane-local.

## Verdicts

- **Surface (a) — inline comment / hidden span: SHARED.** Closest owner of the inline-span
  grammar: `tsukuroi-shokunin/tools/check-btrfs-space-r30.py:174-198` (`comment_state`; caller `visible_table_lines` :200-240).
  Lane-first only for the gate combination listed above; no absorption (a sibling's mechanism is
  reported, never imported — v6 stands on S280 §6.6, not on a sibling).
- **Surface (b) — receipt `rev=` + instrument digest: SIBLING-OWNED by `chousa-shokunin`**
  (`tools/receipt-pin.py`), with `tameshi-shokunin/tools/receipt-revision-gate.py` owning the
  rev=-binding-gate shape and `tsukuroi-shokunin/tools/run-receipt.py` the recorder-side digest.

## Contradictions (stated, not scored away)

1. **The unclosed-opener rule is a live fleet split, and it decides F29.** v6: a mid-line `<!--`
   with no closer is literal text, so F29's honest filings stay visible (`c1-counter.py:299-325`).
   A1 `:176-183`, A2 `:313-317`, A4 `:231-234`, A5 `:151-157` all hide to EOF instead. r56 routed
   defect 4 (refuse B4/C4) does **not** adjudicate this: those shapes are closed. v6 adjudicates
   it from S280 §6.6; the siblings cite no source for the EOF rule, so the two readings cannot be
   reconciled by evidence the lane holds. Any future shared visibility module changes v6's F29
   exit code unless the rule is made an explicit parameter. A6 shows the literal reading is not
   unknown to the fleet — it is simply outside the gate class.
2. **B4's prefix is not a bare NBSP.** `build-fixtures.py:639` writes `'\xc2\xa0'`, which
   `write()` (`:250-254`) encodes as UTF-8 → bytes `c3 82 c2 a0` = U+00C2 + U+00A0, i.e.
   "Â"+NBSP, not U+00A0 (derived: `python3 -c "s='\xc2\xa0'; print([hex(ord(c)) for c in s],
   s.encode().hex())"` → `['0xc2','0xa0'] c382c2a0`). The discriminating property survives (a
   non-space prefix defeats the line-start rule, indent is 0 either way, so v6 takes the inline
   branch and v5 misses → T1 still holds), but the fixture does not test the character its name
   and docstring (`:632-636`) claim. Low severity, sentinel/critic's call.
3. **C2's "capability acquisition" wording needs a fleet reading.** The mechanism is already in
   chousa (B1) and the full-40 durability rule too; the lane-local part is the free-form
   `rev=`/`instrument_sha256=` key set, the manifest over N receipts, the jj keep-only class and
   the instrument-name cross-check. The preregistration's claim is about *this lane's* SCORECARD
   capabilities table, so it is not falsified — but a fleet-novelty reading of C2 would be wrong.

## Shared limit worth naming (same class as the r56 Q109 defect)

C2, B1, B2 and B6 all read the **receipt** from the worktree (`c2-counter.py:103-118`,
`p.read_bytes()` at :110; `receipt-pin.py:45`; `receipt-revision-gate.py:106`). Only the *instrument*
is object-DB-bound. So C2 closes the "which revision was measured" half of Q109 but not the
"the receipt itself was overwritten" half — the very second working-tree run the r56 LOG records.
That is a limit of the whole fleet's receipt class, not a C2 kill.

## Reproduce

```
cd /home/vgpnk/Projects/shokunin
grep -rIl --exclude-dir=.git -e hidden_lines -e in_fence -e splitlines <lane>/tools <lane>/census
grep -rIn --exclude-dir=.git -e '<!--' <lane>/tools <lane>/census
grep -rIl --exclude-dir=.git -e instrument_sha256 -e tool_sha256 -e is-ancestor -e 'cat-file -e' -e blob */tools */census
sed -n '174,240p' tsukuroi-shokunin/tools/check-btrfs-space-r30.py
sed -n '282,320p' kaidoku-shokunin/tools/round-50/c2-record.py
sed -n '1,90p'   chousa-shokunin/tools/receipt-pin.py
sed -n '43,210p' tameshi-shokunin/tools/receipt-revision-gate.py
```

## Bounds observed

Leaf seat: no subagent, no background job. Nothing written outside this seat directory
(`/fast/scratch/hyaku/souji-r57/S57connector01` was created and removed; no scratch receipt was
needed). No sibling file edited or executed; no git/jj mutation anywhere. Sibling verdicts are
source-derived traces of the cited lines ([INFERENCE] for behaviour, [EVIDENCE] for text).
No tool installed or upgraded this session.
