# Round 44 — token binding, repaired oracle, defensive symlink cutover

Round: 44. Author: souji. Claims frozen at `d314fd6e85d62565344fa6c4b102f52f62297884`, `census/round-44/preregistration.txt`; inherited instrument work in `4641e14671e60bf6cdc62ba8045c02a387a0d72c` and `6538a153` retained. The correction counter's missing explicit Git root was repaired before freeze. Historical counters remain unchanged.

## Gate

- Admit S264 for C2's multiset vocabulary only. URL https://docs.python.org/3/library/collections.html#collections.Counter opened 2026-10-30 by SoujiR44a2. Location: Counter objects, class description. Quote: “The Counter class is similar to bags or multisets in other languages.” Located receipt: `census/round-44/sources/collections-located-quote.txt`. This is not proof that any scenario's expected multiset is correct.
- Reject S265, the candidate inference that Counter semantics alone validate the hidden audit. URL https://docs.python.org/3/library/collections.html#collections.Counter opened 2026-10-30, Counter objects class description; same located quote: “The Counter class is similar to bags or multisets in other languages.” The source describes data structures, not this lane's grammar. Flip: independent grammar-derived scenario checks plus a non-crashing discriminating negative control.
- Existing source status/recheck/used-by cells unchanged. New S264 status mined, used-by this lesson; S265 status rejected, used-by none. Sources before census `census/round-44/records/census-before.txt`, exit 0.
- Outside admit/reject spot-check pending: lane-dispatched seats are authors for this protocol and cannot supply outside admission.
- Assimilation: none. No considerthese directory was returned by the lane's named file census; no package adoption or Core promotion claimed.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| oracle multiplicity and post-freeze edit omission | `corpus/lessons/round-43-verifier-spotcheck.md:36-40`; `census/round-44/controls/c2-donothing.txt` retains h4/h6 red | Q106 | `census/round-44/c2-hidden-audit.py` expands repeated FIELD-MISSING entries and includes FROZEN-EDITED; frozen r43 audit stays red. The before receipt demonstrates failure; final counter receipt determines whether repaired audit works. |
| derived token not bound to measured bytes | `corpus/lessons/round-43-verifier-spotcheck.md:78` | Q97/Q101 | frozen C1 compares each correction token with its committed-base derivation. Registration is not proof that already corrected historical facts became newly corrected. |
| formal preregistration after handoff | `corpus/lessons/round-43-verifier-spotcheck.md:83` | Q99 | this round lands preregistration at d314fd6e85d62565344fa6c4b102f52f62297884 before creating w1.ready. No retroactive timing repair claimed. |

## Correction scope

The register below refers only to token referents on historical SCORECARD lines at base `55d7af6f5a22340f7a3de1c386e514ababfaa75f`. Paths are base-tree paths; multi denotes ambiguity, UNHELD/UNRESOLVED denote no derived referent under the finite rules. These tokens do not re-measure historical runtime behavior. Prior correction/supersession entries remain authoritative: registering an already corrected item is bookkeeping, not a second calibration gain. Duplicate occurrence keys share one correction, as the frozen instrument specifies.

