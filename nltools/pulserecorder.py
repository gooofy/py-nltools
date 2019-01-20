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
# simple pulseaudio recording client
#
# based on: http://freshfoo.com/blog/pulseaudio_monitoring

import ctypes
import threading
import logging
import time
    
import numpy as np
from builtins import str as text, range
from nltools.vad import BUFFER_DURATION

SOURCE_TIMEOUT = 30 # 3 seconds

PA_INVALID_INDEX = 4294967295 # ((uint32_t) -1)

pa = ctypes.cdll.LoadLibrary('libpulse.so.0')

class pa_proplist(ctypes.Structure):
    pass
pa_encoding = ctypes.c_int # enum
pa_encoding_t = pa_encoding
class pa_format_info(ctypes.Structure):
    pass
pa_format_info._fields_ = [
    ('encoding', pa_encoding_t),
    ('plist', ctypes.POINTER(pa_proplist)),
]
class pa_context(ctypes.Structure):
    pass
pa_context._fields_ = [ ]
pa_context_notify_cb_t = ctypes.CFUNCTYPE(None, ctypes.POINTER(pa_context), ctypes.c_void_p)
pa_context_success_cb_t = ctypes.CFUNCTYPE(None, ctypes.POINTER(pa_context), ctypes.c_int, ctypes.c_void_p)

pa_sample_format = ctypes.c_int # enum
pa_sample_format_t = pa_sample_format
pa_format_info_set_sample_format = pa.pa_format_info_set_sample_format
pa_format_info_set_sample_format.restype = None
pa_format_info_set_sample_format.argtypes = [ctypes.POINTER(pa_format_info), pa_sample_format_t]
class pa_sink_port_info(ctypes.Structure):
    pass
pa_sink_port_info._fields_ = [
    ('name', ctypes.c_char_p),
    ('description', ctypes.c_char_p),
    ('priority', ctypes.c_uint32),
    ('available', ctypes.c_int),
]
class pa_sink_info(ctypes.Structure):
    pass
class pa_sample_spec(ctypes.Structure):
    pass
pa_sample_spec._fields_ = [
    ('format', pa_sample_format_t),
    ('rate', ctypes.c_uint32),
    ('channels', ctypes.c_uint8),
]
class pa_source_info(ctypes.Structure):
    pass
pa_channel_position = ctypes.c_int # enum
pa_channel_position_t = pa_channel_position
class pa_channel_map(ctypes.Structure):
    pass
pa_channel_map._fields_ = [
    ('channels', ctypes.c_uint8),
    ('map', pa_channel_position_t * 32),
]
class pa_cvolume(ctypes.Structure):
    pass
pa_volume_t = ctypes.c_uint32
pa_cvolume._fields_ = [
    ('channels', ctypes.c_uint8),
    ('values', pa_volume_t * 32),
]
pa_source_flags = ctypes.c_int # enum
pa_source_flags_t = pa_source_flags
pa_source_state = ctypes.c_int # enum
pa_source_state_t = pa_source_state
class pa_source_port_info(ctypes.Structure):
    pass
pa_source_port_info._fields_ = [
    ('name', ctypes.c_char_p),
    ('description', ctypes.c_char_p),
    ('priority', ctypes.c_uint32),
    ('available', ctypes.c_int),
]
pa_source_info._fields_ = [
    ('name', ctypes.c_char_p),
    ('index', ctypes.c_uint32),
    ('description', ctypes.c_char_p),
    ('sample_spec', pa_sample_spec),
    ('channel_map', pa_channel_map),
    ('owner_module', ctypes.c_uint32),
    ('volume', pa_cvolume),
    ('mute', ctypes.c_int),
    ('monitor_of_sink', ctypes.c_uint32),
    ('monitor_of_sink_name', ctypes.c_char_p),
    ('latency', ctypes.c_uint64),
    ('driver', ctypes.c_char_p),
    ('flags', pa_source_flags_t),
    ('proplist', ctypes.POINTER(pa_proplist)),
    ('configured_latency', ctypes.c_uint64),
    ('base_volume', pa_volume_t),
    ('state', pa_source_state_t),
    ('n_volume_steps', ctypes.c_uint32),
    ('card', ctypes.c_uint32),
    ('n_ports', ctypes.c_uint32),
    ('ports', ctypes.POINTER(ctypes.POINTER(pa_source_port_info))),
    ('active_port', ctypes.POINTER(pa_source_port_info)),
    ('n_formats', ctypes.c_uint8),
    ('formats', ctypes.POINTER(ctypes.POINTER(pa_format_info))),
]
pa_source_info_cb_t = ctypes.CFUNCTYPE(None, ctypes.POINTER(pa_context), ctypes.POINTER(pa_source_info), ctypes.c_int, ctypes.c_void_p)
class pa_stream(ctypes.Structure):
    pass
