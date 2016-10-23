import sys
import os

from subprocess import call
from shutil import copytree
from shutil import rmtree

from pybuilder.core import init
from pybuilder.core import use_plugin
from pybuilder.core import task


use_plugin('python.core')
use_plugin('python.flake8')
# Not working:
# use_plugin('pypi:pybuilder_header_plugin')


_SCRIPT_DIR = os.path.dirname(__file__)

# TODO: Improve copying from subprojects. We may override clean files with stale ones
# if we copy subprojects wholesale, if those subprojects have dependencies themselves
# that are the same as deps in this project.
src_common = os.path.join(_SCRIPT_DIR, '..', 'common', 'src')
# src_build = os.path.join(_SCRIPT_DIR, '..', 'build', 'src', 'build')
src_plugin_lib = os.path.join(_SCRIPT_DIR, '..', 'plugin_lib', 'src')
# src_server = os.path.join(_SCRIPT_DIR, '..', 'analysis-server', 'src', 'server')
src_analytics = os.path.join(_SCRIPT_DIR, '..', 'analytics', 'src')
# src_rxst = os.path.join(_SCRIPT_DIR, '..', 'rxst', 'dev', 'src')

dst_common = os.path.join(_SCRIPT_DIR, 'src', 'common')
# dst_build = os.path.join(_SCRIPT_DIR, 'src', 'build')
dst_plugin_lib = os.path.join(_SCRIPT_DIR, 'src', 'plugin_lib')
# dst_server = os.path.join(_SCRIPT_DIR, 'src', 'server')
dst_analytics = os.path.join(_SCRIPT_DIR, 'src', 'analytics')
# dst_rxst = os.path.join(_SCRIPT_DIR, 'src', 'rxst')


@init
def initialize(project):
    project.version = '0.0.1'

    # project.set_property('pybuilder_header_plugin_break_build', True)
    # project.set_property('pybuilder_header_plugin_expected_header', open('header.py').read())
    project.set_property('dir_source_main_python', 'src')


@task
def get():
    """Get dependencies.
    """
    call(['mklink', '/J', dst_common, src_common], shell=True)
    # call(['mklink', '/J', dst_build, src_build], shell=True)
    call(['mklink', '/J', dst_plugin_lib, src_plugin_lib], shell=True)
    # call(['mklink', '/J', dst_server, src_server], shell=True)
    call(['mklink', '/J', dst_analytics, src_analytics], shell=True)
    # call(['mklink', '/J', dst_rxst, src_rxst], shell=True)


@task
def develop():
    """Sets up the package for development.
    """

    if sys.platform == 'win32':
        path_to_sublime_text_data = os.environ.get('SUBLIME_TEXT_DATA')
        if not path_to_sublime_text_data or not os.path.exists(path_to_sublime_text_data):
            raise ValueError('Need directory to sublime text data. Use SUBLIME_TEXT_DATA env var.')

        target = os.path.join(path_to_sublime_text_data, 'Packages', 'FSharp')
        # target_tests = os.path.join(path_to_sublime_text_data, 'Packages', 'Darttests')

        call(['mklink', '/J', target, 'src'], shell=True)
        # call(['mklink', '/J', target_tests, 'tests'], shell=True)
    else:
        raise NotImplementedError('non-windows platform')


@task
def undevelop():
    if sys.platform == 'win32':
        path_to_sublime_text_data = os.environ.get('SUBLIME_TEXT_DATA')
        if not path_to_sublime_text_data or not os.path.exists(path_to_sublime_text_data):
            raise ValueError('Need directory to sublime text data. Use SUBLIME_TEXT_DATA env var.')

        target = os.path.join(path_to_sublime_text_data, 'Packages', 'FSharp')

        os.unlink(target)
    else:
        raise NotImplementedError('non-windows platform')


@task
def clean():
    """Clean dependencies.
    """
    try:
        os.unlink(dst_common)
        # os.unlink(dst_build)
        os.unlink(dst_plugin_lib)
        # os.unlink(dst_server)
        os.unlink(dst_analytics)
        # os.unlink(dst_rxst)
    except FileNotFoundError:
        pass


@task
def noop():
    pass

# Not working:
# default_task = ['check_source_file_headers']
default_task = ['clean', 'get']
