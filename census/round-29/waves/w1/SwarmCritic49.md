# SwarmCritic49 — attack on C3 (round 29, v2 wave)

## Status

STATUS: PARTIAL — the claim is real but its instrumentation is not: a restatement pair reaches every
C3 counter with zero new ground (measured), the delivered pair's genuine increment is about one entry
rather than two, and one admit's Broder ground contradicts the round's own reject reason. A
stricter-only correction that keeps every frozen target is measured below.

## Evidence

All lane reads at base `691dd29211c53d0ef94fa072394cb9c8a69fe92e` (prereg commit
`b8cb4b31ce80e2e3314b88e85d40ea9873180804`). Scratch clone
`/var/tmp/souji-r29-SwarmCritic49.dWsXt4/c` (`git rev-parse --show-toplevel` printed the scratch root
before every commit); scratch revisions named below. Scratch removed after this report.

| # | command (root = lane unless a scratch rev is named) | output | rev |
|---|---|---|---|
| E1 | `git grep -lE '^ground: F3' <base> -- corpus/knowledge/` | 0 lines | base |
| E2 | `git show <base>:corpus/knowledge/dupe-finders-detect-then-act.md \| grep -cE '^ground:'` | `0` | base |
| E3 | `git show <base>:corpus/SOURCES.md \| grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` | `139` | base |
| E4 | `git show <base>:…/dupe-finders-detect-then-act.md` (read fully) | contains `distinct \`stat -c '%d:%i'\``, `\`cmp\` byte equality`, `second \`cmp\` at act time`, `no symlink component`; the minimum-clause bullet is line 34 | base |
| E5 | real drafts + delivered row block + README map row + slice, then `python3 -B tools/souji-gate-check.py --root <scratch> --round-date 2026-10-25 --entries …/*identity.md …/*byte-equality.md --snapshot-dir census/round-29/sources --slice … --slice-verdicts …` | `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, rc 0 | scratch `4a985f8128d04c8434bd99bf9b6a946e8ca9265e` |
| E6 | `python3 -B tools/souji-coverage-agreement.py --root <scratch> --rev <E5>` | `grounded=15 mapped=15 dangling=0 mismatches=0`, rc 0 | E5 |
| E7 | `git -C <scratch> grep -lE '^ground: F3' <E5> -- corpus/knowledge/`, row count | 2 entries, `143` rows | E5 |
| E8 | restatement pair (`junk-restate-a/b.md`, real quotes from the same snapshots, `ground: F3`, map row, used-by) then E5/E6/E7 commands | gate `entries=2 ok=2 … fail=0` rc 0; `grounded=15 mapped=15 … mismatches=0` rc 0; F3=2; rows=143; `SUMMARY k1=6 k2=4 mismatches=10` | scratch `8c372ec66bbccb3daf164e91dc9428b889e6dedf` |
| E9 | corrected pair (S217/Broder line removed from `source:` and from the Gate; S217 `used-by` = `—`) then E5–E7 plus registry counter | gate rc 0 `ok=2`; cov `15/15`; F3=2; rows=143; `SUMMARY k1=6 k2=4 mismatches=10` (k1 back to base) | scratch `7bec948114272defe8196d79cffd4e2048091309` |
| E10 | `git show <base>:corpus/knowledge/dupe-finders-detect-then-act.md \| grep -ci 'exit status' \| grep -ci 'stx_nlink'` | `0`, `0` | base |
| E11 | `sha256sum` of `.ufo/waves/round-29/w1/sources/*` vs entry front matter | all five digests equal (`cmp.1.html 5c68e8d8…`, `link.2.html 9cb197a7…`, `statx.2.html 2a47fe31…`, Broder pdf `da122799…`, txt `3ba1e117…`) | wave files |
| E12 | quote presence after `re.sub(r'\s+',' ')` over snapshots | all Gate quotes verbatim (cmp `Compare two files byte by byte.`; cmp `Exit status is 0 if inputs are the same, 1 if different, 2 if trouble.`; link `This new name may be used exactly as the old one for any operation`; statx `stx_ino; /* Inode number */`; Broder `…roughly contained.` = 23 words) | wave files |
| E13 | cited line numbers | `dupe-finders-detect-then-act.md:34` is the minimum-clause bullet; `SKILL.md:85-86` is the Superseded-snapshot drift paragraph | base |

## Findings

1. **Expansion credit is a file count, not a coverage measure — exact counterexample.** A pair of
   entries that restate only the held entry's minimum clauses, citing the same four rows and quoting
   the same snapshots honestly, reaches `F3=2`, `rows=143`, `grounded=15 mapped=15`, gate `ok=2`, and
   adds no K1 mismatch (E8). The frozen counters and the junk control cannot separate that pair from
   the delivered pair: both print the identical six numbers. Locations: preregistration C3 counter
   block; `tools/souji-gate-check.py:check_entry` (checks 1-6 test form only);
   `tools/souji-coverage-agreement.py:measure` (maps names, not propositions);
   `census/round-29/records/controls.tsv` row `C3-junk(2 sourceless-by-row F3 entries)` — that control
   fails at `check1-no-gate` alone, which a well-formed restatement pair does not.

2. **Genuine increment is about one entry, not two.** The held entry already states every inode/`cmp`
   requirement the pair re-derives (E4: distinct `%d:%i`, `cmp` byte equality not a hash, no symlink
   component, designated original, second `cmp` at act time). The byte-equality draft concedes this in
   its own words — "The lane already requires that primitive" — and its claim 3 re-quotes link(2),
   which the identity entry claims first; S218 and S217 each appear as `source:` in both entries
   (double-counted ground). The one in-scope statement absent from the base entry is `cmp`'s
   three-valued exit contract and its consequence (exit 2 recorded as "different" promotes an
   unreadable file into removal candidates): E10 shows `exit status` and `stx_nlink` are absent from
   the held entry, and E9 shows the corrected pair still carries both. Locations:
   `.ufo/waves/round-29/w1/deliver-duplicate-verdict-identity.md` claim 2 and 3;
   `deliver-duplicate-verdict-byte-equality.md` claim 2 (`The lane already requires that primitive`),
   claim 3, claim 4; `corpus/knowledge/dupe-finders-detect-then-act.md:34`.

3. **One admitted entry's ground contradicts the round's own reject reason (scope).** Line 62 of
   `deliver-duplicate-verdict-identity.md` admits the identity entry partly for its "two-axis
   vocabulary" from S217 (Broder, document similarity); line 64 of the same Gate rejects
   `near-duplicate-threshold-r28.md` for exactly that class — "document-similarity ground outside
   PROVINCE F3's byte-identical scope". `PROVINCE.md` F3 defines the row as duplicate verdicts over
   `byte-identical copies`, so identity claim 3 ("duplicate is a thresholded family of verdicts rather
   than a single predicate") and byte-equality claim 4 (Broder's 50 % resemblance and the 2.1 M / 1.5 M
   cluster split) are the rejected class, admitted at lower volume under the word "vocabulary". The
   frozen reject reason is either wrong (not amendable looser) or is being applied to the staged
   entries only.

4. **The C3 baseline is a tagging artifact, not a knowledge baseline.** E1 gives base 0 because the
   held F3 entry carries no `ground:` front matter (E2 = 0), while `corpus/README.md:41` and
   `PROVINCE.md` name that entry as F3's ground. So `0 -> 2` measures newly added tags; "F3 had no
   ground" would be false. `corpus/QUALITY.md:135` (Q56) requires grounded entries to be mapped but
   never requires an entry to declare `ground:` — with 20 entries and 13 grounded, 7 entries including
   F3's only held one are invisible to the instrument.

5. **Snapshot provenance is self-consistent, not source-anchored.** `check4` only tests that the quote
   occurs in the snapshot the entry names; there is no sha256 or URL binding anywhere in the tool, and
   the slice and its verdicts (`slice_verdicts=8/8`) are written by the same seats being scored. The
   delivered snapshots' digests do match the values stated in the entries (E11) and the quotes are
   verbatim (E12), so there is no evidence of fabrication here — but the kill rule "a snapshot this
   round's seat or the L1 opened" is trust carried by one seat, not a measurement. Locations:
   `tools/souji-gate-check.py:check_entry` (snapshot arm), `check_slice`; prereg kill rule.

6. **Bookkeeping side-effect of the correction, measured.** Dropping S217 from both entries' claims
   leaves the row present with `used-by` = `—`; the registry counter stays at the base `k1=6` and the
   row count stays `143` (E9). No C3 target is harmed by the stricter correction.

## Attack log

Claim tested: "F3-grounded entries 0 -> 2 by `grep -lE '^ground: F3'`; rows 139 -> 143;
coverage-agreement; gate-check; census" as coverage credit for the frontier step.

- **(i) Does the pair add ground the lane did not hold?** Partly. Identity claim 1's "no name is the
  original" refines a class the held entry already excludes via distinct `%d:%i`; identity claim 2 adds
  syscall-level field names and `STATX_MNT_ID_UNIQUE` (Linux 6.8) for the same inode rule; identity
  claim 3 is out of scope (finding 3); byte-equality claims 2 and 3 restate the held entry and the
  identity entry; byte-equality claim 1 (three-valued exit oracle) is genuinely new and operationally
  load-bearing. Net: one entry's worth of new in-scope proposition, one provenance/API-depth layer.
  That is a quality move for one entry and a coverage move for the other — not a two-entry coverage
  move.
- **(ii) Is Broder inside F3?** No under `PROVINCE.md` F3 and under this round's frozen reject reason:
  resemblance and containment are defined over token sets of web documents, outside `byte-identical
  copies`. The r28 precedent (staged near-duplicate paper rejected, reconsider when the duplicate-class
  decision opens) is not satisfied: this round does not open that decision — both admitted entries
  explicitly leave the class and the threshold to the operator (byte-equality "## What this does NOT
  establish").
- **(iii) Can a junk pair reach the targets?** Yes, when it is shaped correctly; E8 is the run. The
  frozen junk control only proves the sourceless shape fails. A stronger junk — restating the held
  entry, quoting real snapshots — passes gate, coverage, entry count, row count, and adds no K1
  mismatch.
- **What would make the claim a restatement** (operational definition): every proposition in an
  admitted entry is entailed by `corpus/knowledge/dupe-finders-detect-then-act.md:34`'s minimum plus
  `SKILL.md:85-86`, i.e. cmp byte equality (not a hash), a designated original never the removal
  target, distinct `%d:%i` with no symlink component, a second cmp at act time. Under that test the
  delivered pair is one new proposition (exit 2 ≠ "different") plus one citation upgrade (statx
  fields) — and the identity entry alone is a restatement plus citations.
- **Smallest safe correction** (frozen targets kept; measured at `7bec9481…`, E9):
  1. Remove S217/Broder from both entries' `source:` lines, from the `## Claim` sections, and from the
     Gate; keep a scope note with no citation. Keep S216/S218/S219 as the three grounds; leave the
     S217 row appended with `used-by` `—` (rows stay 143, k1 stays 6).
  2. State the two admits as what they are: identity = provenance/API grounding of the inode rule;
     byte-equality = the new operand (three-valued exit contract). Report "two newly tagged entries,
     held F3 entry untagged" instead of implying F3 had no ground (finding 4).
  3. **Stricter-only observable to add** (bookkeeping, calibrating C3 the way C1 calibrates records):
     each admitted entry must carry a machine-readable `increment: <one sentence>` line plus a
     `increment-token: <term>`; a check asserts the token occurs in the entry's cited snapshot and is
     absent from the held entry, e.g.
     `git show <base>:corpus/knowledge/dupe-finders-detect-then-act.md | grep -ci '<term>'` = 0 and
     `git show <rev>:corpus/knowledge/<entry>.md | grep -ci '<term>'` >= 1.
     Measured discriminators from E10/E9: `exit status` 0 -> 5 and `stx_nlink` 0 -> 2 for the corrected
     pair. Honest limit: token absence is defeated by paraphrase (my junk pair's `stx_ino` token would
     pass), so the token test is a cost floor, not a proof; with Broder removed the only remaining
     paraphrase avenue is `cmp`/inode wording, and the reviewer's read of the claim against line 34
     stays the discriminator. It makes the coverage claim falsifiable by a command instead of by
     tallying files.

Impacted axes: coverage (findings 1-4), calibration (finding 4, and the claim's own baseline
statement), operability (finding 5 — a snapshot-to-source binding is the missing instrument). The
proposed correction harms no axis: E9 shows the frozen C3 counts unchanged.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/SwarmCritic49.md` (this report)

No lane file was edited or committed; the only commits made were inside
`/var/tmp/souji-r29-SwarmCritic49.dWsXt4/c` (removed). No tools installed. No `agent://all`.
