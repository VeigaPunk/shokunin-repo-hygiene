# S65ScribeEntry — round 65 corpus paperwork (scout/scribe seat)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Lane tip read via
`git -C <lane> rev-parse refs/heads/master` → `16da2445088ccca15aa32c66841d878ee57a8706`.
Base `4a43a4d919c5b51ae9be859a1266ce4b11337b0b`; instruments `2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8`;
controls `3c5bfdc0db50785cb7b2ec60e509facf2d7e9f25`; FREEZE `d2850b3eb160ae65c1c65b93753dfec7f4153b45`;
landing `022cf9791ec83ca6c854733c66c84705016f4d67`; S2 wrap fix / measured rev
`40a371d8232e89e4f50d3ece4ff8779f44c0ee4c`; chronology arm `16da2445088ccca15aa32c66841d878ee57a8706`.

Seat role: DRAFT only. **No lane file was edited**, no commit, no push, no mutating git/jj command anywhere.
All writes are confined to the deliver directory
`.ufo/waves/round-65/w1/S65ScribeEntry/` and the scratch root
`/fast/scratch/hyaku/souji-r65/S65ScribeEntry/` (created, then deleted before this report — see "Scratch").

## Delivered files

| file | what it is |
|---|---|
| `.ufo/waves/round-65/w1/S65ScribeEntry/knowledge-untracked-visibility-concealment.md` | the drafted entry the round lands as `corpus/knowledge/untracked-visibility-concealment.md` |
| `.ufo/waves/round-65/w1/S65ScribeEntry/lesson-round-65.md` | the drafted round lesson (skeleton with Claim / Gate / Mistakes / Named limits / Routed to round 66 / Integrated verification) |
| `.ufo/waves/round-65/w1/S65ScribeEntry/sources-row-s297.md` | the paste-ready S297 registry row + the L1's integration facts |
| `.ufo/waves/round-65/w1/S65ScribeEntry/excl_probe3.py`, `v2_probe.py` | the concealment-arm probes (scripts) |
| `.ufo/waves/round-65/w1/S65ScribeEntry/excl-probe-results.txt`, `v2-probe-results.txt` | the probes' raw output |

The three paperwork drafts are addressed to the L1 (`SoujiR65`), the canonical planner and sole integration
owner. Nothing was sent to `agent://all`.

## Frozen scoring, independently reproduced

Run from the seat's scratch, counters/matrix read from the lane, `--work` under the seat's scratch root
(the counters refuse `/tmp`, `/var/tmp`, `$TMPDIR` and the lane root):

| run | observed | frozen target | verdict |
|---|---|---|---|
| C1 counter, candidate slot (writer at `40a371d8…`) | `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0` | identical | **MET** |
| C1 counter, do-nothing slot (base bytes as new) | `SUMMARY … new_forgeries=12 … class_mismatches=12 regress=PASS`, `EXIT=1` | `new_forgeries=12`, exit 1 | **MET** |
| C2 counter at `40a371d8…` | `MARKERS flag=1 inrun=1 env=1 unmerged=1`, `SUMMARY rows=4 findings=0 verdict=PASS`, `EXIT=0` | identical | **MET** |
| C2 counter at the base revision | `FINDING SCOPE-OVERREACH s2`, `FINDING GOVERNED-STATEMENT-UNRESOLVED s4`, `SUMMARY rows=4 findings=2 verdict=FAIL`, `EXIT=1` | `findings=2` (s2 + s4), exit 1 | **MET** |

Commands, verbatim:

```
python3 -B census/round-65/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --matrix census/round-65/c1-matrix.tsv --base-rev 4a43a4d919c5b51ae9be859a1266ce4b11337b0b \
  --rev 40a371d8232e89e4f50d3ece4ff8779f44c0ee4c --tool tools/souji-receipt-write.py \
  --work /fast/scratch/hyaku/souji-r65/S65ScribeEntry/c1recheck
python3 -B census/round-65/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --matrix census/round-65/c1-matrix.tsv --base-rev 4a43a4d919c5b51ae9be859a1266ce4b11337b0b \
  --new-tool /fast/scratch/hyaku/souji-r65/S65ScribeEntry/base-writer.py \
  --work /fast/scratch/hyaku/souji-r65/S65ScribeEntry/c1dn
python3 -B census/round-65/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --tsv census/round-65/c2-statements.tsv --tsv-rev 2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8 \
  --rev 40a371d8232e89e4f50d3ece4ff8779f44c0ee4c
python3 -B census/round-65/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --tsv census/round-65/c2-statements.tsv --tsv-rev 2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8 \
  --rev 4a43a4d919c5b51ae9be859a1266ce4b11337b0b
```

