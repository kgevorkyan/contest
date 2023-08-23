# this is a very simple runner to iterate over all bitcode files,
# run the tool on each of them and rename reports by their input name

function check_args() {
  [ -d "$WORK_DIR" ] || { echo "working directory not found: $WORK_DIR"; exit 1; }
  [ -f "$TOOL_RUNNER" ] || { echo "runner script not found: $TOOL_RUNNER"; exit 1; }
  rm -rf "$RESULTS_DIR"
  mkdir "$RESULTS_DIR"
}

function run_over_all_bc() {
  find "$WORK_DIR" -type f -name "*.bc" -print0 | while read -r -d $'\0' FILE; do
    bash "$TOOL_RUNNER" "$FILE"
    REPORT="$(basename "$FILE").sarif"
    mv "report.sarif" "$RESULTS_DIR/$(basename "$FILE").sarif" || echo "failed to run on $FILE"
  done
}

function main() {
  TOOL_RUNNER="$(realpath "$1")" || { echo "TOOL_RUNNER must be passed as 1st argument"; exit 1; }
  WORK_DIR="$(realpath "$2")" || { echo "WORK_DIR must be passed as 2nd argument"; exit 1; }
  RESULTS_DIR="$(realpath "$3")" || { echo "RESULTS_DIR must be passed as 3th argument"; exit 1; }
  check_args || exit 1
  run_over_all_bc
}
main "$@"
