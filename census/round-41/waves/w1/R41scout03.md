# R41scout03 — C1 recon (souji round 41)

- Seat: R41scout03 (scout, leaf — no subagents). Date: 2026-10-28.
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, tip = freeze commit `e2a74312af4233963e44e4dbb38838ece07b8bd2`; instruments commit `6682b98175b995ee4646ffd1ea6bd8a12cd353dd`; measured revision `MEASURED = bffcc0f660ff36eb8add3f61582748a7af019a5b` (from `census/round-41/preregistration.txt`, read first).
- Method: read-only. `git show` / `git grep` / `git ls-tree` against the lane and the fleet repo (`/home/vgpnk/Projects/shokunin`, HEAD `5144b531f7ce5b36547e99cd3f3521876424bf10`). No lane file touched; no tools installed or upgraded; pacman untouched. Scratch was pipeline-only and deleted.
- Instrument integrity: `sha256sum census/round-41/c1-counter.py` = `8860dc7af55848db3d67d11aec69cd8ee1f5a413964dd32ac7baddcebe49ab63` and `census/round-41/c1-items.tsv` = `2d2a548e253b7863cd9679ebe9f1f851a10223e47d3456e33345279b79a036cf` — both match the preregistration pins.

## I1 — filed: "`worktree.c` appears in 9 rows" (rows-worktree-c)

Filed, `corpus/lessons/round-40.md:48-50` (bytes at MEASURED unchanged at tip):

> **REJECT — staged entry `fleet-prune-safety-r28.md` (staged row id S160, git v2.56.0
> `worktree.c`).** The lane already holds git's prune gate (`worktree.c` appears in 9 rows of
> `corpus/SOURCES.md`); adopting it again would be a duplicate, not new ground. Flip: none.

