STATUS: DONE — three W1 drafts attacked at ddb7347; 8 findings (2 fabricated registry verdict-maps, 2 stale pin paths, 1 wrong root-rule cell, 1 red-arm mismatch, 1 live-unexecutable rule branch, 1 over-reached replacement route); ONE consolidated SKILL.md patch delivered (two-branch commit rule, 4 error bullets, 8 registry rows + evidence vocabulary), all anchors byte-verified at ddb7347.

# RevSkillDraft — SKILL.md jj integration vs W1 drafts (round 17, wave 2)

Seat `SoujiR17-3.RevSkillDraft-2`, leaf reviewer. Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`.
All line numbers are at **ddb7347** (`git show`-grounded; worktree SKILL.md is byte-identical to ddb7347, and d7e648d touches only `tests/fixtures/r15-preservation-frozen/*`). Read-only throughout: no `jj`, no git write, no lane tool run, no installs (nothing needed).

## 1. Axes

| axis | movement |
|---|---|
| calibration | Registry rows now cite only bytes that exist at ddb7347 or are named L1-pending; two fabricated verdict-map cells corrected against landed code. |
| operability | The two-branch rule carries the helper's real preconditions (init, `--as`, both-paths, push) so a seat cannot hit exit 1/3 and improvise a git fallback. |
| coverage | Four jj error bullets cover the enumerated false-SAFE signatures; one consolidated commit authority replaces the duplicated :58/:121/:123 recipes. |
| consistency | Helper-route adjudication (assignment) applied; ConnHelperDocs' direct-jj alternative rejected but its verified guards (repo-kind pre-gate, refusal=stop) absorbed. |

## 2. Ground state (verified this seat)

| fact | evidence |
|---|---|
| HEAD `d7e648d`; SKILL.md worktree ≡ ddb7347 | `git rev-parse HEAD`; `git diff --stat ddb7347 -- SKILL.md` empty; `git diff --quiet ddb7347 d7e648d -- SKILL.md` → YES |
| landed `census/round-17/` = 5 files | `gate-replays-expected.json`, `gate-replays.py`, `run-matrix.py`, `seat-audit-replay.py`, `transcript-manifest.py` (`git ls-tree ddb7347`) — no `c1-matrix*.json`, no `gate-replays.json`, no `seat-audit-w*.json` |
| fixtures landed | `tests/fixtures/r17-census-hygiene.py`, `tests/fixtures/r17-jj-receipts.sh` |
| souji lane NOT helper-initialized | `stat .jj/repo/config.toml` → ENOENT (helper `commit` exits 1, `jj-lane.sh` "no lane identity recorded"); `.jj` is a directory; 17 `refs/jj/keep/*` refs |
| helper contract (read, not run) | `scripts/hyaku/jj-lane.sh`: `--as` = lane id or `protocol` (:516-517); `snapshot.auto-track="none()"` required, init-only writer (:519-521); branch-tip deletion paths included (:543-546), warn :548, empty → exit 0 (:551); one-sided move NOT refused (`path_ok` :620-643); phantom deletion refused (:650-653); bookmark moved (:658-660); **every commit ends `do_push … || exit 3`** (:669); author stamped `<id>-shokunin` (:599-606) |
| landed receipt roots | `for-each-ref --exclude='refs/jj/'` in all three tools — `tools/souji-verify.sh:854`, `tools/souji-vault-verify.sh:1061`, `tools/souji-quarantine.sh:1155`; header `souji-verify.sh:61-71`: every ref except `refs/jj/*` is a root, `refs/stash`/`refs/original` stay roots |
| landed keep-novelty | `jj_keep_novel` `tools/souji-verify.sh:241-263`: keep-glob query gated on a keep-ref probe; refuses only when the blob at the target is absent from every pushed blob (`rev-list --objects --remotes -- <rel>`); unpushed-touching check unchanged (`--branches --not --remotes`, :273) |
| census D1/D2 | `meta_soft` → stderr `souji-census: git-metadata-unsupported <reason> <path>` (`tools/souji-census.sh:650`); `info/attributes` sole soft exception (:537,:559-568); other seven entries whole-run `protected_fail` (:544,:564) |
| landing-gate D6 | exact-id findings assertions (`tools/souji-landing-gate.py` "exact findings count" :854, "exact ids" :919) |
| drivers' CLIs | `run-matrix.py`: `--changed` (req) `--output` (req) `--fixture-dir` `--allow-dirty-fixtures`; returns only 0/2 (:149,:156,:169,:241→0 at :242) — **no exit-1 path**; `gate-replays.py`: `--gate-rev` (default WORKTREE) `--output` `--expected` `--write-expected` `--selftest` `--scratch=/var/tmp`; `transcript-manifest.py`: `--write DIR`/`--check DIR` group; `seat-audit-replay.py`: `--lane --transcripts --specs --auditor --output`, exit 2 on could-not-evaluate |
| fixtures | `r17-census-hygiene.py`: `--census`/`--tool` alias (:1092-1094), `--case` (debugging), `--list`, `--json`, rc 124 = FAIL, exact `EXPECTED_IDS` tuple (:73,:1183), per-case classes repair/preserve/refuse (:85-89); `r17-jj-receipts.sh`: `--tool-dir` required, `--baseline-dir` optional (absent → J6 SKIP), `--list`, SKIP never a pass (:51), jj absent → J9 SKIP (:709), `die`/usage → exit 2 |
| seat-audit classes | majors include `V-WRITE-RELATIVE` as its own class (`tools/souji-seat-audit.py:18`, returned :148,:175) alongside V-SURFACE (:11), V-LIVE-CENSUS (:14), V-EXEC (:22) |
| stub | `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub` exists (empty dir) |

## 3. Findings (severity-ordered; "smallest fix" is what the patch in §4 does)

**F1 HIGH — fabricated verdict map: `r17-census-matrix` exit 1.** ConnGateRegistryRows.md §Registry rows gives run-matrix "1 the runner itself failed (I/O or unhandled error)". `census/round-17/run-matrix.py` has no exit-1 path: returns 2 at :149,:156,:169,:241 and 0 at :242; the only `return 1`-shaped hits are per-suite helper tuples (rc 127/124 recorded as data, :98,:108). A registry row may not declare an exit code the tool cannot produce (the D6 lesson, now in the table itself). Fix: row states 0/2 with "1 unused by code; an unhandled crash is an unstructured nonzero, never a fixture verdict".

**F2 HIGH — wrong root rule in `r17-jj-receipts` pinned cell.** ConnGateRegistryRows pins "receipt roots are `refs/heads`, `refs/tags`, `refs/remotes` only — never `refs/jj/*`, `refs/stash` or HEAD". Landed code roots on **every ref except `refs/jj/*`** (`tools/souji-verify.sh:854`, header :61-71; vault :1061; quarantine :1155) — `refs/stash` IS a root. SKILL.md:28-29 says installed behavior wins over prose; inserting that cell would make the registry contradict the tool it certifies. Fix: corrected cell in P5 row.

**F3 HIGH — wrong novelty description (same cell).** ConnGateRegistryRows says "the unpushed-touching check adds `--glob=refs/jj/keep/*`". Landed: the branch query is unchanged (`souji-verify.sh:273`); the keep-glob lives in the separate `jj_keep_novel` novelty query (:241-263), gated on a keep probe, refusing only novel blobs. Fix: corrected cell + error bullet 2 states the landed semantics.

**F4 MEDIUM — three stale/never-landed pin paths.** ConnGateRegistryRows pins `census/round-17/c1-matrix-final.json` (actual in-flight record: `c1-matrix.json`), `census/round-17/gate-replays.json` (actual: `gate-replays-ddb7347.json`), and `census/round-17/seat-audit-w{1,2}.json` (never existed; actual: `seat-audit-r16-replay-base5fa6017.json` / `-ddb7347.json`, produced by the landed `census/round-17/seat-audit-replay.py` — a file that report never mentions). Inserting as written fires `LG-MISSING-REG` at landing or pins nothing. Fix: rows cite the landed names; uncommitted records marked "(L1)".

**F5 HIGH — "souji lane itself: helper only" is not executable at ddb7347.** `.jj/repo/config.toml` is absent (stat ENOENT) and no jj `user.name` is set, so `jj-lane.sh commit` exits 1 ("no lane identity recorded (run: jj-lane.sh init)"; init is the only writer of `snapshot.auto-track`, :519-521). Neither W1 draft that proposed a helper route (ScribeSkillJj Edit C) nor ConnHelperDocs (X3) put the precondition into SKILL text. Fix: the rule carries the init precondition and "a refusal is a stop, never a git fallback"; the init itself is the owning operator's act, never souji's.

**F6 MEDIUM — ConnHelperDocs' replacement route over-reaches.** Its X13 conclusion ("ScribeSkillJj Edit C is not applicable … must be replaced by the direct-jj block (B2)") is not the adjudicated rule: the canonical two-branch rule routes colocated repos through the **owning lane's helper** naming both paths. X1 (helper pushes), X2 (`--as` gate), X3 (init) are correct facts and are absorbed as guards in the patch, but B2's raw `jj file track`/`jj commit`/`jj bookmark set` recipe — which also requires per-command identity stamps and would hand-write what the helper does — is rejected. Fix: patch P6b implements the helper route with refusal=stop; ConnHelperDocs' verified X4 pre-gate (nested empty `.git` is not a repo) and X7 (branch must move durably — the helper does it, :658-660) are honored.

**F7 MEDIUM — red-arm cell contradicts the L1 record.** ConnGateRegistryRows' `r17-jj-receipts` self-test cell says the 5fa6017 arm "must fail J1/J2". The measured base arm (context C3 record) fails **J1, J1-vault, J3, J3-vault, J3-quarantine, J9-file, J9-worktree** (7 of 18); J2 is not among them. Fix: cell names the seven.

**F8 LOW — omitted class and omitted selftest.** ConnGateRegistryRows' seat-audit major list omits `V-WRITE-RELATIVE` (its own major class, `tools/souji-seat-audit.py:18`, returned at :148/:175 — and C2's headline fix); its gate-replays row omits the runner's `--selftest` (records the gate's own `SELFTEST pass=N fail=M` tail, `gate-replays.py:32-33,:152`). Fix: both cells corrected.

**F9 LOW — ScribeSkillJj Edit E is not the landed behavior.** Its pre-removal formula `git log --branches --glob='refs/jj/keep/*' HEAD --not --remotes -- <path>` is a prose query the tool does not run (`souji-verify.sh:273` + `jj_keep_novel`); adopting it at SKILL.md:113 would diverge the checklist from the machine form ("installed behavior wins", SKILL.md:28-29). :113 is not in this patch's enumerated scope; flagged for the LOG D3 integration either to cite the tool or to adopt the tool's exact two-query shape.

**F10 LOW — cross-document contradiction left open (not SKILL.md).** With the helper route canonized, AGENTS.md:3-4 ("sibling repos … read-only — never modify") still contradicts a quarantine commit inside a sibling repo, and AGENTS.md:20's git-only identity sentence is unexecutable in a colocated repo (helper stamps `<owner>-shokunin`; envJJ vars unset, :32-33). ConnHelperDocs block E is the right shape; routing to L1 (AGENTS.md is outside this patch).

## 4. THE PATCH — SKILL.md at ddb7347 (apply bottom-up so anchors stay valid)

Column header for all rows (unchanged, SKILL.md:135): `| name | kind | entry command | verdict map (code → class) | self-test command | pinned-value path | write scope | owner |`.

### P9 — replace :58 (Removal flow step 3)

BEFORE (:58):
```text
3. `git mv` (or plain `mv` for untracked) into `<repo>/.ufo-quarantine/<utc-date>/...` — quarantine is a normal commit in the owning repo, made with the guarded form in the Pre-quarantine checklist.
```
AFTER:
```text
3. Move into `<repo>/.ufo-quarantine/<utc-date>/...`: plain repo → `git mv` (or plain `mv` for untracked); colocated repo (`<repo>/.jj` present) → plain `mv` only (jj owns the index; staging is not a durable signal). Then commit BOTH paths (old `<rel>`, new `<qpath>`) by the Pre-quarantine commit route — quarantine is a normal commit in the owning repo.
```

### P8 — insert four bullets after :107 (end of the phantom-fixture bullet), before the :108 blank line

AFTER (insert exactly this block between :107 and :108):
```text
- **jj: `refs/jj/keep/*` is not a durable receipt root** (r17, colocation): jj writes a keep ref for every commit it creates, visible or hidden, so an all-refs root set counts unbookmarked work as durable and an absent-worktree head held only by keep refs can wrongly earn `SAFE(metadata-prune)`. Receipt roots are every ref EXCEPT `refs/jj/*` (`for-each-ref --exclude='refs/jj/'` — `refs/stash`, `refs/original` and friends stay roots): `tools/souji-verify.sh:854`, `tools/souji-vault-verify.sh:1061`, `tools/souji-quarantine.sh:1155`.
- **jj: unbookmarked / keep-only content is invisible to branch queries**: a jj commit detaches HEAD and moves no branch, so `--branches --not --remotes` returns empty for work that exists. A keep-only commit touching the target refuses a `pushed` receipt only when the blob it introduces there is novel — absent from every pushed blob at the path (`jj_keep_novel`, `tools/souji-verify.sh:241-263`; gated on a `refs/jj/keep/` probe, so plain repositories run nothing new). Deletions and identical-content rebase/metaedit predecessors do not refuse. Prose queries without the novelty check stay blind — prefer the tool's verdict.
- **jj: nested `.git` → phantom deletions**: a directory containing a `.git` (even an empty stub) is a nested repository to jj; its files read as `D` and a directory pathspec commits those deletions. Use file-exact pathspecs; never commit a directory that contains a nested `.git` (the helper refuses a committed deletion of a file still on disk). The r16 stub `tests/vault/vadv54-run/p/p6repo/.git` is quarantined at `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub`; the rule holds for any nested `.git`.
- **jj: detached HEAD is not a citable pin**: under colocation `git rev-parse @{u}` fails and `git branch --show-current` prints nothing. Read branch tips as `git rev-parse refs/heads/<b>` and remotes as `refs/remotes/origin/<b>`; never cite `HEAD` or `@{u}` as the measured commit.
```

### P7b — replace :123 (Pre-quarantine commit bullet)

BEFORE (:123):
```text
- [ ] Commit guarded and scoped: `git -C <repo> add -- <approved paths>` then `git -C <repo> -c maintenance.auto=false commit -- <same approved paths>` — never `git add -A` / `.`
```
AFTER (one bullet, three sub-bullets):
```text
- [ ] Commit route is chosen by repo kind — first `git -C <repo> rev-parse --git-dir` must succeed (a nested empty `.git` directory is not a repo; for a linked worktree resolve the main repo with `--git-common-dir`); never `git add -A` / `.`:
  - [ ] souji lane itself: helper only — `"$SHOKUNIN_ROOT/scripts/hyaku/jj-lane.sh" commit <lane> --as souji -m "<receipt class + evidence pointer>" -- <paths>`; the helper demands its own init (`snapshot.auto-track="none()"` — not yet present in this lane at r17 landing, so until the owning operator runs `jj-lane.sh init` a commit need is a stop), refuses any `--as` but the lane id or `protocol`, and ends in a push.
  - [ ] repo souji cleans with `<repo>/.jj` present: the OWNING lane's helper naming BOTH paths — `"$SHOKUNIN_ROOT/scripts/hyaku/jj-lane.sh" commit <repo> --as <owner-id> -m "<receipt class + evidence pointer>" -- <rel> <qpath>`; a one-sided request commits only that half and is NOT refused, so post-check both: `git -C <repo> cat-file -e <landed>:<rel>` fails and `git -C <repo> cat-file -e <landed>:<qpath>` succeeds; cite only the helper's `landed <hash>` line (it prints after ls-remote — the commit also pushes). Never `jj-lane.sh init` a repo souji merely cleans; a refusal (uninitialized, foreign `--as`, path guard, phantom deletion) is a stop, never a git fallback, never a raw `git commit` under colocation.
  - [ ] plain repo (no `.jj`): `git -C <repo> add -- <rel> <qpath>` then `git -C <repo> -c maintenance.auto=false commit -- <rel> <qpath>` — both paths in both commands; a destination-only commit splits the move.
```

### P7a — replace :121 (Pre-quarantine identity bullet)

BEFORE (:121):
```text
- [ ] Lane identity: `souji-shokunin <souji@shokunin.local>`
```
AFTER:
```text
- [ ] Commit identity follows the route: souji lane helper and plain repo → `souji-shokunin <souji@shokunin.local>`; owning lane's helper → `--as <owner-id>` stamps `<owner>-shokunin <owner>@shokunin.local` (the helper refuses any other id except `protocol`)
```

### P1 — append one sentence to the Gate registry intro paragraph (ends :133)

BEFORE (:128-133, final sentence):
```text
… Always use `TMPDIR=/var/tmp`
for the legacy selftests; their historical fallback is not Q4-conformant.
```
AFTER (same paragraph, one sentence appended):
```text
… Always use `TMPDIR=/var/tmp`
for the legacy selftests; their historical fallback is not Q4-conformant.
`evidence` rows are measurement producers, not gates: 0 means the record was written and is internally valid, 1 is unused by code (a red arm is data, not a runner failure), 2 means could-not-evaluate; a row whose self-test cannot fail is a `probe` or an `evidence` row, never a `gate`.
```

### P2 — replace :139 (souji-census row; D1/D2)

BEFORE (:139): the current `souji-census` row (verbatim in ddb7347).
AFTER:
```text
| souji-census | probe | `bash tools/souji-census.sh --root DIR [--compare PREV.tsv]` | 0 census emitted — `dirty` is normal-mode (a wholly untracked directory is one collapsed line) and, D1, measured with explicit `--untracked-files=normal` so it is independent of a repo-local, include-carried or `config.worktree` `status.showUntrackedFiles`; rows may carry `error`/`status-unverifiable`/`not-a-repo` for degraded repositories, so a wholly degraded fleet still exits 0 — placeholders, not measurements; D2: a hardlinked, non-regular or unresolvable `$GIT_DIR/info/attributes` degrades that repository only (stderr `souji-census: git-metadata-unsupported <reason> <path>`; when a degraded config also fires, its soft line prints too); or header-only diff; 3 failed differential comparison; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage/malformed baseline/whole-run `path-protected: git-metadata-*` refusal for config, HEAD, index, packed-refs, commondir, info/exclude or alternates | `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` | historical r16: `census/round-16/c1-matrix-final.json`; r17 behavior: `census/round-17/c1-matrix.json` (L1) read with `r17-census-hygiene` below | read-only census; compare capture and isolated selftest under `/var/tmp` | souji |
```

### P3 — insert three rows after :149 (r15-census-config)

AFTER (:149 stays; insert):
```text
| r17-census-hygiene | gate | `python3 tests/fixtures/r17-census-hygiene.py --census PATH` (`--tool` accepted as an alias) | 0 clean; 1 failed case or id-set, or a census run exceeding the per-case timeout (rc 124 is FAIL, never SKIP); 2 could-not-evaluate missing prerequisite/usage | same default self-invocation over an isolated synthetic HOME and private tempdir; `--case`/`--list` are debugging only, never admission; `--json` emits per-case records | fixture literal `EXPECTED_IDS` compared as an exact ordered tuple with per-case class (`repair`/`preserve`/`refuse`) and expected exit/row; `census/round-17/c1-matrix.json` (L1) | isolated private tempdir under `/var/tmp`; never a real fleet root or credential store | souji |
| r17-census-matrix | evidence | `python3 census/round-17/run-matrix.py --changed <rev or WORKTREE> --output <new.json>` | 0 record written and every suite valid (fixture exit agrees with its SUMMARY; all fixtures clean, or dirty fixtures recorded via `--allow-dirty-fixtures`); 1 unused by code — the runner returns only 0 or 2, an unhandled crash is an unstructured nonzero, never a fixture verdict; 2 could-not-evaluate invalid suite/unknown revision/missing fixture/dirty fixtures without the flag/refused `--output` overwrite/usage | `python3 -m py_compile census/round-17/run-matrix.py`; the runner's selector table supplies each suite's flag (`--census` for r17-hygiene, `--tool` for r15/r14); no in-file behavioral selftest — the record is only as strong as the fixtures it runs | `census/round-17/c1-matrix.json` (L1) read with the r17-census-hygiene, r15-census-config and r14-census-boundary rows | per-fixture isolated `/var/tmp`; writes only `--output` (refuses overwrite) | souji |
| r17-jj-receipts | gate | `bash tests/fixtures/r17-jj-receipts.sh --tool-dir DIR` | 0 clean with every case counted (a case the selected tools cannot express prints `SKIP`; SKIP is never PASS; jj absent → the optional real-jj J9 arm SKIPs); 1 failed case/id-set; 2 could-not-evaluate missing git, missing `--tool-dir`, usage | same default invocation with `--tool-dir tools`; the paired red arm over `5fa6017`-extracted tools must fail J1, J1-vault, J3, J3-vault, J3-quarantine, J9-file, J9-worktree; `--baseline-dir` absent → J6 SKIP | fixture CASE/SUMMARY literals; C3 root rule: receipt roots are every ref except `refs/jj/*` (`for-each-ref --exclude='refs/jj/'`), and a keep-only commit refuses only a novel blob at the target (`tools/souji-verify.sh:241-263`) | isolated `mktemp -d` under `/var/tmp` (sandbox repos removed); never a real fleet repo; `jj` runs only inside the sandbox | souji |
```

### P4 — replace :152 (souji-landing-gate row; D6)

BEFORE (:152): the current `souji-landing-gate` row.
AFTER:
```text
| souji-landing-gate | gate | `python3 tools/souji-landing-gate.py --root LANE --rev REV --round N [--base REV] [--json OUT]` | 0 no findings; 1 findings (LG-PARSE-REG, LG-MISSING-REG, LG-PARSE-CHANGED, LG-FROZEN-PIN, LG-FROZEN-MEASURED, LG-SEAT-UNCARRIED, LG-OPEN-ADMITTED); 2 could-not-evaluate and total: usage/unknown rev/no SKILL.md/missing wave dir, an unreadable blob, a failed git read or a falsy `files` pin — never demoted to a finding | `python3 tools/souji-landing-gate.py --selftest` (exact finding-id sets per case, 28 cases) | literal finding ids, failure vocabulary and frozen-path rule in the tool; committed replays `census/round-17/gate-replays-expected.json` with record `census/round-17/gate-replays-ddb7347.json` (L1) | reads committed blobs; private `/var/tmp` snapshot removed; runs only `bash -n` and Python `compile()` | souji |
```

### P5 — insert one row after :153 (r16-landing-gate)

AFTER (:153 stays; insert):
```text
| r17-gate-replays | gate | `python3 census/round-17/gate-replays.py [--gate-rev REV] --output <new.json>` | 0 every pinned replay's exact (id, path) multiset and exit code equal `census/round-17/gate-replays-expected.json` (b410186 → 1 with 5 ids; a31642d → 0; cc21683 → 0; 6ff91f5 → 0; 79bbe7a → 1 with 29 LG-SEAT-UNCARRIED), the gate's own `--selftest` tail recorded; 1 any divergence (extra/missing row or exit code); 2 could-not-evaluate bad rev/missing gate/output exists/missing expected file/usage | identity run `--gate-rev 5fa6017` against the expected file derived from that same gate exits 0; the worktree/ddb7347 run is the differential and must be explained, never fitted to prose | `census/round-17/gate-replays-expected.json` (committed at ddb7347) and record `census/round-17/gate-replays-ddb7347.json` (L1) | extracts the gate to private `/var/tmp` (also hardcoded in the gate's selftest); writes only `--output`/`--write-expected` | souji |
```

### P6 — replace :154 and append one row (souji-seat-audit; r17-transcript-manifest)

BEFORE (:154): the current `souji-seat-audit` row.
AFTER (two rows):
```text
| souji-seat-audit | gate | `python3 tools/souji-seat-audit.py --spec W.json --transcripts DIR --lane LANE [--json OUT]` | 0 no major violation — majors are `V-SURFACE`, `V-LIVE-CENSUS`, `V-WRITE-SCOPE`, `V-WRITE-RELATIVE`, `V-EXEC`; `V-WRITE-UNPARSED` is status-aware (major on `⇒ ok`, minor on `⇒ error`), `V-PROBE`/`V-RECURSIVE`/`V-WRITE-UNKNOWN` are minors; exit 0 is a disclosure floor, never proof the probe rule held; 1 at least one major; 2 could-not-evaluate usage/unreadable spec or transcript | `python3 tools/souji-seat-audit.py --selftest` (severity-exact, 49 cases) | literal class set and per-case expected class sets in the tool; r16 replay record regenerated by `census/round-17/seat-audit-replay.py` over `census/round-16/transcripts` (MANIFEST-checked): `seat-audit-r16-replay-base5fa6017.json` / `-ddb7347.json` (L1) | reads exported transcripts read-only; writes only `--json` (refuses overwrite) | souji |
| r17-transcript-manifest | gate | `python3 census/round-17/transcript-manifest.py --check DIR` | 0 every listed digest matches, no listed file missing, no unlisted file present; 1 mismatch/missing/extra; 2 usage/unreadable directory | `--write` then `--check` on a private `/var/tmp` copy exits 0; a one-byte mutation of one file makes `--check` exit 1 (negative control) | `census/round-16/transcripts/MANIFEST.sha256` (sorted `sha256  relpath`, `LC_ALL=C`) over the byte-exact r16 w1/w2 transcripts | `--write` creates `MANIFEST.sha256` inside the named directory only; `--check` read-only; never alters transcript bytes | souji |
```

Patch totals: 4 replaced rows + 6 inserted rows + 1 vocabulary sentence + 2 checklist replacements + 4 error bullets + 1 removal-flow step. Net ≈ +22 lines.

## 5. Residual risk and verification gaps

- **Helper route publishes.** A quarantine commit through the owning lane's helper lands AND pushes under the owner's identity (`jj-lane.sh:669`); the patch's `landed`-only citation and stop-on-refusal keep it safe, but if a sibling repo must not receive the push now, the move waits for that lane — no local-only helper mode exists. Disclosed in P6b's "commit also pushes" clause.
- **Souji lane init state.** P7b says the lane is not yet initialized at r17 landing; if L1 runs `jj-lane.sh init` on the lane, that sentence's premise (not the rule) becomes historical. Init writes jj workspace config — an owning-operator action, not a seat or landing action.
- **Unverified-by-execution:** every helper claim in the patch is code-read (`jj-lane.sh` :514-:669), not run — no ALLOWED-EXEC in this seat. The `cat-file` post-check is the falsifier at use time. Similarly `--as <owner-id>` behavior in a real sibling is read-only-derived.
- **Out of patch scope, routed:** SKILL.md:113 pre-removal query still HEAD-only prose (F9); SKILL.md:35 `pushed` row does not mention the keep-novelty refuse (prose defers to tool, SKILL.md:28-29, but LOG D3 may want the clause); AGENTS.md:3-4/:20 contradictions (F10); `tools/souji-quarantine.sh` action mode still uses `git mv`/`git rm --cached` (SimplifySkillCommit R4 — tool owner, not SKILL).
- **Registry insertion timing:** the six new rows cite files landed at ddb7347 (five drivers, two fixtures, MANIFEST) plus three L1-pending JSONs (`c1-matrix.json`, `gate-replays-ddb7347.json`, `seat-audit-r16-replay-*.json`). If the gate runs before those JSONs are committed, `LG-MISSING-REG` fires for exactly those paths — expected and attributable, not a defect. All cited `.py`/`.sh` paths exist at ddb7347, so only the JSON pins can go missing.
- **No frozen pin covers SKILL.md** (ConnGateRegistryRows verified; unchanged by this patch), so editing SKILL.md at landing fires neither `LG-FROZEN-PIN` nor `LG-FROZEN-MEASURED`.

## 6. Commands run (all read-only; no `jj`; no lane tool; no installs)

```text
git -C <lane> rev-parse HEAD; git log --oneline -4
git -C <lane> diff --stat ddb7347 -- SKILL.md                      → empty
git -C <lane> diff --stat ddb7347 d7e648d | tail -5                → r15-preservation files only
git -C <lane> diff --quiet ddb7347 d7e648d -- SKILL.md && echo YES
git -C <lane> ls-tree --name-only ddb7347 census/round-17/ tests/fixtures/ tools/
git -C <lane> ls-tree --name-only ddb7347 census/round-16/transcripts/ | head -4 → MANIFEST.sha256 present
stat .jj/repo/config.toml .jj /home/vgpnk/Projects/shokunin/.jj    → ENOENT / dir / ENOENT
git -C <lane> for-each-ref --format='%(refname)' refs/jj/keep/ | wc -l → 17
grep -n '' SKILL.md                                                → full numbered file (240 lines)
read SKILL.md :1-70 :70-135 :135-175; ConnGateRegistryRows.md :raw:19-19
read scripts/hyaku/jj-lane.sh :495-560 :575-680
read tools/souji-verify.sh :55-80 :241-270
read census/round-17/run-matrix.py :130-172; census/round-17/seat-audit-replay.py :104-125
grep -n anchors in SKILL.md; grep exclude='refs/jj/' + jj_keep_novel in the three receipt tools
grep add_argument/EXPECTED_IDS/timeout in r17-census-hygiene.py; tool-dir/SKIP/0.45.1 in r17-jj-receipts.sh
grep git-metadata-unsupported/info/attributes in tools/souji-census.sh
grep V-WRITE-RELATIVE etc. in tools/souji-seat-audit.py; 'return 1' in run-matrix.py
grep -A3 parser.add_argument r17-census-hygiene.py; repair/preserve/refuse class map
stat .ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub → directory (exists)
grep -n SHOKUNIN_ROOT SKILL.md
```

Probe-rule note: all greps targeted exact named files; no recursive search over any tree. Reports read by exact name: ScribeSkillJj.md, SimplifySkillCommit.md, ConnHelperDocs.md, ConnGateRegistryRows.md (plus SKILL.md, the helper, and the landed drivers/fixtures they cite).
