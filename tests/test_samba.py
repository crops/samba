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
import os
import pytest
import shlex
import shutil
import subprocess
import tempfile
import time
import uuid

# This function will wait for a particular string to appear in "docker logs"
# for a container. It polls, but for testing that's fine.
def docker_logs_wait(sentinel, container, timeout):
    cmd = shlex.split("docker logs {}".format(container))

    i = 0
    while (i < timeout):
        output = subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        if sentinel in output.stdout.decode():
            break

        time.sleep(1)
        i = i + 1

    return output.stdout.decode()


@pytest.fixture()
def volume():
    volumename = uuid.uuid4().hex

    cmd = shlex.split("docker volume create --name {}".format(volumename))
    subprocess.run(cmd, check=True)

    cmd = ("docker run --rm -v {}:/workdir busybox chown "
           "-R 1000:1000 /workdir").format(volumename)
    cmd = shlex.split(cmd)
    subprocess.run(cmd, check=True)

    yield volumename

    cmd = shlex.split("docker volume rm {}".format(volumename))
    subprocess.run(cmd, check=True)


@pytest.fixture
def container(testimage, volume):
    contname = uuid.uuid4().hex

    cmd = shlex.split(("docker create -t "
                       "-p 127.0.0.1:445:445 --name {} "
                       "-v {}:/workdir {}").format(contname, volume,
                                                   testimage))
    subprocess.run(cmd, check=True)

    yield contname

    cmd = shlex.split("docker logs {}".format(contname))
    subprocess.run(cmd, check=True)

    cmd = shlex.split("docker rm -f {}".format(contname))
    subprocess.run(cmd, check=True)

@pytest.fixture
def run_samba(container):
    cmd = shlex.split("docker start {}".format(container))
    subprocess.run(cmd, check=True)

    startedstring = ("STATUS=daemon 'smbd' finished starting up and ready to "
                     "serve connections")
    output = docker_logs_wait(startedstring, container, 10)
    assert startedstring in output

    yield

    cmd = shlex.split("docker stop {}".format(container))
    subprocess.run(cmd, check=True)

@pytest.fixture(params=[(0,0), (1000,0), (0,1000)])
def bad_uid_gid(volume, request):
    uid, gid = request.param
    cmd = ("docker run --rm -v {}:/workdir busybox chown "
           "-R {}:{} /workdir").format(volume, uid, gid)
    cmd = shlex.split(cmd)
    subprocess.run(cmd, check=True)

    return request.param

@pytest.fixture
def mount_samba(run_samba, tmpdir):
    mountpoint = str(tmpdir)

    cmd = "sudo mount -t cifs -o guest //127.0.0.1/workdir {}"
    cmd = shlex.split(cmd.format(mountpoint))
    subprocess.run(cmd, check=True)

    yield mountpoint

    cmd = shlex.split("sudo umount {}".format(mountpoint))
    subprocess.run(cmd, check=True)

def test_container_expected_fail(bad_uid_gid, container):
    cmd = shlex.split("docker start {}".format(container))
    subprocess.run(cmd, check=True)

    errorstring = ("The owner of /workdir is not 1000:1000, "
                   "it is {}:{}").format(bad_uid_gid[0], bad_uid_gid[1])
    output = docker_logs_wait(errorstring, container, 10)
    assert errorstring in output

# Just pass because "run samba" essentially is the test
def test_samba_starts(run_samba):
    pass

# Just pass because "mount samba" essentially is the test
def test_mount(mount_samba):
    pass

# Create a file and make sure the uid and gid are correct
def test_create_file(mount_samba):
    mountpoint = mount_samba

    # Create a file as root to really make sure the uid and gid are being
    # set by samba.
    newfile = os.path.join(mountpoint, "testfile")
    cmd = shlex.split("sudo touch {}".format(newfile))

    subprocess.run(cmd, check=True)

    stat_result = os.stat(newfile)
    assert stat_result.st_uid == 1000 and stat_result.st_gid == 1000
