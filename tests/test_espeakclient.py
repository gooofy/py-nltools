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

import unittest
import logging

from nltools.espeakclient import espeak_gen_ipa, espeak_synth, espeak_synth_phonemes
from nltools.phonetics import ipa2xsampa

G2P_TESTS = [
                (u'GELBSEIDENEN',     u"g'\u025blbza\u026ad\u0259n\u0259n",                 "g'ElbzaId@n@n"),
                (u'UNMUTE',           u"'\u028anmu\u02d0t\u0259",                           "'Unmu:t@"),
                (u'GESCHIRRSCHEUERN', u"g\u0259\u0283'\u026a\u0281\u0283\u0254\xf8\u0250n", "g@S'IRSO26n"),
                (u"DÜSTRE",           u"d'\u028fst\u0281\u0259",                            "d'YstR@"),
                (u"EINGANGE",         u"'a\u026anga\u0273\u0259",                           "'aIngaN@"),
                (u"AUSSCHLÄGEN",      u"'a\u028as\u0283l\u025b\u02d0g\u0259n",              "'aUsSlE:g@n"),
                (u"NACHHÄNGEND",      u"n'axh\u025b\u0273\u0259nt",                         "n'axhEN@nt"),
                (u"HAUPTSTRAßEN",     u"h'a\u028aptst\u0281'a\u02d0s'e\u02d0n",             "h'aUptstR'a:s'e:n"),
                (u"HOCHWEISEN",       u"h'o\u02d0xva\u026az\u0259n",                        "h'o:xvaIz@n"),
                (u"DICKER",           u"d'\u026ak\u0250",                                   "d'Ik6"),
            ]

class TestEspeak (unittest.TestCase):

    def test_g2p(self):

        for word, ipa, xs in G2P_TESTS:

            es_ipa = espeak_gen_ipa ("de", word)
            logging.debug ((u'%12s: %s %s' % (word, ipa, repr(ipa))).encode('utf8'))

            self.assertEqual (es_ipa, ipa)

            es_xs = ipa2xsampa (word, ipa)
            logging.debug ("X-SAMPA: %s" % xs)

            self.assertEqual (es_xs, xs)


    def test_synth(self):
        wav = espeak_synth ("de", "Hallo")
        logging.debug('wav len: %d bytes.' % len(wav))
        self.assertGreater (len(wav), 100)

    def test_synth_phonemes(self):
        wav = espeak_synth_phonemes ("de", "'Unmu:t@")
        logging.debug('wav len: %d bytes.' % len(wav))
        self.assertGreater (len(wav), 100)

if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)
    # logging.basicConfig(level=logging.DEBUG)

    unittest.main()

