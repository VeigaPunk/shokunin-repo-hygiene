# R13 w1 — CertProtocol (C1 calibration support, executable no-relay protocol)

Seat: `SoujiR13.CertProtocol` (executor, leaf). Lane root:
`/home/vgpnk/Projects/shokunin/souji-shokunin`. Baseline HEAD: `31984f4`.

**No suite, gate, fixture, build, lint, formatter, or install was run by this seat.** All counts in
the deliverable are static derivations from the baseline blobs, marked `[derived]`. Certification
remains **OFF**. This seat is not an independent non-author verifier.

## Files changed

- `census/round-13/cert-protocol.md` (new, 718 lines, sha256 `c6fb66d71b65500ca3300fe15bafaa9138358ee7dc37be4f54fb6981ffd37f8b`) — the protocol.
- `.ufo/waves/round-13/w1/CertProtocol.md` (this report).
- Nothing else. No commits. No shared bookkeeping touched. Operator sweep not read.
- Tools installed or updated: **none**. Read-only host probes used existing `git 2.55.0`,
  `bash 5.3.15`, `rg 15.1.0`, `shellcheck 0.11.0`, `python3 3.14.7`, coreutils.

## What the protocol specifies

1. **Installed set and installed bytes.** Exactly four paths (`tools/souji-verify.sh`,
   `souji-vault-verify.sh`, `souji-census.sh`, `souji-quarantine.sh`), each certifiable only when
   the worktree file and `git show HEAD:<path>` are byte-identical. Baseline blob sha256:
   `9adb1764…` / `f9e778ca…` / `6a000c59…` / `141c0fdc…` (full digests and blob oids in §3 of the
   protocol).
2. **One author → one tool → one suite → one fragment → one raw evidence file.** Fragment and
   evidence paths are author-bound and write-once (`noclobber`, Python `open(..., "x")`). A redo gets
   a new `run_id` at a new path; no file is ever edited or re-run in place. The parent aggregates by
   listing paths in `manifest.json`, never by writing into a fragment (`census/round-11/dissent-32.md`
   §4-§5 is the defect this replaces).
3. **Bounded commands.** `timeout --signal=TERM --kill-after=15` with per-tool limits (300 s
   verify/vault/census, 600 s quarantine), forced `TMPDIR=/var/tmp`, isolated `HOME` under
   `/var/tmp`, selftest guard variables unset, single-writer redirection. `rc=124/137` is a failure,
   never a pass; the summary must read `selftest: N checks, 0 failed`.
4. **Fragment schema.** The gate-required keys (`author`, `class`, `artifact`, `sha256`, `command`,
   `exit_code`, `verdict`, `evidence`, `evidence_sha256`) plus protocol keys (`run_id`, `checks`,
   `expected_checks`, `count_command`, host versions, timeout, timestamps). `expected_checks` is the
   anti-silent-skip tripwire.
5. **Completeness preflight** (`cert-manifest-check.sh`, L1 writes it from the protocol body) because
   the gate deliberately has no installed-tool allowlist and can return `clean` for a one-fragment
   manifest (`tools/souji-cert-evidence.py` docstring lines 97-99). The preflight enforces exactly
   four artifacts, distinct authors, digest equality with worktree **and** HEAD, evidence digests,
   summary regex, floors, and no unexpected `SKIP`.
6. **Gate + frozen snapshot commands.** Live gate expected `clean` /
   `summary fragments=4 assessed=4 pass=4 fail=0 findings=0`; frozen expected `clean` /
   `frozen_files=13`. `expected.json` is named as a caller trust anchor, not self-authenticated.
7. **Candidate selection by class probes, never check count.** Installed paths only; the gate's
   `artifact-candidate` finding rejects `cand-*`; class rows are pre-registered and red-before is
   required. Grounded in `dissent-32.md` §6 (impl-46 had 67 checks and failed the class;
   `cand-census-08` had 35 and closed it) and QUALITY Q6.

## Suite inventory — derived from code, not old results

| tool | code range | inventory | expected summary | floor |
|---|---|---|---|---|
| `souji-verify` | `run_selftest` 1223-1284 | 18 `st_case` + 3 `st_status` + H6 + H1/H5 + R9 16 | `selftest: 40 checks, 0 failed`, exit 0 | 38 if R9 locale `SKIP` |
| `souji-vault-verify` | 1441-1590 | 21 `st_case` + 2 `st_status` + 9 explicit + 3 audits + R9 16 | `selftest: 51 checks, 0 failed`, exit 0 | 49 |
| `souji-census` | 511-793 | 33 `st_ok` sites, one 4-iteration loop at 761-769 → 32+4 | `selftest: 36 checks, 0 failed`, exit 0 | 36 |
| `souji-quarantine` | 1304-1514 | 50 `st_check` + 1 `st_ok` + R9 28 | `selftest: 79 checks, 0 failed`, exit 0 | 77 |

