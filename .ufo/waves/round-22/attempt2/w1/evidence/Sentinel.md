# Sentinel — secret / authority review evidence (round 22, attempt 2, w1)

Seat: L1Souji22.Sentinel. Item: adversarial security/authority review, read-only.
Base lane revision: 4edb25dfe262515d0da63224bbba71e02e36cba5. Lane tip at review: 2a130b47db43eb4b3d80b2e7a5112d6b4b021899.
Inventory instant: 2026-10-25T06:48:30Z (the evidence directory was still being written by sibling
seats; every hash below is the bytes present at that instant, and the directory gained files during
the review — the census is a snapshot, not a claim about later state).

No tool installed or upgraded. No package manager run. Commands executed were reads plus the two
read-only counters (`python3 -B`, stdout only). Nothing in the lane repo was written except this file
and `.ufo/waves/round-22/attempt2/w1/Sentinel.md`. No git/jj write, no commit, no index touch, no
signalling, no cleanup, no deletion.

## 1. Scan method

Every regular file under `.ufo/waves/round-22/attempt2/w1/evidence/` was read once, byte-wise, and
matched against seven classes:

| letter | class | pattern (abridged) |
|---|---|---|
| C | credential | `op://`, `gh[pousr]_`, `github_pat_`, `AKIA`, `xox[baprs]-`, `AIza`, `sk-`, `-----BEGIN … PRIVATE KEY-----`, JWT `eyJ….….`, `Authorization: Bearer` |
| K | cookie | `Set-Cookie:`, `Cookie:` |
| T | per-request token | `report-to:`, `"nel"`, `nel: {`, `?s=<20+ opaque>` |
| P | third-party profile | `twitter_screen_name`, `github_login_name`, `profile_image_url`, `permanent_id` |
| H | private path | `/home/<user>`, `/root/`, `~/.ssh`, `~/.aws`, `/etc/shadow` |
| M | email address | RFC-ish `local@domain.tld` |
| - | none of the above | clean for this item |

