#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2013, 2014, 2016, 2017 Guenter Bartsch
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
#
# random tokenization / nlp pre-processing related stuff
#

import sys
import re
import unittest
import logging

def detect_latin1 (fn):

    f = open(fn)

    l1ucnt = 0

    for line in f:

        for c in line:

            o = ord(c)
            if o == 0xc4 or o == 0xd6 or o == 0xdc or o == 0xe4 or o==0xf6 or o==0xfc or o==0xdf:
                l1ucnt += 1


    f.close()

    return l1ucnt > 1

def compress_ws (s):

        vc = True

        res = ''

        for c in s:

                if c == ' ':
                        vc = False
                else:
                        if vc:
                                res = res + c
                        else:
                                res = res + ' ' + c
                        vc = True

        return res 

def isgalnum (s):

    for c in s:
        if c.isalnum():
            continue

        if c == u'%' or c ==u'§':
            continue

        return False

    return True


# word replacement table
wrt = { u'0'             : u'null',
        u'10%'           : u'zehn prozent',
        u'100%'          : u'hundert prozent',
        u'1700'          : u'siebzehnhundert',
        u'1825'          : u'achtzehnhundertfünfundzwanzig',
        u'1949'          : u'neunzehnhundertneunundvierzig',
        u'1960ER'        : u'neunzehnhundertsechziger',
        u'1970ER'        : u'neunzehnhundertsiebziger',
        u'1970ERJAHREN'  : u'neunzehnhundertsiebziger jahren',
        u'1977'          : u'neunzehnhundertsiebenundsiebzig',
        u'1979'          : u'neunzehnhundertneunundsiebzig',
        u'1980ER'        : u'neunzehnhundertachtziger',
        u'1983'          : u'neunzehnhundertdreiundachtzig',
        u'1984'          : u'neunzehnhundertvierundachtzig',
        u'1989'          : u'neunzehnhundertneunundachtzig',
        u'1990'          : u'neunzehnhundertneunzig',
        u'1990ER'        : u'neunzehnhundertneunziger',
        u'1991'          : u'neunzehnhunderteinundneunzig',
        u'1993'          : u'neunzehnhundertdreiundneunzig',
        u'1998'          : u'neunzehnhundertachtundneunzig',
        u'2%'            : u'zwei prozent', 
        u'40%'           : u'vierzig prozent', 
        u'80%'           : u'achtzig prozent',
        u'800'           : u'achthundert',
        u'80ER'          : u'achtziger',
        u'daß'           : u'dass',
        u'haß'           : u'hass',
        u'gross'         : u'groß',
        u'grosse'        : u'große',
        u'grossen'       : u'großen',
        u'grosses'       : u'großes',
        u'faßte'         : u'fasste',
        u'gefaßt'        : u'gefasst',
        u'eingefaßte'    : u'eingefasste',
        u'bißchen'       : u'bisschen',
        u'blaß'          : u'blass',
        u'blaßblauen'    : u'blassblauen',
        u'bläßlich'      : u'blässlich',
        u'entschluß'     : u'entschluss',
        u'eßstube'       : u'essstube',
        u'eßtisch'       : u'esstisch',
        u'eßzimmer'      : u'esszimmer',
        u'gepreßt'       : u'gepresst',
        u'gewiß'         : u'gewiss',
        u'küßte'         : u'küsste',
        u'küßten'        : u'küssten',
        u'laß'           : u'lass',
        u'läßt'          : u'lässt',
        u'mißvergnügt'   : u'missvergnügt',
        u'mißverständnis': u'missverständnis',
        u'müßte'         : u'müsste',
        u'paß'           : u'pass',
        u'paßt'          : u'passt',
        u'preßte'        : u'presste',
        u'photo'         : u'foto',
        u'riß'           : u'riss',
        u'schloß'        : u'schloss',
        u'schluß'        : u'schluss',
        u'telephon'      : u'telefon',
        u'totenblaß'     : u'totenblass',
        u'vermißte'      : u'vermisste',
        u'vermißt'       : u'vermisst',
        u'phantasie'     : u'fantasie',
        u'phantasieren'  : u'fantasieren',
        u'phantastereien': u'fantastereien',
        u'phantastisch'  : u'fantastisch',
        u'mikrophon'     : u'mikrofon',
        u'mikrophone'    : u'mikrofone',
        u'wüßte'         : u'wüsste',
        u'wußte'         : u'wusste',
        u'wußten'        : u'wussten',
        u'muß'           : u'muss',
        u'mußt'          : u'musst',
        u'mußte'         : u'musste',
        u'bewußt'        : u'bewusst',
        u'unbewußt'      : u'unbewusst',
        u'gewußt'        : u'gewusst',
        u'bewußte'       : u'bewusste',
        u'bewußten'      : u'bewussten',
        u'zielbewußte'   : u'zielbewusste',
        u'siegesgewiß'   : u'siegesgewiss',
        u'zerriß'        : u'zerriss',
        u'walther'       : u'walter',
        u'eur'           : u'euro',
        u'sodass'        : u'so dass',
        u'elephant'      : u'elefant',
        u'elephanten'    : u'elefanten',
        u'abschluß'      : u'abschluss',
        u'philipp'       : u'philip',
        u'millenium'     : u'millennium',
        u'stop'          : u'stopp',
        u'§'             : u'paragraph'}


