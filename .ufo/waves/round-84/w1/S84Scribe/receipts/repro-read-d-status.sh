#!/bin/bash
# Minimal reproducer: the identity re-read's exit status decides whether a descendant is signalled.
# A NUL-delimited read of a file with no NUL returns 1 (EOF) even though it read the whole content.
f=/proc/self/stat
now=""
{ IFS= read -r -d '' now < "$f"; } 2>/dev/null || { echo "SKIPPED: read -d '' returned non-zero (content was read: ${#now} bytes)"; exit 3; }
echo "PROCEEDED: content=${#now}"
