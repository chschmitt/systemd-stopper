systemd-stopper
===============

``systemd-stopper`` is a small library for conveniently handling the ``systemctl stop`` operation in Python application running as ``systemd`` units. Since running a Python process with ``systemd`` is simple, handling the stop command should be simple as well. 

Quickstart
----------

Consider the following unit-file defining ``my_app.service``::

    [Unit]
    Description=Cool Python Unit
    After=network.target
    
    [Service]
    ExecStart=/usr/bin/python3 /home/user/my_app.py
    KillMode=Process
    
    [Install]
    WantedBy=multi-user.target


To stop the application gracefully via ``systemctl stop my_app``, we have to implement a signal handler for the ``SIGTERM`` signal. Using the ``signal`` module from the standard library directly is a bit low-level, escpecially if your application is multithreaded or if you have to implement the signal handling in multiple applications.

``systemd-stopper`` lets you handle the stop event straightforward, for example in an application with a simple main loop::

    import systemd_stopper
    stopper = systemd_stopper.install()
    while stopper.run:
        do_stuff()
    handle_graceful_shutdown()

The ``install()`` function sets up the signal handlers and returns a ``Stopper`` object to query the status of the stop command. You have multiple options::

    # Use other signals for stopping the application.
    stopper = systemd_stopper.install('USR1', 'HUP')
    
    # Wait for a threading.Event instead of polling the run attribute.
    stopper.event.wait() # returns when the stop signal has been receive
    
    # Use a callback function that gets called exactly once, which is useful
    # for single-threaded IO loops like those of tornado or asyncio
    ioloop = framework_of_choice.get_io_loop()
    systemd_stopper.install(callback=ioloop.stop)
    

Installation
------------

``pip install systemd-stopper``


Further documentation
---------------------

Further documentation will be added when I have the time to write it.
