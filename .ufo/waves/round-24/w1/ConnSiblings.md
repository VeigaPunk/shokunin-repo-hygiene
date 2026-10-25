# ConnSiblings — sibling-overlap scan (souji r24 w1, read-only)

Seat: L1Souji24.ConnSiblings (connector). Lane rev read: `f9db2181647d91470a724a12d626bd6106805076`.
Preregistration read first: `.ufo/waves/round-24/preregistration.txt` (C1/C2/C3 frozen; nothing below
proposes changing a predicate, target or case set — gameability/construct issues are under Attack log).

## Status

STATUS: PASS. All three topics were scanned in the 20 sibling lanes (souji excluded). Every hit was
classified as reuse, cite or deliberately differ. The scan also ran three falsifiers that hit the frozen
counters: one shows a C1 construct gap, one confirms C3 case d is not killed by the new checks, and one
predicts that C2's base control is non-zero.

## Evidence

Scan scope: `tools/`, `corpus/knowledge/`, `tests/` of each `*-shokunin` lane except souji (only kama has
`tests/`; 9 lanes have `tools/`). Every cited sibling file is tracked and clean at the revision below,
so the bytes I read are the committed bytes. Sibling HEADs: kama `873c5d7774b9`, tsukuroi `564db0b614b2`,
tameshi `322b5cd32b43`, kotodama `21e6a7f3fb63`, mori `b1d7269f4f26`, kaidoku `aa04633a686d`,
kasegi `b76676eedca7`, mado `b4e47e980bfb`, chousa `d29bf47d9414`.

E1. Topic (1) — size/debris census:
`grep -rlE 'count-objects|lost-found|size-garbage|garbage found|worktrees/[^ ]*/refs' <all sibling dirs>`
returned **zero hits**. A broader `git (fsck|gc|prune|repack)|objects/pack|objects/info/alternates|dangling blob|commondir|git-common-dir`
search turned up only kama (promisor/alternates handling), kotodama (a linked-worktree fixture) and mado
(a `.git`-file worktree fixture).

E2. Falsifier — linked-worktree garbage, git 2.56.0, run in `/var/tmp/souji-r24-ConnSiblings` (scratch, removed):
```
git worktree add -q --detach --no-checkout ../wt1 ; git -C ../wt1 count-objects -v
warning: garbage found: /var/tmp/souji-r24-ConnSiblings/r/.git/worktrees/wt1/refs
garbage: 1
git --git-dir="$(git -C ../wt2 rev-parse --path-format=absolute --git-common-dir)" count-objects -v
garbage: 0
git -C r rev-parse --git-common-dir            ->  .git            (relative, from main worktree)
git -C r rev-parse --path-format=absolute --git-common-dir -> /var/tmp/.../r/.git
```

E3. Falsifier — what a real partial clone writes, git 2.56.0, same scratch:
```
git clone -q --no-checkout --filter=blob:none --no-local file://$S/r bl2 ; git -C bl2 config --list --local
core.repositoryformatversion=1 ... remote.origin.promisor=true
remote.origin.partialclonefilter=blob:none
ls bl2/.git/objects/pack/ -> pack-387d….promisor (plus .idx .pack .rev)
git -C bl config --get extensions.partialclone -> rc=1 (absent even before stripping)
after unsetting remote.origin.promisor/partialclonefilter: promisor_files=1, count-objects garbage: 0
```

E4. Falsifier — C3 case a and case d premises. Case a was probed in scratch; case d was read only, on the lane:
```
git commit-tree -m unlanded <tree> -p HEAD -> for-each-ref --contains <c> refs/heads refs/tags refs/remotes = []  ; cat-file -e <c>^{commit} rc=0
for-each-ref --contains <blob-oid> refs/heads -> "error: object … is a blob, not a commit" rc=129
r23 receipts (census/round-23/records/*.tsv, all committed at HEAD):
declared-evidence-after      rev=9301d98c1c68 durable_refs=[refs/heads/master refs/remotes/origin/HEAD refs/remotes/origin/master] tool_in_argv=True
gate-check-at-first-landing  rev=a211e4d1bf6e durable_refs=[same]  tool_in_argv=True
gate-check-at-lane-base      rev=1208bfb4924d durable_refs=[same]  tool_in_argv=True
gate-check-c3                rev=476525026cdb durable_refs=[same]  tool_in_argv=True
agreement-after              rev=eb1aa49783ae durable_refs=[same]  tool_in_argv=True
```
(`tool_in_argv` = `tool=` value is an element of `shlex.split(cmd=…)`.)

