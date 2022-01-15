# Copyright (C) 2015-2016 Intel Corporation
# Copyright (C) 2022 Konsulko Group`
#
# SPDX-License-Identifier: GPL-2.0-only
#

FROM ubuntu:18.04

USER root

RUN apt-get -y update && \
    apt-get -y install samba && \
    apt-get clean && \
    groupadd -g 1000 smbuser && \
    useradd -m -u 1000 -g 1000 smbuser

COPY samba.sh /usr/bin/
COPY smb.conf /etc/samba/
RUN chmod +x /usr/bin/samba.sh

CMD ["samba.sh"]
