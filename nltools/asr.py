#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2017, 2018, 2019 Guenter Bartsch
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
# Abstraction layer for multiple speech recognition engines,
# only kaldi-asr at the moment
#

import traceback
import logging
import time
import re
import struct
import wave
import numpy as np

from base64             import b64encode
from kaldiasr.nnet3     import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder

ASR_ENGINE_NNET3        = 'kaldi-nnet3'

DEFAULT_ENGINE          = ASR_ENGINE_NNET3
DEFAULT_MODEL_DIR       = 'models/kaldi-generic-en-tdnn_f-latest'
DEFAULT_MODEL_NAME      = 'model'
DEFAULT_STREAM_ID       = '__default__'
DEFAULT_SAMPLE_RATE     = 16000

DEFAULT_KALDI_BEAM                      = 7.0 # nnet3: 15.0
DEFAULT_KALDI_ACOUSTIC_SCALE            = 1.0 # nnet3:  0.1
DEFAULT_KALDI_FRAME_SUBSAMPLING_FACTOR  = 3   # nnet3:  1

class ASR(object):

    def __init__(self, 
                 engine      = DEFAULT_ENGINE,
                 model_dir   = DEFAULT_MODEL_DIR,
                 model_name  = DEFAULT_MODEL_NAME,

                 kaldi_beam                     = DEFAULT_KALDI_BEAM,
                 kaldi_acoustic_scale           = DEFAULT_KALDI_ACOUSTIC_SCALE, 
                 kaldi_frame_subsampling_factor = DEFAULT_KALDI_FRAME_SUBSAMPLING_FACTOR, 
                ):

        self._engine      = engine
        self._model_dir   = model_dir
        self._model_name  = model_name
        self.asr_decoders = {} # stream_id -> decoder

        if self._engine == ASR_ENGINE_NNET3:

            logging.debug ('loading ASR model %s from %s...' % (self._model_name, self._model_dir))
            start_time = time.time()
            self.nnet3_model = KaldiNNet3OnlineModel ( self._model_dir, self._model_name, 
                                                       beam                     = kaldi_beam, 
                                                       acoustic_scale           = kaldi_acoustic_scale, 
                                                       frame_subsampling_factor = kaldi_frame_subsampling_factor)
            logging.debug ('ASR model loaded. took %fs' % (time.time() - start_time))

        else:
            raise Exception ('unknown ASR engine: %s' % self._engine)

    def decode (self, audio, do_finalize, sample_rate = DEFAULT_SAMPLE_RATE, stream_id = DEFAULT_STREAM_ID):

        if self._engine == ASR_ENGINE_NNET3:

            if not stream_id in self.asr_decoders:
                self.asr_decoders[stream_id] = KaldiNNet3OnlineDecoder (self.nnet3_model)

            decoder = self.asr_decoders[stream_id]
            decoder.decode(sample_rate, np.array(audio, dtype=np.float32), do_finalize)

            hstr, confidence = decoder.get_decoded_string()
            hstr = hstr.strip()

        else:
            raise Exception ('unknown ASR engine: %s' % self._engine)

        return hstr, confidence


    @property
    def engine(self):
        return self._engine
    # @engine.setter
    # def engine(self, v):
    #     self._engine = v

    @property
    def model_dir(self):
        return self._model_dir
    # @model_dir.setter
    # def model_dir(self, v):
    #     self._model_dir = v

    @property
    def model_name(self):
        return self._model_name
    # @model_name.setter
    # def model_name(self, v):
    #     self._model_name = v

    def decode_wav_file(self, wavfile):

        wavf = wave.open(wavfile, 'rb')

        # check format
        assert wavf.getnchannels()==1
        assert wavf.getsampwidth()==2
        assert wavf.getnframes()>0

        sample_rate = wavf.getframerate()

        # read the whole file into memory, for now
        num_frames = wavf.getnframes()
        frames = wavf.readframes(num_frames)

        samples = struct.unpack_from('<%dh' % num_frames, frames)

        wavf.close()

        return self.decode(samples, True, sample_rate)