E5. Falsifier — C2 base shape. I split `git show HEAD:corpus/README.md` on unescaped `|`; this is my own
split, not the frozen tool:
```
row 40  F2 …  cells=3 naive_cells=6   (two rows in the file carry an escaped pipe inside a cell)
row 68  F2 …  [1] status: "… **r23: the read side now holds three entries** (`git-repo-structure-readonly.md`, `repo-size-census-readonly.md`, …"
              [2] entries: `knowledge/git-repo-structure-readonly.md` (S035/S036/S037); `../tools/souji-repo-structure.sh`; …
grep '^ground:' corpus/knowledge -> repo-size-census-readonly.md: "ground: F2 — …", count-objects-garbage-readings-r25.md: "ground: F2 — …"
```

## Findings

Topic (1) — size/debris census, `count-objects`, `fsck --lost-found`, linked-worktree garbage

1. **No sibling owns this ground (E1).** No other lane has a tool or entry on `count-objects`, `fsck --lost-found`
   or the worktree `garbage` false positive, so souji r24 C1 and its assimilation theme are fleet-novel. There is
   nothing to reuse, and the knowledge entry should not claim a sibling precedent. **Differ (by default).**

2. kama `tools/report-landing-audit.py:58-60` — the commit-citation auditor treats promisor metadata as
   non-evidence and runs every git call with lazy fetch off. Quote: "metadata alone never changes a verdict, and
   the promisor remote is never contacted". **Cite and differ.** Kama keeps auditing a partial clone. Souji C1
   refuses with exit 2, which is the frozen contract. The shared part is the isolation: souji's census should
   pass `GIT_NO_LAZY_FETCH=1` / `--no-lazy-fetch` on every call, as `tools/souji-receipt-run.py` already does,
   so that `fsck` on a promisor repository can never fetch, which would write objects.

3. kama `tests/report-audit/repo-state-grid.py:197-198` (`f_promisor_pack`). Quote: "A blobless clone whose
   promisor config was removed still lacks the". The fixture strips the promisor config and keeps the
   `*.promisor` pack. **Reuse the recipe** for C1 case 6, which E3 reproduces on git 2.56.0. Also
   `:156` `c_shared_clone` (`clone --shared` writes `objects/info/alternates`) is a git-native way to build
   case 5 instead of hand-writing the file. **Reuse.**

4. kama `tests/report-audit/repo-state-grid.py:4-6`. Quote: "premise (a fixture whose fault never
   materialized makes the grid exit 2, not". **Reuse the discipline**: every r24 fixture case should check
   that its fault really exists before scoring the tool. C1 case 4 already does this (raw `garbage: 1`
   witness); cases 2, 3, 5 and 6 should do the same. That means case 2 checks the dangling blob is present,
   case 3 checks the junk pack file is there, case 5 checks the alternates line, and case 6 checks the
   promisor marker or config.

5. kama `tests/report-audit/promisor-grid.py:21-22`. Quote: "before/after object inventory reports as
   `objects_acquired`". This is the closest sibling analogue to C1's no-write `.git` manifest. **Cite.**
   **Differ deliberately**: souji's frozen manifest covers every `.git` file, not only objects, which is
   what catches `fsck --lost-found` (case 7).

