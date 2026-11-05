# Draft — `corpus/knowledge/common-dir-route-receipt-writer.md` (round 67)

**STATUS: SUPERSEDED BY THE L1 LANDING.** The L1 landed an entry at this exact path in commit
`e41f022f0dd018390fa68c7edab1dff734fcfc4f` ("round-67: knowledge entry (common-dir route, S300), registry row S300,
lesson (Gate, Mistakes M1-M10), …"), 2026-11-05 13:48:45 -0300 — while this seat was still gathering
evidence. The landed bytes are the authoritative artifact; this file is kept as the seat's audit trail and as
the corpus paperwork for the **remaining** gap the landing left open (see §5 below).

The landed entry: `corpus/knowledge/common-dir-route-receipt-writer.md`, 41 lines, blob `83ec89288e43d80c8f779337bbd12b2f8b07c303`
at `e41f022f`. Its front matter, its claims, and its named limits are **not** restated here: they are
committed bytes and this seat did not write them.

---

## 1. What this seat measured independently (the landed entry's factual base)

Every number below was measured by this seat in scratch, against committed bytes or the scout's captures.
Nothing here is asserted by the landed entry; it is the scribe-side check of it.

### 1.1 The upstream captures the entry leans on are byte-identical to the scout's

The scout seat delivered `.ufo/waves/round-67/w1/S67ScoutSources/` (16 files). This seat fetched the same
upstream files independently from `raw.githubusercontent.com/git/git/v2.56.0/` into its own scratch and compared
digests. **All six upstream source captures are byte-identical** between the two independent fetches:

| file | sha256 (both fetches) | bytes |
|---|---|---|
| `environment.c` (= scout `environment.txt`) | `5b52a5a123a6b340c78eb4762cfc6b3184c983a30106dfc7828efeff4127c5f3` | 20931 |
| `worktree.c` (= scout `worktree.txt`) | `da5c259a2c78724ac776ad4c21a493f24008ac24d3023f33d30034269b353ff2` | 31092 |
| `setup.c` (= scout `setup.txt`) | `8316b1ad961ac6b1fa29dfdf1094a344aec8673f6637e6c00ba913a6668fc589` | 83214 |
| `run-command.c` (= scout `run-command.txt`) | `5cdcbaccf88f6b6c36397dfe98da9f07e392664a6db79dad63d35ab6853d78b4` | 49361 |
| `repository.c` (= scout `repository.txt`) | `7fb5a64b7592aae4de61a5c2f9affad7e58029a59311207359d6769c11112730` | 12445 |
| `environment.h` (= scout `environment-h.txt`) | `6dc06c6a9167f72103759908c961da150eb6007fd3b135e8744ac8711bdbb90f` | 8738 |

The scout's `environment.html` (the live git(1) page, 244227 bytes) is sha256
`534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1` — **byte-identical to the round-66 capture
`census/round-66/sources/git-environment.html`**, i.e. the git(1) page did not change between the two rounds.

The scout's `doc-git.txt` (47005 bytes, sha256 `050c5330f1a231be22bee3db27c7ef90d8ba22bb7bd6c72c8bab462f6f0a1f79`) is the
upstream `Documentation/git.adoc` at tag v2.56.0, not the rendered page — the file name says `doc-git`, and its
bytes are the `.adoc`.

### 1.2 Every one of the scout's 25 located quotes re-slices

The scout's `quotes.tsv` has 25 rows. This seat re-sliced all 25 against the captured bytes with a
whitespace-collapsing byte matcher (the captures contain newlines and tabs inside the quoted spans, so a
raw byte-equality test is the wrong test):

```
python3 - <<'PY'
import csv, re
rows = list(csv.DictReader(open("quotes.tsv"), delimiter="\t"))
for r in rows:
    data = open(r["source_file"], "rb").read()
    qb   = r["quote"].encode()
    pat  = re.compile(rb"[ \t\r\n\f\v]+".join(re.escape(t) for t in qb.split()))
    m    = pat.search(data, int(r["byte_offset"]))
    print(r["source_file"], r["byte_offset"], "->", "EXACT" if m and m.start()==int(r["byte_offset"]) else "DELTA", m.start() if m else None)
PY
```

**24/25 EXACT** (the stated offset is where the quote starts, modulo whitespace runs). Every quote is ≤25 words
(max 25). One row is off:

> **`environment.html` @ 189753 → the match is at 189853, delta +100.**
> The stated offset is the byte where the sentence *begins* only in the whitespace-normalized view; in the raw
> HTML bytes the sentence starts at 189853 and the 100 bytes before it are the anchor markup
> (`…/docs/git.txt-GITCOMMONDIR"></a><span class='synopsis'><code>GIT_COMMON_DIR</code></span> </dt>`).
> This is a locator-label artifact, not a wrong quote: the sentence itself is exact and present once
> (`h.count(b"If this variable is set to a path, non-worktree files that are normally in $GIT_DIR")` → 1).

**Consequence for the landed paperwork:** the landed lesson's Gate says the located quotes were "verified by
whitespace-normalized match against the captures (line breaks and tabs in the capture defeat the scout's byte
offsets; the match is the check)". That statement is **correct and load-bearing** — it is exactly why the
`environment.html` row's stated offset does not reproduce as a raw byte offset. The landed lesson does not
name the one row where the stated offset and the raw match differ by 100 bytes; a reader who re-runs a raw
byte-equality test over all 25 rows would see 24/25, not 25/25. This is a disclosure gap, not a false claim.

### 1.3 The mechanism the entry describes, re-measured on the host

Host git 2.56.0 (`git --version` → `git version 2.56.0`). Fixture repo `D` under this seat's scratch;
`git -C "$D" rev-parse --show-toplevel` asserted equal to `D` before the first commit.

* A caller-set `GIT_COMMON_DIR` **is** consumed as the repository's common directory:
  `GIT_COMMON_DIR=$D/cd-copy git -C $D rev-parse --git-common-dir` → `$D/cd-copy`.
* Config reads follow it: with `cd-copy/config` carrying `[core] fileMode = false`,
  `GIT_COMMON_DIR=$D/cd-copy git -C $D config --get core.fileMode` → **`false`**, while
  `git -C $D config --get core.fileMode` → **`true`**.
* The tracked-mode-change hiding follows the same redirect: `git -C $D status --porcelain` → ` M f.txt`;
  under the redirect the ` M f.txt` line is **gone** (only the untracked copy dir remains).
* The object store follows it too: with a full copy redirect `cat-file -p <blob>` succeeds and prints the blob;
  after removing `cd-copy/objects` the same command fails (`fatal: not a git repository`) — the redirect moved
  the object store as well.
* The upstream code agrees: `setup.c:310-319 get_common_dir()` returns the env value verbatim when set
  (`strbuf_addstr(sb, git_env_common_dir); return 1;`), and `repository.c:153-167 repo_set_commondir()` stores it
  as `repo->commondir` with `repo->different_commondir = 1`.

### 1.4 The W2 shape the frozen matrix exercises, re-measured against the frozen counter

The frozen C1 counter (`census/round-67/c1-counter.py`, sha256 `69f11706…a136b2`) builds the W1/W2 fixture as a
**byte copy of the fixture repo's `.git` placed BESIDE the repo** (`shutil.copytree(…/.git, …/commondir-copy)`)
with `[core] fileMode = false` appended to the copy's `config`; the caller's `GIT_COMMON_DIR` points at that
copy. W1 additionally seeds a tracked `755→644` mode change on `tools/instr.sh`.

The committed do-nothing control (`census/round-67/controls/c1-do-nothing.txt`, header
`rev=3639087917eaeb28719d7603110a6ec22782100e`) measures at the base:

```
CASE W1 expect=refuse base=accept base_findings=- new=accept new_findings=-
CASE W2 expect=refuse base=accept base_findings=- new=accept new_findings=-
CASE W3 expect=accept base=accept base_findings=- new=accept new_findings=-
SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=2 new_honest=6 class_mismatches=2 regress=PASS
EXIT=1
```

**base_forgeries = 2 = exactly W1 and W2**; the two base forgeries are the common-dir redirect rows, matching
the frozen target `base_forgeries=2 base_honest=6`. W3 (equal value) is honest on the base, so the candidate
must keep accepting it — the Q22 value-aware shape, not a presence refusal.

### 1.5 The refusal value-shape, re-measured on the landed candidate

The landed candidate (`tools/souji-receipt-write.py` at `f70da577`, sha256 `b811ee2a…15a725`) implements
`_check_env_commondir(root)` at candidate lines 290-309:

* presence test first: `"GIT_COMMON_DIR" not in os.environ` → return (absent is fine);
* **empty value refuses** (`if value == "": refuse(mismatch)`);
* resolves the repository's own common dir through `git(root, "rev-parse", "--git-common-dir")` — i.e. through
  the scrubbing helper, so no writer git call reads the caller's value;
* compares `os.path.realpath(value)` against `os.path.realpath(os.path.join(root, out))`; mismatch refuses;
* refusal string is the frozen `RECEIPT-ENV-COMMONDIR-MISMATCH: GIT_COMMON_DIR is set in the writer's
  environment and does not resolve to this repository's common dir (value not shown); unset it and retry` —
  the **value is never printed** (the r66 sentinel F4 redaction rule);
* the call site sits after the `GIT_INDEX_FILE` presence check and before the rev-format check;
* `git()` scrubs `"GIT_COMMON_DIR"` alongside `GIT_DIR` and `GIT_WORK_TREE`.

### 1.6 The three W-rows, re-run against the landed candidate in this seat's scratch clone

The frozen counter was run against the landed candidate **in a scratch clone** (`--no-hardlinks` clone of the
lane under this seat's scratch; the lane tree was never written). Result:

```
SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=0 new_honest=6 class_mismatches=0 regress=PASS
EXIT=0
```

— the frozen target, met. Row detail: W1 base=accept / new=refuse `RECEIPT-ENV-COMMONDIR-MISMATCH`;
W2 base=accept / new=refuse `RECEIPT-ENV-COMMONDIR-MISMATCH`; W3 base=accept / new=accept.

### 1.7 The C2 side, re-measured at the pinned historical state

The r67 C2 counter was run at the pinned state `c13fbb4e1b563a78278ddc14316c20252e9a6ec22782100e` in the scratch
clone (read-only `git show` of committed bytes):

```
FINDING SCOPE-OVERREACH s5: stable wording: claim redirects_closed needs writer markers cdred; writer blob lacks them
MARKERS flag=1 inrun=1 env=1 unmerged=1 envcfg=1 envred=1 cdred=0
SUMMARY rows=5 findings=1 verdict=FAIL rev=c13fbb4e1b563a78278ddc14316c20252e9a6d8d
EXIT=1
```

Exactly one finding, kind `SCOPE-OVERREACH s5`, `rows=5 findings=1 verdict=FAIL`, `EXIT=1` — the frozen target.

**Kill power, re-run from the frozen bytes.** Both mutants were built by the frozen recipe
`census/round-67/c2-mutate.py` into this seat's scratch and run there:

| mutant | command | observed |
|---|---|---|
| declared counter | `--selftest` | `SELFTEST pass cases=17 fail=0`, `EXIT=0` |
| `reverted-rule` | `--selftest` | `SELFTEST-CASE m10-s5-assertion-line-not-live: findings=0 want=1 MISMATCH`; `SELFTEST pass cases=17 fail=1`; `EXIT=1` |
| `enum-weakened` | at pinned `c13fbb4e` | `MARKERS … cdred=0`; `SUMMARY rows=5 findings=0 verdict=PASS`; `EXIT=0` |

Both kill-power targets hold: the reverted rule fails the M10-bound selftest case, and the enum-weakened mutant
scores the finding clean at the pinned state (the finding is enumeration-driven).

The r66 counter's before arm is committed at `census/round-67/controls/c2-do-nothing-r66.txt`:
`SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0` at the same pinned state — the discrimination witness.

---

## 2. The preregistration digest transcription failures, re-measured

The frozen preregistration attempt history, read at each commit:

| attempt | file | commit | C1 Population digest length | value |
|---|---|---|---|---|
| 1 | `census/round-67/preregistration.txt` | `832a4d43` | **63** hex | `5d26b341…9fafdc1fdb302…a692` (truth minus one `f`) |
| 2 | `census/round-67/preregistration-attempt2.txt` | `b3aa70fe` | **63** hex | same 63-hex string as attempt 1 |
| 3 | `census/round-67/preregistration-attempt3.txt` | `d874bf0d` | **62** hex | truth minus `1f` |
| 4 | `census/round-67/preregistration-attempt4.txt` | `4c61efcb` | **64** hex | `5d26b341e4718ba1dc62b8bec2d6ba0d29fafdcf1fdb302d1435736cd976a692` = the measured `sha256sum` of the committed matrix blob |

The freeze checker reproduced both rejections, run in the scratch clone against the frozen commits:

```
$ python3 -B tools/souji-freeze-check.py --root . --prereg census/round-67/preregistration-attempt2.txt --rev b3aa70fe… --substance
FINDING C1 POPULATION-DIGEST census/round-67/c1-matrix.tsv has no sha256=<64 hex> in '…5d26b341…9fafdc1fdb302…a692'
SUMMARY claims=2 findings=1    EXIT=1

$ python3 -B tools/souji-freeze-check.py --root . --prereg census/round-67/preregistration-attempt3.txt --rev d874bf0d… --substance
FINDING C1 POPULATION-DIGEST census/round-67/c1-matrix.tsv has no sha256=<64 hex> in '…5d26b341…9fafdcfdb302…a692'
SUMMARY claims=2 findings=1    EXIT=1

$ python3 -B tools/souji-freeze-check.py --root . --prereg census/round-67/preregistration-attempt4.txt --rev 4c61efcb… --substance
SUMMARY claims=2 findings=0    EXIT=0
```

**One correction to the landed lesson's M1 row.** The landed lesson (`corpus/lessons/round-67.md` M1, at
`e41f022f`) states the attempt-2 length as **63 hex** and the attempt-3 length as **62 hex**, which this seat's
measurement **confirms exactly** (63 and 62). But the *preregistration's own header text* — frozen, never edited —
says something different:

> attempt-3 header: "the stated matrix sha256 carried a transcribed extra character (**65 hex**, rejected by the
> freeze checker POPULATION-DIGEST)"; attempt-4 header: "attempt 2 transcribed **65 hex** and attempt 3
> transcribed 62 hex by hand".

