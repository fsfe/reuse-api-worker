# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2019 Free Software Foundation Europe e.V.

# The resulting Docker image imitates an actual working server to run
# local test on your machine. Start it with docker-compose to set the
# necessary environment.

FROM debian:bullseye-slim

ENV API_ENV=devel
ENV PATH=$PATH:/home/reuse/bin

# Prepare for Ansible
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y ansible python aptitude openssh-server

COPY . /tmp/reuse-api
WORKDIR /tmp/reuse-api/worker-setup
# Let ansible run on this Docker image, not the productive inventory
RUN echo '[reuse_api_servers] \nlocalhost ansible_connection=local' > inv.ini
# Run Ansible on local Docker container
RUN ansible-playbook -i inv.ini setup.yml

# Create logfiles
RUN touch /tmp/ssh.log /tmp/reuse.log

# Start SSH daemon in foregound, and read log files
RUN mkdir /var/run/sshd
CMD /usr/sbin/sshd -E /tmp/ssh.log && tail -f /tmp/*.log