Reproduce (read-only, no writes):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence
python3 -B - <<'EOF'
import os,re,hashlib
… same seven patterns …
EOF
```

### 1.1 Census (209 files at 06:48:30Z) — `<classes>|<sha256[:16]>|<bytes>|<path>`

`.` = clean; `C`/`K`/`T`/`P`/`H`/`M` as above. `M` on a vendored upstream manual page is the
document's own colophon address (public upstream contact text), not lane or operator personal data;
those rows are called out separately in 1.3 and are not counted as defects.

```
-|c2859483649f1d82|31|./.scratchpath
-|fdb37c6bc5cb3dcd|3791|./AuditAxes.tsv
-|c9be5d6dc13a5b75|2383|./AuditCap1.tsv
-|31f6a7b35812f7d0|2045|./AuditCap2.tsv
-|056ce2afadfbd211|5038|./AuditCap3.tsv
-|f3d0723a0f0de449|2687|./AuditCap4.tsv
-|d7843f01ad2dc116|1376|./AuditCap5.tsv
-|05d1154da807eb87|9479|./AuditReadme.tsv
H|99b0aefaed3d40f2|10776|./Connector.md
H|62f6fc45a66ba723|8036|./CritC1Predicate.md
H|aa0e6583969004f6|2965|./CritC2Counter/INDEX.md
-|3e7876d838c665f9|26697|./CritC2Counter/arch-gio.1.html
H|7f537993babb5239|17535|./CritC2Counter/attack-log.json
-|c958ae15d20176cd|501|./CritC2Counter/entries_outside_root/q9.md
M|353442d2ed3db0ff|40146|./CritC2Counter/freedesktop-trash.html
-|12d3c325649ca602|255|./CritC2Counter/fx/F0/census/round-22/attempt2/quarantine-slice
-|23c90d4a764a9071|120|./CritC2Counter/fx/F0/census/round-22/attempt2/slice-verdicts.tsv
-|280808ed6228397c|147|./CritC2Counter/fx/F0/census/round-22/attempt2/sources/authored.txt
-|7b1feadb1922b7b1|279|./CritC2Counter/fx/F0/corpus/SOURCES.md
-|19c2b3f876ea20ab|470|./CritC2Counter/fx/F0/corpus/knowledge/fab-r23.md
-|19c2b3f876ea20ab|470|./CritC2Counter/fx/F0/corpus/knowledge/fab-r24.md
-|198d9b3c83dca2fc|26|./CritC2Counter/fx/Q1/census/round-22/attempt2/quarantine-slice
-|ef1f666fe231b911|22|./CritC2Counter/fx/Q1/census/round-22/attempt2/slice-verdicts.tsv
-|6fc82640a9962927|123|./CritC2Counter/fx/Q1/census/round-22/attempt2/sources/man7-rename.2.txt
-|7b1feadb1922b7b1|279|./CritC2Counter/fx/Q1/corpus/SOURCES.md
-|c29dbae4cdbad9cb|430|./CritC2Counter/fx/Q1/corpus/knowledge/q1.md
-|198d9b3c83dca2fc|26|./CritC2Counter/fx/Q11/census/round-22/attempt2/quarantine-slice
-|ef1f666fe231b911|22|./CritC2Counter/fx/Q11/census/round-22/attempt2/slice-verdicts.tsv
-|6fc82640a9962927|123|./CritC2Counter/fx/Q11/census/round-22/attempt2/sources/q11.txt
-|7b1feadb1922b7b1|279|./CritC2Counter/fx/Q11/corpus/SOURCES.md
-|7e9b7b39cceb1d72|389|./CritC2Counter/fx/Q11/corpus/knowledge/q26.md
-|e7d9c339a38bb6d0|378|./CritC2Counter/fx/Q11/corpus/knowledge/qdangling.md
-|2fdf22a5e04baad6|382|./CritC2Counter/fx/Q11/corpus/knowledge/qnodate.md
-|8f21b2fe18f779b0|363|./CritC2Counter/fx/Q11/corpus/knowledge/qnoreject.md
-|198d9b3c83dca2fc|26|./CritC2Counter/fx/Q2/census/round-22/attempt2/quarantine-slice
-|ef1f666fe231b911|22|./CritC2Counter/fx/Q2/census/round-22/attempt2/slice-verdicts.tsv
M|e998beb4405f5ac9|17383|./CritC2Counter/fx/Q2/census/round-22/attempt2/sources/seam.txt
-|7b1feadb1922b7b1|279|./CritC2Counter/fx/Q2/corpus/SOURCES.md
-|a8b5d4b772eb49bb|331|./CritC2Counter/fx/Q2/corpus/knowledge/q2.md
-|198d9b3c83dca2fc|26|./CritC2Counter/fx/Q2c/census/round-22/attempt2/quarantine-slice
-|ef1f666fe231b911|22|./CritC2Counter/fx/Q2c/census/round-22/attempt2/slice-verdicts.tsv
-|4a604f6e834bd0b9|96|./CritC2Counter/fx/Q2c/census/round-22/attempt2/sources/excerpt.txt
-|7b1feadb1922b7b1|279|./CritC2Counter/fx/Q2c/corpus/SOURCES.md
-|32b412e327825c72|385|./CritC2Counter/fx/Q2c/corpus/knowledge/q2c.md
-|89acb86b2d7e4cfe|386|./CritC2Counter/fx/Q2c/corpus/knowledge/q2c_punct.md
-|198d9b3c83dca2fc|26|./CritC2Counter/fx/Q3/census/round-22/attempt2/quarantine-slice
-|ef1f666fe231b911|22|./CritC2Counter/fx/Q3/census/round-22/attempt2/slice-verdicts.tsv
-|9ecffc884929f4de|37|./CritC2Counter/fx/Q3/census/round-22/attempt2/sources/q3.txt
-|7b1feadb1922b7b1|279|./CritC2Counter/fx/Q3/corpus/SOURCES.md
-|9551a74f77256566|276|./CritC2Counter/fx/Q3/corpus/knowledge/q3.md
-|198d9b3c83dca2fc|26|./CritC2Counter/fx/Q4/census/round-22/attempt2/quarantine-slice
-|ef1f666fe231b911|22|./CritC2Counter/fx/Q4/census/round-22/attempt2/slice-verdicts.tsv
-|6fc82640a9962927|123|./CritC2Counter/fx/Q4/census/round-22/attempt2/sources/q4.txt
-|7b1feadb1922b7b1|279|./CritC2Counter/fx/Q4/corpus/SOURCES.md
-|d3de50f6e7c14dfb|402|./CritC2Counter/fx/Q4/corpus/knowledge/q4.md
-|198d9b3c83dca2fc|26|./CritC2Counter/fx/Q5/census/round-22/attempt2/quarantine-slice
-|ef1f666fe231b911|22|./CritC2Counter/fx/Q5/census/round-22/attempt2/slice-verdicts.tsv
-|9066ba2b4a5b51e0|142|./CritC2Counter/fx/Q5/census/round-22/attempt2/sources/alias.txt
-|7b1feadb1922b7b1|279|./CritC2Counter/fx/Q5/corpus/SOURCES.md
-|218738ca562d7514|408|./CritC2Counter/fx/Q5/corpus/knowledge/q5.md
-|12d3c325649ca602|255|./CritC2Counter/fx/Q6/census/round-22/attempt2/quarantine-slice
-|125d37e33efafab0|13|./CritC2Counter/fx/Q6/census/round-22/attempt2/slice-verdicts.tsv
-|6fc82640a9962927|123|./CritC2Counter/fx/Q6/census/round-22/attempt2/sources/q6.txt
-|7b1feadb1922b7b1|279|./CritC2Counter/fx/Q6/corpus/SOURCES.md
-|d00a8289ec6221d6|381|./CritC2Counter/fx/Q6/corpus/knowledge/q6.md
-|198d9b3c83dca2fc|26|./CritC2Counter/fx/Q7/census/round-22/attempt2/quarantine-slice
-|ef1f666fe231b911|22|./CritC2Counter/fx/Q7/census/round-22/attempt2/slice-verdicts.tsv
-|6fc82640a9962927|123|./CritC2Counter/fx/Q7/census/round-22/attempt2/sources/q7.txt
-|7b1feadb1922b7b1|279|./CritC2Counter/fx/Q7/corpus/SOURCES.md
-|8874a95674f07aaa|447|./CritC2Counter/fx/Q7/corpus/knowledge/q7.md
-|198d9b3c83dca2fc|26|./CritC2Counter/fx/Q8/census/round-22/attempt2/quarantine-slice
-|ef1f666fe231b911|22|./CritC2Counter/fx/Q8/census/round-22/attempt2/slice-verdicts.tsv
-|6fc82640a9962927|123|./CritC2Counter/fx/Q8/census/round-22/attempt2/sources/q8.txt
-|7b1feadb1922b7b1|279|./CritC2Counter/fx/Q8/corpus/SOURCES.md
-|15e048674d63cf61|425|./CritC2Counter/fx/Q8/corpus/knowledge/q8.md
-|a5af1920b16444e0|19401|./CritC2Counter/gtk-filetrash.html
-|9066ba2b4a5b51e0|142|./CritC2Counter/injected-uncommitted.txt
M|d20b49ad254a0c79|11693|./CritC2Counter/man7-mv.1.html
M|8772946a809a0db5|23571|./CritC2Counter/man7-rename.2.html
M|2a47fe319c5894d7|33125|./CritC2Counter/man7-statx.2.html
-|12d3c325649ca602|255|./CritC2Counter/real-slice-copy.txt
H|4c8ef35123a1e715|9500|./CritC2Coverage.md
H|6673f8e74dfe315c|17409|./DraftEntryNoCopy.md
H|f64fb1ec89fb1e12|7395|./DraftEntryOrigin.md
H|3a40f74b6a145bba|11184|./DraftGateLesson.md
H|73a133db26b973d7|11847|./DraftGates.md
H|513cef0bffa5cb28|28817|./DraftSourcesRows.txt
M|58ddbfef46e08f40|14845|./MutDigest-mutant.py
M|58ddbfef46e08f40|14845|./MutDigest-pristine.py
-|00e82f27e517cdad|8221|./MutDigest.md
-|7b329fc0d354c1cd|11321|./MutDigest.raw
-|406299df8827c655|714|./MutPath-work/baseline-selftest.txt
M|58ddbfef46e08f40|14845|./MutPath-work/baseline.py
-|1c1e2b2734be66c5|675|./MutPath-work/direct-counter-probe.txt
-|5d0d988ab999f5b3|714|./MutPath-work/m1-selftest.txt
-|d66d0aaa0b1399d2|561|./MutPath-work/m1.diff
-|4d04a2b1af8f8cd6|714|./MutPath-work/m2-selftest.txt
-|77dc9d95832ff359|442|./MutPath-work/m2.diff
-|abbb42c49d2d2183|9291|./MutPath.md
-|6fd2e7672ba97a43|8614|./MutQuote.md
H|a9155773a1fdc23d|17986|./RevGate.md
H|716a3cc1922eab65|87684|./RevRows.candidate-SOURCES.md
-|cb87b428bf99e44f|3241|./RevRows.tsv
-|31855dc3f8203d67|10896|./RevRows.validate-candidate.out
-|de808aa899532397|7473|./RevScope.tsv
-|da4952a9709f33a1|2712|./RevSliceVerif.tsv
H|cab116e6b2ec1c39|25663|./ScoutCensusMirror.txt
H|a1e5087b8d2ed507|10172|./ScoutCollision.txt
-|93cef11bb18c1f46|1922|./ScoutIdResolve.tsv
-|0fca0701cacbacc5|904|./control/always-zero.py
M|8ae996d76679583d|16106|./control/fixture-gate.py
H|88ca3502de71e97f|4418|./control/transcript-always-zero.txt
-|e5f39d54cf36a9d1|5548|./control/transcript-fixture-audit.txt
H|58aafedc8a51197e|3047|./control/transcript-impl.txt
-|c2bdb513aaeff3fd|52|./gatefix/census/slice
-|e3b0c44298fc1c14|0|./gatefix/census/slice-empty
-|7b0473eaf29399f4|55|./gatefix/census/sources/link-out.txt
-|53133b0bb1adc63b|47|./gatefix/census/sources/section-line.txt
-|b82d4a2612109a65|126|./gatefix/census/sources/w25.txt
-|ba96538192930672|105|./gatefix/census/sources/w26.txt
-|a94f79583c9061fd|105|./gatefix/census/sources/x.txt
-|c38e55a6d1c5f6eb|24|./gatefix/census/sources/x2.txt
-|4f623ac60961d0b7|61|./gatefix/census/verdicts-badclass.tsv
-|0e6184b31262d4f7|80|./gatefix/census/verdicts-comment.tsv
-|859799eac3d1a009|49|./gatefix/census/verdicts-dupe.tsv
-|efd0a99562975888|74|./gatefix/census/verdicts-extra.tsv
-|64f63ba638386104|77|./gatefix/census/verdicts-good.tsv
-|1310d4b3296e53d3|41|./gatefix/census/verdicts-idinside.tsv
-|23c52a14dc26f920|34|./gatefix/census/verdicts-noev.tsv
-|ef1f666fe231b911|22|./gatefix/census/verdicts-partial.tsv
-|68502e4c2962b989|27|./gatefix/census/verdicts-shortrow.tsv
-|53629773e5c3fd57|111|./gatefix/corpus/SOURCES.md
-|7b0473eaf29399f4|55|./gatefix/elsewhere/y.txt
-|dc5470af8672c6f3|279|./gatefix/entries/admit-noreason.md
-|bb9228c0435317b8|292|./gatefix/entries/baddate.md
-|49fb1f8410330feb|429|./gatefix/entries/citedindent.md
-|96b2822805444be2|433|./gatefix/entries/citedlist.md
-|4091e5896c26267c|374|./gatefix/entries/dangling.md
-|9b5eff7861ec3dce|217|./gatefix/entries/gatefirst.md
-|ac8f127b58eca5e0|370|./gatefix/entries/good.md
-|d67b631e7efc2d63|273|./gatefix/entries/locfromfile.md
-|e15bc50cf2fbb289|349|./gatefix/entries/longquote.md
-|64fe7fb45acd4d51|180|./gatefix/entries/noadmit.md
-|56e512f3e8b69ea5|247|./gatefix/entries/nocite.md
-|3f6fcdb81b702a97|96|./gatefix/entries/nogate.md
-|3e08bfe1ccb20651|277|./gatefix/entries/nolocator.md
-|3dfa5d30a1fbef04|239|./gatefix/entries/noreject.md
-|3803271697486d41|282|./gatefix/entries/nosnap.md
-|e7073a272be398ba|285|./gatefix/entries/nourl.md
-|0431578bee647db8|288|./gatefix/entries/perturb.md
-|e86d8169c48c15f4|341|./gatefix/entries/quote25.md
-|cb7e29c8458da3d5|345|./gatefix/entries/quote26.md
-|c84e6d940da15579|295|./gatefix/entries/quoteabsent.md
-|b13c79951a05a1b6|265|./gatefix/entries/reject-emdash.md
-|0abae1687a2ee41f|294|./gatefix/entries/reject-noreason.md
-|85b02f7da196c885|292|./gatefix/entries/snapmissing.md
-|3e2fd6a1b8a16077|282|./gatefix/entries/snapoutside.md
H|f13fb769c418d7e4|3490|./gatefix/entries/staged-copy.md
-|45fb986fdf77e498|288|./gatefix/entries/symlinkesc.md
M|61916d7fb6bd8c9c|19781|./impl-a/souji-declared-evidence.py
-|3be660e1c58dff25|5347|./impl-b/base-assertions.tsv
-|e150beab43988206|64|./impl-b/base-counts.txt
-|f6b64231f3517f23|2123|./impl-b/base-skips.tsv
-|a99a1ad39c5bc414|911|./impl-b/selftest.txt
M|a833daba761bf94a|23299|./impl-b/souji-declared-evidence.py
-|c530f78250f6299d|526|./impl-gate/counts-latest.txt
-|e3b0c44298fc1c14|0|./impl-gate/counts.stderr
-|3af6c4f4f27fac54|77|./impl-gate/counts.txt
-|f62c41dca22dca5f|457|./impl-gate/inputs.sha256
-|d3a20736cd30ab74|1049|./impl-gate/selftest.log
H|66c7af71840470e9|21688|./impl-gate/souji-gate-check.py
-|bc186507f9b160e4|18456|./impl-rows/row-check.py
-|55fb48aa723a60ca|278|./impl-rows/rows-fixture.expect.tsv
-|a6bc936d8ed909dc|4414|./impl-rows/rows-fixture.md
H|ae016294ee3d6329|8884|./impl-rows/transcript.txt
-|a5af1920b16444e0|19401|./rev-docs.gtk.org_gio_method.File.trash.html.html
-|e3b0c44298fc1c14|0|./rev-doi-S118.body
T|40b24280df1e2889|1749|./rev-doi-S118.headers
M|5d3dcd3b6588ce51|27870|./rev-git-scm.com_docs_git-prune.html
M|fa25690b04900cfc|98918|./rev-git-worktree.html
M|8772946a809a0db5|23571|./rev-man7-rename.2.html
P|bf7ddd62859a309b|16825|./rev-qiita-item.json
-|ecefaf6c7249630a|129655|./rev-qiita.com_koseki_items_f1af58f1ec1693f0536a.html
H|c6505d6d9f1dccd7|3214|./slice114-git-prune.txt
M|5d3dcd3b6588ce51|27870|./slice114-git-scm-git-prune.html
-|a500d30a286148cf|691|./slice114-http-headers.txt
-|6cd032eddb4c6b6c|1980|./slice114-man-git-prune.colb.txt
-|b6b361cca397b4cb|736|./slice118-doi.txt
H|537e35b32b1653f3|6620|./slice123-trigger-prune.out
H|1634d206ef534f68|530|./slice124-noreplace-probe.out
M|8772946a809a0db5|23571|./slice124-rename2.html
-|a5af1920b16444e0|19401|./slice126-filetrash.html.txt
H|494a80ec71ccd584|5719|./slice131-worktree-census.out
HM|5e4a81c7f259b711|16839|./slice133-renameat2-probe.out
-|10773183118b0698|129655|./slice138-qiita.html
-|65ca1eddf555c57c|3943|./slice138-qiita.txt
-|a5af1920b16444e0|19401|./snap-filetrash.raw
-|23fb07ce8ca4946f|4140|./snap-filetrash.txt
-|3e7876d838c665f9|26697|./snap-gio1.raw
-|cc4af34906f69137|12125|./snap-gio1.txt
M|d20b49ad254a0c79|11693|./snap-mv1.raw
M|18dc9c2185fbf2b8|4610|./snap-mv1.txt
M|8772946a809a0db5|23571|./snap-rename2.raw
M|88cba52e7f5ee819|15799|./snap-rename2.txt
M|2a47fe319c5894d7|33125|./snap-statx2.raw
M|ca14c31f6608b6e9|19724|./snap-statx2.txt
M|353442d2ed3db0ff|40146|./snap-trashspec.raw
M|aa21fdcbc8f7226e|24788|./snap-trashspec.txt
-|58456a40132aecd2|1358|./snapshot-manifest.tsv
```

No `C`, `K` class hit exists anywhere in the tree at that instant: no `op://` reference, no
provider token, no private key, no JWT, no `Authorization: Bearer`, no cookie header.

