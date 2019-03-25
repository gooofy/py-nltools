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

#
# big phoneme table
#
# entries:
# ( IPA, XSAMPA, MARY, ESPEAK )
#

MAX_PHONEME_LENGTH = 2

big_phoneme_table = [

        #
        # stop
        #

        ( u'p' , 'p' , 'p', 'p' ),
        ( u'b' , 'b' , 'b', 'b' ),
        ( u't' , 't' , 't', 't' ),
        ( u'd' , 'd' , 'd', 'd' ),
        ( u'k' , 'k' , 'k', 'k' ),
        ( u'g' , 'g' , 'g', 'g' ),
        ( u'ʔ' , '?' , '?', '?' ),

        #
        # 2 consonants
        #

        ( u'pf' , 'pf' , 'pf' , 'pf' ),
        ( u'ts' , 'ts' , 'ts' , 'ts' ),
        ( u'tʃ' , 'tS' , 'tS' , 'tS' ),
        ( u'dʒ' , 'dZ' , 'dZ' , 'dZ' ),

        #
        # fricative
        #

        ( u'f' , 'f' , 'f' , 'f' ),
        ( u'v' , 'v' , 'v' , 'v' ),
        ( u'θ' , 'T' , 'T' , 'T' ),
        ( u'ð' , 'D' , 'D' , 'D' ),
        ( u's' , 's' , 's' , 's' ),
        ( u'z' , 'z' , 'z' , 'z' ),
        ( u'ʃ' , 'S' , 'S' , 'S' ),
        ( u'ʒ' , 'Z' , 'Z' , 'Z' ),
        ( u'ç' , 'C' , 'C' , 'C' ),
        ( u'j' , 'j' , 'j' , 'j' ),
        ( u'x' , 'x' , 'x' , 'x' ),
        ( u'ʁ' , 'R' , 'R' , 'R' ),
        ( u'h' , 'h' , 'h' , 'h' ),
        ( u'ɥ' , 'H' , 'H' , 'H' ),

        #
        # nasal
        #

        ( u'm' , 'm' , 'm' , 'm' ),
        ( u'n' , 'n' , 'n' , 'n' ),
        ( u'ɳ' , 'N' , 'N' , 'N' ),
        ( u'ɲ' , 'J' , 'J' , 'J' ),

        #
        # liquid
        #

        ( u'l' , 'l' , 'l' , 'l' ),
        ( u'r' , 'r' , 'r' , 'r' ),

        #
        # glide
        #

        ( u'w' , 'w' , 'w', 'w' ),
        # see above ( u'j' , 'j' , 'j' ),

        #
        # vowels: monophongs
        #

        # front
        ( u'i' , 'i' , 'i' , 'i' ),
        ( u'ɪ' , 'I' , 'I' , 'I' ),
        ( u'y' , 'y' , 'y' , 'y' ),
        ( u'ʏ' , 'Y' , 'Y' , 'y' ),
        ( u'e' , 'e' , 'e' , 'e' ),
        ( u'ø' , '2' , '2' , 'W' ),
        ( u'œ' , '9' , '9' , 'W' ),
        ( u'œ̃' , '9~' , '9~' , 'W~' ),
        ( u'ɛ' , 'E' , 'E' , 'E' ),
        ( u'ɛ̃' , 'E~' , 'E~' , 'E~' ),
        ( u'æ' , '{' , '{' , 'a' ),
        ( u'a' , 'a' , 'a' , 'a' ),

        # central
        ( u'ʌ' , 'V' , 'V' , 'A'  ),
        ( u'ə' , '@' , '@' , '@'  ),
        ( u'ɐ' , '6' , '6' , '@' ),
        ( u'ɜ' , '3' , 'r=', '3'  ), 

        # back
        ( u'u' , 'u' , 'u' , 'u' ),
        ( u'ʊ' , 'U' , 'U' , 'U' ),
        ( u'o' , 'o' , 'o' , 'o' ),
        ( u'ɔ' , 'O' , 'O' , 'O' ),
        ( u'ɔ̃' , 'O~' , 'O~' , 'O~' ),
        ( u'ɑ' , 'A' , 'A' , 'A' ),
        ( u'ɑ̃' , 'A~' , 'A~' , 'A~' ),
        ( u'ɒ' , 'Q' , 'Q' , 'Q' ),

        # diphtongs

        ( u'aɪ' , 'aI' , 'aI' , 'aI' ),
        ( u'ɔɪ' , 'OI' , 'OI' , 'OI' ),
        ( u'aʊ' , 'aU' , 'aU' , 'aU' ),
        ( u'ɔʏ' , 'OY' , 'OY' , 'OY' ),

        #
        # misc
        #
        ( u'ː'  , ':'  , ':'  , ':'  ),
        ( u'-'  , '-'  , '-'  , '-'  ),
        ( u'\'' , '\'' , '\'' , '\'' ),

        #
        # noise
        #

        ( u'#' , '#' , '#' ),
    ]

