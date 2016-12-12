import logging

import sublime

from .plugin_lib.view import exists_and_is_on_disk

from .common.di import inject


_log = logging.getLogger('Palantir.Palantir_fsharp.main')


def is_fsharp_file(view):
    return view.file_name() and view.file_name().endswith('.fsx')


def is_active_file(view):
    return view.id() == sublime.active_window().active_view().id()


##############################################################################
# Make commands available to Sublime Text and start firing events.
##############################################################################
from .commands import *
# from rxst.connectors import AsyncEventsConnector
##############################################################################
