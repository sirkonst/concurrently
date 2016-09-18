from multiprocessing import Queue
import time

import pytest

from concurrently import concurrently, ProcessEngine, UnhandledExceptions

from . import EngineTest, paramz_conc_count, paramz_data_count


def process(data):
    time.sleep(data)
    return time.time()


class TestProcessEngine(EngineTest):

    @paramz_conc_count
    @paramz_data_count
    def test_concurrently(self, conc_count, data_count):
        data = range(data_count)
        q_data = Queue()
        for d in data:
            q_data.put(d)
        q_results = Queue()
        start_time = time.time()

        @concurrently(conc_count, engine=ProcessEngine)
        def _parallel():
            while not q_data.empty():
                d = q_data.get()
                res = process(d)
                q_results.put({d: res})

        _parallel()

        def calc_delta(n):
            if n // conc_count == 0:
                return n
            return n + calc_delta(n - conc_count)

        results = {}
        while not q_results.empty():
            results.update(q_results.get())

        assert len(results) == data_count
        for n, v in results.items():
            delta = v - start_time
            assert int(delta) == calc_delta(n)

    def test_stop(self):
        data = range(3)
        q_data = Queue()
        for d in data:
            q_data.put(d)
        q_results = Queue()
        start_time = time.time()

        @concurrently(2, engine=ProcessEngine)
        def _parallel():
            while not q_data.empty():
                d = q_data.get()
                res = process(d)
                q_results.put({d: res})

        time.sleep(0.5)
        _parallel.stop()

        results = {}
        while not q_results.empty():
            results.update(q_results.get())

        assert len(results) == 1
        assert int(results[0]) == int(start_time)

    def test_exception(self):
        data = range(2)
        q_data = Queue()
        for d in data:
            q_data.put(d)

        @concurrently(2, engine=ProcessEngine)
        def _parallel():
            while not q_data.empty():
                d = q_data.get()
                if d == 1:
                    raise RuntimeError()

        with pytest.raises(UnhandledExceptions) as exc:
            _parallel()

        assert len(exc.value.exceptions) == 1
        assert isinstance(exc.value.exceptions[0], RuntimeError)

    def test_exception_suppress(self):
        data = range(2)
        q_data = Queue()
        for d in data:
            q_data.put(d)
        q_results = Queue()
        start_time = time.time()

        @concurrently(2, engine=ProcessEngine)
        def _parallel():
            while not q_data.empty():
                d = q_data.get()
                if d == 1:
                    raise RuntimeError()
                res = process(d)
                q_results.put({d: res})

        _parallel(suppress_exceptions=True)

        results = {}
        while not q_results.empty():
            results.update(q_results.get())

        assert len(results) == 1
        assert int(results[0]) == int(start_time)

        exc_list = _parallel.exceptions()
        assert len(exc_list) == 1
        assert isinstance(exc_list[0], RuntimeError)

    def test_fail_hard(self):
        data = range(2)
        q_data = Queue()
        for d in data:
            q_data.put(d)
        q_results = Queue()

        @concurrently(2, engine=ProcessEngine)
        def _parallel():
            while not q_data.empty():
                d = q_data.get()
                if d == 1:
                    raise RuntimeError()
                time.sleep(d)
                q_results.put({d: True})

        with pytest.raises(RuntimeError):
            _parallel(fail_hard=True)

        results = {}
        while not q_results.empty():
            results.update(q_results.get())

        assert len(results) == 1
        assert results[0]
