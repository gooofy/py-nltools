#!/usr/bin/env python3
import logging
logging.basicConfig(level=logging.INFO)
from enum                  import Enum
from nltools.asr           import ASR
from nltools.pulserecorder import PulseRecorder
from nltools.vad           import VAD
from nltools.tts           import TTS

MODELDIR          = '/opt/kaldi/model/kaldi-generic-en-tdnn_250'
VOLUME            = 150

class Intent(Enum):
    HELLO     = 1
    LIGHT     = 2
    RADIO     = 3

print ("Initializing...")

radio_on  = False
lights_on = False
asr       = ASR(model_dir = MODELDIR)
rec       = PulseRecorder (volume=VOLUME)
vad       = VAD()
tts       = TTS(engine="espeak", voice="en")

utt_map = {}
def add_utt (utterance, intent):
    utt_map[utterance] = intent

add_utt("hello computer",        Intent.HELLO)
add_utt("switch on the lights",  Intent.LIGHT)
add_utt("switch off the lights", Intent.LIGHT)
add_utt("switch on the radio",   Intent.RADIO)
add_utt("switch off the radio",  Intent.RADIO)

rec.start_recording()
print ("Please speak. (CTRL-C to exit)")

while True:
    samples = rec.get_samples()
    audio, finalize = vad.process_audio(samples)
    if not audio:
        continue

    user_utt, c = asr.decode(audio, finalize)
    print ("\r%s           " % user_utt, end='', flush=True)

    if finalize:
        print ()

        intent = utt_map.get(user_utt, None)
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
        if not intent:
            continue

        rec.stop_recording()
        print (resp)
        tts.say(resp)
        rec.start_recording()
