"""
Column order schemas for polarbayes output
"""

from typing import Iterable

# default and reserved column names
CHAIN_NAME = "chain"
DRAW_NAME = "draw"
VARIABLE_NAME = "variable"
VALUE_NAME = "value"


def order_index_column_names(
    index_columns: Iterable[str],
    chain_name: str | None = None,
    draw_name: str | None = None,
) -> list[str]:
    """
    Order an iterable of index column names by placing the reserved
    names for the chain and draw ids first and then sorting
    additional index columns alphabetically.

    Parameters
    ----------
    index_columns
        Iterable of index column names.

    chain_name
        Reserved name for the chain ID column. Will always
        be placed first in the order, if present. If `None`
        (default), use `"chain"`

    draw_name
        Reserved name for the draw ID column. Will always
        be placed immediately after the `chain_id_col`
        in the order, if present. Default if `None` (default),
        use `"draw"`.

    Returns
    -------
    A list of column names, ordered, with the reserved names first
    and then additional column names ordered alphabetically.
    """
    if chain_name is None:
        chain_name = CHAIN_NAME
    if draw_name is None:
        draw_name = DRAW_NAME
    return sorted(
        index_columns,
        key=lambda x: {chain_name: (0, 0), draw_name: (1, 0)}.get(x, (2, x)),
    )
