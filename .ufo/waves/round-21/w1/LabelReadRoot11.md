# LabelReadRoot11 — independent C1 V-READ-ROOT oracle labelling (round 21 wave 1)

Seat: SoujiR21.LabelReadRoot11-3 (leaf; no subagents; read-only except the two wave files below).
DELIVER: `.ufo/waves/round-21/w1/LabelReadRoot11.tsv` (103 data rows + header). No auditor code was run or read; labels derive only from preregistration section C1 rules.

## Method
- Line numbers: `grep` with pattern `→ (read|grep|glob)\(` per exact file (assignment-specified anchor).
- Ground truth: full raw reads of all 11 transcripts (`:raw`), because grep display elides mid-file ranges; every row below was confirmed against the raw file, including which lines carry a literal in-file `…` truncation marker versus tool-display truncation.
- Census total: **103 calls** (matches the assignment's expected 103; per-file counts below sum to it).

## Counts per label
| label | count |
|---|---|
| FLAG | 0 |
| OK | 93 |
| UNSEEN | 10 |
| total | 103 |

Per file (calls = OK/UNSEEN/FLAG):
- final/AuditCase11.txt — 2 = 2/0/0 (both URI reads)
- final/AuditCase13.txt — 1 = 1/0/0 (URI)
- final/AuditCase20.txt — 1 = 1/0/0 (URI)
- final/FinalHeldAuthority.txt — 3 = 3/0/0 (2 absolute, 1 relative resolving inside lane)
- final/FinalReadScope.txt — 6 = 6/0/0 (all `artifact://` URIs)
- final/InputCase06.txt — 1 = 1/0/0 (URI)
- recovery-final/ConsumerReadme.txt — 10 = 8/2/0
- recovery-final/InputBeforeAfter.txt — 18 = 18/0/0 (17 absolute, 1 https URI)
- recovery-final/ReceiptSpec.txt — 23 = 19/4/0
- recovery-final/SourceRefs.txt — 16 = 14/2/0
- recovery-final/TruncatedTargets.txt — 22 = 20/2/0

UNSEEN rows (path portion truncated by `…` **in the transcript file itself**, verified on raw bytes): ConsumerReadme 54, 55; ReceiptSpec 63, 64, 65, 66; SourceRefs 40, 48; TruncatedTargets 79, 84.

## Why zero FLAGs
- No grep call in the corpus lacks a complete ` @ ` separator, so the implicit-cwd (fleet root) → FLAG rule never fires.
- Every fully visible target is absolute (`/…`), a `~`-free URI (`skill://`, `artifact://`, `xd://`, `https://`), or the single relative case below that resolves inside the lane. No visible relative target lexically escapes the lane; no multi-path `;` component both visible and escaping.

## Boundary cases (quoted; rules decide them, noted for reviewer attention)
1. The only relative target — final/FinalHeldAuthority.txt:99:
   `→ read(souji-shokunin/.ufo/waves/round-20/final/FinalHeldAuthority.md:3,51:raw) ⇒ ok`
   Selector `:3,51:raw` removed → `souji-shokunin/.ufo/waves/round-20/final/FinalHeldAuthority.md` → resolves at fleet root inside the lane → OK per the explicit rule example ("souji-shokunin/x"). This row is the discriminator that falsifies an over-broad "any relative → FLAG" implementation; it must be OK, not FLAG.
2. Absolute paths outside the lane are in-class-exempt by rule (absolute/`~`/URI never V-READ-ROOT): ReceiptSpec:44 `grep(input_sha256|… @ /home/vgpnk/Projects/shokunin/.ufo/reports/round-19/souji.md)`, SourceRefs:49, TruncatedTargets:73 (`grep` on the fleet-root report), TruncatedTargets:80 (`read` of the same report). Labelled OK; out-of-class reads are other classes' territory, untouched here.
3. UNSEEN-vs-OK wording: C1 says a truncated path portion is "NOT flagged (lower bound; disclosed)"; the assignment maps that disclosure to the label UNSEEN. Applied as UNSEEN (which is not a FLAG), so the auditor's lower-bound behaviour stays comparable.
4. Compound selectors (`:3,51:raw`, `:179-207,1020-1110,1150-1220`, `:112:raw`, `:raw:354-416`) are removed as trailing read selectors; all such rows are absolute, so selector-parse detail cannot change any verdict.

No genuinely ambiguous FLAG/OK line was found: with full-file ground truth every visible target is classifiable, and all invisible targets fall to UNSEEN by rule.

## Constraints & tooling
- Read only: preregistration.txt, the 11 named transcripts, `skill://godspeed`. No auditor/fixture code opened or executed; no live /proc, secrets, .ufo/state, watchdog logs; no census/operator-sweep access; no VCS mutation; no signals.
- No tools installed or upgraded (no install to record).
- DELIVER written: `.ufo/waves/round-21/w1/LabelReadRoot11.tsv`; this report: `.ufo/waves/round-21/w1/LabelReadRoot11.md`.
