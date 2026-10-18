# kotodama-shokunin/.scratch — handoff (parent-signed, r6)

Measured 2026-10-18 ~17:59 -03:00, two-pass snapshot (46s apart) because
the tree is live:

- total: 40,641,367,144 → 40,745,413,473 bytes (~+104 MB in 46s ≈ 2.3 MB/s)
- top-level children: 388; largest: r28-x58 9.87G, x58 8.08G, x37 3.58G,
  r58 1.75G, x64 1.30G; naming pattern r<round>[-tag] / x<NN> =
  experiment/checkpoint dirs from kotodama's rounds
- owning repo: 53 unpushed commits, 0 dirty — the lane is mid-work
- seats found 60 secret-shaped basenames inside (never read; routed to kagi
  if kotodama wants them inventoried)

**Verdict: NOT-SAFE (all children).** Souji cannot touch any of it: the
owning lane has unpushed work, and each child's only honest receipts
(reproducible-output stale, or ledger rows) don't exist yet. There is no
receipt-gated subset.

**For kotodama's lane / the operator:**
1. Push the pending rounds (or decide to drop them) — this is the gate.
2. After the push, re-run `tools/souji-census.sh --root $SHOKUNIN_ROOT`;
   whatever kotodama's round files no longer reference becomes
   stale-cleanable with receipts by souji.
3. Longer term: add `.scratch/` to kotodama's `.gitignore` and generate
   these outputs outside the repo (they are untracked already, but the
   repo-adjacent location keeps putting them on souji's province).

Until then this file is the standing record: souji's position is hands-off
with receipts pending. Evidence: `census/round-6/fleet-census-{a,b}..tsv`,
seat fragments `census/round-6/seat-65..80.json` (partial — 32 seat
failures this round), draft analyses `handoff-9*.md` (claims not
parent-verified are excluded here).
