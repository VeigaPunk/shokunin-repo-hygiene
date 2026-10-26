# SwarmSentinel30 — credential and private-URL sentinel (round 31, wave 2)

Read-only seat. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`; swept `git diff --name-only`
base..tip at tip `2c16d018e40db7c23420a2c3bb546b52957bcc25` (142 files, all read at that rev) and the
wave-2 delivery dir `.ufo/waves/round-31/w2/`. Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmSentinel30`
removed after copying this report. No tool installed or upgraded this run (nothing needed).

## Status

STATUS: PARTIAL — 0 secret-material hits in the 142 landed files and in the wave-2 delivery tree
(30-pattern table, live control fires 30/30, plus base64/hex decode pass; 70-file tree re-scanned).
But the round landed instruments that hand the operator's full environment to code taken from the
revision under test — the C2 and C3 counters (v1-v3 each), the A1 regress checker, the C1
capability-cell counter and the landing gate — and a synthetic canary set in that environment reached
a committed-record channel end to end (F1/F2). Credential-safety of the round's evidence path cannot
be certified while that channel is open; no live credential value was exposed this round.

## Evidence

Base and tip, sweep set:

```
$ git -C <lane> rev-parse 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc 2c16d018e40db7c23420a2c3bb546b52957bcc25
9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
2c16d018e40db7c23420a2c3bb546b52957bcc25
$ git -C <lane> diff --name-status <base> <tip> | cut -f1 | sort | uniq -c
    133 A
      9 M
$ git -C <lane> diff --name-only <base> <tip> | wc -l
142
$ git -C <lane> archive <tip> $(cat changed.txt) | tar -x -C $D/landed ; find $D/landed -type f | wc -l
142
```

Sweep instrument `/fast/scratch/hyaku/souji-r31/w2-SwarmSentinel30/scan.py` (30 patterns; every counted
pattern is proven live first):

```
$ python3 -B scan.py --control
CONTROL files=1 binary=0
CONTROL patterns=30 silent=0
$ python3 -B scan.py $D/landed
SCAN dirs=1 files=142 binary_skipped=0
pem-private-key      files=0 hits=0      openssh-key          files=0 hits=0
github-token-ghX     files=0 hits=0      github-pat           files=0 hits=0
gitlab-pat           files=0 hits=0      openai-sk-           files=0 hits=0
stripe-key           files=0 hits=0      slack-xox            files=0 hits=0
aws-akid             files=0 hits=0      aws-secret-name      files=0 hits=0
google-aiza          files=0 hits=0      pypi-token           files=0 hits=0
npm-token            files=0 hits=0      onepassword-uri      files=0 hits=0
auth-header-value    files=2 hits=2      bearer-blob          files=0 hits=0
basic-blob           files=0 hits=0      url-userinfo         files=0 hits=0
jwt                  files=0 hits=0      slack-webhook        files=0 hits=0
telegram-token       files=0 hits=0      netrc-line           files=1 hits=1
signed-url           files=0 hits=0      private-host-url     files=0 hits=0
ip-url               files=0 hits=0      home-secret-path     files=0 hits=0
secret-assignment    files=0 hits=0      env-secret-assign    files=0 hits=0
ssh-publickey        files=0 hits=0      cert-block           files=0 hits=0
```

The three non-zero matches are pattern names in prose, read verbatim this run — no credential material:

- `SCORECARD.md:233` — `certified for deletion authorization: r9 red-team replays still reproduce`
- `census/round-31/waves/w1-results.json:226` — `\"Authorization: header\",` (prompt text echoed into results)
- `census/round-31/waves/w1/SwarmSentinel37.md:51` — `machine … login … password …` (wave-1 pattern table)

Private-URL surface (all changed files): 30 distinct URL hosts, every one a public documentation/blog
host (`git-scm.com` 108, `raw.githubusercontent.com` 81, `github.com` 35, `man7.org` 24, …); userinfo
URLs 0, non-80/443 ports 0, `.internal`/`.local`/`.lan`/IP-literal hosts 0, signed-URL params
(`access_token=`, `X-Amz-*`, `sig=`) 0, `file://`/`mailto:` 0, `ssh://`/`git@host:` 0. Address-shaped
strings are throwaway identities only: `souji@shokunin.local` (`SKILL.md:162`, documented commit
identity), `probe@localhost` (`census/round-31/records/a1-regex-receipt.txt:101`), `r31@fixture.invalid`
family in fixtures.