6. kotodama `tools/harness/receipt_guard.py:663-666`. It builds a linked worktree with
   `worktree add --detach --no-checkout` and asserts `cli("linked-worktree-refused", …, 3,
   "RECEIPT-GUARD-COMMITTED", repo=linked)`. **Reuse the fixture command.** E2 shows that `--no-checkout`
   already produces the `garbage: 1` false positive, so case 4 needs no checkout. **Differ on the verdict**:
   kotodama refuses a linked worktree, while souji C1 resolves it to the common dir and reports.

7. mado `tools/mado-verify.sh:948-951` (OM12). Quote: "the repository test; the worktree's file shape is the
   fixture here." It is a regression fix for testing a worktree by `.git`-directory shape. **Cite** as a
   sibling incident: souji's "not a repository" refusal and its common-dir resolution must use
   `git rev-parse`, never a `-d .git` test. E2 adds one more detail: from the main worktree,
   `--git-common-dir` returns the relative `.git`, so the tool needs `--path-format=absolute`.

Topic (2) — receipt verifiers with durable-rev or argv binding

8. tameshi `tools/evidence-disposition.py:505-523` uses `for-each-ref --contains <commit>` over `refs/heads/`
   and `refs/remotes/`. Quote: "detached HEAD {} is on no branch or remote-tracking branch". This is the same
   durability mechanism as souji's `durable_rev` (`tools/souji-receipt-run.py:126-130`). **Cite. Differ
   deliberately**: souji also counts `refs/tags` and excludes `refs/jj/*` (Q37). The C3 knowledge or
   README text should state that the ref set differs from tameshi's and kotodama's, so a fleet reader does
   not assume they match.

9. kotodama `tools/harness/receipt_guard.py:10-11`. Quote: "A ref that does not resolve to a commit, or any
   for-each-ref warning, fails closed". **Reuse the rule** for C3 `verify`. Souji's current `durable_rev`
   returns `proc.returncode == 0 and bool(proc.stdout.strip())`. That folds every git failure, including
   rc=129 on a blob id (E4), into "not durable". See Attack A2.

10. tsukuroi `tools/_revision.py:23-24`. Quote: "a timeout, or git missing — is E-GIT-FAILED, never "not an
    ancestor"." **Reuse as a refusal-code principle**: a git error is never the not-durable finding. tsukuroi
    `tools/check-revision-binding.py:321` creates an unlanded probe commit and then confirms it is unlanded.
    **Reuse the premise-check shape for C3 case a**, but build the commit with `git commit-tree` (E4), which
    writes no ref or branch, rather than `commit --allow-empty`, which advances `HEAD`.

11. mori `tools/mori-retention-reconcile.py:185`. Quote:
    `require(argv.count(flag)==1 and argv.index(flag)+1<len(argv),'receipt_argv_binding')`. Mori binds a
    receipt's recorded argv option to its inputs exactly once, and normalises an absolute recorded path
    against the recorded `--repo` (`:188-192`). **Reuse the element-equality semantics for C3 case b**: the
    `tool=` value must equal a `shlex.split(cmd=)` element, which all five r23 receipts satisfy (E4). Mori
    goes further with count==1 and absolute-path normalisation. **Differ deliberately**: C3 freezes only
    "occurs as an argv element", so do not add mori's extra rules in r24, since that would change a frozen
    predicate. Note them as residuals instead.

12. kama `tests/llamacpp-live/check-receipt.py:8`. Quote: "an outcome field, exact launch argv binding, and
    pinned source-binding". It is a receipt validator that checks the stored launch argv. **Cite only**: the
    schema and domain differ (a live server receipt, not a git-rev receipt).

13. chousa `corpus/knowledge/per-record-argv-attribution-r36.md:29`. Quote: "The witness binds a log line to
    a record by decoding the argv". **Differ**: this binds log lines to records through argv; it is not
    receipt-to-tool binding. It is a false positive of the keyword search.

Topic (3) — coverage-map / README-map agreement checkers