symb_abbrev_norm = [
        (u'Abk.'    , u'abkürzung '),
        (u'Abk '    , u'abkürzung '),
        (u'Prof.'   , u'professor '),
        (u'Dipl.'   , u'diplom '),
        (u'Ing.'    , u'ingenieur '),
        (u'Inf.'    , u'informatiker '),
        (u'Inform.' , u'informatiker '),
        (u'Tel.'    , u'telefon '),
        (u'bzw.'    , u'beziehungsweise '),
        (u'bzw '    , u'beziehungsweise '),
        (u'bspw.'   , u'beispielsweise '),
        (u'bspw '   , u'beispielsweise '),
        (u'bzgl.'   , u'bezüglich '),
        (u'ca.'     , u'circa '),
        (u'ca '     , u'circa '),
        (u'd.h.'    , u'das heißt '),
        (u'd. h.'   , u'das heißt '),
        (u'Dr. '    , u'doktor '),
        (u'evtl.'   , u'eventuell '),
        (u'evtl '   , u'eventuell '),
        (u'geb.'    , u'geborene '),
        (u'ggf.'    , u'gegebenenfalls '),
        (u'ggf '    , u'gegebenenfalls '),
        (u'kath.'   , u'katholische '),
        (u'Hrsg.'   , u'herausgeber '),
        (u'Mr.'     , u'mister '),
        (u'Mrd.'    , u'milliarden '),
        (u'Mrs.'    , u'misses '),
        (u'Nr.'     , u'nummer '),
        (u'Nrn.'    , u'nummern '),
        (u's.a.'    , u'siehe auch '),
        (u's. a.'   , u'siehe auch '),
        (u's.o.'    , u'siehe oben '),
        (u's. o.'   , u'siehe oben '),
        (u's.u.'    , u'siehe unten '),
        (u's. u.'   , u'siehe unten '),
        (u'jr.'     , u'junior '),
        (u'Str.'    , u'strasse '),
        (u'u.a.'    , u'unter anderem '),
        (u'u. a.'   , u'unter anderem '),
        (u'u.U.'    , u'unter umständen '),
        (u'u. U.'   , u'unter umständen '),
        (u'usw.'    , u'und so weiter '),
        (u'u.s.w.'  , u'und so weiter '),
        (u'u. s. w.', u'und so weiter '),
        (u'v.a.'    , u'vor allem '),
        (u'vgl.'    , u'vergleiche '),
        (u'vgl '    , u'vergleiche '),
        (u'Wdh.'    , u'wiederholung '),
        (u'Ziff.'   , u'ziffer '),
        (u'z.B.'    , u'zum beispiel '),
        (u'z. B.'   , u'zum beispiel '),
        (u'z.T.'    , u'zum teil '),
        (u'z. T.'   , u'zum teil '),
        (u'z.Zt.'   , u'zur zeit '),
        (u'z. Zt.'  , u'zur zeit '),
        (u'GHz'     , u'gigahertz '),
        (u'\ufeff'  , u' '),
        (u'\u2019'  , u' '),
        (u'\xa0'    , u' '),
        (u'\u203a'  , u' '),
        (u'\u2039'  , u' '),
        (u'_'       , u' '),
        (u'&'       , u'und'),
        (u'\xa020'  , u' '),
        (u'„'       , u' '),
        (u'“'       , u' '),
        (u'$'       , u'dollar ')
    ]


# based on code from: http://www.python-forum.de/viewtopic.php?f=11&t=22543

w1 = u"null ein zwei drei vier fünf sechs sieben acht neun zehn elf zwölf dreizehn vierzehn fünfzehn sechzehn siebzehn achtzehn neunzehn".split()
w2 = u"zwanzig dreißig vierzig fünfzig sechzig siebzig achtzig neunzig".split()
 
