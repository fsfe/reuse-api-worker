<!--
  SPDX-License-Identifier: GPL-3.0-or-later
  SPDX-FileCopyrightText: 2019 Free Software Foundation Europe e.V.
-->

# REUSE API Worker

This repository contains two elements for the REUSE API's worker server:

* The Ansible playbook that initiates (and updates) the worker server
itself. Currently written for an Ubuntu server.
* The Docker image that performs a reuse lint for a Git repository. A
container based on this image is spun up for each check.

It is supposed to be invoked by the [REUSE API
service](https://git.fsfe.org/reuse/api).

## Installation

### Server

Just run `ansible-playbook -i inventory setup.yml` to deploy all hosts
given in the inventory. Make sure that you have SSH access to the given
`ansible_user`, and that this user has sudo permissions to become root.

Note the tags that allow you to only run specific routines.

### Docker image

The Docker image is based on fsfe/reuse and contains the simple script
`check-git.sh` in this repository.

To build the image, run `docker build -t reuse-api .`

## Usage

Running the check is fairly simple:

```text
$ ssh -i ~/.ssh/reuse_ed25519 reuse@wrk1.api.reuse.software reuse-lint-repo https://git.fsfe.org/reuse/website
Cloning into '/project'...

Checking REUSE compliance for commit d3121becd4d715df40ba6b72394582b85d1c5cc9:

# SUMMARY

* Bad licenses:
* Missing licenses:
* Unused licenses:
* Used licenses: AGPL-3.0-or-later, Apache-2.0, CC-BY-SA-4.0, CC0-1.0, GPL-3.0-or-later, MIT, OFL-1.1
* Read errors: 0
* Files with copyright information: 61 / 61
* Files with license information: 61 / 61

Congratulations! Your project is compliant with version 3.0 of the REUSE Specification :-)
```

The exit codes of this command can be evaluated in a later stage, so that a web service could decide which badge to display.

## License

GPL-3.0-or-later
