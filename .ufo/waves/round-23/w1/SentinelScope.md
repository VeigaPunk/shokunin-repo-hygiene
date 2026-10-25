# SentinelScope — security and scope review, souji round 23 w1

## Status

STATUS: PARTIAL — 1 HIGH, 4 MEDIUM, 1 LOW; item 4's claim is accurate and confirmed from both the opened page and the installed manual. No credential was read or printed this run; `.scratch/` and operator-sweep contents were not opened.

Verdicts: (1) credential surfaces — **needs-guard** (no redaction, no size cap on the committed echo). (2) read-only runner — **needs-guard** (5 of the needed guards present, 3 absent, 1 fixture assertion blind). (3) scope — **needs-guard** (all cross-repo reads are read-only and gated; one fleet `git status` can write the fleet index). (4) `fsck --lost-found` writes — **clean** (claim accurate; the round's own commands cannot reach it except through the runner's arbitrary `-- cmd…`, covered by F3).

## Evidence

Lane revision `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`; `git --version` → `git version 2.56.0`; `/usr/share/man/man1/git-fsck.1.gz` owned by `git 2.56.0-1`. Surfaces read: `tools/souji-receipt-run.py` (214 lines, landed 05:11), `tools/souji-record-agreement.py` (untracked, landed 05:08), `.ufo/waves/round-23/w1/r23-receipt-run.py` (fixture, 515 lines), `.ufo/waves/round-23/w1-spec.json` (41 items), peers' `ScoutFsck.md` and `ScoutMisroot.md`.

```
$ man git-fsck | col -b | sed -n '79,82p'
     --lost-found
	 Write	  dangling    objects	 into	 .git/lost-found/commit/     or
	 .git/lost-found/other/,  depending  on	 type. If the object is a blob,
	 the contents are written into the file, rather than its object name.
```

```
$ man git | col -b | sed -n '1460,1465p'
     GIT_OPTIONAL_LOCKS
	 If  this  Boolean  environment variable is set to false, Git will com‐
	 plete any requested operation without performing any optional	sub-op‐
	 erations  that	 require  taking a lock. For example, this will prevent
	 git status from refreshing the index as a side effect.
```

```
$ git config --list --name-only | grep -iE 'credential|token|insteadof|user\.'
user.name
user.email
credential.https://github.com.helper
credential.https://origin.cursor.com.helper          (key names only; no values read)
```

```
$ git cat-file -e "HEAD:../../../etc/passwd"
fatal: '../../../etc/passwd' is outside repository at '/home/vgpnk/Projects/shokunin/souji-shokunin'
```

```
$ grep -n "redact\|REDACT\|optional" tools/souji-receipt-run.py
(no output)
```

## Findings

### F1 — HIGH (item 2): `--out` is an under-constrained write primitive that can land outside the lane

Location: `tools/souji-receipt-run.py:105-108` (`OUT-UNDER-TMP`, `OUT-IN-REPO`), `:136` `os.makedirs(os.path.dirname(out) or ".", exist_ok=True)`, `:139-141` `open(out, "w")`.

Only two destinations are refused: `/tmp` and anything inside `--root`. Every other absolute path is accepted, and the parent directories are created on demand.

Exploit: `--out /home/vgpnk/Projects/shokunin/.ufo/state/souji.report-baseline` overwrites orchestrator run state; `--out /home/vgpnk/Projects/shokunin/kotoba-shokunin/x.receipt` writes a sibling lane; `--out ~/.config/...` writes operator config. All three are barred by the HARD BOUND and none is refused.

Second-order note (not a defect, a trap for the L1): C2's counter is `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/`, and `OUT-IN-REPO` makes the natural invocation `--root <lane> --out census/round-23/records/…` impossible. The only legal shape is `--out /var/tmp/…` followed by a landing through `scripts/hyaku/jj-lane.sh` — consistent with C2's "never writes the lane tree", but the fixture pins no *positive* out path (case 6 tests only the `/tmp` refusal).