IPA_normalization = {
        u':' : u'ː',
        u'?' : u'ʔ',
        u'ɾ' : u'ʁ',
        u'ɡ' : u'g',
        u'ŋ' : u'ɳ',
        u' ' : None,
        u'(' : None,
        u')' : None,
        u'\u02c8' : u'\'',
        u'\u032f' : None,
        u'\u0329' : None,
        u'\u02cc' : None,
        u'\u200d' : None,
        u'\u0279' : None,
        u'\u0361' : None,
    }

IPA_vowels = set([
        u'i' ,
        u'ɪ' ,
        u'y' ,
        u'ʏ' ,
        u'e' ,
        u'ø' ,
        u'œ' ,
        u'ɛ' ,
        u'æ' ,
        u'a' ,

        # central
        u'ʌ' ,
        u'ə' ,
        u'ɐ' ,
        u'ɜ' ,

        # back
        u'u' ,
        u'ʊ' ,
        u'o' ,
        u'ɔ' ,
        u'ɑ' ,
        u'ɒ' ,

        # diphtongs

        u'aɪ' ,
        u'ɔɪ' ,
        u'aʊ' ,
        u'ɔʏ' ])

XSAMPA_normalization = {
    ' ': None,
    '~': None,
    '0': 'O',
    ',': None,
    }

def _normalize (s, norm_table):

    buf = ""

    for c in s:

        if c in norm_table:
            
            x = norm_table[c]
            if x:
                buf += x
        else:
            buf += c

    return buf

def _translate (graph, s, f_idx, t_idx, spaces=False):

    buf = ""
    i = 0
    l = len(s)

    while i < l:

        found = False

        for pl in range(MAX_PHONEME_LENGTH, 0, -1):

            if i + pl > l:
                continue

            substr = s[i : i+pl ]

            #print u"i: %s, pl: %d, substr: '%s'" % (i, pl, substr)

            for pe in big_phoneme_table:
                p_f = pe[f_idx]
                p_t = pe[t_idx]

                if substr == p_f:
                    buf += p_t
                    i += pl
                    if i<l and s[i] != u'ː' and spaces:
                        buf += ' '
                    found = True
                    break

            if found:
                break

        if not found:

            p = s[i]
            
            msg = (u"_translate: %s: %s Phoneme not found: %s (%s)" % (graph, s, p, repr(p))).encode('UTF8')

            raise Exception (msg)

    return buf

def ipa_move_stress_to_vowels(ipa):

    stress    = False

    res = u''

    for c in ipa:

        if c == '\'':
            stress = True
            continue

        if stress and c in IPA_vowels:
            res += '\''
            stress = False

        res += c

    return res

def ipa2xsampa (graph, ipas, spaces=False, stress_to_vowels=True):
    ipas = _normalize (ipas,  IPA_normalization)
    if stress_to_vowels:
        ipas = ipa_move_stress_to_vowels(ipas)
    return _translate (graph, ipas, 0, 1, spaces)

def ipa2mary (graph, ipas):
    ipas = _normalize (ipas,  IPA_normalization)
    return _translate (graph, ipas, 0, 2)

def xsampa2ipa (graph, xs):
    xs = _normalize (xs,  XSAMPA_normalization)
    return _translate (graph, xs, 1, 0)

def mary2ipa (graph, ms):
    ms = _normalize (ms,  XSAMPA_normalization)
    return _translate (graph, ms, 2, 0)

ESPEAK_normalization = {
    ' '  : '',
    ';'  : '',
    '~'  : '',
    '0'  : 'O',
    ','  : '',
    # '3'  : '@',
    't#' : 't',
    'E2' : 'E',
    'I#' : 'I',
    'L'  : 'l',
    '_!' : '',
    '_::': '', 
    '_;_': '', 
    '_!' : '',
    '_|' : '',
    '_:' : '',
    '_'  : '',
    '!'  : '',
    '('  : '',
    ')'  : '',
    'Y'  : 'y',
    'pF' : 'pf',
    }

def espeak2ipa (graph, ms):
    for c in ESPEAK_normalization:
        ms = ms.replace(c, ESPEAK_normalization[c])
    return _translate (graph, ms, 3, 0)

