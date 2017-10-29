#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2017 Guenter Bartsch
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
# Abstraction layer for multiple speech recognition engines,
# kaldi-asr and pocketsphinx at the moment
#

import traceback
import logging
import time
import numpy as np

from base64                 import b64encode
from kaldisimple.nnet3      import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder

ASR_ENGINE_NNET3        = 'kaldi-nnet3'
ASR_ENGINE_POCKETSPHINX = 'pocketsphinx'

DEFAULT_ENGINE          = ASR_ENGINE_NNET3
DEFAULT_MODEL_DIR       = 'models/kaldi-nnet3-voxforge-en-latest'
DEFAULT_MODEL_NAME      = 'nnet_tdnn_a'
DEFAULT_STREAM_ID       = '__default__'

class ASR(object):

    def __init__(self, 
                 engine      = DEFAULT_ENGINE,
                 model_dir   = DEFAULT_MODEL_DIR,
                 model_name  = DEFAULT_MODEL_NAME):

        self._engine      = engine
        self._model_dir   = model_dir
        self._model_name  = model_name
        self.asr_decoders = {} # stream_id -> decoder

        if self._engine == ASR_ENGINE_NNET3:

            logging.debug ('loading ASR model %s from %s...' % (self._model_name, self._model_dir))
            start_time = time.time()
            self.nnet3_model = KaldiNNet3OnlineModel ( self._model_dir, self._model_name )
            logging.debug ('ASR model loaded. took %fs' % (time.time() - start_time))

        else:
            raise Exception ('unknown ASR engine: %s' % self._engine)

    def decode (self, sample_rate, audio, do_finalize, stream_id = DEFAULT_STREAM_ID):

        if self._engine == ASR_ENGINE_NNET3:

            if not stream_id in self.asr_decoders:
                self.asr_decoders[stream_id] = KaldiNNet3OnlineDecoder (self.nnet3_model)

            decoder = self.asr_decoders[stream_id]
            decoder.decode(sample_rate, np.array(audio, dtype=np.float32), do_finalize)

            if not do_finalize:
                return None, 0.0

            hstr, confidence = decoder.get_decoded_string()

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

