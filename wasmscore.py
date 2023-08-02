#!/usr/bin/python3.8
""" WasmScore Benchmark """

import os
import sys
import datetime
from datetime import datetime
import argparse
import collections
import subprocess
import textwrap
import logging
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
            available benchmarks:   See list
            available suites:       See list
            available tests:        WasmScore (default), SimdScore



            example usage: ./wasmscore.sh -b shootout -r wasmtime_app
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
    "-t",
    "--tests",
    nargs="+",
    help="Test to run (ignored if suite or individual benchmark(s) specified)",
)
group = parser.add_mutually_exclusive_group()
group.add_argument(
    "-n",
    "--native",
    action="store_true",
    help="Run the benchmark(s) natively. Not all benchmarks supported",
)

group.add_argument(
    "-no-n",
    "--no-native",
    action="store_true",
    help="Will disable running the benchmark(s) natively if done so by default",
)

parser.add_argument(
    "-q",
    "--quiet",
    action="store_true",
    help="Turn off printing of scores",
)

parser.add_argument(
    "-l",
    "--list",
    action="store_true",
    help="List all available suites and individual benchmarks to run",
)

parser.add_argument(
    "-log",
    "--loglevel",
    default="ERROR",
    help="Provide logging level. Example --loglevel debug, default=ERROR",
)


# Global Variables
args = parser.parse_args()
ARGS_DICT = vars(args)
DATE_TIME = datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=args.loglevel.upper())
DEFAULT_BENCH_PROCESS_NUM=3
SG_BENCHMARKS_BASE = "/sightglass/benchmarks/"