14. kaidoku `tools/round-26/c2-calibration.py:120,146-147`. Quotes: `section = readme.split("## Coverage
    map\n", 1)[1].split("\n## ", 1)[0]` and `"missing": sorted(files - mapped),` / `"dangling": sorted(mapped
    - files),`. It is a calibration counter with the same two mismatch classes as souji C2, read from git
    objects at `--rev` (`ls-tree` plus blob), exit 0/1/2, with a mutant that drops one map stem (M5, `:619`).
    **Reuse the read-at-rev pattern and the M5 mutant idea** for `tests/fixtures/r24-coverage-agreement.py`.
    **Differ deliberately**: kaidoku compares sets over the whole section, while souji's predicate is scoped
    per row (an entry counts only under a row whose ground cell starts with its own `F<k>`). An entry mapped
    under the wrong `F` row is MISSING in souji but OK in kaidoku.

15. kaidoku `corpus/knowledge/2026-10-14-r14-02-final-sweep.md:32`. Quote: "Coverage-map section cited **56
    of 70** knowledge files; **14 unmapped**, zero dangling in the". **Cite** as prior fleet evidence that
    coverage-map drift builds up when rounds stop appending map rows. This supports C2 being measured on
    calibration, not hypothetical.

16. kama `tools/round35-coverage-audit.py:9` (and round36/37). Quote: "A name outside the heading '## Coverage
    map — round 35 addition' does not count." These are per-round counters of additions under a named
    heading. **Differ**: they count additions, not agreement between the map and the entries.

17. kasegi `corpus/knowledge/authorised-testing-rules-of-engagement.md:5`. Quote: "ground: F09 (new frontier
    item; extends F03, which holds the platform-side safe-harbour statement only)". kasegi is the only other
    lane using the same `ground: F<k>` front-matter key, with a `## Coverage map` heading
    (`corpus/README.md:7`). **Cite as a cross-lane convention. Differ**: kasegi's map rows live in a
    `## Frontier` table whose entries sit in a different column, with zero-padded ids (`F09`). Souji's frozen
    header predicate (third header cell beginning `entries`) would not match it, so do not imply
    portability.

Cross-axis patterns

