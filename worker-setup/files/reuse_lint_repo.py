#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2023 DB Systel GmbH
# SPDX-FileContributor: Max Mehl

"""
Handler between the REUSE API and the Docker image in which the actual REUSE
lint is executed
"""

import argparse
import hashlib
import json
import logging
import re
import sys
from uuid import uuid4

import docker

parser = argparse.ArgumentParser(description=__doc__)

# Arguments
parser.add_argument(
    "-r",
    "--repository",
    dest="repo",
    required=True,
    help="URL of the repository to lint and to generate the SPDX SBOM for",
)
parser.add_argument(
    "-g",
    "--global-options",
    dest="opt_glob",
    action="append",
    default=[],
    help="Global option for all REUSE commands. Can be used multiple times",
)
parser.add_argument(
    "-l",
    "--lint-options",
    dest="opt_lint",
    action="append",
    default=[],
    help="Additional option for `reuse lint`. Can be used multiple times",
)
parser.add_argument(
    "-s",
    "--spdx-options",
    dest="opt_spdx",
    action="append",
    default=[],
    help="Additional option for `reuse spdx`. Can be used multiple times",
)
parser.add_argument(
    "--stdout-log",
    dest="stdoutlog",
    action="store_true",
    help=(
        "Also log to stdout in addition to the logfile. If used in combination "
        "with -v, verbose logs are sent to both channels"
    ),
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Create verbose output (DEBUG log level)",
)


# Constants
DOCKER_IMAGE = "reuse-api-worker-runner"


def nospecialchars(string: str) -> str:
    """Remove all special chars from a string"""
    return "".join(e for e in string if e.isalnum())


def repourl_to_name(url: str) -> str:
    """Convert a repository URL to user_repo, removing all special chars"""
    url = url.rstrip("/")
    user = nospecialchars(url.split("/")[-2])
    repo = nospecialchars(url.split("/")[-1])

    return f"{user}_{repo}"


def start_container(
    image: str, name: str, env: list
) -> docker.models.containers.Container:
    """Start the Docker container and handle potential issues"""
    # Try to find container. If it exists, delete it
    try:
        container = dclient.containers.get(name)
        log.warning("A container with the name %s already exists. Removing it", name)
        container.remove(force=True)
    except docker.errors.NotFound:
        log.debug("Container name %s is still available", name)

    # Try to start container
    try:
        log.debug("Starting container %s", name)
        container = dclient.containers.run(
            image, environment=env, name=name, detach=True
        )
    except docker.errors.ContainerError as err:
        log.critical("Docker container wasn't able to start: %s", err)
        sys.exit(1)

    return container


def run_check(
    container: docker.models.containers.Container, repourl: str
) -> tuple[int, str]:
    """Run check-git.sh inside of container and return exit code and output"""
    container_name = container.name
    try:
        log.debug("Running check-git.sh in container %s", container_name)
        exit_code, output = container.exec_run(cmd=["check-git.sh", repourl])
        log.info("Container %s exited with code %s", container_name, exit_code)
    except Exception as err:  # pylint: disable=broad-except
        log.error("An error running check-git.sh occured: %s", err)
        sys.exit(1)
    finally:
        # Delete Docker container (this is necessary because if we had `remove=True`
        # in the run command, we couldn't access the output in case of an error :/)
        log.debug("Force-removing container %s", container_name)
        container.remove(force=True)

    # Return decoded results
    return exit_code, output.decode("UTF-8")


def split_container_output(text: str, separator: str) -> list:
    """Split reuse output in parts"""
    parts = re.split(rf"\n(?={separator} *)", text)
    # Remove separators from all parts, and return
    return list(map(lambda x: x.replace(f"{separator}\n", ""), parts))


def main():
    """Main function"""
    log.info(
        "Check repo %s with optional arguments. Global:%s, Lint:%s, SPDX:%s",
        args.repo,
        args.opt_glob,
        args.opt_lint,
        args.opt_spdx,
    )

    # Check if image exists
    try:
        dclient.images.get(DOCKER_IMAGE)
    except docker.errors.ImageNotFound as err:
        log.critical("Docker image for local REUSE check does not exist: %s", err)
        sys.exit(1)

    # Create separator and container name
    # random, 6-digit string as session ID
    sessionid = uuid4().hex[:6]
    # Convert e.g. https://git.fsfe.org/reuse/api to reuse_api
    reponame = repourl_to_name(args.repo)
    # Define docker container name (reponame + repoid), e.g. reuse_api_45bb0095
    dname = f"{reponame}_{REPOID}"
    # Define separator containing a random piece (repoid + sessionid), e.g.
    # REUSE-separator-45bb0095-abc123
    separator = f"REUSE-separator-{REPOID}-{sessionid}"

    # Set environment for Docker container running check-git.sh
    env = [
        f"REUSE_GLOBAL_OPTIONS={' '.join(args.opt_glob)}",
        f"REUSE_LINT_OPTIONS={' '.join(args.opt_lint)}",
        f"REUSE_SPDX_OPTIONS={' '.join(args.opt_spdx)}",
        f"SEPARATOR={separator}",
    ]

    # Run Docker image under given name with the newly created ENV file
    dcont = start_container(DOCKER_IMAGE, dname, env)

    # Run check-git.sh script inside of the container
    exit_code, output = run_check(dcont, args.repo)

    # Split output into separate parts
    try:
        lint_output, spdx_output = split_container_output(output, separator)
    except ValueError as err:
        log.warning(
            "Unable to split output into parts. Probably the earlier check command failed: %s",
            err,
        )
        log.warning("Only passing lint output, removing all others")
        lint_output = output
        spdx_output = None

    # Put parts into dict, and echo it (so SSH can see it)
    result = {
        "exit_code": exit_code,
        "lint_output": lint_output,
        "spdx_output": spdx_output,
    }
    print(json.dumps(result))
    # Exit with the check-git.sh exit code (which is the lint exit code)
    sys.exit(exit_code)


if __name__ == "__main__":
    # Load args
    args = parser.parse_args()
    # Create short hash for URL
    REPOID = hashlib.sha256(args.repo.encode("utf-8")).hexdigest()[:8]

    # Logging
    handlers = [logging.FileHandler("/tmp/reuse.log")]
    # Also log to stdout if --stdout-log
    if args.stdoutlog:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(
        format="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        # Log to file by default
        handlers=handlers,
    )

    # Start logger, providing the repo-ID
    log = logging.getLogger(REPOID)
    # Set loglevel based on --verbose flag
    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    # Initiate Docker client
    try:
        dclient = docker.from_env()
    except docker.errors.DockerException as err_daemon:
        log.critical("Docker daemon does not seem to be available: %s", err_daemon)
        sys.exit(1)

    main()