Smallest remediation: allowlist `out` to `SCRATCH_ROOT + "/souji-r23-"` (refuse everything else with `OUT-NOT-ALLOWLISTED`). Fixture cases: `--out` under `.ufo/state/` refused; `--out` under a sibling lane refused; `--out` under `/var/tmp/souji-r23-*` accepted.

### F2 — HIGH (item 1): the receipt is an unbounded, unredacted echo of `cmd`, stdout and stderr

Location: `tools/souji-receipt-run.py:124-134` — `cmd={shlex.join(args.command)}`, then `proc.stdout.rstrip("\n")` and `proc.stderr.rstrip("\n")` written verbatim between the fences. `grep` for `redact` in the file returns nothing.

What could leak: the runner is a generic executor, so the leak surface is its capability, not its planned uses. `-- git config --list` prints `user.email` and the four `credential.*.helper` keys observed above; `-- git remote -v` prints remote URLs with userinfo; `-- env` prints the whole environment. Receipts are append-only by C1's own K2 predicate ("filed bytes are append-only"), so any leak is permanent and unamendable.

The planned invocations themselves are clean, and I checked this rather than assuming: `souji-gate-check.py` prints only `entries= ok= fail=` counts (`:181-229`), `souji-declared-evidence.py` prints counts (`:192`), and `souji-record-agreement.py` prints only regex-matched scalars plus lane-relative paths (`:254-259`). So F2 is a capability leak, not an observed one.

Smallest remediation — reuse the lane's existing guard, do not invent a second convention: port `redact_secrets` (`tools/souji-proc-census.sh:207-243`: Authorization/Bearer, `--token=`, `ghp_`, `sk-`, `password=`, URL userinfo, `AKIA…`, `xox[baprs]-…`) into the Python runner and apply it to `cmd`, stdout and stderr before the write; cap each stream (e.g. 64 KiB) with an explicit truncation marker. Add a fixture case with a canary in argv and in the child's stdout asserting the canary is absent from the receipt.

Precedent for why this matters: `census/round-21/cmd-compatibility.json` already carries one committed URL-userinfo string (1-char user, 7-char password) under an `input` key. I classified it without printing it — it carries a synthetic `FAKE`-family marker, so it is a canary, not a live credential. `census/` is not automatically redacted; the new receipts must not repeat that class with a real value.

### F3 — MEDIUM (items 2 and 4): the measured command is unconstrained and inherits the environment, so the read-only claim rests on the caller

Location: `tools/souji-receipt-run.py:125` `subprocess.run(args.command, cwd=scratch, capture_output=True, text=True)` — no environment scrub, no argv inspection. Contrast `:63-69`, where the runner's *own* git calls strip `GIT_DIR` and `GIT_WORK_TREE`: the two paths have inconsistent env policy.

Exploit: `cwd=scratch` does not stop an absolute path. `-- git -C /home/vgpnk/Projects/shokunin/souji-shokunin fsck --lost-found` writes `.git/lost-found/other/` with unreachable blob *contents*; `-- git -C <lane> prune` deletes unreachable objects; `-- git -C <lane> fetch` reaches the network. Separately, the child inherits `os.environ` verbatim, so a `GIT_DIR`/`GIT_WORK_TREE` exported in the L1's shell silently retargets any bare `git` the command runs — the same class the runner's own `git()` already defends against.