CORRECTION-R44 id=R44-01 file=SCORECARD.md line=14 class=mismatch:rev-unresolved stale=65817d0d derived=UNRESOLVED rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-02 file=SCORECARD.md line=21 class=mismatch:path-absent stale=c1-after.tsv derived=multi:census/round-24/records/WRONG-c1-after.tsv;census/round-25/records/c1-after.tsv;census/round-26/records/c1-after.tsv;census/round-27/records/c1-after.tsv;census/round-28/records/c1-after.tsv rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-03 file=SCORECARD.md line=22 class=mismatch:path-absent stale=c2-after.tsv derived=multi:census/round-24/records/c2-after.tsv;census/round-25/records/c2-after.tsv;census/round-26/records/c2-after.tsv;census/round-27/records/c2-after.tsv;census/round-28/records/c2-after.tsv;census/round-42/waves/w1/R42critic01/k4/c2-after.tsv rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-04 file=SCORECARD.md line=23 class=mismatch:path-absent stale=c3-after.tsv derived=multi:census/round-24/records/c3-after.tsv;census/round-25/records/c3-after.tsv;census/round-26/records/c3-after.tsv;census/round-27/records/c3-after.tsv;census/round-28/records/c3-after.tsv rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-05 file=SCORECARD.md line=31 class=mismatch:path-absent stale=c1-after.tsv derived=multi:census/round-24/records/c1-after.tsv;census/round-25/records/c1-after.tsv;census/round-26/records/c1-after.tsv;census/round-27/records/c1-after.tsv;census/round-28/records/c1-after.tsv rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-06 file=SCORECARD.md line=50 class=mismatch:path-absent stale=w2/RevR3Counter.md derived=.ufo/waves/round-25/w2/RevR3Counter.md rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-07 file=SCORECARD.md line=68 class=mismatch:path-absent stale=count-objects-garbage-readings-r25.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/count-objects-garbage-readings-r25.md;census/round-26/waves/assimilation/validate/corpus/knowledge/count-objects-garbage-readings-r25.md;corpus/knowledge/count-objects-garbage-readings-r25.md rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-08 file=SCORECARD.md line=68 class=mismatch:path-absent stale=repo-size-census-readonly.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/repo-size-census-readonly.md;census/round-26/waves/assimilation/validate/corpus/knowledge/repo-size-census-readonly.md;corpus/knowledge/repo-size-census-readonly.md rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-09 file=SCORECARD.md line=68 class=mismatch:digest stale=42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44 derived=sha256:bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-10 file=SCORECARD.md line=68 class=mismatch:digest stale=71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897 derived=sha256:bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-11 file=SCORECARD.md line=71 class=mismatch:path-absent stale=git-repo-structure-readonly.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;census/round-26/waves/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;corpus/knowledge/git-repo-structure-readonly.md rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-12 file=SCORECARD.md line=92 class=mismatch:rev-unresolved stale=09bb8e0d derived=UNRESOLVED rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-13 file=SCORECARD.md line=103 class=mismatch:path-absent stale=git-repo-structure-readonly.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;census/round-26/waves/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;corpus/knowledge/git-repo-structure-readonly.md rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-14 file=SCORECARD.md line=174 class=mismatch:path-absent stale=c1-control-stub.tsv derived=census/round-24/records/c1-control-stub.tsv rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-15 file=SCORECARD.md line=175 class=mismatch:path-absent stale=c2-after.tsv derived=multi:census/round-24/records/c2-after.tsv;census/round-25/records/c2-after.tsv;census/round-26/records/c2-after.tsv;census/round-27/records/c2-after.tsv;census/round-28/records/c2-after.tsv;census/round-42/waves/w1/R42critic01/k4/c2-after.tsv rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-16 file=SCORECARD.md line=175 class=mismatch:path-absent stale=c2-fixture-after.tsv derived=census/round-24/records/c2-fixture-after.tsv rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-17 file=SCORECARD.md line=220 class=mismatch:path-absent stale=git-repo-structure-readonly.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;census/round-26/waves/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;corpus/knowledge/git-repo-structure-readonly.md rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-18 file=SCORECARD.md line=221 class=mismatch:path-absent stale=git-auto-maintenance-prunes-worktrees.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/git-auto-maintenance-prunes-worktrees.md;census/round-26/waves/assimilation/validate/corpus/knowledge/git-auto-maintenance-prunes-worktrees.md;corpus/knowledge/git-auto-maintenance-prunes-worktrees.md rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-19 file=SCORECARD.md line=221 class=mismatch:path-absent stale=git-grace-periods-and-expire-to.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/git-grace-periods-and-expire-to.md;census/round-26/waves/assimilation/validate/corpus/knowledge/git-grace-periods-and-expire-to.md;corpus/knowledge/git-grace-periods-and-expire-to.md rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-20 file=SCORECARD.md line=314 class=mismatch:path-absent stale=excluded.tsv derived=multi:census/round-26/waves/excluded.tsv;census/round-42/waves/excluded.tsv rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-21 file=SCORECARD.md line=314 class=mismatch:path-absent stale=symlinks.tsv derived=census/round-26/waves/symlinks.tsv rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-22 file=SCORECARD.md line=424 class=mismatch:path-absent stale=c3-after-c3-counter-v2.txt derived=census/round-31/records/c3-after-c3-counter-v2.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-23 file=SCORECARD.md line=424 class=mismatch:path-absent stale=c3-after-c3-counter-v3.txt derived=census/round-31/records/c3-after-c3-counter-v3.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-24 file=SCORECARD.md line=478 class=mismatch:path-absent stale=.ufo/waves/round-32/a2w1/SwarmExecutor08.md derived=UNHELD rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-25 file=SCORECARD.md line=487 class=mismatch:path-absent stale=SwarmCritic34.md derived=census/round-32/waves/w1/SwarmCritic34.md rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-26 file=SCORECARD.md line=489 class=mismatch:path-absent stale=SwarmCritic26.md derived=multi:census/round-30/waves/w1/SwarmCritic26.md;census/round-31/waves/w2/SwarmCritic26.md;census/round-32/waves/a2w1/SwarmCritic26.md;census/round-33/waves/w1/SwarmCritic26.md;census/round-34/waves/w2/SwarmCritic26.md rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-27 file=SCORECARD.md line=512 class=mismatch:path-absent stale=c1-at-c2-repair.txt derived=census/round-33/records/c1-at-c2-repair.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-28 file=SCORECARD.md line=513 class=mismatch:path-absent stale=c2-at-repair.txt derived=census/round-33/records/c2-at-repair.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-29 file=SCORECARD.md line=525 class=mismatch:path-absent stale=.ufo/waves/round-33/make-spec-w2.py derived=UNHELD rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-30 file=SCORECARD.md line=540 class=mismatch:path-absent stale=controls.txt derived=multi:census/round-33/records/controls.txt;census/round-34/records/controls.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-31 file=SCORECARD.md line=666 class=mismatch:path-absent stale=c1-vacuity2.txt derived=census/round-38/records/c1-vacuity2.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-32 file=SCORECARD.md line=666 class=mismatch:path-absent stale=c1-after2.txt derived=census/round-38/records/c1-after2.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-33 file=SCORECARD.md line=667 class=mismatch:path-absent stale=c2-after2.txt derived=census/round-38/records/c2-after2.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-34 file=SCORECARD.md line=668 class=mismatch:path-absent stale=c3-before.txt derived=multi:census/round-37/records/c3-before.txt;census/round-38/records/c3-before.txt;census/round-39/records/c3-before.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-35 file=SCORECARD.md line=668 class=mismatch:path-absent stale=c3-after2.txt derived=census/round-38/records/c3-after2.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-36 file=SCORECARD.md line=673 class=mismatch:path-absent stale=consumers-after2.txt derived=census/round-38/records/consumers-after2.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-37 file=SCORECARD.md line=699 class=mismatch:path-absent stale=c1-vacuity4.txt derived=census/round-38/records/c1-vacuity4.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-38 file=SCORECARD.md line=700 class=mismatch:path-absent stale=c2-after4.txt derived=census/round-38/records/c2-after4.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-39 file=SCORECARD.md line=701 class=mismatch:path-absent stale=c3-after3.txt derived=census/round-38/records/c3-after3.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-40 file=SCORECARD.md line=702 class=mismatch:path-absent stale=consumers-after4.txt derived=census/round-38/records/consumers-after4.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-41 file=SCORECARD.md line=702 class=mismatch:path-absent stale=a7-counter-fixes.txt derived=census/round-38/records/a7-counter-fixes.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-42 file=SCORECARD.md line=709 class=mismatch:path-absent stale=c1-vacuity5.txt derived=census/round-38/records/c1-vacuity5.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-43 file=SCORECARD.md line=710 class=mismatch:path-absent stale=c2-after5.txt derived=census/round-38/records/c2-after5.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-44 file=SCORECARD.md line=712 class=mismatch:path-absent stale=c3-after4.txt derived=census/round-38/records/c3-after4.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-45 file=SCORECARD.md line=721 class=mismatch:path-absent stale=c1-vacuity6.txt derived=census/round-38/records/c1-vacuity6.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-46 file=SCORECARD.md line=722 class=mismatch:path-absent stale=c2-after6.txt derived=census/round-38/records/c2-after6.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-47 file=SCORECARD.md line=725 class=mismatch:path-absent stale=a7-counter-fixes2.txt derived=census/round-38/records/a7-counter-fixes2.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-48 file=SCORECARD.md line=731 class=mismatch:path-absent stale=c1-after8.txt derived=census/round-38/records/c1-after8.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-49 file=SCORECARD.md line=732 class=mismatch:path-absent stale=c2-after7.txt derived=census/round-38/records/c2-after7.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-50 file=SCORECARD.md line=733 class=mismatch:path-absent stale=c3-arms-filed.txt derived=census/round-38/records/c3-arms-filed.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-51 file=SCORECARD.md line=761 class=mismatch:path-absent stale=c1-after.txt derived=multi:census/round-36/records/c1-after.txt;census/round-37/records/c1-after.txt;census/round-38/records/c1-after.txt;census/round-39/records/c1-after.txt;census/round-41/records/c1-after.txt;census/round-42/records/c1-after.txt;census/round-43/records/c1-after.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-52 file=SCORECARD.md line=762 class=mismatch:path-absent stale=c2-before.txt derived=multi:census/round-37/records/c2-before.txt;census/round-38/records/c2-before.txt;census/round-39/records/c2-before.txt;census/round-43/controls/c2-before.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-53 file=SCORECARD.md line=762 class=mismatch:path-absent stale=c2-after.txt derived=multi:census/round-36/records/c2-after.txt;census/round-37/records/c2-after.txt;census/round-38/records/c2-after.txt;census/round-39/records/c2-after.txt;census/round-40/records/c2-after.txt;census/round-41/records/c2-after.txt;census/round-42/records/c2-after.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-54 file=SCORECARD.md line=763 class=mismatch:path-absent stale=c3-before.txt derived=multi:census/round-37/records/c3-before.txt;census/round-38/records/c3-before.txt;census/round-39/records/c3-before.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-55 file=SCORECARD.md line=763 class=mismatch:path-absent stale=c3-after.txt derived=multi:census/round-36/records/c3-after.txt;census/round-37/records/c3-after.txt;census/round-38/records/c3-after.txt;census/round-39/records/c3-after.txt;census/round-40/records/c3-after.txt;census/round-41/records/c3-after.txt;census/round-42/records/c3-after.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-56 file=SCORECARD.md line=772 class=mismatch:path-absent stale=c2-after.txt derived=multi:census/round-36/records/c2-after.txt;census/round-37/records/c2-after.txt;census/round-38/records/c2-after.txt;census/round-39/records/c2-after.txt;census/round-40/records/c2-after.txt;census/round-41/records/c2-after.txt;census/round-42/records/c2-after.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-57 file=SCORECARD.md line=773 class=mismatch:path-absent stale=c3-after.txt derived=multi:census/round-36/records/c3-after.txt;census/round-37/records/c3-after.txt;census/round-38/records/c3-after.txt;census/round-39/records/c3-after.txt;census/round-40/records/c3-after.txt;census/round-41/records/c3-after.txt;census/round-42/records/c3-after.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-58 file=SCORECARD.md line=792 class=mismatch:path-absent stale=fixtures-after.txt derived=census/round-40/records/fixtures-after.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-59 file=SCORECARD.md line=792 class=mismatch:path-absent stale=c2-after-d.txt derived=census/round-40/records/c2-after-d.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-60 file=SCORECARD.md line=793 class=mismatch:path-absent stale=c3-after-d.txt derived=census/round-40/records/c3-after-d.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-61 file=SCORECARD.md line=811 class=mismatch:path-absent stale=c2-after-h.txt derived=census/round-40/records/c2-after-h.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-62 file=SCORECARD.md line=811 class=mismatch:path-absent stale=c3-after-h.txt derived=census/round-40/records/c3-after-h.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-63 file=SCORECARD.md line=821 class=mismatch:path-absent stale=controls/c1-control.txt derived=multi:census/round-41/controls/c1-control.txt;census/round-42/controls/c1-control.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-64 file=SCORECARD.md line=822 class=mismatch:path-absent stale=controls/c2-control.txt derived=multi:census/round-41/controls/c2-control.txt;census/round-42/controls/c2-control.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-65 file=SCORECARD.md line=823 class=mismatch:path-absent stale=controls/c3-control.txt derived=multi:census/round-41/controls/c3-control.txt;census/round-42/controls/c3-control.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
CORRECTION-R44 id=R44-66 file=SCORECARD.md line=832 class=mismatch:path-absent stale=tip-remeasure.txt derived=census/round-41/records/tip-remeasure.txt rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents

