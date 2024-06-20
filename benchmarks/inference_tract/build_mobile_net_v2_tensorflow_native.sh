#!/usr/bin/env bash

# Build inference_tract benchmark as native shared library (Linux-only).
#
# Usage: ./build_mobile_net_v2_tensorflow_native.sh

(set -x;)
(rm -rf mobile_net_v2_tensorflow_native);
(cp -r mobile_net_v2_tensorflow mobile_net_v2_tensorflow_native);
(cp mobile_net_v2_tensorflow_native.patch mobile_net_v2_tensorflow_native);
(cd mobile_net_v2_tensorflow_native; patch -Np1 -i ./mobile_net_v2_tensorflow_native.patch; mv src/main.rs src/lib.rs; cd -);
(cd mobile_net_v2_tensorflow_native; cargo build --release; cp target/release/libbenchmark.so ../mobile_net_v2_tensorflow_benchmark.so; cd -);
(set +x;)
