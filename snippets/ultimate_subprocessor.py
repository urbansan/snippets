import sys
import subprocess
from threading import Thread, current_thread
from queue import SimpleQueue


class Processor:
    def __init__(self, debug=False):
        self._queue = SimpleQueue()
        self.debug = debug
        self.threads = {}

    def start(self, cmds, proc_count):
        current_proc_count = 0
        for cmd in cmds:
            if current_proc_count < proc_count:
                current_proc_count += 1
                self._start_subprocess(cmd)
            else:
                self._cleanup_subprocess()
                self._start_subprocess(cmd)

        for _ in range(current_proc_count):
            self._cleanup_subprocess()

        self._log('Happy finish:)')

    def _log(self, *args):
        if self.debug:
            print(*args, file=sys.stderr)

    def _start_subprocess(self, cmd):
        th = Thread(target=self._threaded_subprocess, args=(cmd,))
        self.threads[th.name] = th
        th.start()

    def _cleanup_subprocess(self):
        th_name, returncode, exception = self._queue.get()
        self._log(f'Recieved thread "{th_name}" with return code'
                  f' "{returncode}", exception "{exception}"')
        self.threads[th_name].join()

    def _threaded_subprocess(self, cmd):
        th = current_thread()
        try:
            self._log(f'Running cmd "{cmd}" in thread "{th.name}"')
            p = subprocess.run(cmd.split())
            self._queue.put((th.name, p.returncode, None))
        except Exception as e:
            self._queue.put((th.name, -100, str(e)))


if __name__ == '__main__':
    cmds = [
        'sleep 3',
        'sleep 3',
        'sleep 5',
        'sleep 5',
        'sleep 5'
    ]

    p = Processor(debug=True)
    p.start(cmds, 4)
