#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2016, 2017 Guenter Bartsch
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# crude sequitur g2p interface
#

import logging
import tempfile
import traceback

import misc

from phonetics import xsampa2ipa

def sequitur_gen_ipa(modelfn, word):

    ipa = u''

    with tempfile.NamedTemporaryFile() as f:

        f.write((u'%s\n' % word).encode('utf8'))
        f.flush()

        cmd = ['g2p.py', '--encoding=UTF8', '--model', modelfn, '--apply', f.name]

        res = misc.run_command(cmd)

        logging.debug('%s' % ' '.join(cmd))

        for l in res:

            line = l.strip()

            logging.debug('%s' % line)

            if 'stack usage:' in line:
                continue

            if word in line.decode('utf8', errors='ignore'):
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

        cmd = ['g2p.py', '--encoding=UTF8', '--model', modelfn, '--apply', f.name]

        res = misc.run_command(cmd, capture_stderr=False)

        logging.debug('%s' % ' '.join(cmd))

        for l in res:

            line = l.strip()

            logging.debug('%s' % line)

            if 'stack usage:' in line:
                continue

            parts = line.decode('utf8', errors='ignore').split('\t')

            if len(parts) < 2:
                continue

            try:
                word = parts[0]
                if word in words:

                    xs = parts[1]
                    # print 'XS', xs
               
                    ipa = xsampa2ipa(word, xs)
                    ipa_map[word] = ipa
            except:
                logging.error("Error processing line %s:" % line)
                logging.error(traceback.format_exc())

    return ipa_map