def ipa2espeak (graph, ipas, spaces=False, stress_to_vowels=True):
    ipas = _normalize (ipas,  IPA_normalization)
    if stress_to_vowels:
        ipas = ipa_move_stress_to_vowels(ipas)
    return _translate (graph, ipas, 0, 3, spaces)

#
# X-ARPABET is my own creation - similar to arpabet plus
# some of my own creating for those phones defined in
#
# http://www.dev.voxforge.org/projects/de/wiki/PhoneSet
#
# uses only latin alpha chars
#

xs2xa_table = [

    #
    # stop
    #

    ('p'  , 'P'),
    ('b'  , 'B'),
    ('t'  , 'T'),
    ('d'  , 'D'),
    ('k'  , 'K'),
    ('g'  , 'G'),
    ('?'  , 'Q'),

    #
    # 2 consonants
    #

    ('pf'  , 'PF'),
    ('ts'  , 'TS'),
    ('tS'  , 'CH'),
    ('dZ'  , 'JH'),

    #
    # fricative
    #

    ('f'  , 'F'),
    ('v'  , 'V'),
    ('T'  , 'TH'),
    ('D'  , 'DH'),
    ('s'  , 'S'),
    ('z'  , 'Z'),
    ('S'  , 'SH'),
    ('Z'  , 'ZH'),
    ('C'  , 'CC'),
    ('j'  , 'Y'),
    ('x'  , 'X'),
    ('R'  , 'RR'),
    ('h'  , 'HH'),
    ('H'  , 'HHH'),

    #
    # nasal
    #

    ('m'  , 'M'),
    ('n'  , 'N'),
    ('N'  , 'NG'),
    ('J'  , 'NJ'),

    #
    # liquid
    #

    ('l'  , 'L'),
    ('r'  , 'R'),

    #
    # glide
    #

    ('w'  , 'W'),

    #
    # vowels, monophongs
    #

    # front
    ('i'  , 'IY'),
    ('i:' , 'IIH'),
    ('I'  , 'IH'),
    ('y'  , 'UE'),
    ('y:' , 'YYH'),
    ('Y'  , 'YY'),
    ('e'  , 'EE'),
    ('e:' , 'EEH'),
    ('2'  , 'OH'),
    ('2:' , 'OHH'),
    ('9'  , 'OE'),
    ('9~' , 'OEN'),
    ('E'  , 'EH'),
    ('E:' , 'EHH'),
    ('E~' , 'EN'),
    ('{'  , 'AE'),
    ('{:' , 'AEH'),
    ('a'  , 'AH'),
    ('a:' , 'AAH'),
    ('3'  , 'ER'),
    ('3:' , 'ERH'),

    # central
    ('V'  , 'VV'),
    ('@'  , 'AX'),
    ('6'  , 'EX'),
    #('3'  , 'AOR'),

    # back
    ('u'  , 'UH'),
    ('u:' , 'UUH'),
    ('U'  , 'UU'),
    ('o'  , 'AO'),
    ('o:' , 'OOH'),
    ('O'  , 'OO'),
    ('O:' , 'OOOH'),
    ('O~' , 'ON'),
    ('A'  , 'AA'),
    ('A:' , 'AAAH'),
    ('A~' , 'AN'),
    ('Q'  , 'QQ'),

    # diphtongs
    ('aI'  , 'AY'),
    ('OI'  , 'OI'),
    ('aU'  , 'AW'),
    ('OY'  , 'OY'),

    # misc (noise)
    ('#'   , 'NSPC'),

    ]

XARPABET_normalization = {
    '-': None,
    '\'': None,
    }

def xsampa2xarpabet (graph, s):
    s = _normalize (s,  XARPABET_normalization)

    buf = ""
    i = 0
    l = len(s)

    while i < l:

        found = False

        for pl in range(MAX_PHONEME_LENGTH, 0, -1):

            if i + pl > l:
                continue

            substr = s[i : i+pl ]

            #print u"i: %s, pl: %d, substr: '%s'" % (i, pl, substr)

            for pe in xs2xa_table:
                p_f = pe[0]
                p_t = pe[1]

                if substr == p_f:
                    if len(buf)>0:
                        buf += ' '
                    buf += p_t
                    i += pl
                    found = True
                    break

            if found:
                break

        if not found:

            p = s[i]

            msg = u"xsampa2xarpabet: graph:'%s' - s:'%s' Phoneme not found: '%s' (%d) '%s'" % (graph, s, p, ord(p), s[i:])

            raise Exception (msg.encode('UTF8'))

    return buf


