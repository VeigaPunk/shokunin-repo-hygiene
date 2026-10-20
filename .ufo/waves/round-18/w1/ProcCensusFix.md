STATUS: DONE — Fixed W2 process-identity, suffix-ambiguity, redaction, age, and stat-parser findings on 5efb519.

# Souji round 18 — ProcCensusFix

Axis: coverage (with the requested calibration and operability corrections).

## Findings resolved

- **Literal ` (deleted)` names:** `cwd-deleted` is assigned only when the raw `/proc/<pid>/cwd` text ends in the suffix and does not resolve to the held inode (`-e` plus `-ef`). FD targets use the same raw-link inode confirmation before stripping the kernel suffix. Thus an existing directory/file literally named `x (deleted)` is not reported, while an actually unlinked inode remains eligible.
- **argv/FD predicate and prefix scope:** argv accepts a full absolute element or a `--option=/absolute` value, then requires both the candidate and its first component below the selected prefix (top-level scratch directory) to be absent using `! -e`. The FD detector uses the same selected-prefix/top-level rule. `--prefix` is documented and implemented for argv/FD checks only; deleted cwd reporting remains unrestricted. Component boundaries prevent `/tmpfoo` matching `/tmp`.
- **Reason precedence:** one row per PID, `cwd-deleted` > `argv-path-gone` > `fd-path-gone`; selftest exercises both a cwd+argv+FD residue and a live literal cwd with argv+FD residue.
- **Redaction:** before byte truncation, command text masks Authorization/Bearer headers (including split argv elements), case-insensitive `--token` forms, underscore-containing `ghp_` values, `AKIA` plus 16 uppercase alphanumerics, `xox[baprs]-` tokens, and the prior `sk-`, `password=`, and URL-userinfo shapes.
- **Age and identity:** age is `floor((uptime_ticks - starttime) / CLK_TCK)` using `/proc/uptime` hundredths converted to ticks. UID and field-22 starttime are re-read immediately before output. `starttime` remains in the TSV after `age_s`, paired with the `# boot_id` header comment.
- **Newline in `comm`:** `/proc/<pid>/stat` is accumulated across physical lines before extracting the final `) ` delimiter. The selftest includes a synthetic `comm` with an embedded newline and asserts the field-22 result.
- **Selftest signal scope:** workers are single-process `setsid` children; cleanup signals an individual PID only when its parent, session/group, and recorded starttime still match. This avoids the prior stale-PGID group-signal reuse risk. All fixture files remain under `/var/tmp` and are removed by the EXIT trap.

Evidence locations in the pinned clone: prefix documentation/options `tools/souji-proc-census.sh:20-102`; newline-safe stat parsing and UID/self-tree logic `:109-158`; top-level predicate, redaction, argv and FD matching `:160-276`; uptime ticks, boot ID, reason precedence, final UID/starttime revalidation, and TSV output `:278-379`; identity-checked fixture cleanup and regression selftests `:381-669`.

**Verdict: holds for the assigned W2 findings.** The independent fixture executor reported P1–P19 passing against this 5efb519 clone; it also reported its P7 strace saw no signal syscalls outside selftest. My own final syntax, ShellCheck, and selftest gates pass. Smallest remaining fix: none within this move.

## Exact local verification commands and outputs

- `bash -n /var/tmp/souji-r18-ProcCensusFix/lane/tools/souji-proc-census.sh` — exit 0; stdout/stderr empty.
- `shellcheck -S warning /var/tmp/souji-r18-ProcCensusFix/lane/tools/souji-proc-census.sh` — exit 0; stdout/stderr empty.
- `bash /var/tmp/souji-r18-ProcCensusFix/lane/tools/souji-proc-census.sh --selftest` — exit 0; output:

```text
souji-proc-census: selftest PASS (newline comm parser, live literal cwd/fd, age identity, all redactions, prefix boundary/scope, mixed precedence, isolated cleanup)
```

