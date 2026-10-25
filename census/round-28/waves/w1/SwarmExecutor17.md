# SwarmExecutor17 — round 28 w1: frozen SOURCES census (before receipt)

## Status
STATUS: PASS — frozen SOURCES census executed read-only at base 3a2a80d0d18940a5e352ebc526da22a57dad83c4; all counters at frozen front: rows=135, malformed=0, tier A128/B5/C2, status mined111/queued15/rejected9, duplicate ids=0, enum/tier-inflation=0, mined-usedby-missing=0, used-by path missing=0, `sources-census.sh validate` exit 0 (W04 warnings only). Output recorded at `census/round-28/records/c-frontier-before.txt` (delivery file named by the item).

## Evidence
All commands run from the lane root against `git show 3a2a80d0d18940a5e352ebc526da22a57dad83c4:corpus/SOURCES.md` bytes (working-tree `corpus/SOURCES.md` verified byte-identical to base via `cmp`; `git merge-base --is-ancestor BASE HEAD` = yes; HEAD=0c96332 contains the frozen preregistration + before receipts + do-nothing controls).

- rows: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `135` (exit 0).
- malformed (NF!=13): `awk -F'|' '/^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|/{if(NF!=13)n++} END{print n+0}' corpus/SOURCES.md` → `0`.
- tier histogram: `awk -F'|' '/^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|/{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$5); h[$5]++} END{for(k in h) printf "tier.%s %d\n",k,h[k]}' corpus/SOURCES.md | sort` → `tier.A 128`, `tier.B 5`, `tier.C 2`.
- status histogram (same shape, $9): `status.mined 111`, `status.queued 15`, `status.rejected 9`.
- duplicate ids: `grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort | uniq -d` → empty.
- enum/tier-inflation: standalone awk over kind ($4) ∈ {spec,docs,paper,code,tool,dataset,talk,book,community,own-work}, tier ($5) ∈ {A,B,C}, status ($9) ∈ {queued,mined,rejected} → empty; community-at-A count = 0.
- mined used-by missing (W03): mined rows with used-by `—` → 0; used-by path missing on disk relative to lane root (E11-style) → none.
- `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → only W04 duplicate-URL warnings (36 pre-existing, S035–S210), `souji ok …`, exit rc=0.
- Full command/output/exit-code transcript saved at `census/round-28/records/c-frontier-before.txt` (5970 bytes).

## Findings
1. Frozen front confirmed: registry rows 135 (C2 target baseline 135→138), 0 malformed, 0 duplicate ids, validate rc=0 — the C2 counter preconditions hold at base. Location: `corpus/SOURCES.md` Registry (lines 22–212), `census/round-28/records/c-frontier-before.txt`.
2. Gaps: none. No E-codes at base; only pre-existing W04 duplicate-URL warnings, which do not fail validation (exit 0).
3. No installs/upgrades performed; no pacman transaction attempted; no scratch git repo needed; scratch `/var/tmp/souji-r28-SwarmExecutor17/` removed at close. No lane writes other than the item-named delivery file `census/round-28/records/c-frontier-before.txt` and this report.

## Attack log
None (item is a read-only census; no counter/predicate/target touched).
