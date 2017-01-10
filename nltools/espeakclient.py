#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2014, 2016, 2017 Guenter Bartsch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# A simple espeak interface for phone generation and TTS output
#

import tempfile
import logging

from phonetics import ipa2xsampa, xsampa2ipa
from misc import run_command

def espeak_gen_ipa (voice, s):

    ipa = ''

    for line in run_command ( ['espeak', '-x', '--ipa=2', '-v', voice, '-q', s] ):
        ipa = line.decode('utf8').lstrip().rstrip()

    # filter out phonemes we do not handle but translating to X-SAMPA and back:

    xs = ipa2xsampa (s, ipa)
    xs = xs.replace ('r','R').replace('3','6').replace('A','a')
    ipa = xsampa2ipa (s, xs)

    return ipa

def espeak_synth (voice, s):

    wav = None

    with tempfile.NamedTemporaryFile() as f:
        cmd = ['espeak', '-v', voice, '-w', f.name, s]

        logging.debug(' '.join(cmd))

        for line in run_command ( cmd ):
            logging.debug(line)

        f.seek(0)
        wav = f.read()

        logging.debug('read %s, got %d bytes.' % (f.name, len(wav)))

    return wav

def espeak_synth_phonemes (voice, xs):

    wav = None

    with tempfile.NamedTemporaryFile() as f:

        cmd = ['espeak', '-v', voice, '-w', f.name, '[[%s]]' % xs]

        logging.debug('cmd: %s' % ' '.join(cmd))

        for line in run_command ( cmd ):
            logging.debug(line)

        f.seek(0)
        wav = f.read()

    return wav

