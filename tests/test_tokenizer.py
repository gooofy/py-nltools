#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2017 Guenter Bartsch
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

from nltools.tokenizer import *

class TestTokenizer (unittest.TestCase):

    def setUp(self):
        self.seq = range(10)

    # FIXME
    # def test_latin1(self):
    #     self.assertTrue (detect_latin1('/home/ai/voxforge/de/audio/ralfherzog-20071220-de34/etc/prompts-original'))
    #     self.assertFalse (detect_latin1('/home/ai/voxforge/de/audio/mjw-20110527-dyg/etc/prompts-original'))

    def test_tokenize_special(self):

        self.assertEqual (tokenize(u"„kamel“"), [u'kamel'])
        self.assertEqual (tokenize(u"$test"), [u'dollar', u'test'])

    def test_tokenize_wrt(self):

        self.assertEqual (tokenize(u"foo circa bar"), [u'foo', u'circa', u'bar'])
        self.assertEqual (tokenize(u"foo ok bar"), [u'foo', u'okay', u'bar'])
        self.assertEqual (tokenize(u"fook ok baokr"), [u'fook', u'okay', u'baokr'])
        self.assertEqual (tokenize(u"o.k.bar"), [u'okay', u'bar'])
        self.assertEqual (tokenize(u"foo o. k.bar"), [u'foo', u'okay', u'bar'])
        
    def test_tokenize_punctuation(self):

        self.assertEqual (tokenize(u"abc, def. zzz!   (      abc<?)"), [u'abc', u'def', u'zzz', u'abc'])
        self.assertEqual (tokenize(u"abc, def. zzz!   (      abc<?)", keep_punctuation=True), 
                          [u'abc', u',', u'def', u'.', u'zzz', u'!', u'(', u'abc', u'<', u'?', u')'])

    def test_tokenize_numbers(self):

        self.assertEqual (tokenize(u"des individual- verwendungs-weise"), [u"des", u"individual", u"verwendungs", u"weise"])
        self.assertEqual (tokenize(u"-1 -2 3 -42"), [u"minus", u"eins", u"minus", u"zwei", u"drei", u"minus", u"zweiundvierzig"])
        self.assertEqual (tokenize(u"1,2 3.456"), [u"eins", u"komma", u"zwei", u"drei", u"komma", u'vier', u'fünf', u'sechs'])
        self.assertEqual (tokenize(u"-42.23"), [u'minus', u'zweiundvierzig', u'komma', u'zwei', u'drei'])
        self.assertEqual (tokenize(u"1000000 2234567"), [u'einemillion', u'zweimillionenzweihundertvierunddreißigtausendfünfhundertsiebenundsechzig'])
        self.assertEqual (tokenize(u"zahlten 1000000"), [u'zahlten', u'einemillion'])

        self.assertEqual (tokenize(u"b5 mal 3 in abc5"), [u'b5', u'mal', u'drei', u'in', u'abc5'])

        self.assertEqual (tokenize(u"Mein Name ist HAL 9000."), [u'mein', u'name', u'ist', u'hal', u'neuntausend'])

    def test_ws(self):
        self.assertEqual (compress_ws('   ws   foo bar'), ' ws foo bar')

    def test_isgalnum(self):
        self.assertEqual (isgalnum(u'§1234%'), True)
        self.assertEqual (isgalnum(u'§1_234%'), False)

    def test_split(self):
        self.assertEqual (tokenize(u"1 2 3 4"), ["eins", "zwei", "drei", "vier"])
        self.assertEqual (tokenize(u"00 01 02 03 04"), ["null", "eins", "zwei", "drei", "vier"])
        self.assertEqual (tokenize(u"z.B. u. U. Prof. Dr. Dipl. Ing."), [u'zum', u'beispiel', u'unter', u'umständen', u'professor', u'doktor', u'diplom', u'ingenieur'])

    def test_preserve_macros(self):
        self.assertEqual (tokenize(u"was ist @ARTICLE:W name von @KNOWN_PERSON_DE:LABEL", keep_macros=True), [u"was", u"ist", u"@article:w", u"name", u"von", u"@known_person_de:label"])
        self.assertEqual (tokenize(u"what is @ARTICLE:W name of @KNOWN_PERSON_DE:LABEL", lang='en', keep_macros=True), [u"what", u"is", u"@article:w", u"name", u"of", u"@known_person_de:label"])

    def test_zahl_in_worten(self):

        for i in range(10000):
            u = unicode(i)
            z = zahl_in_worten(i)
            #print "%4s : %s" % (u, z)
            if u in wrt:
                self.assertEqual (z, wrt[u])

    def test_editdist(self):
        self.assertEqual (edit_distance(
                             tokenize(u'die leistung wurde zurückverlangt'), 
                             tokenize(u'die leistung wurde zurückverlangt')), 0)
        self.assertEqual (edit_distance(
                             tokenize(u'die leistung wurde'), 
                             tokenize(u'die leistung wurde zurückverlangt')), 1)
        self.assertEqual (edit_distance(
                             tokenize(u'DIE LEISTUNG'), 
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT')), 2)
        self.assertEqual (edit_distance(
                             tokenize(u'DIE'), 
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT')), 3)
        self.assertEqual (edit_distance(
                             tokenize(u'DIE ZURÜCKVERLANGT'), 
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT')), 2)
        self.assertEqual (edit_distance(
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT'), 
                             tokenize(u'LEISTUNG WURDE ZURÜCKVERLANGT')), 1)
        self.assertEqual (edit_distance(
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT'), 
                             tokenize(u'WURDE ZURÜCKVERLANGT')), 2)
        self.assertEqual (edit_distance(
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT'), 
                             tokenize(u'ZURÜCKVERLANGT')), 3)
        self.assertEqual (edit_distance(
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT'), 
                             tokenize(u'')), 4)
        self.assertEqual (edit_distance(
                             tokenize(u'DIE LEISTUNG WURDE ZURÜCKVERLANGT'), 
                             tokenize(u'LEISTUNG FOO ZURÜCKVERLANGT')), 2)
        self.assertEqual (edit_distance(
                             tokenize(u'SIE IST FÜR DIE LEISTUNG DANKBAR'), 
                             tokenize(u'SIE STRITTIG LEISTUNG DANKBAR')), 3)

    def test_kill_umlauts(self):
        self.assertEqual (kill_umlauts(u'Ü ü Ö ö Ä ä ß'), 'Ue ue Oe oe Ae ae ss')

    def test_tokenize_english(self):

        self.assertEqual (tokenize(u"this module’s level", lang='en'), [u'this', u"module's", u'level'])
        self.assertEqual (tokenize(u"$test sequences that don’t correspond can't", lang="en"), [ u"dollar", u"test", u"sequences", u"that", u"don't", u"correspond", u"can't" ])
        self.assertEqual (tokenize(u"but I can't and I'm good.", lang='en'), [u'but', u'i', u"can't", u"and", u"i'm", u"good"])
        self.assertEqual (tokenize(u"we're good she'd do that.", lang='en'), [u"we're", u"good", u"she'd", u"do", u"that"])
        self.assertEqual (tokenize(u"we'll be good.", lang='en'), [u"we'll", u"be", u"good"])
        self.assertEqual (tokenize(u"ZUCKERBERG'S", lang='en'), [u"zuckerberg's"])
        self.assertEqual (tokenize(u"THIS IS ZUCKERBERG'S PROPERTY", lang='en'), [u'this', u'is', u"zuckerberg's", u'property'])
        self.assertEqual (tokenize(u"Okay. A 5% raise, and", lang='en'), [u'ok', u'a', u'five', 'percent', u'raise', u'and'])

    def test_tokenize_numbers_english(self):
        self.assertEqual (tokenize(u"1 2 3 4", lang='en'), ["one", "two", "three", "four"])
        self.assertEqual (tokenize(u"00 01 02 03 04", lang='en'), ["zero", "one", "two", "three", "four"])

if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)
    
    unittest.main()

