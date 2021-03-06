# Copyright (c) 2009 Lemur Consulting Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
r"""Utility functions for Flax searchserver client.

"""
__docformat__ = "restructuredtext en"

safe_idchar_map = {}
for i in range(256):
    c = chr(i)
    if c in ('abcdefghijklmnopqrstuvwxyz' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		    '0123456789_.'):
        safe_idchar_map[c] = c
    else:
        safe_idchar_map[c] = '%%%02X' % i

# Import a json handling library as "json".
try:
    # json is a built-in module from python 2.6 onwards
    import json
    json.dumps
except (ImportError, AttributeError):
    # Depend on simplejson for python 2.5 or earlier.
    import simplejson as json

import urllib
def quote(unistring):
    """Encode a unicode string as utf8 and quote it to be safe to go in a uri.

    """
    if isinstance(unistring, unicode):
        unistring = unistring.encode('utf-8')
    return ''.join(map(safe_idchar_map.__getitem__, unistring))
