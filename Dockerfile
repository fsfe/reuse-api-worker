# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2019 Free Software Foundation Europe e.V.

FROM debian

EXPOSE 22

RUN apt update -y && apt upgrade -y

RUN apt install -y ansible python aptitude
RUN echo "localhost ansible_connection=local" > inv

COPY . .
RUN ansible-playbook -i inv ./worker-setup/setup.yml

CMD echo "success"
