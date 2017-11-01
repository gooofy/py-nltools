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

#
# Voice Activity Detection (VAD) state machine
#

import logging
import webrtcvad

SAMPLE_RATE           = 16000
BUFFER_DURATION       = 30 # ms
RING_BUF_ENTRIES      =  5 * 60 * 1000 / BUFFER_DURATION # 5 minutes max

MIN_BUF_ENTRIES       =            400 / BUFFER_DURATION # min  0.4  sec utterance
MAX_BUF_ENTRIES       =      12 * 1000 / BUFFER_DURATION # max 12.0  sec utterance
MAX_GAP               =            700 / BUFFER_DURATION # max  0.7  sec gaps in utterance

STATE_IDLE            =  0

STATE_PRE_SPEECH      =  1
STATE_PRE_GAP         =  2

STATE_SPEECH          =  3
STATE_GAP             =  4

STATE_IGNORE          =  5
STATE_IGNORE_GAP      =  6

class VAD(object):

    def __init__(self, aggressiveness=2, sample_rate=SAMPLE_RATE):

        self.sample_rate = sample_rate

        self.vad = webrtcvad.Vad()
        self.vad.set_mode(aggressiveness)

        self.state       = STATE_IDLE
        self.buf         = []
        self.buf_sent    = 0

    def _return_audio (self, finalize):

        res = []

        buf_max = len(self.buf)-1

        while self.buf_sent <= buf_max:
            res.extend(self.buf[self.buf_sent].tolist())
            self.buf_sent += 1

        return res, finalize

    def process_audio (self, audio):

        cur_frame = audio

        vad_res = self.vad.is_speech(audio.tobytes(), self.sample_rate)

        if self.state == STATE_IDLE:
            if vad_res:
                self.state       = STATE_PRE_SPEECH
                self.buf         = [ cur_frame ]
                self.buf_sent    = 0

        elif self.state == STATE_PRE_SPEECH:
            self.buf.append(cur_frame)
            if vad_res: 
                if len (self.buf) > MIN_BUF_ENTRIES:
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
                if gap_len > MAX_GAP:
                    logging.debug ("*** PRE GAP (%d) TOO LONG at frame %3d ***" % (gap_len, len(self.buf)))
                    self.state = STATE_IDLE

        elif self.state == STATE_SPEECH:
            self.buf.append(cur_frame)

            # check if attention span is over
            if len (self.buf) > MAX_BUF_ENTRIES:
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
                logging.debug ("*** END OF GAP (%d < %d) at frame %3d ***" % (gap_len, MAX_GAP, len(self.buf)))
                return self._return_audio(False)

            else:
                if gap_len > MAX_GAP:
                    logging.debug ("*** GAP (%d > %d) TOO LONG at frame %3d ***" % (gap_len, MAX_GAP, len(self.buf)))
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
                if gap_len > MAX_GAP:
                    logging.debug ("*** end of ignore at frame %3d ***" % len(self.buf))
                    self.state = STATE_IDLE

        return None, False

