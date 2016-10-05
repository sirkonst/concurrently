.. _waiter:

Waiter
======

The :func:`@concurrently` returns special object :class:`Waiter` to control the
running functions, like a wait until complete, stop and other.


.. autoclass:: concurrently.engines.AbstractWaiter
    :members: __call__, stop, exceptions


UnhandledExceptions
-------------------

.. autoexception:: concurrently.UnhandledExceptions
