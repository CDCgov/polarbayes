import pytest
from polarbayes import schema as s


@pytest.mark.parametrize(
    ["input", "expected", "chain_id_col", "draw_id_col"],
    [
        (["a", "0b", "draw", "chain"], ["chain", "draw", "0b", "a"], None, None),
        (
            ["chain", "draw", "a", "0b", "custom_draw_name", "custom_chain_name"],
            ["custom_chain_name", "custom_draw_name", "0b", "a", "chain", "draw"],
            "custom_chain_name",
            "custom_draw_name",
        ),
        (["a", "0b", "b"], ["0b", "a", "b"], None, None),
        (["a", "0b", "b"], ["0b", "a", "b"], "custom_chain_name", "custom_draw_name"),
        (["draw", "chain"], ["chain", "draw"], None, None),
        (["a", "0b", "chain"], ["chain", "0b", "a"], None, None),
        (["chain", "draw", "a"], ["chain", "draw", "a"], None, None),
        (["a", "0b", "chain"], ["0b", "a", "chain"], "custom_chain_name", None),
        (["draw", "chain"], ["chain", "draw"], "custom_chain_name", "custom_draw_name"),
    ],
)
def test_order_index_column_names(input, expected, chain_id_col, draw_id_col):
    assert (
        s.order_index_column_names(
            input, chain_id_col=chain_id_col, draw_id_col=draw_id_col
        )
        == expected
    )
    # check it works with different types of iterable, not just lists.
    assert (
        s.order_index_column_names(
            iter(input), chain_id_col=chain_id_col, draw_id_col=draw_id_col
        )
        == expected
    )
    assert (
        s.order_index_column_names(
            (x for x in input), chain_id_col=chain_id_col, draw_id_col=draw_id_col
        )
        == expected
    )
