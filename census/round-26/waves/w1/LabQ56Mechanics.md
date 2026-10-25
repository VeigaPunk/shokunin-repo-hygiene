# LabQ56 — `tools/souji-coverage-agreement.py` mechanics + K4 predicate probe

## Status

STATUS: PASS — all three parse layers traced from bytes with pinned line numbers, `--base-rev` vs `--rev` separated by differential runs, and the frozen K4 after-literal (`grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`, rc=0) reproduced at four lane tips and reproduced byte-for-byte at base; six characterisation mutations run in an isolated /var/tmp clone produced four claim-scope ATTACKs (none requires amending a predicate now — all four are satisfiable-before-scoring shapes to record in the round lesson).

Lane revisions observed: base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`; tips seen live during the probe `c594901` → `0c92c2e` → `33e6807` → `9a6e0f13b10cff82c1f6a05059779ed6c06f8a28`. Tool bytes unchanged throughout (`sha256 bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f`, equal to `tool_sha256` in both K4 receipts).

## Evidence

All paths absolute; lane path = `/home/vgpnk/Projects/shokunin/souji-shokunin`.

E1 — base K4 (rev == base-rev), run from the lane:
```
$ python3 -B tools/souji-coverage-agreement.py --root . \
    --rev 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd \
    --base-rev 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd
grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0   (rc=0)
```
Identical stdout, rev, `tool_sha256` and rc as `census/round-26/records/c2-k4-base.tsv` (utc 2026-10-25T17:06:13Z).

E2 — K4 at the four tips (same command, `--rev <tip>`):
```
c594901 / 0c92c2e / 33e6807 / 9a6e0f1:
grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0   (rc=0 each)
```
`census/round-26/records/c2-k4-after.tsv` (rev `33e6807`) and `c2-gate.tsv` (`entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`) exist and match this reproduction. The K4 after-literal is therefore **exactly what the tool prints**; amendment 1's corrected literal (`grounded=9 … kill_tested=7`) is the right one.

E3 — without `--base-rev` the counts line has four fields (tip `0eca7c8`): `grounded=7 mapped=7 dangling=0 mismatches=0` rc=0.

E4 — grounded set at base (7) and at tip (9), dumped via the tool's own functions (`entry_grounds`, `knowledge_tree`):
```
base: count-objects-garbage-readings-r25[F2] count-objects-linked-worktree-garbage[F2]
      git-repo-structure-common-dir[F2] git-repo-structure-readonly[F2]
      quarantine-origin-record-fields-r24[F4] quarantine-staging-no-copy-r23[F4]
      repo-size-census-readonly[F2]
tip : the same 7 + git-auto-maintenance-trigger-set[F1] + git-auto-maintenance-trigger-set-r23[F1]
```
Tip: 17 distinct `knowledge/<name>` names in map rows, 9 grounded, 8 named-but-ungrounded: dupe-finders-detect-then-act.md, git-auto-maintenance-prunes-worktrees.md, git-grace-periods-and-expire-to.md, jj-colocation-receipts.md, obsidian-ledger.tsv, process-residue-observations.md, quarantine-same-filesystem-rename.md, trash-spec-restorable-quarantine.md.

E5 — per-`F<k>` row pooling at tip `c594901` (tool's own `map_rows`/`GROUND_TOKEN`/`CODE_SPAN`/`KNOWLEDGE_PATH`):
```
F1 rows=[39, 216]  union=[…prunes-worktrees, …trigger-set, …trigger-set-r23, …grace-periods, jj-colocation-receipts]
F2 rows=[40, 68, 217, 517, 544]
F3 rows=[41]   F4 rows=[42]   F5 rows=[242, 274]
```
`GROUND_TOKEN` is what makes the `F1-jj` row (README:216) count as k=1.

E6 — refusals (isolated clone, V6): short sha `--rev 0c92c2e` → stderr `--rev must be a full 40-hex commit id` rc=2; `--base-rev 0c92c2e` → same shape rc=2; tree object as `--rev` → `rev-parse --verify … expected commit type, but the object dereferences to tree type` rc=2; missing `--root` → `argv: the following arguments are required: --root` rc=2.

E7 — instrument edge cases in a disposable clone (`/var/tmp/souji-r26-LabQ56Mechanics`, `git init` + `fetch` of the lane master, `git -C "$D" rev-parse --show-toplevel` verified = `$D`, removed after use). Each variant is a scratch commit; base-rev held at `0eca7c8`:
```
V1 stub entry      grounded=10 mapped=10 dangling=0 mismatches=0 kill_tested=7 kill_violations=0  rc=0
V2 F1-jj row only  grounded=9  mapped=9  dangling=0 mismatches=0 kill_tested=7 kill_violations=0  rc=0
V3 no row names    grounded=9  mapped=7  dangling=0 mismatches=2 kill_tested=7 kill_violations=0  rc=1
V4 nested entry    grounded=9  mapped=9  dangling=0 mismatches=0 kill_tested=7 kill_violations=0  rc=0
V5 re-ground F2→F1 grounded=9  mapped=8  dangling=0 mismatches=1 kill_tested=7 kill_violations=1  rc=1
V8 delete base entry grounded=8 mapped=8 dangling=2 mismatches=2 kill_tested=7 kill_violations=1 rc=1
V3 lines: MISMATCH MISSING-FROM-MAP …trigger-set-r23.md ground=F1 map_rows_F1=2 (and …trigger-set.md)
V5 lines: MISMATCH KILL-RULE …count-objects-garbage-readings-r25.md base_grounds=F2 lost=F2 rev_grounds=F1
          MISMATCH MISSING-FROM-MAP … same entry ground=F1 map_rows_F1=2
