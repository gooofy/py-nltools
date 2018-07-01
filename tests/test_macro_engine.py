#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2018 Guenter Bartsch
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

from nltools.macro_engine  import MacroEngine
from nltools               import misc

class TestME (unittest.TestCase):

    def test_implicit_me(self):

        me = MacroEngine()

        expansions = me.expand_macros('en', "(a|b|c) (c|d|e) foo")

        logging.debug(repr(expansions))

        self.assertEqual(len(expansions), 9)
        self.assertEqual(u" ".join(expansions[0][0]), u"c e foo")

    def test_explicit_me(self):

        me = MacroEngine()

        me.add_macro_expansion("prefix",   u"")
        me.add_macro_expansion("prefix",   u"please")
        me.add_macro_expansion("prefix",   u"computer")
        me.add_macro_expansion("location", u"living room")
        me.add_macro_expansion("location", u"bedroom")
        me.add_macro_expansion("location", u"kitchen")


        expansions = me.expand_macros('en', "{prefix:W} switch (on|off) the light in the {location:W}")

        logging.debug(repr(expansions))

        self.assertEqual(len(expansions), 18)
        self.assertEqual(u" ".join(expansions[0][0]), u"computer switch off the light in the kitchen")

if __name__ == "__main__":

    # logging.basicConfig(level=logging.ERROR)
    logging.basicConfig(level=logging.DEBUG)

    unittest.main()

