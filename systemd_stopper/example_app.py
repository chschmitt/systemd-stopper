import os
import time
import logging

import systemd_stopper


def main():
    logging.basicConfig(level='DEBUG')

    logging.info('PID: %d', os.getpid())
    stopper = systemd_stopper.install().ignore('HUP')

    i = 0
    while stopper.run:
        i += 1
        logging.info('sleep iteration %d', i)
        time.sleep(1)

    logging.info('loop was left gracefully')


if __name__ == '__main__':
    main()
