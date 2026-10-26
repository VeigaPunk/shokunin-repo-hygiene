## Status

STATUS: PARTIAL — every measured span and every located quote in the four audited artifacts resolves (8 of 8 quoted `RESULT` spans are exact record lines, 23 of 23 Gate quotes sit at their stated snapshot anchors, all four citation hashes/sizes match the bytes), but 19 sentences carry more than their support: 2 are refuted by a reproduced state (entry claim 1's "Reachability decides nothing", entry claim 7's `--prune=never` attribution) and 17 overreach or mis-locate. All proposed corrections are append-only; none touches a predicate, target, counter, item set or the frozen contract, and no axis is harmed (calibration 7, operability 8, coverage 8 measurements are unchanged by prose).

## Evidence

Audited revision: C3 landing `a92e1aae91dbf46c2d7eff713932cfc820186970`; the four artifacts are byte-identical at the lane tip `4e56c48b8fc828f9aba2746e324dc46aa538bdbf` (`git diff a92e1aa 4e56c48 -- <entry> corpus/README.md PROVINCE.md SKILL.md` empty), so every line number below holds at the tip.

The working tree carries unlanded edits by other a2w1 seats (`git status`: `SKILL.md`, two r15 fixtures, `tools/souji-receipt-run.py`, one new record); I touched none of them. The pending `SKILL.md` edit only rewrites two path prefixes inside the r32 bullet (`../census/…` → `census/…`), same line count, so the line numbers below survive it; they are refs to committed bytes.

Integrity of the cited bytes (all re-derived from committed blobs this run):
```
git cat-file blob a92e1aa:<path> | sha256sum ; git cat-file -s
census/round-32/sources/gitformat-pack.adoc  ec285ba4f4e15a68ad83a570eaf74e8549b477496e49933126ef935d9291381b  27494 B
census/round-32/sources/git-gc.adoc          e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c   6744 B
census/round-32/sources/gc.adoc              0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a   7753 B
census/round-32/records/jj-mtime-clock-run.txt 01cf6dc0011ae8f22d16922846b6834641df5dbce6e3a26cd0c267ede97e8254 1887 B
```
The record equals the fixture seat's delivery byte for byte (`.ufo/waves/round-32/w1/deliver-jj-mtime-clock-run.txt`, same sha256, 1887 B), and the git-gc snapshot equals the round-30 capture at `85b61a1:census/round-30/sources/git-gc.adoc`, so the entry's "installed unchanged at landing" and "byte-identical to the round-30 capture" claims hold.

Span-to-record check: each of the 8 `RESULT` spans quoted in the entry's **Observed** section matched exactly one whole record line (`grep -cxF` = 1 for each, and `grep -cF` = 1 in the entry). Contract check by the committed tool, on the committed bytes:
```
python3 -B tools/souji-record-contract.py --record <a92e1aa:…/jj-mtime-clock-run.txt> --contract <a92e1aa:…/c3-contract.txt>
lines=22 bad=0   rc=0
```
Quote-to-snapshot check: all 23 Gate quotes resolve at their stated anchors — gitformat-pack `:351-353`, `:353-354`, `:613-614`, `:631-632`, `:635-636`, `:638-640`, `:655-656`, `:667-668`, `:674-675`, `:682-683`, `:684-685`, `:688-689`; git-gc `:63-64`, `:64-65`, `:82-83`, `:84`, `:90`, `:160-161`; gc.adoc `:86-88`, `:97`, `:98-99`, `:100-102`, `:102`. The include claim also holds: git-gc.adoc `:136` is `include::config/gc.adoc[]`.

My own measurements (scratch under `/fast/scratch/hyaku/souji-r32/SwarmCritic20/`, git 2.56.0, isolated config `GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null HOME=<scratch>`; these are new measurements, not lane evidence, and the attempt-1 after-records were not used):

