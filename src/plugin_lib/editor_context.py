from collections import defaultdict

import sublime


class EditorContext:

    def __init__(self):
        self.completion_state = None
        self.location = None
        self.locations = defaultdict(lambda: None)

    def update_completion_state(self, view):
        s = list(view.sel())[0]
        text = view.substr(view.line(s.b))
        try:
            text = text.rsplit('.')[-1]
        except IndexError:
            self.locations[view.id()] = None
            return
        self.locations[view.id()] = text, list(view.sel())[0]

    @property
    def should_show_parameter_info(self):
        w = sublime.active_window()
        v = w.active_view()

        s = list(v.sel())[0]
        text = v.substr(v.line(s.b))
        try:
            text = text.rsplit('.')[1]
        except IndexError:
            return False

        locations = self.locations[v.id()]
        return (locations
                and locations[0] == text
                and locations[1] == s)
