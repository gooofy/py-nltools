#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2014, 2016, 2017 Guenter Bartsch
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

#
# these tests assume mary is running on localhost:59125

import unittest
import logging

from nltools.maryclient import mary_init, mary_synth_phonemes, mary_gen_phonemes, mary_synth, mary_set_voice, mary_set_locale
from nltools.phonetics import ipa2mary

MARY_TESTS = [
              ('de_DE', 'bits3',            u'UNMUTE',           u"' ? U n - ' m u: - t @"),
              ('de_DE', 'bits3',            u"DÜSTRE",           u"' d Y s - t R @"),
              ('de_DE', 'bits3',            u"EINGANGE",         u"' aI - N a - N @"),
              ('en_US', 'cmu-rms-hsmm',     u'hello',            u"h @ - ' l @U"),
              ('fr_FR', 'upmc-pierre-hsmm', u'bonjour',          u"' b o~ - Z u R"),
             ]

class TestMaryClient (unittest.TestCase):

    def test_mary(self):

        mary_init()

        for l, voice, word, ph in MARY_TESTS:

            mary_set_locale(l)
            mary_set_voice(voice)

            mary_ph = mary_gen_phonemes (word)

            self.assertEqual (mary_ph, ph)

            wav = mary_synth (word)
            logging.debug('wav len: %d bytes.' % len(wav))
            self.assertGreater (len(wav), 100)

            wav = mary_synth_phonemes (ph)
            logging.debug('wav len: %d bytes.' % len(wav))
            self.assertGreater (len(wav), 100)


if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)
    # logging.basicConfig(level=logging.DEBUG)

    unittest.main()

