import abc
import json
import logging
import os
import sys
import time

from subprocess import PIPE
from subprocess import Popen
from threading import Lock
from threading import Thread

try:
    from subprocess import STARTF_USESHOWWINDOW
    from subprocess import STARTUPINFO
    from subprocess import SW_HIDE
except ImportError:
    STARTF_USESHOWWINDOW = None
    STARTUPINFO = None
    SW_HIDE = None

# from ..build.sdk import DartSdk
from .common.subprocess import kill
from .common.subprocess import ProcessReader

from rx import Observable
from rx.concurrency.schedulerbase import Scheduler
from rx.subjects import Subject

from Palantir.plugin.auto_complete import Element
from Palantir.plugin.auto_complete import CompletionSuggestion

from .plugin_lib.server import ServerWrapper
from .plugin_lib.server import request_id_generator
from .plugin_lib.server import line_reader

from Palantir.plugin_lib.errors import CodeIssue
from Palantir.plugin.palantir import Palantir
from Palantir.plugin.palantir import LanguageServer
from Palantir.plugin.palantir import PalantirConfiguration

# {'Kind': 'errors', 'Data':
# [{'StartLine': 6,
#   'Message': 'Incomplete structured construct at or before this point in pattern',
#    'StartColumn': 1,
#    'FileName': 'C:\\Users\\guill\\Documents\\Dev\\sublime-packages\\sublime-fsharp-package\\package\\src\\foo.fsx',
#    'EndColumn': 1,
#    'EndLine': 6,
#    'Subcategory': 'parse',
#    'Severity': 'Error'}]}

_this_dir_ = os.path.dirname(__file__)
_log = logging.getLogger('Palantir.Palantir_fsharp.server')


def format_error_data(errors):
    '''Adapts FSharp Server errors to ST errors.
    '''
    # TODO: display more errors. ??

    for error in errors[:100]:

        yield CodeIssue(
            # TODO: use CodeIssueSeverity.
            severity=error['Severity'].upper(),
            file=error['FileName'],
            start_line=error['StartLine'],
            start_column=error['StartColumn'],
            message=error['Message'],
            location=None
            )


def format_completion_suggestions(suggestions, *args):
    formatted = []
    for suggestion in suggestions['Data']:
        s = CompletionSuggestion()
        e = Element()
        s.completion = suggestion['ReplacementText']
        s.declaring_type = None
        s.return_type = None
        s.doc_summary = None
        e.return_type = None
        try:
            e.kind = suggestion['Glyph'].upper()
        except AttributeError:
            pass
        s.element = e
        formatted.append(s)
    return formatted


class Domains:

    def __init__(self, source, notifications, server):
        self.server = DomainServer(source, notifications)
        self.analysis = DomainAnalysis(source, notifications)
        self.completion = DomainCompletion(source, notifications, server)
        self.edit = DomainEdit(source, notifications)
        self.search = DomainSearch(source, notifications)
        self.activity = DomainActivity(source, notifications, server)


class Domain:

    def __init__(self, name, source, notifications):
        self.name = name
        self.source = source
        self._notifications = notifications

    @property
    def notifications(self):
        return self._notifications


class DomainEdit(Domain):

    def __init__(self, source, notifications):
        super().__init__('edit', source, notifications)

    def format(self, context):
        pass

    @property
    def results(self):
        return Observable.empty()


class DomainActivity(Domain):

    def __init__(self, source, notifications, server):
        super().__init__('activity', source, notifications)
        self.server = server

    def update_active_file(self, active_file_name, visible_file_names):
        # TODO: make this call accept visible_file_names too
        self.server.update_context(active_file_name)

    def update_file_content(self, file, content):
        self.server.update_file_content(file, content)

    def update_file_saved(self, file):
        pass

    def update_selections(self, selections):
        pass

    # sync call
    def on_pre_save(self, file_name):
        pass


class DomainSearch(Domain):

    def __init__(self, source, notifications):
        super().__init__('search', source, notifications)

    def go_to_definition(self, pattern):
        pass

    @property
    def results(self):
        return Observable.empty()


class DomainAnalysis(Domain):

    def __init__(self, source, notifications):
        super().__init__('analysis', source, notifications)

    @property
    def issues(self):
        return self.notifications \
                .where(lambda notif: is_kind(notif, 'errors')) \
                .select(lambda x: x['Data']) \
                .select(lambda x: list(format_error_data(x)))


class DomainCompletion(Domain):

    def __init__(self, source, notifications, server):
        super().__init__('completion', source, notifications)
        self.server = server

    @property
    def suggestions(self):
        return self.notifications \
                .where(lambda notif: is_kind(notif, 'completion')) \
                .select(format_completion_suggestions)
                # TODO: Deserialize this.

    def update(self, id):
        with self.lock:
            self._id = id

    def request_completion_suggestions(self, context):
        self.server.request_completion_suggestions(context)


