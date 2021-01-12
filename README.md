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

Just run 

``` shell
ansible-playbook setup.yml \
        -i inventory/hosts \
        -l "wrk3.api.reuse.software" \
        # limit to groups \
        # -l "reuse_api_server_ubuntu,reuse_api_server_root" \
```

from the `worker_setup` directory to deploy all hosts given in the inventory.
You need access to the root user of the server.

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


## Local Development

You can imitate the API Worker in a Docker image for local tests (no
production!). There are some specialities with that:

* Instead of the `reuse` user, the root user should execute all checks
* The Docker container does not have its own Docker daemon, but used
  the host's Docker socket
* When spun up this way, you can SSH as root with the `test_ed25519`
  key

To setup everything, follow these steps from within the root of this
repo:

1. Build the reuse-api-worker-runner image that will eventually spin up
   inside the worker for every repo check. Only has to be done once:
   `docker build --no-cache -t reuse-api-worker-runner docker-image/`

2. Build and deploy the REUSE API Worker with:
   `docker-compose up -d --build`

Now you can task the local worker with REUSE checks. You can either do
this via a direct Docker command, or via SSH (just like the REUSE API
does it):

`docker exec reuse-api-worker reuse-lint-repo https://github.com/fsfe/reuse-tool`

`ssh -i ./worker-setup/files/test_ed25519 root@DOCKER-CONTAINER-IP https://git.fsfe.org/reuse/api-worker`

Note that for the latter you enter as root (unlike with the production
API), and you require the container's IP address. In a Docker network,
you can also use the container name `reuse-api-worker`.

## License

GPL-3.0-or-later