pa_stream._fields_ = [
]
pa_stream_request_cb_t = ctypes.CFUNCTYPE(None, ctypes.POINTER(pa_stream), ctypes.c_size_t, ctypes.c_void_p)

class pa_threaded_mainloop(ctypes.Structure):
    pass
pa_threaded_mainloop._fields_ = [
]
pa_threaded_mainloop_new = pa.pa_threaded_mainloop_new
pa_threaded_mainloop_new.restype = ctypes.POINTER(pa_threaded_mainloop)
pa_threaded_mainloop_new.argtypes = []

class pa_mainloop_api(ctypes.Structure):
    pass
pa_threaded_mainloop_get_api = pa.pa_threaded_mainloop_get_api
pa_threaded_mainloop_get_api.restype = ctypes.POINTER(pa_mainloop_api)
pa_threaded_mainloop_get_api.argtypes = [ctypes.POINTER(pa_threaded_mainloop)]

pa_context_new = pa.pa_context_new
pa_context_new.restype = ctypes.POINTER(pa_context)
pa_context_new.argtypes = [ctypes.POINTER(pa_mainloop_api), ctypes.c_char_p]

pa_context_set_state_callback = pa.pa_context_set_state_callback
pa_context_set_state_callback.restype = None
pa_context_set_state_callback.argtypes = [ctypes.POINTER(pa_context), pa_context_notify_cb_t, ctypes.c_void_p]

pa_context_flags = ctypes.c_int # enum
pa_context_flags_t = pa_context_flags

class pa_spawn_api(ctypes.Structure):
    pass

pa_context_connect = pa.pa_context_connect
pa_context_connect.restype = ctypes.c_int
pa_context_connect.argtypes = [ctypes.POINTER(pa_context), ctypes.c_char_p, pa_context_flags_t, ctypes.POINTER(pa_spawn_api)]

pa_threaded_mainloop_start = pa.pa_threaded_mainloop_start
pa_threaded_mainloop_start.restype = ctypes.c_int
pa_threaded_mainloop_start.argtypes = [ctypes.POINTER(pa_threaded_mainloop)]

pa_threaded_mainloop_lock = pa.pa_threaded_mainloop_lock
pa_threaded_mainloop_lock.restype = None
pa_threaded_mainloop_lock.argtypes = [ctypes.POINTER(pa_threaded_mainloop)]

pa_context_disconnect = pa.pa_context_disconnect
pa_context_disconnect.restype = None
pa_context_disconnect.argtypes = [ctypes.POINTER(pa_context)]

pa_context_unref = pa.pa_context_unref
pa_context_unref.restype = None
pa_context_unref.argtypes = [ctypes.POINTER(pa_context)]

pa_threaded_mainloop_unlock = pa.pa_threaded_mainloop_unlock
pa_threaded_mainloop_unlock.restype = None
pa_threaded_mainloop_unlock.argtypes = [ctypes.POINTER(pa_threaded_mainloop)]

pa_threaded_mainloop_stop = pa.pa_threaded_mainloop_stop
pa_threaded_mainloop_stop.restype = None
pa_threaded_mainloop_stop.argtypes = [ctypes.POINTER(pa_threaded_mainloop)]

