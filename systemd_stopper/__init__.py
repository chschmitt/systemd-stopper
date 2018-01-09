import signal
import argparse
import logging
import threading
import os
import time

logger = logging.getLogger('systemd_stopper')


def resolve_signal(name):
    try:
        return getattr(signal, 'SIG{}'.format(name.upper()))
    except AttributeError:
        raise ValueError('could not resolve signal {}'.format(name))


def ignore_signal(name):
    signal.signal(resolve_signal(name), signal.SIG_IGN)


def ignore_int():
    ignore_signal('int')


def ignore_hup():
    ignore_signal('hup')


class StopperBase:
    def set_stop_flag(self):
        raise NotImplementedError

    def handle(self, signal, frame):
        logger.info('received signal {}'.format(signal))
        self.set_stop_flag()

    def ignore(self, *signals):
        for s in signals:
            ignore_signal(s)
        return self

    def install(self, *signals):
        if not signals:
            signals = [signal.SIGTERM, signal.SIGINT]
        else:
            signals = [resolve_signal(sig) for sig in signals]

        current = []
        for sig in signals:
            logger.info('installing handler for signal {}'.format(sig))
            current.append(signal.signal(sig, self.handle))
        return current

    @property
    def run(self):
        return not self.stop

    @classmethod
    def create_and_install(cls, *signals, **stopper_args):
        stopper = cls(**stopper_args)
        stopper.install(*signals)
        return stopper


class SimpleStopper(StopperBase):
    def __init__(self):
        self.stop = False

    def set_stop_flag(self):
        self.stop = True


class EventStopper(StopperBase):
    def __init__(self):
        self.event = threading.Event()

    def set_stop_flag(self):
        self.event.set()

    @property
    def stop(self):
        return self.event.is_set()


class CallbackStopper(EventStopper):
    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback

    def set_stop_flag(self):
        fire_callback = self.run
        super().set_stop_flag()
        if fire_callback and self.callback is not None:
            self.callback()


_singleton_lock = threading.Lock()
_stoppers = []


def current():
    with _singleton_lock:
        if not _stoppers:
            return None
        else:
            return _stoppers[-1]


def install(*signals, check_multiple_invocation='error', **kwargs):
    type = kwargs.pop('type', 'callback')
    callback = kwargs.get('callback', None)

    if callback is not None and type != 'callback':
        raise ValueError('stopper type {} requires callback to be None'.format(type))

    with _singleton_lock:
        stopper_present = bool(_stoppers)

    if stopper_present:
        message = (
            'Another stopper has already been installed. '
            'You should call systemd_stopper.install() only once and keep a '
            'reference to the result. '
            'Alternatively, you can use systemd_stopper.current() to get the '
            'latest stopper.'
            )
        if check_multiple_invocation == 'error':
            raise ValueError(message)
        elif check_multiple_invocation == 'warning':
            logger.warning(message)
        else:
            raise ValueError(
                'unknown value for check_multiple_invocation: {}'.format(
                    check_multiple_invocation))

    typemap = dict(
        simple=SimpleStopper,
        event=EventStopper,
        callback=CallbackStopper)

    cls = typemap[type]
    stopper = cls.create_and_install(*signals, **kwargs)

    with _singleton_lock:
        _stoppers.append(stopper)

    return stopper
