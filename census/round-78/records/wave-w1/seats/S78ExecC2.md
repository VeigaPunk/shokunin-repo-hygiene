# S78ExecC2 — C2 falsification (lane /home/vgpnk/Projects/shokunin/souji-shokunin)

Verdict: C2 REPRODUCED byte-exact at ITEM level; no number differs. A-record rev was L2 (87d45617) not A — explained below (ledger bytes identical).

## Reproduced numbers (all run from lane root, counter sha 9a6a34fd…)
- `python3 -B census/round-78/c2-pointer-counter.py --root <LANE> --rev 319109b0 --fleet-root /home/vgpnk/Projects/shokunin --population census/round-78/c2-population.tsv --ledger census/round-78/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r78.tsv` → `SUMMARY items=22 resolved=22 unresolved=0 refused=0 mismatched=0 errors=0`, `FORGE-SUMMARY forged=12 matched=12 accepted=0`, exit 0. ITEM lines diff-identical to records/c2-after.txt (which binds rev=87d45617 L2, not A; ledger sha256 b0e92fd7… identical at L2, A and worktree, so rev substitution is immaterial).
- base a8558d41 no-ledger → resolved=0 unresolved=22 exit 1; ITEM lines = controls/c2-K-a-no-ledger.txt.
- base + controls/variants/c2-K-b-mechanical-ledger.tsv → resolved=19 refused=3 (L10/L14/L20) exit 1; ITEM lines = controls/c2-K-b-mechanical.txt.
- r77 population (census/round-77/*, forge c2-forge-r77.tsv) at A → `SUMMARY items=35 resolved=35`, `FORGE-SUMMARY forged=7 matched=7 accepted=0`, exit 0; ITEM lines = records/c2-regress-r77.txt.
- `python3 -B tools/souji-pointer-check.py --root . --rev 319109b0 LOG.md` → `SUMMARY files=1 checked=625 missing=19 skipped=65 dead_declared=0`, exit 1. MISSING lines diff-identical to records/c2-pointer-check-after.txt.

## Controls replayed from command= lines
- K-c: `python3 -B census/round-78/c2-forge-legacy.py --root <LANE> --rev a8558d41 --fleet-root <FLEET> --work <scratch>` → `FORGE-SUMMARY forged=7 matched=0 accepted=7`, exit 1; FORGE lines match.
- K-d: population controls/variants/c2-K-d-shifted-population.tsv → `C2-COUNTER-FATAL: population sha256 7c3194b9… is not pinned`, exit 2.
- K-e: `bash census/round-78/probes/g6-collision.sh <LANE> a8558d41 <scratch>` → `G6 r77_accepts=yes r78_refuses=yes`, exit 0.

## K captures: byte identity (counter's own rev_digest/disk_digest)
- L10 .ufo/waves/round-27 frozen d:9beb0719… = rev@K(d90740fe) = disk. L14 w1-results.json f:8cd69971… = rev@K = disk. L20 .ufo/waves/round-68/w1 d:829a80e8… = rev@K = disk. At base all None (absent).
- Committed@K set vs lane disk set: disk-only 0, committed-only 0 (round-27 123 files, r53 1, round-68/w1 116; git ls-tree vs find). Captures are exact, not supersets.

## Ledger truth
- MOVED (4): L11→census/round-42/waves/w3 d:4c83385e…, L12→…/round-44/w1-results.json f:ddc9eada…, L15→…/round-54/wave/S54critic01.md f:d74bf320…, L21→…/round-69/records/wave-w1/w1-results.json f:1110b413…; each rev@A digest MATCHES the frozen population digest (pop col 5). Provenance: r44 L12 via c14d20a6 "capture ignored wave evidence"; r69 L21 via 0d8ce29a "mirror … byte-identical" — same seat/wave artefact, not a copy from elsewhere.
- ABSENT (7: L04, L05, L07, L08, L17, L19): `git log --all -- <token>` = 0 commits in lane; fleet root search found nothing for those token paths except cross-repo noise (kama-shokunin/.ufo/waves/round-16/build, other lanes' corpus/README.md) — LOW: L04's token name exists in a sibling lane, but lane's own evidence is genuinely gone; claim wording "held nowhere" is lane-scoped. L07/L08/L19 are prose tokens verified in LOG.md source text (L13 TOKEN target s272-…-quote.txt f:cce0e62b… present at A; wrap verified LOG.md:2308-2309).
- QUARANTINED L06: token absent at rev, under fleet root AND on lane disk; target is an empty dir (disk d:e3b0c442…, not committed — counter's disk-only check, per its own docstring line 26 line 237; not byte-identity of any file). FLEET rows (L01/L09/L16/L18/L22) all exist under fleet root.

## Findings
- LOW: records/c2-after.txt runs at L2 while its A-commit cites it; ledger bytes identical so numbers unaffected, but the A-record does not re-bind the tip rev.
- LOW: ABSENT L04 token string collides with kama-shokunin's round-16/build (fleet-root search noise); lane-scoped claim holds.
No HIGH/MEDIUM falsification found.

Files written: .ufo/waves/round-78/w1/S78ExecC2.md (this file). Scratch removed.