V8 lines: 2× MISMATCH DANGLING-MAP-PATH …repo-size-census-readonly.md (README:517, README:544)
          MISMATCH KILL-RULE … same base_grounds=F2 rev=absent
```
V7 (worktree dirt): `ground: F1`→`ground: F9` edited in the clone's working tree only, uncommitted; `--rev HEAD` still printed `grounded=9 mapped=9 …` — committed bytes only, as the docstring claims.

## Findings

**M1 — where `ground:` lines come from.** `knowledge_tree` runs a non-recursive `git ls-tree` (`tools/souji-coverage-agreement.py:61`):
```python
    for rec in filter(None, git(root, "ls-tree", "-z", rev, "--", f"{KNOWLEDGE}/").split(b"\0")):
        meta, _, path = rec.decode("utf-8", "surrogateescape").partition("\t")
        out[path.rsplit("/", 1)[-1]] = meta.split()[1]
```
`entry_grounds` keeps only `.md` blobs (`:107`) and parses the blob at `<rev>` via `git show --no-textconv` (`:109`); `front_grounds` (`:92-101`) scans from line 1, **stops at the first line starting `# `** (`:95`), and matches `FRONT_GROUND = re.compile(r"^ground:\s*F([0-9]+)")` (`:34`, use at `:97`). So: no YAML fence required, no anchor/`source` requirement, tab allowed after the colon, and a `## …` heading does not stop the scan. "Grounded" = count of direct-child `.md` blobs with ≥1 such line before their first H1.

