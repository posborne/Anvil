Anvil
-----

Anvil a python library that seeks to simplify accessing and
manipulating data in the Kiln (http://www.fogcreek.com/kiln/) system
easier and more intuitive.

Example
-------

Here's a basic example showing how one might grab the name of all repos:

    >>> from anvil import Anvil
    >>> anvil = Anvil("mycompany")
    >>> anvil.create_session_by_prompting()
    Kiln Username: me@mycomponay.com
    Password: ***********
    >>> repos = anvil.get_repos()
    >>> print '\n'.join(r.name for r in repos)
    RepoA
    RepoB
    RepoC

License
-------

The library is licensed under the MIT license meaning you can use it
however you feel is most appropriate so long as you don't remove the
license notifications.  Contributions back to the project would be
greatly appreciated.
