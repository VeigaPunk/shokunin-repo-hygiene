# SwarmSentinel43 — credential and private-URL sentinel, round 32 wave 1

## Status

STATUS: PASS

Assigned surfaces (246 files, 178,967 lines, manifest-hashed below) contain **0 real credential material and 0 private URLs**. The 17 credential-shaped matches all sit in one committed synthetic-canary regression fixture from round 21 (`census/round-21/reason-oracle-before.txt`, `census/round-21/cmd-compatibility.json`), are self-disclosing (`SOUJIR21FAKE` / `FAKE` markers, `souji-r21-canary-<hex>` path prefix), and their own after-record proves the redaction (`leak=0`, 19/19 canary cases). Zero hits for private-key armor, `op://`, `github_pat_`, `gh[ousr]_`, `ASIA`, `Basic`, and every home-directory secret path.

## Evidence

Contract read first: `census/round-32/records/preregistration.txt` (frozen, 32 lines), base `85b61a151923986e7e6b48f7084b9122561b5f3d`, lane `HEAD = 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1` at scan time (`git -C . rev-parse HEAD`). Only untracked lane file: `census/round-32/measure.sh` (not mine, untouched).

Surfaces scanned (read-only): every file under `.ufo/waves/round-32/w1/` as it appeared (75 files at the final snapshot: deliveries, seat reports, `swarm-registry.json`), `.ufo/waves/round-32/w1/sources/` (4 adoc snapshots + `SHA256SUMS`), and the record trees the C1 bindings name — `census/round-1/`, `census/round-13/`, `census/round-21/`. No C1 binding row had landed yet (`rg -c '^\| N[0-9]{2} \|' SCORECARD.md` → 0), so the binding targets were scanned by round; the additional rounds referenced in `census/round-32/c1-items.tsv` (`round-12`, `round-16`, `round-20`, `round-30`, `round-31`) were also swept: 0 real hits in each.

Command (authoritative, independent engine):

```
python3 -B  # walk the 5 surfaces, re.finditer per class, per-surface sha256 manifest
```

Per-surface snapshot:

```
SNAPSHOT total_files=246 total_lines=178967
  surface w1        files=75   lines=25865   manifest=aef22b0a10a8c9fb
  surface sources   files=5    lines=1443    manifest=be6f27cdcda6700c
  surface round-1   files=66   lines=5809    manifest=8c74cd4a1c1608b8
  surface round-13  files=20   lines=3528    manifest=0d503e8a0856a0ba
  surface round-21  files=80   lines=142322  manifest=7a9f43f7bc986a96
```

Per-pattern counts (`matches` / `files`), cross-checked with `rg -uu -o --no-filename --regexp=…` — the two engines agreed on every class:

```
private-key-header   0 / 0      op-ref                 0 / 0
token:ghp_           2 / 1      auth:Authorization     3 / 2
token:github_pat_    0 / 0      auth:Bearer            2 / 1
token:gh[ousr]_      0 / 0      auth:Basic             0 / 0
token:sk- (>=20)     0 / 0      url:userinfo           3 / 2
token:sk- (>=8)      2 / 1      path:ssh-keys          6 / 2
token:xox            2 / 1      path:home-secret       0 / 0
token:AKIA           3 / 2      path:docker-kube       2 / 2
token:ASIA           0 / 0      path:git-creds        12 / 2
                                path:pypi-npmrc       12 / 2
                                path:gh-hosts          0 / 0
```

Re-measured at the final 75-file w1 snapshot with `--glob '!SwarmSentinel43.md'` (this report excluded): byte-identical counts, every class unchanged.

