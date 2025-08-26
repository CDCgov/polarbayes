"""
Column order schemas for polarbayes output
"""

from typing import Iterable


def order_index_column_names(
    index_columns: Iterable[str], chain_id_col: str = "chain", draw_id_col: str = "draw"
) -> Iterable[str]:
    """
    Order a list of index column names by placing the reserved
    names for the chain and draw ids first and then sorting
    additional index columns alphabetically.

    Parameters
    ----------
    index_columns
        Iterable of index column names.

    chain_id_col
        Reserved name for the chain ID column. Will always
        be placed first in the order, if present. Default
        `"chain"`

    draw_id_col
        Reserved name for the draw ID column. Will always
        be placed immediately after the `chain_id_col`
        in the order, if present. Default `"draw"`.

    Returns
    -------
    The column names, ordered, with the reserved names first
    and then additional column names ordered alphabetically.
    """
    return sorted(
        index_columns,
        key=lambda x: {chain_id_col: (0, 0), draw_id_col: (1, 0)}.get(x, (2, x)),
    )
