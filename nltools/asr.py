#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2017, 2018 Guenter Bartsch
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
# kaldi-asr and pocketsphinx at the moment
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
ASR_ENGINE_POCKETSPHINX = 'pocketsphinx'

DEFAULT_ENGINE          = ASR_ENGINE_NNET3
DEFAULT_MODEL_DIR       = 'models/kaldi-generic-en-tdnn_sp-latest'
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

        elif self._engine == ASR_ENGINE_POCKETSPHINX:

            import pocketsphinx
            self.ps_config = pocketsphinx.Decoder.default_config()

            # determine CFG_N_TIED_STATES, CFG_WAVFILE_SRATE
            # cmusphinx-cont-voxforge-en-latest/etc/sphinx_train.cfg
            traincfg_fn        = '%s/etc/sphinx_train.cfg' % model_dir
            n_tied_states      = 6000
            self.ps_samplerate = 16000
            with open (traincfg_fn, 'r') as traincfg_f:
                for line in traincfg_f:
                    if not line:
                        break
                    # $CFG_N_TIED_STATES = 6000;
                    if 'CFG_N_TIED_STATES' in line:
                        # logging.debug ('parsing train cfg line %s' % line)
                        m = re.match (r"\$CFG_N_TIED_STATES\s+=\s+([0-9]+)\s*;", line.strip())
                        if m:
                            n_tied_states = int(m.group(1))
                            # logging.debug ('matched, n_tied_states=%d' % n_tied_states)

                    # $CFG_WAVFILE_SRATE = 16000.0;
                    if 'CFG_WAVFILE_SRATE' in line:
                        m = re.match (r"\$CFG_WAVFILE_SRATE\s+=\s+([0-9.]+)\s*;", line.strip())
                        if m:
                            self.ps_samplerate = int(float(m.group(1)))
                            
            self.ps_config.set_string('-hmm', '%s/model_parameters/%s.cd_cont_%d' % (model_dir, model_name, n_tied_states))
            self.ps_config.set_float ('-lw', 10)
            self.ps_config.set_string('-feat', '1s_c_d_dd')
            self.ps_config.set_float ('-beam', 1e-80)
            self.ps_config.set_float ('-wbeam', 1e-40)
            self.ps_config.set_string('-dict', '%s/etc/%s.dic' % (model_dir, model_name))
            self.ps_config.set_float ('-wip', 0.2)
            self.ps_config.set_string('-agc', 'none')
            self.ps_config.set_string('-varnorm', 'no')
            self.ps_config.set_string('-cmn', 'current')
            self.ps_config.set_string('-lm', '%s/etc/%s.lm.bin' % (model_dir, model_name))

            self.ps_config.set_string('-logfn', "/dev/null")

            self.asr_in_utt = {} # stream_id -> Boolean

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

        elif self._engine == ASR_ENGINE_POCKETSPHINX:

            if sample_rate != self.ps_samplerate:
                raise Exception ('decode: samplerate does not match model: %d vs %d' % (sample_rate, self.ps_samplerate))

            if not stream_id in self.asr_decoders:
                import pocketsphinx
                self.asr_decoders[stream_id] = pocketsphinx.Decoder(self.ps_config)
                self.asr_in_utt[stream_id] = False

            decoder = self.asr_decoders[stream_id]
            if not self.asr_in_utt[stream_id]:
                decoder.start_utt()
                self.asr_in_utt[stream_id] = True

            audios = struct.pack('<%dh' % len(audio), *audio)

            decoder.process_raw(audios, False, False)

            if not do_finalize:
                return None, 0.0

            decoder.end_utt()
            self.asr_in_utt[stream_id] = False

            hypothesis = decoder.hyp()
            logmath = decoder.get_logmath()
            hstr = hypothesis.hypstr.decode('utf8').strip()
            confidence = logmath.exp(hypothesis.prob)

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