- `bash /var/tmp/souji-r18-ProcCensusFix/lane/tools/souji-proc-census.sh` — live-host read-only run, exit 0. Counts: `cwd-deleted=58`, `argv-path-gone=0`, `fd-path-gone=12` (70 rows total). Full stdout:

```text
# boot_id 3e7084f4-7046-4957-a8a2-c00542a3b469
pid	ppid	pgid	sid	age_s	starttime	state	wchan	reason	cmd
1026787	1497	1024798	1024798	28114	403309	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.p74cclr3/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.tf977fa2/unsafe-repos/r-inc-fifo --include-root
1026800	1026787	1024798	1024798	28114	403310	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.tf977fa2/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
1242228	1497	1240270	1240270	27703	444395	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.jku4qe9z/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.9lkl1cdg/unsafe-repos/r-inc-fifo --include-root
1242241	1242228	1240270	1240270	27703	444397	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.9lkl1cdg/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
1555085	1497	1537128	1537128	27527	461964	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.sc9ho6nz/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.muz4452a/unsafe-repos/r-inc-fifo --include-root
1555223	1555085	1537128	1537128	27527	461966	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.muz4452a/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
1659	1654	1654	1654	32131	1560	S	do_epoll_wait	fd-path-gone:/dev/shm/e193e6b6-9ac8-4a13-8304-2849975419f6	Hyprland --watchdog-fd 4
1845	1497	1845	1845	32130	1677	S	poll_schedule_timeout.constprop.0	fd-path-gone:/dev/shm/.org.chromium.Chromium.USOuxB	/opt/1Password/1password --silent
185592	1497	184733	184726	16228	1591920	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.z0t4kl7c/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.upcupkw1/unsafe-repos/r-inc-fifo --include-root
185605	185592	184733	184726	16228	1591921	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.upcupkw1/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
1983	1497	1983	1983	32130	1694	S	futex_do_wait	fd-path-gone:/dev/shm/699ba6e5-caca-4e8b-ba77-021ef84d0cc1	/usr/lib/xdg-desktop-portal-hyprland
2147	1910	1845	1845	32130	1701	S	futex_do_wait	fd-path-gone:/dev/shm/.org.chromium.Chromium.USOuxB	/opt/1Password/1password --type=gpu-process --ozone-platform=wayland --render-node-override=/dev/dri/renderD128 --crashpad-handler-pid=1999 --enable-crash-repor
2154933	2083049	2082972	2082972	26499	564767	S	futex_do_wait	fd-path-gone:/tmp/.org.chromium.Chromium.uZBQIX	/usr/lib/chromium/chromium --type=renderer --crashpad-handler-pid=2083034 --enable-crash-reporter=,Arch Linux --noerrdialogs --user-data-dir=/home/vgpnk/.omp/ru
2475440	1497	2473532	2473532	26256	589096	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.hy6ocfc4/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.2tbuivzx/unsafe-repos/r-inc-fifo --include-root
2475453	2475440	2473532	2473532	26256	589098	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.2tbuivzx/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2572254	1497	2568042	2568042	26115	603251	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-PreservationRepin/preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.wwwcjof5/unsafe-repos/r-inc-fifo --include-root
2572307	2572254	2568042	2568042	26115	603252	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.wwwcjof5/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2629870	1497	2626165	2626165	26091	605618	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.9az4qh_i/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.x7las1fv/unsafe-repos/r-inc-fifo --include-root
2629891	2629870	2626165	2626165	26091	605619	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.x7las1fv/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2650283	1497	2638126	2638126	28741	340570	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16/preharm.sh --root /var/tmp/r15-census-config.7tgaqhd1/unsafe-repos/r-inc-fifo --include-root
2650499	2650283	2638126	2638126	28741	340572	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.7tgaqhd1/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2764974	1497	2763057	2763057	25881	623239	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.9zgl_8hd/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.f8u_yo2f/unsafe-repos/r-inc-fifo --include-root
2764987	2764974	2763057	2763057	25881	623240	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.f8u_yo2f/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2800031	1497	2794427	2794427	25775	633817	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-PreservationRepin/preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.9bktk3rl/unsafe-repos/r-inc-fifo --include-root
2800121	2800031	2794427	2794427	25775	633819	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.9bktk3rl/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
289650	1497	288604	288604	15862	1628476	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-matrix.qmxy_npd/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config._17e3yjp/unsafe-repos/r-inc-fifo --include-root
289668	289650	288604	288604	15862	1628478	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config._17e3yjp/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2984182	1497	2983119	2983111	25369	677846	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.qucgbnxl/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.su2st6_0/unsafe-repos/r-inc-fifo --include-root
2984195	2984182	2983119	2983111	25369	677847	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.su2st6_0/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
3050160	1497	3049314	3049307	25211	693652	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.scjidogf/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.q4lgeupp/unsafe-repos/r-inc-fifo --include-root
3050173	3050160	3049314	3049307	25211	693653	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.q4lgeupp/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
3139964	1497	3137586	3137586	25027	712012	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.6m58cnsu/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.x8xy7rf3/unsafe-repos/r-inc-fifo --include-root
3139977	3139964	3137586	3137586	25027	712013	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.x8xy7rf3/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
3252942	1497	3250850	3250850	16762	1538504	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-matrix.ccednztz/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.prl783jh/unsafe-repos/r-inc-fifo --include-root
3252974	3252942	3250850	3250850	16762	1538506	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.prl783jh/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
3389250	2083049	2082972	2082972	522	3162473	S	futex_do_wait	fd-path-gone:/tmp/.org.chromium.Chromium.R9ylT1	/usr/lib/chromium/chromium --type=renderer --top-chrome-webui --crashpad-handler-pid=2083034 --enable-crash-reporter=,Arch Linux --noerrdialogs --user-data-dir=
3389266	2083049	2082972	2082972	522	3162475	S	futex_do_wait	fd-path-gone:/tmp/.org.chromium.Chromium.4WJ4GJ	/usr/lib/chromium/chromium --type=renderer --crashpad-handler-pid=2083034 --enable-crash-reporter=,Arch Linux --noerrdialogs --user-data-dir=/home/vgpnk/.omp/ru
3505617	2083049	2082972	2082972	477	3167042	S	futex_do_wait	fd-path-gone:/tmp/.org.chromium.Chromium.JAaT7m	/usr/lib/chromium/chromium --type=renderer --crashpad-handler-pid=2083034 --enable-crash-reporter=,Arch Linux --noerrdialogs --user-data-dir=/home/vgpnk/.omp/ru
3566415	2083049	2082972	2082972	446	3170057	S	futex_do_wait	fd-path-gone:/tmp/.org.chromium.Chromium.qZJ6Be	/usr/lib/chromium/chromium --type=renderer --crashpad-handler-pid=2083034 --enable-crash-reporter=,Arch Linux --noerrdialogs --user-data-dir=/home/vgpnk/.omp/ru
3567055	2083049	2082972	2082972	446	3170130	S	futex_do_wait	fd-path-gone:/tmp/.org.chromium.Chromium.w1h1hz	/usr/lib/chromium/chromium --type=renderer --crashpad-handler-pid=2083034 --enable-crash-reporter=,Arch Linux --noerrdialogs --user-data-dir=/home/vgpnk/.omp/ru
3567275	2083049	2082972	2082972	445	3170158	S	futex_do_wait	fd-path-gone:/tmp/.org.chromium.Chromium.EDjTd8	/usr/lib/chromium/chromium --type=renderer --crashpad-handler-pid=2083034 --enable-crash-reporter=,Arch Linux --noerrdialogs --user-data-dir=/home/vgpnk/.omp/ru
365980	1497	362699	362699	13554	1855882	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-matrix.pmzb8vuw/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.7yc1yrcp/unsafe-repos/r-inc-fifo --include-root
366021	365980	362699	362699	13554	1855888	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.7yc1yrcp/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
3848039	1497	3845852	3845852	24569	757793	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.v6lm0rcz/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.xcfjf9ps/unsafe-repos/r-inc-fifo --include-root
3848052	3848039	3845852	3845852	24569	757794	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.xcfjf9ps/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
4037294	1497	4034162	4034097	10508	2163953	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin._i36vtux/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.1hkjbmmt/unsafe-repos/r-inc-fifo --include-root
4037365	4037294	4034162	4034097	10508	2163954	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.1hkjbmmt/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
562276	1497	558610	558610	18737	1340976	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/a31642d.sh --root /var/tmp/r17-census-hygiene.e80b0xqe/d2-fifo
562277	562276	558610	558610	18737	1340976	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/a31642d.sh --root /var/tmp/r17-census-hygiene.e80b0xqe/d2-fifo
562279	562277	558610	558610	18737	1340976	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r17-census-hygiene.e80b0xqe/d2-fifo/b --no-optional-locks status --porcelain -- . :(exclude).ufo/state :(exclude).ufo/watchdog.log
574643	1497	558608	558608	18736	1341118	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-fifo
574984	574643	558608	558608	18736	1341122	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-fifo
574987	574984	558608	558608	18736	1341122	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-fifo
574989	574987	558608	558608	18736	1341122	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r17-census-hygiene.lwka_g_w/d2-fifo/b --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev
596478	1497	558610	558610	18677	1346977	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/a31642d.sh --root /var/tmp/r17-census-hygiene.e80b0xqe/d2-symlink-fifo
596479	596478	558610	558610	18677	1346977	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/a31642d.sh --root /var/tmp/r17-census-hygiene.e80b0xqe/d2-symlink-fifo
596480	596479	558610	558610	18677	1346977	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r17-census-hygiene.e80b0xqe/d2-symlink-fifo/b --no-optional-locks status --porcelain -- . :(exclude).ufo/state :(exclude).ufo/watchdog.
597162	1497	558608	558608	18676	1347122	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-symlink-fifo
597357	597162	558608	558608	18676	1347128	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-symlink-fifo
597358	597357	558608	558608	18676	1347128	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-symlink-fifo
597359	597358	558608	558608	18676	1347128	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r17-census-hygiene.lwka_g_w/d2-symlink-fifo/b --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesF
598877	1497	598030	598023	18652	1349474	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.v12xk2yg/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.s8n_rh15/unsafe-repos/r-inc-fifo --include-root
598890	598877	598030	598023	18652	1349475	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.s8n_rh15/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
639553	1497	638541	638541	10245	2190206	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-matrix.8cxpl2lv/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.ujpcunsx/unsafe-repos/r-inc-fifo --include-root
639568	639553	638541	638541	10245	2190207	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.ujpcunsx/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
812467	1497	811363	811234	18390	1375688	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.t4vqobh_/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.rxdxzqi8/unsafe-repos/r-inc-fifo --include-root
812480	812467	811363	811234	18390	1375690	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.rxdxzqi8/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
863272	1497	863269	863269	28419	372773	S	poll_schedule_timeout.constprop.0	fd-path-gone:/tmp/kama-r16-FamilyLoadingRace/loading-current.json	import argparse
918756	1497	917810	917803	18227	1391964	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.sf2f30d9/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.otdn8qgj/unsafe-repos/r-inc-fifo --include-root
918769	918756	917810	917803	18227	1391965	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.otdn8qgj/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
```

## Risks and blockers

- This live snapshot only observes; it did not signal any reported process. It contains 58 `cwd-deleted`, 12 `fd-path-gone`, and no `argv-path-gone` rows. The 12 FD rows include PID 863272 from the L1 note.
- `/proc` is sampled non-atomically. UID and field-22 starttime are checked again immediately before output, but a process can still exit after the final check. Redaction covers the specified token families/shapes; it is not a general secret scanner.
- No blocker. No tools were installed or updated. No LSP interface was exposed in this session; this is a standalone script with no existing symbol reference to refactor.
