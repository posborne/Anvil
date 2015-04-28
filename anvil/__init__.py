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

from anvil.entities import KilnProject
from anvil.utils import memoized
import getpass
import json
import requests

__all__ = ['Anvil']


class Anvil(object):
    """An Anvil is the main interface object to the Kiln API

    Example Usage::

        >>> anvil = Anvil("mycompany")
        >>> anvil.create_session()
        >>> anvil.

    """

    def __init__(self, kiln_prefix, verify_ssl_cert):
        self.kiln_prefix = kiln_prefix
        self.verify_ssl_cert = verify_ssl_cert
        self.token = None

    def _kiln_url(self, path):
        return ("{prefix}/Api/1.0/{path}"
                .format(prefix=self.kiln_prefix, path=path))

    def get_json(self, path, **kwargs):
        if not 'sUser' in kwargs and not 'sPassword' in kwargs:
            kwargs['token'] = self.token
        url = self._kiln_url(path)
        r = requests.get(url, params=kwargs, verify=self.verify_ssl_cert)
        return json.loads(r.text)

    def create_session(self, user, password):
        """Create a "session" with Kiln... basically, get a token to use"""
        self.token = \
            self.get_json("Auth/Login", sUser=user, sPassword=password)

    def create_session_by_prompting(self):
        """Prompt user for login credentials"""
        user = raw_input("Kiln Login: ")
        password = getpass.getpass("Password: ")
        self.create_session(user, password)

    @memoized
    def get_projects(self):
        projects = []
        for project_json in self.get_json("Project"):
            projects.append(KilnProject.from_json(self, project_json))
        return projects

    @memoized
    def get_repos(self):
        repo_indices = set()
        repos = []
        for project in self.get_projects():
            for repo_group in project.repo_groups:
                for repo in repo_group.repos:
                    if not repo.index in repo_indices:
                        repo_indices.add(repo.index)
                        repos.append(repo)
        return repos
