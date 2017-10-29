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

import unittest
import logging
import wave
import struct

from nltools.asr import ASR, ASR_ENGINE_NNET3, ASR_ENGINE_POCKETSPHINX
from nltools     import misc

TEST_WAVE_EN    = 'tests/foo.wav'
TEST_WAVE_EN_TS = 'ah indeed'

class TestASR (unittest.TestCase):

    def test_asr_kaldi(self):

        asr = ASR(engine = ASR_ENGINE_NNET3)

        wavf = wave.open(TEST_WAVE_EN, 'rb')

        # check format
        self.assertEqual(wavf.getnchannels(), 1)
        self.assertEqual(wavf.getsampwidth(), 2)

        # process file in 250ms chunks

        chunk_frames = 250 * wavf.getframerate() / 1000
        tot_frames   = wavf.getnframes()

        num_frames = 0
        while num_frames < tot_frames:

            finalize = False
            if (num_frames + chunk_frames) < tot_frames:
                nframes = chunk_frames
            else:
                nframes = tot_frames - num_frames
                finalize = True

            frames = wavf.readframes(nframes)
            num_frames += nframes
            samples = struct.unpack_from('<%dh' % nframes, frames)

            s, l = asr.decode(wavf.getframerate(), samples, finalize)

            if not finalize:
                self.assertEqual(s, None)

        wavf.close()

        self.assertEqual(s.strip(), TEST_WAVE_EN_TS)


if __name__ == "__main__":

    # logging.basicConfig(level=logging.ERROR)
    logging.basicConfig(level=logging.DEBUG)

    unittest.main()

