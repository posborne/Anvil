# Copyright (c) 2012 Paul Osborne <osbpau@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from anvil import Anvil
from anvil.examples.helpers import find_changesets_for_authors
import datetime

AUTHORS = ["Paul Osborne", "Tom Manley"]
START_DT = datetime.datetime(2011, 11, 1)


def main():
    anvil = Anvil("spectrum")
    anvil.create_session_by_prompting()

    print "collecting related changesets"
    changesets_by_author = find_changesets_for_authors(anvil, AUTHORS, START_DT)
    for author, changesets in changesets_by_author.items():
        changesets = [c for c in changesets
                      if c.date_time > datetime.datetime(2011, 11, 1, 1, 1, 1)]
        eligible = [c for c in changesets
                    if (not c.is_merge() and not c.is_tag_changeset())]
        linked = [c for c in eligible if c.is_linked()]
        print "=== %s ===" % author
        print "  Total Changesets: %s" % len(changesets)
        print "  Total Elibigle: %s" % len(eligible)
        print "  Total Linked: %s" % len(linked)
        percentage_linked = (float(len(linked)) / len(eligible)) * 100
        print "  Percentage Linked: %0.2f" % percentage_linked
        print "\n"

if __name__ == '__main__':
    main()
