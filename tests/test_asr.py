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

import unittest
import logging
import wave
import struct

from nltools.asr import ASR, ASR_ENGINE_NNET3, ASR_ENGINE_POCKETSPHINX
from nltools     import misc

TEST_WAVE_EN       = 'tests/foo.wav'
TEST_WAVE_EN_TS    = 'ah indeed'
TEST_WAVE_EN_TS_PS = 'aha indeed'

POCKETSPHINX_MODELDIR  = 'models/cmusphinx-cont-voxforge-en-latest'
POCKETSPHINX_MODELNAME = 'voxforge'

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

    def test_asr_pocketsphinx(self):

        asr = ASR(engine = ASR_ENGINE_POCKETSPHINX, model_dir = POCKETSPHINX_MODELDIR, model_name = POCKETSPHINX_MODELNAME)

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

        self.assertEqual(s.strip(), TEST_WAVE_EN_TS_PS)


if __name__ == "__main__":

    # logging.basicConfig(level=logging.ERROR)
    logging.basicConfig(level=logging.DEBUG)

    unittest.main()

