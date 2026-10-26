# r31 closure defect 2 — draft append-only fixes (C3 entry traceability)

Seat `SwarmScribe25`, round 32 wave 1. Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`; tree read at lane HEAD
`7a6667cd27652baf8d704b5cdb8e3200bd6e27a1` (controls commit), prereg `3ec84fc81b3243429c834a051880b0bcde06291c`.
DRAFT ONLY — nothing below is applied to the lane. The L1 applies it.

Routed defect (verbatim, `corpus/lessons/round-31-verifier-spotcheck.md` `## Routed defects` item 2):

> add S051 to the entry's `source:` lines and the S051 `used-by` cell, or drop the quote (lesson Gate l.19);
> add the CONFIGURATION/`config/gc.adoc` anchor to S063's cell, or open a dedicated row;
> give `gc.recentObjectsHook` a Gate quote (entry correction l.247).

Three decisions, then the exact text, then the run.

---

## (a) S051: cite it, do not drop the quote — append `- source: S051` plus the `used-by` cell

Decision: **add S051** (both halves), keep the quote.

Grounds, all opened this run:

1. The round-31 Gate already prescribed exactly this and only the append did not land
   (`corpus/lessons/round-31.md` `## Gate`, S051 row): "an L1 correction adds S051 to the entry's `source:` lines and its used-by cell, or the quote leaves the entry".
2. S051's own scope cell admits the quoted bytes (`corpus/SOURCES.md`:72): "colocated jj/git workspaces … hooks, attributes, git gc; not keep-ref lifetime". The quote is about `git gc` in a colocated repo, i.e. inside that scope, so the row is the right locator — no new row is needed.
3. The quote is load-bearing, not decoration: entry step 7 (l.78-80) uses it for a *negative* claim — jj does not guarantee that running `git gc` in a colocated repo is safe, so the entry's own `git gc` invocations must be read as measured, not as sanctioned. Dropping it would delete that caveat from an admitted entry, which append-only discipline forbids.
4. The pairing is machine-checked in both directions by `tools/souji-registry-agreement.py` K1 (`cited-not-in-used-by` and `used-by-no-cite`), so one half alone is a defect. Reproduced below (red before, green after).

Placement: the line goes **inside the existing `## Round 31 wave-2 corrections (append-only)` section**, not into the front matter. Both readers accept it there — `tools/souji-registry-agreement.py` matches `^(- )?source:` and `tools/souji-gate-check.py` matches `^\s*(?:[-*]\s*)?source:\s*(S\d{3,})` over the whole file, not only the front matter — and this keeps the entry a byte-suffix of its round-31 blob, so the append-only property survives. (A front-matter insertion after the S054 line would also pass both readers but would break byte-append-only; it is not needed.)

### Exact text appended to `corpus/knowledge/jj-dropped-keep-object-lifetime.md`

Append after the current last line (l.247, the bullet starting `- Qualifies the S063 citations for the config fragment:`), as three new bullets plus the declaration bullet, in this order:

```markdown
- Declares S051 where the entry quotes its bytes: the Gate bullet for `jj docs/git-compatibility.md` v0.45.1 (lines 52-53) cites a file whose registry row is S051 (`corpus/SOURCES.md`:72) and no `source:` line named it, so the entry was not traceable to that row. The quote stays — S051's own scope cell includes `git gc` in a colocated workspace and step 7's caveat is what those bytes say — and the fix is the appended `- source: S051` line below plus the S051 `used-by` cell, which now names this entry.
- source: S051 — jj Git compatibility at tag v0.45.1 — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/git-compatibility.md — § Supported features:11 and the colocated-gc bullet at lines 52-53 — snapshot census/round-31/sources/git-compatibility.md, sha256 0fb71f992b0ed05d547e597d3f5f1cd33ed9e5d56a4e4e4cb851ba30c766c641
- Adds the CONFIGURATION anchor to S063's registry cell (`corpus/SOURCES.md`:84) and supersedes the bullet above's clause `scopes the page to § NOTES first paragraph`: the anchor cell now reads `§ NOTES first paragraph; § CONFIGURATION gc.pruneExpire, gc.reflogExpire and gc.reflogExpireUnreachable, whose text git-gc(1) includes from Documentation/config/gc.adoc at tag v2.56.0 — config/gc.adoc lines 96-147, re-opened 2026-10-26, 181 lines, 7753 B, sha256 0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a`. No dedicated row is opened (the round-31 Gate's decision) and the scope cell is unchanged, because its own teaches clause already reads `once a ref is gone its objects become prunable after the prune date`; the anchor was the only gap.
- Adds the `gc.recentObjectsHook` Gate quote that the bullet above records as missing: `Documentation/config/gc.adoc` at tag v2.56.0 (https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc, opened 2026-10-26, 181 lines, 7753 B, sha256 0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a) lines 144-145 — 'Interpret their output as object IDs which Git will consider as "recent", regardless of their age.' — with lines 145-146 continuing 'By treating their mtimes as "now"' and lines 141-143 defining the key as the shell command run when deciding 'whether or not to remove an object'; the file's own inner quotation marks are kept verbatim under single outer delimiters. The hook is the mtime clock claim 4 sources, and no arm of `census/round-31/records/jj-object-clock-run.txt` sets or measures it, so claim 4's keeper stays sourced rather than measured.
```

Notes for the applier:
- No line above contains a pipe character.
- The documented locator is `§ Supported features:11` and the quote spans `:52-53 — this matches the already-appended correction at entry l.244 ("no such heading — the bullet … sits under `## Supported features` (`:11`) and the quoted sentence spans lines 52-53"), so the two bullets agree.
- Inner double quotes are the file's bytes; the outer delimiters are single quotes only to avoid nesting ambiguity. Quoted spans are 16, 6 and 7 words.

