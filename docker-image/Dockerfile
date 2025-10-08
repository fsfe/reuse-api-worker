# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2019 Free Software Foundation Europe e.V.

FROM fsfe/reuse

RUN mkdir /project

WORKDIR /project

COPY check-git.sh /bin/
COPY wait.sh /bin/

ENTRYPOINT ["wait.sh"]
