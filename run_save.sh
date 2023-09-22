#!/bin/bash

set -e

FILE_PATH=${1}

# were created in setup.sh
BUILD_DIR="./example-analyzer/build"
BITCODE_DIR="./bc_dir"
REPORT_DIR="./reports"

cd $BITCODE_DIR

clang-12 -g -O0 -c -emit-llvm ${FILE_PATH}

cd -

FILE_NAME_WITH_EXTENSION=${FILE_PATH##*/}
FILE_NAME=${FILE_NAME_WITH_EXTENSION%.*}

TEST_SUITE_PATH=$(dirname $(dirname "$FILE_PATH"))
TEST_SUITE_NAME=${TEST_SUITE_PATH##*/}

opt-12 -load-pass-plugin ${BUILD_DIR}/src/libAnalyzer.so -passes=simple -disable-output "$BITCODE_DIR/${FILE_NAME}.bc"

REPORT="${TEST_SUITE_NAME}_$FILE_NAME.sarif"

cp "report.sarif" "$REPORT_DIR/$REPORT" || echo "failed to run on $FILE_NAME"