def zahl_in_worten(n, s=True, z=False, e=False):
    if n < 0: raise ValueError
    if n == 0 and z: return ""
    if n == 1 and s: return "eins"
    if n == 1 and e: return "eine"
    if n < 20: return w1[n]
    if n < 100:
        w = w2[(n - 20) // 10]
        if n % 10:
            w = w1[n % 10] + "und" + w
        return w
    if n < 1000:
        if n // 100 == 1:
            if z: return "einhundert" + zahl_in_worten(n % 100, z=True)
            return "hundert" + zahl_in_worten(n % 100, z=True)
        return w1[n // 100] + "hundert" + zahl_in_worten(n % 100, z=True)
    if n < 2000:
        if n < 1100:
            return  "tausend" + zahl_in_worten(n % 1000, z=True)
        return w1[n // 100] + "hundert" + zahl_in_worten(n % 100, z=True)
    if n < 1000000:
        return zahl_in_worten(n // 1000, s=False) + "tausend" + zahl_in_worten(n % 1000, z=True)
    if n < 1000000000:
        m = n // 1000000
        suff = 'millionen' if m>1 else 'million'
        return zahl_in_worten(m, s=False, e=True) + suff + zahl_in_worten(n % 1000000, z=True)
    # raise ValueError
    logging.warn('zahl_in_worten: cannot handle %s' % n)
    return str(n)

# #
# # init number replacement dict
# #
# 
# for i in range(10000):
#     u = unicode(i)
#     if not u in wrt:
#         wrt[u] = zahl_in_worten(i)
#     wrt[u'0'+u] = zahl_in_worten(i)
#     wrt[u'00'+u] = zahl_in_worten(i)
#     wrt[u'000'+u] = zahl_in_worten(i)



def spellout_number (m):

    numstr = m.group(0)

    # print "spellout number:", numstr

    if numstr[0].isspace():
        numstr = numstr[1:]
        res = ' '
    else:
        res = ''

    if numstr[0] == '-':
        res += 'minus '
        numstr = numstr[1:].strip()

    if not '.' in numstr:
        numstr = numstr.replace(',','.')

    parts = numstr.split ('.')

    # print repr(parts)

    res += zahl_in_worten(int(parts[0]))

    if len(parts)>1:

        # spell out fractional part in digits

        res += ' komma'

        for c in parts[1]:
            res += ' ' + zahl_in_worten(int(c))
    
    return res

NUMBER_PATTERN_START = re.compile(r"^[-]?\d+[,.]?\d*")
NUMBER_PATTERN_SPACE = re.compile(r"\s[-]?\d+[,.]?\d*")

PUNCTUATION = [
    u',', u'.', u';', u':', 
    u'?', u'!', 
    u'+', u'-', u'*', u'#', u'=', u'|'
    u'/', u'\\',  
    u'[', u']', u'(', u')', u'»', u'«', u'<', u'>', 
    u'\'', u'"',
]

def tokenize (s, lang='de', keep_punctuation=False):

    global wrt

    if lang != 'de':
        # FIXME
        raise Exception ("FIXME: implement tokenizer support for language: " + lang)

    for san in symb_abbrev_norm:
        srch = san[0]
        repl = san[1]

        s = s.replace (srch, repl)

    # deal with numbers
    s = NUMBER_PATTERN_START.sub(spellout_number, s)
    s = NUMBER_PATTERN_SPACE.sub(spellout_number, s)

    # deal with punctuation
    if keep_punctuation:
        for p in PUNCTUATION:
            s = s.replace (p, u' ' + p + u' ')
    else:
        for p in PUNCTUATION:
            s = s.replace(p,' ')

    res = []

    words = re.split ('\s+', s)

    # print repr(words)

    for word in words:

        w = word.rstrip().replace(u'–',u'').lower()
        if len(w) > 0:

            if w in wrt:
                w = wrt[w]
        
                words2 = re.split('\s+', w)
                for w2 in words2:
                    res.append(w2)

            else:
                res.append (w)

    return res

def edit_distance (s, t):
    # https://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm

    # for all i and j, d[i,j] will hold the Levenshtein distance between
    # the first i words of s and the first j words of t;
    # note that d has (m+1)x(n+1) values
    
    m = len(s)
    n = len(t)

    d = [[0 for i in range(n+1)] for j in range(m+1)]

    for i in range (m+1):
        d[i][0] = i                        # the distance of any first seq to an empty second seq
    for j in range (n+1):
        d[0][j] = j                         # the distance of any second seq to an empty first seq
  
    for j in range (1, n+1):
        for i in range (1, m+1):

            if s[i-1] == t[j-1]:
                d[i][j] = d[i-1][j-1]       # no operation required
            else:
                d[i][j] = min ([
                            d[i-1][j] + 1,       # a deletion
                            d[i][j-1] + 1,       # an insertion
                            d[i-1][j-1] + 1      # a substitution
                         ])
  
    return d[m][n]

def kill_umlauts(s):
    return s.replace(u'ß',u'ss') \
            .replace(u'Ä',u'Ae') \
            .replace(u'Ö',u'Oe') \
            .replace(u'Ü',u'Ue') \
            .replace(u'ä',u'ae') \
            .replace(u'ö',u'oe') \
            .replace(u'ü',u'ue') 

