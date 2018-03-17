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
# random tokenization / nlp pre-processing related stuff
#

import sys
import re
import unittest
import logging
from num2words import num2words

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

#####################################################################
#
# tokenizer commons
#
#####################################################################

PERCENT_PATTERN_START = re.compile(r"^[-]?\d+[,.]?\d*\s*[%]")
PERCENT_PATTERN_SPACE = re.compile(r"\s[-]?\d+[,.]?\d*\s*[%]")

NUMBER_PATTERN_START = re.compile(r"^[-]?\d+[,.]?\d*")
NUMBER_PATTERN_SPACE = re.compile(r"\s[-]?\d+[,.]?\d*")

PUNCTUATION = [
    u',', u'.', u';',  
    u'?', u'!', 
    u'+', u'-', u'*', u'#', u'=', u'|'
    u'/', u'\\',  
    u'[', u']', u'(', u')', u'»', u'«', u'<', u'>', 
    u'\'', u'"',
]

MACRO_PUNCTUATION = [
    u'@', u':', u'_' 
]

#####################################################################
#
# english tokenizer
#
#####################################################################

# word replacement table
wrt_en = { u'0'          : u'zero',
           u'1'          : u'one',
           u'colour'     : u'color',
           u'okay'       : u'ok',
         }

symb_abbrev_norm_en = [
                       (u'\ufeff'  , u' '),
                       (u'\u2019'  , u"'"),
                       (u'\xa0'    , u' '),
                       (u'\u203a'  , u' '),
                       (u'\u2039'  , u' '),
                       (u'&'       , u'and'),
                       (u'\xa020'  , u' '),
                       (u'„'       , u' '),
                       (u'“'       , u' '),
                       (u'$'       , u'dollar ')
                      ]

def spellout_number_en (m):

    numstr = m.group(0)

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

    if numstr.endswith('%'):
        numstr = numstr[:len(numstr)-1]
        percent = True
    else:
        percent = False

    parts = numstr.split ('.')

    # print repr(parts)

    res += num2words(int(parts[0]))

    if len(parts)>1 and len(parts[1])>0:

        # spell out fractional part in digits

        res += ' point ' + num2words(int(parts[1]))

    if percent:
        res += ' percent'

    return res

APOSTROPHE_S_PATTERN1 = re.compile(r"\w\w+[']s\s")
APOSTROPHE_S_PATTERN2 = re.compile(r"\w\w+[']s$")
APOSTROPHE_S_PATTERN3 = re.compile(r"\w\w+[']s[,.;:]")

def protect_apostrophe_s (m):

    s = m.group(0)

    return s.replace(u"'s", u"✓s")

APOSTROPHE_NT_PATTERN1 = re.compile(r"\wn[']t\s")
APOSTROPHE_NT_PATTERN2 = re.compile(r"\wn[']t$")
APOSTROPHE_NT_PATTERN3 = re.compile(r"\wn[']t[,.;:]")

def protect_apostrophe_nt (m):

    s = m.group(0)

    return s.replace(u"n't", u"n✓t")

APOSTROPHE_D_PATTERN1 = re.compile(r"\w[']d\s")
APOSTROPHE_D_PATTERN2 = re.compile(r"\w[']d$")
APOSTROPHE_D_PATTERN3 = re.compile(r"\w[']d[,.;:]")

def protect_apostrophe_d (m):

    s = m.group(0)

    return s.replace(u"'d", u"✓d")

APOSTROPHE_RE_PATTERN1 = re.compile(r"\w[']re\s")
APOSTROPHE_RE_PATTERN2 = re.compile(r"\w[']re$")
APOSTROPHE_RE_PATTERN3 = re.compile(r"\w[']re[,.;:]")

def protect_apostrophe_re (m):

    s = m.group(0)

    return s.replace(u"'re", u"✓re")

APOSTROPHE_LL_PATTERN1 = re.compile(r"\w[']ll\s")
APOSTROPHE_LL_PATTERN2 = re.compile(r"\w[']ll$")
APOSTROPHE_LL_PATTERN3 = re.compile(r"\w[']ll[,.;:]")