## Wave findings and attribution limits

One v2 wave of 66 seats settled by orchestrator WAVE-DONE before this integration.
`census/round-44/records/wave-summary.json` records 60 nonempty outputs and six
empty terminal outputs, not 66 successful verifications. No replacement ran.
The context's phrase “64 seats” was an arithmetic description error: the validated
spec, dispatch and settled handoff each contain 66 actual items.

- C1: `S44reviewer61/report.md` re-derives the same 70-occurrence population as
  r42, 65 path-bound plus five already scoped/corrected, with zero new unresolved
  beliefs under Q76. `S44critic45/report.md` and `S44critic48/report.md` show that
  natural emitted registers remain red: correction keys use (line,class,stale),
  population keys use (line,token,class), and the later derivation lookup also
  uses a different tuple arity. No frozen counter repair or forged workaround
  was applied. C1 is target-unmet and cannot claim calibration improvement.
- C2: `S44reviewer20/report.md` independently derives h4's four repeated
  FIELD-MISSING classes and kills a missing-Control mutant; other scenario
  reviewers retain their exact observations. `S44mutationtester51/report.md`
  demonstrates a size-branching fake audit that reaches the frozen target
  without executing its tool. Fixed-case target success is not authentication.
  Population text checks do not independently compare want_classes; future
  instruments must bind substance and execution before stronger claims.
