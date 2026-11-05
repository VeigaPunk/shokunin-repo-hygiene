#!/bin/sh
# fsmonitor hook protocol v2: consume stdin, emit a token and zero changed paths
cat >/dev/null
printf 'tok\000'