Encoded-secret pass over the same 142 files (decode then re-test): `STATS {'b64_tried': 1372,
'hex_tried': 1304, 'decoded_ok': 89}` → `HITS 0`. Binary/NUL files: 0 (four landed files are 0 bytes:
`records/empty-slice`, `records/empty-verdicts`, `waves/w1-run.err`, `waves/w2-run.err`).

History is permanent, so the round's 11 commits were swept as patches and messages:

```
$ git -C <lane> log -p <base>..<tip> > hist.patch ; wc -l < hist.patch
18322
gh[pousr]_ … 0   github_pat_ … 8 (prompt prose)   sk- … 0   xox[baprs]- … 1 (prose)
AKIA … 0   op:// … 0   url-userinfo … 0   Bearer blob … 0   git-credentials|.netrc|.ssh/|/.aws/ … 1 (prose)
$ deleted paths in <base>..<tip>: none
$ commit-message scan over %B: all nine token/URL/home-path patterns 0
```

Provenance of the C3 snapshots re-derived: `cd census/round-31/sources && sha256sum -c SHA256SUMS` →
`git-reflog.adoc: OK`, `gc.adoc: OK`, `git-compatibility.md: OK` (3/3, rc=0). Delivered bytes equal
landed bytes: 70/70 same names under `.ufo/waves/round-31/w1/` and `census/round-31/waves/w1/`
(`cmp -s`, 0 diffs), four source files hash-identical between `.ufo/.../w1/sources/` and
`census/round-31/sources/` — so wave-1's 66-file scan carries to the landed copies.

Final wave-2 set: `.ufo/waves/round-31/w2/` was 6 files at 04:31, 32 files / 332144 bytes at
`scan_time_utc=2026-10-26T07:36:03Z`, and 70 files (42 top level plus 28 in three delivery
subdirectories) at `final_scan_utc=2026-10-26T07:37:16Z`; every pattern `files=0 hits=0` in both
scans (69 swept — this report excluded by name, as in wave 1). The directory was still growing while
seats wrote; the reproduction below re-pins it, and new files after 07:37:16Z are not covered.

## Findings

1. **F1 (HIGH, landed instrument — alive credential channel).** Every round counter executes code from
   the revision under test with the operator's whole environment.
   `census/round-31/c3-counter-v3.py:133-134` runs
   `p = subprocess.run(["bash", fx], cwd=exp, capture_output=True, text=True, timeout=900,` with
   `env=dict(os.environ, TMPDIR=td)`; origin of `fx` is `fx = os.path.join(exp, FIXTURE)` where `exp` is
   the `git archive` of `--rev`. Same shape at `c3-counter.py:115`, `c2-counter-v3.py:78`
   (`env = dict(os.environ, TMPDIR=tmp)`), `c2-counter{,-v2}.py`, `a1-regress-full-check.py:53`,
   and `tools/souji-capability-cells.py:216` (`env = dict(os.environ, TMPDIR=tmp, GIT_CONFIG_NOSYSTEM="1")`).
   `tools/souji-landing-gate.py:197` likewise forwards all but six `GIT_*` selectors
   (`for k, v in os.environ.items()`).
   Exploit path, reproduced this run with a synthetic canary (no real secret used): a scratch clone of
   the lane, one commit (`1261b1bd25d4209a3ed2d98279ae57f914c8011f`) replacing
   `tools/souji-coverage-agreement.py` with `print("EXFIL-" + os.environ.get("DEMO_TOKEN","absent"))`,
   then
   `DEMO_TOKEN='CANARY-synthetic-not-a-secret-9f3a' python3 -B census/round-31/c3-counter.py --root $D/c --rev 1261b1b… --base 9f17a1e…`
   printed `L2 FAIL coverage="EXFIL-CANARY-synthetic-not-a-secret-9f3a"`. This seat's environment
   carries, by name only, `OPENAI_CODEX_TOKEN`, `OP_SERVICE_ACCOUNT_TOKEN`, `XAI_OAUTH_TOKEN`,
   `HL_INITIAL_WORKSPACE_TOKEN`, `SSH_AUTH_SOCK` (values never read); the counters run on
   seat-authored mutant commits by design (mutation-testing seats), so any such commit can print those
   values into a leg detail that the L1 then commits as a receipt (this round dispatches three
   `"role": "mutation-tester"` seats — `census/round-31/waves/w2-spec.json` — whose job is to author
   such commits). Impact: credential exfiltration into
   permanent lane history and falsification of the evidence the three claims rest on. Axis harmed:
   operability (instrument hygiene), and calibration/coverage evidence integrity.
   Smallest remediation: pass an allowlist env (`PATH`, `TMPDIR`, `HOME` inside scratch, `LC_ALL`) at
   those call sites and drop credential-bearing names from `GIT_ENV`.
