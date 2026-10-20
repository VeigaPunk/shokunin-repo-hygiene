# ReopenS045 — gitattributes(5) vs `corpus/SOURCES.md` S045

Seat: SoujiR16.ReopenS045-4. Lane HEAD `163158a` ("round-16: lesson, sources S043-S050, ..."). Row S045 is committed at `HEAD:corpus/SOURCES.md:59`; `git diff --stat` over `corpus/SOURCES.md corpus/lessons/round-16.md tools/souji-census.sh tools/souji-landing-gate.py` is empty, so worktree row = HEAD row. Page re-opened 2026-10-20 from https://git-scm.com/docs/gitattributes; the served copy carries "gitattributes last updated in 2.56.0" (2.56.0 entry dated 2026-09-28), matching the anchor cell's version stamp.

## Located quote (20 words)

"In the check-in codepath, the worktree file is first converted with filter driver (if specified and corresponding driver defined)"

Location: § EFFECTS › Interaction between checkin/checkout attributes (served HTML line 847). The `filter` subsection itself (lines 584-586) states the same rule: the `clean` command "is used to convert the contents of worktree file upon checkin".

## Scope / teaches support

- **Scope — HOLDS.** The page's only statement of when the driver runs is the check-in codepath; the page never claims a status-time invocation. The scope's qualifier "not ... in every stat state" is also the accurate one for git 2.55.0: `ie_modified` (read-cache.c:445-493) returns `DATA_CHANGED` from stat data without reading content when the index size is known and non-zero, and reaches `ce_modified_check_fs` → `ce_compare_data` (read-cache.c:232, 287-293) only for racy timestamps or size-unknown entries. So the source is correctly scoped to "check-in", and the status side is an implementation caveat, not a page teaching.
- **Teaches, check-in clause — HOLDS.** Quote above: a `filter=` attribute naming a configured driver makes the clean conversion run on the check-in codepath.
- **Teaches, status clause — FAILS the "page supports it" test.** "which status may re-run to compare with the index" has no basis on this page. A whole-page sweep for `status` returns only the site nav (line 28), the renormalisation example (lines 451, 455), and `status=` tokens of the long-running filter protocol (710-828). The page nowhere links `git status` to a filter driver; the check-in path it names is `git add`/`git commit` (the `text` intro, lines 325-329).
- The status clause is nevertheless true, but by implementation, not by this page: at tag v2.55.0, `ce_modified_check_fs` → `ce_compare_data` → `index_fd` → `convert_to_git` for `OBJ_BLOB` with a path (read-cache.c:232, 287-293; object-file.c:1000-1004, 1358-1377). [code-verified by web read of raw.githubusercontent.com/git/git/v2.55.0]
- **Anchor cell — minor imprecision.** "§ Effects, filter" names the right document region, but the quoted sentence is in the sibling subsection "Interaction between checkin/checkout attributes", not in `filter`. Fix: name both, or the interaction subsection.

## Tier / status / recheck / opened

