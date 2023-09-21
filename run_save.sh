#!/bin/bash

# ---------------------------------- /install_required_packages.sh -------------------------------- #
set -e

if [[ "$EUID" -ne 0 ]]
then
  echo "Please run with root permission!" && exit 1
fi

apt-get update && apt-get install -y clang cmake build-essential clang-format libclang-14-dev \
                                     python3 python3-clang-14 python3-pip curl gnupg gnupg2
pip3 install --prefix=/usr/local libclang==14.0.1 pysarif

PODMAM_SUB_REPO="/kubic:/libcontainers:/stable/xUbuntu_20.04/"
PODMAN_REPO="https://download.opensuse.org/repositories/devel:$PODMAM_SUB_REPO"

echo "deb $PODMAN_REPO /" | tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
curl -L "$PODMAN_REPO/Release.key" | apt-key add -
apt-get update && apt-get install -y podman

# -------------------------------- ./example-analyzer/scripts/build.sh ---------------------------- #
create_directory() {
  DIRECTORY="$1"
  if [ -d "$DIRECTORY" ]; then
    rm -rf "$DIRECTORY"
  fi
  mkdir -p "$DIRECTORY"

}

project_build() {
  BUILD_DIRECTORY="$1"
  cd "$BUILD_DIRECTORY"
  cmake ../
  make
  cd -
}

BUILD_DIR="./example-analyzer/build"
create_directory "$BUILD_DIR"
project_build "$BUILD_DIR"

# ---------------------------------------------------------- #
FILE_PATH=${1}

BITCODE_DIR="./bc_dir"
#create_directory "$BITCODE_DIR"
mkdir "$BITCODE_DIR"

cd $BITCODE_DIR

clang -g -O0 -c -emit-llvm ${FILE_PATH}

cd -

FILE_NAME=${FILE_PATH##*/}

opt-14 -load-pass-plugin ${BUILD_DIR}/src/libAnalyzer.so -passes=simple -disable-output "$BITCODE_DIR/${FILE_NAME%.*}.bc"
