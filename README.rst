Concurrently
============

Library helps to easily write concurrent executed code blocks.

Quick example:

.. code-block:: python

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


Decorator `@concurrently` makes to main thinks:
    * starts concurrent execution specified count of decorated function
    * returns special `waiter` object to control the running functions

By default, the code runs as asyncio coroutines, but there are other supported
ways to execute, by specifying the argument `engine`.


Documentation
-------------

See https://concurrently.readthedocs.io/


Requirements
============

Now support only **Python 3.5** and above.


Install
=======

From PyPi:

.. code-block:: bash

    $ pip install concurrently


From local:

.. code-block:: bash

    # update setuptools
    $ pip install 'setuptools >= 30.4'
    # do install
    $ make install
    # or
    $ pip install .


Development
===========

Prepare and activate virtual environment like:

.. code-block:: bash

    $ python3 -m venv .env
    # for bash
    $ source .env/bin/activate
    # for fish
    $ . .env/bin/activate.fish

Update pre-install dependencies:

.. code-block:: bash

    $ pip install 'setuptools >= 30.4'

Install:

.. code-block:: bash

    $ make install_dev
    # or
    $ pip install --editable .[develop]

Run tests:

.. code-block:: bash

    $ make test
    # or
    $ pytest tests/
