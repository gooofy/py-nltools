#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2013, 2014, 2016, 2017, 2018 Guenter Bartsch
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
# Voice Activity Detection (VAD) state machine
#

import logging
import webrtcvad

SAMPLE_RATE           = 16000
BUFFER_DURATION       = 30 # ms
RING_BUF_ENTRIES      =  5 * 60 * 1000 / BUFFER_DURATION # 5 minutes max

MIN_UTT_LENGTH        = 0.4 # seconds
MAX_UTT_LENGTH        = 12  # seconds
MAX_UTT_GAP           = 0.7 # seconds

STATE_IDLE            =  0

STATE_PRE_SPEECH      =  1
STATE_PRE_GAP         =  2

STATE_SPEECH          =  3
STATE_GAP             =  4

STATE_IGNORE          =  5
STATE_IGNORE_GAP      =  6

FRAME_STAT_CNT        =   300
LOW_VOLUME_THRESH     =   100
HIGH_VOLUME_THRESH    = 25000

class VAD(object):

    def __init__(self, aggressiveness=2, sample_rate=SAMPLE_RATE,
                 min_utt_length = MIN_UTT_LENGTH,
                 max_utt_length = MAX_UTT_LENGTH,
                 max_utt_gap    = MAX_UTT_GAP):


        self.sample_rate = sample_rate

        self.vad = webrtcvad.Vad()
        self.vad.set_mode(aggressiveness)

        self.state          = STATE_IDLE
        self.buf            = []
        self.buf_sent       = 0

        self.min_buf_entries = int(min_utt_length * 1000) / BUFFER_DURATION 
        self.max_buf_entries = int(max_utt_length * 1000) / BUFFER_DURATION
        self.max_gap         = int(max_utt_gap    * 1000) / BUFFER_DURATION

        self.frame_cnt       = 0
        self.avg_vol_sum     = 0.0
        self.avg_vol_cnt     = 0

    def _return_audio (self, finalize):

        res = []

        buf_max = len(self.buf)-1

        while self.buf_sent <= buf_max:
            res.extend(self.buf[self.buf_sent].tolist())
            self.buf_sent += 1

        return res, finalize

    def process_audio (self, audio):

        cur_frame = audio

        # give feedback if volume too low / too high
        if self.frame_cnt <= FRAME_STAT_CNT:

            for sample in audio:
                self.avg_vol_sum += abs(sample)
                self.avg_vol_cnt += 1

            self.frame_cnt += 1
            if self.frame_cnt == FRAME_STAT_CNT:

                # import pdb; pdb.set_trace()

                self.avg_vol_sum /= float(self.avg_vol_cnt)

                if self.avg_vol_sum < LOW_VOLUME_THRESH:
                    logging.error ('VAD: audio volume too low or wrong source?')
                elif self.avg_vol_sum > HIGH_VOLUME_THRESH:
                    logging.error ('VAD: audio volume too high or wrong source?')

        vad_res = self.vad.is_speech(audio.tobytes(), self.sample_rate)

        if self.state == STATE_IDLE:
            if vad_res:
                self.state       = STATE_PRE_SPEECH
                self.buf         = [ cur_frame ]
                self.buf_sent    = 0

        elif self.state == STATE_PRE_SPEECH:
            self.buf.append(cur_frame)
            if vad_res: 
                if len (self.buf) > self.min_buf_entries:
                    logging.debug ("*** SPEECH DETECTED at frame %3d ***" % len(self.buf))
                    self.state = STATE_SPEECH

            else:
                self.state     = STATE_PRE_GAP
                self.gap_start = len(self.buf)

        elif self.state == STATE_PRE_GAP:
            self.buf.append(cur_frame)

            if vad_res:
                self.state = STATE_PRE_SPEECH

            else:
                gap_len = len(self.buf) - self.gap_start
                if gap_len > self.max_gap:
                    logging.debug ("*** PRE GAP (%d) TOO LONG at frame %3d ***" % (gap_len, len(self.buf)))
                    self.state = STATE_IDLE

        elif self.state == STATE_SPEECH:
            self.buf.append(cur_frame)

            # check if attention span is over
            if len (self.buf) > self.max_buf_entries:
                logging.debug ("*** START OF IGNORE at frame %3d ***" % len(self.buf))
                self.state = STATE_IGNORE
                return self._return_audio(True)

            else:
                if not vad_res:
                    logging.debug ("*** START OF GAP at frame %3d ***" % len(self.buf))
                    self.state     = STATE_GAP
                    self.gap_start = len(self.buf)
                return self._return_audio(False)

        elif self.state == STATE_GAP:
            self.buf.append(cur_frame)

            gap_len = len(self.buf) - self.gap_start
            if vad_res:
                self.state = STATE_SPEECH
                logging.debug ("*** END OF GAP (%d < %d) at frame %3d ***" % (gap_len, self.max_gap, len(self.buf)))
                return self._return_audio(False)

            else:
                if gap_len > self.max_gap:
                    logging.debug ("*** GAP (%d > %d) TOO LONG at frame %3d ***" % (gap_len, self.max_gap, len(self.buf)))
                    self.state = STATE_IDLE
                    return self._return_audio(True)
                else:
                    return self._return_audio(False)

        elif self.state == STATE_IGNORE:
            self.buf.append(cur_frame)
            if not vad_res:
                self.state     = STATE_IGNORE_GAP
                self.gap_start = len(self.buf)

        elif self.state == STATE_IGNORE_GAP:
            self.buf.append(cur_frame)
            if vad_res:
                self.state = STATE_IGNORE
            else:
                gap_len = len(self.buf) - self.gap_start
                if gap_len > self.max_gap:
                    logging.debug ("*** end of ignore at frame %3d ***" % len(self.buf))
                    self.state = STATE_IDLE

        return None, False

