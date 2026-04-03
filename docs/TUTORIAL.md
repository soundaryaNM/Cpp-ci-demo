# Complete Tutorial: C++ CI/CD Pipeline from Scratch

## Table of Contents
1. [System Setup](#1-system-setup)
2. [VS Code Setup](#2-vs-code-setup)
3. [Project Creation](#3-project-creation)
4. [Writing C++ Code](#4-writing-c-code)
5. [Setting up CMake](#5-setting-up-cmake)
6. [Google Test](#6-google-test)
7. [Building Locally](#7-building-locally)
8. [Docker Setup](#8-docker-setup)
9. [GitHub Repository Setup](#9-github-repository-setup)
10. [GitHub Actions CI Pipeline](#10-github-actions-ci-pipeline)
11. [Build Badges](#11-build-badges)
12. [Push Docker Image to GHCR](#12-push-docker-image-to-ghcr)
13. [Automatic Release Artifacts](#13-automatic-release-artifacts)
14. [End-to-End Demo Walkthrough](#14-end-to-end-demo-walkthrough)

---

## 1. System Setup

### Install tools on Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    git \
    gcovr \
    lcov \
    docker.io
```

### Verify versions
```bash
g++ --version       # should be >= 9
cmake --version     # should be >= 3.16
ninja --version
docker --version
git --version
```

### macOS
```bash
xcode-select --install
brew install cmake ninja gcovr
brew install --cask docker
```

### Windows
- Install [Visual Studio 2022](https://visualstudio.microsoft.com/) with "Desktop development with C++"
- Install [CMake](https://cmake.org/download/)
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Install [Git for Windows](https://git-scm.com/)

---

## 2. VS Code Setup

### Install VS Code
Download from: https://code.visualstudio.com/

### Required Extensions (install via Ctrl+Shift+X)

| Extension | Publisher | Purpose |
|-----------|-----------|---------|
| C/C++ | Microsoft | IntelliSense, debugging |
| CMake Tools | Microsoft | CMake integration |
| CMake | twxs | CMake syntax highlighting |
| Docker | Microsoft | Dockerfile support |
| GitHub Actions | GitHub | Workflow file editing |
| GitLens | GitKraken | Git history |
| Remote - Containers | Microsoft | Dev containers |

These are auto-prompted via `.vscode/extensions.json` in the project.

### Key VS Code shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+B` | Run default build task |
| `F5` | Start debugger |
| `Ctrl+Shift+P` | Command palette |
| `Ctrl+`` ` | Open integrated terminal |

---

## 3. Project Creation

### Folder structure
```bash
mkdir cpp-ci-demo && cd cpp-ci-demo
mkdir -p src include tests .github/workflows .vscode scripts docs
git init
code .
```

### Final structure
```
cpp-ci-demo/
├── include/
│   └── calculator.h          # Public API
├── src/
│   ├── calculator.cpp        # Implementation
│   └── main.cpp              # Demo executable
├── tests/
│   └── test_calculator.cpp   # Google Test suite
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions (5 jobs)
├── .vscode/
│   ├── settings.json         # CMake auto-configure
│   ├── tasks.json            # Build/test tasks
│   ├── launch.json           # Debug configs
│   └── extensions.json       # Recommended extensions
├── scripts/
│   └── build.sh              # Local helper script
├── docs/
│   └── TUTORIAL.md           # This file
├── CMakeLists.txt
├── Dockerfile                # Multi-stage build
├── .dockerignore
├── .gitignore
└── README.md                 # With build badges
```

---

## 4. Writing C++ Code

### Why library + separate main?
Separating business logic from `main()` is best practice because:
- Tests link against the **library** directly — no main() interference
- The library can be reused in other executables
- Cleaner architecture

### The three layers
```
include/calculator.h    ← Public interface (what callers see)
src/calculator.cpp      ← Implementation (the actual logic)
src/main.cpp            ← Demo program (links the library)
tests/test_calculator.cpp ← Unit tests (also links the library)
```

---

## 5. Setting up CMake

### What is CMake?
CMake is a **meta build system** — it doesn't compile code itself. Instead, it generates native build files for Ninja, Make, or Visual Studio based on your `CMakeLists.txt`.

### Key CMake concepts

```cmake
# Create a static library from source files
add_library(calculator_lib STATIC src/calculator.cpp)

# Tell dependents where to find headers
target_include_directories(calculator_lib PUBLIC include)

# Create an executable
add_executable(calculator_app src/main.cpp)

# Link the executable against our library
target_link_libraries(calculator_app PRIVATE calculator_lib)
```

### FetchContent — auto-download GoogleTest
```cmake
include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.14.0          # pinned version
)
FetchContent_MakeAvailable(googletest)
# GoogleTest is now available as GTest::gtest_main
```
No manual installation needed — CMake downloads it on first configure.

### Build commands
```bash
# Configure: generate Ninja build files in build/
cmake -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON -G Ninja

# Build: compile everything in parallel
cmake --build build --parallel

# Test
cd build && ctest --output-on-failure

# Install binary to /usr/local/bin
cmake --install build --prefix /usr/local
```

### CMake build types
| Type | Flags | When to use |
|------|-------|-------------|
| `Release` | `-O3 -DNDEBUG` | Production, benchmarks |
| `Debug` | `-g -O0` | Step-through debugging |
| `RelWithDebInfo` | `-O2 -g` | Profiling |

---

## 6. Google Test

### Test anatomy
```cpp
// TEST(TestSuiteName, TestCaseName)
TEST(AddTest, PositiveNumbers) {
    EXPECT_DOUBLE_EQ(Calculator::add(2, 3), 5);
}
TEST(AddTest, DivideByZero) {
    EXPECT_THROW(Calculator::divide(5, 0), std::invalid_argument);
}
```

### Matcher reference
| Matcher | Checks |
|---------|--------|
| `EXPECT_EQ(a, b)` | a == b (integers, strings) |
| `EXPECT_DOUBLE_EQ(a, b)` | float equality (ULP-based) |
| `EXPECT_NEAR(a, b, eps)` | \|a-b\| < eps |
| `EXPECT_TRUE(cond)` | condition is true |
| `EXPECT_THROW(expr, T)` | expr throws exception of type T |
| `ASSERT_*` | same but stops test on first failure |

### EXPECT vs ASSERT
- `EXPECT_*` — test continues even if this check fails
- `ASSERT_*` — test stops immediately on failure (use when later code would crash)

### Running tests
```bash
cd build

ctest --output-on-failure                          # standard run
ctest -R "AddTest"                                 # filter by name
ctest -V                                           # verbose (shows gtest output)
ctest --output-junit test-results/junit.xml        # CI XML format

# Or run the test binary directly:
./bin/test_calculator --gtest_color=yes
./bin/test_calculator --gtest_filter="Add*"        # filter suites
./bin/test_calculator --gtest_list_tests           # list all tests
```

---

## 7. Building Locally

### One command
```bash
./scripts/build.sh            # Release build + all tests
./scripts/build.sh coverage   # Debug + gcovr HTML report
./scripts/build.sh clean      # Remove all build artifacts
```

### Step by step (manual)
```bash
# 1. Configure
cmake -B build -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTS=ON -G Ninja

# 2. Build
cmake --build build --parallel

# 3. Test (with output on failure)
cd build && ctest --output-on-failure

# 4. Run the demo app
./bin/calculator_app

# 5. Run tests directly (more verbose)
./bin/test_calculator --gtest_color=yes
```

### VS Code workflow
1. Open VS Code in the project folder
2. CMake Tools auto-configures (or Ctrl+Shift+P → "CMake: Configure")
3. `Ctrl+Shift+B` → "CMake Build"
4. Ctrl+Shift+P → "Tasks: Run Task" → "Run Tests"

---

## 8. Docker Setup

### Why Docker in CI?
Docker guarantees the build environment is **byte-for-byte identical** across:
- Your laptop
- Your colleague's machine
- GitHub's CI servers
- Production servers

### Multi-stage build explained

```
┌─────────────────────────────────────────────────┐
│ Stage 1: builder (ubuntu:22.04 + all dev tools) │
│   - cmake, ninja, gcc, gcovr installed          │
│   - Source code copied in                       │
│   - cmake configure + build                     │
│   - ctest runs → JUnit XML output               │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│ Stage 2: coverage (extends builder)             │
│   - Rebuild with --coverage flags               │
│   - gcovr generates HTML + XML report           │
└─────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│ Stage 3: runtime  ← THIS IS WHAT GETS SHIPPED  │
│   - Fresh ubuntu:22.04 (NO build tools!)        │
│   - COPY only the binary from Stage 1           │
│   - Non-root user (security best practice)      │
│   - Final size: ~80MB vs ~1.2GB                 │
└─────────────────────────────────────────────────┘
```

### Docker commands
```bash
# Build only the lightweight runtime image
docker build --target runtime -t cpp-calculator:local .

# Run it
docker run --rm cpp-calculator:local

# Build the builder stage (useful to debug CI failures locally)
docker build --target builder -t cpp-calculator:builder .

# Run tests inside Docker
docker run --rm cpp-calculator:builder \
  sh -c "cd /app/build && ctest --output-on-failure"

# Check final image size
docker images cpp-calculator:local
```

---

## 9. GitHub Repository Setup

### Create the repo
1. Go to **https://github.com/new**
2. Repository name: `cpp-ci-demo`
3. Set to **Public** (badges work without extra tokens)
4. Do NOT tick "Add README" — you have your own
5. Click **"Create repository"**

### Push your code
```bash
git add .
git commit -m "feat: initial C++ calculator with CI/CD pipeline"
git branch -M main
git remote add origin https://github.com/YOURNAME/cpp-ci-demo.git
git push -u origin main
```

### Enable workflow write permissions (for Docker push)
1. Repo → **Settings** → **Actions** → **General**
2. Scroll to **"Workflow permissions"**
3. Select **"Read and write permissions"**
4. Click **Save**

---

## 10. GitHub Actions CI Pipeline

### How it triggers
Every `git push` to GitHub checks for `.github/workflows/*.yml` and runs matching workflows automatically on GitHub-hosted VMs.

### Job dependency graph
```
[push to main / PR]
        │
        ▼
  build-and-test ──────────────────────────────────┐
        │                                           │
        ├──► coverage                               │
        ├──► multi-platform (Ubuntu/macOS/Windows)  │
        └──► docker ───────────────────────────────►├──► release
                                                    │   (only on v* tags)
                                                    └───────────────────
```

### Key pipeline features

**Test reporting** — results appear as a visual table in the PR:
```yaml
- uses: dorny/test-reporter@v1
  with:
    name: "GTest Results"
    path: "build/test-results/*.xml"
    reporter: java-junit
```

**Build matrix** — tests on 3 OSes in parallel:
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
```

**Docker layer caching** — speeds up image builds:
```yaml
cache-from: type=gha
cache-to:   type=gha,mode=max
```

### View pipeline results
1. GitHub repo → **"Actions"** tab
2. Click any workflow run
3. Each job is shown with pass/fail
4. Click a job → expand steps → view logs

---

## 11. Build Badges

### Badge URL format (GitHub Actions)
```
https://github.com/OWNER/REPO/actions/workflows/FILENAME.yml/badge.svg
```

### Copy-paste for your README
```markdown
[![CI/CD Pipeline](https://github.com/yourname/cpp-ci-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/yourname/cpp-ci-demo/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![C++17](https://img.shields.io/badge/C%2B%2B-17-blue.svg)](https://en.cppreference.com/)
```

**IMPORTANT:** Replace `yourname` with your actual GitHub username.

### Branch-specific badge
```markdown
![main](https://github.com/yourname/repo/actions/workflows/ci.yml/badge.svg?branch=main)
![develop](https://github.com/yourname/repo/actions/workflows/ci.yml/badge.svg?branch=develop)
```

### Custom badges via shields.io
Visit **https://shields.io** to build any badge:
- Coverage percentage
- Latest release version
- Docker image size
- Open issues count

---

## 12. Push Docker Image to GHCR

### Authentication in CI
GitHub automatically provides a `GITHUB_TOKEN` secret in every workflow run. No manual setup needed:

```yaml
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}  # auto-injected by GitHub
```

### Automatic image tags generated
```
ghcr.io/yourname/cpp-ci-demo:main          ← branch push
ghcr.io/yourname/cpp-ci-demo:sha-a3f2b19   ← commit SHA
ghcr.io/yourname/cpp-ci-demo:v1.2.3        ← version tag
ghcr.io/yourname/cpp-ci-demo:1.2           ← major.minor from tag
```

### Pull and use the image
```bash
docker pull ghcr.io/yourname/cpp-ci-demo:main
docker run --rm ghcr.io/yourname/cpp-ci-demo:main
```

### Make the package public
By default packages are private. To make public:
1. Your profile → **Packages** tab
2. Click the package
3. **Package Settings** → Change visibility → **Public**

---

## 13. Automatic Release Artifacts

### What triggers a release?
Only pushes of version tags matching `v*.*.*`:
```bash
git tag v1.0.0
git push origin v1.0.0
```

### What gets published automatically
| File | Description |
|------|-------------|
| `calculator-linux-x86_64.tar.gz` | Compiled binary tarball |
| `SHA256SUMS.txt` | Checksums for verification |
| `test-results/junit-results.xml` | Test evidence |

### Semantic versioning guide
```
v MAJOR . MINOR . PATCH
  │        │       └── Bug fixes (v1.0.1)
  │        └────────── New features, backward compatible (v1.1.0)
  └─────────────────── Breaking changes (v2.0.0)

Pre-release (auto-marked as pre-release in GitHub):
  v2.0.0-alpha.1
  v2.0.0-beta.2
  v1.5.0-rc.1
```

### Full release workflow
```bash
# 1. Make your changes and push
git add .
git commit -m "feat: add modulo function"
git push origin main

# 2. Wait for CI to pass (check Actions tab)

# 3. Tag and push the release
git tag v1.1.0
git push origin v1.1.0

# 4. GitHub Actions automatically:
#    - Builds the Release binary
#    - Creates calculator-linux-x86_64.tar.gz
#    - Generates SHA256SUMS.txt
#    - Pushes Docker image with v1.1.0 tag
#    - Creates GitHub Release with all files attached
```

---

## 14. End-to-End Demo Walkthrough

### Complete flow from zero to running pipeline

```bash
# ── PHASE 1: Setup ────────────────────────────────────────────
git clone https://github.com/yourname/cpp-ci-demo.git
cd cpp-ci-demo
code .
# VS Code prompts to install recommended extensions → install all

# ── PHASE 2: Build locally ────────────────────────────────────
./scripts/build.sh
# Expected output:
# -- Configuring done
# -- Build files have been written to: .../build
# [1/3] Building CXX object ...
# [100%] Linked CXX executable test_calculator
# Test project .../build
#     Start 1: AddTest.PositiveNumbers
# 1/20 Test #1: AddTest.PositiveNumbers ............ Passed
# ...
# 100% tests passed, 0 tests failed

# ── PHASE 3: Docker locally ───────────────────────────────────
docker build --target runtime -t cpp-calculator:local .
docker run --rm cpp-calculator:local
# === C++ Calculator Demo ===
# add(3, 4)        = 7
# ...

# ── PHASE 4: Push to GitHub → CI triggers ────────────────────
git add .
git commit -m "initial commit"
git push origin main
# → Go to GitHub Actions tab and watch the 5 jobs run

# ── PHASE 5: Trigger a release ────────────────────────────────
git tag v1.0.0
git push origin v1.0.0
# → Release job runs → artifacts appear at:
#   https://github.com/yourname/cpp-ci-demo/releases
```

### What to show in a demo
1. **Show the README** — live badges turn green as jobs pass
2. **Show Actions tab** — jobs running in real-time
3. **Click a job** — show the test report table (dorny/test-reporter)
4. **Show Packages tab** — Docker image auto-published
5. **Show Releases tab** — binary + test results auto-attached
6. **Break a test intentionally**, push → show the badge turn red

---

## Troubleshooting

### GoogleTest not found
FetchContent needs internet on first configure:
```bash
# If behind a proxy:
export https_proxy=http://proxy:port
cmake -B build -DBUILD_TESTS=ON
```

### Badge shows "no status"
- The workflow must have run at least once on `main`
- Double-check the filename in the badge URL matches exactly

### Docker push: "denied: permission_denied"
1. Settings → Actions → General
2. Workflow permissions → Read and write → Save

### Tests pass locally but fail in CI
Common reasons:
- Absolute paths in tests (use relative)
- Missing `#include` (be explicit in headers)
- Float precision differences (prefer `EXPECT_NEAR`)
- Timezone/locale differences

### Release job doesn't run
Verify the tag matches the pattern:
```bash
git tag --list           # check existing tags
git tag v1.0.0           # must start with 'v'
git push origin v1.0.0   # push the tag explicitly
```

---

## Summary: What You've Built

| Feature | How |
|---------|-----|
| Auto build on push | GitHub Actions `on: push` trigger |
| Unit tests | Google Test + ctest |
| Test report in PR | dorny/test-reporter |
| Multi-OS builds | Strategy matrix |
| Code coverage | gcovr + Debug build |
| Docker image | Multi-stage Dockerfile |
| GHCR push | docker/build-push-action + GITHUB_TOKEN |
| Build badges | GitHub Actions badge URL in README |
| Release artifacts | softprops/action-gh-release on v* tags |

