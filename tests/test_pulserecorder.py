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
import time

from nltools.pulserecorder import PulseRecorder

SOURCE              = 'Monitor'
SAMPLERATE          = 16000
VOLUME              = 120

class TestPulseRecorder (unittest.TestCase):

    def test_rec(self):

        recorder = PulseRecorder(SOURCE, SAMPLERATE, VOLUME)
        recorder.start_recording(1000)
        time.sleep(1)
        recorder.stop_recording()

        samples = recorder.get_samples()

        logging.debug(repr(samples))

        self.assertGreater (len(samples), 900)
        


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    
    unittest.main()