# Dictionaries
sg_benchmarks_wasm = {
    "blake3-scalar": "blake3-scalar/benchmark.wasm",
    "blake3-simd": "blake3-simd/benchmark.wasm",
    "blind-sig": "blind-sig/benchmark.wasm",
    "bzip2": "bz2/benchmark.wasm",
    "hex-simd": "hex-simd/benchmark.wasm",
    "image-classification": "image-classification/image-classification-benchmark.wasm",
    "intgemm-simd": "intgemm-simd/benchmark.wasm",
    "aead_aes256gcm.wasm": "libsodium/libsodium-aead_aes256gcm.wasm",
    "aead_aes256gcm2.wasm": "libsodium/libsodium-aead_aes256gcm2.wasm",
    "aead_chacha20poly1305.wasm": "libsodium/libsodium-aead_chacha20poly1305.wasm",
    "libsodium-aead_chacha20poly13052.wasm": "libsodium/libsodium-aead_chacha20poly13052.wasm",
    "libsodium-aead_xchacha20poly1305.wasm": "libsodium/libsodium-aead_xchacha20poly1305.wasm",
    "libsodium-auth.wasm": "libsodium/libsodium-auth.wasm",
    "libsodium-auth2.wasm": "libsodium/libsodium-auth2.wasm",
    "libsodium-auth3.wasm": "libsodium/libsodium-auth3.wasm",
    "libsodium-auth5.wasm": "libsodium/libsodium-auth5.wasm",
    "libsodium-auth6.wasm": "libsodium/libsodium-auth6.wasm",
    "libsodium-auth7.wasm": "libsodium/libsodium-auth7.wasm",
    "libsodium-box.wasm": "libsodium/libsodium-box.wasm",
    "libsodium-box2.wasm": "libsodium/libsodium-box2.wasm",
    "libsodium-box7.wasm": "libsodium/libsodium-box7.wasm",
    "libsodium-box8.wasm": "libsodium/libsodium-box8.wasm",
    "libsodium-box_easy.wasm": "libsodium/libsodium-box_easy.wasm",
    "libsodium-box_easy2.wasm": "libsodium/libsodium-box_easy2.wasm",
    "libsodium-box_seal.wasm": "libsodium/libsodium-box_seal.wasm",
    "libsodium-box_seed.wasm": "libsodium/libsodium-box_seed.wasm",
    "libsodium-chacha20.wasm": "libsodium/libsodium-chacha20.wasm",
    "libsodium-codecs.wasm": "libsodium/libsodium-codecs.wasm",
    "libsodium-core1": "libsodium/libsodium-core1.wasm",
    "libsodium-core2": "libsodium/libsodium-core2.wasm",
    "libsodium-core3": "libsodium/libsodium-core3.wasm",
    "libsodium-core4": "libsodium/libsodium-core4.wasm",
    "libsodium-core5": "libsodium/libsodium-core5.wasm",
    "libsodium-core6": "libsodium/libsodium-core6.wasm",
    "libsodium-core_ed25519": "libsodium/libsodium-core_ed25519.wasm",
    "libsodium-core_ristretto255": "libsodium/libsodium-core_ristretto255.wasm",
    "libsodium-ed25519_convert": "libsodium/libsodium-ed25519_convert.wasm",
    "libsodium-generichash": "libsodium/libsodium-generichash.wasm",
    "libsodium-generichash2": "libsodium/libsodium-generichash2.wasm",
    "libsodium/libsodium-generichash3": "libsodium/libsodium-generichash3.wasm",
    "libsodium-hash": "libsodium/libsodium-hash.wasm",
    "libsodium-hash3": "libsodium/libsodium-hash3.wasm",
    "libsodium-kdf": "libsodium/libsodium-kdf.wasm",
    "libsodium-keygen": "libsodium/libsodium-keygen.wasm",
    "libsodium-kx": "libsodium/libsodium-kx.wasm",
    "libsodium-metamorphic": "libsodium/libsodium-metamorphic.wasm",
    "libsodium-misuse": "libsodium/libsodium-misuse.wasm",
    "libsodium-onetimeauth": "libsodium/libsodium-onetimeauth.wasm",
    "libsodium-onetimeauth2": "libsodium/libsodium-onetimeauth2.wasm",
    "libsodium-onetimeauth7": "libsodium/libsodium-onetimeauth7.wasm",
    "libsodium-pwhash_argon2i": "libsodium/libsodium-pwhash_argon2i.wasm",
    "libsodium-pwhash_argon2id": "libsodium/libsodium-pwhash_argon2id.wasm",
    "libsodium-pwhash_scrypt": "libsodium/libsodium-pwhash_scrypt.wasm",
    "libsodium-pwhash_scrypt_ll": "libsodium/libsodium-pwhash_scrypt_ll.wasm",
    "libsodium-randombytes": "libsodium/libsodium-randombytes.wasm",
    "libsodium-scalarmult": "libsodium/libsodium-scalarmult.wasm",
    "libsodium-scalarmult2": "libsodium/libsodium-scalarmult2.wasm",
    "libsodium-scalarmult5": "libsodium/libsodium-scalarmult5.wasm",
    "libsodium-scalarmult6": "libsodium/libsodium-scalarmult6.wasm",
    "libsodium-scalarmult7": "libsodium/libsodium-scalarmult7.wasm",
    "libsodium-scalarmult8": "libsodium/libsodium-scalarmult8.wasm",
    "libsodium-scalarmult_ed25519": "libsodium/libsodium-scalarmult_ed25519.wasm",
    "libsodium-scalarmult_ristretto255": "libsodium/libsodium-scalarmult_ristretto255.wasm",
    "libsodium-secretbox": "libsodium/libsodium-secretbox.wasm",
    "libsodium-secretbox2": "libsodium/libsodium-secretbox2.wasm",
    "libsodium-secretbox7": "libsodium/libsodium-secretbox7.wasm",
    "libsodium-secretbox8": "libsodium/libsodium-secretbox8.wasm",
    "libsodium-secretbox_easy": "libsodium/libsodium-secretbox_easy.wasm",
    "libsodium-secretbox_easy2": "libsodium/libsodium-secretbox_easy2.wasm",
    "libsodium-secretstream": "libsodium/libsodium-secretstream.wasm",
    "libsodium-shorthash": "libsodium/libsodium-shorthash.wasm",
    "libsodium-sign": "libsodium/libsodium-sign.wasm",
    "libsodium-siphashx24": "libsodium/libsodium-siphashx24.wasm",
    "libsodium-sodium_core": "libsodium/libsodium-sodium_core.wasm",
    "libsodium-sodium_utils": "libsodium/libsodium-sodium_utils.wasm",
    "libsodium-sodium_utils2": "libsodium/libsodium-sodium_utils2.wasm",
    "libsodium-sodium_utils3": "libsodium/libsodium-sodium_utils3.wasm",
    "libsodium-sodium_version": "libsodium/libsodium-sodium_version.wasm",
    "libsodium-stream": "libsodium/libsodium-stream.wasm",
    "libsodium-stream2": "libsodium/libsodium-stream2.wasm",
    "libsodium-stream3": "libsodium/libsodium-stream3.wasm",
    "libsodium-stream4": "libsodium/libsodium-stream4.wasm",
    "libsodium-verify1": "libsodium/libsodium-verify1.wasm",
    "libsodium-xchacha20": "libsodium/libsodium-xchacha20.wasm",
    "meshoptimizer": "meshoptimizer/benchmark.wasm",
    "pulldown-cmark": "pulldown-cmark/benchmark.wasm",
    "ackermann": "shootout/shootout-ackermann.wasm",
    "base64": "shootout/shootout-base64.wasm",
    "ctype": "shootout/shootout-ctype.wasm",
    "ed25519": "shootout/shootout-ed25519.wasm",
    "fibonacci": "shootout/shootout-fib2.wasm",
    "gimli": "shootout/shootout-gimli.wasm",
    "heapsort": "shootout/shootout-heapsort.wasm",
    "keccak": "shootout/shootout-keccak.wasm",
    "matrix": "shootout/shootout-matrix.wasm",
    "memmove": "shootout/shootout-memmove.wasm",
    "minicsv": "shootout/shootout-minicsv.wasm",
    "nested-loop": "shootout/shootout-nested-loop.wasm",
    "random": "shootout/shootout-random.wasm",
    "ratelimit": "shootout/shootout-ratelimit.wasm",
    "seqhash": "shootout/shootout-seqhash.wasm",
    "sieve": "shootout/shootout-sieve.wasm",
    "switch": "shootout/shootout-switch.wasm",
    "xblabla20": "shootout/shootout-xblabla20.wasm",
    "xchacha20": "shootout/shootout-xchacha20.wasm",
    "spidermonkey": "spidermonkey/benchmark.wasm",
}