The frozen attempt-2 blob carries **63** hex, not 65. The lesson's M1 number is right; the frozen headers' "65
hex" is wrong. The two transcriptions are both *deletions* of truth characters, not an "extra character":
attempt-2/1 dropped the `f` at index 39 (`…9fafdcf**1**fdb…` → `…9fafdc**1**fdb…`), attempt-3 dropped `1f` at
index 40. Measured with a `difflib.SequenceMatcher` alignment against the true digest (see the scratch recipe).

**Why this matters and is not a nit:** the attempt-3 and attempt-4 headers are the *frozen, never-edited*
narrative of the defect, and the landed lesson quotes the freeze-check evidence without recording that the
frozen headers mis-stated the length. A reader who diffs the lesson's "63 hex" against the attempt-3 header's
"65 hex" sees a contradiction with no reconciling note. The lesson's *numbers* are correct; the *record* is
incomplete. The fix is a lesson note, not a prereg edit (the prereg is frozen).

### 2.1 The attempt-1 control-chronology defect, re-measured

Running the freeze checker at attempt 1 (`832a4d43`) in the scratch clone:

```
FINDING C1 POPULATION-DIGEST census/round-67/c1-matrix.tsv has no sha256=<64 hex> in '…'
FINDING C2 CONTROL-ADDED-NOT-BEFORE-FREEZE census/round-67/controls/c2-do-nothing.txt bytes are not present at any strict ancestor of freeze 832a4d438ab4
SUMMARY claims=2 findings=2
```

