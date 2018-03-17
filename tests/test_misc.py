#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2013, 2014, 2016, 2017, 2018 Guenter Bartsch
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
#

import shutil
import tempfile
import os.path
import unittest
import logging

from nltools           import misc
from nltools.tokenizer import tokenize

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

        self.assertEqual (misc.edit_distance('hubba', 'hubba'), 0)
        self.assertEqual (misc.edit_distance('hubba', 'hubb'), 1)
        self.assertEqual (misc.edit_distance('hubba', 'hub'), 2)
        self.assertEqual (misc.edit_distance('hubba', 'bba'), 2)

        self.assertEqual (misc.edit_distance(
                             tokenize(u'die leistung wurde zurückverlangt'), 
                             tokenize(u'die leistung wurde zurückverlangt')), 0)
        self.assertEqual (misc.edit_distance(
                             tokenize(u'die leistung wurde'), 
                             tokenize(u'die leistung wurde zurückverlangt')), 1)
        self.assertEqual (misc.edit_distance(
                             tokenize(u'DIE LEISTUNG'), 
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT')), 2)
        self.assertEqual (misc.edit_distance(
                             tokenize(u'DIE'), 
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT')), 3)
        self.assertEqual (misc.edit_distance(
                             tokenize(u'DIE ZURÜCKVERLANGT'), 
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT')), 2)
        self.assertEqual (misc.edit_distance(
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT'), 
                             tokenize(u'LEISTUNG WURDE ZURÜCKVERLANGT')), 1)
        self.assertEqual (misc.edit_distance(
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT'), 
                             tokenize(u'WURDE ZURÜCKVERLANGT')), 2)
        self.assertEqual (misc.edit_distance(
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT'), 
                             tokenize(u'ZURÜCKVERLANGT')), 3)
        self.assertEqual (misc.edit_distance(
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT'), 
                             tokenize(u'')), 4)
        self.assertEqual (misc.edit_distance(
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT'), 
                             tokenize(u'LEISTUNG FOO ZURÜCKVERLANGT')), 2)
        self.assertEqual (misc.edit_distance(
                             tokenize(u'SIE IST FÜR DIE LEISTUNG DANKBAR'), 
                             tokenize(u'SIE STRITTIG LEISTUNG DANKBAR')), 3)

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

