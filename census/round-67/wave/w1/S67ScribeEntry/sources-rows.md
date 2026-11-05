# SOURCES.md registry rows — round 67 (round-67 w1, seat S67ScribeEntry)

**STATUS: the row this seat was asked to draft was landed by the L1 before this seat delivered.**
S300 was appended in `e41f022f0dd018390fa68c7edab1dff734fcfc4f` (2026-11-05 13:48:45 -0300). S298 and S299
were pre-existing and were **not** re-added (correctly — the round adds no S298/S299 row).

What this file therefore delivers is: (a) the **S300 row as landed**, verified against the contract and the
census; (b) the **S298 `used-by` correction the landing still owes**, with the controlled measurement that
proves it is the correction; and (c) the audit trail for both.

---

## 1. Row count, before and after

Census command (`SOURCES-CONTRACT-v1` § Census, run from the lane root):

```sh
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
```

* **BEFORE (round start, freeze `4c61efcb`): 222**
* **AFTER (S300 appended, `e41f022f`): 223**

Malformed-row check (11 columns ⇒ NF=13) → **0** at the landed revision.
Duplicate-id check → empty. Enum checks (E05 kind / E06 tier / E07 status / E08 opened / E09 recheck) → clean.

Fleet census, run by this seat against the landed lane:

```
$ bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
… (W04 duplicate-URL warnings — all pre-existing, status-neutral)
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md      rc 0
```

---

## 2. S300 — the new row, as landed

Verbatim from `corpus/SOURCES.md` at the landed revision (cell 12 is the empty trailing cell):

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S300 | git setup.c common-dir resolution and git(1) § ENVIRONMENT VARIABLES at tag v2.56.0 — https://raw.githubusercontent.com/git/git/v2.56.0/setup.c ; https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git.adoc | code | A | GIT_COMMON_DIR as an environment route in git 2.56.0: whether a caller-set value is consumed as the repository's common directory, and in what form (scope: common-dir resolution only; not submodule or worktree export) | tag v2.56.0; accessed 2026-11-05; HTTP 200; captures census/round-67/wave/w1/S67ScoutSources/setup.txt (sha256 8316b1ad…) and doc-git.txt (sha256 050c5330…); whitespace-normalized quote match re-verified at landing; located quotes census/round-67/wave/w1/S67ScoutSources/quotes.tsv | `const char *git_env_common_dir = getenv(GIT_COMMON_DIR_ENVIRONMENT);` (setup.c, function get_common_dir; 13 words) — teaches: a caller-set GIT_COMMON_DIR is used as given, ahead of the commondir file; and the git(1) contract `If this variable is set to a path, non-worktree files that are normally in $GIT_DIR will be taken from this path instead.` (22 words, git.adoc) | mined | 2026-11-05 | on-release | corpus/knowledge/common-dir-route-receipt-writer.md |

### 2.1 Contract conformance, cell by cell

| contract requirement (SOURCES-CONTRACT-v1) | landed value | verdict |
|---|---|---|
| `id` — `S` + 3+ digits, the next unused, never reused | `S300`; the highest pre-existing id was S299 | ok |
| `source` — title — canonical URL | title + two canonical raw URLs at tag v2.56.0 | ok |
| `kind` ∈ enum | `code` | ok |
| `tier` ∈ A\|B\|C | `A` (upstream source at a pinned tag is authoritative for this scope) | ok |
| `scope` — the claim or topic the tier applies to | states the scope AND its exclusion ("common-dir resolution only; not submodule or worktree export") | ok |
| `anchor` — exact section/heading/page/line **plus revision** | `setup.c` function `get_common_dir`, tag v2.56.0, with the capture digests and the quotes.tsv pointer | ok |
| `teaches` — one grounded learner benefit | the env value is used as given, ahead of the commondir file; plus the git(1) contract | ok |
| `status` ∈ queued\|mined\|rejected | `mined` — the row's `used-by` path (`corpus/knowledge/common-dir-route-receipt-writer.md`) exists at the landing revision and the entry cites the row | ok |
| `opened` — ISO date | `2026-11-05` | ok |
| `recheck` — ISO date or cadence | `on-release` | ok |
| `used-by` — repo-relative paths of the entries citing the row, comma-separated | `corpus/knowledge/common-dir-route-receipt-writer.md` | ok |
| no `|` inside any cell | 11 cells, NF=13, no embedded pipe | ok |

### 2.2 The anchor's `teaches` quote, re-verified by this seat

The `teaches` cell's first quote is

> `const char *git_env_common_dir = getenv(GIT_COMMON_DIR_ENVIRONMENT);`

Its stated provenance is `setup.c`, function `get_common_dir`, 13 words. Measured by this seat:

* the 13-word form
  `const char *git_env_common_dir = getenv(GIT_COMMON_DIR_ENVIRONMENT); if (git_env_common_dir) { strbuf_addstr(sb, git_env_common_dir); return 1; } else { return get_common_dir_noenv(sb, gitdir); }`
  is at **`setup.txt` byte offset 9038**, line **310** (`int get_common_dir(struct strbuf *sb, const char *gitdir)`),
  and the shorter one-line form is at **offset 9040**, line **312**;
