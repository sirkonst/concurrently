import asyncio
import time
from queue import Queue

import pytest

from concurrently import concurrently, AsyncIOThreadEngine, UnhandledExceptions

from . import EngineTest, paramz_conc_count, paramz_data_count


def process(data):
    time.sleep(data)
    return time.time()


class TestAsyncIOThreadEngine(EngineTest):

    @pytest.mark.asyncio(forbid_global_loop=True)
    @paramz_conc_count
    @paramz_data_count
    async def test_concurrently(self, conc_count, data_count, event_loop):
        data = range(data_count)
        q_data = Queue()
        for d in data:
            q_data.put(d)
        q_results = Queue()
        start_time = time.time()

        @concurrently(conc_count, engine=AsyncIOThreadEngine, loop=event_loop)
        def _parallel():
            while not q_data.empty():
                d = q_data.get()
                res = process(d)
                q_results.put({d: res})

        await _parallel()

        results = {}
        while not q_results.empty():
            results.update(q_results.get())

        def calc_delta(n):
            if n // conc_count == 0:
                return n
            return n + calc_delta(n - conc_count)

        assert len(results) == data_count
        for n, v in results.items():
            delta = v - start_time
            assert int(delta) == calc_delta(n)

    @pytest.mark.asyncio(forbid_global_loop=True)
    async def test_stop(self, event_loop):
        data = range(3)
        i_data = iter(data)
        results = {}
        start_time = time.time()

        @concurrently(2, engine=AsyncIOThreadEngine, loop=event_loop)
        def _parallel():
            for d in i_data:
                r = process(d)
                results[d] = r

        await asyncio.sleep(0.5, loop=event_loop)
        await _parallel.stop()

        assert len(results) == 1
        assert int(results[0]) == int(start_time)

    @pytest.mark.asyncio(forbid_global_loop=True)
    async def test_exception(self, event_loop):
        data = range(2)
        i_data = iter(data)

        @concurrently(2, engine=AsyncIOThreadEngine, loop=event_loop)
        def _parallel():
            for d in i_data:
                if d == 1:
                    raise RuntimeError()

        with pytest.raises(UnhandledExceptions) as exc:
            await _parallel()

        assert len(exc.value.exceptions) == 1
        assert isinstance(exc.value.exceptions[0], RuntimeError)

    @pytest.mark.asyncio(forbid_global_loop=True)
    async def test_exception_suppress(self, event_loop):
        data = range(2)
        i_data = iter(data)
        results = {}
        start_time = time.time()

        @concurrently(2, engine=AsyncIOThreadEngine, loop=event_loop)
        def _parallel():
            for d in i_data:
                if d == 1:
                    raise RuntimeError()
                res = process(d)
                results[d] = res

        await _parallel(suppress_exceptions=True)

        assert len(results) == 1
        assert int(results[0]) == int(start_time)

        exc_list = _parallel.exceptions()
        assert len(exc_list) == 1
        assert isinstance(exc_list[0], RuntimeError)

    @pytest.mark.asyncio(forbid_global_loop=True)
    async def test_fail_hard(self, event_loop):
        i_data = iter(range(4))
        results = {}

        @concurrently(3, engine=AsyncIOThreadEngine, loop=event_loop)
        def _parallel():
            for d in i_data:
                if d == 1:
                    raise RuntimeError()
                time.sleep(d)
                results[d] = True

        with pytest.raises(RuntimeError):
            await _parallel(fail_hard=True)

        assert len(results) == 1
        assert results[0]

    @pytest.mark.asyncio(forbid_global_loop=True)
    async def test_decorated_fn_is_not_coroutine(self, event_loop):
        with pytest.raises(AssertionError) as e:
            @concurrently(1, engine=AsyncIOThreadEngine, loop=event_loop)
            async def _coroutine():
                pass

        assert str(e.value) == \
            'Decorated function `_coroutine` must be regular not a coroutine'
