# SwarmSentinel37 — credential and private-URL sweep (round 31, wave 1)

Read-only seat. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin` at tip
`1b811368461785040e955f41f9c97e62f61fd67c` when the sweep ran. Nothing written except
this report; no tool installed or upgraded this run.

## Status

STATUS: PASS — 0 secret-material hits across the wave-1 outputs (66 peer files, incl.
`sources/`) and 0 token/key/`op://` material in the 311 prior-round seat reports M1 carries;
the pattern set is proven live by a 2,994-file control whose fixture canaries fire. One
credential-adjacent, non-secret `git config` dump (F1) is the only observation, in a
prior-round report.

## Evidence

Sets (all under the lane root):

- **A** = every peer file under `.ufo/waves/round-31/w1/` → **66** files (includes `sources/`, 4 files;
  this report is excluded so the sentinel does not count its own pattern names). Final re-scan at
  `2026-10-26T06:38:10Z` over all 66: counts unchanged. Manifest sha256 over sorted
  `path\tbytes\tsha256` lines: `0ef0022e957e1e8282d4e74a2dc55579c38248b2a93621f6ff7bda519557f3f0`.
  Files landed after that snapshot are not covered; re-running the reproduction below re-pins them.
- **B** = seat reports: files under `census/round-2{6,7,8}/waves/` and `.ufo/waves/round-26/`
  whose text matches `(?m)^STATUS: (PASS|PARTIAL|FAIL)` → **311**
  (round-26 87, round-27 78, round-28 58, `.ufo/waves/round-26` 88). Every report cited by
  M1's carry deliveries (26 r26 + 29 r27 + 19 r28) is inside B; the four M1-cited artefacts
  with no STATUS line (`axis-check-docs.md`, `gate-draft.md`, `lesson-r26.md`,
  `scorecard-r26.md`) are covered by C instead, and the fifth M1 path, `ControlSeat20.md`,
  exists only in M1's scratch control commit (a planted gate control), not in the lane.
- **C** (positive control) = all files under the same four trees → **2,994**.

Sweep executed with `python3 -B` (regex set below), counts per set:

| pattern | A (66) | B (311) | C (2,994, control) |
|---|---:|---:|---:|
| `-----BEGIN … PRIVATE KEY-----` | 0 | 0 | 0 |
| `ghp_…` | 0 | 0 | 0 |
| `github_pat_…` | 0 | 0 | 0 |
| `sk-…` | 0 | 0 | 2 (synthetic canary) |
| `xox[abposr]-…` | 0 | 0 | 4 (synthetic canary) |
| `AKIA[0-9A-Z]{16}` | 0 | 0 | 14 (synthetic canary) |
| `op://…` | 0 | 0 | 0 |
| `Authorization:` header | 0 | 0 | 0 |
| `Bearer` or `Basic` credential blob | 0 | 0 | 2 (synthetic canary) |
| URL with embedded credential pair | 0 | 0 | 6 (fake `user:pass@example.test`) |
| home-directory secret paths (ssh/aws/gnupg/kube/docker/netrc/npmrc/pypirc/git-credentials/pgpass dot-dirs, cloud-CLI config dirs, private-key filenames) | 0 | 0 | 240 (credential-filename literals inside scanner code/tests; 13 distinct strings, none a real home path) |

Supplementary set (15 patterns: Google `AIza…`, GitLab `glpat-…`, npm/pypi/docker registry
tokens, `eyJ…` JWT, Slack webhook, password/secret assignments, `x-api-key` header, `AWS_*`
env assignment, 1Password session variable, `machine … login … password …`, OpenSSH public
key, PEM certificate, credential-env names): **A 0, B 0**.
Query-parameter credential names (access token, token, signature, password): **A 0**.
Binary/NUL-bearing files in A: **none**; hidden files in A: **none**.
URL hosts in A: `raw.githubusercontent.com`, `github.com`, `git-scm.com`, `pre-commit.com`,
`docs.jj-vcs.dev` only; `userinfo`-without-password 0.

Reproduction (executed; file-set construction plus the regexes above):

