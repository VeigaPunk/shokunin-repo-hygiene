# SwarmSentinel30 — credential and private-URL sentinel, round 32 attempt 2, wave a2w1

## Status

STATUS: PASS — the landed surface (`85b61a151923986e7e6b48f7084b9122561b5f3d..master`, 70 files, 4686 insertions, 0 binary) and the a2w1 wave files (27 at the snapshot, 30 at the closing sweep) carry **0 private-key armor, 0 `ghp_`/`github_pat_`/`sk-`/`xox`/`AKIA` tokens, 0 `op://` refs, 0 value-bearing `Authorization`/`Bearer`/`Basic` headers, 0 URLs with userinfo, 0 home secret paths**. The 39 home-path, 2 `op://`, 2 userinfo and 3 `Authorization` shaped hits in w1 are (a) the w1 sentinel's own rule text, (b) two deny-list tools, (c) the committed round-21 synthetic canary — each located below and re-verified against the landed master copies.

## Evidence

Contract read first: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/records/preregistration.txt` (32 lines, frozen). Lane tip at scan: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse master` → `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`. Diff dumped to scratch and hashed: `git -C <lane> diff 85b61a151923986e7e6b48f7084b9122561b5f3d master > full.diff` → `5680 lines / 358114 B / sha256 b1fb8ccdd37cf451…`; `--numstat` → 70 files, no `-` (binary) row; `--name-status --find-renames` → 47 `A`, 23 `M`, 0 rename.

Per-pattern counts (`grep -acP` on the diff; `grep -raP … | wc -l` on each wave dir; `-a` forces text):

```
class       diff  w1  a2w1   pattern
keyarmor    0     0   0      -----BEGIN [A-Z ]*PRIVATE KEY
ghp         0     0   0      ghp_[A-Za-z0-9]{16,}
ghpat       0     0   0      github_pat_[A-Za-z0-9_]{16,}
sk          0     0   0      sk-[A-Za-z0-9_-]{16,}
xox         0     0   0      xox[abposr]-[A-Za-z0-9-]{8,}
AKIA        0     0   0      AKIA[0-9A-Z]{12,}
opref       0     2   0      op://
authz       0     3   0      (?i)authorization[[:space:]]*[:=]
bearerAny   0     4   0      (?i)\bbearer\b
basic       0     0   0      (?i)\bbasic[[:space:]]+[A-Za-z0-9+/=]{8,}
userinfo    0     2   0      [A-Za-z][…]*://[^/@[:space:]:]+:[^/@[:space:]]+@
homepath    0    39   0      \.ssh/|id_rsa|id_ed25519|id_ecdsa|\.aws/|\.netrc|\.pgpass|\.gnupg|
                             \.config/gh/hosts|\.docker/config\.json|\.kube/config|\.config/op/|
                             \.local/share/op/|\.password-store|\.git-credentials|\.npmrc|
                             \.pypirc|\.local/share/keyrings|\.config/gcloud
```

Supplementary classes, same scope, all `0` on the diff and on a2w1 (w1 counts in `## Attack log`): `ASIA[0-9A-Z]{16}`, `AIza…`, `glpat-…`, `pypi-AgEIcHlwaS5vcmc`, `_authToken=`, `AccountKey=`, `(sk|rk)_live_…`, `npm_…`, `hf_…`, `hooks.slack.com/services`, `-----BEGIN PGP`, `ssh-rsa AAAA…`, `-----BEGIN OPENSSH`, JWT `eyJ….…`, RFC1918 addresses, `.local|.internal|.corp|.lan|.home.arpa` hosts, `git@<host>:` / `ssh://`, generic `(token|secret|password|api_key|access_key|client_secret)\s*[:=]\s*<12+ chars>`.

Zeros are measured, not assumed: a 30-line control file in scratch fires 18/18 token/armor/auth/URL classes, 13/13 home-path alternatives, 3/3 RFC1918 samples (`https://192.168.1.10/admin`, `http://10.0.0.5:8080/x`, `https://172.16.4.9/x`), and a synthetic base64 `Basic dXNlcjpwYXNz…` sample. The committed round-21 canary fixture `census/round-21/reason-oracle-before.txt` fires 6 of the value classes, confirming the patterns match real shapes in this repo.