- C3: `S44reviewer57/report.md` observes new parent-file and parent-loop
  tracebacks at the freeze. The same extended eight-case battery reads
  6/8 before, 8/8 after translating other lstat OSErrors to JSON-UNWRITABLE
  (`census/round-44/records/c3-parent-before.txt`, `c3-parent-after.txt`).
  The counter and its finite five-suite population remain unchanged.
  R43 routed defect 5's operator-decision provenance is unresolved, and the
  question is appended to the fleet L0 queue; technical green is not approval.

Diagnostic attribution: C1 control uses the frozen counter over inherited
revision 4641e14671e60bf6cdc62ba8045c02a387a0d72c; C2 control is the historical
r43 oracle's 8/10, not a full repaired-counter base run; C3 uses the original
base tool/consumer plus a separate old-tool/new-consumer discriminator. These
are not a uniform randomized before/after experiment. The C1 control's phrase
“instruments are unchanged” is too broad: the counter changed pre-freeze;
`census/round-44/records/c1-before.txt` supplies the actual frozen-instrument
baseline. No frozen receipt was rewritten.

All seat pointers in this section are under `.ufo/waves/round-44/w1/`.
`S44critic45/fixture/` was an erroneously retained throwaway clone; L1 removed
that scaffolding after preserving its sibling receipt/candidate files. It was
not committed evidence and is not needed to rerun the retained probe.