These are wave evidence. They do NOT replace `census/round-65/records/c1-after.txt` and
`census/round-65/records/c2-after.txt`, which the L1 produced and which remain the round's after-receipts.

## Finding 1 — the landed writer's docstring overclaims (HIGH; scope defect, NOT a C1 forgery)

`tools/souji-receipt-write.py`'s round-65 (C1) docstring paragraph says:

> every status read overrides status.showUntrackedFiles to `all`, so an operator-injected config cannot hide
> untracked entries from the dirty check or the content snapshot

The first clause is measured true. The second is broader than the bytes support. Measured by this seat
(per-slot FRESH fixture repos, one untracked file `untracked.txt` in each; writer blob `be344a7d` =
`40a371d8…`, base blob `9fb55f35` = `4a43a4d9…`; host git 2.56.0):

| arm | operator state | base | landed writer |
|---|---|---|---|
| A | repo-local `status.showUntrackedFiles=no` (the frozen V1 shape) | accept rc 0 | **refuse rc 2**, `lane worktree is dirty` |
| B | `core.excludesFile` injected via `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0` | accept rc 0 | accept rc 0, receipt written |
| C | repo-local `core.excludesFile` | accept rc 0 | accept rc 0, receipt written |
| D | tracked `.gitignore` naming the file | accept rc 0 | accept rc 0, receipt written |
| E | repo-local `.git/info/exclude` naming the file | accept rc 0 | accept rc 0, receipt written |
| F | control, no concealment | refuse rc 2 | refuse rc 2 |
| V2 | repo-local `showUntrackedFiles=no`, CLEAN tree | accept rc 0 | accept rc 0 (honest polarity holds) |

Mechanism: a path matched by an exclude rule is IGNORED, not untracked, so `showUntrackedFiles=all` does
not surface it. The override is key-scoped, not class-scoped.

Scope of the finding, stated precisely:

- **Not a C1 forgery.** The frozen V1 row's shape is specifically `status.showUntrackedFiles=no`; that row
  PASSES (`new_forgeries=0`, exit 0, reproduced above). Arms B–E accept on the BASE slot too, so they are
  residual shared limits, not round-65 regressions.
- **Not a C2 finding.** `SKILL.md`'s own writer-delta sentence is already key-scoped ("every status read
  overrides `status.showUntrackedFiles=all` (V1/V2)") and IS in the C2 population; the overreach is in the
  writer's docstring, which is not. C2's `findings=0` is unaffected.
- **It IS a defect in the landed wording.** The sentinel seat (`S65SentinelScope`) independently reproduced
  arms B/C/E and rates it HIGH; the two seats agreed on rating and on the wording fix. Evidence:
  `.ufo/waves/round-65/w1/S65SentinelScope/probe-env-output.txt`, final report
  `.ufo/waves/round-65/w1/S65SentinelScope.md`.
- **The fix is a WORDING fix**, not a scrubbing fix: reword the docstring to the key-only claim. Scrubbing
  `GIT_CONFIG_*` or pinning `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM` changes what the writer reads and is
  an operator/design decision, not a wave's. Proposed wording is in the drafted knowledge entry.
- **Route:** round 66 (lesson "Routed to round 66" item 1), plus a candidate matrix row for the ignore
  routes so the general claim gets its own frozen predicate instead of living in a docstring.

Probe artifact, corrected and recorded: this seat's first run of arm D reported a REFUSAL; that reading was
caused by a leftover receipt file inside the shared fixture repo. With per-slot fresh repos, arm D is a
bypass, not a refusal. The correction was made before the finding was reported to the sentinel.

## Finding 2 — the chronology arm landed POST-freeze, not pre-freeze (M1)

The preregistration says "`tools/souji-freeze-check.py --chronology` landed pre-freeze". The tree contradicts
it:

- `2761f0aa…` (instruments, 2026-11-05 09:57) carries the commit message "… + freeze-check chronology arm",
  but its diffstat touches ONLY `census/round-65/**` (8 files). `tools/souji-freeze-check.py` is not in it.
- `git show 2761f0aa:tools/souji-freeze-check.py | grep -c chronology` → 4, and all four hits belong to the
  PRE-EXISTING r61 control-chronology arm (`control_chronology()` at line 295, called at 379). The file is
  byte-identical at the freeze `d2850b3e…` (same 4 hits).
