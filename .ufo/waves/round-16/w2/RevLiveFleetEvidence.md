# RevLiveFleetEvidence — review of `census/round-16/live-fleet.json` and `live-fleet-final.json`

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, reviewed at `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`;
HEAD moved to `163158a706352f1c0ee3521c4da2e5289970db57` during the review, and both artifacts' blobs are
identical at each commit (`git ls-tree`: `live-fleet.json` `16280f8b…`, `live-fleet-final.json`
`94285d5d…`), so every line citation below holds at both. Source-only review; no census run, no writes
outside this report.

**Verdict summary.** The artifacts' core claim survives: two tool revisions **468 diff lines apart**
(`git diff --stat cc21683 0a70bef -- tools/souji-census.sh` → `403 insertions(+), 65 deletions(-)`)
produced byte-identical run rows on the live fleet, and every recorded arm hash reproduces from
git. The failures are evidentiary, not behavioural: the one column the equality claim excludes is
**not stored at all**, the "paired concurrent" design is asserted without a single timestamp, and
the coverage set is silently truncated. No finding invalidates row preservation; three findings
must be fixed before the artifact can carry the claim on its own.

---

## What the artifacts prove

**P1 — Arm bytes are exact and reproducible.** Each `tool_sha256` equals the sha256 of that rev's
committed `tools/souji-census.sh` (computed here):

| arm rev | recorded sha256 | computed |
|---|---|---|
| `cc21683` (r14-harm) | `fcff8b057b3e7dc5…` | `fcff8b05…` ✓ |
| `cbf688a` (earlier changed) | `fed43c710b755b02…` | `fed43c71…` ✓ |
| `0a70bef` (final changed) | `64a60fd0b0ed4101…` | `64a60fd0…` ✓ |

HEAD's `tools/souji-census.sh` hashes to `64a60fd0…`, so the final artifact's changed arm is the
tool currently committed.

**P2 — All recorded arms are reachable from HEAD** (`cc21683`, `cbf688a`, `0a70bef` all appear in
`git log HEAD`), so the provenance chain is reconstructible even though the run worktrees are gone.

**P3 — Row preservation is real and non-trivial.** In `live-fleet-final.json` both arms record
`row_count: 21` and list exactly 21 rows; the arrays are *exactly* equal (checked elementwise, order
included). Given P1 and the 468-line code delta, that is genuine preservation evidence for the
emitted columns.

**P4 — No live repo carried a key the r14 guard refuses.** The final note (line 362) asserts this;
it is independently true. I matched all 21 repos' `.git/config` against r14's exact refusal list
(`include.*`, `includeif.*`, `filter.*.clean|smudge|process`, `core.hooksPath`,
`core.attributesFile`, `core.excludesFile`, `core.alternateRefsCommand`, `remote.*.promisor`,
`extensions.partialClone`, `extensions.worktreeConfig`; `tools/souji-census.sh` @`cc21683` guard
clause): **zero hits**. Consistent with every row carrying no `error` flag.

**P5 — The r15 baseline really does not parse.** `git cat-file -p b410186:tools/souji-census.sh |
bash -n /dev/stdin` → `/dev/stdin: line 1368: syntax error near unexpected token '}'`, `rc=2`,
exactly as `live-fleet.json:394-400` records (line number included).

**P6 — `a31642d`'s exclusion is justified.** In `a31642d` the only status call is
`git -C "$1" --no-optional-locks status --porcelain` with **no** `-c core.fsmonitor=false` and no
`-c core.hooksPath=/dev/null`; `cc21683` adds both at its status call. The `not_run` reason
(`live-fleet-final.json:363`) is therefore mechanically accurate, not a post-hoc excuse.

Corollary worth recording: no row carries `status-unverifiable`, so no live repo had a bound
filter driver (the tool prints that diagnostic to stderr, `tools/souji-census.sh:1027-1029`, and
`stderr_lines: 0`). That is what `stderr_lines: 0` actually proves.

