# W2Bounds — bounds attack, round-23 tip

Seat: `L1Souji23.W2Bounds` (wave 2, falsify). Read-only; no lane commit, no `jj` mutation, no
signal, no install. Scratch `/var/tmp/souji-r23-w2-Bounds/` removed before this report was filed.

Tip attacked: `git rev-parse HEAD` = `102690017115cb202f292828c90b72705f69bf09` (`master`), parents
`c0eeaa7` ← `4765250` ← base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`. `jj @` =
`5e8b78bf396e…` (working-copy commit holding only the two untracked wave-2 files).

## Verdicts

| bound (prereg `Bounds`, carried into every wave) | verdict | evidence |
|---|---|---|
| Deletion **certification OFF** | **survives** | SKILL.md byte-identical to base; SCORECARD bound line unchanged |
| **K5 HELD** | **survives** | same two files; 6/6 occurrences at both ends, zero bound-word lines in the diff |
| **F5 reap + NAMESPACE_SHA256 holds unchanged** | **survives** | SKILL.md:343-345, PROVINCE.md:156-158,171-172, SCORECARD.md:46 — all identical to base |
| **no file outside the lane written by the round** | **survives for fleet-tracked paths** (with a structural blindness, F3) | fleet `git status` + a fleet-wide mtime sweep |
| **no operator-sweep contents read or staged** | **falsified as an unqualified claim; undisclosed** (F1) | the round's own runner materializes the 15 tracked `census/operator-sweep-20261018/*` blobs on every `run`; wave-1 named it, no disposition |

## Evidence

### 1. Certification OFF / K5 HELD / F5 reap + NAMESPACE — no drift

```
$ for f in SKILL.md PROVINCE.md; do git show <base>:$f | sha256sum; sha256sum $f; done
SKILL.md     a6d4797a8c9bca3c2e7c63fe2b1d2a87da5f6f7433c8788c5dccdb2fbd0e4795   (base)
SKILL.md     a6d4797a8c9bca3c2e7c63fe2b1d2a87da5f6f7433c8788c5dccdb2fbd0e4795   (tip)
PROVINCE.md  3a2364d7cbea724485f64d3ff97ce9eb723f013559b969c491343320d582bda8   (base)
PROVINCE.md  3a2364d7cbea724485f64d3ff97ce9eb723f013559b969c491343320d582bda8   (tip)
```

`git diff --name-status <base>..HEAD -- SKILL.md PROVINCE.md SCORECARD.md` → `M SCORECARD.md` only.
Every bound-bearing passage is therefore byte-identical by construction in SKILL.md and PROVINCE.md:

- `SKILL.md:12` "**Deletion certification is OFF** (r11 evidence-integrity failure…)";
- `SKILL.md:343-345` "The specific `souji | round-18` F5 reap and NAMESPACE_SHA256 requests remain
  **HELD** … No listing grants killing, quarantine or deletion. Certification **OFF**, K5 **HELD**.";
- `SKILL.md:362` "inherited reap/NAMESPACE holds, certification OFF and K5 HELD are unchanged";
- `PROVINCE.md:156-158` "F5 reap and NAMESPACE_SHA256 remain HELD … certification OFF, K5 HELD";
- `PROVINCE.md:171-172` "inherited reap and NAMESPACE holds, certification OFF and K5 HELD are unchanged".

SCORECARD.md did change (+23 lines: a new "Round 23 measurements" table and two new registry rows).
The bound statements themselves did not move in substance, and no bound-word line was edited:

```
$ git show <base>:SCORECARD.md | sed -n '29p'
Certification OFF, K5 HELD; inherited reap/NAMESPACE holds unchanged.
$ sed -n '46p' SCORECARD.md
Certification OFF, K5 HELD; inherited reap/NAMESPACE holds unchanged.
$ git show <base>:SCORECARD.md | grep -ciE 'certification (stays )?OFF'   -> 6
$ grep -ciE 'certification (stays )?OFF' SCORECARD.md                     -> 6
$ git show <base>:SCORECARD.md | grep -ciE 'K5 HELD'                      -> 6
$ grep -ciE 'K5 HELD' SCORECARD.md                                        -> 6
$ git diff <base>..HEAD -- SCORECARD.md | grep -E '^[+-].*(ertification|K5|HELD|reap|NAMESPACE)'
(no output)
```

The only `-` line in the SCORECARD hunk is the calibration row; the coverage row (SCORECARD.md:13,
the F5 source/160-byte scope row) is untouched. Additions elsewhere in the diff *reinforce* the
bounds (15 added lines containing "certification OFF" / "K5 HELD", e.g. LOG.md:1620, lessons:…,
wave-1 seat reports); none weaken them. `git diff <base>..HEAD | grep -nE '^\+' | grep -iE
'certification ON|K5 (released|lifted|cleared)|reap (authorized|approved|now)|authorized to
(delete|reap)|hold(s)? (released|lifted)'` → no hits. New `corpus/QUALITY.md` rows Q54/Q55 grant no
reap, namespace or deletion authority.

History is linear and unrewritten:

```
$ git merge-base --is-ancestor <base> HEAD   -> YES
$ git rev-list --merges <base>..HEAD | wc -l -> 0
$ git log --format='%h %an | %cn | %s' <base>..HEAD
1026900 souji-shokunin <souji@shokunin.local> | souji-shokunin <souji@shokunin.local> | round-23: wave-2 spec…
c0eeaa7 souji-shokunin <souji@shokunin.local> | souji-shokunin <souji@shokunin.local> | round-23: receipts…
4765250 souji-shokunin <souji@shokunin.local> | souji-shokunin <souji@shokunin.local> | round-23: record-agreement…
$ jj op log (78 ops in the window; the only rewrite-capable ones)
17bc971657ba 2026-10-25 05:31:31 edit commit metadata for commit 2ffa3c66…
aa2c33caad50 2026-10-25 04:17:52 edit commit metadata for commit 00eceb01…
```

Both metadata edits are `scripts/hyaku/jj-lane.sh:698` (`metaedit --update-author`) — the sanctioned
landing path, not a content rewrite. No `abandon`/`rebase`/`squash`/`undo` op in the window.

### 2. Nothing outside the lane written by the round

```
$ cd /home/vgpnk/Projects/shokunin && git status --porcelain=v1 | wc -l   -> 22 (24 by filing:
   + `?? .ufo/reports/round-24/tabi.md`, + a transient `?? .ufo/waves/round-23|24/` entry that
   appeared and vanished between calls as orchestration proceeded; no souji-attributed change)
$ git status --porcelain=v1
 M .ufo/state/{chousa,kagi,kaidoku,kake,kama,kasegi,kengaku,kumitate,mado,mori,souji,tabi,tameshi,tsukuroi}.report-baseline
 M .ufo/watchdog.log
 M scripts/hyaku/hyaku.env
 M scripts/hyaku/lane-addendum.md
?? .omp/mcp.json
?? .scratch/goal-20261025-hyaku-12h.md
?? .ufo/reports/round-24/tabi.md
?? .ufo/state/{kotoba,kotodama,revenger}.report-baseline
```

No `.ufo/reports/round-23/souji.md` exists yet — `ls .ufo/reports/round-23/ | grep -i souji` returns
nothing, and the `souji.report-baseline` digest `e3b0c442…` is the sha256 of the empty string, i.e.
the watchdog recorded round 23 with no published report. Consistent with the report being drafted
in-lane at `.ufo/waves/round-23/report-draft.md` (untracked, inside the lane).

Attribution of every entry (mtimes, and the only souji-named ones):

| path | mtime | attributable to |
|---|---|---|
| `.ufo/state/souji.report-baseline` | 05:03:02 | `scripts/shokunin-watchdog.sh:122-135`; content diff `22 e3b0c442…` → `23 e3b0c442…`; one second before hyaku's dispatch commit `826024b5` (05:03:03) |
| `.ufo/state/*.report-baseline` (16 others) | 03:23–05:06 | same watchdog, all lanes — fleet-wide churn, not souji-specific |
| `.ufo/watchdog.log` | 05:06:21 / 05:41:06 | watchdog; tail shows `driver=hyaku-inline attempt=1` launches |
| `scripts/hyaku/hyaku.env` | 03:22:37 | **predates base 04:17:52** — not this round |
| `scripts/hyaku/lane-addendum.md` | 04:16:14 | **predates base 04:17:52** — not this round |
| `.omp/mcp.json` | 2026-10-24 18:07 | predates the round |
| `.scratch/goal-20261025-hyaku-12h.md` | 05:23:08 | hyaku goal file (orchestrator), not a lane seat `[INFERENCE: author by path/content, not by process]` |

A fleet-wide sweep for anything written after the base, excluding lanes, `.git`, `.jj`, `.tower`:

```
$ find . -newermt '2026-10-25 04:17:52' -not -path './*-shokunin/*' -not -path '*/.git/*' \
    -not -path './.jj/*' -not -path './.tower/*' -iname '*souji*' -printf '%TH:%TM %p\n' | sort
05:03 ./.ufo/prompts/souji-round-23.md
05:03 ./.ufo/state/souji.report-baseline
$ find ./*-shokunin -newermt '2026-10-25 04:17:52' -iname '*souji*' -not -path './souji-shokunin/*' | head
(no output)
```

The 1 445 fleet-level files touched in the window are `.jj/` op stores, `.ufo/prompts/*` dispatch
prompts for many lanes, `.ufo/state/*` watchdog baselines, `.ufo/watchdog.log`, `.ufo/reports/*`
(hyaku per-lane reports) and `MANIFEST.json` (05:45:19, hyaku's `58c98335` "rounds ledger: mado r36
closure"). No forbidden fleet path carries a round write: `MANIFEST.json`, `.ufo/state/`,
`.ufo/watchdog.log`, `scripts/`, `templates/` were written by the orchestrator/watchdog, not by this
round's seats, and no sibling lane holds a souji-named file from the window.

## State of the working tree at filing (line-number basis)

Every line number below is against **committed HEAD `1026900`** (`git show HEAD:<file>`). The lane
working tree moved while this wave ran: `git status --porcelain` at filing is
`M .ufo/waves/round-23/preregistration.txt, M LOG.md, M SCORECARD.md, M census/round-23/records/refusal-stale-digest.txt,
M census/round-23/sources/qiita-gc-auto.raw, M corpus/README.md, M corpus/knowledge/count-objects-garbage-readings-r25.md,
M corpus/lessons/round-23.md, M tests/fixtures/r23-locator-heading.py, M tests/fixtures/r23-receipt-run.py,
M tools/souji-receipt-run.py, M tools/souji-record-agreement.py` plus the untracked wave-2 reports.

Those in-flight edits do **not** move the bounds: `git diff -- SCORECARD.md LOG.md
corpus/lessons/round-23.md corpus/README.md .ufo/waves/round-23/preregistration.txt | grep -E
'^[+-].*(ertification|K5|HELD|reap|NAMESPACE)'` → no output; `SCORECARD.md` still carries
`Certification OFF, K5 HELD; inherited reap/NAMESPACE holds unchanged.` at `:46` in both HEAD and the
worktree, 6/6 `certification OFF` and 6/6 `K5 HELD` occurrences in both; the `LOG.md` bound passage
is unchanged in text and now sits at `:1621-1622` (HEAD `:1619-1620`).

The in-flight `tools/souji-receipt-run.py` change (+11/−4: all-token argv refusal, `realpath` on
`--out`, `sys.dont_write_bytecode`) contains **no** `sparse`/`pathspec`/`operator-sweep`/checkout
change, so **F1 is unfixed in the repair currently staged in the worktree**.

## Findings

### F1 — MEDIUM — `run` materializes the lane's tracked operator-sweep contents; the bound claim is unqualified and the wave-1 finding has no disposition

- Where the claim is made: `LOG.md:1619-1620` — "no credentials, no live /proc census, **no
  operator-sweep contents**. Certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged."
  The prereg's Bounds paragraph (`preregistration.txt`, "Bounds (unchanged…)") says "no
  operator-sweep contents **read or staged**".
- Where the mechanism is: `tools/souji-receipt-run.py:171-177` — `git clone --no-local --no-checkout`
  then `git checkout --quiet --detach <rev>` with **no pathspec and no sparse filter**, scratch at
  `/var/tmp` (`:53`), removed at `:196`. The lane rev tree tracks 15
  `census/operator-sweep-20261018/*` blobs at base and at tip:

```
$ git ls-tree -r --name-only HEAD | grep -c '^census/operator-sweep'                    -> 15
$ git ls-tree -r --name-only 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd | grep -c '^census/operator-sweep' -> 15
$ grep -n 'sparse\|operator-sweep\|OPERATOR' tools/souji-receipt-run.py
(no output — no exclusion exists)
```

- Executed against the tip bytes (`sha256sum tools/souji-receipt-run.py` =
  `6bb623b8e8ce40028aee740ee40d600963d253e494048ce1ef121d5007d63e45`), in a **synthetic** repo under
  my scratch (never the lane, so no lane sweep byte was read by me):

```
$ python3 -B <lane>/tools/souji-receipt-run.py run --root /var/tmp/souji-r23-w2-Bounds/synth \
    --rev 67147b2f19d15a9188a5f43410423bb4e718bbe1 --tool tools/t.py \
    --out /var/tmp/souji-r23-w2-Bounds/r.tsv -- cat census/operator-sweep-20261019/secret.txt
receipt=/var/tmp/souji-r23-w2-Bounds/r.tsv rev=67147b2f… tool_sha256=61827c88… rc=0 counts=none
$ cat r.tsv
receipt=v1
rev=67147b2f19d15a9188a5f43410423bb4e718bbe1
tool=tools/t.py
tool_sha256=61827c88eda9032977863d841bda9b6dcb8496ff99e542c5ba652a03d8c27b61
cmd=cat census/operator-sweep-20261019/secret.txt
rc=0
--- stdout ---
SECRET-SWEEP-CONTENT
```

  So the clone is a full checkout, an arbitrary command reads an operator-sweep path out of it, and
  the receipt records the content. Applied to the lane `[INFERENCE: executed mechanism + tracked-path
  enumeration; I did not clone the lane]`, every `run` — including the five committed receipts —
  copied the 15 tracked `census/operator-sweep-20261018/*` blobs into `/var/tmp` before deleting them.
- The round already had this finding: `.ufo/waves/round-23/w1/CritC2Value.md:86-97` (E7) and
  `:120-124` ("**Bound exposure (E7).** … Contradicts the lane bound 'no operator-sweep contents read
  or staged'"), `:205` (A6). Its recorded disposition,
  `corpus/lessons/round-23.md:128`, lists the `refs/replace`/digest/refusal repairs and **does not
  mention finding 6**; `.ufo/waves/round-23/report-draft.md:71` likewise summarises CritC2Value as
  the `refs/replace` hole only. `grep -rn 'materializ' .ufo/waves/round-23/report-draft.md
  .ufo/waves/round-23/w1/ScribeReport.md corpus/lessons/round-23.md` → no hits.
- Required action: **fix or disclose, before the round is filed.** Fix = checkout restricted to the
  measured tree (e.g. `--filter=blob:none` + scoped sparse-checkout excluding
  `census/operator-sweep-*`, or a pathspec on the checkout), keeping the counter's git plumbing
  usable; disclose = a named limit in `report-draft.md` C2, `LOG.md` Round23 and
  `corpus/lessons/round-23.md:128` stating that `run` materializes the 15 tracked
  operator-sweep blobs transiently and that no receipt this round derived content from them, plus
  qualifying the unqualified "no operator-sweep contents" sentence at `LOG.md:1619`. As filed, the
  sentence is not literally true of the landed tool.

### F2 — LOW — fleet commit under the lane's git identity (attribution ambiguity, not a bound breach)

`826024b5 2026-10-25 05:03:03 souji-shokunin <souji@shokunin.local> "round-23: souji dispatch
evidence (hyaku inline attempt 1)"` touches exactly one fleet path,
`.ufo/prompts/souji-round-23.md` (483 lines). It is outside the forbidden set (not `.ufo/state/`,
`MANIFEST.json`, `scripts/`, `templates/`), its message names hyaku, and the fleet's landing pattern
for every other lane in the window is identical — so this is the orchestrator writing with the lane
identity, not a lane seat reaching into the fleet repo. No action required; noted so a later audit
does not read "souji authored a fleet commit" as lane drift.

### F3 — INFO — fleet `git status` cannot see lane writes (scope limit of this check)

`.gitignore:1:*-shokunin/` makes every lane invisible to fleet `git status`. The "no file outside
the lane" bound therefore cannot be *proved* by fleet status alone; it is supported here by (a) the
fleet-wide mtime sweep above and (b) the absence of any souji-named path outside the lane. A lane
seat writing a fleet path under a non-souji name would not be caught by either check.

## Residual risk

- The 15 tracked `census/operator-sweep-20261018/*` blobs predate the round (added 2026-10-19 by
  `2f303dc`, "souji: operator-sweep 2026-10-19 bookkeeping"). F1 is about the round's runner
  copying them out, not about the round staging them; base and tip both track 15.
- Watchdog/state/scratch attributions in §2 rest on mtimes plus the watchdog's own writer lines and
  the hyaku dispatch/commit cadence. Without a live `/proc` census (forbidden) the *process* that
  wrote them is not provable; the paths and contents are.
- `verify` does not clone (`cmd_verify` → `blob_sha_bytes(root, rev, tool)`), so the F1 exposure is
  confined to `run`.

## Verification gaps

- I did not clone the lane, so the lane-level materialization is `[INFERENCE]` (F1). The mechanism
  is executed; the object count is enumerated; the combination is not executed end to end.
- I did not read any operator-sweep content in the lane, by design.
- Sibling-lane writes by this round are checked by name (`*souji*`) and by the fleet-level sweep
  only; a rename-obscured write would escape both.
- Tooling: no installs or upgrades performed (no pacman/uv/cargo/npm transactions attempted).
