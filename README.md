# py-nltools

A collection of random bits and pieces of code for natural language processing. Most of them are
pretty hands-on simple-minded compared to projects like NLTK or spaCy and therefore in no way meant
to replace those. 

Non-exhaustive liste of modules contained:

* phonetics: translation functions between various phonetic alphabets (IPA, X-SAMPA, X-ARPABET, ...)
* tts\_client: abstraction layer towards using eSpeak NG, MaryTTS or a remote TTS server and sequitur g2p
* maryclient: g2p and speech synthesis using Mary TTS
* sequiturclient: g2p using sequitur
* pulseplayer: audio playback through pulseaudio
* tokenizer: english and german word tokenizer aimed at spoken language applications
* threadpool: simple thread pool implementation

I plan to add modules as I need them in my AI projects.


Requirements
============

*Note*: probably incomplete.

* Python 2.7 
* Mary TTS
* espeak-ng, py-espeak-ng
* sequitur
* pulseaudio

License
=======

My own code is LGPLv3 licensed unless otherwise noted in the script's copyright
headers.

Some scripts and files are based on works of others, in those cases it is my
intention to keep the original license intact. Please make sure to check the
copyright headers inside for more information.

Author
======

Guenter Bartsch <guenter@zamia.org>