Re-derivation at MEASURED (registry row = line matching the counter's `^\|\s*S\d{3,}\s*\|`):

```
git -C <lane> show bffcc0f…:corpus/SOURCES.md | grep -c 'worktree\.c'                          -> 3
… | grep -E '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' | grep -c 'worktree\.c'                  -> 2
… | grep -c 'v2\.56\.0/worktree\.c'                                                            -> 0
… | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'                                          -> 181 (total rows)
```

The two registry rows are `S009` (line 38, git v2.55.0 `builtin/gc.c, worktree.c, run-command.c, builtin/commit.c`) and `S033` (line 62, gitrepository-layout(5)); the third hit (line 240) is a §negative-results bullet, not a row. Neither row names `v2.56.0/worktree.c`.

- Derived value the counter will require: **`rows=2,v2.56.0=0`** → mismatch confirmed (filed 9).
- Sourced leg: at tip `e2a7431` there is **no S258 row** (max id = S257; `git show e2a7431…:corpus/SOURCES.md | grep -n S258` → no match). The tier-A `mined`/`2026-10-28` row naming both `v2.56.0` and `worktree.c` must be appended during r41 or `sourced=0` kills C1.
- Origin of "9" unproven: fleet repo has no `corpus/SOURCES.md` (`git ls-tree HEAD corpus/` empty) and all four sibling-lane registries contain **0** `worktree.c` registry rows (kama 268 rows, tsukuroi 256, tabi 149, mori 337). [INFERENCE] the number appears invented or drawn from an uncommitted staging note; `fleet-prune-safety-r28` / `appears in 9 rows` were not found anywhere in the fleet worktree outside this lane (timeboxed grep).

## I3 — filed: r40 C1 before/after as one like-for-like pair (register-cells)

Filed, `SCORECARD.md:791` (r40 measurements table, row `| C1 evidence-bound closures + strict-descendant register |`): before cell = "`SUMMARY items=3 open=3 register_cells=6 ...` rc 1 at the frozen base (`census/round-40/records/c1-before.txt`)", after cell = "`SUMMARY items=3 open=0 ... register_cells=3 ...` rc 0 ... (`c1-after-d.txt`)" — one before→after pair.

The two receipts' own headers show different arms:

- `census/round-40/records/c1-before.txt` line 3: `… --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b … --register census/round-39/cells.tsv …`; `REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=0 ok`.
- `census/round-40/records/c1-after-h.txt` line 3: `… --rev dc8bd47c693097a69ccaa39b514ce9689a642edc … --register census/round-40/cells.tsv …`; `REGISTER cells=3 mismatches=0 commit_rows=3 commit_hashes=1 violations=0 ok`.

- Derived value: **`before=6,after=3`** → mismatch confirmed (the pair is not like-for-like: the before arm scores the r39 register, the after arm the r40 register).
- Context: `c1-before.txt` also records `SUMMARY … register_cells=6 …` rc 1 and `c1-after-h.txt` `SUMMARY … register_cells=3 …` rc 0, matching the SCORECARD cells; only the register-file identity differs.

## I4 — filed: dead-seat provider error text recorded (committed-occurrences)

Filed, `LOG.md:1909` (r40 Swarm bullet): "… 2 dead seats (R40w2reviewer01/04, provider error ``Codex error event: Invalid prompt: your prompt was flagged as potentially violating our usage policy``), and R40w2mutationtester01 completed without a report … **All wave evidence is captured under `census/round-40/waves/`.**"

Re-derivation at MEASURED (counter counts the substring `flagged as potentially` under `census/round-40/waves/`):

```
git -C <lane> ls-tree -r --name-only bffcc0f… census/round-40/waves/ | wc -l        -> 136
git -C <lane> ls-tree -r --name-only bffcc0f… census/round-40/waves/ | grep -i 'reviewer01\|reviewer04'  -> no match (rc 1)
git -C <lane> grep -n 'flagged as potentially' bffcc0f… -- census/round-40/waves/   -> no match (rc 1)
git -C <lane> ls-tree -r --name-only bffcc0f… .ufo/waves/round-40/ | wc -l          -> 0 (nothing committed under .ufo at MEASURED)
git -C <lane> grep -n 'flagged as potentially' bffcc0f… -- .ufo/waves/round-40/     -> no match (rc 1)
```

- Derived value: **`occurrences=0`** → mismatch confirmed (zero occurrences in the committed wave evidence the LOG says captured everything; the two dead seats' reports are absent from `census/round-40/waves/` entirely).

Does the provider error text appear ANYWHERE committed (git grep over the named revisions)?

- Lane `souji-shokunin` @ `bffcc0f`: **only `LOG.md:1909` itself** — the filed statement is the sole carrier.
- Lane @ tip `e2a7431`: `LOG.md:1909` plus the frozen r41 instrument bytes that quote the anchor: `census/round-41/c1-counter.py:91` and `census/round-41/c1-items.tsv:4`. No wave-evidence carrier at any revision grepped.
- Fleet repo `/home/vgpnk/Projects/shokunin` @ HEAD `5144b53` (all three tracked, `git ls-files` confirms): **`.ufo/reports/round-40/souji.md:79`** (the fleet round-40 report — "R40w2reviewer01 and R40w2reviewer04 died with ``Codex error event: Invalid prompt: …``"), `.ufo/reports/round-45/mori.md:12`, `.ufo/reports/round-45/tsukuroi.md:111`.
- Fleet worktree, NOT tracked in the fleet repo (`git ls-files` over the lanes = 0, so not "committed" in the fleet repo): `kama-shokunin/.ufo/waves/round-39/w1/outcomes.json:14`, `tsukuroi-shokunin/.ufo/waves/round-39/w1/AsmCollision/urls/staged.rows:93`, `tabi-shokunin/.ufo/waves/round-21/w2-failures.json:10` (+ a nested scratch copy), `mori-shokunin/LOG.md:2620`. The full provider string with its "Please try again with a different prompt … (code=invalid_prompt)" suffix survives only in these sibling captures and the fleet report — the souji lane never captured it.

## Verdict

All three filed r40 statements are **mismatched** against their re-derivations at `bffcc0f`, exactly as the C1 predicate expects, and the counter's own required CORRECTION values are:

- I1: `filed=9-rows derived=rows=2,v2.56.0=0` (source leg blocked until a new S258 tier-A row, mined 2026-10-28, naming `v2.56.0` + `worktree.c`, is appended to `corpus/SOURCES.md`; absent at the freeze tip).
- I3: `filed=like-for-like derived=before=6,after=3` (arms ran over `census/round-39/cells.tsv` vs `census/round-40/cells.tsv`).
- I4: `filed=error-text-recorded derived=occurrences=0` (text committed only in `LOG.md:1909` itself in the lane; the real capture lives in fleet report `.ufo/reports/round-40/souji.md:79` and sibling lanes' untracked wave files).

Recon verdict: **C1 predicate grounded — each item's filed statement disagrees with committed state at MEASURED; no instrument defect found** (counter/items digests match their pins; `.ufo/waves/round-40/` not committed at MEASURED is a fact the counter's `census/round-40/waves/`-only derivation handles).

## Report
Evidence-seat: `.ufo/waves/round-41/w1/R41scout03.md` (this file; only lane path written).