So attempt 1 carried **two** independent defects (the digest **and** the control chronology), which the attempt-2
header records as "the C2 do-nothing receipts landed in the same commit as the attempt-1 file (832a4d43), not
before it". The landed lesson's M6 row records the control-chronology half. Good.

### 2.2 A dangling attempt-2 blob exists outside `master`

`git log --all -- corpus/round-67/preregistration-attempt2.txt` returns two commits: the landed `b3aa70fe` and
**`5b57138076b7de3410aa9bce1ce83959e60eb94e`** (parent `832a4d43`, dated 2026-11-05 13:28:31 -0300), which is
**not an ancestor of `master`** and is in no branch. Its attempt-2 blob also carries 63 hex, so it is not a
different digest variant; it is a stray pre-landing attempt-2 commit (the same file content, added on top of
`832a4d43`). It is unreachable from any ref, so it cannot affect the freeze — but it is unreferenced history
that a reader of `--all` will encounter. Worth one line in the lesson's sweep, since the sweep is supposed to
account for the round's chronology.

---

## 3. The registry-agreement gap the landing left open — **this is the actionable finding**

### 3.1 The check

`tools/souji-registry-agreement.py` (registered in `SKILL.md` as the lane gate `souji-registry-agreement`,
`SKILL.md:265`) has a K1 arm that enforces a **bidirectional** citation binding (QUALITY Q62):

