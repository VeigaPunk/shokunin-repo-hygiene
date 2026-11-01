# Round 48 — carry-in closures: the index-drift recurrence automated, the census conf-name form made runnable

Fresh-start reading done first (round prompt §7): the last three rejected
closures (r43, r44, r45 — MANIFEST + reports) were read and spot-checked
before anything was declared; the rulings-out are in the round report. Both
r47-closure carry-in items became claims. Two claims, two distinct axes; C1
works the lowest non-retired axis (calibration 7). Preregistration frozen at
21ec27361c1ded8d93842b2e89239e874e30f875 before any claim receipt existed;
Amendment 1 landed at 5ca5001b358eca55b70f1da63f8c0c5c3b27b945, also before
any claim receipt; tools/souji-freeze-check.py reads claims=2 findings=0,
exit 0, at the freeze, at the amendment, and at the round tip (the prereg
blob is byte-unchanged — the amendment lives beside it as
census/round-48/amendment-1.txt). Both do-nothing controls are committed in
the freeze commit (control-first). No wave was dispatched: this host has no
seat dispatch surface (standing L0 question; dispatched=0, completed=0,
dead=0; no WAVE-DONE claimed; nothing assumed answered).

## Gate

- S271 admitted: https://git-scm.com/docs/git-update-index opened live
  2026-11-01 by this session (curl HTTP 200, 84442 bytes; capture
  `census/round-48/sources/s271-git-update-index-located-quote.txt`).
  Located quote (17 words): "cacheinfo is useful when the object is in the
  database but the file isn't available locally". Context: section
  "USING --CACHEINFO", paragraph after the `git update-index --add
  --cacheinfo <mode>,<sha1>,<path>` example. Grounds only the plumbing
  operation C1's tool performs — inserting a blob that is already in the
  object database into the host index by id, without touching the object
  database, the worktree, or any commit (the same operation the r47 lesson
  performed by hand and the r47 non-author verifier confirmed honest). The
  page never mentions this host's NTFS checkout limitation, porcelain row
  collapse, or which paths are tolerated; the drift classification stays
  instrument-internal (the frozen Amendment-1 class plus the round-48
  amendment), not source-grounded.
- Census before→after: before `census/round-48/records/census-before.txt`
  (explicit-lane-directory form, rc 0, 58 W04 duplicate-url warnings, rows
  194, `shokunin-repo-hygiene ok`) beside the conf-name form's raw rc-2
  receipt `census/round-48/records/census-confname-before.txt` — carry-in
  item 1's documented host state (`souji missing`; PROVINCE host
  correction). After: the end-of-round receipt lands with the round's end
  receipts, exit 0 required (the round-48 report carries the shas).
- Amendment-1 NTFS exclusion set re-derived at the base: exactly the six
  pinned paths (`census/round-48/records/ntfs-exclusion-check-base.txt`),
  matching the campaign record `state/hyaku/ntfs-excluded/shokunin-repo-hygiene.txt`
  and the r47 receipt; tip re-check lands with the end receipts. Not widened.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| integrator landing leaves the host index outside the frozen tolerance — the r47 lesson's mistake-1 class, recurring exactly as the carry-in predicted | after 8e17a4b1a8f8bd81dd5a978e698e447bd4253b3e (the r47 spot-check commit) landed, the frozen r46 counter at the round base exits 2 could-not-evaluate ("dirty worktree at run time: 2 unexpected rows"; census/round-48/controls/c1-control-donothing.txt, taken pre-freeze), and porcelain shows 7 staged `D` + 1 untracked row against the six tolerated | the round-48 pre-flight: the L1 ran the frozen counter at the base before drafting C1 | C1's committed fail-closed tool `tools/souji-idx-repair.py` (Amendment-1-pinned bytes fd66d4f1…) executed this round: every host-index restoration went through the tool's receipted `update-index --add --cacheinfo` with per-path sha256 proofs (records/idx-repair-base.txt: BEFORE 38 rows → AFTER rows=6 unexpected=0; -content.txt and -end.txt for this round's own helper landings). No manual index repair this round; the frozen Amendment-1 set not widened |