---

## What they do **not** prove

- **N1 — Nothing about config-guard behaviour on a refused key.** Stated honestly at line 362; the
  fixture carries that claim. Do not read the live pair as guard evidence.
- **N2 — Nothing about `mtime_iso` agreement.** The tool emits **7** columns
  (`tools/souji-census.sh:170`, `:1252`); both JSONs store **6**. Column 6 (`mtime_iso`) is absent
  from every row (all row widths are 6, no empty cells). See F1.
- **N3 — Not that the runs were concurrent, or even same-minute.** No timestamps, no durations in
  the final file. See F2.
- **N4 — Not that 21 is the fleet's size.** Coverage is direct children whose `.git` is a
  *directory*; symlinked children, `.git`-file children, dot-dirs and unrepresentable names are
  skipped with no row and no record (`tools/souji-census.sh:1287-1300`). See F4.
- **N5 — Not that sibling-configured commands did not execute.** `stderr_lines: 0` observes stderr,
  not execution. `GIT_CONFIG_COUNT` (`:162-163`) is new in the changed arm; the per-status `-c`
  flags already existed in `cc21683` (P6). Both mechanisms are source-verifiable, but the live run
  does not demonstrate non-execution; the artifact should not be cited as if it did.
- **N6 — Not that rows are independently checkable.** Within probe bounds I cannot verify
  individual counts (`worktree list`, `rev-list` are outside the allowed git subcommands), and the
  artifact records no per-row derivation, so row values rest on the tool's own self-consistency.
- **N7 — Not a stable baseline.** `souji-shokunin`'s own row (`dirty,unpushed,scratch,secret-shaped`)
  is in the census; the snapshot changes as the round proceeds. The final note says this for the
  earlier run; it applies equally to this one.

---

## Findings

### F1 — major — the stored rows are not the tool's rows; the equality claim is unfalsifiable

`live-fleet-final.json:361` and `live-fleet.json:393` assert `"rows_identical_excluding_mtime": true`,
but `mtime_iso` is nowhere in either file. The tool's row is
`repo \t worktrees \t unpushed \t dirty \t scratch_bytes \t mtime_iso \t verdict_flags`
(`tools/souji-census.sh:170`, printed at `:1252`); every stored row is 6 elements. So the boolean
holds over the *projection*, and the excluded column — the only one that could have differed — was
never captured. A reader cannot distinguish "the arms agreed on mtime" from "mtime was never
compared", and cannot feed these rows back to `--compare` (which requires the 7-column header as
line 1, `tools/souji-census.sh:1335`).

*Minimal patch* (both files), preferred — make the claim checkable:

```json
 "mtime_compared": true,
 "mtime_differences": 0,
 "row_columns": ["repo","worktrees","unpushed","dirty","scratch_bytes","verdict_flags"],
```

Minimum honest fallback if mtime was not actually compared: keep `rows_identical_excluding_mtime`
and add `"mtime_compared": false` plus the `row_columns` line. **Verdict: partial.**

### F2 — major — "paired concurrent runs" has no evidence

`live-fleet-final.json:3` says `"observed": "2026-10-20 (L1 SoujiR16), paired concurrent runs"`, and
the note (line 362) rests comparability on that pairing. But the file records no start/end or
duration: `:9` and `:186` are `"result": "rc=0"`, whereas the earlier file still carries
`"rc=0 secs=8"` (`live-fleet.json:9`) and `"rc=0 secs=9"` (`:202`). With no timestamps an operator
cannot tell whether the 21-row agreement came from overlapping windows on the same fleet state, or
from two sequential runs minutes apart — which matters because the artifact set itself documents a
23-repo → 21-repo fleet change between the two observations (F3).

*Minimal patch* (final file): per arm add `"started": "<ISO-8601>"`, `"finished": "<ISO-8601>"`,
`"secs": <n>`; top-level `"paired": {"overlap": true, "window_secs": <n>}`. If the times were not
captured, replace `paired concurrent runs` in `observed` with `two arms, pairing unrecorded`.
**Verdict: fails as written.**

