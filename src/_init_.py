import os
import sys
import logging

from logging import StreamHandler
from logging import Handler


_root_logger = logging.getLogger('FSharp')
_root_logger.setLevel(logging.INFO)
handler = StreamHandler()
handler.setLevel(logging.ERROR)
_root_logger.addHandler(handler)

_log = logging.getLogger(__name__)


# Load rx library
from rxst import _init_

import sublime

from rx.subjects import Subject

from .analytics.ga import GaEvent
from .analytics.ga import GaService
from .analytics.ga import UserAgent

from .plugin_lib.auto_complete import Completions
from .plugin_lib.editor_context import EditorContext
from .plugin_lib.panels import OutputPanel
from .plugin_lib.panels import OutputPanelConfiguration
from .plugin_lib.panels import SublimeTextOutputPanelApi
from .plugin_lib.errors import CodeIssueManager
from .plugin_lib.errors import CodeIssueManagerConfiguration
from .plugin_lib.errors import SublimeTextCodeIssueManagerApi

from .common.di import features
from .common.path import truncate_at_home

# from .server.server import Server
# from .server.server import ServerApi
# from .server.server import ServerWrapper

# from .plugin.sdk import discover_sdk
from ._version_ import version_as_text


telemetry_events = Subject()

agent = UserAgent('ST-F#-Plugin', '2.0', None, None)
telemetry_service = GaService('UA-55288482-1', agent)


def send_telemetry_event(data):
    event = GaEvent(
        data['category'],
        data['action'],
        data['label'],
        data['value']
        )
    sublime.set_timeout_async(
            lambda: telemetry_service.send_event(event.to_dict()), 0)


features.add('telemetry_events', telemetry_events)
features.add('editor_context', EditorContext())

# Working around API loading in ST (not available until after plugin_loaded() has exited).
# features.add('sdk', Exception('workaround for ST API loading'))
features.add('error_manager', Exception('workaround for ST API loading'))
# features.add('server', ServerWrapper(api=Server()))
# features.add('completions', Completions(features.features['server']))


class LogPanelHandler(Handler):
    '''A logging handler that logs to an OutputPanel.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configuration = OutputPanelConfiguration()
        configuration.name = 'fsharp.log'
        configuration.settings = [
                ('syntax', 'Packages/FSharp/Support/Dart Log Output.sublime-syntax'),
                ]

        self.panel = OutputPanel(
                api=SublimeTextOutputPanelApi(),
                configuration=configuration)

    def emit(self, record):
        self.panel.write(self.format(record) + '\n')


def set_up_logger():
    formatter = logging.Formatter(
            "[%(levelname)s] - %(asctime)s - %(name)s - %(message)s")
    handler = LogPanelHandler()
    handler.setFormatter(formatter)
    _root_logger.addHandler(handler)


def plugin_loaded():
    set_up_logger()

    _log.info('Sublime Text Plugin for F# version %s', version_as_text)

    # sdk = discover_sdk()
    # if not sdk:
        # _log.error('No Dart SDK could be autodiscovered. Aborting plugin initialization.')
        # features.features.clear()
        # return

    # del features.features['sdk']
    # features.add('sdk', sdk)

    def make_error_manager():
        configuration = CodeIssueManagerConfiguration()
        configuration.key = 'fsharp.errors'
        configuration.settings = [
            ('syntax', 'Packages/FSharp/Support/FSharp Analysis Output.tmLanguage'),
            ]
        return CodeIssueManager(
                api=SublimeTextCodeIssueManagerApi(configuration=configuration),
                issue_types=['ERROR', 'WARNING', 'INFO'],
                )

    del features.features['error_manager']
    features.add('error_manager', make_error_manager)

    # _log.info('Using dart SDK at %s', os.path.dirname(truncate_at_home(sdk.dart_path)))

    # features.features['server'].start(sdk)

    telemetry_events \
        .subscribe(lambda x: str(x))
        # .subscribe(send_telemetry_event)
