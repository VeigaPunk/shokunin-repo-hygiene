STATUS: DONE — Fixed procfs wchan EOF handling; final L1 follow-up gates pass.

# Souji round 18 — ProcCensus

Axis: coverage.

## Scoped files and behavior

- Implementation: `tools/souji-proc-census.sh` in the executor clone; patch delivered at `.ufo/waves/round-18/w1/ProcCensus.patch`.
- Census rows have ten TSV columns (`pid`, `ppid`, `pgid`, `sid`, `age_s`, raw `starttime`, `state`, `wchan`, `reason`, `cmd`) preceded by `# boot_id <value>`. The real-UID `/proc` scan emits one row per process, with reason precedence `cwd-deleted` > `argv-path-gone:<path>` > `fd-path-gone:<path>`.
- argv candidates are absolute elements or values in `--opt=/path` arguments. Prefix matching uses component boundaries and requires the first component below the selected prefix (the top-level scratch directory) to be absent. The FD scan recognizes `/proc/<pid>/fd/*` readlinks ending in ` (deleted)` and applies the same top-level rule. Normal census mode remains read-only and never signals processes.
- `starttime` is field 22 in ticks; it is emitted next to age, with the host boot ID, so a later operator can bind PID observations. TSV control bytes are replaced in every variable field; command text is redacted before truncation to 160 bytes.
- The Bash `read` of `/proc/<pid>/wchan` may assign its non-newline value and then return failure at EOF. The code now preserves that value instead of resetting it, and the selftest asserts the blocked FIFO reader has a non-`-` wchan.
- The bounded selftest covers deleted-cwd reader and sleeper processes, `--workspace=/path` argv extraction under a deleted top-level scratch directory, a deleted open FD, a `/tmpfoo` component-boundary control, an existing-cwd control, secret redaction, and the boot-ID comment/header. Its EXIT trap kills only isolated fixture worker groups and removes its `/var/tmp` files.
- Evidence locations: CLI/prefix handling `tools/souji-proc-census.sh:20-107`; stat parsing, UID and self-tree exclusion `:109-161`; top-level predicate, argv and FD matching `:162-259`; boot ID, age, reason precedence, wchan capture and output fields `:261-357`; fixture cleanup/selftest `:359-488`.

**Verdict: holds for the assigned C3 implementation and L1 follow-up.** Final syntax, ShellCheck, and selftest gates pass. The live run found 65 rows: `cwd-deleted=58`, `argv-path-gone=0`, `fd-path-gone=7`. The existing live residues were observed only; none were signaled. Smallest fix: none within this move; resolving or reaping existing processes is outside the assignment.

## Exact verification commands and outputs

- `bash -n /var/tmp/souji-r18-ProcCensus/lane/tools/souji-proc-census.sh` — exit 0; stdout/stderr empty.
- `shellcheck -S warning /var/tmp/souji-r18-ProcCensus/lane/tools/souji-proc-census.sh` — exit 0; stdout/stderr empty.
- `bash /var/tmp/souji-r18-ProcCensus/lane/tools/souji-proc-census.sh --selftest` — exit 0; output:

```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```

- `bash /var/tmp/souji-r18-ProcCensus/lane/tools/souji-proc-census.sh` — live-host read-only run, exit 0. Full stdout follows; counts by reason are summarized above.