### 1.2 Findings with exact locations

| # | file:line | class | offending content (sensitive value redacted) | severity |
|---|---|---|---|---|
| S1 | `./rev-doi-S118.headers:13` | T — per-request opaque token | `report-to: {"group":"cf-nel",…"url":"https://a.nel.cloudflare.com/report/v4?s=<REDACTED-32B-OPAQUE>"}` — a Cloudflare NEL report correlation token bound to this fetch | low |
| S2 | `./rev-qiita-item.json:1` (single line) | P — third-party personal data | a fetched Qiita item whose `user` object carries `name`, `id`, `github_login_name`, `twitter_screen_name`, `location`, `website_url`, `profile_image_url`, `permanent_id` (values not reproduced) | low |
| S3 | `./slice124-noreplace-probe.out:2-3` | H — private path | `/home/<user>/Projects/shokunin`, `/home/<user>/Projects/shokuknow` in the probe's device column (file predates the round: mtime 2026-10-23 18:27; sha256 `1634d206…8bb5` = the vendored S109 bytes) | low |
| S4 | `./slice133-renameat2-probe.out:2` | H — private path | `# register : /home/<user>/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md` | low |
| S5 | `./slice123-trigger-prune.out:3,13,21,88` | H — private path | register path and cited-payload paths under `/home/<user>/Projects/shokuknow/…` | low |
| S6 | `./slice131-worktree-census.out:10` | H — private path | `/home/<user>/Projects/shokuknow/lanes/souji/…` | low |
| S7 | `./ScoutCensusMirror.txt:3,7,11,44,48-52,72,83,127,169,211,214,277,302,313` | H — private path | mirrored-census transcript; `cp -r` lines show reads of the lane corpus into `/var/tmp/souji-r22-mirror/corpus/` (scratch, no lane or foreign-repo write) | low |
| S8 | `./ScoutCollision.txt:8-9`, `./Connector.md:12,61,91,96,120`, `./DraftSourcesRows.txt:13,15,193-194,288,406`, `./DraftEntryNoCopy.md:5`, `./DraftEntryOrigin.md:8`, `./DraftGateLesson.md:73`, `./DraftGates.md:115`, `./RevGate.md:10`, `./RevRows.candidate-SOURCES.md:129`, `./CritC2Coverage.md:50`, `./CritC1Predicate.md:*`, `./CritC2Counter/INDEX.md:*`, `./CritC2Counter/attack-log.json:10`, `./control/transcript-*.txt`, `./impl-rows/transcript.txt:3`, `./gatefix/entries/staged-copy.md:19` | H — private path | seat reports/logs that quote absolute host paths (lane root, fleet root, shokuknow package root) | low |
| S9 | `./impl-gate/souji-gate-check.py:56-59` | H — private path, in tool source | `STAGED_ENTRY = "/home/<user>/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r23.md"` | low |

