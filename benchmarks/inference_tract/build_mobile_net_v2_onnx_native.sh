#!/usr/bin/env bash

# Build inference_tract benchmark as a native shared library (Linux-only).
#
# Usage: ./build_mobile_net_v2_onnx_native.sh

(set -x;)
(rm -rf mobile_net_v2_onnx_native);
(cp -r mobile_net_v2_onnx mobile_net_v2_onnx_native);
(cp mobile_net_v2_onnx_native.patch mobile_net_v2_onnx_native);
(cd mobile_net_v2_onnx_native; patch -Np1 -i ./mobile_net_v2_onnx_native.patch; mv src/main.rs src/lib.rs; cd -);
(cd mobile_net_v2_onnx_native; cargo build --release; cp target/release/libbenchmark.so ../mobile_net_v2_onnx_benchmark.so; cd -);
(set +x;)