- **tier A — right.** Official upstream manual, same as every git-scm.com docs row (S001-S004, S042, S043, S049). Caveat: `SOURCES-CONTRACT-v1.md` (cited by `corpus/lessons/round-12.md:137` as the tier definition) is absent from the lane and from `git log --all --` for the candidate paths, so this was checked against registry usage, not the contract's own lines.
- **status `mined` — right.** The row is cited by `corpus/lessons/round-16.md:28` and its claim list at :35, and it is the declared basis for C1's bound-filter skip. A source with an active landed citation is `mined` per the S042/S043 precedent, not `queued`.
- **recheck `on-release` — right.** The manual is release-stamped (2.56.0, latest on the page's version index) and every git-scm docs row uses `on-release`; reopening today still matches.
- **opened 2026-10-20 — right.** Live page served today.

## Is it used by the claim it names?

Claim named in the row's `used-by` (`corpus/lessons/round-16.md`) and at lesson :35: "C1's bound-filter skip ... rest on S045".

- `tools/souji-census.sh` at HEAD `163158a`: the outcome is documented at :105 (`status-unverifiable`, "filter.<name>.clean|smudge|process driver that an attributes source binds to a tracked path"); `guard_bound_filters()` at :983; driver names collected from `^filter\..*\.(clean|smudge|process)$` at :987; lookup is `git ls-files -z --cached ... | git check-attr -z --stdin filter` at :1008; the skip prints `status-skipped: filter-driver-bound` and returns `unverifiable` at :1027-1030; :1226 maps that to `status-unverifiable` with `dirty=0`. So the named claim is truly implemented at HEAD.
- `tools/souji-landing-gate.py` at HEAD: no attribute/filter consumption. Its only matches are `--diff-filter=AM` at :557 and a docstring caveat that `git archive` can alter bytes via export-ignore/export-subst/attributes at :22. The row does not claim the gate uses it, so no mismatch.
- **Counterexample (minor, C1 guard calibration, `tools/souji-census.sh:987-1020`):** the guard collects driver names from `clean`, `smudge` and `process` interchangeably. A driver with only `filter.<name>.smudge` defined, bound to a tracked path, therefore suppresses the dirty count (`status-unverifiable`) although status only ever needs the check-in (clean/process) direction and a smudge-only driver is inert there. This is fail-closed, not unsafe, but it contradicts the row's own mechanism ("converts worktree content on the check-in path") and Q22's rule that a harmless value must not suppress unaffected rows. Smallest fix: collect names from `filter.*.(clean|process)` only for the binding test.

## Verdict

**fails (narrow).** Scope holds and is well calibrated; the check-in clause, tier, status, recheck, opened date, anchor region and the `used-by` claim (census implementation) all hold. The defect is one clause: the teaches cell puts "status may re-run to compare with the index" under a row whose anchor never says it, and lesson :35 makes that the basis of C1. The conclusion is correct by git source, so the smallest honest fix is either:

1. reword teaches to "a filter driver bound by attributes converts worktree content in the check-in codepath; the census refuses status when a configured clean/process driver is bound to a tracked path (defensive; this page does not state a status invocation)", or
2. add a code anchor row (`read-cache.c:232,287-293`; `object-file.c:1000-1004,1358` @ v2.55.0) and cite it for the status half, leaving S045 for the check-in half.

STATUS: FAIL — S045 teaches says status may re-run the bound filter; the cited gitattributes page never states it (check-in clause alone is supported).

## Commands

Shell commands run (verbatim):

```
grep -n "S045" /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '59p' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i "filter" tools/souji-census.sh tools/souji-landing-gate.py | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '960,1045p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls corpus | head -30 && grep -rn "S045" corpus/lessons/round-16.md corpus/SOURCES-CONTRACT-v1.md 2>/dev/null | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '20,40p' corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rln "SOURCES-CONTRACT-v1" corpus docs 2>/dev/null | head; grep -n "tier\|Tier" corpus/QUALITY.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git show HEAD:tools/souji-census.sh | grep -n "guard_bound_filters\|status-skipped\|check-attr" && echo "--- gate ---" && git show HEAD:tools/souji-landing-gate.py | grep -n "attributes\|check-attr\|filter"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "tier\|Tier\|mined\|queued\|on-release\|recheck" corpus/SOURCES.md | head -25 && echo "=== round-12 contract ===" && grep -n -A3 -B3 "SOURCES-CONTRACT\|tier A\|Tier A\|mined\|queued" corpus/lessons/round-12.md | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,40p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '90,130p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1465,1500p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "count_dirty\|status --porcelain\|status-unverifiable" tools/souji-census.sh | head -20 && echo "--- other content commands ---" && grep -nE 'git -C "[^"]*" .*(diff|add|checkout|hash-object|ls-files -s|cat-file)' tools/souji-census.sh | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "filter\.\|filter \"" tools/souji-census.sh | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/SOURCES.md | grep -c "S045"; git log -1 --format='%h %s' HEAD; sha256sum tools/souji-census.sh tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "status_info_file" tools/souji-census.sh | head && sed -n '930,985p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for p in SOURCES-CONTRACT-v1.md docs/SOURCES-CONTRACT-v1.md corpus/SOURCES-CONTRACT-v1.md ../SOURCES-CONTRACT-v1.md ../docs/SOURCES-CONTRACT-v1.md; do [ -f "$p" ] && echo "FOUND $p"; done; git log --oneline --all -- SOURCES-CONTRACT-v1.md docs/SOURCES-CONTRACT-v1.md corpus/SOURCES-CONTRACT-v1.md | head -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat -- corpus/SOURCES.md corpus/lessons/round-16.md tools/souji-census.sh tools/souji-landing-gate.py; git show HEAD:corpus/SOURCES.md | grep -n '^| S045'; git show HEAD:corpus/lessons/round-16.md | grep -n 'S045' | head -3
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '1019,1040p' && echo '--- usage flags ---' && sed -n '1215,1235p' tools/souji-census.sh
```

Web/tool reads (not shell): `read`/`grep` of https://git-scm.com/docs/gitattributes (whole page, then :301-560, :564-760, :835-870); `read`/`grep` of https://raw.githubusercontent.com/git/git/v2.55.0/read-cache.c (:225-275, :279-305, :440-500), https://raw.githubusercontent.com/git/git/v2.55.0/object-file.c (grep `convert_to_git`), https://raw.githubusercontent.com/git/git/v2.55.0/builtin/commit.c (grep `refresh_index`). No writes outside this report; no /var/tmp scratch used; no tool installed or updated.