### F3 — moderate — two fleet repos vanish unexplained, and the note silently excludes them

`live-fleet.json` lists 23 rows including `attrtest` (`:14`, and `:207` in the changed arm) and
`hooktest` (`:54`, `:247`); both directories are now absent from the fleet root. The final artifact
(21 rows) never mentions them; its note (line 362) qualifies the guard claim with "at observation
time", which is true of the final instant but does not account for the fleet's earlier observation,
which held two repos named for attribute/hook testing.

The recorded rows bound the question: under `r14-harm` both are **normal** rows
(`["attrtest","1","1","0","0","unpushed"]`, `["hooktest","1","0","1","0","dirty"]`), not `error` rows.
Since r14's guard is a pure key-pattern match, both repos therefore carried **none** of the refused
keys at that moment. That supports the note — but only by inference from row shape, which the
artifact never states, and the repo contents were never recorded.

*Minimal patch* (final file): add

```json
 "fleet_change": {"earlier_run": "live-fleet.json", "present_then_absent": ["attrtest","hooktest"],
                  "evidence": "both carried no error flag under r14-harm, so neither held a refused key then"},
```

or state the same sentence in `note`. **Verdict: partial** (consistent, not proven by the artifact).

### F4 — moderate — `row_count` is silently a lower bound

`row_count: 21` reads as "the fleet has 21 repos", but `list_repos` drops, with no row and no
counter: dot-dirs (`tools/souji-census.sh:1277-1279`), names with newline/tab/CR (`:1280-1282`),
symlinked children (`:1287`), non-directories (`:1288`), children whose `.git` is a symlink
(`:1290-1293`), and children whose `.git` is a **file** (`:1294-1297`, i.e. linked worktrees and
submodules). Only `-d "$g"` (`:1298`) yields a row. Coverage of direct children with a `.git`
directory is all the artifact establishes.

*Minimal patch* (both files): add
`"coverage": "direct children with a .git directory; symlink/.git-file/dot/name-skipped children emit no row (tools/souji-census.sh:1277-1300) — skipped=<n>"`.
Better long-term: have the tool emit a `not-a-repo`/`skipped` row instead of `continue`, so the
count is self-describing. **Verdict: partial.**

### F5 — minor — the recorded command is not runnable

Both `:4` record `TMPDIR=/var/tmp bash <arm>/tools/souji-census.sh --root /home/vgpnk/Projects/shokunin`
with a literal `<arm>` placeholder, no worktree paths and no output redirection; `live-fleet.json:398`
points at `/var/tmp/souji-r16/live/b.sh`, which no longer exists. Reproduction is possible only by
reconstructing each arm from git — which P1/P2 make safe, so this is a documentation defect, not lost
evidence.

*Minimal patch* (both files): per arm add
`"cmd": "bash <worktree-at-rev>/tools/souji-census.sh --root /home/vgpnk/Projects/shokunin > <tsv>"`,
or replace `command` with
`"reproduce": "git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -p <rev>:tools/souji-census.sh | sha256sum"`.
**Verdict: partial.**

### F6 — minor — `live-fleet.json` has no forward pointer

`live-fleet-final.json:362` refers back to the earlier file, but the earlier file's keys
(`root, observed, command, arms, rows_identical_excluding_mtime, r15-baseline, not_run`) carry no
statement that it is superseded, and no `note` at all — a reader landing on it sees an unqualified
`rows_identical_excluding_mtime: true` for an intermediate revision (`cbf688a`).

*Minimal patch* (`live-fleet.json`): add
`"superseded_by": "live-fleet-final.json", "note": "changed arm is an intermediate revision; not comparable to the final pair across time"`.
**Verdict: partial.**

### F7 — minor — "unpaired" mislabels the earlier run

