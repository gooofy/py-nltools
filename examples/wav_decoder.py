#!/usr/bin/env python3
from nltools.asr import ASR

MODELDIR = '/opt/kaldi/model/kaldi-generic-en-tdnn_250'
WAVFILE  = 'dw961.wav'

asr = ASR(model_dir = MODELDIR)

s, l = asr.decode_wav_file(WAVFILE)
print ("Decoded %s: %s" % (WAVFILE, s))
