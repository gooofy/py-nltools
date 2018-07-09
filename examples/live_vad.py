#!/usr/bin/env python3
import logging
logging.basicConfig(level=logging.INFO)
from nltools.asr           import ASR
from nltools.pulserecorder import PulseRecorder
from nltools.vad           import VAD

MODELDIR = '/opt/kaldi/model/kaldi-generic-en-tdnn_250'
VOLUME   = 150

print ("Initializing...")

rec = PulseRecorder (volume=VOLUME)
asr = ASR(model_dir = MODELDIR)
vad = VAD()

rec.start_recording()
print ("Please speak. (CTRL-C to exit)")

while True:

    samples = rec.get_samples()

    audio, finalize = vad.process_audio(samples)

    if not audio:
        continue

    user_utt, confidence = asr.decode(audio, finalize)

    print ("\r%s           " % user_utt, end='', flush=True)

    if finalize:
        print ()

