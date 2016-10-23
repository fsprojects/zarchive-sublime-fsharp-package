import os


def exists_and_is_on_disk(view):
    return view and view.file_name() and os.path.exists(view.file_name())
