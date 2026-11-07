## Status

STATUS: PASS — the whole host toolchain this round's three counters need is present and working (node v24.21.0, git 2.56.0, gawk 5.4.1, jq 1.8.2, jj 0.45.1, python3 3.14.8), all five named scripts exist with recorded sha256s, the v2 wave policy carries band 64-128 and the live round-27 wave was planned under it (79 spawn lanes, in band), and the lane helper identity rule `jj-lane.sh commit <lane> --as souji` is confirmed against the lane's own jj config. No tool is missing and no install is proposed. Three operability hazards are recorded as findings (F2, F3, F4) for the L1; none is a contract change.

## Evidence

### E1 — Host tool versions (this run)

```
$ node --version            → v24.21.0      (fnm multishell path; /run/user/1000/fnm_multishells/…/bin/node)
$ git --version             → git version 2.56.0
$ jj --version              → jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5   (/home/vgpnk/.local/bin/jj)
$ bash --version            → GNU bash, version 5.3.20(1)-release
$ gawk --version            → GNU Awk 5.4.1, API 4.1, PMA Avon 8-g1
$ jq --version              → jq-1.8.2      (/home/vgpnk/.local/bin/jq and /usr/bin/jq)
$ python3 --version         → Python 3.14.8 ; python3 -B --version → Python 3.14.8
$ flock --version           → flock from util-linux 2.42.4
$ shellcheck --version      → version: 0.11.0
```

Node satisfies the repo's declared floor — `/home/vgpnk/Projects/ufo-fsd-alpha/package.json:42` reads `"node": ">=22"`.

### E2 — Presence + sha256 of every named script

| Path | sha256 | bytes | mtime |
|---|---|---|---|
| `/home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs` | `9dbd91aaa26f9c5804db8a59538d4c27e20af91165601c9048025192322e8322` | 107309 | 2026-10-24 21:55:12 -0300 |
| `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` | `3fb7261569f46423dd80ecc23e0a23789a7926f667c7a3fc559d2439d4a64e30` | 35466 | 2026-10-19 21:22:45 -0300 |
| `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh` | `319a56f7f0641915bdb636d88b2d6b34987a20f430d7b06896150f8ae4c1e429` | 38971 | 2026-10-20 18:39:30 -0300 |
| `/home/vgpnk/Projects/shokunin/scripts/hyaku/fleet-commit.sh` | `5ea19f7193d35a5da50e67524213d68e198e14bea20a4db1aec98ece650ecddc` | 5942 | 2026-10-23 01:07:35 -0300 |
| `/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json` | `f12e1d6dfeae81a4a1ff805f8de50ec8386b3a16ae7f40b171f54c5236812fff` | 12676 | 2026-10-22 15:55:22 -0300 |

Nothing is missing. All five are byte-identical to their committed blobs (worktree `git hash-object` == `git rev-parse HEAD:<path>`), i.e. no local drift:

- `ufo-fsd-alpha` HEAD `fb7157fcf14625be9d0b91bdd425a4b3212e4194`, blob for `scripts/ufo-swarm-wave.mjs` = `e8997ff305670557d055af96ae78114cf87f3f98`; `git status --porcelain scripts/` empty.
- fleet repo HEAD `ecd8086ccc47f9cddd9305948d0e6f1773762716`; blobs `3f314620b2395eeb70d8405410132027dfe608e4` (sources-census.sh), `5edba8ca35e197c0e21e357b5a425709a25b79a6` (jj-lane.sh), `9123644c8eda1ce12b2e88b6772f5cb3e521e5ab` (fleet-commit.sh), `995ae64fb19d3a08f5b8d2b3b255d894cfe5d344` (ufo-wave-policy-v2.json); `git status --porcelain` on all four empty.

Script smoke:

```
$ node …/ufo-swarm-wave.mjs --help
{"schema":"ufo-swarm-wave-error-v1","code":"usage","message":"Usage: ufo-swarm-wave.mjs plan --spec <wave.json|->|…"}   (exit 0)
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh selftest
… selftest ok                                                        (exit 0)
$ bash …/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
35 lines, all W04 duplicate-url-across-scopes, no E-code row          (exit 0)
```

(A prior run of the same validate piped into `head` reported rc 141 = SIGPIPE from the pipe, not the script; re-run unpiped it is rc 0.)

