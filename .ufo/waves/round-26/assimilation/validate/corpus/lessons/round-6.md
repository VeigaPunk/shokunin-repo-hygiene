# Round 6 — gate record
Declared: C1 (docs drift→0), O1 (census tool), K1 (16G .scratch fully classified + handoff).
Outcome: **REJECTED as a round — 2/3 claims verified at closure, K1 NOT-MET.**
15/17 final judges said NOT-MET mid-round; the parent completed C1/O1
before filing; dissent preserved in census/round-6/final-*.json.

## Causes
- 32/128 seat failures (waits + provider limits) gutted the census/scratch
  shards mid-flight.
- K1 measured a live tree: seat counts diverged (535k files/17.9GiB vs
  580k/20.56GiB) — a moving target is not classifiable to 0; the honest
  claim form is a timestamped snapshot RANGE, which the parent delivered.
- One handoff draft carried claims the evidence didn't support — stripped.

## Landed anyway (banked for r7)
- tools/souji-census.sh (impl-33 winner, sha 11bf9cdf…) + two fleet census
  runs (byte-stable except live-delta rows).
- Parent tool fix: pushed receipt now requires no unpushed commits touching
  the path (git idiom --branches --not --remotes; bare --not --remotes
  returns nothing on git 2.55 — recorded as a tool-authors' pitfall).
- SKILL.md taxonomy/surfaces reconciled; AGENTS.md seat-harness clause;
  kotodama handoff (parent-signed, 40.7G live, NOT-SAFE, hands-off).
- kotodama .scratch growth curve: 553M → 1.9G → 16G → 40.4G (r1→r6).