* `setup.txt` sha256 `8316b1ad961ac6b1fa29dfdf1094a344aec8673f6637e6c00ba913a6668fc589`, 83214 bytes —
  **byte-identical** to this seat's independent fetch of
  `raw.githubusercontent.com/git/git/v2.56.0/setup.c` (HTTP 200);
* the git(1) contract quote in the same cell is 22 words (≤25) and is at `doc-git.txt` offset **19977**
  (whitespace-normalized match, verified).

The scout's own `quotes.tsv` row for `setup.txt` @ 9038 (`get_common_dir`, 21 words) re-slices **EXACT** at the
stated offset. All 25 scout quote rows re-slice EXACT except one (§2.3).

### 2.3 One located-quote row whose stated offset does not reproduce as a raw byte offset

Re-slicing all 25 rows of the scout's `quotes.tsv` with a whitespace-collapsing byte matcher:

```
24/25 EXACT
1 DELTA:  environment.html @ 189753 → match at 189853 (delta +100)
```

The 100 bytes before the sentence in the raw HTML are the anchor markup
(`…/docs/git.txt-GITCOMMONDIR"></a><span class='synopsis'><code>GIT_COMMON_DIR</code></span> </dt>`); the
sentence itself is present exactly once in the capture. The landed lesson's Gate already states that the match
test is whitespace-normalized because "line breaks and tabs in the capture defeat the scout's byte offsets" —
so the landed statement is true. The **disclosure gap** is that the Gate does not name the single row where the
stated offset and the raw match differ by 100 bytes. A reader who runs a raw byte-equality test over all 25 rows
sees 24/25 and has no note explaining the 25th.

**Recommendation (a lesson note, not a row edit):** name that row and its 100-byte delta next to the Gate's
existing whitespace-normalization sentence.

---

## 3. S298 and S299 — EXISTING, not re-added (and the correction S298 still owes)

Neither row was re-added; the landing diff on `corpus/SOURCES.md` touched exactly one line:

```
$ git diff 4c61efcb… 11a96e07… -- corpus/SOURCES.md | grep -E "^[+-]\| S(298|299|300)"
+| S300 | git setup.c common-dir resolution and git(1) § ENVIRONMENT VARIABLES at tag v2.56.0 — …
```

S298 and S299 are unchanged rows:

| id | source | kind | tier | status | used-by |
|---|---|---|---|---|---|
| S298 | git(1) § ENVIRONMENT VARIABLES — https://git-scm.com/docs/git | docs | A | mined | corpus/knowledge/caller-env-routes-receipt-writer.md |
| S299 | git-config(1) § ENVIRONMENT, § FILES, § SCOPES, core.excludesFile — https://git-scm.com/docs/git-config | docs | A | mined | corpus/knowledge/caller-env-routes-receipt-writer.md |

### 3.1 The gap: the landed entry cites S298, but S298's `used-by` does not name it

The landed entry's front matter cites **S298 and S300**:

```
$ git show HEAD:corpus/knowledge/common-dir-route-receipt-writer.md | grep -o "S[0-9]\{3\}" | sort -u
S298
S300
```

`S300`'s `used-by` names the entry. **`S298`'s does not.** QUALITY Q62 requires the binding in **both**
directions, and the lane's own `souji-registry-agreement` gate (registered at `SKILL.md:265`) enforces it in its
K1 arm: "every S### cited in the front-matter `source:` lines of a corpus/knowledge/*.md entry must be a row
whose `used-by` lists that entry."

Measured at the landed revision and at the current tip:

```
K1 cited-not-in-used-by S298 corpus/knowledge/common-dir-route-receipt-writer.md   ← introduced by r67
K1 cited-not-in-used-by S251 corpus/knowledge/control-chronology-binding.md          ← pre-existing
K1 cited-not-in-used-by S251 corpus/knowledge/freeze-record-substance-binding.md    ← pre-existing
K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md              ← pre-existing
K1 cited-not-in-used-by S110 corpus/knowledge/quarantine-restore-path-reoccupied.md  ← pre-existing
```

The same call at the **freeze** revision (`4c61efcb`, before any r67 paperwork) prints **4** findings — the four
pre-existing ones. **The r67 landing added the fifth, and it is the round's own entry.**

### 3.2 The correction

`SOURCES-CONTRACT-v1` rule 2 permits exactly one in-place edit to an existing row — **"Only `status`, `recheck`
and `used-by` change in place, and each change is logged old→new in the round lesson."** The correction is a
one-cell edit to S298's `used-by` plus the old→new log line in the lesson's Gate. Nothing else changes.

```
-| S298 | … | mined | 2026-11-05 | on-release | corpus/knowledge/caller-env-routes-receipt-writer.md |
+| S298 | … | mined | 2026-11-05 | on-release | corpus/knowledge/caller-env-routes-receipt-writer.md, corpus/knowledge/common-dir-route-receipt-writer.md |
```

