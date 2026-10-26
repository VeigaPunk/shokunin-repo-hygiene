# Cross-claim and separability check on what landed (Souji r32, attempt 2, wave a2w1)

Seat SwarmConnector29. All claims below were re-derived this run from committed bytes and live
counter runs in scratch clones (origin removed); no lane mutation. Tip = 4e56c48b8fc828f9aba2746e324dc46aa538bdbf.

## Evidence

1. **T18 anchor, static recompute (fixture's own algorithm).** `tests/fixtures/r20-input-binding.py:1252-1256` builds the
   closure from the r13/r14/targeted/demo `MEASURED_PATHS`; `compare_baseline` (:1137-1163) sha256-compares each closure
   file against `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`, one mismatch per differing/added/missing path. Recomputed:
   base `85b61a1…` = **26**, C2 landing `98e5203…` = **31** (+5), C3 landing `a92e1aa…` = **32** (+1), C1 landing and tip = **32**.
   Attribution at C2: `tools/souji-census.sh`, `tools/souji-cert-evidence.py`, `tools/souji-evidence-cache.py`,
   `tools/souji-repo-structure.sh`, `tools/souji-round9-selftest.sh` — all in the r13/r14/demo closure, all patched by 98e5203.
   Attribution at C3: `corpus/knowledge/jj-abandoned-object-mtime-clock.md` (new, +1). `corpus/SOURCES.md` is count-neutral:
   it already differed from 12516f7 at base (one of the 26); C3's edit keeps it one mismatch. Closure membership from bytes:
   `census/round-13/run-verification.py:107` (`corpus/SOURCES.md`), `:108` (`corpus/knowledge`), `:109` (`LOG.md`).
2. **T18 anchor, live runs.** Fixture at base: `SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=26`.
   Fixture at tip: `... baseline_mismatches=32`. Frozen counter at tip, `--only T03,T18`:
   `ITEM T18 FAIL base=rc0:W4233:SUMMARY ... baseline_mismatches=26 sbox=rc0:W4228:SUMMARY ... baseline_mismatches=32 regress`.
3. **C1 run bindings under the landed C2 patch.** Frozen c1-counter (v1 and v2) at tip over all 44 items:
   `SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6` (mismatches = the 6 unbound;
   every bound row MATCHes). Run rows: `N12 … MATCH … SUMMARY total=35 failed=0 skipped=2`;
   `N16 … MATCH … SUMMARY total=17 failed=0 base_discriminating=12`; `N19 … MATCH … grounded=6 mapped=6 dangling=0 mismatches=0`.
4. **T03 immunity.** Frozen c2-counter at tip: `ITEM T03 PASS base=rc1:W0:assertions=252 resolved=229 skipped=401 mismatches=23
   sbox=rc1:W0:assertions=252 resolved=229 skipped=401 mismatches=23`. `tools/souji-declared-evidence.py:73-80` reads the
   declaration from the named revision via git, never the worktree; T03 names `--rev 85b61a1…` (base), so C1's SCORECARD
   append (9e8982b) is invisible to it. C2's patch to the tool (98e5203) is a tempfile-dir/docstring change only.
5. **Q65 recurrences.** `.gitignore:1` = `.ufo/waves/`; `git cat-file -e 4e56c48:.ufo/waves/round-32/w1/SwarmCritic35.md` → rc 128.
   Committed citations of those paths: `census/round-32/records/amendments.txt:14` and
   `corpus/knowledge/jj-abandoned-object-mtime-clock.md:4` (the latter content-addressed: its sha256
   `01cf6dc0011ae8f22d16922846b6834641df5dbce6e3a26cd0c267ede97e8254` matches the on-disk gitignored delivery file).
6. **Salvage records re-derived.** C1 v1+v2 at tip reproduce the amendment's integration reading (`unbound=6 mismatches=6
   withdrawn=17`); C2 `--only T03,T18` reproduces the recorded T18 mechanism (26→32). The attempt-1 after-records are
   consistent with re-derivation.

## Affected axes

- operability (C2): T18 is dead-by-construction — no rev carrying the round's own work can print BASE's `baseline_mismatches=26`.
- calibration (C1): the 6 unbound cells remain; no landed binding moved (N12/N16/N19 MATCH at tip, v1 and v2).
- coverage (C3): not moved by C1/C2 (L2/L3 execute export-at-V bytes; C2's gate-check patch is selftest-scratch-only).

## Findings — couplings the preregistration separability paragraph (Q59) missed

1. **C2→C2 (self).** T18's pass rule (c2-counter.py:174-176) requires SBOX to print BASE's last line verbatim; that line
   embeds `baseline_mismatches=<n>` counting closure files that C2's own repair touches (5 of them). The frozen predicate
   is unsatisfiable for T18 at any rev containing the fix. This is the Q58 class (r28 spotcheck defect 4: a frozen literal
   not derived from the instrument's behavior under the round's own work), not named in the paragraph.
2. **C3→C2.** `corpus/SOURCES.md` and `corpus/knowledge` are T18 closure files (r13 measured paths). Any knowledge-dir
   admission moves the anchor +1 per new file; any SOURCES/knowledge edit moves it if the file matched 12516f7. `LOG.md`
   is also a closure file, so every landing's LOG append moves a hash (count-neutral only because it already differed).
   The paragraph's claim "C3's fixture, entry and rows are outside … C2's item set" is false for T18.
3. **C2→C1 is contingent, not blocked by base blobs.** The paragraph's justification "run bindings execute scripts from the
   --base blob" holds only for the entry script: `c1-counter.py:227-231` materializes just `script_of(argv)` from the base
   blob into the REV clone; everything the script reaches by path is REV bytes. Landed run rows: N12's fixture execs
   `tools/souji-verify.sh|souji-vault-verify.sh|souji-quarantine.sh` (none patched by C2 — unmoved); N16's fixture execs the
   live `tools/souji-seat-audit.py` (patched by C2, grant grammar) — output-neutral on its 17 fixed cases, still MATCH;
   N19 runs `tools/souji-coverage-agreement.py --rev 778747eb…` (git objects at a fixed rev — unmoved). Wave-1 SwarmCritic37
   showed the live form: one C2 rule edit flips run-bound N35/N36 to RUN-MISMATCH; the landed rows rebind N35-N41 as record
   bindings, which is why nothing moved. The coupling survives for any future run row whose fixture execs a C2-owned tool.
4. **C2→C3 is structural but currently output-neutral.** c3-counter L2 runs `tools/souji-coverage-agreement.py` and L3 runs
   `tools/souji-gate-check.py` from the rev-V export (c3-counter.py:150,154), so C2's edits move C3 legs only when the measured
   rev carries them; C2's gate-check hunk is selftest-scratch-only and L3's expectation held (amendments: C3 v1+v2 met at the
   integration commit). Paragraph silent on this direction.
5. **C1→C2 T03: paragraph verified.** See evidence 4 — byte-level confirmation both of fixed-rev reading and of pass-at-tip.
   Also verified for T02/T29/T30: `tools/souji-landing-gate.py:239,1189` reads `SKILL.md`/`corpus/README.md`/`SCORECARD.md`
   via `git ls-tree`/`show` at the named rev, so C1's append and C3's README/SKILL edits do not move them.

## Recurring wave-1 mistake classes (r28–r31 lessons)

- **Q58 class** (r28 spotcheck d4): recurs as T18's frozen S-equality on a count the round's own landings move (Finding 1).
- **Instrument/gaming class** (r31 lesson "instrument" row): C2 v1 passed with clone-local scratch and a fabricated anchor +
  dummy creates (SwarmCritic34 — disclosed, *not* amended); C3 v1 met with a constant-printing fixture and a fetch receipt
  claiming 200 for a 404 URL (SwarmCritic35 → A1, stricter-only: L15-L17).
- **Contract class** (r31 D1/M1): the dishonest-receipt recurrence is SwarmCritic35's fake 200, caught pre-landing by A1 L17;
  M1's guard (`tools/souji-record-contract.py` + C3 leg L14) shipped with its red-before.
- **Reference-drift / cite-uncommitted-evidence** (r29 D1, r30 Q65): recurs in committed r32 text at `amendments.txt:14` and
  `corpus/knowledge/jj-abandoned-object-mtime-clock.md:4`, citing gitignored `.ufo/waves/round-32/…` paths absent from the
  tip tree (evidence 5). Routed r32 defect 4's correction sweep did not catch them.
- **Disposition class** (r31): not recurring — the r32 misses (C1 6 unbound, T18) are recorded with mechanism in amendments.txt.
- **Host-loss class** (new, not from lessons): attempt 1 died in the orchestrator crash; its after-records re-derived clean (evidence 6).

## Proposed move (one, bounded — for the L1's post-wave landing)

In the lesson/LOG landing commit: (a) carry T18 with the byte-attribution table above (5 self-files + 1 C3 file; LOG.md and
SOURCES.md count-neutral), and re-run the frozen C2 counter at the final tip, landing the receipt showing `fail=1`
attributable solely to T18 — this satisfies "target must hold at the final tip" honestly as a recorded miss rather than a
silent one; (b) append-only-correct the two `.ufo/waves/round-32` citations in `amendments.txt:14` and the C3 entry's front
matter to name committed captures (or drop the path and keep the verified sha256); (c) carry C2's disclosed-not-amended v1
predicate gap (SwarmCritic34 Cheats A/B) into the r33 routed list, since wave 2 was told to re-apply the cheats post-amendment
and no amendment landed. No counter, predicate, or target changes; nothing here relaxes the frozen contract.

## Risks

- (a) records a MISS on the operability axis for r32 — already the amendment's disposition; this only makes the attribution
  byte-precise. Risk of not doing it: a future seat "fixes" T18 by reverting closure files or gaming the anchor.
- (b) append-only corrections touch two committed files; both are stricter-only in the sense of r29-D1/Q65 discipline.
- (c) is a routing note; it admits the v1 predicate stays gameable for any r32 re-measurement — mitigated by the disclosure.

## Verification of this check

- Static closure recompute == live fixture runs == frozen counter readings at every landing rev (26/31/32/32/32).
- Frozen c1-counter v1 and v2 at tip; frozen c2-counter `--only T03,T18` at tip; fixture T18 at base and tip.
- All scratch clones under /fast/scratch/hyaku/souji-r32/SwarmConnector29 (removed after the report copies).
