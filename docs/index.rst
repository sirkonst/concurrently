Concurrently
============

Library helps to easily write concurrent executed code blocks.

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
                # some function for download page
                page = await fetch_page(url)
                results[url] = page

        # wait until all concurrent threads finished
        await fetch_urls()
        print(results)


    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(amain(loop))



Decorator :func:`@concurrently` makes to main thinks:
    * starts concurrent execution specified count of decorated function
    * returns special :ref:`waiter` object to control the running functions

By default, the code runs as asyncio coroutines, but there are other supported
ways to execute, by specifying the argument `engine`.


Details
=======

.. toctree::

    waiter
    engines
