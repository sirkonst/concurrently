import asyncio
import time

import pytest

from concurrently import concurrently, AsyncIOEngine


async def process(data, *, loop):
    await asyncio.sleep(data, loop=loop)
    return time.time()


@pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.parametrize(
    'conc_count', range(1, 5), ids=lambda v: 'counc %s' % v
)
@pytest.mark.parametrize(
    'data_count', range(1, 5), ids=lambda v: 'data %s' % v
)
async def test_concurrently(conc_count, data_count, event_loop):
    data = range(data_count)
    i_data = iter(data)
    results = {}
    start_time = time.time()

    @concurrently(conc_count, engine=AsyncIOEngine, loop=event_loop)
    async def _parallel():
        for d in i_data:
            res = await process(d, loop=event_loop)
            results[d] = res

    await _parallel()

    def calc_delta(n):
        if n // conc_count == 0:
            return n
        return n + calc_delta(n - conc_count)

    assert len(results) == data_count
    for n, v in results.items():
        delta = v - start_time
        assert int(delta) == calc_delta(n)


@pytest.mark.asyncio(forbid_global_loop=True)
async def test_stop(event_loop):
    data = range(3)
    i_data = iter(data)
    results = {}
    start_time = time.time()

    @concurrently(2, engine=AsyncIOEngine, loop=event_loop)
    async def _parallel():
        for d in i_data:
            r = await process(d, loop=event_loop)
            results[d] = r

    await asyncio.sleep(0.5, loop=event_loop)
    await _parallel.stop()

    assert len(results) == 1
    assert int(results[0]) == int(start_time)


@pytest.mark.asyncio(forbid_global_loop=True)
async def test_exception(event_loop):
    data = range(2)
    i_data = iter(data)
    results = {}
    start_time = time.time()

    @concurrently(2, engine=AsyncIOEngine, loop=event_loop)
    async def _parallel():
        for d in i_data:
            if d == 1:
                raise RuntimeError()
            res = await process(d, loop=event_loop)
            results[d] = res

    await _parallel()

    assert len(results) == 1
    assert int(results[0]) == int(start_time)

    exc_list = _parallel.exceptions()
    assert len(exc_list) == 1
    assert isinstance(exc_list[0], RuntimeError)