### E3 — Wave policy band 64-128 and the live round-27 wave

`/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json:89-90`:

```
        "waveMinLanes": 64,
        "waveMaxLanes": 128
```

(The v1 sibling `ufo-wave-policy.json:89-90` carries 32-64; `ufo-fsd-alpha/config/ufo.json:90-91` carries 32-256. Only v2 gives the band this round's contract names.)

Re-running the planner against this round's spec with the v2 policy reproduces the dispatch's own policy block exactly:

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && UFO_CONFIG_PATH=/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json \
  UFO_FLEET_ALLOW_EXTERNAL_TOOLS=1 UFO_PROJECT_ROOT=/home/vgpnk/Projects/shokunin/souji-shokunin \
  node /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs plan --spec …/.ufo/waves/round-27/w1-spec.json
policy {'source': 'config', 'maxLanes': 100, 'minLanes': 16, 'waveMinLanes': 64, 'waveMaxLanes': 128,
        'declaredMaxLanes': 100, 'hardCeiling': 256, …}
counts {'spawn': 79, 'resume': 0, 'total': 79}      (exit 0)
```

Identical to the already-written `.ufo/waves/round-27/w1-dispatch.json` policy block — the live wave was planned under v2. 79 lanes is inside 64-128. The hard ceiling is `export const MAX_SWARM_LANES = 256;` (`ufo-mission-result.mjs:2572`), and `policy.source == "config"` proves the config file was read rather than a default fallback.

### E4 — Lane helper identity rule: `jj-lane.sh commit <lane> --as souji`

Confirmed, with the exact accepted-value set.

- Usage line, `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh:12`:
  `#   jj-lane.sh commit  <lane-dir> --as <id> -m <message> [--allow-large] -- <path>...`
- The state verb exists, `jj-lane.sh:59`: `  jj-lane.sh state   <lane-dir>`; it is read-only (git `rev-parse`/`rev-list`/`status` only). Live output:
  `state branch=master local=e78ac7c4837b81b634db4a927605a751a7f006ba remote=e78ac7c4837b81b634db4a927605a751a7f006ba ahead=0 behind=0 head=detached tracked=11 untracked=28` (exit 0). Remote agrees with the frozen base: `git ls-remote origin refs/heads/master` → `e78ac7c4837b81b634db4a927605a751a7f006ba`.
- `--as` is refused unless it is the lane id or the literal `protocol`, `jj-lane.sh:622`:
  `err "--as must be the lane id ($lane_id) or protocol: $id"; exit 1; }`
  (In `[ "$id" = protocol ]` the word is a bare literal, not a variable: verified `bash -c 'id=protocol; [ "$id" = protocol ]'` → matches.)
- The lane id is derived from the repo's own jj `user.name` by stripping the `-shokunin` suffix (`jj-lane.sh:109-114`). The lane's jj config reads `user.name = "souji-shokunin"`, `user.email = "souji@shokunin.local"`, `snapshot.auto-track = "none()"`; git config carries `lane.id=souji`, `lane.branch=master`. Hence `--as souji` is exactly right for this lane, and `--as protocol` is the only other accepted spelling.
- The commit then stamps author AND committer as `souji-shokunin <souji@shokunin.local>`, and the sweep guard re-checks it on the candidate, `jj-lane.sh:595`:
  `err "candidate identity does not match requested --as $id"; return 1; }`
- The addendum's canonical invocation, `/home/vgpnk/Projects/shokunin/scripts/hyaku/lane-addendum.md:199`:
  `       {{FLEET_ROOT}}/scripts/hyaku/jj-lane.sh commit {{LANE_CWD}} --as {{LANE}} \`

Prerequisite for a landing today: jj's working copy `@` is `05f74a90` with parent `@-` = `e78ac7c4837b81b634db4a927605a751a7f006ba` = the `master` tip, and `@` is non-empty — so `cmd_commit`'s "working copy must sit on the branch tip" check is satisfied and no re-anchor is needed.

Commit-path scope, `jj-lane.sh:514`: `err "driver runtime is never committed by a lane: $path"; exit 1 ;;` — the blocked set is exactly `.ufo`, `.ufo/state`, `.ufo/state/*`, `.ufo/watchdog.log` (plus `.git`/`.jj`). Verified by replaying the same `case` over candidate paths: `.ufo/waves/round-27/w1/ScoutTooling.md` and the directory `.ufo/waves/round-27/w1` are ALLOWED; `.ufo`, `.ufo/state/x`, `.ufo/watchdog.log` are REJECTED. So this round's wave reports and the C1/C2 corpus rows are all committable through the lane helper.

### E5 — C1 baseline counter re-run (read-only, at the frozen base)

```
$ python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev e78ac7c4837b81b634db4a927605a751a7f006ba --round 27 --fleet-root /home/vgpnk/Projects/shokunin
LG-DANGLING-PTR  corpus/knowledge/registry            corpus/QUALITY.md:143 cites path absent at e78ac7c4837b
LG-DANGLING-PTR  corpus/lessons/round-24.md:232:S118   corpus/QUALITY.md:141 cites path absent at e78ac7c4837b
SUMMARY  findings=2  checked_reg=50  checked_changed=0  checked_pins=13  checked_measured=3 …
```

`findings=2` at the frozen base, exactly as the preregistration's C1 before-counter states, and the two sites map onto the prereg's attribution (QUALITY.md:143 is the Q59 row; QUALITY.md:141 is the Q57 row).

## Findings

1. **All required tools present; no install proposed.** `node v24.21.0` (repo floor `>=22` met), `git 2.56.0`, `gawk 5.4.1`, `jq 1.8.2`, `bash 5.3.20`, `jj 0.45.1`, `python3 3.14.8`, `flock 2.42.4`, `shellcheck 0.11.0`. Every script this round's counters invoke exists and is byte-identical to its committed blob (E2). Tools installed or upgraded by this seat: **none** — so no RULES.md install record is owed. Per RULES.md's channel order and the host-wide pacman pause, nothing here needs `pacman`, `uv tool`, or a manual binary fetch.

2. **Lane helper identity rule CONFIRMED: `--as souji`.** The only accepted `--as` values are the lane id (`souji`, derived from the lane's own jj `user.name = souji-shokunin`) and the literal `protocol`; the commit then stamps author and committer `souji-shokunin <souji@shokunin.local>` and the candidate is re-checked against that identity before the bookmark moves (E4). Note for the L1: `fleet-commit.sh` is the **fleet-repo** committer (it `cd`s to `/home/vgpnk/Projects/shokunin`), not the lane committer — lane work goes through `jj-lane.sh`, so the fleet repo is never written by this lane.

3. **OPERABILITY HAZARD — the C3 artifacts are not yet at their counter paths.** The preregistration's C3 counter is "tool absent at base → present at tip" at `tools/souji-pre-report-gate.sh` and `tests/fixtures/r27-pre-report-gate.sh`. As of this reading both are absent from the lane: `git ls-tree -r --name-only HEAD` at `e78ac7c4837` returns no `souji-pre-report-gate` / `r27-pre-report-gate` path, `ls tools/souji-pre-report-gate.sh` → "No such file or directory", `ls tests/fixtures/r27-pre-report-gate.sh` → "No such file or directory". Drafts exist but only as untracked wave-report-directory files — `.ufo/waves/round-27/w1/souji-pre-report-gate.sh` and `.ufo/waves/round-27/w1/r27-pre-report-gate.sh` (both `bash -n` clean). The fixture's own tool lookup (`r27-pre-report-gate.sh:46`, `TOOL=${SOUJI_PRE_REPORT_GATE:-"$LANE_ROOT/tools/souji-pre-report-gate.sh"}`) resolves to `tools/…` when installed under `tests/fixtures/`, and to the wrong place from the wave-report directory. **For the L1:** the two files must be installed at their contracted paths (`tools/souji-pre-report-gate.sh`, `tests/fixtures/r27-pre-report-gate.sh`) before the C3 counter can read `tool present at tip`; installing them at the wave-report directory alone will not satisfy it. The scratch root the fixture hardcodes is `/var/tmp/souji-r27-ExecFixtureC3Tests` — under `/var/tmp`, as required.

4. **OPERABILITY HAZARD — the C3 gate's `clean` check will FAIL on the live lane today.** The gate draft's check 4 rejects any `git status --porcelain` entry outside `--allow`; the lane worktree currently has 11 modified tracked paths (all under `.ufo/waves/round-26/w1/`) and 29 untracked paths (`.ufo/waves/round-26/w1/*` drafts, `.ufo/waves/round-27/`, `census/operator-sweep-20261019/`, `tests/fixtures/__pycache__/`, `tools/__pycache__/`) — 40 porcelain entries total. When the L1 runs the gate against this lane it must either land or explicitly `--allow` those paths, or `check-clean=FAIL` will mask a true green. (The two `__pycache__` directories are debris from python runs without `-B`; the lane contract requires `python3 -B`.)

5. **OPERABILITY HAZARD — a stale jj/git divergence on one tracked file can block a broad-path commit.** The lane's jj working copy records a **deletion** of `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` relative to `@-` (`jj status` shows `D census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc`), while git still tracks it at `eab045d284e04ab20334575ed43816b3fcb4ab04` and the file is present on disk with that exact blob (`git hash-object` matches; `git status --porcelain census/round-10/` is empty). The divergence predates this seat (the jj op store's last write is ~21 min before my first command; every jj call I made used `--ignore-working-copy`, and I ran no `jj` mutation). If a `jj-lane.sh commit` request ever names a path that sweeps that file in, the helper's own phantom-deletion guard fires — `jj-lane.sh:560-562` refuses a `D` whose path still exists on disk. **For the L1:** keep the C3 commit request pathspec-limited to the round-27 report dir, the C1 `corpus/pointer-exemptions.tsv`, the C2 corpus rows and the C3 tool+fixture; do not name a broad directory such as `census/`.

6. **The v2 band is only in force when `UFO_CONFIG_PATH` is passed.** `ufo-swarm-wave.mjs:143` resolves the config as `gatedConfigPath(ROOT, process.env.UFO_CONFIG_PATH, join(ROOT, "config", "ufo.json"), "UFO_CONFIG_PATH")`, and `ROOT` follows `UFO_PROJECT_ROOT` (`ufo-swarm-wave.mjs:129-130`). Running the planner with `UFO_PROJECT_ROOT` set to the lane but **without** `UFO_CONFIG_PATH` yields `policy.source == "default"` and band `waveMinLanes 2 / waveMaxLanes 256` — i.e. no 64-128 floor — because the lane has no `config/ufo.json`. The already-written `w1-dispatch.json` shows `source: "config"` with 64/128, so the live wave did pass `UFO_CONFIG_PATH=…/ufo-wave-policy-v2.json`. Any re-plan or re-verify of this wave must repeat that variable.

7. **`jq` resolves to two different implementations depending on the shell — no in-scope script is affected.** Inside this OMP tool session, `jq` is a shell builtin reporting `jaq 3.1.1`; in any child `bash`/`sh` (i.e. inside scripts) it is `jq-1.8.2` at `/home/vgpnk/.local/bin/jq` (and `/usr/bin/jq`). Behaviour diverges: the builtin has no `tostream` and no `ascii`, and its error strings differ (`Error: cannot use … as string` vs `jq: error (at p.json:1): …`). Neither script in this round's counter path calls `jq` — `sources-census.sh` uses gawk (11 references, header line 8 reads `# Bash + coreutils + gawk.`) and `ufo-swarm-wave.mjs` has zero `jq` references — so C2's census counter and C3's fixture are unaffected. Flagged only because seat reports that quote `jq` output from an agent shell should note which implementation produced it.

8. **Minor, no action:** `ufo-wave-policy-v2.json` is mode `0600` (owner-only) while its v1 sibling is `0644`; readable by every seat that runs as `vgpnk`, so it is not blocking, but it is an inconsistency worth one line in the fleet hygiene ledger.

## Attack log

Not an attack item — this seat is a tooling/environment verification, and no predicate, target, counter or case set was touched. All checks above are read-only against the lane and the fleet repo (`git log/show/diff/status/ls-tree/cat-file/rev-parse/ls-remote`, `jj --ignore-working-copy log/status/file list/config list`, `sha256sum`, `--help`/`selftest`/`plan`/`validate` invocations). No `git add/commit/push/stash/checkout/reset`, no `jj` mutation, no `rm`/`mv` of anything I did not create, no signals, and no write outside this report file. Scratch lived only under `/var/tmp/souji-r27-ScoutTooling/` and was removed at the end of the run.
