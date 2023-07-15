import pandas as pd

from indexer import find_new


def build_df(combo):
    rows = {
        'a': ['2023-06-23', 10, 100, 'a'],
        'b': ['2023-06-24', 20, 200, 'b'],
        'c': ['2023-06-22', 40, 400, 'c'],
        'd': ['2023-06-24', 20, 200, 'd'],
    }
    return pd.DataFrame(map(lambda k: rows[k], combo), columns=['Date', 'Value', 'Balance', 'Source']).astype('string')


def assert_order_irrelevant(output, expected):
    result = output.sort_values(output.columns.to_list()).reset_index(drop=True)
    expected = expected.sort_values(expected.columns.to_list()).reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


class TestSingular:
    def test_all_new(self):
        assert_order_irrelevant(find_new(build_df('cd'), build_df('ab')), build_df('cd'))

    def test_some_new(self):
        assert_order_irrelevant(find_new(build_df('abcd'), build_df('bc')), build_df('ad'))

    def test_no_new(self):
        assert_order_irrelevant(find_new(build_df('bc'), build_df('abcd')), build_df(''))

    def test_possibly_new_empty(self):
        assert_order_irrelevant(find_new(build_df(''), build_df('ab')), build_df(''))

    def test_existing_empty(self):
        assert_order_irrelevant(find_new(build_df('ab'), build_df('')), build_df('ab'))

    def test_all_empty(self):
        assert_order_irrelevant(find_new(build_df(''), build_df('')), build_df(''))


class TestDuplicates:
    def test_all_new(self):
        assert_order_irrelevant(find_new(build_df('cc'), build_df('ab')), build_df('cc'))

    def test_some_new(self):
        assert_order_irrelevant(find_new(build_df('abbcc'), build_df('bbc')), build_df('ac'))

    def test_no_new(self):
        assert_order_irrelevant(find_new(build_df('bcc'), build_df('abbcc')), build_df(''))

    def test_possibly_new_empty(self):
        assert_order_irrelevant(find_new(build_df(''), build_df('abb')), build_df(''))

    def test_existing_empty(self):
        assert_order_irrelevant(find_new(build_df('abb'), build_df('')), build_df('abb'))
