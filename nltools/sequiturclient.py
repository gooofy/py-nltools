#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2016, 2017 Guenter Bartsch
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
# crude sequitur g2p interface
#

import logging
import tempfile

import misc

from phonetics import xsampa2ipa

def sequitur_gen_ipa(modelfn, word):

    ipa = u''

    with tempfile.NamedTemporaryFile() as f:

        f.write((u'%s\n' % word).encode('utf8'))
        f.flush()

        cmd = ['g2p.py', '--model', modelfn, '--apply', f.name]

        res = misc.run_command(cmd)

        logging.debug('%s' % ' '.join(cmd))

        for l in res:

            line = l.strip()

            logging.debug('%s' % line)

            if 'stack usage:' in line:
                continue

            if word in line.decode('utf8'):
                parts = line.split('\t')

                if len(parts) < 2:
                    continue

                xs = parts[1]
                # print 'XS', xs
           
                ipa = xsampa2ipa(word, xs)

    return ipa

def sequitur_gen_ipa_multi(modelfn, words):

    ipa_map ={}

    with tempfile.NamedTemporaryFile() as f:

        for word in words:
            f.write((u'%s\n' % word).encode('utf8'))
        f.flush()

        cmd = ['g2p.py', '--model', modelfn, '--apply', f.name]

        res = misc.run_command(cmd)

        logging.debug('%s' % ' '.join(cmd))

        for l in res:

            line = l.strip()

            logging.debug('%s' % line)

            if 'stack usage:' in line:
                continue

            parts = line.decode('utf8').split('\t')

            if len(parts) < 2:
                continue

            word = parts[0]
            if word in words:

                xs = parts[1]
                # print 'XS', xs
           
                ipa = xsampa2ipa(word, xs)
                ipa_map[word] = ipa

    return ipa_map

