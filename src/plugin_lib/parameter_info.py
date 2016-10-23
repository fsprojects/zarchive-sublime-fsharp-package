import logging

import sublime
import sublime_plugin


_log = logging.getLogger(__name__)


__all__ = (
    'ShowParameterInfoCommand',
    )


class ShowParameterInfoCommand(sublime_plugin.TextCommand):

    def __init__(self, completions, editor_context, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editor_context = editor_context
        self.completions = completions

    def run(self, edit):
        try:
            w = sublime.active_window()
            param_name, _ = self.editor_context.locations[self.view.id()]
            r = [c for c in self.completions.cache if c.completion == param_name]
            thing = r[0]
            declaring_type = thing.declaring_type
            return_type = thing.return_type
            msg = "{} {}.{}".format(return_type, declaring_type, thing.completion)
            if thing.element.kind == 'METHOD':
                msg += thing.element.parameters
            summary = thing.doc_summary
            if summary:
                msg += '<br><br>{}'.format(summary)
            self.view.show_popup(msg, max_width=400)
        except Exception as e:
            _log.error(e)
            _log.error(e.stacktrace)
