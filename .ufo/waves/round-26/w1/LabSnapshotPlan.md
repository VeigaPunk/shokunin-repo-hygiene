# LabSnapshotPlan — C2 gate snapshot-file plan (round 26, w1)

seat: labrat (leaf, no dispatch)
date: 2026-10-25
lane base: 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd
tools installed: none

## Status

STATUS: PASS — the gate derives **no** filenames from URLs or source ids; it resolves only the literal
`snapshot:` token written on the same line as each quoted Gate row. All seven landed snapshots verify
against `SHA256SUMS` and entry B is green on both K2 and Q54. Three real hazards remain for the
**still-undrafted** entry A (§ locators on code snapshots fail Q54; C-comment and HTML quotes must be
shaped for `squash()`); the ScoutRegroundDocs filename drift is harmless as landed because the
appended registry rows already name the landed per-file names.

## Evidence

Resolution semantics, `tools/souji-gate-check.py:99-118` (read this run, base revision). The whole
mechanism is five statements — there is no lookup table and no basename search:

```
105:  snap = SNAPSHOT_RE.search(line)                       # only the same line as the quote
106:  spar = snap.group(1)
107:  spath = spar if os.path.isabs(spar) else os.path.normpath(os.path.join(root, spar))
108:  real_sp = os.path.realpath(spath)
109:  if not real_sp.startswith(os.path.realpath(snap_root) + os.sep) ...
112:  if not os.path.isfile(spath): fails.append("check4-snapshot-missing-line-%d" % lineno)
```

`SNAPSHOT_RE = r"snapshot:\s*(\S+)"` (`:34`). Consequences: `snapshot:` resolves relative to
`--root`, **not** to `--snapshot-dir`; `--snapshot-dir` is used only as a containment boundary
(`:109`); an absolute path is accepted if it lands inside that boundary.

Runnable probe, scratch root `/var/tmp/souji-r26-LabSnapshotPlan` (copy of the tool, `corpus/SOURCES.md`,
`census/round-26/sources/`, `empty-slice`, `empty-verdicts`):

```
$ sha256sum -c census/round-26/sources/SHA256SUMS          # in the lane
git-fetch.1.txt: OK ... git-builtin-rebase.c: OK
SUMS_EXIT=0                                                # 7/7

$ python3 -B tools/souji-gate-check.py --root "$D" --round-date 2026-10-25 \
    --entries corpus/knowledge-entryB.md --snapshot-dir census/round-26/sources \
    --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts
entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0
EXIT=0

$ python3 -B tests/fixtures/r23-locator-heading.py --entries corpus/knowledge-entryB.md \
    --snapshot-dir census/round-26/sources
entries=1 locators=1 locators_bad=0
Q54_EXIT=0

# K2 with entry A genuinely absent (its real repo path does not exist yet):
FAIL corpus/knowledge/git-auto-maintenance-trigger-set.md entry-missing: ...
entries=2 ok=1 slice_verdicts=0 slice_total=0 fail=1
EXIT=1
```

`entryB.md` above is the real draft `.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set-r23.md`
copied to `corpus/` in scratch; entry A was supplied as a synthetic Stand-in for the undrafted file.

## The exact filenames the gate will look for

`census/round-26/sources/` — resolved from `snapshot:` tokens, so this is the complete set implied by
the two admitted entries' cited sources:

| entry | cited row | exact filename looked for | present |
|---|---|---|---|
| B (drafted, Gate p.104/107) | S128 git-fetch(1) | `census/round-26/sources/git-fetch.1.txt` | yes |
| A (no draft yet) | S128 git-fetch(1) | `census/round-26/sources/git-fetch.1.txt` | yes |
| A | S129 builtin call sites | `census/round-26/sources/git-builtin-fetch.c`, `-merge.c`, `-rebase.c`, `-am.c`, `-commit.c` | all yes |
| A | S130 pull spawn | `census/round-26/sources/git-builtin-pull.c` | yes |
| both | S131 fixture, S132 census | **none** — cited as `source:`, never `snapshot:`; both point at read-only campaign paths (`lanes/souji/round2/...`), and the gate only requires their S-ids to exist in `corpus/SOURCES.md` (`check5`) | n/a |

