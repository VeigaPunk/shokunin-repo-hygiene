# Dissent — S32, round 11 final judge

I concur with the convergent verdicts of S28 (final-28.json), S29 (final-29.json)
and S30 (final-30.json) on every point I independently re-measured, and my
final-32.json records that convergence. This dissent carries the points where I
would go further than the peer judges, plus one disclosure.

## 1. The certification bar is being argued about when it should simply be applied

Three census-fix lineages (c02 6a000c59, c03 60aef4c0, c08 7eb1b8d9) close the
r10 class and pass the full certifier rule. The round's remaining work is a
`cp` and a re-run. I dissent from any framing that treats "NOT-CERTIFIED AS
INSTALLED" as a judgment on the round's *quality*: the work is done; the state
is one install step from certified. Conversely, I dissent from any shortcut
that flips SCORECARD to certified before preconditions 1–3 of final-32.json
are executed on the installed path — including the current cert-16.json
content, whose CERTIFIED verdict was measured on 60aef4c0 bytes while
462dabd2 sits installed in the worktree. Certification evidence must come
from the certified bytes. That is not pedantry: it is the exact failure mode
(S31's incident) this round already caught once.

## 2. The blank-line semantics split should be pinned, not left to the installer

The certified lineages disagree on one edge: c02/c03/c08 require the header on
line 1 exactly (blank-lead prior → exit 2); the 462dabd2/c06/s07 lineages
accept a blank-lead prior ("first non-blank line"). Both are fail-closed on
every cert-16 case, so this is a spec choice, not a safety defect. But the
mid-round rewrite *documented* the first-non-blank contract while its own
selftest asserted the line-1 contract — the loader and the test were written
against different contracts, and that mismatch is what made its bytes
selftest-red. Whichever lineage the parent installs, the census doc must pin
the blank-line rule in the same commit, or the next concurrent seat will
re-derive a different contract and we will repeat this round.

## 3. The phantom-row variant deserves first-class status, not a footnote

S19 found it; I reproduced it fresh on the committed bytes: a blank-lead prior
against any fleet makes `load_census` parse the prior file's own header as a
data row (`repo='repo'`), fabricating a diff row for a removal that never
happened (rc=3, "repo PRESENT→ABSENT removed"). Against an empty fleet this
fabricates a removal from nothing; against a populated fleet it pollutes a
real diff. The empty-baseline hole (J14/V07) merely *hides* changes; the
phantom row *invents* one. The r10 certifier counted 3 unsafe outcomes because
its battery only probes the empty-baseline shape; a future battery should add
the blank-lead-populated case as a fourth probe so the class's two faces are
both gated. The three certified lineages already refuse it (exit 2) — this is
a battery-completeness note, not a new open defect.

## 4. cert-16.json as a shared relay is a process defect worth naming precisely

The file was overwritten at least three times during the round (S30 recorded
seven observed shas). Each overwrite was a certifier pass doing its job — but
into another seat's assigned file. The result is that the round's most-cited
evidence artifact has no stable identity: at the moment I read it, it claimed
CERTIFIED for bytes that are not installed. I restored the committed content
once myself (after my own harness run auto-wrote it — disclosed below), and it
was overwritten again. The fix is structural: certifier passes write their own
round-scoped files (as cert-09/11/12/14/15 correctly did) and the parent
integrates. I ask the parent to record this as a named process rule, not as a
one-off cleanup.

## 5. Disclosure: my own harness run touched cert-16.json

My full certifier re-run used the harness unmodified, and the harness's
built-in write path targets census/round-10/cert-16.json. My run therefore
overwrote it before the relay overwrites did. I restored the exact committed
bytes (6293283e, verified byte-identical to HEAD) immediately and before any
further work; the current file state is not mine. I flag it because the
assignment rule ("write ONLY your assigned files") was violated by a tool I
chose to run unmodified — the same class of incident I prosecute in §4, and
the reason I recommend the harness's write path be redirected (as S14's
frozen-harness copy correctly did) in any future run.

## 6. Minor: S09's selection rule picked the wrong winner, for an instructive reason

cert-09's assignment rule selected the census candidate with the most selftest
passes — impl-46 (67 checks) — and impl-46 fails the class outright (exit 0 on
empty priors AND on changed fleets). Check *count* is not check *relevance*:
impl-46's 67 checks never exercise the empty-baseline contract, while c08's 35
and c02/c03's 36 do. Selection rules for fix candidates should weight
class-closure probes over raw suite size. S09's own frontier table reached the
right alternatives (c03, impl-40); the rule, not the seat, is the lesson.

## What I do not dissent from

- The r10-merge bytes are NOT-CERTIFIED with 3 unsafe outcomes, one class,
  exactly as cert-16's committed record states — I reproduced every number.
- The three receipt tools (verify 9adb1764, vault f9e778ca, quarantine
  141c0fdc) carry no open defect this round; 121 conservative refusals, all 23
  r9 classes refusing, selftests 40/51/91 and S15 merged 88/0 green.
- Rubric scores stay UNRATED; PROVISIONAL 0/0/0 is lower-bound accounting; the
  three legacy rows stay LEGACY-UNMAPPED; no live removal is authorized by
  anything in this round.
- The fleet census audit (S23) and push-durability audit (S25) are adopted as
  written, including the fleet commit 7aea421 push pending at closure.

— S32, 2026-10-18T23:25:29-0300