class DomainServer(Domain):

    def __init__(self, source, notifications):
        super().__init__('server', source, notifications)

    @property
    def errors(self):
        return self.notifications \
                .where(lambda notif: is_kind(notif, 'errors')) \
                .select(lambda x: x['Data'])
    @property
    def infos(self):
        return self.notifications \
                .where(lambda notif: is_kind(notif, 'info')) \
                .select(lambda x: x['Data'])

    @property
    def connected(self):
        return self.notifications \
                .where(lambda notif: is_kind(notif, 'server.connected'))


def is_kind(notification, name):
    return notification['Kind'] == name


def is_domain_name(notification, name):
    return notification['event'].startswith(name + '.')


def deserialize(notification, type_):
    return type_.from_json(notification['params'])


@Palantir.register
class FSharpServerApi(LanguageServer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'fsharp'
        self.proc = None
        # Commands to be sent to Palantir.
        self.commands = None

        self.subject = Subject()

        self.out = self.subject.select(lambda x: json.loads(x))

        # TODO: Remove this when done.
        self.out.subscribe(_log.info)

        self.notifications = self.out

        self._domains = Domains(self.out, self.notifications, self)
        self._domains.server.errors \
                .subscribe(_log.error)
        self._domains.server.infos \
                .subscribe(_log.info)
        self._domains.server.connected \
                .select(lambda x: x.version) \
                .subscribe(lambda x: _log.info("Connected to Dart Analysis Server %s" % x))

    @property
    def name(self):
        return self._name

    @property
    def domains(self):
        return self._domains

    def has_support_for(self, extension):
        return extension in ('.fs', '.fsx', '.fsi')

    def update_file_content(self, file, content):
        self.send('parse "%s"' % file) # we're sending full name here
        self.send(content)
        self.send('\n<<EOF>>')

    def update_context(self, file_name):
        # if it's fsx, go ahead
        if file_name.endswith('.fsx'):
            self.do_parse(file_name)
        else:
            _log.error('unimplemented: %s', os.path.splitext(file_name)[1])

    def update_priority_files(self, included, excluded):
        pass

    def update_file_saved(self, file_name):
        pass

    def update_analysis_roots(self, data):
        pass

    def remove_file_content(self, file):
        pass

    def sleep(self):
        pass

    def awake(self, commands):
        if not self.commands:
            self.commands = commands
        config = PalantirConfiguration()
        config.member_operator= '.'
        config.call_operator= '('
        config.auto_complete_scope = 'source.fsharp'
        self.commands.update_configuration(config)
        if not self.proc:
            self.start()

    def after_awake(self):
        pass

    def after_start(self):
        pass

    @property
    def code_issues(self):
        return self.domains.analysis.errors

    def request_completion_suggestions(self, context):
        row = context['line']
        col = context['column']
        file = context['file']
        self.send_get_suggestions(file, row, col, context['line_content'])

    @property
    def completion_suggestions(self):
        return Subject()
        return self.domains.completions.suggestions

    def send(self, data):
        bytes_ = data.encode('utf8')
        self.proc.stdin.write(bytes_ + b'\n')
        self.proc.stdin.flush()

    def process_response_callbacks(self, response):
        return super().process_response_callbacks(response)

    def send_request(self, method, params, callback=None):
        self.send('xxx')

    def send_get_suggestions(self, file, row, col, line_content):
        self.send('completion "%s" "%s" %d %d' % (file, line_content, row, col))

    def suggestions_callback(self, data):
        pass

    def do_parse(self, file_name):
        self.send('parse "%s"' % file_name)
        with open(file_name, 'rt') as f:
            self.send(''.join(f.readlines()))
        self.send('\n<<EOF>>')

    def start(self, sdk=None):
        startup_info = None
        if sys.platform == 'win32':
            startup_info = STARTUPINFO()
            startup_info.dwFlags = STARTF_USESHOWWINDOW | SW_HIDE

        _log.info('Starting F# language server...')

        path = os.path.join(_this_dir_, 'fsac', 'fsac', 'fsautocomplete.exe')

        try:
            data, err = Popen(
                [path, '--version'],
                stdout=PIPE,
                startupinfo=startup_info
                ).communicate()
        except Exception as e:
            _log.error('could not retrieve server version')
            _log.error(e)
        else:
            if err:
                _log.error(err)
            else:
                version = data.decode('utf-8').strip()
                _log.info('Starting %s...' % version)

        try:
            self.proc = proc = Popen(
                    [path],
                    stdout=PIPE,
                    stdin=PIPE,
                    startupinfo=startup_info
                    )
        except Exception as e:
            _log.error('error while starting F# language server')
            _log.error(e)
            return
        else:
            t = Thread(target=line_reader, args=(self.proc.stdout, self.subject))
            t.daemon = True
            t.start()

    def stop(self):
        _log.info('stopping F# language server...')
        self.proc.stdin.close()
        self.proc.stdout.close()
        self.subject.dispose()
        _log.info('F# language server stopped.')
        self.proc = None
