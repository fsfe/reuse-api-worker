# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2019 Free Software Foundation Europe e.V.

# The resulting Docker image imitates an actual working server to run
# local test on your machine. Start it with docker-compose to set the
# necessary environment.

FROM debian:buster-slim

ENV API_ENV=devel
ENV PATH=$PATH:/home/reuse/bin

# Prepare for Ansible
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y ansible python aptitude openssh-server

# Let ansible run on this Docker image, not the productive inventory
RUN echo "localhost ansible_connection=local" > inv

# Run Ansible
COPY . .
RUN ansible-playbook -i inv ./worker-setup/setup.yml

# Create logfile
RUN touch /tmp/reuse.log

# Start SSH daemon in foregound, and read log file
RUN mkdir /var/run/sshd
CMD /usr/sbin/sshd -E /tmp/reuse.log && tail -f /tmp/reuse.log