| plain `git status --porcelain` collapses a wholly-untracked directory into one `?? dir/` row — a row whose "path" is a directory, invisible as a defect until a tool must classify it | the freeze landing put 13 new files under census/round-48/ with no index entries, so the repair tool's first real run faced `?? census/round-48/`, refused fail-closed (UNEXPECTED-NOT-IN-REV, nothing repaired; census/round-48/records/idx-repair-base-refused-plain-porcelain.txt, EXIT=1) | the first post-freeze execution of C1's tool, 2026-11-01 | round-48 Amendment 1 (census/round-48/amendment-1.txt, committed 5ca5001b before any claim receipt; prereg blob unchanged): enumeration runs `-uall` (per-file rows), the post-repair AFTER check keeps the plain form for counter parity, one selftest arm proves the collapse class (SELFTEST cases=5 pass=5 fail=0, records/idx-repair-selftest.txt); the C1 tool pin superseded 3c6803da… → fd66d4f1… in the amendment. Receipts written during execution stage to session scratch and land together, so a receipt file never pollutes the porcelain a receipt run reads |
| the plumbing helper commits DISK bytes — naming a path whose file is not yet on disk silently lands an empty commit | the first end-receipts commit 5fd125bdae678b94c24f01fd6bcac66afdc60f74 named five receipt paths that were still staged in session scratch: `git diff-tree -r 5fd125bd` is empty (the tree equals its parent's) while the command exited 0 and pushed | the post-landing verification this round runs after every landing: `git diff-tree -r --name-only <new>` printed nothing for the five named paths | receipts are copied into `census/round-48/records/` BEFORE the helper call; the five receipts re-landed on top as 6231642c94dc91bf1381cc59564ed3f4479cbc34 (diff-tree shows exactly the five files); the empty commit stays as history (never rewritten) and is disclosed here, in the LOG addendum, and in the round report. Standing rule: after every helper landing, verify the named paths with `git diff-tree -r --name-only <new>` before moving on — the same post-landing repair discipline as C1 |

Fresh-start sweep (three rejected closures): r43's defect shape was
preregistration-after-ready-handoff plus instruments that cannot bind their
tokens — ruled out by freezing at 21ec2736 with digest-pinned counters,
populations and red do-nothing controls committed in the freeze commit, and
by the amendment mechanism landing BEFORE any after-receipt (the r43 defect
was the reverse ordering). r44's shape was a frozen predicate honest work
could not meet (registered=0) — ruled out by deriving both targets from
states that already hold at the base (the counter's own Amendment-1
precondition; the census forms' documented rcs) or that an installed tool
produces directly, with red controls proving the targets are not free. r45's
shape was the different-instrument limit (0-to-green by swapping instruments;
axis-fit unprovable) — ruled out by re-using the r46 counter byte-unchanged
(digest-pinned) for C1: the green is restored by repairing the HOST to the
documented frozen precondition, not by swapping instruments; C2's axis
(operability — commands that exist and run) is the direct fit. The full
ruling table is in the round-48 report.

## Admission distinction

C1 is a capability acquisition landing a calibration verdict: the standing
landing-suite receipt is re-derived green at the base and at the tip by the
same frozen r46 instrument (byte-unchanged, digest-pinned), and the new
capability is the receipted, fail-closed host restoration that makes the
standing instrument runnable again after every landing without a manual
step. The class the r47 lesson mined by hand is now automated with red
controls. C2 is an operability move: the contract census command's conf-name
form stays rc 2 on this host (disclosed, never masked — the adapter records
the raw verdict beside the working form), and the committed adapter makes
the contract's exit-0 census derivable here. Numeric axis scores unchanged
(calibration 7, operability 8, coverage 8): both moves make existing
documented surfaces runnable; no new surface enters the province.
