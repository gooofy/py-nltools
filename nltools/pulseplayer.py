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
# simple pulseaudio playback client
#

from io import BytesIO
import wave
import copy
import ctypes
import wave
import sys
import logging

from builtins import str as text

from threading import Thread, Lock, Condition

pa = ctypes.cdll.LoadLibrary('libpulse-simple.so.0')
 
PA_STREAM_PLAYBACK = 1
PA_SAMPLE_S16LE = 3
BUFFSIZE = 1024

# class struct_pa_sample_spec(ctypes.Structure):
#     __slots__ = [
#         'format',
#         'rate',
#         'channels',
#     ]
#  
# struct_pa_sample_spec._fields_ = [
#     ('format', ctypes.c_int),
#     ('rate', ctypes.c_uint32),
#     ('channels', ctypes.c_uint8),
# ]
# pa_sample_spec = struct_pa_sample_spec  # /usr/include/pulse/sample.h:174


class pa_sample_spec(ctypes.Structure):
    _fields_ = [
                ('format',   ctypes.c_int),
                ('rate',     ctypes.c_uint32),
                ('channels', ctypes.c_uint8),
            ]

pa_simple_new = pa.pa_simple_new
pa_simple_new.restype  = ctypes.c_void_p # pointer(pa_simple)
pa_simple_new.argtypes = [
                          ctypes.c_char_p,                   # server
                          ctypes.c_char_p,                   # name,
                          ctypes.c_int,                      # dir,
                          ctypes.c_char_p,                   # dev,
                          ctypes.c_char_p,                   # stream_name,
                          ctypes.POINTER( pa_sample_spec ),  # ss,
                          ctypes.c_void_p, # pointer( pa_channel_map ),  # map,
                          ctypes.c_void_p, # pointer( pa_buffer_attr ),  # attr,
                          ctypes.POINTER(ctypes.c_int),      # error
                         ]

pa_simple_write = pa.pa_simple_write
pa_simple_write.restype = ctypes.c_int
pa_simple_write.argtypes = [
                            ctypes.c_void_p,              # s
                            ctypes.c_void_p,              # data,
                            ctypes.c_size_t,              # bytes,
                            ctypes.POINTER(ctypes.c_int), # error 
                           ]

pa_simple_drain = pa.pa_simple_drain
pa_simple_drain.restype = ctypes.c_int
pa_simple_drain.argtypes = [
                            ctypes.c_void_p,              # s
                            ctypes.POINTER(ctypes.c_int), # error 
                           ]

pa_simple_free = pa.pa_simple_free
pa_simple_free.restype = None
pa_simple_free.argtypes = [ ctypes.c_void_p ]

class PulsePlayer:

    def __init__(self, name):
        self.name      = text(name)
        self.playing   = False
        self.terminate = False
        self.thread    = None
        self.lock      = Lock()
        self.cond      = Condition(self.lock)

    def _play_loop(self):

        logging.debug("_play_loop starts, a_sound: %d bytes" % len(self.a_sound))

        while not self.terminate:
            #latency = pa.pa_simple_get_latency(s, error)
            #if latency == -1:
            #    raise Exception('Getting latency failed!')
        
            #print('{0} usec'.format(latency))
        
            # Reading frames and writing to the stream.
            buf = self.wf.readframes(BUFFSIZE)
            if not buf:
                break

            # logging.debug("_play_loop len: %d self.s: %s" % (len(buf), repr(self.s)))
        
            if pa_simple_write(self.s, buf, len(buf), ctypes.byref(self.error)):
                raise Exception('Could not play file, error: %d!' % self.error.value)
        
        self.wf.close()

        if pa_simple_drain(self.s, ctypes.byref(self.error)):
            raise Exception('Could not simple drain!')

        # Freeing resources and closing connection.
        logging.debug ('pa.pa_simple_free %s...' % repr(self.s))
        pa_simple_free(self.s)

        self.lock.acquire()
        try:
            self.playing = False
            self.cond.notifyAll()
        finally:
            self.lock.release()

    def play(self, a_sound, async=True):

        logging.debug("play starts, async: %s" % repr(async))

        self.lock.acquire()
        try:
            self.terminate = True
            while self.playing:
                self.cond.wait()

            if self.thread:
                self.thread.join()
                self.thread = None

            self.terminate = False
            self.playing   = True
            self.a_sound   = copy.copy(a_sound)

            self.wf = wave.open(BytesIO(self.a_sound), 'rb')

            self.ss = pa_sample_spec()

            self.ss.rate      = self.wf.getframerate()
            self.ss.channels  = self.wf.getnchannels()
            self.ss.format    = PA_SAMPLE_S16LE

            # logging.debug("frame rate: %d, channels: %d" % (self.ss.rate, self.ss.channels))

            self.error = ctypes.c_int(0)
    
            self.s = pa_simple_new(
                None,                    # Default server.
                self.name.encode('utf8'),# Application's name.
                PA_STREAM_PLAYBACK,      # Stream for playback.
                None,                    # Default device.
                b'playback',             # Stream's description.
                ctypes.byref(self.ss),   # Sample format.
                None,                    # Default channel map.
                None,                    # Default buffering attributes.
                ctypes.byref(self.error) # Ignore error code.
            )
            if not self.s:
                raise Exception('Could not create pulse audio stream: {0}!'.format(
                    pa.strerror(ctypes.byref(self.error))))

            logging.debug ('pa_simple_new done, self.s: %s' % repr(self.s))

        finally:
            self.lock.release()

        self.thread = Thread(target=self._play_loop)
        self.thread.start()

        if not async:
            # wait for player to finish
            self.lock.acquire()
            try:
                while self.playing:
                    self.cond.wait()

                self.thread.join()
                self.thread = None
            finally:
                self.lock.release()