2. **F2 (MEDIUM, raw-output channel).** The C3 counter echoes a child's whole stdout into its SUMMARY:
   `c3-counter-v3.py:114-116` captures `cov = subprocess.run([... "tools/souji-coverage-agreement.py" ...]).stdout.strip()`
   and prints `f'coverage="{cov}"'`; that line is the channel F1's canary used. The child at
   `:114` passes no `env=` at all, so it also inherits `GIT_DIR`/`GIT_WORK_TREE`-class variables the
   gate deliberately strips. Axis: operability (a receipt can carry foreign bytes). Remediation: print a
   length-capped, character-class-filtered summary, or compare only an extracted `key=value` allowlist.
3. **F3 (LOW, private home path in committed bytes).** Six landed files embed the absolute harness path
   `/home/vgpnk/.omp/agent/RULES.md`: `census/round-31/waves/make-spec-w1.py:40`,
   `make-spec-w2.py:40`, `w1-spec.json:5`, `w1-dispatch.json:265`, `w2-spec.json:5`, `w2-dispatch.json:253`.
   No secret, but it discloses the operator's home layout and harness location in permanent history.
   Axis: operability (hygiene). Remediation: cite `$HOME/.omp/agent/RULES.md` or "the agent RULES.md".
4. **INFO (mode inconsistency, not a leak).** `.ufo/waves/round-31/w2/swarm-registry.json` is mode 0600
   while every other delivery is 0644 (same as wave-1's observation); content keys are
   `createdAt, members, reportDir, schema, updatedAt, wave` with 36 member entries and no credential
   fields.

Non-findings stated so a later seat does not re-file them: `/fast/scratch/...` paths in committed
reports and records are contract-mandated (absolute paths only); the three pattern-name matches above
are not credentials; wave-1's F1 file was re-located at tip (`census/round-26/waves/w1/LabGitVersion.md`
still holds 9 `credential.` lines) but lies outside this round's `<base>..<tip>` diff and M1 does not
copy it, so nothing new propagates from it this round.

## Attack log

Tried against the 142 landed files and the wave-2 dir, all with the control firing on the same code:

- 30 credential pattern classes (keys, `ghp_`/`github_pat_`/`glpat-`, `sk-`/`sk_live_`, `xox`, `AKIA`,
  `AIza`, pypi/npm, `op://`, `Authorization:` value, Bearer/Basic blobs, URL userinfo, JWT, Slack
  webhook, Telegram token, netrc line, signed-URL params, `.internal`/`.local`/IP hosts, home secret
  paths, secret assignments, `*_TOKEN=` lines, SSH public keys, PEM certs) → 0 real hits.
- base64 and hex decode of every ≥40-char candidate (1372 + 1304 candidates) then re-test → 0.
- NUL/binary files and 0-byte files → none hidden; 142 files read, none skipped for encoding.
- URL host census with ports and query params → 30 public hosts, no userinfo, no signatures.
- Round history (`log -p`, 18322 lines) and all commit messages → no token shapes, no deletions that
  could have hidden a later-removed secret.
- Delivered-vs-landed byte equality (70/70 reports, 4/4 sources) to close the wave-1 snapshot gap.
- `sha256sum -c` on the C3 snapshots → 3/3 OK.
- Environment-name inspection only (no values) to size F1's blast radius.
- F1/F2 reproduced end to end with a synthetic canary in a throwaway clone; `origin` removed, identity
  set with `git -C`, no writes or signals in the lane.

## Deliveries

- `.ufo/waves/round-31/w2/SwarmSentinel30.md` (this report). No other lane file written; scratch
  directory removed.

Reproduction:

```
D=/fast/scratch/hyaku/souji-r31/w2-SwarmSentinel30; mkdir -p $D/tmp; export TMPDIR=$D/tmp
L=/home/vgpnk/Projects/shokunin/souji-shokunin
git -C $L diff --name-only 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc 2c16d018e40db7c23420a2c3bb546b52957bcc25 > $D/changed.txt
mkdir -p $D/landed && git -C $L archive 2c16d018e40db7c23420a2c3bb546b52957bcc25 $(cat $D/changed.txt | tr '\n' ' ') | tar -x -C $D/landed
python3 -B $D/scan.py --control && python3 -B $D/scan.py $D/landed $L/.ufo/waves/round-31/w2
```
