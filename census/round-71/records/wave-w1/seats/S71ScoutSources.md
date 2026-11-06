# S71ScoutSources — round-71 sources falsification (S306–S310)

Seat: S71ScoutSources. Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Scope: re-open the round-71 sources live; check `corpus/SOURCES.md` rows S306–S310.
Tooling: no install, no upgrade (no tool was needed; curl + python3 + git 2.56.0 suffice).

## 1. Fetch receipts (live, fresh)

`curl -sS -L -o <name>.html -w '%{http_code}' https://git-scm.com/docs/<name>` (twice, from
`/fast/scratch/hyaku/souji-r71/S71ScoutSources`):

| page | HTTP | bytes | sha256 | == committed capture |
|---|---|---|---|---|
| gitattributes | 200 | 131046 | 0a1e80158ac05e237f2626fbe047b93460b9291a8da96e893774ade8a9665aee | YES |
| git | 200 | 244227 | 534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1 | YES |
| git-config | 200 | 830605 | 37aa8407b12e377a38f523d5012835d0515cc82f2249c942b9e5cff656019226 | YES |

`cmp` against `census/round-71/srcs/{gitattributes,git,git-config}.html`: byte-identical.
All three sha256 values match the rows' `source` cells and `census/round-71/srcs/*.html`
(sha256sum: 0a1e8015…, 534c674f…, 37aa8407…). `census/round-70/srcs/git-manual.html` and
`census/round-71/srcs/git.html` are the same bytes — S307's "byte-identical to the S304
capture" holds.

Normalization is reproducible: `html.unescape(re.sub(r'<[^>]+>',' ',t))` then
`re.sub(r'\s+',' ',t)` (no strip) reproduces `census/round-71/srcs/*.txt` **byte-for-byte**
(49087 / 59452 / 335077 bytes; `out == committed` True for all three). Every cited offset
below is a **character** offset into that `.txt`; byte offsets differ (+60…+132) because of
non-ASCII in the page.

## 2. Located quotes — offsets, sections, word counts

All five quotes are exact at their cited offsets; all word counts ≤ 25.

| row | file | cited offset | found at | words | section (from raw HTML heading chain) | row claim of section |
|---|---|---|---|---|---|---|
| S306 | gitattributes.txt | 17513 | 17513 (exact) | 15 | h2 EFFECTS → h3 Checking-out and checking-in → **h4 filter** (raw 74478) | "EFFECTS, filter" — AGREE |
| S307 | git.txt | 13322 | 13322 (exact) | 20 | h2 OPTIONS → **dt `Documentation/git.txt---attr-sourcelttree-ishgt`** (raw 105824) | "OPTIONS, dt --attr-source" — AGREE |
| S308 | git-config.txt | 82016 | 82016 (exact) | 17 | h2 CONFIGURATION FILE → h3 Values → h3 **Variables** → dt `…git-config.txt-corefileMode` (raw 303316) | "Variables, core.fileMode" — AGREE |
| S309 | git.txt | 40119 | 40119 (exact) | 10 | h2 **Environment Variables** → dt `…git.txt-spanclasssynopsiscodeGITATTRSOURCEcodespan` (raw 205941) | "ENVIRONMENT VARIABLES, dt GIT_ATTR_SOURCE" — AGREE (heading text is title-case "Environment Variables") |
| S310 | git-config.txt | 53875 | 53875 (exact) | 23 | h3 **Variables** → dt `…git-config.txt-attrtree` (raw 231980) | "Variables, attr.tree" — AGREE |

## 3. Row shape / status / used-by

All five rows have **11 columns** (`|`.split → 13 fields incl. empties) — correct per the
`SOURCES-CONTRACT-v1` table (id, source, kind, tier, scope, anchor, teaches, status, opened,
recheck, used-by). Status values `mined, mined, mined, rejected, queued` are all in the
corpus vocabulary. Recheck values `180d, 180d, 180d, on-release, 90d` are all in vocabulary.
Base 8b9345b had 228 rows, 52e8c3f has 233 (+S306–S310); **no pre-existing row's cell changed**
(diffed all 11 cells × 228 rows → 0 changes), matching the lesson's "228 → 233" claim.

## 4. Per-row verdicts

**S306 — AGREE.** Quote exact (15 words). gitattributes(5) "filter" states the clean command
"is used to convert the contents of worktree file upon checkin". `teaches` says a configured
clean driver "rewrites worktree bytes before git compares them". **The page does not say
this**: `compares`/`when comparing`/`clean filter is applied` = 0 hits; the page's only
comparison sentence is about textconv ("A textconv, by comparison, is much more limiting").
The mechanism is real but is stated by the page only as a *checkin* effect; the status
comparison behaviour is a **git implementation** fact, not a doc sentence. Same wording in
`corpus/knowledge/filter-filemode-witness.md:12` ("git compares the *cleaned* bytes"). Flagged
LOW: teaches-cell over-reaches its cited page; the witness is the probe
(`census/round-71/probes/attr-filemode-probe-base.txt` P2/P3), not gitattributes(5).

