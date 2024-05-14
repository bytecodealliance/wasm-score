FROM rust:1.75 AS builder
RUN rustup target add wasm32-wasi
RUN mkdir /benchmark
WORKDIR /usr/src

# Compile mobile_net_v2_onnx
ADD mobile_net_v2_onnx rust-benchmark
WORKDIR /usr/src/rust-benchmark
ENV CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse
RUN (cd mobile_net_v2_onnx; cargo build --release --target wasm32-wasi)
RUN cp target/wasm32-wasi/release/*benchmark.wasm /benchmark/mobile_net_v2_onnx_benchmark.wasm
RUN rm -rf rust-benchmark


# Compile mobile_net_v2_tensorflow
ADD mobile_net_v2_tensorflow rust-benchmark
WORKDIR /usr/src/rust-benchmark
ENV CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse
RUN (cd mobile_net_v2_tensorflow; cargo build --release --target wasm32-wasi)
RUN cp target/wasm32-wasi/release/*benchmark.wasm /benchmark/mobile_net_v2_tensorflow_benchmark.wasm
RUN rm -rf rust-benchmark