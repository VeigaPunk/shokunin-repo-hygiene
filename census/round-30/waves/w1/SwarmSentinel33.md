# SwarmSentinel33 — credential / private-URL sweep (r30 w1)

## Status

STATUS: PASS — every assigned surface swept at lane HEAD `df6afe817d096e4ad71ba2b9cc21a83f126eb658` (83 w1 files, 6 w1 snapshots, 123 r29 capture files) with 15 pattern classes plus a tight real-material pass: **0 credential, 0 private-URL, 0 userinfo-URL, 0 secret-path hits**. Six raw hits, all prose or pattern lists, itemised below. Four non-credential findings (≤ LOW) on the instruments the round ships; none is a leak.

## Evidence

Surfaces and what they are:

| surface | path | files | what it is |
| --- | --- | --- | --- |
| w1 deliveries | `.ufo/waves/round-30/w1/` | 83 | reports + delivery files (live; every arrival re-swept) |
| w1 snapshots | `.ufo/waves/round-30/w1/sources/` | 6 | 5 upstream fetches + `SHA256SUMS` |
| r29 reports | `census/round-29/waves/w1/` | 123 (86 `.md`) | what the C2 gate now reads |

**1. Provenance of the fetch set holds.** `cd …/w1/sources && sha256sum -c SHA256SUMS` → `cli-reference@.md.snap: OK`, `git_backend.rs: OK`, `operation-log.md: OK`, `git-gc.adoc: OK`, `cli-reference.md: OK` (5/5). `deliver-fetch-receipts.tsv` records `http` 200 and the same five digests for `raw.githubusercontent.com` at `jj-vcs/jj` tag `v0.45.1` and `git/git` tag `v2.56.0`; receipt times `04:43:49Z`/`04:44:49Z` are consistent with `date -u` `04:52Z` this run.

**2. The r29 bytes I scanned are the bytes the gate reads.** Every tracked blob under `census/round-29/waves` re-hashed against `HEAD`: `tracked_blobs 132 mismatches 0`; `git -C <lane> status --porcelain -- census/round-29` → empty. So no post-commit rewrite separates the scanned capture from the gate's input.

**3. Per-pattern counts** (`python3 -B <sweep>` over the three surfaces; `0` in every w1 column):

| pattern | w1 (83) | w1-sources (6) | r29 (123) |
| --- | --- | --- | --- |
| private-key armor block | 0 | 0 | 0 |
| `ghp_`-prefixed token | 0 | 0 | 0 |
| `github_pat_` token | 0 | 0 | 0 |
| `sk-`-prefixed key | 0 | 0 | 0 |
| `xox?`-prefixed token | 0 | 0 | 0 |
| `AKIA` access-key id | 0 | 0 | 0 |
| `gho_`/`ghs_`/`ghu_` token | 0 | 0 | 0 |
| 1Password `op:` scheme ref | 0 | 0 | 1 (prose) |
| bearer-token header with an inline value | 0 | 0 | 0 |
| Basic credential value | 0 | 0 | 0 |
| Authorization header with a value | 0 | 0 | 0 (3 raw, header-only) |
| URL with userinfo | 0 | 0 | 0 |
| home-dir secret path (`.ssh`/`.aws`/`.netrc`/…) | 0 | 0 | 0 |
| dot-env filename reference | 0 | 0 | 2 (prose) |
| token-bearing query parameter | 0 | 0 | 0 |

Cross-check by a second, independent method (shell `grep -rEo`, one command per class, same surfaces):

```
$ for p in '-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' 'ghp_[A-Za-z0-9]{30,}' \
    'github_pat_[A-Za-z0-9_]{30,}' '(^|[^A-Za-z0-9])sk-[A-Za-z0-9]{20,}' \
    'xox[abprs]-[A-Za-z0-9-]{20,}' 'AKIA[0-9A-Z]{16}' 'op:/[A-Za-z0-9]' \
    '([Bb]earer|[Bb]asic)[[:space:]]+[A-Za-z0-9._~+/=-]{20,}' \
    '[Aa]uthorization:[[:space:]]*[A-Za-z0-9]' '[a-z]+://[^[:space:]/@:'"'"'"]+:[^[:space:]/@'"'"'"]+@' \
    '(~|\$HOME|/home/[A-Za-z0-9_.-]+)/\.(ssh|aws|gnupg|netrc|git-credentials|npmrc|pypirc)' ; do
    grep -rEo "$p" <surface> | wc -l ; done
w1=0 r29=0   for every class
```