Exact guard needed, three parts: (a) run the command with a scrubbed env — drop every `GIT_*`, set `GIT_OPTIONAL_LOCKS=0`; (b) refuse argv containing a mutating git subcommand, minimum set for this lane: `fsck`, `prune`, `gc`, `repack`, `maintenance`, `fetch`, `pull`, `push`, `clone`, `remote`, `config`, `credential`, `reflog`, `bundle`, `update-server-info`, `filter-branch`, `fast-import`, `submodule`, `worktree`, `stash`, `reset`, `clean`, `checkout`, `switch`, `add`, `commit`, `rm`, `mv`, `update-ref`, `update-index`, `hash-object`, `read-tree`, `write-tree`, `commit-tree`, `init`, `am`, `apply`, `merge`, `rebase`, `cherry-pick`, `revert`, `notes`, `tag`, `branch`; (c) refuse any argv element that is an absolute path outside the scratch tree.

Guards that *are* correctly present, for the record: `maintenance.auto=false` and `core.fsmonitor=false` on every git call (`:58-68`) — this is what stops background auto-gc/prune from writing the measured repo; `REV_RE` full 40-hex; `cat-file -e <rev>^{commit}`; `durable_rev` via `for-each-ref --contains refs/heads refs/tags refs/remotes` (excludes `refs/jj/*`); `git archive` + extract rather than checkout; `cwd=scratch`; `shutil.rmtree` in `finally`. `--tool` traversal is blocked by git itself, not by the runner (`git cat-file` refuses `..` — probe above), so that is clean but load-bearing on git's behaviour.

Gap also worth naming: `cmd_verify` (`:170-197`) does not repeat `durable_rev`, so a receipt naming a rev reachable only from `refs/jj/*` verifies. Cheap fix: call `durable_rev` in `cmd_verify` too.

### F4 — MEDIUM (item 2): fixture case 7 cannot detect the writes it claims to exclude

Location: `.ufo/waves/round-23/w1/r23-receipt-run.py:369-381` — `before = ctx.status()` … `git status --porcelain` before and after `run`.

`git status --porcelain` reports worktree/index-vs-HEAD differences only. `fsck --lost-found` writes `.git/lost-found/…`, `prune` deletes `.git/objects/…`, `gc` rewrites packs, and an index refresh rewrites `.git/index` — every one of them invisible to porcelain. A runner that prunes therefore passes case 7.

Smallest remediation: fingerprint the whole git directory before and after — `find .git -type f -printf '%P %s\n' | sort | sha256sum` — and assert equality, plus an explicit `test ! -e .git/lost-found`. Keep the porcelain check as a second, weaker assertion.

### F5 — MEDIUM (items 1 and 2): the C1 instrument writes an arbitrary path and refreshes the lane index

Location: `tools/souji-record-agreement.py:254-263` (`open(as_json, "w", encoding="utf-8")`, no path constraint at all) and `:63-69` (`git()` env carries no `GIT_OPTIONAL_LOCKS`), used at `:241` `git(self.root, "status", "--porcelain")`.

Two defects. First, `--json` is an unconstrained write primitive: `--json /home/vgpnk/Projects/shokunin/.ufo/state/x` writes operator run state, and unlike the receipt runner there is not even a `/tmp` refusal. Second, the K4 working-tree query can refresh `.git/index` as a side effect — the manual states the mechanism directly: setting `GIT_OPTIONAL_LOCKS` false "will prevent git status from refreshing the index as a side effect". The C1 receipt captures this tool's stdout, so it would record a command that may have written the lane index, against the round's read-only framing.

Smallest remediation: add `env["GIT_OPTIONAL_LOCKS"] = "0"` to the existing env dict in `git()` (one line, same place `GIT_DIR` is already stripped), and constrain `--json` to a prefix the caller passes explicitly or refuse it outside `/var/tmp`.

Related K4 note, which is a guard rather than a defect: default `normal` untracked mode collapses untracked directories (`man git-status`: "normal — Show untracked files and directories"), which is why K4 emits `census/operator-sweep-20261019/` and not its 25 children. NEVER add `-uall` to that query: it would print operator-sweep filenames into a committed receipt. This confirms `ScoutMisroot.md` finding 5 from the security side — the only predicate-legal repair for that path is a committed `uncommitted:` exemption row naming the path (contents unstaged, path not read).