Registry is already at 132 rows including S128-S132 (`corpus/SOURCES.md:149-153`), so `check5` is
satisfied for the ids both entries cite.

## Findings

1. **No URL→filename mapping exists, so the "spec filename" question cannot bind the gate.**
   `tools/souji-gate-check.py:105` reads only the per-line `snapshot:` token. Any file name is legal
   provided the entry says it and it sits under the snapshot dir. The gate would pass an entry naming
   `census/round-26/sources/anything.txt` if that file held the quote. Consequence: the L1 must
   choose names that the **entry drafts** actually write; the spec's list is advisory only.

2. **ScoutRegroundDocs delivered different names than its spec — harmless as landed, but do not
   propagate the spec names.** Spec (`make-spec.py:193-194`) demanded `git-fetch.1.txt`,
   `git-builtin-v2560.txt`, `git-pull-c.txt`. Actual scratch output
   (`/var/tmp/souji-r26-ScoutRegroundDocs/`, read this run) is `git-fetch.1.html`, `git-fetch.adoc`,
   `builtin-{am,commit,fetch,merge,pull,rebase}.c`, `git-v2.56.0.tar.gz`: there is **no**
   `git-builtin-v2560.txt` and no `git-pull-c.txt`. The L1 already copied the split form, and the
   appended rows match it (`corpus/SOURCES.md:150` names `git-builtin-{fetch,merge,rebase,am,commit}.c`;
   `:151` names `git-builtin-pull.c`). So no dangling registry path — but entry A must be written
   against the **landed** names. Proven discriminating in scratch:

   ```
   # snapshot: .../git-builtin-v2560.txt  (S129) and .../git-pull-c.txt (S130)
   FAIL ... check4-snapshot-missing-line-6
   FAIL ... check4-snapshot-missing-line-8
   entries=1 ok=0 fail=6        EXIT=1
   # same entry with git-builtin-fetch.c / git-builtin-merge.c / git-builtin-pull.c
   entries=1 ok=1 fail=0        EXIT=0
   ```

3. **Entry A has no Gate at all, so C2's K2 cannot pass yet.** The staged file
   `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/git-auto-maintenance-trigger-set.md`
   has sections `## Claim`, `## What this does NOT establish`, `## Lane link and consequence`,
   `## Freshness` — no `## Gate`, no `snapshot:`, no ADMIT/REJECT. `.ufo/waves/round-26/w1/` contains
   only entry B's draft. Measured red arm with the real repo path absent:
   `entries=2 ok=1 fail=1 EXIT=1` (`entry-missing`). Entry A must be drafted (Gate + ≥1 ADMIT + ≥1
   REJECT with reason+flip) or K2 stays red.

4. **`§ <file>:<line>` locators on code snapshots pass the gate and fail Q54.** Q54's fixture
   (`tests/fixtures/r23-locator-heading.py:67-79`) builds its heading set from `<h1..6>` tags or
   all-caps short lines; a C file has neither for a path. Measured on a synthetic entry A whose Gate
   passed K2 cleanly:

   ```
   entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0        EXIT=0   # K2 green
   LOCATOR-BAD  ...  builtin/fetch.c:2926  'builtin/fetch.c:2926' is no heading in: ...
   LOCATOR-BAD  ...  builtin/merge.c:506   ...
   LOCATOR-BAD  ...  builtin/pull.c:392    ...
   entries=1 locators=4 locators_bad=3                          Q54_EXIT=1
   ```

   The prereg's C2 kill rule is "any admitted entry's Gate locator failing Q54", so this is blocking.
   **Remediated shape, verified:** write code locators as `line 2926 of builtin/fetch.c` (no `§`).
   The gate's `LOCATOR_RE` accepts `line ` (`:33`) and Q54 only scans `§` (`:30`); the same entry then
   reads `entries=1 ok=1 fail=0 EXIT=0` **and** `entries=1 locators=1 locators_bad=0 Q54_EXIT=0`.

5. **Multi-line C comments squash with their ` * ` markers, so a natural comment quote is rejected.**
   Measured against the landed snapshot:

   ```
   ABSENT   git-builtin-merge.c | We ignore errors in 'gc --auto', since the user should see them.
   PRESENT  git-builtin-merge.c | We ignore errors in 'gc --auto', since the * user should see them.
   ```

   Entry A's merge/rebase error-ignoring ADMIT (staged body lines 30-34) must carry the ` * ` or be
   trimmed to a single source line.