def protect_apostrophe_ll (m):

    s = m.group(0)

    return s.replace(u"'ll", u"✓ll")

def tokenize_en (s, keep_punctuation=False, keep_macros=False):

    global wrt_en, symb_abbrev_norm_en

    for san in symb_abbrev_norm_en:
        srch = san[0]
        repl = san[1]

        s = s.replace (srch, repl)

    s = s.lower()

    # deal with numbers
    s = PERCENT_PATTERN_START.sub(spellout_number_en, s)
    s = PERCENT_PATTERN_SPACE.sub(spellout_number_en, s)

    s = NUMBER_PATTERN_START.sub(spellout_number_en, s)
    s = NUMBER_PATTERN_SPACE.sub(spellout_number_en, s)

    # deal with apostrophe-s
    s = APOSTROPHE_S_PATTERN1.sub(protect_apostrophe_s, s)
    s = APOSTROPHE_S_PATTERN2.sub(protect_apostrophe_s, s)
    s = APOSTROPHE_S_PATTERN3.sub(protect_apostrophe_s, s)

    # deal with apostrophe-nt
    s = APOSTROPHE_NT_PATTERN1.sub(protect_apostrophe_nt, s)
    s = APOSTROPHE_NT_PATTERN2.sub(protect_apostrophe_nt, s)
    s = APOSTROPHE_NT_PATTERN3.sub(protect_apostrophe_nt, s)

    # deal with apostrophe-d (I'd we'd)
    s = APOSTROPHE_D_PATTERN1.sub(protect_apostrophe_d, s)
    s = APOSTROPHE_D_PATTERN2.sub(protect_apostrophe_d, s)
    s = APOSTROPHE_D_PATTERN3.sub(protect_apostrophe_d, s)

    # deal with apostrophe-re (we're they're)
    s = APOSTROPHE_RE_PATTERN1.sub(protect_apostrophe_re, s)
    s = APOSTROPHE_RE_PATTERN2.sub(protect_apostrophe_re, s)
    s = APOSTROPHE_RE_PATTERN3.sub(protect_apostrophe_re, s)

    # deal with apostrophe-ll (we'll they'll)
    s = APOSTROPHE_LL_PATTERN1.sub(protect_apostrophe_ll, s)
    s = APOSTROPHE_LL_PATTERN2.sub(protect_apostrophe_ll, s)
    s = APOSTROPHE_LL_PATTERN3.sub(protect_apostrophe_ll, s)

    # I'm, I've
    s = s.replace (u"i'm", u'i✓m')
    s = s.replace (u"i've", u'i✓ve')

    # deal with punctuation
    if keep_punctuation:
        for p in PUNCTUATION:
            s = s.replace (p, u' ' + p + u' ')
    else:
        for p in PUNCTUATION:
            s = s.replace(p,' ')
        if not keep_macros:
            for p in MACRO_PUNCTUATION:
                s = s.replace(p,' ')

    # re-insert apostrophes
    s = s.replace (u'✓', u"'")

    res = []

    words = re.split ('\s+', s)

    # print repr(words)

    for word in words:

        w = word.rstrip().replace(u'–',u'')
        if len(w) > 0:

            if w in wrt_en:
                w = wrt_en[w]
        
                words2 = re.split('\s+', w)
                for w2 in words2:
                    res.append(w2)

            else:
                res.append (w)

    return res

