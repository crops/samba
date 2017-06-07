# Copyright (C) 2015-2016 Intel Corporation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

FROM ubuntu:16.04

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
