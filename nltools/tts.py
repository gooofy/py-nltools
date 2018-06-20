#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2016, 2017, 2018 Guenter Bartsch
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
# Abstraction layer for multiple TTS engines (Mary TTS, SVOX Pico TTS and eSpeak NG at the moment)
# can run those locally or act as a client for our HTTP TTS server
#

import traceback
import json
import logging
import requests
import urllib

from base64                 import b64encode
from nltools.pulseplayer    import PulsePlayer
from nltools.phonetics      import ipa2mary, mary2ipa, ipa2xsampa, xsampa2ipa
from espeakng               import ESpeakNG
from marytts                import MaryTTS

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

class TTS(object):

    def __init__(self, 
                 host_tts    =        'local', 
                 port_tts    =           8300, 
                 locale      =        'en_US', 
                 engine      =         'mary', 
                 voice       = 'cmu-rms-hsmm',
                 pitch       =             50,  # 0-99
                 speed       =            175): # approx. words per minute

        self._host_tts = host_tts
        self._port_tts = port_tts
        self._locale   = locale
        self._engine   = engine
        self._voice    = voice
        self._pitch    = pitch
        self._speed    = speed

        if host_tts == 'local':
            self.player  = PulsePlayer('Local TTS Client')
            self.espeak  = ESpeakNG()
            self.marytts = MaryTTS()
            self.picotts = None # lazy-loading to reduce package dependencies

    @property
    def locale(self):
        return self._locale
    @locale.setter
    def locale(self, v):
        self._locale = v

    @property
    def engine(self):
        return self._engine
    @engine.setter
    def engine(self, v):
        self._engine = v

    @property
    def voice(self):
        return self._voice
    @voice.setter
    def voice(self, v):
        self._voice = v

    @property
    def pitch(self):
        return self._pitch
    @pitch.setter
    def pitch(self, v):
        self._pitch = v

    @property
    def speed(self):
        return self._speed
    @speed.setter
    def speed(self, v):
        self._speed = v

    def synthesize(self, txt, mode='txt'):

        if self._host_tts == 'local':

            # import pdb; pdb.set_trace()

            wav = None

            if self.engine == 'mary':

                self.marytts.voice  = self._voice
                self.marytts.locale = self._locale

                if mode == 'txt':
                    wav = self.marytts.synth_wav (txt)
                elif mode == 'ipa':
                    xs = ipa2mary ('ipa', txt)
                    wav = self.marytts.synth_wav (xs, fmt='xs')
                else:
                    raise Exception ("unknown mary mode '%s'" % mode)

            elif self.engine == 'espeak':

                if mode == 'txt':

                    self.espeak.voice = self._voice
                    self.espeak.speed = self._speed
                    self.espeak.pitch = self._pitch
                    wav = self.espeak.synth_wav (txt)
                    # logging.debug ('synthesize: %s %s -> %s' % (txt, mode, repr(wav)))

                elif mode == 'ipa':
                    xs = ipa2xsampa ('ipa', txt)
                    logging.debug ('synthesize: %s %s -> %s' % (txt, mode, repr(xs)))
                    wav = self.espeak.synth_wav (xs, fmt='xs')

            elif self.engine == 'pico':

                if mode == 'txt':

                    if not self.picotts:
                        from picotts import PicoTTS
                        self.picotts = PicoTTS()

                    self.picotts.voice = self._voice
                    wav = self.picotts.synth_wav (txt)
                    # logging.debug ('synthesize: %s %s -> %s' % (txt, mode, repr(wav)))

                else:
                    raise Exception ("unknown pico mode '%s'" % mode)
            else:

                raise Exception ("unknown engine '%s'" % self.engine)

        else:

            args = {'l': self._locale,
                    'v': self._voice,
                    'e': self._engine,
                    'm': mode,
                    't': txt.encode('utf8')}
            url = 'http://%s:%s/tts/synth?%s' % (self._host_tts, self._port_tts, urllib.urlencode(args))

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

        if self._host_tts == 'local':

            if wav:
                self.player.play(wav, async)
            else:
                raise Exception ('no wav given')

        else:

            url = 'http://%s:%s/tts/play' % (self._host_tts, self._port_tts)
                          
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

        if self._host_tts == 'local':

            if self.engine == 'mary':

                self.marytts.voice  = self._voice
                self.marytts.locale = self._locale

                mp = self.marytts.g2p (word)
                return mary2ipa(word, mp)

            elif self.engine == 'espeak':

                self.espeak.voice = self._voice
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
            args = {'l': self._locale,
                    'v': self._voice,
                    'e': self._engine,
                    't': word.encode('utf8')}
            url = 'http://%s:%s/tts/g2p?%s' % (self._host_tts, self._port_tts, urllib.urlencode(args))

            response = requests.get(url)

            if response.status_code != 200:
                return None

            return response.json()['ipa']

