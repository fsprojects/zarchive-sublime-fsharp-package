import logging

import sublime

from .plugin_lib.editor_activity import EditorActivity
from .plugin_lib.view import exists_and_is_on_disk

from .common.di import inject


_log = logging.getLogger(__name__)


def if_fsharp_file(view):
    return view.file_name() and view.file_name().endswith('.fs')


def is_active_file(view):
    return view.id() == sublime.active_window().active_view().id()


class FSharpEditorActivity(EditorActivity):

    @inject
    def __init__(self, server, error_manager, completions, editor_context):
        super().__init__(server, error_manager, editor_context, completions)
        self.completions = completions
        self.editor_context = editor_context

    def configure_member_access_operator_observable(self, observable):
        return observable \
                .where(lambda x, _: if_fsharp_file(x.data)) \
                .where(lambda x, _: is_active_file(x.data))

    def configure_call_operator_observable(self, observable):
        return observable \
                .where(lambda x, _: if_fsharp_file(x.data)) \
                .where(lambda x, _: is_active_file(x.data))

    def configure_file_changes_observable(self, observable):
        return observable \
                .where(lambda x, _: if_fsharp_file(x.data)) \
                .debounce(200)

    def configure_post_commit_completion_observable(self, observable):
        return observable \
                .where(lambda x: exists_and_is_on_disk(x.data)) \
                .where(lambda x: if_fsharp_file(x.data)) \
                .where(lambda x: len(x.data.sel()) == 1) \
                .where(lambda x: x.data.view.has_non_empty_selection_region())

    def on_typed_call_operator(self, event_args):
        pass
        # event_args.data.run_command('dart_show_parameter_info')


def plugin_loaded():
    pass
    # sublime.set_timeout(FSharpEditorActivity, 500)



##############################################################################
# Make commands available to Sublime Text and start firing events.
##############################################################################
from .commands import *
# from rxst.connectors import AsyncEventsConnector
##############################################################################
