# S69ScoutSources — independent re-verification of the round-69 candidate sources S302 / S303

Scope: re-open the two admitted candidate sources, re-derive every number from committed bytes.
Nothing outside my seat directory and my scratch dir was written; no lane tracked file was edited;
no git/jj mutation was run in the lane or the fleet repo.

Scratch: `/fast/scratch/hyaku/souji-r69/scout-sources` (fresh dir, `mktemp -d` fixtures inside it,
`rm -rf` at the end of each fixture; `git rev-parse --show-toplevel` asserted equal to the fixture
dir before the first commit). Tooling: **nothing installed or upgraded** — stdlib only
(`html.parser`, `bs4 4.15.0` already present in the image). No pacman/`uv`/`npm` action was taken.

## Item 1 — fresh sha256 vs the lane's recorded values: AGREE, byte-for-byte

Commands (run from my scratch dir):
```
curl -sS -o git-status.fresh.html https://git-scm.com/docs/git-status   # HTTP 200, 99934 bytes
curl -sS -o git.fresh.html        https://git-scm.com/docs/git            # HTTP 200, 244227 bytes
sha256sum git-status.fresh.html git.fresh.html
```
Observed (my fresh values):
`af1fbb494104a6bcbfb44d65f8d75b2dad850fc9e9b5d43501cc2a6c995f58f6  git-status.fresh.html`
`534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1  git.fresh.html`
These equal the lane's recorded values byte-for-byte (`census/round-69/srcs/S-opening.txt:3-4,7-8`;
frozen `git show 1412037c9fac1cd18381075d22fefbac06ae5bac:census/round-69/srcs/S-opening.txt`).
`cmp` against the committed captures `census/round-69/srcs/git-status.html` and
`census/round-69/srcs/git-manual.html` → **identical**; the pages did not change since the lane's
fetch. No sha256 mismatch, so no drift finding. The pages are the ones the round admits.

## Item 2 — quote bytes and word counts: quotes VERIFIED; the frozen counts/offsets do NOT reproduce

Method: the lane's own canonical extraction, `census/round-66/sources/recipe.py` (copy at
`S69ScoutSources/recipe-lane-r66-canonical.py`), applied to the fresh bytes. Control: it reproduces
the lane's committed artifact `census/round-66/sources/git-environment.txt` **byte-for-byte**
(sha256 `624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035`, 58863 bytes) — so the
recipe and the fetch are the lane's own. Then whitespace-normalised search.

| item | quote (as recorded) | present? | byte offset in lane-recipe stripped text | words (whitespace split) |
|---|---|---|---|---|
| S302 git-status(1) | "Scripts running status in the background should consider using git --no-optional-locks status" | YES | **17905** (normalised; source lines at 17891 / 17962) | **12** |
| S303 git(1) | "require locks. This is equivalent to setting the GIT_OPTIONAL_LOCKS to 0" | YES | **11261** (normalised; source lines at 11221 / 11284) | **11** |

Both quotes are exact substrings of the whitespace-normalised tag-stripped text (verified against
the fresh fetch and against the committed `census/round-69/srcs/*.html`). Both are ≤25 words under
every convention (11/12 words as quoted; 16/17 words for the full source sentences) — the ≤25-word
rule holds.

Findings:
- **MEDIUM — frozen word counts do not reproduce.** Frozen `S-opening.txt:5` says "16 words" and
  `:9` says "14 words" for the two quoted strings; the quoted strings contain 12 and 11 words
  (`wc -w` on the quoted bytes). The frozen counts are the counts of the *source sentences*, not of
  the strings the file quotes. The L1's uncommitted working-tree amendment already restates 12 and
  11 — my independent count agrees with the amendment exactly. Benign for the rule (≤25 either way).
- **MEDIUM — the frozen byte offsets do not locate the quotes.** Frozen `S-opening.txt:5` cites
  "byte 18440"; the S303 registry locator cited 11933. Under the lane's own recipe the quotes sit
  at 17905 and 11261 (delta −535 / −672). I swept ~200 extraction variants (tags→space/empty/
  newline, unescape before/after, whitespace-collapse modes, script/style drop, header/nav/footer
  drop, nbsp handling, bs4 html.parser+lxml, `html.parser` join, `sed`/`perl` strip, bs4 with and
  without separators): **0 variants** reproduce 18440 or 11933; closest are 18532 (delta +92) and
  11957 (delta +24). In the **raw** page bytes 18440 is site chrome (a `red-dot.png` image) and
  11933 is a nav sidebar link — neither is the quote (raw quote positions 93859 and 102674). The
  offsets are unreproducible pointers, not merely off-by-N. The L1's working-tree amendment has
  already dropped them ("offset not reproduced across extractions, so not cited"); my sweep
  independently confirms that decision and supplies the reproducible offsets above.
