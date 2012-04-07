from anvil import Anvil
import datetime
import functools
import threading
import times
from matplotlib import pyplot as pp

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
    changesets = find_changesets_for_authors(
        anvil, ['Paul Osborne', ], datetime.datetime(2009, 1, 1)).values()[0]

    commit_hour = [times.to_local(c.date_time, 'US/Central').hour for c in changesets]
    pp.hist(commit_hour, 24)
    a = pp.gca()
    a.set_xlim([0, 23])
    pp.show()


if __name__ == '__main__':
    main()