### Registry cell (logged old -> new)

`corpus/SOURCES.md`:72, column `used-by` (last cell):

- old: `corpus/knowledge/jj-colocation-receipts.md`
- new: `corpus/knowledge/jj-colocation-receipts.md, corpus/knowledge/jj-dropped-keep-object-lifetime.md`

No other S051 cell changes.

---

## (b) S063: add the CONFIGURATION anchor to the same row; no dedicated row

Decision: **anchor cell append on S063**, no new row. The round-31 Gate refused a dedicated row for `Documentation/config/gc.adoc` ("no new row (cite `S063`)", `corpus/lessons/round-31.md` Gate), and the S063 `teaches` cell already asserts the prune date ("once a ref is gone its objects become prunable after the prune date"), so the row's declared content already reaches these keys — only the anchor was missing.

`corpus/SOURCES.md`:84, column `anchor` (7th field):

- old:

```
web manual "git-gc last updated in 2.52.0", "2.53.0 → 2.56.0 no changes", opened 2026-10-20; § NOTES first paragraph
```

- new:

```
web manual "git-gc last updated in 2.52.0", "2.53.0 → 2.56.0 no changes", opened 2026-10-20; § NOTES first paragraph; § CONFIGURATION gc.pruneExpire, gc.reflogExpire and gc.reflogExpireUnreachable, whose text git-gc(1) includes from Documentation/config/gc.adoc at tag v2.56.0 — config/gc.adoc lines 96-147, re-opened 2026-10-26, 181 lines, 7753 B, sha256 0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a
```

Scope, `teaches`, `status`, `opened`, `recheck` and `used-by` cells: unchanged. The anchor mirrors the entry's own S063 `source:` line (l.2), which already names `§ CONFIGURATION gc.pruneExpire, gc.reflogExpire and gc.reflogExpireUnreachable … Documentation/config/gc.adoc at tag v2.56.0 lines 96-147`.

---

## (c) `gc.recentObjectsHook` Gate quote

Fetched by this seat, not taken from a record:
`https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc` → 181 lines, 7 753 B,
sha256 `0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a`, byte-identical to the committed
`census/round-31/sources/gc.adoc` (`cmp` identical).

Located quote, lines 144-145, 16 words, no pipe:

> 'Interpret their output as object IDs which Git will consider as "recent", regardless of their age.'

Supporting spans on the same bytes: lines 141-143 `whether or not to remove an object` (the key is a decision hook),
lines 145-146 `By treating their mtimes as "now"` (the same mtime clock `gc.pruneExpire` reads).

The quote lands as the last appended bullet in (a) above; it is not inserted into the Gate section, because the Gate
section is admitted text and the entry is append-only.

---

## Run (scratch clone, edits committed there; scratch deleted before this seat finished)

Tool: `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-registry-agreement.py --root <scratch clone> --rev <commit> --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`.

**The tool's own entry point could not evaluate at this list-rev** — control run at lane HEAD
`7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`, before any edit:

```
COULD-NOT-EVALUATE derived facts are trivial
rc=2
```

Cause, reproduced directly: its `facts()` runs the digest-pinned `census/round-29/c2-counter.py` at `--list-rev` and
requires a non-zero `failed`; the frozen r26 counter now prints `r26 records=1381 failed=0`, so the triviality guard
trips before K1 is evaluated. Same at the fixed commit (`rc=2`, identical message). This is an r29-tool limitation at
r32's prereg revision, not a fault in the edits; it is reported as finding 5 below.

So K1 was evaluated by importing that same file unmodified and calling its own `k1()` at the same two revisions
(scratch driver, ~20 lines, no logic copied).

Red before — commit A, entry declares `- source: S051` but S051's `used-by` cell is untouched:

```
K1 cited-not-in-used-by S051 corpus/knowledge/jj-dropped-keep-object-lifetime.md
SUMMARY k1=1 rev=526a162debf900b3889a358f5accc7b1ac936ca9 list_rev=3ec84fc81b3243429c834a051880b0bcde06291c
rc=1
```

Green after — commit B, same clone, both halves plus the S063 anchor and the appended bullets:

```
SUMMARY k1=0 rev=98c9af913500d18229528d27c53b2e7250745e0c list_rev=3ec84fc81b3243429c834a051880b0bcde06291c
rc=0
```

(Scratch commit hashes are disposable: the clone lived under `/fast/scratch/hyaku/souji-r32/Defect2Fix/` and is gone.)

Independent checks on the same commit B:

- `scripts/sources-census.sh validate --file <clone>/corpus/SOURCES.md` → `rc=0`, `file ok …`, 36 W04 lines and
  **0 E-class lines**; the lane's own `corpus/SOURCES.md` control gives the same `rc=0` and the same 36 W04. So the two
  cell edits change no census class.
- `git diff` of `corpus/SOURCES.md` between lane HEAD and commit B touches exactly lines 72 and 84, each a single-cell
  edit; `teaches`, `status`, `opened` and `recheck` are byte-identical.
- Regex used by the two readers over commit B's entry: `source:` ids = `S222 S063 S002 S117 S220 S054 S051`.
- Each quoted span is a whitespace-normalised substring of the committed snapshot bytes it names (checked for all four
  spans), and each is ≤ 25 words with no pipe.

## Files the L1 applies

1. `corpus/knowledge/jj-dropped-keep-object-lifetime.md` — append the four bullets of (a).
2. `corpus/SOURCES.md` — `:72` used-by cell, `:84` anchor cell (old -> new above).
3. `census/round-32/records/` — a touched-row log entry for the two cells, per the lane's r31 convention.

Nothing else: no SCORECARD row, no record, no counter, no fixture, no LOG/SKILL/PROVINCE text.
