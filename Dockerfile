FROM ubuntu:20.04
ARG ARCH
ENV LD_LIBRARY_PATH=/usr/local/lib
ENV PATH=/usr/local/bin:$PATH
CMD ["/bin/bash"]
ENV DEBIAN_FRONTEND="noninteractive" TZ="America"
ARG RUST_VERSION="nightly-2023-04-01"
ARG WASMTIME_REPO="https://github.com/bytecodealliance/wasmtime/"
ARG WASMTIME_COMMIT="1bfe4b5" # v9.0.1
ARG SIGHTGLASS_REPO="https://github.com/bytecodealliance/sightglass.git"
ARG SIGHTGLASS_BRANCH="main"
ARG SIGHTGLASS_COMMIT="e89fce0"

# Get some prerequisites
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	apt-utils build-essential gpg-agent \
	curl ca-certificates wget software-properties-common \
	psmisc lsof git nano zlib1g-dev libedit-dev time yasm \
	libssl-dev pkg-config

# Bionic does not carry a recent enough cmake needed for wamr but upgrading
# to Focal causes other build issues so the straight forward solution is to just
# install a version of cmake that is recent enough from a separate repository
RUN wget -qO - https://apt.kitware.com/keys/kitware-archive-latest.asc | apt-key add -
RUN apt-add-repository 'deb https://apt.kitware.com/ubuntu/ focal main'
RUN apt-get update && apt-get install --yes cmake

# Install wabt
WORKDIR /opt
RUN git clone --recurse-submodules https://github.com/WebAssembly/wabt.git \
	&& cd wabt \
	&& mkdir build \
	&& cd build \
	&& cmake .. \
	&& cmake --build . \
	&& make
ENV PATH=$PATH:/opt/wabt/bin/

# Install rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -sSf | sh -s -- --default-toolchain ${RUST_VERSION} -y
ENV PATH=/root/.cargo/bin:${PATH}

# Install clang
RUN apt-get install -y --no-install-recommends clang

# Install python
RUN apt-get install -y --no-install-recommends python3.8 libpython3.8 python3-distutils python3-pip
RUN python3 -m pip install termgraph \
	&& python3 -m pip install pandas \
	&& python3 -m pip install termcolor \
	&& python3 -m pip install pyyaml

# Install sightglass
WORKDIR /
RUN git clone --recurse-submodules ${SIGHTGLASS_REPO} sightglass
WORKDIR /sightglass
RUN git checkout ${SIGHTGLASS_COMMIT} -b ${SIGHTGLASS_COMMIT}
COPY add_time_metric.diff /sightglass/add_time_metric.diff
RUN git apply add_time_metric.diff
RUN cargo build --release
RUN mkdir results

# Build wasmtime engine for sightglass
WORKDIR /
RUN git clone --recurse-submodule ${WASMTIME_REPO} wasmtime
WORKDIR /wasmtime
RUN git checkout ${WASMTIME_COMMIT} -b ${WASMTIME_COMMIT}
RUN git submodule update --init --recursive
RUN cargo build -p wasmtime-bench-api --release
RUN cp target/release/libwasmtime_bench_api.so /sightglass/engines/wasmtime/libengine.so

# Build native engine for sightglass
WORKDIR /sightglass/engines/native/libengine
RUN cargo build --release
RUN cp target/release/libnative_bench_api.so ../libengine.so

# Replace sightglass benchmarks folder with custom version
WORKDIR /
RUN rm -rf /sightglass/benchmarks
ADD benchmarks /sightglass/benchmarks

# Copy driver/helpers into the image
WORKDIR /
COPY wasmscore.sh /
COPY wasmscore.py /sightglass/wasmscore.py
COPY add_time_metric.diff build.sh requirements.txt Dockerfile wasmscore.py config.inc /sightglass/

# Set default entry and command
ENTRYPOINT ["/bin/bash", "/wasmscore.sh"]
CMD ["-t", "wasmscore"]