**S307 — AGREE.** Quote exact (20 words). Page says --attr-source reads "instead of the
worktree" and is "equivalent to setting the GIT_ATTR_SOURCE environment variable"; `teaches`
("replaces the worktree attributes for every git call that inherits it") is supported.

**S308 — AGREE.** Quote exact (17 words), `core.fileMode` entry: "Tells Git if the executable
bit of files in the working tree is to be honored." `teaches` says a per-call `-c` pin
overrides it — git-config(1) SCOPES lists "the -c option" as the `command` scope, and git(1)
OPTIONS: "-c <name>=<value> … The value given will override values from configuration files."
I verified the behaviour: repo-local `core.fileMode=false` → `status --porcelain` empty;
same repo with `-c core.fileMode=true` → ` M f.txt`.

**S309 — DISAGREE on the reject reason; the reject is over-stated (MEDIUM).**
The row claims the ENVIRONMENT entry "names the tree but not that it replaces the worktree
attributes". **That part is true** — the entry reads only "GIT_ATTR_SOURCE Sets the treeish
that gitattributes will be read from." But the row's own `teaches` cell and the
`flip` condition are wrong: the claim "the variable replaces the worktree attributes" **is**
grounded on the *same page*, at the OPTIONS `--attr-source` entry, which says "Read
gitattributes from <tree-ish> **instead of the worktree**" and is "equivalent to setting the
GIT_ATTR_SOURCE environment variable" (S307 quotes exactly this). S309 is therefore not a
separate rejected candidate with an open flip; it is a **duplicate anchor of S307's page**,
and the ENVIRONMENT entry is a *different* fact (it names the treeish, not the worktree
replacement). Rejecting it is defensible as de-duplication, but the row's stated reason
("the entry names the tree but not that it replaces the worktree attributes") inverts the
actual state of the evidence: the *entry* lacks the sentence, but the *page* has it and the
r71 writer relies on it. Also `flip: a release adds that sentence here` is wrong — the
sentence already exists on the page, in OPTIONS. Correct reason: "duplicate of S307 on the
same capture; the ENVIRONMENT entry names the treeish only."

**S310 — DISAGREE (HIGH). Three defects.**

1. **Wrong cell — `used-by` points at a file that does not exist at the revision.**
   `used-by: corpus/lessons/round-71.md`. That path is **ABSENT at 52e8c3f** (and at
   1c2239cd, and at base 8b9345b); the file exists only as an untracked worktree file
   (`git ls-files` → 0). The lane's own registry tool says so:
   `tools/souji-registry-agreement.py` k1 → **`K1 used-by-missing S310 corpus/lessons/round-71.md`**
   (new at 52e8c3f; base k1 has 5 findings, none of them S310). This breaks QUALITY Q62
   ("every row's `used-by` path must exist at the revision and name that row id").
2. **Wrong cell — `used-by` also misses the entry that cites it.**
   `corpus/knowledge/filter-filemode-witness.md:1` lists S310 in its `source:` front matter,
   but S310's `used-by` does not name that file → k1
   **`K1 cited-not-in-used-by S310 corpus/knowledge/filter-filemode-witness.md`** (also new).
   Q62 requires bidirectionality. (S306/S307/S308 are correct in both directions.)
3. **The row's `teaches` cell is materially wrong, and the row is mis-statused.**
   It says the writer's check-attr read "honor it (**unmeasured**)". It is **measurable, and
   I measured it**: on git 2.56.0 a repository-local `attr.tree` naming a tree that carries
   `.gitattributes` with `filter=xx` is honoured by `git check-attr` **and hides the edit from
   `git status`**: fixture with `attr.tree=<tree>`, `filter.xx.clean="sed s/v2/v1/"`,
   worktree `v2` vs committed `v1` → `status --porcelain` is **empty**; and the **base writer
   writes a receipt over it** (`RECORD … rc=0`, `EXIT=0`) — i.e. `attr.tree` is a *live forgery
   route* of exactly the S306/S307 class. The r71 **candidate** writer refuses it
   (`RECEIPT-FILTER-DRIVER-SET`) because its `check-attr` read also honours `attr.tree`.
   So the round's own r71 probe never covered `attr.tree` (a **named limit** in
   `census/round-71/preregistration.txt:100`), while the row asserts the opposite
   ("the writer's check-attr reads honor it (unmeasured)") and the knowledge entry repeats
   the omission at `corpus/knowledge/filter-filemode-witness.md:39-40` ("the writer's
   `check-attr` read honors both, but no matrix row measures either" — true of the *matrix*,
   but the parenthetical in S310 says the *behaviour* is unmeasured, and it is measured here).
   Also note git-config(1) states the precedence the row's scope claims but never quotes:
   "When the GIT_ATTR_SOURCE environment variable or --attr-source command line option are
   used, this configuration variable has no effect." (git-config.txt offset 54097, 18 words)
   — which **contradicts** the writer's r71 scrub design in one direction (a caller
   `GIT_ATTR_SOURCE` makes `attr.tree` inert, so scrubbing `GIT_ATTR_SOURCE` *re-enables*
   `attr.tree`). The row's scope cell promises "the variable's precedence against
   GIT_ATTR_SOURCE" but the quoted anchor does not carry it.
   **Recommendation: S310 should be `mined`, not `queued`** — it is a real, doc-grounded,
   now-measured route; or the teaches cell must be corrected and a matrix row added.