```text
# boot_id 3e7084f4-7046-4957-a8a2-c00542a3b469
pid	ppid	pgid	sid	age_s	starttime	state	wchan	reason	cmd
1026787	1497	1024798	1024798	22450	403309	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.p74cclr3/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.tf977fa2/unsafe-repos/r-inc-fifo --include-root
1026800	1026787	1024798	1024798	22450	403310	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.tf977fa2/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
1242228	1497	1240270	1240270	22040	444395	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.jku4qe9z/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.9lkl1cdg/unsafe-repos/r-inc-fifo --include-root
1242241	1242228	1240270	1240270	22040	444397	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.9lkl1cdg/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
1555085	1497	1537128	1537128	21864	461964	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.sc9ho6nz/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.muz4452a/unsafe-repos/r-inc-fifo --include-root
1555223	1555085	1537128	1537128	21864	461966	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.muz4452a/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
1659	1654	1654	1654	26468	1560	S	do_epoll_wait	fd-path-gone:/dev/shm/e193e6b6-9ac8-4a13-8304-2849975419f6	Hyprland --watchdog-fd 4
1845	1497	1845	1845	26467	1677	S	poll_schedule_timeout.constprop.0	fd-path-gone:/dev/shm/.org.chromium.Chromium.USOuxB	/opt/1Password/1password --silent
185592	1497	184733	184726	10564	1591920	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.z0t4kl7c/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.upcupkw1/unsafe-repos/r-inc-fifo --include-root
185605	185592	184733	184726	10564	1591921	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.upcupkw1/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
1983	1497	1983	1983	26467	1694	S	futex_do_wait	fd-path-gone:/dev/shm/699ba6e5-caca-4e8b-ba77-021ef84d0cc1	/usr/lib/xdg-desktop-portal-hyprland
2147	1910	1845	1845	26466	1701	S	futex_do_wait	fd-path-gone:/dev/shm/.org.chromium.Chromium.USOuxB	/opt/1Password/1password --type=gpu-process --ozone-platform=wayland --render-node-override=/dev/dri/renderD128 --crashpad-handler-pid=1999 --enable-crash-repor
2154933	2083049	2082972	2082972	20836	564767	S	futex_do_wait	fd-path-gone:/tmp/.org.chromium.Chromium.uZBQIX	/usr/lib/chromium/chromium --type=renderer --crashpad-handler-pid=2083034 --enable-crash-reporter=,Arch Linux --noerrdialogs --user-data-dir=/home/vgpnk/.omp/ru
2257336	2083049	2082972	2082972	20822	566120	S	futex_do_wait	fd-path-gone:/tmp/.org.chromium.Chromium.IH5fhS	/usr/lib/chromium/chromium --type=renderer --crashpad-handler-pid=2083034 --enable-crash-reporter=,Arch Linux --noerrdialogs --user-data-dir=/home/vgpnk/.omp/ru
2475440	1497	2473532	2473532	20593	589096	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.hy6ocfc4/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.2tbuivzx/unsafe-repos/r-inc-fifo --include-root
2475453	2475440	2473532	2473532	20593	589098	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.2tbuivzx/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2572254	1497	2568042	2568042	20451	603251	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-PreservationRepin/preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.wwwcjof5/unsafe-repos/r-inc-fifo --include-root
2572307	2572254	2568042	2568042	20451	603252	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.wwwcjof5/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2629870	1497	2626165	2626165	20427	605618	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.9az4qh_i/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.x7las1fv/unsafe-repos/r-inc-fifo --include-root
2629891	2629870	2626165	2626165	20427	605619	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.x7las1fv/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2650283	1497	2638126	2638126	23078	340570	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16/preharm.sh --root /var/tmp/r15-census-config.7tgaqhd1/unsafe-repos/r-inc-fifo --include-root
2650499	2650283	2638126	2638126	23078	340572	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.7tgaqhd1/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2764974	1497	2763057	2763057	20251	623239	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.9zgl_8hd/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.f8u_yo2f/unsafe-repos/r-inc-fifo --include-root
2764987	2764974	2763057	2763057	20251	623240	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.f8u_yo2f/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2800031	1497	2794427	2794427	20145	633817	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-PreservationRepin/preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.9bktk3rl/unsafe-repos/r-inc-fifo --include-root
2800121	2800031	2794427	2794427	20145	633819	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.9bktk3rl/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
289650	1497	288604	288604	10199	1628476	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-matrix.qmxy_npd/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config._17e3yjp/unsafe-repos/r-inc-fifo --include-root
289668	289650	288604	288604	10199	1628478	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config._17e3yjp/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
2984182	1497	2983119	2983111	19705	677846	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.qucgbnxl/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.su2st6_0/unsafe-repos/r-inc-fifo --include-root
2984195	2984182	2983119	2983111	19705	677847	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.su2st6_0/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
3050160	1497	3049314	3049307	19547	693652	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.scjidogf/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.q4lgeupp/unsafe-repos/r-inc-fifo --include-root
3050173	3050160	3049314	3049307	19547	693653	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.q4lgeupp/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
3139964	1497	3137586	3137586	19363	712012	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.6m58cnsu/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.x8xy7rf3/unsafe-repos/r-inc-fifo --include-root
3139977	3139964	3137586	3137586	19363	712013	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.x8xy7rf3/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
3252942	1497	3250850	3250850	11098	1538504	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-matrix.ccednztz/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.prl783jh/unsafe-repos/r-inc-fifo --include-root
3252974	3252942	3250850	3250850	11098	1538506	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.prl783jh/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
365980	1497	362699	362699	7925	1855882	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-matrix.pmzb8vuw/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.7yc1yrcp/unsafe-repos/r-inc-fifo --include-root
366021	365980	362699	362699	7925	1855888	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.7yc1yrcp/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
3848039	1497	3845852	3845852	18906	757793	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-matrix.v6lm0rcz/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.xcfjf9ps/unsafe-repos/r-inc-fifo --include-root
3848052	3848039	3845852	3845852	18906	757794	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.xcfjf9ps/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
4037294	1497	4034162	4034097	4844	2163953	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin._i36vtux/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.1hkjbmmt/unsafe-repos/r-inc-fifo --include-root
4037365	4037294	4034162	4034097	4844	2163954	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.1hkjbmmt/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
562276	1497	558610	558610	13074	1340976	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/a31642d.sh --root /var/tmp/r17-census-hygiene.e80b0xqe/d2-fifo
562277	562276	558610	558610	13074	1340976	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/a31642d.sh --root /var/tmp/r17-census-hygiene.e80b0xqe/d2-fifo
562279	562277	558610	558610	13074	1340976	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r17-census-hygiene.e80b0xqe/d2-fifo/b --no-optional-locks status --porcelain -- . :(exclude).ufo/state :(exclude).ufo/watchdog.log
574643	1497	558608	558608	13072	1341118	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-fifo
574984	574643	558608	558608	13072	1341122	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-fifo
574987	574984	558608	558608	13072	1341122	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-fifo
574989	574987	558608	558608	13072	1341122	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r17-census-hygiene.lwka_g_w/d2-fifo/b --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev
596478	1497	558610	558610	13014	1346977	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/a31642d.sh --root /var/tmp/r17-census-hygiene.e80b0xqe/d2-symlink-fifo
596479	596478	558610	558610	13014	1346977	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/a31642d.sh --root /var/tmp/r17-census-hygiene.e80b0xqe/d2-symlink-fifo
596480	596479	558610	558610	13014	1346977	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r17-census-hygiene.e80b0xqe/d2-symlink-fifo/b --no-optional-locks status --porcelain -- . :(exclude).ufo/state :(exclude).ufo/watchdog.
597162	1497	558608	558608	13012	1347122	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-symlink-fifo
597357	597162	558608	558608	13012	1347128	S	anon_pipe_read	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-symlink-fifo
597358	597357	558608	558608	13012	1347128	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-FixtureR17Census/cc21683.sh --root /var/tmp/r17-census-hygiene.lwka_g_w/d2-symlink-fifo
597359	597358	558608	558608	13012	1347128	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r17-census-hygiene.lwka_g_w/d2-symlink-fifo/b --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesF
598877	1497	598030	598023	12989	1349474	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.v12xk2yg/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.s8n_rh15/unsafe-repos/r-inc-fifo --include-root
598890	598877	598030	598023	12989	1349475	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.s8n_rh15/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
639553	1497	638541	638541	4581	2190206	S	do_wait	cwd-deleted	bash /var/tmp/souji-r17-matrix.8cxpl2lv/pre-harm/tools/souji-census.sh --root /var/tmp/r15-census-config.ujpcunsx/unsafe-repos/r-inc-fifo --include-root
639568	639553	638541	638541	4581	2190207	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.ujpcunsx/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
812467	1497	811363	811234	12727	1375688	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.t4vqobh_/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.rxdxzqi8/unsafe-repos/r-inc-fifo --include-root
812480	812467	811363	811234	12727	1375690	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.rxdxzqi8/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
863272	1497	863269	863269	22756	372773	S	poll_schedule_timeout.constprop.0	fd-path-gone:/tmp/kama-r16-FamilyLoadingRace/loading-current.json	import argparse
918756	1497	917810	917803	12564	1391964	S	do_wait	cwd-deleted	bash /var/tmp/souji-r16-repin.sf2f30d9/baseline_preharm/tools/souji-census.sh --root /var/tmp/r15-census-config.otdn8qgj/unsafe-repos/r-inc-fifo --include-root
918769	918756	917810	917803	12564	1391965	S	wait_for_partner	cwd-deleted	/usr/bin/git -C /var/tmp/r15-census-config.otdn8qgj/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
```

## Risks and blockers

- This live read only observes; it did not signal any reported process. The output includes 58 existing deleted-cwd fixture processes and seven deleted-FD holders, including PID 863272 from the L1 note. No `argv-path-gone` rows were emitted in this snapshot.
- Command redaction covers the requested secret shapes, not arbitrary unknown credential formats. Procfs reads are snapshots and can race process exit; stat starttime is rechecked against the census snapshot before emitting each row.
- No blocker. No tools were installed or updated. No LSP interface was exposed in this tool session; this is a standalone script with no existing symbol references to refactor.