`M` rows: the six `snap-*.raw`/`snap-*.txt` pairs and their `CritC2Counter`/`rev-*`/`slice114`/`slice124`
copies carry upstream colophon addresses (`man-pages@man7.org`, `bug-coreutils@gnu.org`, and the four
freedesktop Trash-spec author addresses at `snap-trashspec.raw:58-61` / `snap-trashspec.txt:17-20,394`).
Those are the vendored documents' own text; stripping them would falsify a byte-exact snapshot whose
sha256 the round publishes. Classified `clean:upstream-document-text`, not a defect.

Two zero-byte artifacts are not secrets but are provenance-bearing: `./rev-doi-S118.body` (0 bytes) and
`./gatefix/census/slice-empty` (0 bytes). `./slice118-doi.txt` is not fetched bytes — it is a
self-authored receipt appended into the snapshot path after a 0-byte fetch. It lives outside
`census/round-22/attempt2/sources/`, so the counter's containment rule can never match a quote
against it; note for anyone tempted to name it as a `snapshot:`.

### 1.3 Corpus-bound artifacts outside the evidence dir (same classes)

Committed at `a211e4d`:

| file:line | class | content |
|---|---|---|
| `census/round-22/attempt2/sources/vendor-noreplace-probe.out:2-3` | H | `/home/<user>/Projects/shokunin`, `/home/<user>/Projects/shokuknow` — byte-exact vendored probe (S109 cites its sha256 `1634d206…8bb5`) |
| `corpus/knowledge/quarantine-staging-no-copy-r23.md:32-33` | H | same two host paths in prose (not inside any Gate quote) |
| `corpus/SOURCES.md:129` | H | the new S109 row's prose repeats the three host mount paths |
| `corpus/README.md:425` | H | `/home/<user>/Projects/shokuknow/merge/souji/` package path |

