import argparse
import logging
import os
import hashlib
import time

from systemd_stopper import resolve_signal

logger = logging.getLogger('systemd_stopper')


class WaitContext:
    def __init__(self, pid, sleep_interval=0.1, cmdhash=None):
        self.pid = pid
        self.sleep_interval = sleep_interval
        self.cmdhash = cmdhash
        self.permission_denied_implies_exit = True

    def wait(self):
        while self._wait_iteration():
            time.sleep(self.sleep_interval)

    def inithash(self):
        self.cmdhash = self.gethash()

    def try_inithash(self):
        try:
            self.inithash()
        except Exception:
            logger.exception('could not get cmdline hash for pid {}'.format(self.pid))

    def gethash(self):
            with open('/proc/{:d}/cmdline'.format(self.pid), 'rb') as fd:
                cmdline = fd.read()
            cmdhash = hashlib.sha1(cmdline).digest()
            return cmdhash

    def _wait_iteration(self):
        try:
            # If we arrive here, a process with the given pid is running.
            # Since cmdline could be large, we compute its hash.
            cmdhash = self.gethash()

            if self.cmdhash is None:
                # We can rather safely assume that the running process is
                # indeed the unit that is to be stopped by systemd.
                # That the same pid is reused with exactly the same command line
                # for another process is unlikely, because it requires the unit
                # to have died (unexpectedly) *after* ExecStop is called by
                # systemd and before this code block is reached, which should
                # be a sufficiently small amount of time.
                self.cmdhash = cmdhash
            elif self.cmdhash != self.cmdhash:
                # We assume that the unit has died when the command line changes.
                # The worst thing that could happen is that the MAINPID of unit
                # uses an exec* syscall as a normal means of operation or
                # termination (which seems like a very strange pattern) and is
                # in fact still running. In that case, systemd_stopper may
                # return before the legitimate MAINPID has exited gracefully and
                # systemd will kill it by force.
                logger.info('pid {} was replaced with another cmdline'.format(self.pid))
                return False

            return True

        except PermissionError:
            # If we do not have permissions to read the cmdline, we assume that
            # the MAINPID process has been replaced and the unit has exited.
            return self.permission_denied_implies_exit
        except FileNotFoundError:
            return False
        except IOError:
            logger.warning()
            return False


def main(**kwargs):
    args = parse_args(**kwargs)

    flag_map = {
        'wait': (False, True),
        'kill-wait': (True, True),
        'kill': (True, False),
        }

    sig = resolve_signal(args.signal)
    do_kill, do_wait = flag_map[args.action]

    waiter = WaitContext(args.pid)
    waiter.try_inithash()

    if do_kill:
        logger.info('sending signal {} to pid {}'.format(sig, args.pid))
        os.kill(args.pid, sig)

    if do_wait:
        logger.info('waiting for {}'.format(args.pid))
        waiter.wait()
        logger.info('pid {} assumed to have died'.format(args.pid))


def parse_args(**kwargs):
    p = argparse.ArgumentParser(prog='systemd_stopper')
    p.add_argument('action', choices=['wait', 'kill-wait', 'kill'])
    p.add_argument('pid', type=int)
    p.add_argument('--signal', '-s', default='TERM', help='The signal to stop the main pid')
    return p.parse_args(**kwargs)


if __name__ == '__main__':
    main()
