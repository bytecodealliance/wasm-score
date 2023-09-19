# WasmScore

## Intro
WasmScore aims to provide a view of WebAssembly performance when executed outside the browser. It uses a containerized suite of benchmarks (both user facing codes and purpose built benchmarks) and leverages [Sightglass](https://github.com/bytecodealliance/sightglass) to benchmark the underline platform. A score based on a formula that aggregates execution time of the suites that make up the "wasmscore" test is provided. In addition to scoring wasm performance, the benchmark is also a tool capable of executing any assortment of other tests, suites, or benchmarks supported by the driver. This WasmScore is work in development.

## Description
One of the most important and challenging aspect of benchmarking is deciding how to interpret the results; should you consider the results to be good or bad? To decide, you really need context on what it is you are trying to achieve, and this often starts with a baseline used to serve as a point of comparison. For example, that baseline could be the execution of that same original source but before some transformation was applied when lowered to WebAssembly, or that baseline could be a modified configuration of the runtime that executes the WebAssembly. In the case of WasmScore, for every Wasm real code and micro that is run, WasmScore also executes the native code compile from the same high-level source used to generate the Wasm to serve as a baseline. In this way WasmScore provides a comparison point for the Wasm performance which will ideally be the theoretical upper for the performance of WebAssembly. This allows a user to quickly gauge the performance impact of using Wasm instead of using a native compile of the same code when run on that particular platform. It allows developers to see opportunity to improve compilers, or to improve Wasm runtimes, or improve the Wasm spec, or to suggest other solutions (such as Wasi) to address gaps.

## Benchmarks
Typically a benchmark reports either the amount of work done over a constant amount of time or it reports the time taken to do a constant amount of work. The benchmarks here all do the later. The initial commit of the benchmarks avaialble have been pulled Sightglass however the benchmarks used with WasmScore come from the local directory here and have no dependency on the benchmarks stored there. However, how the benchmarks here are built and run directly dependent on changes to the external Sightglass repo.

Also, benchmarks are often categorized based on their origin. Two such buckets of benchmarks are (1) codes written with the intent of being user facing (library paths, application use cases) and (2) codes written specifically to benchmark some important/common code construct or platform feature. WasmScore will not necessarily favor either of these benchmarking buckets as both are valuable for the evaluation of standalone Wasm performance depending on what you want to know. The extent that it does will depending on the test run, where currently there is only the primary "wasmscore" test though a simdscore test is in the plans.

## Goals
A standalone benchmark that is:
- Convenient to build and run with easy to interpret results
- Is portable and enables cross-platform comparisons
- Provides a breadth of coverage for current standalone binaries
- Is convenient to analyze

## WasmScore Suites
Any number of test can be created but WasmScore is the initial and default test. It includes a mix of relevant in use codes and targeted benchmarks Wasm performance outside the browser that is broken down into categories:
- App:  [‘Meshoptimizer’]
- Core: [‘Ackermann', ‘Ctype', ‘Fibonacci’]
- Crypto: [‘Base64', ‘Ed25519', ‘Seqhash']
- AI: (Coming)
- Regex: (Coming)

## Plan
Next steps include:
- Improving stability and user experience
- Adding benchmarks to the AI, Regex, and APP suites
- Adding more benchmarks
- Complete the SIMD test
- Publish a list of planned milestone

## Usage

### Use Prebuilt Images

Download and run the latest prebuilt benchmark image:

**X86-64:**
```
docker pull ghcr.io/bytecodealliance/wasm-score/wasmscore_x86_64_linux:latest
```
```
docker run -it ghcr.io/bytecodealliance/wasm-score/wasmscore_x86_64_linux:latest
```
**AArch64:**
```
docker pull ghcr.io/bytecodealliance/wasm-score/wasmscore_aarch64_linux:latest
```
```
docker run -it ghcr.io/bytecodealliance/wasm-score/wasmscore_aarch64_linux:latest
```

### Build and Run Yourself

To build:
```
./build.sh
```
To run from this local build:
```
docker run -ti wasmscore <--help>
```

To build containerless:
> Not yet supported

## Screenshots

WasmScore example output:

<img src="https://github.com/bytecodealliance/wasm-score/blob/main/docs/assets/Screenshot-WasmScore.png" height="60%" width="60%" >