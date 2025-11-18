from typing import Iterable

import arviz as az
import numpy as np
import pandas as pd
import polars as pl
import polars.selectors as cs

from polarbayes.schema import order_index_column_names


def spread_draws_to_pandas_(
    data: az.InferenceData,
    group: str = "posterior",
    combined: bool = True,
    var_names: Iterable[str] | None = None,
    filter_vars: str | None = None,
    num_samples: int | None = None,
    rng: bool | int | np.random.Generator | None = None,
) -> pd.DataFrame:
    """
    Convert an ArviZ InferenceData object group to a Pandas
    DataFrame of tidy (spread) draws, using the syntax of
    arviz.extract

    Parameters
    ----------
    data
        Data to convert.

    group
        `group` parameter passed to [`arviz.extract`][].

    combined
        `combined` parameter passed to [`arviz.extract`][].

    var_names
        `var_names` parameter passed to [`arviz.extract`][].

    filter_vars
        `filter_vars` parameter passed to [`arviz.extract`][].

    num_samples
        `num_samples` parameter passed to [`arviz.extract`][].

    rng
        `rng` parameter passed to [`arviz.extract`][].

    Returns
    -------
    pd.DataFrame
       Pandas DataFrame with a MultiIndex on the chain id,
       draw id, and any additional indices determined by
       the dimensions of the variables selected via
       `var_names` or `filter_vars`, with columns containing
       the associated values of those variables.
    """
    return az.extract(
        data,
        group=group,
        combined=combined,
        var_names=var_names,
        filter_vars=filter_vars,
        num_samples=num_samples,
        keep_dataset=True,
        rng=rng,
    ).to_dataframe()


def spread_draws_and_get_index_cols(
    data: az.InferenceData,
    group: str = "posterior",
    combined: bool = True,
    var_names: Iterable[str] | None = None,
    filter_vars: str | None = None,
    num_samples: int | None = None,
    rng: bool | int | np.random.Generator | None = None,
) -> tuple[pl.DataFrame, tuple]:
    """
    Convert an ArviZ InferenceData object to a polars
    DataFrame of tidy (spread) draws, using the syntax of
    arviz.extract. Return that DataFrame alongside a tuple
    giving the names of the DataFrame's index columns.

    Parameters
    ----------
    data
        Data to convert.

    group
        `group` parameter passed to [`arviz.extract`][].

    combined
        `combined` parameter passed to [`arviz.extract`][].

    var_names
        `var_names` parameter passed to [`arviz.extract`][].

    filter_vars
        `filter_vars` parameter passed to [`arviz.extract`][].

    num_samples
        `num_samples` parameter passed to [`arviz.extract`][].

    rng
        `rng` parameter passed to [`arviz.extract`][].

    Returns
    -------
    tuple[pl.DataFrame, tuple]
        Two-entry whose first entry is the DataFrame, and whose
        second entry is a tuple giving the names of that DataFrame's
        index columns. The DataFrame consists of columns named for
        variables and index columns. Columns named for variables
        contain the sampled values of those variables. Index columns
        include standard columns to identify a unique
        sample (typically `"chain"` and `"draw"`) plus (as needed)
        columns that index array-valued variables.
    """

    df = spread_draws_to_pandas_(
        data,
        group=group,
        combined=combined,
        var_names=var_names,
        filter_vars=filter_vars,
        num_samples=num_samples,
        rng=rng,
    )
    df, index_cols = pl.DataFrame(df.reset_index()), df.index.names
    index_cols_ordered = order_index_column_names(index_cols)

    return (
        df.select(
            cs.by_name(index_cols_ordered, require_all=True),
            cs.exclude(index_cols_ordered),
        ),
        index_cols_ordered,
    )


def spread_draws(
    data: az.InferenceData,
    group: str = "posterior",
    combined: bool = True,
    var_names: Iterable[str] | None = None,
    filter_vars: str | None = None,
    num_samples: int | None = None,
    rng: bool | int | np.random.Generator | None = None,
) -> pl.DataFrame:
    """
    Convert an ArviZ InferenceData object to a polars
    DataFrame of tidy (spread) draws, using the syntax of
    [`arviz.extract`][].

    Parameters
    ----------
    data
        Data to convert.

    group
        `group` parameter passed to [`arviz.extract`][].

    combined
        `combined` parameter passed to [`arviz.extract`][].

    var_names
        `var_names` parameter passed to [`arviz.extract`][].

    filter_vars
        `var_names` parameter passed to [`arviz.extract`][].

    num_samples
        `num_samples` parameter passed to [`arviz.extract`][].

    rng
        `rng` parameter passed to [`arviz.extract`][].

    Returns
    -------
    pl.DataFrame
        The DataFrame of tidy draws. Consists of columns named for
        variables and index columns. Columns named for variables
        contain the sampled values of those variables. Index columns
        include standard columns to identify a unique
        sample (typically `"chain"` and `"draw"`) plus (as needed)
        columns that index array-valued variables.
    """
    result, _ = spread_draws_and_get_index_cols(
        data,
        group=group,
        combined=combined,
        var_names=var_names,
        filter_vars=filter_vars,
        num_samples=num_samples,
        rng=rng,
    )
    return result
