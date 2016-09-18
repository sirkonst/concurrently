import pytest


paramz_conc_count = pytest.mark.parametrize(
    'conc_count', range(1, 5), ids=lambda v: 'counc %s' % v
)
paramz_data_count = pytest.mark.parametrize(
    'data_count', range(1, 5), ids=lambda v: 'data %s' % v
)


class EngineTest:

    @paramz_conc_count
    @paramz_data_count
    def test_concurrently(self, conc_count: int, data_count: int, *_):
        pytest.skip('test not implemented')

    def test_stop(self, *_):
        pytest.skip('test not implemented')

    def test_exception(self, *_):
        pytest.skip('test not implemented')

    def test_exception_suppress(self, **_):
        pytest.skip('test not implemented')

    def test_fail_hard(self, *_):
        pytest.skip('test not implemented')
