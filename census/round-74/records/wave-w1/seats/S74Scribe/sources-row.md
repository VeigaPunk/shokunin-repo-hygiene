| S317 | gitformat-index(5) at tag v2.56.0, Index entry, https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-index.adoc (sha256 c8aca94073fed907c47f631db8a9c53a9a0a0007f8ea3cdce9722224bebbaa93, fetched 2026-11-06, HTTP 200, 15194 bytes; capture census/round-74/srcs/gitformat-index.adoc) | docs | A | what one index entry records (scope: the stat(2) fields, the mode object type and the object name of an entry; extensions and sparse entries not used) | Index entry, 32-bit mode; quote at offset 2194 of census/round-74/srcs/gitformat-index.txt (whitespace-normalized): "4-bit object type valid values in binary are 1000 (regular file), 1010 (symbolic link) and 1110 (gitlink)" | an entry keeps stat(2) data, a type and the object name side by side, so a gate can compare the worktree with the object name (hashing regular files, the link target for 1010) and leave gitlinks out, instead of trusting the stat fields git status compares (measured: r74 rows GF1-GF3, census/round-74/records/c1-after.txt) | mined | 2026-11-06 | 180d | corpus/knowledge/filter-filemode-witness.md |

<!-- Draft append target: corpus/SOURCES.md, immediately after the S316 row (line 275 at lane base
43cd74bba84bb498b57a74377ccb0567d10864d5). Verified against committed bytes, 2026-11-06:
- capture sha256 c8aca94073fed907c47f631db8a9c53a9a0a0007f8ea3cdce9722224bebbaa93, 15194 bytes
  (census/round-74/srcs/gitformat-index.adoc);
- quote occurs once in census/round-74/srcs/gitformat-index.txt at byte offset 2194, 17 words;
- 11 pipe-delimited cells, no `|` inside any cell (delimiters only). -->
