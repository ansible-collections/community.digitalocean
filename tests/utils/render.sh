#!/usr/bin/env bash

# Renders tests/integration/integration_config.yml

set -e
set -o pipefail
set -u

function main()
{
  # shellcheck disable=SC2155
  readonly template="$1"; shift
  # shellcheck disable=SC2155
  readonly content="$(cat "$template")"

  eval "echo \"$content\""
}

main "$@"
