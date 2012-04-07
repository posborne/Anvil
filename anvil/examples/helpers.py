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

from anvil.utils import parallel_execute
import datetime
import functools


def find_changesets_for_authors(anvil, authors, start_dt,
                                end_dt=datetime.datetime.now()):
    """parallel search for changesets by some set of users in a date range"""
    results = {}

    def compute_and_store(repo, person, start_date, end_date):
        result = repo.search_changesets(
            'edited:"{}:{}" author:"{}"'.format(start_date,
                                                end_date, person))
        results[(repo, person)] = result

    kiln_start_date = start_dt.strftime("%m/%d/%Y")
    kiln_end_date = end_dt.strftime("%m/%d/%Y")

    computations = []
    repos = anvil.get_repos()
    for repo in repos:
        for person in authors:
            f = functools.partial(
                compute_and_store,
                repo, person, kiln_start_date, kiln_end_date)
            computations.append(f)

    parallel_execute(*computations)

    changesets_by_author = {}
    for (repo, author), changesets in results.items():
        changesets_by_author.setdefault(author, []).extend(changesets)

    return changesets_by_author
