STATUS: DONE — `--compare` is correct and crash-free against census TSVs containing per-repo timeout rows: all five produced pairs gave exit 3 with complete diff rows (or exit 0 header-only for identical timeout rows); nothing hung, no partial row leaked, no stray process survived.

# ProbeCompareMode — `--compare` with timeout rows

Attacked claim: C1 operability, the `--compare` half of `tools/souji-census.sh`
(`--compare PREV.tsv` must diff a fresh census against a prior one; exit 0 for a
header-only diff, exit 3 when any row differs, census rows never mixed into the
diff) under the r18 timeout-row contract: a timed-out repository is emitted as
`<repo>\t0\t0\t0\t0\t\terror` with `souji-census: repo-timeout <N>s <repo>` on
stderr and the run still exits 0 for the census / 3 for a drifting compare.

Work performed in a private clone at the wave-1 tip
`5efb519f00075d958c3d1109ef6fcb24c487eb87` (`git status --porcelain` empty;
`tools/souji-census.sh` sha256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`),
fixtures under `/var/tmp/souji-r18w2-ProbeCompareMode/`. No tool install/update.

## Findings

### F1 — measured → timeout during `--compare`: exit 3, exact rows (holds)

Baseline: 3-repo fixture fleet, all `clean`; the shim hangs any `git -C
<fleet>/hang` call, `--repo-timeout 2`.

```
CASE baseline                           rc=0 wall_ms=1022
CASE baseline-hang                      rc=0 wall_ms=4939
CASE cmp-hang-vs-baseline               rc=3 wall_ms=5044
```

Diff stdout (exactly, no census row mixed in):

```
repo	field	before	after	change
.../fleet/hang	worktrees	1	0	-1
.../fleet/hang	mtime_iso	2026-10-20T18:19:42-03:00		changed
.../fleet/hang	verdict_flags	clean	error	changed
```

stderr: `souji-census: repo-timeout 2s /var/tmp/.../fleet/hang`. The `after`
values (`0 0 0 0 <empty> error`) confirm the placeholder row reached `load_census`
and diffed exactly. Mechanism: `emit_compare` runs `emit_census`, whose timeout
branch writes the placeholder at `tools/souji-census.sh:1709` (census_one) /
`:1693` (list-phase preflight), and `load_census` (`:1732`) accepts the empty
`mtime_iso`/`verdict_flags=error` because only columns 2–5 are numeric-checked
(`:1772-1777`).

### F2 — timeout row in the prior census vs measured now (holds)

`--compare` against the hung baseline, run without the shim: exit 3, reversed rows
(`worktrees 0→1 +1`, `mtime_iso ""→<iso> changed`, `verdict_flags error→clean
changed`), no stderr. Empty `before` mtime prints as the empty TSV field; parsers
see two adjacent tabs as documented.

### F3 — timeout on both sides: header-only, exit 0 (holds)

Two consecutive hangs compared against the hung baseline:

```
CASE cmp-hang-vs-baselinehang           rc=0 wall_ms=4972
=== cmp-hang-vs-baselinehang.tsv ===
repo	field	before	after	change
```

stderr still carries `souji-census: repo-timeout 2s ...`. Exit 0 is the documented
header-only rule; the timeout remains visible on stderr, not misreported as drift.

### F4 — list-phase guard (preflight) timeout under `--compare` (holds)

Distinct code path: hung `git config --file <repo>/.git/config` makes the
`list_repos` guard phase exceed the bound, so `preflight_timeout[$repo]=1`
(`:1680`) and `census_one` is skipped entirely (`:1693`). Result: exit 3 in
4489 ms, the same three rows, identical stderr diagnostic. The preflight and
census_one placeholder branches are behaviorally identical.

### F5 — KILL escalation, mid-measurement hang, mixed drift (holds)

- Worker ignoring SIGTERM (`trap '' TERM` loop): watchdog escalates to SIGKILL;
  exit 3, the same three rows, no `repo-timeout-unreaped`.
- Hang injected on the 5th `git -C` call (mid-`census_one`, after `worktree list`/
  `rev-list`): exit 3, placeholder row only — no partial measurement leaks into the
  row file or the diff.
- Timeout plus a real neighbour change in one run: exit 3; both the neighbour rows
  (`dirty 0→1 +1`, `mtime_iso changed`, `verdict_flags clean→dirty`) and the
  timeout rows appear, repos `LC_ALL=C`-sorted.
- `SOUJI_CENSUS_REPO_TIMEOUT=2` instead of `--repo-timeout 2`: exit 3, same rows,
  same diagnostic.

### F6 — added/removed repos carrying timeout rows (holds)

- New repo whose census times out, absent from baseline: exactly
  `<repo>\trepo\tABSENT\tPRESENT\tadded`, exit 3.
- Baseline row is a timeout placeholder, repo then deleted, now-census measured:
  exactly `<repo>\trepo\tPRESENT\tABSENT\tremoved`, exit 3 — the empty `mtime_iso`
  in the `before` row does not disturb the removal path.
- `--include-root` where the root repo itself times out: exit 3, four rows
  (`worktrees 1→0 -1`, `dirty 1→0 -1`, `mtime_iso changed`, `verdict_flags
  dirty→error`), child measured normally.

### F7 — Coverage gap in the claimed fixture evidence (finding, not a tool defect)

`grep -c -- '--compare' tests/fixtures/r18-census-bounded.py` → `0`. B1–B8
(`tests/fixtures/r18-census-bounded.py:32`) never invoke `--compare`, and the
in-tool selftest's compare checks (`tools/souji-census.sh:2124`, `:2154`, `:2176`)
use healthy fixtures only. So the claimed C1 fixture evidence does **not** exercise
compare against a timeout row; the only coverage is this live probe. Suggest one
B9: baseline → shim hang → `--compare`, assert exit 3 plus the three rows, and a
second `--compare` of two hung runs asserting header-only/exit 0.

### F8 — Placeholder semantics visible in the diff (observation, per contract)

Because the timeout row's numeric fields are placeholders (`:160`, `:1309`,
`:1693`, `:1709`), `--compare` reports synthetic numeric movement: `worktrees
1→0 -1`, and `dirty 1→0 -1` when the prior census had a dirty tree. The true
signal is the accompanying `verdict_flags … error` row; the tool cannot
distinguish "count fell" from "unmeasured" in the numeric row. Also, a timeout row
and a config-unsupported row are byte-identical, so two different unmeasured causes
compare clean. Both follow the documented placeholder contract (`:157-163`,
`:165-169`), not a violation.

## Verdict

**holds** — no crash, no hung compare, no exit-code surprise in any of the 10
compare runs across five timeout shapes (measured→error, error→measured,
error→error, preflight, root, KILL escalation, mid-census, added, removed, mixed).
`--compare` exits 3 exactly when a diff row exists, 0 when the diff is header-only,
never 1/2 on the timeout path, and its stdout is pure diff TSV.

Smallest fix: none required for C1. If the evidence gap in F7 matters, add the B9
fixture case above; the tool needs no change.

## Cleanup

Clone and all fixture/shim directories under
`/var/tmp/souji-r18w2-ProbeCompareMode/` removed after the runs; no processes from
this probe remain (`ps` filtered on the probe path was empty after the harness
exited), no lane file, fleet repo, or shared record was written — this report only.
