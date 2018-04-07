#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2014, 2015, 2016, 2017 Guenter Bartsch
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
# just a collection of random utility subprograms
#

import sys
import os
import subprocess
try:
    import ConfigParser as configparser
except ImportError:
    import configparser
try:
    from imp import reload
except ImportError:
    pass
import shutil
import errno
import curses
import curses.textpad
import traceback
import logging
import code
import signal

from setproctitle import setproctitle
from os.path import expanduser

def load_config(configfn = '.nlprc', defaults={}):

    home_path = expanduser("~")

    config = configparser.ConfigParser(defaults)
    config.read("%s/%s" % (home_path, configfn))

    return config

def _debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging.
    
    source: http://stackoverflow.com/questions/132058/showing-the-stack-trace-from-a-running-python-application
    """
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message  = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)

def init_app (proc_title):

    setproctitle (proc_title)

    if sys.version_info < (3, 0):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    # install signal handler so SIGUSR1 will enter pdb

    signal.signal(signal.SIGUSR1, _debug)  # Register handler


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

def run_command(command, capture_stderr=True):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT if capture_stderr else subprocess.PIPE)
    return iter(p.stdout.readline, b'')

tex_umlaut_map = { u'ä': '"a', u'ü': '"u', u'ö': '"o', u'Ä':'"A', u'Ü':'"U', u'Ö':'"O', u'ß':'"s' }

def tex_encode (u):

    s = ''

    for c in u:

        if c in tex_umlaut_map:
            s += tex_umlaut_map[c]
        else:
            s += str(c)

    return s

def tex_decode (s):

    u = ''

    pos = 0
    while (pos < len(s)):

        found = False

        for umlaut in tex_umlaut_map:
            v = tex_umlaut_map[umlaut]
            if s[pos:].startswith(v):
                u += umlaut
                pos += len(v)
                found = True
                break

        if not found:
            u += unicode(s[pos])
            pos += 1

    return u

def symlink(targetfn, linkfn):
    try:
        os.symlink(targetfn, linkfn)
    except OSError as e:
        if e.errno == errno.EEXIST:
            logging.debug('symlink %s -> %s already exists' % (targetfn, linkfn))

def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def copy_file (src, dst):
    logging.debug("copying %s to %s" % (src, dst))
    shutil.copy(src, dst)


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

def limit_str(s, limit):

    l = len(s)

    if l<=limit:
        return s

    l = limit-3

    return s[:l] + '...'


#
# curses utils
#

def edit_popup (stdscr, title, s):

    my, mx = stdscr.getmaxyx()

    ww = mx * 9 / 10
    wh = 3

    wox = mx / 2 - ww/2
    woy = my / 2 - wh/2

    win = curses.newwin(wh, ww, woy, wox)
    win.box()
    win.addstr(0, 3, title)

    win.refresh()

    swin = win.derwin (1, ww-4, 1, 2)

    tb = curses.textpad.Textbox(swin, insert_mode=True)

    swin.insstr (0, 0, tex_encode(s))

    swin.refresh()

    s = tex_decode(tb.edit())

    return s.rstrip()

def message_popup (stdscr, title, msg):

    my, mx = stdscr.getmaxyx()

    ww = len(title)

    lines = msg.split('\n')
    for line in lines:
        if len(line)>ww:
            ww = len(line)
    ww += 6
    wh = len(lines) + 2

    wox = mx / 2 - ww/2
    woy = my / 2 - wh/2

    win = curses.newwin(wh, ww, woy, wox)
    win.box()
    win.addstr(0, 3, title.encode('utf8'))

    win.refresh()

    swin = win.derwin (wh-2, ww-4, 1, 1)

    for i, line in enumerate(lines):
        swin.insstr (i, 0, line.encode('utf8'))

    swin.refresh()

    return swin

def render_template(template_file, dst_file, **kwargs):
    """Copy template and substitute template strings

    File `template_file` is copied to `dst_file`. Then, each template variable
    is replaced by a value. Template variables are of the form

        {{val}}

    Example:

    Contents of template_file:

        VAR1={{val1}}
        VAR2={{val2}}
        VAR3={{val3}}

    render_template(template_file, output_file, val1="hello", val2="world")

    Contents of output_file:

        VAR1=hello
        VAR2=world
        VAR3={{val3}}

    :param template_file: Path to the template file.
    :param dst_file: Path to the destination file.
    :param kwargs: Keys correspond to template variables.
    :return:
    """
    with open(template_file) as f:
        template_text = f.read()

    dst_text = template_text

    for key, value in kwargs.iteritems():
        dst_text = dst_text .replace("{{" + key + "}}", value)

    with open(dst_file, "wt") as f:
        f.write(dst_text)
