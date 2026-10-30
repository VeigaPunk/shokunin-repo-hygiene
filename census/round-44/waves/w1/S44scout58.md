# S44scout58 — source opening result

Complete report, exact fetch/provenance commands, outputs, one scoped A-row proposal, and preservation-authority rejection: [S44scout58/report.md](S44scout58/report.md).

Axes: calibration / operability / coverage; coverage-only evidence, no score delta or admission claim. Registry untouched.

Both requested sources opened on 2026-10-30 with HTTP 200; raw snapshots and HTTP headers preserved under `S44scout58/`:

- [symlink(2), DESCRIPTION](https://man7.org/linux/man-pages/man2/symlink.2.html#DESCRIPTION): “symlink() creates a symbolic link named linkpath which contains the string target.” (12 words; snapshot lines 98–99).
- [Python os.open](https://docs.python.org/3/library/os.html#os.open): “Return the file descriptor for the newly opened file.” (9 words; snapshot line 1620).
- Same Python section: “For a description of the flag and mode values, see the C run-time documentation;” (14 words; snapshot line 1622).

Bounded HTML-decoding checks: all three quotes present, all <=25 words. Frozen C3 counter digest matched preregistration and d314fd6e85d62565344fa6c4b102f52f62297884: `eba3e69ffef1493f4733c5c5537b8b2e5ed0a4cdcbaf551f560e03e8bcc64d66`.

Rejected inference: interface documentation or leaf refusal proves universal preservation and authorizes deleting rejected paths. Neither source grants that authority; C3 remains a defensive caller-output contract. Runtime races, hardlinks, ancestors, fixture outcomes, and non-author admission are not established by this source opening. Confidence: high for quotations and provenance; no implementation-safety claim.

Cleanup command: `rmdir /fast/scratch/hyaku/souji-r44/S44scout58 && printf 'seat scratch removed\n'`; exit 0, output `seat scratch removed`. No installs/updates or production/registry changes.
