import pytest
from polarbayes import schema as s


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        (["a", "0b", "draw", "chain"], ["chain", "draw", "0b", "a"]),
        (["a", "0b", "b"], ["0b", "a", "b"]),
        (["draw", "chain"], ["chain", "draw"]),
        (["a", "0b", "chain"], ["chain", "0b", "a"]),
        (["chain", "draw", "a"], ["chain", "draw", "a"]),
    ],
)
def test_order_index_column_names(input, expected):
    assert s.order_index_column_names(input) == expected
