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

from anvil.utils import iso_8601_to_datetime


class KilnChangeset(object):

    @classmethod
    def from_json(cls, anvil, changeset_json):
        reviews = changeset_json['ixReviews']
        bugs = changeset_json['ixBugs']
        rev = changeset_json['rev']
        rev_parent1 = changeset_json['revParent1']
        rev_parent2 = changeset_json['revParent2']
        author = changeset_json['sAuthor']
        description = changeset_json['sDescription']
        date_time = iso_8601_to_datetime(changeset_json['dt'].rsplit('.', 1)[0])
        return cls(anvil, reviews, bugs, rev, rev_parent1, rev_parent2,
                   author, description, date_time)

    def is_merge(self):
        return (None not in (self.rev_parent1, self.rev_parent2))

    def is_tag_changeset(self):
        # use the beginning of the description
        return self.description.lower().startswith("added tag")

    def is_linked(self):
        return len(self.bugs) > 0

    def __init__(self, anvil, reviews, bugs, rev, rev_parent1,
                  rev_parent2, author, description, date_time):
        self.anvil = anvil
        self.reviews = reviews
        self.bugs = bugs
        self.rev = rev
        self.rev_parent1 = rev_parent1
        self.rev_parent2 = rev_parent2
        self.author = author
        self.description = description
        self.date_time = date_time


class KilnPerson(object):

    @classmethod
    def from_json(cls, anvil, person_json):
        index = person_json['ixPerson']
        email = person_json['sEmail']
        name = person_json['sName']
        return cls(anvil, index, email, name)

    def __init__(self, anvil, index, email, name):
        self.anvil = anvil
        self.index = index
        self.email = email
        self.name = name

class KilnAnnotation(object):

    @classmethod
    def from_json(cls, anvil, annotation_json):
        lines = annotation_json['nLines']
        rev = annotation_json['rev']
        author = annotation_json['sAuthor']
        return cls(anvil, lines, rev, author)

    def __init__(self, anvil, lines, rev, author):
        self.anvil = anvil
        self.lines = lines
        self.rev = rev
        self.author = author

class KilnCat(object):

    @classmethod
    def from_json(cls, anvil, cat_json):
        lines = cat_json['bsLines']
        annotations = cat_json['annotations']
        return cls(anvil, lines, annotations)

    def __init__(self, anvil, lines, annotations):
        self.anvil = anvil
        self.lines = lines
        self.annotations = annotations

class KilnRepo(object):

    @classmethod
    def from_json(cls, anvil, repo_json):
        index = repo_json['ixRepo']
        repo_group_index = repo_json['ixRepoGroup']
        parent_index = repo_json['ixRepo']
        central = repo_json['fCentral']
        permission_default = repo_json['permissionDefault']
        creator = repo_json['personCreator']
        if creator:
            creator = KilnPerson.from_json(anvil, creator)
        branches = repo_json['repoBranches']
        repo_group_aliases = repo_json['rgAliases']
        description = repo_json['sDescription']
        group_slug = repo_json['sGroupSlug']
        name = repo_json['sName']
        project_slug = repo_json['sProjectSlug']
        slug = repo_json['sSlug']
        status = repo_json['sStatus']
        return cls(anvil, index, repo_group_index, parent_index, central,
                   permission_default, creator, branches, repo_group_aliases,
                   description, group_slug, name, project_slug, slug, status)

    def __init__(self, anvil, index, repo_group_index, parent_index, central,
                   permission_default, creator, branches, repo_group_aliases,
                   description, group_slug, name, project_slug, slug, status):
        self.anvil = anvil
        self.index = index
        self.repo_group_index = repo_group_index
        self.parent_index = parent_index
        self.central = central
        self.permission_default = permission_default
        self.creator = creator
        self.branches = branches
        self.repo_group_aliases = repo_group_aliases
        self.description = description
        self.group_slug = group_slug
        self.name = name
        self.project_slug = project_slug
        self.slug = slug
        self.status = status

    def search_changesets(self, query, max_results=400):
        """Query this repository, returns a list of KilnChangesets"""
        res = self.anvil.get_json("Search/Changesets", ixRepo=self.index,
                                  sQuery=query, cHits=max_results)
        changesets = []
        for changeset_json in res['resultChangeset']:
            changesets.append(KilnChangeset.from_json(self.anvil, changeset_json))
        return changesets
    
    def where_used(self):
        """
        Return a list of repositories that have this repository as a sub-repo.
        """
        subrepos = []
        projects = []
        path = ''.join("%02X" % ord(x) for x in ".hgsub")
        for project_json in self.anvil.get_json("Project"):
            projects.append(KilnProject.from_json(self, project_json))
        for project in projects:
            for repo_group in project.repo_groups:
                for repo in repo_group.repos:
                    if repo.index != self.index:
                        tmp = "Repo/" + str(repo.index) + "/File/" + path
                        res = self.anvil.get_json(tmp)
                        if not res.has_key('errors'):
                            print "Checking repo index %d for %s..." % \
                                  (repo.index, self.name)
                            cat = KilnCat.from_json(self.anvil, res)
                            for entry in cat.lines:
                               if self.name in entry:
                                   subrepos.append(repo)
        return subrepos

class KilnRepoGroup(object):

    @classmethod
    def from_json(cls, anvil, repo_group_json):
        project_index = repo_group_json['ixProject']
        index = repo_group_json['ixRepoGroup']
        repos = [KilnRepo.from_json(anvil, repo_json)
                 for repo_json in repo_group_json['repos']]
        name = repo_group_json['sName']
        slug = repo_group_json['sSlug']
        return cls(anvil, index, project_index, name, slug, repos)

    def __init__(self, anvil, index, project_index, name, slug, repos):
        self.anvil = anvil
        self.index = index
        self.project_index = project_index
        self.name = name
        self.slug = slug
        self.repos = repos


class KilnProject(object):

    @classmethod
    def from_json(cls, anvil, project_json):
        index = project_json['ixProject']
        permission_default = project_json.get('permission_default')
        description = project_json['sDescription']
        name = project_json['sName']
        slug = project_json['sSlug']
        repo_groups = [KilnRepoGroup.from_json(anvil, repo_group_json)
                       for repo_group_json in project_json['repoGroups']]
        return cls(anvil, index, permission_default, description, name,
                   slug, repo_groups)

    def __init__(self, anvil, index, permission_default, description,
                 name, slug, repo_groups):
        self.anvil = anvil
        self.index = index
        self.permission_default = permission_default
        self.description = description
        self.name = name
        self.slug = slug
        self.repo_groups = repo_groups
