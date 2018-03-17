#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2014, 2016, 2017 Guenter Bartsch
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

PICO_TESTS = [
              ('en-US', u'musicians'),
              ('de-DE', u'Andromeda'),
             ]

class TestTTS (unittest.TestCase):

    def test_tts_mary(self):

        config = misc.load_config('.speechrc')
        
        tts = TTS(config.get('tts', 'host'), int(config.get('tts', 'port')))

        # test mary

        tts.engine = 'mary'

        for l, voice, word, ph in MARY_TESTS:

            tts.locale = l
            tts.voice  = voice

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

    def test_tts_espeak(self):

        config = misc.load_config('.speechrc')
        
        tts = TTS(config.get('tts', 'host'), int(config.get('tts', 'port')))

        tts.engine = 'espeak'

        first = True
        for v, word, ph in ESPEAK_TESTS:

            tts.locale = v
            tts.voice  = v

            espeak_ph = tts.gen_ipa (word)

            self.assertEqual (espeak_ph, ph)

            wav = tts.synthesize (word)
            logging.debug('wav len: %d bytes.' % len(wav))
            self.assertGreater (len(wav), 100)

            wav = tts.synthesize (ph, mode='ipa')
            logging.debug('wav len: %d bytes.' % len(wav))
            self.assertGreater (len(wav), 100)

            if first:
                tts.say (word)
                first = False
            # tts.play_wav(wav)

    def test_tts_pico(self):

        config = misc.load_config('.speechrc')
        
        tts = TTS(config.get('tts', 'host'), int(config.get('tts', 'port')))

        tts.engine = 'pico'

        for v, word in PICO_TESTS:

            tts.locale = v
            tts.voice  = v

            wav = tts.synthesize (word)
            logging.debug('wav len: %d bytes.' % len(wav))
            self.assertGreater (len(wav), 100)

            tts.say (word)

if __name__ == "__main__":

    # logging.basicConfig(level=logging.ERROR)
    logging.basicConfig(level=logging.DEBUG)

    unittest.main()

