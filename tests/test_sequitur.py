#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2014, 2016, 2017, 2018 Guenter Bartsch
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

from nltools.sequiturclient import sequitur_gen_ipa

MODELFN = 'models/sequitur-dict-de.ipa-latest'

G2P_TESTS = [
                (u'gelbseidenen',     u"'g\u025blb-za\u026a-d\u0259-n\u0259n", ),
                (u'unmute',           u"'\u0294\u028an-mu\u02d0-t\u0259",      ),
            ]

class TestSequitur (unittest.TestCase):

    def test_g2p(self):

        for word, ipa in G2P_TESTS:

            sq_ipa = sequitur_gen_ipa (MODELFN, word)

            self.assertEqual (sq_ipa, ipa)


if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)
    # logging.basicConfig(level=logging.DEBUG)

    unittest.main()

