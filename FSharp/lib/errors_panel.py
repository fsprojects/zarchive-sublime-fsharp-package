from threading import Lock

import sublime

from FSharp.sublime_plugin_lib.panels import OutputPanel


# TODO: move this to common plugin lib.
class ErrorsPanel(object):
    _errors_pattern = r'^\w+\|\w+\|(.+)\|(\d+)\|(\d+)\|(.+)$'
    _lock = Lock()

    def __init__(self, name):
        self.name = name
        self._errors = []

    @property
    def errors(self):
        with self._lock:
            return self._errors

    @errors.setter
    def errors(self, value):
        with self._lock:
            self._errors = value

    def display(self):
        if len(self.errors) == 0:
            panel = OutputPanel(self.name)
            panel.hide()
            return

        formatted = self.format()
        with self._lock:
            panel = OutputPanel(self.name)
            panel.set('result_file_regex', self._errors_pattern)
            if sublime.version() > '3083':
                panel.view.set_syntax_file('Packages/FSharp/Support/FSharp Analyzer Output.sublime-syntax')
            else:
                panel.view.set_syntax_file('Packages/FSharp/Support/FSharp Analyzer Output.tmLanguage')
            panel.write(formatted)
            # TODO(guillermooo): Do not show now if other panel is showing.
            panel.show()

    def clear(self):
        self.errors = []

    def update(self, errors):
        self.errors = list(sorted(errors, key=lambda x: x.start_line))

    def format(self):
        tpl = '{severity}|{subcategory}|{file_name}|{start_line}|{start_column}|{message}'
        formatted = (tpl.format(**e.to_regex_result_data()) for e in self.errors)
        return '\n'.join(formatted)
