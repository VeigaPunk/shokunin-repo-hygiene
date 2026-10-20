STATUS: DONE — three receipt tools reviewed at pinned bytes; C3(a)/(b) live sites located (roots 3+2, unpushed 8 live/3 dead), one shared-array spelling per file delivered, and 522 lines of unreachable guard code in `souji-quarantine.sh` proven dead (the C3(a)/(b) lines named there are inert).

# SimplifyJjRoots — duplicate receipt authority in souji-verify / souji-vault-verify / souji-quarantine

Seat: simplifier, WAVE 1, round 17. No subagent dispatch. Advisory only: **no lane file was edited by
this seat**; the only file I wrote is this report.

## Axes

1. **Correctness of C3** — every root/unpushed site that can decide a receipt uses only
   `refs/heads|refs/tags|refs/remotes` as roots, and seeds `refs/jj/keep/*` when counting unpushed
   touching commits.
2. **Weight** — one spelling of "durable roots" and one of "unpushed heads" per file; no second
   convention, no shared library, no duplicate authority left able to answer.
3. **Provability** — each retained/removed line backed by a read-only git probe on real lane data,
   not by intent.

## Snapshot (these are the bytes reviewed)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
5fa6017ddcae9f6bd4412df44765f6360cb16294
16b42a6d0e89ec04e9c09ee3fa421893d6f7982cdc4bc06c10314784afdd9ded  tools/souji-verify.sh    (close; was 9adb1764… at F1/F2 census)
be3f60bba7dc2aac70e5c2434e5b9de0ccc6743abaef2f305732e4f0a2bf40ee  tools/souji-vault-verify.sh (close; was 546d8600…, then d3582d3a…)
df4075112c36bae804b98766c4eb66b0e5b2b80b76d7333475ede27b06b168c4  tools/souji-quarantine.sh (unchanged throughout)
```

**Both `souji-verify.sh` and `souji-vault-verify.sh` are being edited concurrently by the C3 lane
while this seat reads them** (`git status --porcelain -- tools/` → `M tools/souji-verify.sh`,
`M tools/souji-vault-verify.sh`, `M tools/souji-seat-audit.py`; `git diff --stat` at close →
`2 files changed, 73 insertions(+), 3 deletions(-)`). F1/F2 quote the offsets and bytes at the
**census snapshot** (verify `9adb1764…`, vault `d3582d3a…`) and both corrections are keyed by exact
text so they still apply; **F7 records what had actually landed at close and is the state to act on.**
No write by this seat reached any tool file — every `sha256sum` change above predates my report write
and matches `git diff` hunks authored after my reads.

Method note: this seat has **no `lsp` device mounted** (tool set is read/edit/bash/eval/glob/grep/task/
wait/web_search/write plus the REA MCP server; no `lsp` path responds), so deletion candidates were
proven with a parser-based reference census over each exact named file (function definitions + body
identifier graph + dispatch roots) and targeted `grep -n` on named files — recorded here as the
literal fallback, never presented as semantic call-graph proof. The census is conservative: identifiers
inside comments/strings count as references, so it can only *under*-report dead functions.

## F1 — C3(a) durable roots: 3 live all-refs lists + 2 shadowed `--not --all`

Live (last-definition) roots lists, one per tool:

| file | line | current text (exact) |
|---|---|---|
| souji-verify.sh | 809 | `    if ! refs=$(git -C "$owner" for-each-ref --format='%(objectname)' 2>/dev/null); then` |
| souji-vault-verify.sh | 1027 | same text |
| souji-quarantine.sh | 1069 | same text — **unreachable** (see F4) |

Shadowed duplicates (defined, then redefined later; the first body can never run because every caller
is invoked after the whole file has been sourced — `scan_worktrees`/`evaluate_path` run only in the
tail dispatch):

| file | first def | live override | current text (exact) |
|---|---|---|---|
| souji-verify.sh | 333–382 | 1004–1023 | `    if ! uniq=$(git -C "$owner" log --oneline "$head" --not --all 2>/dev/null \| wc -l); then` (:351; **at close :384, still `--not --all`**) |
| souji-vault-verify.sh | 499 | 1192 | same text — **at close :554, already respelled `--not --branches --tags --remotes`** |
| souji-quarantine.sh | — (no base copy) | — | — |

Close-state offsets for the live all-refs table above: verify `:809 → :842` (still all-refs),
vault `:1027 → :1034` (still all-refs), quarantine `:1069` (unchanged, unreachable). So at close the
C3(a) inversion is: **vault fixed the shadowed base copy and left the live copy broken; verify fixed
neither.**

`--not --all` is wrong on two counts for (a): it roots at `refs/jj/*`/`refs/stash` **and** at `HEAD`
(`git rev-list` documents `--all` as "all the refs in refs/, along with HEAD").

Empirical proof on this lane (8 `refs/jj` refs, 0 tags, 0 stash, 11 refs total):

```
--- ref counts by prefix        --- all-refs count        --- durable patterns only
1 refs/heads                    11                       3
8 refs/jj                       (for-each-ref, no patt.) contains refs/jj|stash? 0
2 refs/remotes
--- per keep ref: unique vs ALL roots vs durable roots
0254661427 uniqueAll=0 uniqueDurable=1     c46eabf80f uniqueAll=0 uniqueDurable=0
1e0d8d1644 uniqueAll=0 uniqueDurable=1     dcc1512e2a uniqueAll=0 uniqueDurable=1
41ab059d7d uniqueAll=0 uniqueDurable=1     dd2e322686 uniqueAll=0 uniqueDurable=1
5fa6017ddc uniqueAll=0 uniqueDurable=0     719154dc9d uniqueAll=0 uniqueDurable=1
```

i.e. **all 8** keep-held heads are `unique=0` against `--not --all` (⇒ today's code would print
`SAFE(metadata-prune)` for any absent-worktree registration pointing at one), while **6 of 8** are
`unique=1` against `refs/heads refs/tags refs/remotes` — exactly the claim's "6 keep-only commits".
The two `uniqueDurable=0` refs (`5fa6017d`, `c46eabf8`) are also reachable from a durable ref, so the
restricted roots do not over-refuse them.

Replacement (primary, see F3 — one array, one convention):

```
-    if ! refs=$(git -C "$owner" for-each-ref --format='%(objectname)' 2>/dev/null); then
-      R_EVIDENCE="durable-refs-unverifiable"; return
-    fi
-    if [ -n "$refs" ]; then mapfile -t roots <<< "$refs"; fi
-    if ! uniq=$(git -C "$owner" rev-list --count "$head" --not "${roots[@]}" -- 2>/dev/null); then
+    if ! uniq=$(git -C "$owner" rev-list --count "$head" --not "${DURABLE_REFS[@]}" -- 2>/dev/null); then
       R_EVIDENCE="worktree-ancestry-unverifiable"; return
```

and in the same function delete ` -a roots=()` and `refs` from its `local` line:
`  local target=$1 meta=$2 owner head branch unp uniq dirty refs status` → `… dirty status`.

Shadowed-base line (one token, keeps the composition record honest even though it is unreachable):

```
-    if ! uniq=$(git -C "$owner" log --oneline "$head" --not --all 2>/dev/null | wc -l); then
+    if ! uniq=$(git -C "$owner" log --oneline "$head" --not "${DURABLE_REFS[@]}" 2>/dev/null | wc -l); then
```

**Fallback spelling** if L1 prefers to keep the distinct `durable-refs-unverifiable` diagnostic
(identical verdicts, one extra failure-mode string):

```
DURABLE_ROOTS=(refs/heads refs/tags refs/remotes)      # for-each-ref patterns
...
    if ! refs=$(git -C "$owner" for-each-ref --format='%(objectname)' "${DURABLE_ROOTS[@]}" 2>/dev/null); then
```
with the shadowed line spelled `--not --branches --tags --remotes` (patterns are not revs, so the
patterns array cannot be reused there — that asymmetry is the only cost of the fallback).

Tradeoff recorded: the primary spelling cannot distinguish "refs unreadable" from "ancestry
unreadable"; both remain `NOT-SAFE` with receipt `none`, differing only in the evidence string, and
**no selftest asserts that token** (`grep -n 'durable-refs-unverifiable'` → only the three
definitions, no `st_case`). Fails safe if the array is ever empty (`--not` excludes nothing).

## F2 — C3(b) unpushed-touching: 8 live sites, 3 dead

Live sites (all eight take the positive set `--branches` before `--not --remotes`):

| file | line | exact current text |
|---|---|---|
| verify | 234 | `  if [ "$(git -C "$repo" log --branches --not --remotes --oneline -- "$target" 2>/dev/null \| wc -l)" != "0" ]; then` |
| verify | 321 | `  unpushed=$(git -C "$target" log --branches --not --remotes --oneline 2>/dev/null \| wc -l \|\| true)` |
| verify | 671 | `  if ! touching=$(git -C "$repo" log --format=%H HEAD --branches --not --remotes -- "$target" 2>/dev/null); then` |
| verify | 952 | `      if ! touching=$(git -C "$CREPO" log --format=%H HEAD --branches --not --remotes -- "$REL" 2>/dev/null) \|\| [ -n "$touching" ]; then` |
| vault | 442 | mirrors verify:234 |
| vault | 517 | mirrors verify:321 (`"$target"`) |
| vault | 889 | mirrors verify:671 |
| vault | 1170 | mirrors verify:952 |
| quarantine | 299 | `        if unpushed_n=$(git -C "$CREPO" log --branches --not --remotes --oneline -- "$REL" 2>/dev/null \| wc -l); then` |

Dead sites (inside quarantine's unreachable block, F4): `:931`, `:1251`.

Close state (verify `16b42a6d`, vault `be3f60bb`): **all four vault sites now carry the seed**
(`:443`, `:520`, `:896`, `:1182`, each followed by a helper-driven `jj-keep-unpushed` NOTE), while
**all four verify sites remain unseeded** (`:267`, `:354`, `:704`, `:985`) and quarantine `:299` is
unchanged. Probe on the real phantom path `tests/vault/vadv54-run/p/p6repo/one.txt`:
`git log --branches --glob='refs/jj/keep/*' --not --remotes --oneline -- <p>` → **4** (the landed
spelling) vs `git log --branches --not --remotes --oneline -- <p>` → **0** (verify, still unseeded).

Replacement, uniform — insert `"${UNPUSHED_HEADS[@]}"` where `--branches` sits:

```
-  if [ "$(git -C "$repo" log --branches --not --remotes --oneline -- "$target" 2>/dev/null | wc -l)" != "0" ]; then
+  if [ "$(git -C "$repo" log "${UNPUSHED_HEADS[@]}" --not --remotes --oneline -- "$target" 2>/dev/null | wc -l)" != "0" ]; then
-  if ! touching=$(git -C "$repo" log --format=%H HEAD --branches --not --remotes -- "$target" 2>/dev/null); then
+  if ! touching=$(git -C "$repo" log --format=%H HEAD "${UNPUSHED_HEADS[@]}" --not --remotes -- "$target" 2>/dev/null); then
```
(`--branches` and the quoted glob both expand as *positive* revs; `--not` still governs only
`--remotes`. `git log` without a matching glob exits 0, proven below.)

Proof the live change is load-bearing on real lane data (phantom-deletion paths from the 4 keep-only
commits — `0254661`, `1e0d8d1`, `41ab059`, `719154d` each `D tests/vault/vadv54-run/p/p6repo/one.txt`
and `…/inner/keep.txt`):

```
--- current touching check (no keep)     0
--- C3 touching check (+keep)            4
--- same for inner/keep.txt              0   then 4
--- glob-only (no --branches)            4
--- no-match glob must not error: exit=0, 0 lines
--- repo-root: branches-not-remotes=0 ; branches+keep-not-remotes=6
--- array spelling: UNPUSHED_HEADS=(--branches '--glob=refs/jj/keep/*') → 6
--- DURABLE_REFS=(--branches --tags --remotes) ; rev-list --count HEAD --not "${DURABLE_REFS[@]}" → 0
--- rev-list --count <keep-only-oid> --not --branches --tags --remotes --  → 1
--- bash -n on the proposed snippets → SYNTAX-OK
```

This matches the disclosed conservative effect (C3: hidden rewritten predecessors that touched the
target also refuse). Note `--glob='refs/jj/keep/*'` must be **quoted**: unquoted, bash pathname
expansion would fire on the word if a path literally beginning `--glob=refs/jj/keep/` existed.

Do **not** touch the two branch-scoped checks (`verify:338/:799`, `vault:534/:1017`,
`quarantine:1059`): they are `"$branch" --not --remotes`, and seeding keep refs there would *lower*
the unpushed count (wrong direction). Keeping them byte-identical is correct, not an omission.

## F3 — smallest shared spelling: two arrays per file, no library, no helper

Per the advisory, keep the files independent (no new sourced file) and name each authority once.
Primary form (rev-list/`--not` compatible, also usable by the shadowed log line):

Insert once per file, directly after the globals block:

**`tools/souji-verify.sh`** — after `declare -A WT_MAP=()` (line 85 at the census snapshot, 94 at close;
anchor on the text):
```sh
# r17 C3: durable-receipt revsets. Roots of trust are heads/tags/remotes only
# (never refs/jj/*, refs/stash or HEAD). jj keep refs are hidden rewritten
# predecessors: they never establish a receipt, but a commit only they hold
# still counts as unpushed work when it touches the target (conservative).
DURABLE_REFS=(--branches --tags --remotes)
UNPUSHED_HEADS=(--branches '--glob=refs/jj/keep/*')
```

**`tools/souji-vault-verify.sh`** — after `declare -A WT_MAP=()` (now line 85; text anchor:
`LEDGER_ROWS=()` follows it): same six lines, prefixed `# r17 C3 (same as tools/souji-verify.sh): …`.

**`tools/souji-quarantine.sh`** — after `TARGETS=()` / `STALE_DAYS=…` (lines 166–167):
```sh
# r17 C3: durable roots as in tools/souji-verify.sh. Only UNPUSHED_HEADS is
# live here: receipt re-derivation delegates to $VERIFY_BIN, and the inlined
# evaluate_* guard block below is unreachable (see round-17 SimplifyJjRoots).
UNPUSHED_HEADS=(--branches '--glob=refs/jj/keep/*')
```
(add `DURABLE_REFS` too only if L1 retains the dead block instead of deleting it).

Diff accounting vs today: verify 1 declaration (+1 array the fallback would also need) and 7 one-line
edits of which 1 is dead; vault the same 7; quarantine 1 declaration + 1 line. No per-site glob literal
is repeated (zero at present → one), which is the whole point: 11 copies of the ref policy collapse to
one per file.

**Rejected moves (and why):**
- *Extract a shared `receipt-refs.sh` sourced by all three*: forbidden by the advisory (files stay
  independent) and would add a fourth authority to keep in sync across the guard snapshot copies.
- *`jj_keep_unpushed()` helper now present at `souji-vault-verify.sh:412+` (sibling edit)*: it runs
  **two** history walks plus a `for-each-ref | grep -q` per call site to recover information the single
  seeded revset already has, and at `d3582d3a…` it has **no call sites** (15 lines of dead code).
  If the `jj-keep-unpushed` disclosure token is wanted, get it for free with a static note on the
  existing refusal path — `NOTES+=("pushed=unpushed-commits-touching(incl refs/jj/keep) intro=…")` —
  which is truthful (that refusal *does* include keep heads), costs zero git calls, and keeps one
  convention. Otherwise delete the helper.
- *Replacing the roots check with `log --oneline … | wc -l`* to match the spec's prose*: `rev-list
  --count` is the existing live spelling; changing it would create a third convention for nothing.

## F4 — Duplicate authority: 522 unreachable lines in quarantine, 267 in verify, 224 in vault

Proven with the reference census (defs + body identifier graph + tail-dispatch roots
`{usage,usage_err,run_selftest,scan_worktrees,evaluate_path,emit_result[,load_ledger]}` /
`{usage,usage_err,run_mode,run_selftest}`), then spot-confirmed by `grep -n` on each file.

**`souji-quarantine.sh` (df407511) — headline.** 20 of the file's 51 function definitions are
unreachable — **522 of 1677 lines (31%)** — from `is_hex64` (702) through `evaluate_worktree`
(1303–1322), with live helpers (`content_digest`, `q_special_*`, `q_stage2_fail`, `s18_path_ok`,
`s18_scope_ok`) interleaved in that range. The dead set includes:
`s18_evaluate_worktree_one` 1049–1088, `evaluate_path` 1089–1265, `scan_worktrees` 1266–1289,
`_wt_record` 1290–1302, `evaluate_worktree` 1303–1322, and everything only they reach
(`try_pushed`, `try_stale`, `count_live_refs`, `try_obsidian`, `try_ledger`, `load_ledger`,
`s18_*` helpers). Confirmed: `evaluate_path` has **no call site** (`grep -n evaluate_path` → def at
1089 and `s18_evaluate_path "$raw"` at 1107 only); `try_pushed`/`try_stale` call sites exist only at
916/1027 and 940/1017 inside the island.

Consequence for C3: the claim's quarantine lines `:1069–1073` (roots), `:931`, `:1251` (touching) are
**inert**. Editing them satisfies the letter of the claim but adds weight to code that cannot run;
the tool's header says receipt authority is delegated ("invoked as a child … never re-implemented
here", `:1–6`, `VERIFY_BIN` at `:158`). Smallest correct move: delete the island (and its `NOTES`-style
leftovers), or at minimum record that the C3 edits there are cosmetic. Deleting it also removes the
only duplicate of `try_pushed`/`try_stale`/`count_live_refs` in the tool — no behaviour change is
possible because none is reachable.

**`souji-verify.sh` (9adb1764).** Two classes:
1. Ten names are defined twice; the **first** definition is dead by shadowing (last def wins for every
   caller, all of which run after load): `file_sha` 153, `dir_digest` 155, `ledger_lines` 167,
   `count_live_refs` 197, `try_pushed` 219, `try_obsidian` 247, `try_stale` 297, `evaluate_worktree`
   333, `_wt_record` 436, `scan_worktrees` 445 — **228 lines**, including the base `--not --all`
   evaluator at 333–382.
2. A genuinely unreachable last-def island: `load_ledger` 566–577 + `try_ledger` 615–639 (**39 lines**).
   `try_ledger` calls `s18_try_ledger` and `finish_mismatch`, which **do not exist in this file**
   (`grep -c` → 2 references, 0 definitions) — it is a vault leftover that would abort if ever called.

**`souji-vault-verify.sh` (d3582d3a).** Same shape: ten shadowed first definitions (**192 lines**,
   incl. base `evaluate_worktree` 499–548 at the census snapshot, 530–579 now) and an unreachable
   island `ledger_lines` + `try_obsidian` (**32 lines**, they only call each other; 771/780 at the
   census snapshot, 801/810 at `d3582d3a` — the file grew while this seat was reading it). Plus the
   new, currently uncalled `jj_keep_unpushed` (15 lines, see F3).

These are candidates, not actions: the files are explicitly presented as compositions ("round-2 base +
S08 repairs with the S18 shared hardening layer inlined after it", verify `:481–486`), so removing the
base half is a provenance-adjacent decision for L1, not a simplifier edit. The safe, mechanical cut
is the *dead islands* (39 + 32 + 522 = 593 lines) and the `jj_keep_unpushed` helper; the shadowed
base halves (228 + 192) should be either kept as the composition record with their root sets corrected
(F1) or removed wholesale in a dedicated round.

## F5 — Routed wording/spec deltas

1. `tools/souji-verify.spec.md:29–30` still specifies `--not --all` as the binding rule for
   `SAFE(metadata-prune)`. It is binding, so C3 must change it in the same change:
   ```
   -   - dir absent AND unique commits = 0 (`git -C <owner> log --oneline
   -     <HEAD> --not --all | wc -l`) → `SAFE(metadata-prune)`
   +   - dir absent AND unique commits = 0 (`git -C <owner> rev-list --count
   +     <HEAD> --not --branches --tags --remotes`) → `SAFE(metadata-prune)`; roots of
   +     trust are heads/tags/remotes only (never refs/jj/*, refs/stash or HEAD),
   +     and unpushed-touching checks also seed `--glob=refs/jj/keep/*`
   ```
   (Keep the `log … | wc -l` phrasing instead if the spec should mirror prose rather than the
   implementation; either way `--all` must go.)
2. `tools/souji-verify.sh:54–57` (rule D-b rationale) states the historical measurement
   "0 unique commits vs `--not --all`". Once F1 lands this is history, not the live rule. Leave it as
   provenance (it explains *why* branch-unpushed precedes the shortcut) or append
   "(`--not --all` at the time; r17 restricts roots to durable refs)".
3. `tools/souji-vault-verify.sh:41–51` (sibling's new header note, at `d3582d3a`) **claims the change
   is done** ("Every ancestry exclusion that used to be `--not --all` now roots only at durable ref
   namespaces") while `:547` still reads `--not --all` and `:1027` still lists all refs. Half-landed
   docs are worse than none; either land F1/F3 in the same commit or mark the note as the target state.
4. Drift risk: the inlined layer's historical source copies still carry the old roots —
   `tools/souji-guard.r9-s18.sh:275` (all-refs `for-each-ref`), `:166`, `:411` (unseeded touching
   checks); `tools/souji-verify.r9-s18.sh` (2 × `--not --all`), `tools/souji-vault-verify.r9-s18.sh`
   (1 ×). They are historical snapshots — do not edit — but note that any future re-inlining from them
   regresses C3 silently. Also stated in the sibling's own helper comment: plain repos must stay
   byte-identical; the array spelling preserves that (no `refs/jj` ⇒ glob matches nothing ⇒ identical
   revset, proven by the no-match probe above).

## F7 — Observed close state, and what the helper route costs

`grep -n` at close (exact):

```
16b42a6d… verify      :267 :354 :704 :985 unseeded   | :384 --not --all | :842 all-refs for-each-ref
                      helpers jj_has_keep:232 jj_keep_touching:236 jj_repo_keep_unpushed:246
                      → no call sites (18 lines, currently dead)
be3f60bb… vault       :443 :520 :896 :1182 seeded    | :554 --not --branches --tags --remotes
                      | :1034 all-refs for-each-ref  | jj_keep_unpushed:421, 4 call sites (:445 :530 :901 :1184)
df407511… quarantine  unchanged (no C3 work; its named sites are unreachable, F4)
```

Consequences to act on:

1. **C3(b) is half-landed.** Vault is complete (4/4); verify is 0/4 and its three helpers are dead.
   The claim's counting command cannot pass on verify's bytes.
2. **C3(a) is landed in the wrong copy of vault.** `:554` is the *shadowed base* evaluator; the live
   authority is `evaluate_worktree` → `s18_evaluate_worktree_one`, whose all-refs `for-each-ref` at
   `:1034` is untouched. Until `:1034` (and verify `:842`) is restricted, an absent-worktree head
   held only by a keep ref still prints `SAFE(metadata-prune)` — the probe proves it: every one of the
   8 keep refs is `unique=0` against `--all`, 6 of 8 are `unique=1` against durable roots.
3. **Weight of the helper route vs one array.** Vault's landed route costs +43 lines, one new function,
   a new evidence token, and three extra git invocations per refusal (`for-each-ref` + two `log`
   walks, one of which recomputes a count the caller already held at `:443`/`:520`/`:896`/`:1182`).
   The array route seeds each site with one token and costs zero processes. Both satisfy (b); the
   difference is pure weight and one more convention to keep in sync across three files.
   If the disclosure token is kept, note that `jj_keep_unpushed` is **repo-scoped, not target-scoped**:
   at `:529–531` it can print `jj-keep-unpushed` on a row refused by a branch commit merely because
   the repo holds unrelated keep-only commits. Either pass `-- "$target"` there too, or drop the token
   and disclose in the knowledge entry/header (C3(c)/(d)) as the claim already requires.
4. **Post-landing invariants** (run once, lane read-only; today's values in comments):
   ```
   git -C <lane> log --branches --glob='refs/jj/keep/*' --not --remotes --oneline -- \
        tests/vault/vadv54-run/p/p6repo/one.txt | wc -l          # 4  (unseeded spelling gives 0)
   git -C <lane> rev-list --count 0254661427750f47e04f20864c5091cfc74e2e0e \
        --not --branches --tags --remotes --                     # 1  (all-refs spelling gives 0)
   git -C <lane> for-each-ref --format='%(objectname)' refs/heads refs/tags refs/remotes | wc -l
                                                                 # 3, and never refs/jj/* or refs/stash
   ```
   plus the four selftest `metadata-prune` rows (heads are `c2`, reachable from
   `refs/remotes/origin/master`), which stay green under either spelling.

## Preserved contract (what must not move)

- Verdict/receipt vocabulary unchanged: `SAFE(metadata-prune)`, `NOT-SAFE(unpushed-branch)`,
  `NOT-SAFE(dirty)`, `NOT-SAFE(none)`, `unpushed`/`dirty` repo-root receipts,
  `registration-conflict`, and quarantine's `SKIPPED metadata-prune`.
- Selftest rows that pin metadata-prune stay green by construction: `verify:1139` F4 head `c2` and
  `:1143` E3 head `c2` are both reachable from `refs/remotes/origin/master` set at `:1118–1120`;
  the same fixture shape is used in vault (`updates at 1323–1325`, row `:1454`). `git log/rev-list`
  treat an annotated tag object supplied as an OID and one reached via `--tags` identically (peeled),
  so the roots restriction is equivalent to the OID list for tags.
- Branch-scoped unpushed checks stay branch-scoped (F2).
- Plain (non-jj) repositories: byte-identical output; the only observable additions are (i) the
  C3-intended refusals where a keep-only commit touches the target and (ii) optionally a static
  disclosure token.

## Commands run (all read-only; no lane writes, no `jj`, no git write, no protected tool)

```
git -C <lane> rev-parse HEAD                      → 5fa6017ddcae9f6bd4412df44765f6360cb16294
stat -c '%n %F' .git .jj                          → both directories (jj-colocated)
git -C <lane> for-each-ref --format='%(refname)' | awk -F/ '{print $1"/"$2}' | sort | uniq -c
                                                  → 1 refs/heads, 8 refs/jj, 2 refs/remotes (11 total)
git -C <lane> for-each-ref --format='%(refname)' refs/heads refs/tags refs/remotes | wc -l → 3
  … | grep -c -E '^refs/(jj|stash|bisect)/'                                                → 0
<per keep ref> rev-list --count <oid> --not --all                                     → 0 ×8
<per keep ref> rev-list --count <oid> --not --branches --tags --remotes               → 1 ×6, 0 ×2
git -C <lane> log --oneline --branches --not --remotes | wc -l                        → 0
git -C <lane> log --oneline --branches '--glob=refs/jj/keep/*' --not --remotes | wc -l → 6
git -C <lane> log --oneline --branches '--glob=refs/nonexistent/*' --not --remotes    → 0, exit 0
git -C <lane> log --format=%H HEAD --branches --not --remotes -- <p6repo one.txt>     → 0
git -C <lane> log --format=%H HEAD --branches '--glob=refs/jj/keep/*' --not --remotes -- <same> → 4
git -C <lane> rev-list --count <keep-only-oid> --not --branches --tags --remotes --   → 1
git -C <lane> log -1 --format= --name-status <6 keep-only oids>  → 4 touch the two p6repo paths
git --version                                                                         → 2.56.0
bash -n <<< proposed snippets                                                         → SYNTAX-OK
grep -n 'durable-refs-unverifiable|durable-refs-only|--not --all|for-each-ref --format=%(objectname)|--branches --not --remotes' <3 files>
grep -n 'evaluate_path|try_pushed|try_stale|count_live_refs' tools/souji-quarantine.sh
git status --porcelain -- tools/ ; git diff --stat -- <3 files> ; git diff -U2 -- tools/souji-vault-verify.sh
sha256sum tools/souji-{verify,vault-verify,quarantine}.sh
```
No tools installed or upgraded (nothing needed; git 2.56.0 and bash suffice).

## Verdict

- C3(a): **PARTIAL / fails where it counts.** At close the live all-refs roots list is untouched in
  `souji-verify.sh:842` and `souji-vault-verify.sh:1034` (quarantine's `:1069` is unreachable), so an
  absent-worktree head held only by a keep ref still yields `SAFE(metadata-prune)`. Vault respelled
  only the *shadowed* base copy (`:554`). The fix is proven by probe: restricted roots flip 6 real
  keep-only heads from `unique=0` to `unique=1`.
- C3(b): **PARTIAL.** Vault landed all four sites; verify landed none of four; quarantine's two sites
  are unreachable. The seed is load-bearing on this lane (0 → 4 touching commits on two real tracked
  paths; 0 → 6 repo-root unpushed).
- Shared spelling: **one array pair per file suffices**; the helper route actually landed adds +43
  lines, a repo-scoped disclosure token, and three extra git invocations per refusal, while verify's
  three helpers are 18 lines of code with no callers. Prefer the arrays (F3) and, if disclosure is
  wanted, a static note on the existing refusal path.
- Simplification frontier: quarantine's 522-line guard island is the largest removable duplicate
  authority (it contains 1 of the 3 roots sites and 2 of the 11 unpushed sites); verify 39 + vault 32
  further dead lines; 420 lines of shadowed base definitions are candidates only with L1 sign-off.

**Smallest fix** (ordered, at close): (1) restrict the two live roots lists — verify `:842` and vault
`:1034` — with the F1 primary snippet (one `rev-list --not "${DURABLE_REFS[@]}"` line each); (2) seed
verify's four touching sites (`:267`, `:354`, `:704`, `:985`); (3) quarantine: `:299` only, and delete
the inert island (or annotate it inert); (4) update `tools/souji-verify.spec.md:29–30`, correct
`souji-verify.sh:57`, and reconcile `souji-vault-verify.sh:41–51` with what actually landed;
(5) delete verify's unused `jj_*` helpers, and either scope vault's note to the target or replace it
with the static token. Stop here: the next deletion (the shadowed base halves) would harm the
composition-provenance axis without a dedicated round.
