import threading
from collections import defaultdict

import sublime
import sublime_plugin

# move this code to the sublime_plugin_lib
from FSharp.sublime_plugin_lib.sublime import after


class IdleIntervalEventListener(sublime_plugin.EventListener):
    """
    Monitors idle time and calls .on_idle() after the specified duration.

    Idle time is defined as time during which no calls to .on_modified[_async]()
    have been made.
    """

    def __init__(self, *args, duration=500, **kwargs):
        """
        @duration
          Interval after which an .on_idle() call will be made, expressed in
          milliseconds.
        """

        # TODO: Maybe it's more efficient to collect .on_idle() functions and
        # manage edits globally, then call collected functions when idle.
        self.edits = defaultdict(int)
        self.lock = threading.Lock()

        # Expressed in milliseconds.
        self.duration = duration
        super().__init__(*args, **kwargs)

    @property
    def is_subclass(self):
        return hasattr(self, 'on_idle')

    def _add_edit(self, view):
        with self.lock:
            self.edits[view.id()] += 1
        # TODO: are we running async or sync?
        after(self.duration, lambda: self._subtract_edit(view))

    def _subtract_edit(self, view):
        with self.lock:
            self.edits[view.id()] -= 1
            if self.edits[view.id()] == 0:
                self.on_idle(view)

    # def on_idle(self, view):
    #     """
    #     Executes after @self.duration milliseconds have passed without a call
    #     to .on_modified[_async]().
    #     """
    #     pass

    def on_modified_async(self, view):
        # TODO: improve check for widgets and overlays.
        if not all((view, self.is_subclass, self.check(view))):
            return
        self._add_edit(view)

    # Override in derived class if needed.
    def check(self, view):
        """
        Checks if @view should be monitored for idleness.

        @view
          The view that is about to be monitored for idleness.
        """
        return True
