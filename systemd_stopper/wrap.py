import sys
import subprocess
import traceback
import logging

from systemd_stopper.waiter import WaitContext

logger = logging.getLogger('systemd_stopper')


def main():
    logging.basicConfig(level='DEBUG')
    pid = int(sys.argv[1])
    cmd = sys.argv[2:]

    waiter = WaitContext(int(pid))
    try:
        waiter.inithash()
    except Exception:
        traceback.print_exc()
        logging.warning('could not hash cmdline')

    logger.debug('executing and waiting for cmd: ' + (' ').join(cmd))
    res = subprocess.Popen(cmd)
    res.wait()
    logger.debug('cmd returned with %d', res.returncode)
    
    logger.debug('waiting for pid %d to return...', pid)
    waiter.wait()

    logger.debug('...done')
    return res.returncode


if __name__ == '__main__':
    sys.exit(main() or 0)
