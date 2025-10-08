# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2019 Free Software Foundation Europe e.V.

FROM fsfe/reuse

COPY check-git.sh /bin/
COPY wait.sh /bin/

RUN mkdir /project
WORKDIR /project

ENTRYPOINT ["wait.sh"]
