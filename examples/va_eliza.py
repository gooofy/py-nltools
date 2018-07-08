#!/usr/bin/env python3

# this is a complete voice assistant example complete with ELIZA fallback mode

from enum import Enum

from nltools.asr           import ASR
from nltools.pulserecorder import PulseRecorder
from nltools.vad           import VAD, BUFFER_DURATION
from nltools.tts           import TTS
from nltools.macro_engine  import MacroEngine
from nltools.misc          import edit_distance
from nltools.tokenizer     import tokenize
from eliza                 import eliza

MODELDIR            = '/opt/kaldi/model/kaldi-generic-en-tdnn_250'

SAMPLE_RATE         = 16000
FRAMES_PER_BUFFER   = int(SAMPLE_RATE * BUFFER_DURATION / 1000)
SOURCE              = 'CM108'
VOLUME              = 150
AGGRESSIVENESS      = 2
ED_THRESHOLD        = 2

class Intent(Enum):
    HELLO     = 1
    LIGHT     = 2
    RADIO     = 3

print ("Initializing....")

me = MacroEngine()

utterance_map = {}
def add_utterance (pattern, intent):
    for utterance, t in me.expand_macros('en', pattern):
        utt = ' '.join(utterance)
        utterance_map[utt] = intent

add_utterance("(hi|hello|ok) (computer|machine|raspberry)",                      Intent.HELLO)
add_utterance("(computer|) (please|) (turn|switch) (on|off) the (light|lights)", Intent.LIGHT)
add_utterance("(computer|) (please|) (turn|switch) the (light|lights) (on|off)", Intent.LIGHT)
add_utterance("(computer|) (please|) (turn|switch) (on|off) the (music|radio)",  Intent.RADIO)
add_utterance("(computer|) (please|) (turn|switch) the (music|radio) (on|off)",  Intent.RADIO)

radio_on  = False
lights_on = False

asr = ASR(model_dir = MODELDIR)

rec = PulseRecorder (SOURCE, SAMPLE_RATE, VOLUME)

vad = VAD(aggressiveness=AGGRESSIVENESS, sample_rate=SAMPLE_RATE)

tts = TTS(engine="espeak", voice="en")

eliza = eliza()

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

        best_dist = ED_THRESHOLD
        intent = None
        for utt in utterance_map:
            dist = edit_distance (tokenize (utt, lang='en'), tokenize (user_utt, lang='en'))
            if ( dist < ED_THRESHOLD ) and ( dist < best_dist ):
                best_dist = dist
                intent = utterance_map[utt]

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
        rec.start_recording(FRAMES_PER_BUFFER)

