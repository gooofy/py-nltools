#!/usr/bin/env python3

import logging
import wave
import struct
import os
import sys

from datetime import date
from optparse import OptionParser

from nltools.asr           import ASR
from nltools.pulserecorder import PulseRecorder, MIX_MODE_BOTH, MIX_MODE_LEFT, MIX_MODE_RIGHT
from nltools.vad           import VAD
from nltools               import misc

DEFAULT_VOLUME   =   150
SAMPLE_RATE      = 16000
DEFAULT_MIX_MODE = 'both'

#
# init 
#

misc.init_app ('live_recorder')

#
# commandline parsing
#

parser = OptionParser("usage: %prog [options]")

parser.add_option ("-m", "--mix-mode", dest='mix_mode', type='str', default=DEFAULT_MIX_MODE,
                   help="mix mode (left, right, both - default: %s)" % DEFAULT_MIX_MODE)

parser.add_option ("-V", "--volume", dest='volume', type='int', default=DEFAULT_VOLUME,
                   help="volume, default: %d%%" % DEFAULT_VOLUME)

parser.add_option ("-v", "--verbose", action="store_true", dest="verbose",
                   help="enable verbose logging")

(options, args) = parser.parse_args()

if options.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


if options.mix_mode == 'left':
    mix_mode = MIX_MODE_LEFT
elif options.mix_mode == 'right':
    mix_mode = MIX_MODE_RIGHT
elif options.mix_mode == 'both':
    mix_mode = MIX_MODE_BOTH
else:
    parser.print_usage()
    sys.exit(1)


logging.info ("Initializing...")

rec = PulseRecorder (volume=options.volume)
vad = VAD()

rec.start_recording(mix_mode=mix_mode)
logging.info ("Please speak. (CTRL-C to exit)")

cnt = 0
wfs = None

while True:

    samples = rec.get_samples()

    audio, finalize = vad.process_audio(samples)

    if not audio:
        continue

    logging.debug ("%8d got audio. finalize: %s" % (cnt, repr(finalize)))
    cnt =+ 1

    if not wfs:

        ds = date.strftime(date.today(), '%Y%m%d')
        audiofn = 'rec-%s.wav' % ds
        logging.debug('audiofn: %s' % audiofn)
        
        audiocnt = 0
        while True:
            audiocnt += 1
            audiofn = 'rec-%s-%03d.wav' % (ds, audiocnt)
            if not os.path.isfile(audiofn):
                break
        
        
        # create wav file 
        
        wfs = wave.open(audiofn, 'wb')
        wfs.setnchannels(1)
        wfs.setsampwidth(2)
        wfs.setframerate(SAMPLE_RATE)

        logging.info('voice activity detected, recording to: %s' % audiofn)

    packed_audio = struct.pack('%sh' % len(audio), *audio)
    wfs.writeframes(packed_audio)

    if finalize:

        logging.info('recording to %s finished.' % audiofn)

        wfs.close()
        wfs = None


