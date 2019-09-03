#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2019 Free Software Foundation Europe e.V.

# Git repo
GIT="${1}"
# All further options from ENV variable, provided to docker
OPTIONS="${REUSE_OPT}"

# Test if remote repository is valid
if ! timeout 5 git ls-remote "${GIT}" > /dev/null; then
  echo "${GIT} is not a valid git repository"
  exit 42
fi

# Cloning git repo
git clone --depth 1 "${GIT}" /project

# Running reuse lint with optional parameters
reuse lint "${OPTIONS}"
