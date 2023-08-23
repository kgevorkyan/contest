#!/bin/bash

DATE="$(date '+%Y_%m_%d_%H_%M_%S')"
RESULT_DIR="$(realpath "results_dir_$DATE")"
TESTS_BC="$RESULT_DIR/tests"
ROOT_DIR="$(realpath "$(dirname "$(readlink -f "$0")")")"
RESOURCES="$ROOT_DIR/resources"
TESTS_DIR="$RESOURCES/test_suites"
TRUE_REPORTS="$RESOURCES/test_suites.true_reports.sarif"
RES="result_sarif_files"

function execute() {
  COMMAND="$1"
  GOAL="$2"

  echo "$GOAL : running"
  eval "$COMMAND" || exit 1
  echo "$GOAL : done"
}

function check_tools_list_file() {
  if [ ! -f "$TOOLS_LIST" ]; then
    echo "TOOLS_LIST variable must contain a path to file containing urls list of tools" && exit 1
  fi
  TOOLS_LIST="$(realpath "$TOOLS_LIST")"
}

function check_env() {
  check_tools_list_file
}

function clean_container_image() {
  NAME="$1"
  podman rm -f "$C_NAME"
  podman image rm -f "$IMG_NAME"
}

function run_tool() {
  URL="$1"
  RUNNER="run_over_all_bc.sh"
  HASH_FOR_NAME="$(echo -n "$DATE$URL" | md5sum | cut -d ' ' -f 1)"
  REPO_NAME="$(echo "$github_url" | awk -F'/' '{print $NF}')"
  REPO_DIR="$REPO_NAME"_"$HASH_FOR_NAME"
  IMG_NAME="$HASH_FOR_NAME"
  C_NAME="$HASH_FOR_NAME"

  C_WD="/root"
  C_TESTS_BC="$C_WD/tests_bc"
  C_RESULTS="$C_WD/$RES"

  export GIT_TERMINAL_PROMPT=0
  git clone "$URL" "$REPO_DIR" || return 1
  podman build -t "$IMG_NAME" "$REPO_DIR" || return 1
  podman run --name "$C_NAME" -dit "$IMG_NAME" || return 1

  podman cp "$RESOURCES/$RUNNER" "$C_NAME:$C_WD" || { clean_container_image; return 1; }
  podman cp "$TESTS_BC" "$C_NAME:$C_TESTS_BC" || { clean_container_image; return 1; }
  RUN_SH="$(podman exec "$C_NAME" find "$C_WD" -name "run.sh" -executable -print -quit)"
  podman exec $C_NAME bash -c "bash $C_WD/$RUNNER $RUN_SH $C_TESTS_BC $C_RESULTS" || \
        { clean_container_image; return 1; }
  podman cp "$C_NAME:$C_RESULTS" "$REPO_DIR" || { clean_container_image; return 1; }

  clean_container_image
}

function run_tools() {
  MSG="getting results for each tool"

  execute "mkdir -p '$RESULT_DIR' '$TESTS_BC' && cd '$RESULT_DIR'" \
          "creating $RESULT_DIR as a result directory and redirect"

  execute "bash $RESOURCES/get_all_bitcode_files.sh $TESTS_DIR $TESTS_BC" \
          "generating bitcode files from tests"

  echo "$MSG : running"

  while IFS= read -r URL || [ -n "$URL" ]; do
    run_tool "$URL"

    if [ "$?" -eq 0 ]; then
      echo "$URL" >> "$RESULT_DIR/tools.succeed"
    else
      echo "$URL" >> "$RESULT_DIR/tools.failed"
    fi
  done < "$TOOLS_LIST"

  echo "$MSG : done"
}

function main() {
  check_env
  run_tools
  python3 "$ROOT_DIR/evaluate.py" \
          --test "$TESTS_DIR" --tools-results "$RESULT_DIR" --true-reports "$TRUE_REPORTS"
}

main "$@"
