import os
import abc

from collections import defaultdict
from threading import Lock

import sublime

from sublime import Region as R
from sublime import Phantom
from sublime import PhantomSet

from .section_list import SectionList

from .panels import OutputPanel
from .panels import OutputPanelConfiguration
from .panels import SublimeTextOutputPanelApi
from .panels import LineByLineOutputPanelNavigator


def truncate_at_home(path):
    """Truncates a path at the $HOME path if they share
    the same prefix, or returns the path as is if not.
    """
    p = os.path.abspath(path)
    home = os.path.expanduser('~')
    if os.path.commonprefix([home, p]) == home:
        return os.path.join('~', p[len(home):])
    return path


class CodeIssueSeverity:

    ERROR = 500
    WARNING = 400
    INFO = 300


class CodeIssue:
    '''Represents an issue with source code: build error, linter warning, etc.

    This class can represent also misspellings or any other source code or
    textual issue worth flagging for inspection.
    '''

    def __init__(self,
                severity,
                file,
                start_line,
                start_column,
                message,
                location
                ):
        self._severity = severity
        self._path = file
        self._start_line = start_line
        self._start_column = start_column
        self._message = message
        self._location = location

    @property
    def severity(self):
        return self._severity

    @property
    def file(self):
        return self._path

    @property
    def start_line(self):
        return self._start_line

    @property
    def start_column(self):
        return self._start_column

    @property
    def message(self):
        return self._message

    @property
    def location(self):
        return self._location

    def to_panel_line(self):
        return "{:<7}|{}:{:0>4}:{:0>4}|{}".format(
                self._severity,
                truncate_at_home(self._path),
                self._start_line,
                self._start_column,
                self._message,
                )


class CodeIssueManager:
    '''Manages a collection of CodeIssues.

    To use this class, first instantiate it and then call it as a function
    passing in an iterable of CodeIssues whenever you want to update the
    collection of issues.
    '''

    def __init__(self, api, issue_types):
        # The native editor API that does the low-level work.
        # Must implement CodeIssueManagerApi.
        self.api = api
        self.issue_types = issue_types
        self.issues = SectionList(self.issue_types)
        self.current = self.issues.head
        self.lock = Lock()

    def __call__(self, issues):
        issue_list = list(issues)

        self.update_issues(issue_list)

        file = None

        try:
            file = issue_list[0].file
        except IndexError:
            self.api.unhighlight()
            self.api.hide_details()
            self.api.reset_panel()
            return

        self.api.reset_panel()
        assert self.api.panel, 'we need a panel here'

        error_lines, error_regions = self._prepare_data(issue_list)

        self.api.highlight(error_regions)
        self.api.write_panel(error_lines)

    def update_issues(self, issues):
        new_list = SectionList(self.issue_types)

        for error in issues:
            new_list.add(error.severity, error)

        with self.lock:
            self.issues = new_list
            self.current = self.issues.head

    def _prepare_data(self, issues):
        lines = []
        regions = []
        for error in issues:
            lines.append(error.to_panel_line())
            regions.append(error.location)
        return (lines, regions)

    def show_next(self):
        node = None

        with self.lock:
            if not self.current:
                self.current = self.issues.head

            node = self.current.next

            if not node and self.issues.head.next:
                self.current = self.issues.head
                node = self.current.next
            elif not node:
                self.current = self.issues.head
                return

            self.current = node

        error = node.value

        self.api.show_details(error)


# Implements the native editor API for managing and displaying code issues.

class ActiveViewGetter:

    def __get__(self, obj, ins):
        return sublime.active_window().active_view()


class CodeIssueManagerApi(metaclass=abc.ABCMeta):
    '''Defines an interface for editors that want to display code issues and let
    users navigate them.
    '''

    @abc.abstractmethod
    def highlight(self, error_regions):
        '''Shows errors in the ui (for example, outlining regions of text.)
        '''
        pass

    @abc.abstractmethod
    def unhighlight(self):
        pass

    @abc.abstractmethod
    def write_panel(self, lines):
        '''Writes errors to a panel.
        '''
        pass

    @abc.abstractmethod
    def reset_panel(self):
        '''Resets the underlying panel used to display errors. After calling
        this method, it's assumed the panel is in a pristine state.
        '''
        pass

    @abc.abstractmethod
    def set_base_directory(self, path):
        '''Sets the directory at which relative paths for finding errored files
        are to be rooted.
        '''
        pass

    @abc.abstractmethod
    def show_details(self, error):
        '''Shows details about a single error (for example, next to the
        offending line of code).
        '''
        pass

    @abc.abstractmethod
    def hide_details(self):
        pass


class CodeIssueManagerConfiguration:

    def __init__(self):
        self.key = None
        self.settings = []


class SublimeTextCodeIssueManagerApi(CodeIssueManagerApi):

    view = ActiveViewGetter()

    def __init__(self, configuration):
        self.configuration = configuration
        self.phantom_set_by_view = defaultdict(
                lambda: PhantomSet(self.view, self.configuration.key)
                )
        configuration = OutputPanelConfiguration()
        configuration.name = self.configuration.key
        configuration.settings = self.configuration.settings
        # configuration.settings = [
                # ('syntax', 'Packages/Dart/Syntaxes/Dart Analysis Output.sublime-syntax')
                # ]
        configuration.navigator = LineByLineOutputPanelNavigator
        api = SublimeTextOutputPanelApi()
        self.panel = OutputPanel(api=api, configuration=configuration)

    def reset_panel(self):
        self.panel.reset()

    def highlight(self, error_regions):
        self.view.add_regions(
                self.configuration.key,
                [R(*r) for r in error_regions],
                'invalid',
                'dot',
                sublime.DRAW_SQUIGGLY_UNDERLINE
                        | sublime.DRAW_NO_FILL
                        | sublime.DRAW_NO_OUTLINE)

    def write_panel(self, lines):
        if lines:
            self.panel.write('\n'.join(lines))

    def unhighlight(self):
        self.view.erase_regions(self.configuration.key)

    def set_base_directory(self, path):
        pass

    def show_details(self, error):
        style = '''
        <style>
            div {
                color: gray;
                padding: 0.3em;
                background-color: black
            }
        </style>
        '''

        phantom = Phantom(
                R(*error.location),
                (style +
                '<div>'
                + error.message
                + '</div>'),
                sublime.LAYOUT_BLOCK)

        phantom_set = self.phantom_set_by_view[self.view.id()]
        phantom_set.update([phantom])

        view = self.view
        view.sel().clear()
        view.sel().add(R(*error.location).begin())
        view.show(view.sel()[0])

        self.panel.navigator.next()

    def hide_details(self):
        self.view.erase_phantoms(self.configuration.key)