Surfaces: w1 `107 files / 31846 lines / manifest 3aa5248340db1f18`; a2w1 `27 files / 2669 lines / manifest 37b2c49b3daeab38` (sha256 over sorted `name+content`; the tree grew 19 → 27 files while this seat ran, see the delta below).

Delta and self-scan. After the report above was drafted I re-took the snapshot and re-ran the full class set: diff unchanged (`sha256 b1fb8ccdd37cf451`, tip still `4e56c48`), w1 unchanged at `3aa5248340db1f18`, a2w1 grown to the 27-file `37b2c49b3daeab38`. The files added while this seat ran — `SwarmCritic19.md`, `SwarmCritic26.md`, `SwarmExecutor17.md`, `SwarmExecutor18.md`, `SwarmMutationTester15.md`, `SwarmReviewer11.md`, `SwarmReviewer14.md`, `SwarmScribe32.md`–`34.md`, `deliver-lesson-sections.md`, `deliver-records-w2.md`, `deliver-report-draft.md` and this report — were swept in place with all 30 classes: `0` value-bearing hits; a closing snapshot taken just before cleanup (`a2w1 30 files / 3010 lines / manifest 632dff5d9a96a30e`, w1 unchanged) re-ran the same set with the same result. The only files outside this report that match any class are five w1 files already analysed (`deliver-souji-evidence-cache.py`, `deliver-souji-preservation-evidence.py`, `deliver-souji-receipt-run.py`, `deliver-r13-run-verification.py` — deny-lists and the redaction regex) and `w1/SwarmSentinel43.md` (its own rule text); nothing in a2w1 matches. Self-scan, disclosed: this report matches 6 of its own lines because it names the patterns (`op://` ×2 in Status and the table, `Authorization` ×1 pattern literal, `Basic` ×1 control, `.ssh/|id_ed25519` ×4 in Finding 2 and the deny-list text). The one `Basic` control is written truncated (`Basic dXNlcjpwYXNz…`); no value is reproduced anywhere in this report.

URL hosts in the landed added lines (`grep -aoP 'https?://[^/[:space:]"]+' full.diff | sort | uniq -c`): `raw.githubusercontent.com` 26, `git-scm.com` 24, `docs.jj-vcs.dev` 5, `gnu.org` 2, `man7.org` 2, `github.com` 2, `docs.python.org` 2, `shellcheck.net` 1, `web.archive.org` 1 — all public; `0` absolute addresses, `0` userinfo. w1/a2w1 add only `example.invalid` (RFC 6761 reserved, 4) and the round-21 canary pair.

Tree-wide filename sweep at master (`git ls-tree -r master --name-only | grep -nE '(\.env|\.netrc|\.pgpass|id_rsa|id_ed25519|id_ecdsa|credentials|\.npmrc|\.pypirc|hosts\.yml)$|\.(pem|key|p12|pfx|keystore|jks)$'`, 8156 entries): 3 hits, all the same pre-existing round-26 fixture blob.

No tool installed or upgraded this seat (`RULES.md` read; pacman untouched; no `uv`/`npx`/binary install).

## Findings

1. **PASS — the landed diff is credential-free across 30 pattern classes.** Location: `git -C <lane> diff 85b61a151923986e7e6b48f7084b9122561b5f3d master`, 70 files, 4686 added lines. Includes the five C3 vendor snapshots (`census/round-32/sources/gitformat-pack.adoc` 704 lines and peers), all six after/before records, the two counters and the r32 fixture.

