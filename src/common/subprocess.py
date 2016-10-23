import sys
import subprocess as sp

from subprocess import Popen
from subprocess import PIPE
from subprocess import STARTUPINFO
from threading import Thread

try:
    from subprocess import STARTUPINFO
    from subprocess import STARTF_USESHOWWINDOW
    from subprocess import SW_HIDE
except ImportError:
    STARTUPINFO = None
    STARTF_USESHOWWINDOW = None
    SW_HIDE = None


class ProcessReader(Thread):

    def __init__(self, stream, on_data=None, on_completed=None, buffer_size=1024*3):
        super().__init__()
        self.stream = stream
        self.on_data = on_data
        self.on_completed = on_completed
        self.buffer_size = buffer_size

    def start(self):
        count = self.buffer_size
        line_buffer = []
        while True:
            data = self.stream.read(count)
            if not data:
                self.stream.close()
                if self.on_completed:
                    self.on_completed()
                return
            if self.on_data:
                if self.buffer_size == 1 and data == b'\n':
                    line_buffer.append(data)
                    data = b''.join(line_buffer)
                    line_buffer.clear()
                elif self.buffer_size == 1:
                    line_buffer.append(data)
                    continue
                self.on_data(data)


class ProcessManager(object):

    def __init__(self, args, on_data=None, on_completed=None, buffer_size=1024*3):
        self.args = args
        self.on_data = on_data
        self.on_completed = on_completed
        self.proc = None
        self.buffer_size = buffer_size

    def start(self, **kwargs):
        startup_info = None
        if sys.platform == 'win32':
            startup_info = STARTUPINFO()
            startup_info.dwFlags = STARTF_USESHOWWINDOW | SW_HIDE
        self.proc = Popen(self.args, stdout=PIPE, stderr=PIPE, startupinfo=startup_info, **kwargs)

        def do_start():
            out = ProcessReader(self.proc.stdout, self.on_data, buffer_size=self.buffer_size)
            err = ProcessReader(self.proc.stderr, self.on_data, buffer_size=self.buffer_size)
            out.start()
            err.start()
            if out.is_alive():
                out.join()
            if err.is_alive():
                err.join()
            # Avoid duplicating call to .on_completed() by moving it here and out
            # of the reader threads.
            if self.on_completed:
                self.on_completed()

        worker = Thread(target=do_start)
        worker.start()

    def wait(self, timeout=None):
        self.proc.wait(timeout)

    def kill(self):
        self.proc.kill()


def check_output(args, shell=False, universal_newlines=False, timeout=None):
    """Reads a process' output. On Windows, it supresses the console window.
    """

    if not sys.platform == 'win32':
        return sp.check_output(args, shell=shell, universal_newlines=universal_newlines, timeout=timeout)

    startup_info = STARTUPINFO()
    startup_info.dwFlags = STARTF_USESHOWWINDOW | SW_HIDE

    proc = Popen(args, stdout=PIPE, stderr=PIPE, shell=shell, universal_newlines=universal_newlines,
                 startupinfo=startup_info)
    data, err = proc.communicate(timeout=timeout)

    return data or err


def kill(proc):
    if sys.platform == 'win32':
        startup_info = STARTUPINFO()
        startup_info.dwFlags = STARTF_USESHOWWINDOW | SW_HIDE
        sp.call(['taskkill', '/PID', str(proc.pid)], startupinfo=startup_info)
    else:
        proc.kill()
