.. -*- mode: rst -*-

.. image:: https://travis-ci.org/sirkonst/concurrently.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/sirkonst/concurrently

.. image:: https://coveralls.io/repos/github/sirkonst/concurrently/badge.svg?branch=master
    :alt: Code Coverage
    :target: https://coveralls.io/github/sirkonst/concurrently?branch=master

Concurrently
============

Library helps easy write concurrent executed code blocks.

Quick example::

    import asyncio
    from concurrently import concurrently


    async def amain(loop):
        """
        How to fetch some web pages with concurrently.
        """
        urls = [  # define pages urls
            'http://test/page_1',
            'http://test/page_2',
            'http://test/page_3',
            'http://test/page_4',
        ]
        results = {}

        # immediately run wrapped function concurrent
        # in 2 thread (asyncio coroutines)
        @concurrently(2)
        async def fetch_urls():
            for url in urls:
                page = await fetch_page(url)  # some function for download page
                results[url] = page

        # wait until all concurrent threads finished
        await fetch_urls()
        print(results)


    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(amain(loop))


``Concurrently`` supports specific different concurrent engines.

Engines
=======

AsyncIOEngine
-------------

Default engine for concurrently run code as asyncio coroutines::

    from concurrently import concurrently, AsyncIOEngine

    ...
    @concurrently(2, engine=AsyncIOEngine, loop=loop)  # loop is option
    async def fetch_urls():
        ...

    await fetch_urls()


AsyncIOExecutorEngine
---------------------

Concurrently run code by asyncio executor::

    from concurrent.futures import ThreadPoolExecutor
    from concurrently import concurrently, AsyncIOExecutorEngine

    ...
    my_pool = ThreadPoolExecutor()

    @concurrently(2, engine=AsyncIOExecutorEngine, loop=loop, executor=my_pool)
    def fetch_urls():  # not async def
        ...

    await fetch_urls()

If ``executor`` is ``None`` or not set will using default asyncio executor.

Note: ``ProcessPoolExecutor`` is not supported.


ThreadEngine
------------

Concurrently run code in system threads::

    from concurrently import concurrently, ThreadEngine

    ...
    @concurrently(2, engine=ThreadEngine)
    def fetch_urls():  # not async def
        ...

    fetch_urls()  # not await


ThreadPoolEngine
----------------

Concurrently run code in system threads by use ``concurrent.futures.ThreadPoolExecutor``::

    from concurrent.futures import ThreadPoolExecutor
    from concurrently import concurrently, ThreadPoolEngine

    ...
    pool = ThreadPoolExecutor()

    @concurrently(2, engine=ThreadPoolEngine, pool=pool)
    def fetch_urls():
        ...

    fetch_urls()

``pool`` is option for specifying custom pool otherwise will using default pool.

Note: with this engine ``stop()`` is not work correctly.


ProcessEngine
-------------

Concurrently run code in system process::

    from concurrently import concurrently, ProcessEngine

    ...
    @concurrently(2, engine=ProcessEngine)
    def fetch_urls():
        ...

    fetch_urls()
