#!/usr/bin/env bash
# build.sh — local build helper
# Usage: ./scripts/build.sh [release|coverage|clean]
set -euo pipefail

MODE=${1:-release}
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

case "$MODE" in
  release)
    echo "Configuring (Release)..."
    cmake -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON -G Ninja
    cmake --build build --parallel
    echo "Running tests..."
    cd build && ctest --output-on-failure
    ;;
  coverage)
    echo "Configuring (Coverage)..."
    cmake -B build-cov -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTS=ON -DBUILD_COVERAGE=ON -G Ninja
    cmake --build build-cov --parallel
    cd build-cov && ctest --output-on-failure || true
    cd "$ROOT"
    mkdir -p coverage-report
    gcovr --root . --filter src/ --filter include/ \
      --html-details coverage-report/index.html \
      --xml coverage-report/coverage.xml --txt build-cov/
    echo "Coverage report: coverage-report/index.html"
    ;;
  clean)
    rm -rf build build-cov coverage-report
    echo "Clean done"
    ;;
  *)
    echo "Usage: $0 [release|coverage|clean]"
    exit 1
    ;;
esac
echo "Done."
