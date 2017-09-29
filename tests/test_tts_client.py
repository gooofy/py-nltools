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
# these tests read tts settings from ~/.speechrc
#

import unittest
import logging

from nltools.tts import TTS
from nltools     import misc

MARY_TESTS = [
              ('de_DE', 'bits3',            u'UNMUTE',           u"'\u0294\u028an-'mu\u02d0-t\u0259"),
              ('de_DE', 'bits3',            u"DÜSTRE",           u"'d\u028fs-t\u0281\u0259"),
              ('de_DE', 'bits3',            u"EINGANGE",         u"'a\u026a-\u0273a-\u0273\u0259"),
              ('en_US', 'cmu-rms-hsmm',     u'hello',            u"h\u0259-'l\u0259\u028a"),
              ('fr_FR', 'upmc-pierre-hsmm', u'bonjour',          u"'bo-\u0292u\u0281"),
             ]

ESPEAK_TESTS = [
                ('de', u'GELBSEIDENEN',     u"g'\u025blbza\u026ad\u0259n\u0259n"),
                ('de', u'UNMUTE',           u"'\u028anmu\u02d0t\u0259"),
               ]
class TestTTS (unittest.TestCase):

    def test_tts(self):

        config = misc.load_config('.speechrc')
        
        tts = TTS(config.get('tts', 'host'), int(config.get('tts', 'port')))

        # test mary

        tts.set_engine('mary')

        for l, voice, word, ph in MARY_TESTS:

            tts.set_locale(l)
            tts.set_voice(voice)

            mary_ph = tts.gen_ipa (word)

            self.assertEqual (mary_ph, ph)

            wav = tts.synthesize (word)
            logging.debug('wav len: %d bytes.' % len(wav))
            self.assertGreater (len(wav), 100)

            wav = tts.synthesize (ph, mode='ipa')
            logging.debug('wav len: %d bytes.' % len(wav))
            self.assertGreater (len(wav), 100)

            # tts.say (word)
            # tts.play_wav(wav)

        # test espeak

        tts.set_engine('espeak')

        for v, word, ph in ESPEAK_TESTS:

            tts.set_locale(v)
            tts.set_voice(v)

            espeak_ph = tts.gen_ipa (word)

            self.assertEqual (espeak_ph, ph)

            wav = tts.synthesize (word)
            logging.debug('wav len: %d bytes.' % len(wav))
            self.assertGreater (len(wav), 100)

            wav = tts.synthesize (ph, mode='ipa')
            logging.debug('wav len: %d bytes.' % len(wav))
            self.assertGreater (len(wav), 100)

            # tts.say (word)
            # tts.play_wav(wav)

if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)
    # logging.basicConfig(level=logging.DEBUG)

    unittest.main()

