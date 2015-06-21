# We don't use __init__.py because ST & Python load the file twice and two
# instances of fsautocomplete are started.

import logging

from FSharp import PluginLogger
from FSharp.lib.editor import Editor
from FSharp.lib.response_processor import process_resp


logger = PluginLogger(__name__)

logger.debug('starting editor context...')

editor_context = None
editor_context = Editor(process_resp)


def plugin_unloaded():
    editor_context.fsac.stop()
