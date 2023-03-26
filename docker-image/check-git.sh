#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2019 Free Software Foundation Europe e.V.
# SPDX-FileCopyrightText: 2023 DB Systel GmbH

# This script is executed in the reuse-api-worker-runner Docker image. It runs
# lint and spdx, and returns the output with a random separator, and the exit
# code of lint.
#
# The only normal argument is $1, the Git repo URL. It takes its further option
# as ENV variables: REUSE_GLOBAL_OPTIONS, REUSE_LINT_OPTIONS,
# REUSE_SPDX_OPTIONS, SEPARATOR
#
# The script assumes that the current working directory is /project

# Git repo
GIT="${1}"

# Test if remote repository is valid
if ! timeout 5 git ls-remote "${GIT}" > /dev/null; then
  echo "${GIT} is not a valid git repository"
  exit 42
fi
# Test if there is no separator provided
if [ -z "${SEPARATOR}" ]; then
  echo "No separator provided as environment variable"
  exit 43
fi

# Cloning git repo without output
git clone -q --depth 1 "${GIT}" /project

# Running reuse lint with optional parameters
# shellcheck disable=SC2086
lint_output="$(reuse ${REUSE_GLOBAL_OPTIONS} lint ${REUSE_LINT_OPTIONS})"
lint_status=$?

# Running reuse spdx with optional parameters
# shellcheck disable=SC2086
spdx_output="$(reuse ${REUSE_GLOBAL_OPTIONS} spdx ${REUSE_SPDX_OPTIONS})"

# Paste output of lint and spdx, separated by $SEPARATOR
cat << EOF
${lint_output}
${SEPARATOR}
${spdx_output}
EOF

# Exit with lint code
exit $lint_status
