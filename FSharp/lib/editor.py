# Copyright (c) 2014, Guillermo López-Anglada. Please see the AUTHORS file for details.
# All rights reserved. Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.)

import os
import logging
import threading

import sublime

from FSharp.fsac import server
from FSharp.fsac.client import FsacClient
from FSharp.fsac.request import CompilerLocationRequest
from FSharp.fsac.request import ParseRequest
from FSharp.fsac.request import ProjectRequest
from FSharp.lib import response_processor
from FSharp.lib.project import FSharpFile
from FSharp.lib.project import FSharpProjectFile
from FSharp.lib.response_processor import ON_COMPILER_PATH_AVAILABLE
from FSharp.lib.response_processor import ON_ERRORS_AVAILABLE


_logger = logging.getLogger(__name__)


class Editor(object):
    """Global editor state.
    """
    def __init__(self, resp_proc):
        _logger.info ('Starting F# language services...')

        self.fsac = FsacClient(server.start(), resp_proc)

        self.compilers_path = None
        self.project_file = None

        self._errors = []

        self.fsac.send_request(CompilerLocationRequest())
        # todo: register as decorator instead?
        response_processor.add_listener(ON_COMPILER_PATH_AVAILABLE,
                                        self.on_compiler_path_available)

        response_processor.add_listener(ON_ERRORS_AVAILABLE,
                                        self.on_errors_available)

        self._write_lock = threading.Lock()

    def on_compiler_path_available(self, data):
        self.compilers_path = data['response'].compilers_path

    def on_errors_available(self, data):
        self.errors = data['response']['Data']

    @property
    def errors(self):
        with self._write_lock:
            return self._errors

    @errors.setter
    def errors(self, value):
        assert isinstance(value, list), 'bad call'
        with self._write_lock:
            self._errors = value

    @property
    def compiler_path(self):
        if self.compilers_path is None:
            return
        return os.path.join(self.compilers_path, 'fsc.exe')

    @property
    def interpreter_path(self):
        if self.compilers_path is None:
            return None
        return os.path.join(self.compilers_path, 'fsi.exe')

    def refresh(self, fs_file):
        assert isinstance(fs_file, FSharpFile), 'wrong argument: %s' % fs_file
        # todo: run in alternate thread

        if fs_file.is_script_file:
            return

        if not self.project_file or not self.project_file.governs(fs_file.path):
            self.project_file = FSharpProjectFile.from_path(fs_file.path)

            if not self.project_file:
                _logger.info('could not find an .fsproject file for %s' % fs_file)
                return

            self.set_project()
            return

    def set_project(self):
        self.fsac.send_request(ProjectRequest(self.project_file.path))

    def parse_file(self, fs_file, content):
        self.fsac.send_request(ParseRequest(fs_file.path, content))

    def parse_view(self, view):
        # todo: what about unsaved files?
        fs_file = FSharpFile(view)
        if not fs_file.is_fsharp_file:
            return
        self.refresh(fs_file)
        # todo: very inneficient
        if fs_file.is_code:
            content = view.substr(sublime.Region (0, view.size()))
            self.parse_file(fs_file, content)
