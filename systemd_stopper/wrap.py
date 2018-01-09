import sys
import subprocess
import traceback
import logging

from systemd_stopper.waiter import WaitContext

logger = logging.getLogger('systemd_stopper')


def main():
    logging.basicConfig(level='INFO')
    pid = sys.argv[1]
    cmd = sys.argv[2:]

    waiter = WaitContext(int(pid))
    try:
        waiter.inithash()
    except Exception:
        traceback.print_exc()
        logging.warning('could not hash cmdline')

    res = subprocess.Popen(cmd)
    res.wait()

    return res.returncode


if __name__ == '__main__':
    sys.exit(main() or 0)