R9 multiplicities from `tools/souji-round9-selftest.sh`: verify/vault get 16 (2×nested-stale,
2×nested-pushed, 1 gitfile, 2×2 worktree-discovery, 1 readonly-index, 2 locale, 2×2 ledger);
quarantine gets 18 base (same, but 3×2 ledger because the quarantine branch has abort + staged-bytes
+ revocation-reached) plus 3×2 NUL-list and 2×2 default-ref = 28. The Turkish-locale block is
conditional (`:162,176`), so `N` is recorded in the fragment rather than hard-coded. Host
prerequisites for the active locale block are present (`/usr/share/i18n/locales/tr_TR`, UTF-8
charmaps, `localedef`).

Structural bound: quarantine has 51 internal sites and at most 28 R9 checks, so the historical
`quarantine 91/0` (`SCORECARD.md:65`, `census/round-11/S08-fragment.md:50`) cannot describe these
bytes. The protocol lists five old claims (INSTALL.json `7efda63b…`, r3 `24/24`, r11 `40/51/91`,
census `35`, census `36/36`) and states why none is admissible without its own evidence and
`run_id`.

## Decision: broad certification NO (blockers, with citations)

| blocker | observed at baseline |
|---|---|
| Q8 open in installed quarantine | `grep -c timeout` = 0; unwrapped `git mv` at `souji-quarantine.sh:529`, `mv --` at `:536`; digests via `content_digest` `:196`, whose `file_sha` resolves to the last definition `:722` (`:184` is dead), and `dir_digest` `:727` shadows `:186`; no FIFO case in `run_selftest` 1304-1514 |
| No admissible evidence set | `census/round-13/cert/` absent; gate untracked and changing (1377→1442→1509 lines observed during the wave); `tests/results/INSTALL.json:4` pins `7efda63b…` while HEAD `tools/souji-verify.sh` is `9adb1764…` |
| Gate lacks coverage enforcement | docstring 97-99: no allowlist; zero/one-fragment manifests can be `clean`; protocol preflight is new and unproven |
| Harnesses do not satisfy Q4 literally | `souji-census.sh:418,516` use `${TMPDIR:-/tmp}` with no `/var/tmp` literal; `souji-verify.sh:1105`, `souji-vault-verify.sh:1308`, `souji-quarantine.sh:1247` do the same and only get `/var/tmp` from a top-level export (`:490`, `:680`, `:685`) |
| No Q5/Q7/Q9 completion | blind re-derivation, guarded commit, and `shellcheck -S warning` are still pending L1 |

Admissible at most: a per-tool `suite-green, evidence-consistent` row, with deletion authorization
explicitly unchanged. Flip conditions (future, not this round): four valid rows + COMPLETE preflight
+ live/frozen `clean` + named blind re-derivation + Q9 green + operator decision.

## Risks

- `tools/souji-quarantine.sh` and `tools/souji-cert-evidence.py` are both moving under other seats;
  at the end of this seat's work the worktree showed `M tools/souji-quarantine.sh` (C2 in flight).
  The protocol anchors to the baseline blob only and requires re-derivation of `expected_checks`
  after integration. A fragment that hard-codes 79 after C2 adds cases will fail the equality check
  by design.
- The preflight cannot prove a command was executed; the gate says the same (docstring 136-139).
  Author identity is an unauthenticated string. Both are stated as limitations, not papered over.
- The gate selftest depends on `tests/fixtures/r13-cert-frozen/`, absent at observation; until C1
  commits it, the gate selftest exits 2 `selftest-unavailable`.
- Q8's literal grep is a proxy; a correct wrapper behind a function could still fail it. The protocol
  requires both the grep and the behavioral red-before fixture and says the fixture outranks the
  proxy.

## Probes and scope

One early lane-wide `grep -rIn` for `cert-16` / relay tokens may have traversed
`census/operator-sweep-20261019/`; it returned no sweep paths, no sweep content was read, opened, or
used, and every later probe was scoped to `tools/`, `corpus/`, `census/round-1x/`, `LOG.md`,
`SCORECARD.md`, `PROVINCE.md`, `SKILL.md`, and fixture directory names. No credentials or secrets
were read. No `cd` was used; git calls used `-C`.

## Blockers

None for this slice. The deliverable is a protocol, not a certification: no runs were permitted, and
the decision it records is NO for broad certification this round.
