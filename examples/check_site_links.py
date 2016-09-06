import argparse
import asyncio
import logging
import urllib.parse

import aiohttp
from lxml import etree

from concurrently import concurrently

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument(
    '-u', '--base-url', metavar='URL', required=True,
    help='Entry point for scan site'
)
parser.add_argument(
    '-n', '--concurrency', metavar='COUNT', type=int, default=10,
    help='Number of multiple requests to make at a time (default: 10)'
)


async def amain(base_url, concurrency, *, loop):
    pages = {base_url}

    pending_pages = asyncio.Queue()
    for page in pages:
        await pending_pages.put(page)

    @concurrently(concurrency, loop=loop)
    async def _page_parser():
        with aiohttp.ClientSession(loop=loop) as session:
            while True:
                url = await pending_pages.get()
                log = logger.getChild(url)

                log.debug('Start parsing')
                async with session.get(url) as resp:
                    log.info(
                        'Response status: %s, type: "%s", size: %s',
                        resp.status,
                        resp.headers.get('Content-Type', '(unknown)'),
                        resp.headers.get('Content-Length', '(unknown)')
                    )

                    if resp.status != 200:
                        pending_pages.task_done()
                        continue

                    body = await resp.read()
                    log.debug('Body size: %s', len(body))

                html = etree.HTML(body)
                for tag_a in html.xpath('//a/@href'):
                    next_url = urllib.parse.urljoin(url, tag_a)
                    if (
                        next_url.startswith(base_url)
                        and '?' not in next_url
                        and '#' not in next_url
                        and next_url not in pages
                    ):
                        pages.add(next_url)
                        await pending_pages.put(next_url)

                pending_pages.task_done()

    await pending_pages.join()
    await _page_parser.stop()


def main(arguments):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        amain(arguments.base_url, arguments.concurrency, loop=loop)
    )


if __name__ == '__main__':
    logging.basicConfig(
        format='%(name)s: %(message)s',
        level=logging.INFO
    )

    arguments = parser.parse_args()

    try:
        main(arguments)
    except KeyboardInterrupt:
        pass
