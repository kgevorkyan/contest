./install_required_packages.sh
./example-analyzer/scripts/build.sh

clang -g -O0 -c -emit-llvm resources/test_suites/memory_leak/EASY01/EASY01.c

./example-analyzer/run.sh EASY01.bc

opt-14 -load-pass-plugin example-analyzer/build/src/libAnalyzer.so -passes=simple -f EASY01.bc
