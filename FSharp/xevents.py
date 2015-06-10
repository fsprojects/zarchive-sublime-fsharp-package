# Copyright (c) 2014, Guillermo López-Anglada. Please see the AUTHORS file for details.
# All rights reserved. Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.)

from collections import defaultdict
import json
import logging
import threading

import sublime
import sublime_plugin

from FSharp.fsac.server import completions_queue
from FSharp.fsharp import editor_context
from FSharp.lib.project import FileInfo
from FSharp.lib.response_processor import add_listener
from FSharp.lib.response_processor import ON_COMPLETIONS_REQUESTED
from FSharp.sublime_plugin_lib.context import ContextProviderMixin
from FSharp.sublime_plugin_lib.sublime import after
from FSharp.sublime_plugin_lib.events import IdleIntervalEventListener


_logger = logging.getLogger(__name__)


class IdleAutocomplete(IdleIntervalEventListener):
    """
    Shows the autocomplete list after @self.duration milliseconds of inactivity.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duration = 400

    # FIXME: we should exclude widgets and overlays in the base class.
    def check(self, view):
        # Offer F# completions in F# files when the caret isn't in a string or
        # comment. If strings or comments, offer plain Sublime Text completions.
        return all((
            view.file_name(),
            not view.match_selector(view.sel()[0].b, 'source.fsharp string, source.fsharp comment'),
            FileInfo(view).is_fsharp_code))

    def on_idle(self, view):
        self._show_completions(view)

    def _show_completions(self, view):
        try:
            # TODO: We probably should show completions after other chars.
            is_after_dot = view.substr(view.sel()[0].b - 1) == '.'
        except IndexError:
            return

        if is_after_dot:
            view.window().run_command('fs_run_fsac', {'cmd': 'completion'})


class FSharpProjectTracker(sublime_plugin.EventListener):
    """
    Event listeners.
    """

    parsed = {}
    parsed_lock = threading.Lock()

    def on_activated_async(self, view):
        # It seems we may receive a None in some cases -- check for it.
        if not view or not view.file_name() or not FileInfo(view).is_fsharp_code:
            return

        with FSharpProjectTracker.parsed_lock:
            view_id = view.file_name() or view.id()
            if FSharpProjectTracker.parsed.get(view_id):
                return

        editor_context.parse_view(view)
        self.set_parsed(view, True)

    def on_load_async(self, view):
        self.on_activated_async(view)

    def set_parsed(self, view, value):
        with FSharpProjectTracker.parsed_lock:
            view_id = view.file_name() or view.id()
            FSharpProjectTracker.parsed[view_id] = value

    def on_modified_async(self, view):
        if not view or not view.file_name() or not FileInfo(view).is_fsharp_code:
            return

        self.set_parsed(view, False)


class FSharpContextProvider(sublime_plugin.EventListener, ContextProviderMixin):
    """
    Implements contexts for .sublime-keymap files.
    """

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == 'fs_is_code_file':
            value = FileInfo(view).is_fsharp_code
            return self._check(value, operator, operand, match_all)


class FSharpAutocomplete(sublime_plugin.EventListener):
    """
    Provides completion suggestions from fsautocomplete.
    """

    WAIT_ON_COMPLETIONS = False
    _INHIBIT_OTHER = (sublime.INHIBIT_WORD_COMPLETIONS |
               sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    @staticmethod
    def on_completions_requested(data):
        FSharpAutocomplete.WAIT_ON_COMPLETIONS = True

    @staticmethod
    def fetch_completions():
        data = completions_queue.get(block=True, timeout=.75)
        data = json.loads(data.decode('utf-8'))
        completions = [[item, item] for item in data['Data']]
        return completions

    @staticmethod
    def _in_string_or_comment(view, locations):
        return all((view.match_selector(loc, 'source.fsharp comment, source.fsharp string')
            or view.match_selector(loc - 1, 'source.fsharp comment, sorce.fsharp string'))
                for loc in locations)

    def on_query_completions(self, view, prefix, locations):
        if not FSharpAutocomplete.WAIT_ON_COMPLETIONS:
            if not FileInfo(view).is_fsharp_code:
                return []

            if self._in_string_or_comment(view, locations):
                return []

            return ([], self._INHIBIT_OTHER)

        try:
            return (self.fetch_completions(), self._INHIBIT_OTHER)
        # FIXME: Be more explicit about caught exceptions.
        except:
            return ([], self._INHIBIT_OTHER)
        finally:
            FSharpAutocomplete.WAIT_ON_COMPLETIONS = False


# TODO: make decorator?
add_listener(ON_COMPLETIONS_REQUESTED, FSharpAutocomplete.on_completions_requested)
