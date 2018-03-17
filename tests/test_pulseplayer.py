#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2013, 2014, 2016, 2017 Guenter Bartsch
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

import unittest
import logging

from nltools.pulseplayer import PulsePlayer

class TestPulsePlayer (unittest.TestCase):

    def test_playback(self):

        player = PulsePlayer('nltools unittest')

        with open('foo.wav', 'rb') as wavf:
            wav = wavf.read()

            player.play(wav)

if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)
    
    unittest.main()

