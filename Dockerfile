# Multi-Stage Dockerfile for C++ CI Pipeline

# ── Stage 1: Builder ─────────────────────────────────────────────
FROM ubuntu:22.04 AS builder

LABEL maintainer="your-email@example.com"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential cmake ninja-build git lcov gcovr ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY CMakeLists.txt .
COPY src/     src/
COPY include/ include/
COPY tests/   tests/

RUN cmake -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON -G Ninja
RUN cmake --build build --parallel
RUN cd build && ctest --output-on-failure \
    --output-junit test-results/junit-results.xml || true

# ── Stage 2: Coverage ────────────────────────────────────────────
FROM builder AS coverage

RUN cmake -B build-cov -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTS=ON -DBUILD_COVERAGE=ON -G Ninja
RUN cmake --build build-cov --parallel
RUN cd build-cov && ctest --output-on-failure || true
RUN gcovr --root /app --filter /app/src --filter /app/include \
    --html-details /app/coverage-report/index.html \
    --xml /app/coverage-report/coverage.xml --txt build-cov/

# ── Stage 3: Runtime (minimal production image) ──────────────────
FROM ubuntu:22.04 AS runtime

LABEL description="C++ Calculator - Production Runtime"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash appuser
USER appuser
WORKDIR /home/appuser

COPY --from=builder /app/build/bin/calculator_app ./calculator

ENTRYPOINT ["./calculator"]
