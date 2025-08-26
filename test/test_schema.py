import pytest
from polarbayes import schema as s


@pytest.mark.parametrize(
    ["input", "expected", "chain_name", "draw_name"],
    [
        (
            ["a", "0b", s.DRAW_NAME, s.CHAIN_NAME],
            [s.CHAIN_NAME, s.DRAW_NAME, "0b", "a"],
            None,
            None,
        ),
        (
            [
                s.CHAIN_NAME,
                s.DRAW_NAME,
                "a",
                "0b",
                s.CHAIN_NAME + "_custom",
                s.DRAW_NAME + "_custom",
            ],
            [
                s.CHAIN_NAME + "_custom",
                s.DRAW_NAME + "_custom",
                "0b",
                "a",
                s.CHAIN_NAME,
                s.DRAW_NAME,
            ],
            s.CHAIN_NAME + "_custom",
            s.DRAW_NAME + "_custom",
        ),
        (["a", "0b", "b"], ["0b", "a", "b"], None, None),
        (["a", "0b", "b"], ["0b", "a", "b"], "custom_chain_name", "custom_draw_name"),
        ([s.DRAW_NAME, s.CHAIN_NAME], [s.CHAIN_NAME, s.DRAW_NAME], None, None),
        (["a", "0b", s.CHAIN_NAME], [s.CHAIN_NAME, "0b", "a"], None, None),
        (["a", "0b", s.DRAW_NAME], [s.DRAW_NAME, "0b", "a"], None, None),
        (
            [s.CHAIN_NAME, s.DRAW_NAME, "a"],
            [s.CHAIN_NAME, s.DRAW_NAME, "a"],
            None,
            None,
        ),
        (
            ["a", "0b", s.CHAIN_NAME],
            ["0b", "a", s.CHAIN_NAME],
            s.CHAIN_NAME + "_custom",
            None,
        ),
        (
            [s.CHAIN_NAME, s.DRAW_NAME],
            [s.CHAIN_NAME, s.DRAW_NAME],
            s.CHAIN_NAME + "_custom",
            s.DRAW_NAME + "_custom",
        ),
    ],
)
def test_order_index_column_names(input, expected, chain_name, draw_name):
    assert (
        s.order_index_column_names(input, chain_name=chain_name, draw_name=draw_name)
        == expected
    )
    # check it works with different types of iterable, not just lists.
    assert (
        s.order_index_column_names(
            iter(input), chain_name=chain_name, draw_name=draw_name
        )
        == expected
    )
    assert (
        s.order_index_column_names(
            (x for x in input), chain_name=chain_name, draw_name=draw_name
        )
        == expected
    )
