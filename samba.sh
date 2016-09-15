#!/bin/bash
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

shareowner="$(stat -c %u /workdir):$(stat -c %g /workdir)"
if [ "$shareowner" != "1000:1000" ]; then
    echo "The owner of /workdir is not 1000:1000, it is $shareowner. Make" \
	 "sure you specified the correct volume and that the uid and gid are" \
	 "set to 1000."
    exit 1
fi

exec /usr/sbin/smbd -FS
