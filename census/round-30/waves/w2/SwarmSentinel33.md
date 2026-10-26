# SwarmSentinel33 — credential / private-URL sweep (r30 w2, attack on w1 + the landed set)

## Status

STATUS: PASS — the attack ran to completion: all 196 paths changed between base `9420341d…` and lane tip `9dcd3676…` (including the four `census/round-30/sources/*` snapshots and the whole `census/round-30/waves/**` capture) swept with 20 credential/private-URL classes plus an independent shell cross-check, twice by two engines: **0 credential, 0 private-URL, 0 userinfo-URL, 0 secret-path, 0 token-query hits**. Two non-leak defects in instruments landed after wave-1 (record→URL→committed-stdout channel; full caller env to row argv). Wave-1's headline conclusion HOLDS at full scope; one of its r29 counts is unreproducible.

## Evidence

Scope: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --name-only 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b 9dcd367655fc28ba73d679a0e2cadaff96d2bcb8` → **196** paths, list sha256 `b366db81…a7a7`, all present at tip (missing=0), modes 180 × 100644 + 16 × 100755, no symlink, no binary. Split: `census/round-30/waves/**` 151 (w1 142 + top-level 9), `census/round-30/sources/**` 5, rest 40 (22 records, 7 census/round-30 root, 4 corpus, 3 docs, 2 tools, 2 tests). Sweep ran on a `git clone --no-local` copy checked out at tip, origin removed.

Per-class counts over the three surfaces (python3 -B sweep, 20 classes; shell `grep -rEc` cross-check on 15 assigned classes agreed exactly): every credential class 0; only `.env`-filename references 2 (`SKILL.md:68`, `census/round-30/waves/w1-results.json:202`, both prose). Broader classes also 0: `glpat-`, `npm_`, `hf_`, `sk-ant-`, `sk-or-v1-`, `SG.`, `ssh-ed25519`/`ssh-rsa` key blobs, `BEGIN CERTIFICATE`, `KUBECONFIG`, `GOOGLE_APPLICATION_CREDENTIALS`, `AWS_PROFILE`, `VAULT_TOKEN`, `1password`, `.pem`/`.p12`, `id_rsa`, `id_ed25519`, AWS-secret/`password`/`api_key`/`secret` assignments.

High-entropy pass (runs ≥40 chars): 549 git-sha1, 258 sha256, 25 hex-hyphen, 1,349 mixed path/hash fragments; **0 secret-shaped**.

Private-URL pass: 470 URL-shaped tokens over 41 distinct real hosts — every host public (docs.jj-vcs.dev 171, raw.githubusercontent.com 82, git-scm.com 61, github.com 37, man7.org 27, … ); no loopback, no RFC1918 literal, no `file:`/`s3:`/`ftp:`, no `X-Amz-*` presigned query, no `.onion`, no port-bearing host, **0 userinfo URLs**. `https:` 462, `agent://` 5 and `xd://` 3 (harness URIs in seat prompts/prose, not addresses; 6 of the 47 raw host keys are regex artefacts of `agent://all` / `xd://report_issue`). Email-shaped tokens: only reserved/synthetic domains — `example.com`, `bar.com`, `fixture.invalid`, `example.invalid`, `scratch.invalid` — plus the documented lane commit identity `souji@shokunin.local` (`SKILL.md:161`); no real address.

Provenance of the newly landed snapshots HOLDS: `sha256sum -c census/round-30/sources/SHA256SUMS` → 4/4 OK; each `fetch-receipts.tsv` digest equals the landed file's sha256 (4/4 MATCH); each landed snapshot is byte-identical (`cmp`) to its `waves/w1/sources/` copy; `sha256sum -c census/round-30/waves/manifest.sha256` → **150/150 OK**, manifest set == tree set exactly; live `.ufo/waves/round-30/w1/` == committed capture, 142/142 files identical. So the gate reads the bytes the seats wrote and the L1 committed.

Deleted side of the diff: 8 removed lines, none credential-shaped (the C1 SCORECARD rewording and the gate's old `prefix`/`.md` rule).

Live wave-2 dir at `2026-10-26T05:27:51Z`: 94 files, 0 hits (point-in-time; later arrivals are outside this measurement).

Pending bytes (not landed, swept as a courtesy): uncommitted `SKILL.md` + `corpus/QUALITY.md` diffs and untracked `corpus/lessons/round-30.md` — 0 hits in 10 classes.

## Findings

1. **LOW — record-supplied URL is fetched by `curl` without a protocol fence and, on failure, is printed into a committed after-record.** Location: `census/round-30/c3-counter-v2.py:90` — `q = subprocess.run(["curl", "-fsSL", "-m", "60", url], capture_output=True)`. `url` comes from `census/round-30/records/fetch-receipts.tsv` (a record, not code). Exploit path: a record row edited to `https://user:pass@host/x` or `…?access_token=…` → fetch fails or redirects → line `…COULD-NOT-EVALUATE fetch {url}` prints the whole URL, and `census/round-30/records/c3-after-v2.txt` is a committed artifact; additionally `-L` has no `--proto`/`--max-redirs` limit (a `file://` URL would read a local file, hash it, and its existence would show up in `bad=`). No credential today: the four recorded URLs are bare `raw.githubusercontent.com` paths and the after-record carries only `E1…E4` lines. Impact: the round's only network call has an unfenced record→argv→stdout→commit path for credential-shaped bytes. Smallest remediation: argv `["curl", "-q", "-fsSL", "--proto", "=https", "--max-redirs", "0", "-m", "60", "--", url]` and print the receipt filename, never the URL, on failure.

2. **LOW — lane-authored row argv runs with the caller's whole environment, and the committed `observed=` tail is unfiltered.** Location: `tools/souji-capability-agreement.py:160` — `env = dict(os.environ, TMPDIR=tmp, GIT_CONFIG_NOSYSTEM="1")`; those bytes are then committed at `:209` — `…\tobserved={s}\t{verdict}`. `GIT_CONFIG_NOSYSTEM` is set but `HOME` is not redirected, so `~/.gitconfig` (and any credential helper it names) is still in reach of every row command, and a row whose output ends in a digit-bearing line carrying an env-derived value lands verbatim in `census/round-30/records/c1-after-{v1,a3}.txt`. Exploit path: one row edited (the rows file is lane-authored) to print `$SOME_TOKEN` next to a counter → the token is committed as an observation. No hit today: the 18 rows print counts (`observed=SUMMARY total=5 failed=0 …`) and A3 rejects usage/help banners. Impact: the C1 after-records are a leak-free but unfiltered echo channel. Smallest remediation: pass a minimal env (`PATH`, `TMPDIR`, `HOME=<sandbox>`, `GIT_CONFIG_NOSYSTEM=1`) and refuse an `observed` value matching the lane's shared secret patterns.

3. **LOW — wave-1's r29 `op:` count cannot be produced by the command printed beside it.** Location: `census/round-30/waves/w1/SwarmSentinel33.md:32` states `1` for that class, while `:46` prints the class as `'op:/[A-Za-z0-9]'`. Measured at tip: strict regex **0**; loose `op:` **3**, none a credential — `census/round-29/waves/w1/SwarmSentinel61.md:40` and `:66` (`op://` inside a prose pattern table) and `deliver-sources-rows.md:88` (`… Stop: the four locators were opened …`, the `op:` inside "Stop:"). Impact: a table cell (harmless here) breaks the round's own rule that a count carries its command; a reader cannot reproduce `1` by any of the three readings. Smallest remediation: record the `op:` cell as 0 strict / 3 loose with the three locations.

4. **INFO — wave-1's PASS covered 83 of the 142 w1 files now committed and none of the other 54 changed paths.** Its declared surfaces were the live `.ufo/waves/round-30/w1/` (83 files at HEAD `df6afe8`), its 6 snapshots and the 123 r29 files; the C1/C2/C3 records, `census/round-30/sources/`, the 9 top-level wave records, `corpus/`, `tools/`, `tests/` and the three docs were outside all three. `git diff --name-only df6afe8 9dcd3676…` = 182 paths landed after that HEAD. Its disclaimer ("files written after that timestamp are outside this report's measurement") is accurate, so this is a coverage statement, not a false claim: my full-set sweep returns the same 0, and the conclusion HOLDS at full scope.

5. **INFO — the same upstream bytes ship twice in the round.** `census/round-30/sources/{cli-reference@.md.snap,git_backend.rs,git-gc.adoc,operation-log.md}` (266,707 bytes) are byte-identical (`cmp`) to `census/round-30/waves/w1/sources/` copies. Not a leak and both copies verify against their own `SHA256SUMS`; recorded because the lane is the hygiene lane and one copy plus a receipt pointer would carry the same provenance.

6. **INFO — `souji@shokunin.local` is a private-TLD identity that the C3 reserved-TLD guard does not cover.** `SKILL.md:161` documents it as the lane commit identity (`souji-shokunin <souji@shokunin.local>`); `census/round-30/c3-counter-v2.py` L7's reserved list is `.test .example .invalid .localhost`, so a future row citing an mDNS-private `.local` host would pass. No credential and no URL today.

## Attack log

| attacked | method | verdict |
| --- | --- | --- |
| all 196 changed paths, 20 credential classes | python sweep on a tip checkout + shell `grep -rEc` cross-check per surface group | **HOLDS** (0 everywhere; 2 `.env` prose) |
| private-URL class: hosts, schemes, userinfo, query params, presigned | URL/host enumeration over the changed bytes; literal greps for loopback/RFC1918/`.internal`/`.onion`/`file:`/`s3:`/`ftp:` | **HOLDS** (47 public hosts, 0 userinfo, 0 token params) |
| secret stores and key material | `.ssh`/`.aws`/`.gnupg`/`netrc`/`git-credentials`/`.npmrc`/`.pypirc` paths; `id_rsa`/`id_ed25519`/`.pem`/`.p12`; key armor; JWT; `AKIA`/`ghp_`/`github_pat_`/`sk-`/`xox`/`gh[osur]_`/`AIza` | **HOLDS** (0; the only raw class-name matches are the sentinel's own pattern table and its spec prompts) |
| high-entropy runs | classify every ≥40-char run | **HOLDS** (0 secret-shaped) |
| snapshot provenance (fabricated-readiness check) | `sha256sum -c` on both `SHA256SUMS` sets and the 150-entry wave manifest; receipt digest vs landed bytes; `cmp` across duplicates; live-vs-committed w1 equality | **HOLDS** (4/4, 4/4, 150/150, 142/142) |
| wave-1 conclusion at full scope | re-swept the 142 committed w1 files with wave-1's 15 classes | **HOLDS** (0 in w1; r29 2 `.env` prose only) |
| wave-1 r29 `op:` count | strict regex, loose regex, word-boundary regex on the same surface | **BROKEN** (1 claimed; 0 strict / 3 loose, all non-credential — finding 3) |
| wave-1 finding 1 (non-seat `.md` classified as reports) | measured the two files at tip | **HOLDS** (`w1/sources/cli-reference.md`, `w1/sources/operation-log.md`: `STATUS:` 0, `Report:` 0, round pointers 0; 49 `.md` under the capture) |
| wave-1 finding 4 (fleet script executed read-only) | inspected the landed argv and the fleet guard | **HOLDS** (`c3-counter.py:79` passes `validate --file <scratch>` only; no `--out`, so `emit`/`out_sink` write nothing) |
| newly landed instrument command construction / env | reviewed every `subprocess`/`os.environ`/`rm -rf`/`mktemp` in the 10 changed code files | **DEFECT-NOT-FATAL** ×2 (findings 1, 2); no `shell=True`; every `rm -rf` target is a `mktemp -d` under `$TMPDIR`; no home-store traversal |
| deleted lines of the diff | 8 removed lines re-scanned | **HOLDS** (clean) |
| live w2 arrivals | same 20 classes over `.ufo/waves/round-30/w2/` | **HOLDS** at `05:27:51Z`, 94 files, 0 hits (incomplete by construction) |
| pending uncommitted bytes | SKILL.md + QUALITY.md diffs, untracked round-30 lesson | **HOLDS** (0 in 10 classes) |

Method note for the next sentinel: `cli-reference@.md.snap` matches an email regex 84 times (upstream filename, not an address); exclude upstream filenames before counting addresses.

## Deliveries

- `.ufo/waves/round-30/w2/SwarmSentinel33.md` (this report)
- `.ufo/waves/round-30/w2/SwarmSentinel33-receipts.txt` (per-class counts, host/email lists, provenance and reproducibility checks, wave-1 and live-w2 numbers)

Scratch `/fast/scratch/hyaku/souji-r30/SwarmSentinel33/` removed on completion. No lane mutation, no `git`/`jj` write, no tool installed or upgraded, no `pacman` transaction.

Report: .ufo/waves/round-30/w2/SwarmSentinel33.md
