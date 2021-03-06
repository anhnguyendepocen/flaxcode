#!/usr/bin/env python
#
# Copyright (C) 2007 Lemur Consulting Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""Get the current SVN revision.

The revision is written to a python file.

"""
__docformat__ = "restructuredtext en"

import os
import subprocess
from xml.sax.handler import ContentHandler
from xml.sax import parseString

class SvnInfoXmlHandler(ContentHandler):
    """XML parser for SVN info.

    """
    def __init__(self):
        self.rev = None
        self.url = None
        self.root = ''
        self.uuid = ''

    def startElement(self, name, attrs):
        self.text = ''
        if name == 'entry':
            rev = attrs['revision']
            if self.rev is None or self.rev < rev:
                self.rev = rev

    def endElement(self, name):
        if name == 'url':
            if self.url is None:
                self.url = self.text
            else:
                if len(self.text) < len(self.url):
                    assert(self.url.startswith(self.text))
                    self.url = self.text
        elif name == 'root':
            self.root = self.text
        elif name == 'uuid':
            self.uuid = self.text
        self.text = ''

    def characters(self, text):
        self.text += text


class RevisionException(Exception):
    """An error which occurred while getting the svn revision.

    """
    pass

def get_svn_rev():
    """Get the latest revision of subversion for any file in the checkout.

    This examines the SVN repository starting at the directory above the source
    directory for this file.  If this directory is not part of a SVN checkout,
    or the svn command line tools are not available, raises a RevisionException
    error with an explanatory message - otherwise, returns the revision (as a
    string).  Note that the revision may not be a pure number - it may include
    various strings to indicate that a branch, or a third-party repository, is
    being used.

    """
    if not os.path.exists(__file__):
        raise RevisionException("__file__ is not a path")
    toppath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    try:
        process = subprocess.Popen(['svn', '-R', '--xml', 'info', toppath],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        (out, err) = process.communicate()
    except Exception, e:
        raise RevisionException("Error running svn tools: %s" % str(e))

    out = out.strip()
    err = err.strip()
    if err != '':
        raise RevisionException("Error when attempting to run SVN command line tools: %s" %
                               str(err))
    info = SvnInfoXmlHandler()
    if out.strip() == '':
        raise RevisionException("SVN command line tools produced no output")
    parseString(out, info)

    if info.rev is None:
        raise RevisionException("No revision details found in output from svn info")

    if info.uuid != '07824224-6132-0410-9051-db7a3662f6e8':
        #print "Unknown external repository %r in use (uuid:%r)" % (info.root, info.uuid)
        info.rev = "ext" + info.rev
    else:
        info.rev = info.rev

    if not info.url.startswith(info.root + '/'):
        raise RevisionException("Invalid URL found in repository: url was %r, root was %r" %
                               (info.url, info.root))

    branch = info.url[len(info.root) + 1:]
    if branch != 'trunk':
        #print "Unknown branch %r" % branch
        info.rev = info.rev + branch

    return info.rev

def gen_revision_file(rev):
    """Generate the revision file, with the supplied revision number.

    This is intended to be run during a "build distribution" process - eg, when
    preparing tarballs, or freezing an executable for windows.

    """
    print "Generating svnrevision.py with revision set to %r" % rev
    
    toppath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    svnrevision_path = os.path.join(toppath, 'src', 'svnrevision.py')
    fd = open(svnrevision_path, 'wb')
    fd.write('''
# THIS FILE IS AUTOMATICALLY GENERATED
#
# Copyright (C) 2007 Lemur Consulting Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""Get the revision of SVN used to build this version of flax.

This file is generated by the utils/getsvnrev.py script.  Do not edit it
manually.  The script should be run whenever building snapshot releases, or
frozen binaries for windows.

"""
__docformat__ = "restructuredtext en"

svn_revision = %r
    '''.strip() % rev + '\n')
    fd.close()

if __name__ == '__main__':
    # Get the revision number
    try:
        rev = get_svn_rev()
    except RevisionException, e:
        print "Error - couldn't get SVN revision number: %s" % str(e)
    else:
        gen_revision_file(rev)
