from multiprocessing import Pipe
from threading import Thread, current_thread
import subprocess

cmds = [
    'sleep 3',
    'sleep 3',
    'sleep 5',
    'sleep 5',
    'sleep 5'
]

class Processor:
    def __init__(self):
        self._in, self._out = Pipe()
        self.threads = {}

    def start(self, cmds, proc_count):
        current_proc_count = 0
        for cmd in cmds:

            if current_proc_count < proc_count:
                current_proc_count += 1
                self.start_subprocess(cmd)
            else:
                self.cleanup_subprocess()
                self.start_subprocess(cmd)

        for _ in range(current_proc_count):
            self.cleanup_subprocess()

        print('Happy finish:)')

    def start_subprocess(self, cmd):
        th = Thread(target=self._threaded_subprocess, args=(cmd,))
        self.threads[th.name] = th
        th.start()

    def cleanup_subprocess(self):
        th_name, returncode, exception = self._out.recv()
        print(f'Recieved thread "{th_name}" with return code "{returncode}", exception "{exception}"')
        self.threads[th_name].join()


    def _threaded_subprocess(self, cmd):
        th = current_thread()
        try:
            print(f'Running cmd "{cmd}" in thread "{th.name}"')
            # 10/0
            p = subprocess.run(cmd.split())
            self._in.send((th.name, p.returncode, None))
        except Exception as e:
            self._in.send((th.name, -100, str(e)))


if __name__ == '__main__':
     p = Processor()
     p.start(cmds, 4)
