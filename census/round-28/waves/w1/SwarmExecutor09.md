## Status
STATUS: PASS — both committed round-27 GLib snapshots match their digest pins and fetched tag 2.84.0 bytes.

## Evidence
- `cd /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-27/sources && sha256sum -c SHA256SUMS && sha256sum glocalfile.c gfileutils.c` → both `OK`; digests `66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f` and `5161ae435ee57448c280323de064e1d6d62dc1ba3ba2771c5982b913888dfad5`.
- `curl -fsSL` for each raw URL at tag `2.84.0`, then `sha256sum` and `git hash-object` → both downloaded byte hashes equal pins and committed snapshot blob IDs (`03a793716358234c4e6b2ed02362b0f84e34de04`, `25500cbf5f50b1f5ce46e11086b900572d9cd04b`).
- Lane revision observed: `0c96332932e66bbaf9cf1c246091d3275a0ab612`.
- Receipt: `census/round-28/records/f4-recheck.tsv`.

## Findings
1. `census/round-27/sources/SHA256SUMS:1-2` — each pin verifies; tag URLs opened this run: `https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c` (“GIO - GLib Input, Output and Streaming Library”) and `https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c` (“gfileutils.c - File utility functions”). Both downloaded files match their pinned SHA-256 and snapshot blob identities.
2. `corpus/SOURCES.md:S152,S210,S211` — GLib records identify the relevant tag paths; row S152 quote: “GLib g_local_file_trash descriptor lifecycle”.

## Attack log
None.