sg_benchmarks_native = {
    "meshoptimizer": "meshoptimizer/codecbench-simd.so",
    "ackermann": "shootout/shootout-ackermann.so",
    "base64": "shootout/shootout-base64.so",
    "ctype": "shootout/shootout-ctype.so",
    "ed25519": "shootout/shootout-ed25519.so",
    "fibonacci": "shootout/shootout-fib2.so",
    "gimli": "shootout/shootout-gimli.so",
    "heapsort": "shootout/shootout-heapsort.so",
    "keccak": "shootout/shootout-keccak.so",
    "matrix": "shootout/shootout-matrix.so",
    "memmove": "shootout/shootout-memmove.so",
    "minicsv": "shootout/shootout-minicsv.so",
    "nested-loop": "shootout/shootout-nested-loop.so",
    "random": "shootout/shootout-random.so",
    "ratelimit": "shootout/shootout-ratelimit.so",
    "seqhash": "shootout/shootout-seqhash.so",
    "sieve": "shootout/shootout-sieve.so",
    "switch": "shootout/shootout-switch.so",
    "xblabla20": "shootout/shootout-xblabla20.so",
    "xchacha20": "shootout/shootout-xchacha20.so",
}

perf_suites = {
    "app-wasmscore": ["meshoptimizer"],
    "core-wasmscore": ["ackermann", "ctype"],
    #"core-wasmscore": ["ackermann", "ctype", "fibonacci"],
    "crypto-wasmscore": [],
    #"crypto-wasmscore": ["base64", "ed25519", "seqhash"],
    "ai-wasmscore": [],
    "regex-wasmscore": [],
    "shootout": [
        "base64",
        "ctype",
        "fibonacci",
        "gimli",
        "heapsort",
        "keccak",
        "matrix",
        "memmove",
        "minicsv",
        "nested-loop",
        "random",
        "ratelimit",
        "seqhash",
        "sieve",
        "switch",
        "xblahblah20",
        "xchacha20",
    ],
    "libsodium": [
        "libsodium-aead_aes256gcm.wasm",
        "libsodium-aead_aes256gcm2.wasm",
        "libsodium-aead_chacha20poly1305.wasm",
        "libsodium-aead_chacha20poly13052.wasm",
        "libsodium-aead_xchacha20poly1305.wasm",
        "libsodium-auth.wasm",
        "libsodium-auth2.wasm",
        "libsodium-auth3.wasm",
        "libsodium-auth5.wasm",
        "libsodium-auth6.wasm",
        "libsodium-auth7.wasm",
        "libsodium-box.wasm",
        "libsodium-box2.wasm",
        "libsodium-box7.wasm",
        "libsodium-box8.wasm",
        "libsodium-box_easy.wasm",
        "libsodium-box_easy2.wasm",
        "libsodium-box_seal.wasm",
        "libsodium-box_seed.wasm",
        "libsodium-chacha20.wasm",
        "libsodium-codecs.wasm",
        "libsodium-core1.wasm",
        "libsodium-core2.wasm",
        "libsodium-core3.wasm",
        "libsodium-core4.wasm",
        "libsodium-core5.wasm",
        "libsodium-core6.wasm",
        "libsodium-core_ed25519.wasm",
        "libsodium-core_ristretto255.wasm",
        "libsodium-ed25519_convert.wasm",
        "libsodium-generichash.wasm",
        "libsodium-generichash2.wasm",
        "libsodium-generichash3.wasm",
        "libsodium-hash.wasm",
        "libsodium-hash3.wasm",
        "libsodium-kdf.wasm",
        "libsodium-keygen.wasm",
        "libsodium-kx.wasm",
        "libsodium-metamorphic.wasm",
        "libsodium-misuse.wasm",
        "libsodium-onetimeauth.wasm",
        "libsodium-onetimeauth2.wasm",
        "libsodium-onetimeauth7.wasm",
        "libsodium-pwhash_argon2i.wasm",
        "libsodium-pwhash_argon2id.wasm",
        "libsodium-pwhash_scrypt.wasm",
        "libsodium-pwhash_scrypt_ll.wasm",
        "libsodium-randombytes.wasm",
        "libsodium-scalarmult.wasm",
        "libsodium-scalarmult2.wasm",
        "libsodium-scalarmult5.wasm",
        "libsodium-scalarmult6.wasm",
        "libsodium-scalarmult7.wasm",
        "libsodium-scalarmult8.wasm",
        "libsodium-scalarmult_ed25519.wasm",
        "libsodium-scalarmult_ristretto255.wasm",
        "libsodium-secretbox.wasm",
        "libsodium-secretbox2.wasm",
        "libsodium-secretbox7.wasm",
        "libsodium-secretbox8.wasm",
        "libsodium-secretbox_easy.wasm",
        "libsodium-secretbox_easy2.wasm",
        "libsodium-secretstream.wasm",
        "libsodium-shorthash.wasm",
        "libsodium-sign.wasm",
        "libsodium-siphashx24.wasm",
        "libsodium-sodium_core.wasm",
        "libsodium-sodium_utils.wasm",
        "libsodium-sodium_utils2.wasm",
        "libsodium-sodium_utils3.wasm",
        "libsodium-sodium_version.wasm",
        "libsodium-stream.wasm",
        "libsodium-stream2.wasm",
        "libsodium-stream3.wasm",
        "libsodium-stream4.wasm",
        "libsodium-verify1.wasm",
        "libsodium-xchacha20.wasm",
    ],
    "simd-simdscore": ["blake3-simd"],
    "scalar-simdscore": ["blake3-scalar"],
}

