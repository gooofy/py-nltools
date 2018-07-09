#!/usr/bin/env python3
import logging
logging.basicConfig(level=logging.INFO)
from enum                  import Enum
from nltools.asr           import ASR
from nltools.pulserecorder import PulseRecorder
from nltools.vad           import VAD
from nltools.tts           import TTS
from nltools.macro_engine  import MacroEngine
from nltools.misc          import edit_distance
from nltools.tokenizer     import tokenize
from eliza                 import eliza

MODELDIR          = '/opt/kaldi/model/kaldi-generic-en-tdnn_250'
VOLUME            = 150
ED_THRESHOLD      = 2

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
me        = MacroEngine()
eliza     = eliza()

utt_map   = {}
def add_utt (pattern, intent):
    for utterance, t in me.expand_macros('en', pattern):
        utt = ' '.join(utterance)
        utt_map[utt] = intent

add_utt("(hi|hello|ok) computer",             Intent.HELLO)
add_utt("switch (on|off) the (light|lights)", Intent.LIGHT)
add_utt("switch the (light|lights) (on|off)", Intent.LIGHT)
add_utt("switch (on|off) the (music|radio)",  Intent.RADIO)
add_utt("switch the (music|radio) (on|off)",  Intent.RADIO)

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

        best_dist = ED_THRESHOLD
        intent = None
        for utt in utt_map:
            dist = edit_distance (tokenize (utt, lang='en'), 
                       tokenize (user_utt, lang='en'))
            if (dist<ED_THRESHOLD) and (dist<best_dist):
                best_dist = dist
                intent    = utt_map[utt]

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
            resp = eliza.respond (user_utt)

        rec.stop_recording()
        print (resp)
        tts.say(resp)
        rec.start_recording()
