#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2017, 2018 Guenter Bartsch
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
        self.assertEqual (tokenize(u"ip_1 ip_2 x_1"), [u'ip_1', u'ip_2', u'x_1'])
# Sowie das zauberische Fuhrwerk im dichten Gebüsch verschwand, noch im sanften Nachhallen der Harmonikatöne, fiel Balthasar, ganz außer sich vor Wonne und Entzücken, dem Freunde um den Hals und rief: Referendarius, wir sind gerettet!
        self.assertEqual (tokenize(u"und rief: Referendarius, wir sind gerettet", keep_punctuation=True), 
                          [u'und', u'rief', u':', u'referendarius', u',', u'wir', u'sind', u'gerettet'])
        self.assertEqual (tokenize(u"Flughafen Leipzig/Halle ist"), [u'flughafen', u'leipzig', u'halle', u'ist'])
        self.assertEqual (tokenize(u"nach … Wecker"), [u'nach', u'wecker'])

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

    def test_tokenize_french(self):
        self.assertEqual (tokenize(u"aujourd'hui", lang='fr'), [u"aujourd'hui"])
        self.assertEqual (tokenize(u"entr’ouvert", lang='fr'), [u"entr'ouvert"])
        self.assertEqual (tokenize(u"qu’il", lang='fr'), [u"qu'il"])
        self.assertEqual (tokenize(u"jusqu'alors", lang='fr'), [u"jusqu'alors"])
        self.assertEqual (tokenize(u"j’adore", lang='fr'), [u"j'adore"])
        self.assertEqual (tokenize(u"je l'adore", lang='fr'), [u"je", u"l'adore"])
        self.assertEqual (tokenize(u"il s'adore", lang='fr'), [u"il", u"s'adore"])
        self.assertEqual (tokenize(u"sagement les émigrants suivent les péripéties de l'écran", lang='fr'), [u"sagement", u"les", u"émigrants", u"suivent", u"les", u"péripéties", u"de", u"l'écran"])
        self.assertEqual (tokenize(u"-c'était", lang='fr'), [u"c'était"])
        self.assertEqual (tokenize(u"—c'était", lang='fr'), [u"—c'était"])
        self.assertEqual (tokenize(u"pensa-t-il", lang='fr'), [u"pensa-t-il"])
        self.assertEqual (tokenize(u"jugea-t-elle", lang='fr'), [u"jugea-t-elle"])
        self.assertEqual (tokenize(u"dira-t-on", lang='fr'), [u"dira-t-on"])
        self.assertEqual (tokenize(u"fallait-il", lang='fr'), [u"fallait-il"])
        self.assertEqual (tokenize(u"zéro (9 degrés", lang='fr'), [u"zéro", u"neuf", u"degrés"])
        self.assertEqual (tokenize(u"du 31 décembre 1861!", lang='fr'), [u"du", u"trente", u"et", u"un", u"décembre", u"mille", u"huit", "cent", "soixante", u"et", u"un"])        
        self.assertEqual (tokenize(u"FR3", lang='fr'), [u"fr3"])
        self.assertEqual (tokenize(u"G20", lang='fr'), [u"g20"])
        self.assertEqual (tokenize(u"d'aujourd'hui", lang='fr'), [u"d'aujourd'hui"])
        self.assertEqual (tokenize(u"qu'aujourd'hui", lang='fr'), [u"qu'aujourd'hui"])

    def test_tokenize_numbers_french(self):
        self.assertEqual (tokenize(u'1 2 3 4', lang='fr'), [u'un', u'deux', u'trois', u'quatre'])
        self.assertEqual (tokenize(u'00 01 02 03 04', lang='fr'), [u'zéro', u'un', u'deux', u'trois', u'quatre'])
        self.assertEqual (tokenize(u'5,5 %', lang='fr'), [u'cinq', u'virgule', u'cinq', u'pour', u'cent'])
        self.assertEqual (tokenize(u'-1 -2 3 -42', lang='fr'), [u'moins', u'un', u'moins', u'deux', u'trois', u'moins', u'quarante-deux'])
        self.assertEqual (tokenize(u'1,2 3.456', lang='fr'), [u'un', u'virgule', u'deux', u'trois', u'virgule', u'quatre', u'cent', u'cinquante-six'])
        self.assertEqual (tokenize(u'-42.23', lang='fr'), [u'moins', u'quarante-deux', u'virgule', u'vingt-trois'])
        self.assertEqual (tokenize(u'71', lang='fr'), [u'soixante', u'et', u'onze'])
        self.assertEqual (tokenize(u'72', lang='fr'), [u'soixante-douze'])
        self.assertEqual (tokenize(u'80', lang='fr'), [u'quatre-vingts'])
        self.assertEqual (tokenize(u'81', lang='fr'), [u'quatre-vingt-un'])
        self.assertEqual (tokenize(u'91', lang='fr'), [u'quatre-vingt-onze'])
        self.assertEqual (tokenize(u'92', lang='fr'), [u'quatre-vingt-douze'])
        self.assertEqual (tokenize(u'1,15', lang='fr'), [u'un', u'virgule', u'quinze'])
        self.assertEqual (tokenize(u'1,015', lang='fr'), [u'un', u'virgule', u'zéro', u'quinze'])
        self.assertEqual (tokenize(u'1,0015', lang='fr'), [u'un', u'virgule', u'zéro', u'zéro', u'quinze'])
        self.assertEqual (tokenize(u'1,00015', lang='fr'), [u'un', u'virgule', u'zéro', u'zéro', u'zéro', u'quinze'])
        self.assertEqual (tokenize(u'1,000015', lang='fr'), [u'un', u'virgule', u'zéro', u'zéro', u'zéro', u'zéro', u'quinze'])
        self.assertEqual (tokenize(u'1,00001523', lang='fr'), [u'un', u'virgule', u'zéro', u'zéro', u'zéro', u'zéro', u'un', u'cinq', u'deux', u'trois'])
        self.assertEqual (tokenize(u'1000000 2234567', lang='fr'), [u'un', u'million', u'deux', u'millions', u'deux', u'cent', u'trente-quatre', u'mille', u'cinq', u'cent', u'soixante-sept'])
        self.assertEqual (tokenize(u'42,00', lang='fr'), [u'quarante-deux', u'virgule', u'zéro', u'zéro'])

    def test_nombre_en_mots(self):
        self.assertEqual (nombre_en_mots(1), u'un')
        self.assertEqual (nombre_en_mots(19), u'dix-neuf')
        self.assertEqual (nombre_en_mots(20), u'vingt')
        self.assertEqual (nombre_en_mots(21), u'vingt et un')
        self.assertEqual (nombre_en_mots(23), u'vingt-trois')
        self.assertEqual (nombre_en_mots(30), u'trente')
        self.assertEqual (nombre_en_mots(31), u'trente et un')
        self.assertEqual (nombre_en_mots(60), u'soixante')
        self.assertEqual (nombre_en_mots(61), u'soixante et un')
        self.assertEqual (nombre_en_mots(62), u'soixante-deux')
        self.assertEqual (nombre_en_mots(70), u'soixante-dix')
        self.assertEqual (nombre_en_mots(71), u'soixante et onze')
        self.assertEqual (nombre_en_mots(79), u'soixante-dix-neuf')
        self.assertEqual (nombre_en_mots(80), u'quatre-vingts')
        self.assertEqual (nombre_en_mots(81), u'quatre-vingt-un')
        self.assertEqual (nombre_en_mots(85), u'quatre-vingt-cinq')
        self.assertEqual (nombre_en_mots(90), u'quatre-vingt-dix')
        self.assertEqual (nombre_en_mots(91), u'quatre-vingt-onze')
        self.assertEqual (nombre_en_mots(99), u'quatre-vingt-dix-neuf')
        self.assertEqual (nombre_en_mots(120), u'cent vingt')
        self.assertEqual (nombre_en_mots(121), u'cent vingt et un')
        self.assertEqual (nombre_en_mots(123), u'cent vingt-trois')
        self.assertEqual (nombre_en_mots(1515), u'mille cinq cent quinze')

if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)
    
    unittest.main()