### F6 — LOW (item 3): the fleet misroot query can write the fleet index

Location: `.ufo/waves/round-23/w1-spec.json`, ScoutMisroot prompt — `git -C /home/vgpnk/Projects/shokunin status --porcelain`; executed, output at `.ufo/waves/round-23/w1/ScoutMisroot.md` Evidence §1.

Same optional-lock refresh as F5, but against the fleet repository, whose state the bound declares untouchable. The query lists `.scratch/` and `.ufo/state/` *names* and does not open `.scratch/` contents — correct, and the scout said so. Guard for this and every future fleet query: `GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin status --porcelain`.

### Item 3 — scope verdict in full: needs-guard (one item), clean otherwise

- shokuknow `/home/vgpnk/Projects/shokuknow/merge/souji/`: read by ScoutCommunity, ScribeEntryRepoSize, ScribeEntryGarbage, ScoutIdCollision (`SOURCES.append.md` grep). All four carry an explicit read-only clause ("Do not write into shokuknow", "READ-ONLY: never write into shokuknow"). Clean.
- Sibling lanes: ConnectorSiblingSources greps `"$d/corpus/SOURCES.md"` with `grep -l` only. Clean, provided it stays `grep -l` and never recurses into a sibling `.git`.
- `.scratch/`: named only as "NEVER a misroot and never touched"; contents not read by any item. Clean.
- `.ufo/state/`, `.ufo/watchdog.log`, `MANIFEST.json`, fleet `scripts/`, `templates/`: appear only in the bounds text; no item writes them. Clean — except F1's `--out` breadth, which can reach `.ufo/state/`, and F6's index refresh.
- `census/operator-sweep-20261019/`: untracked in the lane, never staged, contents never read. F5's note names the only legal K4 repair.

### Item 4 — verdict: clean, claim accurate, and the write is worse than "writes"

The C3 entry's claim that `git fsck --lost-found` WRITES is confirmed on both surfaces, verbatim and in agreement: live page https://git-scm.com/docs/git-fsck § OPTIONS (opened 2026-10-25) — "Write dangling objects into .git/lost-found/commit/ or .git/lost-found/other/, depending on type." — and `man git-fsck` lines 79-82, identical modulo hyphenation. The page's follow-on sentence is the security-relevant half: "If the object is a blob, the contents are written into the file, rather than its object name." That makes `--lost-found` a *secret-resurrection* primitive, not merely a directory-creating one: unreachable blobs — a deleted `.env`, a rotated token committed by mistake — are re-materialised as plaintext files inside the repository being measured.

Reachability from the round's own commands: none of them invoke it. `grep -rn "fsck\|lost-found\|prune" tools/souji-gate-check.py tools/souji-declared-evidence.py` returns nothing; the only fsck execution this round is `ScoutFsck.md` Evidence, which ran `git fsck --no-dangling --no-reflogs --unreachable --no-progress` and verified `.git/lost-found` absent with an unchanged `.git` mtime. The single path by which the round could reach `--lost-found` is the C2 runner's arbitrary `-- cmd…` — that is F3, and closing F3 closes this reachability.

## Attack log

No counter attack filed; the frozen predicates were not exercised and nothing in the preregistration was proposed for change. One calibration observation, offered as data not as an edit: C2's counter (`grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/`) counts receipt *files*, so it is satisfied by any file containing the header line — including one whose `verify` exits nonzero. The preregistration's own verifier sentence ("each verifiable with `python3 tools/souji-receipt-run.py verify <receipt>`") carries the real predicate; the grep counter alone does not.

Bounds honoured: no `git add/commit/push/stash/checkout`, no `jj` mutation, no `rm`/`mv`, no signals, no writes outside this report, no `.scratch/` or operator-sweep contents, no credential values read or printed (config **key names** only), no live `/proc` census. Tooling: no install or upgrade performed this run.
