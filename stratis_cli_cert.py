# Copyright 2019 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Tests of the stratis CLI.
"""

import argparse
import sys
import time
import unittest

from testlib.utils import exec_command, process_exists
from testlib.stratis import StratisCli, STRATIS_CLI, fs_n, p_n

DISKS = []


class StratisCertify(unittest.TestCase):
    """
    Unit tests for Stratis
    """

    def setUp(self):
        """
        Ensure we are ready, which includes stratisd process is up and running
        and we have an empty configuration.  If not we will attempt to make
        the configuration empty.
        :return: None
        """
        self.addCleanup(self._clean_up)

        # The daemon should already be running, if not lets starts it and wait
        # a bit
        if process_exists("stratisd") is None:
            exec_command(["systemctl", "start", "stratisd"])
            time.sleep(20)

        StratisCli.destroy_all()
        self.assertEqual(0, len(StratisCli.pool_list()))

    def _clean_up(self):
        """
        If an exception in raised in setUp, tearDown will not be called, thus
        we will place our cleanup in a method which is called after tearDown
        :return: None
        """
        StratisCli.destroy_all()
        self.assertEqual(0, len(StratisCli.pool_list()))

    def test_daemon_redundancy(self):
        """
        Test daemon redundancy returns expected values.
        :return:
        """
        self.assertEqual(("NONE", 0), StratisCli.daemon_redundancy())

    @unittest.expectedFailure
    def test_no_args(self):  # pylint: disable=no-self-use
        """
        Ref. https://github.com/stratis-storage/stratis-cli/issues/248
        :return: None
        """
        exec_command([STRATIS_CLI], 2)
        exec_command([STRATIS_CLI, "daemon"], 2)

    def test_no_list_listings(self):
        """
        Test that commands that optionally take a list work both ways.
        :return: None
        """
        pool_name = p_n()
        fs_name = fs_n()
        StratisCli.pool_create(pool_name, block_devices=DISKS)
        StratisCli.fs_create(pool_name, fs_name)

        self.assertEqual(StratisCli.pool_list(), StratisCli.pool_list(False))
        self.assertEqual(StratisCli.fs_list(), StratisCli.fs_list(False))
        self.assertEqual(StratisCli.blockdev_list(), StratisCli.blockdev_list(False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--disk", action="append", dest="DISKS", help="disks to use", required=True
    )
    disks, args = ap.parse_known_args()
    DISKS = disks.DISKS
    print("Using block device(s) for tests: %s" % DISKS)
    unittest.main(argv=sys.argv[:1] + args)
