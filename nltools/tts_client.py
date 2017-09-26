#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2016, 2017 Guenter Bartsch
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
# client utility functions to access our HTTP TTS server
#

import traceback
import json
import logging
import requests
import urllib

from base64                 import b64encode
from nltools.pulseplayer    import PulsePlayer
from nltools.maryclient     import mary_init, mary_set_voice, mary_set_locale, mary_synth,\
                                   mary_synth_phonemes, mary_gen_phonemes
from nltools.phonetics      import ipa2mary, mary2ipa, ipa2xsampa, xsampa2ipa
from espeakng               import ESpeakNG

MARY_VOICES = {

    'en_US': { 'male':   [ "cmu-rms-hsmm", "dfki-spike", "dfki-obadiah", "dfki-obadiah-hsmm", "cmu-bdl-hsmm"],
               'female': [ "cmu-slt-hsmm", "dfki-poppy", "dfki-poppy-hsmm", "dfki-prudence", "dfki-prudence-hsmm" ]
             },

    'de_DE': { 'male':   ["bits3", "bits3-hsmm", "dfki-pavoque-neutral", "dfki-pavoque-neutral-hsmm", "dfki-pavoque-styles"],
               'female': ["bits1-hsmm"]
             }
    }
DEFAULT_MARY_VOICE   = 'cmu-rms-hsmm'
DEFAULT_MARY_LOCALE  = 'en_US'

ESPEAK_VOICES = ['english-us', 'de']

class TTSClient(object):

    def __init__(self, host_tts='local', port_tts=8300, locale='en_US', engine='mary', voice='cmu-rms-hsmm'):

        self.host_tts = host_tts
        self.port_tts = port_tts
        self.locale  = locale
        self.engine = engine
        self.voice  = voice

        if host_tts == 'local':

            self.player = PulsePlayer('Local TTS Client')

            mary_init()
            mary_set_voice  (DEFAULT_MARY_VOICE)
            mary_set_locale (DEFAULT_MARY_LOCALE)

            self.espeak = ESpeakNG()

    def set_locale(self, locale):
        self.locale = locale

    def set_voice(self, voice):
        self.voice = voice

    def set_engine(self, engine):
        self.engine = engine

    def synthesize(self, txt, mode='txt'):

        if self.host_tts == 'local':

            wav = None

            if self.engine == 'mary':

                mary_set_voice  (self.voice)
                mary_set_locale (self.locale)

                if mode == 'txt':
                    wav = mary_synth (txt)
                elif mode == 'ipa':
                    xs = ipa2mary ('ipa', txt)
                    wav = mary_synth_phonemes (xs)
                else:
                    raise Exception ("unknown mary mode '%s'" % mode)

            elif self.engine == 'espeak':

                if mode == 'txt':

                    self.espeak.voice = self.voice
                    wav = self.espeak.synth_wav (txt)

                elif mode == 'ipa':
                    xs = ipa2xsampa ('ipa', txt)
                    logging.debug ('synthesize: %s %s -> %s' % (txt, mode, repr(xs)))
                    wav = self.espeak.synth_wav (xs, fmt='xs')

                else:
                    raise Exception ("unknown espeak mode '%s'" % mode)
            else:

                raise Exception ("unknown engine '%s'" % self.engine)

        else:

            args = {'l': self.locale,
                    'v': self.voice,
                    'e': self.engine,
                    'm': mode,
                    't': txt.encode('utf8')}
            url = 'http://%s:%s/tts/synth?%s' % (self.host_tts, self.port_tts, urllib.urlencode(args))

            response = requests.get(url)

            if response.status_code != 200:
                return None

            wav = response.content

        if wav:
            logging.debug ('synthesize: %s %s -> WAV' % (txt, mode))
        else:
            logging.error ('synthesize: %s %s -> NO WAV' % (txt, mode))

        return wav

    def play_wav (self, wav, async=False):

        if self.host_tts == 'local':

            if wav:
                self.player.play(wav, async)
            else:
                raise Exception ('no wav given')

        else:

            url = 'http://%s:%s/tts/play' % (self.host_tts, self.port_tts)
                          
            if async:
                url += '?async=t'

            response = requests.post(url, data=wav)

    def say (self, utterance, async=False):

        wav = self.synthesize(utterance)
        self.play_wav(wav, async=async)

    def say_ipa (self, ipa, async=False):

        wav = self.synthesize(ipa, mode='ipa')
        self.play_wav(wav, async=async)

    def gen_ipa (self, word):

        if self.host_tts == 'local':

            if self.engine == 'mary':

                mary_set_voice  (self.voice)
                mary_set_locale (self.locale)

                mp = mary_gen_phonemes (word)
                return mary2ipa(word, mp)

            elif self.engine == 'espeak':

                self.espeak.voice = self.voice
                e_ipa = self.espeak.g2p (word, ipa='2')
                xs = ipa2xsampa(word, e_ipa)
                ipa = xsampa2ipa(word, xs)

                logging.debug (u'espeak g2p: %s -> %s -> %s -> %s' % (word, e_ipa, xs, ipa))

                return ipa

            elif self.engine == 'sequitur':

                if not self.voice in SEQUITUR_MODELS:
                    raise Exception ("no sequitur model for voice '%s'" % self.voice)

                return sequitur_gen_ipa (SEQUITUR_MODELS[self.voice], word)

            else:
                raise Exception ("unknown engine '%s'" % self.engine)


        else:
            args = {'l': self.locale,
                    'v': self.voice,
                    'e': self.engine,
                    't': word.encode('utf8')}
            url = 'http://%s:%s/tts/g2p?%s' % (self.host_tts, self.port_tts, urllib.urlencode(args))

            response = requests.get(url)

            if response.status_code != 200:
                return None

            return response.json()['ipa']

