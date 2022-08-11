#!/usr/bin/env bash
# Generates the badges markdown for the README.md

for test in $(ls tests/integration/targets); do
  echo "![${test}](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/mamercad/81f3b3f50394767aaf986e344dcdf6fd/raw/${test}.json)"
done