## 5. Frozen-claim re-derivation (independent runs)

| arm | command (abridged) | observed | verdict |
|---|---|---|---|
| C1 candidate | `c1-counter.py --root … --matrix … --base-rev 8b9345b1… --rev a1db6c85… --tool tools/souji-receipt-write.py --work $S/c1` | `SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=0` | REPRODUCES |
| C1 do-nothing | same with `--new-tool census/round-71/controls/base-writer-8b9345b1.py` | `new_forgeries=7 … class_mismatches=7` / `EXIT=1` | REPRODUCES (= controls/c1-do-nothing.txt) |
| counter selftest | `c1-counter.py --selftest …` | `SELFTEST cases=39 pass=39 fail=0` / `EXIT=0` | REPRODUCES |
| writer selftest | `tools/souji-receipt-write.py --selftest --work $S/wst` | `SELFTEST cases=40 pass=40 fail=0` | REPRODUCES |
| C2 after | `c2-harness.py --label c2-after-r71 --counter census/round-71/c1-counter.py … --mutants census/round-71/c2-mutants.json` | `SUMMARY label=c2-after-r71 positive_selftest=PASS x_mutants=5 x_killed=5 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0` / `EXIT=0` | REPRODUCES |
| C2 before | `--label c2-before-r70 --counter census/round-70/c1-counter.py --matrix census/round-70/c1-matrix.tsv --base-rev e063a2fc…` | `SUMMARY label=c2-before-r70 … x_killed=0 x_survived=5 … score=5` / `EXIT=1` | REPRODUCES (= controls/c2-before-r70.txt) |

I re-ran the counter independently rather than trusting the committed receipts; all six
SUMMARY/EXIT pairs match the committed records byte-for-byte. **C1 and C2 as frozen both hold.**

## 6. Findings

- **HIGH** — S310 `used-by: corpus/lessons/round-71.md` does not exist at 52e8c3f (untracked
  file). k1: `K1 used-by-missing S310 corpus/lessons/round-71.md`. Violates QUALITY Q62.
- **HIGH** — S310 `used-by` omits `corpus/knowledge/filter-filemode-witness.md`, which cites
  S310 at its `source:` line. k1: `K1 cited-not-in-used-by S310
  corpus/knowledge/filter-filemode-witness.md`. Violates Q62 bidirectionality.
- **HIGH** — S310 `teaches` says the writer's check-attr honouring of `attr.tree` is
  "unmeasured"; it is measurable and I measured it: `attr.tree` + configured clean driver
  makes `git status` report a clean tree over a changed file, and the **base writer writes a
  receipt** over it (`EXIT=0`). The r71 candidate refuses it
  (`RECEIPT-FILTER-DRIVER-SET`), but no matrix row measures it and the r71 probe never
  covered it (`preregistration.txt:100` names it a limit). S310 should be `mined`, and a
  matrix row for `attr.tree` is missing.
- **MEDIUM** — S309's reject reason and flip are wrong: the page (git(1) OPTIONS
  `--attr-source`) already carries "instead of the worktree" + "equivalent to setting the
  GIT_ATTR_SOURCE environment variable"; S309 is a duplicate of S307's anchor, not a page
  lacking the sentence. Correct reason: duplicate anchor of S307; the ENVIRONMENT entry
  names the treeish only.
- **MEDIUM** — S310's scope promises "the variable's precedence against GIT_ATTR_SOURCE" but
  the quoted anchor carries no precedence; the sentence exists at git-config.txt offset 54097
  (18 words): "When the GIT_ATTR_SOURCE environment variable or --attr-source command line
  option are used, this configuration variable has no effect." It also means the writer's
  `GIT_ATTR_SOURCE` scrub *re-enables* `attr.tree` rather than neutralising it.
- **LOW** — S306 `teaches` ("rewrites worktree bytes before git compares them") asserts a
  status-comparison mechanism gitattributes(5) does not state (0 hits for
  compare/compares/applied). The witness is the probe, not the page.
- **LOW** — cited offsets are **character** offsets into `census/round-71/srcs/*.txt`; byte
  offsets differ by +60…+132 (non-ASCII). Rows do not say which; a byte-offset reader will
  mis-locate every quote. The S304 precedent (`census/round-66/sources/git-environment.txt`
  "byte offset") suggests byte offsets were the earlier convention.
- No tooling installed or updated (nothing needed).

## 7. Files written

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-71/w1/S71ScoutSources.md`
  (this report)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-71/w1/S71ScoutSources/`
  — receipts: `fetch-receipts.tsv`, `quote-locations.tsv`, `runs.tsv`,
  `registry-k1.txt`, `attr-tree-probe.txt`
Scratch `/fast/scratch/hyaku/souji-r71/S71ScoutSources` removed on completion.