```
A: find /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1 -type f
B: find census/round-2{6,7,8}/waves .ufo/waves/round-26 -type f | xargs grep -lE '^STATUS: (PASS|PARTIAL|FAIL)'
C: find census/round-2{6,7,8}/waves .ufo/waves/round-26 -type f
python3 -B  # re.finditer over each file's text, counts summed; regexes = the table rows
```

Provenance of the new inputs (read-only, no fetch this run):

```
$ cd .ufo/waves/round-31/w1/sources && sha256sum -c SHA256SUMS
git-reflog.adoc: OK      gc.adoc: OK      git-compatibility.md: OK      (3/3)
```

All three receipt rows name public `https://raw.githubusercontent.com/...` URLs for
`git/git v2.56.0` and `jj-vcs/jj v0.45.1`, `http 200`, sizes 5657 / 7753 / 12284 — equal to
the staged byte counts; no userinfo, no query token.

## Findings

1. **F1 (low, pre-existing, not a secret value, not carried)** — `census/round-26/waves/w1/LabGitVersion.md`
   (byte-identical copy at `.ufo/waves/round-26/w1/LabGitVersion.md`) commits a full
   `git config --list --show-origin` dump: 9 `credential.*` lines (lines 64–71, 76) naming
   `!/home/<user>/.local/bin/gh auth git-credential`, a vendored helper binary for a
   **private vendor git host (redacted)**, and `credential.helper=…git-credential-libsecret`;
   31 config-origin lines exposing `/home/<user>/.config/git/config`, plus aliases and the
   throwaway probe identity `probe` / `probe@example.invalid`. No token, password, or key
   value is present. Exploit path: a reader of the committed report learns which helper
   binaries hold credentials and the name of a private git endpoint — a ready target list;
   the same dump technique would exfiltrate tokens on a host whose config held them.
   Impact: host/endpoint and credential-wiring disclosure only. Smallest remediation: when
   such a dump is quoted, emit key names only and redact helper commands and origins (this
   file is a PASS report at line 5 and M1 does not copy it, so nothing new propagates; the
   committed file can only be corrected by an L1-appended erratum, never in place).
2. **F2 (informational, provenance)** — `deliver-fetch-receipts.tsv:2-4` states `snapshot`
   paths `census/round-31/sources/<basename>`, but that directory does not exist at tip
   `1b81136`; the bytes are staged at `.ufo/waves/round-31/w1/sources/`, and
   `deliver-c3-anchor-lines.md:4-5` + `SwarmExecutor09.md:88` declare the L1 landing step.
   Not a defect if landed; until then the receipts are unverifiable provenance. Landing
   check: directory exists and `sha256sum -c SHA256SUMS` returns 3/3 OK.
3. **F3 (informational, do not clean)** — round-26 fixture trees contain deliberate
   credential-shaped canaries: `census/round-26/waves/assimilation/validate/tests/fixtures/r18-proc-census.sh:107-108`
   (`AKIA…`, `xoxb-…fake-not-a-token`), `…/r21-reason-canary.sh:62-68` (`sk-…FAKE`,
   `AKIA…`, `Bearer …FAKE`, a URL with a fake credential pair before `@host`), the
   `.ufo/waves/round-26/…` duplicates,
   and `…/tests/fixtures/case-F10/creds.pem` (132 bytes, first line: "souji F10 fixture —
   synthetic placeholder, not a key, never read"). These are what make the control fire;
   they are not leaks and must stay (hard bound: this seat deletes nothing).
4. **F4 (informational, classified non-credential)** — the `localhost` matches in A are
   `user.email=probe@localhost` inside `deliver-a1-regex-receipt.txt:101` (throwaway git
   identity for a scratch commit), not URL credentials; `swarm-registry.json` is the only
   non-0644 file in A (mode 0600) and carries no credential fields (`schema`, `wave`,
   `createdAt`, `updatedAt`, `reportDir`, `members`).

## Deliveries

- `.ufo/waves/round-31/w1/SwarmSentinel37.md` (this report). No other file written; no
  scratch directory created, so none to remove.
