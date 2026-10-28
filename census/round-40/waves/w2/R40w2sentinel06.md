# R40w2sentinel06 — scratch-residue review

**Verdict: INCONCLUSIVE for complete residue inventory; SAFE for the targeted alive-process check as of this snapshot.** This ticket audits scratch residue, not C1/C2/C3 source behavior. No committed code or fixtures were attacked; consequently no source file:line applies. The only observed live round-40 process identified was in executor06 and was left untouched.

## Commands and observed results

1. `find /fast/scratch/hyaku/souji-r40 -mindepth 1 -printf '%TY-%Tm-%Td %TH:%TM:%TS %y %p\\n' | sort`

   Output was 45,255 lines (large output elided by the tool). It showed extensive dated seat work, including a new `/fast/scratch/hyaku/souji-r40/w2/R40w2critic08/...` tree with timestamps around 17:09 and `R40w2mutationtester05/...` around 17:09. This command did not filter the requested time threshold and therefore is not a complete/concise evidence list.

2. `find /tmp -mindepth 1 -newermt '2026-10-28 16:45:00' -printf '%TY-%Tm-%Td %TH:%TM:%TS %y %p\\n' | sort`

   Result: enormous listing (99,859 lines; tool output elided), with permission-denied errors for systemd-private directories and several vanished `tameshi-*` temporary paths. Top-level recent entries included numerous unrelated seat temp files/directories. Because listing was broad and truncation/permission errors occurred, a definitive round-40-only `/tmp` inventory is not established.

3. `df -h /tmp /fast/scratch`

   ```
   Filesystem      Size  Used Avail Use% Mounted on
   /dev/nvme1n1p1  128G   27G  102G  21% /tmp
   /dev/nvme1n1p2  804G  278G  526G  35% /fast
   ```

4. `find /fast/scratch/hyaku/souji-r40/w2 -mindepth 1 -maxdepth 2 -type d -newermt '2026-10-28 16:45:00' -printf '%TY-%Tm-%Td %TH:%TM:%TS %p\\n' | sort; printf '\\nProcesses mentioning round scratch:\\n'; ps -eo pid,etime,args | grep -E 'souji-r40|R40w2' | grep -v grep; printf '\\nRecent top-level /tmp entries:\\n'; find /tmp -mindepth 1 -maxdepth 1 -newermt '2026-10-28 16:45:00' -printf '%TY-%Tm-%Td %TH:%TM:%TS %y %p\\n' | sort`

   The recent round scratch top-level paths shown include `R40w2mutationtester07`, `R40w2executor06`, `R40w2sentinel01`, reviewer/critic/executor/mutationtester/revenger/simplifier/scout seat dirs. Most names directly map to round-40 seat naming. The process listing contained live round-40 seat work, including:
   - PID 2791264: `c3-counter.py ... --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2critic07/c3`.
   - PID 2794619 and descendants: critic07 `r40-branches.py` / M15.py fixture execution under `/fast/scratch/hyaku/souji-r40/w2/R40w2critic07/c3/...`.
   - Several processes using executor06 lane tools, with scratch roots below `/fast/scratch/hyaku/souji-r40/w2/R40w2executor06`.

5. `ps -eo pid,etime,args | grep -F '/fast/scratch/hyaku/souji-r40/w2/' | grep -v grep; printf '\\nDisk:\\n'; df -h /tmp /fast/scratch`

   This second snapshot confirmed active round-40 tasks at that instant, including critic07 C3 counter and fixture commands and executor06 tools. Space snapshot:

   ```
   Filesystem      Size  Used Avail Use% Mounted on
   /dev/nvme1n1p1  128G   26G  103G  21% /tmp
   /dev/nvme1n1p2  804G  277G  527G  35% /fast
   ```

## Disposition

No scratch was created by this seat, so **this seat's scratch directory was not created and was not removed**. No residue was deleted. Any live-process-associated scratch was deliberately preserved. Full classification of each recent `/tmp` item as round-40 versus unrelated remains **INCONCLUSIVE**, because the exhaustive listing was too large/truncated and included inaccessible and disappeared entries; rerun a focused timestamp-filtered listing and process-owner mapping to complete that inventory. No tools were installed.