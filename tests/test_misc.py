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

import unittest
import logging

from nltools import misc

class TestMisc (unittest.TestCase):

    def test_load_config(self):

        cfg = misc.load_config()

        port = int(cfg.get('tts', 'port'))

        self.assertEqual (port, 8300)


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

if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)
    
    unittest.main()

