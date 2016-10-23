import logging

import sublime

from sublime import Region as R

from rxst._init_ import async_events


_log = logging.getLogger(__name__)


def is_for_current_file(errors):
    v = sublime.active_window().active_view()
    try:
        return v.file_name() == errors[0].file
    except IndexError:
        return True


class EditorActivity:

    def __init__(self, server, error_manager, editor_context, completions):
        self.member_operator = '.'
        self.call_operator = '('
        self.server = server
        self.error_manager = error_manager
        self.editor_context = editor_context
        self.completions = completions

        self.code_issues_subscription = self.server.code_issues \
            .where(lambda x: is_for_current_file(x)) \
            .debounce(750) \
            .subscribe(self.on_errors_received)

        self.completion_suggestions_subscription = self.server.completion_suggestions \
            .subscribe(self.on_completion_suggestions_received)

        # FIXME: ST unable to detect active view if clone of the same view exists.
        typed_member_access_operator = async_events \
            .where(lambda x: x.name == 'on_modified_async')
        typed_member_access_operator = self.configure_member_access_operator_observable(typed_member_access_operator)
        self.typed_member_access_operator_subscription = typed_member_access_operator \
            .where(lambda x, _: is_string(x, self.member_operator)) \
            .subscribe(self.on_typed_member_access_operator)

        # FIXME: ST unable to detect active view if clone of the same view exists.
        typed_call_operator = async_events \
            .where(lambda x: x.name == 'on_modified_async')
        typed_call_operator = self.configure_call_operator_observable(typed_call_operator)
        self.typed_call_operator_subscription = typed_call_operator \
            .where(lambda x, _: is_string(x, self.call_operator)) \
            .subscribe(self.on_typed_call_operator)

        file_changes = async_events \
            .where(lambda x: x.name == 'on_file_content_changed')
        file_changes = self.configure_file_changes_observable(file_changes)
        self.file_changes_subscription = file_changes \
            .subscribe(self.on_file_changed)

        post_commit_completion = async_events \
            .where(lambda x: x.name == 'on_post_commit_completion')
        post_commit_completion = self.configure_file_changes_observable(post_commit_completion)
        self.post_commit_completion_subscription = post_commit_completion \
            .subscribe(self.on_post_commit_completion)

    def configure_member_access_operator_observable(self, observable):
        return observable

    def configure_call_operator_observable(self, observable):
        return observable

    def configure_file_changes_observable(self, observable):
        return observable

    def configure_post_commit_completion_observable(self, observable):
        return observable

    def on_errors_received(self, errors):
        self.error_manager(errors)

    # TODO: add completions dep.
    def on_completion_suggestions_received(self, suggestions):
        self.completions.handler(suggestions)

    def on_typed_member_access_operator(self, event_args):
        # afford the server time to process the changes to the buffer; this will most likely
        # fail for relatively long files
        sublime.set_timeout_async(
                lambda: self.completions.send_request(event_args.data), 500)

    def on_post_commit_completion(self, event_args):
        self.editor_context.update_completion_state(event_args.data)

    def on_typed_call_operator(self, event_args):
        raise NotImplementedError()

    def on_file_changed(self, event_args):
        view = event_args.data
        self.server.update_file_content(
                view.file_name(),
                view.substr(R(0, view.size()))
                )


def is_string(args, s):
    view = args.data
    r = view.sel()[0]
    return view.substr(R(r.b - len(s), r.b)) == s
