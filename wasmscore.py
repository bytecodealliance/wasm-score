#!/usr/bin/python3.8

import os
import datetime
from datetime import datetime
import argparse
import collections
import textwrap
import pandas as pd
import numpy as np
from termcolor import colored
import yaml

# Command line options
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent(
        """
            available engines:      Wasmtime (default), Native
            available tests:        WasmScore (default)
            available suites:       See options above
            available benchmarks:   See options above

            example usage: ./wasmscore.sh -p shootout -r wasmtime_app
         """
    ),
)
parser.add_argument(
    "-r", "--runtime", nargs="+", help="Runtime to use for performance runs"
)
parser.add_argument("-b", "--benchmarks", nargs="+", help="Benchmarks to run")
parser.add_argument(
    "-s",
    "--suites",
    nargs="+",
    help="Suite to run (ignored if individual benchmark(s) specified)",
)
parser.add_argument(
    "-n",
    "--native",
    action="store_true",
    help="Will also run the benchmark natively. Not all benchmarks supported",
)
parser.add_argument(
    "-l",
    "--list",
    action="store_true",
    help="List all available suites and individual benchmarks to run",
)

# Global Variables
CWD = os.getcwd()
args = parser.parse_args()
ARGS_DICT = vars(args)
DATE_TIME = datetime.now().strftime("%Y-%m-%d")

# Dictionaries
# FIXME: Scan predefined directory to populate
perf_benchmarks = {
    "blake3-scalar": "blake3-scalar",
    "blake3-simd": "blake3-simd",
    "bzip2": "bz2",
    "meshoptimizer": "meshoptimizer",
    "ackermann": "shootout-ackermann",
    #
    # https://base64.guru/learn/base64-algorithm/encode
    "base64": "shootout-base64",
    "ctype": "shootout-ctype",
    "ed25519": "shootout-ed25519",
    "fibonacci": "shootout-fib2",
    "gimli": "shootout-gimli",
    "heapsort": "shootout-heapsort",
    "keccak": "shootout-keccak",
    "matrix": "shootout-matrix",
    "memmove": "shootout-memmove",
    "minicsv": "shootout-minicsv",
    "nested-loop": "shootout-nested-loop",
    "random": "shootout-random",
    "ratelimit": "shootout-ratelimit",
    "seqhash": "shootout-seqhash",
    "sieve": "shootout-sieve",
    "spidermonkey": "spidermonkey",
    "switch": "shootout-switch",
    "xblabla20": "shootout-xblabla20",
    "xchacha20": "shootout-xchacha20",
}

perf_suites = {
    "applications": ["meshoptimizer"],
    "applications-score": ["meshoptimizer"],
    "core-score": ["base64", "blake3-scalar", "ctype", "fibonacci", "bzip2"],
    "shootout": ["base64", "ctype", "fibonacci", "gimli", "heapsort", "keccak", "matrix", "memmove", "minicsv", "nested-loop", "random", "ratelimit", "seqhash", "sieve", "switch", "xblahblah20", "xchacha20"],
    "simd-score": ["blake3-simd", "hex-simd", "intgemm-simd"],
}

perf_tests = {
    "wasmscore": ["applications-score", "core-score", "simd-score"]
}

# Appended by build_dics()
suite_summary = collections.OrderedDict()

# Build dictionaries based on cmd flags and directory file structure
def run_benchmarks(benchmark, run_native=False):

    execution_native = 0
    if run_native:
        print("")
        print("Collecting Native ({}).".format(benchmark))

        benchmark_dir = "/sightglass/benchmarks/" + perf_benchmarks[benchmark]
        wasm_benchmark_path = (
            "/sightglass/benchmarks/" + perf_benchmarks[benchmark] + "/benchmark.wasm"
        )
        results_path = (
            "/sightglass/results/" + perf_benchmarks[benchmark] + "_native_results.csv"
        )
        results_summarized_path = (
            "/sightglass/results/"
            + perf_benchmarks[benchmark]
            + "_results_native_summarized.csv"
        )
        results_summarized_transposed_path = (
            "/sightglass/results/"
            + perf_benchmarks[benchmark]
            + "_results_native_summarized_transposed.csv"
        )
        termgraph_title = "{} native time(ns)".format(benchmark)
        os.system("cd {}; cargo run > /dev/null 2>&1".format(benchmark_dir))
        os.system("cd {}; cp target/benchmark.so .".format(benchmark_dir))
        os.system(
            "cd {}; LD_LIBRARY_PATH=/sightglass/engines/native/ /sightglass/target/release/sightglass-cli benchmark {} --engine /sightglass/engines/native/libengine.so  --processes=1 --raw --output-format csv --output-file {} > /dev/null 2>&1".format(
                benchmark_dir, wasm_benchmark_path, results_path
            )
        )
        os.system(
            "./target/release/sightglass-cli summarize --input-format csv --output-format csv -f {} > {}".format(
                results_path, results_summarized_path
            )
        )
        if os.stat(results_summarized_path).st_size == 0:
            print("Native execution did not run properly ... skipping")
        else:
            os.system(
                'grep -v "cycles"  {} > results/tmpfile && mv results/tmpfile {}'.format(
                    results_summarized_path, results_summarized_path
                )
            )
            pd.read_csv(
                results_summarized_path, usecols=["phase", "mean"], header=0
            ).to_csv(results_summarized_transposed_path, header=True, index=False)
            os.system("sed -i 1d {}".format(results_summarized_transposed_path))
            dict_native = pd.read_csv(
                results_summarized_transposed_path,
                index_col=0,
                usecols=[0, 1],
                header=None,
            ).T.to_dict("list")
            for key, value in dict_native.items():
                if key == "Execution":
                    execution_native = value[0]
            os.system(
                'termgraph {} --title "{}" --color blue'.format(
                    results_summarized_transposed_path, termgraph_title
                )
            )
            os.system("cd /sightglass".format(benchmark_dir))

    print("")
    print("Collecting Wasm ({}).".format(benchmark))

    wasm_benchmark_path = (
        "/sightglass/benchmarks/" + perf_benchmarks[benchmark] + "/benchmark.wasm"
    )
    results_path = "/sightglass/results/" + perf_benchmarks[benchmark] + "_results.csv"
    results_summarized_path = (
        "/sightglass/results/" + perf_benchmarks[benchmark] + "_results_summarized.csv"
    )
    results_summarized_transposed_path = (
        "/sightglass/results/"
        + perf_benchmarks[benchmark]
        + "_results_summarized_transposed.csv"
    )
    termgraph_title = "{} wasm time(ns)".format(benchmark)

    os.system(
        "./target/release/sightglass-cli benchmark --processes 1 --engine ./engines/wasmtime/libengine.so --raw --output-format csv --output-file {} -- {}".format(
            results_path, wasm_benchmark_path
        )
    )
    os.system(
        "./target/release/sightglass-cli summarize --input-format csv --output-format csv -f {} > {}".format(
            results_path, results_summarized_path
        )
    )
    os.system(
        'grep -v "cycles"  {} > results/tmpfile && mv results/tmpfile {}'.format(
            results_summarized_path, results_summarized_path
        )
    )
    pd.read_csv(results_summarized_path, usecols=["phase", "mean"], header=0).to_csv(
        results_summarized_transposed_path, header=True, index=False
    )

    os.system("sed -i 1d {}".format(results_summarized_transposed_path))
    dict = pd.read_csv(
        results_summarized_transposed_path, index_col=0, usecols=[0, 1], header=None
    ).T.to_dict("list")
    os.system(
        'termgraph {} --title "{}" --color blue'.format(
            results_summarized_transposed_path, termgraph_title
        )
    )

    if execution_native > 0:
        for key, value in dict.items():
            if key == "Execution":
                dict["Efficiency"] = execution_native / value[0]
                break
    return dict


