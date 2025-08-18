from collections.abc import Sequence
from typing import Iterable

import arviz as az
import numpy as np
import polars as pl
import polars.selectors as cs
from polars._typing import ColumnNameOrSelector

from polarbayes.spread import spread_draws_and_get_index_cols


def _assert_not_in_index_columns(
    arg_name: str, arg_value: str, index_columns: Iterable[str]
) -> None:
    """
    Assert that a specified value is not present in a set of index columns,
    with an informative error message.

    Parameters
    ----------
    arg_name
        The name of the argument being validated.
    arg_value
        The value of the argument to check against index columns.
    index_columns
        Iterable of index column names to check against.

    Returns
    -------
    None
       If validation passes.

    Raises
    ------
    ValueError
        If `arg_value` is found in `index_columns`.
    """
    if arg_value in index_columns:
        raise ValueError(
            f"Specified {arg_name}='{arg_value}' for the output data frame "
            f"but there is an index column named '{arg_value}' "
            f"in the input data frame. Either specify a different "
            f" {arg_name} or rename the index column named '{arg_value}'."
        )
    return None


def gather_variables(
    data: pl.LazyFrame | pl.DataFrame,
    index: ColumnNameOrSelector | Sequence[ColumnNameOrSelector] | None = None,
    value_name: str = "value",
    variable_name: str = "variable",
):
    """
    Gather variable columns into key-value pairs.
    Light wrapper of `pl.DataFrame.unpivot()`.
    designed for use with `spread_draws()` output.

    Parameters
    ----------
    data
        Input DataFrame to (un)pivot from wide to long format.
    index
        Polars expression selecting mandatory or optional columns to
        index the gather. Passed as the `index` argument to
        `pl.DataFrame.unpivot()`. If `None` (default), use the columns
        `["chain", "draw"]` if they are present. Those are the MCMC
        index columns created when `spread_draws()` is on a standard
        `az.InferenceData` object.

    value_name
        Name for the value column in the output DataFrame. Default `"value"`.

    variable_name
        Name for the variable column in the output DataFrame. Default `"variable"`.

    Returns
    -------
    pl.LazyFrame | pl.DataFrame
        Unpivoted (pivoted longer) tidy data frame with index columns plus
        variable name and value columns.

    Raises
    ------
    ValueError
        If `value_name` or `variable_name` conflicts with requested index columns.
    """
    if index is None:
        index = cs.by_name("chain", "draw", require_all=False)

    index_names = data.select(index).collect_schema().names()

    # more informative error message than `unpivot()` gives on its own
    [
        _assert_not_in_index_columns(k, v, index_names)
        for k, v in dict(
            value_name=value_name, variable_name=variable_name
        ).items()
    ]

    return data.unpivot(
        index=index, variable_name=variable_name, value_name=value_name
    )


def gather_draws(
    data: az.InferenceData,
    group: str = "posterior",
    combined: bool = True,
    var_names: Iterable[str] = None,
    filter_vars: str = None,
    num_samples: int = None,
    rng: bool | int | np.random.Generator = None,
    value_name: str = "value",
    variable_name: str = "variable",
) -> pl.DataFrame:
    """
    Convert an ArviZ InferenceData object to a polars
    DataFrame of tidy (gathered) draws, using the syntax of
    `arviz.extract`.

    Parameters
    ----------
    data
        Data to convert.

    group
        `group` parameter passed to `az.extract`.

    combined
        `combined` parameter passed to `az.extract`.

    var_names
        `var_names` parameter passed to `az.extract`.

    filter_vars
        `filter_vars` parameter passed to `az.extract`.

    num_samples
        `num_samples` parameter passed to `az.extract`.

    rng
        `rng` parameter passed to `az.extract`.

    value_name
        Name for the value column in the output DataFrame. Default `"value"`.

    variable_name
        Name for the variable column in the output DataFrame. Default `"variable"`.

    Returns
    -------
    pl.DataFrame
        The DataFrame of tidy (gathered) draws, including
        standard columns to identify a unique sample
        (typically `"chain"` and "draw"`), a column of variable
        names, a column of associated variable values,
        plus (as needed) columns that index array-valued variables.
    """
    # need to extract all variables jointly to ensure same
    # draws for each
    extracted = az.extract(
        data,
        group=group,
        combined=combined,
        var_names=var_names,
        filter_vars=filter_vars,
        num_samples=num_samples,
        keep_dataset=True,
        rng=rng,
    )
    var_names = extracted.data_vars.keys()
    return pl.concat(
        [
            gather_variables(
                *spread_draws_and_get_index_cols(
                    extracted,
                    group=group,
                    var_names=var,
                    combined=False,
                    filter_vars=None,
                    num_samples=None,
                    rng=False,
                    enforce_drop_chain_draw=combined,
                ),
                variable_name="variable",
                value_name="value",
            )
            for var in var_names
        ],
        how="diagonal",
    )