`live-fleet-final.json:362` calls `live-fleet.json` "An earlier unpaired run". That file *is* paired
internally — r14-harm `cc21683` and changed `cbf688a`, both `rc=0`, identical rows. What it lacks is
comparability with the final pair across time, which the rest of the sentence correctly says.

*Minimal patch*: s/An earlier unpaired run (live-fleet.json, cbf688a)/An earlier internally paired run
(live-fleet.json, changed=cbf688a)/. **Verdict: partial.**

---

## Residual risk / verification gaps

- I did not run `souji-census.sh` anywhere (forbidden), so row *values* are unverified per repo; only
  the arm hashes, the config-key absence, and the b410186 parse failure were independently checked.
- The 21 configs were read as exact named files; a key supplied through `include.path` would have
  shown as an `[include]` section and did not. `config.worktree` (only relevant with
  `extensions.worktreeConfig`, itself refused and absent) was not separately enumerated.
- Whether the 21 rows were produced by one process over an unchanging fleet cannot be established
  from the file (F2); the 23→21 row-set change between observations shows the fleet does move.
- F1's preferred patch requires the operator to still have the two 7-column TSVs; if they are gone,
  only the minimal fallback is honest, and the mtime equality claim should be narrowed.

## Commands

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain | head -50 && ls -la census/round-16/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -c census/round-16/live-fleet.json census/round-16/live-fleet-final.json 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'  # json structure dump of both files
import json
for f in ("census/round-16/live-fleet.json","census/round-16/live-fleet-final.json"):
    d=json.load(open(f))
    print("=====",f)
    print("keys:",list(d.keys()))
    for k,v in d.items():
        if k=="arms":
            for a,av in v.items():
                print(f"  arm {a}: keys={list(av.keys())} rc={av.get('result')} rows={av.get('row_count')} sha={av.get('tool_sha256')}")
        else:
            print(f"  {k} = {v!r}")
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'  # row dump per arm, both files
import json
d=json.load(open("census/round-16/live-fleet-final.json"))
for a,av in d["arms"].items():
    print("=====",a,av["rev"],av["result"],av["row_count"])
    for r in av["rows"]:
        print(json.dumps(r))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba census/round-16/live-fleet-final.json | sed -n '1,40p' && echo "-----TAIL" && nl -ba census/round-16/live-fleet-final.json | tail -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba census/round-16/live-fleet.json | sed -n '1,40p' && echo "-----TAIL" && nl -ba census/round-16/live-fleet.json | tail -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "live-fleet\|rows_identical" --include='*.py' --include='*.sh' --include='*.md' . | grep -v '^./census/operator-sweep' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "printf\|ROW_\|TAB\|\\t" tools/souji-census.sh | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in cc21683 cbf688a a31642d b410186 0a70bef; do printf '%s: ' "$r"; git cat-file -p "$r:tools/souji-census.sh" 2>/dev/null | grep -c 'GIT_CONFIG_COUNT\|GIT_NO_LAZY_FETCH' | tr -d '\n'; printf '  cc=%s lazy=%s\n' "$(git cat-file -p "$r:tools/souji-census.sh" 2>/dev/null | grep -c 'GIT_CONFIG_COUNT=0\|GIT_CONFIG_COUNT=1')" "$(git cat-file -p "$r:tools/souji-census.sh" 2>/dev/null | grep -c GIT_NO_LAZY_FETCH)"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in cc21683 cbf688a a31642d b410186 0a70bef; do printf '%s ' "$r"; if git cat-file -e "$r:tools/souji-census.sh" 2>/dev/null; then git cat-file -p "$r:tools/souji-census.sh" | sha256sum | cut -d' ' -f1 | tr -d '\n'; echo; else echo "MISSING"; fi; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== cc21683 hooks/fsmonitor/config ===" && git cat-file -p cc21683:tools/souji-census.sh | grep -n 'hooksPath\|fsmonitor\|GIT_CONFIG\|GIT_NO_LAZY\|core\.fsmonitor\|GIT_TERMINAL\|GIT_OPTIONAL' | head -40; echo "=== 0a70bef same ==="; git cat-file -p 0a70bef:tools/souji-census.sh | grep -n 'hooksPath\|fsmonitor\|GIT_CONFIG\|GIT_NO_LAZY\|core\.fsmonitor' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== a31642d ===" && git cat-file -p a31642d:tools/souji-census.sh | grep -n 'hooksPath\|fsmonitor\|GIT_CONFIG\|GIT_NO_LAZY' | head -20; echo "=== b410186 ==="; git cat-file -p b410186:tools/souji-census.sh | grep -n 'hooksPath\|fsmonitor\|GIT_CONFIG\|GIT_NO_LAZY' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== a31642d git calls ==="; git cat-file -p a31642d:tools/souji-census.sh | grep -n 'git -C\|git --git\|core\.' | head -25; echo; echo "=== b410186 bash -n ==="; git cat-file -p b410186:tools/souji-census.sh | bash -n /dev/stdin; echo "bash_n_rc=$?"; echo "lines=$(git cat-file -p b410186:tools/souji-census.sh | wc -l)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rln "rows_identical_excluding_mtime\|live-fleet-final" .ufo/waves/round-16/ census/round-16/ tests/ 2>/dev/null | head; echo "--- git log for artifacts ---"; git log --oneline -3 -- census/round-16/live-fleet.json census/round-16/live-fleet-final.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'  # repo-set diff, row widths, exact equality