- The actual arm — the `--chronology` CLI flag, the `r64 --chronology` docs, `evaluate(..., chronology=)`,
  the receipt-rev-after-freeze check — landed at `16da2445…` (2026-11-05 10:43), AFTER the freeze. Only there
  does the count reach 24.
- Consequence: `census/round-65/records/freeze-check-substance-at-freeze.txt` (`SUMMARY claims=2 findings=0`)
  and `census/round-65/records/freeze-check-selftest-chronology.txt` (`SELFTEST cases=52 pass=52 fail=0`) are
  evidence about the pre- or post-freeze bytes, NOT about the bytes that existed at the freeze.

Captured by: "the pre-freeze landing checklist had no working-tree copy step" — the checklist verified the
candidate's bytes and the instruments commit's census files, but never verified that the modified working-tree
file `tools/souji-freeze-check.py` was actually STAGED into that commit. Fix: for every file the round intends
to land, assert `git show <commit>:<path>` equals the working-tree bytes AND that `<path>` appears in
`git show --stat <commit>`. A commit message asserting a file is not evidence that the file is in the commit.

This is disclosed in the round's own chronology and the closure judge rules; it is recorded here as M1 with
its evidence pointer, not as an amendment of any frozen predicate.

## Finding 3 — source-row provenance discipline (M3)

The S297 row's quote was located by this seat in its OWN capture and, independently, by the scout seat in its
capture. The HTML digests are IDENTICAL (`37aa8407…9226`, HTTP 200, 830605 bytes, third-client confirmed), but
the tag-stripped TEXT captures differ, because the tag-strip recipes differ (`s297-git-config.txt` sha256
`a692dbcb…7c3f` for the scout, `49851586…4284` for this seat). Offsets are meaningful only against the exact
bytes plus the recipe that produced them; the recipe must travel with the capture.

This seat's first lesson draft quoted a raw-HTML offset of 762518 for `Show no untracked files.` — that was a
CHARACTER offset in the decoded string, not a BYTE offset (the capture holds 100 multi-byte characters before
that point; the byte offset is 762618, and `- Show no untracked files.` starts at 762616). The scout caught
the discrepancy and this seat re-measured and corrected it. Recorded so it is not repeated.

## Sources — S297 (the round's frontier step)

S297 is opened this round and cited by this round's evidence. The row is ready to paste:

```
| S297 | git-config(1) § status.showUntrackedFiles — https://git-scm.com/docs/git-config | docs | A | the writer's untracked-visibility refusal (receipt hygiene, C1 V1/V2 rows) | § status.showUntrackedFiles, accessed 2026-11-05; HTTP 200; 830605 bytes; sha256 37aa8407…9226; capture census/round-65/sources/s297-git-config.html; tag-stripped text census/round-65/sources/s297-git-config.txt; located quote census/round-65/sources/s297-located-quote.txt | `So, this variable controls how the commands display the untracked files.` (11 words) — the page's own words, located at byte offset 299266 of the tag-stripped text capture with `assert text[299266:299338] == quote_bytes` PASSED; the three documented values are `no` (show no untracked files), `normal` (show untracked files and directories) and `all` (show also individual files in untracked directories), and the default is `normal`; the page does not say that a tool must override the variable, and it says nothing about the precedence of `-c` or of `GIT_CONFIG_COUNT` | queued | 2026-11-05 | 180d | corpus/knowledge/untracked-visibility-concealment.md |
```

Shape validated on a SCRATCH COPY of the registry (never the lane): 11 content cells (`awk -F'|'` NF=13), no
`|` inside any cell, kind `docs`, tier `A`, status `queued`, recheck `180d`, quote 11 words ≤ 25, tier
histogram A=209→210 (219→220 rows). The full row text, the cell-by-cell table and the reproduction command
are in `sources-row-s297.md`.

The quote and its offsets are **verified-by-scout** (the scout's `s297-located-quote.txt`, whose offsets are
re-run slice assertions from `s297-make-located-quote.py`, not copied numbers). This seat independently
re-ran those assertions against the scout's DELIVERED bytes: text 299266 / 299360 / 299390 / 299437 / 299496
PASSED; man-page carrier 330781 / 330827 / 330890 PASSED; the section anchor `Documentation/git-config.txt-statusshowUntrackedFiles`
is at raw HTML byte offset 761837.

