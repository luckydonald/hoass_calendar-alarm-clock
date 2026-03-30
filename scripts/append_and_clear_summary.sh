#!/usr/bin/env bash

# Resolve the full path of the script, even if it was called via a symlink
SOURCE="${BASH_SOURCE[0]}"
while [ -h "${SOURCE}" ]; do   # resolve ${SOURCE} until the file is no longer a symlink
  DIR="$(cd -P "$(dirname "${SOURCE}")" && pwd)"
  SOURCE="$(readlink "${SOURCE}")"
  # If ${SOURCE} was a relative symlink, prepend the directory where the symlink resides
  [[ ${SOURCE} != /* ]] && SOURCE="${DIR}/${SOURCE}"
done

# Directory containing the script
SCRIPT_DIR="$(cd -P "$(dirname "${SOURCE}")" && pwd)"
# echo "Script directory: ${SCRIPT_DIR}"

ROOT_DIR="$(cd -P "$(dirname "${SCRIPT_DIR}")" && pwd)"
echo "Project directory: ${ROOT_DIR}"


SUMMARY_MD="ai/summary.md"
SUMMARY_MD_FULL="${ROOT_DIR}/${SUMMARY_MD}"
QUERY_MD="ai/query.md"
QUERY_MD_FULL="${ROOT_DIR}/${QUERY_MD}"

SUMMARY=$(cat "${SUMMARY_MD_FULL}")
# remove leading \n
SUMMARY="${SUMMARY#$'\n'}"
# remove trailing \n
SUMMARY="${SUMMARY%$'\n'}"


echo "" >> "${QUERY_MD_FULL}"
echo "${SUMMARY}" >> "${QUERY_MD_FULL}"
echo "" > "${SUMMARY_MD_FULL}"

echo "Appended summary to ${QUERY_MD} and truncated ${SUMMARY_MD}."
