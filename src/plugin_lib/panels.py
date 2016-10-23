# Copyright (c) 2014, Guillermo López-Anglada. Please see the AUTHORS file for details.
# All rights reserved. Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.)

import os
import abc

from threading import Lock

import sublime

from sublime import Region as R

from .sublime import after


class LineByLineOutputPanelNavigator:

    def __init__(self, view):
        self._current = -1
        self.view = view

    def next(self):
        if self._current >= self.view.rowcol(self.view.size())[0]:
            self._current = -1
        self._current += 1
        line = self.view.line(self.view.text_point(self._current, 0))
        self.view.sel().clear()
        self.view.erase_regions('self.higlights')
        self.view.add_regions('self.higlights', [line], 'comment', '', sublime.DRAW_NO_FILL)

    def previous(self):
        if self._current <= 0:
            self._current = self.view.rowcol(self.view.size())[0]
        else:
            self._current -= 1
        line = self.view.line(self.view.text_point(self._current, 0))
        self.view.sel().clear()
        self.view.erase_regions('self.higlights')
        self.view.add_regions('self.higlights', [line], 'comment', '', sublime.DRAW_NO_FILL)

    @property
    def current(self):
        raise NotImplementedError()

    @classmethod
    def from_panel(cls, view):
        return cls(view)


class OutputPanelConfiguration:

    def __init__(self):
        self._navigator = None
        self._settings = []
        self._name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def navigator(self):
        '''The navigator used to navigate the panel content.

        Defaults to a navigator that can navigate content by line.
        '''
        return self._navigator

    @navigator.setter
    def navigator(self, value):
        self._navigator = value

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        self._settings = value


class OutputPanelApi(metaclass=abc.ABCMeta):

    def __init__(self):
        self._navigator = None

    @abc.abstractmethod
    def write(self, content):
        pass

    @abc.abstractmethod
    def flush(self):
        pass

    @abc.abstractmethod
    def show(self, name):
        pass

    @abc.abstractmethod
    def hide(self, name):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def set(self, name, value):
        pass

    @abc.abstractmethod
    def get(self, name):
        pass

    @abc.abstractmethod
    def create_output_panel(self, name):
        pass

    @abc.abstractproperty
    @property
    def name(self):
        pass


class SublimeTextOutputPanelApi(OutputPanelApi):

    def __init__(self):
        self._name = None
        # Panels by window.
        self.panels = {}
        self.lock = Lock()
        self.window_of_last_write = None
        self._configuration = None
        self._navigators = {}


    def write(self, content):
        self.signal_change_of_panel()
        with self.lock:
            self.panel.run_command('append', {
                    'characters': content,
                    'force': True,
                    'scroll_to_end': True,
                    })
            self.window_of_last_write = self.window

    def signal_change_of_panel(self):
        if self.window_of_last_write:
            if self.window_of_last_write.id() != self.window.id():
                panel = self.window_of_last_write.find_output_panel(self.name)
                if panel:
                    with self.lock:
                        panel.run_command('append', {
                            'characters': '# ============ input moved to a different window ============',
                        })

    def flush(self):
        pass

    def show(self):
        self.window.run_command('show_panel', {
                'panel': 'output.%s' % self.name
                })

    def hide(self):
        self.window.run_command('hide_panel', {
                'panel': 'output.%s' % self.name
                })

    def clear(self):
        raise Exception('not supported')

    def reset(self):
        for w in sublime.windows():
            if w.id() in self.panels:
                w.destroy_output_panel(self.name)
        self.panels.clear()
        self.create_output_panel()

    def set(self, name, value):
        self.panel.settings().set(name, value)

    def get(self, name, default=None):
        return self.panel.settings().get(name, default)

    def create_output_panel(self):
        view = self.window.create_output_panel(self.name)
        view.sel().clear()
        self.panels[self.window.id()] = view
        self.configure()
        if self.configuration.navigator:
            self._navigators[self.window.id()] = self.configuration.navigator(view)
        return view

    def find_output_panel(self):
        return self.window.find_output_panel(self.name)

    @property
    def panel(self):
        panel = self.panels.get(self.window.id())
        if not panel:
            self.create_output_panel()
        return self.panels[self.window.id()]

    @property
    def content(self):
        with self.lock:
            return self.panel.substr(R(0, self.panel.size()))

    @property
    def window(self):
        w = sublime.active_window()
        if not w:
            raise ValueError('a window is required')
        return w

    @property
    def name(self):
        return self._name

    def configure(self):
        assert self.configuration, 'valid configuration required'

        # default config
        self.set('word_wrap', False)
        self.set('line_numbers', False)
        self.set('gutter', False)
        self.set('scroll_past_end', False)

        for name, value in self.configuration.settings:
            self.set(name, value)
            # If we don't do this, the syntax change does not seem to take effect,
            # even though the syntax property is set.
            if name == 'syntax':
                self.panel.set_syntax_file(value)

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        self._name = value.name
        self._configuration = value

    @property
    def navigator(self):
        # Ensure we have a panel and a navigator, if available.
        _ = self.panel
        return self._navigators.get(self.window.id())


