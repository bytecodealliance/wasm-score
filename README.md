# WasmScore

This benchmark is designed to provide a simple, convenient and portable view of the performance of WebAssembly outside the browser on the underlying platform it is run on. It uses a containerized suite of real codes and micros leveraged directly from [Sightglass](https://github.com/bytecodealliance/sightglass) to benchmark the platform and provide a “WasmScore” that is based on a formula that aggregates execution time. In addition, the driver for the benchmark serves as an easy-to-use tool for executing any user determined assortment of Sightglass benchmarks supported by the driver.

One of the most important and challenging aspect of benchmarking is deciding how to interpret the results; should you consider the results to be good or bad? To decide, you really need context on what it is you are trying to achieve, and this often starts with a baseline used to serve as a point of comparison. That baseline could be the execution of that same original source but before some transformation was applied when lowered to WebAssembly, or that baseline could be a modified configuration of the runtime that executes the WebAssembly. In the case of WasmScore, a novel aspect is that for every Wasm real code and micro that is run, WasmScore also executes the native versions of those code compiled from the same high-level source used to generate the Wasm. In this way WasmScore provides a comparison point for the Wasm performance which will ideally be the theoretical upper for the performance of WebAssembly. This feature allows a user to quickly gauge the performance impact of using Wasm instead of using a native compile of the same code when run on that particular platform. It allows developers to see opportunity to improve compilers, or to improve Wasm runtimes, or improve the Wasm spec, or to suggest other solutions (such as Wasi) to address gaps.

Another important feature of WasmScore is simplicity and convenience. Specifically, the user is not expected to have to build the benchmark where they might have to deal with installing or updating dependencies. The user is also not expected contend interpreting the need for turning on or off a myriad of flags and features; to get a platforms WasmScore the user simply runs wasmscore.sh inside the container. Still, while it is meant for the user to simply pull a containerized image and then run the benchmark on the desired platform without worrying, WasmScore can of course be built and then run either within or outside (TODO) the containerized environment. In either case is intended for the compile of all codes to properly utilizes underlying hardware features. To that end, the ideal use case and indeed the target use case for WasmScore is for a quick, simple and consistent cross platform view of Wasm performance. The benchmark especially wants to target usecases and applications that are emerging for Wasm in standalone client and cloud environments. WasmScore is intended to be run on X86-64 and AArch64 Linux platforms.


## Usage

### Use Prebuilt Images

Download and run the latest prebuilt benchmark image:

**X86-64:**
```
docker pull ghcr.io/jlb6740/wasmscore/wasmscore_x86_64:latest
```
```
docker run -it ghcr.io/jlb6740/wasmscore/wasmscore_x86_64:latest /bin/bash /wasmscore.sh
```
**AArch64:**
```
docker pull ghcr.io/jlb6740/wasmscore/wasmscore_aarch64:latest
```
```
docker run -it ghcr.io/jlb6740/wasmscore/wasmscore_aarch64:latest /bin/bash /wasmscore.sh
```

### Build and Run Yourself

To build:
```
./build.sh
```
To run from this local build:
```
docker run -ti wasmscore /bin/bash wasmscore.sh --help
```

To build containerless:
> Not yet supported

### Other Useful Commands

For a detached setup that allows for copying files to the image or entering the container (being mindful of the container name), use the following commands:
```
docker run -ti -d wasmscore /bin/bash
```
```
wasmscore_container_id=$(docker ps | grep -m 1 wasmscore | awk '{ print $1 }')
```
```
docker cp <file> ${wasmscore_container_id}:
```
or
```
docker exec -ti ${wasmscore_container_id} /bin/bash
```
## Example Screenshots



