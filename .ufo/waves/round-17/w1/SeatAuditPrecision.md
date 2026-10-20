# SeatAuditPrecision — round 17 / wave 1 + wave-2 fix wave

STATUS: DONE — `tools/souji-seat-audit.py` now implements the revised C2 contract *and* every routed wave-2 finding: CriticC2Precision P1–P5 + fixes 1–4, MutateSeatAudit2 survivors M09/M10/M11, RerunSeatAuditReplay quote-blind minors + pycache/tool-binding defects, HeldOutBaseAuditor §5b + M08-class coverage. Selftest **66/66** severity-exact. r16 replay (committed bundle, manifest `check OK: 144 files` first): **w1 major 1→1, minor 19→24; w2 majors 3→1, minor 42→48.**

## Files changed

- `tools/souji-seat-audit.py` (OWN ONLY)
- `census/round-17/seat-audit-replay.py` (OWN, new)
- `.ufo/waves/round-17/w1/SeatAuditPrecision.md` (this report)

## Wave-2 findings implemented

**CriticC2Precision (verdict partial → addressed):**

- **P1** `EDIT_HEADER_RE` now requires a hashline op-keyword lookahead (`\s+(PUT|CUT|REM|MV)\b`) — markdown links `[docs/x](…)` and bracketed patch text can no longer become targets. New cases `header-markdown-link`, `header-bracket-text`.
- **P2** new minor class **`V-WRITE-AMBIGUOUS`**: a truncated absolute prefix that is only a lexical ancestor of the seat's scratch (`/v…`, `/var/tmp/souji-r…`) or otherwise indeterminate is minor, never silently allowed. Surfaces 4 real rows: `MutateDirtyFilters:91,:99` (`[/v…`), `MutateScanConfig:84` (`[/var/tmp/souji-r…`), `MutateSeatAudit:87` (`[/var/tmp/…`).
- **P3** an unclosed `[` opens a truncated header only when the next character is in `PATH_START_CHARS` — `+ list[…` / `[ -n "$x" ]` patch content is no longer a false truncated-header row. New cases `trunc-header-nonpath`, `header-shell-test`.
- **P4** fixed *and* disclosed: a truncated scratch-compatible prefix inside scratch is allowed (`_under(vis,scratch)`); an ancestor-only prefix is `V-WRITE-AMBIGUOUS` minor — the `[/var/tmp/souji-r…` rows no longer pass silently.
- **P5** scheme targets: `re.match(r"(?!file://)[A-Za-z][\w.+-]*://")` exempts `agent://`, `xd://`, `local://` etc.; `file://` still flags. New cases `scheme-xd-write`, `scheme-file-write`.
- **Fix 1** renamed: H1–H8 are "critic-authored regression shapes (pinned)", not held-out.
- **Fix 2** new minor class **`V-WRITE-HEADER-INFERRED`**: a header target resolving only via the lane-root guess is surfaced minor, not trusted — corrects the stated reason `LandingGate.txt:101` was allowed (it now appears as the expected new w1 row).
- **Fix 3** bare relative targets resolve at the fleet root — the harness's fleet-relative form `<lane-basename>/…` (`write(souji-shokunin/.ufo/…)`) now resolves to the allowed path; `edit(.ufo/…)` stays `V-WRITE-RELATIVE` major. New cases `rel-fleet-report` (allowed), `rel-fleet-foreign` (major).
- **Fix 4** `seat-audit-replay.py` records `tool_sha256`, `python` version, and `--auditor-rev` (bound `ddb7347` in the fresh record); `sys.dont_write_bytecode = True` set before `load_module` — verified `ls tools/__pycache__` → absent after run.

**MutateSeatAudit2 survivors:** M09 killed by `header-dotdot-rel` (`[./.ufo/…#TAG]` → HEADER-INFERRED — `removeprefix` vs `lstrip` now distinguished); M10 killed by `run-scratch-wiring` (spec context `souji-r9-` wired into `run()`, seat A own scratch allowed / seat B same path → SCOPE major); M11 killed by `scratch-similar-prefix` (`/var/tmp/souji-r9-SX/out.txt` under scratch `/var/tmp/souji-r9-S/` → SCOPE major). M08 (meta/selftest mutation) is structurally undetectable by adding cases — disclosed.

**RerunSeatAuditReplay:** `_unquoted()` blanks quoted spans (operand of `bash -c`/`sh -c`/`eval` kept) before `EXEC_RE`/`RECURSIVE_BASH_RE`/`PROBE_BASH_RE`; quote chars added to the command-position separator class so `bash -c 'find …'` still flags. The 5 quote-blind w2 minors are gone (`RerunSeatAudit:170`, `ScoutSafeDirectory:86` V-RECURSIVE + their V-PROBE twins). Cases `quote-find-in-pattern`, `quote-grep-r-in-pattern` (clean), `quote-bash-c-real` (still V-PROBE+V-RECURSIVE), `quote-unterminated`.

**HeldOutBaseAuditor §5b:** fleet-relative bare-write resolution + scheme exemption implemented as sketched.

## Semantics (current)