- **LOW — the "->" in the version list is a transcription.** The page bytes carry the UTF-8 arrow:
  `2.54.0 → 2.56.0 no changes` (U+2192). `S-opening.txt:3` writes ASCII `->`, so that string is not
  byte-verbatim on the page.

## Item 3 — does git-status(1) document GIT_OPTIONAL_LOCKS; is the quote in BACKGROUND REFRESH: AGREE

- `grep -c GIT_OPTIONAL_LOCKS` on the fresh git-status page = **0**. The page never names the
  variable; it mentions "optional-locks" exactly once, in the quoted advice. The S302 registry
  cell ("GIT_OPTIONAL_LOCKS is not named on this page") is **correct**.
- The quoted sentence **is** in §BACKGROUND REFRESH: raw h2 ids are `_background_refresh` (93059) and
  the next `_untracked_files_and_performance` (94160); the quote is at raw 93859, between them. AGREE.

## Item 4 — D18 named limit: GROUNDED, but the registry's teaches cell INVERTS the documented direction

What the docs actually say:
- git-status(1) §BACKGROUND REFRESH: "the lock held during the write may conflict with other
  simultaneous processes, causing them to fail" — the failures are attributed to *other* processes;
  the page never says git status itself fails, and neither page contains the string "index.lock".
- git(1) §ENVIRONMENT VARIABLES GIT_OPTIONAL_LOCKS: setting it false makes git "complete any
  requested operation without performing any optional sub-operations that require taking a lock",
  and it "will prevent git status from refreshing the index as a side effect."

My independent probe (fixture repo, stale index, held `.git/index.lock`, `git status --porcelain`,
`GIT_TRACE2_EVENT` + `GIT_TRACE=1`):
| case | rc | stdout | stderr | trace2 `do_write_index` |
|---|---|---|---|---|
| pin UNSET, no lock held | 0 | ` M f.txt` | (only the GIT_TRACE line) | **2** (index written) |
| pin UNSET, lock HELD | 0 | ` M f.txt` | empty | **0** (write skipped, no failure) |
| pin SET (0), no lock held | 0 | ` M f.txt` | empty | **0** |
| pin SET (0), lock HELD | 0 | ` M f.txt` | empty | **0** |

So the prereg's D18 wording — "git status attempts no optional index-write lock under a held
index.lock" (`preregistration.txt:18-19,99-100`) and "the index.lock probe (P2) shows git status rc 0
with empty stderr with and without the pin" (`:111-113`, and
`census/round-69/probes/lock-and-commondir-probe.txt:3`) — is **reproduced**: git status does not
fail under a held lock, with or without the pin, and the pin changes no observable. The D18 named
limit is **GROUNDED, not overreaching**. Mechanism confirmed in git's own source (v2.56.0
`builtin/commit.c:1635,1657`): the optional lock is taken without `LOCK_DIE_ON_ERROR`, so a held
lock fails softly and the index update is skipped rather than fatal.

- **HIGH — the S302 registry teaches cell inverts the documented failure direction.**
  `corpus/SOURCES.md:259` (working tree, uncommitted) teaches: "Background git status may fail on a
  lock another process holds". The page says the opposite direction: status's own write-lock may
  make *other simultaneous processes* fail. The docs never claim status fails on another's lock, and
  my probe shows status returns rc 0 with empty stderr when a lock is held. The knowledge entry
  (`corpus/knowledge/battery-outcome-split.md:36-37`) states the page's direction correctly, so the
  registry row is the outlier.
- **LOW — the epistemic hedge is now resolvable.** `battery-outcome-split.md:38-41` says the output
  "cannot tell a skipped lock from no attempt". Plain stdout/stderr indeed cannot, but
  `GIT_TRACE2_EVENT` does: under a held lock `do_write_index` is 0, identical to the pin-set case,
  proving the write is *skipped* (never attempted) rather than attempted-and-failed. The named limit
  stands; only the "undocumented on this host" framing is now partly resolvable.