Final re-scan (after the wave's last deliveries, 75 w1 files, HEAD unchanged at 7a6667c): `sources/`, `round-1/`, `round-13/` all 0; `round-21/` unchanged at its 2 canary files.

Self-scan, disclosed: this report matches 12 of its own classes because it names the patterns, prints one example URL pair and quotes `.ssh/id_`; measured with

```
rg -uu -o --no-filename --regexp="$ALL" .ufo/waves/round-32/w1/SwarmSentinel43.md | wc -l   # 12
rg -uu -o --no-filename --glob '!SwarmSentinel43.md' --regexp="$ALL" .ufo/waves/round-32/w1 | wc -l   # 32
```

The 32 w1 matches outside this report are the deny-list names in the two tools of Finding 4 (`path:ssh-keys` 6, `path:docker-kube` 2, `path:git-creds` 12, `path:pypi-npmrc` 12); no value-bearing class fires in any w1 file. No credential value is reproduced verbatim in this report: the canary tails are cut with `…` before they reach a class's minimum length.

Delta at yield: the w1 tree had grown to 78 files after the snapshot; a value-class-only re-sweep of it (`rg -uu -l --regexp='ghp_[A-Za-z0-9]{16,}|(?:^|[^A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----|[Bb]earer[ \t]+[A-Za-z0-9._~+/=-]{20,}'`) returned 0 match files outside this report.

Zero-hit loops run (each with its exact `rg` command, output `0`):

```
rg -uu -o --no-filename --regexp='-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' $S
rg -uu -o --no-filename --regexp='github_pat_[A-Za-z0-9_]{16,}' $S
rg -uu -o --no-filename --regexp='gh[ousr]_[A-Za-z0-9]{20,}' $S
rg -uu -o --no-filename --regexp='ASIA[0-9A-Z]{16}' $S
rg -uu -o --no-filename --regexp='op://' $S
rg -uu -o --no-filename --regexp='[Bb]asic[[:space:]]+[A-Za-z0-9+/=]{8,}' $S
rg -uu -o --no-filename --regexp='(~/|/home/[^/[:space:]]+/|\$HOME/)\.(ssh|aws|gnupg|netrc|git-credentials|docker|kube|password-store|npmrc|pypirc|local/share/keyrings)' $S
rg -uu -o --no-filename --regexp='\.config/gh/hosts' $S
```

where `S=".ufo/waves/round-32/w1 .ufo/waves/round-32/w1/sources census/round-1 census/round-13 census/round-21"`. Supplementary classes also 0: `eyJ…` JWT, `AIza…`, Slack webhook path, `pypi-AgEIcHlwaS5vcmc`, `_authToken=`, `AccountKey=`, `-----BEGIN PGP`, `glpat-`, `(sk|rk)_live_`, `ssh://…@`. All 18 classes pass a positive control (one synthetic value per class, 18/18 fire), so the zeros are measured, not assumed.

Lane-hygiene note (not credential material, not mine): `census/round-32/__pycache__/c1-counter-v2.cpython-314.pyc` (31585 B, 05:31) exists in the lane — some seat ran a counter without `-B`. Gitignored (`.gitignore:3`), so the tree is clean, but the contract asks for `python3 -B`; I created no bytecode (every run here was `python3 -B`, scripts lived in scratch).

Snapshot integrity: `sha256sum -c SHA256SUMS` → `gitformat-pack.adoc: OK`, `git-gc.adoc: OK`, `gc.adoc: OK`, `git-repack.adoc: OK`.

## Findings

1. **INFO — every credential-shaped string is the round-21 synthetic canary fixture, not a secret.** Locations and masked values:
   - `census/round-21/reason-oracle-before.txt:2,18` — `ghp_SOUJIR21FAKE1****`; `:4,20` — `sk-…FAKE2…`; `:6,22` — `AKIA****ABCDEF`; `:8,24` — `xoxb-…FAKE3…`; `:16,32` — `Authorization: Bearer …FAKE7…`; `:12,28` — `https://u:SOUJIR21FAKE5****@host/x`.
   - `census/round-21/cmd-compatibility.json:3,21,27` — `Authorization: Bearer FAKE001`, `https://u:FAKE006@h/x`, `AKIA****ABCDEF xoxb-FAKE007`.
   Provenance: commit `4d5bf78` "round-21: redact and bound reason fields with synthetic canaries"; both files are tracked (`git ls-files --error-unmatch`). Inventory of canary values: 7 distinct `SOUJIR21FAKE<nnnnn>` tokens, 2 occurrences each, plus the 3 `…FAKE00n` entries in the compatibility matrix.

2. **LOW — two committed canaries are shape-identical to live token formats, so a CI secret scanner will flag them.** `AKIA`-shaped (`AKIA` + 16 uppercase) (`reason-oracle-before.txt:6,22`, `cmd-compatibility.json:27`) and `ghp_` + 16 alnum (`reason-oracle-before.txt:2,18`) match gitleaks/trufflehog/GitHub secret-scanning rules verbatim. Impact is false-positive triage cost on a permanently tracked file, not exposure — the values are fake by construction. Smallest remediation: add a scanner allowlist entry citing those three `file:line` pairs (`gitleaks:allow` comment on the JSON key, or a `.gitleaksignore` fingerprint), or reshape the canaries (`ghp_` → `ghpX_`, `AKIA` + 16 → `AKIA` + 8) with a matching update to the round-21 oracle expectations. No change made — outside my write scope.

3. **INFO — `reason-oracle-before.txt` is a red-before record, and the fix is proven in the same tree.** Its 21 failing cases (of 27) print `leak=1` because the reason field echoed the canary bytes into committed output; `census/round-21/reason-after.txt:2-20` shows `leak=0 base_leak=1` for all 19 canary cases. This is the pre-fix state preserved on purpose, not a live leak. No action.

4. **INFO — the two w1 files with secret-path hits are deny-lists, not collectors, and their `.ssh` writes stay inside a tempdir.** `deliver-souji-evidence-cache.py:125-138,292-310` and `deliver-souji-preservation-evidence.py:163-172,383-400` name `~/.ssh`, `~/.aws`, `.password-store`, `.npmrc`, `.kube/config` only as refused trees. The `.ssh/id_ed25519` writes at `deliver-souji-evidence-cache.py:1306,1492`, `deliver-souji-preservation-evidence.py:1971,2250` are inside `base = Path(tempfile.mkdtemp(...))` with `HOME` repointed to `base/"home"`, content `synthetic home, never read` (`:1306`). The real `$HOME` is never the target. No credential read or write path found.

5. **INFO — instrument defect hit during this scan (harness, not the lane): this host's shell `grep` and a shell-builtin `rg` wrapper silently reject `-e <pattern>`.** `grep -rEoI -e '-----BEGIN …' <dir>` exits 0 with `error: unexpected argument …` on stderr and prints nothing, so a per-surface table reads all-zero. Reproduced with that exact command. Remediation already applied in this report: `--regexp=` (or `-f <file>`), plus the 18-class positive control that would have caught it. Worth carrying into later sentinels — a zero-hit sweep via `-e` is not evidence.

6. **INFO — one delivered tool hard-codes the operator's home path.** `deliver-r31-landing-gate-precision.py:77-78` sets `LANE_ROOT`/`FLEET_ROOT` to literal `/home/vgpnk/Projects/shokunin/...`. Not a secret and not a private URL, it is the only `/home/vgpnk` literal in executable w1 code (45 such literals appear across 21 w1 files, the other 20 being markdown that names lane paths), and it blocks running the tool from another account. No action under my scope.

7. **INFO — no private URLs anywhere in scope.** Distinct URL hosts extracted from w1 are public or reserved: `raw.githubusercontent.com` (4), `example.invalid` (2, RFC 2606), plus scheme strings that are not URLs (`file://%s`, `xd://…`, `agent://…`, `local://…`, `history://…`, `ssh://fixture-host` with no userinfo). `sources/` yields zero absolute URLs. No URL carries userinfo except the round-21 canary, and no internal hostname, RFC1918 address, or `.local` host appears.

## Attack log

Not an attack seat (sentinel). One probe was run and is reported as Finding 5: an adversarial check of my own sweep's false-negative rate, which found the `-e` rejection. No attacks filed against C1/C2/C3.

## Deliveries

- `.ufo/waves/round-32/w1/SwarmSentinel43.md` (this report)

Scratch `/fast/scratch/hyaku/souji-r32/SwarmSentinel43` removed after the final re-scan; nothing written to the lane outside this report.
