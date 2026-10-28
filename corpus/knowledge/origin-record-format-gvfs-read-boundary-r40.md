source: S257 GNOME/gvfs 1.62.0 `daemon/trashlib/trashitem.c` — https://raw.githubusercontent.com/GNOME/gvfs/1.62.0/daemon/trashlib/trashitem.c (tag 1.62.0, snapshot census/round-40/sources/gvfs-trashitem-1.62.0.c sha256 3a8f8cbb057ac3bb8d4ba4901d43f8fd1abcd89b9ff095ef927999154af3d25b; opened 2026-10-28)
verified-at: 2026-10-28 — the pinned implementation lines were re-opened (172-195); no record was written or read in a live trash directory
recheck: 365d — re-fetch at tag 1.62.0 and re-read lines 172-195: `curl -sS https://raw.githubusercontent.com/GNOME/gvfs/1.62.0/daemon/trashlib/trashitem.c`
ground: F4 — restorable quarantine, implementation read-side boundary (correction to the r40 GVFS assimilation entry)

# The GVFS reader queries the two trash-info keys but does not require both values

S257 **supersedes S254's overstatement** that every record “must carry” both `Path` and
`DeletionDate`. At tag 1.62.0, `trash_item_get_trashinfo()` reads `Path` with
`g_key_file_get_string()` at lines 172-174, then explicitly accepts a missing value:

> “if (orig == NULL)”

(`census/round-40/sources/gvfs-trashitem-1.62.0.c:174`.) If `Path` is absent, the reader sets
`*original = NULL`; it does not reject the record. It queries `DeletionDate` at lines 192-194, but the
source does not enforce its presence either. Therefore the implementation demonstrates which keys the
reader queries and how a present path is resolved; it does NOT establish a required-field schema.

The lane's normative source remains S022. S254's exact path-template and URI-unescape excerpts remain
true as code quotations; only the “required two-key record” inference is superseded here. The
campaign-staged S146 is the same GVFS document but its id is not used: this lane's source register is
append-only, and the new correction follows the local id sequence at S257.