Pre-existing convention, not introduced by the concept: `git grep -c '/home/vgpnk' -- corpus census/round-22`
already matches `LOG.md` (7), `SCORECARD.md`, `corpus/lessons/round-12..22`, and four older knowledge
files. The round adds the four lines above plus `.ufo/.../w1-dispatch.json` (250 host paths in the
committed seat prompts), i.e. no new class — only new instances.

## 2. Candidate tools — authority matrix (source-read, plus the two marked executions)

Primary candidates (the two named by the preregistration counters):

| property | `tools/souji-declared-evidence.py` (sha `58ddbfef…`) | `tools/souji-gate-check.py` (sha `d85c2696…`) |
|---|---|---|
| `eval`/`exec`/`compile`/`__import__` | absent | absent |
| `shell=True`, `os.system`, `os.popen` | absent | absent |
| network (`socket`/`urllib`/`requests`/`http.client`) | absent (imports: argparse, fnmatch, hashlib, io, os, re, subprocess, sys, tempfile) | absent (imports: argparse, io, os, re, subprocess, sys, tempfile) |
| `chmod` / ownership change | absent | absent |
| subprocess, counter mode | `git -C <root> -c maintenance.auto=false` + `rev-parse`/`cat-file`/`ls-tree`/`show` — fixed argv, no shell, no user text on a command line except hex rev and a `rev:path` object spec | none |
| subprocess, selftest only | `git init/add/commit/rev-parse` in `tempfile.mkdtemp(dir="/var/tmp")`; `[sys.executable, control]`; `["rm","-rf",base]` | `["rm","-rf",base]` |
| writes, counter mode | stdout only | stdout/stderr only |
| writes, selftest | its own `/var/tmp/souji-declared-evidence-*` tree | its own `/var/tmp/souji-gate-check-*` tree |
| untrusted-input → filesystem | SCORECARD tokens reach only `git show <rev>:<path>`; git refuses paths outside the tree (`git show rev:../x` errors) → no filesystem read | entry Gate `snapshot:` paths are `normpath`-checked against `--snapshot-dir` but **not** `realpath`-checked → symlink inside the dir escapes (E1) |

