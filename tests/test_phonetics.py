#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2013, 2014, 2016, 2017 Guenter Bartsch
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

import logging
import unittest
from nltools.phonetics import ipa2xsampa, ipa2mary, xsampa2xarpabet, xs2xa_table, xsampa2ipa

class TestPhoneticAlphabets (unittest.TestCase):

    def setUp(self):
        self.seq = range(10)

    def test_ipa(self):

        res = ipa2xsampa ("EISENBAHN", u"ˈaɪ̯zən̩ˌbaːn")
        #print "res: %s" % res
        self.assertEqual (res, "'aIz@nba:n")

        res = ipa2xsampa ("DIPHTONGTEST", u"aɪɔɪaʊɜ'")
        #print "res: %s" % res
        self.assertEqual (res, "aIOIaU3")

        res = ipa2xsampa ("BON", u"bɔ̃")
        #print "res: %s" % res
        self.assertEqual (res, "bO~")

        res = ipa2xsampa ("RESTAURANT", u"ʁɛstɔʁɑ̃")
        #print "res: %s" % res
        self.assertEqual (res, "REstORA~")

        res = ipa2xsampa ("VIN", u"vɛ̃")
        #print "res: %s" % res
        self.assertEqual (res, "vE~")

        res = ipa2xsampa ("BRUN", u"bʁœ̃")
        #print "res: %s" % res
        self.assertEqual (res, "bR9~")

        res = ipa2xsampa ("POIGNANT", u"pwaɲɑ̃")
        #print "res: %s" % res
        self.assertEqual (res, "pwaJA~")

        res = ipa2mary ("EISENBAHN", u"ˈaɪ̯zən̩ˌbaːn")
        #print "res: %s" % res
        self.assertEqual (res, "'aIz@nba:n")

        res = ipa2mary ("DIPHTONGTEST", u"aɪɔɪaʊɜ'")
        #print "res: %s" % res
        self.assertEqual (res, "aIOIaUr='")

        res = ipa2mary ("BON", u"bɔ̃")
        #print "res: %s" % res
        self.assertEqual (res, "bO~")

        res = ipa2mary ("RESTAURANT", u"ʁɛstɔʁɑ̃")
        #print "res: %s" % res
        self.assertEqual (res, "REstORA~")

        res = ipa2mary ("VIN", u"vɛ̃")
        #print "res: %s" % res
        self.assertEqual (res, "vE~")

        res = ipa2mary ("BRUN", u"bʁœ̃")
        #print "res: %s" % res
        self.assertEqual (res, "bR9~")

        res = ipa2mary ("POIGNANT", u"pwaɲɑ̃")
        #print "res: %s" % res
        self.assertEqual (res, "pwaJA~")

        res = xsampa2ipa(u"entrée A~ t R e", u"A~ t R e")
        #print "res: %s" % res
        self.assertEqual (res, u"ɑ̃tʁe")

    def test_xarpa(self):

        res = xsampa2xarpabet ("JAHRHUNDERTE", "ja:6-'hUn-d6-t@")
        #print "res: %s" % res
        self.assertEqual (res, "Y AAH EX HH UU N D EX T AX")

        res = xsampa2xarpabet ("ABGESCHRIEBEN", "'ap-g@-SRi:-b@n")
        #print "res: %s" % res
        self.assertEqual (res, "AH P G AX SH RR IIH B AX N")

        res = xsampa2xarpabet ("ZUGEGRIFFEN", "'tsu:-g@-gRI-f@n")
        #print "res: %s" % res
        self.assertEqual (res, "TS UUH G AX G RR IH F AX N")

        res = xsampa2xarpabet ("AUSLEGUNG", "'aU-sle:-gUN")
        #print "res: %s" % res
        self.assertEqual (res, "AW S L EEH G UU NG")

        res = xsampa2xarpabet ("BON", "bO~")
        #print "res: %s" % res
        self.assertEqual (res, "B ON")

        res = xsampa2xarpabet ("RESTAURANT", "REstORA~")
        #print "res: %s" % res
        self.assertEqual (res, "RR EH S T OO RR AN")

        res = xsampa2xarpabet ("VIN", u"vE~")
        #print "res: %s" % res
        self.assertEqual (res, "V EN")

        res = xsampa2xarpabet ("BRUN", u"bR9~")
        #print "res: %s" % res
        self.assertEqual (res, "B RR OEN")

        res = xsampa2xarpabet ("POIGNANT", u"pwaJA~")
        #print "res: %s" % res
        self.assertEqual (res, "P W AH NJ AN")

    def test_xarpa_unique(self):

        # all xarpa transcriptions have to be unique

        uniq_xs = set()
        uniq_xa = set()

        for entry in xs2xa_table:
            xs = entry[0]
            xa = entry[1]
            #print (u"xs: %s, xa: %s" % (xs, xa)).encode('utf8')
            self.assertFalse (xa in uniq_xa)
            uniq_xa.add(xa)
            self.assertFalse (xs in uniq_xs)
            uniq_xs.add(xs)
        
if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)
    
    unittest.main()