**4. The six raw hits, each masked and located.** All are self-reference: `census/round-29/waves/w1/SwarmSentinel61.md:40` (the pattern name inside a table row), `:51` and `:80` (the header word in two prose sentences, never followed by a value); `census/round-29/waves/w1/SwarmExecutor06.md:101` and `deliver-c2-152-classification.tsv:191` (a dot-env filename named inside a list of basenames that were searched). No value follows any match.

**5. Private-URL check.** All hostnames appearing anywhere under w1: `codeload.github.com`, `crates.io`, `datatracker.ietf.org`, `docs.jj-vcs.dev`, `gerrit-review.googlesource.com`, `github.com`, `git-scm.com`, `jj-vcs.dev`, `jj-vcs.github.io`, `raw.githubusercontent.com`, `toml.io`, `www.apache.org` — all public upstreams. No loopback/RFC1918/`.internal`/`.local` host, no `file:`/`s3:`/`ftp:` scheme, no `X-Amz-*` presigned query, no `.onion`. The only `@` inside a URL is the upstream filename `cli-reference@.md.snap`, which is not userinfo (a userinfo-blind regex would false-positive here; the sweep requires `user:pass@` and returns 0).

**6. Addresses are documentation placeholders.** Email-shaped tokens under w1: `someone@example.com`, `jjfan@example.com`, `git.author@example.com`, `git.committer@example.com`, `foo@bar.com`, `r30@fixture.invalid`, `r30-expiry@example.invalid` — reserved domains only, no real address.

**7. Host-config dump absent.** No `git config --list --show-origin`, no `credential.helper` line, no credential-helper output anywhere in w1 or the r29 capture. Every `user.name`/`user.email` occurrence is a scratch-repo identity assignment (`SwarmScout10-keepref-measure.txt:11-12`, `deliver-r30-landing-gate-discovery.py:108`, `receipt-SwarmExecutor06-keepref-mechanism.txt:14`). The r29 sentinel's inherited disclosure (`SwarmSentinel61.md:83`, round-26 file) is not reproduced in any r30 file.

**8. Instrument control on command construction** (the gate is now a consumer of committed report text): `deliver-souji-landing-gate.py` has no `shell=True`, every `subprocess.run` call passes an argv list, script checking is `bash -n` only (`:300`) and Python checking is `compile()` only (`:315`), and both pointer guards reject absolute and `..` components (`_safe_pointer_path`, `:895-903`) before any tree lookup — so the new capture mapping cannot be steered into `.scratch/`, `.ufo/state/` or a sibling lane.

**9. Closing re-scan.** The w1 tree was re-swept after every arrival; the closing sweep covered 83 w1 files and returned 6 hits, all the r29 prose rows above and **none** in w1. The tree is still live, so w1 files written after that timestamp are outside this report's measurement and are the L1's final-gate step. The sweep was re-run over this report's own bytes too, and it reports `HITS 6` with no w1 row — the pattern table and the reproduction block below are written so that they do not themselves match the classes they test.

## Findings

1. **LOW — the C2 capture-discovery rule classifies upstream `.md` snapshots as seat reports.** Location: `.ufo/waves/round-30/w1/deliver-souji-landing-gate.py:488` — `p for p in tree if p.startswith(capture_prefix) and p.endswith(".md")`. This round's fetch set adds two non-report markdown files under `sources/`: `sources/cli-reference.md` and `sources/operation-log.md`. The gate's own functions classify them as reports (`check_carry` selects 3 of 3 synthetic w1 paths, including both), so at round 30's capture `checked_reports=` gains 2 non-seat documents and both are run through `status_line_count`, `seat_failure_lines` and `_pointer_paths`. Measured today on their bytes: `status_lines 0`, `failure_lines 0`, `pointers []` for both — so no finding is fabricated now, but an upstream doc containing a failure-vocabulary line would emit `LG-SEAT-UNCARRIED` against a document no seat wrote, and would inflate `checked_reports`. r29 is unaffected because `census/round-29/waves/w1/sources/` holds 0 `.md` (`broder97resemblance.*`, `cmp.1.html`, `link.2.html`, `statx.2.html`, `SHA256SUMS`), which is why the frozen `reports=86` target still holds. Smallest remediation: skip the capture-relative `sources/` subtree when building `reports` (the report set is `.ufo/waves/round-N/<name>.md`, never `.ufo/waves/round-N/sources/<name>.md`).