#####################################################################
#
# german tokenizer
#
#####################################################################

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
        u'heisst'        : u'heißt',
        u'heissen'       : u'heißen',
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
        u'ok'            : u'okay',
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
        u'colour'        : u'color',

        # umlauts...

        u'aendern'             : u'ändern',
        u'aerztin'             : u'ärztin',
        u'aufraeumt'           : u'aufräumt',
        u'aufzaehlen'          : u'aufzählen',
        u'beschaeftigt'        : u'beschäftigt',
        u'daemlich'            : u'dämlich',
        u'daemliche'           : u'dämliche',
        u'erklaeren'           : u'erklären',
        u'erklaerung'          : u'erklärung',
        u'erzaehl'             : u'erzähl',
        u'erzaehle'            : u'erzähle',
        u'erzaehlen'           : u'erzählen',
        u'erzaehlt'            : u'erzählt',
        u'faellt'              : u'fällt',
        u'faengst'             : u'fängst',
        u'gefaellt'            : u'gefällt',
        u'gespraech'           : u'gespräch',
        u'gespraechig'         : u'gesprächig',
        u'haeltst'             : u'hältst',
        u'haende'              : u'hände',
        u'haesslich'           : u'hässlich',
        u'haesslicher'         : u'hässlicher',
        u'haette'              : u'hätte',
        u'haettest'            : u'hättest',
        u'laecherlich'         : u'lächerlich',
        u'laender'             : u'länder',
        u'laeufst'             : u'läufst',
        u'laeuft'              : u'läuft',
        u'lernfaehig'          : u'lernfähig',
        u'liebesfaehig'        : u'liebesfähig',
        u'maedchen'            : u'mädchen',
        u'maenner'             : u'männer',
        u'maennlich'           : u'männlich',
        u'maerchen'            : u'märchen',
        u'naechste'            : u'nächste',
        u'naechsten'           : u'nächsten',
        u'naechstes'           : u'nächstes',
        u'relativitaetstheorie': u'relativitätstheorie',
        u'saetze'              : u'sätze',
        u'schaetze'            : u'schätze',
        u'schlaefst'           : u'schläfst',
        u'spaet'               : u'spät',
        u'taeglich'            : u'täglich',
        u'traegst'             : u'trägst',
        u'traeume'             : u'träume',
        u'traeumen'            : u'träumen',
        u'ungefaehr'           : u'ungefähr',
        u'waehl'               : u'wähl',
        u'waehle'              : u'wähle',
        u'weitererzaehlen'     : u'weitererzählen',

        u'bloed'             : u'blöd',
        u'bloede'            : u'blöde',
        u'bloedes'           : u'blödes',
        u'bloedsinn'         : u'blödsinn',
        u'boese'             : u'böse',
        u'doener'            : u'döner',
        u'franzoesisch'      : u'französisch',
        u'froehlich'         : u'fröhlich',
        u'gehoert'           : u'gehört',
        u'hoechste'          : u'höchste',
        u'hoeflich'          : u'höflich',
        u'hoeflicher'        : u'höflicher',
        u'hoelle'            : u'hölle',
        u'hoer'              : u'hör',
        u'hoere'             : u'höre',
        u'hoeren'            : u'hören',
        u'hoerst'            : u'hörst',
        u'koennen'           : u'können',
        u'koennte'           : u'könnte',
        u'koenntest'         : u'könntest',
        u'koerperlich'       : u'körperlich',
        u'koerper'           : u'körper',
        u'loewe'             : u'löwe',
        u'moechte'           : u'möchte',
        u'moechtest'         : u'möchtest',
        u'moeglich'          : u'möglich',
        u'moeglichkeit'      : u'möglichkeit',
        u'monroe'            : u'monrö',
        u'noetig'            : u'nötig',
        u'oefter'            : u'öfter',
        u'oefters'           : u'öfters',
        u'schluesselwoerter' : u'schluesselwörter',
        u'schoenen'          : u'schönen',
        u'schoene'           : u'schöne',
        u'schoen'            : u'schön',
        u'schoepfer'         : u'schöpfer',
        u'schroeder'         : u'schröder',
        u'stoert'            : u'stört',
        u'unmoeglich'        : u'unmöglich',
        u'verhoer'           : u'verhör',
        u'voellig'           : u'völlig',
        u'woerter'           : u'wörter',
        u'zuhoeren'          : u'zuhören',

        u'betruege'         : u'betrüge',
        u'buecher'          : u'bücher',
        u'bueck'            : u'bück',
        u'darueber'         : u'darüber',
        u'duesseldorf'      : u'düsseldorf',
        u'fuehle'           : u'fühle',
        u'fuehlen'          : u'fühlen',
        u'fuehlst'          : u'fühlst',
        u'fuehlt'           : u'fühlt',
        u'fuenf'            : u'fünf',
        u'fuer'             : u'für',
        u'fuessen'          : u'füssen',
        u'gefuehl'          : u'gefühl',
        u'gefuehle'         : u'gefühle',
        u'gegenueber'       : u'gegenüber',
        u'geruecht'         : u'gerücht',
        u'gluecklich'       : u'glücklich',
        u'gruen'            : u'grün',
        u'gruenen'          : u'grünen',
        u'gruener'          : u'grüner',
        u'huebsch'          : u'hübsch',
        u'kluegste'         : u'klügste',
        u'kuenstlich'       : u'künstlich',
        u'kuenstliche'      : u'künstliche',
        u'luegen'           : u'lügen',
        u'luegner'          : u'lügner',
        u'luegst'           : u'lügst',
        u'muede'            : u'müde',
        u'muelheim'         : u'mülheim',
        u'muelltonne'       : u'mülltonne',
        u'muesstest'        : u'müsstest',
        u'natuerlich'       : u'natürlich',
        u'saarbruecken'     : u'saarbrücken',
        u'schluesselwoerter': u'schlüsselwörter',
        u'schuechtern'      : u'schüchtern',
        u'schueler'         : u'schüler',
        u'schuetze'         : u'schütze',
        u'sebstbezueglich'  : u'sebstbezüglich',
        u'spruenge'         : u'sprünge',
        u'suess'            : u'süß',
        u'tschuess'         : u'tschüss',
        u'tuerkisch'        : u'türkisch',
        u'ueber'            : u'über',
        u'ueberall'         : u'überall',
        u'ueberhaupt'       : u'überhaupt',
        u'uebersetzer'      : u'übersetzer',
        u'uebersetzt'       : u'übersetzt',
        u'verrueckt'        : u'verrückt',
        u'wofuer'           : u'wofür',
        u'worueber'         : u'worüber',
        u'wuerde'           : u'würde',
        u'wuerdest'         : u'würdest',
        u'wuesste'          : u'wüsste',
        u'wuetend'          : u'wütend',
        u'zuerich'          : u'zürich',
        u'zurueck'          : u'zurück',

        u'spass'            : u'spaß',
        u'weisst'           : u'weißt',
        u'schliesse'        : u'schließe',
        u'schliessen'       : u'schließen',

        u'swr3'             : u'swr drei',
        u'zx81'             : u'zx einundachtzig',

        u'§'                : u'paragraph'}


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
        (u'o.k.'    , u'okay '),
        (u'o. k.'   , u'okay '),
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

    if len(parts)>1 and len(parts[1])>0:

        # spell out fractional part in digits

        res += ' komma'

        for c in parts[1]:
            res += ' ' + zahl_in_worten(int(c))
    
    return res

def tokenize (s, lang='de', keep_punctuation=False, keep_macros=False):

    global wrt

    if lang == 'en':
        return tokenize_en(s, keep_punctuation, keep_macros)

    if lang != 'de':
        # FIXME
        raise Exception ("FIXME: implement tokenizer support for language: " + lang)

    # print '#1', s

    for san in symb_abbrev_norm:
        srch = san[0]
        repl = san[1]

        s = s.replace (srch, repl)

    # print '#2', s

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
        if not keep_macros:
            for p in MACRO_PUNCTUATION:
                s = s.replace(p,' ')

    # print '#3', s

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

def kill_umlauts(s):
    return s.replace(u'ß',u'ss') \
            .replace(u'Ä',u'Ae') \
            .replace(u'Ö',u'Oe') \
            .replace(u'Ü',u'Ue') \
            .replace(u'ä',u'ae') \
            .replace(u'ö',u'oe') \
            .replace(u'ü',u'ue') 

