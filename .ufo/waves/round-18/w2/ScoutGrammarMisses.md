STATUS: DONE — C2 recall attacked at 5efb519; 1 missed dangling citation found (SKILL.md:110, `.ufo/quarantine/...`), 7 other grammar-invisible citation classes tested and cleared; the recorded numbers reproduce exactly.

# ScoutGrammarMisses — C2 recall (round 18, wave 2)

Attacked claim: C2 calibration at `5efb519f00075d958c3d1109ef6fcb24c487eb87` — the landing gate's pointer grammar sees every evidence pointer in the authority files, so `LG-DANGLING-PTR` is 0 at the tip (b576341: 10 findings; tip: 0). Scope: `SKILL.md`, `SCORECARD.md`, `PROVINCE.md`, `corpus/README.md`, `corpus/QUALITY.md`, `corpus/lessons/round-18.md`.

Confidence language: **OBSERVED** = reproduced from copied source or read from git; **INFERENCE** = reasoning from those facts.

## Method (read-only; no lane code executed, no census/gate binary run)

I copied the gate's pointer grammar verbatim from `tools/souji-landing-gate.py` at the tip (`POINTER_ROOTS` :122, `POINTER_PATH_RE` :124-128, `_trim_pointer_token` :700, `_normalize_pointer_path` :710, `_pointer_paths` :718-749, `_safe_pointer_path` :752, `check_pointers` :792-876) into a local replay, then ran it over the gate's declared source set at both revs (`SKILL.md`, `SHONEN.md`, `SCORECARD.md`, `PROVINCE.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/lessons/round-18*.md`, `corpus/knowledge/*.md`, LOG.md round-18 section only). In parallel I ran an independent broad tokenizer over the six assigned files (any `/`-bearing or dotted token, any context), and tested every candidate with `git cat-file -e`, then lane-tree stat and fleet-root stat.

Reproduction of the claims (OBSERVED):

- b576341, full declared source set: **319 pointer tokens, 3 fleet, 9 LG-DANGLING-PTR**, plus the 1 `LG-FROZEN-MEASURED` = the recorded **10** findings. This is byte-for-byte the findings list in `census/round-18/gate-pointers-before-b576341.json` (`checked_ptrs: 319`, `ptr_fleet: 3`). The six-file subset at b576341 gives the same 5 findings the record attributes to those files (`SKILL.md:110,163,165`, `corpus/README.md:81,216`).
- 5efb519, full declared source set: **445 tokens, 3 fleet, 0 LG-DANGLING-PTR**. The "after: 0" claim holds for the grammar-defined token set (pointer class only; frozen-measured/stale classes are outside this slice — see Remaining unknowns).

## Finding F1 — missed dangling citation: SKILL.md:110, `.ufo/quarantine/...` (OBSERVED)

`SKILL.md:110` (identical bytes at b576341 and 5efb519) says: "The r16 stub `tests/vault/vadv54-run/p/p6repo/.git` is quarantined at `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub`".

Evidence:

- Grammar output for that exact line is exactly one token: `tests/vault/vadv54-run/p/p6repo/.git` (the exempted source). The destination is invisible because `POINTER_PATH_RE` only accepts `census|tests|tools|corpus|.ufo/waves/`; the inner `tests/` substring is preceded by `/`, which the `(?<![A-Za-z0-9_./<>*])` lookbehind rejects.
- `git -C … cat-file -e 5efb519f…:.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub` → **rc 128**, `fatal: path '.ufo/quarantine/round-17/…/dot-git-empty-stub' exists on disk, but not in '5efb519…'`. Same at b576341 (rc 128, "exists on disk, but not in 'b576341…'").
- `git ls-tree -r --name-only <rev> -- .ufo/quarantine .ufo/scopes` → **0 entries at both revs**; `git ls-files .ufo/quarantine` → 0 (directory is untracked; git also cannot track the empty directory itself).
- On disk it is an empty directory: `stat` → `inode=30073199 size=0 mtime=2026-10-18 14:51:47`, matching LOG.md:946 ("moved to `.ufo/quarantine/round-17/…` (inode 30073199, empty)").
- It cannot be exempted: `load_pointer_exemptions` (`tools/souji-landing-gate.py:779`) requires `fields[0].startswith(POINTER_ROOTS)`. I simulated the natural row `".ufo/quarantine/…/dot-git-empty-stub<TAB>empty directory…"` — **rejected** (would raise `EvalError: malformed exemption row`).
- If the token were visible, `check_pointers` would flag it: tree absent, fleet-root `/home/vgpnk/Projects/shokunin/.ufo/quarantine/…` absent (`fleet_path` = path, :849-853), no exemption → `LG-DANGLING-PTR` (simulated loop returns True).
- Neither `tests/fixtures/r18-landing-pointers.py` (11 cases: skill-uncommitted-target, knowledge-committed-target, lesson-line-suffix-resolves, brace-one-missing, round-range-expands, placeholder-skipped, exemption-honored, malformed-exemption-exit2, round-17-no-pointer-finding, historical-b576341-round-18, …) nor the gate selftest contains any `.ufo/quarantine`, `.ufo/scopes` or `scripts/` case.

Impact on the claim numbers (INFERENCE from the above): the sentence names a second evidence location that is absent at the landing revision and unexempted — the same "deliberate non-file" class Q31 (`corpus/QUALITY.md:80`) requires to carry a reasoned exemption (cf. the `census/operator-sweep-20261019/` row). A recall-complete gate would report **11 findings at b576341** (not 10) and **1 at 5efb519** (not 0). The gate is blind here for two independent reasons: the root list omits `.ufo/quarantine/`, and the tree model cannot represent an empty, intentionally untracked directory.

## Grammar-invisible classes tested (no dangling target; gaps only)

- `.ufo/scopes/` — `SCORECARD.md:63` cites `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`. Absent at lane REV; **present at fleet root** (`/home/vgpnk/Projects/shokunin/.ufo/scopes/...`). Not dangling; if `.ufo/` were added to the root list, the existing fleet fallback (:849-853) would classify it `fleet`, not a finding.
- `scripts/` — `SKILL.md:130,131` (`$SHOKUNIN_ROOT/scripts/hyaku/jj-lane.sh`, fleet-qualified) and `corpus/lessons/round-18.md:43` (`scripts/sources-census.sh`, run with `--root /home/vgpnk/Projects/shokunin`). Both absent at lane REV, **present at fleet root**. Not dangling.
- Bare names (no known prefix) — `knowledge/...` ×8, `lessons/...` ×8 in `corpus/README.md`; ~12 bare `.ufo/waves/round-18/w1/*.md` report names in the lesson; `LOG.md`, `SCORECARD.md`, `QUALITY.md`, `SOURCES.md`, `AXES.md`, `CORPUS.md`, `LEARNING.md`, `cert-16.json`, `counts.json`, `seat-audit-w2.json`, `leak-count-live-1721.json`, `jj-receipts-*.txt`, `regenerate.py`. All resolve under their conventional directories at REV (e.g. `census/round-16/seat-audit-w2.json`, `corpus/knowledge/obsidian-ledger.tsv`, `tests/fixtures/r15-preservation-frozen/regenerate.py`). The only non-resolving bare names are `gate-replays-ddb7347.json`, `jj-receipts-ddb7347.txt`, `-ddb7347.json`; every occurrence is explicitly labelled "never committed" (SKILL.md:168, SCORECARD.md:14, QUALITY.md:80, lesson:7). **This is the prefix-drop bypass:** dropping `census/round-17/` makes a never-committed record name invisible — so the tip's 0 is achieved partly by prose form, not by resolution.
- Globs — `census/round-14/verification*.json` (3 matches), `census/round-17/jj-receipts-*.txt` (2), `corpus/knowledge/*.md` (7), `souji-shokunin/census/**` and `souji-shokunin/tests/**` (non-empty). All resolve at tip; `*` is skipped by `_pointer_paths` (:721). A glob matching zero paths would be silently clean.
- Elided `…` forms — 6 occurrences (SKILL.md:58, SCORECARD.md:51, QUALITY.md:39, lesson:6,27,43). None is a live evidence claim. The lesson's "`… / -ddb7347.json` at SKILL.md:166" is accurate **at b576341** (line 166 then held `` `seat-audit-r16-replay-base5fa6017.json` / `-ddb7347.json` ``) and the fixing is verified at tip (line 168 now cites `census/round-17/seat-audit-r16-replay-base5fa6017.json` / `…-4f48343.json`, with "was `-ddb7347.json`, never committed").
- `path:line` refs — 26 checked (QUALITY.md's lesson pointers, the four `## Seat-reported failures` `:1` refs, lesson:7/:60 `corpus/README.md:216`, `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148`, `LOG.md:916`). All lines are ≤ EOF and the content matches the claim (seat reports' line 1 is the STATUS line in all four). The trim regex (`_trim_pointer_token`, :700-708) strips `:N`, so line-level dangles are structurally invisible — no instance found here.
- `./`-prefixed citations — none in the six files. Latent hole: the lookbehind `(?<![A-Za-z0-9_./<>*])` rejects `./census/...`, so that very natural spelling would be skipped.
- Space-containing paths — 3 tracked paths contain spaces (`tests/vault/vadv-56/...`), none cited in the six files. The whitespace-terminated tokenizer would truncate rather than miss a cited one (false positive, not a recall hole) for these.
- Fleet/absolute/external — `/home/vgpnk/Projects/shokunin`, `/var/tmp/...`, `/proc/...`, `refs/jj/*`, `op://`, `~/.config/**`: out of the gate's declared scope and correctly non-lane.