## Item 5 — page header versions vs the measured git version: AGREE

`git --version` → **git version 2.56.0** (host).
- git-status(1): header "git-status last updated in 2.53.0", version list "2.54.0 → 2.56.0 no
  changes" → the git-status manual is unchanged from 2.53.0 through 2.56.0, so it applies to the
  measured 2.56.0. AGREE.
- git(1): header "git last updated in 2.56.0" → matches the measured version exactly. AGREE.
(Note: the already-mined row `corpus/SOURCES.md:235` S275 records the same URL at 244355 bytes /
sha256 `0c126da2…` as of 2026-11-03; today's bytes are 244227 / `534c674f…`. The page did change
between 11-03 and 11-05 — the round-69 S303 row pins its own fresh hash, so it is unaffected.)

## Extra finding — frozen prereg internal inconsistency (not in my seat's brief, reported)

- **MEDIUM — `preregistration.txt:25` says "battery-manifest.tsv 27 mutants"; the file holds 26
  mutants** (27 lines including the header). The outcome tally of those 26 rows is exactly
  18 forgery + 5 label-only + 2 over-refusal + 1 echo-violation = 26, matching the C1 predicate at
  `:47-48` ("26-mutant manifest", `BATTERY mutants=26 …`). Line 25 appears to have counted the
  header row. Benign for the C1 numbers (they reconcile), but a frozen receipt number that does not
  reproduce is a defect on its face.
- The D18 control receipt `census/round-69/controls/d18-limit-battery.txt` does carry 47 CASE lines
  and `MUTANT D18 outcome=survived` — consistent with `preregistration.txt:111-112`.

## Verdict summary

| item | verdict |
|---|---|
| 1 sha256 | **AGREE** — both hashes reproduce exactly; committed captures identical to fresh fetch |
| 2 quote bytes | quotes **VERIFIED** verbatim; frozen word counts (16/14 vs 12/11) and byte offsets (18440/11933) **do not reproduce** |
| 3 GIT_OPTIONAL_LOCKS on git-status / BACKGROUND REFRESH | **AGREE** on both |
| 4 D18 named limit | **GROUNDED** (not overreaching); but the S302 registry teaches cell **inverts** the documented direction → **HIGH** |
| 5 header vs git 2.56.0 | **AGREE** on both pages |

Findings: HIGH ×1 (S302 registry teaches cell inverts the doc's failure direction);
MEDIUM ×4 (frozen word counts; frozen byte offsets unreproducible; prereg manifest count 27 vs 26;
S303 locator labels a "GLOBAL OPTIONS" section that exists on neither the served page nor in
`Documentation/git.adoc` at v2.56.0 — the quote's real section is OPTIONS, raw h2 `_options` at
90637, dt anchor `Documentation/git.txt---no-optional-locks` at 102674; `grep -c "GLOBAL OPTIONS"`
= 0 on the served page, 0 in git.adoc v2.56.0, 0 in git.txt v2.30.0 and v1.8.0, and absent from
`man git` on this host); LOW ×2 (ASCII `->` vs U+2192 arrow; the "cannot tell a skipped lock from no
attempt" hedge is resolvable with GIT_TRACE2).

## Files written under my seat directory

- `.ufo/waves/round-69/w1/S69ScoutSources.md` (this report)
- `.ufo/waves/round-69/w1/S69ScoutSources/receipts.txt` — fresh sha256/size, byte-identical cmp
  results, lane-recipe stripped-text hashes, quote offsets, host git version
- `.ufo/waves/round-69/w1/S69ScoutSources/git-status.stripped.txt` — lane-recipe text of the
  git-status page (21138 bytes, sha256 `63248a62387ae946…`)
- `.ufo/waves/round-69/w1/S69ScoutSources/git.stripped.txt` — lane-recipe text of the git(1) page
  (58863 bytes, sha256 `624e85efcf2f2eb7…`; identical to the lane's committed artifact)
- `.ufo/waves/round-69/w1/S69ScoutSources/recipe-lane-r66-canonical.py` — copy of the lane's
  canonical extraction recipe, for reproduction