def geo_mean_overflow(iterable):
    a = np.log(iterable)
    return np.exp(a.mean())


def run_suites(suite_name, run_native=False):
    print("")
    print(
        colored(
            "Benchmarking {}: {}".format(suite_name, perf_suites[suite_name]),
            "green",
            attrs=["bold"],
        )
    )
    suite_summary.clear()
    for benchmark in perf_suites[suite_name]:
        if ARGS_DICT["native"]:
            dict = run_benchmarks(benchmark, True)
        else:
            dict = run_benchmarks(benchmark)

        for key, value in dict.items():
            try:
                suite_summary[key].append(value)
            except KeyError:
                suite_summary[key] = [value]

    for key, value in suite_summary.items():
        suite_summary[key] = geo_mean_overflow(value)

    return {"efficiency_score": suite_summary, "execution_score": suite_summary}


def run_wasmscore():
    efficiency_summary = collections.OrderedDict()
    execution_summary = collections.OrderedDict()

    for suite in perf_tests["wasmscore"]:
        if ARGS_DICT["native"]:
            dict = run_suites(suite, True)
        else:
            dict = run_suites(suite)

        for key, value in dict["execution_score"].items():
            try:
                execution_summary[key].append(value)
            except KeyError:
                execution_summary[key] = [value]

        for key, value in dict["efficiency_score"].items():
            try:
                efficiency_summary[key].append(value)
            except KeyError:
                efficiency_summary[key] = [value]

    compilation_score = 0
    efficiency_score = 0
    for key, value in execution_summary.items():
        if key == "Compilation":
            compilation_score = geo_mean_overflow(value)
        elif key == "Instantiation":
            instantiation_score = geo_mean_overflow(value)
        elif key == "Execution":
            execution_score = geo_mean_overflow(value)
        elif key == "Efficiency":
            efficiency_score = geo_mean_overflow(value)
        else:
            print("Other Key: {}".format(key))

    overall_score = instantiation_score + execution_score
    print("")
    print(
        colored(
            "Final Wasm Score (Higher Better): {:.2f}".format(
                1 / overall_score * 10000000000
            ),
            "green",
            attrs=["bold"],
        )
    )
    if ARGS_DICT["native"]:
        print(
            colored(
                "Final Wasm Efficiency Score (Higher Better): {:.2f}".format(
                    efficiency_score
                ),
                "green",
                attrs=["bold"],
            )
        )
    print("")

def main():
    print("")
    print("WasmScore")
    if ARGS_DICT["list"]:
        print("")
        print("Scores\n------")
        print(yaml.dump(perf_tests, sort_keys=True, default_flow_style=False))
        print("Suites\n------")
        print(yaml.dump(perf_suites, sort_keys=True, default_flow_style=False))
        return

    if ARGS_DICT["benchmarks"]:
        for benchmark in ARGS_DICT["benchmarks"]:
            if benchmark in perf_benchmarks:
                if ARGS_DICT["native"]:
                    run_benchmarks(benchmark, True)
                else:
                    run_benchmarks(benchmark)
            else:
                print("Benchmark {} is not valid".format(benchmark))
    elif ARGS_DICT["suites"]:
        for suite in ARGS_DICT["suites"]:
            if suite in perf_suites:
                if ARGS_DICT["native"]:
                    run_suites(suite, True)
                else:
                    run_suites(suite)
            else:
                print("Suite {} is not valid".format(suite))
    else:
        run_wasmscore()

if __name__ == "__main__":
    main()
