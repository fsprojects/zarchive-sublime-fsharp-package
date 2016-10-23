import logging

import sublime
import sublime_plugin

from threading import Lock


_log = logging.getLogger(__name__)


class CompletionSuggestion:

    def __ini__(self):
        self.completion = None
        self.element = None
        self.declaring_type = None
        self.doc_summary = None


class Element:

    def __init__(self):
        self.return_type = None
        self.parameters = None
        self.kind = None


class Completions:

    def __init__(self, server):
        self.server = server
        self.lock = Lock()
        self.previous_pos = None
        self.view = None
        self.handler = CompletionsHandler(self)
        self.cache = None
        self.completions_formatter = CompletionsFormatter()
        self.latest = { }

    def send_request(self, view):
        assert view, 'need a non-null view'
        assert view.file_name(), 'need a view with a file path'
        self.cache = None
        with self.lock:
            self.previous_pos = list(view.sel())[0]
            self.view = view
        context = {
            'file': view.file_name(),
            'offset': view.sel()[0].b,
            'callback': None,
        }
        self.server.request_completion_suggestions(context)

    def fetch_latest(self):
        if self.latest:
            self.cache = self.latest
            return self.format(self.latest)
        else:
            self.cache = None

    def format(self, data):
        if not data:
            return []
        return self.completions_formatter(data)

    def check_is_response_valid(self, response):
        # response: {
        #   "id": String
        #   "error": optional RequestError
        #   "result": {
        #     "id": CompletionId
        #   }
        # }
        with self.lock:
            return (self.view
                    and self.previous_pos == list(self.view.sel())[0])


class CompletionsHandler:

    def __init__(self, completions):
        self.completions = completions

    def __call__(self, data):
        if not self.completions.check_is_response_valid(data):
            return
        self.completions.latest = data
        v = sublime.active_window().active_view()
        v.run_command('auto_complete')


class CompletionsFormatter:

    def __init__(self):
        self.symbols = {
            'METHOD': '►',
            'INVOCATION': '►',
            'FIELD': '○',
            'GETTER': '●',
        }

    def __call__(self, results):
        return [["{} {}{} → {}".format(
                self.symbols.get(r.element.kind),
                r.completion,
                r.element.parameters,
                r.return_type),
                r.completion]
                for r in results
                ]


class AutocompleteEventListener(sublime_plugin.EventListener):

    _INHIBIT_OTHER = (
            sublime.INHIBIT_WORD_COMPLETIONS
            | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def __init__(self, completions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completions = completions

    def check(self, view):
        message = ("must return a bool indicating "
                "if the view should be offered completions")
        raise NotImplementedError(message)

    def check_scope(self, locations):
        message = ("must return a bool indicating "
                "if we're in a string or comment")
        raise NotImplementedError(message)

    def _is_in_string_or_comment(self, view, locations):
        return self.check_scope(view, locations)

    def on_query_completions(self, view, prefix, locations):
        if not self.check(view):
            return ([], 0)

        if view.settings().get('command_mode') is True:
            return ([], self._INHIBIT_OTHER)

        if self._is_in_string_or_comment(view, locations):
            return ([], 0)

        completions = self.completions.fetch_latest()
        return (completions or [], self._INHIBIT_OTHER)
