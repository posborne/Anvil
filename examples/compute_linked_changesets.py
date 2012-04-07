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
import datetime
import functools
import threading

AUTHORS = ["Paul Osborne", "Tom Manley"]
START_DT = datetime.datetime(2011, 11, 1)


def find_changesets_for_authors(anvil, authors, start_dt,
                                end_dt=datetime.datetime.now()):
    """parallel search for changesets by some set of users in a date range"""
    repos = anvil.get_repos()

    kiln_start_date = start_dt.strftime("%m/%d/%Y")
    kiln_end_date = end_dt.strftime("%m/%d/%Y")

    results = {}

    def compute_and_store(repo, person, start_date, end_date):
        result = repo.search_changesets(
            'edited:"{}:{}" author:"{}"'.format(kiln_start_date, kiln_end_date, person))
        results[(repo, person)] = result

    computations = []
    for repo in repos:
        for person in authors:
            f = functools.partial(compute_and_store,
                                  repo, person, "11/1/11", "4/6/12")
            computations.append(f)

    threads = [threading.Thread(target=computation)
               for computation in computations]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    changesets_by_author = {}
    for (repo, author), changesets in results.items():
        changesets_by_author.setdefault(author, []).extend(changesets)

    return changesets_by_author


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
