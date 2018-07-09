#!/usr/bin/env python3
from nltools.tts import TTS

tts = TTS(engine="espeak", voice="en")
tts.say("hello from your pi")
