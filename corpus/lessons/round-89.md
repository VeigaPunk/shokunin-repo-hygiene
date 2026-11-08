author: SoujiR89 (souji L1, round 89)
# Round 89 — three of four C1 bindings verify; the C2 kill rule passes with a narrowed headline

Lane base `a2cef94a` (r88 closed; spot-check `corpus/lessons/round-88-verifier-spotcheck.md`, verdict **admit**).
Instruments and controls P `c9329534`; preregistration alone F `d8bc7484`; harness fix `a3c7cb1f` (A0.6).
Wave evidence `.ufo/waves/round-89/w1/`; receipts `census/round-89/records/` and `census/round-89/controls/`.

## Gate

Sources opened this round (each read here; ids continue the registry after S350):

- **S351 — Python `codecs` § Error Handlers, the `surrogateescape` entry** (https://docs.python.org/3/library/codecs.html#error-handlers,
  HTTP 200, 181610 bytes, sha256 `62a3d3da3bb2fffb31d902d32f136db7ca803e0d1c52e85ba01713cd4a7fea6f`, capture
  `census/round-89/srcs/codecs.html`, page title "Python 3.15.2 documentation", opened 2026-11-08). Quote, § Error
  Handlers, rendered offset 12792 of the tag-stripped text: "On decoding, replace byte with individual surrogate
  code ranging from U+DC80 to U+DCFF." (13 words). **ADMIT**, `docs`, tier A, `mined` — it grounds C2's
  injective decode (`_decode_record`, `_escape_text`'s `0xDC80 <= o <= 0xDCFF` arm) and is the exact scope S253
  excludes ("not the `ignore` or `surrogateescape` handlers"). Duplicate-URL check: same page as S253/S256 (both
  the `replace` handler) — a scope-narrowing row on a held URL, not a duplicate scope. Version note: the capture
  carries the 3.15.2 book while the host is 3.14.8; the scout's 3.14 fetch and the filed capture agree on the
  quoted sentence byte-for-byte, so the row is version-robust (A3).
- **S352 — Python `base64` § `b64encode`/`validate`** (same base64 page, opened this round). **REJECT sample, not
  filed**: S349 already holds that exact scope, quote, rejection and flip on the versioned URL, and its quote
  re-verifies `True 15` on both the 3.14 and the 3.15.2 captures. Filing S352 would add registry weight, not a
  decision. Flip condition (from S349, unmet): a round that must decide padding/`canonical`/`validate` semantics
  for a frame whose producer is outside the lane's own child process.

## Measured

- **C1 (calibration 7) — verifiable in part, target NOT met.** `census/round-89/controls/c1-before.txt`: the same
  sixteen mutants on the r88 53-row population kill twelve, survivors `m18b`, `m17b`, `m17c`, `m18d`,
  `SUMMARY killed_r88=12`, EXIT 0 (identical on every ARM/MUTANT/SUMMARY line in the reviewer's re-run save the
  harness-sha header, which the A0.6 fix moved). `census/round-89/records/c1-after.txt`: pristine 53/0 and 57/0,
  fifteen killed on r89, `m17c-no-malformed killed=no`, `SUMMARY killed_r88=12 killed_r89=15 killed_total=27`,
  battery EXIT 1. The frozen target (16/28/EXIT 0) is **not met**; the after receipt is composed from three
  seats' independent full-matrix runs because the L1's detached battery was reaped at mutant 3. Per-row
  attribution (S89MutCounter §6): `NF6h` is the only r89 killer of `m18b`, `LD1b` of `m17b`, `NF6i` of `m18d`;
  `LD2` kills no filed mutant. The C1 claim as frozen is therefore **not verified**; the narrowed true sentence
  and the measured `LD2b` design are in `plans/round-89.md` A1.
- **C2 (operability 8) — kill rule met, headline narrowed.** `census/round-89/controls/c2-before.txt`: r88 bytes
  as both arms, `SUMMARY cases=10 tool_pass=8 before_pass=8`, KFF6/KFF8 fail, EXIT 1. `records/c2-after.txt`
  (re-run after F because the first run predated the freeze; identical numbers): `SUMMARY cases=10
  tool_pass=10 before_pass=8`, EXIT 0. The r87 12-row K4 counter on the filed tool reads `rows=12
  mismatches=0 errors=0` (S89ExecC2 §2). Five attack payloads in S89ExecC2 §4 all fail closed, one K4 row,
  one physical line each. The enumerated kill rule passes; the title "injective on the bytes" is narrowed
  (0x85/U+0085 collide; the raw window is 202 bytes) in `plans/round-89.md` A2.
- No owned axis score changed (calibration 7, coverage 8, operability 8 — the lane still has no reproducible
  0–10 mapping); both rows carry verdicts, commands and measured commits instead.

## Narrowed before filing

A1 (C1/LD2), A2 (C2 injectivity + 202-byte window), A3 (S352 redundancy + version note), A0.6 (harness pin
superseded by `6165eade…`). Four wave seats (S89MutCounter, S89Reviewer, S89Sentinel, S89Simplifier)
independently measured the C1 15/27 value; three seats (S89ExecC2, S89Critic, S89Scribe) flagged the C2
202-byte window.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | row design never measured before freezing: LD2's appended `P02` was already in the frozen r77 ledger, so the row discriminated nothing | S89MutCounter F1/§6; S89Sentinel §3.4; census/round-89/records/c1-after.txt | `_ledger` guard reading (the duplicate clause fires on any repeated id); the before-arm only measures mutants that SURVIVE, and `m17c` surviving r88 says nothing about the new row's placement | the malformed-row guard is now measured dead-or-unbound by LD2's failure; binding row `LD2b` (append `ZZ9\tABSENT`, an absent id) is recorded with its reproducer for r90; QUALITY Q164 records the same shape for tool design |
| M2 | the frozen C2 `c2-after.txt` was written 13 min before P/F (mtime 09:32 vs 09:45) — pre-freeze after-data | S89Reviewer §2 chronology | the freeze-before-scoring rule (r63 M2) and the commit timestamps it leaves | the after receipt was re-run after F and re-filed; numbers identical; the pre-freeze run is disclosed here, not used as evidence |
| M3 | the wave dispatch carried r88's claim wording verbatim (53 rows / 12 mutants / killed_total=22 / 7 cases) — five seats read the brief and had to reconcile against the prereg | S89Sentinel §0/§F-2; S89ExecC2 §0; S89Scribe §0; S89Simplifier §Contract; S89Reviewer §1 | the build-spec.py rewrite (this L1 changed the milestone string but not the CTX claims block copy) | every seat measured the prereg; the falsification ledger is reconciled against the prereg, not the dispatch; build-spec.py now carries r89 wording for future rounds |
| M4 | a `write` of the preregistration misrooted at the fleet root (`/home/vgpnk/Projects/shokunin/census/`) | `plans/round-89.md` A0.4; the fleet `git status` sweep | the lane-cwd discipline (the write tool's cwd was the lane repo, the path was fleet-absolute) | the file was moved byte-exact (`cmp`), the fleet directory removed; the misroot sweep before the report confirms no other fleet write |

## Routed to round 90

- `LD2b` (append `ZZ9\tABSENT`) binds `m17c`; `LD1c`/`LD1d` bind the class-conflict and conflict-keyed ledger
  readers (S89MutCounter F3); `NF6i2` binds the other occurrence order (F4); `NF6j` binds the six remaining
  PATHCH predecessors (F5).
- The `0x85`/U+0085 collision: spell the real character as `\u0085` in `_escape_text` (S89ExecC2 §6 advisory)
  or add a KFF9 row; `S89Connector` proposes the `` vs `` prefix distinction.
- `_one_line` deletion and battery required-defaults (S89Simplifier #5/#4, zero-risk patches in its `diffs/`).
