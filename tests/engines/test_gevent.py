import time

import gevent  # type: ignore
import pytest  # type: ignore

from concurrently import GeventEngine, UnhandledExceptions, concurrently

from . import EngineTest, paramz_conc_count, paramz_data_count


def process(data):
    gevent.sleep(data)
    return time.monotonic()


class TestGeventEngine(EngineTest):
    @paramz_conc_count
    @paramz_data_count
    def test_concurrently(self, conc_count, data_count):
        data = range(data_count)
        i_data = iter(data)
        results = {}
        start_time = time.monotonic()

        @concurrently(conc_count, engine=GeventEngine)
        def _parallel():
            for d in i_data:
                res = process(d)
                results[d] = res

        _parallel()

        def calc_delta(n):
            if n // conc_count == 0:
                return n
            return n + calc_delta(n - conc_count)

        assert len(results) == data_count
        for n, v in results.items():
            delta = v - start_time
            assert int(delta) == calc_delta(n)

    def test_stop(self):
        data = range(3)
        i_data = iter(data)
        results = {}
        start_time = time.monotonic()

        @concurrently(2, engine=GeventEngine)
        def _parallel():
            for d in i_data:
                r = process(d)
                results[d] = r

        gevent.sleep(0.5)
        _parallel.stop()

        assert len(results) == 1
        assert int(results[0]) == int(start_time)

    def test_exception(self):
        data = range(2)
        i_data = iter(data)

        @concurrently(2, engine=GeventEngine)
        def _parallel():
            for d in i_data:
                if d == 1:
                    raise RuntimeError()

        with pytest.raises(UnhandledExceptions) as exc:
            _parallel()

        assert len(exc.value.exceptions) == 1
        assert isinstance(exc.value.exceptions[0], RuntimeError)

    def test_exception_suppress(self):
        data = range(2)
        i_data = iter(data)
        results = {}
        start_time = time.monotonic()

        @concurrently(2, engine=GeventEngine)
        def _parallel():
            for d in i_data:
                if d == 1:
                    raise RuntimeError()
                res = process(d)
                results[d] = res

        _parallel(suppress_exceptions=True)

        assert len(results) == 1
        assert int(results[0]) == int(start_time)

        exc_list = _parallel.exceptions()
        assert len(exc_list) == 1
        assert isinstance(exc_list[0], RuntimeError)

    def test_fail_hard(self):
        i_data = iter(range(4))
        results = {}

        @concurrently(3, engine=GeventEngine)
        def _parallel():
            for d in i_data:
                if d == 1:
                    raise RuntimeError()
                gevent.sleep(d)
                results[d] = True

        gevent.sleep(0.1)

        with pytest.raises(RuntimeError):
            _parallel(fail_hard=True)

        assert len(results) == 1
        assert results[0]