Executed proofs (both read-only, `-B`, stdout only, lane tree unchanged afterwards):

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
rc=0

$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev HEAD --format counts
assertions=58 resolved=58 skipped=36 mismatches=0
rc=0
```

E1 — symlink containment bypass in the committed C2 counter (proved, not inferred):

```
$ ls -l .ufo/.../evidence/gatefix/census/sources/link-out.txt
lrwxrwxrwx … link-out.txt -> /home/<user>/…/w1/evidence/gatefix/elsewhere/y.txt
$ python3 -B tools/souji-gate-check.py \
    --root .ufo/waves/round-22/attempt2/w1/evidence/gatefix --round-date 2026-10-25 \
    --entries entries/symlinkesc.md --snapshot-dir census/sources \
    --slice census/slice --slice-verdicts census/verdicts-good.tsv
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0      # rc=0
```

The entry's `snapshot: census/sources/link-out.txt` resolves to bytes physically outside the snapshot
directory, yet check 4 passes: the frozen predicate's "that snapshot lives under --snapshot-dir" is
satisfied only syntactically. `tools/souji-gate-check.py:96-99`:

```
            spar = snap.group(1)
            spath = spar if os.path.isabs(spar) else os.path.normpath(os.path.join(root, spar))
            if not spath.startswith(snap_root + os.sep) and spath != snap_root:
```

The in-flight staging copy already repairs it — `impl-gate/souji-gate-check.py:94` defines
`return os.path.realpath(rel if os.path.isabs(rel) else os.path.join(root, rel))` — and
`gatefix/entries/symlinkesc.md` is its negative fixture. Minimal fix to the committed tool: resolve
`os.path.realpath()` for both `spath` and `snap_root` before the containment test.

E2 — kill-rule fixture 6 as frozen versus as shipped:

* frozen: "a byte-exact copy of the staged package entry (no Gate) -> fail";
* `tools/souji-gate-check.py` selftest cases: `good`, `no-date`, `long-quote`, `quote-absent`,
  `dangling-source`, `no-reject`, `no-gate` — `no-gate` is a 3-line synthetic file, and the tool never
  reads the staged package, so the byte-exact condition cannot hold for it;
* `impl-gate/souji-gate-check.py:425-455` does implement it (copy staged bytes, assert
  `staged_sha == copy_sha`, require `failed == {"check1"}`) and its receipt records
  `PASS fixture-6-staged-entry-copy … sha256=f13fb769c418d7e4 byte-exact=True got-fail=check1`
  (`impl-gate/selftest.log`), which matches `gatefix/entries/staged-copy.md`
  (sha256 `f13fb769c418d7e4…`).

E3 — receipt binding: `impl-gate/inputs.sha256` still lists the pre-edit r24 digest
`8a21704de532233b…`, while the committed entry is `f47efc7b80003767…`; `impl-gate/counts-latest.txt`
carries the corrected `f47efc7b…`. The two receipts in one directory disagree; the earlier one is
stale, not wrong-at-the-time. `impl-gate/counts.txt` (`entries=2 ok=2 slice_verdicts=8 slice_total=8
fail=0`, `counter_rc=0`) was produced by the staging binary sha `66c7af71…`, not by the committed
`d85c2696…` — the committed counter reproduces the same counts (executed above), so nothing false
survives, but the receipt does not bind the named binary.

Additional authority deltas in the in-flight copies (not committed; relevant only if promoted):

* `impl-gate/souji-gate-check.py`: writes fixture files (`:367`, `:441`) and `shutil.rmtree(base,
  ignore_errors=True)` (`:486`); reads another repository by absolute path (`:56-59`); fails closed
  when that path is absent (`staged-entry-missing=…`, `control=FALSE-GREEN-UNMEASURED`).
* `impl-a/souji-declared-evidence.py:82`: `git --no-optional-locks -c maintenance.auto=false -C root`
  with `stdout=PIPE, stderr=DEVNULL` (no `env=`); `shutil.rmtree` at `:412`.
* `impl-b/souji-declared-evidence.py`: scrubbed `env=git_env()` (`:94`) — best of the three — plus
  `os.remove(os.path.join(repo, "docs/old-only.md"))` at `:414`, strictly inside its own scratch repo.

`control/fixture-gate.py` (the C1 control harness) executes a caller-supplied `candidate` path
(`:294-299`), writes only under `tempfile.mkdtemp(prefix="c1-fixtures-")`, and pins the child
environment (`HOME`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`,
`GIT_TERMINAL_PROMPT=0`, fixed author/committer). No shell, no network, no lane write. Its authority
is exactly "run one named program with a pinned env in a throwaway repo" — the correct shape for a
control, and the shape the two committed counters should copy for their own selftests.

## 3. Deletion authority

`git diff --stat 4edb25d..2a130b4` adds no `.sh`, no quarantine tool, no `mv`/`chmod`/`unlink` helper:
the only new executables are the two `.py` counters. Round-added paths: preregistration, dispatch/spec/
registry JSON, `LOG.md`, `SCORECARD.md`, `declared-evidence-before.tsv`, `quarantine-slice`,
`slice-verdicts.tsv`, 15 `census/round-22/attempt2/sources/*` files, `corpus/SOURCES.md` rows, the two
knowledge entries, `corpus/lessons/round-22.md`, `corpus/README.md`, and the two tools.

Removal primitives introduced by the round (complete list):

| where | form | scope |
|---|---|---|
| `tools/souji-declared-evidence.py:287` | `subprocess.run(["rm","-rf",base], check=False)` | `base = tempfile.mkdtemp(prefix="souji-declared-evidence-", dir="/var/tmp")`, `--selftest` only |
| `tools/souji-gate-check.py:275` | `subprocess.run(["rm","-rf",base], check=False)` | `base = tempfile.mkdtemp(prefix="souji-gate-check-", dir="/var/tmp")`, `--selftest` only |