**M2 — how map rows and entry names are paired.** `map_rows` (`:74-89`) opens a table on the first line whose left-strip starts `|` (`:78`), accepts it as a coverage map iff the header has ≥3 cells, cell0 `.lower() == "ground"` and cell2 `.lower().startswith("entries")` (`:84-85`); it skips separator rows (`:87`) and yields `(lineno, row[0], row[2])` (`:89`). `cells` (`:67-72`) splits on unescaped `|` (`CELL_SPLIT = r"(?<!\\)\|"`, `:35`), so `\|` inside a cell (README:40) does not split. In `measure`:
```python
141:    for lineno, ground, entries in map_rows(show(root, rev, README)):
142:        tok = GROUND_TOKEN.match(ground)          # GROUND_TOKEN = r"^F([0-9]+)(?=[ \-]|$)"  (:33)
144:        for span in CODE_SPAN.findall(entries):    # CODE_SPAN = r"`([^`\n]+)`"              (:37)
145:            m = KNOWLEDGE_PATH.search(span.strip())# r"(?:^|/)knowledge/([^/\s]+)$"          (:38)
146:            if m and m.group(1) not in names:
147:                names.append(m.group(1))
151:        if tok:
152:            k = int(tok.group(1))
153:            rows_by_k[k] = rows_by_k.get(k, 0) + 1
154:            mapped_by_k.setdefault(k, set()).update(names)
155:    dangling = len(mismatches)
156:    grounds = entry_grounds(root, rev, tree)
159:        missing = [k for k in sorted(ks) if name not in mapped_by_k.get(k, set())]
160:        mapped += not missing
```
A row's `entries` cell contributes a name only when the backticked span **ends** in `knowledge/<name>`; `mapped_by_k[k]` is the union over *every* qualifying row in the whole README (`:154`), and an entry is mapped iff, for **each** k in its ground set, its filename is in that union (`:159-160`). Not checked: that the row is the canonical F1 row, the row's status text, that the entry actually cites the row's sources, or that a map-named file carries a `ground:` line at all (8 map-named files carry none, E4).

**M3 — `--base-rev` vs `--rev`.** Both are validated identically (`FULL_REV` 40-hex at `:32`, then `rev-parse --verify --quiet <sha>^{commit}` at `:180-184`, called at `:193` and `:195`), and any refusal exits 2. `--rev` selects the entire measurement (tree, README, entry bytes). `--base-rev` is read **only** by `kill_rule` (`:166-170`): it recomputes `entry_grounds` over the base tree (`:118-121`) and emits one row per base-grounded name that is not a blob at rev (`rev=absent|tree`, `:125-126`) or whose base k-set is not a subset of its rev k-set (`lost=…`, `:127-131`); `kill_tested` = |base-grounded| (`:132`), `kill_violations` = |rows| (`:170`). Kill rows are appended to the printed `MISMATCH` rows (`:168`) **after** `counts["mismatches"]` was fixed at `:164`, so `mismatches=` counts map-side rows only (V5 proves it: two MISMATCH lines, `mismatches=1`); exit is `0 iff counts["mismatches"]==0 and kill_violations==0` (`:203`). New entries are never kill-tested — `kill_tested` stays 7 no matter how many entries the tip grounds (V1: grounded=10, kill_tested=7).

**M4 — the K4 predicate is verified, not inferred.** `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0` with rc=0 at `c594901`, `0c92c2e`, `33e6807` and `9a6e0f1` (E2), matching the committed `c2-k4-after.tsv`; base prints the 7/7 line of `c2-k4-base.tsv` (E1). The delta is exactly the two admitted entries (`ground:` at `corpus/knowledge/git-auto-maintenance-trigger-set.md:6` and `…-trigger-set-r23.md:8`) named at `corpus/README.md:39`; `kill_tested` stays 7 because only base-grounded names are tested.

## Attack log

ATTACK A26-K4-1 (severity: high; satisfiable-before-scoring, no predicate change requested). **K4 is met by hollow entries.** A 66-byte `corpus/knowledge/zz-stub.md` whose only content is `ground: F1 — …`, appended to README:39, yields `grounded=10 mapped=10 … kill_tested=7 kill_violations=0`, rc=0 (V1). The instrument measures map↔ground bookkeeping only; entry substance, source rows, Gate locators and registry rows are invisible to it, and the kill rule cannot see new entries. K4 alone cannot attest the C2 claim — only K2/K3 do. Location: `tools/souji-coverage-agreement.py:103-112,135-160`; scratch V1.

ATTACK A26-K4-2 (severity: high; same class). **`F1-jj` satisfies `F1`.** `GROUND_TOKEN` accepts `F1-jj …` as k=1 (`:33`; README:216). Moving both admitted entries off the canonical F1 row and naming them only in the F1-jj edge-class row still prints `grounded=9 mapped=9`, rc=0 (V2). The frozen after-condition "the 2 new F1 entries named in the README F1 row's entries column" is therefore *not* what the instrument enforces: it enforces "named in any row whose ground cell starts `F<k>`", and F1's name-set is polluted by an edge-class row about jj colocation. Location: `:33,:142-154`; README:39 vs README:216.

ATTACK A26-K4-3 (severity: medium). **Pooling is document-wide and one-directional.** Names are unioned from every qualifying table in README.md, including obsolete round-scoped tables (README:68 r13-era, :517, :544), and `mapped` never consults the reverse direction: 8 map-named files without a `ground:` line are silently outside `grounded` (E4). A name sitting only in a superseded table currently counts as mapped; the printed `map_rows_F<k>=N` (V3) is the only hint of how many tables participated.

ATTACK A26-K4-4 (severity: low-medium). **Nested knowledge entries are invisible.** `git ls-tree` without `-r` (`:61`) keys a subdirectory as a `tree` entry, dropped by the blob filter (`:107`). `corpus/knowledge/sub/zz-sub.md` with `ground: F1` leaves `grounded=9` (V4). A base-grounded entry *moved* into a subdirectory would surface only as a `KILL-RULE … rev=tree` row — i.e. only when `--base-rev` is supplied.

Disclosed harness detail: all mutations were applied in the disposable `/var/tmp/souji-r26-LabQ56Mechanics` clone only (V3's README truncation used `sed -i` in that clone); no lane file outside `w1/LabQ56Mechanics.md` was written, no lane git state touched. Scratch removed (`/var/tmp/souji-r26-LabQ56Mechanics` absent at end). No tools installed or upgraded this run (nothing was needed).

Blocker: none. Out-of-scope observation: the lane tip advanced three times mid-probe by concurrent C2/C3 landings; K4's printed line is invariant across all four tips, so the receipt pair (base 0eca7c8, after 33e6807) is stable under those landings.