## Mistake follow-through

| class | evidence | captured-by | fix |
|---|---|---|---|
| new output preflight broke established parent-error refusal | `.ufo/waves/round-44/w1/S44reviewer57/probe-receipt-valid.json` | Q73 | added OSError conversion and two parent-error fixture cases; identical extended fixture red 6/8 before, green 8/8 after, receipts above |
| frozen registration keys incompatible | `.ufo/waves/round-44/w1/S44critic48/report.md` | Q78/Q100 | not repaired after scoring; frozen target retained red, no new calibration credit; a future freeze needs a passing honest register before mutant interpretation |
| retained clone in evidence root | `.ufo/waves/round-44/w1/S44critic45/report.md` | round scratch discipline | removed owned throwaway fixture clone, retained independent baseline/extra-row lessons and receipts |

### Routed r43 follow-through

Routed 1: derived-token binding was attempted but mechanical C1 defects block
verification; remains open. Routed 2: r44 controls are separately executed and
non-crash-checked, while the historical r43 memorizer's crash is retained, not
certified. Routed 3/4: the old wrapper/sniff/CRLF mutation limitations remain
historical and are not used as new coverage evidence; no old frozen target is
rewritten. Routed 5: joint defensive contract cutover technically implemented;
operator disposition remains open. Routed 6: preregistration precedes ready
this time. Routed 7: no previously denied provider seat was bypassed.