import json
a=json.load(open("census/round-16/live-fleet.json"))
b=json.load(open("census/round-16/live-fleet-final.json"))
ra={r[0] for r in a["arms"]["r14-harm"]["rows"]}
rb={r[0] for r in b["arms"]["r14-harm"]["rows"]}
print("live-fleet.json rows listed:",len(ra),"claimed",a["arms"]["r14-harm"]["row_count"])
print("final rows listed:",len(rb),"claimed",b["arms"]["r14-harm"]["row_count"])
print("present earlier, absent final:",sorted(ra-rb))
print("present final, absent earlier:",sorted(rb-ra))
for f,d in (("live-fleet.json",a),("live-fleet-final.json",b)):
    x=d["arms"]["changed"]["rows"]; y=d["arms"]["r14-harm"]["rows"]
    print(f, "changed==r14-harm exact:", x==y, "lens",len(x),len(y),
          "empty_fields:", sum(1 for r in x if any(c=="" for c in r)))
    print(f, "row widths:", sorted({len(r) for r in x+y}))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== cc21683 guard keys ==="; git cat-file -p cc21683:tools/souji-census.sh | grep -n 'core\.\|extensions\.\|include\.\|case ' | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'  # attrtest/hooktest rows
import json
a=json.load(open("census/round-16/live-fleet.json"))
for arm in a["arms"]:
    print(arm)
    for r in a["arms"][arm]["rows"]:
        if r[0] in ("attrtest","hooktest"): print("   ",json.dumps(r))
