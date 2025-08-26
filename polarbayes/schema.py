"""
Column order schemas for polarbayes output
"""


def order_index_column_names(
    index_columns: list[str], chain_id_col: str = "chain", draw_id_col: str = "draw"
) -> list[str]:
    """
    Order a list of index column names by placing the reserved
    names for the chain and draw ids first and then sorting
    additional index columns alphabetically.
    """
    return sorted(
        index_columns,
        key=lambda x: {chain_id_col: (0, 0), draw_id_col: (1, 0)}.get(x, (2, x)),
    )
