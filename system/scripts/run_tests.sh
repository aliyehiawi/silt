#!/usr/bin/env bash
# Run all script tests. From any directory:
#   bash system/scripts/run_tests.sh
# Exit code is non-zero on any failure.
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "== test_transform.py =="
python3 "$DIR/tests/test_transform.py" -v
echo
echo "== test_audit.py =="
python3 "$DIR/tests/test_audit.py" -v
echo
echo "== test_repair_links.py =="
python3 "$DIR/tests/test_repair_links.py" -v
echo
echo
echo "== test_broken_links.py =="
python3 "$DIR/tests/test_broken_links.py" -v
echo
echo "All tests passed."