pa_threaded_mainloop_free = pa.pa_threaded_mainloop_free
pa_threaded_mainloop_free.restype = None
pa_threaded_mainloop_free.argtypes = [ctypes.POINTER(pa_threaded_mainloop)]

pa_context_get_state = pa.pa_context_get_state
pa_context_get_state.restype = ctypes.c_int
pa_context_get_state.argtypes = [ctypes.POINTER(pa_context)]

PA_CONTEXT_NOFLAGS = 0
PA_CONTEXT_NOFAIL = 2
PA_CONTEXT_NOAUTOSPAWN = 1

PA_CONTEXT_UNCONNECTED = 0
PA_CONTEXT_CONNECTING = 1
PA_CONTEXT_AUTHORIZING = 2
PA_CONTEXT_READY = 4
PA_CONTEXT_FAILED = 5
PA_CONTEXT_TERMINATED = 6

class pa_operation(ctypes.Structure):
    pass
pa_context_get_source_info_list = pa.pa_context_get_source_info_list
pa_context_get_source_info_list.restype = ctypes.POINTER(pa_operation)
pa_context_get_source_info_list.argtypes = [ctypes.POINTER(pa_context), pa_source_info_cb_t, ctypes.c_void_p]

PA_VOLUME_NORM = 65536

pa_context_set_source_volume_by_index = pa.pa_context_set_source_volume_by_index
pa_context_set_source_volume_by_index.restype = ctypes.POINTER(pa_operation)
pa_context_set_source_volume_by_index.argtypes = [ctypes.POINTER(pa_context), ctypes.c_uint32, ctypes.POINTER(pa_cvolume), pa_context_success_cb_t, ctypes.c_void_p]

pa_operation_unref = pa.pa_operation_unref
pa_operation_unref.restype = None
pa_operation_unref.argtypes = [ctypes.POINTER(pa_operation)]

PA_SAMPLE_INVALID = -1
PA_SAMPLE_U8 = 0
PA_SAMPLE_ALAW = 1
PA_SAMPLE_ULAW = 2
PA_SAMPLE_S16LE = 3
PA_SAMPLE_S16BE = 4
PA_SAMPLE_FLOAT32LE = 5
PA_SAMPLE_FLOAT32BE = 6
PA_SAMPLE_S32LE = 7
PA_SAMPLE_S32BE = 8
PA_SAMPLE_S24LE = 9
PA_SAMPLE_S24BE = 10
PA_SAMPLE_S24_32LE = 11
PA_SAMPLE_S24_32BE = 12
PA_SAMPLE_MAX = 13

pa_stream_new = pa.pa_stream_new
pa_stream_new.restype = ctypes.POINTER(pa_stream)
pa_stream_new.argtypes = [ctypes.POINTER(pa_context), ctypes.c_char_p, ctypes.POINTER(pa_sample_spec), ctypes.POINTER(pa_channel_map)]

pa_stream_set_read_callback = pa.pa_stream_set_read_callback
pa_stream_set_read_callback.restype = None
pa_stream_set_read_callback.argtypes = [ctypes.POINTER(pa_stream), pa_stream_request_cb_t, ctypes.c_void_p]

PA_STREAM_ADJUST_LATENCY = 8192

pa_stream_flags = ctypes.c_int # enum
pa_stream_flags_t = pa_stream_flags
class pa_buffer_attr(ctypes.Structure):
    pass
pa_buffer_attr._fields_ = [
    ('maxlength', ctypes.c_uint32),
    ('tlength',   ctypes.c_uint32),
    ('prebuf',    ctypes.c_uint32),
    ('minreq',    ctypes.c_uint32),
    ('fragsize',  ctypes.c_uint32),
]

pa_stream_connect_record = pa.pa_stream_connect_record
pa_stream_connect_record.restype = ctypes.c_int
pa_stream_connect_record.argtypes = [ctypes.POINTER(pa_stream), ctypes.c_char_p, ctypes.POINTER(pa_buffer_attr), pa_stream_flags_t]

pa_stream_peek = pa.pa_stream_peek
pa_stream_peek.restype = ctypes.c_int
pa_stream_peek.argtypes = [ctypes.POINTER(pa_stream), ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_size_t)]

