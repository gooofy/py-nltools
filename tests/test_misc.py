#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2013, 2014, 2016, 2017 Guenter Bartsch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import shutil
import tempfile
import os.path
import unittest
import logging

from nltools import misc

class TestMisc (unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_config(self):

        cfg = misc.load_config('.speechrc')

        host = cfg.get('tts', 'host')

        self.assertEqual (host, 'local')


    def test_compress_ws(self):

        self.assertEqual (misc.compress_ws(u'   abc cde   12   '), u' abc cde 12')

    def test_run_command(self):

        txt = ''
        for line in misc.run_command(['uname', '-a']):
            txt += line.strip()

        self.assertEqual('Linux' in txt, True)

    def test_tex(self):

        self.assertEqual(misc.tex_decode('"uber'), u'\xfcber')
        self.assertEqual(misc.tex_decode('da"s'), u'daß')

        self.assertEqual(misc.tex_encode(u'über'), '"uber')
        self.assertEqual(misc.tex_encode(u'daß'), 'da"s')

    def test_edit_distance(self):

        self.assertEqual(misc.edit_distance('hubba', 'hubba'), 0)
        self.assertEqual(misc.edit_distance('hubba', 'hubb'), 1)
        self.assertEqual(misc.edit_distance('hubba', 'hub'), 2)
        self.assertEqual(misc.edit_distance('hubba', 'bba'), 2)

    def test_limit_str(self):

        self.assertEqual(misc.limit_str('1234567890', 10), '1234567890')
        self.assertEqual(misc.limit_str('1234567890',  9), '123456...')

    def test_render_template(self):
        # given
        template_text = """VAR1={{val1}}
        VAR2={{val2}}
        """

        val1 = "v1"
        val2 = "v2"

        expected_text = """VAR1=%s
        VAR2=%s
        """ % (val1, val2)

        src_path = os.path.join(str(self.test_dir), "src.txt")
        dst_path = os.path.join(str(self.test_dir), "dst.txt")

        with open(src_path, "wt") as f:
            f.write(template_text)

        # when
        misc.render_template(src_path, dst_path, val1=val1, val2=val2)

        # then
        with open(dst_path) as f:
            actual_text = f.read()

        self.assertEqual(expected_text, actual_text)


if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)
    
    unittest.main()

