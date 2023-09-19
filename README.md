# WasmScore

## Intro
WasmScore aims to provide a view of WebAssembly performance when executed outside the browser. It uses a containerized suite of codes and leverages [Sightglass](https://github.com/bytecodealliance/sightglass) to benchmark the underline platform. After running, an execution score and an efficiency score is provided for scoring the performance of Wasm on the underlying platform. In addition to scoring wasm performance, the benchmark is also a tool capable of executing any assortment of indivdual tests, suites, or benchmarks supported by the driver. WasmScore is work in development.

## Description
One of the most important and challenging aspect of benchmarking is deciding how to interpret the results; should you consider the results to be good or bad? To decide, you really need a baseline to serve as a point of comparison where this baseline depends on what it is you're trying to achieve. For example, that baseline could that same original source but before some code transformation was applied, or that baseline could be a modified configuration of the runtime that executes the WebAssembly. In the case of WasmScore (and specifically the wasmscore test), for every Wasm real code and micro that is run, WasmScore also executes the native code compile from the same high-level source used to generate the Wasm, to serve as a baseline. In this way WasmScore provides native execution of codes to serve as a comparison point for the Wasm performance where this baseline can be seen as the theoretical upper-bound for the performance of WebAssembly. This allows a user to quickly gauge the performance impact (hit) when using Wasm instead of using a native compile of the same code. It also allows developers to find opportunities to improve compilers, or to improve Wasm runtimes, or improve the Wasm spec, or to suggest other solutions (such as Wasi) to address gaps.

## Benchmarks
Typically a benchmark reports either the amount of work done over a constant amount of time or it reports the time taken to do a constant amount of work. The benchmarks here all do the later. The initial commit of the benchmarks available have been pulled from Sightglass however the benchmarks used with WasmScore come from the local directory here and have no dependency on the benchmarks stored in the Sightglass repo. However, how the benchmarks here are built and run do directly dependent on changes to the external Sightglass repo.

Benchmarks are often categorized based on their purpose and origin. Two such buckets are (1) codes written with the original intent of being user facing (hot paths in library codes, a typical application usage, etc) and (2) codes written specifically to target benchmarking some important or commonly used code construct or platform component. WasmScore does not aim to favor either of these benchmarking buckets as both are valuable in the evaluation of standalone Wasm performance depending on what you want to test and what you are trying to achieve.

## WasmScore principles
WasmScore aims to serve as a standalone Wasm benchmark and benchmarking framework that:
- Is convenient to build and run with useful and easy to interpret results.
- Is portable, enabling cross-platform comparisons.
- Provides a breadth of coverage for typical current standalone use cases and expected future use cases.
- Can be executed in a way that is convenient to analyze.

## WasmScore Tests
Any number of test can be created but "wasmscore" is the initial and default test. It includes a mix of relevant in use codes and platform targeted benchmarks for testing Wasm performance outside the browser. The test is a collection of several subtests (also referred to as suites):

### wasmscore (default):
- App:  [‘Meshoptimizer’]
- Core: [‘Ackermann', ‘Ctype', ‘Fibonacci’]
- Crypto: [‘Base64', ‘Ed25519', ‘Seqhash']
- AI: (Coming)
- Regex: (Coming)

## 2023 Q4 Goals
Next steps include:
- Improving stability and user experience
- Adding benchmarks to the AI, Regex, and App suites
- Adding more benchmarks
- Complete the "simdscore" test
- Publish a list of planned milestone with corresponding releases

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