## Verdict

**Partially fails on recall.** The recorded numbers are exact for the grammar-defined token set (independently reproduced 319/3/9 at b576341 and 0 at tip), and the disclosed limits (elided tokens, prefix-less prose, fleet working tree) are accurate. But C2's stated purpose — "authority files cite only evidence that exists at the landing revision" — is not enforced for `.ufo/quarantine/`, and SKILL.md:110 still cites a landing-revision-absent location as where the r16 stub "is quarantined", with no exemption and no possible exemption row under the current loader. The base record undercounts by one and the tip result is 1, not 0, for a recall-complete reading of Q31's own rule.

## Smallest fix

1. Add `.ufo/quarantine/` (or `.ufo/`) to `POINTER_ROOTS` and the `POINTER_PATH_RE` alternation. This is safe: `.ufo/scopes/…` and `.ufo/state/…`, `.ufo/watchdog.log` then resolve at the fleet root and are classified `fleet`, never findings.
2. Add one exemption row (valid once the root list includes it): `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub<TAB>empty directory, untrackable by git; working-tree quarantine disclosed at LOG.md:946 (inode 30073199)`.
3. Add a fixture case to `tests/fixtures/r18-landing-pointers.py`: an authority file citing a `.ufo/quarantine/...` path present only on disk must yield `LG-DANGLING-PTR`; the exempted row must suppress it. Without this the class stays un-failable.

If no root-list change is wanted, reword SKILL.md:110 to name the quarantine as untracked working-tree state (evidence pointer LOG.md:946) instead of asserting a location.

## Remaining unknowns

- I did not execute the gate binary (probe rule forbids it outside `/var/tmp`); the replay is a copied-source reimplementation. Its exact match to the recorded 319/3/9 (and to the six-file subset of the recorded findings) is the cross-check.
- Frozen-pin / `measured_commit` and exemption-staleness classes were only spot-checked: the r14 `record.json` exemption is used at tip (synthetic `0123456789…` does not resolve, `record_repo` is in exemptions), so no stale row is expected; not re-derived end-to-end.
- Other declared sources (`SHONEN.md`, knowledge entries, LOG.md r18 section) were replayed for the pointer class but not exhaustively triaged for non-pointer findings.
- Tool installs/updates: none.

Report: .ufo/waves/round-18/w2/ScoutGrammarMisses.md
