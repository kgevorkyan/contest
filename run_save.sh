#!/bin/bash

# ---------------------------------- /install_required_packages.sh -------------------------------- #

set -e

if [[ "$EUID" -ne 0 ]]
then
  echo "Please run with root permission!" && exit 1
fi

ALL="all"
if [[ "$1" -eq "$ALL" ]]
then
  TIME_ZONE="Asia/Yerevan"
  ln -snf /usr/share/zoneinfo/"$TIME_ZONE" /etc/localtime && echo "$TIME_ZONE" > /etc/timezone
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

ROOT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"

check_build_file() {
  BUILD_DIRECTORY="$1"
  if [ -d "$BUILD_DIRECTORY" ]; then
    rm -rf "$BUILD_DIRECTORY"
  fi

  mkdir -p "$BUILD_DIRECTORY"
}

project_build() {
  BUILD_DIRECTORY="$1"
  cd "$BUILD_DIRECTORY"
  cmake ../
  make
  cd -
}

# ./example-analyzer/scripts/build.sh

BUILD_DIR="./example-analyzer/build"
check_build_file "$BUILD_DIR"
project_build "$BUILD_DIR"

# ---------------------------------------------------------- #

clang -g -O0 -c -emit-llvm ./resources/test_suites/memory_leak/EASY01/EASY01.c

./example-analyzer/run.sh EASY01.bc

opt-14 -load-pass-plugin example-analyzer/build/src/libAnalyzer.so -passes=simple -f EASY01.bc