> "every `used-by` path of a SOURCES.md row must exist at REV and name the row id; every S### cited in the
> front-matter `source:` lines of a corpus/knowledge/*.md entry must be a row whose `used-by` lists that entry."

The landed entry's front matter cites **S298** and **S300**:

```
$ git show HEAD:corpus/knowledge/common-dir-route-receipt-writer.md | grep -o "S[0-9]\{3\}" | sort -u
S298
S300
```

`S300`'s `used-by` names the new entry (correct). **`S298`'s `used-by` does not.** The landing commit changed
exactly one line of `corpus/SOURCES.md` — the appended `| S300 | …` row — and left `S298`'s `used-by` cell
untouched:

```
$ git diff 4c61efcb… 11a96e07… -- corpus/SOURCES.md | grep -E "^[+-]\| S(298|299|300)"
+| S300 | git setup.c common-dir resolution and git(1) § ENVIRONMENT VARIABLES at tag v2.56.0 — …
```

(The `+`/`-` filter shows only the S300 addition: S298's row was not edited at all.)

### 3.2 The K1 arm at the landed revision

```
$ python3 - <<'PY'
import importlib.util, subprocess
spec = importlib.util.spec_from_file_location("ra", "tools/souji-registry-agreement.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
rev = subprocess.run(["git","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
for o in m.k1(".", rev, rev): print(o)
PY
```

At the **round-67 landing** (`11a96e07`, and unchanged at the current tip `36200ad8`):

```
K1 cited-not-in-used-by S298 corpus/knowledge/common-dir-route-receipt-writer.md   ← NEW, introduced by r67
K1 cited-not-in-used-by S251 corpus/knowledge/control-chronology-binding.md          ← pre-existing
K1 cited-not-in-used-by S251 corpus/knowledge/freeze-record-substance-binding.md    ← pre-existing
K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md              ← pre-existing
K1 cited-not-in-used-by S110 corpus/knowledge/quarantine-restore-path-reoccupied.md  ← pre-existing
```

At the **freeze** (`4c61efcb`, before any r67 paperwork) the same call prints **4** findings — the four
pre-existing ones. **The round-67 landing added the fifth**, and it is the round's own entry:

> **The r67 landing introduced one new K1 registry finding: the landed knowledge entry cites S298 in its
> front matter, but S298's `used-by` cell was not extended to name `corpus/knowledge/common-dir-route-receipt-writer.md`.**

### 3.3 The fix, and the controlled measurement that shows it is the fix

`SOURCES-CONTRACT-v1` rule 2 allows exactly one in-place edit to an existing row: **"Only `status`, `recheck` and
`used-by` change in place, and each change is logged old→new in the round lesson."** So the correction is a
one-cell edit to S298's `used-by`, plus the old→new log line in the lesson's Gate. Nothing else.

The edit, in the contract's own idiom (`SOURCES.md` rows are comma-separated in the `used-by` cell):

```
-| S298 | … | mined | 2026-11-05 | on-release | corpus/knowledge/caller-env-routes-receipt-writer.md |
+| S298 | … | mined | 2026-11-05 | on-release | corpus/knowledge/caller-env-routes-receipt-writer.md, corpus/knowledge/common-dir-route-receipt-writer.md |
```

**Measured, in a fixture (never the lane).** A fixture repo was created under this seat's scratch
(`D=$(mktemp -d -p /fast/scratch/hyaku/souji-r67/S67ScribeEntry)`; `git init -q`; `git -C "$D" rev-parse
--show-toplevel` asserted equal to `$D` before the first commit), populated with the freeze revision's
`corpus/SOURCES.md`, the r66 entry, the r67 entry, and the appended S300 row. The K1 arm was then run against
two committed states of that fixture:

| fixture state | K1 findings mentioning S298/S299/S300/common-dir |
|---|---|
| **A** — S300 row + r67 entry present, **S298 `used-by` NOT extended** | `K1 cited-not-in-used-by S298 corpus/knowledge/common-dir-route-receipt-writer.md` **(the defect reproduces exactly)** |
| **B** — same, with S298's `used-by` extended by one cell | **none** (the S298 finding is gone; the only remaining hits are `used-by-missing S124/S125/S126`, which are artifacts of the fixture not carrying `corpus/knowledge/git-repo-structure-common-dir.md`) |

State A reproduces the landed defect; state B clears it. The one-cell `used-by` edit is the whole fix.

Two notes the L1 must keep in view when applying it:

1. **Do not extend S299's `used-by` as well.** The r67 entry does **not** cite S299. A fixture run with S299's
   `used-by` extended and S299 not cited produces the mirror-image finding
   `K1 used-by-no-cite S299 corpus/knowledge/common-dir-route-receipt-writer.md`. Extend **S298 only**.
2. **S298's `used-by` change must be logged old→new**, per SOURCES-CONTRACT-v1 rule 2 (the change is logged
   old→new in the round lesson). The sentence the correction makes false is in **`corpus/README.md:990`** — the
   r67 frontier section's sources bullet: *"S300 added (…, rc 0, 223 rows). **S298/S299 unchanged.**"* The
   landed LOG entry already has a **"Corrections (append-only; the frozen files are not edited)"** bullet, which
   is the natural home for the old→new log.

### 3.4 Why the landing did not catch it

The lane's landing gate (`tools/souji-landing-gate.py`) does not run the registry-agreement arm — grep for
`registry-agreement` in that tool returns nothing; the arm is registered in `SKILL.md:265` as a separately
invoked gate. The fleet census (`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`)
also passes at the landed revision (rc 0, `ok`), because its `E11` check only verifies that a **`mined`** row's
`used-by` paths **exist on disk** — it does not check the reverse direction (that a row's `used-by` names an
entry which actually cites it). So neither gate catches the gap; only the K1 arm does.

---

## 4. Corpus/registry census at the landed revision

```
$ bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
… (W04 duplicate-URL warnings, all pre-existing)
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md      rc 0
```

Row count: **222 → 223** (S300 appended); malformed-row count (`awk … NF!=13`) → **0**; the S300 row's cell
count is **NF=13** (11 columns), `kind=code`, `tier=A`, `status=mined`, `opened=2026-11-05`, `recheck=on-release`
— every enum in `SOURCES-CONTRACT-v1` / the census's E05–E10 checks.

```
$ python3 -B tools/souji-coverage-agreement.py --root . --rev 36200ad8…
grounded=27 mapped=27 dangling=0 mismatches=0
```

---

## 5. What this seat recommends the L1 do next

1. **Apply the one-cell S298 `used-by` correction** (§3.3) and log the old→new where the contract's rule 2
   requires it — in the round lesson — using the landed LOG entry's existing **"Corrections (append-only; the
   frozen files are not edited)"** bullet. The sentence the correction makes false is in
   **`corpus/README.md:990`** (*"S298/S299 unchanged."*), which must be updated too.
2. **Add a lesson note** recording that the frozen attempt-3/attempt-4 headers state "65 hex" for attempt 2
   while the frozen attempt-2 blob carries 63 hex (§2) — the M1 numbers are right, the frozen narrative is not,
   and the difference is unrecorded.
3. **Disclose the one quote row whose stated offset does not reproduce as a raw byte offset**
   (`environment.html` @ 189753 → 189853, delta 100, §1.2), next to the Gate's existing note that the match
   test is whitespace-normalized.
4. **Optionally** record the dangling pre-landing commit `5b571380` in the lesson's chronology sweep (§2.2).

None of these is a claim change: C1 and C2 keep their frozen predicates, and the landed measurements stand.

---

## 6. Provenance of every measurement in this file

| what | how | where |
|---|---|---|
| upstream captures | independent fetch of `raw.githubusercontent.com/git/git/v2.56.0/{environment.c,worktree.c,setup.c,run-command.c,repository.c,environment.h}`, sha256 compared against the scout's captures | this seat's scratch, removed at yield |
| scout quote re-slice | 25/25 rows re-sliced with a whitespace-collapsing byte matcher over the captured bytes | scout `.ufo/waves/round-67/w1/S67ScoutSources/quotes.tsv` |
| mechanism probes | fixture git repo `D` under this seat's scratch; `git rev-parse --show-toplevel` asserted before the first commit; `GIT_COMMON_DIR` redirects checked for common-dir, config, status and object reads | this seat's scratch, removed at yield |
| C1 frozen counter against the landed candidate | `--no-hardlinks` clone of the lane under this seat's scratch; the lane tree was never written | `census/round-67/c1-counter.py` (sha256 `69f11706…a136b2`) |
| C2 at the pinned state + both mutants | frozen counter and frozen recipe run in the scratch clone; mutants written to this seat's scratch | `census/round-67/c2-counter.py` (sha256 `045b47d1…c14916`), `census/round-67/c2-mutate.py` |
| digest lengths | `git show <attempt commit>:census/round-67/preregistration-attempt*.txt` at each freeze commit, plus a `difflib` alignment against the measured `sha256sum` of the committed matrix blob | freeze commits `832a4d43`, `b3aa70fe`, `d874bf0d`, `4c61efcb` |
| freeze-checker rejections | `tools/souji-freeze-check.py --substance` at each attempt commit, in the scratch clone | freeze-check output quoted verbatim above |
| K1 registry gap | `tools/souji-registry-agreement.py`'s `k1()` called directly at the freeze revision, the landing revision and the current tip; the fix measured in a fixture repo | tool `tools/souji-registry-agreement.py` |
| coverage map | `tools/souji-coverage-agreement.py` at the current tip | tool output quoted above |

**No lane file was edited by this seat.** No git/jj mutating command was run against the lane, a sibling repo, or
any fixture outside this seat's own scratch. All lane reads were read-only (`git show`, `git log`, `git status`,
`git rev-parse`, `git ls-tree`, `git merge-base`).
