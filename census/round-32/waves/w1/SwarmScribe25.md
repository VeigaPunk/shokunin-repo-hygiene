# SwarmScribe25 — r32 w1: draft append-only fixes for r31 closure defect 2

STATUS: PASS — decided and drafted all three parts of routed defect 2 (S051 citation, S063 CONFIGURATION anchor, `gc.recentObjectsHook` quote) with exact appended text, and proved the S051 pairing with the lane's own registry-agreement K1 (red then green) in a scratch clone; the tool's own entry point could not evaluate at r32's prereg revision, which is reported as finding 4.

Lane tree read: `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`; prereg `3ec84fc81b3243429c834a051880b0bcde06291c`; lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`. No lane file was modified; all experiments ran in `/fast/scratch/hyaku/souji-r32/Defect2Fix/` (deleted).

## Evidence

**Subject read** — the three cells the defect names, at lane HEAD:

```
$ awk -F'|' 'NR==72{print $12} NR==84{print $7}' corpus/SOURCES.md
 corpus/knowledge/jj-colocation-receipts.md
 web manual "git-gc last updated in 2.52.0", "2.53.0 → 2.56.0 no changes", opened 2026-10-20; § NOTES first paragraph
```
Entry `source:` ids before the fix: `S222 S063 S002 S117 S220 S054` — S051 absent while the entry quotes its bytes at the Gate bullet (`jj docs/git-compatibility.md v0.45.1 … line 52`) and at step 7 (l.78-80).

**(a) S051 — cite, do not drop.** Grounds opened this run: `corpus/lessons/round-31.md` `## Gate`, S051 row — "an L1 correction adds S051 to the entry's `source:` lines and its used-by cell, or the quote leaves the entry" (20 words); `corpus/SOURCES.md`:72 scope — "colocated jj/git workspaces … hooks, attributes, git gc; not keep-ref lifetime", which is exactly the quoted sentence's subject; and the quote carries entry step 7's negative claim that jj calls that safety untested, so dropping it would delete a caveat from admitted text. Exact appended text is in the delivery file; placement is inside `## Round 31 wave-2 corrections (append-only)` because both readers accept any `- source:` line (`tools/souji-registry-agreement.py:52` `^(- )?source:`; `tools/souji-gate-check.py:40` `^\s*(?:[-*]\s*)?source:\s*(S\d{3,})`) and the entry then stays a byte-prefix of its r31 blob — measured `base=29421 rev=31936 startswith=True`.

**(b) S063 — anchor append, no dedicated row.** The r31 Gate refused a separate row for `Documentation/config/gc.adoc`, and S063's `teaches` cell already asserts the prune date, so only the anchor was missing. Old -> new (7th field, `:84`) in the delivery file; `scope`, `teaches`, `status`, `opened`, `recheck`, `used-by` unchanged. The new anchor mirrors the entry's own S063 `source:` line (l.2).

**(c) `gc.recentObjectsHook`.** Fetched by this seat: `https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc`, 181 lines, 7 753 B, sha256 `0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a`; `git show HEAD:census/round-31/sources/gc.adoc | cmp - <fetch>` → identical. Lines 144-145, 16 words, no pipe: `Interpret their output as object IDs which Git will consider as "recent", regardless of their age.` Supporting spans: lines 141-143 `whether or not to remove an object` (7 words), lines 145-146 `By treating their mtimes as "now"` (6 words). All four spans (with the S051 quote) are whitespace-normalised substrings of the committed snapshot bytes they cite.

**Verification run** — scratch clone of the lane, `origin` removed, throwaway identity set with `git -C` inside scratch, `TMPDIR` under scratch.

The tool's entry point, control at lane HEAD before any edit:

```
$ python3 -B tools/souji-registry-agreement.py --root <clone> --rev 7a6667cd… --list-rev 3ec84fc8…
COULD-NOT-EVALUATE derived facts are trivial
rc=2
```
Cause reproduced directly: its `facts()` runs the digest-pinned `census/round-29/c2-counter.py` at `--list-rev` and needs a non-zero `failed`; that counter now prints `r26 records=1381 failed=0`. Same `rc=2` at the fixed commit, i.e. the edits are not the cause.

K1 therefore evaluated by importing the same file unmodified and calling its own `k1()`:

```
# commit A: entry declares "- source: S051" only, used-by cell untouched
K1 cited-not-in-used-by S051 corpus/knowledge/jj-dropped-keep-object-lifetime.md
SUMMARY k1=1 rev=526a162debf900b3889a358f5accc7b1ac936ca9 list_rev=3ec84fc81b3243429c834a051880b0bcde06291c
rc=1
# commit B: + S051 used-by, + S063 anchor, + appended bullets
SUMMARY k1=0 rev=98c9af913500d18229528d27c53b2e7250745e0c list_rev=3ec84fc81b3243429c834a051880b0bcde06291c
rc=0
```

(Scratch hashes are disposable; the clone was deleted.)

Cross-checks at commit B: `scripts/sources-census.sh validate --file <clone>/corpus/SOURCES.md` → `rc=0`, `file ok`, 36 W04 lines, 0 E-class lines, identical to the control on the lane's own `corpus/SOURCES.md` (`rc=0`, 36 W04); `git diff --numstat` on `corpus/SOURCES.md` = `2 2` in 2 hunks (lines 72 and 84 only), registry row count 253 → 253; entry diff has 0 deleted lines.

Not run: the r32 counters (C1/C2/C3), the lane gates, any landing. Their interaction with these edits is [INFERENCE] except C3's L11, whose subject (`corpus/SOURCES.md` via `sources-census.sh validate`) is the validator I did run.

## Findings

1. The defect-2(a) fix must land as a pair: entry `- source: S051` bullet **and** S051's `used-by` cell. One half alone is caught by `tools/souji-registry-agreement.py` K1 as `cited-not-in-used-by` (reproduced, commit A above). Location: `corpus/SOURCES.md`:72, `corpus/knowledge/jj-dropped-keep-object-lifetime.md` (append).
2. Dropping the quote is the wrong branch: it removes step 7's caveat that jj does not guarantee `git gc` safety in a colocated repo, from admitted text. Location: entry l.78-80 (`corpus/knowledge/jj-dropped-keep-object-lifetime.md`).
3. S063 needs no dedicated row and no scope change — the `teaches` cell already reads "once a ref is gone its objects become prunable after the prune date". Location: `corpus/SOURCES.md`:84, 7th field.
4. `tools/souji-registry-agreement.py` cannot evaluate at r32's `--list-rev 3ec84fc8…`: `facts()` requires a non-zero r26 `failed` and the frozen counter now reports `failed=0`, so `main()` exits 2 (`COULD-NOT-EVALUATE derived facts are trivial`) and K1 is never printed. Any seat told to verify with this tool will hit the same wall. Reproduced state above; it is an r29-tool limitation at this revision, not an attack on a frozen r32 counter. Location: `tools/souji-registry-agreement.py:98-117` (`facts`, triviality guard at `:116`), control run at `7a6667cd…`.
5. Companion gap, not part of defect 2's letter and therefore not drafted: S051's `anchor` cell lists only the round-17 sections (`§ Colocated workspaces, :115, :158, :229`) and never names `:52-53`, the sentence the entry actually quotes. A stricter-only completion would append to that cell: `; re-opened 2026-10-26 at the same tag: § Supported features:11, :52-53 the colocated git gc sentence (12284 B, sha256 0fb71f99…)`. Location: `corpus/SOURCES.md`:72, 7th field.
6. The entry's last r31 correction bullet (l.247) says S063's cell "scopes the page to `§ NOTES first paragraph`"; after the anchor edit that clause is stale, so the applied bullet set supersedes it explicitly rather than leaving two contradictory sentences. Location: entry l.247 vs the appended third bullet.

## Attack log

Not an attack seat. Finding 4 is a reproduced instrument limitation, not a counter attack; no frozen r32 predicate, target, counter or item set is disputed.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-defect2-fix.md` — decisions (a)(b)(c), exact appended entry text, both registry old -> new cells, and the verification transcript with the tool's own `rc=2` limitation.
- `.ufo/waves/round-32/w1/SwarmScribe25.md` — this report.

Out of scope, not touched: SCORECARD rows, any record, any counter or fixture, LOG/SKILL/PROVINCE/QUALITY text, the untracked `census/round-32/measure.sh` another seat owns, and everything outside `souji-shokunin/`. No tool was installed or upgraded (none was needed; nothing ran through pacman).