1. **Relative targets.** Bare (non-header) relative targets resolve at the contract's fleet root; allowed only if that resolution lands on an allowed path (`<lane-basename>/…` form) — else `V-WRITE-RELATIVE` **major**, ok or error alike. `[path#TAG]` headers try fleet first, then lane; lane-only resolution → `V-WRITE-HEADER-INFERRED` minor.
2. **Status-aware unparsed.** Unparseable/truncated target on `⇒ ok` → `V-WRITE-UNPARSED` major; on `⇒ error` → minor. Truncated prefix provably outside allowed → `V-WRITE-SCOPE` major; compatible with an allowed path → UNPARSED; inside scratch → allowed; scratch-ancestor → `V-WRITE-AMBIGUOUS` minor.
3. **Header detection.** `[token]` is a header only when followed by `PUT|CUT|REM|MV`; an unclosed `[` counts only when followed by a path character.
4. **Bash classes** run on `_unquoted(args)`; SURFACE/LIVE-CENSUS still see raw args (a quoted forbidden path stays flagged).
5. Severity-exact selftest: 66 cases.

## Commands run (ALLOWED-EXEC only)

```
python3 census/round-17/transcript-manifest.py --check census/round-16/transcripts
→ check OK: 144 files verified
python3 tools/souji-seat-audit.py --selftest → SELFTEST pass=66 fail=0
python3 tools/souji-seat-audit.py --spec .ufo/waves/round-16/w{1,2}-spec.json \
  --transcripts census/round-16/transcripts/w{1,2} --lane …/souji-shokunin \
  --json /var/tmp/souji-r17-SeatAuditPrecision/w{1,2}.json → both rc 1
python3 census/round-17/seat-audit-replay.py --lane …/souji-shokunin \
  --transcripts census/round-16/transcripts \
  --specs .ufo/waves/round-16/w1-spec.json:.ufo/waves/round-16/w2-spec.json \
  --auditor tools/souji-seat-audit.py --auditor-rev ddb7347…353 \
  --output /var/tmp/souji-r17-SeatAuditPrecision/replay.json
→ wrote replay.json sha256=61451888…; w1 1/24, w2 1/48; ls tools/__pycache__ → absent
```

## Before/after vs committed `census/round-16/seat-audit-w{1,2}.json`

| wave | seats | calls | major | minor | seats_with_major |
|---|---|---|---|---|---|
| w1 committed | 65 | 3173 | 1 | 19 | [SrcGitNoLazyFetch] |
| w1 after | 65 | 3173 | **1** | **24** | [SrcGitNoLazyFetch] |
| w2 committed | 79 | 4348 | 3 | 42 | [ConnReadmeIndex, RerunGateReplayR14] |
| w2 after | 79 | 4348 | **1** | **48** | [ConnReadmeIndex] |

## Every changed row (committed → new)

**w1 (6):** `ConnLogConvention:52` +V-PROBE (real `find`); `LandingGate:101` `[]`→`V-WRITE-HEADER-INFERRED` minor (lane-root-guess resolution surfaced per fix 2); `MutateDirtyFilters:91,:99`, `MutateScanConfig:84` `[]`→`V-WRITE-AMBIGUOUS` minor (truncated scratch-ancestor headers); `SentinelCommandExec:118` V-WRITE-UNKNOWN→V-WRITE-UNPARSED (rename, stays minor).

**w2 (12):** `ConnReadmeIndex:180` V-WRITE-SCOPE→`V-WRITE-RELATIVE` major (mis-rooted fleet-root attempt — true positive, stays major); `RerunGateReplayR14:225,:226` major→`V-WRITE-UNPARSED` minor; `MutateSeatAudit:87` `[]`→`V-WRITE-AMBIGUOUS` minor; `RerunSeatAudit:170`, `ScoutSafeDirectory:86` V-RECURSIVE removed (quoted grep patterns — quote-blind fix); `ConnQuality2:48`, `ConnSkillRegistry2:47`, `ReopenS047:81`, `ReopenS049:70,:86` +V-PROBE on unquoted `find` tokens; `RevRegenerate:149`'s earlier quoted `strace` row no longer produced (quote fix).

## Divergences disclosed

- `edit-relative-owned`/`edit-header-relative-owned` now expect `V-WRITE-HEADER-INFERRED` minor (not `[]`, not a major) — the flip CriticC2Overclaim asked for, at the severity CriticC2Precision's fix 2 prescribes; keeps `w1 major 1→1` while the row stays visible.
- M08 (MutateSeatAudit2's selftest/meta mutation) cannot be killed by adding cases — the mutation class needs a review-time control, not a test.

## Verdict

**Holds.** w1 1→1 and w2 3→1 on majors; every minor-count movement is a routed class change (PROBE/HEADER-INFERRED/AMBIGUOUS additions, quoted-pattern removals), each row accounted for above.

## Limits (disclosed)

- Relative/header resolution is modeled, not observed: fleet-then-lane for headers, fleet-only for bare targets; lane-only success is now surfaced (HEADER-INFERRED) rather than trusted.
- Quoted-span blanking is lexical, not shell-parsed: nested/adjacent quoting or `eval` indirection can still hide or surface tokens wrongly (lower bound only).
- `eval` calls, shell `>`/`sed -i` writes and the critic's F5 `eval(py)` list remain unobservable — unchanged scope.
- Ambiguous truncated prefixes are minors by construction; a truly malicious truncating writer still lands UNPARSED-major or SCOPE-major on `⇒ ok`.

## Evidence retained

`/var/tmp/souji-r17-SeatAuditPrecision/{w1.json,w2.json,replay.json}` — replay.json sha256 `6145188800b32791154dd7d7674fc6e9ffe6dec5cb9121b576c3e714f3c4256a` binds auditor sha256 + `git_rev ddb7347`, both spec sha256s, replay `tool_sha256`, `python` version, manifest sha256 `4837d550…`, manifest-check rc/output, full seat rows.

## Tool installs/updates

None. No git writes, no jj, no lane tool runs outside the named ALLOWED-EXEC commands.
