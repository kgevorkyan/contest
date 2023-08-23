# this is a very simple script to iterate over all inner directories,
# build and get bitcode files from *.c files
# if there's no *.c file, then it'll just move *.bc files into $RESULT_DIR

function check_args() {
  [ -d "$TESTS_DIR" ] || { echo "tests directory not found: $TESTS_DIR"; exit 1; }
  [ -d "$RESULT_DIR" ] || { echo "results directory not found: $RESULT_DIR"; exit 1; }
}

function check_and_get_bc() {
  SRC_DIR="$1"
  PREFIX="$(echo "$TESTS_DIR" | sed "s/\//_/g")"
  UNIQUE_NAME="$(echo "$SRC_DIR" | sed "s/\//_/g")"
  MAIN_BC="$RESULT_DIR/${UNIQUE_NAME#$PREFIX}.bc"

  C_FILES_NUM="$(find "$SRC_DIR" -maxdepth 1 -type f -name "*.c" | wc -l)"
  if [ "$C_FILES_NUM" -gt 0 ]; then
    clang-12 -c -g -O0 -emit-llvm "$SRC_DIR"/*.c
    llvm-link-12 *.bc -o "$MAIN_BC"
    rm -f *.bc
    [ -f "$MAIN_BC" ] || echo "failed to get bitcode from $SRC_DIR"
  else
    find "$SRC_DIR" -maxdepth 1 -type f -name "*.bc" -exec bash -c 'cp {} $RESULT_DIR' \;
  fi
}

function get_all_bitcode_files() {
  find "$TESTS_DIR" -type d -print0 | while read -r -d $'\0' TMP_DIR; do
    check_and_get_bc "$TMP_DIR"
  done
}

function main() {
  TESTS_DIR="$(realpath "$1")"
  RESULT_DIR="$(realpath "$2")"
  check_args || exit 1
  get_all_bitcode_files

  BC_FILES_NUM="$(find "$RESULT_DIR" -type f -name "*.bc" | wc -l)"
  if [ "$BC_FILES_NUM" -eq 0 ]; then
    echo "No bitcode created!"
    exit 1
  fi
}

main "$@"
