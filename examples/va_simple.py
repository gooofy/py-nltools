#!/usr/bin/env python3

from enum import Enum

from nltools.asr           import ASR
from nltools.pulserecorder import PulseRecorder
from nltools.vad           import VAD, BUFFER_DURATION
from nltools.tts           import TTS

MODELDIR            = '/opt/kaldi/model/kaldi-generic-en-tdnn_250'

SAMPLE_RATE         = 16000
FRAMES_PER_BUFFER   = int(SAMPLE_RATE * BUFFER_DURATION / 1000)
SOURCE              = 'CM108'
VOLUME              = 150
AGGRESSIVENESS      = 2

class Intent(Enum):
    HELLO     = 1
    LIGHT     = 2
    RADIO     = 3

utterance_map = {}
def add_utterance (utterance, intent):
    utterance_map[utterance] = intent

add_utterance("hello computer",        Intent.HELLO)
add_utterance("switch on the lights",  Intent.LIGHT)
add_utterance("switch off the lights", Intent.LIGHT)
add_utterance("switch on the radio",   Intent.RADIO)
add_utterance("switch off the radio",  Intent.RADIO)

radio_on  = False
lights_on = False

asr = ASR(model_dir = MODELDIR)

rec = PulseRecorder (SOURCE, SAMPLE_RATE, VOLUME)

vad = VAD(aggressiveness=AGGRESSIVENESS, sample_rate=SAMPLE_RATE)

tts = TTS(engine="espeak", voice="en")

rec.start_recording(FRAMES_PER_BUFFER)

intent = None

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

        intent = utterance_map.get(user_utt, None)
        if intent == Intent.HELLO:
            resp = "Hello there!"

        elif intent == Intent.LIGHT:
            if lights_on:
                resp = "OK, switching off the lights."
            else:
                resp = "OK, switching on the lights."
            lights_on = not lights_on

        elif intent == Intent.RADIO:
            if radio_on:
                resp = "OK, switching off the radio."
            else:
                resp = "OK, switching on the radio."
            radio_on = not radio_on

        if intent:
            rec.stop_recording()
            print (resp)
            tts.say(resp)
            rec.start_recording(FRAMES_PER_BUFFER)

