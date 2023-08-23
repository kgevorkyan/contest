#!/bin/bash

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

apt-get update && apt-get install -y clang cmake build-essential clang-format libclang-12-dev \
                                     python3 python3-clang-12 python3-pip curl gnupg gnupg2
pip3 install --prefix=/usr/local libclang==14.0.1 pysarif

PODMAM_SUB_REPO="/kubic:/libcontainers:/stable/xUbuntu_20.04/"
PODMAN_REPO="https://download.opensuse.org/repositories/devel:$PODMAM_SUB_REPO"

echo "deb $PODMAN_REPO /" | tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
curl -L "$PODMAN_REPO/Release.key" | apt-key add -
apt-get update && apt-get install -y podman
