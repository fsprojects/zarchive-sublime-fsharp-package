import os


def truncate_at_home(path):
    """Truncates a path at the $HOME path if they share
    the same prefix, or returns the path as is if not.
    """
    p = os.path.abspath(path)
    home = os.path.expanduser('~')
    if os.path.commonprefix([home, p]) == home:
        return os.path.join('~', p[len(home):])
    return path
