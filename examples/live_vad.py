#!/usr/bin/env python3

from nltools.asr           import ASR
from nltools.pulserecorder import PulseRecorder
from nltools.vad           import VAD, BUFFER_DURATION

MODELDIR            = '/opt/kaldi/model/kaldi-generic-en-tdnn_250'

SAMPLE_RATE         = 16000
FRAMES_PER_BUFFER   = int(SAMPLE_RATE * BUFFER_DURATION / 1000)
SOURCE              = 'CM108'
VOLUME              = 150
AGGRESSIVENESS      = 2

asr = ASR(model_dir = MODELDIR)

rec = PulseRecorder (SOURCE, SAMPLE_RATE, VOLUME)

vad = VAD(aggressiveness=AGGRESSIVENESS, sample_rate=SAMPLE_RATE)

rec.start_recording(FRAMES_PER_BUFFER)

print ("Please speak.")

while True:

    samples = rec.get_samples()

    audio, finalize = vad.process_audio(samples)

    if not audio:
        continue

    user_utt, confidence = asr.decode(SAMPLE_RATE, audio, finalize)

    print ("\r%s                     " % user_utt, end='', flush=True)

    if finalize:
        print ()

