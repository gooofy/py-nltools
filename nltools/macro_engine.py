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

#
# simple macro engine aimed at generating natural language expansions
#
# maintains dict of named macros for various languages
# contains utility functions that expand macros to produce
# training data input
#

import logging

from copy                import copy
from past.builtins       import basestring

from nltools.tokenizer   import tokenize

class MacroEngine(object):

    def __init__(self):
        self.named_macros = {}

    def add_macro_expansion(self, name, expansion):
        if not name in self.named_macros:
            self.named_macros[name] = []

        if isinstance(expansion, dict):
            exp = expansion
        else:
            exp = {'W': expansion}

        self.named_macros[name].append(exp)

    def expand_macros (self, lang, txt):

        logging.debug(u"expand macros  : %s" % txt)

        implicit_macros = {}

        txt2 = ''

        i = 0
        while i<len(txt):

            if txt[i] == '(':

                j = txt[i+1:].find(')')
                if j<0:
                    raise Exception (') missing')
                j += i

                # extract macro

                macro_s = txt[i+1:j+1]

                # print "macro_s: %s" % macro_s

                macro_name = 'MACRO_%d' % len(implicit_macros)

                implicit_macros[macro_name] = []
                for s in macro_s.split('|'):
                    sub_parts = tokenize(s, lang=lang, keep_punctuation=False)
                    implicit_macros[macro_name].append({'W': sub_parts})

                txt2 += '{' + macro_name + ':W}'

                i = j+2
            else:

                txt2 += txt[i]
                i+=1

        logging.debug ( "implicit macros: %s" % repr(implicit_macros) )
        logging.debug ( "txt2           : %s" % txt2 )

        parts = []
        for p1 in txt2.split('{'):
            for p2 in p1.split('}'):
                parts.append(p2)

        done = []

        todo = [ (parts, 0, [], {}, {}) ]

        # import pdb; pdb.set_trace()
        while len(todo)>0:

            parts1, cnt, r, mpos, macro_rs = todo.pop()

            if cnt >= len(parts1):
                done.append((r, mpos))
                continue

            p1 = parts1[cnt]

            if cnt % 2 == 1:
                
                sub_parts = p1.split(':')

                if len(sub_parts) != 2:
                    raise Exception ('syntax error in macro call %s' % repr(p1))

                name = sub_parts[0]

                if name == 'empty':
                    todo.append((parts, cnt+1, copy(r), mpos, copy(macro_rs)))
                else:

                    vn    = sub_parts[1]

                    if name in macro_rs:
                        macro = [ macro_rs[name] ]
                    else:
                        macro = self.named_macros.get(name, None)
                        if not macro:
                            macro = implicit_macros.get(name, None)
                        if not macro:
                            raise Exception ('unknown macro "%s" called' % name)

                    for r3 in macro:
                        r1        = copy(r)
                        mpos1     = copy(mpos)
                        macro_rs1 = copy(macro_rs)

                        macro_rs1[name] = r3

                        # take care of multiple invocactions of the same macro
        
                        mpnn = 0
                        while True:
                            mpn = '%s_%d_start' % (name, mpnn)
                            if not mpn in mpos1:
                                break
                            mpnn += 1

                        mpos1['%s_%d_start' % (name, mpnn)] = len(r1)
                        s3 = r3[vn]
                        if isinstance (s3, basestring):
                            s3 = tokenize (s3, lang=lang)
                            r3[vn] = s3
                        r1.extend(r3[vn])
                        mpos1['%s_%d_end' % (name, mpnn)]   = len(r1)

                        for vn3 in r3:
                            mpos1['%s_%d_%s' % (name, mpnn, vn3.lower())] = r3[vn3]

                        todo.append((parts, cnt+1, r1, mpos1, macro_rs1))
                        
                        # if name == 'home_locations':
                        #     import pdb; pdb.set_trace()

            else:

                sub_parts = tokenize(p1, lang=lang, keep_punctuation=False)

                r  = copy(r)
                r.extend(sub_parts)

                todo.append((parts, cnt+1, r, mpos, macro_rs))

        return done