2. **INFO — every shaped hit in w1 is a deny-list, a redaction regex, or the round-21 canary.** `deliver-souji-evidence-cache.py:124-138,288-309`, `deliver-souji-preservation-evidence.py:160-172,379-400`, `deliver-r13-run-verification.py:48` name `~/.ssh`, `.aws`, `.password-store`, `.git-credentials`, `.npmrc`, `.pypirc`, `.local/share/keyrings` only as refused trees; `deliver-souji-receipt-run.py:90` is the redactor `(?i)(authorization:\s*bearer\s+)\S+` → `\1[REDACTED]`; `SwarmSentinel43.md:7,37,52,70-93` is rule text with `…`-truncated canaries. Verified against the **landed** master copies, not the delivery: `tools/souji-evidence-cache.py:411-417` and `tools/souji-preservation-evidence.py:494-500` use `expanduser("~")`/`pwd.getpwuid` only to build `PROTECTED_SYSTEM + home/PROTECTED_ABSOLUTE` deny trees, and the only `.ssh` write, `_write_text(home / ".ssh/id_ed25519", "synthetic home, never read\n")` (`evidence-cache:1299-1306`, `preservation:1958-1964`), targets `home = base / "home"` with `base = Path(tempfile.mkdtemp(prefix=…))` and `HOME` repointed to it. No `open|read_text|read_bytes|iterdir|glob` in either file names a home or secret path.

3. **INFO — the three `creds.pem` files are one pre-existing synthetic placeholder.** `tests/fixtures/case-F10/creds.pem`, `census/round-26/waves/assimilation/validate/tests/fixtures/case-F10/creds.pem`, `.ufo/waves/round-26/assimilation/validate/tests/fixtures/case-F10/creds.pem` — all blob `8d4b36847fafba0105e21eefaa02d1176d20a6d5`, 132 B, body `# souji F10 fixture — synthetic placeholder, not a key, never read`. Unchanged this round (0 diff hits); no action.

