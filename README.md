# WasmScore

## Intro
WasmScore aims to benchmark platform performance when executing WebAssembly outside the browser. It leverages [Sightglass](https://github.com/bytecodealliance/sightglass) to run benchmarks and measure performance and then summarizes these results as both an execution score and an efficiency score. In addition to providing a general default scores for the platform, the benchmark is also capable of executing other individual or specialized tests, suites, or individual benchmarks supported by the driver. WasmScore development is still at early stages and is work in development.

## Description
A basic part of benchmarking is interpreting the results; should you consider the results to be good or bad? To decide, you need a baseline (or goal) to serve as a point of comparison. For example, that baseline could be a measure of the performance before some code optimization was applied or before some configuration change was made to the runtime. In the case of WasmScore (specifically the default score) that baseline is the execution of the native code compiled from the same high-level source used to generate the Wasm. The native execution of codes serves as the expected upper-bound for the performance of WebAssembly. This both informs the performance impact of targeting Wasm instead of native for compiled code and it also allows developers to find opportunities to improve compilers, to improve Wasm runtimes, to improve the Wasm spec, and/or to suggest other solutions (such as Wasi) to address gaps.

## Benchmarks
Typically a benchmark reports either the amount of work done over a constant amount of time or it reports the time taken to do a constant amount of work. The benchmarks here all do the later. The initial commit of the benchmarks available are pulled directly from Sightglass. How the benchmarks stored here are built and run depends on the Sightglass revision used.

Benchmarks are often categorized based on their purpose and origin. Two example buckets include (1) codes written with the original intent of being user facing and (2) codes written specifically to target benchmarking some important or commonly used code construct or platform component. WasmScore does not aim to favor one of these over the other as both are valuable and relevant in the evaluation of standalone Wasm depending on what you are trying to learn.

## WasmScore Principles
WasmScore aims to:
- Be convenient to build and run with useful and easy to interpret results.
- Be portable, enabling cross-platform comparisons.
- Inform a wide coverage of typical and interesting standalone use cases.
- Be convenient to analyze with common perf tools.

## WasmScore Tests
"wasmscore" is the initial and default test. It includes a mix of benchmarks for testing Wasm performance outside the browser. The test is a collection of several subtests:

### wasmscore (default):
- App:  [‘meshoptimizer’]
- Core: [‘ackermann', ‘ctype', ‘fibonacci’]
- Crypto: [‘base64', ‘ed25519', ‘seqhash']
- AI: ['tract_mobilenet_v2_onnx', 'tract_mobilenet_v2_tensorflow']
- Regex: (Coming)

## 2024 Q3 Goals
Next steps include:
- Improving stability and user experience
- Adding benchmarks to the AI, Regex, and App suites
- Adding more benchmarks (including w/native build support)
- Publish a list of planned milestone with corresponding releases

## Usage

### Use Prebuilt Images

Download and run the latest prebuilt benchmark image:

**X86-64:**
```
docker run -it ghcr.io/bytecodealliance/wasm-score/wasmscore_x86_64_linux:latest
```
**AArch64:**
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