## Durable settlement and final measurements

The ignored `.ufo/waves/round-44/` source is captured byte-exact into
`census/round-44/waves/`; every wave pointer above resolves there by replacing
that prefix. Capture reports 405 records, no renames/exclusions/symlinks;
committed verification at `c14d20a679bf8edd6dd796c303272f7f14da4145` reports
failed=0 uncovered=0 (`census/round-44/records/capture-committed.txt`).
The initial integration commit did not include ignored wave files; durable
capture fixed that before the report. Three temporary new SCORECARD pointer
mismatches were corrected before final measurement; C1 new_mismatches=0.

Actual targets: C1 remains red, registered=0 missing=70; C2 target met; C3
technical target met with prior=5/5. Measured commits and exact commands are
in SCORECARD's Round 44 committed measurements and `records/c1-final.txt`,
`records/c2-after.txt`, `records/c3-after.txt` under `census/round-44/`.
No target changed after scoring. No whole-round admission claimed.

Six terminal errors are retained exactly in
`census/round-44/records/seat-terminal-errors.json`: critics41–44 hit MiniMax
Token Plan limits, mutationtester53 ended on Devin permission_denied after
provider-rate-limit fallback, scribe64 hit Cursor USAGE_PRICING_REQUIRED.
They supply no verification and were not replaced. Actual answering models
are in `census/round-44/records/seat-models.json`, not inferred from labels.

Source census rows 187→189, A178→180/B6/C3 unchanged, mined156→157,
queued14 unchanged/rejected17→18 (`census/round-44/records/source-counts.json`).
Both source-census commands exit 0, complete outputs in before/after receipts.
Q107 and Q108 are grounded in the reproduced parent-error and honest-register
failures above. No knowledge entry or frontier ground is promoted. Outside
spot-check remains pending, so no new outside discernment verdict is asserted.

Fleet misroot sweep found only operator run-state modification and unrelated
`rerun-daemons.log` (“command not found: ./rerun-daemons.sh”); neither names
this wave or was written by its seats. Both left untouched. Full sweep:
`census/round-44/records/fleet-misroot-sweep.txt`.
