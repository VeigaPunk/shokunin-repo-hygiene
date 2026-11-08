# S88ExecC2 — C2 FLAGFAIL re-derivation + attack
Receipts in .ufo/waves/round-88/w1/S88ExecC2/receipts/

## Instrument hashes (re-measured, all match)
- tests/fixtures/r88-k4-flagfail.py aa79133a7ed302b84abda3c194974b9e38250fd82be55743d9bc909f43e8335d MATCH
- tools/souji-record-agreement.py c0604b4abf10a45dfcf6eb9f7bb2ad8efb805321c24677e45a192e9a73e4fdef MATCH
- controls/c2-before-tool.py e1b00e8ae14f7059cb5d649dd9ae6e3a3a0498813beb22427af2473c8ac67ccc MATCH

## C2 arms re-derived
- After: `SUMMARY cases=7 tool_pass=7 before_pass=3` EXIT 0 — all KFF1-5+KFC1/2 pass on current tool, before fails KFF2-5.
- Before (r87 tool as both arms): `SUMMARY cases=7 tool_pass=3 before_pass=3` EXIT 1, KFF2-5 fail — do-nothing control holds, no vacuous delta.
- Verdict: both arms VERIFY stated wording.

## r87 12-row counter regression
`SUMMARY rows=12 mismatches=0 errors=0` EXIT 0 — no row moved (KH1,KH2,KU1,KU2,KF1-3,KG1-2,KN1-3 all matched).

## Five attacks (own scratch writer, real tool copy; detail = 5th cell of MISMATCH K4 row)
- A4000 (4000-byte stderr `AttributeError: y…`): K4 rows=1, DETAIL='the index-flag read failed (AttributeError: yyy…(100 head)…yyyy…(99 tail)\\n); tracked bytes are unverified' len 259, one physical line, no raw control/NEL/U2028/29. PASS (both ends kept, middle trimmed).
- A-fffe (b'\xff\xfe'): K4 rows=1, DETAIL='the index-flag read failed (\\\\xff\\\\xfe); tracked bytes are unverified' — backslashreplace spelling, one line, no raw. PASS.
- A-U2029 (stderr b'\xe2\x80\xa9\n'): K4 rows=1, DETAIL='the index-flag read failed (\\u2029\\n); tracked bytes are unverified' — escaped, one line, no raw U+2029. PASS.
- A-forge (exec-time `FLAGFAIL !!!not-base64!!!`): K4 rows=1, DETAIL='the index-flag read failed (undecodable detail); tracked bytes are unverified' — parent `b64decode(validate=True)` fails closed, never emits forged text. PASS.
- A-fake-WRITER (writer prints `WRITER deadbeef…` then CLEAN path): K4 rows=1, DETAIL='the receipt writer produced no verdict (exit 0: CLEAN); tracked bytes are unverified' — second WRITER line defeats `startswith("CLEAN")`, no clean verdict, fail-closed. No injected MISMATCH row in any attack (SPLITLINES=10 stable). PASS.

## Excerpt arithmetic (400-char AttributeError line)
`_one_line` → 200 chars: head 100 == line[:100], mid = '…' (U+2026) at position 100, tail 99 == line[-99:], total 100+1+99=200. Full K4 detail `the index-flag read failed (<200>); tracked bytes are unverified` — exactly one line, 0 tabs, no newline. Verdict: PASS.

## Falsification check
No artifact falsifies C2 stated wording. Limits intact: middle trimmed (both ends kept), fake writer (no real-writer honesty claim), injective escaping (backslash doubled).
