# C1 V-READ-ROOT oracle labels — OracleCallerCases

## Result

Observed source: /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/recovery-final/OracleCallerCases.txt

I searched the exact transcript with the requested pattern “→ (read|grep|glob)(”. I labelled every matching tool-call line under the frozen C1 rules; this is independent oracle work only and does not inspect or run auditor code.

| Label | Count |
|---|---:|
| OK | 143 |
| FLAG | 0 |
| UNSEEN | 37 |
| Total | 180 |

All visible complete targets are absolute paths (exempt from V-READ-ROOT) or the skill://godspeed URI. No relative fleet-root target or complete pathless grep was observed. The 37 UNSEEN entries have a truncated target/path in the archived call text; they are lower-bound observations, not flags.

## Ambiguity and gaps

No visible complete call has an ambiguous C1 rule application. For example, physical line 104 is recorded as “→ grep(def output_path|--output|input_sha256|checked_inputs|checked_inputs\(|write_text|with output.open|def main|if __name__|…)”: the call text ends in an ellipsis before its target is fully visible, so it is UNSEEN under the explicit truncation rule. Similar truncations are listed individually in the TSV.

No shell commands or target code were executed; a short JS generation snippet wrote the two deliverables. No auditor code was read and no tools were installed or updated.

TSV deliverable: .ufo/waves/round-21/w1/LabelReadRoot01.tsv.
