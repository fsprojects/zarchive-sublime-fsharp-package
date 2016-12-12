import os
import sys
import logging

from logging import StreamHandler
from logging import Handler


_root_logger = logging.getLogger('Palantir.Palantir_fsharp')
_root_logger.setLevel(logging.INFO)
handler = StreamHandler()
handler.setLevel(logging.ERROR)
_root_logger.addHandler(handler)

_log = logging.getLogger('Palantir.Palantir_fsharp._init_')


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

from .server import FSharpServerApi
from .plugin_lib.server import ServerWrapper

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

def plugin_loaded():

    _log.info('Sublime Text Plugin for F# version %s', version_as_text)

    telemetry_events \
        .subscribe(lambda x: str(x))
        # .subscribe(send_telemetry_event)