4. **LOW — uncommitted worktree state at scan, outside the committed diff, and one provenance trap in it.** `git -C <lane> status --porcelain` → ` M SKILL.md`, ` M tests/fixtures/r15-preservation-frozen/expected.json`, ` M tests/fixtures/r15-preservation-frozen/record.json`, `?? census/round-32/records/a2-l1-salvage-tip-measure.txt`. Not credential material (swept: 0 hits, all 30 classes). But `record.json` now pins `"measured_commit": "4e56c48b8fc828f9aba2746e324dc46aa538bdbf"` — the orchestrator **salvage** commit, whose own message says "not a landed round" — and embeds a literal `/var/tmp/souji-r16-repin.lzfjr0et/changed/tools/souji-census.sh` path, i.e. a scratch root that will be reaped. Impact: if this state is landed as-is, the r15 frozen record measures a non-landed commit and cites a deleted path, so a later `--frozen` re-measure cannot reproduce it. Smallest remediation for the L1: either re-run the repin against the final tip with a TMPDIR-rooted path and land both JSON files together, or revert the two JSON files and leave the pin at `005f3d37…`; the `/var/tmp` literal must not enter a committed record (it also contradicts C2's own claim). This is the only dirt in the lane worktree; the dirty `SKILL.md` hunk also fixes `../census/...` → `census/...` text, benign.

5. **INFO — this sweep closes the w1 sentinel's surface gap.** `SwarmSentinel43.md` scanned at `HEAD 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1` (246 files); the four commits after it — `98e5203` C2, `a92e1aa` C3+A1+defect 2, `9e8982b` C1, `4e56c48` salvage — added 70 files / 4686 insertions that it never saw. Those are this report's primary surface and are clean; its w1 findings 1-4 also still hold at the landed tip.

6. **INFO — the C3 fixture and record carry no identity or credential material.** `tests/fixtures/r32-jj-mtime-clock.sh` sets `NAME=r32-mtime-clock`, `EMAIL=r32-mtime-clock@example.invalid` per invocation (`--config user.name=… user.email=…`, line 88), refuses a `TMPDIR` inside the lane or fleet root (lines 62-68) and builds under `mktemp -d "$TMPDIR/…"`. `grep -nP '\b(fetch|push|remote|clone|ls-remote|credential)\b'` → no match, so no credentialed transport is reachable; the only tool calls are `jj git init --colocate`, `git gc`/`cat-file`/`update-ref`-class calls and `touch`. The committed record `census/round-32/records/jj-mtime-clock-run.txt` holds 24 lines of `jj-version`/`git-version`/`RESULT` only. It does not neutralize `HOME`/`GIT_CONFIG_GLOBAL`, so it inherits the caller's git/jj config (no secret is read, and the run is offline).

## Attack log

Sentinel seat; no C1/C2/C3 attacks filed. Probes run against my own sweep, since a zero is only evidence if the pattern can fire:

- **A — false negative in the assignment's private-URL class.** My first RFC1918 regex (`(10|192\.168|172\.…)\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}`) demanded 5 octets from the `192.168` branch and returned `0` on a control line `https://192.168.1.10/admin`. Fixed to `(?:^|[^0-9.])(?:10|192\.168|172\.(?:1[6-9]|2[0-9]|3[01]))\.\d{1,3}\.\d{1,3}(?!\d)`; control then 3/3, scope still 0. Every other zero in this report is backed by a control that fires — the w1 sentinel's `-e` incident (its Finding 5) is the same failure mode and this seat hit it independently.
- **B — assignment-literal class set can hide a key in a non-canonical shape.** Extended to 30 classes; w1's only generic-assignment hits are code identifiers, not values: `deliver-souji-landing-gate.py:877 token = token.rstrip(".,;:!?")`, `deliver-souji-declared-evidence.py:127 token = LINE_SUFFIX_RE.sub("", raw)`. Diff and a2w1: 0.
- **C — high-entropy strings that no token regex keys on.** `grep -aP '^\+' full.diff | grep -oP '[A-Za-z0-9+/=_-]{40,}' | sort -u`: 143 matching added lines, every distinct run is a 40-hex git revision (`85b61a15…`, `3ec84fc8…`, `a92e1aae…` …) or a 64-hex sha256 in a record, plus repo paths and `LANE=/home/vgpnk/Projects/shokunin/souji-shokunin`. No base64 blob, no key body.
- **D — environment capture into a committed record.** Landed counters pass the parent env down (`env = dict(os.environ, TMPDIR=tmp, GIT_CONFIG_NOSYSTEM="1", …)` at `census/round-32/c1-counter.py`, `c2-counter.py`, `c3-counter.py` added lines) and the r20 private-`/var/tmp` wrapper does the same (`tests/fixtures/r20-audit-contract.py:683`). No added line serializes `os.environ`, runs `printenv`, or echoes a child's env into a record; the records carry `ITEM`/`RESULT`/`SUMMARY`/sha256 lines only. Residual: a child that echoes `$GITHUB_TOKEN` in its own stderr would be captured by `capture_output` and could reach a record — no such child exists in the 27 C2 items or the C3 fixture, and no record in the landed set contains a token-shaped line.
- **E — hidden copy of a home secret into a shared scratch dir via the C2 TMPDIR move.** The two selftests that build a fake `$HOME` moved their `mkdtemp` root from `/var/tmp` to the caller's `TMPDIR` (`tools/souji-evidence-cache.py:1295`, `tools/souji-preservation-evidence.py:1956`); the fake home's only secret-shaped content is `synthetic home, never read` / `"0" * 64` digests, and the real `$HOME` is never a target (Finding 2). No exposure path.
- **F — out-of-scope hygiene noted, not pursued:** `tests/fixtures/r20-audit-contract.py:433` still creates `tempfile.mkdtemp(…, dir="/var/tmp")` at master; the C2 fix routes it through `_private_var_tmp()` (bwrap `--bind private /var/tmp` + re-exec, added hunk lines 663-684), which is a scratch-discipline question for the C2 owners, not a credential one. The wrapper binds the whole host root (`--dev-bind / /`), so it is a private `/var/tmp`, not a sandbox — accurate naming, no credential claim implied.

## Deliveries

- `.ufo/waves/round-32/a2w1/SwarmSentinel30.md` (this report)

Scratch `/fast/scratch/hyaku/souji-r32/SwarmSentinel30` removed after the closing re-sweep; nothing written to the lane outside this report.
