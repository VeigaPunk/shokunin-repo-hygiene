# R92ExecC2Sweep report

## NO-FALSIFICATION

No property counterexample found for the filed tool in 200,000 seeded payloads plus targeted adversarial probes. Verdict: **NO-FALSIFICATION** (searched as described below, nothing falsified C2 wording).

## What was tested

- Filed tool: `tools/souji-record-agreement.py` (sha256 `fc0e35c2...`, matches prereg), imported via `importlib.util.spec_from_file_location` from scratch: exposed `_one_line_bytes`, `_escape_text`, `_decode_record`, `_cut_head`, `_cut_tail`. Source copy: `.ufo/waves/round-92/w1/R92ExecC2Sweep/sweep2.py`.
- r91 tool: `census/round-92/controls/c2-before-tool.py` (sha256 `21e5c740...`), same import path.
- Generator: seeded `random.Random(92092)`, lengths 201–260, token pool = printable ASCII (40×), control bytes (`\n \r \t \\ \x00 \x01 \x1f \x7f \x0b \x0c`), every Table 3-7 boundary valid seq (`C282 C2A0 C285 DFBF E0A080 E282AC ED9FBF EE8080 E280A8 F0908080 F48F8FBF F0A08080`, 30×), ill-formed/truncated/overlong/surrogate (`C0 C1 F5 FF FE 80 85 BF E080 E08080 E09FBF EDA080 EDFB80 F4908080 F0808080 E2 F0 C2 E282 E280 A085 A0 9F 90 8F B0 E280 F090 8080 6185`, 20×).
- Properties checked per payload (both tools, same payloads):
  - (a) window ≤ 202 raw bytes (`h + 3 + (len−t) ≤ 202` for len>200)
  - (b) head is a prefix and tail a suffix of `_escape_text(_decode_record(raw))` (whole rendering); exact excerpt = head + U+2026 + tail
  - (c) one physical line: no raw `\n`/`\r` in output and `output.splitlines()` has exactly one element
  - (d) cut moves only across bytes forming a single strict-decodable character: head-move slice must be the *prefix* of a well-formed sequence straddling the original cut; tail-move slice must be the *suffix* of one (the claim's "candidate bytes" semantics — the moved slice alone is never the whole character when the sequence extends past the cut).
- Targeted probes (filed tool, 256-pair exhaustive two-token placement around both cuts + line-separator injection with U+0085/U+2028/U+2029/LF/CR/VT/FF): 0 failures.
- Counts (identical N=200,000 payloads per tool, seed 92092):
  - filed: (a) 0, (b) 0, (b-text) 0, (c) 0, (d-head) 0, (d-tail) 0 — **none in 200,000**
  - before (r91 tool): (a) 0 (structural length also bounds the window), (b) 269 head/tail prefix-suffix violations, (d-head) 9,120, (d-tail) 11,954. 12 distinct `b` payloads visible in the capped 1,000-line file; full `b`=269 in the run summary (file holds first 1,000 counterexamples total).
- Counterexamples: filed none (`counterexamples-filed-v2.jsonl`, 0 bytes — saved only to prove emptiness). Before-tool first 1,000: `counterexamples-before-v2.jsonl` (1,000 lines; contains 12 `b` examples + head/tail `d` examples).
- Timing (same host, `python3 -B`, 5 reps averaged where noted):
  - `_one_line_bytes` on 1 MB payload (ASCII and mixed content): filed 0.03–0.04 ms/call — the function slices a 200-byte window first, so payload size does not affect excerpt cost; no super-linear growth observed.
  - 10,000 random payloads (201–260 bytes): filed 0.26–0.29 s total (~0.026 ms/payload); before 0.24–0.25 s. Filed is marginally slower on short payloads (strict-decode probe) but linear.

## Mechanism note (why the counts are what they are)

- Before-tool (b) failures: the tail cut moves by structural length *into* a later valid sequence (e.g. moved `90 79 f0` across bytes of an ill-formed `F4 90` run + `y` + lead `F0`), leaving the tail starting mid-sequence (`a0 80 80` of `f0 a0 80 80`); the tail then is not a suffix of the whole rendering, and raw `f0 a0 80 80` respells. One concrete payload above shows filed `t == 148` (no move, suffix holds) vs before `t == 151` (moved 3 bytes, tail `a0 80 80` mid-sequence).
- Filed tool: 0 violations on every axis across 200k payloads; the finite fixture sweep (KFF18 29,700) extends without a single counterexample.

## Artifact paths (all under `.ufo/waves/round-92/w1/R92ExecC2Sweep/` in the lane `souji-shokunin`)

- `sweep2.py` — generator + checker (seed, properties, timing)
- `counterexamples-filed-v2.jsonl` — empty (0 bytes, filed-tool counterexamples: none in 200,000)
- `counterexamples-before-v2.jsonl` — first 1,000 before-tool counterexamples (12 `b` examples incl. the diagnosed one, `d-head`/`d-tail`)

## Tool installs

None — system `python3` (3.14.8) only. No tool installs/updates per the round's tooling authorization (no pacman run; no `pacman -Sp` / `-Sy` executed). Per operator tooling authorization: no installs needed.

## Risks / blockers

- None blocking. Checked at default `limit=200` only (head=100, keep=99, t_orig=len−99) — the call sites in the tool use the default, so head/tail positions are fixed; sweep covers them but not an alternate `limit` value. To test a different limit, edit `head_n`/`keep_n` in `sweep2.py` — the claim only pins the default (fixture + r87 regression both use default), so coverage of the default is the material question.
- Scratch at `/fast/scratch/hyaku/souji-r92/R92ExecC2Sweep/` deleted before yielding (was Python-only temp copies, no fixtures/clones held; peak well under 20 GB).
