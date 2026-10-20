# TranscriptBundle — r16 w1/w2 transcript bundle + manifest tool

STATUS: DONE — 144 transcripts placed in the worktree byte-exact (no git commit; seats cannot commit), sha256 manifest generated and re-verified; tool exit codes exercised on all specified paths.

## Files written (OWN ONLY)

- `census/round-16/transcripts/w1/` — 65 files, `cp -p` from `/var/tmp/souji-r16/transcripts/w1/`
- `census/round-16/transcripts/w2/` — 79 files, `cp -p` from `/var/tmp/souji-r16/transcripts/w2/`
- `census/round-16/transcripts/MANIFEST.sha256` — 144 lines, `sha256  relpath` (two-space sha256sum text format), sorted LC_ALL=C by relpath
- `census/round-17/transcript-manifest.py` — `--write <dir>` / `--check <dir>`; exit 0 ok, 1 mismatch/missing/extra, 2 usage (also missing manifest, unparseable line, non-directory)

## Counts and digests (measured)

| Metric | Value |
|---|---|
| w1 files | 65 |
| w2 files | 79 |
| total files | 144 |
| total bytes (`du -sb`) | 1,992,055 |
| MANIFEST.sha256 sha256 | `4837d55097206079b273aaf4023aaa67bf0a9feff022ca308b3d8cc5f5b6edac` |
| `--check` exit | 0 (`check OK: 144 files verified`) |

Assignment claimed w1=70, w2=77 (147). Measured on disk at `/var/tmp/souji-r16/transcripts` is 65+79=144 — disclosed discrepancy; all 144 source files were copied. SentinelTranscripts independently measured the same 65/79 counts and the same manifest digest — cross-verified.

## Byte-exactness

Every source file verified with `cmp -s` post-copy: `cmp-verified: 144 files, failures: 0`. `cp -p` preserved modes/timestamps. No bytes altered, no redaction.

## Credential scan (pre-copy gate)

Searched `/var/tmp/souji-r16/transcripts` case-sensitively and case-insensitively for `token=`, `ghp_`, `sk-`, `Bearer`, `BEGIN PRIVATE KEY` — **zero hits** in all 144 files. Scan output suppressed values by construction; nothing to report as `path:line`. Copy proceeded.

## transcript-manifest.py behavior (all paths exercised in /var/tmp/souji-r17-TranscriptBundle, since deleted)

- `--write` → 0, writes `MANIFEST.sha256` atomically (tmp + `os.replace`), excludes itself from enumeration
- `--check` clean → 0 (`check OK: N files verified`)
- `--check` corrupted byte → 1 (`mismatch:`)
- `--check` listed-but-absent file → 1 (`missing:`)
- `--check` unlisted on-disk file → 1 (`extra:`)
- `--check` without manifest → 2 (`error: no manifest …`)
- no args / non-directory → 2 (argparse usage / explicit error)
- Re-`--write` inside a dir containing `MANIFEST.sha256` does not flag it as extra on `--check` → 0

Manifest parser rejects: short lines, wrong separator (must be `<64-hex><space><space>`), non-hex digests, absolute or `..`-traversal relpaths → all unparseable → exit 2.

## Calibration note (C2 axis)

These are the exact bytes `tools/souji-seat-audit.py` will be run against for the D4 false-positive fix. Digest pinned above; `census/round-17/transcript-manifest.py --check census/round-16/transcripts` re-verifies the placed set at any later point without trusting mtime.

## Tools installed

None. All work used system `cp`/`cmp`/`sha256sum`/`find` and `python3` — no installs needed, pacman untouched.

## Risks / blockers

- None. The 65/79 vs claimed 70/77 count gap is disclosed; if the expected 3 missing files exist elsewhere they were not under `/var/tmp/souji-r16/transcripts` at scan time.