pa_stream_drop = pa.pa_stream_drop
pa_stream_drop.restype = ctypes.c_int
pa_stream_drop.argtypes = [ctypes.POINTER(pa_stream)]

def null_cb(a=None, b=None, c=None, d=None):
    return

MIX_MODE_BOTH             = 0
MIX_MODE_LEFT             = 1
MIX_MODE_RIGHT            = 2

DEFAULT_VOLUME            =   100
DEFAULT_RATE              = 16000
DEFAULT_NAME              = b'Python PulseRecorder'
DEFAULT_FRAMES_PER_BUFFER = int(DEFAULT_RATE * BUFFER_DURATION / 1000)
DEFAULT_MIX_MODE          = MIX_MODE_BOTH

class PulseRecorder(object):

    def __init__(self, volume=DEFAULT_VOLUME, rate=DEFAULT_RATE, source_name=None):
        self.match_source_name  = source_name
        self.rate               = rate
        self.volume             = volume
        self.source_idx         = -1
        self.source_score       = 0
        self.source_log         = False
        self.source_name        = ''
        self.source_description = ''

        # Wrap callback methods in appropriate ctypefunc instances so
        # that the Pulseaudio C API can call them
        self._context_notify_cb = pa_context_notify_cb_t(self.context_notify_cb)
        self._source_info_cb    = pa_source_info_cb_t(self.source_info_cb)
        self._stream_read_cb    = pa_stream_request_cb_t(self.stream_read_cb)
        self._null_cb           = pa_context_success_cb_t(null_cb)

        # lock/cond for buffers

        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock) 

    def start_recording(self, frames_per_buffer = DEFAULT_FRAMES_PER_BUFFER, mix_mode = DEFAULT_MIX_MODE):

        logging.debug("start_recording...")

        self._frames_per_buffer = frames_per_buffer
        self._mix_mode          = mix_mode
        self._record_stereo     = mix_mode != MIX_MODE_BOTH
        self._buffers           = []
        self._cur_buf_cnt       = 0
        self.source_idx         = -1
        self.source_score       = 0
        self.source_log         = False
        self.source_name        = ''
        self.source_description = ''

        self._buffers.append(np.empty(self._frames_per_buffer, dtype=np.int16))

        self._mainloop = pa_threaded_mainloop_new()
        _mainloop_api  = pa_threaded_mainloop_get_api(self._mainloop)
        self._context  = pa_context_new(_mainloop_api, DEFAULT_NAME)

        pa_context_set_state_callback(self._context, self._context_notify_cb, None)
        pa_context_connect(self._context, None, 0, None)

        pa_threaded_mainloop_start(self._mainloop)

        # wait for audio source detection
        cnt = 0
        while (self.source_idx < 0) and (cnt < SOURCE_TIMEOUT):
            cnt += 1
            time.sleep (0.1)
        if self.source_idx < 0:
            raise Exception ("Pulserecorder: no suitable input source found.")


    def stop_recording(self):

        logging.debug("stop_recording...")

        pa_threaded_mainloop_lock(self._mainloop)
        pa_context_disconnect(self._context)
        pa_context_unref(self._context)
        pa_threaded_mainloop_unlock(self._mainloop)

        pa_threaded_mainloop_stop(self._mainloop)
        pa_threaded_mainloop_free(self._mainloop)

        self.source_idx  = -1

    def context_notify_cb(self, context, _):
        state = pa_context_get_state(context)

        if state == PA_CONTEXT_READY:
            logging.debug("Pulseaudio connection ready...")
            o = pa_context_get_source_info_list(context, self._source_info_cb, None)
            pa_operation_unref(o)

        elif state == PA_CONTEXT_FAILED :
            logging.error("Connection failed")

        elif state == PA_CONTEXT_TERMINATED:
            logging.debug("Connection terminated")

    def source_info_cb(self, context, source_info_p, eol, __):
        logging.debug("source_info_cb... eol: %d" % eol)

        if eol:
            if not self.source_log:
                logging.info(u'audio source: %s' % self.source_description.decode('utf8','ignore'))
                logging.debug(u'name: %s' % text(self.source_name) )
                self.source_log = True

            if self.source_idx < 0:
                logging.error ("Pulserecorder: no suitable input source found.")

            #
            # set volume first
            #

            cvol = pa_cvolume()
            cvol.channels = 1
            cvol.values[0] = int((self.volume * PA_VOLUME_NORM) / 100)

            operation = pa_context_set_source_volume_by_index (self._context, self.source_idx, cvol, self._null_cb, None)
            pa_operation_unref(operation)

            logging.debug('recording from %s' % self.source_name)

            samplespec = pa_sample_spec()
            samplespec.channels = 2 if self._record_stereo else 1
            samplespec.format   = PA_SAMPLE_S16LE
            samplespec.rate     = self.rate

            pa_stream = pa_stream_new(context, b"pulserecorder", samplespec, None)
            pa_stream_set_read_callback(pa_stream,
                                        self._stream_read_cb,
                                        self.source_idx)

            # flags = PA_STREAM_NOFLAGS
            flags = PA_STREAM_ADJUST_LATENCY
            
            # buffer_attr = None
            fragsize = self._frames_per_buffer*2
            if self._record_stereo:
                fragsize *= 2
            buffer_attr = pa_buffer_attr(-1, -1, -1, -1, fragsize=fragsize)

            pa_stream_connect_record(pa_stream,
                                     self.source_name,
                                     buffer_attr,
                                     flags)

        if not source_info_p:
            return

        source_info = source_info_p.contents

        logging.debug('index       : %d' % source_info.index)
        logging.debug('name        : %s' % source_info.name)
        logging.debug('description : %s' % source_info.description)
        logging.debug('monitor of  : %d' % source_info.monitor_of_sink)

        if source_info.monitor_of_sink != PA_INVALID_INDEX:
            logging.debug("ignoring source: monitor")
            return

        score = 1

        if self.match_source_name and (text(self.match_source_name) in text(source_info.description)):
            score += 100


        # microphone source auto-detection magic

        # import pdb; pdb.set_trace()

        if source_info.ports:
            score += 1

            mic_port = False
            for pi in range(source_info.n_ports):
                if text('mic') in text(source_info.ports[pi].contents.name):
                    logging.debug("mic port found")
                    score += 1
                    break

        logging.debug('source score: %d, highest score so far: %d' % (score, self.source_score))

        if score > self.source_score:

            self.source_idx         = source_info.index
            self.source_score       = score
            self.source_name        = source_info.name
            self.source_description = source_info.description


    def stream_read_cb(self, stream, length, index_incr):
        data = ctypes.c_void_p()
        pa_stream_peek(stream, data, ctypes.c_ulong(length))
        data = ctypes.cast(data, ctypes.POINTER(ctypes.c_ubyte))

        self._lock.acquire()

        bytes_per_sample = 4 if self._record_stereo else 2
        num_samples = int(length / bytes_per_sample)

        for i in range(num_samples):

            if self._mix_mode == MIX_MODE_BOTH:
                off_low  = 0
                off_high = 1
            elif self._mix_mode == MIX_MODE_LEFT:
                off_low  = 0
                off_high = 1
            elif self._mix_mode == MIX_MODE_RIGHT:
                off_low  = 2
                off_high = 3

            sample = data[i*bytes_per_sample +off_low ] + 256 * data[i*bytes_per_sample+off_high]

            self._buffers[len(self._buffers)-1][self._cur_buf_cnt] = sample
            self._cur_buf_cnt += 1 

            # buffer full?
            if self._cur_buf_cnt >= self._frames_per_buffer:

                self._buffers.append(np.empty(self._frames_per_buffer, dtype=np.int16))
                self._cur_buf_cnt = 0

                self._cond.notifyAll()


        self._lock.release()

        pa_stream_drop(stream)


    def get_samples(self):

        self._lock.acquire()

        buf = None
        while len(self._buffers) < 2:
            self._cond.wait()

        buf = self._buffers.pop(0)

        self._lock.release()

        return buf