18. **One refusal grammar, three lanes.** The same rule appears in tsukuroi (`E-GIT-FAILED` is never
    not-landed), kotodama (a warning fails closed) and kama (`could-not-evaluate` exit 2: "Errors are never
    verdicts", `report-landing-audit.py:46`). Souji r24 uses exit 2 for refusals in C1, C2 (input) and C3.
    Applying "git error ≠ finding" to all three tools at once improves operability without touching any
    counter.

19. **One manifest or premise function, two claims.** C1's `.git` manifest (case 1/2/3/6/7) and a premise
    check (finding 4) are the same helper shape that C3 fixtures need for "verify writes nothing". kaidoku
    `tools/round-25/ruler.py:62` and mori `tools/mori-evidence-loss.py:217` snapshot `st_mtime_ns` (integer
    nanoseconds). [INFERENCE] Souji's manifest should use `st_mtime_ns`, not float `st_mtime`, so it can
    detect a rewrite within the same second.

20. **One "isolated git env" across C1 and C3.** souji-receipt-run already sets `GIT_NO_REPLACE_OBJECTS`,
    `GIT_NO_LAZY_FETCH` and `GIT_OPTIONAL_LOCKS=0` (`tools/souji-receipt-run.py:208-210`). kama neutralises
    the same channels (`report-landing-audit.py:48-51`). The C1 census should share this environment, so
    that the no-write envelope is measured under the same isolation the receipts record.

## Attack log

A1 (C1 case 6 construct validity, coverage). **Real partial clones carry no `extensions.partialClone` on git
2.56.0 (E3).** The frozen CLI says "promisor/partialClone repo" → exit 2. A tool keyed on
`git config extensions.partialClone` would pass a fixture built the way kama's selftest builds one
(`report-landing-audit.py:1358`, `("extensions.partialClone", "origin"),`), yet accept a real
`--filter=blob:none` clone. It would also accept the config-stripped clone, which still has
`objects/pack/*.promisor` (E3, finding 3).

This is not a case-set change, because case 6 already reads "partialClone repo". The finding is how the
fixture should construct that repository: from `git clone --filter=blob:none --no-local file://…`. The
refusal predicate should then fire on any of `extensions.partialclone`, `remote.*.promisor=true`, or a
`*.promisor` pack. If the fixture is config-only, report C1 case 6 as weaker than its label.

A2 (C3 case a gameability, operability/calibration). The current `durable_rev` returns False on any
`for-each-ref` failure (E4: rc=129 on a blob id). A `verify` that reuses it would print
`RECEIPT-REV-NOT-DURABLE` for a 40-hex blob or a missing object, as well as for the real case. Case a still
passes, because it uses a real unlanded commit, so the counter cannot tell a correct verify from one that
folds errors into this finding. Add a guard for `verify`, not a counter change: check
`cat-file -e <rev>^{commit}` first, and treat rc ≥ 2 or stderr as a git failure (findings 9 and 10).
Disclose the gap as a residual.

A3 (C3 kill rule, falsifier run — **not killed**). All five r23 regression receipts have revs on
`refs/heads/master` and `refs/remotes/origin/master`. In each, the `tool=` value is an exact
`shlex.split(cmd=)` element (E4), so the two new refusals cannot regress case d at the current refs.
The residual risk is that a `jj` rewrite moving master off those commits before the landing would make
case d fail at tip. [INFERENCE] Re-run E4 at the landing tip.

A4 (C2 base control, calibration — prediction, not a score). By my own split (E5), the two `ground: F2`
entries `repo-size-census-readonly.md` and `count-objects-garbage-readings-r25.md` are named only in the
**status** cell of README row 68, not the entries cell. Under the frozen predicate, the base control should
therefore show `mismatches ≥ 2` (MISSING-FROM-MAP). [INFERENCE] The frozen tool, once built, is the only
scorer. Two parser hazards:
- Two map rows contain an escaped pipe inside a cell (row 40: 3 real cells, 6 by a naive `split("|")`).
  The tool must split on unescaped pipes; kaidoku's `' | '` split also survives this.
- C1's new F2 entry plus these two must be added to an F2 entries cell for C2 tip = 0. This is the coupling
  that the preregistration's separability note already names (lines 120-121).

A5 (C1 case 1/7 manifest ambiguity, coverage). The frozen manifest reads "sorted path+type+mode+size+mtime+
sha256 of regular files". If only regular files are listed, a write that creates only a directory, such as
an empty `.git/lost-found/`, is invisible. Case 7 still works, because `fsck --lost-found` creates a
regular file under `other/<oid>`. Recommend that the fixture list every entry with its type (directories
included) and hash only the regular files. This is a reading of "type", not a change. Report it if the
built fixture lists files only.

## Proposed move (one, bounded)

Build one shared isolation-and-premise helper pattern into the three r24 fixtures, with no change to any
frozen predicate:
- (a) Construct C1 case 6 from a real `--filter=blob:none` clone, plus kama's config-stripped variant, and
  refuse on config or the `*.promisor` marker (A1).
- (b) Check every case's premise before scoring, with exit 2 on a missing premise (finding 4).
- (c) Treat a git error as never being a finding in the C3 `verify` path and the C1 census (A2, finding 18).

Axes:
- coverage: up. Case 6 tests the real partial-clone shape.
- operability: up. Refusal codes become unambiguous.
- calibration: unharmed, and C2 is untouched.

Risks: if the tool and fixture authors already built case 6 config-only, A1 becomes a disclosed weakness
rather than a fix. Adding a `*.promisor` check cannot break cases 1-5, because none has a promisor pack
(E3 also shows `count-objects` reads `garbage: 0` with a `.promisor` file present).

Verification:
- `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` at the landing tip, with
  case 6 built by `git clone --filter=blob:none`. The tool must exit 2 on both the configured clone and the
  config-stripped clone.
- `for-each-ref --contains` and the `shlex` check (E4) re-run at the landing tip for case d.

## Tooling

No installs or upgrades. git 2.56.0 and python3 were already present.
