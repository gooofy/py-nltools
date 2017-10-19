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
import time

from nltools.pulserecorder import PulseRecorder

SOURCE              = 'CM108'
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

    logging.basicConfig(level=logging.INFO)
    
    unittest.main()

