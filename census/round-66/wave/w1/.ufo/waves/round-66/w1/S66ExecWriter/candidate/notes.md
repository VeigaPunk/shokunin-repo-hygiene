# S66ExecWriter — round-66 candidate writer notes

Base: tools/souji-receipt-write.py at 045e103478fa4a7eff77db2cab5b9e2f26959a0a (round-65 landed bytes, 1374 lines).
Candidate committed in scratch clone at **6ec59b3aa5f07c95aa77b73a46a8bf750d356b48**; candidate bytes =
committed blob (verified with `git show HEAD:tools/souji-receipt-write.py | cmp`). Candidate is 1478 lines.
Line numbers below are in candidate/souji-receipt-write.py.

## Changes, by line

1. **Docstring** — line 49 reworded: "GIT_CONFIG_* passthrough ... (round-65 named limits; round 66 routes)" →
   "GIT_CONFIG_* passthrough is closed by the round-66 env gate (see below)". Lines 54–60: round-66 paragraph
   naming the refused env routes (RECEIPT-ENV-CONFIG-SET, RECEIPT-ENV-REDIRECT-SET), the git-call pins, the
   full-permission-bits mode byte, and the ignore routes that stay named limits. Every other docstring line unchanged.
2. **Env gate in write_receipt()** — lines 288–299, placed directly before the existing GIT_INDEX_FILE gate
   and before any git call:
   - lines 290–294 (refuse at 293): RECEIPT-ENV-CONFIG-SET when GIT_CONFIG_COUNT, GIT_CONFIG_PARAMETERS, or any
     GIT_CONFIG_KEY_* / GIT_CONFIG_VALUE_* name is present. Message carries the sorted NAMES only; presence is the
     test (an empty value refuses).
   - lines 295–299 (refuse at 298): RECEIPT-ENV-REDIRECT-SET, same shape, for GIT_OBJECT_DIRECTORY,
     GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE.
3. **GIT_INDEX_FILE gate** — lines 301–306. Line 304 `if "GIT_INDEX_FILE" in os.environ:` kept byte-identical; the
   2-line refuse at 305–306 keeps the shape with RECEIPT-INDEX-ENV-SET on the call line. Only the message body changed:
   the variable is named and its value is never echoed ("(value not shown); unset it and retry"). Base body echoed
   `{os.environ['GIT_INDEX_FILE']!r}` (r65 sentinel F4).
4. **git() helper** — lines 90–99 (def at 90, body 91–99). Keeps the GIT_DIR/GIT_WORK_TREE scrub and
   GIT_OPTIONAL_LOCKS=0; adds GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM=1, GIT_NO_REPLACE_OBJECTS=1 to env,
   and `-c core.excludesFile=<os.devnull>` to argv beside `-c core.fsmonitor=false` (line 98–99).
5. **_snapshot_entry()** — def at 154; line 176 mode mask `0o777` → `0o7777` (setuid/setgid/sticky recorded). Format
   stays `oct(...)`, so `_delta_label` (def 184, through ~199) still classes a mode-only flip as `mode`. The
   docstring (lines 155–159) names the full permission bits.
6. **Selftest** — cases 30 → **33** (`SELFTEST cases=33 pass=33 fail=0`, rc 0; existing case results and helpers
   unchanged). New functions: `case_31_env_config_refused` (1303–1326): GIT_CONFIG_COUNT triple (KEY_/VALUE_ names,
   value never echoed) and an EMPTY GIT_CONFIG_PARAMETERS refuse by name; `case_32_env_redirect_refused`
   (1327–1352): GIT_OBJECT_DIRECTORY, empty GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE (RECEIPT-ENV-REDIRECT-SET,
   names only), and GIT_INDEX_FILE with a value asserted absent from stderr (RECEIPT-INDEX-ENV-SET); `case_33_mode_setuid_refused`
   (1353–1377): dirty baseline accepted, then in-run chmod 644→4644 under --allow-dirty refuses with
   `RECEIPT-STATE-CHANGED-DURING-RUN: mode tracked.txt`. CASES entries at 1409–1411.

## Refusal classes and where they are raised (candidate line numbers)

| Class | Raised at |
|---|---|
| RECEIPT-ENV-CONFIG-SET | 293 (write_receipt env gate, before any git call) |
| RECEIPT-ENV-REDIRECT-SET | 298 (write_receipt env gate, before any git call) |
| RECEIPT-INDEX-ENV-SET | 305 (write_receipt, value no longer echoed) |
| RECEIPT-INDEX-UNMERGED | 132 (_flag_refusal, def 125) |
| RECEIPT-GITLINK-CONCEALED | 136 (_flag_refusal) |
| RECEIPT-INDEX-CONCEALED-ABSENT | 140 (_flag_refusal) |
| RECEIPT-INDEX-FLAG-CONCEALED | 143 (_flag_refusal; generic fallback) |
| lane worktree is dirty | 366 (dirty check) |
| RECEIPT-STATE-CHANGED-DURING-RUN | 480 (post-run compare; mode rows produced by _snapshot_entry line 176 and _delta_label) |

Not changed: no refusal class beyond the matrix's named ones was added; the other refuse() call sites (rev, instrument,
out, max-bytes, etc.) are unchanged in text and position.

## git() coverage

Every git call on the receipt path goes through git(): lines 112, 151, 315, 340, 349, 361, 382, 401, 462, 463 (11 call
sites total, incl. the def). The remaining `subprocess.run(["git", ...])` calls at 557–986 are in the selftest harness's
own fixture builders/asserters, run against fresh fixtures under --work (pre-existing, untouched). The wrapped command
(Popen at 434) and the signal-test Popen (715) are not git calls.

## Measurements

- C1 counter at the candidate commit (candidate/c1-run.txt):
  `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0`.
  REGRESS base=PASS, new=PASS (fixture `pass=8 fail=0` on both slots).
  Per-row new classes: E1/E2 RECEIPT-ENV-CONFIG-SET; E3 lane worktree is dirty; E4/E5/E6 RECEIPT-ENV-REDIRECT-SET;
  MOD2/MOD3 RECEIPT-STATE-CHANGED-DURING-RUN; base accepted E1–E6, MOD2, MOD3 (8 base forgeries).
- Writer selftest on candidate bytes (candidate/selftest.txt): `SELFTEST cases=33 pass=33 fail=0`, rc 0.
- No tools installed or upgraded; no pacman transactions; scratch under /fast/scratch/hyaku/souji-r66/S66ExecWriter/.
