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

from nltools.sequiturclient import sequitur_gen_ipa

MODELFN = 'models/sequitur-voxforge-de-latest'

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