**Measured in a fixture (never the lane).** Fixture repo created under this seat's scratch
(`D=$(mktemp -d -p /fast/scratch/hyaku/souji-r67/S67ScribeEntry)`; `git init -q`;
`git -C "$D" rev-parse --show-toplevel` asserted equal to `$D` before the first commit), carrying the freeze
revision's `corpus/SOURCES.md`, the r66 entry, the r67 entry and the appended S300 row. The K1 arm was run
against two committed states of that fixture:

| fixture state | K1 findings mentioning S298/S299/S300/common-dir |
|---|---|
| **A** — S300 row + r67 entry present, **S298 `used-by` not extended** | `K1 cited-not-in-used-by S298 corpus/knowledge/common-dir-route-receipt-writer.md` — **the landed defect reproduces exactly** |
| **B** — same, with S298's `used-by` extended by one cell | **none.** (The only remaining hits are `used-by-missing S124/S125/S126`, artifacts of the fixture not carrying `corpus/knowledge/git-repo-structure-common-dir.md`.) |

Two constraints the L1 must respect:

1. **Extend S298 only.** The r67 entry does **not** cite S299. A fixture state with S299's `used-by` extended
   and S299 uncited produces the mirror finding `K1 used-by-no-cite S299 corpus/knowledge/common-dir-route-receipt-writer.md`.
   Measured; do not extend S299.
2. **Log the change old→new.** The sentence that the correction makes false is in **`corpus/README.md:990`** —
   the r67 frontier section's sources bullet: *"S300 added (…, rc 0, 223 rows). **S298/S299 unchanged.**"* The
   contract's rule 2 requires the old→new to be logged in the round lesson; the landed LOG entry already has a
   **"Corrections (append-only; the frozen files are not edited)"** bullet, which is its natural home. Both
   places should be updated: the README bullet (it becomes false) and the lesson/LOG correction log.

### 3.3 Neither gate that ran at landing would have caught this

* `tools/souji-landing-gate.py` does **not** invoke the registry-agreement arm — `grep -n "registry-agreement"`
  in that tool returns nothing. The arm is registered in `SKILL.md:265` as a separately invoked gate.
* `scripts/sources-census.sh validate` passes at the landed revision (rc 0, `ok`) because its `E11` check only
  verifies that a **`mined`** row's `used-by` paths **exist on disk**. It does not check the reverse direction
  (that a row's `used-by` names an entry that actually cites it).

So the gap is invisible to both gates that ran; only the K1 arm sees it. That is the reason to run the K1 arm
explicitly before the round closes.

---

## 4. Row-shape checklist for the S300 row, machine-verified by this seat

| check | command | result |
|---|---|---|
| cell count | `awk -F'|' '/^\| S300 /{print NF}' corpus/SOURCES.md` | **13** (11 columns + 2 empty edge cells) |
| no pipe inside a cell | field split yields 13, all fields accounted for | ok |
| id format | matches `^S[0-9]{3,}$` | ok |
| id not duplicated | `awk … \| sort \| uniq -d` | empty |
| kind enum | `code` ∈ enum | ok |
| tier enum | `A` | ok |
| status enum | `mined` | ok |
| opened ISO date, not future | `2026-11-05`, today `2026-11-05` | ok (E08 does not fire) |
| recheck cadence | `on-release` ∈ symbolic cadences | ok |
| used-by path exists at the landing revision | `corpus/knowledge/common-dir-route-receipt-writer.md` is a blob at `e41f022f` | ok (E11 does not fire) |
| the used-by entry cites the row | the entry's `source:` line names `S300` | ok (K1 satisfied in that direction) |
| the entry's cited rows name the entry in `used-by` | S300 ✔ / **S298 ✘** | **S298 fails — see §3** |
| duplicate URL across scopes | census W04 warnings only, pre-existing class | status-neutral |

---

## 5. Notes for the L1

1. **Apply the S298 `used-by` correction** (§3.2) and log the old→new in the lesson's Gate.
2. **Do not extend S299's `used-by`** — the entry does not cite it, and extending it produces a new K1 finding.
3. **Record the `environment.html` quote-offset delta** (+100 bytes) in the Gate next to the existing
   whitespace-normalization note (§2.3).
4. **S300's `teaches` cell names two quotes in one cell** (the `setup.c` line and the git(1) contract sentence).
   This is inside the contract's one-benefit rule — both halves teach the same fact ("a caller-set value is used
   as given") — but a reader counting "one grounded line" against two quoted spans should be pointed at the
   Gate's two-bullet quote list, which separates them by capture.
5. **The `source` cell carries two URLs separated by ` ; `.** `SOURCES-CONTRACT-v1` says "canonical URL or DOI"
   (singular) but several pre-existing rows carry two (e.g. S009, S222, S223), and the census's `E04`
   duplicate-URL check reads the first URL only, so it does not fire. Status-neutral; noted for the record.