- `GIT_TRACE=1 git gc --prune=never` in a scratch repo prints `trace: run_command: git repack -d -l --cruft --cruft-expiration=never` and `trace: run_command: git prune --expire never`.
- `GIT_TRACE=1 git gc` prints `trace: run_command: git repack -d -l --cruft --cruft-expiration=2.weeks.ago` then `trace: run_command: git prune --expire 2.weeks.ago`.
- Faithful plain-git analogue of the `mixed` arm (A, B on A; reset to A; C on A; every ref and reflog entry naming B or C gone; B's island backdated 30 d; `gc --prune=never`; then `git gc`): `start B=loose C=loose`, `after --prune=never B=cruft C=cruft cruft_packs=1`, `after default gc B=absent C=cruft` — the record's four `mixed` lines reproduce exactly.
- Plain-git analogue of the `old` arm (loose old B, default `git gc`): B absent — the record's `arm=old` line reproduces.

## Findings

**F1 (refuted; entry `:21`).** "Reachability decides nothing at that boundary" — neither support nor the fixture's design carries it. The sentence's own quote keeps "along with everything reachable from it" (git-gc.adoc:160-161), and the fixture backdates the whole unreachable island *because* a recent descendant would otherwise hold B (`island_commits` :214-219, `backdate_island` :231-236). Reproduced: A, then B on A, then C on B; reset to A; reflog expired; only B's own island backdated 30 days; `git gc` → `B=cruft C=cruft` (B kept by the recent unreachable descendant). Correction: append "Reachability is not the criterion applied to the object itself; a recent object reachable from it is kept with it, which is why the old arms backdate the whole island."

**F2 (outcome-relevant understatement; entry `:26`).** "backdates B's own commit, tree and blob files" — the fixture backdates every commit of B's unreachable island, not B's three objects (`backdate_island` :231-236 over `island_commits` :214-219). A reader reproducing claim 1's stated method gets F1's opposite result (reproduced above). Correction: replace with "backdates every commit in B's unreachable island (commit, tree and blob per `rev-list --objects … --not …^`, :222-229)".

**F3 (support gap; entry `:64-65`).** "One pack, one command, two fates, decided by the per-object dates." No record line counts packs or places B and C in the same pack; `where` only says the object is listed in a pack that has a `.mtimes` sibling (:107-120). My plain-git analogue produced one cruft pack, but that is not a line of the record. Correction: "one invocation, two fates" (pack count unmeasured by any arm).

**F4 (call attribution unmeasured; entry `:72-73` and `:143-145`).** "and B was not loose at that point, so no loose prune can account for the removal" and "The record measures both removal paths: the packed old object goes at the cruft call". The record has no call-level field, and the entry's own limits bullet (`:167-168`) says the internal path "is not measured". My `GIT_TRACE` run supplies the missing measurement (repack, then prune, same date). Correction: either cite a trace receipt or hedge to "the record localises the removal by location, not by internal call".

**F5 (refuted; entry `:85-93`, and the third REJECT at `:226`).** At `:86` the entry attaches `"Do not prune any loose objects." (git-gc.adoc:89-90)` to `--prune=never`; snapshot `:89-90` is the `--no-prune` option, and the Gate's own line for that quote is labelled "§ OPTIONS --no-prune line 90". The measured option is `--prune=<date>` (`:81-87`). The inference also fails: `git gc --prune=never` forwards `never` to the cruft call (`repack … --cruft --cruft-expiration=never`, traced), so the mixed-arm outcome is the flag's forwarding, not "more than its one-line description claims"; the record does bear it out. Correction: attribute the quote to `--no-prune`; keep the receipt rule (record the argv) but justify it by the single date both calls receive (gc.adoc:96-99), and rewrite the REJECT reason to rest on the forwarded date, not on an undocumented reach.

**F6 (overstatement; entry `:164-166`).** "so the flag's forwarding to the cruft call is measured, not explained" — only the outcome is measured; no record line carries an argv, and L12 counts calls without printing them. Correction: "the outcome is measured; the forwarding is inferred from it and from gc.adoc:96-99".

**F7 (wrong count and range; entry `:178-179`).** "`corpus/README.md`:679-681 is the F1 frontier line that names the two questions this entry answers". README `:679-682` names four remaining items (the exposure numerator at `:46`, which reflog file carries the naming entry, the cruft-handling question, the real 90/30-day windows); this entry answers one of them, and the object's own clock is named at `:701`, not there. Correction: "the cruft-handling question at README `:680-681`; the clock question is the `:701` wave-2 correction".

**F8 (impossible location; entry `:1`).** "§ cruft packs lines 611-689, including the `.mtimes` table at lines 341-354" — `:341` is a different section header (`== pack-*.mtimes files have the format:`), not inside `611-689`. Correction: name the two ranges separately (611-689; 341-358).

**F9 (stale identity; entry `:1` and `:198`).** "placeholder id: the L1 renumbers by document" and "The gitformat-pack row is a placeholder id for the L1 to renumber by document." At the landing commit `corpus/SOURCES.md:168` already holds S223 as the canonical gitformat-pack row; the instruction tells a later seat the id is provisional. Correction: "S223 = corpus/SOURCES.md:168".

**F10 (cross-arm inference; entry `:46-48`).** "so one variable, `gc.cruftPacks`, decides which" — the two arms differ in repository composition (arm `recent` holds only B; arm `nocruft` holds B and C) as well as in that value and in object identity. Correction: "in the arms that differ in that value".

**F11 (circular citation; entry `:99`, README `:725`).** "so repeated runs print identical lines (fixture header, tests/fixtures/r32-jj-mtime-clock.sh:35-46)" and README's "deterministic across runs" cite the fixture's own assertion; the measured support is the counter's replay leg L9 (two replays; SKILL `:253`). I did not replay the fixture, so this is a citation defect, not a failed check. Correction: cite L9 (and note the attempt-1 after-record is unverified until re-derived).

**F12 (legend narrower than the contract; entry `:103`).** The `where` legend omits `pack`, one of the frozen contract's four allowed values (`c3-contract.txt` lists loose, cruft, pack, absent), and omits the membership test at `:114`. No record line prints `pack`, so no factual error. Correction: add "else `pack` when the object is listed in a pack without a `.mtimes` sibling".

**F13 (incomplete enumeration presented as complete; README `:738-741`).** "the classes the entry's own limits section leaves open — no lane or fleet repository gc'd, the mtime keeper not isolated against a live keep ref or a reflog entry, the `never` asymmetry read from the docs rather than implemented, and the two-week window sourced rather than waited out" — the entry's limits section leaves seven classes open (adds the unread `.mtimes` contents, the unopened cruft-call argument, and `gc.recentObjectsHook`). Correction: append the three omissions.

**F14 (misstates what is implemented; README `:740`).** "the `never` asymmetry read from the docs rather than implemented" — both never levers are implemented and measured (`arm=never step=gc-pruneexpire-never`, `arm=mixed step=gc-prune-never`); what is documentary is why the flag reaches repack, and that forwarding is now traceable. Correction: "the flag's forwarding is not opened in this round's record (a trace does show it)".

**F15 (false at round scope; PROVINCE `:256`).** "The round's one tool change is `tools/souji-record-contract.py`" — round 32's C2 commit `98e5203` changed 12 files under `tools/` (`souji-census.sh`, `souji-cert-evidence.py`, `souji-declared-evidence.py`, `souji-evidence-cache.py`, `souji-gate-check.py`, `souji-landing-gate.py`, `souji-preservation-evidence.py`, `souji-receipt-run.py`, `souji-repo-structure.sh`, `souji-rev-pin.py`, `souji-round9-selftest.sh`, `souji-seat-audit.py`) plus 15 fixtures, and `tools/souji-record-contract.py` was added earlier, at `3ec84fc`. Correction: scope the sentence to C3 ("this note's one tool change") and record the C2 tool count.

**F16 (unsupported sentence; PROVINCE `:250`).** "absence is not proved by an object count the lane did not run" — no count appears in this claim, and no record line or snapshot names one. Correction: restore the r31 formulation (a receipt must name the expiry and prune date it observed) or name the count.

**F17 (overreach and inverted wording; SKILL `:144-145`).** "the object's own modification time is what decides its fate under `git gc`" omits the two deciders the entry itself names: a recent descendant (F1, reproduced) and `gc.recentObjectsHook` (entry `:169-170`, r31 claim 4). "a recent object survives the `gc.pruneExpire` window" reads as outliving the window; a recent object is kept *inside* it (record `arm=old`). Correction: add "with no recent descendant and no `gc.recentObjectsHook` in play" and reword to "a recent object is kept inside the window".

**F18 (stale instrument identity, adjacent to the bullet; SKILL `:253`).** "the judging instrument is the r32 C3 counter's legs L8 (record shape and arm coverage), L9 (two replays equal the record), L12" — amendment A1 landed in the same commit as C3 and made L15/L16/L17 part of the amended target (`legs=17`). Correction: name v2 and its added legs.

**F19 (provenance version; entry Gate `:218-222`).** The five S002 Gate lines name no version while their quotes come from the v2.56.0 `config/gc.adoc` snapshot and SOURCES `S002` is scoped to "git 2.55.0 grace periods"; S063 and S223 Gate lines do name v2.56.0. Correction: add "v2.56.0" to the S002 Gate lines (the entry header already carries it).

No finding touches the counter, the item set, the contract, the fixture's refusal guards, the record's 22 lines or the three claim targets.

## Attack log

- **A1 — claim 1's reachability clause. Result: refuted, reproduced.** Constructed A←B←C with C on B, reset to A, expired every reflog, backdated only B's island 30 days, `git gc` → B kept (`where=cruft`). Reachability decided, contrary to the sentence; the fixture avoids exactly this case by backdating the island.
- **A2 — claim 7's flag reach. Result: refuted, traced.** `GIT_TRACE=1 git gc --prune=never` → `repack -d -l --cruft --cruft-expiration=never` and `prune --expire never`; the flag hands its own date to the cruft call, so the mixed outcome is the documented forwarding. The body's quote is `--no-prune`, which the artifact's own Gate labels correctly.
- **A3 — is the record's `mixed`/`old` outcome reproducible in plain git? Result: attack withdrawn.** My first plain-git mixed analogue kept the old B and clamped its `.mtimes` to 14 days; the cause was my construction (C committed on B, a recent descendant), not the record. The faithful analogue (C on A, isolated config) reproduces `B=absent C=cruft` and `cruft_packs=1`; the loose-old analogue reproduces `arm=old`. The record's outcome lines are sound; only their prose attribution (F3, F4) is not.
- **A4 — duplicate authority: "the round's one tool change".** Repo evidence refutes it (F15); this is the finding most likely to mislead a later receipt-root reading, because C2 patched `souji-receipt-run.py` and `souji-landing-gate.py` in the same round.
- **A5 — identity/staleness cluster** (F8, F9, F18): a location that cannot exist, a placeholder note for an id already assigned, and a judge list that predates the amendment landed beside it.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/a2w1/SwarmCritic20.md` (this report).
- Scratch `/fast/scratch/hyaku/souji-r32/SwarmCritic20/` removed after copying; nothing written or committed in the lane, no lane git/jj state touched, no tool installed.