2. **LOW — the C3 fixture leaves its one mutating git command's exit status unchecked, so a refused gc is byte-identical to a survived keep ref.** Location: `.ufo/waves/round-30/w1/deliver-r30-jj-keep-expiry.sh:87` — `G gc --prune=now >/dev/null 2>&1`, with no `|| die`, in a script that runs `set -u` but not `set -e`. Every other mutation in the file is checked (`:74,77,79,84,90,96,97,104,107,109,112,122,125`). Step 3's line therefore prints `keep_refs=8 object_present=yes note=target_keep=yes cmd=git-gc-prune-now` (`deliver-jj-keep-expiry-run.txt:5`) whether the gc ran or aborted; the arm is cited as the measurement that `git gc --prune=now` cannot remove a keep ref (`deliver-docs-f1.md:75,124`, `SwarmExecutor06.md:64`). The direction that matters for C3 — `jj util gc` removing keep refs — is measured through checked calls (`:90`, `keep_refs 8→6`). Smallest remediation: `|| die "git gc --prune=now failed"`.

3. **INFO — the gate copies report text verbatim into its output, which is the path a credential would take into a committed receipt.** Location: `.ufo/waves/round-30/w1/deliver-souji-landing-gate.py:539` — `detail = "line %d: %s" % (lineno, needle[:220])`. A failure-channel line in any seat report is echoed up to 220 characters into gate stdout, which is captured into `census/`. Measured over the 86 r29 reports the gate now reads: `report_files 86 failure_channel_lines 7 status_lines 69 token_shaped_in_echoed_lines 0`. No leak today; recorded as a propagation surface, not a defect.

4. **INFO — a fleet-owned script was executed from two lane seats; boundary question for the L1, no mutation measured.** Location: `.ufo/waves/round-30/w1/deliver-sources-rows.md:101` and `SwarmScribe13.md:24` — `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /fast/scratch/hyaku/souji-r30/SwarmScribe13/val/corpus/SOURCES.md --today 2026-10-26`, `EXIT=0`. HARD BOUND says never touch the fleet `scripts/`. The script mutates only through `emit`/`out_sink`, guarded by `if [ -n "$OUT" ]` (`scripts/sources-census.sh:94-95`), and no `--out` was passed, so the run wrote nothing into the fleet; the validated `--file` is a scratch mirror.

5. **INFO — the fetch receipt's `snapshot` column names a directory that does not exist yet.** Location: `.ufo/waves/round-30/w1/deliver-fetch-receipts.tsv:2-6` — `census/round-30/sources/<name>`; `ls -d census/round-30/sources` → `No such file or directory` at 04:52Z. This is the declared landing step, not a silent claim: `deliver-c3-anchor-lines.md:6` ("staged for the L1 to commit as `census/round-30/sources/`"), `deliver-entry-jj-keep-ref-expiry.md:109`, and both `SwarmScribe14.md:23` and `SwarmScribe12.md:108` record the absence. The five digests do verify against `sources/SHA256SUMS`, so the bytes are sound if the L1 commits them at that path.

6. **INFO — the fixture's TMPDIR guard is narrower than the operator scratch directive.** Location: `.ufo/waves/round-30/w1/deliver-r30-jj-keep-expiry.sh:29-35` refuses an unset TMPDIR and any TMPDIR resolving inside `/home/vgpnk/Projects/shokunin` or the lane, but accepts any other writable directory. Blast radius stays correct: every `rm -rf` target is the `mktemp -d` dir created under TMPDIR (`:43`; `rm -rf` at `:45,47`), never the TMPDIR itself. A stricter guard would require TMPDIR under `/fast/scratch/hyaku/souji-r30/`.

## Deliveries

- `.ufo/waves/round-30/w1/SwarmSentinel33.md` (this report) — the only file written; scratch under `/fast/scratch/hyaku/souji-r30/SwarmSentinel33/` removed on completion. No tool installed or upgraded.