Integration facts for the L1 (all in `sources-row-s297.md`): the row and the knowledge entry must land
TOGETHER (K1 `used-by-missing` / `used-by-no-cite` until then); the L1 must copy the captures to
`census/round-65/sources/` under the names the anchor cell names; S291's `used-by` must gain the new entry
path or K1 fires `cited-not-in-used-by` in the other direction (the old→new pair must be logged in the
lesson); a duplicate-url warning (W04) is expected — the git-config URL is already carried by S042, S057 and
S238, and S297's scope is distinct (S057's scope cell reads "not which value the census should use", which
S297 is exactly the complement of).

## The `:(top)` code-kind row — ROUTED, NOT ADOPTED

The round's one reject candidate. The pathspec long-form spelling `:(top)` is composed by the reader, not
printed on the git-scm.com page (r64's S296 named limit; the binding is code — `pathspec.c` v2.56.0 line 106
`{PATHSPEC_FROMTOP,'/',"top"}` and `parse_long_magic()` line 333). A code-kind registry row for it was
proposed in round 64 and remains **pending the operator L0** on whether the registry admits code-kind rows.
No operator answer is recorded in this lane, so no such row may be appended under round 65.

## Out of scope for this seat

- The `refs/replace` arm is the sentinel seat's finding, not this seat's measurement. It is cited in the
  lesson's Named limits with the sentinel's own evidence pointers (`.ufo/waves/round-65/w1/S65SentinelScope/probe-replace-excludes.sh`
  case p6b, `probe-env-output.txt`, final report `S65SentinelScope.md`): with a replacement ref on the
  instrument blob and `--allow-dirty`, the writer accepts and the receipt's `instrument_sha256` is the
  REPLACEMENT's bytes (`aea35bbef2e7f0c0…`) against committed blob `8f513b9f361acb7e…`. The base-slot
  outcome for that arm was NOT measured (the sentinel's probe ran only the new writer) and is marked as not
  measured. This seat did not re-run it.
- The knowledge-repo assimilation (`/home/vgpnk/Projects/shokunin/shokuknow/merge/souji/MERGE-REPORT.md`,
  read-only) is the connector seat's duty; this seat did not read it.
- No product code was edited; no commit, push, publish, deploy or mutating git/jj command was run anywhere;
  no foreign process was signalled; no sysctl was touched; no pacman transaction was run.
- No tools were installed for this seat (nothing was needed).

## Scratch and hygiene

- Scratch root `/fast/scratch/hyaku/souji-r65/S65ScribeEntry/` was created, used for the counter runs
  (`--work` paths `c1recheck`, `c1dn`), the fixture repos, and the source captures — and deleted before
  this report (Python `shutil.rmtree`, no `rm -rf --`).
- Nothing was written under `/tmp`, `/var/tmp` or `$TMPDIR` beyond a transient Python heredoc; the fixture
  repos lived in the scratch root.
- The lane tree was read only: `git show`, `git rev-parse`, `grep`, `read`. The only lane-side writes are
  the files under `.ufo/waves/round-65/w1/S65ScribeEntry/`.
- Peer messages: `S65ScoutSources` (row fields, the offset correction), `S65SentinelScope` (the
  config-precedence and ignore-route probes, the rating agreement, the refs/replace citation form). No
  broadcast to `agent://all`.

## Checks the main agent should run (not run by this seat)

1. `python3 -B census/round-65/c1-counter.py --root . --matrix census/round-65/c1-matrix.tsv --base-rev 4a43a4d919c5b51ae9be859a1266ce4b11337b0b --rev 40a371d8232e89e4f50d3ece4ff8779f44c0ee4c --tool tools/souji-receipt-write.py --work DIR` → expect `new_forgeries=0 … EXIT=0`.
2. `python3 -B census/round-65/c2-counter.py --root . --tsv census/round-65/c2-statements.tsv --tsv-rev 2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8 --rev 40a371d8232e89e4f50d3ece4ff8779f44c0ee4c` → expect `findings=0 verdict=PASS`, exit 0.
3. After landing the entry + the row: `tools/souji-registry-agreement.py` (K1) must report no
   `used-by-missing` / `used-by-no-cite` / `cited-not-in-used-by` for S297 or S291.
4. `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0; row count 219 → 220.
5. `git show 2761f0aa:tools/souji-freeze-check.py | grep -c chronology` → 4 (not 24) — the M1 evidence, if the
   L1 wants to re-derive it independently.