class OutputPanel:
    """Manages an ST output panel.

    Can be used as a file-like object.
    """

    def __init__(self, api, configuration):
        self.configuration = configuration
        self.api = api
        self.api.configuration = self.configuration

    def set(self, name, value):
        self.api.set(name, value)

    def _clean_text(self, text):
        return text.replace('\r', '')

    def write(self, text):
        assert isinstance(text, str), 'must pass decoded text data'
        self.api.write(self._clean_text(text))

    def flush(self):
        self.api.flush()

    def hide(self):
        self.api.hide()

    def show(self):
        self.api.show()

    def clear(self):
        self.reset()

    def reset(self):
        self.api.reset()

    @property
    def name(self):
        return self.configuration.name

    @property
    def navigator(self):
        return self.api.navigator


# TOOD: fix this
class ErrorPanel(object):
    def __init__(self):
        self.panel = OutputPanel('dart.info')
        self.panel.write('=' * 80)
        self.panel.write('\n')
        self.panel.write("Dart - Something's not quite right\n")
        self.panel.write('=' * 80)
        self.panel.write('\n')
        self.panel.write('\n')

    def write(self, text):
        self.panel.write(text)

    def show(self):
        self.panel.show()


# TODO: move this to common plugin lib.
class ErrorsPanel(object):
    """
    A panel that displays errors and enables error navigation.
    """
    _sublime_syntax_file = None
    _tm_language_file = None
    _errors_pattern = ''
    _errors_template = ''

    _lock = Lock()

    def __init__(self, name):
        """
        @name
          The name of the underlying output panel.
        """
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

    @property
    def errors_pattern(self):
        """
        Subclasses can override this to provide a more suitable pattern to
        capture errors.
        """
        return self._errors_pattern

    @property
    def errors_template(self):
        """
        Subclasses can override this to provide a more suitable template to
        display errors.
        """
        return self._errors_template

    def display(self):
        if len(self.errors) == 0:
            panel = OutputPanel(self.name)
            panel.hide()
            return

        # Like this to avoid deadlock. XXX: Maybe use RLock instead?
        formatted = self.format()
        with self._lock:
            # XXX: If we store this panel as an instance member, it won't work.
            # Revise implementation.
            panel = OutputPanel(self.name)
            panel.set('result_file_regex', self.errors_pattern)
            # TODO: remove this when we don't support tmLanguage any more.
            if sublime.version() > '3083':
                panel.view.set_syntax_file(self._sublime_syntax_file)
            else:
                panel.view.set_syntax_file(self._tm_language_file)
            panel.write(formatted)
            # TODO(guillermooo): Do not show now if other panel is showing;
            # for example, the console.
            panel.show()

    def clear(self):
        self.errors = []

    def update(self, errors, sort_key=None):
        self.errors = list(sorted(errors, key=sort_key))

    def get_item_result_data(self, item):
        """
        Subclasses must implement this method.

        Must return a dictionary to be used as data for `errors_template`.
        """
        return {}

    def format(self):
        formatted = (self.errors_template.format(**self.get_item_result_data(e))
                for e in self.errors)
        return '\n'.join(formatted)
