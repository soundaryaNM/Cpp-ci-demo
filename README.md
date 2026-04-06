# C++ Calculator — CI/CD Demo

<!-- REPLACE soundaryaNM/cpp-ci-demo with your actual GitHub username/repo -->

[![CI/CD Pipeline](https://github.com/soundaryaNM/cpp-ci-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/soundaryaNM/cpp-ci-demo/actions/workflows/ci.yml)
[![Build Status](https://github.com/soundaryaNM/cpp-ci-demo/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/soundaryaNM/cpp-ci-demo/actions/workflows/ci.yml)
[![Docker Image](https://ghcr.io/soundaryaNM/cpp-ci-demo/cpp-calculator)](https://github.com/soundaryaNM/cpp-ci-demo/pkgs/container/cpp-ci-demo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![C++17](https://img.shields.io/badge/C%2B%2B-17-blue.svg)](https://en.cppreference.com/w/cpp/17)
[![CMake](https://img.shields.io/badge/CMake-3.16+-green.svg)](https://cmake.org)

A demonstration project showing a **complete C++ CI/CD pipeline** using:

- 🔨 CMake + Ninja build system
- 🧪 Google Test framework
- 🐳 Docker (multi-stage builds)
- ⚙️ GitHub Actions (build → test → coverage → Docker → release)
- 📊 Code coverage with gcovr

---

## Project Structure

```
cpp-ci-demo/
├── include/
│   └── calculator.h          # Public API header
├── src/
│   ├── calculator.cpp        # Library implementation
│   └── main.cpp              # Demo executable
├── tests/
│   └── test_calculator.cpp   # Google Test unit tests
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions pipeline
├── .vscode/                  # VS Code settings, tasks, launch configs
├── scripts/
│   └── build.sh              # Local build helper
├── CMakeLists.txt
└── Dockerfile                # Multi-stage Docker build
```

---

## Quick Start (Local)

### Prerequisites

- CMake ≥ 3.16
- GCC ≥ 9 or Clang ≥ 10
- Ninja (`sudo apt install ninja-build`)
- Git (for FetchContent to download GoogleTest)

### Build & Test

```bash
# Clone
git clone https://github.com/soundaryaNM/cpp-ci-demo.git
cd cpp-ci-demo

# Build + run tests (one command)
./scripts/build.sh

# OR manually:
cmake -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON -G Ninja
cmake --build build --parallel
cd build && ctest --output-on-failure
```

### Run the app

```bash
./build/bin/calculator_app
```

### Coverage report

```bash
./scripts/build.sh coverage
# Open coverage-report/index.html in your browser
```

---

## Docker

### Build locally

```bash
# Production runtime image
docker build --target runtime -t cpp-calculator:local .

# Run it
docker run --rm cpp-calculator:local
```

### Pull from GitHub Container Registry

```bash
docker pull ghcr.io/soundaryaNM/cpp-ci-demo:main
docker run --rm ghcr.io/soundaryaNM/cpp-ci-demo:main
```

---

## CI/CD Pipeline

The pipeline has **5 jobs** that run automatically on every push:

| Job | Trigger | What it does |
|-----|---------|-------------|
| `build-and-test` | Every push/PR | Builds + runs tests, uploads JUnit XML report |
| `coverage` | After tests pass | Debug build with gcovr coverage report |
| `multi-platform` | After tests pass | Matrix build: Ubuntu, macOS, Windows |
| `docker` | After tests pass | Builds + pushes image to GHCR |
| `release` | On `v*` tags only | Packages binary, creates GitHub Release |

### Trigger a release

```bash
git tag v1.0.0
git push origin v1.0.0
# Pipeline creates a release with binary + test results automatically
```

---

## VS Code Setup

1. Open the folder in VS Code
2. Install recommended extensions (prompted automatically via `.vscode/extensions.json`)
3. CMake Tools will auto-configure on open
4. Use **Ctrl+Shift+B** to build, or run the **"Run Tests"** task

---

## License

MIT — see [LICENSE](LICENSE)