6. **Quotes spanning inline HTML tags are rejected in `git-fetch.1.txt`.** The snapshot is the
   git-scm.com HTML rendering (`<title>Git - git-fetch Documentation</title>`, `:31`), so the command
   name in prose is split across `<span>`/`<code>`:

   ```
   ABSENT   git-fetch.1.txt | Run git maintenance run --auto at the end
   PRESENT  git-fetch.1.txt | repository maintenance if needed. This is enabled by default.
   ```

   Entry B already uses the safe plain-prose form (`w1/entry-...-r23.md:107`); entry A must not quote
   through a tag. The version pin is evidenced in-snapshot (`:1340` "git-fetch last updated in
   2.56.0"), so the `git 2.56.0` tier claim is backed.

7. **A quote containing a double quote breaks `QUOTE_RE`.** `QUOTE_RE = r'"([^"]{2,400})"'` (`:20`)
   terminates at the embedded `"`, so a Gate row quoting
   `strvec_pushl(&cmd.args, "fetch", "--update-head-ok", NULL);` yields a truncated "quote" that is
   absent from the snapshot. Verified: the fragment `strvec_pushl(&cmd.args,` is PRESENT in
   `git-builtin-pull.c`; the full line with embedded quotes is not usable. Entry A's S130 ADMIT must
   quote a quote-free fragment (or the C string pieces will be split into bogus sub-quotes).

8. **`--snapshot-dir` is a boundary, not a search path.** Measured: a `snapshot:` of
   `corpus/SOURCES.md` with an existing file gives `check4-snapshot-outside-dir-line-6 EXIT=1`; an
   absolute path inside the snapshot dir gives `ok=1 EXIT=0`. The L1 may therefore pass absolute
   paths when running from outside the lane, but may never point `snapshot:` at `corpus/`.

9. **Provenance nit on the S128 row.** `corpus/SOURCES.md:149` writes `installed man page git 2.56.0`,
   but the committed snapshot is the git-scm.com HTML page, not man output. The host does have
   `/usr/share/man/man1/git-fetch.1.gz`, so the phrase is not false about the host — it is simply not
   the artifact the row's own `snapshot` names. Suggest `git-scm.com HTML rendering, last updated in
   2.56.0` so the notes cell matches the bytes.

10. **Slice arms are inert as configured.** `empty-slice` yields `slice_verdicts=0 slice_total=0`, so
    `v == t` holds and `run()`'s exit depends only on `ok == len(entries)` and `total_f` (`:183`).
    No snapshot work is needed for the slice arm.

## Attack log

ATTACK (A1, gate gameability — K2): the gate never resolves headings; `LOCATOR_RE` (`:33`) only
demands that a locator-ish token appear once on the quoted line. Any entry can satisfy it with a
locator naming a section absent from its snapshot, as long as Q54 is not run separately. K2 alone is
therefore weaker than the C2 kill rule that names Q54: **the L1 must run
`tests/fixtures/r23-locator-heading.py` as a second command, or K2 green is not evidence of the
locator rule.**

ATTACK (A2, Q54 first-word truncation): `LOCATOR_RE` in the fixture captures to the first space, and
the check is substring-against-a-union-of-headings. So `§ OPTIONS --auto-maintenance` scores as
"OPTIONS exists" even though `--auto-maintenance` is a `<dt>`, not a heading, and a locator may
resolve in a *different* snapshot than the one its own ADMIT row names. The round's actual entry B
locator is exactly this shape: `locators=1 locators_bad=0` is honest only as "the OPTIONS section
exists in a snapshot this Gate names". Do not read it as validating the flag anchor.

## Bounds

Read-only against the lane: no git/jj mutation, no writes outside this report. Campaign package and
`/var/tmp/souji-r26-ScoutRegroundDocs/` read only; nothing written under
`/home/vgpnk/Projects/shokuknow`. Scratch `/var/tmp/souji-r26-LabSnapshotPlan/` removed after the
runs. No installs, so no tool-change record.
