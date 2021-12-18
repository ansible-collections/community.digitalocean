#!/usr/bin/env bash
set -eu -o pipefail

# We're stacking up tags that look like this:
# k8s:abbba098-372f-4341-a5b1-21cc468970fe
# Need to figure out why; this is a band-aid.

function count() {
  doctl compute tag list | grep '-' | grep -E ' 0' | awk '{print $1}' | wc -l
}

function purge() {
  local count=${1:-10}
  echo "Going to purge up to $count orphaned tags."
  for tag in $(doctl compute tag list | grep '-' | grep ' 0' | awk '{print $1}' | head -${count})
  do
    echo -n "Deleting tag ${tag} ... "
    doctl compute tag delete -f $tag
    echo done.
  done
}

echo There are $(count) orphaned tags, purging them.
purge 10
echo After purging, $(count) orphaned tags remain.