Both arguments are generated, never supplied: no flag, no stdin, no fetched content reaches `base`.
No `os.remove`, `os.unlink`, `os.rename`, `os.replace`, or `chmod` exists in either committed tool.

Quarantine-before-delete state (unchanged by this round — `tools/souji-quarantine.sh` is not in the
diff):

* `tools/souji-quarantine.sh:181` `DRYRUN=0`; `:680-694` mutation is refused with exit 4 when `<repo>`
  lies inside the live fleet root unless `SOUJI_QUARANTINE_ALLOW_LIVE=1`, and `--dry-run` "is always
  allowed anywhere (it changes nothing)";
* the round's own text states the policy rather than changing the tool:
  `corpus/knowledge/quarantine-staging-no-copy-r23.md` — "the audit's own rule is *dry-run by default,
  quarantine before delete*" and "No staging tool is changed by this entry. It removes a blocker; it
  grants no new deletion or move authority";
* `corpus/README.md:408` — "No new knowledge path, frontier promotion, deletion authority or F5 scope
  expansion follows"; `:430-438` — "the operator still owns the record format and any staging tool
  change";
* no seat prompt in `w1-dispatch.json`/`w1-spec.json` contains `rm -rf`, `git add|commit|push|reset|
  clean|prune`, `chmod`, `sudo`, a quarantine `--apply`, or `SOUJI_QUARANTINE_ALLOW_LIVE`
  (grep returns only the words `gio trash` and `chmod,` inside prose).

Consequence: the round creates no new deletion authority; the only new removal power is the two
temp-scoped `rm -rf` selftest calls above. The pre-existing default of the quarantine tool is
mutation-capable-but-live-fleet-guarded, not dry-run; that is unchanged state, not a round regression.

## 4. Environment residue observed (not produced by this seat)

* `tools/__pycache__/souji-declared-evidence.cpython-314.pyc` (26345 B) and
  `tools/__pycache__/souji-gate-check.cpython-314.pyc` (22284 B), mtime 03:47 — a sibling ran a counter
  without `-B`. Untracked residue in the lane; also noted by `./MutQuote.md` "Observed, not produced by
  this seat". Every command this seat ran used `python3 -B`.
* `git status --porcelain` at 06:49Z reported ` D census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc`
  — a tracked file currently deleted in the worktree, plus modifications under `tests/vault/…`. None of
  these paths is touched by the counters above; provenance is a sibling seat, not this review.

## 5. Addendum — the lane advanced during the review (lane tip `af73b8b`)

Three commits landed while this review ran: `5ff5041` (locators, slice verdicts, stale digest,
lesson M17–M21), `d6a75ba` (connector/registry/README), `af73b8b` (gate-check hardening, entry
reasons, row wording). Everything in §2 about `tools/souji-gate-check.py` sha `d85c2696…` is
superseded; the sections above are kept because they document the state that was actually measured
and executed at the time.

Second census instant: `2026-10-25T06:54:07Z`, 224 files = the 209 above + the 15 below + this file.
The fifteen added files were scanned with the same seven classes; none carries C/K/T/P:

```
61366ac18635cc4d   11078  ./AuditSkillShonen.tsv
9ffe78f5103f425e     796  ./CritC2Counter/attack-log-worktree.json
e3b0c44298fc1c14       0  ./CritC2Counter/fx/Q6/census/round-22/attempt2/slice-empty
e9c7dd7e773f76f3     105  ./CritC2Counter/fx/Q6/census/round-22/attempt2/slice-verdicts-7of8.tsv
2d23c6517fedccb1     146  ./CritC2Counter/fx/Q6/census/round-22/attempt2/slice-verdicts-extra-row.tsv
53225fc01f1fab64   15760  ./DraftMistakes.md                  (H)
88a3d0345eed1ade    9221  ./DraftScorecard.md
8c3b2ec912eb8a4e   11052  ./RevImplA.md                       (H)
616e9f59ab45e878      57  ./impl-a/base-4edb25d.counts
8838663f28dd28b0    8600  ./impl-a/base-4edb25d.tsv
7abf02f84c0569cf    4306  ./impl-a/base-skipped.txt
d3363b18de352c0e     556  ./impl-a/selftest.txt
d11de402d850e81a      57  ./impl-a/tip-70af563.counts
51c7a99b97e9c39d    8726  ./impl-a/tip-70af563.tsv             (H)
```

`./Sentinel.md` (this file) self-matches C/K/T/P because its §1 table names the patterns
(`op://`, `Set-Cookie:`, `twitter_screen_name`, …). Exclude it from any later re-scan.

### 5.1 Tool state at `af73b8b`

| property | `tools/souji-declared-evidence.py` | `tools/souji-gate-check.py` |
|---|---|---|
| sha256 | `58ddbfef46e08f40…` (unchanged) | `5b8025a83f16957c…` (was `d85c269624f4ade5…`) |
| containment | n/a (git object specs only) | `spath`/`snap_root` both `os.path.realpath()`-resolved at `:101-103` |
| selftest writes | `rm -rf` at `:287` | `shutil.copyfile` at `:252`, `assert` at `:255`, `rm -rf` at `:286` |
| execution sinks | git plumbing; `[sys.executable, control]` | none |
| network / chmod / eval / shell | none | none |

E1 re-executed against the hardened tool — the symlink fixture is now rejected:

```
$ python3 -B tools/souji-gate-check.py --root .ufo/waves/round-22/attempt2/w1/evidence/gatefix \
    --round-date 2026-10-25 --entries entries/symlinkesc.md --snapshot-dir census/sources \
    --slice census/slice --slice-verdicts census/verdicts-good.tsv
FAIL entries/symlinkesc.md check4-snapshot-outside-dir-line-6
FAIL entries/symlinkesc.md check3-no-located-quote-with-snapshot
FAIL entries/symlinkesc.md check6-row-without-reason
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=3        rc=1
```

Against `d85c2696…` the same command returned `entries=1 ok=1 … fail=0`, `rc=0`. Both executions are
in this session's transcript; the difference is the `realpath` hunk in `af73b8b`.

Fixture 6 at `af73b8b` (`tools/souji-gate-check.py:243-255`) now copies a **synthetic** entry
(`pkg/staged-entry.md`) byte-exactly and guards it with `assert`. It is byte-exact; it is not the
staged *package* entry the frozen kill rule names, and an `assert` disappears under `python -O`.

The printed control line (`:280-284`) is still computed as
`green.startswith("entries=1 ok=1 …") and score("no-gate")[1].startswith(…)`, where `green` is a
literal string — the first conjunct is True by construction, so the line can never report a
surviving control. `./MutQuote.md` records it as `PASS … FALSE-GREEN-REJECTED` for the same reason:
it is a decoration, not a measurement. The fixture set, not this line, does the rejecting.

### 5.2 Receipts versus current bytes

| input | HEAD bytes (sha256) | `impl-gate/inputs.sha256` | `impl-gate/counts-latest.txt` |
|---|---|---|---|
| `corpus/knowledge/quarantine-staging-no-copy-r23.md` | `de5f27f5b73af74b…` | `80a6a895…` stale | `80a6a895…` stale |
| `corpus/knowledge/quarantine-origin-record-fields-r24.md` | `015d42930bc18d63…` | `8a21704d…` stale | `f47efc7b…` stale |
| `census/round-22/attempt2/quarantine-slice` | `12d3c325649ca602…` | matches | matches |
| `census/round-22/attempt2/slice-verdicts.tsv` | `9eb1d40679be0977…` | `12cad84e…` stale | `12cad84e…` stale |

Both receipt files predate `5ff5041`/`af73b8b`; neither binds the bytes now at HEAD. The counter
itself was re-executed at `af73b8b` and is green:

```
$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev HEAD --format counts
assertions=59 resolved=59 skipped=36 mismatches=0            rc=0
$ python3 -B tools/souji-gate-check.py … (preregistration C2 command)
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0         rc=0
```

### 5.3 Host paths at `af73b8b` (committed)

```
HEAD:census/round-22/attempt2/sources/vendor-noreplace-probe.out:2,3
HEAD:corpus/knowledge/quarantine-staging-no-copy-r23.md:40,41
HEAD:corpus/SOURCES.md:129
HEAD:corpus/README.md:425
```

`corpus/SOURCES.md:129` cites the vendor digest `1634d206…8bb5`, and
`sha256sum census/round-22/attempt2/sources/vendor-noreplace-probe.out` = `1634d206ef534f68…8bb5`.
The citation is true; redacting those two lines would break it.

## 6. Addendum 2 — tip `ee1aef2`, C1 tool dirty in the worktree

After §5 the lane advanced twice more: `5fdd5d5` ("declared-evidence instrument hardening and honest
calibration row": `SCORECARD.md`, `corpus/knowledge/quarantine-staging-no-copy-r23.md`,
`tools/souji-declared-evidence.py`) and `ee1aef2`. Measured at `ee1aef2`:

```
git rev-parse --short HEAD            -> ee1aef2
git status --porcelain -- tools/      ->  M tools/souji-declared-evidence.py      # dirty
sha256sum tools/souji-gate-check.py   -> 5b8025a83f16957cb2ff6aca0adecfc3a6a1ff796c3eed1d70018ecc339b3062
python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev HEAD --format counts
  tools/souji-declared-evidence.py:108: SyntaxWarning: "\|" is an invalid escape sequence.
  assertions=60 resolved=60 skipped=38 mismatches=0        rc=0
python3 -B tools/souji-gate-check.py … (preregistration C2 command)
  entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0     rc=0
```

Warning source: `tools/souji-declared-evidence.py:108`, the non-raw docstring
`"""Table cells when the line is a table row (escaped \| does not split), else the whole line."""`.
stderr only, so the one-line stdout contract holds; but the counter was measured from a dirty
worktree, and `\|` becomes an error in a future Python. Fix: `r"""…"""`, commit, re-run from a clean
tree. (`tools/souji-declared-evidence.py:306` still ends the selftest with
`subprocess.run(["rm","-rf",base], check=False)`; `:55-58` still calls `subprocess.run` with no
`env=`.)

Hardening landed at `5fdd5d5` that changes this review's §2 reasoning:

* `Repo.read_declaration` no longer falls back to the filesystem for a repo-relative declaration;
  it raises `SystemExit("declaration is not present at %s: %s")`. Only an absolute path (selftest
  fixture) is read from disk. A declaration token therefore cannot reach the filesystem at all.
* class-A globs now go through `_segmatch` (per-segment `fnmatchcase`), so `*` never crosses `/`.
* `PATH_RE`/`GLOB_RE` widened to `[A-Za-z0-9_./@+-]` and the hex regexes are case-insensitive with
  `(?<![0-9A-Za-z_])` boundaries — no authority change; `../../../etc/passwd.md` still matches
  `PATH_RE`, so F10's warning about a worktree-reading repair remains current.

Both counters are green at `ee1aef2`; the `impl-gate/` receipts remain stale against these bytes
(§5.2), and one more edit of the C1 tool is in flight, so no digest in this file should be read as
the round's final receipt.