perf_tests = [
    "WasmScore",
    "SimdScore",
    "Quickrun-WasmScore",
    "Quickrun-SimdScore",
    "Quickrun-All",
]

# Appended by build_dict()
suite_summary = collections.OrderedDict()


# Build dictionaries based on cmd flags and directory file structure
def run_benchmarks(benchmark, run_native=False):
    """Runs the benchmark"""

    logging.info("Running benchmark ...")
    logging.info("Run native ... %s", run_native)

    execution_native = 0
    if run_native and sg_benchmarks_native[benchmark]:
        #print_verbose("")
        print_verbose(f"Collecting Native ({benchmark}).")

        native_benchmark_dir = os.path.dirname(
            f"{SG_BENCHMARKS_BASE}" + sg_benchmarks_native[benchmark]
        )
        logging.debug("native_benchmark_dir ... %s", native_benchmark_dir)

        native_benchmark_path = (
            f"{SG_BENCHMARKS_BASE}" + sg_benchmarks_native[benchmark]
        )
        logging.debug("native_benchmark_path ... %s", native_benchmark_path)

        results_dir = f"{SG_BENCHMARKS_BASE}/results/"
        results_path = (
            f"{results_dir}/{benchmark}" + "_native_results.csv"
        )
        logging.debug("results_path ... %s", results_path)

        results_summarized_path = (
            f"{SG_BENCHMARKS_BASE}/results/{benchmark}"
            + "_results_native_summarized.csv"
        )
        logging.debug("results_summarized_path ... %s", results_summarized_path)

        results_summarized_transposed_path = (
            f"{SG_BENCHMARKS_BASE}/results/{benchmark}"
            + "_results_native_summarized_transposed.csv"
        )
        logging.debug(
            "results_summarized_transposed_path ... %s",
            results_summarized_transposed_path,
        )

        native_build_cmd_string = "./build-native.sh"
        try:
            logging.info("Trying native build ... ")
            output = subprocess.check_output(
                native_build_cmd_string.split(),
                shell=True,
                text=True,
                cwd=f"{native_benchmark_dir}",
                stderr=subprocess.STDOUT,
            )
            logging.debug("%s", output)
        except subprocess.CalledProcessError as error:
            print(f"Building native failed with error code {error.returncode}")
            sys.exit(error.returncode)

        if not os.path.basename(f"{native_benchmark_path}") == "benchmark.so":
            native_build_cp_string = f"cp {native_benchmark_path} ./benchmark.so"
            try:
                logging.info("Trying native cp ... ")
                output = subprocess.check_output(
                    native_build_cp_string.split(),
                    shell=False,
                    text=True,
                    cwd=f"{native_benchmark_dir}",
                    stderr=subprocess.STDOUT,
                )
                logging.debug("%s", output)
            except subprocess.CalledProcessError as error:
                print(f"Building native failed with error code {error.returncode}")
                sys.exit(error.returncode)

        create_results_path_cmd_string = f"mkdir -p {results_dir}"
        try:
            logging.info("Trying mkdir for results_path ... %s", create_results_path_cmd_string)
            output = subprocess.check_output(
                create_results_path_cmd_string,
                shell=True,
                text=True,
                stderr=subprocess.STDOUT,
            )
            logging.debug("%s", output)
        except subprocess.CalledProcessError as error:
            print(f"mkdir for build folder failed with error code {error.returncode}")
            sys.exit(error.returncode)


        cli_cmd_string = (
            "LD_LIBRARY_PATH=/sightglass/engines/native/ "
            "/sightglass/target/release/sightglass-cli benchmark "
            f"{native_benchmark_path} --engine "
            f"/sightglass/engines/native/libengine.so --processes={DEFAULT_BENCH_PROCESS_NUM} --raw "
            f"--output-format csv --output-file {results_path}"
        )

        try:
            logging.info("Trying sightglass-cli benchmark command for native ... %s", cli_cmd_string)
            output = subprocess.check_output(
                cli_cmd_string,
                shell=True,
                text=True,
                cwd=f"{native_benchmark_dir}",
                #stderr=subprocess.STDOUT,
                executable='/bin/bash',
            )
            logging.debug("%s", output)
        except subprocess.CalledProcessError as error:
            print(f"Running sightglass-cli benchmark failed with error code {error.returncode}")
            sys.exit(error.returncode)

        cli_summarize_string = (
            f"/sightglass/target/release/sightglass-cli summarize --input-format csv "
            f"--output-format csv -f {results_path} > {results_summarized_path}"
        )

        try:
            logging.info("Trying sightglass-cli summarize command for native ... %s", cli_summarize_string)
            output = subprocess.check_output(
                cli_summarize_string,
                shell=True,
                text=True,
                cwd=f"{native_benchmark_dir}",
                stderr=subprocess.STDOUT,
                executable='/bin/bash',
            )
            logging.debug("%s", output)
        except subprocess.CalledProcessError as error:
            print(f"Running sightglass-cli summarize failed with error code {error.returncode}")
            sys.exit(error.returncode)


        if os.stat(results_summarized_path).st_size == 0:
            print("Native execution did not run properly ... exiting")
            sys.exit(1)
        else:
            logging.info("Trying printing native benchmark results ...")
            os.system(
                f'grep -v "cycles"  {results_summarized_path} > results/tmpfile '
                f"&& mv results/tmpfile {results_summarized_path}"
            )
            pd.read_csv(
                results_summarized_path, usecols=["phase", "mean"], header=0
            ).to_csv(results_summarized_transposed_path, header=True, index=False)
            os.system(f"sed -i 1d {results_summarized_transposed_path}")
            dict_native = pd.read_csv(
                results_summarized_transposed_path,
                index_col=0,
                usecols=[0, 1],
                header=None,
            ).T.to_dict("list")
            for key, value in dict_native.items():
                if key == "Execution":
                    execution_native = value[0]

            termgraph_title = f"{benchmark} native time(ns)"
            os.system(
                f"termgraph {results_summarized_transposed_path} "
                f'--title "{termgraph_title}" --color blue'
            )
            os.system("cd /sightglass".format(native_benchmark_dir))
    elif run_native:
        print_verbose(f"Native {benchmark} is not supported")

    #print_verbose("")
    print_verbose(f"Collecting Wasm ({benchmark}).")

    #wasm_benchmark_path = (
    #    f"{SG_BENCHMARKS_BASE}" + sg_benchmarks_wasm[benchmark] + "/benchmark.wasm"
    #)
    #logging.debug("wasm_benchmark_path ... %s", wasm_benchmark_path)

    #results_path = (
    #    f"{SG_BENCHMARKS_BASE}/results/"
    #    + sg_benchmarks_wasm[benchmark]
    #    + "_results.csv"
    #)
    #logging.debug("results_path ... %s", results_path)

    #results_summarized_path = (
    #    f"{SG_BENCHMARKS_BASE}/results/"
    #    + sg_benchmarks_wasm[benchmark]
    #    + "_results_summarized.csv"
    #)
    #logging.debug("results_summarized_path ... %s", results_summarized_path)

    #results_summarized_transposed_path = (
    #    f"{SG_BENCHMARKS_BASE}/results/"
    #    + sg_benchmarks_wasm[benchmark]
    #    + "_results_summarized_transposed.csv"
    #)
    #logging.debug(
    #    "results_summarized_transposed_path ... %s", results_summarized_transposed_path
    #)

    wasm_benchmark_dir = os.path.dirname(
        f"{SG_BENCHMARKS_BASE}" + sg_benchmarks_wasm[benchmark]
    )
    logging.debug("wasm_benchmark_dir ... %s", wasm_benchmark_dir)

    wasm_benchmark_path = (
        f"{SG_BENCHMARKS_BASE}" + sg_benchmarks_wasm[benchmark]
    )
    logging.debug("wasm_benchmark_path ... %s", wasm_benchmark_path)

    results_dir = f"{SG_BENCHMARKS_BASE}/results/"
    results_path = (
        f"{results_dir}/{benchmark}" + "_wasm_results.csv"
    )
    logging.debug("results_path ... %s", results_path)

    results_summarized_path = (
        f"{SG_BENCHMARKS_BASE}/results/{benchmark}"
        + "_results_wasm_summarized.csv"
    )
    logging.debug("results_summarized_path ... %s", results_summarized_path)

    results_summarized_transposed_path = (
        f"{SG_BENCHMARKS_BASE}/results/{benchmark}"
        + "_results_wasm_summarized_transposed.csv"
    )
    logging.debug(
        "results_summarized_transposed_path ... %s",
        results_summarized_transposed_path,
    )

    termgraph_title = f"{benchmark} wasm time(ns)"

    cli_cmd_string = (
        f"/sightglass/target/release/sightglass-cli benchmark "
        f"--processes={DEFAULT_BENCH_PROCESS_NUM} --engine "
        f"/sightglass/engines/wasmtime/libengine.so --raw --output-format csv --output-file "
        f"{results_path} -- {wasm_benchmark_path}"
    )

    try:
        logging.info("Trying sightglass-cli benchmark command for wasm ... %s", cli_cmd_string)
        output = subprocess.check_output(
            cli_cmd_string,
            shell=True,
            text=True,
            cwd=f"{wasm_benchmark_dir}",
            #stderr=subprocess.STDOUT,
            executable='/bin/bash',
        )
        logging.debug("%s", output)
    except subprocess.CalledProcessError as error:
        print(f"Running sightglass-cli benchmark failed with error code {error.returncode}")
        sys.exit(error.returncode)


    #logging.debug("sightglass-cli command ... %s", cli_cmd_string)
    #try:
    #    subprocess.check_output(cli_cmd_string.split())
    #except subprocess.CalledProcessError as error:
    #    print(f"Sightglass cli command failed with error code {error.returncode}")

    # os.system(
    #    f"./target/release/sightglass-cli benchmark --processes 1 --engine "
    #    f"./engines/wasmtime/libengine.so --raw --output-format csv --output-file "
    #    f"{results_path} -- {wasm_benchmark_path}"
    # )

    cli_summarize_string = (
        f"/sightglass/target/release/sightglass-cli summarize --input-format csv "
        f"--output-format csv -f {results_path} > {results_summarized_path}"
    )

    try:
        logging.info("Trying sightglass-cli summarize command for wasm ... %s", cli_summarize_string)
        output = subprocess.check_output(
            cli_summarize_string,
            shell=True,
            text=True,
            cwd=f"{wasm_benchmark_dir}",
            stderr=subprocess.STDOUT,
            executable='/bin/bash',
        )
        logging.debug("%s", output)
    except subprocess.CalledProcessError as error:
        print(f"Running sightglass-cli summarize failed with error code {error.returncode}")
        sys.exit(error.returncode)

    #os.system(
    #    f"./target/release/sightglass-cli summarize --input-format csv "
    #    f"--output-format csv -f {results_path} > {results_summarized_path}"
    #)


    os.system(
        f'grep -v "cycles"  {results_summarized_path} > results/tmpfile && '
        f"mv results/tmpfile {results_summarized_path}"
    )
    pd.read_csv(results_summarized_path, usecols=["phase", "mean"], header=0).to_csv(
        results_summarized_transposed_path, header=True, index=False
    )

    os.system(f"sed -i 1d {results_summarized_transposed_path}")
    bench_dict = pd.read_csv(
        results_summarized_transposed_path, index_col=0, usecols=[0, 1], header=None
    ).T.to_dict("list")
    os.system(
        f'termgraph {results_summarized_transposed_path} --title "{termgraph_title}" --color blue'
    )

    if execution_native > 0:
        for key, value in bench_dict.items():
            if key == "Execution":
                bench_dict["Efficiency"] = execution_native / value[0]
                break
    return bench_dict


