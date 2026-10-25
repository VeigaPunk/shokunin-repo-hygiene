STATUS: PASS

# ResScopeNoHarm — no-harm audit of the landed round-22 attempt-2 bytes

Seat: `L1Souji22.ResScopeNoHarm` (leaf; no subagent dispatch). Read-only except this report and
`residual/evidence/r22a2-*`. No tool installs were run or needed; no package-manager transaction.

Moving-target note: the lane tip advanced from `ee1aef2` to `c9f1fe3` while this audit ran
(`4a6ee90` "escaped-pipe cell split in the declared-evidence scanner" and `c9f1fe3` "wave report
evidence (52 of 53 seats)" landed between my first and last measurement). All items below were
re-derived at final lane tip `c9f1fe3caf642dfe3a9e00de94caf1d4bf86503f` (`jj-lane.sh state .`
→ `local=c9f1fe3… remote=c9f1fe3… ahead=0 behind=0`; executed 2026-10-25). Round span audited:
`4edb25d..c9f1fe3` = 11 commits (evidence: `r22a2-commits.txt`).

Round-1 cross-reference: w1 seats `RevScope` and `Sentinel` already emitted findings against
earlier tips. Each is checked against the landed bytes below and marked fixed / still open /
out-of-scope rather than restated as new.

---

## Item 1 — no new deletion/move authority — finding:low (still open, not new)

Executed:

```
$ git log --diff-filter=A --name-only --format='' 4edb25d..HEAD | grep '^tools/'
tools/souji-declared-evidence.py
tools/souji-gate-check.py
```

Two new tool files; every other `cand-*.sh` untouched this round (`git log --diff-filter=AM`
shows only those two under `tools/`). No `rm`|`mv`/`shutil.move`/`os.remove`/`os.rename`/
`truncate`/`chmod`/`eval`/`exec`/`shell=True`/network calls in either tool's counter path —
`Repo.git` runs read-only plumbing (`rev-parse --show-toplevel`, `cat-file -e`, `show <rev>:<p>`,
`ls-tree`), gate-check is pure file reads. The only writes are selftest fixtures inside
`tempfile.mkdtemp(prefix=…, dir="/var/tmp")`.

Still-open (round-1 `Sentinel` **F4**, `finding:low`): both tools do contain
`subprocess.run(["rm","-rf", base], check=False)` —
`tools/souji-declared-evidence.py:310`, `tools/souji-gate-check.py:286` — in the selftest `finally`,
where `base` is the tool's own `mkdtemp` under `/var/tmp`. Not reachable from a flag, stdin,
SCORECARD text, Gate text or the network; never in the counter path. So the literal wording
"`tools/` has no new file that deletes" is technically breached (a new file does exec an external
`rm -rf`), but it is confined to the tool's own scratch and grants no authority over lane or
foreign bytes. **Still open, severity low** — smallest remediation stays `TemporaryDirectory`.

Quarantine path: **clean**. No quarantine executor exists in the round's diff; the pre-existing
`tools/cand-*-quarantine.sh` files are byte-unchanged this round, and no new tool performs a move
in any mode. `quarantine-staging-no-copy-r23.md` itself records "the audit's own rule is *dry-run
by default, quarantine before delete*" (lines 22-23) and "No staging tool is changed by this
entry. It removes a blocker; it grants no new deletion or move authority" (lines 62-63). The
theme was assimilated as *evidence that the primitive exists* (F4 ground); the operator-owned
staging-tool change remains future work, not landed authority.

## Item 2 — secrets / op-refs / private paths — clean for secrets; private-path finding:low (still open, not new)

Executed — pattern scan (`ghp_|gho_|ghs_|github_pat_|sk-|AKIA|xox[baprs]-|PRIVATE KEY|password|
token=|api_key|cookie|sessionid|bearer|/home/*|/root/|.ssh|.gnupg|op://|op-ref|1password|keychain`)
plus an entropy scan (AWS/GitHub/Slack/JWT/bearer/44+-char base64) over:

- `corpus/knowledge/quarantine-staging-no-copy-r23.md`
- `corpus/knowledge/quarantine-origin-record-fields-r24.md`
- `corpus/lessons/round-22.md`
- all 13 files under `census/round-22/attempt2/sources/` (raw + txt + vendored payload)
- the six committed SOURCES rows `S109–S114` (`corpus/SOURCES.md:129-134`)
- `census/round-22/attempt2/{quarantine-slice,slice-verdicts.tsv}`

Observed: **zero** credential-shaped hits. The only pattern hits were:

- `arch-gio.1.{raw,txt}`: man-page prose "command may ask for user IDs, passwords, and so on"
  — upstream descriptive text, not a secret.
- Long-token matches were all sha256 digests and commit hashes (expected evidence).
- Private-path class (`finding:low`, still open — round-1 `Sentinel` **F8**):
  - `corpus/knowledge/quarantine-staging-no-copy-r23.md:40-41` — `/var/tmp`,
    `/home/vgpnk/Projects/shokunin`, `/home/vgpnk/Projects/shokuknow`, `/dev/shm`, `/tmp`
  - `corpus/SOURCES.md:129` (S109 row) — `lanes/souji/round2/evidence/…` plus the five mount paths
  - `census/round-22/attempt2/sources/vendor-noreplace-probe.out:2-3` — the two `/home/vgpnk/…`
    rows inside the **vendored** payload itself (do not edit: the S109 row and the r23 entry
    bind its sha256 `1634d206…8bb5`; I re-derived that digest and it matches the committed bytes).
  - `corpus/README.md:425` — `/home/vgpnk/Projects/shokuknow/merge/souji/` package root.

  Local username + directory layout, no credentials, no op-refs, no cookies anywhere in scope.
  Pre-existing convention (older lessons/LOG carry the same class), so ~a dozen new durable
  lines of it. Smallest remediation per F8: mount labels in prose; never edit the vendored
  payload — if the paths must go, re-vendor a redacted copy and update S109 + entry digest
  atomically.

## Item 3 — commits touch only lane paths — clean

Executed:

```
$ bash /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state .
state branch=master local=c9f1fe3caf642dfe3a9e00de94caf1d4bf86503f remote=c9f1fe3… ahead=0 behind=0 head=detached tracked=5 untracked=3

$ git log --name-only --format='' 4edb25d..HEAD | sort -u   # 315 paths, evidence/r22a2-touched-paths.txt
top-level histogram: 289 .ufo/waves/round-22/… · 16 census/round-22/attempt2/… · 5 corpus/
                     · 2 tools/ · 1 SCORECARD.md · 1 SKILL.md · 1 LOG.md
```

Per-commit `git show --stat` on all 11 commits (a211e4d, 70af563, 2a130b4, 3216c19, 5ff5041,
d6a75ba, af73b8b, 5fdd5d5, ee1aef2, 4a6ee90, c9f1fe3 — evidence `r22a2-late-commit-stats.txt`
for the two late landers): every path sits under `souji-shokunin/` — git cannot commit outside
the repo root, so fleet-root `templates/`, `scripts/`, `MANIFEST.json` and `.ufo/state` are
unreachable by construction, and additionally **zero** touched paths match `MANIFEST.json`,
`\.ufo/state`, `watchdog`, `^templates/`, `^scripts/` (grep over the 315-path set → no match;
all `.ufo/` writes are lane-local `.ufo/waves/round-22/`). The lane repo contains no
`templates/`, `scripts/` or `MANIFEST.json` to collide with.

Lane worktree `git status --porcelain` at audit time shows only sibling-seed work in flight
(5 tracked `.ufo/waves/round-22/attempt2/w1/*.md` modifications + 2 untracked impl-a evidence
files + untracked `census/operator-sweep-20261019/` — operator-owned, untouched and uncommitted
by the round; none of the round's commits include it). `tools/` is clean at tip: the
`ee1aef2`-era dirty `souji-declared-evidence.py` was committed by `4a6ee90`.

Round-1 `RevScope` fleet findings (F5/F6 — modified fleet `scripts/hyaku/*`, `.bak` files,
uncommitted contract): **out of scope** for lane commits — operator-owned fleet-root state,
unchanged attribution (external round-35 sweep was active); no round-22 commit reaches them.

## Item 4 — vendored probe labelled as vendored — clean

Payload: `census/round-22/attempt2/sources/vendor-noreplace-probe.out`,
`sha256 1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5` — executed
`cmp` against the stated origin `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/
noreplace-probe.out`: **byte-identical** (both digest to the cited value). Labelling:

| citation | label present |
|---|---|
| `corpus/knowledge/quarantine-staging-no-copy-r23.md:1` | "vendored byte-exact … not re-run in this lane" |
| r23 entry body :36-42 | "**vendored**, five-device availability observation … produced 2026-10-23 by the `corpus-expansion-1` staging lane" |
| `corpus/SOURCES.md:129` (S109) | "vendored — lanes/souji/round2/evidence/noreplace_probe.py and noreplace-probe.out (byte-exact copy …, sha256 1634d206…8bb5)"; `own-work`; "produced 2026-10-23, not re-run in this lane" |
| `corpus/lessons/round-22.md:333` | "a *vendored* byte-exact copy (sha256 `1634d206…8bb5`) labelled as not re-run here" |
| `corpus/README.md:431` | "the five-device measurement vendored and labelled, not re-run here" |
| `LOG.md:1502` | "byte-exact payload (sha256 1634d206...8bb5) labelled as not re-run" |
| `slice-verdicts.tsv` S124 / `w1/Slice124.md` | refers to the **register row's** campaign payload (`lanes/souji/round2/evidence/noreplace-probe.out`), byte-identical to the vendored copy (same sha256 re-derived, Slice124.md:109); the verdict is a provenance verdict about the register, not a fresh claim of this lane's execution |

Every durable citation carries the vendored/byte-exact/not-re-run provenance. **Clean.**

---

## Round-1 findings checked against landed bytes (no restatement)

- `Sentinel` F1 (symlink escape in snapshot-dir containment) — **fixed:verified** at
  `af73b8b` (`os.path.realpath` on both sides, gate-check.py:101-103); holds at tip.
- `Sentinel` F4 (`rm -rf` selftest teardown) — **still open**, low; mapped to item 1.
- `Sentinel` F8 (host absolute paths in durable text) — **still open**, low; mapped to item 2.
- `Sentinel` F14 (C1 counter measured from dirty worktree + `SyntaxWarning: "\|"`) — **fixed**:
  tool committed at `4a6ee90`; `python3 -Werror -c py_compile` on the tip bytes → no warning
  (the docstring was made raw/escaped-pipe fix landed with the cell-split repair).
- `Sentinel` F6/F7 (per-request `report-to` token in `rev-doi-S118.headers`; third-party
  personal data in `rev-qiita-item.json`) — **still open** but out of this item's scope: both
  are w1 evidence files under `.ufo/waves/round-22/attempt2/w1/evidence/`, not in the four
  enumerated durable surfaces; no copy of those values reached the corpus (grepped).
- `RevScope` F5/F6 (fleet-root `scripts/` modifications, `.bak` leftovers) — **out of scope**,
  operator-owned; no round commit touches them.

## Net

No new deletion/move authority over lane or foreign bytes was created (the two selftest-scoped
`rm -rf` calls on a `mkdtemp` under `/var/tmp` are the sole new removal-power surface and were
already flagged F4). No secret, credential, cookie or op-ref appears in any in-scope durable
file; the only private-path class is the documented, already-found F8 pattern including the
vendored payload's own rows (do-not-edit). All 11 commits touch only lane paths. The vendored
probe is byte-exact to its origin and labelled vendored everywhere it is cited.

Per item: (1) `finding:low` still-open @ tools/souji-declared-evidence.py:310,
tools/souji-gate-check.py:286 — confined scratch teardown, not authority; (2) `clean` for
secrets + `finding:low` still-open for host paths @ r23:40-41, SOURCES.md:129,
vendor-noreplace-probe.out:2-3, README.md:425; (3) `clean`; (4) `clean`.
