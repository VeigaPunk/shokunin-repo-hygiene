# S30 runner — evidence summary (round 4, Obsidian-CLI vault verification)

Date: 2026-10-18. Seat: S30 (identical runner + supplementary r4 candidate
matrix). Tool under test for the identical runner: `tools/souji-verify.sh`
(sha256 7efda63bd760…, the installed r2 artifact).

## Deliverables

| file | what |
|---|---|
| `tests/results/vrun-30.json` | identical-runner fragment: 26 pass / 0 fail / 11 info, status=pass |
| `tests/vault/runner-30.sh` | the runner (sha256 45125b2fdafc…) |
| `tests/results/vrun-30-r4.json` | supplementary round-4 candidate matrix |
| `tests/vault/runner-30-r4.sh` | matrix harness (sha256 fc4898ee6f42…) |
| `tests/vault/s30-adjudicate.sh` | S55-FAIL adjudication harness (13/14 pass; A11 real) |
| `tests/vault/s30-r4-raw/*.out` | raw per-tool outputs of every matrix case |

## Headline findings

1. **Official CLI entry point: absent on this host (NOT-VERIFIED as an
   execution path).** No shim at `~/.local/bin/obsidian` or
   `/usr/local/bin/obsidian` (twice-censused). Asar strings declare the
   mechanism: client = electron run as `obsidian-cli`; socket =
   `$XDG_RUNTIME_DIR/.obsidian-cli.sock`; shim = symlink named `obsidian`
   in `~/.local/bin`. `/usr/bin/obs` is OBS Studio (not Obsidian).
   `/usr/bin/obsidian` is the GUI launcher (bash → `electron43
   /usr/lib/obsidian/app.asar`) — never executed by this seat.
2. **Socket observed live during the round** (app launched externally at
   13:58:37, pid 2203988; exited; relaunched 14:05, pid 4127347, still
   LISTEN at 14:09). The app is operator-controlled; souji never starts it.
3. **sha256sum fallback is the operational vault-side receipt** — verified
   live against the real vault by every candidate.
4. **S55's false-SAFE FAILs are a probe-design confound, not tool bugs.**
   Adjudication with isolated single-row ledgers: 12/13 of S55's bad-row
   cases flip to NOT-SAFE when isolated (A1–A10). Root cause: S55 wrote
   several rows for the same source path in one ledger; the tool returns
   SAFE on the first fully-matching row (a matching row exists), so a later
   bad row cannot flip it. B1/B2 replicate both orderings and both yield
   SAFE by design.
5. **One genuine S55 finding survives:** a valid ledger row WITHOUT a
   trailing newline is dropped (`read` drops unterminated final line) →
   NOT-SAFE (conservative, never a false-SAFE). Reproduced isolated (A11;
   vrun-30.json V14). Recorded as info-level in the identical runner;
   direction is conservative.
6. **Round-4 candidate matrix (normalized: VERIFIED==SAFE):**
   - `souji-vault-verify.impl-20.sh` (52885564f324…): 16/16 measured pass
     (selftest 35 checks 0 fail). CLI disagreement path verified live:
     `cli=disagreement(claimed=000000000000)` on a lying mock; bounded on a
     hanging mock; launcher-shaped CLI not executed.
   - `souji-vault-verify.impl-24.sh` (2b224647abed…): 16/16 measured pass
     (selftest 13/0). `--cli` is probe-only: never executes any CLI
     (mock call count = 0 in all modes); reports cli-state (socket-live /
     unavailable) and degrades cleanly.
   - `tools/impl-21.sh` (ed1881e8fd82…): **2 failures** — (a) its own
     `--selftest` fails (rc=1: L2 false-SAFE on a self-move-shaped fixture,
     C1 evidence contract); (b) **crash on a lying CLI**: `line 322/786:
     vh: unbound variable` (rc=1, no verdict line). Its GUI-content guard
     works (launcher-shaped CLI not executed; marker absent).
   - `tools/souji-verify.sh` (r2 baseline): 12/12 measured pass.
7. **obsidian-cli-inspector is NOT the official CLI** (v1.0.3, third-party,
   own sqlite index). Its `hash` column is a `size:mtime` pseudo-hash
   (e.g. `15ed:1791921146`), not a content digest — it cannot serve as the
   vault-side sha256 receipt. Confirmed first-hand via read-only sqlite
   query of `~/.config/obsidian-cli-inspector/vault.db`.
8. **Guards held all round:** real vault byte-identical before/after every
   battery (58 files, manifest 449d1e6c…; vault untouched), live ledger
   header-only and sha-unchanged (3f7e9f2ab9e6…, 1 line), no Obsidian GUI
   process spawned by any seat-30 action (pgrep before/after equal).

## Adjudication verdicts (isolated single-row replays)

A1 bad-src NOT-SAFE PASS · A2 bad-vault NOT-SAFE PASS · A3 empty-src
NOT-SAFE PASS · A4 empty-vault NOT-SAFE PASS · A5 both-empty NOT-SAFE PASS ·
A6 dir-empty NOT-SAFE PASS · A7 dir-ok SAFE PASS · A8 vault-missing
NOT-SAFE PASS · A9 vault-is-dir NOT-SAFE PASS · A10 reordered NOT-SAFE
PASS · A11 nonl-row SAFE **FAIL** (real: row dropped) · B1/B2 shared-ledger
orderings SAFE (confound confirmed) · B3 only-bad-row NOT-SAFE PASS.

## Caveats

- impl-20 was edited mid-round (14:07, sha 52885564…); matrix results above
  are against the final sha shown. impl-20 had a transient syntax error at
  14:03 while its seat was still writing — do not grade the intermediate.
- Candidate tool naming differs from the assignment's guess; the selection
  order in both runner-30.sh and runner-30-r4.sh prefers
  `tools/obsidian-vault-verify.sh` → `tools/vault-verify.sh` → `*vault*` →
  `*obsidian*` → `souji-verify.sh`.
