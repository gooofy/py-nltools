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
# A simple MARY TTS client in Python
#
# based on Code from Hugh Sasse (maryclient-http.py)
#

import httplib, urllib

import sys
import re 
import traceback
import logging

import xml.etree.ElementTree as ET

from misc import compress_ws

class maryclient:

    def __init__(self, host="127.0.0.1", port=59125):

        self.host          = host
        self.port          = port
        self.input_type    = "TEXT"
        self.output_type   = "AUDIO"
        self.audio         = "WAVE_FILE"
        self.locale        = "en_US"
        self.voice         = "cmu-bdl-hsmm"

    def set_host(self, a_host):
        """Set the host for the TTS server."""
        self.host = a_host

    def get_host(self):
        """Get the host for the TTS server."""
        self.host

    def set_port(self, a_port):
        """Set the port for the TTS server."""
        self.port = a_port

    def get_port(self):
        """Get the port for the TTS server."""
        self.port

    def set_input_type(self, type):
        """Set the type of input being 
           supplied to the TTS server
           (such as 'TEXT')."""
        self.input_type = type

    def get_input_type(self):
        """Get the type of input being 
           supplied to the TTS server
           (such as 'TEXT')."""
        self.input_type

    def set_output_type(self, type):
        """Set the type of input being 
           supplied to the TTS server
           (such as 'AUDIO')."""
        self.output_type = type

    def get_output_type(self):
        """Get the type of input being 
           supplied to the TTS server
           (such as "AUDIO")."""
        self.output_type

    def set_locale(self, a_locale):
        """Set the locale
           (such as "en_US")."""
        self.locale = a_locale

    def get_locale(self):
        """Get the locale
           (such as "en_US")."""
        self.locale

    def set_audio(self, audio_type):
        """Set the audio type for playback
           (such as "WAVE_FILE")."""
        self.audio = audio_type

    def get_audio(self):
        """Get the audio type for playback
           (such as "WAVE_FILE")."""
        self.audio

    def set_voice(self, a_voice):
        """Set the voice to speak with
           (such as "dfki-prudence-hsmm")."""
        self.voice = a_voice

    def get_voice(self):
        """Get the voice to speak with
           (such as "dfki-prudence-hsmm")."""
        self.voice

    def generate(self, message):
        """Given a message in message,
           return a response in the appropriate
           format."""
        raw_params = {"INPUT_TEXT"  : message.encode('UTF8'),
                      "INPUT_TYPE"  : self.input_type,
                      "OUTPUT_TYPE" : self.output_type,
                      "LOCALE"      : self.locale,
                      "AUDIO"       : self.audio,
                      "VOICE"       : self.voice,
                      }
        params = urllib.urlencode(raw_params)
        headers = {}

        logging.debug('maryclient: generate, raw_params=%s' % repr(raw_params))

        # Open connection to self.host, self.port.
        conn = httplib.HTTPConnection(self.host, self.port)

        #conn.set_debuglevel(5)
        
        conn.request("POST", "/process", params, headers)
        response = conn.getresponse()
        if response.status != 200:
            logging.error(response.getheaders())
            raise Exception ("{0}: {1}".format(response.status, response.reason))
        return response.read()

#
# higher-level functions
#

def mary_init ():

    global mclient

    mclient = maryclient()
    mclient.set_locale ("en")
    mclient.set_voice  ("dfki-spike")
   
def mary_synth_phonemes (phonemes):

    global mclient

    wav = None

    try:
        s = '<maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="%s"><p><s><t g2p_method="lexicon" ph="%s" pos="NE"></t></s></p></maryxml>' % (mclient.locale[:2], phonemes)

        #print s

        mclient.set_input_type("PHONEMES")
        mclient.set_output_type("AUDIO")
        wav = mclient.generate(s)

    except:
        logging.error("*** ERROR: unexpected error: %s " % sys.exc_info()[0])
        traceback.print_exc()

    return wav

def _mary_gather_ph (parent):

	res = ""

	for child in parent:
		r = _mary_gather_ph (child)
		if len(r) > 0:
			res += r + " "

	if 'ph' in parent.attrib:
		res += parent.attrib['ph'] + " "

	return compress_ws(res)


def mary_gen_phonemes (word):

    global mclient

    mclient.set_input_type ("TEXT")
    mclient.set_output_type ("PHONEMES")

    xmls = mclient.generate(word.lower())

    #print "Got: For %s %s" % (graph.encode('utf-8'), xmls)

    root = ET.fromstring(xmls)

    #print "ROOT: %s" % repr(root)

    mph = _mary_gather_ph (root)

    return re.sub(u"^ \?", "", re.sub(u"^ ' \?", "'", mph))

def mary_synth(txt):

    ph = mary_gen_phonemes(txt)
    wav = mary_synth_phonemes(ph)

    return wav

def mary_set_voice (voice):

    global mclient

    mclient.set_voice (voice) 

def mary_set_locale (l):

    global mclient

    mclient.set_locale (l) 


