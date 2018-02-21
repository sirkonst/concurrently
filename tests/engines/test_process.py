import time
from multiprocessing import Queue
from queue import Empty

import pytest

from concurrently import concurrently, ProcessEngine, UnhandledExceptions
from . import EngineTest, paramz_conc_count


def process(data):
    time.sleep(data)
    return time.time()


class TestProcessEngine(EngineTest):

    @paramz_conc_count
    def test_concurrently(self, conc_count):
        q_results = Queue()

        start_time = time.time()

        @concurrently(conc_count, engine=ProcessEngine)
        def _parallel():
            st = time.time()
            time.sleep(1)
            et = time.time()

            q_results.put((st, et))

        _parallel()
        end_time = time.time()

        results = []
        while not q_results.empty():
            results.append(q_results.get())

        assert len(results) == conc_count, results

        for st, et in results:
            assert 0 <= st - start_time < 0.1
            assert 0 <= end_time - et < 0.1

    def test_stop(self):
        data = range(3)
        q_data = Queue()
        for d in data:
            q_data.put(d)
        q_results = Queue()
        start_time = time.time()

        @concurrently(2, engine=ProcessEngine)
        def _parallel():
            while True:
                try:
                    d = q_data.get_nowait()
                except Empty:
                    break

                if d != 0:
                    time.sleep(1)

                q_results.put({d: time.time()})

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
                else:
                    time.sleep(0.1)

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
            while True:
                try:
                    d = q_data.get_nowait()
                except Empty:
                    break

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
