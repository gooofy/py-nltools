# py-nltools

A collection of random bits and pieces of code for natural language processing. Most of them are
pretty hands-on simple-minded compared to projects like NLTK or spaCy and therefore in no way meant
to replace those. 

Non-exhaustive liste of modules contained:

* phonetics: translation functions between various phonetic alphabets (IPA, X-SAMPA, X-ARPABET, ...)
* espeakclient: g2p and speech synthesis using espeak
* maryclient: g2p and speech synthesis using Mary TTS
* sequiturclient: g2p using sequitur
* pulseplayer: audio playback through pulseaudio
* tokenizer: (as of this writing: german only) word tokenizer aimed at spoken language applications

I plan to add modules as I need them in my AI projects.


Requirements
============

*Note*: very incomplete.

* Python 2.7 
* Mary TTS
* espeak
* pulseaudio

License
=======

My own code is LGPLv3 licensed unless otherwise noted in the scritp's copyright
headers.

Some scripts and files are based on works of others, in those cases it is my
intention to keep the original license intact. Please make sure to check the
copyright headers inside for more information.

Author
======

Guenter Bartsch <guenter@zamia.org>