EOF
echo "--- existence ---"; for d in attrtest hooktest; do if [ -e "/home/vgpnk/Projects/shokunin/$d" ]; then echo "$d EXISTS"; else echo "$d absent"; fi; done
cd /home/vgpnk/Projects/shokunin && for r in audio-shokunin chousa-shokunin game-dev-2d-shokunin game-dev-3d-shokunin kagi-shokunin kaidoku-shokunin kake-shokunin kama-shokunin kasegi-shokunin kengaku-shokunin kotoba-shokunin kotodama-shokunin kumitate-shokunin lore-shokunin mado-shokunin mori-shokunin revenger-shokunin souji-shokunin tabi-shokunin tameshi-shokunin tsukuroi-shokunin; do f="$r/.git/config"; if [ -f "$f" ]; then h=$(grep -inE 'hookspath|attributesfile|excludesfile|alternaterefscommand|partialclone|worktreeconfig|promisor|^\s*\[include' "$f"); if [ -n "$h" ]; then echo "== $r"; printf '%s\n' "$h"; fi; fi; done; echo "done"
cd /home/vgpnk/Projects/shokunin && for r in audio-shokunin chousa-shokunin game-dev-2d-shokunin game-dev-3d-shokunin kagi-shokunin kaidoku-shokunin kake-shokunin kama-shokunin kasegi-shokunin kengaku-shokunin kotoba-shokunin kotodama-shokunin kumitate-shokunin lore-shokunin mado-shokunin mori-shokunin revenger-shokunin souji-shokunin tabi-shokunin tameshi-shokunin tsukuroi-shokunin; do f="$r/.git/config"; [ -f "$f" ] || { echo "NOCONFIG $r"; continue; }; h=$(grep -inE '^[[:space:]]*\[(include|includeif|filter)|hookspath|attributesfile|excludesfile|alternaterefscommand|partialclone|worktreeconfig|promisor' "$f"); [ -n "$h" ] && { echo "== $r"; printf '%s\n' "$h"; }; done; echo "scan-done"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== diffstat arms ==="; git diff --stat cc21683 0a70bef -- tools/souji-census.sh; echo "=== config read calls in 0a70bef ==="; git cat-file -p 0a70bef:tools/souji-census.sh | grep -n 'config --file\|config --list\|--no-includes\|-C "\$repo" config\|git config' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file -p 0a70bef:tools/souji-census.sh | grep -n 'list_repos() {\|if \[ -L "\$d" \]\|if \[ -f "\$g" \]\|if \[ -d "\$g" \]\|not a repo root'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "cbf688a: $(git log --oneline -1 cbf688a 2>&1)"; echo "reachable-from-HEAD: $(git log --format=%h HEAD | grep -c '^cbf688a$')"; echo "cc21683: $(git log --oneline -1 cc21683 2>&1)"; echo "0a70bef: $(git log --oneline -1 0a70bef 2>&1)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1280,1302p' tools/souji-census.sh | cat -n; echo "=== lesson 18-22 ==="; nl -ba corpus/lessons/round-16.md | sed -n '18,22p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree HEAD census/round-16/; echo "--- attrtest/hooktest line numbers ---"; grep -n 'attrtest\|hooktest' census/round-16/live-fleet.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh; sed -n '170p;1252p' tools/souji-census.sh; grep -n 'header must be the FIRST' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'rows_identical_excluding_mtime\|"observed"\|"command"\|"result"\|"not_run"\|"note"' census/round-16/live-fleet-final.json census/round-16/live-fleet.json
printf '%s\n' /home/vgpnk/Projects/shokunin/*/.git; echo "--- count ---"; printf '%s\n' /home/vgpnk/Projects/shokunin/*/.git | wc -l
for p in AXES.md CORPUS.md bash local reports scripts templates research; do d="/home/vgpnk/Projects/shokunin/$p"; if [ -d "$d" ]; then echo "DIR  $p"; elif [ -e "$d" ]; then echo "FILE $p"; else echo "NONE $p"; fi; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '\.\*) continue\|case "\$base" in\|\*\$'"'"'\\n'"'"'\*.*continue' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -l .ufo/waves/round-16/w2/RevLiveFleetEvidence.md && git status --porcelain .ufo/waves/round-16/w2/RevLiveFleetEvidence.md
```

Reads (non-shell): `census/round-16/live-fleet.json`, `census/round-16/live-fleet-final.json`,
`tools/souji-census.sh:999-1053,1062-1133,1225-1345`; `glob` tool over
`/home/vgpnk/Projects/shokunin/*/.git` (returned no matches, so the fleet's direct-child repo set was
*not* independently enumerated; F4 rests on the tool's `list_repos` branches, not on a live count).

STATUS: ok
