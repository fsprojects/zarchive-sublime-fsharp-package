import json
import logging
import os
import queue
import threading

from FSharp.subtrees.plugin_lib.plat import is_windows

from .pipe_server import PipeServer


PATH_TO_FSAC = os.path.join(os.path.dirname(__file__),
                            'fsac/fsautocomplete.exe')

# Incoming requests from client (plugin).
requests_queue = queue.Queue()
# Outgoing responses from FsacServer.
responses_queue = queue.Queue()
# Special response queue for completions.
# Completions don't ever hit the regular `responses_queue`.
completions_queue = queue.Queue()
# Internal queue to orchestrate thread termination, etc.
_internal_comm = queue.Queue()

STOP_SIGNAL = '__STOP'

_logger = logging.getLogger(__name__)


def request_reader(requests, server, internal_msgs=_internal_comm):
    '''Reads requests from @requests and forwards them to @server.

    @requests
      A queue of requests.
    @server
      `FsacServer` instance.
    @internal_msgs
      A queue of internal messages for orchestration.
    '''
    while True:
        try:
            request = requests.get(block=True, timeout=5)

            try:
                # have we been asked to do anything?
                if internal_msgs.get(block=False) == STOP_SIGNAL:
                    _logger.info('asked to exit; complying')
                    internal_msgs.put(STOP_SIGNAL)
                    break
            except queue.Empty:
                pass
            except Exception as e:
                _logger.error('unhandled exception: %s', e)
                # improve stack trace
                raise

            if not request:
                # Requests should always be valid, so log this but keep
                # running; most likely it isn't pathological.
                _logger.error('unexpected empty request: %s', request)
                continue

            _logger.debug('reading request: %s', request[:140])
            server.fsac.proc.stdin.write(request)
            server.fsac.proc.stdin.flush()
        except queue.Empty:
            continue
        except Exception as e:
            _logger.error('unhandled exception: %s', e)
            raise

    _logger.info("request reader exiting...")


def response_reader(responses, server, internal_msgs=_internal_comm):
    '''Reads requests from @server and forwards them to @responses.

    @responses
      A queue of responses.
    @server
      `PipeServer` instance wrapping `fsautocomplete.exe`.
    @internal_msgs
      A queue of internal messages for orchestration.
    '''
    while True:
        try:
            data = server.fsac.proc.stdout.readline()
            if not data:
                _logger.debug('no data; exiting')
                break

            try:
                # Have we been asked to do anything?
                if internal_msgs.get(block=False) == STOP_SIGNAL:
                    print('asked to exit; complying')
                    internal_msgs.put(STOP_SIGNAL)
                    break
            except queue.Empty:
                pass
            except Exception as e:
                _logger.error('unhandled exception: %s', e)
                raise

            _logger.debug('reading response: %s', data[:140])
            # TODO: if we're decoding here, .put() the decoded data.
            data_json = json.loads(data.decode('utf-8'))
            if data_json['Kind'] == 'completion':
                completions_queue.put(data)
                continue

            responses.put(data)
        except queue.Empty:
            continue
        except Exception as e:
            _logger.error('unhandled exception: %s', e)
            raise

    _logger.info("response reader exiting...")


class FsacServer(object):
    '''Wraps `fsautocomplete.exe`.
    '''
    def __init__(self, cmd):
        '''
        @cmd
          A command line as a list to start fsautocomplete.exe.
        '''
        fsac = PipeServer(cmd)
        fsac.start()
        fsac.proc.stdin.write('outputmode json\n'.encode('ascii'))
        fsac.proc.stdin.flush()
        self.fsac = fsac

        threading.Thread(
                target=request_reader, args=(requests_queue, self)).start()
        threading.Thread(
                target=response_reader, args=(responses_queue, self)).start()

    def stop(self):
        self._internal_comm.put(STOP_SIGNAL)
        self.fsac.stop()


def start(path=PATH_TO_FSAC):
    '''Starts a `FsacServer`.

    Returns a `PipeServer`.

    @path
     Path to `fsautocomplete.exe`.
    '''
    args = [path] if is_windows() else ['mono', path]
    return FsacServer(args)
