#!/bin/bash

set -e

FILE_PATH=${1}

# were created in setup.sh
BUILD_DIR="./example-analyzer/build"
BITCODE_DIR="./bc_dir"
REPORT_DIR="./reports"

cd $BITCODE_DIR

clang -g -O0 -c -emit-llvm ${FILE_PATH}

cd -

FILE_NAME=${FILE_PATH##*/}

opt-14 -load-pass-plugin ${BUILD_DIR}/src/libAnalyzer.so -passes=simple -disable-output "$BITCODE_DIR/${FILE_NAME%.*}.bc"

REPORT="$FILE_NAME.sarif"

cp "report.sarif" "$REPORT_DIR/$REPORT" || echo "failed to run on $FILE_NAME"