source: S022 https://specifications.freedesktop.org/trash/latest/ (header "Version: 1.0"; §5 Trash directories; §6 Contents of a trash directory; §9 Implementation notes); S023 https://github.com/andreafrancia/trash-cli README.rst (command list :14-18; trash-empty :78-86; FAQ :122-130)
verified-at: 2026-10-19; Trash Specification Version 1.0 (Publication Date 2014-01-02), local copy sha256 353442d2…; trash-cli README (master, sha256 863bf38a…), trash-cli 0.26.9.29 per ART; host: gio present, trash-put absent (scout-surfaces.md:124); no trashing was performed
recheck: bash -c 'p=$(curl -fsSL https://specifications.freedesktop.org/trash/latest/ | sed "s/<[^>]*>//g" | tr -s " \n" " "); for s in "Version: 1.0" "MUST check that this directory is not a symbolic link" "MUST create the corresponding file in \$trash/info first" "opening with O_EXCL" "must not overwrite a previous copy" "this is an emergency case"; do printf "%s\t%s\n" "$(grep -cF "$s" <<<"$p")" "$s"; done'   # expect 1 on every line

# Trash spec 1.0: a restorable-quarantine format with ordering and no-overwrite rules

## Claim
The FreeDesktop Trash spec 1.0 defines removal that can be undone:
- A trash dir has `files/` (payload) and `info/` (one `<name>.trashinfo` per payload, `[Trash Info]`, `Path=` original location, `DeletionDate=`).
- The info file is created FIRST, atomically (generate name, open with O_EXCL; on failure pick another name). Payload follows.
- Names in `files/` are unique; re-trashing the same path never overwrites an earlier copy. The payload name is never trusted to recover the original path; a payload without info is an "emergency case" that MUST be shown as such.
- A shared `$topdir/.Trash` MUST be checked for the sticky bit and MUST NOT be a symlink; failing either, it MUST NOT be used (fallback `$topdir/.Trash-$uid`).
- Home trash `$XDG_DATA_HOME/Trash` SHOULD receive same-filesystem trashings; cross-partition trashing into it "leads to costly file copying".
trash-cli implements it: `trash-put`, `trash-list`, `trash-restore`, `trash-rm`, `trash-empty [<days>]`.

## Evidence
- S022 header: "Publication Date: 2014-01-02, Version: 1.0" — agree.
- §5: "The implementation also MUST check that this directory is not a symbolic link." (the `$topdir/.Trash` paragraph) — agree; "If any of these checks fail, the implementation MUST NOT use this directory for either trashing or undeleting files".
- §6: "Even if a file with the same name and location gets trashed many times, each subsequent trashing must not overwrite a previous copy." — agree.
- §6 Important: "A filename in the $trash/files directory MUST NEVER be used to recover the original filename; use the info file … (If an info file corresponding to a file/directory in $trash/files is not available, this is an emergency case, and MUST be clearly presented as such …)" — agree.
- §6: "The key "Path" contains the original location"; example `Path=foo/bar/meow.bow-wow`, `DeletionDate=20040831T22:32:08`.
- §6: "When trashing a file or directory, the implementation MUST create the corresponding file in $trash/info first. … On Unix-line systems this is done by generating a filename, and then opening with O_EXCL." — agree (spec text says "Unix-line").
- §5: "Files that the user trashes from the same file system (device/partition) SHOULD be stored here"; "this solution leads to costly file copying (between partitions, …)".
- §9: names in info/ "SHOULD be somehow related to original file names. This can help manual recovery in emergency cases".
- S023 FAQ :122-130 "Can I alias `rm` to `trash-put`? … You can but you shouldn't." because `rm` "requires `-R` for deleting directories `trash-put` does not."

## Failure cases (Q3)
- Symlinked trash root: spec §5 forbids using a symlinked `.Trash`. souji hit the same shape: r10 C2-Q1, `<repo>/.ufo-quarantine` as a symlink "is followed. `mkdir -p`/`mv`/`rm -rf` then operate through the link"; the ABORTED path left payload "resting outside the repo … with the original gone" (census/round-10/S06-cluster-C-member2.md:53-63).
- Lost info file = emergency case (§6): a payload with no recorded origin cannot be restored by name.

## Lane link
- Installed tools/souji-quarantine.sh (sha256 141c0fdc…) stages into `<repo>/.ufo-quarantine/<utc-date>/` keeping the repo-relative path (:42-45), refuses `quarantine-collision` (:478, ≈ spec's no-overwrite rule) and `symlink-or-noncanonical-quarantine-path` (:1111, ≈ §5). It writes no per-item info record; the origin is encoded in the staged path (what §6 says MUST NEVER be relied on).
- LOG.md:447-451: operator directive emptied `~/.local/share/Trash` (694M, 3 entries) after capturing a manifest to `/home/vgpnk/.souji-quarantine/hf-20261019/`; "no receipts class applies". LOG.md:445: the same quarantine used a "model manifest", not per-item trashinfo.
- Home Trash and all lane repos share device 30 (`/home`) (census/round-12/scout-surfaces.md:94), so spec home-trash moves from those repos are renames.
- Adopting a trashinfo-style record (info-first, O_EXCL, Path=, DeletionDate=) for souji quarantine is a tool/format change: OPERATOR DECISION.

## Limits
- Spec text only; no trashing was run (no `gio trash`, no `trash-put`). trash-cli's own O_EXCL/symlink handling was not read in source.
- The spec's "atomic" claim is qualified "(at least on the same machine)"; network filesystems are out of scope.
