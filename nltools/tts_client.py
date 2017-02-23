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
from base64 import b64encode
import logging
import requests
import urllib

MARY_VOICES = {

    'en_US': { 'male':   [ "cmu-rms-hsmm", "dfki-spike", "dfki-obadiah", "dfki-obadiah-hsmm", "cmu-bdl-hsmm"],
               'female': [ "cmu-slt-hsmm", "dfki-poppy", "dfki-poppy-hsmm", "dfki-prudence", "dfki-prudence-hsmm" ]
             },

    'de_DE': { 'male':   ["bits3", "bits3-hsmm", "dfki-pavoque-neutral", "dfki-pavoque-neutral-hsmm", "dfki-pavoque-styles"],
               'female': ["bits1-hsmm"]
             }
    }

ESPEAK_VOICES = ['en', 'de']


class TTSClient(object):

    def __init__(self, host_tts='localhost', port_tts=8300, locale='en_US', engine='mary', voice='cmu-rms-hsmm'):

        self.host_tts = host_tts
        self.port_tts = port_tts
        self.locale  = locale
        self.engine = engine
        self.voice  = voice

    def set_locale(self, locale):
        self.locale = locale

    def set_voice(self, voice):
        self.voice = voice

    def set_engine(self, engine):
        self.engine = engine

    def synthesize(self, utterance, mode='txt'):

        args = {'l': self.locale,
                'v': self.voice,
                'e': self.engine,
                'm': mode,
                't': utterance.encode('utf8')}
        url = 'http://%s:%s/tts/synth?%s' % (self.host_tts, self.port_tts, urllib.urlencode(args))

        response = requests.get(url)

        assert response.status_code == 200

        wav = response.content

        return wav

    def play_wav (self, wav, async=False):

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

        args = {'l': self.locale,
                'v': self.voice,
                'e': self.engine,
                't': word.encode('utf8')}
        url = 'http://%s:%s/tts/g2p?%s' % (self.host_tts, self.port_tts, urllib.urlencode(args))

        response = requests.get(url)

        assert response.status_code == 200

        return response.json()['ipa']