def geo_mean_overflow(iterable):
    """Helper function to avoid overflow errors during geo-mean calculation"""
    calc = np.log(iterable)
    return np.exp(calc.mean())


def run_suites(suite_name, run_native=False):
    """Benchmark a suite"""

    logging.info("Running suite ...")
    print_verbose("")
    print_verbose(
        colored(
            f"Benchmarking {suite_name}: {perf_suites[suite_name]}",
            "green",
            attrs=["bold"],
        )
    )
    suite_summary.clear()
    for benchmark in perf_suites[suite_name]:
        if ARGS_DICT["native"] or run_native:
            bench_dict = run_benchmarks(benchmark, True)
        else:
            bench_dict = run_benchmarks(benchmark)

        for key, value in bench_dict.items():
            try:
                suite_summary[key].append(value)
            except KeyError:
                suite_summary[key] = [value]

    for key, value in suite_summary.items():
        suite_summary[key] = geo_mean_overflow(value)

    return {"efficiency_score": suite_summary, "execution_score": suite_summary}


def run_wasmscore():
    """WasmScore test. Runs a collection of suites, both Wasm and native benchmarks
    by default, and reports out a Wasm performance score based a geo-mean of the
    performances of the benchmark suites. The test also reports a Wasm efficiency based
    on Wasm's performance relative to native."""

    logging.info("Running WasmScore test ... ")
    efficiency_summary = collections.OrderedDict()
    execution_summary = collections.OrderedDict()

    for suite in [
        "ai-wasmscore",
        "app-wasmscore",
        "core-wasmscore",
        "crypto-wasmscore",
        "regex-wasmscore",
    ]:
        score_dict = run_suites(suite, not ARGS_DICT["no_native"])

        print(score_dict)

        for key, value in score_dict["execution_score"].items():
            try:
                execution_summary[key].append(value)
            except KeyError:
                execution_summary[key] = [value]

        for key, value in score_dict["efficiency_score"].items():
            try:
                efficiency_summary[key].append(value)
            except KeyError:
                efficiency_summary[key] = [value]

    print("print exectuion_summary")
    print(execution_summary)
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
            print(f"Other Key: {key}")

    print(f"Print other")
    print(f"{instantiation_score}")
    print(f"{execution_score}")
    print(f"{efficiency_score}")

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
    print(
        colored(
            "Final Wasm Score (Higher Better): {1 / overall_score * 10000000000:.2f}",
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


def run_simdscore():
    """SimdScore test: Benchmarks scalar and simd version of select benchmarks and
    reports a Wasm's scalar and simd performance score based on a geo-mean of
    the performances of the benchmarks. The test also reports a Wasm simd efficiency
    score calculated using Wasm's simd speed-up relative to native."""

    logging.info("Running SimdScore test ...")


def run_quickrun_wasmscore():
    """SimdScore test: Benchmarks scalar and simd version of select benchmarks and
    reports a Wasm's scalar and simd performance score based on a geo-mean of
    the performances of the benchmarks. The test also reports a Wasm simd efficiency
    score calculated using Wasm's simd speed-up relative to native."""

    logging.info("Running QuickRun-WasmScore ...")
    global DEFAULT_BENCH_PROCESS_NUM
    DEFAULT_BENCH_PROCESS_NUM=1
    run_wasmscore()

def run_quickrun_simdscore():
    """SimdScore test: Benchmarks scalar and simd version of select benchmarks and
    reports a Wasm's scalar and simd performance score based on a geo-mean of
    the performances of the benchmarks. The test also reports a Wasm simd efficiency
    score calculated using Wasm's simd speed-up relative to native."""

    logging.info("Running QuickRun-SimdScore ...")
    global DEFAULT_BENCH_PROCESS_NUM
    DEFAULT_BENCH_PROCESS_NUM=1
    run_simdscore()

def run_quickrun_all():
    """SimdScore test: Benchmarks scalar and simd version of select benchmarks and
    reports a Wasm's scalar and simd performance score based on a geo-mean of
    the performances of the benchmarks. The test also reports a Wasm simd efficiency
    score calculated using Wasm's simd speed-up relative to native."""

    logging.info("Running QuickRun-All ...")


def print_verbose(string):
    """Print verbose score details"""
    if not ARGS_DICT["quiet"]:
        print(string)


def main():
    """Top level entry"""
    print_verbose("")
    print_verbose("WasmScore")

    if ARGS_DICT["list"]:
        print("")
        print("Scores\n------")
        print(yaml.dump(perf_tests, sort_keys=True, default_flow_style=False))
        print("Suites\n------")
        print(yaml.dump(perf_suites, sort_keys=True, default_flow_style=False))
        return

    if ARGS_DICT["benchmarks"]:
        for benchmark in ARGS_DICT["benchmarks"]:
            if benchmark in sg_benchmarks_wasm:
                if ARGS_DICT["native"]:
                    run_benchmarks(benchmark, True)
                else:
                    run_benchmarks(benchmark)
            else:
                print(f"Benchmark {benchmark} is not valid")
    elif ARGS_DICT["suites"]:
        for suite in ARGS_DICT["suites"]:
            if suite in perf_suites:
                if ARGS_DICT["native"]:
                    run_suites(suite, True)
                else:
                    run_suites(suite)
            else:
                print(f"Suite {suite} is not valid")
    elif ARGS_DICT["tests"]:
        for test in ARGS_DICT["tests"]:
            if test.lower() == "wasmscore":
                run_wasmscore()
            elif test.lower() == "simdscore":
                run_simdscore()
            elif test.lower() == "quickrun_wasmscore":
                run_quickrun_wasmscore()
            elif test.lower() == "quickrun_simdscore":
                run_quickrun_simdscore()
            elif test.lower() == "quickrun_all":
                run_quickrun_all()
            else:
                print(f"Test {test} is not valid")
    else:
        run_quickrun_wasmscore()


if __name__ == "__main__":
    main()
